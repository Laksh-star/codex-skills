# Case Study Template

Use this template when turning an experiment into a public or internal writeup.

## Title

Replicating Expert Judgment In [Domain Task]

## One-Sentence Thesis

We tested whether a task-specific data and evaluation loop could teach a model to reproduce [expert role]'s repeated judgment about [decision].

## Context

- Domain:
- Expert decision:
- Inputs:
- Labels/actions:
- Why generic prompting is insufficient:

## Process

1. Defined the label taxonomy and action schema.
2. Built seed train/validation/test data.
3. Ran naive and expert-prompt baselines.
4. Analyzed errors and contested examples.
5. Built targeted repair sets.
6. Fine-tuned or otherwise trained task-specific models.
7. Evaluated on held-out and transfer sets.
8. Tried rubric-first modeling if final-label prediction stayed brittle.

## Results

Include a compact table:

| Run | Main Eval | Transfer Eval | Safety Misses | Decision |
| --- | --- | --- | --- | --- |
| Baseline | | | | |
| Repair v1 | | | | |
| Best current | | | | |

## What Worked

- Schema or enum reliability:
- Boundary improvements:
- Transfer gains:
- Cost or workflow improvements:

## What Failed

- Remaining brittle labels:
- Sparse real-world failures:
- Safety regressions:
- Data quality limits:

## Bridgewater/Tinker Mapping

Use `bridgewater-tinker-process-map.md` if the user wants this framing. Be clear whether the project replicated the conceptual process, the dataset/eval loop, or the exact training recipe.

## Next Step

End with the next concrete repair loop, not vague future work:

- examples to adjudicate
- eval slice to protect
- model or prompt change to test
- success gate
