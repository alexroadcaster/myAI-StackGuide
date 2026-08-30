# Product Requirements: myAI-StackGuide V1

## Status

Active product requirements for the selected plugin-first V1. Requirements describe intended behavior; plugin, scanner, recommendations and MCP runtime are not implemented by CP-01.

V1 entrypoint decision: **Codex plugin + bounded local scanner + remote MCP**, without custom MCP UI.

This PRD owns product meaning and acceptance for R01-R14; the [detailed CP plan](plan/2026-08-30-codex-plugin-v1-implementation-plan.md) owns task contracts and engineering defaults. [REQUIREMENTS.md](../REQUIREMENTS.md) maps execution IDs; [V1 roadmap](V1_ROADMAP.md) owns milestone order. The historical appendix is preserved in full and is not active acceptance. CP-01 applies the owner's accepted direction; runtime, storage, auth, budget and retention choices remain open in CP-02.

## Active Product Definition And Users

myAI-StackGuide helps founders/product owners, product managers, engineers and internal operators choose what open-source solution to inspect, compare, adopt, defer or avoid for a goal and local project. An idea or empty workspace is a valid input. Non-technical owners remain the primary ICP; their outcome is a plain-language decision they can discuss with an engineer, not a requirement to connect GitHub.

The entrypoint is a Codex plugin combining a skill, local scripts and remote MCP, without custom MCP UI. The workflow ends with a saved Project Context Brief and Decision Report in local offline HTML. The report includes project understanding, constraints, category path, role-based shortlist, fit reasons, comparison, avoid/defer guidance, reading path, evidence, caveats and the next human decision. A justified no-match is valid.

The product does not install recommended software, modify the analyzed project's source, execute its scripts/tests/build, perform Git operations, or deploy it. A subsequent implementation workflow needs separate authorization. Writing the plugin's own local artifacts and authorized public candidate metadata is distinct from the read-only scanner.

## Active Plugin V1 Requirements

The IDs and task mappings below preserve R01-R14 from the owner-provided plugin direction. All acceptance checks remain future product evidence; documentation reconciliation does not pass them.

| ID | Required behavior and acceptance | Tasks |
| --- | --- | --- |
| R01 | Public Codex plugin: skill + local scripts + remote MCP; no hosted project-acquisition app or custom MCP UI. Packaging/support prerequisites require CP-02 verification and CP-16 clean-install evidence. | CP-01, CP-02, CP-07, CP-16 |
| R02 | Ask 1-10 adaptive questions only when the answer changes scope, eligibility or decision. Reuse answers, persist sanitized state after each answer, support resume/corrections and truthful progress. At the limit proceed with explicit assumptions or `clarification_required`, never invented answers. | CP-03, CP-07, CP-11 |
| R03 | Support idea/empty, compact, standard and large/monorepo contexts with progressive bounded scanning. Empty is valid; exhausted budgets yield `coverage_partial` and visible uninspected areas. CP-02 closes unresolved budget and precedence rules. | CP-02, CP-03, CP-08 |
| R04 | Raw source stays inside the local scanner/sanitizer. The model receives sanitized structures only; MCP receives a minimal allowlisted DiscoveryQuery. No source-reading agent bypass, raw excerpts, full Brief, answers, local absolute paths or private project identifiers enter MCP/ledger. | CP-03, CP-08, CP-12, CP-15 |
| R05 | Version and separate facts, inferences, assumptions, corrections, gaps and evidence references. Corrections preserve evidence history and invalidate dependent recommendations. | CP-03, CP-07, CP-08, CP-10 |
| R06 | After a preliminary Brief, run local catalog and bounded public GitHub discovery lanes in parallel when authorized. Auth/consent refusal, unavailable discovery or rate limits produce explicit catalog-only fallback; no silent live-success claim. | CP-09, CP-12, CP-13, CP-14 |
| R07 | Dedupe by canonical identity, apply hard constraints, retain reason codes and roles, and show source/freshness badges. Unknown mandatory constraints do not satisfy a match; each primary candidate needs traceable fit and evidence. | CP-03, CP-06, CP-09, CP-13 |
| R08 | Automatically append eligible public candidates only within an authorized overlay workflow. Keep `catalog_status`, evidence stage and `recommendation_eligibility` separate; machine evidence never assigns curator `accepted`. | CP-03, CP-12, CP-15 |
| R09 | Require auth/authz, per-user limits, audit, idempotency, bounded retries and public-provenance validation for own-backend writes; no anonymous mutation. Credentials stay outside project artifacts. Exact mechanisms remain CP-02 decisions. | CP-02, CP-12, CP-14, CP-15 |
| R10 | Atomically persist `docs/myai-stackguide/state.json` after answers and phases. Generate deterministic offline `status.html`; finalized `runs/{run_id}.json` snapshots are immutable. Support safe crash recovery, version history and concurrent-run protection. | CP-03, CP-07, CP-10, CP-11 |
| R11 | Pin `catalog_snapshot_id` plus `candidate_overlay_version`. Compact after 100 new candidates or 24 hours; scheduler activation is separate. Replay, retention, concurrent updates and retractions require CP-02/03 contracts. | CP-03, CP-12, CP-13, CP-16 |
| R12 | Require recommendation evals, privacy/provenance gates, rendered browser QA, actual runtime evidence, rollback and owner acceptance before release. Prove one useful local synthetic case before expanding; preserve separate evidence levels. | CP-04, CP-11, CP-14, CP-15, CP-16 |
| R13 | End with a Decision Report and next human decision. Installation, source modification, Git, deployment/publication and external writes require distinct authorization; the authorized candidate-overlay exception is narrowly defined below. | CP-01, CP-07, CP-14, CP-16 |
| R14 | Popularity, legacy scores, incomplete metadata and static checks do not prove fit, security, legal/procurement suitability or production readiness. Show unknowns and caveats rather than promoting them into verified facts. | CP-06, CP-09, CP-15 |

