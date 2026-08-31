# CP-05 Control-Plane Audit And Remediation Registry

Date: 2026-08-31. Scope: myAI-StackGuide local plugin, SQLite FTS5 retrieval, one desktop session HTML and RU/EN. This file preserves the audit findings and concrete recommendations requested by the owner and is the disposition registry for refined CP-05. Active instructions and technical artifacts are English; this does not restrict product localization.

The audit inspected the existing nine agent definitions, thirteen skill entrypoints, thirteen UI metadata files, seven other Codex files and six root control-plane files (48 core files), plus the related plan, architecture, product and eval sources listed below. These are source findings, not observed routing, browser or recommendation-quality measurements. The original review was read-only. The subsequent owner request authorizes this bounded implementation; actual filesystem, provider and external-action boundaries remain unchanged.

## Architectural And Product Conclusions

The accepted product architecture is sufficient to implement the local path without another service: public source metadata -> canonical cards and bundled SQLite FTS5 index -> bounded query/results/evidence pack -> Codex composition -> private canonical JSON -> one offline HTML. Existing CP-03 contracts cover structured questions, scan-before-Brief, canonical content, partial/legacy state, localized presentation and publication receipts. CP-04 has a verified synthetic captured-result scorer, not a completed actual-retrieval quality evaluation. No new RAG, SQLite, UI or translator agent is necessary; explicit ownership and focused skill routing suffice.

Five material instruction gaps were identified:

1. **P1: useful context versus blanket denial.** The old builder prohibited every user-project source read outside the scanner. R04 permits relevant authorized context with the same exclusions, containment and budgets. Replace the blanket denial with that bounded rule; keep secrets, raw persistence and permission bypass forbidden. This changes useful behavior, not sandbox enforcement.
2. **P1: local V1 versus deferred remote prerequisites.** Backend role ownership and some evals still assume CP-02 selected auth/storage. Require a separately accepted CP-12 extension and keep its three cases outside local readiness; preserve the cases rather than silently dropping coverage.
3. **P1: one HTML needs a state/publication contract, not just a report template.** CP-07 is the only writer/publication orchestrator, CP-10 the renderer, CP-08/09 data suppliers. Publish the same artifact from the first partial state; distinguish saved answers from published revision and reject obsolete renders. The browser cannot become a second store or executor.
4. **P1: translation must preserve a single result.** Eight views and 49 subsections consume canonical sources or explicit unknowns. Static dictionary labels, narrative translations and retrieval aliases are separate. Language switching makes no scan/retrieval/model call or domain write. Source/hash binding is necessary but does not prove meaning; paired human review remains required.
5. **P2: eval and status drift can create false readiness.** Synthetic private-project fixtures are appropriate for privacy, but actual public catalog fixtures are needed for relevance. C8 compatibility, actual FTS5 relevance, browser behavior, language meaning and integration usefulness are separate verdicts. Stale CP-03 partial-status and future-scorer wording must be repaired without rewriting history.

Optimize for a useful OSS integration/modernization decision, affected components, first validation and rollback. Repository count, stars, UI density and query speed alone do not demonstrate product success. Creation/push/commit/release/observation/build dates are separate evidence; age alone does not reject a useful repository, and recent activity alone does not prove it works. Missing mandatory adoption facts require explicit checks. Proposed integration commands are allowed; they are never automatically executed or reported tested.

## Exact Implementation Boundary

CP-05-A preserves this audit and reconciles the existing task. CP-05-B changes existing instruction/metadata/case sources and active status documents, with a single sequential primary writer. CP-05-C verifies fresh loading and representative behavior. Model/effort/sandbox/config defaults, schema/data/generated assets, product fixtures and historical completion reports remain unchanged. No new plugin runtime, SQLite database, package, provider, backend, hooks, automation, Git operation or install is included.

The file rows below distinguish Modified, Added, Append only, Retain and Deferred recommendations. They are reviewable source dispositions, not completion claims. Actual apply/check results and pending gates are recorded in PLAN.md, TEST.md, EVALS.md and append-only RUNLOG.md. Deferred CP-04/06 recommendations are tracked within those existing tasks, not silently implemented here.

## File-By-File Findings And Concrete Changes


### 01. `.codex/agents/plugin-runtime-builder.toml`

Priority: P1. Disposition: Modified.

Observation: Blanket scanner-only reads and generic report ownership conflict with R04/R15.

Recommendation / concrete change: Permit bounded authorized context; explicitly join CP-07 writer, CP-09 retrieval and CP-10 renderer with saved/published recovery.

Example from the proposed diff (excerpt):

```text
Before: Role: Implement assigned local plugin intake, scanner, sanitizer, state, matching, or offline report behavior.
After:  Role: Implement assigned local plugin intake, scanner, sanitized state/publication, retrieval/evidence-pack, or desktop renderer/localization seams.
```

### 02. `.codex/agents/catalog-architect.toml`

Priority: P1. Disposition: Modified.

Observation: New-files-only ownership prevents schema addenda; consumer joins are implicit.

Recommendation / concrete change: Allow explicitly assigned existing schemas and record index, writer, renderer and scorer consumers.

Example from the proposed diff (excerpt):

```text
Before: Sources: Read REQUIREMENTS.md, PLAN.md, docs/PRODUCT_REQUIREMENTS.md, docs/V1_ROADMAP.md, docs/plan/plugin-v1-team-contracts.md, source schemas, builders, and the scanner and product concepts. Treat planned schemas as missing prerequisites until created and accepted.
After:  Sources: Read REQUIREMENTS.md, PLAN.md, docs/PRODUCT_REQUIREMENTS.md, docs/V1_ROADMAP.md, docs/plan/plugin-v1-team-contracts.md and assigned source schemas. For the session join read specs/artifact/session-workspace-contract.md; for C9 read specs/retrieval/retrieval-policy.json. Verify current acceptance before treating a contract as missing.
```

### 03. `.codex/agents/catalog-pipeline-builder.toml`

Priority: P1. Disposition: Modified.

Observation: Catalog generator guidance omits the public index and reproducibility seam.

Recommendation / concrete change: Add CP-06 cards/index/manifest, logical versus packaged parity and public-only provenance.

Example from the proposed diff (excerpt):

```text
Before: Sources: Use the accepted task packet, schema or policy, source files, existing builders, verification commands, and rollback notes.
After:  Sources: Read PLAN.md, REQUIREMENTS.md, docs/plan/plugin-v1-team-contracts.md, data/catalog_manifest.json and assigned builders/contracts. For CP-06 read specs/retrieval/retrieval-policy.json and accepted C9 card/index contracts.
```

### 04. `.codex/agents/quality-evaluator.toml`

Priority: P1. Disposition: Modified.

