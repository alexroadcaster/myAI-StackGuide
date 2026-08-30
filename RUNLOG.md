# RUNLOG.md

Durable run log for analysis, update decisions, failed checks, and residual risks. Keep entries concise, factual, and tied to commands or files.

## 2026-05-24 - Deep Project Analysis And Control-Plane Docs

### Scope

- Analyzed the workspace as a two-layer project:
  - Parent `github_research`: one-off GitHub account research archive for `alexroadcaster`.
  - Nested `agentic-engineering-catalog`: durable Git repository and catalog product.
- Added project-control documentation for future agentic work:
  - `AGENTS.md`
  - `RUNLOG.md`
  - `RELEASE_PROCESS.md`

### Project Reading

- The catalog started as a personal fork analysis and grew into a broader AI repository decision catalog.
- The product intent is practical repository triage for founders, product managers, engineers, designers, growth teams, operations, and researchers.
- The current generated unified catalog contains 42 categories, 351 category placements, and 314 unique repositories.
- The base account fork catalog contains 107 repositories from `data/source_repos.csv`.
- The parent account report says the public GitHub account is 107/107 forks, with 0 public original repositories and 0 public stars on those forks.

### Architecture Findings

- `scripts/build_catalog.py` builds the base account fork catalog from `data/source_repos.csv`.
- `scripts/build_unified_catalog.py` combines:
  - `data/repos.csv`
  - `research/github_curated_recommendations_2026-05-23.json`
  - `research/github_business_curated_recommendations_2026-05-23.json`
- `scripts/build_catalog_html.py` builds the standalone interactive HTML artifact from the same unified payload.
- Generated outputs are reproducible: in-memory generated `UNIFIED_CATALOG.md` and `UNIFIED_CATALOG.html` matched checked-in files during analysis.

### Data Quality Findings

- AI/engineering research data is mostly structured GitHub API data.
- Business/product research data is lower-confidence because the checked-in snapshot was produced from GitHub public HTML search plus repository pages.
- In the checked-in business/product snapshot, most rows lack language/license metadata and forks are effectively unavailable.
- Catalog scores are useful for triage but should not be presented as due diligence, security review, production-readiness, or code-quality certification.

### Decisions

- Put durable agent instructions in the nested Git repository, not the parent workspace, because the parent directory is not a Git repo.
- Keep new control-plane docs in English to match existing repository documentation.
- Do not regenerate catalog outputs in this run because the user asked for control-plane artifacts, not a data refresh.
- Preserve root-level GitHub account research artifacts as archive inputs rather than moving or editing them.

### Commands And Evidence

```powershell
Get-ChildItem -Force
Get-ChildItem -Path . -Recurse -Filter AGENTS.md -Force
Get-ChildItem -Path . -Recurse -Include RUNLOG.md,RELEASE.md,UPDATE.md,PROCESS.md -File -Force
git -c core.excludesfile= status --short
python -c "<in-memory unified Markdown and HTML parity check>"
rg -n "[ \t]+$" AGENTS.md RUNLOG.md RELEASE_PROCESS.md
git -c core.excludesfile= ls-files --others --exclude-standard
```

Observed:

- No existing `AGENTS.md`, `RUNLOG.md`, or release/update process document was present before this change.
- `agentic-engineering-catalog` had no tracked or untracked changes before edits.
- Generated unified Markdown and HTML parity check returned matches before edits.
- After edits, generated unified Markdown and HTML parity still returned `parity ok`.
- After edits, no trailing whitespace was found in the new Markdown files.
- After edits, the only untracked files were `AGENTS.md`, `RELEASE_PROCESS.md`, and `RUNLOG.md`.

### Residual Risks

- GitHub metadata is snapshot data from 2026-05-23 and can become stale quickly.
- Business/product metadata needs API enrichment before it should be treated as comparable to AI/engineering metadata.
- There is no committed automated test suite or CI workflow for schema validation, generated-output parity, or HTML smoke checks.
- `graphify` was not installed in the current Python environment, so no persistent graph was built during this run.

### Recommended Next Slice

- Add a lightweight validation script that checks source schemas, unique repository identity, generated-output parity, and business/product metadata gaps.

## 2026-05-24 - Product Decision Layer

### Scope

- Strengthened the product layer with:
  - When to use the catalog.
  - When to avoid using the catalog as a decision source.
  - Stack recipes for common adoption scenarios.
  - Compare views for trade-off analysis.
