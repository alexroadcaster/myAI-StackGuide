---
name: design-catalog-contracts
description: Design source-owned myAI-StackGuide repository-card, taxonomy, provenance, identity, and compatibility contracts. Use for catalog schemas, category rules, candidate states, or generated-data interfaces; do not use it for implementation or generated-output edits before contract acceptance.
---

# Design Catalog Contracts

## Workflow

1. Read `PRODUCT_REQUIREMENTS.md` data requirements, `METHODOLOGY.md`, `AGENTS.md`, current `data/*.json`, and the relevant builders.
2. Preserve upstream factual metadata and distinguish baseline, advisory, computed, snapshot, live-evidence, and curator fields.
3. Define stable identifiers, required fields, nullability, enums, provenance, freshness, trust, verification, and compatibility behavior.
4. Provide positive, negative, and boundary fixtures before claiming the contract is ready.
5. Map every generated consumer and assign migration, regeneration, docs, test, and rollback ownership.
6. Keep new GitHub discoveries outside canonical source data until curator promotion.

## Output

Return exact schema files, field contract, consumer map, fixture plan, compatibility risks, verification commands, rollback, and handoff.

## Stop Conditions

Stop on invented metadata, unclear source ownership, untraceable identity, silent breaking change, or overlapping ownership of shared schemas and generated outputs.
