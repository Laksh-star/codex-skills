# Skill Release Checklist

Skill: `competitive-intelligence-agent`

Date: 2026-06-22

## Scope

- Recurring task: operate, test, document, or extend an agent-first competitive-intelligence workflow with sample data, MCP tools, and optional live CocoIndex/Postgres ingestion.
- Expected users: Codex users, agent builders, and demo authors who want competitor intelligence workflows that other agents can call.
- Explicitly not for: storing secrets, publishing generated private reports, or claiming live CocoIndex execution when only sample data was used.

## Files

- [x] `SKILL.md`
- [x] `agents/openai.yaml`
- [x] `references/cocoindex-agent-demo.md`
- [x] scripts/assets not needed

## Validation

- [x] `quick_validate.py` passes
- [x] Manual read-through completed
- [x] Tested against a realistic competitive-intelligence workspace
- [x] Known limitations documented

## Publishing

- [x] README link added
- [x] No secrets or private paths
- [x] Install instructions checked
- [x] GitHub description/topics do not need immediate changes
