# Content OS Integrations

Use this reference only when the user asks for connector, automation, or ingestion workflows.

## Default Safety Rules

- Do not access Teams, Slack, email, Readwise, or analytics unless the user explicitly asks.
- Do not send or post outbound messages unless the user explicitly asks.
- Prefer draft-first behavior for outbound communication.
- Summarize candidate feedback before writing it into the Content OS unless the user asks for direct routing.

## Teams Feedback Workflow

Use when the user asks to capture feedback from Microsoft Teams.

1. Resolve the Teams scope:
   - project/channel/chat name
   - date range
   - topic or post title
2. Search/read relevant Teams messages using available Teams connector tools.
3. Extract only content-relevant feedback:
   - comments on a draft or post
   - objections
   - confusing sections
   - praise from target readers
   - suggested follow-ups
4. Present candidate entries for review.
5. If approved, append structured entries to `feedback/feedback-log.md`.

Feedback entry format:

```markdown
## YYYY-MM-DD - <short source/title>

- Post:
- Source: Teams
- Feedback:
- Type: Praise / Confusion / Objection / Correction / Suggestion / Metric signal
- Importance: Low / Medium / High
- Action:
- Related theme:
```

## Slack Feedback Workflow

Use the same review-first pattern as Teams:

1. Resolve channel/user/thread/date range.
2. Search or read relevant messages.
3. Extract candidate content feedback.
4. Ask for approval before writing unless direct routing was requested.

## Email Feedback Workflow

Use when the user asks to process reader replies, newsletter feedback, or editorial email.

1. Search email for the requested topic, sender, or post title.
2. Fetch full message bodies only when needed.
3. Extract feedback into the standard feedback entry format.
4. Do not reply or forward unless the user explicitly asks.

## Readwise Or Reader Workflow

Use when the user asks to import highlights or saved articles.

Route:
- raw highlights to `inbox/raw-notes.md`
- article links to `inbox/links.md`
- polished idea candidates to `ideas/idea-backlog.md`

## Analytics Workflow

Use when the user provides metrics manually or via export.

Store performance notes in `feedback/analytics-log.md` and link them to the matching post record in `published/`.

Do not invent missing metrics.

## Automations

Create automations only when the user asks.

Good defaults:

- Daily capture: review inbox and route raw notes.
- Weekly review: update themes and recommend next posts.
- Post-publish review: create published record and start feedback tracking.

Automation prompts should be self-contained and should point to the absolute Content OS folder path.

