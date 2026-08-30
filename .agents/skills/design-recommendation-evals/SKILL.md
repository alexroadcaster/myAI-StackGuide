---
name: design-recommendation-evals
description: Design myAI-StackGuide recommendation eval cases, rubrics, thresholds, regression gates, and evidence ownership. Use for recommendation behavior, scanner interpretation, shortlist quality, avoid/defer guidance, or promotion decisions; do not use it to claim quality without a current eval run.
---

# Design Recommendation Evals

## Workflow

1. Map each eval to requirement IDs, persona, Project Context Brief, user goal, constraints, and catalog snapshot.
2. Combine deterministic contract checks with human judgment for fit, usefulness, caveats, and decision support.
3. Include typical, low-context, contradictory, sensitive-source, stale-evidence, refusal, and regression cases.
4. Define required sections, forbidden claims, critical failures, scoring rubric, threshold, evidence owner, and accepted-gap policy.
5. Keep fixtures synthetic and free of secrets, private repository content, customer data, and production payloads.
6. Record baseline, model/config identity when applicable, latency/cost gaps, and promotion decision.

## Output

Return case format, cases, rubric, thresholds, deterministic checks, human-review instructions, critical failures, evidence owner, and next role.

## Stop Conditions

Stop when expected behavior is undefined, the dataset is unsafe, a proxy metric is treated as success, or a quality claim lacks a current eval run.
