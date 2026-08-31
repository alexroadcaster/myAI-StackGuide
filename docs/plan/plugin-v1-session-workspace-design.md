# Session Workspace: Detailed Design And RU-EN Plan

Owner revision: 2026-08-31. The detailed eight-view design and RU-EN direction are `owner_accepted`; the owner requested an implementation-plan update against this baseline. Target desktop PCs and laptops only; mobile layouts and mobile acceptance are excluded. Concept approval is complete and is not a repeated prerequisite for implementation. Rendered usefulness, localization and runtime acceptance remain pending. No HTML, localization runtime, schema migration or plugin execution is implemented by this document.

## Product And Technical Findings

The product outcome is a useful OSS integration or modernization decision grounded in a project, followed by a small validation slice when implementation is requested. A larger shortlist is not the outcome. Founders need the business consequence; engineers need integration boundaries, evidence and a first check. Both must be able to read the same artifact without repeating the interview.

The first concepts established navigation and clear states but omitted important existing requirements: category paths, all recommendation roles, avoid/defer with revisit conditions, reading order, source provenance, constraint evidence, affected components, prerequisites, and explicit recovery. Large headings and whitespace gave these decision details too little space. Activity dates alone do not explain technical fit. A generic four-step plan does not give a coding agent sufficient context.

Use three reading levels: (1) decision and next step, (2) supporting product/technical detail, (3) expanded evidence and diagnostics. Increase meaningful structure rather than shrinking text or filling the page with metrics. The analytical artifacts are evidence ledgers, a comparison matrix and a small proposed integration diagram; ordinary HTML tables/lists are the fallback. No chart library, decorative scores, confidence percentages, automatic telemetry or animation is needed.

The CP-03 addendum now supplies the [workspace contract](../../specs/artifact/session-workspace-contract.md), including source mappings, locale presentation and transient publication outcomes. It adds saved questions/scan and sourced audience/workflow/integration details to versioned schemas. Full standards/semantic and bounded C8/C9 compatibility checks pass (46 CP-03 and 27 C8 tests plus scorer CLI). CP-04 quality calibration remains pending. The renderer must consume these fields or explicit unknowns rather than generate facts. A UI proposal does not prove runtime behavior.

## Shared Shell And Interaction Boundary

- One `docs/myai-stackguide/status.html` serves the current session with eight navigable views. These are not eight HTML files, eight runs or separate applications. Regeneration retains the same path.
- `state.json` owns the current committed domain state; finalized `runs/{run_id}.json` remains immutable. There is no second browser database or raw-chat archive.
- Desktop: compact eight-item sidebar; a common header with project label, saved revision, saved timestamp/timezone, explicit snapshot state and persistent `RU | EN` language control. No online dot or fake live progress.
- Main area: modest heading and decision summary, readable subsections, an evidence inspector or expandable details, and one primary next action. Avoid equal-weight dashboard cards. Safe long content scrolls instead of shrinking to illegible text.
- Always distinguish facts, user statements, interpretations, unknowns, proposed actions and actual execution evidence. Amber denotes uncertainty or a required check; green denotes focus/selection, not certified quality.
- Codex chat owns answers, context corrections, scan requests, retrieval changes and implementation authorization. HTML supports navigation, disclosure, language switching, comparison selection and copying a scoped request. A copy action has a visible text-selection fallback; it must not require a network or filesystem bridge.
- Browsing a comparison changes only the view. Persisting a chosen solution or changing a constraint uses the existing Codex/state writer workflow. Editing an answer cannot be disguised as a browser-only preference.
- Generated text, paths and URLs are untrusted data. Escape content; permit only safe link schemes; never execute commands from a displayed plan. Link labels must distinguish external documentation from internal evidence.
- Rendered HTML states what was known at generation. It cannot detect arbitrary later `state.json` edits while opened as a standalone file. The writer/Codex reports publication failures; an old file never claims it has checked the latest state. No polling/fetch, daemon or new service is introduced.
- View state may use a validated fragment such as `#view=compare&lang=en`, with stable public/opaque identifiers only. Never put goals, answers, project paths, source excerpts or secrets into the fragment. Browser Back and invalid-fragment fallback are CP-10 checks.

