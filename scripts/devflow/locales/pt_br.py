"""Português do Brasil: o idioma de referência. Toda chave de mensagem existe aqui."""

from __future__ import annotations

from typing import Any

_COMMON_SECTIONS = [
    "Contexto",
    "Objetivo",
    "Escopo",
    "Abordagem técnica",
    "Critérios de aceite",
    "Plano de testes",
    "Documentação a atualizar",
    "Riscos e dependências",
    "Definição de pronto",
]

DEFAULTS: dict[str, Any] = {
    "types": {
        "bug": {"description": "Comportamento incorreto ou regressão"},
        "feature": {"description": "Nova funcionalidade"},
        "enhancement": {"description": "Melhoria de funcionalidade existente"},
        "documentation": {"description": "Somente documentação"},
        "refactor": {"description": "Reestruturação sem mudança de comportamento"},
        "test": {"description": "Somente testes, fixtures ou evidência de verificação"},
        "ci": {"description": "Pipeline e checks automáticos"},
        "chore": {"description": "Dependências, ferramentas e configuração de desenvolvimento"},
    },
    "issues": {
        "items_section": "Itens",
        "depends_marker": "depende de",
        "acceptance_section": "Critérios de aceite",
        "sections": {
            "default": _COMMON_SECTIONS,
            "bug": [
                "Comportamento observado",
                "Comportamento esperado",
                "Passos para reproduzir",
                *_COMMON_SECTIONS[2:],
            ],
            "documentation": ["Contexto", "Objetivo", "Critérios de aceite", "Definição de pronto"],
        },
    },
    "pr": {
        "required_sections": ["Issues", "Resumo", "Testes executados", "Documentação", "Versão"],
        "version_section": "Versão",
        "tests_section": "Testes executados",
        "docs_section": "Documentação",
        "override_reason_marker": "Motivo da sobreposição",
    },
    "changelog": {
        "intro": (
            "Todas as mudanças publicadas deste projeto. Este arquivo é escrito pela automação de release; "
            "não edite as seções de versão à mão."
        ),
        "sections": [
            {"id": "breaking", "title": "⚠ Mudanças incompatíveis"},
            {"id": "features", "title": "Funcionalidades"},
            {"id": "improvements", "title": "Melhorias"},
            {"id": "fixes", "title": "Correções"},
            {"id": "docs", "title": "Documentação"},
            {"id": "maintenance", "title": "Manutenção"},
        ],
    },
}

MESSAGES: dict[str, str] = {
    # --- configuração --------------------------------------------------------------------------
    "config.language.unknown": "não é um idioma aceito; use um de {accepted}.",
    # --- labels (o GitHub limita a descrição a 100 caracteres) ----------------------------------
    "label.epic": "Acompanhamento de um plano com várias issues",
    "label.release": "O merge publica uma versão com tudo que está acumulado; sem este label, o PR fica acumulado",
    "label.breaking": "Quebra de compatibilidade para quem usa o projeto",
    "label.override": "Sobrepõe o nível calculado: {level} ({meaning})",
    "label.override.major": "incompatível",
    "label.override.minor": "funcionalidade",
    "label.override.patch": "correção",
}
