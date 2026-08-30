---
name: build-stackguide-mcp
description: Implement the four-tool myAI-StackGuide MCP backend and candidate ledger using accepted auth, storage, and schema contracts. Use for local or mocked backend slices; do not use it to choose unresolved architecture, deploy, use credentials, or activate external writes.
---

# Build StackGuide MCP

## Inputs And Gate

Require the accepted CP-02 stack/auth/storage decisions and exact owned paths/commands, CP-03 tool/ledger contracts, the assigned CP task, and synthetic fixtures. Without them, return the missing gate and owner. This skill is not a general-purpose MCP scaffolder or a deployment authorization.

## Workflow

1. Read Implementation Loop And Handoff, Candidate Identity And Lifecycle, Permission And Tool Contract, and the relevant backend gates in [Team contracts](../../../docs/plan/plugin-v1-team-contracts.md).
2. Implement only the accepted four tools. Use explicit input/output schemas, bounded results, typed errors, accurate annotations, and server-side auth/authz. Never expand API coverage merely because an SDK supports more operations.
3. Start with one local/mock semantic scenario. Reject private fields and revalidate public provenance; keep catalog status, evidence stage, and eligibility independent.
4. Test replay/idempotency, concurrent writes, pinned-version conflicts, auth expiry/refusal, rate limits, retraction and compaction boundaries. Upsert is an own-backend write; public GitHub retrieval remains read-only.
5. Verify accepted migration/restore, health, sanitized logs, dependency failures, and disable/rollback contracts. Do not enable schedulers or contact production to satisfy a local test.

## Output And Stops

Return exact files, tool/contract versions, command evidence, negative cases, local/mock limitations, migration/rollback notes, gaps, and next owner. Stop on unsafe data, missing authorization, machine-to-accepted promotion, canonical snapshot mutation, unresolved decisions, or scope expansion. Actual MCP connection, credentials, deployment, provider costs, and remote writes require the separate CP-14 approval boundary.
