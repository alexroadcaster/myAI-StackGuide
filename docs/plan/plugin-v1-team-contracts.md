# Plugin V1 Team Execution Contracts

Scope: development-team guidance, revised 2026-08-31 for the owner-selected local SQLite FTS5, relevant-context, activity-evidence and integration-handoff plan. These contracts do not implement runtime enforcement or grant access. Read the active CP task and accepted architecture decisions before using a section below. Paths are relative to the repository root.

## Source Routing

- Current canonical catalog: `data/catalog_manifest.json`, `data/catalog_manifest.schema.json`, `templates/unified_catalog.html`, and `scripts/build_catalog_html.py`. CAT-10 has frozen the exact 2,500-identity CP-06 handoff in `docs/reports/catalog-final-freeze-2026-09-01.json`; the CAT-07A artifact is retained only as historical pre-application candidate evidence.
- Legacy account taxonomy: `data/categories.json` and `scripts/build_catalog.py`; legacy unified Markdown has its separate dated research inputs. Do not use either to replace current v5 identities, metadata, or taxonomy.
- Product direction: `docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md`; active ownership and approved slice: `PLAN.md` and its linked task packet.
- Product background: `docs/PRODUCT_REQUIREMENTS.md`, `docs/V1_ROADMAP.md`, `docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`, `docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md`. Hosted-first detail is historical where marked.
- Local C1-C6/C9 specs include the CP-03 presentation/publication addendum and linked historical/current fixtures. `CP-03-C9-V2` contract-verifies the active card/activity/policy/index tuple and matching C8 captures; full CP-03 standards/semantic and C8 envelope/scorer compatibility checks pass. CP-04 quality calibration and downstream CP-06/09 runtime acceptance remain open. Existing CP-02 ADRs are design evidence. Remote C4/C7 belongs to deferred CP-12 and does not block local CP-03. Never claim to have read a proposed schema.

## Implementation Loop And Handoff

1. Confirm exact owned implementation files, exact test files, requirement IDs, accepted contracts, permitted actions, and expected evidence in the task packet. A directory alone is not an implementation assignment.
2. State one observable acceptance scenario before changing behavior. Use a synthetic fixture and a public seam where practical.
3. For a test-first slice, name the expected failing assertion and failure reason before running RED. A missing dependency, unexpected import error, unrelated failure, or permission denial is not expected RED.
4. Implement the smallest owned change, run the targeted check, and inspect its observed result. Continue ordinary fix/check cycles within ownership; do not hand off each routine failure. Stop if the fix would alter acceptance, another owner's files, permissions, or a shared schema.
5. Broaden checks once the semantic slice passes, proportional to changed surfaces. Do not repeat unchanged broad suites after documentation-only adjustments.
6. Hand off exact file changes, command results, supported/unsupported claims, rollback, unresolved risks, and next owner. Refactoring is separately reviewable and must retain the same acceptance behavior.

Test ownership is explicit, not automatic: Quality Evaluator owns acceptance/eval definitions. A builder may own named unit-test files only when the task packet assigns them and releases any overlapping evaluator ownership. Otherwise the evaluator authors tests and hands them off sequentially; the builder runs but does not rewrite those tests. The reviewer remains read-only.

## Candidate Identity And Lifecycle

Keep three axes independent:

- `catalog_status`: `candidate` is not `accepted`; only a separate curator decision can assign acceptance.
- Evidence stage: local `baseline`, `identity_validated`, or `advisory_evidence_complete` as defined by CP-03. Remote `discovered_live` / `machine_evidence_complete` and ledger rejection semantics remain deferred CP-12 work; do not map them automatically.
- `recommendation_eligibility`: `primary_eligible`, `reference_only`, or `blocked`; a request-specific recommendation role is another decision.

Legacy research labels such as `normalized_candidate` and `verified_catalog_entry` describe historical workflow, not automatic mappings to the new enums. CP-03 records the explicit mapping in [taxonomy rules](../../specs/catalog/taxonomy-rules.md); ambiguous promotion is rejected.

