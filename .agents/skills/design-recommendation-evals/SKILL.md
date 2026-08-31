---
name: design-recommendation-evals
description: Design team behavior, FTS5 relevance, publication recovery, RU/EN and integration-usefulness evals. Use for cases and evidence gates; no quality claim without observed runs.
---

# Design Recommendation Evals

## Workflow

1. Read EVALS.md, .codex/agent-eval-workflow.md, evals/plugin-v1/runner-contract.md and relevant [team contracts](../../../docs/plan/plugin-v1-team-contracts.md).
2. Separate team routing from C8 captured-result compatibility, actual retrieval relevance, state/render recovery, browser behavior and human integration usefulness. Do not treat the existing scorer as an actual retrieval/model runner.
3. Use synthetic private-project fixtures and provenance-backed actual public catalog fixtures. Freeze independent judgments and development/held-out splits; synthetic scale data is only scaling evidence.
4. Cover direct/indirect/incomplete/non-trigger and adversarial/regression cases: authorized reads plus exclusions, incompatible index versus no-match, partial workspace, saved/published failure, stale translation, language switching, authorized coding handoff and activity unknowns.
5. Compare RU and EN against the same canonical capture, including negation, constraints, caveats, sources and execution state. Define deterministic critical failures separately from human meaning/usefulness judgments.
6. Record versions/hashes, baseline, thresholds, observed action trace, model/config identity, latency/cost gaps and reviewer. Fresh behavior is required after instruction changes; model comparisons are required before durable model/effort changes.

## Output

Return exact owned files or findings, requirement/contract mapping, observed checks and failures, evidence limits, rollback, risks and next owner. Stop on unsafe data, missing applicable acceptance, ownership conflict or action outside existing authorization; do not invent evidence.
