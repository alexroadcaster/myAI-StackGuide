# REQUIREMENTS.md

Compact Product-Agent OS execution registry for myAI-StackGuide. The product definition and full V1 requirements remain in `docs/PRODUCT_REQUIREMENTS.md`; milestone sequencing remains in `docs/V1_ROADMAP.md`.

## Lifecycle State

- State: `partially_verified` for the product. CP-01 reconciles documentation only; behavioral/product evidence remains open.
- Usage mode: `standard-product` with `ai-product` and read-only integration constraints.
- Decision horizon: `MVP` leading to `beta`.
- Build status: plugin-first direction and CP-01 documentation implementation authorized by the owner; plugin/backend implementation and runtime acceptance remain gated by the detailed CP plan.
- CP-01 outcome: `implemented`, documentation scope verified and independently reviewed; no product-runtime acceptance is implied. Current-run evidence is in RUNLOG.md.

## Active Direction And Traceability

The active product requirements are [PRD: Plugin V1](docs/PRODUCT_REQUIREMENTS.md#active-plugin-v1-requirements), R01 through R14. [V1 roadmap](docs/V1_ROADMAP.md#active-plugin-v1-milestones) owns phases; [PLAN.md](PLAN.md) and the [detailed CP plan](docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md) own execution. AR-01 through AR-06 are completed local preparation, not the active work queue. CP-01 is the authorized documentation slice; CP-02 decisions are next, without automatic implementation authorization.

The PRD contains complete FR1-FR15 and cross-cutting legacy mappings. Historical sections below and in the supporting documents are retained for traceability, not a second set of V1 requirements. R01-R14 acceptance is planned product behavior, not delivered capability.

| Active requirement | Execution tasks | Acceptance / evidence owner |
| --- | --- | --- |
| R01 | CP-01, CP-02, CP-07, CP-16 | Product Planner / plugin packaging and runtime review |
| R02 | CP-03, CP-07, CP-11 | Quality Evaluator / adaptive intake, correction and resume cases |
| R03 | CP-02, CP-03, CP-08 | Catalog Architect + Quality Evaluator / bounded scan cases |
| R04 | CP-03, CP-08, CP-12, CP-15 | Evidence Reviewer + Quality Evaluator / data-boundary negative cases |
| R05 | CP-03, CP-07, CP-08, CP-10 | Quality Evaluator / versioned fact and correction contracts |
| R06 | CP-09, CP-12, CP-13, CP-14 | Quality Evaluator / both retrieval lanes and visible fallback |
| R07 | CP-03, CP-06, CP-09, CP-13 | Catalog Architect + Quality Evaluator / eligibility and provenance |
| R08 | CP-03, CP-12, CP-15 | Evidence Reviewer / candidate versus curator acceptance |
| R09 | CP-02, CP-12, CP-14, CP-15 | Quality Evaluator + Evidence Reviewer / auth and side-effect evidence |
| R10 | CP-03, CP-07, CP-10, CP-11 | Quality Evaluator / state recovery, offline HTML and run history |
| R11 | CP-03, CP-12, CP-13, CP-16 | Quality Evaluator / pinned snapshot and overlay replay |
| R12 | CP-04, CP-11, CP-14, CP-15, CP-16 | Quality Evaluator + Product Planner / quality, privacy and release gates |
| R13 | CP-01, CP-07, CP-14, CP-16 | Product Planner + Evidence Reviewer / advisory and approval boundaries |
| R14 | CP-06, CP-09, CP-15 | Evidence Reviewer / no popularity-to-fit or unsupported readiness claims |

### Legacy Execution-ID Mapping

| Existing requirement | Plugin-plan requirement | Disposition |
| --- | --- | --- |
| CP-001 through CP-005 | R01, R12, R14 | Retain control-plane and evidence goals; AR tasks repair the implementation contracts |
| V1-CAT-001, V1-TAX-001 | R06, R07, R08, R11 | Preserve current v5 manifest; add candidate overlay separately, never automatic curator acceptance |
| V1-SCAN-001 | R03, R04 | Local bounded scanning replaces hosted-first project acquisition |
| V1-CTX-001 | R02, R04, R05, R10 | Add adaptive intake, corrections, resume, and sanitized state |
| V1-MEMO-001 | R07, R10, R13 | Decision Report remains advisory; offline HTML is a projection |
| V1-EVAL-001 | R12 | Separate team behavior, deterministic product contracts, and recommendation usefulness |
| V1-GH-001 | R06, R08, R09 | GitHub retrieval stays read-only; own-backend ledger writes have a distinct approval/auth boundary |

CP-02 decisions, CP-03 schemas, and product quality runs remain open. No missing architecture decision is accepted implicitly by this mapping.

## Goal

Help a user choose what open-source solution to inspect, compare, adopt, defer, or avoid for an idea or local project, ending with a saved Project Context Brief and offline Decision Report. The selected entrypoint is a Codex plugin with local scripts and remote MCP, not a hosted project-acquisition app. CP-01 aligns this goal and its acceptance across documents; it does not create schemas or runtime.

## Historical Requirement Registry

The rows below preserve the earlier contract-definition baseline, including its statuses and source references. Their active successors are mapped above; old counts, hosted/private-access assumptions, and read-only MCP shorthand do not add requirements or authorize execution.

| ID | Requirement | Source | Acceptance | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| `CP-001` | Maintain a compact control plane with requirements, plan, test, eval, evidence, ownership, and stop conditions. | `AGENTS.md`, user request | All six root control-plane files exist and validation reports no missing files. | Product Planner | `implemented` |
| `CP-002` | Define project-scoped Codex agents with disjoint ownership and fresh-context handoffs. | user request, `AGENTS.md` | Agent TOML files parse, required fields exist, and `.codex/TEAM.md` maps ownership and sequential fallback. | Product Planner | `implemented` |
| `CP-003` | Assign the smallest relevant set of reusable project skills to every custom agent. | owner-approved team audit | Assigned names resolve to discovered skills; no fixed skill quota; trigger and output quality require separate behavioral evidence. | Product Planner | `partially_verified` |
| `CP-004` | Use official portable Codex project locations and runtime configuration. | official Codex documentation | Skills are discovered from `.agents/skills`, agent files contain no workspace-absolute skill paths, and `.codex/config.toml` sets bounded multi-agent defaults. | Product Planner | `present_verified` |
| `CP-005` | Configure a tier-aware GPT-5.6 model and reasoning policy without inflating readiness claims. | official GPT-5.6 migration and prompting guidance | Sol/high and Terra/medium role mappings parse, static eval specs exist, and behavioral suitability remains explicitly unverified until fresh-context comparisons run. | Quality Evaluator | `configured_not_behaviorally_verified` |
| `CAT-V5-001` | Make the current HTML v5 catalog reproducible from source-owned data and a stable template without changing its user-owned content. | project owner decision, `docs/UNIFIED_CATALOG.html` | Canonical manifest and schema exist, the builder validates identity/count/reference invariants, and generated HTML matches the checked-in artifact byte-for-byte. | Catalog Pipeline Builder | `implemented_verified` |
| `V1-CAT-001` | Define baseline and advisory repository card JSON contracts with provenance, freshness, trust, and verification fields. | `docs/PRODUCT_REQUIREMENTS.md` FR7/FR13 and Data Requirements | Schema fixtures distinguish required baseline fields from optional advisory fields and reject missing identity/provenance. | Catalog Architect | `planned` |
| `V1-TAX-001` | Define the V1 taxonomy contract and controlled evolution rules for 60–90 categories. | `docs/V1_ROADMAP.md` Milestone 1 | Category IDs, labels, parent relationships, aliases, ownership, and duplicate rules are explicit. | Catalog Architect | `planned` |
| `V1-SCAN-001` | Define allowlist-first scanning and sensitive-source exclusions. | `docs/PRODUCT_REQUIREMENTS.md` FR3/FR4, Context Scanner | Policy covers included groups, denied patterns, no execution, no dependency install, redaction, and observable scan reporting. | Catalog Architect | `planned` |
| `V1-CTX-001` | Define the Project Context Brief JSON contract. | `docs/PRODUCT_REQUIREMENTS.md` FR5, Context Scanner | Facts, inferences, evidence, confidence, corrections, missing context, and sanitized source references are separate. | Catalog Architect | `planned` |
| `V1-MEMO-001` | Define the recommendation memo JSON contract. | `docs/PRODUCT_REQUIREMENTS.md` FR8–FR13 | Output includes category path, roles, shortlist, avoid/defer, comparison, reading path, caveats, evidence, and next human decision. | Catalog Architect | `planned` |
| `V1-EVAL-001` | Define recommendation eval case and result formats. | `docs/PRODUCT_REQUIREMENTS.md` FR15, `docs/V1_ROADMAP.md` Milestone 9 | Cases map requirement to scenario, rubric, deterministic checks, human judgment, evidence owner, and promotion threshold. | Quality Evaluator | `planned` |
| `V1-GH-001` | Stage a read-only GitHub MCP permission and provenance contract after the schemas exist. | FR2/FR13 and current GitHub MCP research | Tool allowlist, no-write mode, data boundary, evidence provenance, rate-limit behavior, and fallback are reviewed before activation. | Catalog Architect | `approval_required` |

## Product Hypothesis And Metrics

- Hypothesis: grounding repository guidance in a corrected Project Context Brief and evidence-bearing catalog cards reduces research time without presenting discovery signals as due diligence.
- Primary value metric: percentage of target-user recommendation memos judged useful for the next decision.
- Input metrics: evidence completeness, shortlist relevance, advisory-card coverage, and time to first memo.
- Counter-metrics: Project Context Brief correction rate, false-positive recommendation rate, stale evidence rate, and sensitive-source policy violations.
- Privacy classification: repository metadata is public or explicitly authorized; private repository content is confidential and minimized.
- Metric classification: useful decisions and reduced research time are intended outcomes; evidence coverage and time from plugin intake to Brief/report are product indicators. No measured improvement is claimed.
- Analytics tracking plan: `applicable_missing`; collecting product telemetry requires a separate privacy/consent decision. CP-01 adds no telemetry or target values.
- Release measurement evidence: `applicable_missing`; no plugin release or recommendation-quality pass is claimed.

## Scope

In scope for CP-01: align this registry, PLAN.md, README, PRD, roadmap, product/scanner/architecture summaries, the CP-01 task record, and RUNLOG; preserve historical text and map it to R01-R14. Product scope is defined in the active PRD, not by this documentation assignment.

Next dependency: CP-02 architecture, runtime, auth, storage, scan budgets, consent and retention decisions; no values are selected in CP-01. CP-03 schemas and CP-04 eval contracts follow their own dependencies and assignments.

Out of scope:

- Plugin/backend code, schemas, tests/eval policy changes, durable agent/skill/config changes, catalog edits or regeneration.
- Hosted app, GitHub OAuth/project acquisition, private repository access, or credentials.
- MCP activation, candidate upload, deployment, publication, hooks, schedules, GitHub Actions, or Agents SDK runners. Future authorized own-backend writes are distinct from read-only GitHub retrieval.
- Claims that catalog scores prove production readiness, security, legal, or procurement suitability.

## Constraints

- Preserve `data/source_repos.csv` and the two dated research JSON files as their documented source-of-truth layers.
- Preserve the current `data/catalog_manifest.json` and template unchanged; old quantity goals do not mandate a new catalog refresh or imply advisory eligibility.
- Change source data or builders before generated catalog outputs; regenerate and verify parity when those sources change.
- Separate `catalog_snapshot`, `github_live_evidence`, `curator_decision`, and `recommendation_output` states.
- Preserve read-only scanning, no code execution, no dependency installation, and sensitive-file exclusions.
- Scanner raw source remains local; the model receives sanitized structures only, with no direct raw-source bypass. MCP accepts only a minimal DiscoveryQuery and public candidate metadata, never the full Brief, answers, excerpts, absolute paths, secrets or private project identifiers.
- Future plugin writes are limited to `docs/myai-stackguide/` in the selected project. Own-backend candidate writes require auth and explicit consent or a bounded standing policy; refusal preserves a visible catalog-only report. No contribution-consent exception permits private project data in the public ledger.
- Do not place secrets, private repository content, customer data, credentials, or raw conversations in artifacts or fixtures.
- Use fresh-context handoffs and disjoint write ownership for subagents.

## Acceptance And Evidence

- Behavior changes require a declarative scenario or an explicit accepted gap.
- Every non-trivial plan row names exact files, owner, forbidden files, expected evidence, rollback, and stop conditions.
- Schema and policy work must include positive, negative, and boundary fixtures before implementation claims.
- AI recommendation quality needs deterministic contract checks plus a human-judgment rubric; either one alone is insufficient.
- Current command evidence is recorded in `RUNLOG.md`; generated files or status summaries alone are not proof.

## Open Decisions And Ownership

- CP-02 / Catalog Architect and product owner: supported runtime/OS and packaging, backend/storage/auth, credential location, consent/retention, per-user limits, retry/latency/cost budgets, quick/topology/time/depth/file-size limits, monorepo precedence, replay/concurrency/recovery and stale/archive policy.
- CP-03 / Catalog Architect: exact schemas, advisory eligibility fields, lifecycle/compatibility and migration contracts. The current taxonomy remains the starting point, not an accepted new schema.
- CP-04 / Quality Evaluator and Product Planner: representative corpus, executable runner contract and human calibration; no new quality thresholds in CP-01.
- CP-05 / primary orchestrator and Quality Evaluator: loaded role/skill routing and model comparison evidence. Explicit delegation during documentation work does not close this gate.
- CP-06 / Catalog Pipeline Builder: evidence-qualified seed/advisory coverage; historical 1,000 and 100-200 quantity targets are not new release gates.
- Hosted project OAuth, archive upload, standalone CLI, SDK/widget, hosted boards and general catalog API are deferred alternatives, not unresolved choices blocking plugin V1.