## Active Journey And Output

1. Start or resume the plugin in a selected local project, or describe an idea; establish goal, stage, constraints and adoption mode through adaptive intake.
2. Before file access, disclose scan scope, exclusions, local persistence, model-facing sanitization and the separate MCP transmission boundary. Warn users not to type secrets into Codex chat.
3. Run only the authorized bounded scanner; show coverage, exclusions, cancellation or missing context honestly. Do not run project commands.
4. Build a preliminary Brief from sanitized observations and answers. Let the user correct it; version changes invalidate dependent results, including any provisional matching.
5. Match the pinned catalog; in the authorized mixed mode also discover public GitHub candidates using minimal queries. Merge/dedupe evidence without overwriting snapshot provenance or assigning curator acceptance.
6. Save the current state and offline report with comparisons, avoid/defer reasons, reading paths, source/freshness badges, ingestion status, limitations and next decision. Resume interrupted work from the last valid state; preserve finalized run history.

Progress is `Intake -> Scan -> Context Review -> Matching -> Report`, with question number, last saved and next action. Progress is not confidence. No hosted decision board or Markdown export is required for plugin V1; the former memo/Integration Blueprint terminology does not authorize implementation.

## Active Privacy And Side-Effect Boundaries

| Surface | Allowed data/action | Excluded or gated |
| --- | --- | --- |
| Scanner | Read allowlisted local project scope; emit sanitized facts and evidence references | No secrets, credential files, dumps, production logs, customer exports, dependency/build folders, project subprocesses, dependency installation, network or path/junction escape |
| Codex/model | Sanitized structures and user-entered chat; distinguish facts from inference | No agent bypass to raw source. Text already typed into chat cannot be made retroactively untransmitted; redact secret-like answers before persistence and MCP use |
| Plugin artifacts | Write only `docs/myai-stackguide/` in the selected project; state, offline HTML and finalized run snapshots | No source changes, raw-source storage, raw conversations, secrets or MCP credentials; atomicity and concurrency must be tested |
| GitHub discovery | Read public repository evidence through the bounded MCP query contract | No GitHub writes or private-project acquisition. Initial plan budget: 3-5 sanitized queries and at most 20 normalized candidates/run |
| Candidate backend | Append public candidate metadata after gates, auth and explicit consent or bounded standing policy | `candidate_batch_upsert` is an external write, not read-only. No full Brief, answers, private content, project identifiers, raw excerpts or absolute local paths; no private-data contribution exception |

