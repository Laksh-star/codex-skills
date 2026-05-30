#!/usr/bin/env python3
"""Create a markdown Content OS folder without overwriting existing files by default."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_TARGET = Path.cwd() / "content-os"


DIRS = [
    "inbox",
    "ideas",
    "drafts/active",
    "drafts/ready-to-publish",
    "drafts/archived",
    "feedback",
    "published/posts",
    "themes/weekly-theme-reviews",
    "prompts",
    "automations",
    "exports/newsletter",
    "exports/linkedin",
    "exports/x-twitter",
    "exports/blog",
]


FILES = {
    "README.md": """# Content OS

This folder is the durable store for a Codex-assisted content workflow.

Use it to track:

- Ideas
- Drafts
- Feedback
- Published posts
- Recurring themes

Start with `inbox/raw-notes.md`, then move strong ideas into `ideas/selected-ideas.md`.
""",
    "inbox/raw-notes.md": """# Raw Notes

Unprocessed thoughts, clips, quotes, and observations.

## Entries
""",
    "inbox/links.md": """# Links

Unprocessed links that may become ideas, examples, or references.

## Entries
""",
    "ideas/idea-backlog.md": """# Idea Backlog

Structured content ideas.

## Ideas
""",
    "ideas/selected-ideas.md": """# Selected Ideas

Ideas chosen for drafting soon.

## Selected
""",
    "ideas/parked-ideas.md": """# Parked Ideas

Interesting ideas that are not urgent.

## Parked
""",
    "ideas/idea-template.md": """# Idea

## One-Line Idea

## Source

## Why It Matters

## Possible Angle

## Target Audience

## Format

- Newsletter
- Blog post
- X thread
- LinkedIn post
- Video
- Podcast segment
- Internal memo

## Status

- Raw
- Promising
- Selected
- Drafted
- Published
- Parked

## Related Ideas

## Notes
""",
    "drafts/draft-template.md": """# Draft Title

## Status

outline

## Source Idea

## Target Audience

## Core Thesis

## Outline

1.
2.
3.

## Draft

## Open Questions

## Revision Notes

## Publishing Plan

- Platform:
- Target date:
- Supporting assets:
- CTA:
""",
    "feedback/feedback-log.md": """# Feedback Log

Reader, editor, teammate, and audience feedback.

## Entries
""",
    "feedback/analytics-log.md": """# Analytics Log

Performance observations for published content.

## Entries
""",
    "feedback/feedback-template.md": """# Feedback Entry

## Post

## Source

## Feedback

## Type

- Praise
- Confusion
- Objection
- Correction
- Suggestion
- Follow-up idea
- Metric signal

## Importance

- Low
- Medium
- High

## Action

## Related Theme
""",
    "published/published-index.md": """# Published Index

Catalog of shipped content.

## Posts
""",
    "published/post-template.md": """# Published Post

## Title

## URL

## Publish Date

## Platform

## Format

## Topic

## Core Thesis

## Target Audience

## Performance Metrics

- Views:
- Opens:
- Clicks:
- Replies:
- Shares:
- Saves:
- Conversions:

## Feedback Summary

## What Worked

## What Did Not Work

## Follow-Up Ideas

## Related Themes
""",
    "themes/theme-map.md": """# Theme Map

Recurring topics, arguments, audience questions, and series opportunities.

## Current Themes

## Emerging Themes

## Series Ideas
""",
    "themes/series-ideas.md": """# Series Ideas

Potential multi-post content series.

## Ideas
""",
    "prompts/ideas-thread.md": """# Content Ideas Thread

You are my content ideas tracker.

Content OS path: `<CONTENT_OS_PATH>`

Your job:
- Capture new content ideas.
- Classify each idea by topic, audience, format, and urgency.
- Merge duplicate or overlapping ideas.
- Maintain `ideas/idea-backlog.md`.
- Move strong near-term ideas into `ideas/selected-ideas.md`.
- Move interesting but non-urgent ideas into `ideas/parked-ideas.md`.

Rules:
- Use `inbox/raw-notes.md` and `inbox/links.md` as unprocessed sources.
- Do not edit drafts unless I explicitly ask.
- Keep entries structured and concise.
""",
    "prompts/drafts-thread.md": """# Content Drafts Thread

You are my drafting assistant.

Content OS path: `<CONTENT_OS_PATH>`

Your job:
- Turn selected ideas into outlines.
- Turn outlines into rough drafts.
- Revise drafts while preserving my voice.
- Track draft status.
- Identify weak arguments, missing examples, and unclear sections.

Storage:
- Read from `ideas/selected-ideas.md`.
- Store active work in `drafts/active/`.
- Move finished work to `drafts/ready-to-publish/`.
- Move stale or abandoned work to `drafts/archived/`.
""",
    "prompts/weekly-review-thread.md": """# Content Weekly Review Thread

You are my weekly content reviewer.

Content OS path: `<CONTENT_OS_PATH>`

Your job:
- Review ideas, active drafts, feedback, published posts, and theme notes.
- Update `themes/theme-map.md`.
- Recommend what to write next.
- Identify recurring themes and series opportunities.

Weekly output:
- Top recurring themes.
- 5 recommended next posts.
- Drafts to continue.
- Drafts to pause or archive.
- Feedback patterns.
- One larger essay or series opportunity.
""",
    "automations/daily-capture.md": """# Daily Capture

Review inbox notes and links, then route them into ideas, feedback, or published records.
""",
    "automations/weekly-review.md": """# Weekly Review

Review ideas, drafts, feedback, published posts, and themes. Recommend next writing priorities.
""",
}


OPTIONAL_PROMPTS = {
    "prompts/router-thread.md": "# Content Router Thread\n\nRoute notes, links, comments, metrics, drafts, and ideas into the correct Content OS files.\n",
    "prompts/feedback-thread.md": "# Content Feedback Thread\n\nTrack reader, editor, teammate, Teams, Slack, email, and analytics feedback.\n",
    "prompts/published-thread.md": "# Published Content Thread\n\nMaintain the published content archive and post records.\n",
    "prompts/themes-thread.md": "# Content Themes Thread\n\nAnalyze recurring themes, series opportunities, and audience patterns.\n",
}


def write_file(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return "exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "written"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a markdown Content OS.")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help="Target content-os folder.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--expanded", action="store_true", help="Also create optional expanded thread prompts.")
    args = parser.parse_args()

    target = args.target.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    for rel in DIRS:
        (target / rel).mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    for rel, content in FILES.items():
        status = write_file(target / rel, content.replace("<CONTENT_OS_PATH>", str(target)), args.force)
        if status == "written":
            written += 1
        else:
            skipped += 1

    if args.expanded:
        for rel, content in OPTIONAL_PROMPTS.items():
            status = write_file(target / rel, content.replace("<CONTENT_OS_PATH>", str(target)), args.force)
            if status == "written":
                written += 1
            else:
                skipped += 1

    print(f"Content OS target: {target}")
    print(f"Directories ensured: {len(DIRS)}")
    print(f"Files written: {written}")
    print(f"Files skipped: {skipped}")
    if skipped and not args.force:
        print("Existing files were preserved. Re-run with --force to overwrite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
