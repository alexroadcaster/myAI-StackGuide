---
name: design-catalog-contracts
description: Design source-owned catalog and C9 SQLite query/card/index/evidence-pack contracts. Use for identity, provenance and compatibility; remote ledgers require separate acceptance.
---

# Design Catalog Contracts

## Workflow

1. Read PLAN.md, data/catalog_manifest.json, specs/retrieval/retrieval-policy.json and relevant [team contracts](../../../docs/plan/plugin-v1-team-contracts.md).
2. Keep current manifest taxonomy authoritative; separate canonical identity, catalog status, evidence stage, recommendation eligibility and request-specific role.
3. Specify public source cards, index/manifest pins, structured bounded query, result and evidence pack for CP-06/09 and the C8 scorer. Public index cannot contain project context.
4. Keep activity dates and per-field provenance separate; unknown is not false or current. No snapshot TTL, stars or BM25 score proves adoption fit.
5. Preserve accepted limits/aliases/weights and explicit no-hit versus failure. Version compatible consumer changes; do not add vector/server dependencies.
6. Map positive/negative examples and rollback to exact owners. CP-12 remote contracts remain separately deferred.

## Output

Return exact owned files or findings, requirement/contract mapping, observed checks and failures, evidence limits, rollback, risks and next owner. Stop on unsafe data, missing applicable acceptance, ownership conflict or action outside existing authorization; do not invent evidence.
