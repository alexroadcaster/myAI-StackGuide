---
name: evolve-catalog-pipeline
description: Implement assigned source-first catalog, public-card or bundled SQLite index generation. Use for owned builders; not user-state storage, runtime search or policy calibration.
---

# Evolve Catalog Pipeline

## Workflow

1. Read PLAN.md, data/catalog_manifest.json, relevant source builders and [team contracts](../../../docs/plan/plugin-v1-team-contracts.md).
2. For CP-06 read accepted C9 contracts and specs/retrieval/retrieval-policy.json. Freeze exact scripts, public source files, package outputs and tests before editing.
3. Preserve source-owned identities, aliases, dates, unknowns and provenance; browser enrichment cannot substitute for persisted public facts.
4. Generate public cards/index/manifest without user context, runtime query logging, embeddings or automatic startup rebuild. Derive policy from the accepted source, not a parallel constant set.
5. Check logical row/query parity independently of package-byte hashes. Keep taxonomy/current/legacy pipelines distinct and regenerate only assigned outputs sequentially.
6. Run focused positive/negative checks and inspect the diff; report actual evidence and hand off runtime retrieval to its owner.

## Output

Return exact owned files or findings, requirement/contract mapping, observed checks and failures, evidence limits, rollback, risks and next owner. Stop on unsafe data, missing applicable acceptance, ownership conflict or action outside existing authorization; do not invent evidence.
