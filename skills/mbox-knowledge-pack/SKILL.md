---
name: mbox-knowledge-pack
description: "Convert local .mbox email exports into local-first knowledge packs for analysis, curation, wiki compile staging, writing projects, and optional fine-tuning dataset preparation. Use when asked to analyze an mbox, summarize old emails, curate email threads, prepare a Karpathy/Claude-style wiki raw import, or derive supervised examples from an email corpus. Do not use for live mailbox operations."
---

# Mbox Knowledge Pack

Use this skill when the user has a local `.mbox` export and wants to turn it into a structured, private knowledge asset. The default outcome is an analysis pack, not a public archive or live-mail action.

## Boundaries

- Work locally from files the user provides or points to.
- Never mutate the original mbox.
- Do not upload, send, or publish email content.
- Do not fetch links by default; record URL provenance unless the user asks for link checking.
- Do not create final wiki pages directly for a Claude/Karpathy wiki unless the user explicitly asks. Prefer raw compile packets.
- Treat fine-tuning as an optional advanced preparation mode, never the default.

## Core Workflow

1. Inspect the mbox and output location.
2. Parse messages safely: MIME decoding, dates, subjects, message IDs, thread IDs when available, labels, plain text bodies, URLs, and attachment metadata.
3. Build a local analysis pack:
   - `messages.jsonl`
   - `threads.jsonl`
   - `links.jsonl`
   - `attachments/manifest.jsonl`
   - `analysis.sqlite`
   - `manifest.json`
   - `summary.json`
4. Produce reports: corpus profile, timeline, theme map, source/domain signals, and import/defer/exclude recommendations.
5. If requested, curate strongest threads into a smaller first batch with evidence message IDs and rationale.
6. If a wiki target is provided, prepare raw source packets that match that wiki's compile conventions.
7. If writing output is requested, create book/article concept notes and outlines grounded in selected threads.
8. If fine-tuning prep is requested, create a separate redacted dataset candidate pack and audit report.

## Helper Script

Use the bundled helper when a deterministic local pack is useful:

```bash
python3 skills/mbox-knowledge-pack/scripts/mbox_knowledge_pack.py   --mbox /absolute/path/export.mbox   --out /absolute/path/analysis-pack
```

Optional modes:

```bash
python3 skills/mbox-knowledge-pack/scripts/mbox_knowledge_pack.py   --mbox /absolute/path/export.mbox   --out /absolute/path/analysis-pack   --fine-tune-prep
```

The script is intentionally conservative. It extracts and scores; it does not claim semantic understanding equivalent to a manual review.

## Wiki Import

Read `references/karpathy-wiki-import.md` when the target is a Claude/Karpathy-style markdown wiki, especially one with `CLAUDE.md`, `CODEX.md`, or `WIKI-JOURNEY.md` conventions.

Important default: generate grouped raw packets under a target such as `raw/memories/<collection>/`; let that wiki's `/compile` and `/lint` commands create final articles and backlinks.

## Fine-Tuning Prep

Read `references/fine-tuning-prep.md` before creating model-training files. Email archives are usually noisy, private, and copyright-mixed. Prepare fine-tuning datasets only from explicitly selected/approved material, with redaction, split separation, and an audit report.

## Privacy And Verification

Read `references/privacy-and-verification.md` when creating shareable exports, wiki packs, or fine-tune datasets. Preserve provenance while removing private addresses, raw recipient lists, local absolute paths, and sensitive context from public-facing outputs.

## Reporting Rules

- State which outputs are deterministic extraction vs heuristic analysis vs human-curated recommendation.
- Include counts and source hashes in manifests.
- Keep evidence IDs so recommendations can be traced back to source messages.
- Distinguish `import`, `defer`, and `exclude`; never imply every email deserves promotion.
- For fine-tuning, distinguish RAG/search suitability from supervised-training readiness.
