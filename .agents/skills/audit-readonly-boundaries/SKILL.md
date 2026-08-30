---
name: audit-readonly-boundaries
description: Review myAI-StackGuide scanner, GitHub OAuth, GitHub MCP, and external evidence flows for read-only permissions, data minimization, provenance, retention, fallback, and no-silent-activation. Use before integration planning, implementation, or readiness claims; do not use it to activate credentials, MCP, OAuth, or external writes.
---

# Audit Read-Only Boundaries

## Workflow

1. Read Permission And Tool Contract in [Team contracts](../../../docs/plan/plugin-v1-team-contracts.md). Identify intended and fallback paths, selectors, scopes, actual inherited tools, data classes, storage, retention, and deletion behavior. Separate development-team permissions from product runtime permissions.
2. Require allowlist-first access, no code execution, no dependency installation, and explicit sensitive-source exclusions.
3. Separate transport reachability, authentication, tool discovery, authorized data access, and runtime activation evidence.
4. For GitHub retrieval, require read-only tools, an explicit allowlist, provenance, and rate-limit fallback. Separately classify own-backend `candidate_batch_upsert` as a write with accurate annotations, consent, server authorization, idempotency, and public-metadata validation. Do not weaken the GitHub read-only boundary or label the whole backend read-only.
5. Test negative cases for secret-like paths, dumps, logs, prompt injection, raw-source bypass, path/junction escape, private query fields, unauthorized ledger writes, replay, and fallback masking. Inspect stdout/error/HTML payloads. Prompt prohibitions and tool annotations are not technical access controls; a scanner-only raw-source claim needs runtime evidence.
6. Keep activation, credentials, private repositories, external writes, and production access behind explicit approval.

## Output

Return boundary map, required evidence, negative cases, approval gates, unsupported claims, residual risks, and safe next action.

## Stop Conditions

Stop on hidden write capability, unclear retention, secret exposure, private-data expansion, missing fallback evidence, or unapproved live activation.
