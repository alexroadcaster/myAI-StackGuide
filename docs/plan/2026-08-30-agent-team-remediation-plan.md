# Agent Team Audit Remediation

Historical remediation record. Current local FTS5/session/localization instruction work is CP-05 in [the active plan](2026-08-30-codex-plugin-v1-implementation-plan.md) and [full audit](2026-08-31-cp05-control-plane-audit.md). Original task reports below remain dated evidence.

Date: 2026-08-30. Status: `implemented` for scoped local remediation; behavioral and product readiness remain unverified.

The owner approved the preceding team audit and requested a task list and implementation. This authorizes repository-local control-plane, agent/skill, test, and offline eval-tooling changes. It does not authorize product runtime implementation, external skill installation, provider calls, credentials, MCP activation, deployment, publication, Git history changes, or permission changes.

## Task Start Brief

- Active slice: AR-01 through AR-06 below; parent product plan: `docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md`.
- Outcome: remove known instruction drift and provide testable team contracts without claiming behavioral or product readiness.
- Execution owner: primary agent, sequentially acting in the listed owner roles. No subagents are dispatched by this plan. Final review is an explicit self-review, not independent behavioral evidence.
- Baseline: preserve the existing `RUNLOG.md` changes and existing plugin plan. Preserve catalog inputs/outputs byte-for-byte and leave `.codex/config.toml`, permissions, hooks, and automation unchanged.
- Architecture boundary: development-team configuration and local evaluation utilities only; these are not the distributed plugin.
- Verification: targeted unit tests and static validators; synthetic grader tests are not agent/model runs.
- Rollback: reverse only this slice's reviewed hunks; retain pre-existing edits and historical plan/evidence records. Do not use destructive Git commands.
- Stop: unclear ownership, unsafe data, denied filesystem access, unapproved external action, or acceptance-changing architectural choice. Continue unaffected local tasks when a protected path is blocked; report the exact gap.
- Methodology: acceptance-first, source-first, short vertical test cycles, contract checks, and explicit evidence levels. DDD, FSD, hosted telemetry, and production SLO implementation are not applicable to this control-plane slice.

## Tasks And Ownership

This bounded remediation uses the index, exact file sets, acceptance scenarios, and detailed task blocks below as its execution packet. It does not replace the CP-01 through CP-16 product matrix.

| ID | Task | Accountable role | Skills | Depends on | Status |
| --- | --- | --- | --- | --- | --- |
| AR-01 | Record scope, align active navigation, and enforce English control-plane text | Product Planner / Docs Maintainer | implementation-planner; maintain-control-plane | Owner approval | implemented |
| AR-02 | Repair source paths, current/legacy taxonomy routing, and candidate-state semantics | Catalog Architect | skill-creator; design-catalog-contracts | AR-01 | implemented |
| AR-03 | Define implementation loop, test ownership, permission boundaries, and handoffs | Primary orchestrator / Catalog Architect | agent-team-designer; maintain-control-plane | AR-01 | implemented |
| AR-04 | Prepare two scoped builder roles and extend narrowly targeted project skills | Primary orchestrator | agent-team-designer; skill-creator | AR-02, AR-03 | implemented |
| AR-05 | Replace count-based checks and add versioned offline behavioral-result grading | Quality Evaluator | design-recommendation-evals; python-code-style | AR-02, AR-03, AR-04 | implemented |
| AR-06 | Run regression checks, review the diff, and record remaining product gates | Quality Evaluator / Docs Maintainer | maintain-control-plane; review-advisory-evidence | AR-01 through AR-05 | implemented |

## Exact File Ownership

All paths are relative to the repository root. Shared files are edited sequentially by the primary agent. Role labels are accountability, not evidence of separate execution.

