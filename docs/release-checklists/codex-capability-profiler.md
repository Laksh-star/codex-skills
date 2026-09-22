# Codex Capability Profiler Release Checklist

## Privacy

- [ ] Demo assets are generated only from `assets/sample-threads.json`.
- [ ] No local task titles, IDs, paths, request text, or generated private reports are committed.
- [ ] `--redacted` removes sensitive text from JSON, Markdown, HTML, and DOM attributes.
- [ ] Documentation states that normal output is private and local.

## Source Coverage

- [ ] SQLite discovery uses the newest `state_*.sqlite` under `CODEX_HOME`.
- [ ] `session_index.jsonl` remains a fallback and naming cross-check.
- [ ] The report fails when an ingested task ID disappears before the Thread Log.
- [ ] Archived tasks remain included and filterable.
- [ ] Cloud conversations absent from local state are explicitly out of scope.

## Validation

Run from the repository root:

```bash
bash plugins/codex-capability-profiler/skills/codex-capability-profiler/scripts/smoke-test.sh
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/codex-capability-profiler/skills/codex-capability-profiler
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" \
  plugins/codex-capability-profiler
```

- [ ] Private fixture report builds.
- [ ] Redacted fixture report builds and leak checks pass.
- [ ] Local-history smoke test completes without committing its output.
- [ ] Skill validation passes.
- [ ] Plugin validation passes.
- [ ] Dashboard screenshot is visually inspected at desktop width.
- [ ] README links and screenshot render correctly.

## Interpretation

- [ ] Capability classifications are labeled heuristic.
- [ ] Scores are positioned as longitudinal self-review, not cross-user ranking.
- [ ] A complete source scan is not confused with complete classification.
- [ ] Changes in scores can be explained through task counts, recency, and rubric thresholds.