## Eight Views And Their Detail Levels

### 01 Goal

**Decision:** what improvement is worth making, for whom, and what counts as useful?

1. Outcome brief: current problem, target user/workflow, requested build/replace/compare/learn/evaluate intent, stage and desired change. Modernization is expressed through the existing intent plus goal; do not silently add an unsupported enum.
2. Current versus target behavior: a concise scenario, not invented adoption or revenue metrics. Identify whether statements came from the user, project evidence or interpretation.
3. Acceptance: the first observable success criterion, its current baseline and what has not been measured. A target is not a completed result.
4. Constraints ledger: hard requirements, preferences and unknowns covering stack, deployment, data boundaries, licenses, team capacity and time horizon. Use a source/reference and consequence for each material constraint.
5. Scope and non-goals: affected product surface, what stays unchanged, whether a new service or migration is allowed. Ideas and empty projects remain valid inputs.
6. Session summary: saved phase, completed deliverables and next decision. Resume an active run rather than create a competing run.

**Sources:** C1 intake, C3 Brief/summary, C6 revision. C3 details and the workspace contract now map audience/workflow/constraints; absent source values remain explicitly unknown. **States:** no goal, idea/manual context, active, incomplete, finalized. **Primary action:** copy the next clarification for Codex.

### 02 Questions

**Decision:** which missing answer would change the recommendation?

1. Current question with rationale and its decision consequence; show ordinal and the ten-question ceiling without a fake completion percentage or a fixed compulsory form.
2. Suggested answer shapes as non-input examples, plus free-form reply guidance for Codex.
3. Saved answer ledger with question, sanitized answer, answered/skipped status and correction action. Never display an unsaved answer as saved or store the complete chat.
4. Coverage by topic: goal, deployment, existing stack, license/data limits and integration boundary. This means topic coverage, not proof that all requirements are understood.
5. Early completion: explain why available context is sufficient, or list the remaining assumptions and the smallest useful clarification.
6. Correction impact: identify dependent Brief/retrieval/report invalidation before a changed answer is applied by the writer.

**Sources:** C1 answers/state, C3 corrections, C6 saved revision. **States:** asking, skipped, ready early, ten-question ceiling, cancelled, save failure/conflict. **Primary action:** copy the current question; answers remain in Codex.

### 03 Scan

**Decision:** is the available project evidence sufficient for this decision, and where is the gap?

1. Selected project scope and classification, with the reason and completeness. A reached cap is not proof of a monorepo; incomplete enumeration is never proof of an empty project.
2. Mode and budgets: quick/standard/deep, actual consumption against selected file/byte/time limits, and explicit limit labels. Use recorded values only; unavailable counts are unknown.
3. High-signal findings: manifests, languages, frameworks, storage, product surfaces and integrations, each with safe source references. Do not infer verified runtime architecture from package names alone.
4. Source ledger: relevant safe path/reference, disposition, extracted finding and limitation. Aggregate sensitive/generated/unsafe exclusions; never show sensitive filenames or values discovered during scanning.
5. Coverage gaps: why a file/domain was skipped, how it affects the decision and the next bounded read. Do not imply every source file should be read.
6. Boundary panel: no execution, dependency installation or secret collection; what is persisted and what remains unknown. Optional targeted context is purpose-bound and charged to the existing budgets.

**Sources:** C2 scan report/manifest, C3 summary/selection. **States:** not started, complete within selected scope, partial, cancelled, unavailable, idea/manual context. **Primary action:** copy a targeted follow-up scan request; no HTML scan launcher.

### 04 Context

**Decision:** is the model's understanding of the project good enough to guide a change?

