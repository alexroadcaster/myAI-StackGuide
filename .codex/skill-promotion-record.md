# Skill Promotion Record

Current state: `spec_present_not_model_run`

All project skills use the official repo discovery location `.agents/skills`. Structural checks do not prove implicit activation or output quality.

The builder skills and expanded contracts are authored but not behaviorally promoted. The offline team grader and its synthetic unit tests do not change this status. New or changed instructions require fresh-session discovery and trace-backed activation/output review; see `.codex/agent-eval-workflow.md`.

Promotion requires:

- direct and indirect trigger cases;
- incomplete-input behavior;
- non-trigger and unsafe-action cases;
- output and stop-condition review;
- no secret, unauthorized private-data, credential, external-write, or silent-activation regression;
- a fresh-context run with evidence recorded in `RUNLOG.md`.

No skill in this repository currently authorizes MCP activation, OAuth, external writes, deployment, Git history changes, hooks, automation, or an Agents SDK runner.

## CP-05 Instruction Revision

The [CP-05 audit](../docs/plan/2026-08-31-cp05-control-plane-audit.md) records every role/skill/metadata disposition. All thirteen SKILL.md entrypoints change; eleven discovery metadata files change, while taxonomy and product-slice metadata remain accurate. Static validation and a changed source hash are configuration evidence only.

For each changed skill, promotion requires its direct, indirect, incomplete and non-trigger cases, plus relevant local team regressions. Use the exact case and instruction hashes. CP-12-only cases/skills remain deferred for the local release; a dormant capability must still reject unaccepted activation. No observed run or model comparison is claimed by this record. Current gate results belong to PLAN.md and RUNLOG.md.
