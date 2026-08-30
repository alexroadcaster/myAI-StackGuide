---
name: review-advisory-evidence
description: Independently audit myAI-StackGuide catalog and recommendation claims for provenance, freshness, confidence, fit, caveats, and advisory boundaries. Use before promotion, documentation, release, or completion claims; do not use it to implement fixes or approve unsupported runtime behavior.
---

# Review Advisory Evidence

## Workflow

1. Build a claim ledger linking each material statement to source, date, artifact, and verification status.
2. Classify claims as supported, unsupported, inferred, stale, contradicted, blocked, or accepted gap.
3. Challenge popularity bias, false authority, missing caveats, snapshot/live conflation, and claims beyond security, legal, procurement, or runtime evidence.
4. Check requirement coverage, negative cases, current command/eval/runtime evidence, approval boundaries, and fallback masking.
5. Lead with severity-ordered findings and exact file references.
6. Remain read-only unless a separate task assigns documentation ownership.

## Output

Return findings, claim ledger, evidence ledger, requirement gaps, accepted gaps, blockers, residual risks, and next safe action.

## Stop Conditions

Stop when source or diff context is incomplete, evidence is unavailable, private data is required, or review is asked to approve an unverified runtime or external action.