1. Product brief: user/workflow, project stage, goal and success criterion in plain language.
2. System outline: known frontend/backend/data/integration components and their evidence; any suggested connection is marked inferred rather than observed.
3. Capabilities and gaps: what can be reused, what is missing and why the gap matters for the goal. Do not assert absent functionality just because a scan did not find it.
4. Evidence ledger separating observed facts, user statements, inferences and unknowns. Expanded details include source type, safe location, evidence ID and the precise supported claim.
5. Constraints and tensions: hard limits versus preferences, conflicting interpretations and the next user decision; no silent reconciliation.
6. Corrections and readiness: Brief version, interpretation changes, dependent invalidation and readiness with caveats. Correcting interpretation never rewrites underlying observed facts.

**Sources:** C3 Brief/summary/corrections, C6 revision. **States:** preliminary, partial, reviewed, conflicting, outdated downstream results. **Primary action:** copy a bounded context correction for Codex.

### 05 Options

**Decision:** what should be inspected or integrated first, and why did it survive the constraints?

1. Short recommendation summary tied to this project's goal and adoption intent; primary selection is explicitly conditional when mandatory facts are missing.
2. Category path with reasons, followed by distinct roles: primary candidate, supporting tool, reference only, compare against and avoid for now. A known hard-constraint failure cannot be presented as an eligible alternative without its disqualification.
3. Expanded candidate: canonical repository link/type, product value, matched requirements, integration surface, known prerequisites, caveats and next check. Evidence links sit next to the claims they support.
4. Activity and provenance: creation, last push, verified last commit/release, observation and snapshot/build dates remain distinct; missing values stay unknown. Do not copy push into commit or turn activity into an operability badge.
5. Retrieval disclosure: structured intent/aliases/constraints, matched fields, source/index/policy identity, actual candidate/card/byte counts, dedupe/exclusion/truncation reasons. The 60 candidates / 12 cards / 48 KiB values are labeled ceilings, never reported as actual results by default. Display is not limited to three cards by the sample mockup.
6. Avoid/defer ledger with rationale and revisit condition, plus an ordered documentation reading path. Scores, if exposed in diagnostics, are lexical ranks rather than fit probabilities.

**Sources:** C4 public cards/activity/eligibility, C5 memo/category path/roles/reading path, C9 retrieval/pack/pins. **States:** recommendations, conditional guidance, no match, retrieval unavailable, invalidated. Distinguish no match from index failure. **Primary action:** open comparison; saving a decision uses Codex.

### 06 Compare

**Decision:** which trade-offs change the choice for this project?

1. Comparison scope and currently inspected candidates; include the existing/no-change approach where useful. A no-change baseline is not an extra retrieved repository card.
2. Decision matrix: required capability, deployment, language/version compatibility, integration/migration surface, license, operating burden and evidence gaps. Empty/unknown cells are explicit.
3. Focused criterion inspector: expand a cell into source, claim, limitation and next check. Use direct labels and consistent row meaning, not stars or a synthetic total score.
4. Selection rationale: why one approach is worth the first experiment, strongest counterargument and the condition that would change the choice.
5. Hard exclusions/avoid-for-now remain visible separately from viable choices. Comparison does not override a mandatory constraint.
6. Next decision and draft selection: show that viewing/selecting a column is not a persisted adoption decision or verified compatibility.

**Sources:** C5 comparison/recommendations, C4 evidence, C3 constraints. **States:** fewer than two candidates, no candidates, unknown evidence, changed constraints, historical read-only. **Primary action:** inspect the integration plan or copy the decision to Codex. Narrow desktop windows can compare two options with accessible replacement controls; do not squeeze all columns below readable text size. Mobile is out of scope.

### 07 Integration

**Decision:** what is the smallest useful, reversible change to attempt next?

