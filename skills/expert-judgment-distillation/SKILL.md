---
name: expert-judgment-distillation
description: "Design, audit, and document domain-specific expert judgment distillation workflows: label taxonomies, seed datasets, prompt baselines, contested-example review, fine-tuning or Tinker-style experiment loops, failure taxonomies, repair sets, held-out evals, two-stage rubric models, and case-study writeups. Use when asked to replicate expert judgment, model a workflow after the Thinking Machines/Bridgewater Tinker article, build a domain judgment dataset, analyze a judgment model's failures, or package an experiment as a reusable case study."
---

# Expert Judgment Distillation

Use this skill when a user wants to turn repeated expert decisions into a reusable model-training and evaluation workflow. The goal is not generic classification; it is capturing domain taste with clear labels, hard evals, and failure-driven repair.

## Quick Start

For a new domain, first produce four small artifacts before suggesting any training run:

1. **Decision brief:** what expert judgment is being replicated, who makes it, and what action follows.
2. **Draft taxonomy:** 3-8 labels with definitions, examples, counterexamples, and safety overrides.
3. **Seed eval plan:** initial train/validation/test/holdout split and the one slice that must not regress.
4. **Failure-review queue:** a CSV/JSONL shape for contested examples.

Minimal example:

```text
Task: editorial item triage
Input: headline + short text + platform context
Labels: clip_now, publish_normally, send_for_review, ignore, save_for_evergreen
Dangerous miss: risky or unverified content classified as publish_normally
Protected holdout: sparse real-world headlines
```

Non-editorial example:

```text
Task: sales lead prioritization
Input: company, role, inbound message, source, firmographic context
Labels: urgent_sales_followup, nurture, disqualify, needs_human_review
Dangerous miss: qualified enterprise lead classified as nurture or disqualify
Protected holdout: short ambiguous inbound messages from high-value accounts
```

## Core Workflow

1. Define the expert decision.
   - Identify the domain expert, task, input unit, downstream action, and trust threshold.
   - Separate final labels from operational actions when they differ.
2. Build the first taxonomy.
   - Write label definitions, risk/safety overrides, examples, and counterexamples.
   - Mark ambiguous cases for human or expert review instead of forcing false certainty.
   - Output `taxonomy.md` with a table: label, action, definition, examples, counterexamples, override rules.
3. Create seed data and splits.
   - Keep `train`, `validation`, `test`, and a continuity holdout separate.
   - Add an edge-case shortlist for disputed labels and boundary cases.
4. Run prompt baselines.
   - Compare naive prompt, expert prompt, and structured-output prompt.
   - Track accuracy, macro F1, invalid outputs, and domain-specific safety misses.
5. Analyze failures before adding data.
   - Use confusion matrices, error CSVs, prediction samples, and risk-miss reports.
   - Convert recurring confusions into named failure buckets.
   - Output `failure-taxonomy.md` with bucket name, severity, count, examples, suspected cause, and repair strategy.
6. Build targeted repair sets.
   - Add contrastive pairs and sparse real-world variants for the actual failures.
   - Do not leak exact holdout examples into training.
   - Preserve prior regression evals.
   - Output `repair-manifest.md` explaining which failure each repair set targets and which evals it must protect.
7. Evaluate every run against continuity gates.
   - Do not call a run better if it improves one slice while regressing a required safety or transfer eval.
8. Escalate to two-stage rubric modeling when final-label prediction stays brittle.
   - Have the model predict rubric fields first.
   - Derive the final label with deterministic rules.
   - Compare model candidate labels vs derived labels to locate whether failures are rubric-field errors or mapping errors.
   - Output a candidate-vs-derived report and field-level failure summary before recommending more data.
9. Write the case study.
   - Explain what the workflow replicated, what improved, what failed, and which claims are supported by held-out evidence.

## Required Agent Outputs

When guiding a full workflow, produce these artifacts in order:

| Stage | Required output |
| --- | --- |
| Decision definition | `decision-brief.md` |
| Taxonomy | `taxonomy.md` |
| Seed dataset | JSONL/CSV files plus `dataset-card.md` |
| Baseline | `baseline-report.md` |
| Failure analysis | `failure-taxonomy.md` and error CSV |
| Repair data | repair JSONL/CSV plus `repair-manifest.md` |
| Eval | `eval-report.md` with metrics, gates, and promotion decision |
| Case study | `case-study.md` or public-safe article draft |

For small requests, return the smallest useful subset instead of creating every artifact.

## When The User Mentions Bridgewater Or Tinker

Read `references/bridgewater-tinker-process-map.md` before answering. Use it to cite the Thinking Machines/Bridgewater article as a conceptual basis without copying article text or implying endorsement.

## Dataset And Eval References

- Read `references/dataset-schemas.md` when creating JSONL/CSV schemas, rubric fields, or output formats.
- Read `references/eval-metrics.md` when choosing metrics, gates, and failure reports.
- Read `references/case-study-template.md` when drafting a public or internal case study.
- Read `references/extension-playbook.md` when the user asks what else to add, how to make the workflow more visual, or how to mature the skill into a stronger ML/eval toolkit.

## Validation Helper

For local JSONL datasets, use:

```bash
python3 scripts/validate_judgment_dataset.py \
  --train path/to/train.jsonl \
  --validation path/to/validation.jsonl \
  --test path/to/test.jsonl \
  --holdout path/to/holdout.jsonl \
  --label-field final_label \
  --allowed-labels labels.txt \
  --text-fields headline summary text
```

The script checks JSONL validity, required labels, enum values, duplicate IDs, repeated text fingerprints, split leakage, and optional holdout leakage.

Good output:

```json
{"ok": true, "errors": [], "splits": {"train": 100, "validation": 20}}
```

Bad output:

```json
{"ok": false, "errors": ["id leakage across splits: example_42 in ['train', 'holdout']"]}
```

## Reporting Rules

- Be explicit about whether the work is prompt engineering, supervised fine-tuning, RL/distillation, or only dataset/eval design.
- Do not claim expert-level performance without held-out evidence.
- Distinguish dangerous misses from taxonomy-safe escalations.
- Keep article references short and cited; do not reproduce copyrighted article tables, figures, or long passages.
- For public artifacts, remove private paths, credentials, proprietary source rows, and machine-specific assumptions.

## Common Anti-Patterns This Skill Prevents

- Training before defining the decision and action.
- Reporting aggregate accuracy while ignoring dangerous misses.
- Treating weak or synthetic labels as final truth.
- Adding broad data instead of targeted repair data.
- Leaking exact holdout examples into training.
- Declaring victory on in-domain test sets while transfer evals regress.
- Claiming to reproduce a paper or article's training recipe when only the process pattern was reused.
