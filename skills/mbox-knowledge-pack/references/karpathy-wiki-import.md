# Karpathy / Claude Wiki Import

Use this reference when an mbox corpus should feed a local LLM-maintained markdown wiki.

## Default Pattern

Do not create final wiki pages directly. Create raw source packets and let the wiki's compile/lint workflow write final articles.

Typical target:

```text
raw/memories/<collection>/
  README.md
  01-theme-packet.md
  02-theme-packet.md
```

Use `raw/memories/` when the emails are the user's own reflections, self-notes, sent memos, experiments, or operating lessons. Use `raw/feeds/` or `raw/newsletters/` only when the corpus is primarily external publications.

## Packet Shape

Each packet should include:

- source collection and mbox hash
- theme title
- suggested domains/topics from the target wiki
- compile guidance: likely concepts, bridge opportunities, and what not to do
- selected source threads with thread IDs, dates, rationale, evidence message IDs, selected excerpts, and links

## Compile Guidance

Tell the downstream wiki agent:

- synthesize across packets
- avoid one-to-one thread-to-article conversion
- create bridge/framework/entity articles when the wiki supports them
- scan for user aphorisms or voice markers only from user-authored text
- update related existing articles during the compounding step
- run the wiki linter after compile

## What Good Looks Like

A 45-thread email curation might become 8-12 raw packets and then 10-18 final wiki articles, not 45 pages. The wiki should gain durable concepts, backlinks, memory entries, and bridge articles rather than a private email archive dump.
