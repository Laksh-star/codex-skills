---
name: wiki-maintainer
description: >
  Build and maintain a personal LLM Wiki: a local, interlinked markdown
  knowledge base compiled from raw sources. Use when the user wants to set up
  a knowledge wiki, ingest or compile sources into it, ask grounded questions
  of it, lint wiki health, find knowledge gaps, generate publishable outputs
  from wiki content, or export a concise context layer for a downstream
  assistant. Triggers include "set up my LLM wiki", "compile my wiki", "add
  this source to my wiki", "ask my wiki", "lint my wiki", "what gaps does my
  wiki have", and "export agent context".
---

# Wiki Maintainer

Maintain a personal LLM Wiki: a local folder of markdown files that Codex compiles and keeps current from the user's raw source material. This adapts the Karpathy LLM Wiki pattern with domains, bridge articles, optional voice capture, publishable outputs, and an agent-export layer.

The human curates sources and asks questions. Codex does the writing and bookkeeping: summarizing, cross-referencing, filing, linting, and logging.

## Architecture

Four layers live in the wiki root:

```text
raw/           Immutable source material. Read but never modify.
               Suggested subfolders: feeds/ books/ videos/ newsletters/
               memories/ journal/ voice/ web/
wiki/          Canonical knowledge base: concept articles, entity articles,
               bridge articles, and meta files such as index.md, inbox.md,
               log.md, voice.md, and about.md.
outputs/       Audience-facing artifacts generated on request.
agent_exports/ Concise context layer for a downstream assistant.
```

Always read the vault's `CLAUDE.md`, `CODEX.md`, `AGENTS.md`, or `wiki/about.md` first if present. Those files define the user's domains, naming, and local conventions and override the defaults here.

## Core Principles

1. Keep memory explicit and visible as plain markdown files.
2. Treat `raw/` as source truth and never edit it.
3. Compile new sources into existing thinking, not just retrieval notes.
4. Compound every ingest by updating related existing articles.
5. Cite sources and flag contradictions instead of silently replacing prior claims.

## Article Frontmatter

Every article should start with:

```yaml
---
title: Human-readable title
tags: [tag1, tag2]
created: YYYY-MM-DD
source: "Full citation"
source_type: feed | book | video | newsletter | memory | journal | voice | web
content_type: informative | explainer | opinion | framework | bridge | entity | memory
status: processed
domains: [domain-a, domain-b]
voice: false
---
```

Derive `source_type` from the `raw/` subfolder when possible. Use only domains declared by the vault.

## Setup A New Vault

When asked to set up a wiki:

1. Confirm the target folder. Create it if needed.
2. Ask for 3-6 domains and whether to enable voice capture.
3. Create:

```text
raw/feeds/ raw/books/ raw/videos/ raw/newsletters/
raw/memories/ raw/journal/ raw/voice/ raw/web/
wiki/
outputs/
agent_exports/
```

4. Write a compact `CODEX.md` at the vault root with the chosen domains, frontmatter rules, bridge-article rule, compounding rule, and the main operations from this skill. If the user also uses Claude Code, writing `CLAUDE.md` with the same content is reasonable.
5. Seed:
   - `wiki/index.md` with a heading for each domain.
   - `wiki/inbox.md` as the processing queue.
   - `wiki/log.md` with `## [YYYY-MM-DD] setup | vault created`.
   - `wiki/about.md` with domains, frontmatter reference, and operation list.
   - `wiki/voice.md` only if voice capture is enabled.
6. Ask before initializing git. If approved, run `git init`, add a small `.gitignore`, and make an initial commit.
7. End with next steps: open the folder in Obsidian or any markdown editor, drop a source under `raw/`, then ask Codex to compile the wiki.

Keep setup idempotent. If important files already exist, report what exists and ask before overwriting.

## Compile Sources

For each new file in `raw/` or a user-specified raw path:

1. Read the vault conventions and determine whether the source is already marked done in `wiki/inbox.md`.
2. Read the source. For PDFs, use `pdftotext` or another available extractor without modifying the original.
3. Create or update a concept/entity/bridge article with full frontmatter, `## Summary`, topic sections, `## Related`, and `## Sources`.
4. Revisit 5-10 related existing articles and update them with links, evidence, or flagged contradictions.
5. Keep `[[wikilinks]]` bidirectional.
6. Capture voice lines only when the vault enables voice capture and only from text the user actually wrote or said.
7. Update `wiki/index.md`, mark the source done in `wiki/inbox.md`, and append to `wiki/log.md`.
8. Summarize sources processed, new articles, updated articles, bridge articles, voice lines, and unresolved questions.

A single source should usually touch multiple wiki pages. If a source is low signal, explain why and leave it unprocessed unless the user asks.

## Bridge Articles

Bridge articles connect two or more declared domains. When a source spans domains:

- Set `content_type: bridge`.
- Add `bridge` to `tags`.
- In `## Summary`, name the connection explicitly, such as `A bridge between ai-strategy and consulting: ...`.

Prefer bridge articles when they capture the user's distinctive synthesis.

## Query The Wiki

For Q&A:

1. Read `wiki/index.md` first.
2. Read only targeted relevant articles.
3. Answer with `[[article]]` citations so the user can verify.
4. Offer to file valuable syntheses back as new pages with `source_type: journal`.

Do not answer from memory alone when the wiki files are available.

## Lint And Repair

Use the bundled scripts when available from this skill folder:

```bash
python3 skills/wiki-maintainer/scripts/lint.py --wiki ./wiki
python3 skills/wiki-maintainer/scripts/backlinks.py --wiki ./wiki
python3 skills/wiki-maintainer/scripts/backlinks.py --wiki ./wiki --fix
```

The linter checks broken links, asymmetric backlinks, orphan pages, and missing frontmatter. With `--fix`, repair asymmetric backlinks only. Contradictions and stale claims require agent review; flag them for the user and do not auto-resolve.

Append a concise lint entry to `wiki/log.md`, for example:

```text
## [YYYY-MM-DD] lint | 4 backlinks repaired, 1 stale claim flagged
```

## Next Actions

For gap analysis:

1. Read `wiki/log.md`, `wiki/index.md`, and domain distribution.
2. Identify thin domains, missing bridge opportunities, concepts mentioned without pages, and questions worth investigating.
3. Separate content gaps from sourcing gaps. If a gap persists across repeated checks, call it a sourcing problem and tell the user what to add to `raw/`.
4. Append a short entry to `wiki/recommendations.md`.

## Outputs

Generate audience-facing artifacts into `outputs/` and never modify `wiki/` unless the user asks for the output to become part of the wiki.

Common formats:

- `medium` -> `outputs/medium--<slug>.md`
- `newsletter` -> `outputs/newsletter--<YYYY-WW>.md`
- `thread` -> `outputs/thread--<slug>.md`
- `deck` -> `outputs/deck--<slug>.md` with Marp frontmatter

Draw only from wiki content and carry citations through.

## Agent Export

Distill the current wiki into short files under `agent_exports/`:

- `wiki-brief.md`
- `active-projects.md`
- `writing-style.md`
- `reusable-frameworks.md`
- `article-pipeline.md`
- `assistant-context.md`

Keep these operational and concise. They orient a downstream assistant without replacing the deeper wiki.

## Helper Script

Use the article scaffold helper for new pages when it saves time:

```bash
python3 skills/wiki-maintainer/scripts/new_article.py --wiki ./wiki \
  --slug forward-deployed-engineer \
  --title "Forward-Deployed Engineer Model" \
  --domains ai-strategy,consulting \
  --source "raw/feeds/fde.md" \
  --source-type feed \
  --type bridge
```

The helper refuses to overwrite existing articles. After creating a scaffold, fill in the article and add bidirectional links.
