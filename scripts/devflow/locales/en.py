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
    "config.prerelease_prefix.empty": "must be a non-empty string, for example `release:`.",
    "config.prerelease_prefix.clash": (
        "produces the label `{label}` for channel `{channel}`, which is already another label of the workflow; "
        "change the prefix."
    ),
    # --- version plan --------------------------------------------------------------------------
    "plan.cycle.target_changed": (
        "The target of the cycle changed from {old} to {new}: what accumulated now asks for more than {tag} "
        "expected, and channel numbering starts over at {new}."
    ),
    "plan.request.unknown_label": (
        "The label `{label}` on {change} is not a pre-release channel of this project ({accepted}) and asks for "
        "no version."
    ),
    "plan.request.manual_prerelease": (
        "The manual run asks for the `{channel}` pre-release and wins over the labels in this run; "
        "requests from new PRs: {asked}."
    ),
    "plan.request.manual_final": (
        "The manual run asks for the final version and wins over the labels in this run; "
        "requests from new PRs: {asked}."
    ),
    "plan.request.most_mature": "The most mature request wins: {winner}. Also asked for a version: {others}.",
    "plan.request.promoted": (
        "The label `{label}` asks for a channel before `{current}`, which the {core} cycle has already published "
        "({tag}): the pre-release goes out as `{current}`, because a channel never goes back."
    ),
    "plan.prerelease.nothing_new": (
        "Nothing new since {tag}: another `{channel}` pre-release would be identical to it. To promote, ask for a "
        "more mature channel; for the final version, run with `--force`."
    ),
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
    "release.beginning": "the beginning",
    "release.nothing": (
        "Nothing to release: {count} change(s) accumulated since {base}, none in a PR with a version label ({labels})."
    ),
    "release.nothing.cycle": (
        "Nothing to release: {count} change(s) accumulated since {base}, {fresh} after {previous}; "
        "none of these in a PR with a version label ({labels})."
    ),
    "release.manual.answered": (
        "The request of this manual run was answered by {tag}, which has just been published; "
        "nothing came in after it."
    ),
    "report.cycle": "Pre-release cycle in progress: {cycle}. Current version: {current}.",
    # --- release notes -------------------------------------------------------------------------
    "notes.news.title": "New since {previous}",
    "notes.news.none": (
        "Nothing new since {previous}: this version takes the same content to the `{channel}` channel."
    ),
    "notes.accumulated.title": "Everything since {base}",
    # --- preview and check of the version request ----------------------------------------------
    "preview.prerelease.title": (
        "### Version preview: when merged, this PR publishes the pre-release **{tag}** ({level})"
    ),
    "preview.prerelease.body": (
        "It includes this PR and {others} change(s) accumulated since {base}. It is a test version of the "
        "`{channel}` channel: the changelog and the comments on the issues wait for the final version, requested "
        "with `{release}`."
    ),
    "preview.prerelease.news": (
        "New since {previous}: this PR and {fresh} change(s) that have not been in a pre-release yet."
    ),
    "preview.final.closes_cycle": (
        "It closes the pre-release cycle in progress ({cycle}): it covers everything since {base}, and it is the "
        "one that writes the changelog and the comments on the issues."
    ),
    "preview.pending.title": "### Version preview: this PR asks for no version, but it goes into **{tag}** ({level})",
    "preview.pending.body": (
        "A version request is still unanswered ({asked}): **{tag}** is not out yet, and this PR goes into it when "
        "merged. If that is not the intention, wait for the version before merging, or remove the label from "
        "whoever asked."
    ),
    "preview.none.channels": "With a channel label ({labels}), it would publish a pre-release of that number.",
    "check.version_labels.many": (
        "More than one version label ({labels}); keep only one: `{release}` publishes the final version, and each "
        "channel label a pre-release."
    ),
    "check.version_labels.unknown": (
        "The label `{label}` is not a pre-release channel of this project ({accepted}): it asks for no version."
    ),
    "evidence.version.prerelease": (
        "**Version:** the PR asks for a pre-release of the `{channel}` channel. The final version, with the "
        "changelog, comes later; the release automation comments here when it is out."
    ),
    "check.request.none": "PR #{pr} has no version label: it asks for no version, nothing to check.",
    "check.request.ok": "PR #{pr}: the `{label}` request can be published ({tag}).",
    "check.request.inherited": (
        "PR #{pr}: the `{label}` request runs into {count} problem(s) that already exist without this PR (above). "
        "The check does not fail for them, but the release stops until they are solved."
    ),
    "check.request.analysis": (
        "PR #{pr}: the `{label}` request is waiting for the version analysis (warning above). The check does "
        "not fail for it, because recording the analysis does not run the check again; the release stops "
        "until it is recorded."
    ),
    "check.request.refused": (
        "PR #{pr}: the `{label}` request cannot be published ({count} problem(s) above). Fix it or remove the label."
    ),
    # === issues.py, text.py, epics.py (#37): as chaves deste módulo ====================================
    # (fim de issues)
    # === config.py, semver.py, gh.py, plan.py (#38): as chaves deste módulo ==============================
    # config.py: shape and types (the key comes first, in `dev-workflow.toml: `key` ...`)
    "config.type.bool": "boolean",
    "config.type.int": "integer",
    "config.type.float": "number",
    "config.type.str": "string",
    "config.type.list": "list",
    "config.type.dict": "table",
    "config.type.other": "another type",
    "config.shape.table": "must be a table, not {got}.",
    "config.shape.type": "must be of type {expected}, not {got}.",
    "config.key.unknown_close": "is not a known key. Did you mean `{close}`?",
    "config.key.unknown": "is not a known key. Accepted: {accepted}.",
    # config.py: values
    "config.schema": "must be 1.",
    "config.types.empty": "needs at least one type.",
    "config.changelog.section_missing": "needs a section with id `{id}`.",
    "config.one_of": "must be one of {accepted}.",
    "config.types.prefixes": "needs at least one commit and branch prefix.",
    "config.types.section": "does not match an id of `changelog.sections`.",
    "config.regex.invalid": "is not a valid regular expression: {error}.",
    "config.initial_version": "is not a SemVer version.",
    "config.required": "is required.",
    "config.files.search_or_regex": "needs exactly one of `search` and `regex`.",
    "config.files.replace": "is required with `regex`.",
    "config.files.marker": (
        "needs a `{{current…}}` marker (for example `version = \"{{current}}\"`): without it the replacement "
        "changes nothing."
    ),
    "config.files.count": "must be an integer greater than zero.",
    "config.globs.empty": "needs at least one pattern.",
    "config.floors.group": "needs a capture group with the version.",
    "config.commit_message.tag": "must contain `{{tag}}`.",
    "config.release.mark": "accepts `comment` and `milestone`.",
    "config.file.not_utf8": "{path}: is not UTF-8; save the file as UTF-8.",
    # semver.py
    "semver.parse": "'{text}' is not a SemVer version (major.minor.patch[-pre][+build]).",
    "semver.bump": "Level '{level}' does not increment the version.",
    "semver.level.unknown": "Unknown level: '{level}'. Use one of {accepted}.",
    "semver.zero_major.unknown": "Unknown 0.x policy: '{policy}'.",
    "semver.channel.invalid": "Invalid pre-release channel: '{channel}'.",
    "semver.channel.outside": "Pre-release channel '{channel}' is not in the project's list ({accepted}).",
    "semver.channel.empty_list": "empty",
    # gh.py
    "gh.exit": "exit {code}",
    "gh.missing.gh": (
        "`{command}` was not found: the GitHub CLI is required (https://cli.github.com, then "
        "`gh auth login`). To go on with git only, without GitHub, use {env}=1."
    ),
    "gh.missing.tool": "`{command}` was not found on the PATH; install it or check the PATH.",
    "gh.timeout": "did not answer in {seconds} s; raise {env} if the network is slow.",
    "gh.env.invalid": "{env} must be a JSON list of strings.",
    "gh.api.failed": "GitHub answered {shown} on {route}: {detail}",
    "gh.api.failed_after": "GitHub answered {shown} on {route} after {count} attempts: {detail}",
    "gh.api.not_json": "the response of {route} is not valid JSON: {body}",
    # plan.py: signals (the detail of each `Signal`; the `source` code does not change with the language)
    "plan.signal.issue": "#{number} has the label `{label}`",
    "plan.signal.pr_title": "PR title",
    "plan.signal.commit": "`{type}` in {where}",
    "plan.signal.bang": "`!` in {where}: {description}",
    "plan.signal.breaking_commit": "BREAKING CHANGE in {where}: {note}",
    "plan.signal.label": "label `{label}`",
    "plan.signal.breaking_body": "BREAKING CHANGE in the PR body: {note}",
    "plan.signal.surface_added": '`{path}` added to the "{surface}" surface',
    "plan.signal.surface_modified": '`{path}` changed in the "{surface}" surface',
    "plan.signal.surface_removed": '`{path}` removed from the "{surface}" surface',
    # plan.py: notes
    "plan.none": "none",
    "plan.note.issue_type": (
        "#{number} (cited by {change}) does not have exactly one type label ({found}): it decides neither "
        "the level nor the changelog section. Leave a single type on the issue."
    ),
    "plan.note.reverted": (
        "{revert} reverts {original} ({title}) before the release: both leave the level calculation and the "
        "changelog."
    ),
    "plan.note.stale_analysis": (
        "{change}: analysis older than the last commit of the PR; it does not count, and the change stays "
        "without analysis until a new one is recorded."
    ),
    "plan.note.at_least_patch": "No signal asks for an increment; a published version bumps at least the patch.",
    "plan.note.zero_major": (
        "Version 0.x: a breaking change bumps the minor. To declare the API stable and go to 1.0.0, "
        "use the `{label}` label on the release PR."
    ),
    "plan.note.floor_raised": "`{path}` declares the floor {version}: the level goes up from {old} to {new}.",
    "plan.override.source": "label `{label}` on {change}",
    "plan.override.no_reason": "(no reason given)",
    # plan.py: problems
    "plan.problem.nothing": "Nothing has accumulated since the last version; there is nothing to publish.",
    "plan.problem.floor": (
        "`{path}` declares the floor {version}, above the version {target} that would be published. "
        "Fix the floor or classify the change so that the version reaches it."
    ),
    "plan.problem.tag_exists": (
        "The tag {tag} already exists. A maintenance branch only takes fixes; check the branch and the "
        "computed level."
    ),
    "plan.problem.analysis_missing": (
        "Changes to public surfaces without a recorded analysis: {changes}. Record the analysis "
        "(`release.py record-analysis`) or override the level with a reason."
    ),
    # plan.py: recorded analysis (format errors)
    "plan.analysis.schema": 'The analysis needs `"schema": 1` and a `changes` list.',
    "plan.analysis.object": "{where} must be an object.",
    "plan.analysis.reference": "{where} needs `pr` (a number) or `commit` (a SHA with 7 characters or more).",
    "plan.analysis.level": "{where}.level must be one of {accepted}.",
    "plan.analysis.summary": "{where}.summary is required: one sentence with the reason for the level.",
    "plan.analysis.evidence": "{where}.evidence must be a list of strings.",
    # plan.py: changelog and justification of the number
    "plan.changelog.part_of": "— part of {issues}",
    "plan.changelog.empty": "No changes visible to those who use the project.",
    "plan.origin.initial": "{version} (initial version, no tag)",
    "plan.justification.headline": "**{origin} → {target}** — level **{level}**.",
    "plan.justification.override": (
        "Level overridden to **{level}** ({source}); the calculation gave **{natural}**. Reason: {reason}"
    ),
    "plan.justification.table_header": "| Change | Level | Signals |",
    "plan.justification.unanalyzed": "public surface touched without analysis: {paths}",
    "plan.justification.analysis_all": "Agent analysis: covers every change.",
    "plan.justification.analysis_some": (
        "Agent analysis: covers {analyzed} of {total} changes; the others only have deterministic signals."
    ),
    "plan.justification.analysis_none": "Agent analysis: missing; the level comes only from deterministic signals.",
    # (fim de plan)
    # === release.py (#39): as chaves deste módulo =====================================================
    # (fim de release)
    # === bootstrap.py (#40): as chaves deste módulo =================================================
    # (fim de bootstrap)
    # --- labels (GitHub limits the description to 100 characters) -------------------------------
    "label.prerelease": "Merging publishes a {channel} pre-release with everything accumulated",
    "label.epic": "Tracks a plan made of several issues",
    "label.release": "Merging publishes a version with everything accumulated; without it, the PR waits",
    "label.breaking": "Breaks compatibility for those who use the project",
    "label.override": "Overrides the computed level: {level} ({meaning})",
    "label.override.major": "incompatible",
    "label.override.minor": "feature",
    "label.override.patch": "fix",
}