- Made the guidance reusable through `scripts/product_guidance.py`.
- Added the layer to `README.md`, generated `UNIFIED_CATALOG.md`, and generated `UNIFIED_CATALOG.html`.
- Protected `README.md` as a curated product-facing guide by stopping `scripts/build_catalog.py` from overwriting it during base catalog regeneration.

### Product Analysis

- The existing catalog already had role-based navigation, but it did not clearly say when the catalog should be trusted, when it should not be used, or how to assemble category paths into real stacks.
- The most useful product frame is workflow-first: start from a decision scenario, choose a category path, then inspect repositories with source and freshness caveats.
- The main risk was generator drift: the checked-in README had been manually improved after the initial generator, while `build_catalog.py` still contained an older README writer.

### Files Changed

- `README.md`
- `UNIFIED_CATALOG.md`
- `UNIFIED_CATALOG.html`
- `AGENTS.md`
- `RELEASE_PROCESS.md`
- `scripts/product_guidance.py`
- `scripts/build_catalog.py`
- `scripts/build_unified_catalog.py`
- `scripts/build_catalog_html.py`

### Commands And Evidence

```powershell
python -m py_compile scripts\product_guidance.py scripts\build_catalog.py scripts\build_unified_catalog.py scripts\build_catalog_html.py
python scripts/build_catalog.py
python scripts/build_unified_catalog.py
python scripts/build_catalog_html.py
python -c "<in-memory unified Markdown and HTML parity check>"
rg -n "Product Decision Layer|When To Use|When To Avoid|Stack Recipes|Compare Views|Coding Agent Delivery Loop|RAG Knowledge Product" README.md UNIFIED_CATALOG.md UNIFIED_CATALOG.html scripts\product_guidance.py
node --check C:\tmp\catalog-script-check.js
python -c "<parse UNIFIED_CATALOG.html catalog-data and assert productGuidance counts>"
git -c core.excludesfile= status --short
```

Observed:

- Python compile check exited 0.
- Base catalog rebuild still produced 107 repositories and 17 base categories.
- Unified rebuild still produced 42 categories, 351 category placements, and 314 unique repositories.
- Generated-output parity returned `parity ok`.
- Product guidance is present in `README.md`, `UNIFIED_CATALOG.md`, `UNIFIED_CATALOG.html`, and `scripts/product_guidance.py`.
- HTML payload parse returned `html payload ok`.
- Embedded JS syntax check exited 0.

### Residual Risks

- This is a product/documentation and navigation improvement, not a metadata refresh.
- GitHub metadata remains a 2026-05-23 snapshot.
- Business/product rows still need API enrichment before their metadata quality is comparable to AI/engineering rows.

## 2026-05-24 - myAI-StackGuide Product Concept

### Scope

- Captured the product concept for a repository-selection-only assistant.
- Created `MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`.
- Clarified that the agent is an advisory guide, not a coding or implementation agent.

### Product Decision

- The agent should help users navigate a large repository library by understanding their project context, task, mood, constraints, and stage.
- The agent should recommend repository shelves, category paths, shortlists, compare views, and reading paths.
- The agent must not write code, scaffold projects, modify files, install tools, or claim implementation ownership.

### Key Concept

- The catalog is the library.
- Repositories are books.
- Categories and stack recipes are shelves and reading routes.
- The agent is the guide who helps the user choose what to inspect next.

### Files Changed

- `MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`
- `RUNLOG.md`

### Residual Risks

- The concept is intentionally product-level and does not yet define a concrete data schema migration, retrieval implementation, or evaluation harness.
- V1 can contain 1,000 repositories, but high-confidence primary recommendations still require advisory metadata and recommendation evals.

## 2026-05-24 - myAI-StackGuide Product Feature Set

### Scope

- Expanded `MYAI_STACKGUIDE_PRODUCT_CONCEPT.md` with a full product feature set for turning the guide into a usable product.
- Changed the first product version scope from a smaller prototype to **1,000 repositories across different categories**.
- Preserved the advisory-only boundary: the guide recommends, compares, warns, and exports decision artifacts, but does not write or modify user code.

### Product Decisions

- V1 should include 1,000 repositories, but recommendations should still expose `trust_level`, `verification_status`, source type, and freshness caveats.
- Not every V1 repository needs to be a high-confidence primary recommendation on day one.
- High-confidence recommendation pools should be promoted through curator review and recommendation evals.
- The product should be a decision workflow, not only a searchable catalog.

### Feature Areas Added

