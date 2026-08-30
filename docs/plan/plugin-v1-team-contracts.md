# Plugin V1 Team Execution Contracts

Scope: development-team guidance for the accepted plugin-first plan. These contracts do not implement runtime enforcement or grant access. Read the active CP task and accepted architecture decisions before using a section below. Paths are relative to the repository root.

## Source Routing

- Current catalog: `data/catalog_manifest.json`, `data/catalog_manifest.schema.json`, `templates/unified_catalog.html`, and `scripts/build_catalog_html.py`.
- Legacy account taxonomy: `data/categories.json` and `scripts/build_catalog.py`; legacy unified Markdown has its separate dated research inputs. Do not use either to replace current v5 identities, metadata, or taxonomy.
- Product direction: `docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md`; active ownership and approved slice: `PLAN.md` and its linked task packet.
- Product background: `docs/PRODUCT_REQUIREMENTS.md`, `docs/V1_ROADMAP.md`, `docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`, `docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md`. Hosted-first detail is historical where marked.
- Planned `specs/**` files are missing prerequisites until accepted and created; never claim to have read a proposed schema.

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
- Evidence stage: `discovered_live`, `identity_validated`, `machine_evidence_complete`, or rejected evidence as defined by CP-03.
- `recommendation_eligibility`: `primary_eligible`, `reference_only`, or `blocked`; a request-specific recommendation role is another decision.

Legacy research labels such as `normalized_candidate` and `verified_catalog_entry` describe historical workflow, not automatic mappings to the new enums. CP-03 owns an explicit compatibility mapping and must reject ambiguous promotion.

A separately authorized own-backend candidate overlay may append public candidate evidence after minimum gates without curator acceptance. It must not silently mutate the frozen curated snapshot. Pin `catalog_snapshot_id` and `candidate_overlay_version`; preserve canonical identity on dedupe. Retractions and invalidation use new events, not hidden history edits. Compaction is not curator approval and its scheduler is separately activated.

## Intake, Context, And Local State

CP-03/07 own typed state and transition contracts; this document does not invent their final enum values.

- Intake asks 1-10 adaptive questions. Reuse existing answers; expose relevant gaps; end early when enough context exists. On cancellation, disclose incompleteness rather than synthesizing answers.
- Persist sanitized state atomically after each answer and completed phase. A correction preserves observed facts, increments the relevant version, and invalidates dependent recommendations. Resume must validate schema/run/version compatibility.
- Keep observed facts, inferences, user corrections, assumptions, missing context, and evidence references separate. Do not infer credentials, permissions, budget approval, or product facts from missing answers.
- Empty projects are valid. Monorepo precedence, quick/topology/time/depth caps and file-size limits require accepted CP-02 decisions. Standard/deep budgets are in the product plan; cap exhaustion yields partial coverage and truthful confidence.
- Prevent path traversal, symlink/junction escape, sensitive reads, project subprocesses, and dependency installation. Avoid including raw excerpts, secret values, absolute local paths, or raw user answers in model/tool-facing scanner output.
- `state.json` is mutable current state; `status.html` is an escaped offline projection; finalized run JSON is immutable. Concurrent runs cannot overwrite each other. Crash/recovery behavior must be tested.

## Permission And Tool Contract

| Surface | Allowed intent | Required evidence before runtime acceptance |
| --- | --- | --- |
| Development team | Read/edit assigned repository files under active permissions | Loaded instructions, exact task ownership, local checks; this is distinct from product scanner access |
| Product scanner | Read only approved project scope and emit sanitized structures | Canonical containment, sensitive exclusions, bounded I/O, negative tests, cancellation and error-output inspection |
| Product model | Consume sanitized context; no direct raw-source bypass | Selected runtime/tool surface and an adversarial bypass test; prompt wording alone is not enforcement |
| `catalog_delta_get` | Read bounded snapshot/overlay deltas | Version pins, pagination, compatibility, expiry and malformed-input tests |
| `github_discover` | Read public GitHub evidence from minimal sanitized DiscoveryQuery | Query/candidate caps, provenance, no private project fields, rate-limit fallback |
| `candidate_batch_upsert` | Authorized public-metadata write to our backend | Per-request auth/authz, consent or bounded standing policy, backend provenance validation, idempotency and concurrency tests |
| `candidate_status_get` | Read permitted candidate status | Authorization where applicable, bounded IDs/results, no cross-user information leak |

