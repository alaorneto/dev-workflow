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
    "config.prerelease.table": "must be a table (`[versioning.prerelease]`) with the `channels` list.",
    "config.channels.type": 'must be a list of strings, for example `["alpha", "beta", "rc"]`.',
    "config.channels.name": (
        "has the channel `{channel}`, which is not a valid name: use lowercase, starting with a letter "
        "(letters, digits and hyphen)."
    ),
    "config.channels.order": (
        "must go from the least to the most mature channel, in SemVer precedence order, which is alphabetical "
        "(ASCII): `{later}` does not come after `{earlier}`. That is the order package managers apply."
    ),
    "config.channels.pep440": (
        "has the channel `{channel}`, which has no PEP 440 form, and `versioning.files` uses a `_pep440` marker. "
        "Channels with a PEP 440 form: {accepted}."
    ),
    "config.channels.pep440_clash": (
        "has `{first}` and `{second}`, which become the same PEP 440 form (`{form}`); keep only one of them."
    ),
    # --- version plan --------------------------------------------------------------------------
    "plan.cycle.floor": (
        "The cycle in progress has already published {tag}: the version does not go down, so the target stays at "
        "{floor} (the calculation would give {target})."
    ),
    "plan.cycle.override_below": (
        "The override asks for {target}, below {floor}, which the cycle in progress has already published as a "
        "pre-release ({tag}). A version never goes back: drop the override or use a level that reaches {floor}."
    ),
    "plan.channel.regressed": (
        "Channel `{channel}` comes before `{current}`, which the {core} cycle has already published ({tag}). "
        "A pre-release never goes back a channel: use `{current}` or a more mature one."
    ),
    "plan.core.taken": (
        "Version {core} already has a tag on another line ({tags}), out of reach of this branch. "
        "Two lines never publish the same number: check the branch and the computed level."
    ),
    # --- release -------------------------------------------------------------------------------
    "release.channel.unknown": (
        "Pre-release channel `{channel}` is not in the project's list. "
        "Accepted channels (`versioning.prerelease.channels`): {accepted}."
    ),
    "release.channel.none": "This project accepts no pre-releases: `versioning.prerelease.channels` is empty.",
    # --- labels (GitHub limits the description to 100 characters) -------------------------------
    "label.epic": "Tracks a plan made of several issues",
    "label.release": "Merging publishes a version with everything accumulated; without it, the PR waits",
    "label.breaking": "Breaks compatibility for those who use the project",
    "label.override": "Overrides the computed level: {level} ({meaning})",
    "label.override.major": "incompatible",
    "label.override.minor": "feature",
    "label.override.patch": "fix",
}
