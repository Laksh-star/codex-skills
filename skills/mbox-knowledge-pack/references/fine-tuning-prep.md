# Fine-Tuning Preparation

Mbox knowledge packs can support fine-tuning preparation, but raw emails should not become training data automatically.

## When To Use

Use fine-tune prep only when the user explicitly asks to prepare a dataset for model training or distillation.

Good candidate tasks:

- raw article -> user-style summary
- transcript -> script or show notes
- Telugu/local-language source -> English adaptation
- AI output -> verified/humanized revision
- messy instruction -> improved prompt
- source material -> management insight or framework

## Required Outputs

Create a separate folder such as:

```text
fine-tune-prep/
  candidates.jsonl
  train.jsonl
  validation.jsonl
  holdout.jsonl
  dataset-card.md
  audit-report.md
```

Use provider-compatible chat JSONL only after the target provider/schema is known. Until then, use candidate records with explicit fields:

```json
{"id":"...","task":"article_to_summary","input":"...","output":"...","source_message_ids":["..."],"redaction":"applied","review_status":"needs_human_review"}
```

## Guardrails

- Use only selected/approved messages or threads.
- Redact email addresses, private names when needed, local paths, phone numbers, IDs, and sensitive internal context.
- Exclude forwarded copyrighted material unless the output is a user-authored transformation and the source is represented only minimally.
- Keep train, validation, and holdout separated.
- Preserve source provenance in metadata, not in model-visible text unless needed.
- Mark all unreviewed examples as `needs_human_review`.
- Do not claim the dataset is training-ready until format validation and human review pass.

## RAG vs Fine-Tuning

Most email corpora are better first used for RAG/search/wiki memory. Fine-tuning is appropriate only for repeated behavior patterns: style, transformation, classification, or judgment tasks with clean input-output examples.
