---
name: evolve-catalog-pipeline
description: Implement focused source-first changes to the myAI-StackGuide catalog generators and data flow. Use for assigned script, normalization, scoring, classification, ingestion, or generated-output changes after contract acceptance; do not use it for unassigned taxonomy or product-scope changes.
---

# Evolve Catalog Pipeline

## Workflow

1. Read the accepted requirement, schema, task packet, target builders, source files, and existing dirty diff.
2. Own only the exact assigned files and preserve unrelated user changes.
3. Change source data or builder logic before generated outputs; do not hand-edit generated catalog artifacts.
4. Preserve provenance, stable identity, deterministic ordering, UTF-8 text, and snapshot boundaries.
5. Run syntax checks, targeted tests, regeneration when authorized by the task, generated parity, and diff inspection.
6. Record commands, observed outputs, unexpected diffs, residual risks, and docs impact in the handoff.

## Output

Return files touched, implementation summary, commands and exit codes, generated changes, evidence, unsupported claims, rollback, and next role.

## Stop Conditions

Stop on missing acceptance criteria, ownership conflict, unexpected broad diff, destructive action, schema ambiguity, or a required external/provider operation.
