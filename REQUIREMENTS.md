# REQUIREMENTS.md

Compact Product-Agent OS execution registry for myAI-StackGuide. The product definition and full V1 requirements remain in `docs/PRODUCT_REQUIREMENTS.md`; milestone sequencing remains in `docs/V1_ROADMAP.md`.

## Lifecycle State

- State: `partially_verified` after local team remediation; structural checks pass, behavioral/product evidence remains open. The earlier registry below retains historical traceability.
- Usage mode: `standard-product` with `ai-product` and read-only integration constraints.
- Decision horizon: `MVP` leading to `beta`.
- Build status: plugin-first direction accepted; team remediation authorized; plugin/backend implementation and runtime acceptance remain gated by the detailed CP plan.

## Active Direction And Traceability

The current product direction is `docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md` (R01 through R14). The active bounded task list is `docs/plan/2026-08-30-agent-team-remediation-plan.md`. Earlier hosted-first requirements are historical where they conflict; they must not silently govern new task packets.

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

Define the source-owned schemas, policies, taxonomy, and eval contract needed before building the hosted GitHub read-only product.

## Requirement Registry

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
- Analytics tracking plan: `applicable_missing`; it is required before hosted beta telemetry, not before the contract-definition slice.
- Release measurement evidence: `applicable_missing`; no hosted product release exists.

## Scope

In scope for the next slice:

- Repository card schema.
- Category taxonomy contract.
- Scanner allowlist and exclusion policy.
- Project Context Brief schema.
- Recommendation memo schema.
- Eval scenario and result formats.
- Read-only GitHub evidence provenance design after the schema contracts.

Out of scope:

- Hosted application implementation.
- GitHub OAuth activation or private repository access.
- MCP server activation or write-capable GitHub tools.
- Automated ingestion, deployment, hooks, schedules, GitHub Actions, or Agents SDK runners.
- Claims that catalog scores prove production readiness, security, legal, or procurement suitability.

## Constraints

- Preserve `data/source_repos.csv` and the two dated research JSON files as their documented source-of-truth layers.
- Change source data or builders before generated catalog outputs; regenerate and verify parity when those sources change.
- Separate `catalog_snapshot`, `github_live_evidence`, `curator_decision`, and `recommendation_output` states.
- Preserve read-only scanning, no code execution, no dependency installation, and sensitive-file exclusions.
- Do not place secrets, private repository content, customer data, credentials, or raw conversations in artifacts or fixtures.
- Use fresh-context handoffs and disjoint write ownership for subagents.

## Acceptance And Evidence

- Behavior changes require a declarative scenario or an explicit accepted gap.
- Every non-trivial plan row names exact files, owner, forbidden files, expected evidence, rollback, and stop conditions.
- Schema and policy work must include positive, negative, and boundary fixtures before implementation claims.
- AI recommendation quality needs deterministic contract checks plus a human-judgment rubric; either one alone is insufficient.
- Current command evidence is recorded in `RUNLOG.md`; generated files or status summaries alone are not proof.

## Open Decisions

- Minimum advisory fields required before a repository can become a primary candidate.
- First 60–90 categories and the initial 100–200 high-confidence repositories.
- Private repository retention default and deletion SLA.
- Hosted model/retrieval stack and cost/latency budget.
- Exact GitHub OAuth and MCP permission profile; activation remains separately approval-gated.