- AR-01: this file; `AGENTS.md`; `PLAN.md`; `REQUIREMENTS.md`; `README.md`; framing in `docs/PRODUCT_REQUIREMENTS.md`, `docs/V1_ROADMAP.md`, `docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`, `docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md`, and `docs/MYAI_STACKGUIDE_MODULE_ARCHITECTURE.md`; task clarifications in the parent plugin plan.
- AR-02: `.codex/agents/product-planner.toml`, `.codex/agents/catalog-architect.toml`; `.agents/skills/shape-product-slice/SKILL.md`, `.agents/skills/design-catalog-contracts/SKILL.md`, `.agents/skills/design-context-contracts/SKILL.md`, `.agents/skills/curate-catalog-taxonomy/SKILL.md`, `.agents/skills/research-github-candidates/SKILL.md`.
- AR-03: `.codex/TEAM.md`; `.codex/artifact-templates/agent-task-packet.md`; `.codex/agents/catalog-pipeline-builder.toml`, `.codex/agents/quality-evaluator.toml`; `docs/plan/plugin-v1-team-contracts.md`.
- AR-04: `.codex/agents/plugin-runtime-builder.toml`, `.codex/agents/mcp-backend-builder.toml`; `.agents/skills/build-stackguide-plugin/SKILL.md`, `.agents/skills/build-stackguide-plugin/agents/openai.yaml`, `.agents/skills/build-stackguide-mcp/SKILL.md`, `.agents/skills/build-stackguide-mcp/agents/openai.yaml`; `.agents/skills/audit-readonly-boundaries/SKILL.md`, `.agents/skills/design-recommendation-evals/SKILL.md`; sequential follow-up to `.codex/TEAM.md`.
- AR-05: `tests/test_codex_contracts.py`, `tests/test_agent_eval_grader.py`, `scripts/grade_agent_evals.py`; `evals/agents/agent-routing-cases.json`, `evals/skills/skill-activation-cases.json`, `evals/agents/team-behavior-cases.json`; `.codex/agent-eval-workflow.md`, `.codex/skill-promotion-record.md`; `TEST.md`, `EVALS.md`.
- AR-06: verification only outside `RUNLOG.md`, this task list, and status/verification sections of `PLAN.md`, `REQUIREMENTS.md`, `README.md`, and the parent plugin plan.
- Forbidden: catalog source/fixtures/generated surfaces, `.codex/config.toml`, existing model/effort defaults, Git internals, credentials, external systems, installed plugin caches, global skills, actual plugin/backend runtime directories.

## Acceptance Scenarios

| ID | Given / When / Then | Check | Evidence owner |
| --- | --- | --- | --- |
| AR-01 | Given a Russian user request, when a team member writes control-plane artifacts, then the artifacts use English while conversation may remain Russian. Existing history is retained. | Review shared language rule and English changed text; inspect old/new requirement mapping | Docs Maintainer |
| AR-02 | Given current and legacy catalog sources, when a skill chooses taxonomy or metadata, then current work uses the manifest and legacy builders remain explicitly historical. A misspelled existing source must fail validation. | Source-path checks and current/legacy boundary review | Catalog Architect |
| AR-03 | Given a planned RED test, when its named assertion fails as expected, then the owner may implement the owned fix; an unexpected failure must not be relabeled RED. | Workflow examples, task packet fields, and reviewer inspection | Quality Evaluator |
| AR-04 | Given a plugin/backend request without accepted CP-02 decisions, when the new role is selected, then it stops before runtime implementation and returns the missing contracts. | Static role/skill checks now; fresh-context behavior remains unrun | Primary orchestrator |
| AR-05 | Given an offline result packet, when routes/actions/reviews violate a case or the packet is missing, duplicate, malformed, unreviewed, or synthetic-only, then it cannot earn behavioral promotion. | Positive/negative grader unit tests | Quality Evaluator |
| AR-06 | Given passing static checks, when completion is recorded, then no model, MCP, runtime, security, or release pass is inferred. | Diff review and RUNLOG evidence ceiling | Docs Maintainer |

## Commands And Expected Evidence

Run from the repository root. Commands below are proposed until their observed outcome is recorded in RUNLOG.

```powershell
python -B -m unittest discover -s tests -p test_codex_contracts.py -v
python -B -m unittest discover -s tests -p test_agent_eval_grader.py -v
python -B scripts/grade_agent_evals.py --validate-cases evals/agents/team-behavior-cases.json
python -B -m unittest discover -s tests -v
python -B scripts/build_catalog_html.py --check
git diff --check
```

- Expected: tests pass; case validation exits zero; catalog HTML retains exact parity; no whitespace errors. A failing test is only expected RED when its assertion and owner are declared before the run.
- Product-Agent OS `validate_control_plane.py .` and `validate_agents.py .codex/agents` are additional structural gates using the installed plugin's scripts. They cannot certify routing or product behavior.
- The official skill validator requires PyYAML. If unavailable, keep that command gap explicit and use dependency-free repository contract checks; do not install dependencies merely to hide the gap.
- Do not rerun `codex doctor` as a pure config check: it includes environment/network diagnostics and its exit status is not an agent-TOML-only verdict.