A separately authorized own-backend candidate overlay may append public candidate evidence after minimum gates without curator acceptance. It must not silently mutate the frozen curated snapshot. Pin `catalog_snapshot_id` and `candidate_overlay_version`; preserve canonical identity on dedupe. Retractions and invalidation use new events, not hidden history edits. Compaction is not curator approval and its scheduler is separately activated.

## Intake, Context, And Local State

CP-03/07 own typed state and transition contracts; this document does not invent their final enum values.

- Intake asks 1-10 adaptive questions. Reuse existing answers; expose relevant gaps; end early when enough context exists. On cancellation, disclose incompleteness rather than synthesizing answers.
- Persist sanitized state atomically after each answer and completed phase. A correction preserves observed facts, increments the relevant version, and invalidates dependent recommendations. Resume must validate schema/run/version compatibility.
- Keep observed facts, inferences, user corrections, assumptions, missing context, and evidence references separate. Do not infer credentials, permissions, budget approval, or product facts from missing answers.
- Empty projects are valid. Monorepo precedence, quick/topology/time/depth caps and file-size limits require accepted CP-02 decisions. Standard/deep budgets are in the product plan; cap exhaustion yields partial coverage and truthful confidence.
- Prevent path traversal, symlink/junction escape, sensitive reads, project subprocesses, and dependency installation. Structured scanner output remains minimized. Separately selected relevant excerpts may inform Codex transiently within actual authorization; persist only minimized findings/safe references, not raw source, secrets or chat. Both paths obey sensitive exclusions and containment.
- `state.json` is mutable current state; `status.html` is an escaped offline projection; finalized run JSON is immutable. Concurrent runs cannot overwrite each other. Crash/recovery behavior must be tested.

## Session Workspace And Localization

Read [workspace contract](../../specs/artifact/session-workspace-contract.md) for exact fields/revisions and [desktop design](plugin-v1-session-workspace-design.md) for all 49 subsections. The eight views are Goal, Questions, Scan, Context, Options, Compare, Integration and History. This inventory is coverage, not a UI-density success metric.

- Publish one session HTML from the first committed partial state, without waiting for a Brief, scan or recommendation. Null/not-started/unknown/stale/legacy states remain useful. Desktop and laptop only; no mobile adaptation.
- Codex asks questions, accepts answers/corrections, scans and composes recommendations. HTML displays saved answers/evidence and copyable next actions; it is not a second input store, live scanner, retrieval engine or command runner.
- CP-07 owns canonical state writes and commit/publication orchestration; CP-10 owns rendering. CP-08/09 feed the same boundary. Keep domain content, storage and presentation revisions distinct. Finalized history is immutable; compatible legacy reads cannot silently upgrade it.
- Saved state and published HTML can differ after failure. Preserve saved answers and the previous valid HTML; report both revisions and typed errors to Codex. Retry rendering only within accepted bounds, cancel obsolete renders, and never let a stale render replace a newer publication. The opened HTML is a reloadable snapshot, not a live observer.
- Separate bundled static RU/EN dictionary labels, localized narrative presentation and lexical retrieval aliases. Narrative translations bind to the same canonical field/source hash, evidence, literal values and relevant content revision. Validate bindings before save/render; semantic equivalence still needs human review.
- Language display switching performs no domain write, scan, retrieval, model or translation-provider call. Missing narrative translation shows the original plus an explicit partial/unavailable notice. Missing static keys fail build. Apply accepted state/HTML/evidence budgets without duplicating translations in the retrieval pack.
- CP-10 A implements shell/localization; B views 1-4; C views 5-7; D History/recovery. Quality Evaluator owns browser/state/meaning evidence, Product Planner checks useful decisions, Evidence Reviewer audits claim limits. Images and static parity are not runtime acceptance.
- Integration output names source-supported integration surfaces, affected components, steps/prerequisites, first validation and rollback. Displayed commands are proposals. An explicit ordinary coding request may authorize a bounded implementation handoff without blanket refusal; installs, disclosure, destructive or external actions retain their boundaries.

## Permission And Tool Contract

