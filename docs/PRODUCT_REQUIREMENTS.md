# Product Requirements: myAI-StackGuide V1

## Status

Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation records. CP-03 is implemented and verified at contract level: 22 local schemas, the presentation/publication addendum and linked fixtures pass all 46 checks. The bounded CP-04 C8/C9 join passes all 27 checks and both scorer CLI gates; synthetic compatibility is accepted, while quality corpus/baseline/thresholds and human calibration remain open. CP-05 source alignment is implemented and statically verified; fresh-session behavioral acceptance remains pending; CP-06-CP-16 remain planned, with CP-12-CP-14 deferred. Runtime and permissions are unchanged.

This PRD owns active product meaning. [Detailed CP plan](plan/2026-08-30-codex-plugin-v1-implementation-plan.md) owns exact implementation files, owners and gates; [local architecture](../specs/decisions/plugin-v1-architecture.md) owns selected runtime/data-flow decisions. Historical text below remains recoverable and inactive.

## Active Product Definition And Users

myAI-StackGuide helps founders, product owners, engineers and operators build or modernize solutions faster through appropriate open-source integration. It works as a Codex plugin from the user's project, combining a useful context Brief, local catalog retrieval and an actionable Decision Report. The goal is a short path to a working validation slice; actual time saved and integration success remain unmeasured product hypotheses.

## Active Plugin V1 Requirements

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

## Active Journey And Output

User goal -> up to ten relevant questions -> bounded scan/targeted context -> corrected versioned Brief -> local FTS5 search -> constrained evidence pack -> comparison and integration plan -> local state/offline HTML -> coding-agent handoff when implementation is requested. Empty projects and manual context are valid. Do not force questions or exhaustive review when enough information exists for a useful result.

The report identifies a component and role, evidence-backed fit, alternatives, license/version/deployment unknowns, integration surface, affected components, sequence of work, first validation slice, risks and rollback. Commands/examples may be proposed without executing them or claiming verification. A user request to implement carries its own scope and authority; do not refuse all coding by product policy or repeat approvals already granted. A recommendation alone authorizes no automatic installation or code change.

## Active Session Workspace And Localization

The owner selected a desktop/laptop-only product, with no mobile adaptation. It uses one persistent session HTML with eight views: Goal, Questions, Scan, Context, Options, Compare, Integration and History. The [detailed workspace design](plan/plugin-v1-session-workspace-design.md) defines the decision, subsections, sources and incomplete/error states for each. It deepens existing R02-R14 behavior instead of introducing separate pages/services. The saved report must support both plain-language product decisions and a technical integration handoff.

R15 requires a visible RU-EN switch on every view, translated interface/status/error/accessibility text and paired narrative presentation tied to the same facts, constraints, roles, evidence and revision. Original user/source language and technical literals are preserved; missing translations are explicitly partial. Both core language flows are required for local release. Switching is local presentation only: no scan, retrieval, model/API call, private-data transfer or implicit state mutation. Full details, fallback, storage budgets and CP ownership are in the design document. The detailed visual baseline is owner-approved; working localization and rendered usefulness still require implementation verification.

The HTML must exist from the first committed session state, including unanswered questions and unavailable results, and update at the same path after each saved answer or completed phase. Codex owns user input and state changes; the HTML presents saved progress, evidence and copyable next actions. A publication failure must preserve a saved answer, report the saved-versus-published revision to Codex and allow a render-only retry. An already-open file is a snapshot to reload, not a live monitor. The shared writer/renderer contract and CP-10 A-D checkpoints are specified in the approved design sequence.

## Active Privacy And Side-Effect Boundaries

R04 no longer promises scanner-only source isolation. Relevant project reads/excerpts may inform Codex under existing user/host permissions, with sensitive exclusions and bounded scope. The scanner remains read-only, non-executing and local; it does not run project tests/builds or install dependencies. Do not bypass failed safety checks through another tool.

Persist minimized findings, sanitized answers and safe references under `docs/myai-stackguide/`, never full source, raw chat, secrets or customer exports. The public catalog/index contains no user context. Codex data handling remains the host's; local scripts/artifacts do not mean an offline model or a no-transmission guarantee. No new service, credential, upload or telemetry is introduced. Public/remote/private access and destructive/costly actions retain their actual approval boundaries. See [permissions](../specs/decisions/plugin-v1-permissions.md).

## Active Catalog And Quality Baseline