MCP tools are `catalog_delta_get`, `github_discover`, `candidate_batch_upsert` and `candidate_status_get`. CP-03 owns their typed input/output/errors, limits and annotations; CP-02 owns auth/consent/credential/retention decisions. Declining auth or transmission preserves a visible catalog-only path. Failed candidate upload is visible but does not block delivery of the local report. Disclosure of permitted local scan data to the model is a separate boundary from reading it locally; a scan approval does not authorize raw-source transmission.

Snapshot metadata, live GitHub evidence, machine inference, recommendation roles and curator decisions must remain distinguishable. Policy wording is a requirement, not proof of technical enforcement.

## Active Catalog And Quality Baseline

The current source is `data/catalog_manifest.json`, snapshot 2026-08-12: 1,142 repositories and 77 categories. These are snapshot counts, not current GitHub checks or a count of primary-eligible solutions. Preserve the manifest and template. CP-03 defines advisory contracts and explicit unknowns; CP-06 adapts the catalog without mapping legacy scores to fit or automatically promoting candidates.

The old 1,000-repository, 60-90-category and 100-200 enriched-pool targets are historical planning context, not additional plugin release gates. One evidence-qualified seed is sufficient for the first local semantic case; broader quality/coverage still needs CP-04/15 evidence.

Desired business outcome: reduce research effort and improve adoption decisions. Primary product metric: share of target-user Decision Reports judged useful for the next decision. Supporting indicators: time from plugin intake to first Brief/report, primary evidence completeness, shortlist relevance, avoid/defer usefulness and advisory coverage. Counter-metrics: incorrect recommendations, stale evidence, correction rate and privacy violations. Targets, telemetry and measured gains are not invented here; CP-04 owns operational evaluation and human calibration.

Release acceptance follows CP-11 (local semantic case), CP-14 (authorized live integration), CP-15 (privacy/auth/evals/browser and owner review) and CP-16 (package/rollback/publication gate). Existing rubric thresholds remain in [EVALS.md](../EVALS.md) and the CP plan: at least 16/20, no critical dimension below 1, zero critical failures, and evidence for every primary recommendation. CP-04 must calibrate them; no quality pass is claimed.

## Legacy Requirement Disposition

| Historical requirement | Active successor | Decision |
| --- | --- | --- |
| FR1 hosted interface | R01, R02, R10 | Replace hosted onboarding and account settings with plugin intake/local artifacts; hosted app deferred |
| FR2 GitHub connection | R03, R04, R06, R09 | Local project selection replaces OAuth acquisition; public GitHub retrieval stays read-only; own-backend writes have separate auth |
| FR3 permission review | R03, R04, R09 | Retain explicit scan/transmission disclosure and consent/refusal; no implicit upload |
| FR4 scanner | R03, R04 | Retain allowlists/exclusions/no execution; add bounded modes and escape protection |
| FR5 Brief | R05, R10 | Retain plain-language facts/inferences/corrections; add versions and invalidation |
| FR6 post-scan interview | R02, R05 | Replace fixed post-scan ordering with adaptive intake, persistence and resume |
| FR7 catalog | R07, R08, R11, R14 | Preserve v5; define advisory eligibility separately; old quantity targets do not prove fit |
| FR8 matching | R06, R07, R14 | Retain context, role and caveat goals; add mixed lanes, strict unknowns and explicit no-match |
| FR9 comparison | R07, R10, R13 | Retain decision-relevant trade-offs in offline report; old 2-5 workbench limit is not a new UI requirement |
| FR10 avoid/defer | R07, R13, R14 | Retain reasons and conditions for revisiting |
| FR11 reading path | R07, R13 | Retain inspection guidance, without implementation commands |
| FR12 memo/boards/export | R10, R13 | Replace hosted boards/Markdown export with local state, HTML Decision Report and immutable runs |
| FR13 freshness | R06, R07, R11, R14 | Replace shortlist-only live checking with bounded discovery; preserve snapshot/live distinction |
| FR14 curator queue | R08, R09 | Retain auditable curator-only acceptance; dedicated queue UI deferred; candidate overlay is not curator approval |
| FR15 evals | R12 | Retain persona/negative/regression goals; CP-04/15 own corpus and human usefulness acceptance |

