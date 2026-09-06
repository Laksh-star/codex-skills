---
name: fork-sync-rebase
description: Safely review and selectively integrate an upstream repository into a long-lived personal, team, or client fork. Use when a fork has local features that must remain isolated while upstream continues to change.
---

# Fork Sync Rebase

Use this skill for repositories with a distinct upstream remote and fork remote. The goal is to keep the fork maintainable without treating upstream changes as automatically safe or desirable.

## Invocation

Use one of these requests:

- `Run fork sync review for <repo>.`
- `Review upstream changes for <repo>; do not alter branches.`
- `Integrate upstream into <fork branch> using the fork sync workflow.`

Default to **review mode** unless the user explicitly asks to integrate or rebase.

## Safety Invariants

- Identify the actual repository root before running Git commands.
- Confirm which remote is the upstream source and which remote is the user's fork. Do not infer this from remote names alone.
- Never push to upstream. An upstream pull request requires a separate explicit user request.
- Never rebase the active development branch in place as the first action.
- Never force-push a shared or user-facing branch unless the user explicitly asks and understands the consequence.
- Preserve fork-specific identity, signing, storage, privacy, billing, updater, and local integration changes unless the user asks to remove them.
- Do not stage, delete, or reset unrelated tracked or untracked work.

## Review Mode

1. Inspect worktree status, remotes, current branch, tracking branch, recent commits, and existing integration/reference branches.
2. Fetch upstream. Fetching is allowed in review mode; it must not merge or rebase anything.
3. Compare the active fork branch to the refreshed upstream default branch:
   - commit divergence and tags/releases
   - changed subsystems and likely conflict areas
   - upstream changes worth integrating now, deferring, or intentionally excluding
4. Report a recommendation with a concise integration plan. Include whether an integration is low, medium, or high risk.
5. Stop before rebasing, merging, changing branches, installing dependencies, building, or pushing unless the user explicitly requested integration.

## Integration Mode

Use this only after explicit user authorization.

1. Require no tracked worktree edits. List untracked files, but leave them untouched unless they directly block the operation.
2. Fetch upstream and create a dated, read-only reference branch pointing at the refreshed upstream default branch, for example `agent/upstream-YYYY-MM-DD`.
3. Create a disposable integration branch from the active fork branch, for example `agent/rebase-YYYY-MM-DD`.
4. Rebase the disposable integration branch onto the dated upstream reference.
5. Resolve conflicts by first preserving the fork's explicit local boundaries, then adapting feature code to upstream architecture. Avoid broad refactors unrelated to integration.
6. Run the repository's focused build/test/install path. For desktop apps, distinguish compilation from runtime/manual validation.
7. Review the resulting diff and summarize preserved local changes, adopted upstream changes, and deferred conflicts or exclusions.
8. Only after successful validation, update the active fork branch from the verified integration branch. Push to the verified fork remote, never upstream.

## Decision Criteria

Prefer integration when upstream includes security, data integrity, recording/capture, dependency, platform compatibility, or provider/runtime fixes that affect the fork.

Defer large upstream subsystems when they introduce architecture the fork does not yet need, carry unresolved privacy or product implications, or would make local feature maintenance materially harder. Record deferred items in the repository's existing project log when one exists.

## Completion Report

State:

- upstream revision and dated reference branch
- active fork branch and verified fork remote
- integration branch, if used
- adopted, deferred, and excluded upstream areas
- build/test/install evidence and remaining manual checks
- exact push destination
