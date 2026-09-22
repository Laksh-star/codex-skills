# Data Sources And Boundaries

## Preferred source order

1. Newest `state_*.sqlite` under `CODEX_HOME`, using the local `threads` table.
2. `session_index.jsonl` as a naming fallback and cross-check.
3. A user-supplied normalized JSON file when local Codex state is unavailable.

The SQLite database is local application state, not a stable public API. Detect columns before querying, keep the query narrow, and fail with a useful diagnostic when the schema changes. If the `sqlite3` command is unavailable, continue with `session_index.jsonl` and label the reduced coverage.

## Completeness contract

For each run, record:

- unique tasks found in each source;
- unique merged task IDs;
- app-database IDs represented in the final Thread Log;
- archived tasks included;
- classified and unclassified task counts.

Fail report generation when an ingested task ID disappears between ingestion and the Thread Log. Do not describe the report as covering cloud ChatGPT conversations that are absent from local Codex state.

## Privacy contract

The normal report is local and may contain task titles and bounded request context. The redacted report must remove:

- task titles and IDs;
- request text;
- filesystem paths;
- project names derived from paths;
- source snippets that could identify a person, company, or private project.

Classification may happen before redaction, but sensitive evidence must not survive in redacted JSON, Markdown, HTML, or DOM data attributes.

## Scoring boundary

The classifier identifies feature-related workflow signals. It does not inspect every transcript turn and does not prove expertise. Scores are most useful as a longitudinal self-comparison, especially when paired with curated evidence and manual review.
