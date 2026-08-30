# PLAN.md

Active Product-Agent OS plan for myAI-StackGuide. Detailed product milestones remain in `docs/V1_ROADMAP.md`; this file owns the current execution order and gates.

## Lifecycle

- Current state: `partially_verified` after local agent-team remediation. Static contracts and offline grader checks pass; fresh-session loading, behavioral runs, and product CP-02/03 gates remain open. The historical `team_ready` did not apply to plugin-first runtime.
- Entry evidence: V1 PRD and roadmap exist; current requirements are mapped in `REQUIREMENTS.md`.
- Build boundary: no hosted app, provider activation, or live GitHub access is authorized by this plan.
- Remediation exit: AR-01 through AR-06 have scoped changes, current local checks, self-review, and a RUNLOG handoff. Product exit remains the separately accepted CP plan, not the historical six-contract slice.
- CP-01: `implemented` with documentation checks and independent review; the owner's instruction authorized this scope. No additional product or architecture decision was needed. The next unexecuted task is CP-02.
- Stop condition: missing ownership, overlapping write scopes, unverified source claims, secret-bearing data, failed checks, or required external approval.

## Active Dependency Order

Completed local preparation: [Agent Team Audit Remediation](docs/plan/2026-08-30-agent-team-remediation-plan.md), AR-01 through AR-06. CP-01 is the owner-authorized documentation reconciliation; its result and checks are recorded in the [detailed CP plan](docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md#task-cp-01) and RUNLOG. Product requirements are [R01-R14 in the PRD](docs/PRODUCT_REQUIREMENTS.md#active-plugin-v1-requirements); phases are in the [active roadmap](docs/V1_ROADMAP.md#active-plugin-v1-milestones).

1. CP-01: align requirements, history, scope and acceptance; documentation only.
2. CP-02: accept architecture, runtime and permission decisions. CP-04 eval-contract preparation can follow CP-01 independently, with CP-03 compatibility review before acceptance.
3. CP-03: accept schemas; CP-05: complete builder readiness after CP-01/02, preserving already-authored roles. Runtime dispatch also requires applicable CP-03 contracts and actual loading/routing evidence.
4. CP-06-CP-11: implement and verify the local vertical slice under separate assignments; prove one useful synthetic case first, without MCP.
5. CP-12-CP-14: local mock-first backend and mixed retrieval after CP-11, then separately authorized test-environment integration.
6. CP-15-CP-16: independent verification, owner acceptance and release packaging; publication/deployment require their own authorization.

CP-01 does not authorize the later tasks. The detailed task dependency graph governs over this phase summary. The historical sequence and matrix below are not a competing dispatch queue.

### CP-01 Execution Boundary

- Owner authorization: implement CP-01 with agents and skills, preserving the accepted plugin-first product meaning. No new hosting, disclosure, cost, retention or implementation decision is implied.
- Primary acts as Product Planner, then sequential Docs Maintainer; independent read-only scope audit and final Evidence Reviewer receive complete fresh-context packets. One writer owns shared documents.
- Exact editable files: `REQUIREMENTS.md`, `PLAN.md`, `README.md`, `docs/PRODUCT_REQUIREMENTS.md`, `docs/V1_ROADMAP.md`, `docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`, `docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md`, `docs/MYAI_STACKGUIDE_MODULE_ARCHITECTURE.md`, `docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md` (CP-01/status references only), and `RUNLOG.md`.
- Forbidden: product code, schemas, catalog/source/generated data, agent/skill/config changes, TEST/EVALS policy changes, credentials, external actions and Git history. Temporary local verification artifacts are not product implementation.
- Acceptance: all R01-R14 map to unchanged CP tasks; FR1-FR15 and older milestones/cross-cutting rules have explicit dispositions; active docs agree on scanner/model/MCP/local-write boundaries; open CP-02 choices remain open; historical requirements remain recoverable.
- Verification: V-DOC, local links/anchors and UTF-8, requirement coverage and dependency DAG, historical-text preservation, targeted control-plane contracts, protected-surface diff, and independent semantic review. No new product tests or model evaluation are required for this documentation slice.
- Runtime evidence: the current session exposes the project instructions and requested skills; their files and team contracts were read before explicit delegation. This does not prove automatic named-agent loading, implicit skill selection, model suitability or CP-05 promotion.
- Rollback: review and reverse only CP-01 document changes against the starting worktree; preserve any unrelated edits. No runtime rollback or catalog regeneration is needed.

### Historical Contract-Definition Sequence

1. Stabilize the control plane and custom-agent team.
2. Define repository card and taxonomy contracts.
3. Define scanner and Project Context Brief contracts.
4. Define recommendation memo and eval contracts.
5. Validate cross-contract identity, provenance, confidence, and evidence fields.
6. Stage the GitHub MCP read-only permission/provenance review.
7. Only after contract acceptance, plan catalog expansion and hosted application slices.

## Task Matrix

The CP-S and V1-S rows below retain historical traceability. New execution uses the linked AR/CP task plans, not these rows as fresh dispatch authorization.

| Task | Owner | Exact output files | Depends on | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| `CP-S1` | Product Planner | `REQUIREMENTS.md`, `PLAN.md`, `TEST.md`, `EVALS.md`, `.codex/config.toml`, `.codex/TEAM.md`, `.codex/agents/*.toml`, `.agents/skills/*/SKILL.md`, `tests/test_codex_contracts.py`, `evals/**` | Existing PRD and roadmap | Product-Agent OS validators, contract tests, skill validators, TOML parse, placeholder scan, `git diff --check` | `partially_verified` |
| `CP-S2` | Quality Evaluator | `.codex/model-reasoning-policy.md`, `.codex/agent-eval-workflow.md`, `.codex/skill-promotion-record.md`, `evals/agents/**`, `evals/skills/**` | `CP-S1` | Static contract tests now; fresh-context GPT-5.6 baseline versus one-lower behavioral comparisons before promotion | `configured_not_behaviorally_verified` |
| `CAT-V5-SOURCE` | Catalog Pipeline Builder | `data/catalog_manifest.json`, `data/catalog_manifest.schema.json`, `templates/unified_catalog.html`, `scripts/build_catalog_html.py`, `docs/UNIFIED_CATALOG.html`, `tests/test_catalog_v5_pipeline.py` | Owner-selected reproducibility option | Exact byte/hash parity, manifest invariants, focused tests, documentation and residual-gap review | `implemented_verified` |
| `V1-S1` | Catalog Architect | `specs/catalog/repository-card.schema.json`, `specs/catalog/repository-card-examples.json` | `CP-S1` | Positive/negative JSON Schema fixtures and provenance review | `planned` |
| `V1-S2` | Catalog Architect | `specs/catalog/taxonomy.yaml`, `specs/catalog/taxonomy-rules.md` | `V1-S1` | Unique IDs, alias collision check, category coverage report | `planned` |
| `V1-S3` | Catalog Architect | `specs/scanner/scan-policy.yaml`, `specs/scanner/exclusion-cases.json` | `V1-S1` | Sensitive-source negative cases and no-execution/no-install assertions | `planned` |
| `V1-S4` | Catalog Architect | `specs/context/project-context-brief.schema.json`, `specs/context/project-context-brief-examples.json` | `V1-S3` | Fact/inference/confidence/correction contract tests | `planned` |
| `V1-S5` | Catalog Architect | `specs/recommendation/recommendation-memo.schema.json`, `specs/recommendation/recommendation-memo-examples.json` | `V1-S1`, `V1-S2`, `V1-S4` | Role, evidence, avoid/defer, caveat, and next-decision contract tests | `planned` |
| `V1-S6` | Quality Evaluator | `evals/scenario.schema.json`, `evals/result.schema.json`, `evals/cases/*.json` | `V1-S4`, `V1-S5` | Schema validation, rubric review, boundary and regression cases | `planned` |
| `V1-S7` | Catalog Architect | `.codex/reviews/github-mcp-permission-review.md` | `V1-S1`, `V1-S4`, `V1-S5` | Owner review of tool allowlist, read-only mode, provenance, retention, fallback, and no-activation proof | `approval_required` |

## Ownership Boundaries

- Product Planner owns root requirements and active plan. It does not edit implementation scripts or source data.
- Catalog Architect owns new `specs/**` contracts. It does not edit generated catalog outputs.
- GitHub Research Curator owns `research/**` proposals and candidate evidence. Changes to `data/source_repos.csv` require a sequential handoff to the Pipeline Builder.
- Catalog Pipeline Builder owns `scripts/**` and source-first generator changes assigned by an accepted plan. Generated outputs are shared release surfaces and cannot be edited in parallel.
- Quality Evaluator owns `TEST.md`, `EVALS.md`, `tests/**`, and `evals/**`; it does not repair implementation failures unless explicitly reassigned.
- Docs & Evidence Maintainer owns `RUNLOG.md`, source-backed documentation updates, and handoff closure. It does not change product meaning without Product Planner review.
- Evidence Reviewer is read-only and can block promotion; it does not implement fixes.

## Verification Strategy

- Static control-plane validation before assigning agents.
- JSON/YAML schema validation and positive/negative fixtures before contract acceptance.
- Generated-output parity after any source or builder change.
- Recommendation evals with deterministic contract checks and human judgment before promotion.
- Runtime, browser, privacy, and GitHub permission evidence are later gates; static files do not prove them.

## Conditional Readiness Gates

| Gate | Status | Owner | Required evidence |
| --- | --- | --- | --- |
| Control-plane presence | `present_verified` | Product Planner | Product-Agent OS validator output from current run |
| Custom-agent file structure | `present_verified` | Product Planner | Current nine-agent validator and contract tests; refreshed runtime loading is not yet verified |
| Repository skill discovery | `present_verified` | Product Planner | Canonical `.agents/skills` location, no path pinning, and contract test from the remediation run |
| GPT-5.6 role policy | `configured_not_behaviorally_verified` | Quality Evaluator | Static model mapping and eval specs; no fresh-context model comparison yet |
| Fresh-context handoff | `proposal_staged` | Product Planner | `.codex/artifact-templates/agent-task-packet.md` and completed packet per task |
| Repository contracts | `applicable_missing` | Catalog Architect | CP-03 schemas/fixtures; V1-S1-V1-S5 remain historical references |
| Recommendation eval contract | `applicable_missing` | Quality Evaluator | CP-04 runner/corpus and human rubric; offline team grader is separate |
| MCP permission review | `approval_required` | Project Owner | CP-02/03 read/write/auth contracts and CP-14 bounded activation decision |
| Hosted runtime evidence | `not_applicable` | Project Owner | Not applicable to the current contract-definition slice |
| FSD structure | `not_applicable` | Catalog Architect | No application UI structure exists yet |
| Production telemetry | `not_applicable` | Product Planner | Not part of CP-01; collection requires an explicit privacy/consent design |

## Rollback

- Preserve all pre-existing dirty-worktree changes.
- Review the exact diff before reverting any artifact.
- Roll back only files created or lines added by the rejected slice; do not regenerate or overwrite unrelated catalog outputs.
- MCP, hooks, automation, workflows, deployment, Git history, and external systems remain unchanged, so no runtime rollback is required for `CP-S1`.

## Handoff Rule

Every agent receives a completed `.codex/artifact-templates/agent-task-packet.md` containing the task ID, complete context, allowed sources, owned and forbidden files, commands, expected evidence, stop conditions, and sequential fallback. Agents must return files touched, commands run, observed evidence, unsupported claims, risks, and the next role.
