"""Regras puras: SemVer, leitura de texto, configuração, arquivos de versão e changelog."""

import ast
import json
import os
import string
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support  # noqa: F401  (põe scripts/ no sys.path antes de importar devflow)
from devflow import i18n
from devflow.config import Config, ConfigError, load
from devflow.plan import _glob_match, surface_hits, validate_analysis
from devflow.release import ReleaseError, fit_notes, rewrite, truncate_lines, update_changelog
from devflow.semver import (
    Version,
    cycle_floor,
    effective_level,
    level_between,
    max_level,
    next_prerelease,
    next_version,
    not_surpassed,
)
from devflow.text import (
    breaking_notes,
    checkboxes,
    marked_value,
    meaningful,
    parse_conventional,
    referenced_issues,
    sections,
    slugify,
)

V = Version.parse
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class SemverTest(unittest.TestCase):
    def test_parse_and_print_round_trip(self):
        for text in ("0.5.0", "1.2.3-rc.1", "1.0.0-alpha.beta+build.5", "10.20.30"):
            self.assertEqual(str(V(text)), text)
        for text in ("1.2", "v1.2.3", "01.2.3", "1.2.3-", "1.2.3-01", "abc", ""):
            self.assertIsNone(Version.try_parse(text), text)

    def test_precedence_follows_the_specification(self):
        ordered = [
            "1.0.0-alpha",
            "1.0.0-alpha.1",
            "1.0.0-alpha.beta",
            "1.0.0-beta",
            "1.0.0-beta.2",
            "1.0.0-beta.11",
            "1.0.0-rc.1",
            "1.0.0",
            "1.0.1",
            "1.1.0",
            "2.0.0",
        ]
        self.assertEqual([str(v) for v in sorted(map(V, reversed(ordered)), key=Version.key)], ordered)
        self.assertEqual(V("1.0.0+a").key(), V("1.0.0+b").key())

    def test_next_number_for_each_level(self):
        self.assertEqual(str(next_version(V("1.2.3"), "patch")), "1.2.4")
        self.assertEqual(str(next_version(V("1.2.3"), "minor")), "1.3.0")
        self.assertEqual(str(next_version(V("1.2.3"), "major")), "2.0.0")
        self.assertEqual(str(next_version(V("1.3.0-rc.2"), "patch")), "1.3.1")
        with self.assertRaises(ValueError):
            next_version(V("1.2.3"), "none")

    def test_zero_major_keeps_breaking_changes_in_the_minor(self):
        self.assertEqual(effective_level(V("0.5.0"), "major"), "minor")
        self.assertEqual(str(next_version(V("0.5.2"), "major")), "0.6.0")
        self.assertEqual(str(next_version(V("0.5.2"), "minor")), "0.6.0")
        self.assertEqual(str(next_version(V("0.5.2"), "patch")), "0.5.3")
        self.assertEqual(str(next_version(V("0.5.2"), "major", "strict")), "1.0.0")
        self.assertEqual(effective_level(V("1.0.0"), "major"), "major")

    def test_the_highest_level_wins(self):
        self.assertEqual(max_level(["none", "patch", "minor", "patch"]), "minor")
        self.assertEqual(max_level([]), "none")

    def test_prereleases_count_per_target_and_channel(self):
        existing = [V("1.3.0-rc.1"), V("1.3.0-rc.2"), V("1.3.0-beta.7"), V("1.4.0-rc.9")]
        self.assertEqual(str(next_prerelease(V("1.3.0"), "rc", existing)), "1.3.0-rc.3")
        self.assertEqual(str(next_prerelease(V("2.0.0"), "rc", existing)), "2.0.0-rc.1")
        with self.assertRaises(ValueError):
            next_prerelease(V("1.3.0"), "r c", [])
        allowed = ["alpha", "beta", "rc"]
        self.assertEqual(str(next_prerelease(V("1.3.0"), "beta", existing, allowed)), "1.3.0-beta.8")
        with self.assertRaises(ValueError) as raised:
            next_prerelease(V("1.3.0"), "nightly", existing, allowed)
        self.assertIn("alpha, beta, rc", str(raised.exception))

    def test_the_cycle_floor_is_the_highest_target_already_published_as_a_prerelease(self):
        self.assertIsNone(cycle_floor([]))
        self.assertEqual(str(cycle_floor(map(V, ["1.3.0-beta.2", "2.0.0-alpha.1", "1.3.0-rc.1"]))), "2.0.0")
        self.assertEqual(level_between(V("0.9.0"), V("1.0.0")), "major")
        self.assertEqual(level_between(V("1.2.0"), V("1.3.0")), "minor")
        self.assertEqual(level_between(V("1.2.0"), V("1.2.1")), "patch")

    def test_a_new_prerelease_must_come_after_every_one_of_the_same_target(self):
        cycle = [V("1.3.0-beta.1"), V("1.3.0-beta.2"), V("1.2.1-rc.4")]
        self.assertEqual(str(not_surpassed(V("1.3.0-alpha.1"), cycle)), "1.3.0-beta.2")
        self.assertEqual(str(not_surpassed(V("1.3.0-beta.2"), cycle)), "1.3.0-beta.2")
        for later in ("1.3.0-beta.3", "1.3.0-rc.1", "1.3.0"):
            self.assertIsNone(not_surpassed(V(later), cycle), later)
        # em outro alvo a numeração e o canal recomeçam: a precedência já é maior
        self.assertIsNone(not_surpassed(V("2.0.0-alpha.1"), cycle))
        self.assertIsNone(not_surpassed(V("1.3.0-alpha.1"), []))

    def test_pep440_form(self):
        self.assertEqual(V("1.3.0-rc.1").pep440(), "1.3.0rc1")
        self.assertEqual(V("1.3.0-alpha.2").pep440(), "1.3.0a2")
        self.assertEqual(V("1.3.0").pep440(), "1.3.0")
        self.assertEqual(V("1.3.0-nightly.5").pep440(), "1.3.0-nightly.5")


