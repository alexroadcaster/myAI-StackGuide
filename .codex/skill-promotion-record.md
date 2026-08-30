# Skill Promotion Record

Current state: `spec_present_not_model_run`

All project skills use the official repo discovery location `.agents/skills`. Structural checks do not prove implicit activation or output quality.

The builder skills and expanded contracts are authored but not behaviorally promoted. The offline team grader and its synthetic unit tests do not change this status. New or changed instructions require fresh-session discovery and trace-backed activation/output review; see `.codex/agent-eval-workflow.md`.

Promotion requires:

- direct and indirect trigger cases;
- incomplete-input behavior;
- non-trigger and unsafe-action cases;
- output and stop-condition review;
- no secret, private-data, credential, external-write, or silent-activation regression;
- a fresh-context run with evidence recorded in `RUNLOG.md`.

No skill in this repository currently authorizes MCP activation, OAuth, external writes, deployment, Git history changes, hooks, automation, or an Agents SDK runner.
