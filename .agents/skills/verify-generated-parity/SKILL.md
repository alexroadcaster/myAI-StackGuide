---
name: verify-generated-parity
description: Verify myAI-StackGuide generated Markdown, HTML, JSON, CSV, and category outputs against source builders and invariants. Use after source or generator changes, during review, or before release claims; do not use it to repair failures without implementation ownership.
---

# Verify Generated Parity

## Workflow

1. Identify the source files, builders, and generated consumers affected by the slice.
2. Prefer in-memory parity checks when the task does not authorize writing generated files.
3. Run the smallest relevant syntax, schema, count, identity, ordering, and payload checks.
4. Inspect the diff for unrelated rewrites, stale titles, encoding damage, duplicate identities, and missing provenance.
5. Report exact command, exit code, observed result, skipped checks, and whether evidence is static or runtime.
6. Do not repair failures unless implementation ownership is explicitly reassigned.

## Output

Return checks run, expected and observed results, parity verdict, files inspected, unsupported claims, residual risks, and next role.

## Stop Conditions

Stop on missing builder ownership, generated/source disagreement, encoding corruption, unexpected destructive rewrite, or a check requiring unapproved external access.