1. Proposed outcome and execution state; never imply the proposal has run. Carry the chosen candidates, Brief version and unresolved decisions.
2. A small proposed integration diagram with changed/reused boundaries, labeled as proposed. It describes this project's intended component join, not the plugin's own FTS5 retrieval pipeline.
3. Prerequisite table: version/license/API, data shape, deployment and necessary authorization, with evidence or the missing check. Preserve already-granted authorization; do not introduce blanket reapproval.
4. Step plan: action, affected component/path when grounded, dependency, proposed command if actually known, and per-step acceptance. Unsupported paths or commands remain hypotheses or are omitted.
5. First validation slice: synthetic/example input, expected behavior, actual result currently not run, and criterion for widening scope. No fabricated timings, estimates or passing checks.
6. Risk and rollback: what might fail, how to retain/restore the previous path, and when to stop.
7. Coding-agent handoff: goal, scope/non-goals, evidence, first slice, acceptance, stop conditions and actual authority boundary. Copyable, but not executed by HTML.

**Sources:** C5 integration plan/handoff, C3 context, C4/C9 evidence. **States:** proposed, prerequisites missing, invalidated, no selected candidate. Actual implementation status needs a later evidence contract; current proposal fields cannot be repurposed as execution tracking. **Primary action:** copy the scoped task for Codex.

### 08 History

**Decision:** what is saved, what can be resumed, and can this result still be used?

1. Current run, saved revision/phase/timestamp, Brief version and rendering revision as known at generation; separate incomplete/finalized status from useful partial content.
2. Artifact ledger: `state.json`, `status.html`, immutable `runs/{run_id}.json`, their roles and safe relative locations. Do not turn the internal recovery files into alternative current truth.
3. Finalized run history: decision summary, final revision/status and predecessor. Never promise a full archive or diff of every intermediate revision; only recorded corrections are available.
4. Provenance/replay inspector: catalog snapshot, schema, index/policy versions and actual hashes when present. Retrieval replay does not promise identical future model wording.
5. Recovery messages for writer-reported stale HTML, conflict/busy state, interrupted finalization or storage limit, with a safe next action. No automatic deletion, lock stealing or HTML filesystem repair.
6. Storage/privacy and language metadata: record-derived usage versus existing limits; sanitized confidential content may still enter Git/backups. Show default presentation language, translation coverage and source revision.

**Sources:** C6 state/history, C3 corrections, C9 pins. **States:** active, finalized, finalized incomplete, historical view, publication failure, integrity/storage problem. Detailed historical content is rendered from a validated selected run via Codex or safely embedded when bounded; a standalone HTML does not silently fetch arbitrary local JSON. **Primary action:** copy resume/view/recovery request, never mutate finalized history in the browser.

## RU-EN Localization Architecture

R15 adds full Russian and English interface support to the single artifact. It is distinct from existing RU/EN query alias coverage. `RU | EN` appears in the shared desktop header, uses language names/accessible labels rather than flags, and remains available on every view including errors.