## Relationship To The Product Plan

- CP-01: this remediation activates plugin-first direction and records old-to-new traceability; complete PRD/roadmap acceptance remains separately reviewable.
- CP-02: runtime, backend/storage, auth, budgets, retention, and operating decisions remain open. This remediation supplies decision/check ownership, not invented selections.
- CP-03: project schemas and fixtures remain unimplemented; team guidance must reference them as required future inputs, not existing files.
- CP-04: this slice supplies an offline team-result grader and testable corpus; a product recommendation runner, representative model runs, held-out quality evidence, and human usefulness acceptance remain separate gates.
- CP-05: authoring stack-neutral builder definitions is permitted by this approval. Execution readiness still depends on CP-02/03, a fresh session loading the updated instructions, complete task packets, and measured routing.
- CP-07 through CP-16: no product implementation or activation starts in this remediation.

## External Skills Decision

Reuse available `tdd`, `documentation-and-adrs`, browser QA, and language-specific skills when applicable. The external `anthropics/skills@mcp-builder` and `vercel-labs/agent-skills@web-design-guidelines` candidates remain optional and uninstalled. Local project skills encode the accepted four-tool and privacy boundaries without copying an external workflow wholesale.

## Completion Ledger

Local remediation is implemented with the scoped evidence below. Full YAML validation and fresh-session/model behavior remain unverified. Product CP gates remain open; these AR outcomes do not close them. Exact commands, failures, and evidence limits are recorded in RUNLOG.md.

## Detailed Task Blocks

These blocks use `task_matrix_plan_v1`. Completion timestamps identify the local implementation checkpoint, not runtime acceptance. The summary table is an index; detailed ownership and evidence are authoritative for this remediation only.

### Task `AR-01`

- Task: AR-01 - Align active control-plane direction and language
- Status: implemented
- Schema version: task_matrix_plan_v1
- Timezone: Europe/Moscow
- Plan trigger: Owner-approved team audit identified this bounded preparation gap.
- Validator target: detailed task blocks
- Date and time of task implementation: 30-08-2026 20:56
- Depends on: Owner approval
- Blocks: AR-02, AR-03
- Source: Approved team audit; parent plugin plan; current repository files named in Scope.
- Short description: Align active control-plane direction and language
- Technical value: Active documents identify plugin-first direction, retain historical context, map old IDs, and require English artifacts without claiming runtime readiness.
- Product value: Reduce implementation ambiguity without claiming the plugin exists or is ready.
- Scope: AGENTS.md; PLAN.md; REQUIREMENTS.md; README.md; docs/PRODUCT_REQUIREMENTS.md; docs/V1_ROADMAP.md; docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md; docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md; docs/MYAI_STACKGUIDE_MODULE_ARCHITECTURE.md; docs/plan/2026-08-30-agent-team-remediation-plan.md; docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md
- Non-goals: No product runtime, external skill installation, provider calls, credentials, deployment, Git mutations, or permission/model-default changes.
- Expected result: Added shared English rule, active navigation, historical notices, requirement mapping, and bounded remediation tasks.
- Acceptance criteria: Active documents identify plugin-first direction, retain historical context, map old IDs, and require English artifacts without claiming runtime readiness.
- Verification gates: python -B -m unittest discover -s tests -p test_codex_contracts.py -v; python -B -m unittest discover -s tests -p test_agent_eval_grader.py -v; product validators and git diff --check as scoped above.
- Risks / approval gates: Full hosted-PRD rewriting and CP-02 decisions remain open; historical multilingual source remains explicitly marked.
- Complexity: S
- Estimated execution time: Completed local preparation; no prospective delivery or model-cost commitment.
- Agents: Product Planner / Docs Maintainer; executed sequentially by the primary agent, not dispatched workers.
- Skills: implementation-planner; maintain-control-plane
- Output artifacts: AGENTS.md; PLAN.md; REQUIREMENTS.md; README.md; docs/PRODUCT_REQUIREMENTS.md; docs/V1_ROADMAP.md; docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md; docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md; docs/MYAI_STACKGUIDE_MODULE_ARCHITECTURE.md; docs/plan/2026-08-30-agent-team-remediation-plan.md; docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md
- Evidence owner: Product Planner / Docs Maintainer
- Docs update path: RUNLOG.md and this task file; PLAN.md links the current state.
- Rollback: Reverse only the reviewed remediation hunks in the named owned files; preserve pre-existing edits and historical records.
- Stop conditions: Missing accepted inputs, unsafe data, ownership conflict, unexpected permission need, or acceptance-changing implementation.
- Next step: CP-01 full requirements reconciliation and CP-02 accepted architecture decisions

