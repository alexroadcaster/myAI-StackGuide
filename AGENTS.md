# AGENTS.md

Project guidance for Codex App, CLI, IDE extension, subagents, skills, MCP, and other agentic contributors working in this repository.

## Project Identity

This repository is the durable product and catalog layer for **myAI-StackGuide**, a myAI Labs product for context-aware open-source stack guidance. It curates open-source GitHub repositories for agentic engineering, AI development infrastructure, and business/product operations.

Treat the catalog as a decision map, not as an "awesome list." The highest-value output is a trustworthy way to decide what to inspect, compare, adopt, ignore, or revisit.

The workspace parent directory also contains one-off GitHub account research artifacts. This repository is the durable product layer.

## Source Of Truth

- Conversation may follow the user's Russian language preference. Write and maintain active control-plane documents, plans, agent/skill instructions, schemas, and technical execution artifacts in English. Preserve canonical identifiers and quoted source text; retained historical sources are not active instructions.

- `data/catalog_manifest.json` is the source of truth for the current standalone HTML catalog; `data/catalog_manifest.schema.json` owns its stable top-level contract.
- `templates/unified_catalog.html` is the source of truth for the standalone HTML shell and UI.
- `data/source_repos.csv` is the source of truth for the legacy account fork catalog.
- `research/github_curated_recommendations_2026-05-23.json` is the dated source of truth for legacy AI/engineering expansion research.
- `research/github_business_curated_recommendations_2026-05-23.json` is the dated source of truth for legacy business/product expansion research.
- `scripts/*.py` define the reproducible generation pipeline.
- Curated product/control docs include `README.md`, `AGENTS.md`, `RUNLOG.md`, `docs/RELEASE_PROCESS.md`, `docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`, `docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md`, `docs/PRODUCT_REQUIREMENTS.md`, and `docs/V1_ROADMAP.md`.
- Generated artifacts include `categories/*.md`, `data/repos.csv`, `data/repos.json`, `data/categories.json`, `docs/UNIFIED_CATALOG.md`, and `docs/UNIFIED_CATALOG.html`.

Do not hand-edit generated catalog outputs unless the task is explicitly editorial and the generation impact is understood. Prefer changing source data or scripts, then regenerating. Keep `README.md` product-facing and intentional; `scripts/build_catalog.py` must not overwrite it.

## Local Plugin Contract Routing

- Read the accepted task and `docs/plan/plugin-v1-team-contracts.md`; state/rendering work also reads `specs/artifact/session-workspace-contract.md` and the linked eight-view design. Retrieval work reads `specs/retrieval/retrieval-policy.json` and assigned C9 contracts. Do not duplicate policy constants in instructions.
- Keep the public bundled SQLite FTS5 index separate from private canonical JSON session state. Codex owns answers, scanning and composition; the one offline desktop HTML displays validated state and copyable next actions.
- CP-07 owns the single state writer/publication boundary; CP-10 owns rendering and RU/EN presentation. Local generation within an authorized task is not external publication. English control documents do not prohibit RU/EN product content.
- Development agents/skills are not the shipped plugin runtime. CP-12-14 backend/MCP work is deferred and is not a local release prerequisite. Resolve already accepted contracts before declaring them missing.

## Change Sizing And Context Budget

Classify the requested change before loading broad context:

- **Micro:** one literal, limit, label, link or narrowly owned assertion changes without altering a contract shape or dependency.
- **Contract-value:** an accepted value changes across one owning source and its direct runtime, fixture, generated or documentation consumers, while the contract shape remains stable.
- **Structural:** keys, types, required fields, semantics, ownership, task dependencies, persistence, trust, release or public behavior change.

For micro and contract-value work, read `AGENTS.md`, the owning source and only the direct consumers found by targeted search. Do not read the full PRD, roadmap, PLAN, TEST, EVALS or RUNLOG merely because they mention the same value. Search RUNLOG by task, policy or evidence ID only when historical evidence is decision-relevant. Follow links to broader sources only when the change alters their owned meaning.

Use at most one primary skill for micro or contract-value work. Do not invoke `maintain-control-plane` unless active status, ownership, dependencies, acceptance or evidence claims materially change. Do not spawn subagents for these changes. Prefer a canonical link or machine-readable source over copied prose and do not add tests that only mirror a policy literal already validated at its owning boundary.

Before editing, if the expected compatibility unit exceeds eight files, two control-document families or one skill, state the concrete coupling that requires the expansion and choose the smallest coherent unit. Generated outputs and exact hash consumers count as one compatibility unit when their builder proves deterministic propagation.

## Policy And Schema Versioning

- Change `schema_version` only when keys, types, required fields or normative semantics change.
- Use `policy_revision` for numeric ceilings, weights and thresholds that change without changing the policy shape. Consumers bind the exact policy content with `policy_sha256` where trust or reproducibility requires it.
- Change `index_format_version` only when the serialized index representation or reader compatibility changes.
- Runtime, fixtures and tests should read policy values from the canonical policy or deterministic generated projection. Avoid duplicating policy constants in prose and assertion code when a reference or derived check is sufficient.
- When an older artifact uses `policy_version` as a compatibility pin, document whether it identifies the schema or the policy revision before changing the field. Do not silently reinterpret an existing pin.

## Build And Verification Commands

Run commands from this directory.

```powershell
python scripts/build_catalog.py
python scripts/build_unified_catalog.py
python scripts/build_catalog_html.py
```

After regeneration, inspect the diff.

```powershell
git -c core.excludesfile= status --short
git diff -- README.md docs data templates categories scripts tests
```

For generated-output parity without writing files, import the builders in Python and compare in-memory output to checked-in files.

