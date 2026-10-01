# Codex Capability Profiler 0.2.1 release checklist

This is a skills-only release candidate. Local validation does not establish OpenAI directory acceptance. See the [plugin README](../../plugins/codex-capability-profiler/README.md) and [privacy policy](../../plugins/codex-capability-profiler/PRIVACY.md).

## Privacy and source coverage

- [x] Demo assets use only the 24-task synthetic fixture.
- [x] Context is opt-in for classification and output storage.
- [x] Redaction removes titles, IDs, source labels, context, and per-task dates from JSON, Markdown, HTML, and DOM attributes.
- [x] Documentation explains retained aggregates, execution-host storage, host-assistant processing, and the need to review redaction.
- [x] SQLite queries are read-only; a synthetic database remains byte-identical after analysis.
- [x] Missing SQLite, unreadable database, missing index, and malformed index rows surface reduced coverage.
- [x] ID reconciliation and heuristic classification coverage are distinct.
- [x] Cloud history absent from the local sources is out of scope.
- [x] Private/redacted output collision and source-input overwrite are refused.
- [x] The exact package allowlist excludes user history and generated reports.

## Repeatable validation

Run from the repository root. Developer validation tools use temporary dependencies; the report builder has no third-party runtime packages.

```sh
bash plugins/codex-capability-profiler/skills/codex-capability-profiler/scripts/smoke-test.sh
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/codex-capability-profiler/skills/codex-capability-profiler
python3 tools/build-profiler-release.py --out /your/release-output
```

The packer checks matching manifests, asset references, icon dimensions, public name lengths, version, local path exclusions, and an exact file allowlist. It excludes the repository-only synthetic screenshot because skills-only directory submissions cannot declare screenshots. It produces a deterministic ZIP, SHA256SUMS, and package-receipt.json. It is a local structural check, not OpenAI's submission validator.

Validate plugin.json against the official schema at https://agent-plugins.org/schemas/1.0.0/plugin.schema.json using a JSON Schema validator. OpenAI extension fields need the current directory tooling/review as well.

- [x] Fixture smoke checks and 12 privacy/source regression checks pass.
- [x] Skill Creator frontmatter validation passes.
- [x] Portable manifest passes the official Agent Plugins 1.0.0 schema.
- [x] Desktop (1440px) and mobile (390px) checks pass without page errors or page overflow.
- [x] Search, archived and unclassified filters work against the synthetic fixture.
- [x] Live local-history scan reconciles the ingested task IDs; outputs are outside the repository and ZIP.

Extract the final ZIP into a fresh directory and run its packaged smoke script before submission. Use its receipt hash to identify the exact archive.

## Reviewer scenarios

1. Ask to profile local Codex workflows. Expect private files, source scope, counts, heuristic limitations, and no upload.
2. Use the bundled synthetic export where no local database exists. Expect 24 tasks, including two archived tasks; all IDs represented.
3. Ask for a redacted report in a separate output directory. Expect generic labels, hidden task dates, aggregate caveats, and a review reminder.
4. Ask about token allowance or billing. Expect this skill to stay outside that request and refer to the appropriate host capability.
5. Run without local history or supplied export. Expect a clear limitation and no fabricated analysis.
6. Attempt to reuse a private output directory for redacted data or overwrite the input file. Expect refusal while preserving original files.

These are recommended prompts and expected behavior, not a claim of end-to-end assistant installation or portal review.

## Public release remains pending

- [x] Repository publication authorized; implementation merged in PR #2.
- [x] Privacy/support/usage pages published on main; HTTP and rendered browser checks passed.
- [ ] Confirm publisher identity, ownership, and directory access.
- [x] Codex marketplace installation confirms version 0.2.1, enabled; the installed builder passes the synthetic sample.
- [ ] Complete OpenAI portal validation and resolve eligibility feedback.
- [ ] Upload the exact ZIP and complete required scans/review.
- [ ] Explicitly publish after acceptance.

No developer telemetry, MCP server, account integration, payment flow, upgrade promotion, or monetization claim is included. A paid team product requires a separate product and policy assessment.

## Public release status: 1 October 2026

[GitHub release 0.2.1](https://github.com/Laksh-star/codex-skills/releases/tag/capability-profiler-v0.2.1) provides the tested ZIP and SHA256SUMS. GitHub asset digest matches the locally validated archive.

OpenAI draft creation is blocked at the verified developer identity requirement. No package has been uploaded there, and portal scans, review, and directory publication have not occurred. Resolve the account prerequisite before continuing; GitHub publication is separate from directory availability.