1. **Static interface.** Bundle reviewed, keyed `ru` and `en` dictionaries for navigation, field labels, roles, statuses, validation/errors, unknown/partial/stale text, buttons, accessibility labels and print headings. Proposed CP-10 source files: `plugins/myai-stackguide/assets/locales/ru.json` and `en.json`. The renderer embeds them in the one HTML; no CDN, runtime translation API, fetch or new frontend framework is required.
2. **Narrative content.** Brief summaries, questions/rationales, fit/caveat explanations, comparison conclusions and integration/handoff prose need paired localized presentation fields tied to the same canonical domain field/evidence IDs and source revision. Produce them in the authorized host composition workflow, then sanitize/validate before saving. Never generate two independent recommendations. Original sanitized user statements and permitted minimized evidence text retain their language and attribution; do not persist raw source excerpts or chat; a translation is a labeled additional view, not replacement source evidence. New translations of finalized historical content must not rewrite the immutable run; use an explicitly derived view/new run with source provenance under the accepted contract.
3. **Contract amendment.** CP-03 now specifies `default_locale`, source language, presentation revision, translation coverage/status and field/locale mappings in `specs/artifact/localized-presentation.schema.json`, joined to affected source/state schemas. Version 1.1.0 adds these fields explicitly; original legacy examples are retained. The contract implementation is separate from the still-pending renderer and language runtime. Both languages must preserve negation, uncertainty, role, mandatory constraint, execution state and evidence references. Bind translated content to the relevant Brief version, memo/plan identity and content revision. A saved locale-preference-only change may advance the state revision without changing semantic content, invalidating retrieval or requiring a new translation; The workspace contract distinguishes these revision domains explicitly; runtime enforcement remains CP-07/10 work.
4. **Instant switch.** Switch labels and available precomputed narrative locally. A language click does not scan, retrieve, invoke a model, translate through a service, write `state.json`, change candidates or invalidate a pack. Preserve selected view, compared IDs, expanded evidence and focus. The saved locale changes only through the existing authorized writer workflow; the browser can retain a current-view choice in its fragment.
5. **Fallback.** A missing dynamic translation displays the original with its source language and an explicit translation-unavailable notice; it never looks like a complete translation. Static dictionary gaps fail the build. A critical translation missing at runtime yields a partial presentation, not a fabricated value, empty success, automatic model retry or blocked access to otherwise useful evidence. Complete RU and EN core flows are a local-release acceptance requirement.
6. **Canonical literals.** Repository/product names, IDs, URLs, filenames, commands, technology names, code, schema keys and raw evidence stay canonical. Dates/numbers are formatted for the selected locale while stored ISO timestamps/numbers remain unchanged; unknown values and units retain their semantics. Timezone is explicit rather than guessed from language.
7. **Persistence and accessibility.** Use a validated explicit fragment locale, then saved `default_locale`, then a documented `ru` default. Do not depend on `localStorage` for `file:` persistence. Switching updates document `lang`, accessible control labels, status text and localized prose; original-language passages carry their own `lang`. Preserve visible keyboard focus and readable controls at 200% text zoom. No-JS output remains a useful saved-default-language report with an honest notice that the interactive language switch is unavailable.
8. **Budgets and release.** One canonical evidence pack keeps the existing 48 KiB limit; duplicate translations are not added to FTS retrieval inputs or the model evidence pack. Paired presentation can increase generation work and stored bytes, so CP-04/11 measure its extra latency/size and semantic consistency. Existing 2 MiB state, 5 MiB HTML, output-root and history caps remain unchanged. On overflow return an explicit partial/error state under the accepted contract; do not silently raise caps, drop required evidence or prune history. CP-16 packages and version-pins both dictionaries with the tested template; older incompatible state must not be silently rewritten.

Browser constraints were checked against primary documentation: [MDN localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage) describes undefined `file:` behavior and possible storage errors; [HTML lang](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/lang) provides language semantics; [Intl](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl) provides locale-aware formatting. These references support the design, not tested browser behavior here.

## Implementation Order And Ownership

Keep the CP graph; localization is a cross-cutting acceptance slice, not a new hosted branch or CP-17.

| Task | Required amendment / owner | Acceptance before closure |
| --- | --- | --- |
| CP-03 | Catalog Architect: map the eight views to contracts; add localized-presentation and missing structured context mappings, revision/invalidation/size semantics; update linked examples in its own assignment | 22 local schemas accepted; 46 CP-03 and 27 C8 checks plus scorer CLI pass; renderer/runtime evidence remains future work |
| CP-04 | Quality Evaluator: paired-language cases for questions, summaries, uncertainty, caveats, integration and action authority; distinguish query retrieval evals from presentation parity | No meaning/role/constraint/authority drift; record translation latency/byte overhead without quality claims from static UI |
| CP-05 | Existing owner: align host composition/handoff behavior with one canonical result and localized presentation | No automatic translation-provider call or language-triggered retrieval; protected definitions require their assigned workflow |
| CP-07 | Plugin Runtime Builder: saved default locale and presentation revision through the shared writer; localized question-bank text; old-state compatibility | Resume/corrections and language metadata survive atomic save; no second state store |
| CP-09 | Plugin Runtime Builder: retain stable query/pack/result identifiers through display-locale changes | Same captured retrieval remains unchanged when only display language changes; semantic query edits remain real new work |
| CP-10 | Plugin Runtime Builder: eight-view renderer, RU/EN dictionaries, safe local switch, disclosure/comparison/copy fallback, print and desktop-window resizing | Both languages cover all sections/states and fit; no external resources; build rejects missing UI keys |
| CP-11 | Quality Evaluator with sequential builder fixes: first useful 1/1 bilingual join, then negative/size cases | One actual FTS5 result viewed in both languages; unchanged domain result and bounded state/HTML; distinguish this from independent RU/EN searches |
| CP-15 | Quality Evaluator/Evidence Reviewer: independent usefulness, translation/evidence parity and browser acceptance | Readable Russian/English desktop and laptop windows, keyboard and long-text/error/partial states; accept the working artifact against the already-approved composition |
| CP-16 | Package owner: include and pin dictionaries/template, verify fresh install/resume/upgrade/fallback | Offline artifact language switch works without service/credentials; old valid state remains recoverable and incompatible state is explicit |

