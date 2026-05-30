# Codex Skills

![Codex Skills](https://img.shields.io/badge/Codex-Skills-111827?style=for-the-badge)
![Workflow UI](https://img.shields.io/badge/Agentic%20UI-Workflow%20First-2563eb?style=for-the-badge)
![CopilotKit](https://img.shields.io/badge/CopilotKit-Ready-10b981?style=for-the-badge)
![Plugins](https://img.shields.io/badge/Plugins-Repo%20Packaging-7c3aed?style=for-the-badge)
![Cloudflare](https://img.shields.io/badge/Cloudflare-Remote%20MCP-f97316?style=for-the-badge)
![Content OS](https://img.shields.io/badge/Content%20OS-Codex%20Threads-14b8a6?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Validated-f59e0b?style=for-the-badge)

Reusable Codex skills for turning real workflows into useful AI-assisted software artifacts.

This repo collects practical skills built from real Codex work: workflow-first CopilotKit interfaces, repo-local plugin packaging, and other repeatable engineering patterns that are useful beyond a single project.

## Skills

| Skill | Purpose | Status |
| --- | --- | --- |
| [`copilotkit-workflow-ui-builder`](skills/copilotkit-workflow-ui-builder/SKILL.md) | Add a CopilotKit UI around an existing workflow or backend. | Validated locally |
| [`repo-plugin-packaging`](skills/repo-plugin-packaging/SKILL.md) | Turn an existing project into a shareable repo-local Codex plugin. | Validated locally |
| [`cloudflare-remote-mcp-worker`](skills/cloudflare-remote-mcp-worker/SKILL.md) | Deploy an MCP-capable repo as a Cloudflare Worker with remote `/mcp` verification. | Validated locally |
| [`bumblebee-inventory`](skills/bumblebee-inventory/SKILL.md) | Run Bumblebee package/MCP inventory scans and generate raw, public, and agent-ready reports. | Validated locally |
| [`content-os-manager`](skills/content-os-manager/SKILL.md) | Set up a markdown Content OS with Codex thread prompts for ideas, drafts, feedback, published posts, and themes. | Validated locally |

## Why This Exists

Most agent UI examples start as chat-first demos. These skills are meant for the harder and more useful path: start with an existing workflow, then add an AI interface that understands the product state and helps move real work forward.

The working pattern is:

1. Inspect the existing app and backend.
2. Map workflow state into copilot context.
3. Register narrow frontend tools for app control.
4. Render structured UI for evidence, decisions, approvals, and outputs.
5. Keep human gates visible.
6. Validate with real build, smoke, and browser checks where possible.
7. Produce handoff notes that a builder or community reader can reuse.

## Install A Skill Locally

From this repo:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/copilotkit-workflow-ui-builder "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/repo-plugin-packaging "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/cloudflare-remote-mcp-worker "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/bumblebee-inventory "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/content-os-manager "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Then start a new Codex session and ask for the skill by name, or ask for a task that matches its description.

## Validate A Skill

If you have the Codex skill creator tools available:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/copilotkit-workflow-ui-builder

python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/repo-plugin-packaging

python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/cloudflare-remote-mcp-worker

python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/bumblebee-inventory

python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/content-os-manager
```

Each published skill is validated locally before being added here.

## Repository Standards

- Keep each skill self-contained under `skills/<skill-name>/`.
- Use lowercase hyphen-case skill names.
- Keep `SKILL.md` concise and action-oriented.
- Put deeper workflow details in `references/`.
- Avoid repo-specific secrets, private paths, and fragile local assumptions.
- Add a release checklist entry before publishing a skill publicly.

See [publishing guidelines](docs/publishing-guidelines.md) and the [release checklist template](templates/skill-release-checklist.md).

Only validated, reusable skills are published under `skills/`.

## Suggested GitHub About Fields

GitHub description:

```text
Reusable Codex skills for building workflow-first AI and CopilotKit interfaces around real apps.
```

Topics:

```text
codex, codex-skills, copilotkit, agentic-ui, ai-agents, developer-tools, workflow-automation
```