#### Completion report

- status: implemented
- what was done: Added shared English rule, active navigation, historical notices, requirement mapping, and bounded remediation tasks.
- files touched / work locations: AGENTS.md; PLAN.md; REQUIREMENTS.md; README.md; docs/PRODUCT_REQUIREMENTS.md; docs/V1_ROADMAP.md; docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md; docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md; docs/MYAI_STACKGUIDE_MODULE_ARCHITECTURE.md; docs/plan/2026-08-30-agent-team-remediation-plan.md; docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md
- technical value delivered: Active documents identify plugin-first direction, retain historical context, map old IDs, and require English artifacts without claiming runtime readiness.
- product value delivered: Scoped preparation only; runtime and recommendation quality are not claimed.
- actual implementation date and time: 30-08-2026 20:56
- verification evidence: Control-plane validator returned ok; active-text/source-path tests pass; current diff retains historical content.
- residual risks: Full hosted-PRD rewriting and CP-02 decisions remain open; historical multilingual source remains explicitly marked.
- follow-up: CP-01 full requirements reconciliation and CP-02 accepted architecture decisions

### Task `AR-02`

- Task: AR-02 - Repair authoritative sources and candidate lifecycle guidance
- Status: implemented
- Schema version: task_matrix_plan_v1
- Timezone: Europe/Moscow
- Plan trigger: Owner-approved team audit identified this bounded preparation gap.
- Validator target: detailed task blocks
- Date and time of task implementation: 30-08-2026 20:56
- Depends on: AR-01
- Blocks: AR-04, AR-05
- Source: Approved team audit; parent plugin plan; current repository files named in Scope.
- Short description: Repair authoritative sources and candidate lifecycle guidance
- Technical value: Concrete sources resolve; current work uses the manifest; candidate overlay, evidence stage, eligibility, and curator acceptance remain separate.
- Product value: Reduce implementation ambiguity without claiming the plugin exists or is ready.
- Scope: .codex/agents/product-planner.toml; .codex/agents/catalog-architect.toml; .agents/skills/shape-product-slice/SKILL.md; .agents/skills/design-catalog-contracts/SKILL.md; .agents/skills/design-context-contracts/SKILL.md; .agents/skills/curate-catalog-taxonomy/SKILL.md; .agents/skills/research-github-candidates/SKILL.md
- Non-goals: No product runtime, external skill installation, provider calls, credentials, deployment, Git mutations, or permission/model-default changes.
- Expected result: Corrected stale root paths and legacy taxonomy routing; clarified candidate states and intake/state invariants.
- Acceptance criteria: Concrete sources resolve; current work uses the manifest; candidate overlay, evidence stage, eligibility, and curator acceptance remain separate.
- Verification gates: python -B -m unittest discover -s tests -p test_codex_contracts.py -v; python -B -m unittest discover -s tests -p test_agent_eval_grader.py -v; product validators and git diff --check as scoped above.
- Risks / approval gates: These instructions do not implement schema migrations or validate live metadata.
- Complexity: S
- Estimated execution time: Completed local preparation; no prospective delivery or model-cost commitment.
- Agents: Catalog Architect; executed sequentially by the primary agent, not dispatched workers.
- Skills: skill-creator; design-catalog-contracts
- Output artifacts: .codex/agents/product-planner.toml; .codex/agents/catalog-architect.toml; .agents/skills/shape-product-slice/SKILL.md; .agents/skills/design-catalog-contracts/SKILL.md; .agents/skills/design-context-contracts/SKILL.md; .agents/skills/curate-catalog-taxonomy/SKILL.md; .agents/skills/research-github-candidates/SKILL.md
- Evidence owner: Catalog Architect
- Docs update path: RUNLOG.md and this task file; PLAN.md links the current state.
- Rollback: Reverse only the reviewed remediation hunks in the named owned files; preserve pre-existing edits and historical records.
- Stop conditions: Missing accepted inputs, unsafe data, ownership conflict, unexpected permission need, or acceptance-changing implementation.
- Next step: CP-03 accepted schemas and explicit legacy-state compatibility mapping

