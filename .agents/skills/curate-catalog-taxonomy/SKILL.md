---
name: curate-catalog-taxonomy
description: Evolve the myAI-StackGuide category system without duplicate concepts, unstable labels, or shallow coverage. Use for classification, category proposals, aliases, parent relationships, coverage gaps, and taxonomy review; do not use it to edit generators or promote source data without a separate implementation handoff.
---

# Curate Catalog Taxonomy

## Workflow

1. Read current `data/categories.json`, generated category pages, taxonomy-related builder rules, PRD coverage goals, and candidate evidence.
2. Prefer stable domain names over temporary phase labels or vendor-specific buckets.
3. Define category ID, label, scope, inclusion rule, exclusion rule, aliases, parent, examples, and owner.
4. Check duplicate meaning, orphan parents, alias collisions, category depth, and coverage imbalance.
5. Use `PRIMARY_OVERRIDES` only for stable known exceptions; use general keyword rules for reusable classification.
6. Stage proposals separately from generator or source-data implementation.

## Output

Return category changes, classification rationale, affected repositories, conflicts, coverage impact, verification route, and sequential builder handoff.

## Stop Conditions

Stop when category meaning is unsupported, one repository drives a permanent taxonomy decision, or taxonomy and generator files would be edited by parallel workers.
