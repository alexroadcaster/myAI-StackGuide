---
name: build-stackguide-mcp
description: Implement an explicitly accepted deferred CP-12 local/mock backend slice. Do not use for local V1 plugin, SQLite retrieval, session HTML or unapproved service activation.
---

# Build StackGuide MCP

## Workflow

1. Read PLAN.md and relevant [team contracts](../../../docs/plan/plugin-v1-team-contracts.md); require a separately accepted CP-12 extension decision and exact backend paths.
2. Verify accepted auth/storage/tool/error contracts; local CP-02/03 acceptance does not select a backend or authorize a provider.
3. Implement only the assigned four-tool or candidate-ledger seam using synthetic local/mock fixtures. GitHub retrieval remains read-only; authorized backend upsert is a write, not curator acceptance.
4. Enforce bounded inputs, server validation/authz, provenance, version pins, idempotency and failure behavior. Never persist raw project context or credentials in a public ledger.
5. Run exact assigned negative/retry/concurrency checks without live activation, remote calls, deployment or compaction scheduling.
6. Return local/mock evidence, unsupported live claims, rollback and next owner. Missing extension acceptance keeps the role dormant.

## Output

Return exact owned files or findings, requirement/contract mapping, observed checks and failures, evidence limits, rollback, risks and next owner. Stop on unsafe data, missing applicable acceptance, ownership conflict or action outside existing authorization; do not invent evidence.