#### Completion report

- status: implemented
- what was done: Corrected stale root paths and legacy taxonomy routing; clarified candidate states and intake/state invariants.
- files touched / work locations: .codex/agents/product-planner.toml; .codex/agents/catalog-architect.toml; .agents/skills/shape-product-slice/SKILL.md; .agents/skills/design-catalog-contracts/SKILL.md; .agents/skills/design-context-contracts/SKILL.md; .agents/skills/curate-catalog-taxonomy/SKILL.md; .agents/skills/research-github-candidates/SKILL.md
- technical value delivered: Concrete sources resolve; current work uses the manifest; candidate overlay, evidence stage, eligibility, and curator acceptance remain separate.
- product value delivered: Scoped preparation only; runtime and recommendation quality are not claimed.
- actual implementation date and time: 30-08-2026 20:56
- verification evidence: Source existence, broken-path rejection, known role/skill, and skill-link tests pass; catalog parity unchanged.
- residual risks: These instructions do not implement schema migrations or validate live metadata.
- follow-up: CP-03 accepted schemas and explicit legacy-state compatibility mapping

### Task `AR-03`

- Task: AR-03 - Make implementation and permission boundaries actionable
- Status: implemented
- Schema version: task_matrix_plan_v1
- Timezone: Europe/Moscow
- Plan trigger: Owner-approved team audit identified this bounded preparation gap.
- Validator target: detailed task blocks
- Date and time of task implementation: 30-08-2026 20:56
- Depends on: AR-01
- Blocks: AR-04, AR-05
- Source: Approved team audit; parent plugin plan; current repository files named in Scope.
- Short description: Make implementation and permission boundaries actionable
- Technical value: Named unit-test ownership, declared expected RED, ordinary in-scope repair, escalation, four-tool boundaries, and methodology evidence owners are explicit.
- Product value: Reduce implementation ambiguity without claiming the plugin exists or is ready.
- Scope: .codex/TEAM.md; .codex/artifact-templates/agent-task-packet.md; .codex/agents/catalog-pipeline-builder.toml; .codex/agents/quality-evaluator.toml; docs/plan/plugin-v1-team-contracts.md
- Non-goals: No product runtime, external skill installation, provider calls, credentials, deployment, Git mutations, or permission/model-default changes.
- Expected result: Recorded implementation loop, source and trust boundaries, methodology gates, and fresh-context packet requirements.
- Acceptance criteria: Named unit-test ownership, declared expected RED, ordinary in-scope repair, escalation, four-tool boundaries, and methodology evidence owners are explicit.
- Verification gates: python -B -m unittest discover -s tests -p test_codex_contracts.py -v; python -B -m unittest discover -s tests -p test_agent_eval_grader.py -v; product validators and git diff --check as scoped above.
- Risks / approval gates: Same-session edits do not prove refreshed Codex loading; no scanner bypass or live authorization test has run.
- Complexity: S
- Estimated execution time: Completed local preparation; no prospective delivery or model-cost commitment.
- Agents: Primary orchestrator / Catalog Architect; executed sequentially by the primary agent, not dispatched workers.
- Skills: agent-team-designer; maintain-control-plane
- Output artifacts: .codex/TEAM.md; .codex/artifact-templates/agent-task-packet.md; .codex/agents/catalog-pipeline-builder.toml; .codex/agents/quality-evaluator.toml; docs/plan/plugin-v1-team-contracts.md
- Evidence owner: Primary orchestrator / Catalog Architect
- Docs update path: RUNLOG.md and this task file; PLAN.md links the current state.
- Rollback: Reverse only the reviewed remediation hunks in the named owned files; preserve pre-existing edits and historical records.
- Stop conditions: Missing accepted inputs, unsafe data, ownership conflict, unexpected permission need, or acceptance-changing implementation.
- Next step: Start a fresh session before actual delegation; accepted CP-02 decisions select enforcement and runtime commands

#### Completion report

