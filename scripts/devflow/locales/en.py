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
    # commit-msg hook
    "issues.commit_msg.added": "commit-msg: added 'Refs: #{issue}' from the branch {branch}.",
    "issues.commit_msg.missing": (
        "commit-msg: the commit must reference a GitHub issue.\n"
        "  Add a 'Refs #N' trailer (or work on a <prefix>/<N>-<slug> branch, using the prefix of a\n"
        "  type: {prefixes}). The '(#N)' suffix and 'other/repo#N' do not count.\n"
        "  No issue yet? Create one first: see the dev-workflow skill."
    ),
    # check-pr
    "check.links.none": (
        "The PR body references no issue: use `Closes #N` (complete delivery) or `Refs #N` (partial)."
    ),
    "check.links.missing": "#{number} does not exist in {repository}.",
    "check.links.pull_request": "#{number} is a pull request, not an issue.",
    "check.links.type": "#{number} needs exactly one type label ({types}); found: {found}.",
    "check.links.no_type": "none",
    "check.links.only_epics": "The PR references only epics; cite the child issue it delivers (`Closes #N`).",
    "check.exempt.author": "PR by {author}: exempt from the issue flow.",
    "check.exempt.release": "Release PR created by the automation: exempt.",
    "check.closing_list": (
        "#{number} is in a closing list (`Closes #A, #{number}`), but GitHub only closes the first issue of "
        "the list: repeat the keyword (`Closes #{number}`) or use `Refs #{number}` if the delivery is partial."
    ),
    "check.section.missing": "The PR body has no `## {name}` section (use the PR template).",
    "check.section.empty": "The `## {name}` section is empty: fill it in or write `Not applicable — reason`.",
    "check.override.many": "More than one override label ({levels}); keep only one.",
    "check.override.level": "`{label}` is not major, minor or patch.",
    "check.override.channels": " or with a channel label ({labels})",
    "check.override.needs_release": (
        "`{label}` only applies to a PR labeled `{release}`{also}: the override decides the number of the "
        "version this PR publishes."
    ),
    "check.override.reason": (
        "Version override without a reason: write `{marker}: <reason>` in the `## {section}` section."
    ),
    "check.forged.title": (
        "The title `{subject}` looks like the release commit, which only the automation creates: it publishes "
        "no version and disappears from the changelog. Change the text; to publish, use the `{release}` label."
    ),
    "check.forged.commit": (
        "The commit `{subject}` looks like the release commit, which only the automation creates: it publishes "
        "no version and disappears from the changelog. Change the text; to publish, use the `{release}` label."
    ),
    "check.title": (
        "The title `{title}` does not follow Conventional Commits (`<type>(<scope>): <subject>`); it becomes "
        "the commit of a squash and goes into the changelog."
    ),
    "check.issue.sections": "#{number} is missing template sections: {missing} (use `Not applicable — reason`).",
    "check.issue.criteria": (
        "#{number} has {pending} of {total} acceptance criteria unchecked; check the verified ones or record "
        "the waiver in the issue before merging."
    ),
    "check.type_mismatch": (
        "The title uses `{type}`, but the linked issues are of type {types} "
        "(expected prefixes: {prefixes}). Check the classification."
    ),
    "check.annotation.title": "PR check",
    "check.annotation.error": "ERROR",
    "check.annotation.warning": "warning",
    "check.usage": (
        "usage: github_issues.py check-pr --pr N (or PR_NUMBER), with GITHUB_REPOSITORY or an authenticated `gh`"
    ),
    "check.channels.none": "none",
    "check.pr.not_found": "PR #{number} not found in {repository}.",
    "check.done": "PR #{number} checked: {count} warning(s).",
    # evidence comment (pr-merged)
    "evidence.delivered.by": "**Delivered by PR #{number}**, merged by @{merged_by}.",
    "evidence.delivered": "**Delivered by PR #{number}.**",
    "evidence.partial": (
        "**Partial delivery by PR #{number}** (the PR cites this issue with `Refs`; it stays open)."
    ),
    "evidence.commits": "**Commits**",
    "evidence.commits.unreadable": "- (the commit list could not be read; see the PR)",
    "evidence.tests": "Tests run",
    "evidence.docs": "Documentation",
    "evidence.declared": "**{label}** (as stated in the PR)",
    "evidence.not_stated": "- Not stated in the PR.",
    "evidence.criteria.none": "**Acceptance criteria:** the issue has no criteria list.",
    "evidence.criteria.pending": "**Acceptance criteria:** {pending} of {total} unchecked at merge time:",
    "evidence.criteria.pending_hint": (
        "Check them if they were verified, or reopen the issue and record what is missing."
    ),
    "evidence.criteria.done": "**Acceptance criteria:** all {total} checked.",
    "evidence.version.release": (
        "**Version:** the PR is labeled for a release; the release automation comments here when the version is out."
    ),
    "evidence.version.none": (
        "**Version:** the PR creates no version; this delivery accumulates and goes into the next published version."
    ),
    "issues.merged.not_found": "PR #{number} not found.",
    "issues.merged.not_merged": "PR #{number} was not merged; nothing to record.",
    "issues.merged.already": "#{issue}: the evidence from PR #{number} is already recorded.",
    "issues.merged.recorded": "#{issue}: evidence from PR #{number} recorded.",
    # start and sync-labels
    "issues.start.untyped": "#{number} needs exactly one type label ({types}) before it becomes a branch.",
    "issues.start.not_issue": "#{number} is not an issue of {repository}.",
    "issues.start.dirty": (
        "The working tree has changes: commit them, discard them or use another worktree before switching branches."
    ),
    "issues.start.exists": "The branch {name} already exists; switched to it.",
    "issues.start.created": "Branch {name} created from {base}.",
    "issues.labels.ok": "label {name} ok",
    "issues.labels.failed": "label {name} ERROR: {error}",
    # command line
    "issues.cli.not_a_number": "`{value}` is not an issue number",
    "issues.cli.description": (
        "Issues, PRs and epics of the dev-workflow flow. Exit codes: 0 ok, 1 failure, 2 usage or configuration."
    ),
    "issues.cli.command": "command",
    "issues.cli.commit_msg": "git hook: requires a reference to an issue in the message",
    "issues.cli.commit_msg.file_metavar": "FILE",
    "issues.cli.commit_msg.file": "the message file that git passes to the hook",
    "issues.cli.check_pr": "the PR check (link, sections, labels, title)",
    "issues.cli.pr": "PR number (default: PR_NUMBER)",
    "issues.cli.pr_merged": "comments the merged PR's evidence on the issues it cites",
    "issues.cli.start": "creates (or switches to) the issue's <prefix>/<N>-<slug> branch",
    "issues.cli.start.dry_run": "only prints the branch name",
    "issues.cli.sync_labels": "creates or updates the labels the flow uses",
    "issues.cli.sync_epic": "creates sub-issues and 'blocked by' links from the Items section",
    "issues.cli.all": "every issue with the epic label",
    "issues.cli.sync_checklist": "sets the checkboxes of the epics' Items section",
    "issues.cli.parent_of": "the parent epic of issue N",
    "issues.cli.close_epic": "closes the parent epic when its last child closes",
    "issues.cli.repository": "could not identify the repository (GITHUB_REPOSITORY, the origin remote or `gh`).",
    "issues.cli.choose": "{command}: use exactly one of {options}",
    "issues.cli.choose.epic": "N [N...] or --all",
    "issues.cli.choose.checklist": "N [N...], --all or --parent-of N",
    "issues.cli.pr_merged.number": "pr-merged: pass --pr N (or PR_NUMBER)",
    "issues.error": "ERROR: {error}",
    # text.py
    "text.slug.fallback": "work",
    # epics.py: links
    "epics.operation.sub_issue": "#{ref} becomes a sub-issue of #{target}",
    "epics.operation.blocked_by": "#{target} becomes blocked by #{ref}",
    "epics.item.foreign": "item from another repository ignored: {item}",
    "epics.item.repeated": "#{number} appears more than once in the list",
    "epics.item.foreign_dependency": "#{number}: dependency on another repository ignored ({ref})",
    "epics.item.self_dependency": "#{number} depends on itself",
    "epics.not_issue": "#{number} does not exist or is not an issue",
    "epics.lists_itself": "#{epic} lists itself as an item",
    "epics.other_parent": "#{number} is already a sub-issue of {parent}; parent left unchanged",
    "epics.missing_dependency": "#{number} depends on #{dep}, which does not exist or is not an issue",
    "epics.unlisted": "{ref} is a sub-issue of #{epic} but is not in the Items section",
    "epics.truncated": (
        "#{number} has more than 100 sub-issues or blockers; the read is incomplete "
        "and no automatic action is safe."
    ),
    "epics.graphql_failed": "gh api graphql failed: {error}",
    "epics.repository_unreachable": "repository {repository} is not reachable: {error}",
    # epics.py: checkboxes of the items section
    "epics.checklist.check": "{prefix}check #{number} in the Items section",
    "epics.checklist.uncheck": "{prefix}uncheck #{number} in the Items section",
    "epics.checklist.write_failed": "ERROR updating the Items section of #{epic}: {error}",
    "epics.checklist.unstable": "ERROR: the Items section of #{epic} did not settle after {attempts} attempts",
    "epics.checklist.no_parent": "#{issue} is not a sub-issue of an epic in this repository; nothing to do.",
    # epics.py: automatic closing
    "epics.close.no_parent": "#{issue} is not a sub-issue of an epic in this repository; nothing to close.",
    "epics.close.not_epic": "#{parent} does not have the epic label; it is not closed automatically.",
    "epics.close.already_closed": "#{parent} is already closed.",
    "epics.close.no_children": "#{parent} has no native sub-issues; nothing to close.",
    "epics.close.foreign": "#{parent} has sub-issues from another repository ({foreign}); close it by hand.",
    "epics.close.pending": "#{parent} stays open: {pending} still open.",
    "epics.close.dry_run": "[dry-run] would close #{parent} as {reason}:\n{comment}",
    "epics.close.raced": "#{parent} was already closed by another run.",
    "epics.close.failed": "ERROR closing #{parent}: {error}",
    "epics.close.done": "#{parent} closed as {reason}.",
    "epics.close.too_deep": "ERROR: the chain of epics above #{issue} is deeper than {depth} levels.",
    "epics.summary.head": "Closed automatically by the epic flow: all {count} sub-issues are closed.",
    "epics.summary.item": "- #{number} {title} — {state}",
    "epics.summary.completed": "completed",
    "epics.summary.not_planned": "not planned",
    "epics.summary.foot": (
        "If any completion criterion of the epic is still missing, reopen the epic and record what is left."
    ),
    # epics.py: sync-epic
    "epics.sync.not_epic": "#{epic} does not have the epic label",
    "epics.sync.shared": "#{number} is in more than one epic ({epics}); link it by hand",
    "epics.sync.summary": "#{epic}: {items} items, {links} links to create",
    "epics.sync.candidates": ", {count} candidates without an issue",
    "epics.sync.failed": "ERROR {operation}: {error}",
    "epics.sync.problem": "mismatch: {problem}",
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
    "config.changelog.hide": "has `{hidden}`, which is not an id of `changelog.sections` ({accepted}).",
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
