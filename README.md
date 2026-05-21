# Codex Skills Lab

![Codex Skills](https://img.shields.io/badge/Codex-Skills%20Lab-111827?style=for-the-badge)
![Workflow UI](https://img.shields.io/badge/Agentic%20UI-Workflow%20First-2563eb?style=for-the-badge)
![CopilotKit](https://img.shields.io/badge/CopilotKit-Ready-10b981?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Lab%20Quality-f59e0b?style=for-the-badge)

Reusable Codex skills for turning real workflows into useful AI-assisted software artifacts.

This repo starts with a practical CopilotKit workflow skill: a repeatable way to wrap an existing backend, internal tool, or decision process with a Copilot-powered UI that can read app state, operate frontend tools, render structured workflow surfaces, and preserve explicit human approval gates.

## Skills

| Skill | Purpose | Status |
| --- | --- | --- |
| [`copilotkit-workflow-ui-builder`](skills/copilotkit-workflow-ui-builder/SKILL.md) | Add a CopilotKit UI around an existing workflow or backend. | Validated locally |

## Why This Exists

Most agent UI examples start as chat-first demos. These skills are meant for the harder and more useful path: start with an existing workflow, then add an AI interface that understands the product state and helps move real work forward.

The pattern is:

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
```

Then start a new Codex session and ask for the skill by name, or ask for a task that matches its description.

## Validate A Skill

If you have the Codex skill creator tools available:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/copilotkit-workflow-ui-builder
```

The first skill was validated locally before being added here.

## Repository Standards

- Keep each skill self-contained under `skills/<skill-name>/`.
- Use lowercase hyphen-case skill names.
- Keep `SKILL.md` concise and action-oriented.
- Put deeper workflow details in `references/`.
- Avoid repo-specific secrets, private paths, and fragile local assumptions.
- Add a release checklist entry before publishing a skill publicly.

See [publishing guidelines](docs/publishing-guidelines.md) and the [release checklist template](templates/skill-release-checklist.md).

## Suggested GitHub About Fields

GitHub description:

```text
Reusable Codex skills for building workflow-first AI and CopilotKit interfaces around real apps.
```

Topics:

```text
codex, codex-skills, copilotkit, agentic-ui, ai-agents, developer-tools, workflow-automation
```
