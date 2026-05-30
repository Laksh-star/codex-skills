# Content OS Blueprint

Use this reference when creating or repairing a Content OS folder.

## Default Target

`./content-os` in the current workspace.

## MVP Structure

```text
content-os/
  README.md
  inbox/
    raw-notes.md
    links.md
  ideas/
    idea-backlog.md
    selected-ideas.md
    parked-ideas.md
    idea-template.md
  drafts/
    active/
    ready-to-publish/
    archived/
    draft-template.md
  feedback/
    feedback-log.md
    analytics-log.md
    feedback-template.md
  published/
    published-index.md
    posts/
    post-template.md
  themes/
    theme-map.md
    weekly-theme-reviews/
    series-ideas.md
  prompts/
    ideas-thread.md
    drafts-thread.md
    weekly-review-thread.md
  automations/
    daily-capture.md
    weekly-review.md
  exports/
    newsletter/
    linkedin/
    x-twitter/
    blog/
```

## Optional Expanded Prompts

Add these only when the user wants the six-thread system:

```text
prompts/router-thread.md
prompts/feedback-thread.md
prompts/published-thread.md
prompts/themes-thread.md
```

## Naming Conventions

Use date-prefixed filenames for drafts and published post records:

```text
YYYY-MM-DD-title.md
```

Use simple IDs inside index files when helpful:

```text
IDEA-001
POST-001
```

## Required Starter Content

`README.md` should explain that this folder is the durable store for the content workflow.

Each log/index file should contain a title, a short purpose statement, and an empty section ready for entries.

Templates should be complete enough for immediate use, but short enough that users will actually fill them in.
