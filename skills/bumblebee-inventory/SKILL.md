---
name: bumblebee-inventory
description: Run repeatable Bumblebee supply-chain inventory scans against the current repo or explicit repo roots, including package metadata, MCP JSON configs, raw NDJSON preservation, sanitized public reports, and AI coding agent handoff notes. Use when asked to scan projects with Bumblebee, check package exposure, inventory MCP configs, run a supply-chain scan, or create public-safe dependency inventory reports.
---

# Bumblebee Inventory

Use this skill to run a local, read-only Bumblebee inventory workflow and turn the results into both raw audit artifacts and public-safe summaries.

## Quick Start

Prefer the bundled script:

```bash
skills/bumblebee-inventory/scripts/bumblebee_scan.sh roots
skills/bumblebee-inventory/scripts/bumblebee_scan.sh inventory
skills/bumblebee-inventory/scripts/bumblebee_scan.sh inventory --only-root /path/to/repo
skills/bumblebee-inventory/scripts/bumblebee_scan.sh exposure --catalog /path/to/catalog.json
```

If `bumblebee` is not installed, report the script's install guidance. Do not auto-install tools unless the user asks.

Outputs are written under:

```text
${BUMBLEBEE_RUNS_DIR:-./bumblebee-runs}/<timestamp>/
```

Each scan run emits:

- `inventory.ndjson` and `diagnostics.ndjson` for raw local audit.
- `summary.md` and `report.html` for local review.
- `public-report.html`, `public-summary.md`, `agent-notes.md`, and `sanitized-inventory.ndjson` for public writeups or AI-agent handoff.

## Workflow

1. Run `roots` first when checking what will be scanned.
2. Run `inventory` for routine scans. This uses Bumblebee's `project` profile.
3. Run `exposure --catalog <path>` only when the user provides or points to an exposure catalog.
4. Use a single explicit root for publishable examples:

```bash
skills/bumblebee-inventory/scripts/bumblebee_scan.sh inventory --only-root "$(pwd)"
```

5. Use `public-report.html` and `public-summary.md` for article/public sharing. Keep raw local reports private.

## Reporting

Summarize:

- output directory
- scanned roots
- ecosystems seen
- package records, finding records, and MCP config records
- high-confidence package count
- diagnostic warning/error count
- any skipped roots

Be precise about interpretation: an inventory run with zero findings is not a security verdict. Exposure checks require a reviewed catalog.

## References

Read `references/project-roots.md` when deciding how to choose scan roots or how to adapt the default root selection for a local workspace.
