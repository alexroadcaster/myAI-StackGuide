---
name: design-catalog-contracts
description: Design source-owned myAI-StackGuide repository-card, taxonomy, provenance, identity, and compatibility contracts. Use for catalog schemas, category rules, candidate states, or generated-data interfaces; do not use it for implementation or generated-output edits before contract acceptance.
---

# Design Catalog Contracts

## Workflow

1. Read `docs/PRODUCT_REQUIREMENTS.md`, `docs/METHODOLOGY.md`, `AGENTS.md`, `data/catalog_manifest.json`, `data/catalog_manifest.schema.json`, and the relevant builders from the repository root. Read Source Routing and Candidate Identity And Lifecycle in [Team contracts](../../../docs/plan/plugin-v1-team-contracts.md).
2. Preserve upstream factual metadata and distinguish baseline, advisory, computed, snapshot, live-evidence, and curator fields.
3. Define stable identifiers, required fields, nullability, enums, provenance, freshness, trust, verification, and compatibility behavior.
4. Provide positive, negative, and boundary fixtures before claiming the contract is ready.
5. Map every generated consumer and assign migration, regeneration, docs, test, and rollback ownership.
6. Keep automatic candidate overlay events separate from the frozen curated snapshot. Machine evidence and recommendation eligibility never assign curator acceptance. Define snapshot/overlay pinning, dedupe, replay, rejection, and explicit legacy-state mapping; authorized own-backend candidate writes are not GitHub writes.

## Output

Return exact schema files, field contract, consumer map, fixture plan, compatibility risks, verification commands, rollback, and handoff.

## Stop Conditions

Stop on invented metadata, unclear source ownership, untraceable identity, silent breaking change, or overlapping ownership of shared schemas and generated outputs.
