---
name: curate-catalog-taxonomy
description: Evolve the myAI-StackGuide category system without duplicate concepts, unstable labels, or shallow coverage. Use for classification, category proposals, aliases, parent relationships, coverage gaps, and taxonomy review; do not use it to edit generators or promote source data without a separate implementation handoff.
---

# Curate Catalog Taxonomy

## Workflow

1. Read current `data/catalog_manifest.json` and `data/catalog_manifest.schema.json`, PRD coverage goals, and candidate evidence from the repository root. Read Source Routing in [Team contracts](../../../docs/plan/plugin-v1-team-contracts.md). Use `data/categories.json` and generated category pages only for an explicitly assigned legacy taxonomy task.
2. Prefer stable domain names over temporary phase labels or vendor-specific buckets.
3. Define category ID, label, scope, inclusion rule, exclusion rule, aliases, parent, examples, and owner.
4. Check duplicate meaning, orphan parents, alias collisions, category depth, and coverage imbalance.
5. Route current taxonomy changes through the manifest contract and its consumers. `PRIMARY_OVERRIDES` and general keyword rules belong only to the legacy builder; they must not overwrite current taxonomy or silently map newer categories.
6. Stage proposals separately from generator or source-data implementation.

## Local Product Alignment

Keep taxonomy concepts/aliases, multilingual retrieval query aliases and RU/EN interface translations distinct. Do not change semantic category IDs merely to translate the interface.

## Output

Return category changes, classification rationale, affected repositories, conflicts, coverage impact, verification route, and sequential builder handoff.

## Stop Conditions

Stop when category meaning is unsupported, one repository drives a permanent taxonomy decision, or taxonomy and generator files would be edited by parallel workers.