class TextTest(unittest.TestCase):
    def test_closing_keywords_are_told_apart_from_references(self):
        body = "Closes #1\nRefs #2\nfixes acme/demo#3\nPart of #4\nResolves other/repo#9"
        self.assertEqual(referenced_issues(body, "acme/demo"), [1, 2, 3, 4])
        self.assertEqual(referenced_issues(body, "acme/demo", closing_only=True), [1, 3])
        self.assertEqual(referenced_issues("feat: x (#7)", closing_only=True), [])

    def test_sections_accept_both_heading_levels_and_skip_code_fences(self):
        body = "## Resumo\ntexto\n```\n## falso\n```\n### Critérios de aceite\n- [x] a\n- [ ] b\n"
        found = sections(body)
        self.assertEqual(list(found), ["resumo", "critérios de aceite"])
        self.assertIn("## falso", found["resumo"])
        self.assertEqual(checkboxes(found["critérios de aceite"]), [(True, "a"), (False, "b")])

    def test_template_leftovers_are_not_content(self):
        self.assertEqual(meaningful("<!-- dica -->\n- \n-\n- [ ] \n_No response_\n"), "")
        self.assertEqual(meaningful("<!-- dica -->\n- `make test` — ok"), "- `make test` — ok")
        self.assertEqual(
            marked_value("- Motivo da sobreposição: só muda o padrão", "motivo da sobreposição"), "só muda o padrão"
        )
        self.assertEqual(marked_value("- Motivo da sobreposição:", "Motivo da sobreposição"), "")

    def test_conventional_commits_and_breaking_markers(self):
        parsed = parse_conventional("feat(api)!: drop v1")
        self.assertEqual(
            (parsed.type, parsed.scope, parsed.breaking, parsed.description), ("feat", "api", True, "drop v1")
        )
        self.assertIsNone(parse_conventional("Merge branch 'main'"))
        self.assertEqual(breaking_notes("fix: x\n\nBREAKING CHANGE: a virou b\nBREAKING-CHANGE: c"), ["a virou b", "c"])
        self.assertEqual(breaking_notes("<!-- BREAKING CHANGE: exemplo do modelo -->"), [])

    def test_slug(self):
        self.assertEqual(slugify("Corrigir a origem pública do e-mail!"), "corrigir-a-origem-publica-do-e-mail")
        self.assertLessEqual(len(slugify("x" * 200)), 40)
        self.assertEqual(slugify("???"), "trabalho")