```powershell
python scripts/build_catalog_html.py --check
python -c "import sys; from pathlib import Path; sys.dont_write_bytecode=True; root=Path.cwd(); sys.path.insert(0, str(root/'scripts')); import build_unified_catalog as u; c=u.load_categories(); u.load_repositories(c); assert u.build_markdown(c)==(root/'docs'/'UNIFIED_CATALOG.md').read_text(encoding='utf-8'); print('markdown parity ok')"
```

## Data Quality Rules

- Preserve upstream factual metadata. Do not invent stars, licenses, descriptions, update dates, owners, or URLs.
- Public GitHub stars and freshness are triage signals only. They are not endorsements, production-readiness claims, security reviews, or code-quality ratings.
- Treat HTML-scraped business/product data as lower-confidence than GitHub API data unless it has been enriched and rechecked.
- Add or keep notes about source type, freshness, and verification status when extending the schema.
- Do not disclose or persist secrets, credentials, unrelated private data or unnecessary customer information. Relevant task-authorized project context may inform Codex transiently within containment, exclusions and budgets; persist only minimized findings and sanitized answers. Do not archive raw source/chat in state or HTML or send private context to public catalog/index/remote evidence stores.

## Change Workflow

1. Classify the change size and task type, then read the owning source and direct consumers. Read `README.md`, `docs/METHODOLOGY.md` or `docs/RELEASE_PROCESS.md` only when product presentation, methodology or release behavior is in scope.
2. Classify the task surface: data update, taxonomy update, generation pipeline change, HTML UX change, research refresh, control-plane repair or release packaging.
3. Keep changes focused. Do not mix unrelated taxonomy, scoring, UI, and research-refresh changes in one pass.
4. Route current catalog taxonomy changes through `data/catalog_manifest.json` and its contract. Use `PRIMARY_OVERRIDES` in `scripts/build_catalog.py` only for the explicitly selected legacy fork-catalog pipeline; never substitute `data/categories.json` for the current taxonomy.
5. Regenerate outputs after source or script changes.
6. Verify the smallest affected boundary and inspect the focused diff. Append `RUNLOG.md` only for a durable decision, compatibility migration, material failure, residual risk, release evidence or lifecycle-status change; routine literal synchronization does not require a new entry.

## Verification Stop Rule

- For micro and contract-value work, run one targeted semantic or contract check and one parity or focused-diff check. Stop when both support the requested claim.
- Broaden verification only when changed executable code crosses another boundary, the targeted check finds a product defect, a new trust/persistence/compatibility/release risk appears, or a concrete review finding requires it.
- Record an unrelated tooling, ACL, dependency or environment failure once. Do not repair or repeatedly probe it unless the requested outcome depends on that gate.
- A failed command may justify one bounded repair and rerun of the affected check. It does not authorize a broad suite or repeated retry loop.

## Release Discipline

- Use `docs/RELEASE_PROCESS.md` for update and release steps.
- Every catalog snapshot should state the snapshot date and source artifacts used.
- Before publishing or presenting a release, identify stale-data risks and any lower-confidence source groups.
- Do not claim the catalog is current unless the relevant GitHub data was refreshed in the current run.

## Agent Collaboration

- Use subagents only for independent structural slices where parallel coverage materially exceeds coordination cost, with clear file ownership such as data-quality audit, taxonomy review, HTML UX review, or release notes. Do not use them for micro or contract-value changes.
- Handoffs must include sources read, assumptions, files touched or proposed, verification evidence, open risks, and recommended next action.
- `RUNLOG.md` is the durable memory for this project cycle. Keep it concise and factual.

## Product-Agent OS Control Plane

- Root control-plane files are `AGENTS.md`, `REQUIREMENTS.md`, `PLAN.md`, `TEST.md`, `EVALS.md`, and `RUNLOG.md`.
- `docs/PRODUCT_REQUIREMENTS.md` remains the V1 product PRD; `REQUIREMENTS.md` is the compact execution registry that maps current slices back to the PRD and roadmap.
- `docs/V1_ROADMAP.md` remains the milestone source; `PLAN.md` owns the active dependency order, file ownership, verification gates, and rollback notes.
- Project-scoped custom agents live in `.codex/agents/`; automatically discovered repository skills live in `.agents/skills/`; project runtime defaults live in `.codex/config.toml`; the team contract lives in `.codex/TEAM.md`.
- Before delegating, read `.codex/TEAM.md` and provide a completed `.codex/artifact-templates/agent-task-packet.md`; `TEAM.md` and templates are orchestration documents, not automatically loaded Codex instructions.
- Every subagent or parallel worker must receive a fresh-context packet based on `.codex/artifact-templates/agent-task-packet.md`. Raw conversation history is not a handoff.
- Parallel writes are allowed only when owned files and generated surfaces do not overlap. Use sequential handoff for shared schemas, source data, generators, and generated outputs.
- MCP, hooks, automation, external writes, GitHub Actions changes, deployment, and an Agents SDK runner are not activated by these files. Each requires an explicit, separately reviewed approval boundary.
- GitHub discovery and verification are read-only by default. Live GitHub evidence must remain distinct from catalog snapshots and curator-approved catalog entries.
- Completion claims require current command, eval, runtime, or owner evidence. Generated reports and dashboards are orientation artifacts, not proof.

## Code Review Rules

- Treat generated catalog files as consumers: verify the owning source data or builder before proposing a direct edit.
- Flag invented metadata, snapshot/live evidence conflation, unsupported readiness claims, missing provenance, and private-data or credential exposure.
- Require current parity or targeted test evidence for source, builder, schema, agent, skill, or generated-output changes.
- Treat static agent and skill validation as configuration evidence only; it does not prove routing quality, model suitability, runtime activation, or external integration behavior.
