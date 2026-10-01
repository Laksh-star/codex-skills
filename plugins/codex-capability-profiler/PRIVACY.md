# Capability Profiler privacy

Version 0.2.1 · 1 October 2026

## What the builder reads

When asked to profile local history, the script reads task metadata from the newest local Codex state database and session index on the execution host. It queries task identifiers, names/titles, timestamps, and lifecycle fields in read-only mode. It does not read full conversation rollout files, credentials, browser history, email, or payment information.

Alternatively, it reads the task JSON file you supply. A task title may itself contain request text. Titles are bounded to 240 characters; optional request context is bounded to 1,600 characters. Context is used and retained only when `--include-context` is selected.

## Processing and recipients

The deterministic builder makes no network requests and has no developer telemetry, hosted database, account system, or automatic upload. Reports are written to the location you choose on the execution host, which may be your own computer or another configured execution environment.

When you use the skill through ChatGPT or Codex, the host assistant may read source material, command output, or reports to answer your request. Those interactions remain subject to that platform's data practices and your workspace settings. This policy does not imply that using an assistant is offline.

## Reports and retention

Private reports retain task titles, dates, lifecycle, capability signals, and aggregate counts. Explicit context mode also retains bounded request context. Redacted reports remove task IDs, titles, source labels, request context, and per-task dates. They retain counts, capability/rubric labels, lifecycle flags, timezone, and report generation time. Redaction is not guaranteed anonymity.

Generated files remain until you delete them from the execution host. The builder has no background service or retention schedule and does not modify or delete the source history. Delete the selected report directory to remove generated files; source-file retention is controlled by you and the host product.

## Your controls

Choose which source/export to use, keep context mode off, generate a separate redacted report, review it before sharing, and delete outputs when no longer needed. Generated reports are not sent to the plugin developer. Sharing, publishing, or committing a report requires your separate instruction.

For assistance, follow [Support](SUPPORT.md). Use synthetic/redacted examples and omit secrets or personal task history from public issues.