- status: implemented
- what was done: Recorded implementation loop, source and trust boundaries, methodology gates, and fresh-context packet requirements.
- files touched / work locations: .codex/TEAM.md; .codex/artifact-templates/agent-task-packet.md; .codex/agents/catalog-pipeline-builder.toml; .codex/agents/quality-evaluator.toml; docs/plan/plugin-v1-team-contracts.md
- technical value delivered: Named unit-test ownership, declared expected RED, ordinary in-scope repair, escalation, four-tool boundaries, and methodology evidence owners are explicit.
- product value delivered: Scoped preparation only; runtime and recommendation quality are not claimed.
- actual implementation date and time: 30-08-2026 20:56
- verification evidence: Agent validator and targeted contract tests pass; self-review distinguishes instructions from technical enforcement.
- residual risks: Same-session edits do not prove refreshed Codex loading; no scanner bypass or live authorization test has run.
- follow-up: Start a fresh session before actual delegation; accepted CP-02 decisions select enforcement and runtime commands

### Task `AR-04`

- Task: AR-04 - Prepare scoped plugin and MCP builder contracts
- Status: implemented
- Schema version: task_matrix_plan_v1
- Timezone: Europe/Moscow
- Plan trigger: Owner-approved team audit identified this bounded preparation gap.
- Validator target: detailed task blocks
- Date and time of task implementation: 30-08-2026 20:56
- Depends on: AR-02, AR-03
- Blocks: AR-05
- Source: Approved team audit; parent plugin plan; current repository files named in Scope.
- Short description: Prepare scoped plugin and MCP builder contracts
- Technical value: Two stack-neutral definitions and skills exist, with exact-packet ownership and missing-CP-02/03 stops; model/permission defaults stay unchanged.
- Product value: Reduce implementation ambiguity without claiming the plugin exists or is ready.
- Scope: .codex/agents/plugin-runtime-builder.toml; .codex/agents/mcp-backend-builder.toml; .agents/skills/build-stackguide-plugin/SKILL.md; .agents/skills/build-stackguide-plugin/agents/openai.yaml; .agents/skills/build-stackguide-mcp/SKILL.md; .agents/skills/build-stackguide-mcp/agents/openai.yaml; .agents/skills/audit-readonly-boundaries/SKILL.md; .agents/skills/design-recommendation-evals/SKILL.md; .codex/TEAM.md
- Non-goals: No product runtime, external skill installation, provider calls, credentials, deployment, Git mutations, or permission/model-default changes.
- Expected result: Authored two builder TOMLs and two skills with UI metadata; expanded privacy and eval instructions without installing external skills.
- Acceptance criteria: Two stack-neutral definitions and skills exist, with exact-packet ownership and missing-CP-02/03 stops; model/permission defaults stay unchanged.
- Verification gates: python -B -m unittest discover -s tests -p test_codex_contracts.py -v; python -B -m unittest discover -s tests -p test_agent_eval_grader.py -v; product validators and git diff --check as scoped above.
- Risks / approval gates: Official PyYAML-dependent skill validation remains unavailable; routing/model suitability and product execution remain unverified.
- Complexity: S
- Estimated execution time: Completed local preparation; no prospective delivery or model-cost commitment.
- Agents: Primary orchestrator; executed sequentially by the primary agent, not dispatched workers.
- Skills: agent-team-designer; skill-creator
- Output artifacts: .codex/agents/plugin-runtime-builder.toml; .codex/agents/mcp-backend-builder.toml; .agents/skills/build-stackguide-plugin/SKILL.md; .agents/skills/build-stackguide-plugin/agents/openai.yaml; .agents/skills/build-stackguide-mcp/SKILL.md; .agents/skills/build-stackguide-mcp/agents/openai.yaml; .agents/skills/audit-readonly-boundaries/SKILL.md; .agents/skills/design-recommendation-evals/SKILL.md; .codex/TEAM.md
- Evidence owner: Primary orchestrator
- Docs update path: RUNLOG.md and this task file; PLAN.md links the current state.
- Rollback: Reverse only the reviewed remediation hunks in the named owned files; preserve pre-existing edits and historical records.
- Stop conditions: Missing accepted inputs, unsafe data, ownership conflict, unexpected permission need, or acceptance-changing implementation.
- Next step: Close CP-02/03 and complete fresh-context routing evidence before builder dispatch

#### Completion report