class ConfigTest(unittest.TestCase):
    def test_defaults_are_valid_and_expose_the_labels(self):
        cfg = Config()
        self.assertEqual(cfg.type_for_prefix("fix"), "bug")
        self.assertEqual(cfg.type_level("feature"), "minor")
        for label in ("bug", "epic", "release", "breaking-change", "semver:major"):
            self.assertIn(label, cfg.all_labels())

    def test_project_values_override_key_by_key_but_types_replace_whole(self):
        cfg = Config({"versioning": {"tag_prefix": "rel-"}, "types": {"task": {"prefixes": ["task"]}}})
        self.assertEqual(cfg.tag_prefix, "rel-")
        self.assertEqual(cfg.versioning["zero_major"], "breaking-is-minor")
        self.assertEqual(cfg.type_labels, ["task"])
        self.assertNotIn("release", Config({"versioning": {"enabled": False}}).all_labels())
        self.assertNotIn("no-release", Config().all_labels())

    def test_invalid_values_name_the_key(self):
        cases = {
            "types.bug.level": {"types": {"bug": {"prefixes": ["fix"], "level": "huge"}}},
            "versioning.files[0]": {"versioning": {"files": [{"path": "a", "search": "x", "regex": "y"}]}},
            "versioning.files[0].replace": {"versioning": {"files": [{"path": "a", "regex": "y"}]}},
            "versioning.initial_version": {"versioning": {"initial_version": "1.0"}},
            "versioning.floors[0].regex": {"versioning": {"floors": [{"globs": ["*"], "regex": "nogroup"}]}},
            "release.mode": {"release": {"mode": "magic"}},
            "release.commit_message": {"release": {"commit_message": "release"}},
            "pr.severity.title": {"pr": {"severity": {"title": "fatal"}}},
            "schema": {"schema": 2},
        }
        for key, data in cases.items():
            with self.subTest(key), self.assertRaises(ConfigError) as raised:
                Config(data)
            self.assertIn(f"`{key}`", str(raised.exception))

    def test_prerelease_channels_are_a_closed_list_in_semver_order(self):
        key = "`versioning.prerelease.channels`"
        pep440 = {"files": [{"path": "pyproject.toml", "search": 'version = "{current_pep440}"'}]}

        def channels(names, **versioning):
            return Config({"versioning": {"prerelease": {"channels": names}, **versioning}})

        self.assertEqual(Config().prerelease_channels, ["alpha", "beta", "rc"])
        self.assertEqual(channels(["dev", "nightly", "rc"]).prerelease_channels, ["dev", "nightly", "rc"])
        self.assertEqual(channels([]).prerelease_channels, [])
        self.assertEqual(channels(["alpha", "beta", "preview"], **pep440).prerelease_channels[-1], "preview")
        refused = {
            "ordem trocada": (["beta", "alpha"], {}, "`alpha` não vem depois de `beta`"),
            "canal repetido": (["rc", "rc"], {}, "`rc` não vem depois de `rc`"),
            "snapshot acima de rc": (["alpha", "snapshot", "rc"], {}, "`rc` não vem depois de `snapshot`"),
            "maiúsculas": (["Alpha"], {}, "`Alpha`"),
            "começa por dígito": (["1rc"], {}, "`1rc`"),
            "não é lista": ("rc", {}, "lista de textos"),
            "sem forma PEP 440": (["alpha", "dev"], pep440, "`dev`, que não tem forma PEP 440"),
            "mesma forma PEP 440": (["a", "alpha"], pep440, "`a` e `alpha`"),
            "pre e rc": (["pre", "rc"], pep440, "(`rc`)"),
        }
        for name, (names, versioning, expected) in refused.items():
            with self.subTest(name), self.assertRaises(ConfigError) as raised:
                channels(names, **versioning)
            self.assertIn(key, str(raised.exception))
            self.assertIn(expected, str(raised.exception))
        with self.assertRaises(ConfigError) as raised:
            channels(["beta", "alpha"])
        self.assertIn("precedência do SemVer", str(raised.exception))  # a mensagem explica a ordem
        # sem arquivo em PEP 440 a forma não importa
        self.assertEqual(channels(["a", "alpha", "dev"]).prerelease_channels, ["a", "alpha", "dev"])
        with self.assertRaises(ConfigError) as raised:
            Config({"versioning": {"prerelease": "rc"}})
        self.assertIn("`versioning.prerelease`", str(raised.exception))

    def test_release_commit_is_recognised_with_and_without_squash_suffix(self):
        pattern = Config().release_subject_pattern()
        self.assertEqual(pattern.match("chore(release): v1.2.3")["tag"], "v1.2.3")
        self.assertEqual(pattern.match("chore(release): v1.2.3 (#45)")["tag"], "v1.2.3")
        self.assertIsNone(pattern.match('Revert "chore(release): v1.2.3"'))
        self.assertIsNone(pattern.match("chore(release): v1.2.3 and more"))


