---
name: cloudflare-remote-mcp-worker
description: Deploy or extend an existing MCP-capable repo onto a Cloudflare Worker when the user wants a remote `/mcp` URL, Cloudflare-hosted testing, auth/docs/screenshots, or a clean path from local repo work to repo-visible `main`.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Cloudflare Remote MCP Worker

## When to use

Use this when a repo already has an MCP server or similar backend and the user wants:
- a Cloudflare-hosted remote MCP endpoint,
- a browser app and MCP tool sharing the same Worker logic,
- Cloudflare deploy/secret setup notes,
- verification that the result is usable through `/mcp`,
- repo-visible docs/screenshots/auth cleanup that should land on `main`.

Do not use it for local-only stdio/plugin packaging with no remote deployment goal. Use `skills/repo-plugin-packaging/SKILL.md` for Codex plugin UI packaging.

## Inputs and context to gather

1. Confirm repo root, branch, dirty state, and default branch:

```bash
git rev-parse --show-toplevel
git status --short --branch
git remote show origin | sed -n '1,40p'
```

2. Find the current MCP/server entrypoints and deployment files:

```bash
rg -n "StdioServerTransport|createMcpHandler|/mcp|wrangler|worker" src package.json README.md plugins scripts
```

3. Check whether the repo already has:
- a local stdio path that must remain intact,
- an existing Worker entrypoint,
- a smoke test script,
- `.env` or other local config the Worker dev path should reuse.

4. If secrets are needed, plan the split:
- repo-safe work in-session,
- `wrangler login`, `wrangler secret put ...`, or any real token entry handed to the user.

## Procedure

1. Keep the local path intact. If the repo already has a local stdio launcher, add the Worker as a separate entrypoint rather than replacing the existing local integration.
2. Create or extend the Worker entrypoint so it exposes:
- `POST /mcp` for the remote MCP server,
- `GET /health` for fast verification,
- optional browser/demo routes such as `/` or `/api/...` when the repo needs a user-facing demo.
3. Add/update `wrangler.jsonc` and package scripts. Keep the naming explicit:
- `worker:dev`
- `worker:dry-run`
- `worker:deploy`
4. If local dev should reuse `.env`, add a sync step for Wrangler local vars before `wrangler dev`.
5. Document the remote connector shape in README/docs using placeholders, not personal deployed URLs.
6. Add or update smoke tests:
- local build/smoke,
- MCP tool-surface contract smoke if the repo already has a non-trivial tool set,
- remote MCP protocol smoke against `/mcp`,
- app/API smoke if a browser/demo route exists.
7. If auth is needed, prefer a single clear mechanism such as `ACCESS_TOKEN` with `Authorization: Bearer ...`, and document the client limitation if some MCP clients cannot send custom headers.
8. Create local-only handoff notes only if the user asks. Keep them out of shared history with `.git/info/exclude` unless the repo explicitly wants shared docs.
9. For repo visibility, do not stop at a feature branch if the user expects the work visible on GitHub’s default branch. Verify whether it has landed on `main`.

## Efficiency plan

- Search for existing server/deploy code before writing new scaffolding.
- If the repo already exposes many tools, add or reuse one contract smoke that checks the expected list and samples a few representative workflow calls before expanding the surface further.
- Reuse one shared ranking/service layer when both browser UI and MCP tool need the same behavior.
- Use `/health` first, then remote MCP smoke, then richer UI/API smoke.
- If the task changes Worker-visible HTML/app behavior, assume a redeploy is needed after merge and verify the hosted URL again instead of stopping at GitHub.
- Stop early if the blocker is secret entry or Cloudflare login and hand that step to the user instead of stalling.

## Pitfalls and fixes

- Symptom: `wrangler deploy --dry-run` or `wrangler dev` fails on a macOS log-path permission error.
  Cause: Wrangler is trying to write logs outside the workspace.
  Fix: set `WRANGLER_LOG_PATH=/tmp/<repo>-wrangler.log` before rerunning.
- Symptom: remote Worker works locally but public docs leak a personal `workers.dev` URL.
  Cause: committed docs used the real deployed URL instead of placeholders.
  Fix: scrub the concrete URL from committed docs and keep it only in local notes.
- Symptom: user says “I don’t see it on GitHub.”
  Cause: the work exists only on a feature branch or PR.
  Fix: verify `origin/main` explicitly before claiming the change is public.
- Symptom: a new smoke/verification script fails because one tool is missing locally but exists remotely.
  Cause: local stdio and Worker tool surfaces drifted.
  Fix: treat it as a parity bug and wire the missing tool into the local entrypoint instead of weakening the smoke.
- Symptom: UI or browser-demo changes merged to GitHub are not visible at the `workers.dev` URL.
  Cause: GitHub merge did not redeploy the Cloudflare Worker.
  Fix: rerun `worker:dry-run`, then `worker:deploy`, then verify `/health` and the remote `/mcp` smoke again.
- Symptom: remote MCP auth works in smoke scripts but not in a third-party client.
  Cause: the client cannot send bearer headers.
  Fix: choose public mode, a different route/token scheme, or Cloudflare Access/OAuth.
- Symptom: live upstream API calls fail intermittently with resets.
  Cause: network flakiness or upstream instability.
  Fix: add retries and partial-failure tolerance instead of failing the whole result.

## Verification checklist

- Local stdio/plugin path still works if the repo had one before.
- `npm run build` or equivalent succeeds.
- `worker:dry-run` or local Worker validation succeeds.
- `/health` responds with the expected shape.
- Remote MCP smoke reaches `/mcp` and lists/calls the expected tools.
- If the repo has a workflow-tool contract smoke, it passes locally and against the deployed Worker.
- Browser/API smoke passes if demo routes exist.
- Docs use placeholder URLs and explain auth/client caveats honestly.
- If the user expects public GitHub visibility, verify the final state on `main`, not just the feature branch.
