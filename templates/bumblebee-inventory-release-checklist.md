# Skill Release Checklist

Skill: `bumblebee-inventory`

Date: 2026-05-24

## Scope

- Handles repeatable Bumblebee package/MCP inventory scans for a current repo or explicit roots.
- Expected users are developers using Codex to operationalize local supply-chain inventory and public-safe reports.
- Does not install Bumblebee automatically, replace vulnerability scanners, or claim that zero inventory findings means secure.

## Files

- [x] `SKILL.md`
- [x] `agents/openai.yaml`
- [x] `references/project-roots.md`
- [x] `scripts/bumblebee_scan.sh`

## Validation

- [ ] `quick_validate.py` passes (`PyYAML` missing in the local validator environment during this check)
- [x] Manual read-through completed
- [x] Tested against realistic public repos: `mcp-server-tmdb` and `greenlighting-agent`
- [x] Known limitations documented
- [x] Fallback frontmatter/YAML shape validation passed

## Publishing

- [x] README link added
- [x] No secrets or private paths
- [x] Install instructions checked
- [ ] GitHub description/topics updated if needed
