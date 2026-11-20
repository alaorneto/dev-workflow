"""Configuração do fluxo por projeto (``.github/dev-workflow.toml``).

Tudo que é específico de um projeto (tipos de issue, seções, arquivos de versão, superfícies
públicas) vive nesse arquivo. Sem arquivo, valem os padrões abaixo, que bastam para o hook
``commit-msg``. As tabelas do arquivo se sobrepõem aos padrões chave a chave; ``types`` e as
listas substituem o padrão por inteiro, para que um projeto possa ter menos tipos ou seções.

Os padrões têm duas partes: a base neutra (``BASE``) e o que depende do idioma (``language``,
``pt-BR`` quando a chave falta), que vem de ``locales/``. O idioma é lido dos dados crus antes
da composição, porque é ele que decide quais padrões compor.
"""

from __future__ import annotations

import copy
import fnmatch
import os
import re
import tomllib
from pathlib import Path
from typing import Any

from . import i18n
from .semver import CHANNEL_NAME, LEVELS, PEP440_CHANNELS, ZERO_MAJOR_POLICIES, Version, pep440_channel

CONFIG_ENV = "DEV_WORKFLOW_CONFIG"
CONFIG_CANDIDATES = (".github/dev-workflow.toml", "dev-workflow.toml", ".dev-workflow.toml")
SURFACE_ACTIONS = (*LEVELS, "review")
SEVERITIES = ("error", "warning", "off")
RELEASE_MODES = ("direct", "pull-request")

# O que não depende do idioma. Nomes de seção, marcadores, títulos do changelog e descrições dos
# tipos vêm do idioma (``locales/``) e são compostos sobre esta base em ``defaults_for``.
BASE: dict[str, Any] = {
    "schema": 1,
    "repository": {"default_branch": "main", "release_branches": ["main", "release/*"]},
    "types": {
        "bug": {"color": "d73a4a", "prefixes": ["fix"], "level": "patch", "section": "fixes"},
        "feature": {"color": "1d76db", "prefixes": ["feat"], "level": "minor", "section": "features"},
        "enhancement": {"color": "a2eeef", "prefixes": ["feat", "perf"], "level": "minor", "section": "improvements"},
        "documentation": {"color": "0075ca", "prefixes": ["docs"], "level": "none", "section": "docs"},
        "refactor": {"color": "fbca04", "prefixes": ["refactor"], "level": "none", "section": "maintenance"},
        "test": {"color": "bfd4f2", "prefixes": ["test"], "level": "none", "section": "maintenance"},
        "ci": {"color": "5319e7", "prefixes": ["ci"], "level": "none", "section": "maintenance"},
        "chore": {"color": "c5def5", "prefixes": ["chore", "build"], "level": "none", "section": "maintenance"},
    },
    "labels": {
        "epic": "epic",
        "release": "release",
        "breaking": "breaking-change",
        "override_prefix": "semver:",
        "extra": {},
    },
    "commits": {"levels": {"feat": "minor", "fix": "patch", "perf": "patch"}},
    "issues": {},
    "pr": {
        "title_pattern": r"^(feat|fix|perf|docs|refactor|test|ci|chore|build|revert)(\([\w./ -]+\))?!?: \S.*",
        "exempt_authors": ["dependabot[bot]"],
        "severity": {
            "sections": "error",
            "title": "error",
            "unchecked_criteria": "warning",
            "issue_sections": "warning",
            "type_mismatch": "warning",
        },
    },
    "versioning": {
        "enabled": True,
        "tag_prefix": "v",
        "initial_version": "0.1.0",
        "zero_major": "breaking-is-minor",
        "require_analysis": False,
        "trusted_bots": ["github-actions[bot]", "claude[bot]"],
        # Canais de pré-release aceitos, do menos ao mais maduro: é a ordem de precedência do SemVer.
        "prerelease": {"channels": ["alpha", "beta", "rc"]},
        "files": [],
        "public_surfaces": [],
        "floors": [],
    },
    "changelog": {"path": "CHANGELOG.md", "title": "# Changelog", "prereleases": False, "hide": []},
    "release": {
        "mode": "direct",
        "commit_message": "chore(release): {tag}",
        "pr_branch": "release/next",
        "mark": ["comment", "milestone"],
        "dispatch_workflow": "",
    },
}


