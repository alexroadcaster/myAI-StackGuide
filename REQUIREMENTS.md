# REQUIREMENTS.md

Compact execution registry. The [active PRD](docs/PRODUCT_REQUIREMENTS.md#active-plugin-v1-requirements) owns product meaning; [roadmap](docs/V1_ROADMAP.md#active-plugin-v1-milestones) and [detailed CP plan](docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md) own phases and tasks.

## Lifecycle State

Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation records. CP-03 is implemented and verified at contract level: 22 local schemas, the presentation/publication addendum and linked fixtures pass all 46 checks. The bounded CP-04 C8/C9 join passes all 27 checks and both scorer CLI gates; synthetic compatibility is accepted, while quality corpus/baseline/thresholds and human calibration remain open. CP-05 source alignment is implemented and statically verified; fresh-session behavioral acceptance remains pending; CP-06-CP-16 remain planned, with CP-12-CP-14 deferred. Runtime and permissions are unchanged.

Product state is `partially_verified`: existing static control-plane/catalog work is not plugin runtime, retrieval quality or release evidence. CP-03 now supplies local schemas/policies/examples, the eight-view presentation/publication addendum and semantic checks. CP-03 passes full standards and semantic gates; CP-04 supplies verified C8/scorer compatibility, with quality calibration still open. No later runtime task is executed.

## Active Direction And Traceability

Stable R01-R14 identifiers are retained; their wording and task mappings below are explicitly revised by the owner, not frozen to the earlier remote/scanner-only design. R15 adds the owner's RU-EN localization requirement. The PRD retains all FR1-FR15 and cross-cutting historical dispositions. [CP-02 ADRs](specs/decisions/plugin-v1-architecture.md) define local FTS5, index/state separation, context budgets, activity semantics and integration boundaries.

| ID | Requirement | Tasks |
| --- | --- | --- |
| R01 | Codex plugin with local Python scripts, bundled catalog and SQLite FTS5 index; no hosted app, service, custom MCP UI or remote prerequisite. | CP-01, CP-02, CP-07, CP-16 |
| R02 | 1-10 adaptive questions, early useful result, resume/corrections, persistence after each answer and truthful progress. | CP-03, CP-07, CP-11 |
| R03 | Idea/empty, compact, standard and large/monorepo contexts; bounded progressive scanning with explicit coverage gaps. | CP-02, CP-03, CP-08 |
| R04 | Relevant project context may be read under user/host permissions; minimize persisted context, exclude secrets, and do not promise host-wide source isolation. No private context in public catalog/index or future MCP. | CP-02, CP-03, CP-05, CP-08, CP-15 |
| R05 | Versioned facts, inferences, assumptions, corrections, gaps and evidence references; corrections invalidate dependent retrieval and recommendations. | CP-03, CP-07, CP-08, CP-10 |
| R06 | Local lexical RAG: structured query -> SQLite FTS5/BM25 -> bounded evidence pack -> Codex comparison. Never load the entire catalog into model context; remote discovery is deferred. | CP-03, CP-04, CP-06, CP-09, CP-11 |
| R07 | Canonical dedupe, task-specific constraints/reasons/roles; distinguish creation, last push, verified last commit/release and observation dates. No blanket snapshot-age rejection. | CP-03, CP-06, CP-09, CP-10 |
| R08 | Separate catalog status, machine evidence and recommendation eligibility; curator-only acceptance. Automatic public candidate overlay is a deferred extension. | CP-03, CP-06, CP-09, CP-12, CP-13 |
| R09 | No service credentials/auth or shared writes in local V1. Future remote auth, consent, idempotency, quotas and audit require an explicit extension decision. | CP-02, CP-12, CP-14 |
| R10 | Atomic minimized state, offline HTML, immutable finalized runs, safe concurrency, recovery and version history. | CP-03, CP-07, CP-10, CP-11 |
| R11 | Pin catalog, index, schema and retrieval-policy versions/hashes; reproduce candidate selection and reject mismatches. Remote overlay/compaction remains deferred. | CP-03, CP-06, CP-09, CP-11, CP-13, CP-16 |
| R12 | Retrieval relevance, bounded context/scale, recommendation usefulness, privacy/provenance, rendered UI, local runtime and rollback evidence before local release. | CP-04, CP-11, CP-15, CP-16 |
| R13 | Help build or modernize through an actionable integration plan and coding-agent handoff. Recommendations do not execute changes; an explicit implementation request authorizes its own bounded workflow. | CP-01, CP-03, CP-05, CP-07, CP-10, CP-11, CP-15, CP-16 |
| R14 | Activity/popularity are signals, not proof of operability or fit; missing mandatory facts remain unknown. Prefer useful caveated guidance over unnecessary refusal. | CP-03, CP-04, CP-06, CP-09, CP-15 |
| R15 | One session HTML supports RU-EN interface and localized narrative, preserving canonical facts, evidence, decisions and technical literals; offline switching performs no retrieval/model call or domain-state write. | CP-03, CP-04, CP-05, CP-07, CP-09, CP-10, CP-11, CP-15, CP-16 |

Acceptance owners: Product Planner owns usefulness and scope; Catalog Architect owns local domain/retrieval/context contracts; Quality Evaluator owns tests/evals and acceptance evidence; Evidence Reviewer independently reviews provenance/permissions/claims. Builders own only their assigned runtime, source or index files.

### Legacy Execution-ID Mapping

| Existing requirement | Plugin-plan requirement | Disposition |
| --- | --- | --- |
| CP-001 through CP-005 | R01, R12, R14 | Retain control-plane and evidence goals; AR tasks repair the implementation contracts |
| V1-CAT-001, V1-TAX-001 | R06, R07, R08, R11 | Preserve v5; add normalized public cards and FTS5 index; overlay deferred, never automatic curator acceptance |
| V1-SCAN-001 | R03, R04 | Local bounded scanning replaces hosted-first project acquisition |
| V1-CTX-001 | R02, R04, R05, R10 | Add adaptive intake, corrections, resume, and sanitized state |
| V1-MEMO-001 | R07, R10, R13 | Decision Report adds an actionable integration plan/handoff; offline HTML remains a projection, no automatic execution |
| V1-EVAL-001 | R12 | Separate team behavior, deterministic product contracts, and recommendation usefulness |
| V1-GH-001 | R06, R08, R09 | GitHub retrieval stays read-only; own-backend ledger writes have a distinct approval/auth boundary |

CP-02 selects the local design; CP-03 schemas and presentation/publication joins are verified at contract level. Product quality evidence remains future work. Deferred remote contracts move to CP-12 and do not block local acceptance.

## Goal

Enable a user to build or modernize a solution faster by integrating suitable OSS, beginning with an idea or local project and ending with a persisted Brief, offline comparison and actionable integration handoff. SQLite FTS5 retrieves a bounded evidence set; the model never needs the whole catalog. No measured speedup or runtime readiness is claimed yet.

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
| `V1-CAT-001` | Define baseline and advisory repository card JSON contracts with provenance, freshness, trust, and verification fields. | `docs/PRODUCT_REQUIREMENTS.md` FR7/FR13 and Data Requirements | Schema fixtures distinguish required baseline fields from optional advisory fields and reject missing identity/provenance. | Catalog Architect | `contract_verified` |
| `V1-TAX-001` | Define the V1 taxonomy contract and controlled evolution rules. The current version has 111 thematic leaves, 14 navigation containers and one review queue; node count is not a product quota. | `docs/V1_ROADMAP.md` Milestone 1 | Category IDs, labels, parent relationships, aliases, ownership, and duplicate rules are explicit. Future node-count changes require a reviewed versioned amendment supported by a repeated coherent functional cluster. | Catalog Architect | `contract_verified` |
| `V1-SCAN-001` | Define allowlist-first scanning and sensitive-source exclusions. | `docs/PRODUCT_REQUIREMENTS.md` FR3/FR4, Context Scanner | Policy covers included groups, denied patterns, no execution, no dependency install, redaction, and observable scan reporting. | Catalog Architect | `contract_verified` |
| `V1-CTX-001` | Define the Project Context Brief JSON contract. | `docs/PRODUCT_REQUIREMENTS.md` FR5, Context Scanner | Facts, inferences, evidence, confidence, corrections, missing context, and sanitized source references are separate. | Catalog Architect | `contract_verified` |
| `V1-MEMO-001` | Define the recommendation memo JSON contract. | `docs/PRODUCT_REQUIREMENTS.md` FR8–FR13 | Output includes category path, roles, shortlist, avoid/defer, comparison, reading path, caveats, evidence, and next human decision. | Catalog Architect | `contract_verified` |
| `V1-EVAL-001` | Define recommendation eval case and result formats. | `docs/PRODUCT_REQUIREMENTS.md` FR15, `docs/V1_ROADMAP.md` Milestone 9 | Cases map requirement to scenario, rubric, deterministic checks, human judgment, evidence owner, and promotion threshold. | Quality Evaluator | `partially_implemented` |
| `V1-GH-001` | Stage a read-only GitHub MCP permission and provenance contract after the schemas exist. | FR2/FR13 and current GitHub MCP research | Tool allowlist, no-write mode, data boundary, evidence provenance, rate-limit behavior, and fallback are reviewed before activation. | Catalog Architect | `approval_required` |

## Product Hypothesis And Metrics

- Primary outcome: useful integration/modernization plans and time to the first validated integration slice, when a user elects to implement.
- Process metrics: time to a useful report, avoidable questions/tool calls, evidence completeness, actionable handoff completeness and correction rate.
- Retrieval metrics: held-out Recall@k/nDCG@k, hard-constraint false matches/exclusions, RU/EN/alias coverage, query latency/memory and evidence-pack bytes/tokens under a declared measurement method.
- Counter-metrics: unsupported operability/currentness claims, stale observations presented as current, missing mandatory integration facts, unnecessary refusals, secret exposure, unauthorized actions and context-budget overruns.
- These are evaluation goals, not measured gains. CP-04 freezes thresholds/runner/judgments before quality runs; CP-15 records independent outcomes. Use the exact CAT-10/CP-06 2,500-card snapshot for actual relevance and capacity, and a separately labeled 10,000-row synthetic fixture only for headroom; synthetic rows do not prove semantic quality.
- No telemetry collection is introduced. User project context remains confidential; the SQLite bundle contains only public source-owned catalog data.

## Scope

Completed assignment: implement and verify the CP-03 contract addendum and bounded CP-04 compatibility join against the owner-approved [session workspace design](docs/plan/plugin-v1-session-workspace-design.md). Publish one HTML from session start through each committed answer/phase; answers and saved decisions remain in Codex, with one canonical state writer. Static UI dictionaries and revision-bound narrative translations are distinct from RU/EN retrieval aliases. The [contract addendum](specs/artifact/session-workspace-contract.md) is implemented and verified: 46 CP-03 checks, 27 C8 checks and scorer CLI gates pass. Runtime is unchanged. Preserve historical completion evidence. Mobile adaptation is excluded; concept approval is complete and rendered implementation acceptance is pending.

Current owner-authorized work: save the full [CP-05 audit](docs/plan/2026-08-31-cp05-control-plane-audit.md), reconcile its task and implement scoped existing agent/skill/Codex/eval/control-plane alignment. PLAN.md owns exact outputs and static versus fresh-session gates. Preserve R01-R15, historical evidence and unrelated work; append RUNLOG.

The completed CP-03 assignment authorized the registered local schemas, policies, fixtures and tests. Its then-out-of-scope list was: runtime/index creation, catalog refresh/regeneration, protected .codex/.agents definitions or behavioral JSON edits, installations without permission, host/model/permission changes, Git operations and external activation. Later implementation requires its own assignment; CP-12-14 additionally needs a new remote extension decision.

## Constraints

- Target desktop PCs and laptops only; mobile adaptation is explicitly excluded by the owner. Desktop window resizing, keyboard access, readable text zoom and RU/EN layout remain acceptance requirements.
- Preserve the current canonical source, template and generated artifacts until CAT-08 performs its pinned reconciliation. The canonical intermediate snapshot has 1,800 repositories and 126 taxonomy nodes; CAT-07A freezes a separate non-canonical 2,500-identity candidate. CAT-10 owns the verified snapshot handoff, and CP-06 owns normalized metadata/card/index adapters from that exact version. Browser enrichment is not persisted source proof. Source changes precede regeneration and parity checks.
- No blanket snapshot-age rejection. Separate creation/push/verified commit/release/observation/build dates and unknowns; activity/popularity alone cannot prove quality, operability or fit.
- Local `catalog_only` source uses `sqlite_fts5`; public index is immutable/read-only at runtime. Pin source/card/index/policy versions and reject mismatches visibly. No vector/provider/server dependency, startup index rebuild or full-catalog prompt fallback.
- Allow relevant project context within actual user/host permissions. Scanner and targeted reads remain bounded with secrets/unsafe paths excluded; scanner never executes project code. Persist minimized findings/references, not raw source or chat; no private data in public index/future MCP.
- Recommendation output may propose integration commands/steps and a coding-agent handoff. It does not execute them; a user implementation request authorizes its own scope without unnecessary repeated confirmations.
- Artifact writes remain under `docs/myai-stackguide/` with CP-02 state/recovery/storage limits; no automatic pruning, upload, global cache or telemetry.
- Use completed fresh-context packets and disjoint ownership for any delegated work; CP-05 aligns loaded roles/skills with the revised scope before runtime dispatch.

## Acceptance And Evidence

Every task maps requirement -> scenario -> owner -> command/evidence -> rollback. Local CP-03 covers C1-C6/C9; CP-04 owns C8; remote C4/C7 move to deferred CP-12. Positive/negative/edge contracts precede runtime acceptance. Product evaluation combines deterministic retrieval/boundary checks with human integration usefulness; static configuration or synthetic throughput alone is insufficient.

CP-15 depends only on CP-04/10/11. CP-16 depends only on CP-01/05/06/15. Their transitive local dependencies exclude CP-12/13/14. Installation/publication and remote effects retain their actual authorization boundaries. Current commands, evidence ceiling and remaining gaps are recorded in RUNLOG.

## Open Decisions And Ownership

- Selected, not open: local plugin, SQLite FTS5/BM25, no strict host-wide isolation promise, no blanket snapshot TTL and actionable integration handoff.
- CP-03 / Catalog Architect: these local contracts, grammar/aliases/weights, allocation and activity/compatibility semantics are accepted. Future amendments require assigned consumer review; selected engineering values are not calibrated quality claims.
- CP-04 / Quality Evaluator + Product Planner: held-out relevance judgments, the offline captured-result scorer evals/plugin-v1/evaluate_retrieval.py and metric fixtures, exact command contract, calibrated thresholds and human rubric. Bind actual captures to the CAT-10/CP-06 2,500-card snapshot and stratify thin/dense leaves, containers, baseline/expansion cohorts, aliases and secondary-category dedupe. A 16/20 score alone is insufficient.
- CP-05 / primary + Quality Evaluator: align existing definitions/fixtures and verify fresh-session behavior within file permissions; static passes do not promote behavior.
- CP-06 / Pipeline Builder + Curator: consume the exact CAT-10 2,500-card snapshot, source-persisted metadata coverage, evidence-qualified seed, canonical dedupe and build/index parity; exhaustive recommendation narratives are not a prerequisite for a useful slice.
- CP-08/09/11 / builders + Quality Evaluator: containment and runtime FTS5 compatibility, all 111 leaf/14 container/review routes, relevance limitations, fixed caps, actual 2,500-card performance, separately labeled 10,000-row synthetic headroom and the intended route.
- Future CP-12-14 owner: remote architecture/auth/consent/storage/cost/retries/commands and index update protocol only if selected. Hosted OAuth, archive intake, standalone CLI, SDK/widget and scheduled compaction are deferred.
