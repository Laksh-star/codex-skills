# Evaluation Metrics And Gates

Use metrics that match the workflow's actual risk. Accuracy alone is rarely enough for expert judgment.

## Core Metrics

- Accuracy: useful for balanced single-label tasks.
- Macro F1: important when labels are imbalanced or minority classes matter.
- Per-label precision/recall/F1: required for labels with operational consequences.
- Exact match: useful for truncation, segmentation, extraction, or structured outputs.
- Invalid output rate: required for JSON, enum, schema, or action-constrained models.

## Judgment-Specific Metrics

Use domain names, but keep the concepts:

- Dangerous miss: model under-escalates a risky or high-impact item.
- Taxonomy-safe escalation: model escalates to review when the exact label is wrong but the action is safe.
- Action accuracy: final operational action is correct, regardless of taxonomy nuance.
- Value calibration: model distinguishes high-value from routine or durable from short-lived.
- Transfer accuracy: performance on sparse or real-world holdout examples.
- Candidate-vs-derived disagreement: for rubric-first models.

## Required Reports

For each run, produce:

- metrics summary JSON
- confusion matrix
- error analysis CSV
- dangerous miss report
- regression comparison against prior best
- short written decision: promote, repair, or reject

## Gate Template

Example gates:

```text
valid_json_rate == 1.0
valid_enum_rate == 1.0
macro_f1 >= 0.80
dangerous_miss_count == 0
key_label_recall >= 0.90
transfer_holdout_accuracy >= prior_best
no regression on continuity evals
```

Use stricter gates for safety, legal, compliance, medical, finance, public communications, or any workflow where under-escalation creates harm.

## Failure Taxonomy

Convert repeated errors into repair buckets:

- high value mistaken for routine
- routine content over-prioritized
- risky content under-escalated
- safe content over-escalated
- durable content mistaken for short-lived
- low-value noise mistaken for expert review
- schema or enum failures
- sparse input transfer failure

Repair data should target buckets directly, with contrastive pairs where possible.
