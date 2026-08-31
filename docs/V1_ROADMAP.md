# V1 Roadmap: myAI-StackGuide

## Roadmap Goal

Deliver a local Codex plugin that turns a user goal and project context into a useful OSS integration or modernization plan. Owner revision 2026-08-31 selects SQLite FTS5 and removes the strict host-isolation and snapshot-age blockers. Runtime remains unimplemented. [PRD](PRODUCT_REQUIREMENTS.md#active-plugin-v1-requirements) defines meaning; [detailed plan](plan/2026-08-30-codex-plugin-v1-implementation-plan.md) defines the dependency graph.

## Active Plugin V1 Milestones

| Phase | Tasks | Exit evidence / status |
| --- | --- | --- |
| P0: direction and design | CP-01, CP-02 | Documentation implemented, amended to FTS5/relevant context/activity/integration; no runtime proof |
| P1: local contracts and readiness | CP-03, CP-04, CP-05 | CP-03 contracts accepted (46/46); bounded C8/C9 compatibility and scorer verified (27/27 plus CLI); CP-05 instructions applied/static-verified; CP-04 quality calibration and CP-05 fresh-session behavior remain open |
| P2: local useful vertical slice | CP-06-CP-11 | Persist public metadata/cards, build index, intake/state, bounded context, FTS5/evidence pack and integration report; actual 1/1 route then targeted negatives/scaling; planned |
| P3: optional remote extension | CP-12-CP-14 | Deferred pending a separate service/auth/consent/architecture decision; no local P4/P5 dependency |
| P4: independent local acceptance | CP-15 | Depends on CP-04, CP-10, CP-11; held-out retrieval, privacy, rendered UI and integration usefulness; planned |
| P5: local package and release decision | CP-16 | Depends on CP-01, CP-05, CP-06, CP-15; actual package/index/runtime/fresh-session/rollback evidence; publication separately authorized |

Execution path is P0 -> P1 -> P2 -> P4 -> P5. Phase numbering retains historical IDs; P3 is a side extension, not a skipped mandatory step. Later inclusion of remote features requires their own supplemental P4/P5 evidence without rewriting the local release's historical result.

## Active Acceptance And Scope Control

- The detailed desktop/laptop-only eight-view design and R15 RU-EN direction are owner-approved. CP-03/04/05 prepare contracts/evals/behavior; CP-07 owns the shared commit/publication boundary; CP-10 A-D builds shell/localization, views 1-4, views 5-7 and History/recovery while CP-08/09 supply context/retrieval. CP-11 joins the full bilingual lifecycle, CP-15 accepts the working artifact and CP-16 packages it. [Approved workspace sequence](plan/plugin-v1-session-workspace-design.md#approved-implementation-sequence) owns depth, language semantics and fallback. The HTML starts with the session, not only with final recommendations. The dependency graph and remote deferral stay unchanged; mobile is excluded and runtime remains unimplemented.
- FTS5/BM25 is the baseline, not an option awaiting another choice. No mandatory vectors, embeddings, service, provider key or Cloudflare work.
- CP-03 owns complete local contracts including retrieval and integration handoff. Remote C4/C7 move to CP-12; they do not prevent local CP-03 completion.
- CP-06 must persist available activity metadata and report coverage, preserve unknowns/canonical identity, and build a public-only versioned read-only index. Do not wait for exhaustive enrichment of every repository before a useful slice.
- CP-09 must keep candidate/model-input budgets fixed and report retrieval failure separately from no-match. CP-04/11/15 measure multilingual relevance and 2,000/10,000 synthetic scaling without treating synthetic rows as real inventory.
- Relevant authorized source context is allowed; secrets, needless persistence, execution during scanning and unauthorized external disclosure remain prohibited. The report carries an actionable integration plan; executing it requires a user implementation request.
- CP-15 reviews the local product; CP-16 verifies clean install, FTS5/index compatibility, read-only search, state preservation and rollback. Neither waits for live auth/ledger/scheduler.
- No new runtime, source refresh, agent-definition edit, model call, installation, Git action or publication is authorized by this planning revision. Estimates in the detailed plan are preliminary and must be rechecked per assigned slice.

## Historical Milestone Mapping

| Earlier milestone | Active successor | Disposition |
| --- | --- | --- |
| Milestone 0: product baseline | CP-01, CP-02 | Replace hosted scope with accepted plugin direction |
| Milestone 1: catalog foundation | CP-03, CP-06 | Preserve current v5; formalize contracts without imposing old expansion quotas |
| Milestone 2: advisory metadata/curation | CP-03, CP-06, CP-12 | Retain evidence/eligibility, separate public candidate overlay from curator acceptance |
| Milestone 3: hosted shell/GitHub connection | CP-02, CP-07, CP-16 | Superseded by local plugin intake/package; backend auth and hosted app deferred |
| Milestone 4: scanner | CP-03, CP-08 | Retain read-only purpose; add local bounded modes and strict exclusions |
| Milestone 5: Brief/interview | CP-03, CP-07, CP-08, CP-11 | Adaptive intake, correction/resume/versioning replace post-scan-only ordering |
| Milestone 6: recommendations | CP-09, CP-13 | Local SQLite FTS5 and bounded evidence first; CP-13 is an optional later extension |
| Milestone 7: workbench/memo | CP-10, CP-11 | Offline HTML/state/run history replace hosted boards and required Markdown export |
| Milestone 8: freshness | CP-03, CP-06, CP-09, CP-15 | Persisted activity/observation and provenance; no blanket snapshot TTL; CP-12-14 live discovery deferred |
| Milestone 9: beta quality | CP-04, CP-15, CP-16 | Separate eval design, observed quality and authorized public alpha release |

The old post-V1 list, dependency order, beta checklist, rollback cuts and immediate slice below are historical too. Local plugin scripts remain active work. The four-tool remote MCP is preserved as a future requirement and deferred by the owner's current local-project direction, not selected as a prerequisite by the earlier CLI/MCP list.

## Historical Hosted-First Roadmap — Not An Execution Queue

Everything below retains the earlier roadmap verbatim from its original journey sentence onward. Old statuses, rollout order and checkbox lists do not represent current progress or acceptance.

<details>
<summary>Preserved historical roadmap</summary>

V1 must let a user connect a repository, approve a read-only scan, receive a Project Context Brief, and get a context-aware open-source recommendation memo from a curated catalog of 1,000 repositories.

## Roadmap Principles

- Build the decision workflow before expanding into broad integrations.
- Keep V1 advisory-only.
- Use GitHub read-only access only.
- Treat project scanning as context acquisition, not implementation.
- Make privacy, scan scope, and retention visible before scanning.
- Promote repositories into high-confidence recommendations only after metadata enrichment and evals.
- Prefer a smaller reliable user journey over a broad but shallow platform.

## V1 Milestones

### Milestone 0: Product Baseline

Purpose:

Turn the current concept documents into implementation-ready product scope.

Deliverables:

- `PRODUCT_REQUIREMENTS.md`
- `V1_ROADMAP.md`
- Confirmed V1 entrypoint: Hosted Web App + GitHub read-only connection.
- Confirmed no-code advisory boundary.
- Confirmed V1 catalog target: 1,000 repositories.

Exit criteria:

- PRD and roadmap exist.
- Product scope, non-goals, data requirements, privacy requirements, and acceptance criteria are staged.
- Open questions are explicit.

Status:

- In progress.

### Milestone 1: Catalog Foundation For 1,000 Repositories

Purpose:

Prepare the data foundation required for useful recommendations.

Deliverables:

- Final V1 taxonomy with 60 to 90 categories.
- 1,000 unique repository candidates.
- Deduplication rules.
- Source provenance for every repository.
- Baseline repository card schema.
- High-confidence advisory card schema.
- Data validation script for required fields and duplicates.
- Coverage map showing category counts and confidence gaps.

Exit criteria:

- Catalog has 1,000 unique repositories.
- Every repository has baseline metadata.
- Category coverage is visible.
- Low-confidence source groups are marked.
- Validation catches missing required fields.

Risks:

- Business/product metadata may remain lower-confidence without API enrichment.
- Category expansion can create shallow coverage if advisory fields are not added.

### Milestone 2: Advisory Metadata And Curator Workflow

Purpose:

Make recommendations explainable instead of search-like.

Deliverables:

- Advisory fields for high-value repositories:
  - `best_for`
  - `avoid_if`
  - `adoption_mode`
  - `project_stage`
  - `complexity`
  - `integration_surface`
  - `pairs_well_with`
  - `compare_against`
  - `known_caveats`
  - `trust_level`
  - `verification_status`
- Internal curator review queue specification.
- Promotion rules for high-confidence primary candidates.
- Initial high-confidence pool of 100 to 200 repositories.

Exit criteria:

- The product can explain why a repository fits or does not fit.
- High-confidence pool is distinguishable from general discovery entries.
- Curators can identify metadata gaps and category gaps.

Risks:

- Manual curation can become a bottleneck.
- Inconsistent advisory fields can reduce recommendation quality.

### Milestone 3: Hosted App Shell And GitHub Read-Only Connection

Purpose:

Create the first usable hosted product entrypoint.

Deliverables:

- Hosted web app shell.
- User account/session model.
- GitHub read-only connection flow.
- Repository picker.
- Disconnect/revoke access flow.
- Permission explanation screen.
- Basic audit record for permission mode and selected repository.

Exit criteria:

- User can connect GitHub read-only from the hosted app.
- User can select one repository.
- Product clearly states that V1 does not request write access.
- User can disconnect access.

Risks:

- GitHub permission wording may be too technical for non-technical users.
- Private repository access requires high trust before beta.

### Milestone 4: Read-Only Project Scanner

Purpose:

Safely turn a selected repository into a sanitized project summary.

Deliverables:

- Allowlist-based file inventory.
- Exclusion rules for secrets, credentials, dumps, logs, generated folders, and build outputs.
- Scan report showing included and excluded source groups.
- Stack and dependency detection.
- Product surface detection.
- Domain entity extraction.
- Integration detection.
- Maturity signal extraction from tests, docs, releases, and eval files.

Exit criteria:

- Scanner does not modify the repository.
- Scanner does not execute project code.
- Scanner does not install dependencies.
- Scanner avoids excluded file patterns.
- Scanner produces a structured sanitized summary.

Risks:

- Partial repositories can produce misleading inferences.
- Exclusion rules must be tested against sensitive-file scenarios.

### Milestone 5: Project Context Brief

Purpose:

Create the bridge between project scan and recommendations.

Deliverables:

- Project Context Brief generator.
- Observed facts vs inferred claims separation.
- Confidence fields for product understanding, technical stack, and recommendation readiness.
- User correction/annotation step.
- Short post-scan interview for goal, stage, constraints, and recommendation mode.

Exit criteria:

- Non-technical user can understand the brief.
- Technical reviewer can see evidence and caveats.
- User can correct the brief before recommendation.
- Low-confidence scan produces questions rather than overconfident recommendations.

Risks:

- Poor brief quality will weaken every downstream recommendation.
- Users may skip corrections unless the interface makes them lightweight.

### Milestone 6: Context-Aware Recommendation Engine

Purpose:

Map project context and user intent to repository categories, stack recipes, and shortlists.

Deliverables:

- Task archetype classifier.
- Category path selector.
- Stack recipe selector.
- Candidate retrieval from curated catalog.
- Filtering by stage, complexity, license tolerance, deployment model, and integration surface.
- Role assignment:
  - primary candidate
  - supporting tool
  - reference-only
  - compare-against
  - avoid-for-now
- Caveat and missing-context generation.

Exit criteria:

- Recommendation output includes category path, shortlist, roles, reasons, avoid/defer, compare view, reading path, caveats, evidence, and next decision.
- Recommendations cite catalog metadata and Project Context Brief signals.
- Output does not include implementation commands.

Risks:

- Popular repositories may dominate without fit-first ranking.
- Low-confidence entries may look more authoritative than they are.

### Milestone 7: Compare Workbench And Decision Memo

Purpose:

Turn recommendations into decision artifacts.

Deliverables:

- Compare view for two to five repositories or categories.
- Comparison dimensions:
  - fit
  - adoption mode
  - maturity
  - maintenance
  - docs
  - license
  - deployment
  - integration surface
  - complexity
  - trust level
  - caveats
- Reading path generator.
- Decision memo view.
- Markdown export.
- Saved decision board.

Exit criteria:

- User can compare recommended options.
- User can save a decision board.
- User can export a memo.
- Memo ends with next human decision.

Risks:

- Compare tables can become too dense for non-technical users.
- Decision memos must avoid sounding like procurement approval.

### Milestone 8: Evidence, Freshness, And GitHub Verification

Purpose:

Avoid false authority and stale recommendations.

Deliverables:

- Evidence panel for recommendations.
- Snapshot date display.
- Source type display.
- Trust level and verification status display.
- On-demand current-state check for shortlist repositories.
- Metadata refresh record.
- Staleness warnings.

Exit criteria:

- User can see which facts are snapshot data.
- User can see which repositories were refreshed during the session.
- Stale or low-confidence data is visible.

Risks:

- GitHub API rate limits can affect on-demand verification.
- Users may overvalue stars or recent commits without caveats.

### Milestone 9: Recommendation Evals And Beta Gate

Purpose:

Check recommendation quality before broader use.

Deliverables:

- Eval scenario set for:
  - non-technical founder
  - product manager
  - engineer
  - internal operator
  - low-context repository
  - sensitive-file repository
  - RAG product
  - support workflow product
  - business ops product
- Eval rubric.
- Regression record for recommendation changes.
- Beta readiness checklist.

Exit criteria:

- Core eval scenarios pass.
- Scanner exclusion tests pass.
- Recommendation outputs preserve advisory-only boundary.
- Known gaps are documented.

Risks:

- Subjective recommendation quality requires human review.
- Passing evals does not prove production suitability for all categories.

## Post-V1 Candidates

These are intentionally outside the first product release:

- Uploaded repository archive support.
- Local CLI scanner.
- Embeddable SDK/widget.
- myAI-StackGuide MCP server.
- Enterprise policy profiles.
- Team admin and role-based access controls.
- Watchlists and monthly reports.
- Multi-provider repository connections beyond GitHub.
- Deep repository documentation reader.
- Public catalog API.
- Automated repository ingestion pipeline with curator approval.

## Dependency Order

Recommended sequence:

1. Product baseline.
2. Catalog schema and taxonomy.
3. Repository expansion to 1,000.
4. Advisory metadata for high-confidence pool.
5. Hosted app and GitHub read-only connection.
6. Read-only scanner.
7. Project Context Brief.
8. Recommendation engine.
9. Compare and decision memo.
10. Evidence/freshness verification.
11. Evals and beta gate.

The scanner and recommendation engine depend on catalog schema clarity. The hosted app can be prototyped earlier, but meaningful product quality requires repository cards and evals.

## V1 Beta Readiness Checklist

- [ ] 1,000 repository catalog exists.
- [ ] 60 to 90 categories defined.
- [ ] Baseline repository card fields populated.
- [ ] High-confidence pool enriched.
- [ ] Hosted app supports GitHub read-only connection.
- [ ] Repository picker works.
- [ ] Permission screen explains read-only scan and retention.
- [ ] Scanner excludes sensitive files.
- [ ] Project Context Brief is generated.
- [ ] User can correct brief.
- [ ] Short user interview is implemented.
- [ ] Recommendation memo is generated.
- [ ] Compare view works.
- [ ] Avoid/defer guidance is present.
- [ ] Reading path is present.
- [ ] Evidence and freshness are visible.
- [ ] Decision memo can be exported.
- [ ] Saved decision board works.
- [ ] Core eval scenarios pass.
- [ ] Advisory-only boundary is visible in product copy.

## Rollback And Scope Control

If V1 scope becomes too large, cut in this order:

1. Saved decision boards can become local/session-only.
2. Compare workbench can start as generated static comparison tables.
3. On-demand GitHub verification can start with shortlist-only metadata refresh.
4. Curator review queue can start as a structured CSV/JSON workflow.
5. High-confidence pool can start with 100 repositories while the full catalog still contains 1,000 entries.

Do not cut:

- Read-only GitHub permission boundary.
- Sensitive-file exclusions.
- Project Context Brief.
- Role-based shortlist.
- Avoid/defer guidance.
- Evidence and confidence display.
- Advisory-only no-code boundary.

## Immediate Next Slice

The next implementation planning slice should produce:

- V1 data schema for repository cards.
- V1 category taxonomy.
- Scanner allowlist and exclusion specification.
- Project Context Brief JSON schema.
- Recommendation memo schema.
- Eval scenario file format.

These artifacts should be created before building the hosted application.

</details>
