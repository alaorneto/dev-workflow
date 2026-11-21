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
    # (fim de plan)
    # === release.py (#39): as chaves deste módulo =====================================================
    # --- run: messages for whoever operates it ---------------------------------------------------
    "release.error": "ERROR: {text}",
    "release.warning": "warning: {text}",
    "release.push.refused": (
        "the push of the release commit to `{branch}` was refused by GitHub (branch protection or token "
        "permission), not because the branch moved: {detail}\n"
        "Two ways out: `release.mode = \"pull-request\"` in the configuration, so the release reaches the branch "
        "through a PR; or a `RELEASE_TOKEN` secret allowed to write to it (for example, from someone who can "
        "bypass the protection). Nothing was published; run again after adjusting."
    ),
    "release.push.moved": "The remote branch moved during the release; recalculating.",
    "release.unstable": "the release did not settle; run again and check the state of the branch.",
    "release.analysis.missing": "the analysis file `{path}` does not exist.",
    "release.analysis.encoding": "the analysis file `{path}` is not in UTF-8.",
    "release.analysis.unreadable": "could not read the analysis file `{path}`: {error}.",
    "release.analysis.invalid": "the analysis file `{path}` is not valid JSON: {error}.",
    "release.analysis.refused": "Invalid analysis: {error}",
    "release.analysis.head_filled": (
        "The analysis does not say which `head` it analyzed; recorded for the current tip of the PR ({sha})."
    ),
    "release.analysis.no_head": (
        "Warning: the analysis does not say which `head` it analyzed; it will not count in the release."
    ),
    "release.analysis.recorded": "Analysis recorded on PR #{pr}: level {level}, {count} change(s).",
    "release.files.count": (
        "{path}: expected {expected} occurrence(s) of `{needle}`, found {found}. "
        "The file drifted from the current version or the pattern in `versioning.files` is wrong."
    ),
    "release.files.count_regex": "{path}: expected {expected} occurrence(s) of /{regex}/, found {found}.",
    "release.files.encoding": "{path}: not in UTF-8; convert the file (the version is written in UTF-8).",
    "release.files.unreadable": "{path}: could not read it ({error}).",
    "release.files.drift": "{path}: the content does not match version {version}.",
    "release.forged.merge": (
        "it came through merge {sha}, which is not the release PR's (`{branch}` of this repository)"
    ),
    "release.forged.not_pr": "it came through merge {sha}, which is not a PR's",
    "release.forged.other_pr": (
        "it came through PR #{number}, which is not the release PR (`{branch}` of this repository)"
    ),
    "release.forged.ignored": "Release commit {sha} ({tag}) ignored: {reason}. No version comes out of it.",
    "release.mark.failed": "could not mark #{number}: {error}",
    "release.tag.created": "Tag {tag} created on {sha}.",
    "release.github.created": "GitHub Release {tag} created.",
    "release.dispatch.done": "Workflow {workflow} dispatched for {tag}.",
    "release.dispatch.failed": "could not dispatch {workflow}: {error}",
    "release.pr.updated": "Release PR #{number} updated to {tag}.",
    "release.pr.opened": "Release PR #{number} opened for {tag}.",
    "release.reconcile": "Tag {tag} has no GitHub Release; finishing the publication.",
    "release.disabled": "Versioning is off in dev-workflow.toml (`versioning.enabled = false`).",
    "release.branch.not_release": "Branch `{branch}` does not publish versions (see `repository.release_branches`).",
    "release.branch.release_pr": (
        "Branch `{branch}` is the release PR's (`release.pr_branch`): the version comes out when that PR is "
        "merged, not from here."
    ),
    "release.override.no_reason": "(no reason given)",
    "release.override.manual": "manual run",
    "release.prepared.publishing": "Release commit of {tag} has no tag yet; publishing.",
    "release.preview.no_tag": "No reachable version tag: the preview starts after `release.py baseline`.",
    "release.preview.comment_failed": "could not comment the preview on the PR: {error}",
    "release.baseline.exists": "The repository already has version tags; the base tag is not needed.",
    "release.baseline.message": (
        "Baseline of the automatic versioning: what came before this tag is version {version}."
    ),
    "release.baseline.created": "Base tag {tag} created on {sha}.",
    "release.baseline.pushed": "Tag pushed to the remote.",
    "release.check.no_tree": "--tree {tree} is not a directory.",
    "release.check.pr_tip": ", the highest reachable from the PR tip",
    "release.check.initial": "versioning.initial_version (no tag yet)",
    "release.check.prepared": (
        "Release PR ({tag}): {count} file entry(ies) consistent with version {version}, which it publishes."
    ),
    "release.check.ok": "{count} file entry(ies) consistent with version {version} ({origin}).",
    "release.bump.none": "No file changed.",
    "release.level.invalid": "Invalid level: {level}.",
    "release.cli.description": "Semantic versioning of the project.",
    "release.cli.pr": "include an open PR as if it were merged",
    "release.cli.base_ref": "with --pr: the target branch (default: origin/<default branch>)",
    "release.cli.head_ref": "with --pr: the tip of the PR",
    "release.cli.tree": "check the files of another tree (the PR checkout) with this tree's configuration",
    "release.cli.check": "do not comment: fail if this PR's version request cannot be published",
    "release.cli.force": "publish what accumulated even without a labelled PR",
    "release.cli.prerelease": "pre-release channel, for example rc; implies --force",
    # --- plan report (`release.py plan`, `run`) ------------------------------------------------
    "release.report.nothing": "Nothing accumulated since {base}.",
    "release.report.next.title": "### Next version: **{tag}** ({level}) — {state}",
    "release.report.next.will": "will be published",
    "release.report.next.would": "would be published (no PR has asked for a version yet)",
    "release.report.requested_by": "Version requested by: {changes}.",
    "release.report.problems": "**Problems that block the release**",
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