| Historical cross-cutting section | Active disposition |
| --- | --- |
| Product definition, problem, ICP, JTBD and goals | Retain decision-support intent/users; replace mandatory GitHub connection with local project or idea |
| Scope and core journey | Replace with active R01-R14/journey above; standalone CLI, archive/doc upload, SDK/widget, hosted boards and general catalog API remain deferred |
| Data requirements | Carry baseline/advisory/provenance intent into CP-03/06; preserve current source IDs/unknowns; do not treat historical field lists as accepted schemas |
| Privacy/security and UX | Use active boundary table, including local writes and restricted public overlay; historical private-contribution and raw-storage exceptions are superseded |
| Success metrics and beta criteria | Use plugin intake/Brief/report timing, useful decisions and CP-11/14/15/16 evidence; no hosted release checklist |
| Non-functional requirements | Retain observable progress, bounded deterministic scanning, graceful failure and versioned evidence. Pinned replay does not promise identical model text |
| Assumptions/open questions/source notes | Resolve entrypoint/scope through this PRD; route runtime/OS/backend/auth/consent/retention/budgets/replay choices to CP-02, schemas to CP-03, calibration to CP-04 |

## Historical Hosted-First PRD — Not Active Acceptance

Everything below is the preserved earlier PRD, including its original FR IDs, present-tense requirements, assumptions and source notes. None is an additional plugin requirement or authorization. The mappings above are exhaustive for its functional and cross-cutting sections; consult the active PRD and CP tasks when preparing new work.

<details>
<summary>Preserved historical PRD</summary>


## Product Definition

myAI-StackGuide is a context-aware open-source adoption advisor.

It helps users connect a GitHub repository, safely scan project context in read-only mode, understand what kind of product they have, and receive grounded open-source repository recommendations from a curated catalog of 1,000 repositories.

The product does not write code, install dependencies, create pull requests, run migrations, or implement user projects. It produces advisory artifacts: project context briefs, repository shortlists, compare views, avoid/defer guidance, reading paths, and decision memos.

## Problem

Users often need open-source recommendations before making product and technical decisions, but they usually face three problems:

1. They do not know what to search for.
2. They cannot describe their product's technical context accurately.
3. Existing tools help inspect a known repository or call GitHub APIs, but they do not turn a user's product context into a clear recommendation path.

This is especially acute for founders, product managers, internal operators, and non-technical owners who understand the business problem but cannot name the right categories, libraries, platforms, or trade-offs.

## Product Goal

V1 should let a user connect a GitHub repository in read-only mode and receive a context-aware open-source adoption memo that answers:

- What kind of product is this?
- What stack, product surface, and domain signals are visible?
- Which repository categories are relevant?
- Which open-source repositories should be inspected first?
- Which repositories or categories should be avoided or deferred?
- What should the user compare before deciding?
- What should be read first in the recommended repositories?
- What caveats and missing context should be checked manually?

## Target Users

### Primary ICP: Non-Technical Founder Or Product Owner

Needs to understand what open-source tools may help their product but cannot fully explain the technical stack.

Success means receiving a plain-language recommendation memo they can discuss with an engineer, advisor, or team.

### Secondary ICP: Product Manager

Needs a structured decision memo for a product workflow, support system, RAG feature, analytics stack, automation layer, or internal tool.

Success means comparing options and deciding what to research next.

### Secondary ICP: Engineer Or Technical Lead

Needs faster landscape triage grounded in an existing repository.

Success means receiving a shortlist, caveats, and reading path that reduce research time.

### Secondary ICP: Internal Operator

Needs help identifying open-source options for support, CRM, analytics, finance, workflow, or back-office operations.

Success means seeing categories and tools matched to the actual product/workflow context.

## Jobs To Be Done

1. When I connect my product repository, help me understand what kind of product and stack I actually have.
2. When I describe my goal, combine that goal with project evidence before recommending repositories.
3. When the open-source landscape is broad, narrow it to a category path and shortlist.
4. When a popular project looks attractive, tell me whether it fits my current context.
5. When I need to explain options to a team, produce a decision memo with caveats and next decisions.
6. When metadata is stale or incomplete, show the confidence level and what must be verified.

## In Scope For V1