## Approved Implementation Sequence

The existing task graph remains authoritative. The labels below sequence work within CP-10, not new CP tasks or independent file owners. Start the renderer after CP-03/05/07 prerequisites; it can consume accepted partial-state fixtures while CP-08/09 are built. Fixture rendering does not prove scanner, retrieval or installed-plugin routing. Do not wait for finished recommendations to create the first session HTML.

| Order | Implementation and owned files | Smallest acceptance checkpoint |
| --- | --- | --- |
| 1. CP-03, joined with CP-04; CP-05 readiness | Architect amends the registered presentation and affected domain schemas/examples; evaluator joins C8/C9 and language cases; existing role owners align host composition | Every subsection maps to a typed source or explicit unknown; content versus storage revisions, partial translations and publication outcomes are defined. Preserve accepted standards/compatibility evidence and verify each new runtime consumer |
| 2. CP-06 and CP-07 foundations | Pipeline Builder owns public cards/index; Runtime Builder owns the registered intake, question bank and shared state writer | Trusted Python/FTS5 preflight, one canonical state, saved answers/default locale, correction invalidation and a bounded commit/publication interface. No second persistence path |
| 3. CP-10-A: shell and language | Runtime Builder starts `plugins/myai-stackguide/scripts/render_report.py`, `assets/status-template.html`, `assets/locales/ru.json` and `assets/locales/en.json` under the same plugin root | One typical saved-start fixture renders the same `status.html` path with eight navigable views, honest unavailable sections and RU-EN switching. No dependency on a populated memo; no-JS saved-language content works |
| 4. CP-10-B: Goal, Questions, Scan, Context | Same renderer/template owner; CP-08 supplies accepted scan/context data through the common writer | All four source/section mappings render with facts versus interpretation, question rationale and saved answer ledger, coverage/limits, corrections and next Codex action. Idea/manual and partial-scan cases remain useful |
| 5. CP-10-C: Options, Compare, Integration | Same renderer/template owner; CP-09 supplies the captured FTS5 result/pack and canonical recommendation | Render every available role/card within existing caps, constraint/evidence matrix, counterargument, proposed component diagram, prerequisites, first check, rollback and copyable handoff. Demonstration content is confined to fixtures, never a production default |
| 6. CP-10-D: History and recovery | Same implementation owner; evaluator owns `tests/test_plugin_artifact.py` and rendered evidence throughout A-D | Immutable run summaries, revision/provenance, save-versus-render failures, long/empty/error content, desktop sizing, keyboard, 200% zoom, print and fallback behavior pass focused checks; then one complete eight-view RU/EN review |
| 7. CP-11, CP-15, CP-16 | Evaluator joins the lifecycle and independently reviews quality; package owners freeze the tested template/dictionaries/index and instructions | One actual useful FTS5 lifecycle first, then affected negatives/scaling, held-out usefulness and rendered acceptance, then authorized clean-install/resume/upgrade/rollback checks. Remote CP-12-14 remain deferred |