- Idea-to-repo path.
- Role-based shortlists.
- Compare workbench.
- Decision memo export.
- Avoid/defer lens.
- Stack recipe builder.
- Reading path generator.
- Saved decision boards.
- Watchlists and monthly reports.
- Evidence and freshness panel.
- On-demand current-state verification.
- Policy profiles.
- Curator review queue.
- Recommendation evals.
- Coverage map.
- Curated catalog API.
- myAI-StackGuide MCP.
- GitHub refresh connector.

### Residual Risks

- V1 scale creates quality risk unless repository cards, curator review, and eval scenarios are built before public positioning.
- Live verification will need rate-limit handling and read-only access discipline.
- The feature set is product-level; implementation sequencing still needs a separate plan.

## 2026-05-24 - myAI-StackGuide Context Scanner

### Scope

- Added `MYAI_STACKGUIDE_CONTEXT_SCANNER.md`.
- Captured the idea that users should be able to load the guide into their own product, repository, or workspace.
- Defined read-only project scanning as context acquisition for better recommendations, not implementation.
- Linked the embedded scanner design from `MYAI_STACKGUIDE_PRODUCT_CONCEPT.md` under "Embedded Mode And Project Context".

### Product Decisions

- The embedded guide should combine user conversation with project context scanning.
- The scanner should produce a Project Context Brief before repository recommendations.
- The product should support hosted GitHub read-only connection, uploaded archives, local CLI summaries, embedded SDK/widget context, and read-only MCP context providers.
- Recommendations should be grounded in detected stack, product surface, domain entities, integrations, maturity signals, and user goals.
- The advisory-only boundary remains unchanged: no code edits, dependency installs, migrations, pull requests, or implementation ownership.

### Risk Notes

- Private repository trust depends on clear permission screens, allowlist scanning, exclusions, redaction, and conservative retention.
- The scanner can infer the wrong product shape from partial context, so confidence and user correction need to be first-class.
- Non-technical users may treat recommendations as instructions, so outputs must end with decision questions rather than implementation steps.

## 2026-05-24 - V1 PRD And Roadmap

### Scope

- Added `PRODUCT_REQUIREMENTS.md`.
- Added `V1_ROADMAP.md`.
- Linked both documents from `README.md`.
- Linked both documents from `MYAI_STACKGUIDE_PRODUCT_CONCEPT.md` under "Version 1 Product Scope".

### Product Decision

- V1 primary entrypoint is **Hosted Web App + GitHub read-only connection**.
- V1 should connect to one GitHub repository, show scan permissions, run a read-only scanner, generate a Project Context Brief, ask a short user interview, and produce a repository recommendation memo.
- Uploaded archives, local CLI scanner, embeddable SDK/widget, public MCP server, enterprise policy profiles, and broad multi-provider support are post-V1 candidates.

### Requirements Notes

- V1 still targets 1,000 curated repositories across 60 to 90 categories.
- Repository recommendations must preserve the advisory-only boundary: no code edits, dependency installs, migrations, pull requests, or implementation ownership.
- Private repository trust depends on read-only GitHub permissions, explicit scan scope, sensitive-file exclusions, and deletion/retention controls.

### Residual Risks

- PRD and roadmap are product planning artifacts; they do not yet define concrete database schema, API contracts, UI wireframes, or implementation tasks.
- The next slice should create schemas for repository cards, scanner outputs, Project Context Briefs, recommendation memos, and eval scenarios.

## 2026-05-24 - Naming Update To myAI-StackGuide

### Scope

- Renamed the product from the working "Repository Archivist" concept to **myAI-StackGuide**.
- Renamed concept documents:
  - `REPOSITORY_ARCHIVIST_AGENT_CONCEPT.md` -> `MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`
  - `EMBEDDED_ARCHIVIST_CONTEXT_SCANNER.md` -> `MYAI_STACKGUIDE_CONTEXT_SCANNER.md`
- Updated README, AGENTS, PRD, roadmap, concept, scanner, and run log wording to use the new brand.
- Updated generated catalog titles through `scripts/build_unified_catalog.py` and `scripts/build_catalog_html.py`, then rebuilt `UNIFIED_CATALOG.md` and `UNIFIED_CATALOG.html`.

### Product Decision

- Company/brand line: myAI Labs.
- Product name: myAI-StackGuide.
- Repository slug: `myai-stackguide`.
- The product remains a context-aware open-source adoption advisor and does not become a coding agent.

### Rationale

- "Archivist" sounded too passive and implied storing or archiving old material.
- "StackGuide" better communicates forward motion, practical guidance, and helping users discover paths that accelerate product realization.
- The `myAI` prefix keeps the product aligned with myAI-Guide, myAI, myPartners, myDarkHistory, and myAgentOS.

