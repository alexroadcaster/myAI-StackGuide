---
name: design-recommendation-evals
description: Design myAI-StackGuide recommendation eval cases, rubrics, thresholds, regression gates, and evidence ownership. Use for recommendation behavior, scanner interpretation, shortlist quality, avoid/defer guidance, or promotion decisions; do not use it to claim quality without a current eval run.
---

# Design Recommendation Evals

## Workflow

1. Read `EVALS.md` and `.codex/agent-eval-workflow.md` from the repository root. Separate static configuration, team routing, deterministic product behavior, and human recommendation usefulness. Map each eval to requirement IDs, versioned inputs, persona, goal, constraints, snapshot, and overlay version where applicable.
2. Combine deterministic contract checks with human judgment for fit, usefulness, caveats, and decision support.
3. Include typical, low-context, contradictory, sensitive-source, stale-evidence, refusal, and regression cases. Add ambiguous routing, non-trigger, malicious retrieved instructions, scanner bypass, correction/resume, permission refusal, visible catalog-only fallback, ledger retry/idempotency, and forbidden machine-to-accepted cases.
4. Define required sections, forbidden claims, critical failures, scoring rubric, threshold, evidence owner, and accepted-gap policy.
5. Keep fixtures synthetic and free of secrets, private repository content, customer data, and production payloads.
6. Record baseline, case-set identity, model/config identity, reviewed tool/action traces, latency/cost gaps, and promotion decision. Offline grading of synthetic records validates the grader only. Actual agent results need separate trace-backed review and owner acceptance; a score cannot override critical failures. Use the local team grader for team cases, not as a substitute for the future product recommendation runner.

## Output

Return case format, cases, rubric, thresholds, deterministic checks, human-review instructions, critical failures, evidence owner, and next role.

## Stop Conditions

Stop when expected behavior is undefined, the dataset is unsafe, a proxy metric is treated as success, or a quality claim lacks a current eval run.