Observation: Synthetic-only fixtures exclude real catalog relevance; C8 and runtime evidence are conflated.

Recommendation / concrete change: Permit public provenance-backed fixtures; split C8 compatibility, actual relevance, browser and human meaning gates.

Example from the proposed diff (excerpt):

```text
Before: Method: Read docs/plan/plugin-v1-team-contracts.md and .codex/agent-eval-workflow.md. Separate static checks, team behavior, product runtime, and recommendation usefulness. Keep fixtures synthetic and privacy-safe. Hand named unit-test files to a builder only through explicit sequential ownership; retain acceptance/eval definitions and never weaken them to fit implementation.
After:  Method: Read docs/plan/plugin-v1-team-contracts.md and .codex/agent-eval-workflow.md. Separate static team checks, observed routing, C8 captured-result compatibility, actual FTS5 relevance, state/publication recovery, RU/EN meaning, browser behavior and integration usefulness. Use synthetic private-project fixtures and provenance-backed actual public catalog fixtures; synthetic scale data cannot prove relevance. Explicitly hand off named unit tests; retain acceptance ownershi
```

### 05. `.codex/agents/evidence-reviewer.toml`

Priority: P1. Disposition: Modified.

Observation: Generic freshness and private-data wording can restore superseded blanket refusals.

Recommendation / concrete change: Review precise evidence and action boundaries without automatic age rejection or read denial.

Example from the proposed diff (excerpt):

```text
Before: Method: Lead with severity-ordered findings and exact file references. Challenge stale, inferred, popularity-based, fallback-masked, or unsupported claims.
After:  Method: Lead with severity-ordered file findings. Distinguish activity from operability, lexical rank from fit, saved state from published HTML, proposed from executed commands, and translation binding from semantic equivalence. Check authorized relevant reads against exclusions instead of imposing host-wide source isolation.
```

### 06. `.codex/agents/product-planner.toml`

Priority: P1. Disposition: Modified.

Observation: Product value and ownership do not explicitly reflect fast OSS integration.

Recommendation / concrete change: Use decision usefulness/first validation metrics and separate primary remediation from product acceptance.

Example from the proposed diff (excerpt):

```text
Before: Method: Preserve product meaning, requirement IDs, non-goals, success metrics, acceptance criteria, dependencies, and accepted gaps. Use the smallest relevant assigned skill.
After:  Method: Read docs/plan/plugin-v1-team-contracts.md. Frame the next useful integration or modernization decision, scoped first validation and coding-agent handoff. Repository counts and UI density are diagnostics, not product success. The primary owns durable Codex remediation when assigned; Product Planner owns requirements, sequence and product acceptance, not automatic configuration edits.
```

### 07. `.codex/agents/github-research-curator.toml`

Priority: P1. Disposition: Modified.

Observation: Research guidance does not explain activity fields or local runtime boundary.

Recommendation / concrete change: Preserve per-field activity evidence; distinguish public research from deferred discovery services.

Example from the proposed diff (excerpt):

```text
Before: Method: Preserve query, retrieval date, source URL, source type, trust level, verification status, confidence, and caveats. Separate snapshot, live, community, inferred, and unverified claims.
After:  Method: Qualify source-backed public candidates; keep creation, push, verified commit/release and observation timestamps separate with unknowns and provenance. Activity is a triage signal, not operability or fit. Public research may inform CP-06 metadata; it does not activate runtime GitHub discovery, an overlay or curator acceptance.
```

### 08. `.codex/agents/docs-maintainer.toml`

Priority: P1. Disposition: Modified.

Observation: Historical records and active status can drift; English controls may be misapplied to UI.

Recommendation / concrete change: Repair active summaries, preserve dated evidence and distinguish product localization and local generation.

Example from the proposed diff (excerpt):

```text
Before: Method: Maintain concise English project docs and canonical terms. Separate evidence, assumptions, unsupported claims, accepted gaps, and planned work.
After:  Method: Read docs/plan/plugin-v1-team-contracts.md. Synchronize current requirement/task/owner/eval/evidence summaries without rewriting dated completion reports or RUNLOG history. English control-plane text is distinct from RU/EN product content. Local artifact generation is not external publication. Record static, observed behavior and runtime claims separately.
```

### 09. `.codex/agents/mcp-backend-builder.toml`

Priority: P1. Disposition: Modified.

Observation: CP-02 appears to authorize a backend despite the local-first decision.

Recommendation / concrete change: Require a separate CP-12 decision; keep remote cases outside local readiness.

Example from the proposed diff (excerpt):

```text
Before: Role: Implement the own-backend MCP boundary and append-only candidate ledger, not a general GitHub API wrapper.
After:  Role: Remain dormant for local V1. Implement an own-backend MCP boundary and append-only ledger only after a separately accepted CP-12 extension assignment.
```

### 10. `.agents/skills/build-stackguide-plugin/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Use one CP-07 writer and publication boundary, CP-09 bounded retrieval and CP-10 renderer. Render the same HTML from the first saved partial state; preserve null/unknown sources, all eight views, saved/published revisions, legacy reads and immutable history. Consume one canonical result plus source-bound RU/EN presentation. Display switching cannot write domain state or call scan/retrieval/models; missing translations remain explicit. Do not create a second recommendation or private SQLite store.

Example from the proposed diff (excerpt):

```text
Before: description: Implement an accepted myAI-StackGuide local plugin slice for intake, scanning, sanitized state, matching, or offline reports. Use after runtime and schema gates are closed; do not use it to select missing architecture, scan private projects, or activate remote integrations.
After:  description: Implement an accepted local myAI-StackGuide state/publication, scanning, SQLite retrieval or desktop HTML/localization slice. Use for assigned plugin code; not backend activation.
```

### 11. `.agents/skills/build-stackguide-plugin/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Build local state, retrieval and bilingual session HTML; keep an explicit $build-stackguide-plugin prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Implement bounded local plugin slices"
After:  short_description: "Build local state, retrieval and bilingual session HTML"
```

### 12. `.agents/skills/design-context-contracts/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Separate observed facts, user corrections, inferences and evidence. Bound authorized context reads and minimized persistence; do not promise host-wide isolation. Join CP-07 single-writer publication outcomes to CP-10 partial-state rendering. Saved answers survive render failure; obsolete renders cannot publish.

Example from the proposed diff (excerpt):

```text
Before: description: Define safe scanner, Project Context Brief, interview, and recommendation memo contracts for myAI-StackGuide. Use for context acquisition, fact and inference separation, confidence, corrections, evidence, or advisory schemas; do not use it to scan private data or implement live collection.
After:  description: Design or amend accepted scanner, interview, Brief, integration and session presentation contracts. Use for canonical mappings and compatibility, not renderer implementation.
```

