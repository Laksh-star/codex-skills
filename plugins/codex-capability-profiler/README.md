# Codex Capability Profiler

Version 0.2.1. An independent community plugin; not affiliated with or endorsed by OpenAI.

Understand recurring Codex workflows using evidence from local task history or a supplied export. Generate local HTML, Markdown, and JSON reports with ten heuristic capability areas, a searchable task log, archived tasks, and explicit source-coverage warnings.

Requires **Node.js 22 or later**. `sqlite3` is optional for reading the local task database; without it, the report explains the reduced scope. No API key, account registration, hosted service, or network connection is required by the builder.

## Start

After installing from a supported local marketplace, ask:

> Profile my local Codex capability maturity.

Or run the packaged builder from your chosen output location:

```sh
node skills/codex-capability-profiler/scripts/build-capability-report.mjs --out ./private-report
```

On a host without local Codex history, supply an export:

```sh
node skills/codex-capability-profiler/scripts/build-capability-report.mjs --input ./threads.json --out ./private-report
```

The export is a non-empty task array or an object with a `threads` array. Task fields include `id`, `title`, `updatedAt`, `archived`, and optional `searchText`. Duplicate IDs are rejected. Missing IDs receive synthetic identifiers for this input only.

## Privacy

Reports stay on the chosen execution host. Private output contains task titles. Request context is used and retained only with `--include-context`. Do not place output inside your source archive or a public repository.

Generate a separate redacted report with `--redacted` and a different output directory. Titles, task IDs, source labels, request context, and per-task dates are removed. Aggregate usage patterns and custom rubric labels can still be sensitive; review before sharing.

[Privacy details](PRIVACY.md) · [Support](SUPPORT.md) · [License](LICENSE)

## Interpretation and scope

Scores are keyword-based workflow signals, not validated expertise scores, billing figures, or a comparison with all Codex users. Repeated scheduled tasks can dominate the evidence. A score of zero means no observed signal in the chosen source, not that the user lacks that capability.

Local Codex database formats may change. Cloud ChatGPT conversations absent from local sources are outside scope. Source reconciliation and classification coverage are reported separately. Trend comparisons require a consistent rubric, evidence mode, and history scope.

## Example and validation

The bundled sample contains **24 synthetic tasks**, never personal history. A sample report can be built using `--input skills/codex-capability-profiler/assets/sample-threads.json`.

Run `bash skills/codex-capability-profiler/scripts/smoke-test.sh` on a macOS/Linux development host. It checks fixture reports and privacy/source-handling regressions. This package has no MCP server, app connector, lifecycle hooks, or in-plugin commerce.

The ZIP and portable manifest are release candidates. Local checks do not establish OpenAI directory acceptance.