- status: implemented
- what was done: Authored two builder TOMLs and two skills with UI metadata; expanded privacy and eval instructions without installing external skills.
- files touched / work locations: .codex/agents/plugin-runtime-builder.toml; .codex/agents/mcp-backend-builder.toml; .agents/skills/build-stackguide-plugin/SKILL.md; .agents/skills/build-stackguide-plugin/agents/openai.yaml; .agents/skills/build-stackguide-mcp/SKILL.md; .agents/skills/build-stackguide-mcp/agents/openai.yaml; .agents/skills/audit-readonly-boundaries/SKILL.md; .agents/skills/design-recommendation-evals/SKILL.md; .codex/TEAM.md
- technical value delivered: Two stack-neutral definitions and skills exist, with exact-packet ownership and missing-CP-02/03 stops; model/permission defaults stay unchanged.
- product value delivered: Scoped preparation only; runtime and recommendation quality are not claimed.
- actual implementation date and time: 30-08-2026 20:56
- verification evidence: Nine-agent validator returns ok; discovered skills, model baselines, links, and read-only reviewer checks pass.
- residual risks: Official PyYAML-dependent skill validation remains unavailable; routing/model suitability and product execution remain unverified.
- follow-up: Close CP-02/03 and complete fresh-context routing evidence before builder dispatch

### Task `AR-05`

- Task: AR-05 - Implement extensible static checks and offline result grading
- Status: implemented
- Schema version: task_matrix_plan_v1
- Timezone: Europe/Moscow
- Plan trigger: Owner-approved team audit identified this bounded preparation gap.
- Validator target: detailed task blocks
- Date and time of task implementation: 30-08-2026 20:56
- Depends on: AR-02, AR-03, AR-04
- Blocks: AR-06
- Source: Approved team audit; parent plugin plan; current repository files named in Scope.
- Short description: Implement extensible static checks and offline result grading
- Technical value: No fixed skill-count quota; malformed/incomplete/stale/unreviewed/forbidden-action packets fail; synthetic fixtures never earn behavioral promotion.
- Product value: Reduce implementation ambiguity without claiming the plugin exists or is ready.
- Scope: tests/test_codex_contracts.py; tests/test_agent_eval_grader.py; scripts/grade_agent_evals.py; evals/agents/agent-routing-cases.json; evals/skills/skill-activation-cases.json; evals/agents/team-behavior-cases.json; .codex/agent-eval-workflow.md; .codex/skill-promotion-record.md; TEST.md; EVALS.md
- Non-goals: No product runtime, external skill installation, provider calls, credentials, deployment, Git mutations, or permission/model-default changes.
- Expected result: Added strict versioned offline grading, negative tests, typed team cases, and documented result protocol; preserved the missing product-eval-runner gate.
- Acceptance criteria: No fixed skill-count quota; malformed/incomplete/stale/unreviewed/forbidden-action packets fail; synthetic fixtures never earn behavioral promotion.
- Verification gates: python -B -m unittest discover -s tests -p test_codex_contracts.py -v; python -B -m unittest discover -s tests -p test_agent_eval_grader.py -v; product validators and git diff --check as scoped above.
- Risks / approval gates: The grader validates reviewer-supplied observations and trace integrity, not reviewer authenticity, missing actions, or recommendation usefulness.
- Complexity: M
- Estimated execution time: Completed local preparation; no prospective delivery or model-cost commitment.
- Agents: Quality Evaluator; executed sequentially by the primary agent, not dispatched workers.
- Skills: design-recommendation-evals; python-code-style
- Output artifacts: tests/test_codex_contracts.py; tests/test_agent_eval_grader.py; scripts/grade_agent_evals.py; evals/agents/agent-routing-cases.json; evals/skills/skill-activation-cases.json; evals/agents/team-behavior-cases.json; .codex/agent-eval-workflow.md; .codex/skill-promotion-record.md; TEST.md; EVALS.md
- Evidence owner: Quality Evaluator
- Docs update path: RUNLOG.md and this task file; PLAN.md links the current state.
- Rollback: Reverse only the reviewed remediation hunks in the named owned files; preserve pre-existing edits and historical records.
- Stop conditions: Missing accepted inputs, unsafe data, ownership conflict, unexpected permission need, or acceptance-changing implementation.
- Next step: Prepare frozen synthetic runtime fixtures and separately authorized observed runs; CP-04 still owns the product recommendation runner

#### Completion report

