---
name: shape-product-slice
description: Frame a bounded myAI-StackGuide product slice with users, value, non-goals, metrics, acceptance, dependencies, and evidence owners. Use for requirement changes, roadmap slicing, scope repair, or pre-implementation framing; do not use it to begin architecture or implementation before acceptance.
---

# Shape Product Slice

## Workflow

1. Read `PRODUCT_REQUIREMENTS.md`, `V1_ROADMAP.md`, `REQUIREMENTS.md`, `PLAN.md`, and the relevant concept document.
2. Identify the user decision improved by the slice and separate business outcome, product outcome, and feature metric.
3. Map the slice to existing requirement IDs; add a new ID only when the behavior is not already covered.
4. Name in-scope outputs, non-goals, dependencies, privacy boundary, owner, acceptance criteria, and evidence needed.
5. Keep external activation, deployment, Git history, and provider access behind explicit approval.
6. Hand architecture work to `catalog_architect` and eval design to `quality_evaluator`.

## Output

Return requirement IDs, exact artifacts, acceptance criteria, metrics, counter-metrics, risks, open decisions, and next role.

## Stop Conditions

Stop when product meaning is unresolved, a source document conflicts materially, ownership overlaps, or implementation would begin before acceptance and verification are explicit.