### Commands And Evidence

```powershell
python -m py_compile scripts\build_unified_catalog.py scripts\build_catalog_html.py
python scripts\build_unified_catalog.py
python scripts\build_catalog_html.py
```

Observed:

- Unified catalog rebuild produced 42 categories, 351 category placements, and 314 unique repositories.
- HTML catalog rebuild produced 42 categories, 351 placements, and 314 unique repositories.

## 2026-08-05 - Product-Agent OS Control Plane And Agent Team

### Scope

- Added the missing root Product-Agent OS control-plane files: `REQUIREMENTS.md`, `PLAN.md`, `TEST.md`, and `EVALS.md`.
- Extended `AGENTS.md` with control-plane precedence, handoff, ownership, evidence, and no-silent-activation rules.
- Added `.codex/TEAM.md` and fresh-context/acceptance templates.
- Added seven project-scoped custom agents with disjoint ownership boundaries.
- Added eleven project skills and assigned exactly three enabled skills to every agent.
- Mapped the immediate V1 contract slice to repository card, taxonomy, scanner policy, Project Context Brief, recommendation memo, eval format, and later GitHub MCP permission review artifacts.

### Product-Agent OS Decisions

- Complexity profile is `standard-product` with `ai-product` and read-only integration constraints.
- Custom agents inherit the parent model; project files set reasoning effort but do not pin a model ID.
- Shared schemas, source data, generators, generated outputs, root control-plane files, and permission contracts use sequential handoff.
- GitHub MCP remains a planned read-only integration review. No MCP, hooks, automation, GitHub Actions, deployment, Agents SDK runner, or external writes were activated.
- `PRODUCT_REQUIREMENTS.md` remains the product PRD, `V1_ROADMAP.md` remains the milestone source, and the new root control-plane files own current execution routing and evidence.

### Commands And Evidence

```powershell
python C:\Users\user\.codex\plugins\cache\personal-product-agent-plugins\product-agent-os\0.1.0\scripts\validate_control_plane.py .
python C:\Users\user\.codex\plugins\cache\personal-product-agent-plugins\product-agent-os\0.1.0\scripts\validate_agents.py .codex\agents
codex --strict-config doctor --summary
git diff --check
rg -n "TODO|TBD|\?\?\?|\[TODO|\{project_name\}|\{workspace_path\}|\{generated_at\}" REQUIREMENTS.md PLAN.md TEST.md EVALS.md .codex
python -B -c "<in-memory unified Markdown and HTML parity check>"
python -B -c "<parse all agent TOML files and assert exactly three skills each>"
python -B - "<dependency-free skill frontmatter and metadata validation>"
```

Observed:

- Control-plane validator returned `ok: true` with no missing files.
- Agent validator returned `ok: true` for seven TOML files.
- Codex Doctor v0.146.0 returned 0 failures; it reported unrelated optional MCP environment-variable warnings from the loaded configuration.
- All seven agents parsed and contained exactly three `skills.config` entries.
- Placeholder search returned no matches.
- Dependency-free validation checked all eleven skills for frontmatter keys, names, descriptions, placeholders, and `$skill-name` metadata and passed.
- Generated-output parity returned `parity ok`.
- `git diff --check` reported no whitespace errors; it displayed existing LF-to-CRLF warnings for previously modified files.

### Verification Gap

- The bundled `skill-creator/scripts/quick_validate.py` could not run because both available Python runtimes lacked the `yaml` module. PyYAML was not installed because dependency installation was outside this slice. The equivalent local checks passed, but `CP-003` remains `partially_verified` until the official validator runs in an environment with PyYAML.

### Residual Risks

- Agent skill paths are absolute to this Windows workspace; moving or cloning the repository to another path requires rewriting those paths or adopting a verified portable path convention.
- Static validation does not prove subagent delegation behavior, GitHub authentication, MCP tool discovery, scanner privacy, recommendation quality, hosted runtime, or browser flows.

## 2026-08-05 - Official Codex Agent And Skill Remediation

### Changes

