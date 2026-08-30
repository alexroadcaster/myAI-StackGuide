---
name: design-context-contracts
description: Define safe scanner, Project Context Brief, interview, and recommendation memo contracts for myAI-StackGuide. Use for context acquisition, fact and inference separation, confidence, corrections, evidence, or advisory schemas; do not use it to scan private data or implement live collection.
---

# Design Context Contracts

## Workflow

1. Read `MYAI_STACKGUIDE_CONTEXT_SCANNER.md`, `MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`, the PRD, and current control-plane requirements.
2. Keep raw scan data, sanitized summaries, user corrections, catalog evidence, and final memo as distinct data classes.
3. Model observed facts separately from inferences, confidence, missing context, evidence references, and user corrections.
4. Preserve allowlist-first scanning, no code execution, no dependency installation, redaction, deletion, and retention boundaries.
5. Require the memo to include category path, candidate roles, reasons, avoid/defer, comparison, reading path, caveats, evidence, and next human decision.
6. Add positive, low-context, contradictory-evidence, and sensitive-source fixtures.

## Output

Return schema proposal, invariants, failure modes, privacy boundary, fixtures, checks, evidence owner, and next role.

## Stop Conditions

Stop when private-data handling is ambiguous, an inference can masquerade as fact, evidence cannot be traced, or the output crosses into implementation ownership.
