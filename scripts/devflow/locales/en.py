"""English. A key missing here falls back to pt-BR (see ``devflow.i18n``)."""

from __future__ import annotations

from typing import Any

_COMMON_SECTIONS = [
    "Context",
    "Goal",
    "Scope",
    "Technical approach",
    "Acceptance criteria",
    "Test plan",
    "Documentation to update",
    "Risks and dependencies",
    "Definition of done",
]

DEFAULTS: dict[str, Any] = {
    "types": {
        "bug": {"description": "Incorrect behavior or regression"},
        "feature": {"description": "New capability"},
        "enhancement": {"description": "Improvement to something that already exists"},
        "documentation": {"description": "Documentation only"},
        "refactor": {"description": "Restructuring with no change in behavior"},
        "test": {"description": "Tests, fixtures or verification evidence only"},
        "ci": {"description": "Pipeline and automated checks"},
        "chore": {"description": "Dependencies, tooling and development configuration"},
    },
    "issues": {
        "items_section": "Items",
        "depends_marker": "depends on",
        "acceptance_section": "Acceptance criteria",
        "sections": {
            "default": _COMMON_SECTIONS,
            "bug": [
                "Observed behavior",
                "Expected behavior",
                "Steps to reproduce",
                *_COMMON_SECTIONS[2:],
            ],
            "documentation": ["Context", "Goal", "Acceptance criteria", "Definition of done"],
        },
    },
    "pr": {
        "required_sections": ["Issues", "Summary", "Tests run", "Documentation", "Version"],
        "version_section": "Version",
        "tests_section": "Tests run",
        "docs_section": "Documentation",
        "override_reason_marker": "Override reason",
    },
    "changelog": {
        "intro": (
            "All published changes of this project. This file is written by the release automation; "
            "do not edit the version sections by hand."
        ),
        "sections": [
            {"id": "breaking", "title": "⚠ Breaking changes"},
            {"id": "features", "title": "Features"},
            {"id": "improvements", "title": "Improvements"},
            {"id": "fixes", "title": "Fixes"},
            {"id": "docs", "title": "Documentation"},
            {"id": "maintenance", "title": "Maintenance"},
        ],
    },
}

MESSAGES: dict[str, str] = {
    # --- configuration -------------------------------------------------------------------------
    "config.language.unknown": "is not an accepted language; use one of {accepted}.",
    # --- labels (GitHub limits the description to 100 characters) -------------------------------
    "label.epic": "Tracks a plan made of several issues",
    "label.release": "Merging publishes a version with everything accumulated; without it, the PR waits",
    "label.breaking": "Breaks compatibility for those who use the project",
    "label.override": "Overrides the computed level: {level} ({meaning})",
    "label.override.major": "incompatible",
    "label.override.minor": "feature",
    "label.override.patch": "fix",
}