- Hosted web application.
- GitHub read-only repository connection.
- Repository selection after connection.
- Permission and privacy disclosure before scanning.
- Allowlist-based project scanner.
- Secret and sensitive file exclusions.
- Project Context Brief generation.
- Short user interview after scan.
- Curated catalog with 1,000 repositories.
- 60 to 90 product categories.
- Repository card baseline metadata for every catalog entry.
- Full advisory metadata for high-confidence entries.
- Context-aware repository shortlist.
- Avoid/defer recommendations.
- Compare view.
- Reading path.
- Evidence and freshness panel.
- Decision memo export.
- Saved decision board.
- Internal curator review queue.
- Recommendation quality evals.

## Out Of Scope For V1

- Writing or editing user code.
- Installing packages or repositories.
- Creating branches, commits, or pull requests.
- Running migrations or deployment commands.
- Autonomous implementation agents.
- Full security scanning.
- Legal, license, compliance, procurement, or vendor approval.
- Local CLI scanner.
- Embeddable SDK/widget.
- Public myAI-StackGuide MCP server.
- Multi-tenant enterprise admin controls beyond basic account/team separation.
- Exhaustive GitHub-wide search.
- Claims that a repository is production-ready without hands-on validation.

## Core User Journey

1. User opens the hosted web app.
2. User signs in and connects GitHub with read-only permissions.
3. User selects one repository to analyze.
4. Product shows scan scope, ignored files, retention mode, and advisory-only boundary.
5. User approves read-only scan.
6. Scanner builds a sanitized project summary.
7. myAI-StackGuide generates a Project Context Brief.
8. User answers a short goal/stage/constraint interview.
9. myAI-StackGuide maps the project to category paths and task archetypes.
10. myAI-StackGuide recommends repositories from the curated catalog.
11. User opens compare view and avoid/defer guidance.
12. User exports or saves a decision memo.

## Functional Requirements

### FR1: Hosted Web App

The product must provide a hosted web interface for onboarding, GitHub connection, repository selection, scan review, recommendation review, compare views, and decision boards.

Acceptance criteria:

- User can start without local setup.
- User can connect GitHub from the hosted app.
- User can select a repository after connection.
- User can disconnect GitHub access from account settings.

### FR2: GitHub Read-Only Connection

The product must use least-privilege GitHub access.

Acceptance criteria:

- The app requests read-only repository access only.
- The permission screen explains what the app can and cannot read.
- The product does not request write access for V1 recommendation flows.
- The product records permission mode in the scan metadata.

### FR3: Scan Permission Review

Before scanning, the product must show a clear permission and privacy screen.

Acceptance criteria:

- User sees what sources will be scanned.
- User sees what sources will be excluded.
- User sees whether raw files, summaries, or decision boards are stored.
- User must approve before scan starts.

### FR4: Read-Only Project Scanner

The scanner must collect project context without modifying the repository.

Acceptance criteria:

- Scanner reads allowlisted file types and metadata.
- Scanner ignores excluded paths and sensitive file patterns.
- Scanner does not execute project code.
- Scanner does not install dependencies.
- Scanner produces a scan report with included and excluded source groups.

### FR5: Project Context Brief

The product must generate a Project Context Brief from scan output.

Acceptance criteria:

- Brief includes product type, target users when inferable, project stage, stack, product surface, domain entities, integrations, detected capabilities, possible gaps, relevant archetypes, category paths, confidence, and caveats.
- Brief separates observed facts from inferences.
- Brief is understandable by a non-technical user.
- User can correct or annotate the brief before recommendations are finalized.

### FR6: User Interview

The guide must ask only a short set of clarifying questions after scan.

Acceptance criteria:

- Interview asks about goal, stage, constraints, and recommendation mode.
- Interview avoids long questionnaires.
- If scan confidence is high, the guide can proceed with explicit assumptions.
- User answers are stored with the decision board if saved.

### FR7: Curated Repository Catalog

V1 must include a curated catalog of 1,000 repositories.

Acceptance criteria:

- Catalog includes 1,000 unique repositories.
- Catalog covers 60 to 90 categories.
- Every repository has baseline metadata.
- High-confidence repositories have advisory fields including `best_for`, `avoid_if`, `adoption_mode`, `project_stage`, `complexity`, `integration_surface`, `trust_level`, `verification_status`, and `last_verified_at`.
- Scores are presented as triage signals, not objective quality ratings.