The GitHub retrieval surface has no GitHub write tools. The own-backend write is not read-only and must have accurate MCP annotations. Every tool needs input/output schemas, typed errors, bounded results, and server-side validation. Tool annotations, role ownership prose, and skills are not authorization enforcement. Inherited tools/permissions must be reviewed rather than assumed absent.

Auth refusal, missing consent, network failure, and ingestion failure must preserve a visible catalog-only path; a failed upsert must not prevent delivering the local report. Credentials stay outside project artifacts. No raw Brief, answers, excerpts, absolute paths, or project identifiers enter the public candidate ledger.

## Methodology And Decision Gates

| Gate | Owner | Required contract / evidence | Product task |
| --- | --- | --- | --- |
| Acceptance-first | Product Planner + Quality Evaluator | Requirement -> scenario -> check -> evidence owner; negative cases and non-goals | CP-01/04 |
| Runtime and packaging | Catalog Architect | Supported OS/runtime, prerequisites, exact paths/commands, plugin manifest/MCP mapping, clean install and fresh-session verification plan | CP-02/16 |
| Domain/API | Catalog Architect | Identity/lifecycle invariants, consumers, versions, errors, permission matrix; focused domain modeling, not forced full DDD | CP-02/03 |
| Scanner privacy | Catalog Architect + Plugin Runtime Builder | Data flow/threat cases and technically testable raw-source boundary; no prompt-only guarantee | CP-02/08 |
| Local state | Plugin Runtime Builder | Atomic writes, version invalidation, concurrency, interruption/recovery, escaped offline output | CP-07/10 |
| Backend failure behavior | MCP Backend Builder | Dependency failure matrix, rate/retry/time budgets, auth expiry, idempotency, consistency, migrations and backup/restore | CP-02/12 |
| Operations | MCP Backend Builder | Health semantics, sanitized observability, latency/availability targets or explicit owner gap, secret handling, disable/rollback runbook | CP-02/12/14 |
| Team and AI quality | Quality Evaluator | Versioned cases/results, direct/indirect/incomplete/non-trigger/adversarial checks, trace review, baseline vs one-lower comparison | CP-04/05/15 |
| UI acceptance | Plugin Runtime Builder + Quality Evaluator | Offline/error/empty/partial states, accessibility, escaping, rendered browser checks | CP-10/15 |
| Release | Docs Maintainer + Evidence Reviewer | Versioned artifact, compatibility, clean installation evidence, rollback, approval for publication/scheduler | CP-16 |

Use the existing CP-02/03 artifacts for these gates. Do not generate one template per row or select a backend/framework/provider to make a checklist look complete. Final runtime decisions require accepted ADR evidence.

## Verification And Promotion

Static configuration tests, offline grading, actual fresh-context agent behavior, product synthetic runtime, live integration, and human usefulness are different evidence levels. None substitutes for another.

Agent/skill cases and offline result protocol are owned by `evals/agents/team-behavior-cases.json`, `scripts/grade_agent_evals.py`, and `.codex/agent-eval-workflow.md`. Synthetic grader fixtures cannot authorize promotion. The product rubric remains in `EVALS.md`; CP-04 owns its executable recommendation runner and human calibration.

Changing durable instructions requires a fresh session to verify what Codex loaded. A same-session file check cannot prove discovery or routing of newly created roles/skills. Do not change model/effort defaults without the recorded comparison and owner decision.

## Source Basis And Limits

The following official pages were reviewed in the preceding 2026-08-30 audit: [Codex subagents](https://developers.openai.com/codex/subagents), [Build skills](https://developers.openai.com/plugins/build/skills), [Build an MCP server](https://developers.openai.com/plugins/build/mcp-server), and [Plugin packaging](https://developers.openai.com/plugins/build/plugins). They support placement, focused instructions, tool/schema/auth separation, and package testing. Recheck volatile packaging/auth details during CP-02/16. The project-specific workflow and thresholds here are not universal OpenAI requirements.