class VersionFilesTest(unittest.TestCase):
    def test_literal_search_replaces_the_current_version(self):
        entry = {"path": "p", "search": 'version = "{current}"'}
        self.assertEqual(
            rewrite('name = "x"\nversion = "1.2.0"\n', entry, V("1.2.0"), V("1.3.0")), 'name = "x"\nversion = "1.3.0"\n'
        )

    def test_the_occurrence_count_is_enforced(self):
        entry = {"path": "p", "search": 'version = "{current}"'}
        for text in ('version = "9.9.9"\n', 'version = "1.2.0"\nversion = "1.2.0"\n'):
            with self.assertRaises(ReleaseError):
                rewrite(text, entry, V("1.2.0"), V("1.3.0"))
        twice = {**entry, "count": 2}
        self.assertEqual(
            rewrite('version = "1.2.0"\nversion = "1.2.0"\n', twice, V("1.2.0"), V("1.3.0")).count("1.3.0"), 2
        )

    def test_regex_entries_and_derived_tokens(self):
        entry = {
            "path": "m",
            "regex": r'"core": ">=\d+\.\d+\.\d+,<\d+\.\d+\.\d+"',
            "replace": '"core": ">={new_major}.{new_minor}.0,<{new_next_minor}"',
        }
        text = '{"core": ">=0.5.0,<0.6.0"}'
        self.assertEqual(rewrite(text, entry, V("0.5.0"), V("0.5.1")), text)
        self.assertEqual(rewrite(text, entry, V("0.5.1"), V("0.6.0")), '{"core": ">=0.6.0,<0.7.0"}')
        pep = {"path": "p", "search": 'version = "{current_pep440}"'}
        self.assertEqual(rewrite('version = "1.3.0rc1"', pep, V("1.3.0-rc.1"), V("1.3.0")), 'version = "1.3.0"')

    def test_replacement_text_is_literal(self):
        entry = {"path": "p", "regex": r"VERSION=\S+", "replace": r"VERSION={new}\1"}
        self.assertEqual(rewrite("VERSION=1.0.0", entry, V("1.0.0"), V("1.0.1")), r"VERSION=1.0.1\1")


class ChangelogFileTest(unittest.TestCase):
    cfg = Config()

    def test_first_release_creates_the_file_with_its_header(self):
        text = update_changelog(None, "1.0.0", "## [1.0.0] — 2030-01-01", "### Correções\n\n- a", self.cfg)
        self.assertTrue(text.startswith("# Changelog\n\n"))
        self.assertTrue(text.endswith("## [1.0.0] — 2030-01-01\n\n### Correções\n\n- a\n"))

    def test_new_versions_go_on_top_and_rewriting_one_is_idempotent(self):
        first = update_changelog(None, "1.0.0", "## [1.0.0] — d", "- a", self.cfg)
        second = update_changelog(first, "1.1.0", "## [1.1.0](url) — d", "- b", self.cfg)
        self.assertLess(second.index("## [1.1.0]"), second.index("## [1.0.0]"))
        self.assertEqual(update_changelog(second, "1.1.0", "## [1.1.0](url) — d", "- b", self.cfg), second)
        replaced = update_changelog(second, "1.1.0", "## [1.1.0](url) — d", "- c", self.cfg)
        self.assertIn("- c", replaced)
        self.assertNotIn("- b", replaced)
        self.assertIn("- a", replaced)
        self.assertEqual(replaced.count("## ["), 2)

    def test_a_version_is_not_confused_with_one_that_starts_the_same(self):
        text = update_changelog(None, "1.1.10", "## [1.1.10] — d", "- ten", self.cfg)
        text = update_changelog(text, "1.1.1", "## [1.1.1] — d", "- one", self.cfg)
        self.assertIn("- ten", text)
        self.assertEqual(text.count("## ["), 2)