| Surface | Allowed intent | Required evidence before runtime acceptance |
| --- | --- | --- |
| Development team | Read/edit assigned repository files under active permissions | Loaded instructions, exact task ownership, local checks; this is distinct from product scanner access |
| Product scanner | Read only approved project scope and emit sanitized structures | Canonical containment, sensitive exclusions, bounded I/O, negative tests, cancellation and error-output inspection |
| Product model | Consume the Brief, bounded public evidence and relevant authorized project context | Useful-read and sensitive-exclusion traces; no full-project ingestion/persistence or host-wide isolation claim |
| Local retrieval | Read bundled public SQLite FTS5 with a compiled bounded query | Actual FTS5 route, source/index/policy pins, read-only open, caps and explicit no-hit versus failure |
| `catalog_delta_get` | Read bounded snapshot/overlay deltas | Version pins, pagination, compatibility, expiry and malformed-input tests |
| `github_discover` | Read public GitHub evidence from minimal sanitized DiscoveryQuery | Query/candidate caps, provenance, no private project fields, rate-limit fallback |
| `candidate_batch_upsert` | Authorized public-metadata write to our backend | Per-request auth/authz, consent or bounded standing policy, backend provenance validation, idempotency and concurrency tests |
| `candidate_status_get` | Read permitted candidate status | Authorization where applicable, bounded IDs/results, no cross-user information leak |

The four remote rows above are deferred CP-12-14 extension contracts; none is required for local CP-15/16. The GitHub retrieval surface has no GitHub write tools. The own-backend write is not read-only and must have accurate MCP annotations. Every tool needs input/output schemas, typed errors, bounded results, and server-side validation. Tool annotations, role ownership prose, and skills are not authorization enforcement. Inherited tools/permissions must be reviewed rather than assumed absent.

Auth refusal, missing consent, network failure, and ingestion failure must preserve a visible catalog-only path; a failed upsert must not prevent delivering the local report. Credentials stay outside project artifacts. No raw Brief, answers, excerpts, absolute paths, or project identifiers enter the public candidate ledger.

## Local Retrieval And Integration Contracts

After the atomic `CP-03-C9-V2` contract gate, CP-06 consumes only the exact CAT-10 2,500-record snapshot and emits one self-contained `RepositoryCardV2` per positive numeric `github_repository_id`; no public card fact lives only in a metadata sidecar. The same numeric ID joins index/result/evidence/memo/integration consumers. Exact catalog IDs remain lineage inside card identity, historical `owner/name` aliases are separate searchable names, upstream and catalog descriptions remain distinct, and one typed classification-assignment list preserves role/kind/parent/source. Normalized repository, delivery, activity, advisory, provenance and evidence sections preserve unknowns plus baseline/expansion lineage without browser enrichment.

CP-06 builds the paired FTS v2/card-2.0.0/policy-2.0.0/index-format-2 assets. The index projection uses fixed explicit columns for current name, historical aliases, upstream description, catalog description, topics, category labels, use cases, integration surface and best-for. CP-09 opens only that paired index read-only, validates pins, compiles/escapes structured queries, returns numeric canonical IDs and exact matched fields, verifies all leaf/container/review routes and assignment dedupe, and enforces the CP-03 60-candidate/12-card/48-KiB ceilings across variants. Mixed v1/v2 artifacts fail explicitly; there is no coercion, rebuild or active v1 fallback. Model context never receives the whole catalog; public index never receives user context. Actual SQLite support and query route require evidence; a prose/static pass is not activation.

Creation, push, verified commit/release, observation and build dates are separate. No snapshot TTL automatically rejects useful candidates. Missing mandatory adoption facts remain unknown and trigger concrete checks, while baseline-valid cards can still be retrieved. Activity/popularity alone does not prove operability or fit. Catalog status, eligibility and role remain independent.

Report output includes integration surface, affected components, steps/prerequisites, first validation, rollback and a coding-agent handoff. Proposed commands are allowed but not automatically executed or claimed tested. A user implementation request can authorize ordinary scoped coding; do not repeat permissions or refuse merely because the workflow began as a recommendation. Secret/install/external/destructive/cost boundaries remain in force.

