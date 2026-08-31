---
name: verify-generated-parity
description: Verify source-to-output parity for catalog, bundled public index or session HTML projection. Use after assigned generation changes; static parity does not prove browser or search quality.
---

# Verify Generated Parity

## Workflow

1. Read PLAN.md, the owning sources/builders and relevant [team contracts](../../../docs/plan/plugin-v1-team-contracts.md).
2. Select the affected family: current or legacy catalog outputs, CP-06 public cards/index/manifest, or CP-10 session projection. Do not regenerate unrelated surfaces.
3. Check reproducible logical content, canonical IDs and provenance. Use exact package hashes for distribution integrity, not SQLite semantic equivalence.
4. For session projection use specs/artifact/session-workspace-contract.md: canonical/source bindings, partial/null sources, saved/published revisions and RU/EN coverage. Do not edit state or translate facts during verification.
5. Inspect changed-source parity, escaping and size constraints with read-only checks where available. Browser behavior, language meaning and retrieval relevance require separate evidence.
6. Report exact commands, versions, mismatches, evidence ceiling and owning source correction; never repair generated output alone.

## Output

Return exact owned files or findings, requirement/contract mapping, observed checks and failures, evidence limits, rollback, risks and next owner. Stop on unsafe data, missing applicable acceptance, ownership conflict or action outside existing authorization; do not invent evidence.