### FR8: Context-Aware Matching

The guide must match project context to repository categories and candidates.

Acceptance criteria:

- Recommendation uses Project Context Brief, user interview, category paths, stack recipes, repository cards, and policy constraints.
- Output groups repositories by role: primary candidate, supporting tool, reference-only, compare-against, and avoid-for-now.
- Output explains why each recommendation fits the user's project context.
- Output includes missing-context caveats when confidence is low.

### FR9: Compare View

The product must support comparison of repository candidates.

Acceptance criteria:

- User can compare two to five repositories or categories.
- Compare dimensions include fit, adoption mode, maturity, maintenance, docs, license, deployment model, integration surface, complexity, trust level, and caveats.
- Compare view explains trade-offs instead of only ranking repositories.

### FR10: Avoid/Defer Guidance

The guide must explicitly identify mismatched or premature options.

Acceptance criteria:

- Recommendation includes avoid/defer items when relevant.
- Avoid/defer entries include reason and trigger condition for revisiting.
- Popular repositories can be deprioritized when they do not fit the context.

### FR11: Reading Path

The product must tell users what to inspect first.

Acceptance criteria:

- Reading path includes ordered repository inspection steps.
- Reading path can include README, docs, examples, deployment guide, releases, issues, license, and alternatives.
- Reading path is advisory and does not include implementation commands.

### FR12: Decision Memo

The product must generate an exportable decision memo.

Acceptance criteria:

- Memo includes product understanding, detected constraints, category path, shortlist, avoid/defer, compare view, reading path, caveats, evidence, and next decision.
- Memo can be saved to a decision board.
- Memo can be exported as Markdown.

### FR13: Evidence And Freshness

Recommendations must expose evidence and freshness.

Acceptance criteria:

- Repository cards show source type, snapshot date, last verified date, trust level, and verification status.
- Current GitHub metadata is refreshed on demand for shortlist candidates where API access permits.
- Stale or low-confidence metadata is visible in the recommendation.

### FR14: Curator Review Queue

The product must support internal quality review for catalog and recommendation issues.

Acceptance criteria:

- Curators can see metadata gaps, low-confidence cards, duplicate candidates, category gaps, and failed recommendation cases.
- Curators can mark repository cards for enrichment.
- Curator changes are auditable.

### FR15: Recommendation Evals

The product must include evaluation scenarios before V1 beta.

Acceptance criteria:

- Evals cover non-technical founder, product manager, engineer, operator, low-context, private-repo, and sensitive-file scenarios.
- Evals check task interpretation, category path, shortlist relevance, avoid/defer quality, caveats, and no-code boundary.
- Recommendation changes are not promoted without passing core eval scenarios.

## Data Requirements

### Catalog Size

V1 requires 1,000 repositories.

### Category Coverage

V1 requires 60 to 90 categories across:

- AI and agentic engineering.
- Developer tooling.
- RAG, retrieval, memory, and knowledge graphs.
- MCP and integrations.
- Evals, observability, and prompt ops.
- Security and supply chain.
- Documents, OCR, and parsing.
- Frontend, UI, browser, desktop, and mobile.
- Business operations.
- Sales, CRM, and support.
- Analytics, BI, and reporting.
- Product management, feedback, and roadmap.
- Marketing and growth.
- Finance, legal, and operations.
- Research, learning, and reference projects.

### Baseline Repository Card Fields

Every V1 repository must have:

- `full_name`
- `url`
- `description`
- `primary_category`
- `secondary_categories`
- `stars`
- `forks`
- `license`
- `language`
- `last_pushed_at`
- `source_type`
- `snapshot_date`
- `trust_level`
- `verification_status`

### Advisory Repository Card Fields

High-confidence repositories should also have:

- `primary_use_case`
- `secondary_use_cases`
- `task_archetypes`
- `best_for`
- `avoid_if`
- `adoption_mode`
- `project_stage`
- `complexity`
- `maturity_signal`
- `maintenance_signal`
- `docs_signal`
- `license_signal`
- `security_signal`
- `integration_surface`
- `deployment_model`
- `data_sensitivity_fit`
- `pairs_well_with`
- `compare_against`
- `reference_value`
- `known_caveats`
- `last_verified_at`