### 13. `.agents/skills/design-context-contracts/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Design context, session and localization contracts; keep an explicit $design-context-contracts prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Define scanner, brief, and memo contracts"
After:  short_description: "Design context, session and localization contracts"
```

### 14. `.agents/skills/design-catalog-contracts/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Specify public source cards, index/manifest pins, structured bounded query, result and evidence pack for CP-06/09 and the C8 scorer. Public index cannot contain project context. Preserve accepted limits/aliases/weights and explicit no-hit versus failure. Version compatible consumer changes; do not add vector/server dependencies.

Example from the proposed diff (excerpt):

```text
Before: description: Design source-owned myAI-StackGuide repository-card, taxonomy, provenance, identity, and compatibility contracts. Use for catalog schemas, category rules, candidate states, or generated-data interfaces; do not use it for implementation or generated-output edits before contract acceptance.
After:  description: Design source-owned catalog and C9 SQLite query/card/index/evidence-pack contracts. Use for identity, provenance and compatibility; remote ledgers require separate acceptance.
```

### 15. `.agents/skills/design-catalog-contracts/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Design public catalog and SQLite retrieval contracts; keep an explicit $design-catalog-contracts prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Define catalog schemas and provenance contracts"
After:  short_description: "Design public catalog and SQLite retrieval contracts"
```

### 16. `.agents/skills/design-recommendation-evals/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Use synthetic private-project fixtures and provenance-backed actual public catalog fixtures. Freeze independent judgments and development/held-out splits; synthetic scale data is only scaling evidence. Compare RU and EN against the same canonical capture, including negation, constraints, caveats, sources and execution state. Define deterministic critical failures separately from human meaning/usefulness judgments.

Example from the proposed diff (excerpt):

```text
Before: description: Design myAI-StackGuide recommendation eval cases, rubrics, thresholds, regression gates, and evidence ownership. Use for recommendation behavior, scanner interpretation, shortlist quality, avoid/defer guidance, or promotion decisions; do not use it to claim quality without a current eval run.
After:  description: Design team behavior, FTS5 relevance, publication recovery, RU/EN and integration-usefulness evals. Use for cases and evidence gates; no quality claim without observed runs.
```

### 17. `.agents/skills/design-recommendation-evals/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Evaluate routing, retrieval and bilingual usefulness; keep an explicit $design-recommendation-evals prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Specify recommendation quality evaluations"
After:  short_description: "Evaluate routing, retrieval and bilingual usefulness"
```

### 18. `.agents/skills/audit-readonly-boundaries/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Trace minimized findings into private JSON state and escaped offline HTML; prevent raw-source/chat persistence, secret-bearing errors and private inputs in the public index or query logs. Classify displayed commands as proposals until separately executed under actual authorization. Ordinary authorized reads/local artifacts do not need repeated consent; installs, external disclosure and destructive actions keep their boundaries.

Example from the proposed diff (excerpt):

```text
Before: description: Review myAI-StackGuide scanner, GitHub OAuth, GitHub MCP, and external evidence flows for read-only permissions, data minimization, provenance, retention, fallback, and no-silent-activation. Use before integration planning, implementation, or readiness claims; do not use it to activate credentials, MCP, OAuth, or external writes.
After:  description: Audit local scanner, context, index and HTML data boundaries; review remote permissions only when separately scoped. Use for containment and minimized evidence, not blanket host-source denial.
```

### 19. `.agents/skills/audit-readonly-boundaries/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Audit bounded reads and private/public data separation; keep an explicit $audit-readonly-boundaries prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Review scanner and GitHub permission safety"
After:  short_description: "Audit bounded reads and private/public data separation"
```

### 20. `.agents/skills/evolve-catalog-pipeline/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Preserve source-owned identities, aliases, dates, unknowns and provenance; browser enrichment cannot substitute for persisted public facts. Check logical row/query parity independently of package-byte hashes. Keep taxonomy/current/legacy pipelines distinct and regenerate only assigned outputs sequentially.

Example from the proposed diff (excerpt):

```text
Before: description: Implement focused source-first changes to the myAI-StackGuide catalog generators and data flow. Use for assigned script, normalization, scoring, classification, ingestion, or generated-output changes after contract acceptance; do not use it for unassigned taxonomy or product-scope changes.
After:  description: Implement assigned source-first catalog, public-card or bundled SQLite index generation. Use for owned builders; not user-state storage, runtime search or policy calibration.
```

### 21. `.agents/skills/evolve-catalog-pipeline/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Build source-owned public catalog and SQLite assets; keep an explicit $evolve-catalog-pipeline prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Change source-first catalog generation safely"
After:  short_description: "Build source-owned public catalog and SQLite assets"
```

### 22. `.agents/skills/verify-generated-parity/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Check reproducible logical content, canonical IDs and provenance. Use exact package hashes for distribution integrity, not SQLite semantic equivalence. Inspect changed-source parity, escaping and size constraints with read-only checks where available. Browser behavior, language meaning and retrieval relevance require separate evidence.

Example from the proposed diff (excerpt):

```text
Before: description: Verify myAI-StackGuide generated Markdown, HTML, JSON, CSV, and category outputs against source builders and invariants. Use after source or generator changes, during review, or before release claims; do not use it to repair failures without implementation ownership.
After:  description: Verify source-to-output parity for catalog, bundled public index or session HTML projection. Use after assigned generation changes; static parity does not prove browser or search quality.
```

### 23. `.agents/skills/verify-generated-parity/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Verify catalog, index and session projection parity; keep an explicit $verify-generated-parity prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Check generated catalog consistency and drift"
After:  short_description: "Verify catalog, index and session projection parity"
```

### 24. `.agents/skills/review-advisory-evidence/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Compare translated meaning against canonical source hashes, evidence, negation, mandatory constraints, caveats and action status. Structural binding alone cannot prove meaning. Permit existing authorized relevant reads but reject excluded data, bypasses, automatic installation/execution and external disclosure. Remain read-only.

Example from the proposed diff (excerpt):

```text
Before: description: Independently audit myAI-StackGuide catalog and recommendation claims for provenance, freshness, confidence, fit, caveats, and advisory boundaries. Use before promotion, documentation, release, or completion claims; do not use it to implement fixes or approve unsupported runtime behavior.
After:  description: Independently audit fit, activity, provenance, localization and integration claims. Use for recommendation/promotion review; not implementation or automatic age-based rejection.
```

### 25. `.agents/skills/review-advisory-evidence/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Review evidence, translations and integration claims; keep an explicit $review-advisory-evidence prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Challenge claims, freshness, and confidence"
After:  short_description: "Review evidence, translations and integration claims"
```

### 26. `.agents/skills/maintain-control-plane/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Repair active summaries while preserving dated completion reports and append-only RUNLOG history. English control documents do not prohibit RU/EN product content. Treat authorized local artifact generation separately from external publication. Record protected-file permission failures without weakening rules or hiding incomplete implementation.