class NotesLimitTest(unittest.TestCase):
    def test_lines_are_cut_whole_and_the_note_counts_what_was_left_out(self):
        text = "### Correções\n\n" + "\n".join(f"- item {n}" for n in range(10))
        cut = truncate_lines(text, 60, "_e mais {omitted}_")
        self.assertLessEqual(len(cut), 60)
        kept = [line for line in cut.splitlines() if line.startswith("- ")]
        self.assertEqual(cut.splitlines()[-1], f"_e mais {10 - len(kept)}_")
        self.assertTrue(all(line in text.splitlines() for line in kept))
        self.assertEqual(truncate_lines(text, len(text), "_x_"), text)

    def test_notes_that_fit_are_untouched(self):
        notes = fit_notes("- a", "tabela", "curta", "extra", 1000, full_list="no `CHANGELOG.md`")
        self.assertEqual(notes, "- a\n\n### Por que este número\n\ntabela\n\nextra\n")
        self.assertEqual(fit_notes("- a", "t", "c", "", None, full_list="x"), "- a\n\n### Por que este número\n\nt\n")

    def test_the_table_goes_first_then_the_changelog_is_cut(self):
        changelog = "\n".join(f"- entrada {n}" for n in range(50))
        table = "| a |\n" * 200
        only_table = fit_notes(changelog, table, "curta", "registro", len(changelog) + 100, full_list="no x")
        self.assertIn(changelog, only_table)
        self.assertNotIn("| a |", only_table)
        self.assertNotIn("registro", only_table)
        self.assertTrue(only_table.endswith("### Por que este número\n\ncurta\n"))
        both = fit_notes(changelog, table, "curta", "", 200, full_list="no x")
        self.assertLessEqual(len(both), 200)
        self.assertIn("a lista completa está no x._", both)
        self.assertTrue(both.endswith("curta\n"))


class AnalysisFormatTest(unittest.TestCase):
    def test_level_is_recomputed_from_the_changes(self):
        data = validate_analysis(
            {
                "schema": 1,
                "level": "patch",
                "changes": [
                    {"pr": 3, "level": "minor", "summary": "x"},
                    {"commit": "abcdef1", "level": "major", "summary": "y"},
                ],
            }
        )
        self.assertEqual(data["level"], "major")
        self.assertTrue(data["changes"][1]["breaking"])

    def test_malformed_input_is_refused(self):
        for bad in (
            [],
            {"schema": 2, "changes": []},
            {"schema": 1, "changes": [{"level": "patch", "summary": "x"}]},
            {"schema": 1, "changes": [{"pr": True, "level": "patch", "summary": "x"}]},
            {"schema": 1, "changes": [{"pr": 1, "level": "patch", "summary": " "}]},
            {"schema": 1, "changes": [{"pr": 1, "level": "patch", "summary": "x", "evidence": "y"}]},
        ):
            with self.subTest(bad), self.assertRaises(ValueError):
                validate_analysis(bad)


class GlobTest(unittest.TestCase):
    """``*`` e ``?`` ficam num nível de diretório; só ``**`` cruza."""

    CASES = (
        ("scripts/*.py", "scripts/release.py", True),
        ("scripts/*.py", "scripts/devflow/semver.py", False),
        ("*.md", "README.md", True),
        ("*.md", "docs/a.md", False),
        ("**/*.md", "README.md", True),
        ("**/*.md", "docs/a/b.md", True),
        ("assets/**", "assets/workflows/release.yml", True),
        ("assets/**", "assets/x", True),
        ("assets/**", "assetsx/y", False),
        ("assets/**", "other/assets/x", False),
        ("src/**/api.py", "src/api.py", True),
        ("src/**/api.py", "src/a/b/api.py", True),
        ("src/**/api.py", "src/a/b/xapi.py", False),
        ("src/**/*.py", "src/x.py", True),
        ("src/**/*.py", "src/a/b/x.py", True),
        ("src/**/*.py", "lib/x.py", False),
        ("docs/**.md", "docs/a/b.md", True),
        ("api/v?/client.py", "api/v1/client.py", True),
        ("api/v?/client.py", "api/v//client.py", False),
        ("api/v[12]/*.py", "api/v2/a.py", True),
        ("api/v[12]/*.py", "api/v3/a.py", False),
        ("api/v[!12]/*.py", "api/v3/a.py", True),
        ("api/v[!12]/*.py", "api/v1/a.py", False),
        ("a.b/c+d.py", "a.b/c+d.py", True),
        ("a.b/c+d.py", "axb/c+d.py", False),
        ("VERSION", "VERSION", True),
        ("VERSION", "sub/VERSION", False),
        ("src/[x", "src/[x", True),
    )

    def test_a_single_star_stays_in_one_directory_and_a_double_star_crosses(self):
        for pattern, path, expected in self.CASES:
            with self.subTest(pattern=pattern, path=path):
                self.assertIs(_glob_match(path, [pattern]), expected)
        self.assertTrue(_glob_match("docs/a.md", ["*.txt", "**/*.md"]))
        self.assertFalse(_glob_match("docs/a.md", []))

    def test_public_surfaces_follow_the_same_rule(self):
        cfg = Config({"versioning": {"public_surfaces": [{"name": "Scripts", "globs": ["scripts/*.py"]}]}})
        events = [("modify", "scripts/release.py"), ("modify", "scripts/devflow/semver.py")]
        self.assertEqual([hit.path for hit in surface_hits(events, cfg)], ["scripts/release.py"])