## Privacy And Security Requirements

- Default access must be read-only.
- V1 must not request write access to GitHub repositories.
- Scanner must not execute user project code in hosted mode.
- Scanner must not install dependencies.
- Scanner must ignore secrets, credentials, tokens, private keys, customer exports, database dumps, production logs, and generated dependency/build directories.
- Product must show what is scanned and what is excluded before scan starts.
- Product must support deletion of saved project context and decision boards.
- Product must separate raw scan data, sanitized summaries, and saved decision memos.
- Product must not store secrets in prompts, fixtures, logs, docs, or examples.
- Private repository data must not be used to enrich the public catalog unless the user explicitly contributes it.

## UX Requirements

- The first screen must ask the user to connect GitHub or explain the product goal.
- The GitHub permission step must be understandable to non-technical users.
- The Project Context Brief must be readable before recommendations.
- Users must be able to correct product understanding.
- Recommendations must be grouped by role, not dumped as a flat list.
- The product must display why a repository was included and why some options were avoided.
- The final output must end with a next decision, not implementation steps.

## Success Metrics

V1 should be evaluated with product and quality metrics:

- Time from GitHub connection to first Project Context Brief.
- Time from repository selection to first recommendation memo.
- Percentage of recommendation memos rated useful by target users.
- Percentage of eval scenarios passing core criteria.
- Percentage of recommendations with visible evidence and freshness metadata.
- Percentage of high-confidence repository cards with full advisory metadata.
- Rate of user corrections to Project Context Brief.
- Rate of avoid/defer items judged useful.

## Acceptance Criteria For V1 Beta

V1 beta is ready when:

- Hosted app supports GitHub read-only connection.
- Scanner can produce Project Context Briefs for representative repositories.
- Catalog contains 1,000 unique repositories.
- At least the highest-value recommendation pool has full advisory metadata.
- Recommendation flow returns category path, shortlist, compare view, avoid/defer, reading path, caveats, evidence, and next decision.
- Decision memo export works.
- Sensitive-file exclusions are tested.
- Core recommendation evals pass.
- Product copy clearly states advisory-only boundaries.
- RUNLOG or release notes record known data freshness and confidence limitations.

## Non-Functional Requirements

- Recommendation flow should remain responsive enough for interactive use; long scans should show progress.
- Scanner behavior should be deterministic enough to debug and audit.
- Recommendation output should be reproducible from stored scan summary, user answers, catalog snapshot, and model/config version.
- Catalog snapshots should record source artifacts and snapshot date.
- Failed scans should degrade gracefully and ask the user for a manual description instead of blocking all recommendations.

## Assumptions

- V1 uses GitHub as the first repository provider.
- V1 prioritizes repository recommendations over code implementation.
- V1 can start with a curated high-confidence subset inside the 1,000-repository catalog.
- GitHub metadata is a triage signal and must be refreshed or caveated before current claims.
- The product can use AI models for context summarization and recommendation generation, but recommendation quality must be evaluated with scenario tests.

## Open Questions

- Should private repository scan summaries be ephemeral by default, or saved by default after explicit approval?
- What minimum advisory metadata is required before a repository can appear as a primary candidate?
- What are the first 60 to 90 V1 categories?
- Which 100 to 200 repositories should form the high-confidence pool for beta?
- What exact GitHub permission model will be used for private repositories?
- What model and retrieval stack will power recommendation generation?
- What retention and deletion controls are required before private beta?

## Source Notes

- `MYAI_STACKGUIDE_PRODUCT_CONCEPT.md` defines the advisory-only repository selection product, V1 catalog size, feature layers, repository card model, and recommendation output contract.
- `MYAI_STACKGUIDE_CONTEXT_SCANNER.md` defines embedded/project scanning, read-only boundaries, Project Context Brief schema, deployment modes, exclusions, and scanner risks.
- `README.md` distinguishes the current HTML v5 snapshot (2026-08-12, 1,142 repository records, 77 categories, and 1,290 placements) from the legacy Markdown/research boundary (2026-05-23, 314 repositories, 42 categories, and 351 placements).
- Catalog metadata is snapshot evidence and must not be described as live or current without a fresh source-backed check.

</details>