CP-05 owns role/skill and behavior-case alignment for R04/R13/R15 using the exact audit/file registry. Source edits, static checks and fresh-session behavior are separate gates; inspect PLAN.md and RUNLOG.md for current evidence. No model/host permission change may bypass a mismatch. Local readiness cases are separate from deferred CP-12/13 extension cases.

## Methodology And Decision Gates

| Gate | Owner | Required contract / evidence | Product task |
| --- | --- | --- | --- |
| Acceptance-first | Product Planner + Quality Evaluator | Requirement -> scenario -> check -> evidence owner; negative cases and non-goals | CP-01/04 |
| Runtime and packaging | Catalog Architect | Supported OS/runtime, prerequisites, exact paths/commands, local manifest/index/FTS5 compatibility; remote wiring deferred, clean install and fresh-session verification plan | CP-02/16 |
| Domain/API | Catalog Architect | Identity/lifecycle invariants, consumers, versions, errors, permission matrix; focused domain modeling, not forced full DDD | CP-02/03 |
| Scanner privacy | Catalog Architect + Plugin Runtime Builder | Useful relevant-context reads, containment/exclusions, minimized persistence and no scanner execution; no host-isolation promise | CP-02/08 |
| Local retrieval | Pipeline Builder + Plugin Runtime Builder | Source-owned metadata/cards/index, query grammar/aliases, BM25/dedupe/constraints, total context caps and version pairing | CP-03/06/09 |
| Integration output | Plugin Runtime Builder + Product Planner | Sourced plan, first validation slice and coding handoff; no automatic execution, no blanket refusal of authorized coding | CP-03/10/11/15 |
| Local state | Plugin Runtime Builder | Atomic writes, version invalidation, concurrency, interruption/recovery, escaped offline output | CP-07/10 |
| Backend failure behavior | MCP Backend Builder | Dependency failure matrix, rate/retry/time budgets, auth expiry, idempotency, consistency, migrations and backup/restore | Deferred CP-12 |
| Operations | MCP Backend Builder | Health semantics, sanitized observability, latency/availability targets or explicit owner gap, secret handling, disable/rollback runbook | Deferred CP-12/14 |
| Team and AI quality | Quality Evaluator | Versioned cases/results, direct/indirect/incomplete/non-trigger/adversarial checks, trace review, baseline vs one-lower comparison | CP-04/05/15 |
| UI acceptance | Plugin Runtime Builder + Quality Evaluator | Offline/error/empty/partial states, accessibility, escaping, rendered browser checks | CP-10/15 |
| Release | Assigned Builder + Quality Evaluator; Docs Maintainer records and Evidence Reviewer audits | Local package/index/FTS5 compatibility, clean installation and rollback; no remote prerequisite; publication separately authorized | CP-16 |

Use the existing CP-02/03 artifacts for these gates. Do not generate one template per row or select a backend/framework/provider to make a checklist look complete. Final runtime decisions require accepted ADR evidence.

## Verification And Promotion

Static configuration tests, offline grading, actual fresh-context agent behavior, product synthetic runtime, live integration, and human usefulness are different evidence levels. None substitutes for another.

Agent/skill cases and offline result protocol are owned by `evals/agents/team-behavior-cases.json`, `scripts/grade_agent_evals.py`, and `.codex/agent-eval-workflow.md`. Synthetic grader fixtures cannot authorize promotion. The product rubric remains in `EVALS.md`; CP-04 owns its executable recommendation runner and human calibration.

Changing durable instructions requires a fresh session to verify what Codex loaded. A same-session file check cannot prove discovery or routing of newly created roles/skills. Do not change model/effort defaults without the recorded comparison and owner decision.

## Source Basis And Limits

The following official pages were reviewed in the preceding 2026-08-30 audit: [Codex subagents](https://developers.openai.com/codex/subagents), [Build skills](https://developers.openai.com/plugins/build/skills), [Build an MCP server](https://developers.openai.com/plugins/build/mcp-server), and [Plugin packaging](https://developers.openai.com/plugins/build/plugins). They support placement, focused instructions, tool/schema/auth separation, and package testing. Recheck volatile packaging/auth details during CP-02/16. The project-specific workflow and thresholds here are not universal OpenAI requirements.