- Moved all eleven repository skills from `.codex/skills` to the official auto-discovery location `.agents/skills`.
- Removed workspace-absolute `skills.config` paths from all custom agents. Each agent now names exactly three assigned skills inside `developer_instructions`; `.codex/TEAM.md` remains the ownership map.
- Added `.codex/config.toml` with a three-agent concurrency cap, `gpt-5.6-sol/high` project baseline, and `gpt-5.6-terra/medium` unnamed-subagent baseline.
- Configured Product Planner, Catalog Architect, Pipeline Builder, Quality Evaluator, and Evidence Reviewer for Sol/high; configured GitHub Research Curator and Docs Maintainer for Terra/medium.
- Expanded every executable `developer_instructions` contract with role, sources, ownership, assigned skills, method, constraints, verification, output, and stop rules. Product-Agent OS metadata fields remain for its validator.
- Added GPT-5.6 model policy, agent/skill eval workflow, skill promotion record, deterministic contract tests, seven agent routing cases, and eleven skills with direct, indirect, incomplete, and non-trigger cases.
- Added repository Code Review Rules and updated handoff templates with model, reasoning, skill, and evidence-state fields.

### Official Guidance Applied

- Repository skills use `.agents/skills`; custom agents use `.codex/agents`; project runtime defaults use `.codex/config.toml`.
- GPT-5.6 migration is tier-aware rather than a global Sol replacement.
- Current reasoning effort is the baseline; one-lower comparisons are required before a durable downgrade.
- `xhigh`, `max`, Pro mode, persisted reasoning, Programmatic Tool Calling, and API multi-agent beta remain unconfigured pending measured need.

### Current Verification

```powershell
python -m unittest tests.test_codex_contracts -v
python C:\Users\user\.codex\plugins\cache\personal-product-agent-plugins\product-agent-os\0.1.0\scripts\validate_control_plane.py .
python C:\Users\user\.codex\plugins\cache\personal-product-agent-plugins\product-agent-os\0.1.0\scripts\validate_agents.py .codex\agents
codex --strict-config doctor --summary
git diff --check
python -c "<generated catalog in-memory parity check>"
```

- Contract tests: 5 passed.
- Product-Agent OS control-plane and seven-agent validators: `ok: true`.
- Codex Doctor 0.146.0: `15 ok`, `2 warn`, `0 fail`; warnings are optional existing MCP environment issues.
- Generated Markdown and HTML parity: `parity ok`.
- `git diff --check`: exit 0; existing LF-to-CRLF warnings remain for previously modified tracked files.
- Official `skill-creator/scripts/quick_validate.py` remains blocked because available Python runtimes do not include PyYAML. The dependency-free project tests cover the required frontmatter, naming, metadata, location, assignment, and activation-spec structure, but `CP-003` remains `partially_verified`.

### Evidence Boundary

- Static configuration and contract checks are verified.
- Skill implicit activation, custom-agent routing quality, and GPT-5.6 model suitability are `spec_present_not_model_run` / `configured_not_behaviorally_verified` until fresh-context behavioral comparisons run.
- No MCP, OAuth, hook, automation, GitHub Action, deployment, Agents SDK runner, external write, or Git operation was activated.
- A completed fresh-context packet is still required per task before parallel workers start.
- The working tree already contained user changes before this slice; no unrelated changes were reverted, staged, committed, or published.

### Next Action

- Start `V1-S1` and `V1-S2` sequentially with `catalog_architect`: define repository card and taxonomy contracts plus fixtures before scanner, recommendation, GitHub MCP, or hosted application implementation.

## 2026-08-30 - Public Repository Foundation And Reproducible HTML v5

### Scope And Owner Decision

- Created `alexroadcaster/myAI-StackGuide`, connected it as `origin`, and changed its visibility from private to public after explicit owner confirmation.
- The remote remains empty in this run: no push, tag, release, or pull request was authorized.
- The owner selected the source-first option for the first project-foundation commit: preserve the user-owned HTML v5 exactly while extracting reproducible source data and template inputs.

### Pipeline Changes

- Extracted the embedded v5 payload into canonical compact `data/catalog_manifest.json` and added `data/catalog_manifest.schema.json`.
- Extracted the standalone UI shell into `templates/unified_catalog.html` with one deterministic data marker.
- Replaced the legacy HTML builder with a manifest/template builder that validates schema version, required fields, summary counts, identities, categories, compatibility references, canonical JSON, and unsafe closing-script sequences.
- Moved generated HTML and Markdown ownership to `docs/UNIFIED_CATALOG.html` and `docs/UNIFIED_CATALOG.md`.
- Updated the legacy catalog builder to write methodology, contribution guidance, and license output under `docs/`.
- Updated README, release instructions, control-plane paths, tests, and source-of-truth documentation to distinguish the current 2026-08-12 HTML v5 snapshot from the dated 2026-05-23 Markdown/research boundary.

