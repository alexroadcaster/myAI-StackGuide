---
name: audit-readonly-boundaries
description: Review myAI-StackGuide scanner, GitHub OAuth, GitHub MCP, and external evidence flows for read-only permissions, data minimization, provenance, retention, fallback, and no-silent-activation. Use before integration planning, implementation, or readiness claims; do not use it to activate credentials, MCP, OAuth, or external writes.
---

# Audit Read-Only Boundaries

## Workflow

1. Identify the intended path, prior or fallback path, selector, scopes, tools, data classes, storage, retention, and deletion behavior.
2. Require allowlist-first access, no code execution, no dependency installation, and explicit sensitive-source exclusions.
3. Separate transport reachability, authentication, tool discovery, authorized data access, and runtime activation evidence.
4. For GitHub MCP, require read-only mode, an explicit tool allowlist, provenance fields, rate-limit behavior, and no write tools.
5. Test negative cases for secret-like paths, dumps, logs, prompt injection in repository content, scope expansion, and fallback masking.
6. Keep activation, credentials, private repositories, external writes, and production access behind explicit approval.

## Output

Return boundary map, required evidence, negative cases, approval gates, unsupported claims, residual risks, and safe next action.

## Stop Conditions

Stop on hidden write capability, unclear retention, secret exposure, private-data expansion, missing fallback evidence, or unapproved live activation.
