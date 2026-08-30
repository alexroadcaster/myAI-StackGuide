# PLAN.md

Active Product-Agent OS plan for myAI-StackGuide. Detailed product milestones remain in `docs/V1_ROADMAP.md`; this file owns the current execution order and gates.

## Lifecycle

- Current state: `team_ready` for the contract-definition slice after static validation.
- Entry evidence: V1 PRD and roadmap exist; current requirements are mapped in `REQUIREMENTS.md`.
- Build boundary: no hosted app, provider activation, or live GitHub access is authorized by this plan.
- Exit condition: the six contract artifacts have schemas/policies, fixtures, deterministic checks, review evidence, and a `RUNLOG.md` handoff.
- Stop condition: missing ownership, overlapping write scopes, unverified source claims, secret-bearing data, failed checks, or required external approval.

## Active Dependency Order

1. Stabilize the control plane and custom-agent team.
2. Define repository card and taxonomy contracts.
3. Define scanner and Project Context Brief contracts.
4. Define recommendation memo and eval contracts.
5. Validate cross-contract identity, provenance, confidence, and evidence fields.
6. Stage the GitHub MCP read-only permission/provenance review.
7. Only after contract acceptance, plan catalog expansion and hosted application slices.

## Task Matrix

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
| Custom-agent configuration | `present_verified` | Product Planner | Agent validator, contract tests, and Codex strict-config from the remediation run |
| Repository skill discovery | `present_verified` | Product Planner | Canonical `.agents/skills` location, no path pinning, and contract test from the remediation run |
| GPT-5.6 role policy | `configured_not_behaviorally_verified` | Quality Evaluator | Static model mapping and eval specs; no fresh-context model comparison yet |
| Fresh-context handoff | `proposal_staged` | Product Planner | `.codex/artifact-templates/agent-task-packet.md` and completed packet per task |
| Repository contracts | `applicable_missing` | Catalog Architect | Schemas, fixtures, and checks from `V1-S1`–`V1-S5` |
| Recommendation eval contract | `applicable_missing` | Quality Evaluator | `V1-S6` artifacts and rubric review |
| GitHub MCP permission review | `approval_required` | Project Owner | `V1-S7` review and explicit activation decision |
| Hosted runtime evidence | `not_applicable` | Project Owner | Not applicable to the current contract-definition slice |
| FSD structure | `not_applicable` | Catalog Architect | No application UI structure exists yet |
| Production telemetry | `not_applicable` | Product Planner | No hosted runtime exists; define before beta |

## Rollback

- Preserve all pre-existing dirty-worktree changes.
- Review the exact diff before reverting any artifact.
- Roll back only files created or lines added by the rejected slice; do not regenerate or overwrite unrelated catalog outputs.
- MCP, hooks, automation, workflows, deployment, Git history, and external systems remain unchanged, so no runtime rollback is required for `CP-S1`.

## Handoff Rule

Every agent receives a completed `.codex/artifact-templates/agent-task-packet.md` containing the task ID, complete context, allowed sources, owned and forbidden files, commands, expected evidence, stop conditions, and sequential fallback. Agents must return files touched, commands run, observed evidence, unsupported claims, risks, and the next role.