- status: implemented
- what was done: Added strict versioned offline grading, negative tests, typed team cases, and documented result protocol; preserved the missing product-eval-runner gate.
- files touched / work locations: tests/test_codex_contracts.py; tests/test_agent_eval_grader.py; scripts/grade_agent_evals.py; evals/agents/agent-routing-cases.json; evals/skills/skill-activation-cases.json; evals/agents/team-behavior-cases.json; .codex/agent-eval-workflow.md; .codex/skill-promotion-record.md; TEST.md; EVALS.md
- technical value delivered: No fixed skill-count quota; malformed/incomplete/stale/unreviewed/forbidden-action packets fail; synthetic fixtures never earn behavioral promotion.
- product value delivered: Scoped preparation only; runtime and recommendation quality are not claimed.
- actual implementation date and time: 30-08-2026 20:56
- verification evidence: 16 grader tests and 11 contract tests pass; 14 team cases validate with model_runs=0.
- residual risks: The grader validates reviewer-supplied observations and trace integrity, not reviewer authenticity, missing actions, or recommendation usefulness.
- follow-up: Prepare frozen synthetic runtime fixtures and separately authorized observed runs; CP-04 still owns the product recommendation runner

### Task `AR-06`

- Task: AR-06 - Verify remediation and preserve explicit readiness gaps
- Status: implemented
- Schema version: task_matrix_plan_v1
- Timezone: Europe/Moscow
- Plan trigger: Owner-approved team audit identified this bounded preparation gap.
- Validator target: detailed task blocks
- Date and time of task implementation: 30-08-2026 20:56
- Depends on: AR-01 through AR-05
- Blocks: Product execution until its own CP gates close
- Source: Approved team audit; parent plugin plan; current repository files named in Scope.
- Short description: Verify remediation and preserve explicit readiness gaps
- Technical value: Current local checks and diff review support only scoped implementation claims; catalog and configuration baseline are preserved and all missing runtime evidence remains explicit.
- Product value: Reduce implementation ambiguity without claiming the plugin exists or is ready.
- Scope: RUNLOG.md; PLAN.md; README.md; REQUIREMENTS.md; docs/plan/2026-08-30-agent-team-remediation-plan.md; docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md
- Non-goals: No product runtime, external skill installation, provider calls, credentials, deployment, Git mutations, or permission/model-default changes.
- Expected result: Performed explicit self-review and scoped checks; recorded known gaps and unchanged external/runtime boundaries.
- Acceptance criteria: Current local checks and diff review support only scoped implementation claims; catalog and configuration baseline are preserved and all missing runtime evidence remains explicit.
- Verification gates: python -B -m unittest discover -s tests -p test_codex_contracts.py -v; python -B -m unittest discover -s tests -p test_agent_eval_grader.py -v; product validators and git diff --check as scoped above.
- Risks / approval gates: No independent agent review, fresh-session routing, model comparison, private scan, MCP activation, or release evidence exists.
- Complexity: S
- Estimated execution time: Completed local preparation; no prospective delivery or model-cost commitment.
- Agents: Quality Evaluator / Docs Maintainer; executed sequentially by the primary agent, not dispatched workers.
- Skills: maintain-control-plane; review-advisory-evidence
- Output artifacts: RUNLOG.md; PLAN.md; README.md; REQUIREMENTS.md; docs/plan/2026-08-30-agent-team-remediation-plan.md; docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md
- Evidence owner: Quality Evaluator / Docs Maintainer
- Docs update path: RUNLOG.md and this task file; PLAN.md links the current state.
- Rollback: Reverse only the reviewed remediation hunks in the named owned files; preserve pre-existing edits and historical records.
- Stop conditions: Missing accepted inputs, unsafe data, ownership conflict, unexpected permission need, or acceptance-changing implementation.
- Next step: Fresh-session instruction verification, then remaining CP-01/02 decisions before product implementation

#### Completion report

- status: implemented
- what was done: Performed explicit self-review and scoped checks; recorded known gaps and unchanged external/runtime boundaries.
- files touched / work locations: RUNLOG.md; PLAN.md; README.md; REQUIREMENTS.md; docs/plan/2026-08-30-agent-team-remediation-plan.md; docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md
- technical value delivered: Current local checks and diff review support only scoped implementation claims; catalog and configuration baseline are preserved and all missing runtime evidence remains explicit.
- product value delivered: Scoped preparation only; runtime and recommendation quality are not claimed.
- actual implementation date and time: 30-08-2026 20:56
- verification evidence: Final full suite: 36 tests passed; 14 team cases validated with zero model runs; exact HTML parity; control-plane, nine-agent, parent-plan, and remediation-plan validators returned ok.
- residual risks: No independent agent review, fresh-session routing, model comparison, private scan, MCP activation, or release evidence exists.
- follow-up: Fresh-session instruction verification, then remaining CP-01/02 decisions before product implementation
