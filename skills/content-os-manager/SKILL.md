---
name: content-os-manager
description: Set up and operate a markdown-based Content OS for tracking content ideas, drafts, feedback, published posts, and recurring themes. Use when the user asks to create a content OS, initialize content-os folders/templates, create Codex content threads, route writing notes, or optionally ingest Teams/Slack/email feedback into a review-first content workflow.
---

# Content OS Manager

Use this skill to set up and run a local markdown Content OS. The default mode is a setup assistant: create durable folders, templates, and thread prompts, then guide or create Codex threads when thread tools are available.

Do not treat this as an always-running service. Threads and automations only run when the user asks or when the environment has explicit thread/automation tools and the user approves creating them.

## Quick Start

1. Choose the target folder:
   - Use the user-provided folder when specified.
   - Otherwise default to `./content-os` in the current workspace.
2. Read `references/content-os-blueprint.md` for the folder and file layout.
3. Run `scripts/create_content_os.py --target <folder>` to create the starter structure.
4. Read `references/thread-prompts.md` and create or suggest the three MVP threads:
   - `Content Ideas Thread`
   - `Content Drafts Thread`
   - `Content Weekly Review Thread`
5. Only read `references/integrations.md` when the user asks for Teams, Slack, email, Readwise, analytics, or automation integration.

## Setup Rules

- Keep the default setup small: MVP folders and three thread prompts.
- Do not overwrite existing user content unless the user explicitly asks; pass `--force` only after confirmation.
- Store durable content in markdown files, not only thread memory.
- Keep thread responsibilities narrow.
- Treat the router, feedback, published, and themes specialist threads as optional expansion beyond the MVP.

## Thread Creation Rules

When thread-management tools are available, use them only after the target folder exists and prompt files have been created.

Create each thread with an initial prompt that includes:

- The thread name and role.
- The absolute `content-os` folder path.
- The relevant prompt from `prompts/`.
- A rule to modify only the relevant Content OS files unless the user asks otherwise.

If thread tools are unavailable, give the user the exact thread names and prompt file paths to start manually.

## Integration Rules

Teams, Slack, email, Readwise, and analytics are opt-in.

- Do not read connector data automatically.
- Do not post or send messages unless the user explicitly asks.
- Prefer draft/review-first behavior for outbound messages.
- For feedback ingestion, summarize candidate feedback first, then route approved items into `feedback/feedback-log.md`.

Read `references/integrations.md` before using any connector workflow.

## Common Requests

For "set up my Content OS":

- Run the setup script with the default or requested target folder.
- Report the created folder and the three prompt files.
- Offer the three MVP thread names if thread creation was not requested.

For "create the three threads":

- Confirm the `content-os` folder exists.
- Read the prompt files.
- Use available thread tools to create `Content Ideas Thread`, `Content Drafts Thread`, and `Content Weekly Review Thread`, or provide copy-paste prompts.

For "pull Teams feedback into my Content OS":

- Read `references/integrations.md`.
- Ask for the Teams chat/channel/project scope if it is not provided.
- Search and summarize candidate feedback.
- Ask for approval before writing feedback entries if the user has not already requested direct routing.