def _overlay(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """``extra`` sobre ``base``, tabela a tabela; listas e valores simples substituem."""
    result = copy.deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _overlay(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def defaults_for(language: str) -> dict[str, Any]:
    """Padrões completos de um idioma: a base neutra com o que o idioma define."""
    return _overlay(BASE, i18n.defaults(language))


DEFAULTS: dict[str, Any] = defaults_for(i18n.DEFAULT_LANGUAGE)

BREAKING_SECTION = "breaking"
FALLBACK_SECTION = "maintenance"


class ConfigError(ValueError):
    """Configuração inválida; a mensagem aponta a chave."""


def _merge(base: dict[str, Any], override: dict[str, Any], path: str = "") -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        where = f"{path}.{key}" if path else key
        replace_whole = where in ("types", "labels.extra", "issues.sections", "commits.levels")
        if isinstance(value, dict) and isinstance(result.get(key), dict) and not replace_whole:
            result[key] = _merge(result[key], value, where)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _fail(key: str, message: str) -> None:
    raise ConfigError(f"dev-workflow.toml: `{key}` {message}")


class Config:
    """Acesso tipado ao dicionário validado."""

    def __init__(self, data: dict[str, Any] | None = None, *, path: Path | None = None, root: Path | None = None):
        raw = dict(data or {})
        language = i18n.normalize(raw.get("language", i18n.DEFAULT_LANGUAGE))
        if language is None:
            _fail("language", i18n.t("config.language.unknown", accepted=", ".join(i18n.LANGUAGES)))
        self.language: str = str(language)
        if "language" in raw:
            raw["language"] = self.language
        self.data = _merge(defaults_for(self.language), raw)
        self.path = path
        self.root = root or Path.cwd()
        self._validate()

    def t(self, key: str, /, **values: Any) -> str:
        """Mensagem do catálogo no idioma do projeto."""
        return i18n.translate(self.language, key, **values)

    # --- validação -------------------------------------------------------------------------

    def _validate(self) -> None:
        d = self.data
        if d.get("schema") != 1:
            _fail("schema", "deve ser 1.")
        if not isinstance(d["types"], dict) or not d["types"]:
            _fail("types", "precisa de ao menos um tipo.")
        section_ids = {section.get("id") for section in d["changelog"]["sections"]}
        for needed in (BREAKING_SECTION, FALLBACK_SECTION):
            if needed not in section_ids:
                _fail("changelog.sections", f"precisa de uma seção com id `{needed}`.")
        for name, spec in d["types"].items():
            if spec.get("level", "none") not in LEVELS:
                _fail(f"types.{name}.level", f"deve ser um de {', '.join(LEVELS)}.")
            if not spec.get("prefixes"):
                _fail(f"types.{name}.prefixes", "precisa de ao menos um prefixo de commit e branch.")
            if spec.get("section", FALLBACK_SECTION) not in section_ids:
                _fail(f"types.{name}.section", "não corresponde a um id de `changelog.sections`.")
        for kind, level in d["commits"]["levels"].items():
            if level not in LEVELS:
                _fail(f"commits.levels.{kind}", f"deve ser um de {', '.join(LEVELS)}.")
        for key, value in d["pr"]["severity"].items():
            if value not in SEVERITIES:
                _fail(f"pr.severity.{key}", f"deve ser um de {', '.join(SEVERITIES)}.")
        try:
            re.compile(d["pr"]["title_pattern"])
        except re.error as exc:
            _fail("pr.title_pattern", f"não é uma expressão regular válida: {exc}.")
        v = d["versioning"]
        if v["zero_major"] not in ZERO_MAJOR_POLICIES:
            _fail("versioning.zero_major", f"deve ser um de {', '.join(ZERO_MAJOR_POLICIES)}.")
        if Version.try_parse(str(v["initial_version"])) is None:
            _fail("versioning.initial_version", "não é uma versão SemVer.")
        for index, entry in enumerate(v["files"]):
            key = f"versioning.files[{index}]"
            if not entry.get("path"):
                _fail(f"{key}.path", "é obrigatório.")
            if bool(entry.get("search")) == bool(entry.get("regex")):
                _fail(key, "precisa de exatamente um entre `search` e `regex`.")
            if entry.get("regex") and "replace" not in entry:
                _fail(f"{key}.replace", "é obrigatório com `regex`.")
            if not isinstance(entry.get("count", 1), int) or entry.get("count", 1) < 1:
                _fail(f"{key}.count", "deve ser um inteiro maior que zero.")
        for index, entry in enumerate(v["public_surfaces"]):
            key = f"versioning.public_surfaces[{index}]"
            if not entry.get("globs"):
                _fail(f"{key}.globs", "precisa de ao menos um padrão.")
            for event in ("on_add", "on_modify", "on_remove"):
                if entry.get(event, "review") not in SURFACE_ACTIONS:
                    _fail(f"{key}.{event}", f"deve ser um de {', '.join(SURFACE_ACTIONS)}.")
        for index, entry in enumerate(v["floors"]):
            key = f"versioning.floors[{index}]"
            if not entry.get("globs"):
                _fail(f"{key}.globs", "precisa de ao menos um padrão.")
            try:
                if re.compile(entry.get("regex", "")).groups < 1:
                    _fail(f"{key}.regex", "precisa de um grupo de captura com a versão.")
            except re.error as exc:
                _fail(f"{key}.regex", f"não é uma expressão regular válida: {exc}.")
        self._validate_channels()
        r = d["release"]
        if r["mode"] not in RELEASE_MODES:
            _fail("release.mode", f"deve ser um de {', '.join(RELEASE_MODES)}.")
        if "{tag}" not in r["commit_message"]:
            _fail("release.commit_message", "precisa conter `{tag}`.")
        for item in r["mark"]:
            if item not in ("comment", "milestone"):
                _fail("release.mark", "aceita `comment` e `milestone`.")

    def _validate_channels(self) -> None:
        """Canais de pré-release: lista fechada, em minúsculas, na ordem de precedência do SemVer.

        O SemVer compara identificadores alfanuméricos em ordem ASCII, e é essa a ordem que os
        gerenciadores de pacote aplicam: uma lista fora dela prometeria uma maturidade que os
        números não cumprem (``snapshot`` fica acima de ``rc``).
        """
        v, key = self.data["versioning"], "versioning.prerelease.channels"
        if not isinstance(v.get("prerelease"), dict):
            _fail("versioning.prerelease", self.t("config.prerelease.table"))
        channels = v["prerelease"].get("channels")
        if not isinstance(channels, list) or not all(isinstance(item, str) for item in channels):
            _fail(key, self.t("config.channels.type"))
        for channel in channels:
            if not CHANNEL_NAME.fullmatch(channel):
                _fail(key, self.t("config.channels.name", channel=channel))
        for earlier, later in zip(channels, channels[1:], strict=False):
            if not earlier < later:
                _fail(key, self.t("config.channels.order", earlier=earlier, later=later))
        fields = ("search", "regex", "replace")
        if any("_pep440}" in str(entry.get(field, "")) for entry in v["files"] for field in fields):
            forms: dict[str, str] = {}
            for channel in channels:
                form = pep440_channel(channel)
                if form is None:
                    accepted = ", ".join(sorted(PEP440_CHANNELS))
                    _fail(key, self.t("config.channels.pep440", channel=channel, accepted=accepted))
                elif form in forms:
                    _fail(key, self.t("config.channels.pep440_clash", first=forms[form], second=channel, form=form))
                else:
                    forms[form] = channel

    # --- tipos e labels --------------------------------------------------------------------

    @property
    def types(self) -> dict[str, dict[str, Any]]:
        return self.data["types"]

    @property
    def type_labels(self) -> list[str]:
        return list(self.types)

    def label(self, name: str) -> str:
        return str(self.data["labels"][name])

    def type_level(self, type_label: str) -> str:
        return str(self.types[type_label].get("level", "none"))

    def type_section(self, type_label: str) -> str:
        return str(self.types[type_label].get("section", FALLBACK_SECTION))

    def type_for_prefix(self, prefix: str) -> str | None:
        """Primeiro tipo que aceita o prefixo de commit (``fix`` → ``bug``)."""
        return next((name for name, spec in self.types.items() if prefix in spec["prefixes"]), None)

    def all_labels(self) -> dict[str, tuple[str, str]]:
        """Labels que o fluxo usa: ``{nome: (cor, descrição)}``."""
        labels = {name: (spec.get("color", "ededed"), spec.get("description", "")) for name, spec in self.types.items()}
        labels[self.label("epic")] = ("3e4b9e", self.t("label.epic"))
        for name, spec in self.data["labels"]["extra"].items():
            labels[name] = (spec.get("color", "ededed"), spec.get("description", ""))
        if self.versioning_enabled:
            labels[self.label("release")] = ("0e8a16", self.t("label.release"))
            labels[self.label("breaking")] = ("b60205", self.t("label.breaking"))
            meanings = (
                ("major", self.t("label.override.major")),
                ("minor", self.t("label.override.minor")),
                ("patch", self.t("label.override.patch")),
            )
            for level, meaning in meanings:
                labels[self.override_label(level)] = ("d4c5f9", self.t("label.override", level=level, meaning=meaning))
        return labels

    def override_label(self, level: str) -> str:
        return f"{self.label('override_prefix')}{level}"

    # --- demais seções ---------------------------------------------------------------------

    @property
    def default_branch(self) -> str:
        return str(self.data["repository"]["default_branch"])

    def is_release_branch(self, branch: str) -> bool:
        return any(fnmatch.fnmatchcase(branch, pattern) for pattern in self.data["repository"]["release_branches"])

    def is_release_pull(self, pull: dict[str, Any] | None) -> bool:
        """O PR é o de release da automação: sai de ``release.pr_branch`` deste repositório.

        O nome da branch não basta: um fork pode ter uma branch igual. Num fork apagado a API
        devolve ``head.repo: null``, e o PR também não conta.
        """
        head, base = (pull or {}).get("head") or {}, (pull or {}).get("base") or {}
        source = str((head.get("repo") or {}).get("full_name") or "").lower()
        target = str((base.get("repo") or {}).get("full_name") or "").lower()
        return str(head.get("ref", "")) == self.release["pr_branch"] and bool(source) and source == target

    @property
    def issues(self) -> dict[str, Any]:
        return self.data["issues"]

    def issue_sections(self, type_label: str | None) -> list[str]:
        sections = self.issues["sections"]
        return list(sections.get(type_label or "", sections.get("default", [])))

    @property
    def pr(self) -> dict[str, Any]:
        return self.data["pr"]

    def severity(self, rule: str) -> str:
        return str(self.pr["severity"].get(rule, "error"))

    @property
    def versioning(self) -> dict[str, Any]:
        return self.data["versioning"]

    @property
    def versioning_enabled(self) -> bool:
        return bool(self.versioning["enabled"])

    @property
    def tag_prefix(self) -> str:
        return str(self.versioning["tag_prefix"])

    @property
    def prerelease_channels(self) -> list[str]:
        """Canais de pré-release aceitos, do menos ao mais maduro."""
        return list(self.versioning["prerelease"]["channels"])

    @property
    def changelog(self) -> dict[str, Any]:
        return self.data["changelog"]

    @property
    def release(self) -> dict[str, Any]:
        return self.data["release"]

    def release_subject(self, tag: str) -> str:
        return str(self.release["commit_message"]).replace("{tag}", tag)

    def release_subject_pattern(self) -> re.Pattern[str]:
        """Reconhece o commit de release, inclusive com o sufixo ``(#N)`` de um squash."""
        template = re.escape(str(self.release["commit_message"])).replace(re.escape("{tag}"), r"(?P<tag>\S+)")
        return re.compile(rf"^{template}(?: \(#\d+\))?$")


def find_root(start: Path | None = None) -> Path:
    """Raiz do repositório git que contém ``start``; sem git, o próprio diretório."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def find_config(root: Path) -> Path | None:
    explicit = os.environ.get(CONFIG_ENV)
    if explicit:
        return Path(explicit)
    return next((root / name for name in CONFIG_CANDIDATES if (root / name).is_file()), None)


def load(root: Path | None = None) -> Config:
    root = root or find_root()
    path = find_config(root)
    if path is None:
        cfg = Config(root=root)
        i18n.activate(cfg.language)
        return cfg
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"{path}: {exc}") from exc
    cfg = Config(data, path=path, root=root)
    i18n.activate(cfg.language)  # mensagens de quem não recebe a configuração
    return cfg
