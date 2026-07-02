---
name: expert-judgment-distillation
description: "Design, audit, and document domain-specific expert judgment distillation workflows: label taxonomies, seed datasets, prompt baselines, contested-example review, fine-tuning or Tinker-style experiment loops, failure taxonomies, repair sets, held-out evals, two-stage rubric models, and case-study writeups. Use when asked to replicate expert judgment, model a workflow after the Thinking Machines/Bridgewater Tinker article, build a domain judgment dataset, analyze a judgment model's failures, or package an experiment as a reusable case study."
---

# Expert Judgment Distillation

Use this skill when a user wants to turn repeated expert decisions into a reusable model-training and evaluation workflow. The goal is not generic classification; it is capturing domain taste with clear labels, hard evals, and failure-driven repair.

## Core Workflow

1. Define the expert decision.
   - Identify the domain expert, task, input unit, downstream action, and trust threshold.
   - Separate final labels from operational actions when they differ.
2. Build the first taxonomy.
   - Write label definitions, risk/safety overrides, examples, and counterexamples.
   - Mark ambiguous cases for human or expert review instead of forcing false certainty.
3. Create seed data and splits.
   - Keep `train`, `validation`, `test`, and a continuity holdout separate.
   - Add an edge-case shortlist for disputed labels and boundary cases.
4. Run prompt baselines.
   - Compare naive prompt, expert prompt, and structured-output prompt.
   - Track accuracy, macro F1, invalid outputs, and domain-specific safety misses.
5. Analyze failures before adding data.
   - Use confusion matrices, error CSVs, prediction samples, and risk-miss reports.
   - Convert recurring confusions into named failure buckets.
6. Build targeted repair sets.
   - Add contrastive pairs and sparse real-world variants for the actual failures.
   - Do not leak exact holdout examples into training.
   - Preserve prior regression evals.
7. Evaluate every run against continuity gates.
   - Do not call a run better if it improves one slice while regressing a required safety or transfer eval.
8. Escalate to two-stage rubric modeling when final-label prediction stays brittle.
   - Have the model predict rubric fields first.
   - Derive the final label with deterministic rules.
   - Compare model candidate labels vs derived labels to locate whether failures are rubric-field errors or mapping errors.
9. Write the case study.
   - Explain what the workflow replicated, what improved, what failed, and which claims are supported by held-out evidence.

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

## Reporting Rules

- Be explicit about whether the work is prompt engineering, supervised fine-tuning, RL/distillation, or only dataset/eval design.
- Do not claim expert-level performance without held-out evidence.
- Distinguish dangerous misses from taxonomy-safe escalations.
- Keep article references short and cited; do not reproduce copyrighted article tables, figures, or long passages.
- For public artifacts, remove private paths, credentials, proprietary source rows, and machine-specific assumptions.
