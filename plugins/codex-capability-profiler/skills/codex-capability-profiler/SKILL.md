---
name: codex-capability-profiler
description: Analyze local Codex task history and generate a private capability-maturity dashboard with coverage checks, heuristic feature signals, searchable task logs, and an optional redacted export. Use when a user asks how deeply they use Codex features, wants a repeatable capability audit, or needs to compare their workflow maturity over time. Do not use for token allowance or billing analysis.
---

# Codex Capability Profiler

Build an evidence-labeled view of how the user works with Codex. Measure workflow signals, not token consumption and not personal worth.

## Run The Profiler

Use the bundled builder from the user's chosen output directory:

```bash
node <skill-dir>/scripts/build-capability-report.mjs --out ./codex-capability-report
```

The builder discovers `CODEX_HOME` or defaults to `~/.codex`, merges the newest local `state_*.sqlite` task table with `session_index.jsonl`, reconciles task IDs, and writes `report.html`, `report.md`, and `report.json`.

Use a normalized JSON fixture or export when direct local history is unavailable:

```bash
node <skill-dir>/scripts/build-capability-report.mjs \
  --input ./threads.json \
  --out ./codex-capability-report
```

The input may be an array or `{ "threads": [...] }`. Each thread may include `id`, `title`, `searchText`, `updatedAt`, `archived`, and `sources`.

## Privacy And Sharing

Default output is private and local. Do not upload, publish, commit, or transmit it unless the user explicitly requests that action.

For a shareable report, generate a separate redacted export:

```bash
node <skill-dir>/scripts/build-capability-report.mjs \
  --out ./codex-capability-report-public \
  --redacted
```

Redacted mode removes task titles, IDs, paths, and request context. Never represent a non-redacted report as safe to share.

## Interpretation

- Treat capability matches as heuristic signals from task names and bounded request context.
- Distinguish source coverage from classification coverage. A complete task scan may still contain unclassified tasks.
- State the observable boundary: local Codex sources do not guarantee coverage of cloud conversations absent from the local database.
- Explain score changes using underlying signal counts, recency, and rubric thresholds.
- Avoid comparing users as if the scores were standardized benchmarks. The useful comparison is the same user's trend over time.

Read [references/data-sources.md](references/data-sources.md) when source discovery fails, SQLite fields drift, or coverage is incomplete. The default capability taxonomy is in [references/default-rubric.json](references/default-rubric.json).

## Verification

After changing the builder or rubric, run:

```bash
bash <skill-dir>/scripts/smoke-test.sh
```

Do not claim success unless the builder's ID reconciliation passes and the generated report opens without script errors.
