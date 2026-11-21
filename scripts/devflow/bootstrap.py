"""Instalação e conferência do fluxo num projeto (``bootstrap.py <subcomando>``).

- ``init [--skill-dir D] [--default-branch B] [--initial-version V] [--force] [--no-labels] [--dry-run]``:
  gera a configuração, os workflows, os modelos de issue e de PR e instala o hook ``commit-msg``. Se
  o skill estiver fora do repositório, copia-o para ``--skill-dir`` (padrão
  ``.claude/skills/dev-workflow``; o CI precisa dos scripts versionados). Arquivos que já existem só
  são trocados com ``--force``. Grava o manifesto (``.github/dev-workflow-manifest.json``).
- ``update [--force] [--dry-run]``: rodado a partir da versão nova do skill (fora do projeto),
  troca a cópia no caminho registrado no manifesto, regenera os workflows e modelos que não foram
  personalizados, remove os que a versão nova deixou de gerar e renova o hook. Tudo ou nada: uma
  falha no meio devolve a cópia e os arquivos anteriores. A configuração do projeto nunca é tocada.
- ``uninstall [--yes]``: lista o que sai (o que não foi personalizado) e o que fica; com ``--yes``,
  remove.
- ``install-hook``: instala o hook ``commit-msg`` em ``.git/hooks`` (projetos sem pre-commit).
- ``doctor``: confere a instalação e lista o que falta, inclusive os passos de quem é dono.
- ``version``: a versão do skill.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from .config import CONFIG_CANDIDATES, Config, ConfigError, find_root, load
from .gh import CommandError, Git, GitHub, current_repository, offline, run_gh, utf8_streams
from .plan import Repo
from .release import ReleaseError, check_version_files
from .semver import Version
from .text import normalize_title, sections

SKILL = Path(__file__).resolve().parents[2]
ASSETS = SKILL / "assets"
VENDOR_PATH = ".claude/skills/dev-workflow"
# O que é do repositório do skill, não do skill: não vai para a cópia dentro de um projeto.
COPY_IGNORE = ("__pycache__", "*.pyc", "*-workspace", ".git", ".github", ".pr-head")
WORKFLOWS = ("pr-check.yml", "pr-merged.yml", "release.yml", "epic-checklist.yml", "semver-analysis.yml")
OPTIONAL_WORKFLOWS = ("dev-workflow-selftest.yml",)
# O que o fluxo gerou neste projeto: versão, onde está o skill e o hash de cada arquivo gerado.
MANIFEST = ".github/dev-workflow-manifest.json"
MANIFEST_SCHEMA = 1
# Primeira linha de comentário do hook gerado: é o que o distingue de um hook de outra origem.
HOOK_MARK = "Hook commit-msg do skill dev-workflow"
CLAUDE_HOOK = "assets/claude/dev-workflow-hook.mjs"
CLAUDE_SETTINGS = (".claude/settings.json", ".claude/settings.local.json")

# (arquivo, expressão que captura a versão, marcador usado no padrão de busca)
DETECTORS: tuple[tuple[str, str, str], ...] = (
    ("pyproject.toml", r'^version\s*=\s*"(?P<v>[^"]+)"', "{current_pep440}"),
    ("package.json", r'^\s*"version"\s*:\s*"(?P<v>[^"]+)"', "{current}"),
    ("Cargo.toml", r'^version\s*=\s*"(?P<v>[^"]+)"', "{current}"),
    ("composer.json", r'^\s*"version"\s*:\s*"(?P<v>[^"]+)"', "{current}"),
    ("pubspec.yaml", r"^version:\s*(?P<v>\S+)", "{current}"),
    ("mix.exs", r'version:\s*"(?P<v>[^"]+)"', "{current}"),
    ("build.gradle", r"^version\s*=?\s*'(?P<v>[^']+)'", "{current}"),
    ("build.gradle.kts", r'^version\s*=\s*"(?P<v>[^"]+)"', "{current}"),
    ("Directory.Build.props", r"<Version>(?P<v>[^<]+)</Version>", "{current}"),
    ("VERSION", r"^(?P<v>\d+\.\d+\.\d+[^\s]*)\s*$", "{current}"),
    ("version.txt", r"^(?P<v>\d+\.\d+\.\d+[^\s]*)\s*$", "{current}"),
)


def skill_version(skill: Path = SKILL) -> str:
    """Versão do skill (arquivo ``VERSION``); ``"?"`` numa cópia antiga, sem o arquivo."""
    try:
        return (skill / "VERSION").read_text(encoding="utf-8").strip() or "?"
    except OSError:
        return "?"


def is_skill(path: Path) -> bool:
    """O diretório tem este skill (e não outro com o mesmo caminho)?"""
    skill_md = path / "SKILL.md"
    if not skill_md.is_file() or not (path / "scripts" / "bootstrap.py").is_file():
        return False
    head = skill_md.read_text(encoding="utf-8", errors="replace")[:400]
    return re.search(r"^name:\s*dev-workflow\s*$", head, re.MULTILINE) is not None


def _skill_files(base: Path) -> set[str]:
    """Arquivos do skill em ``base``, relativos a ela, sem o que é só do repositório do skill."""
    ignore = shutil.ignore_patterns(*COPY_IGNORE)
    found: set[str] = set()
    for directory, dirs, names in os.walk(base):
        skipped = ignore(directory, [*dirs, *names])
        dirs[:] = [name for name in dirs if name not in skipped]
        here = Path(directory)
        found |= {(here / name).relative_to(base).as_posix() for name in names if name not in skipped}
    return found


def copy_skill(source: Path, destination: Path) -> tuple[list[str], list[str]]:
    """Espelha ``source`` em ``destination``: copia tudo e remove o que saiu. Devolve (copiados, removidos)."""
    wanted = _skill_files(source)
    removed = sorted(_skill_files(destination) - wanted) if destination.exists() else []
    for name in removed:
        (destination / name).unlink()
    for name in sorted(wanted):
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
    for directory, _dirs, _names in sorted(os.walk(destination), key=lambda item: -len(Path(item[0]).parts)):
        if Path(directory) != destination and not any(Path(directory).iterdir()):
            Path(directory).rmdir()
    return sorted(wanted), removed


def _normalize(version: str) -> Version | None:
    """Aceita SemVer e a forma PEP 440 das pré-releases (``1.2.0rc1``)."""
    direct = Version.try_parse(version)
    if direct:
        return direct
    match = re.fullmatch(r"(\d+\.\d+\.\d+)(a|b|rc)(\d+)", version)
    names = {"a": "alpha", "b": "beta", "rc": "rc"}
    return Version.try_parse(f"{match[1]}-{names[match[2]]}.{match[3]}") if match else None


def detect_version_files(root: Path) -> tuple[list[dict[str, str]], Version | None]:
    """Arquivos de versão reconhecidos na raiz e a versão que eles declaram."""
    entries: list[dict[str, str]] = []
    found: Version | None = None
    for name, pattern, token in DETECTORS:
        path = root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(pattern, text, re.MULTILINE)
        version = _normalize(match.group("v")) if match else None
        if not match or version is None:
            continue
        literal = match.group(0).strip()
        entry = {"path": name, "search": literal.replace(match.group("v"), token)}
        occurrences = text.count(literal)
        if occurrences != 1:
            entry["note"] = f"ATENÇÃO: `{literal}` aparece {occurrences} vezes; ajuste `search` ou use `count`."
        entries.append(entry)
        found = found or version
    return entries, found


def _toml_string(value: str) -> str:
    return f"'{value}'" if "'" not in value else json.dumps(value, ensure_ascii=False)


def render_version_files(entries: list[dict[str, str]]) -> str:
    if not entries:
        return (
            "# Nenhum arquivo de versão reconhecido: a versão vive só nas tags. Para escrevê-la em arquivos:\n"
            '# [[versioning.files]]\n# path = "caminho/do/arquivo"\n# search = \'version = "{current}"\'\n'
        )
    blocks = []
    for entry in entries:
        note = f"# {entry['note']}\n" if entry.get("note") else ""
        blocks.append(
            f'{note}[[versioning.files]]\npath = "{entry["path"]}"\nsearch = {_toml_string(entry["search"])}\n'
        )
    return "\n".join(blocks)


# Linha condicional de um modelo: ``conteúdo  # __IF_NOME__`` só fica se ``values["IF_NOME"]`` não é vazio.
_CONDITIONAL = re.compile(r"^(?P<line>.*?)[ \t]*# __IF_(?P<flag>\w+)__[ \t]*(?:\n|\Z)", re.MULTILINE)


def render(template: str, values: dict[str, str]) -> str:
    template = _CONDITIONAL.sub(
        lambda match: match["line"] + "\n" if values.get(f"IF_{match['flag']}") else "", template
    )
    for key, value in values.items():
        template = template.replace(f"__{key}__", value)
    return template


def default_branch(git: Git) -> str:
    head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD", check=False)
    if head.startswith("origin/"):
        return head[len("origin/") :]
    return git("symbolic-ref", "--short", "HEAD", check=False) or "main"


def skill_dir_in(root: Path) -> str | None:
    """Caminho do skill relativo à raiz do repositório, ou ``None`` se estiver fora dela."""
    try:
        return SKILL.relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def template_values(root: Path, skill_dir: str, branch: str, cfg: Config | None, git: Git) -> dict[str, str]:
    repository = current_repository(git) or "OWNER/REPO"
    return {
        "SKILL_DIR": skill_dir,
        "SKILL_GLOB": "**" if skill_dir == "." else f"{skill_dir}/**",
        "SKILL_PATH": "" if skill_dir == "." else f"{skill_dir}/",
        "DEFAULT_BRANCH": branch,
        "RELEASE_LABEL": cfg.label("release") if cfg else "release",
        "PRERELEASE_PREFIX": cfg.label("prerelease_prefix") if cfg else "release:",
        "REPOSITORY_URL": f"https://github.com/{repository}",
        # `actions: write` no release.yml só quando há workflow de publicação a disparar.
        "IF_DISPATCH": "1" if cfg and cfg.release["dispatch_workflow"] else "",
    }


def planned_files(values: dict[str, str], *, selftest: bool, assets: Path = ASSETS) -> dict[str, str]:
    """``{caminho no projeto: conteúdo}`` dos modelos, sem a configuração."""
    files: dict[str, str] = {}
    for name in (*WORKFLOWS, *(OPTIONAL_WORKFLOWS if selftest else ())):
        template = assets / "workflows" / name
        if template.is_file():
            files[f".github/workflows/{name}"] = render(template.read_text(encoding="utf-8"), values)
    for template in sorted((assets / "ISSUE_TEMPLATE").glob("*.yml")):
        files[f".github/ISSUE_TEMPLATE/{template.name}"] = render(template.read_text(encoding="utf-8"), values)
    pull_request = assets / "pull_request_template.md"
    if pull_request.is_file():
        files[".github/pull_request_template.md"] = pull_request.read_text(encoding="utf-8")
    return files


# --- manifesto ---------------------------------------------------------------------------------


class ManifestError(ValueError):
    """Manifesto ilegível ou de outro formato."""


@dataclass
class Manifest:
    """O que uma instalação gerou: com ele, arquivo gerado e não editado é reconhecido pelo hash,
    mesmo depois de a configuração (label, branch) mudar o que o modelo renderiza."""

    version: str
    skill_dir: str
    files: dict[str, str] = field(default_factory=dict)

    def pristine(self, name: str, text: str) -> bool:
        return self.files.get(name) == digest(text)

    def text(self) -> str:
        data = {
            "about": "Gerado pelo bootstrap.py do skill dev-workflow; não edite à mão.",
            "schema": MANIFEST_SCHEMA,
            "version": self.version,
            "skill_dir": self.skill_dir,
            "files": dict(sorted(self.files.items())),
        }
        return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def digest(text: str) -> str:
    """sha256 do conteúdo com fim de linha LF: um checkout com ``autocrlf`` não parece editado."""
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def read_manifest(root: Path) -> Manifest | None:
    path = root / MANIFEST
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ManifestError(f"{MANIFEST} ilegível: {exc}") from exc
    files = data.get("files") if isinstance(data, dict) else None
    if (
        not isinstance(files, dict)
        or data.get("schema") != MANIFEST_SCHEMA
        or not isinstance(data.get("skill_dir"), str)
        or not all(isinstance(key, str) and isinstance(value, str) for key, value in files.items())
    ):
        raise ManifestError(f"{MANIFEST} não está no formato {MANIFEST_SCHEMA} (schema, version, skill_dir, files)")
    try:
        skill_dir = "." if data["skill_dir"] == "." else normalize_skill_dir(data["skill_dir"])
    except ValueError as exc:
        raise ManifestError(f"{MANIFEST}: {exc}") from exc
    return Manifest(str(data.get("version", "?")), skill_dir, dict(files))


def normalize_skill_dir(value: str) -> str:
    """Caminho do skill relativo à raiz, com ``/``; recusa o que sairia do repositório."""
    raw = value.strip().replace("\\", "/")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or re.match(r"^[A-Za-z]:", raw) or ".." in path.parts:
        raise ValueError(f"o caminho do skill ({value!r}) tem de ser relativo à raiz e ficar dentro do repositório")
    normalized = path.as_posix()
    if normalized in ("", ".") or path.parts[0] == ".git":
        raise ValueError(f"o caminho do skill ({value!r}) não pode ser a raiz do repositório nem ficar em .git")
    return normalized


def installed_skill_dir(root: Path, manifest: Manifest | None) -> str:
    """Onde está o skill do projeto: este mesmo, se roda de dentro; senão o do manifesto ou o padrão."""
    inside = skill_dir_in(root)
    if inside is not None:
        return inside
    return manifest.skill_dir if manifest else VENDOR_PATH


class Transaction:
    """Grava tudo ou nada: guarda o estado anterior de cada caminho e o devolve se algo falhar."""

    def __init__(self) -> None:
        self._undo: list[Callable[[], None]] = []
        self._leftovers: list[Path] = []

    def write(self, path: Path, content: str, *, executable: bool = False) -> None:
        previous = path.read_bytes() if path.is_file() else None
        missing = [parent for parent in reversed(path.parents) if not parent.exists()]
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.dev-workflow-tmp")
        temporary.write_bytes(content.encode("utf-8"))
        try:
            os.replace(temporary, path)
        except OSError:
            temporary.unlink(missing_ok=True)
            for parent in reversed(missing):
                _rmdir_if_empty(parent)
            raise
        if executable:
            path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        def undo() -> None:
            if previous is None:
                path.unlink(missing_ok=True)
                for parent in reversed(missing):
                    _rmdir_if_empty(parent)
            else:
                path.write_bytes(previous)

        self._undo.append(undo)

    def remove(self, path: Path) -> None:
        previous = path.read_bytes()
        path.unlink()
        self._undo.append(lambda: (path.parent.mkdir(parents=True, exist_ok=True), path.write_bytes(previous)))

    def swap_dir(self, staged: Path, destination: Path) -> None:
        """Põe ``staged`` no lugar de ``destination``; a anterior fica de reserva até o fim."""
        backup = destination.with_name(f".{destination.name}.update-old")
        _rmtree(backup)
        os.rename(destination, backup)
        try:
            os.rename(staged, destination)
        except OSError:
            os.rename(backup, destination)
            raise

        def undo() -> None:
            _rmtree(destination)
            os.rename(backup, destination)

        self._undo.append(undo)
        self._leftovers.append(backup)

    def rollback(self) -> list[str]:
        """Desfaz na ordem inversa; devolve o que não conseguiu desfazer."""
        failures = []
        for undo in reversed(self._undo):
            try:
                undo()
            except OSError as exc:
                failures.append(str(exc))
        self._undo.clear()
        return failures

    def commit(self) -> None:
        for path in self._leftovers:
            _rmtree(path)
        self._undo.clear()


def _rmtree(path: Path) -> None:
    def retry(function, name, _exc):  # arquivo somente leitura no Windows
        os.chmod(name, stat.S_IWRITE)
        function(name)

    if path.exists():
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, onexc=retry)
        else:
            shutil.rmtree(path, onerror=retry)


def _rmdir_if_empty(path: Path) -> None:
    try:
        path.rmdir()
    except OSError:
        pass


def _prune_empty(path: Path, root: Path) -> None:
    """Remove os diretórios que ficaram vazios, de ``path`` até a raiz (exclusive)."""
    root = root.resolve()
    current = path.resolve()
    while current != root and root in current.parents:
        if not current.is_dir() or any(current.iterdir()):
            return
        current.rmdir()
        current = current.parent


# --- hook commit-msg -----------------------------------------------------------------------------


def hook_path(git: Git) -> Path:
    path = Path(git("rev-parse", "--git-path", "hooks/commit-msg"))
    return path if path.is_absolute() else (git.root or Path.cwd()) / path


def hook_content(skill_dir: str, assets: Path = ASSETS) -> str:
    return render((assets / "hooks" / "commit-msg").read_text(encoding="utf-8"), {"SKILL_DIR": skill_dir})


def install_hook(root: Path, skill_dir: str, *, force: bool = False) -> str:
    git = Git(root)
    target = hook_path(git)
    content = hook_content(skill_dir)
    if target.exists() and not force:
        existing = target.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        if existing == content:
            return f"hook commit-msg já instalado em {target}"
        if HOOK_MARK in existing:
            pass  # o hook deste skill, de outra versão ou de outro caminho: é renovado
        elif "github_issues.py" in existing or "pre-commit" in existing:
            return f"hook commit-msg já instalado em {target}"
        else:
            return f"ATENÇÃO: {target} já existe e é de outra origem; use --force para trocar ou chame o script a partir dele"
    renewed = target.exists()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content.encode("utf-8"))
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return f"hook commit-msg {'renovado' if renewed else 'instalado'} em {target}"


def init(args: argparse.Namespace) -> int:
    root = find_root()
    git = Git(root)
    if not (root / ".git").exists():
        print("ERRO: rode dentro de um repositório git (`git init` primeiro).", file=sys.stderr)
        return 1
    try:
        wanted = normalize_skill_dir(args.skill_dir) if args.skill_dir else None
        manifest = read_manifest(root)
    except ValueError as exc:
        return _refuse(str(exc))
    skill_dir = skill_dir_in(root)
    actions: list[str] = []
    if skill_dir is not None and wanted is not None and wanted != skill_dir:
        return _refuse(
            f"este skill já está no repositório, em {skill_dir}; --skill-dir só vale rodando o init de uma cópia "
            "de fora do projeto."
        )
    if skill_dir is None:
        skill_dir = wanted or (manifest.skill_dir if manifest else VENDOR_PATH)
        destination = root / skill_dir
        if destination.exists() and not args.force:
            return _refuse(f"{skill_dir} já existe; rode o bootstrap de lá ou use --force.")
        if not args.dry_run:
            copy_skill(SKILL, destination)
        actions.append(
            f"skill dev-workflow {skill_version()} copiado para {skill_dir} "
            "(os workflows do CI chamam os scripts de lá)"
        )
    branch = args.default_branch or default_branch(git)
    entries, detected = detect_version_files(root)
    initial = args.initial_version or (str(detected) if detected else "0.1.0")
    if Version.try_parse(initial) is None:
        return _refuse(f"'{initial}' não é uma versão SemVer.")
    existing_config = next((name for name in CONFIG_CANDIDATES if (root / name).is_file()), None)
    cfg: Config | None = None
    if existing_config is not None and not args.force:
        try:  # os modelos seguem a configuração que fica (labels, por exemplo)
            cfg = load(root)
        except ConfigError as exc:
            actions.append(f"ATENÇÃO: {exc}; modelos gerados com os valores padrão")
    values = template_values(
        root, skill_dir, cfg.default_branch if cfg and not args.default_branch else branch, cfg, git
    )
    files = planned_files(values, selftest=args.selftest)
    if existing_config is None or args.force:
        config_values = {**values, "INITIAL_VERSION": initial, "VERSION_FILES": render_version_files(entries)}
        files = {
            CONFIG_CANDIDATES[0]: render(
                (ASSETS / "dev-workflow.toml")
                .read_text(encoding="utf-8")
                .replace("# __VERSION_FILES__", "__VERSION_FILES__"),
                config_values,
            ),
            **files,
        }
    else:
        actions.append(f"{existing_config} mantido (já existe)")
    # O manifesto registra o que é do fluxo: o que este init gravou e o que já estava igual ao modelo.
    recorded = Manifest(skill_version(), skill_dir, dict(manifest.files) if manifest else {})
    for name, content in files.items():
        target = root / name
        if target.exists() and not args.force:
            same = target.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n") == content
            if same:
                recorded.files[name] = digest(content)
            actions.append(
                f"{name} {'já está igual ao modelo' if same else 'mantido (já existe e difere do modelo; --force troca)'}"
            )
            continue
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content.encode("utf-8"))
        recorded.files[name] = digest(content)
        actions.append(f"{name} criado")
    if not args.dry_run:
        (root / MANIFEST).parent.mkdir(parents=True, exist_ok=True)
        (root / MANIFEST).write_bytes(recorded.text().encode("utf-8"))
    actions.append(f"{MANIFEST} gravado (versão, caminho do skill e hash de cada arquivo gerado)")
    if (root / ".pre-commit-config.yaml").is_file():
        actions.append(
            f"projeto usa pre-commit: acrescente o trecho de {skill_dir}/assets/pre-commit-hook.yaml e rode `pre-commit install`"
        )
    elif not args.dry_run:
        actions.append(install_hook(root, skill_dir, force=args.force))
    if not args.no_labels and not args.dry_run and not offline():
        from .issues import sync_labels  # noqa: PLC0415

        try:
            ok = sync_labels(load(root)) == 0
        except (ConfigError, OSError) as exc:
            ok = False
            actions.append(f"labels: {exc}")
        actions.append(
            "labels criados no GitHub"
            if ok
            else "labels NÃO criados: rode `github_issues.py sync-labels` com o gh autenticado"
        )
    prefix = "[dry-run] " if args.dry_run else ""
    for action in actions:
        print(f"{prefix}{action}")
    print(
        "\nPróximos passos:\n"
        f"  1. Revise .github/dev-workflow.toml (arquivos de versão, superfícies públicas) e rode\n"
        f"     python3 {skill_dir}/scripts/bootstrap.py doctor\n"
        "  2. Commite os arquivos gerados e mescle na branch padrão: workflows só valem a partir dela.\n"
        f"  3. Crie a tag de base: python3 {skill_dir}/scripts/release.py baseline --push\n"
        f"  4. Passos de quem é dono (segredos, permissões, proteção de branch): {skill_dir}/references/installation.md"
    )
    return 0


# --- update ------------------------------------------------------------------------------------


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError:
        return None


def _refuse(message: str) -> int:
    print(f"ERRO: {message}", file=sys.stderr)
    return 1


def update(args: argparse.Namespace) -> int:
    """Troca a cópia do skill no projeto pela versão que está rodando este comando."""
    root = find_root()
    if skill_dir_in(root) is not None:
        return _refuse(
            "este é o skill que já está no projeto. Rode o update a partir da versão nova (por exemplo o\n"
            "clone do repositório do skill): python3 <skill-novo>/scripts/bootstrap.py update"
        )
    try:
        manifest = read_manifest(root)
    except ManifestError as exc:
        return _refuse(str(exc))
    skill_dir = manifest.skill_dir if manifest else VENDOR_PATH
    destination = root / skill_dir
    if not is_skill(destination):
        return _refuse(f"{skill_dir} não tem o skill dev-workflow; para instalar, use `bootstrap.py init`.")
    old, new = skill_version(destination), skill_version()
    old_version, new_version = Version.try_parse(old), Version.try_parse(new)
    if new_version is None:
        return _refuse(f"a versão do skill de origem ({new}) não é SemVer; confira o arquivo VERSION.")
    if old_version is not None and new_version.key() < old_version.key() and not args.force:
        return _refuse(f"a cópia instalada ({old}) é mais nova que a de origem ({new}); use --force para voltar.")
    try:
        cfg = load(root)
    except ConfigError as exc:
        return _refuse(str(exc))
    git = Git(root)

    # Arquivo não personalizado recebe o modelo novo: o hash bate com o do manifesto ou, sem ele, o
    # conteúdo é o modelo antigo com os valores de hoje. Arquivo personalizado só é trocado com
    # --force. Opcional ausente continua ausente.
    values = template_values(root, skill_dir, cfg.default_branch, cfg, git)
    before = planned_files(values, selftest=True, assets=destination / "assets")
    after = planned_files(values, selftest=True)
    recorded = manifest.files if manifest else {}
    renewed = Manifest(new, skill_dir, dict(recorded))
    optional = {f".github/workflows/{name}" for name in (*OPTIONAL_WORKFLOWS, "semver-analysis.yml")}

    def pristine(name: str, text: str) -> bool:
        return recorded.get(name) == digest(text) or text == before.get(name)

    regenerate: dict[str, str] = {}
    customized: list[str] = []
    for name, content in after.items():
        current = _read(root / name)
        if current == content:
            renewed.files[name] = digest(content)
        elif current is None and name in optional:
            renewed.files.pop(name, None)
        elif current is None or pristine(name, current) or args.force:
            regenerate[name] = content
            renewed.files[name] = digest(content)
        else:
            customized.append(name)
    # O que a versão nova deixou de gerar: sai se não foi editado; se foi, fica e deixa de ser do fluxo.
    obsolete: list[str] = []
    orphaned: list[str] = []
    for name in sorted((set(recorded) | set(before)) - set(after) - set(CONFIG_CANDIDATES)):
        renewed.files.pop(name, None)
        current = _read(root / name)
        if current is not None:
            (obsolete if pristine(name, current) else orphaned).append(name)

    # O hook deste checkout: renovado se é o do skill (o de outra origem não é tocado).
    hook = hook_path(git)
    current_hook = _read(hook)
    new_hook = hook_content(skill_dir)
    renew_hook = current_hook is not None and current_hook != new_hook and HOOK_MARK in current_hook

    prefix = "[dry-run] " if args.dry_run else ""
    wanted = _skill_files(SKILL)
    removed = sorted(_skill_files(destination) - wanted)
    if args.dry_run:
        print(f"{prefix}skill dev-workflow {old} → {new} em {skill_dir}")
    else:
        staged = destination.with_name(f".{destination.name}.update-new")
        _rmtree(staged)
        _rmtree(destination.with_name(f".{destination.name}.update-old"))
        transaction = Transaction()
        try:
            # Tudo o que pode falhar por espaço ou permissão acontece antes de tocar no projeto.
            copy_skill(SKILL, staged)
            transaction.swap_dir(staged, destination)
            for name, content in regenerate.items():
                transaction.write(root / name, content)
            for name in obsolete:
                transaction.remove(root / name)
            transaction.write(root / MANIFEST, renewed.text())
            if renew_hook:
                transaction.write(hook, new_hook, executable=True)
        except OSError as exc:
            failures = transaction.rollback()
            _rmtree(staged)
            if failures:
                return _refuse(
                    f"o update falhou ({exc}) e não consegui desfazer tudo: {'; '.join(failures)}. "
                    "Confira com `git status` e restaure com `git checkout -- .`."
                )
            return _refuse(
                f"o update falhou ({exc}); nada foi trocado: a cópia {old} e os arquivos continuam como antes."
            )
        transaction.commit()
        for name in obsolete:
            _prune_empty((root / name).parent, root)
        print(f"skill dev-workflow {old} → {new} em {skill_dir}: {len(wanted)} arquivo(s), {len(removed)} removido(s)")
        for name in removed:
            print(f"  removido {skill_dir}/{name}")
    for name in regenerate:
        print(f"{prefix}{name} atualizado pelo modelo novo")
    for name in obsolete:
        print(f"{prefix}{name} removido (a versão nova não o gera mais)")
    for name in customized:
        print(
            f"{prefix}ATENÇÃO: {name} foi personalizado e difere do modelo novo; compare e ajuste à mão "
            "(ou rode de novo com --force para trocar)"
        )
    for name in orphaned:
        print(f"{prefix}ATENÇÃO: {name} não é mais gerado pela versão nova, mas foi personalizado: ficou; remova à mão")
    if renew_hook:
        print(f"{prefix}hook commit-msg renovado em {hook}")
    print(f"{prefix}{MANIFEST} {'gravado' if manifest is None else 'atualizado'}")
    print(f"{prefix}{CONFIG_CANDIDATES[0]} mantido (o update nunca troca a configuração)")
    print(
        "\nPróximos passos:\n"
        f"  1. python3 {skill_dir}/scripts/bootstrap.py doctor\n"
        "  2. Revise o diff e commite numa branch da issue da atualização; workflows novos valem depois\n"
        "     do merge na branch padrão. Os outros checkouts renovam o hook com `bootstrap.py install-hook`."
    )
    return 0


# --- uninstall ---------------------------------------------------------------------------------


def _claude_hook_files(root: Path) -> list[str]:
    """Arquivos de configuração do Claude Code que chamam o hook do skill."""
    return [name for name in CLAUDE_SETTINGS if "dev-workflow-hook.mjs" in (_read(root / name) or "")]


def uninstall(args: argparse.Namespace) -> int:
    """Remove o que o fluxo gerou e não foi personalizado; lista o resto. Sem ``--yes``, só lista."""
    root = find_root()
    git = Git(root)
    try:
        manifest = read_manifest(root)
        cfg = load(root)
    except (ManifestError, ConfigError) as exc:
        return _refuse(str(exc))
    skill_dir = installed_skill_dir(root, manifest)
    copy = root / skill_dir
    # O skill na raiz do repositório é o próprio projeto: só os arquivos gerados saem.
    remove_copy = skill_dir != "." and is_skill(copy)
    assets = (copy if is_skill(copy) else SKILL) / "assets"
    values = template_values(root, skill_dir, cfg.default_branch, cfg, git)
    planned = planned_files(values, selftest=True, assets=assets)
    recorded = manifest.files if manifest else {}
    config = cfg.path.relative_to(root).as_posix() if cfg.path and cfg.path.is_relative_to(root) else None

    remove: list[str] = []
    keep: list[str] = []
    for name in sorted(set(recorded) | set(planned) | ({config} if config else set())):
        current = _read(root / name)
        if current is None:
            continue
        if recorded.get(name) == digest(current) or current == planned.get(name):
            remove.append(name)
        else:
            keep.append(f"{name} (personalizado)" if name != config else f"{name} (configuração do projeto)")
    hook = hook_path(git)
    hook_text = _read(hook)
    remove_hook = hook_text is not None and hook_text in (hook_content(skill_dir, assets), hook_content(skill_dir))
    if hook_text is not None and not remove_hook and HOOK_MARK in hook_text:
        keep.append(f"{hook} (hook commit-msg editado)")
    if (root / ".pre-commit-config.yaml").is_file() and "github_issues.py" in (
        _read(root / ".pre-commit-config.yaml") or ""
    ):
        keep.append(".pre-commit-config.yaml (tire o trecho do dev-workflow e rode `pre-commit install`)")
    keep += [f"{name} (tire os hooks que chamam dev-workflow-hook.mjs)" for name in _claude_hook_files(root)]
    keep.append("labels no GitHub, tags de versão e changelog (são o histórico; remova à mão se quiser)")

    print(f"Desinstalação do dev-workflow em {root}:")
    if remove_copy:
        print(f"  sai   {skill_dir}/ (cópia do skill {skill_version(copy)})")
    for name in remove:
        print(f"  sai   {name}")
    if remove_hook:
        print(f"  sai   {hook}")
    if (root / MANIFEST).is_file():
        print(f"  sai   {MANIFEST}")
    for item in keep:
        print(f"  fica  {item}")
    if not args.yes:
        print("\nNada foi removido: confira a lista e rode de novo com --yes.")
        return 0

    for name in remove:
        (root / name).unlink()
        _prune_empty((root / name).parent, root)
    if remove_hook:
        hook.unlink()
    (root / MANIFEST).unlink(missing_ok=True)
    _prune_empty((root / MANIFEST).parent, root)
    if remove_copy:  # por último: pode ser a cópia que está rodando este comando
        _rmtree(copy)
        _prune_empty(copy.parent, root)
    print("\nRemovido. Commite a remoção numa branch de issue; o que ficou está na lista acima.")
    return 0


# --- doctor ------------------------------------------------------------------------------------


class Report:
    def __init__(self) -> None:
        self.errors = 0
        self.pending = 0

    def ok(self, message: str) -> None:
        print(f"  ok        {message}")

    def todo(self, message: str) -> None:
        self.pending += 1
        print(f"  PENDENTE  {message}")

    def error(self, message: str) -> None:
        self.errors += 1
        print(f"  ERRO      {message}")


_SCRIPT_CALL = re.compile(r"""(?:python3?\s+|script=")([^\s"'$]+)/scripts/(?:release|github_issues)\.py""")


def workflow_problems(name: str, text: str, cfg: Config, skill_dir: str) -> list[str]:
    """O que no workflow contradiz a configuração ou o lugar do skill (vale para os personalizados)."""
    problems = []
    paths = sorted({match.group(1) for match in _SCRIPT_CALL.finditer(text)} - {skill_dir})
    if paths:
        problems.append(f"chama os scripts em {', '.join(paths)}, mas o skill está em {skill_dir}")
    if name.endswith("/release.yml"):
        match = re.search(r"^\s*branches:\s*\[(?P<items>[^\]]*)\]", text, re.MULTILINE)
        branches = [item.strip().strip("'\"") for item in match.group("items").split(",")] if match else []
        if match and cfg.default_branch not in branches:
            problems.append(f"não roda no push da branch padrão {cfg.default_branch} (branches: {', '.join(branches)})")
    dispatch = cfg.release["dispatch_workflow"]
    if name.endswith("/release.yml") and dispatch and not re.search(r"^\s*actions:\s*write\b", text, re.MULTILINE):
        problems.append(f"release.dispatch_workflow ({dispatch}) precisa de `actions: write`")
    if name.endswith("/semver-analysis.yml"):
        release, prefix = cfg.label("release"), cfg.label("prerelease_prefix")
        if f"'{release}'" not in text or f"',{prefix}'" not in text:
            problems.append(f"não reage aos labels de versão da configuração ({release}, {prefix}<canal>)")
    return problems


def hook_python() -> str | None:
    """O primeiro Python 3.11+ que o hook commit-msg acharia, na mesma ordem que ele tenta."""
    for candidate in (["python3"], ["python"], ["py", "-3"]):
        executable = shutil.which(candidate[0])
        if executable is None:
            continue
        try:
            completed = subprocess.run(
                [executable, *candidate[1:], "-c", "import sys; sys.exit(sys.version_info < (3, 11))"],
                capture_output=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if completed.returncode == 0:
            return " ".join(candidate)
    return None


def hook_report(report: Report, hook: Path, skill_dir: str) -> None:
    text = _read(hook)
    if text is None:
        report.todo("hook commit-msg ausente: `pre-commit install` ou `bootstrap.py install-hook`")
        return
    if text == hook_content(skill_dir):
        report.ok("hook commit-msg instalado neste checkout")
    elif HOOK_MARK in text:
        report.todo(
            "hook commit-msg desatualizado (de outra versão ou de outro caminho): `bootstrap.py install-hook` renova"
        )
    elif "github_issues.py" in text or "pre-commit" in text:
        report.ok("hook commit-msg instalado neste checkout (pre-commit ou de outra origem)")
        return
    else:
        report.todo(f"{hook} é de outra origem e não chama github_issues.py commit-msg")
        return
    found = hook_python()
    if found:
        report.ok(f"o hook commit-msg acha Python 3.11+ ({found})")
    else:
        report.error("nenhum python3, python ou `py -3` do PATH é 3.11+: o hook commit-msg recusa todo commit")


_CLAUDE_HOOK_PATH = re.compile(r"""(?:\$\{?CLAUDE_PROJECT_DIR\}?/)?([^\s"']*dev-workflow-hook\.mjs)""")


def claude_hooks_report(report: Report, root: Path, skill_dir: str) -> None:
    """Hooks do Claude Code: opcionais, mas se configurados precisam apontar para o skill e ter node."""
    expected = CLAUDE_HOOK if skill_dir == "." else f"{skill_dir}/{CLAUDE_HOOK}"
    configured = False
    for name in CLAUDE_SETTINGS:
        text = _read(root / name)
        if text is None:
            continue
        try:
            data = json.loads(text)
        except ValueError as exc:
            report.error(f"{name} não é JSON válido: {exc}")
            continue
        hooks = data.get("hooks") if isinstance(data, dict) else None
        commands = [
            str(hook.get("command", ""))
            for groups in (hooks.values() if isinstance(hooks, dict) else [])
            if isinstance(groups, list)
            for group in groups
            if isinstance(group, dict) and isinstance(group.get("hooks"), list)
            for hook in group["hooks"]
            if isinstance(hook, dict)
        ]
        paths = {match.group(1) for command in commands for match in _CLAUDE_HOOK_PATH.finditer(command)}
        configured = configured or bool(paths)
        for path in sorted(paths):
            if path != expected:
                report.error(f"{name}: hook do Claude Code aponta para {path}, mas o skill está em {expected}")
        if paths and not (root / expected).is_file():
            report.error(f"{name}: hook do Claude Code {expected} não existe")
        elif paths and expected in paths:
            report.ok(f"hooks do Claude Code configurados em {name}")
    if not configured:
        report.ok("hooks do Claude Code não configurados (opcionais)")
    elif shutil.which("node") is None:
        report.todo("hooks do Claude Code configurados, mas `node` não está no PATH: eles não rodam")


def doctor(_args: argparse.Namespace) -> int:
    root = find_root()
    git = Git(root)
    report = Report()
    print(f"dev-workflow em {root}")
    try:
        cfg = load(root)
    except ConfigError as exc:
        report.error(str(exc))
        return 1
    if cfg.path is None:
        report.error("sem .github/dev-workflow.toml: rode `bootstrap.py init`.")
    else:
        report.ok(f"configuração válida: {cfg.path.relative_to(root).as_posix()}")
    # Abaixo de 3.11 o bootstrap.py nem chega aqui: recusa antes de importar (tomllib).
    report.ok(f"Python {sys.version_info.major}.{sys.version_info.minor} rodando este comando (3.11+)")
    try:
        manifest = read_manifest(root)
    except ManifestError as exc:
        report.error(str(exc))
        manifest = None
    skill_dir = skill_dir_in(root)
    if skill_dir is None:
        skill_dir = manifest.skill_dir if manifest else VENDOR_PATH
        report.error(
            f"o skill está fora do repositório; o CI precisa dele versionado (bootstrap.py init copia para {skill_dir})."
        )
    else:
        report.ok(f"skill dev-workflow {skill_version()} versionado em {skill_dir}")
    if manifest is None:
        report.ok(f"sem {MANIFEST}: o próximo `update` o grava; até lá, personalizado é o que difere do modelo")
    elif manifest.skill_dir != skill_dir:
        report.error(f"{MANIFEST} registra o skill em {manifest.skill_dir}, mas ele está em {skill_dir}")
    elif skill_dir != "." and manifest.version != skill_version():
        report.todo(
            f"os arquivos gerados são da versão {manifest.version} e a cópia é a {skill_version()}: "
            "rode o `update` a partir do clone do skill"
        )
    else:
        report.ok(f"{MANIFEST}: versão {manifest.version}, {len(manifest.files)} arquivo(s) gerado(s)")

    values = template_values(root, skill_dir, cfg.default_branch, cfg, git)
    for name, content in planned_files(values, selftest=False).items():
        target = root / name
        optional = name.endswith("semver-analysis.yml")
        current = _read(target)
        if current is None:
            (report.ok if optional else report.todo)(
                f"{name} ausente" + (" (opcional)" if optional else ": rode `bootstrap.py init`")
            )
            continue
        problems = workflow_problems(name, current, cfg, skill_dir) if ".github/workflows/" in name else []
        for problem in problems:
            report.error(f"{name} não corresponde à configuração: {problem}")
        if ".github/workflows/" not in name or current == content:
            report.ok(name)
        elif manifest is not None and manifest.pristine(name, current):
            report.todo(
                f"{name} foi gerado pelo skill e não foi editado, mas não corresponde ao modelo desta versão com a "
                "configuração atual: regenere com o `update` a partir do clone do skill"
            )
        elif not problems:
            report.todo(f"{name} difere do modelo do skill (personalizado ou desatualizado)")
    template = root / ".github/pull_request_template.md"
    try:
        template_text = template.read_text(encoding="utf-8") if template.is_file() else None
    except UnicodeDecodeError:
        report.error(f"{template.relative_to(root).as_posix()} não está em UTF-8; salve o arquivo em UTF-8.")
        template_text = None
    if template_text is not None:
        present = sections(template_text)
        missing = [name for name in cfg.pr["required_sections"] if normalize_title(name) not in present]
        if missing:
            report.error(f"o modelo de PR não tem as seções exigidas em pr.required_sections: {', '.join(missing)}")

    hook_report(report, hook_path(git), skill_dir)
    claude_hooks_report(report, root, skill_dir)

    repo = Repo(cfg, git)
    if cfg.versioning_enabled:
        latest = repo.current("HEAD") if git.ok("rev-parse", "HEAD") else None
        current = latest[1] if latest else Version.parse(str(cfg.versioning["initial_version"]))
        problems = check_version_files(cfg, current)
        for problem in problems:
            report.error(problem)
        if not problems:
            report.ok(f"{len(cfg.versioning['files'])} entrada(s) de arquivo de versão coerentes com {current}")
        if latest is None:
            report.todo(
                f"sem tag de versão: crie a linha de base com `release.py baseline --push` ({cfg.tag_prefix}{current})"
            )
        else:
            report.ok(f"última tag de versão: {latest[0]}")

    repository = current_repository(git)
    github = GitHub(repository)
    if not github.enabled:
        report.todo("sem acesso ao GitHub (gh ou GITHUB_REPOSITORY): labels e permissões não conferidos")
    else:
        completed = run_gh(["label", "list", "--repo", str(repository), "--limit", "300", "--json", "name"])
        if completed.returncode != 0:
            report.todo(f"não consegui listar labels: {completed.stderr.strip() or 'gh indisponível'}")
        else:
            existing = {item["name"] for item in json.loads(completed.stdout or "[]")}
            missing = [name for name in cfg.all_labels() if name not in existing]
            if missing:
                report.todo(f"labels ausentes: {', '.join(missing)} (rode `github_issues.py sync-labels`)")
            else:
                report.ok(f"{len(cfg.all_labels())} labels do fluxo existem no GitHub")
        permissions = github.api("actions/permissions/workflow") if cfg.release["mode"] == "pull-request" else None
        if permissions and not permissions.get("can_approve_pull_request_reviews"):
            report.todo(
                'modo pull-request: habilite "Allow GitHub Actions to create and approve pull requests" nas configurações do Actions'
            )
    print(
        "\nPassos de quem é dono, que este comando não consegue conferir: check obrigatório na proteção de branch, "
        f"segredos opcionais (RELEASE_TOKEN, ANTHROPIC_API_KEY). Veja {skill_dir}/references/installation.md."
    )
    print(f"\n{report.errors} erro(s), {report.pending} pendência(s).")
    return 1 if report.errors else 0


def main(argv: Sequence[str] | None = None) -> int:
    """Códigos de saída: 0 ok, 1 falha (``doctor`` com erro ou erro de operação), 2 uso."""
    utf8_streams()
    try:
        return _main(argv)
    except (CommandError, ConfigError, ReleaseError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    except UnicodeDecodeError as exc:
        print(f"ERRO: um arquivo lido não está em UTF-8 ({exc.reason}); salve-o em UTF-8.", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bootstrap.py", description="Instala e confere o skill dev-workflow.")
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("init")
    command.add_argument(
        "--skill-dir", default="", help=f"onde copiar o skill, relativo à raiz (padrão: {VENDOR_PATH})"
    )
    command.add_argument("--default-branch", default="")
    command.add_argument("--initial-version", default="")
    command.add_argument("--force", action="store_true", help="troca arquivos que já existem")
    command.add_argument("--no-labels", action="store_true")
    command.add_argument("--selftest", action="store_true", help="instala também o workflow de autoteste do skill")
    command.add_argument("--dry-run", action="store_true")
    command = sub.add_parser("update", help="troca a cópia do skill no projeto por esta versão")
    command.add_argument(
        "--force", action="store_true", help="volta a uma versão anterior e troca modelos personalizados"
    )
    command.add_argument("--dry-run", action="store_true")
    command = sub.add_parser("uninstall", help="remove o que o fluxo gerou e não foi personalizado")
    command.add_argument("--yes", action="store_true", help="remove de fato; sem ele, só lista")
    command = sub.add_parser("install-hook")
    command.add_argument("--force", action="store_true")
    sub.add_parser("doctor")
    sub.add_parser("version", help="mostra a versão do skill")
    args = parser.parse_args(argv)
    if args.command == "init":
        return init(args)
    if args.command == "update":
        return update(args)
    if args.command == "uninstall":
        return uninstall(args)
    if args.command == "version":
        print(skill_version())
        return 0
    if args.command == "install-hook":
        root = find_root()
        skill_dir = skill_dir_in(root)
        if skill_dir is None:
            print("ERRO: o skill está fora deste repositório; rode `bootstrap.py init` primeiro.", file=sys.stderr)
            return 1
        print(install_hook(root, skill_dir, force=args.force))
        return 0
    return doctor(args)
