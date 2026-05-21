---
name: repo-plugin-packaging
description: Build or refine a repo-local Codex plugin from an existing project, especially when the user asks whether a repo can become a plugin, wants it shareable, visible in Codex plugin UI, or pushed cleanly.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Repo Plugin Packaging

## When to use

Use this when the user asks whether a repo can become a Codex plugin, wants plugin utility ideas grounded in a repo, asks for a shareable/local plugin scaffold, or wants plugin work committed and pushed.

Do not use it for generic MCP-only server setup unless the user wants Codex plugin packaging, plugin UI visibility, marketplace metadata, or shareability.

## Inputs and context to gather

1. Identify the repo root with `git rev-parse --show-toplevel` and inspect `README.md`, package/config files, scripts, and existing workflow docs.
2. Check current branch, remotes, and dirty state with `git status --short --branch` and `git remote -v`.
3. Determine whether the right target is:
   - a workflow plugin with skills/scripts,
   - a wrapper around an existing MCP server,
   - documentation and install flow only.
4. If secrets are involved, use `.env.example` and local `.env`; never store real keys in memory or docs.

## Procedure

1. Ground the plugin idea in actual repo workflows. Prefer the repo's existing commands and outputs over generic plugin concepts.
2. For a new scaffold, prefer the system helper when available:

```bash
python3 /Users/ln-mini/.codex/skills/.system/plugin-creator/scripts/create_basic_plugin.py <plugin-name> --with-skills --with-scripts --with-marketplace
```

3. Patch the scaffold to include repo-specific metadata, skills, scripts, and validation commands. For Python wrappers, do not assume `uv` exists; detect it and fall back to `sys.executable`.
4. For MCP-server plugins, build the server first and use a repo-owned launcher script as the stable entrypoint. Do not hardcode one-off commands into user-level config if the repo can own a launcher.
5. Document the install and smoke-test path. Keep the root README concise with quick start and validation; move deeper plugin maintenance detail into the plugin README.
6. Verify locally before publishing:
   - compile/build scripts,
   - run plugin helper scripts,
   - run an offline smoke test when possible,
   - run an online smoke test only after sourcing local env safely.
7. Before git work, inspect status and stage only intended files. Use a `codex/` feature branch unless the user explicitly wants otherwise.
8. If pushing, check whether `gh` is available early if PR creation is expected. Plain `git push -u origin <branch>` is sufficient when PR creation is unavailable.

## Efficiency plan

- Search for existing commands first: `rg "validate|build|seed|smoke|mcp|server|plugin" README.md package.json pyproject.toml scripts plugins .agents`.
- Reuse existing local scripts and docs instead of inventing new orchestration.
- Treat fresh-session or post-restart plugin visibility as the decisive test for Codex UI plugin work.
- Stop before broad refactors; a minimal functional plugin is preferred when the user accepts a practical first version.

## Pitfalls and fixes

- Symptom: `FileNotFoundError: [Errno 2] No such file or directory: 'uv'`.
  Cause: generated wrapper assumed `uv` exists on PATH.
  Fix: detect `uv` and fall back to `sys.executable`.
- Symptom: repo-local plugin bundle exists but Codex does not show a plugin card.
  Cause: only MCP config/scaffold was installed, not the plugin cache/marketplace enablement.
  Fix: install the local plugin payload and marketplace/config enablement, then restart Codex and verify in a fresh session.
- Symptom: online smoke test fails even though `.env` exists.
  Cause: script does not auto-load `.env`.
  Fix: run `set -a && source ./.env && set +a && <smoke command>`.
- Symptom: dirty tree includes generated or unrelated files.
  Cause: side effects from local UI/testing or pre-existing edits.
  Fix: stage explicit paths only; do not use `git add -A` by default.

## Verification checklist

- Repo root and target workflow are identified from actual files.
- Plugin manifest and marketplace metadata exist where expected.
- Helper scripts compile and run.
- Offline smoke/validation passes.
- Online smoke uses sourced env and redacts secrets from output.
- Root README has concise quick start; plugin README has deeper details.
- `git status --short` confirms only intended files were staged/committed.
- If pushed, branch, commit, and remote tracking are reported.