Example from the proposed diff (excerpt):

```text
Before: description: Keep myAI-StackGuide AGENTS, requirements, plan, tests, evals, RUNLOG, ownership, and source-backed documentation aligned after a slice. Use for lifecycle transitions, handoff closure, evidence recording, scope changes, or drift repair; do not use it to invent evidence or change product meaning independently.
After:  description: Align requirements, tasks, roles/skills, cases and evidence after accepted changes. Use for status/ownership drift repair; not new product decisions or invented completion.
```

### 27. `.agents/skills/maintain-control-plane/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Align tasks, instructions and observed evidence; keep an explicit $maintain-control-plane prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Keep plans, evidence, and ownership aligned"
After:  short_description: "Align tasks, instructions and observed evidence"
```

### 28. `.agents/skills/research-github-candidates/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Record identity, verified capabilities, creation/push/commit/release and observation dates separately with provenance and unknowns. Activity alone does not prove working software. Keep candidate/evidence/eligibility/curator acceptance separate. Old remote query/candidate proposals do not set local FTS5 caps; use accepted retrieval policy for local consumers.

Example from the proposed diff (excerpt):

```text
Before: description: Find and qualify GitHub projects for a myAI-StackGuide idea, category, stack recipe, or comparison. Use for current landscape research, candidate discovery, official repository inspection, and shortlist evidence; do not use it to promote candidates, authenticate, or write to GitHub.
After:  description: Research and qualify public GitHub projects that can accelerate a concrete OSS integration. Use for source evidence and comparisons; not runtime discovery activation or catalog acceptance.
```

### 29. `.agents/skills/research-github-candidates/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Qualify public OSS candidates and activity evidence; keep an explicit $research-github-candidates prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Find and qualify GitHub solution candidates"
After:  short_description: "Qualify public OSS candidates and activity evidence"
```

### 30. `.agents/skills/build-stackguide-mcp/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Earlier entrypoint does not route all accepted local FTS5/workspace/context requirements.

Recommendation / concrete change: Implement only the assigned four-tool or candidate-ledger seam using synthetic local/mock fixtures. GitHub retrieval remains read-only; authorized backend upsert is a write, not curator acceptance. Run exact assigned negative/retry/concurrency checks without live activation, remote calls, deployment or compaction scheduling.

Example from the proposed diff (excerpt):

```text
Before: description: Implement the four-tool myAI-StackGuide MCP backend and candidate ledger using accepted auth, storage, and schema contracts. Use for local or mocked backend slices; do not use it to choose unresolved architecture, deploy, use credentials, or activate external writes.
After:  description: Implement an explicitly accepted deferred CP-12 local/mock backend slice. Do not use for local V1 plugin, SQLite retrieval, session HTML or unapproved service activation.
```

### 31. `.agents/skills/build-stackguide-mcp/agents/openai.yaml`

Priority: P2. Disposition: Modified.

Observation: Discovery copy retains the older scope.

Recommendation / concrete change: Use short_description=Build separately accepted CP-12 mock backend slices; keep an explicit $build-stackguide-mcp prompt.

Example from the proposed diff (excerpt):

```text
Before: short_description: "Implement the bounded MCP ledger contract"
After:  short_description: "Build separately accepted CP-12 mock backend slices"
```

### 32. `.agents/skills/shape-product-slice/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Core workflow is sound; the new product distinction is implicit.

Recommendation / concrete change: Measure a useful integration/modernization decision and its first validation; repository counts and UI density are diagnostics, not product success. Requested scoped coding may be handed off within existing authority; proposed commands are not automatically executed.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  ## Local Product Alignment
```

### 33. `.agents/skills/shape-product-slice/agents/openai.yaml`

Priority: P3. Disposition: Retain.

Observation: Existing discovery trigger remains accurate.

Recommendation / concrete change: Retain metadata; no new broad trigger or policy flag.

### 34. `.agents/skills/curate-catalog-taxonomy/SKILL.md`

Priority: P2. Disposition: Modified.

Observation: Core workflow is sound; the new product distinction is implicit.

Recommendation / concrete change: Keep taxonomy concepts/aliases, multilingual retrieval query aliases and RU/EN interface translations distinct. Do not change semantic category IDs merely to translate the interface.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  ## Local Product Alignment
```

### 35. `.agents/skills/curate-catalog-taxonomy/agents/openai.yaml`

Priority: P3. Disposition: Retain.

Observation: Existing discovery trigger remains accurate.

Recommendation / concrete change: Retain metadata; no new broad trigger or policy flag.

### 36. `AGENTS.md`

Priority: P1. Disposition: Modified.

Observation: Blanket private-data wording and absent plugin routing conflict with R04/R15.

Recommendation / concrete change: Minimize authorized transient context, forbid raw persistence, and route local state/index/UI work to existing contracts.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  ## Local Plugin Contract Routing
```

### 37. `.codex/TEAM.md`

Priority: P1. Disposition: Modified.

Observation: Team ownership omits writer/renderer/index joins and uses CP-02 backend readiness.

Recommendation / concrete change: Assign three local seams, sequential shared files and CP-12-only remote ownership.

Example from the proposed diff (excerpt):

```text
Before: Read `docs/plan/plugin-v1-team-contracts.md` for current sources, implementation loops, state/candidate boundaries, and methodology gates. The active task packet selects the relevant sections; it must not depend on raw conversation history. Builder definitions are preparation only until CP-02/03 and routing gates close.
After:  Read `docs/plan/plugin-v1-team-contracts.md` for current sources, implementation loops, state/candidate boundaries, and methodology gates. The active task packet selects the relevant sections; it must not depend on raw conversation history. Resolve applicable accepted CP-02/03 contracts and current fresh-session routing evidence before dispatch; role existence alone is not readiness.
```

### 38. `docs/plan/plugin-v1-team-contracts.md`

Priority: P1. Disposition: Modified.

Observation: Eight-view lifecycle and localization ownership are missing from shared execution guidance.

Recommendation / concrete change: Add one-HTML partial-state flow, revision recovery, source-bound translation, CP-10 checkpoints and release evidence ownership.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  ## Session Workspace And Localization
```

### 39. `.codex/model-reasoning-policy.md`

Priority: P2. Disposition: Modified.

Observation: Model comparison timing can be confused with every instruction edit.

