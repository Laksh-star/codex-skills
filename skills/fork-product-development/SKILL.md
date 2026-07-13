---
name: fork-product-development
description: Maintain an open-source product fork that also needs private, team, client, or experimental features. Use when planning or implementing work in a forked repo, deciding what should stay fork-only versus become an upstream pull request, syncing from upstream, preparing clean PR branches, avoiding local branding/config leakage, or documenting a long-lived downstream product variant.
---

# Fork Product Development

## Operating Principle

Treat upstream and the fork as related but separate products. Upstream is the public source of truth; the fork is a downstream product variant that may include private workflows, local defaults, team/client features, and experimental integrations.

Use the detailed reference when needed: `references/fork-product-playbook.md`.

## First Pass

When starting work in a forked repo:

1. Inspect remotes and branch state.
   - Identify `upstream`, `origin` or fork remotes, current branch, uncommitted changes, and ignored/generated files.
   - Do not assume `main` is the active product branch.
   - Preserve unrelated user changes.

2. Classify the requested change before editing.
   - **Upstream candidate:** generic, optional, documented, broadly useful, reviewable.
   - **Fork-only:** local identity, private/team/client workflow, personal default, local signing/storage, paid-product removal, private integration.
   - **Maybe later:** useful but needs abstraction, tests, docs, or UX cleanup before upstream.

3. Choose the right branch path.
   - For fork product work, use the long-lived downstream branch.
   - For upstream PR work, create a clean branch from `upstream/main` and cherry-pick or reimplement only the generic feature.
   - Keep local-only commits out of PR branches.

4. Implement with boundary discipline.
   - Keep fork-only app identity, data paths, install scripts, and branding isolated in obvious files.
   - Keep upstream-friendly features generic and optional.
   - Avoid generated artifacts and unrelated cleanup.

5. Validate and install as the product requires.
   - Run repo-native build/test/smoke commands.
   - For local app forks, verify the installed app identity, bundle/package ID, executable path, and data directory before telling the user to launch it.
   - If a command fails because of sandbox/network/cache permissions, rerun with proper approval instead of changing the workflow.

6. Document current state.
   - Maintain a repo-local report or note with branch model, fork-only choices, upstream candidates, latest sync, build/install commands, and known gaps.
   - Add PR links and review status when upstream work is opened.

## Branch Model

Prefer this shape unless the repo already has a stronger convention:

- `upstream/main`: public source of truth.
- `main`: clean mirror of upstream in the user's fork.
- `<owner>/<product-dev>` or similar: long-lived downstream product branch.
- `pr/<feature>`: short-lived clean branch created from `upstream/main`.

Use rebase for small/young forks:

```bash
git fetch upstream
git checkout <product-dev-branch>
git rebase upstream/main
```

Use merge once the downstream branch is a durable product line with many local-only commits:

```bash
git fetch upstream
git checkout <product-dev-branch>
git merge upstream/main
```

## Upstream PR Hygiene

For upstream PRs:

- Start from `upstream/main`.
- Keep one PR to one feature.
- Exclude fork branding, local signing, local data paths, generated files, credentials, and team/client defaults.
- Add focused tests when the behavior can regress.
- Explain the value for upstream users, not just the fork.
- Keep the diff small enough for a maintainer to review without understanding the whole downstream product.

## Fork-Only Hygiene

For downstream product work:

- Make local app identity obvious.
- Keep private integrations opt-in and documented.
- Prefer explicit config files or settings over hidden constants.
- Document why a feature is fork-only.
- Keep a repeatable install/run path for the private/team build.
- Regularly pull upstream changes and resolve conflicts deliberately.

## Deliverable Checklist

Before finishing:

- Branch choice matches the change classification.
- Tests/build/smoke checks were run or explicitly reported as not run.
- Installed app/package identity was verified when relevant.
- Repo-local fork documentation was updated when policy or product behavior changed.
- Only intended files are staged and committed.
- Push target is the fork remote unless the user explicitly requests upstream work.

## Common Pitfalls

- Building from the wrong branch and launching the public/upstream app by mistake.
- Letting local product naming leak into an upstream PR.
- Sending one large PR that mixes generic features with fork-only workflow changes.
- Treating a private fork as temporary and failing to document how to sync upstream.
- Reverting user work while trying to get back to a clean upstream state.
- Trusting app recents, build folders, or LaunchServices names without checking bundle/package identity.
