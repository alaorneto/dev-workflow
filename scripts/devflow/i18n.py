"""Idioma do fluxo: catálogo de mensagens e padrões de configuração que dependem dele.

Cada idioma é um módulo de ``locales/`` com dois dicionários: ``MESSAGES`` (os textos que as
ferramentas escrevem) e ``DEFAULTS`` (os padrões de configuração que mudam com o idioma: nomes
de seção, marcadores, títulos do changelog, descrições dos tipos). São dicionários Python de
propósito: gettext exigiria arquivos ``.mo`` compilados e TOML não quebra linhas longas.

Uma chave que falta no idioma cai para o pt-BR e, se também faltar lá, para a própria chave:
uma tradução incompleta nunca derruba um comando.
"""

from __future__ import annotations

import copy
import functools
import importlib
import string
from types import ModuleType
from typing import Any

DEFAULT_LANGUAGE = "pt-BR"
LANGUAGES = {"pt-BR": "pt_br", "en": "en"}  # idioma → módulo de locales/
_active = DEFAULT_LANGUAGE


def normalize(value: Any) -> str | None:
    """``pt-br``, ``pt_BR`` e ``PT-BR`` são ``pt-BR``; ``None`` para o que não é um idioma aceito."""
    if not isinstance(value, str):
        return None
    wanted = value.strip().replace("_", "-").casefold()
    return next((name for name in LANGUAGES if name.casefold() == wanted), None)


@functools.cache
def _locale(language: str) -> ModuleType:
    return importlib.import_module(f".locales.{LANGUAGES[language]}", __package__)


def messages(language: str) -> dict[str, str]:
    return _locale(language).MESSAGES


def defaults(language: str) -> dict[str, Any]:
    """Cópia dos padrões de configuração do idioma."""
    return copy.deepcopy(_locale(language).DEFAULTS)


class _Keep(dict):
    """Marcador sem valor continua no texto, em vez de derrubar a formatação."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def translate(language: str, key: str, /, **values: Any) -> str:
    """O texto de ``key`` em ``language``, com os marcadores ``{nome}`` preenchidos."""
    template = None
    for candidate in (language, DEFAULT_LANGUAGE):
        if candidate in LANGUAGES:
            template = messages(candidate).get(key)
        if template is not None:
            break
    if template is None:
        return key
    try:
        return string.Formatter().vformat(template, (), _Keep(values))
    except (ValueError, IndexError, KeyError, AttributeError):
        return template


def activate(language: str) -> None:
    """Idioma das mensagens de quem não tem uma ``Config`` à mão. ``config.load`` chama isto."""
    global _active  # noqa: PLW0603
    _active = language if language in LANGUAGES else DEFAULT_LANGUAGE


def active() -> str:
    return _active


def t(key: str, /, **values: Any) -> str:
    """``translate`` no idioma ativo."""
    return translate(_active, key, **values)
