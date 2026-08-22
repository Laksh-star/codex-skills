# Privacy And Verification

Email exports are private by default. Preserve analytical utility without exposing raw mailbox details.

## Local-First Rules

- Keep original mbox untouched.
- Write derived artifacts locally.
- Do not upload, email, or publish outputs without explicit user approval.
- Use source hashes and stable IDs for provenance.

## Redaction Rules For Shareable Outputs

Remove or mask:

- email addresses and raw recipient lists
- phone numbers and physical addresses
- local absolute paths
- message IDs when they identify private systems
- sensitive client/internal references
- attachments unless reviewed

Keep:

- stable generated IDs
- dates at useful granularity
- themes and summaries
- non-sensitive source domains
- evidence IDs for local audit

## Verification Checks

A useful pack should verify:

- parsed message count equals mbox count
- JSONL files are valid
- SQLite counts match JSONL counts
- links reference known message IDs
- thread records reference known message IDs
- curated recommendations include evidence message IDs
- fine-tune examples are split and do not duplicate across train/validation/holdout

## Reporting Language

Call deterministic extraction `parsed` or `extracted`. Call keyword/topic logic `heuristic`. Call handpicked lists `curated` only when an agent or human has reviewed them against explicit criteria.