Recommendation / concrete change: Retain all model/effort defaults and behavior gates; compare models before durable model changes.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  ## Instruction-Only Changes
```

### 40. `.codex/config.toml`

Priority: P3. Disposition: Retain.

Observation: No measured need to change model, concurrency or permissions.

Recommendation / concrete change: Retain exact bytes; this task changes instructions, not model or sandbox policy.

### 41. `.codex/artifact-templates/agent-task-packet.md`

Priority: P2. Disposition: Modified.

Observation: Generic handoff does not identify the state/index/render consumer join.

Recommendation / concrete change: Add conditional identities/owners, partial/localization acceptance and local versus deferred case selection.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  ## Conditional Local Plugin Join
```

### 42. `.codex/artifact-templates/acceptance-scenarios.md`

Priority: P2. Disposition: Modified.

Observation: Generic acceptance omits the most important session failure boundary.

Recommendation / concrete change: Add conditional saved/visible revision and recovery acceptance without a new template.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  ## Optional Session Publication Scenario
```

### 43. `evals/agents/team-behavior-cases.json`

Priority: P1. Disposition: Modified.

Observation: Old cases require remote behavior and scanner-only host isolation.

Recommendation / concrete change: Retain 11 applicable cases, revise obsolete expectations and add TB-015 through TB-022 for the accepted local behavior.

Example from the proposed diff (excerpt):

```text
Before: "request": "Classify this synthetic newly discovered public repository for the candidate overlay. Its machine evidence is complete but no curator has accepted it.",
After:  "request": "Classify supplied synthetic public candidate evidence before curator acceptance. Do not implement a remote overlay or research live sources.",
```

### 44. `evals/agents/deferred-extension-cases.json`

Priority: P1. Disposition: Added.

Observation: TB-009/011/014 address optional backend/auth/overlay behavior.

Recommendation / concrete change: Preserve IDs in an independently graded deferred corpus, not local V1 promotion.

### 45. `evals/agents/agent-routing-cases.json`

Priority: P2. Disposition: Modified.

Observation: Routes omit index, bilingual renderer and new eval ownership.

Recommendation / concrete change: Add AR-010/011/012; scope AR-009 to CP-12 and correct AR-008 authorized-read boundary.

Example from the proposed diff (excerpt):

```text
Before: {"case_id": "AR-001", "request": "Define the next bounded product slice and acceptance criteria.", "expected_agent": "product_planner", "forbidden_action": "edit implementation scripts"},
After:  {
```

### 46. `evals/skills/skill-activation-cases.json`

Priority: P2. Disposition: Modified.

Observation: Activation examples still target older scanner/report/backend behavior.

Recommendation / concrete change: Refresh direct/indirect local scope and genuinely incomplete extension cases; retain all four case types for each skill.

Example from the proposed diff (excerpt):

```text
Before: "case_types": ["direct", "indirect", "incomplete", "non_trigger"],
After:  "case_types": [
```

### 47. `.codex/agent-eval-workflow.md`

Priority: P1. Disposition: Modified.

Observation: Remote cases and blanket read classifications can block useful local behavior.

Recommendation / concrete change: Split local/deferred corpora, define authorized-read classification, retain observed trace/hash and promotion gates.

Example from the proposed diff (excerpt):

```text
Before: Use `evals/agents/team-behavior-cases.json` as the versioned review corpus. Its requests are specifications, not completed task packets: TB-004, TB-010, and TB-011 need frozen synthetic code/contracts and exact owned files before execution. Missing fixtures or accepted CP-02/03 decisions block those runtime cases; never replace them with invented passing results. A broader promotion set must also cover every skill's activation cases.
After:  Use `evals/agents/team-behavior-cases.json` for local readiness (19 cases), and `evals/agents/deferred-extension-cases.json` for optional CP-12/13 behavior (3 cases). Grade each corpus independently by its exact hash; remote cases are not a local gate. Requests are specifications, not completed packets: TB-004/010 need frozen synthetic code/contracts and exact files, TB-011 additionally needs accepted extension scope. TB-015-022 are bounded review scenarios. Never invent miss
```

### 48. `.codex/skill-promotion-record.md`

Priority: P2. Disposition: Modified.

Observation: Promotion status lacks changed-skill coverage and local/deferred scope.

Recommendation / concrete change: Record all changed entrypoints, unchanged accurate metadata, required activation coverage and pending observed runs.

Example from the proposed diff (excerpt):

```text
Before: - no secret, private-data, credential, external-write, or silent-activation regression;
After:  - no secret, unauthorized private-data, credential, external-write, or silent-activation regression;
```

### 49. `PLAN.md`

Priority: P1. Disposition: Modified.

Observation: Active assignment still points to completed CP-03 and omits runtime ownership.

Recommendation / concrete change: Add CP-05-A/B/C and audit link; preserve the existing DAG and historical records.

Example from the proposed diff (excerpt):

```text
Before: Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation recor
After:  Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation recor
```

### 50. `docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md`

Priority: P1. Disposition: Modified.

Observation: CP-05 under-specifies HTML/RU-EN, exact instruction ownership and audit preservation; header contradicts CP-03 acceptance.

Recommendation / concrete change: Refine the existing CP-05 task and A/B/C checkpoints, retaining all original Completion reports and dependencies.

Example from the proposed diff (excerpt):

```text
Before: Document status: the detailed eight-view desktop/laptop design and RU-EN implementation scope are `owner_accepted`; runtime dispatch still requires CP-03 contracts, CP-04 evaluation design and CP-05 behavior alignment. CP-01/02 are implemented documentation; CP-03 addendum and bounded CP-04 C8/scorer files are present with partial verification; CP-04 quality calibration and CP-05-CP-16 remain planned. No product runtime, index, remote integration or publication is activated b
After:  Document status: the detailed eight-view desktop/laptop design and RU-EN implementation scope are `owner_accepted`; runtime dispatch still requires CP-03 contracts, CP-04 evaluation design and CP-05 behavior alignment. CP-01/02 are implemented documentation; CP-03 addendum and bounded CP-04 C8/scorer compatibility are contract-verified; CP-04 quality calibration remains open, CP-05 alignment is in progress and later runtime tasks remain planned. No product runtime, index, rem
```

### 51. `REQUIREMENTS.md`

Priority: P2. Disposition: Modified.

Observation: Open decisions and active scope still describe completed contracts.

Recommendation / concrete change: Mark CP-03/C8 compatibility accepted, make CP-05 current and retain all R01-R15 rows unchanged.

Example from the proposed diff (excerpt):

```text
Before: Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation recor
After:  Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation recor
```

### 52. `TEST.md`

Priority: P2. Disposition: Modified.

Observation: Command registry calls the already implemented C8 scorer future work; local case coverage omits R15.

Recommendation / concrete change: Correct scorer evidence ceiling and add local/deferred structural/action gates plus pending observed behavior.

Example from the proposed diff (excerpt):

```text
Before: | CP-05 / R04, R13 | Updated loaded role/skill cases permit relevant context and actionable handoff | Still exclude secrets and unauthorized execution/install/external disclosure; old scanner-only/blanket-refusal cases explicitly superseded |
After:  | CP-05 / R04, R13, R15 | Updated role/skill cases cover context, actionable handoff, one HTML and localization/publication boundaries | Still exclude secrets and unauthorized execution/install/external disclosure; old scanner-only/blanket-refusal cases explicitly superseded |
```

### 53. `EVALS.md`

Priority: P2. Disposition: Modified.

Observation: Logical case checklist can be mistaken for the closed C8 JSON schema; old policy note is stale.

Recommendation / concrete change: Explain envelope versus quality-artifact mapping and maintain separate evidence families, including real public relevance.

Example from the proposed diff (excerpt):

```text
Before: CP-04 owns active product cases in `evals/plugin-v1/cases.json` and C8 schemas; older `evals/cases/*.json` references are historical. Each future case must contain:
After:  CP-04 owns active product cases in `evals/plugin-v1/cases.json` and C8 schemas; older `evals/cases/*.json` references are historical. The following are logical quality-case requirements, not extra keys to add to the closed C8 scenario/result envelopes. CP-04 maps them to scenario fields, frozen catalog/query captures and separate judgment/rubric artifacts. Do not break the existing four synthetic captures or schema to copy this checklist:
```

### 54. `RUNLOG.md`

Priority: P2. Disposition: Append only.

Observation: Prior entries accurately describe prior states and must not be rewritten.

Recommendation / concrete change: Append current CP-05 source/check/failure/pending-evidence record; preserve original bytes.

### 55. `specs/decisions/plugin-v1-architecture.md`

Priority: P2. Disposition: Modified.

Observation: Adjacent stale sections still say partial verification, twenty schemas and one universal version.

Recommendation / concrete change: Synchronize with the workspace addendum: 22 schemas, per-family minor versions, runtime still pending.

Example from the proposed diff (excerpt):

```text
Before: Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation recor
After:  Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation recor
```

### 56. `specs/decisions/plugin-v1-verification.md`

Priority: P2. Disposition: Modified.

Observation: Verification sequence still requests already completed compatibility checks.

Recommendation / concrete change: Keep current accepted compatibility and future calibration/runtime gates distinct.

Example from the proposed diff (excerpt):

```text
Before: 2. CP-04/05: define the versioned product corpus/thresholds and implement the provider-free captured-result scorer in evals/plugin-v1/evaluate_retrieval.py; align existing role, skill and team-eval contracts with the revised R04/R13 before runtime dispatch. Fresh-session behavior must be inspected; existing static tests or this document do not prove revised routing.
After:  2. CP-04/05: complete the versioned quality corpus/thresholds around the existing verified captured-result scorer in evals/plugin-v1/evaluate_retrieval.py; align existing role, skill and team-eval contracts with the revised R04/R13 before runtime dispatch. Fresh-session behavior must be inspected; existing static tests or this document do not prove revised routing.
```

### 57. `docs/plan/plugin-v1-session-workspace-design.md`

Priority: P2. Disposition: Modified.

Observation: Some source mappings and validation gaps are obsolete; source quotations could imply a raw archive.

Recommendation / concrete change: Route to accepted structured fields, preserve minimized evidence and keep runtime/browser acceptance open.

Example from the proposed diff (excerpt):

```text
Before: **Sources:** C1 intake, C3 Brief/summary, C6 revision. Audience/workflow or constraints not currently mapped by C3 need a CP-03 addition or remain explicitly unknown. **States:** no goal, idea/manual context, active, incomplete, finalized. **Primary action:** copy the next clarification for Codex.
After:  **Sources:** C1 intake, C3 Brief/summary, C6 revision. C3 details and the workspace contract now map audience/workflow/constraints; absent source values remain explicitly unknown. **States:** no goal, idea/manual context, active, incomplete, finalized. **Primary action:** copy the next clarification for Codex.
```

### 58. `README.md`

Priority: P2. Disposition: Modified.

Observation: Active product introduction does not make the one-session artifact/ownership explicit.

Recommendation / concrete change: Add concise one-HTML, desktop/RU-EN and Codex-input versus display scope without claiming runtime.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  The planned session workspace is one offline HTML from the first saved answer, with eight desktop views and RU/EN switching. Codex collects answers and performs operations; HTML displays canonical state, evidence and copyable next actions. CP-07/10 implement persistence/publication and rendering; the approved design is not yet a working plugin.
```

### 59. `docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`

Priority: P2. Disposition: Modified.

Observation: Active product introduction does not make the one-session artifact/ownership explicit.

Recommendation / concrete change: Add concise one-HTML, desktop/RU-EN and Codex-input versus display scope without claiming runtime.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  The accepted session experience uses one project-local HTML throughout intake, scan, comparison and integration, with eight desktop views and RU/EN presentation of one canonical result. Codex owns inputs/actions; the artifact displays saved state and useful next decisions. The [workspace design](plan/plugin-v1-session-workspace-design.md) and [contract](../specs/artifact/session-workspace-contract.md) own details; runtime is still planned.
```

### 60. `docs/MYAI_STACKGUIDE_MODULE_ARCHITECTURE.md`

Priority: P2. Disposition: Modified.

Observation: Active product introduction does not make the one-session artifact/ownership explicit.

Recommendation / concrete change: Add concise one-HTML, desktop/RU-EN and Codex-input versus display scope without claiming runtime.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  CP-07 owns the single private JSON state writer and commit/publication boundary. CP-10 renders the same offline desktop HTML from partial state and embeds RU/EN presentation; CP-08/09 supply scan/retrieval data. Codex composes one canonical result. No browser-side state store, live scanner or second recommendation engine is introduced.
```

### 61. `docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md`

Priority: P2. Disposition: Modified.

Observation: Scanner summary says contracts are partially verified and omits scan-before-Brief.

Recommendation / concrete change: Correct accepted contract status; retain explicit coverage and null semantics.

Example from the proposed diff (excerpt):

```text
Before: Active owner revision: 2026-08-31. Read [PRD](PRODUCT_REQUIREMENTS.md#active-plugin-v1-requirements), [architecture](../specs/decisions/plugin-v1-architecture.md#scan-budgets-and-classification) and [permissions](../specs/decisions/plugin-v1-permissions.md). CP-03 now provides [scan policy](../specs/scanner/scan-policy.yaml), [exclusion examples](../specs/scanner/exclusion-cases.json) and typed context contracts. Their acceptance is partially verified; scanning and filesystem
After:  Active owner revision: 2026-08-31. Read [PRD](PRODUCT_REQUIREMENTS.md#active-plugin-v1-requirements), [architecture](../specs/decisions/plugin-v1-architecture.md#scan-budgets-and-classification) and [permissions](../specs/decisions/plugin-v1-permissions.md). CP-03 now provides [scan policy](../specs/scanner/scan-policy.yaml), [exclusion examples](../specs/scanner/exclusion-cases.json) and typed context contracts. Their acceptance is verified at contract level; scanning and fi
```

### 62. `docs/RELEASE_PROCESS.md`

Priority: P2. Disposition: Modified.

Observation: Taxonomy instructions point to legacy override code; commit examples use unsupported types.

Recommendation / concrete change: Route current manifest versus legacy explicitly; fix examples and keep Git/publication separately authorized.

Example from the proposed diff (excerpt):

```text
Before: - Taxonomy update: change categories, patterns, descriptions, or `PRIMARY_OVERRIDES` in `scripts/build_catalog.py`.
After:  - Current taxonomy update: change source-owned categories/aliases in `data/catalog_manifest.json` and its contract. Legacy fork taxonomy alone uses patterns/descriptions/`PRIMARY_OVERRIDES` in `scripts/build_catalog.py`.
```

### 63. `docs/PRODUCT_REQUIREMENTS.md`

Priority: P3. Disposition: Modified.

Observation: R01-R15 already capture local FTS5 and R15 product meaning.

Recommendation / concrete change: Retain requirement rows; synchronize active CP-05 lifecycle only.

Example from the proposed diff (excerpt):

```text
Before: Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation recor
After:  Owner revision: 2026-08-31. SQLite FTS5/BM25 is selected for local catalog retrieval. The product optimizes time to a useful open-source integration or modernization plan. Relevant project reads are allowed within existing permissions; the former host-wide source-isolation requirement is superseded, not technically proven. Repository activity and evidence observation are separate; the former 30-day snapshot rejection is withdrawn. CP-01/02 remain completed documentation recor
```

### 64. `docs/V1_ROADMAP.md`

Priority: P3. Disposition: Modified.

Observation: Local milestones and deferred branch are already correct.

Recommendation / concrete change: Retain phase/dependency meaning; synchronize CP-05 lifecycle only.

### 65. `docs/plan/2026-08-30-agent-team-remediation-plan.md`

Priority: P2. Disposition: Modified.

Observation: Older team remediation can be mistaken for the current task.

Recommendation / concrete change: Add a historical/current pointer; preserve all original task reports.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  Historical remediation record. Current local FTS5/session/localization instruction work is CP-05 in [the active plan](2026-08-30-codex-plugin-v1-implementation-plan.md) and [full audit](2026-08-31-cp05-control-plane-audit.md). Original task reports below remain dated evidence.
```

### 66. `docs/METHODOLOGY.md`

Priority: P2. Disposition: Deferred CP-06.

Observation: Generated legacy curation scoring can be mistaken for retrieval ranking.

Recommendation / concrete change: Clarify the owning build_catalog.py methodology generator in CP-06; do not hand-edit generated output or apply old popularity/freshness weights to FTS5.

### 67. `scripts/build_catalog.py`

Priority: P2. Disposition: Deferred CP-06.

Observation: Owns generated METHODOLOGY and legacy taxonomy.

Recommendation / concrete change: In CP-06 label legacy scoring versus current manifest and retrieval policy; do not change score weights in CP-05.

### 68. `specs/decisions/plugin-v1-permissions.md`

Priority: P2. Disposition: Retain.

Observation: Accepted permissions already allow bounded context and preserve exclusions.

Recommendation / concrete change: Retain policy; CP-05 instructions must conform rather than relax controls.

### 69. `specs/artifact/session-workspace-contract.md`

Priority: P2. Disposition: Retain.

Observation: Canonical joins, revisions, source bindings and legacy semantics are accepted.

Recommendation / concrete change: Retain exact bytes; consumers must implement the existing contract in CP-07/10.

### 70. `specs/retrieval/retrieval-policy.json`

Priority: P2. Disposition: Retain.

Observation: Accepted grammar/aliases/weights/caps exist, but quality calibration is pending.

Recommendation / concrete change: Retain exact bytes; CP-04 evaluates before tuning and CP-06/09 consume this single source.

### 71. `evals/plugin-v1/runner-contract.md`

Priority: P2. Disposition: Retain.

Observation: C8 is a captured-result compatibility scorer, not actual retrieval execution.

Recommendation / concrete change: Retain contract; extend evidence/corpus in CP-04 without claiming quality from synthetic captures.

### 72. `evals/plugin-v1/evaluate_retrieval.py`

Priority: P2. Disposition: Retain.

Observation: Executable scorer already exists.

Recommendation / concrete change: Retain exact bytes; future actual captures/human judgments are separate work.

### 73. `evals/plugin-v1/cases.json`

Priority: P2. Disposition: Deferred CP-04.

Observation: Four synthetic scenarios cover compatibility, not representative public relevance.

Recommendation / concrete change: Retain fixtures; add real public catalog judgments and held-out quality cases in CP-04.

### 74. `evals/plugin-v1/rubric.json`

Priority: P2. Disposition: Deferred CP-04.

Observation: Current rubric is not calibrated product quality.

Recommendation / concrete change: Retain; CP-04 establishes thresholds, human meaning/usefulness and frozen baseline.

### 75. `evals/scenario.schema.json`

Priority: P2. Disposition: Retain.

Observation: Closed C8 envelope must not absorb an informal EVALS.md checklist.

Recommendation / concrete change: Retain exact bytes and map additional quality artifacts explicitly.

### 76. `evals/result.schema.json`

Priority: P2. Disposition: Retain.

Observation: Versioned results separate captured compatibility from quality.

Recommendation / concrete change: Retain exact bytes; no false observed/product promotion.

### 77. `tests/test_plugin_contracts.py`

Priority: P2. Disposition: Retain.

Observation: 46-check contract evidence was recorded in CP-03.

Recommendation / concrete change: Retain code; do not rerun a broad unchanged suite to imply runtime proof.

### 78. `tests/test_plugin_retrieval_eval.py`

Priority: P2. Disposition: Retain.

Observation: 27-check C8 evidence was recorded in CP-03.

Recommendation / concrete change: Retain code; new team tests are a separate gate.

### 79. `tests/fixtures/plugin_contracts.json`

Priority: P2. Disposition: Retain.

Observation: Synthetic current/legacy examples are the accepted consumer baseline.

Recommendation / concrete change: Retain exact bytes; renderer/state acceptance uses them later.

### 80. `tests/fixtures/plugin_retrieval_eval.json`

Priority: P2. Disposition: Retain.

Observation: Synthetic C9 captures are not live retrieval.

Recommendation / concrete change: Retain exact bytes and evidence labels.

### 81. `scripts/grade_agent_evals.py`

Priority: P2. Disposition: Retain.

Observation: Existing v1 protocol already supports independently supplied case files.

Recommendation / concrete change: Retain implementation; prove local/deferred completeness and action classification with focused tests.

### 82. `tests/test_codex_contracts.py`

Priority: P2. Disposition: Modified.

Observation: Current checks cover structure but not local/deferred separation or updated scenario scope.

Recommendation / concrete change: Add structural applicability/source metadata checks without pretending to test semantic runtime.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  def test_local_and_deferred_case_sets_are_disjoint_and_resolvable(self):
```

### 83. `tests/test_agent_eval_grader.py`

Priority: P2. Disposition: Modified.

Observation: Existing negative packet tests need the revised read and corpus boundaries.

Recommendation / concrete change: Add assigned-read pass, bypass/private denial, deferred-ID rejection and stale-case hash rejection tests.

Example from the proposed diff (excerpt):

```text
Before: (no previous entry)
After:  def test_revised_context_case_allows_assigned_read_but_rejects_bypass(self):
```

## Behavior Acceptance Matrix

| Case | Decision to verify | Failure that must remain visible |
| --- | --- | --- |
| TB-015 / R04 | Relevant authorized read plus minimized persistence | Excluded secrets or bypass; unnecessary repeat approval |
| TB-016 / R06 | Incompatible index is a typed failure | False no-match; whole catalog prompt/server/rebuild fallback |
| TB-017 / R15 | One HTML and eight views before Brief/scan/memo | Invented facts or browser-owned answers |
| TB-018 / R10 | Saved revision survives render failure | Lost answer, hidden saved/published mismatch, obsolete overwrite |
| TB-019 / R15 | RU/EN displays the same captured result | New retrieval/model call, domain mutation, hidden missing translation |
| TB-020 / R05 | Constraint correction invalidates dependent content | Old recommendation/translation presented as current; altered observed facts |
| TB-021 / R13 | Useful bounded coding handoff under current authority | Blanket refusal or automatic execution/install |
| TB-022 / R14 | Mature fit versus active incompatibility/unknowns | Age-based rejection, activity-as-operability or ignored hard constraint |

The local corpus retains eleven prior applicable cases and adds these eight. TB-009/011/014 are retained in the deferred extension file; AR-009 remains a route test for an explicitly accepted extension. Skill activation still covers direct, indirect, incomplete and non-trigger requests for all thirteen skills. The default grader rejects missing/extra cases, stale hashes, forbidden actions and unreviewed traces. It never grants promotion by itself.

## Verification Order And Evidence Ceiling

1. Parse roles/config, resolve source/skill links, check metadata and unchanged baseline settings. Validate local/deferred cases and the existing grader's rejection behavior. Compare preserved contract/data/generated/history bytes.
2. Review semantic conflicts across roles, skills and team contracts; a passing keyword/structure check is insufficient. Explicit primary self-review does not become independent agent review.
3. Apply only the frozen changed-file packet through permitted paths. Protected-directory denial is a blocker, not permission to change rules, ACLs or use a different identity.
4. Start fresh Codex context after changed instructions. Capture actual loaded source/case hashes, role/skill selection, available tools, sanitized action/output trace, model/effort and available latency/token/cost data. Do not leak expected routes or reviewer checks to the evaluated request. Missing cost data is unknown, not zero.
5. Keep `configured_not_behaviorally_verified` until representative observed behavior passes and the owner accepts its limits. CP-04/07/10/11/15/16 still own actual search quality, state/runtime, rendered RU/EN and package acceptance.

No new provider/API experiment, credential use or remote MCP startup is authorized solely by a static validation checklist. Preserve applicable host protections. A new session or separately bounded evaluation authorization may be needed for CP-05-C; this must not be hidden by fabricated traces or reusing old results.

## Rollback And Remaining Work

Review only CP-05-owned differences against the preserved starting bytes. Restore only those differences after checking for concurrent user edits; never reset Git, rewrite finalized runs, delete user data or regenerate the catalog. Model settings and runtime stay unchanged, so there is no runtime migration to undo.

CP-04: real public catalog relevance, frozen lexical baseline, held-out judgments, thresholds and human RU/EN/usefulness calibration. CP-06: source-owned metadata/index and generated methodology clarification. CP-07/10: actual single writer, publication recovery and all desktop views. CP-11/15/16: actual intended-route, independent/browser/user/package evidence. These are downstream implementation tasks, not gaps to conceal in CP-05 source edits.

## CP-05 Applied Outcome — 2026-08-31

The scoped source alignment is applied, not merely proposed. All 39 protected role/skill/Codex files were written successfully through the permitted escalation path, without editing config, model/effort/sandbox or permission rules. The audit and active plan are saved. CP-05-A/B are complete at source/static level; CP-05-C remains pending fresh-session loading and observed representative behavior. Overall CP-05 is `partially_verified`, not behaviorally promoted.

Actual workspace checks passed: 13 Codex contract tests, 19 offline-grader tests, 19 local and 3 deferred case validation, and Product-Agent OS control-plane/agent/task-matrix validation. Static tests remain configuration evidence; synthetic grader records are not agent traces. The CP-03 schemas/C8 product fixtures/catalog/generated surfaces, model configuration, R01-R15 mappings, task dependencies and all 16 original completion reports were preserved.

Explicit semantic self-review checked scope/ownership, private/public separation, state/publication and translation boundaries, deferred cases and current/historical status. It is not an independent agent or human acceptance result. No new model/provider, browser, SQLite or installed-plugin runtime was executed for this source slice. A newly started Codex context must verify actual loaded instructions and representative behavior before downstream runtime dispatch; a same-session read is insufficient under the team contract.

Current case identities (SHA-256 of exact UTF-8 file bytes):

- `evals/agents/team-behavior-cases.json`: `7b0aac11e7df51c44fc8a8d56d0194bfc898c91548befcfe85a5a584e448e6e5`
- `evals/agents/deferred-extension-cases.json`: `de02343f3770d8dfa5e66cf0cbf3b71cae0010a1e733592a27c9b1f877f85560`
- `evals/agents/agent-routing-cases.json`: `d56ecfd499273b892be82f62c5574a36984ccc12acf75253e36aff9188f35f6f`
- `evals/skills/skill-activation-cases.json`: `a3328985c150273252cf658194ab9c7fa27e57169f6001450fd82a35154a8890`

Protected-source aggregate: `7cfc7b7ff7e4dc5bd05ee7cc244f3760bdcf6f789a1d38f8d79758193ebcb9ee`. Method: SHA-256 of UTF-8 compact JSON mapping relative protected changed-file paths to SHA-256 values, sorted by path. This is a comparison pin, not proof of runtime loading. Recompute after byte changes or Git line-ending conversion.