### Commands And Observed Evidence

```powershell
python scripts\build_catalog.py
python scripts\build_unified_catalog.py
python scripts\build_catalog_html.py
python scripts\build_catalog_html.py --check
python -m unittest discover -s tests -v
python C:\Users\user\.codex\plugins\cache\personal-product-agent-plugins\product-agent-os\0.1.0\scripts\validate_control_plane.py .
python C:\Users\user\.codex\plugins\cache\personal-product-agent-plugins\product-agent-os\0.1.0\scripts\validate_agents.py .codex\agents
git diff --check
```

- Current HTML source summary: schema `5.0-full-refresh`, snapshot `2026-08-12`, 1,142 canonical repositories, 77 categories, 1,290 placements, and 10 stack recipes.
- Exact HTML parity passed at 2,165,599 UTF-8 bytes with SHA-256 `8766e6d56a69e8a3a824269f1a7a624dcd71ff3b3608f094cd12557a74e446eb`.
- Legacy Markdown parity passed with 42 categories, 351 placements, and 314 unique repositories.
- Unit/contract tests: 14 passed.
- Product-Agent OS control-plane validator: `ok: true`; seven-agent validator: `ok: true`.
- README local-link check passed; manifest recursive secret-pattern scan and repository text secret-pattern scan found no token, private-key, or API-secret matches.
- `git diff --check`: exit 0 with existing LF-to-CRLF conversion warnings for modified tracked files.

### Residual Risks And Evidence Boundary

- The source snapshot preserves 18 legacy placement records across 14 unresolved repository keys. The builder reports this warning and the focused tests pin the observed count; resolving identities requires a separate source-backed data-quality slice.
- The optional external `jsonschema` package is unavailable in the current Python environment. The schema parses as JSON and the dependency-free builder/tests validate the owned contract and negative cases, but no third-party JSON Schema engine was run.
- Exact byte parity proves deterministic reconstruction of the checked-in HTML; it does not prove browser behavior, live GitHub freshness, security, legal suitability, recommendation quality, hosted runtime, or release readiness.
- Docs impact: updated. No product meaning, catalog records, or UI bytes were intentionally changed in this reproducibility slice.

## 2026-08-30 - README Product Positioning Rewrite

### Scope And Decisions

- Rewrote `README.md` around the product purpose: a context-aware advisor that helps users decide which existing open-source solutions to inspect, compare, adopt, defer, or avoid.
- Made the intended journey explicit: read-only project context, short user interview, Project Context Brief, catalog matching, shortlist, comparison, and an advisory decision memo or Integration Blueprint.
- Separated current evidence from planned capability. The reproducible catalog and project-scoped control plane exist now; the hosted scanner, GitHub OAuth flow, recommendation/interview runtime, MCP surface, and Agents SDK runtime remain planned.
- Preserved the advisory boundary: the product does not automatically edit code, install dependencies, create migrations, or replace security, legal, procurement, or engineering review.
- Updated stale current-state wording in `docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md` and `docs/PRODUCT_REQUIREMENTS.md` to distinguish the 2026-08-12 HTML v5 snapshot from the legacy 2026-05-23 boundary.

### Commands And Observed Evidence

```powershell
python -c "<README local-link check>"
python -c "<README claims versus data/catalog_manifest.json>"
python scripts\build_catalog_html.py --check
python -m unittest discover -s tests -v
python C:\Users\user\.codex\plugins\cache\personal-product-agent-plugins\product-agent-os\0.1.0\scripts\validate_control_plane.py .
git diff --check
```

- README local links: 17 checked; all targets exist.
- README snapshot and summary claims matched `data/catalog_manifest.json`.
- Exact HTML parity passed at 2,165,599 UTF-8 bytes with SHA-256 `8766e6d56a69e8a3a824269f1a7a624dcd71ff3b3608f094cd12557a74e446eb`.
- Unit/contract tests: 14 passed.
- Product-Agent OS control-plane validator: `ok: true`.
- `git diff --check`: exit 0 with LF-to-CRLF conversion warnings for the modified Markdown files.
- The first inline manifest-claim check was rejected by PowerShell parsing around a Python format expression; the simplified equivalent check then passed without changing files.

### Evidence Boundary

- This slice changes product documentation only. It does not implement or verify scanner behavior, GitHub authentication, interview orchestration, recommendations, MCP, an Agents SDK runtime, deployment, or live catalog freshness.
- No files were staged, committed, pushed, released, or published in this slice.
