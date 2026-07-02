# Dataset Schemas

Use these schemas as starting points. Adapt fields to the user's domain instead of forcing editorial or financial names.

## Final-Label JSONL

Each line should be one example:

```json
{
  "id": "example_0001",
  "input": {
    "headline": "Short item title",
    "summary": "One or two sentence source text",
    "source_type": "article",
    "context": "Optional platform, market, team, workflow, or user request context"
  },
  "final_label": "needs_expert_review",
  "recommended_action": "send_for_review",
  "risk_level": "medium",
  "expert_notes": "Short adjudication reason",
  "data_origin": "seed|expert_review|repair|stress|holdout",
  "failure_bucket": "optional_bucket_name"
}
```

Recommended required fields:

- `id`
- input text fields such as `headline`, `summary`, or `text`
- `final_label`
- `recommended_action` when labels and actions are not identical
- `data_origin`

## Rubric-First JSONL

Use this when final labels are too brittle or hide multiple judgments.

```json
{
  "id": "example_0001",
  "input": {
    "headline": "Short item title",
    "summary": "Source text"
  },
  "rubric": {
    "timeliness": "timely",
    "urgency": "routine",
    "durability": "short_lived",
    "expert_value": "normal",
    "risk_level": "low",
    "verification_need": "standard",
    "content_quality": "adequate",
    "recommended_action": "publish_normally",
    "final_label_candidate": "normal_publish"
  },
  "derived_final_label": "normal_publish",
  "data_origin": "rubric_repair"
}
```

Good rubric fields usually separate:

- value or relevance
- urgency
- risk
- verification need
- quality
- action
- final label candidate

## Split Discipline

- Keep exact holdout rows out of training and repair files.
- Keep continuity evals stable across versions.
- Mark close variants as variants, not as the original examples.
- Track `data_origin` and `failure_bucket` so repair sets can be audited later.
- Store human-adjudicated labels separately from raw or weak labels when possible.

## Edge Review Queue

Use a CSV or JSONL queue for contested cases:

```json
{
  "id": "example_0042",
  "current_label": "normal_publish",
  "model_label": "high_priority_clip",
  "disagreement_type": "model_vs_label",
  "expert_decision": "",
  "expert_reason": "",
  "status": "pending"
}
```

Route examples here when:

- model and label disagree on training data
- two labels are plausible
- risk/safety consequences are high
- an example exposes a repeated boundary failure
