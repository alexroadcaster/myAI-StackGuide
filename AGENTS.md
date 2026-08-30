# AGENTS.md

Project guidance for Codex App, CLI, IDE extension, subagents, skills, MCP, and other agentic contributors working in this repository.

## Project Identity

This repository is the durable product and catalog layer for **myAI-StackGuide**, a myAI Labs product for context-aware open-source stack guidance. It curates open-source GitHub repositories for agentic engineering, AI development infrastructure, and business/product operations.

Treat the catalog as a decision map, not as an "awesome list." The highest-value output is a trustworthy way to decide what to inspect, compare, adopt, ignore, or revisit.

The workspace parent directory also contains one-off GitHub account research artifacts. This repository is the durable product layer.

## Source Of Truth

- `data/catalog_manifest.json` is the source of truth for the current standalone HTML catalog; `data/catalog_manifest.schema.json` owns its stable top-level contract.
- `templates/unified_catalog.html` is the source of truth for the standalone HTML shell and UI.
- `data/source_repos.csv` is the source of truth for the legacy account fork catalog.
- `research/github_curated_recommendations_2026-05-23.json` is the dated source of truth for legacy AI/engineering expansion research.
- `research/github_business_curated_recommendations_2026-05-23.json` is the dated source of truth for legacy business/product expansion research.
- `scripts/*.py` define the reproducible generation pipeline.
- Curated product/control docs include `README.md`, `AGENTS.md`, `RUNLOG.md`, `docs/RELEASE_PROCESS.md`, `docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md`, `docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md`, `docs/PRODUCT_REQUIREMENTS.md`, and `docs/V1_ROADMAP.md`.
- Generated artifacts include `categories/*.md`, `data/repos.csv`, `data/repos.json`, `data/categories.json`, `docs/UNIFIED_CATALOG.md`, and `docs/UNIFIED_CATALOG.html`.

Do not hand-edit generated catalog outputs unless the task is explicitly editorial and the generation impact is understood. Prefer changing source data or scripts, then regenerating. Keep `README.md` product-facing and intentional; `scripts/build_catalog.py` must not overwrite it.

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
- Do not store secrets, tokens, private repository data, customer data, or credentials in prompts, fixtures, docs, examples, CSV, JSON, or logs.

## Change Workflow

1. Read `README.md`, `docs/METHODOLOGY.md`, `docs/RELEASE_PROCESS.md`, and the target source files before editing.
2. Classify the task: data update, taxonomy update, generation pipeline change, HTML UX change, research refresh, or release packaging.
3. Keep changes focused. Do not mix unrelated taxonomy, scoring, UI, and research-refresh changes in one pass.
4. If a repository is misclassified, prefer `PRIMARY_OVERRIDES` in `scripts/build_catalog.py` for stable known projects and keyword patterns for general rules.
5. Regenerate outputs after source or script changes.
6. Verify generated parity, inspect diffs, and update `RUNLOG.md` with decisions, commands, failures, and residual risks.

## Release Discipline

- Use `docs/RELEASE_PROCESS.md` for update and release steps.
- Every catalog snapshot should state the snapshot date and source artifacts used.
- Before publishing or presenting a release, identify stale-data risks and any lower-confidence source groups.
- Do not claim the catalog is current unless the relevant GitHub data was refreshed in the current run.

## Agent Collaboration

- Use subagents only for independent slices with clear file ownership, such as data-quality audit, taxonomy review, HTML UX review, or release notes.
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
