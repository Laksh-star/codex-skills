# Skill Release Checklist

Skill: `fork-product-development`

Date: 2026-07-13

## Scope

- Recurring task: maintain an open-source product fork that also carries private/team/client features, while selectively preparing clean upstream pull requests.
- Expected user/community: developers using Codex to work in forked product repos, especially when upstream sync, local app identity, and PR hygiene all matter.
- Explicitly not for: replacing project-specific fork notes, deciding legal/commercial licensing questions, or bypassing upstream maintainer expectations.

## Files

- [x] `SKILL.md`
- [x] `agents/openai.yaml`
- [x] `references/` files, if needed
- [x] scripts/assets, if needed

No scripts or assets are needed for this workflow.

## Validation

- [x] `quick_validate.py` passes
- [x] Manual read-through completed
- [x] Tested against a realistic workspace
- [x] Known limitations documented

Realistic workspace used for shaping and validation: a local Dayflow fork with a long-lived dev branch, a clean upstream PR branch, local app identity, install script, project report, and fork/upstream policy note.

## Publishing

- [x] README link added
- [x] No secrets or private paths
- [x] Install instructions checked
- [x] GitHub description/topics updated

No GitHub description/topic changes are required for this incremental skill addition.