The CAT-10 canonical source snapshot is frozen at the exact 2026-09-01 manifest hash with 2,500 repositories, 126 taxonomy nodes and 2,630 direct placements. CAT-08 applied the frozen CAT-07A candidate; CAT-09 passed exhaustive source/output parity plus representative offline Chrome startup/search/filter/navigation thresholds for the same projection. The [CAT-10 report](reports/catalog-final-freeze-2026-09-01.json) pins the source/schema/taxonomy/field contract, output hashes and CP-06 migration rules. These counts are snapshot inventory, not live GitHub facts. CP-06 persists available metadata and provenance before index build; browser-only observations are not reproducible source facts. Missing fields stay unknown. Index one normalized canonical repository card, with concise category/use-case signals, not repeated category prose or arbitrary JSON chunks.

SQLite FTS5/BM25 is selected. The local `catalog_only` source uses `sqlite_fts5`; no vectors/embedding models/database service required. Retrieve at most 60 candidates across query variants, deliver at most 12 cards and 48 KiB UTF-8 evidence including provenance; these uncalibrated ceilings are not token or quality promises. CP-03 allocates Brief and retrieval budgets; CP-04 validates RU/EN/aliases, retrieval relevance and integration usefulness. Missing index/FTS5 is an explicit failure, not silent full-catalog context loading.

Dates distinguish creation, push, verified commit/release, observation and snapshot/index build. No blanket snapshot expiry rejects recommendations. Activity helps triage; it does not prove a repository works, fits or is secure. Show dated facts, gaps and the next verification step. A baseline-valid sparse card can be retrieved without qualifying for unconditional primary adoption. Curator acceptance is separate from evidence and role assignment.

Local release requires CP-11 intended-route evidence, CP-15 independent relevance/privacy/UI/usefulness acceptance and CP-16 installed package/index compatibility/rollback. Remote CP-12-14, auth, shared ledger and scheduler are deferred, not release prerequisites. Evals retain the 16/20 rubric plus zero critical failures, with revised authorized-context/integration behavior and independently measured retrieval metrics. No runtime, recommendation-quality or release success is claimed by this PRD.

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
| FR8 matching | R06, R07, R14 | Retain context, role and caveat goals; add local SQLite FTS5, bounded evidence, explicit unknowns and useful conditional guidance; mixed retrieval deferred |
| FR9 comparison | R07, R10, R13 | Retain decision-relevant trade-offs in offline report; old 2-5 workbench limit is not a new UI requirement |
| FR10 avoid/defer | R07, R13, R14 | Retain reasons and conditions for revisiting |
| FR11 reading path | R07, R13 | Expand into a sourced integration plan, proposed validation commands and coding-agent handoff; no execution implied |
| FR12 memo/boards/export | R10, R13 | Replace hosted boards/Markdown export with local state, HTML Decision Report and immutable runs |
| FR13 freshness | R06, R07, R11, R14 | Use persisted creation/push/verified commit/release/observation facts; no blanket snapshot TTL; live extension deferred |
| FR14 curator queue | R08, R09 | Retain auditable curator-only acceptance; dedicated queue UI deferred; candidate overlay is not curator approval |
| FR15 evals | R12 | Retain persona/negative/regression goals; CP-04/15 own corpus and human usefulness acceptance |

| Historical cross-cutting section | Active disposition |
| --- | --- |
| Product definition, problem, ICP, JTBD and goals | Retain decision-support intent/users; replace mandatory GitHub connection with local project or idea |
| Scope and core journey | Replace with active R01-R14/journey above; standalone CLI, archive/doc upload, SDK/widget, hosted boards and general catalog API remain deferred |
| Data requirements | Carry baseline/advisory/provenance intent into CP-03/06; preserve current source IDs/unknowns; do not treat historical field lists as accepted schemas |
| Privacy/security and UX | Use active revised R04/R13 boundaries, local minimized writes and deferred public overlay; historical private-contribution and raw-storage exceptions are superseded |
| Success metrics and beta criteria | Use time to useful integration guidance, retrieval quality and local CP-11/15/16 evidence; CP-14 is extension-only |
| Non-functional requirements | Retain observable progress, bounded deterministic scanning, graceful failure and versioned evidence. Pinned replay does not promise identical model text |
| Assumptions/open questions/source notes | Resolve entrypoint/scope through this PRD; local runtime/FTS5/context/activity design is selected in CP-02; local schemas CP-03, calibration CP-04, remote choices deferred CP-12 |

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
- `README.md` distinguishes the current CAT-08 canonical HTML v5.1 snapshot (2026-09-01, 2,500 repository records, 126 taxonomy nodes and 2,630 direct placements), the frozen CAT-07A input, and the legacy Markdown/research boundary (2026-05-23, 314 repositories, 42 categories, and 351 placements).
- Catalog metadata is snapshot evidence and must not be described as live or current without a fresh source-backed check.

</details>
