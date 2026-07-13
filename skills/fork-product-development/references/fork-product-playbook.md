# Fork Product Playbook

Use this reference when the task needs more than the quick checklist in `SKILL.md`.

## When This Pattern Applies

This pattern applies when a repo is both:

- an open-source upstream that may accept contributions, and
- a foundation for a private, personal, team, client, or experimental product build.

Common examples:

- A public app with a paid hosted version, while the user builds a local/dev fork.
- A framework or agent system that needs client-specific integrations.
- An open-source product used as a base for internal tools.
- A research/prototype fork where some improvements may become PRs later.

## Initial Repo Audit

Start with facts:

```bash
git remote -v
git status --short --branch
git branch --all --verbose
git log --oneline --decorate -10
```

Then inspect:

- project build commands,
- local install/deploy scripts,
- ignored/generated folders,
- app/package identity files,
- config/secrets conventions,
- existing docs for fork policy or release process.

If working with a desktop/mobile app, identify:

- product name,
- bundle/package ID,
- data directory,
- keychain/credential namespace,
- update channel,
- URL scheme/deep links,
- permissions identity,
- installed path.

## Feature Classification Guide

### Upstream Candidate

Use this bucket when the change:

- helps many upstream users,
- is optional or backward-compatible,
- avoids personal/team/client defaults,
- has a focused implementation,
- can be tested or reasoned about clearly,
- does not depend on private services,
- does not weaken upstream business boundaries.

Examples:

- export improvements,
- generic provider support,
- privacy/exclusion rules,
- repair/retry tools,
- better diagnostics,
- generic project tagging.

### Fork-Only

Use this bucket when the change:

- changes local product identity,
- removes or hides paid/commercial UX for a private build,
- stores data in private/team-specific locations,
- uses personal API keys or private infrastructure,
- bakes in client-specific exports/reports,
- changes defaults around one user's workflow,
- is not appropriate for upstream maintainers to support.

Examples:

- `MyCompany Dev.app`,
- local app bundle ID and permissions identity,
- internal Toggl/client mappings,
- private report templates,
- client-specific automation hooks,
- local install scripts for one machine/team.

### Maybe Later

Use this bucket when the idea is probably useful but not ready:

- behavior is too coupled to the fork,
- UI copy is confusing,
- there are no tests,
- configuration is too hard-coded,
- provider assumptions are too narrow,
- docs are missing,
- failure modes are unclear.

Keep maybe-later features on the product branch until they are generalized.

## Branching Patterns

### Long-Lived Downstream Product Branch

Use a long-lived branch for the actual forked product:

```text
<owner>/<product-dev>
agent/<feature-dev-fork>
team/<client-product>
```

This branch may include fork-only commits. It should still be buildable and documented.

### Clean Upstream PR Branch

Create PR branches from `upstream/main`:

```bash
git fetch upstream
git checkout -b pr/<feature-name> upstream/main
```

Bring over only the generic work:

```bash
git cherry-pick <commit>
```

If cherry-pick drags in fork-only changes, stop and reimplement the generic part manually.

### Syncing Upstream Into Product Branch

For small forks:

```bash
git fetch upstream
git checkout <product-dev-branch>
git rebase upstream/main
```

For mature forks:

```bash
git fetch upstream
git checkout <product-dev-branch>
git merge upstream/main
```

Choose merge when conflict history itself becomes useful documentation.

## PR Preparation Checklist

Before opening an upstream PR:

- Branch starts from `upstream/main`.
- Diff contains one feature only.
- No private paths, secrets, local IDs, or personal branding.
- No generated build artifacts.
- Tests/build pass or failures are clearly unrelated.
- README/docs are updated only if upstream users need them.
- Commit message describes the generic feature.
- PR body explains problem, solution, tests, and limitations.

Good PR title shape:

```text
Add Markdown timeline export
Add OpenAI-compatible provider configuration
Add failed-batch repair controls
```

Avoid PR title shape:

```text
Add my local Dayflow changes
Fix lots of stuff
Make app work for client workflow
```

## Downstream Product Checklist

Before shipping/running the forked product:

- Build came from the product branch.
- Installed binary/app path is expected.
- Bundle/package ID is expected.
- Display name is expected.
- Data directory is expected.
- Credentials/keychain namespace is separate if needed.
- Update channel will not overwrite the fork with upstream/public builds.
- Permissions identity is stable across rebuilds.
- User-facing copy does not imply a paid/public product flow that does not apply.
- Repo-local notes describe local-only changes.

For macOS apps, useful checks include:

```bash
plutil -p "/Applications/<App>.app/Contents/Info.plist" | rg "CFBundleName|CFBundleIdentifier"
codesign -dv "/Applications/<App>.app"
stat -f "%Sm %N" "/Applications/<App>.app/Contents/MacOS/<Executable>"
```

For Node/web apps, useful checks include:

```bash
git status --short --branch
npm run build
npm test
npm run lint
```

Use the repo's own commands when available.

## Documentation Pattern

Keep two levels of documentation:

1. **Policy note:** durable rules for how this fork is maintained.
2. **Project report:** current state, commits, branch names, PR links, known gaps, install/build notes.

Good filenames:

```text
docs/fork-development-practices.md
docs/fork-policy.md
project-report.md
FORK_REPORT.md
```

The report should track:

- upstream remote,
- fork remote,
- active product branch,
- clean PR branches,
- current local app/package identity,
- fork-only features,
- upstream candidates,
- known gaps,
- latest sync with upstream,
- latest successful validation commands.

## Recommended User Communication

When explaining decisions, be explicit:

- "This belongs upstream because it is generic and optional."
- "This should stay fork-only because it changes local product identity."
- "This is maybe-later because the idea is useful but the implementation is too coupled to this fork."
- "I will build from the product branch and verify the installed app identity before telling you to launch it."
- "I will create a clean PR branch from upstream/main so the PR does not include local fork changes."

## Failure Recovery

If the wrong app or product build was launched:

1. Stop and inspect bundle/package identity.
2. Verify current branch and build output path.
3. Rebuild from the intended branch.
4. Install/copy through the documented script.
5. Verify executable timestamp and identity.
6. Only then tell the user to launch.

If a PR branch accidentally includes fork-only changes:

1. Do not force-push blindly.
2. Create a fresh branch from `upstream/main`.
3. Cherry-pick only clean commits or reapply the generic diff manually.
4. Run tests.
5. Open or update the PR from the clean branch.

If upstream sync produces conflicts:

1. Classify each conflict as upstream-owned, fork-owned, or true integration.
2. Preserve fork identity/config intentionally.
3. Prefer upstream behavior for generic product logic unless the fork has a documented reason to differ.
4. Update project notes if the conflict changes the fork policy.