def _placeholders(template):
    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


def _restricted(value, reference):
    """``value`` só com as chaves que ``reference`` tem, tabela a tabela."""
    if isinstance(value, dict) and isinstance(reference, dict):
        return {key: _restricted(value[key], reference[key]) for key in reference if key in value}
    return value


def _shape(value):
    """A forma de um valor de configuração: as chaves de cada tabela e o tamanho de cada lista."""
    if isinstance(value, dict):
        return {key: _shape(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_shape(item) if isinstance(item, dict) else "" for item in value]
    return ""


def _message_calls():
    """``(arquivo, linha, chave)`` de cada chamada ao catálogo e as chamadas sem chave literal."""
    literal, dynamic = [], []
    for path in sorted((support.SCRIPTS / "devflow").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        # As próprias funções ``t`` repassam a chave que receberam: não são uso do catálogo.
        forwarding = {
            id(call)
            for function in ast.walk(tree)
            if isinstance(function, ast.FunctionDef) and function.name == "t"
            for call in ast.walk(function)
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or id(node) in forwarding:
                continue
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name not in ("t", "translate"):
                continue
            arguments = node.args[1:] if name == "translate" else node.args
            key = arguments[0] if arguments else None
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                literal.append((path.name, node.lineno, key.value))
            else:
                dynamic.append(f"{path.name}:{node.lineno}")
    return literal, dynamic


class LanguageTest(unittest.TestCase):
    """Idioma: padrões por idioma, catálogo de mensagens e queda para o pt-BR."""

    def test_without_the_key_the_configuration_is_exactly_the_previous_one(self):
        golden = json.loads((FIXTURES / "config-defaults-pt-br.json").read_text(encoding="utf-8"))
        labels = json.loads((FIXTURES / "labels-pt-br.json").read_text(encoding="utf-8"))
        cfg = Config()
        self.assertEqual(cfg.language, "pt-BR")
        # O retrato é de antes da chave `language`: tudo que ele tem continua com o mesmo valor.
        # Chaves criadas depois ficam de fora da comparação, mas não podem mudar as antigas.
        self.assertEqual(_restricted(cfg.data, golden), golden)
        self.assertNotIn("language", cfg.data)
        self.assertEqual(list(cfg.types), list(golden["types"]))
        current = {name: list(value) for name, value in cfg.all_labels().items()}
        self.assertEqual({name: current.get(name) for name in labels}, labels)
        explicit = Config({"language": "pt_br"})
        self.assertEqual(explicit.data["language"], "pt-BR")
        self.assertEqual({key: value for key, value in explicit.data.items() if key != "language"}, cfg.data)

    def test_english_changes_what_depends_on_the_language_and_nothing_else(self):
        en, pt = Config({"language": "en"}), Config()
        self.assertEqual(en.pr["required_sections"], ["Issues", "Summary", "Tests run", "Documentation", "Version"])
        self.assertEqual(en.pr["override_reason_marker"], "Override reason")
        self.assertEqual((en.issues["items_section"], en.issues["depends_marker"]), ("Items", "depends on"))
        self.assertEqual(en.issue_sections("bug")[:3], ["Observed behavior", "Expected behavior", "Steps to reproduce"])
        self.assertEqual([item["title"] for item in en.changelog["sections"]][:2], ["⚠ Breaking changes", "Features"])
        self.assertEqual(en.types["bug"]["description"], "Incorrect behavior or regression")
        self.assertIn("Overrides the computed level: major", en.all_labels()["semver:major"][1])
        for key in ("repository", "labels", "commits", "versioning", "release"):
            self.assertEqual(en.data[key], pt.data[key], key)
        self.assertEqual(_shape(en.data), {**_shape(pt.data), "language": ""})
        self.assertEqual(
            [item["id"] for item in en.changelog["sections"]], [item["id"] for item in pt.changelog["sections"]]
        )
        self.assertEqual(sorted(en.all_labels()), sorted(pt.all_labels()))
        custom = Config({"language": "en", "pr": {"version_section": "Release"}})
        self.assertEqual((custom.pr["version_section"], custom.pr["tests_section"]), ("Release", "Tests run"))

    def test_an_unknown_language_is_refused_with_the_key(self):
        for value in ("fr", "", 3):
            with self.subTest(value), self.assertRaises(ConfigError) as raised:
                Config({"language": value})
            self.assertIn("`language`", str(raised.exception))
            self.assertIn("pt-BR, en", str(raised.exception))

    def test_a_missing_message_falls_back_and_never_raises(self):
        portuguese = i18n.messages("pt-BR")["label.epic"]
        with mock.patch.dict(i18n.messages("en")) as english:
            del english["label.epic"]
            self.assertEqual(i18n.translate("en", "label.epic"), portuguese)
        self.assertEqual(i18n.translate("xx", "label.epic"), portuguese)
        self.assertEqual(i18n.translate("en", "no.such.key", value=1), "no.such.key")
        self.assertEqual(
            i18n.translate("en", "label.override", level="major"), "Overrides the computed level: major ({meaning})"
        )
        with mock.patch.dict(i18n.messages("en"), {"label.epic": "broken {"}):
            self.assertEqual(i18n.translate("en", "label.epic"), "broken {")

    def test_load_sets_the_language_of_the_messages(self):
        self.addCleanup(i18n.activate, i18n.active())
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "dev-workflow.toml").write_text('schema = 1\nlanguage = "en"\n', encoding="utf-8")
            with mock.patch.dict("os.environ"):
                os.environ.pop("DEV_WORKFLOW_CONFIG", None)
                cfg = load(Path(folder))
            self.assertEqual((cfg.language, i18n.active()), ("en", "en"))
            self.assertEqual(i18n.t("label.epic"), cfg.t("label.epic"))
            (Path(folder) / "dev-workflow.toml").write_text("schema = 1\n", encoding="utf-8")
            with mock.patch.dict("os.environ"):
                os.environ.pop("DEV_WORKFLOW_CONFIG", None)
                load(Path(folder))
            self.assertEqual(i18n.active(), "pt-BR")

    def test_both_catalogs_have_the_same_keys_and_placeholders(self):
        portuguese, english = i18n.messages("pt-BR"), i18n.messages("en")
        self.assertEqual(sorted(portuguese), sorted(english))
        for key, template in portuguese.items():
            with self.subTest(key):
                self.assertEqual(_placeholders(template), _placeholders(english[key]))

    def test_both_languages_define_the_same_defaults(self):
        self.assertEqual(_shape(i18n.defaults("pt-BR")), _shape(i18n.defaults("en")))
        self.assertIsNot(i18n.defaults("en")["pr"], i18n.defaults("en")["pr"])  # cópia: ninguém altera o idioma

    def test_every_message_key_used_in_the_code_exists_and_none_is_left_over(self):
        literal, dynamic = _message_calls()
        self.assertEqual(dynamic, [], "a chave do catálogo tem de ser um texto literal na chamada")
        catalog = i18n.messages("pt-BR")
        self.assertEqual([call for call in literal if call[2] not in catalog], [])
        self.assertEqual(sorted(set(catalog) - {key for _, _, key in literal}), [])

    def test_label_descriptions_fit_the_github_limit(self):
        for language in i18n.LANGUAGES:
            for name, (_color, description) in Config({"language": language}).all_labels().items():
                with self.subTest(language=language, label=name):
                    self.assertLessEqual(len(description), 100)


if __name__ == "__main__":
    unittest.main()
