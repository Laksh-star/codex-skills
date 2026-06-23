# Skill Release Checklist

Skill: `wiki-maintainer`

Date: 2026-06-23

## Scope

- Recurring task: set up and maintain a local, interlinked markdown LLM Wiki from raw sources, including compile, lint, Q&A, outputs, gap analysis, and agent-export refreshes.
- Expected users: Codex users, knowledge workers, writers, researchers, and agent builders who want a portable plain-markdown personal knowledge base.
- Explicitly not for: modifying raw source files, silently resolving contradictions, storing secrets, or replacing a user's canonical wiki files with hidden agent memory.

## Files

- [x] `SKILL.md`
- [x] `agents/openai.yaml`
- [x] scripts for linting, backlink repair, and article scaffolding
- [x] references/assets not needed

## Validation

- [x] `quick_validate.py` passes
- [x] Manual read-through completed
- [x] Helper scripts compile with Python
- [x] Known limitations documented in `SKILL.md`

## Publishing

- [x] README link added
- [x] No secrets or private paths
- [x] Install instructions checked
- [x] GitHub description/topics do not need immediate changes