Runtime Builder owns renderer and state-writer integration; Quality Evaluator owns tests and evidence; Product Planner checks decision usefulness; Evidence Reviewer independently checks claims in CP-15. Handoffs for shared `intake.py`, `state_store.py` and the plugin skill are sequential under their CP-07 ownership, even when needed to complete CP-10. Do not create duplicate writers or overlapping parallel edits. Existing team packets/skills apply at implementation dispatch; this planning update does not activate agents or modify protected instructions.

## Commit And HTML Publication Lifecycle

1. The normal plugin entry workflow starts or resumes one run and publishes the initial shell from committed state. Questions and later sections can be incomplete. The user does not need a separate manual report command after each answer.
2. Each successful answer, context correction, completed scan/context/retrieval/recommendation phase, saved decision, saved locale preference or finalization uses CP-07's shared writer. Validate/sanitize, check expected run/revision and commit atomically; then publish `status.html` from that committed revision. Unsaved streaming chat or transient scan activity is not represented as saved progress.
3. CP-03 defines the publication outcome contract; CP-07 implements the shared boundary and can verify it with a renderer fixture until CP-10 binds the real renderer. Report saved run/revision separately from the published run/revision and a typed failure reason. Publication status is an operation result, not a competing domain store. CP-08/09 consume this boundary; they do not invent independent HTML pipelines.
4. Preserve the existing lock/revision/atomic-replace protocol. Before replacing HTML, verify that its input run/revision is still current under the shared lock; a late older render must never overwrite a newer published result. Do not hold the lock while waiting for user/model input or scanning. Failed state commit never reports an answer saved; failed rendering never rolls back an already committed answer or removes a previous valid HTML.
5. A saved-state/render failure returns an explicit pending/stale-publication result to Codex. Retry publication from validated current state with bounded attempts, without repeating the question, scan, retrieval or model composition. If the first render fails, report that no HTML is available yet. A rendered file displays only its known generation revision/time; it cannot detect a subsequent failed publication itself.
6. Codex links the same artifact after successful publication and tells the user to reopen/reload an already-open snapshot when needed. No automatic local-file polling, server, browser write bridge or live progress claim. Browser language/view/compare changes remain local presentation operations and do not enter the commit workflow.

CP-11's first lifecycle checkpoint is start -> saved answer -> scan/Brief -> captured FTS5 result -> integration memo -> correction/invalidation -> resume -> finalization. Assert the same HTML path, correct committed/published revision after successful publication, preserved finalized history, and no stale candidate presented as current after correction. Inject one publication failure and one competing newer revision to check preservation/retry and late-render rejection before broadening the suite.

## Verification And Concept Coverage

The design set comprises eight separate desktop views, one English comparison view; no mobile concepts. The selected light/forest palette, common shell and snapshot/Codex boundary remain; semantic depth increases. Each synthetic example is labeled as demonstration data. No real repository or scan result is fabricated for visual density.

Runtime checks are planned, not executed: all eight views in RU/EN at laptop/desktop widths (1280, 1440 and 1920 CSS pixels), a narrower desktop window, 200% text zoom, long RU labels and English fallback passages, keyboard/focus/`lang`, print source/caveat retention, no JavaScript, denied storage, unavailable clipboard, offline/zero requests, escaped hostile strings, invalid fragment, partial translation, missing dictionary key, corrected Brief invalidation, interrupted report publication, 2 MiB/5 MiB caps, unchanged canonical identifiers/candidates/evidence on locale switch, and immutable finalized history.

Product acceptance asks: can a founder explain why this approach is worth trying, can an engineer identify the affected component and first check, and can both distinguish unknowns from facts without opening every detail? First-screen usefulness must survive the increased density. No arbitrary number of subsections or image fidelity alone proves that outcome.

Rollback of this planning revision restores only its document differences against the saved dirty-worktree baseline. Runtime remains unmodified. The detailed visual baseline is owner-approved; compare the working artifact against it during CP-10/15 rather than requesting concept approval again. Documentation records scope rather than claims of working localization.
