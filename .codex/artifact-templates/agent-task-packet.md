# Agent Task Packet

Use this fresh-context handoff before every subagent or parallel worker. Do not attach raw conversation history.

## Task

- Task row ID:
- Lifecycle state:
- Goal:
- Owner and recommended agent:
- Configured model and reasoning effort:
- Assigned project skills:
- Dependency status:

## Complete Context

- Requirements and source documents:
- Complete task context:
- Acceptance criteria:
- Architecture boundary:
- Allowed sources:
- Inputs already used:
- Verified facts:
- Assumptions or unsupported claims:

## Ownership

- Owned files:
- Out-of-scope files:
- Forbidden files:
- Shared/generated surfaces:
- Cross-agent conflict status:
- Worktree or sequential handoff requirement:

## Execution Contract

- Allowed actions:
- Actions requiring approval:
- Commands to run:
- Named unit-test owner and acceptance/eval owner:
- Expected-RED assertion and reason, if test-first (otherwise not applicable):
- In-scope repair boundary and escalation trigger:
- Required accepted CP-02/03 decisions and source versions:
- Actual tool/permission surface; restrictions enforced technically versus instructions only:
- Expected outputs and evidence:
- Required static or behavioral agent/skill eval cases:
- Baseline versus one-lower reasoning comparison required:
- Documentation update path:
- Rollback notes:
- Accepted gaps:

## Stop Conditions

- Stop on missing context, ownership ambiguity, shared write scope, absent evidence, acceptance-changing repair, secret-bearing data, private data beyond scope, or unapproved external action. A declared expected-RED assertion permits the assigned implementation step; unrelated failures do not. Repair ordinary failures within exact owned files without weakening acceptance.
- Stop before MCP, hook, automation, GitHub Action, deployment, provider, Git history, or external write activation unless separately approved.

## Sequential Fallback

- Sequential fallback owner:
- Handoff point:
- Reason parallel work is unsafe:

## Required Return Packet

- Files touched:
- Files proposed:
- Commands run and exit codes:
- Verification evidence:
- Agent, skill, model, and reasoning evidence:
- Supported claims:
- Unsupported claims:
- Residual risks:
- Stop reason:
- Recommended next role and task:
