# myAI-StackGuide Agent Team

Project-scoped team design for the current Product-Agent OS lifecycle. Codex loads `.codex/agents/*.toml`; repository skills are auto-discovered from `.agents/skills`. This file documents orchestration and must be read explicitly before delegation. It does not auto-dispatch workers or activate external systems.

## Team

Read `docs/plan/plugin-v1-team-contracts.md` for current sources, implementation loops, state/candidate boundaries, and methodology gates. The active task packet selects the relevant sections; it must not depend on raw conversation history. Builder definitions are preparation only until CP-02/03 and routing gates close.

| Agent | Primary responsibility | Write ownership | Assigned project skills |
| --- | --- | --- | --- |
| `product_planner` | Scope, value, requirements, metrics, and active sequence | `REQUIREMENTS.md`, `PLAN.md`, product acceptance sections explicitly assigned by task | `shape-product-slice`, `design-recommendation-evals`, `maintain-control-plane` |
| `catalog_architect` | Catalog, scanner, context, memo, provenance, and permission contracts | `specs/**` | `design-catalog-contracts`, `design-context-contracts`, `audit-readonly-boundaries` |
| `github_research_curator` | GitHub landscape discovery, source qualification, and taxonomy proposals | New task-owned files under `research/**`; no generated outputs | `research-github-candidates`, `curate-catalog-taxonomy`, `review-advisory-evidence` |
| `catalog_pipeline_builder` | Source-first catalog generators and focused implementation | Assigned files under `scripts/**`; generated outputs only in a sequential regeneration step | `evolve-catalog-pipeline`, `verify-generated-parity`, `design-catalog-contracts` |
| `quality_evaluator` | Contract tests, scanner boundary tests, recommendation evals, and failure evidence | `TEST.md`, `EVALS.md`, `tests/**`, `evals/**` when assigned | `design-recommendation-evals`, `verify-generated-parity`, `audit-readonly-boundaries` |
| `evidence_reviewer` | Independent claim, provenance, permission, and regression review | Read-only | `review-advisory-evidence`, `audit-readonly-boundaries`, `verify-generated-parity` |
| `docs_maintainer` | RUNLOG, source-backed docs, decision trace, and handoff closure | `RUNLOG.md` and explicitly assigned curated docs; not product requirements meaning | `maintain-control-plane`, `review-advisory-evidence`, `curate-catalog-taxonomy` |
| `plugin_runtime_builder` | Local plugin intake, scanner, state, matching, and offline report | Exact assigned files under `plugins/myai-stackguide/`; unit tests only by explicit packet assignment | `build-stackguide-plugin`, `design-context-contracts`, `audit-readonly-boundaries` |
| `mcp_backend_builder` | Own-backend MCP tools and candidate ledger | Exact backend and test paths accepted in CP-02; never the plugin bundle or current catalog | `build-stackguide-mcp`, `design-catalog-contracts`, `audit-readonly-boundaries`, `design-recommendation-evals` |

## Methodology Ownership

- Product Planner owns product hypothesis, scope, acceptance, metric classification, and accepted-gap routing.
- Catalog Architect owns architecture boundaries, shared identifiers, schema compatibility, provenance, and rollback design.
- GitHub Research Curator owns source qualification and must label snapshot, live, community, inferred, and unverified evidence distinctly.
- Catalog Pipeline Builder owns implementation only after a task packet names exact source files, generated surfaces, and verification commands.
- Quality Evaluator owns the evidence gate and does not convert failed checks into passing claims.
- Evidence Reviewer can block promotion but does not implement fixes.
- Docs Maintainer records observed evidence and unsupported claims without changing product decisions independently.

## Parallelism Rules

Safe in parallel:

- Read-only GitHub research in separate query/source slices.
- Read-only evidence review while another agent works on disjoint files.
- Test or eval case authoring when it does not edit the schema being implemented.

Sequential only:

- Shared JSON/YAML schemas and their fixtures.
- `data/source_repos.csv`, research promotion, and generator changes.
- `scripts/**` changes followed by regeneration of `data/**`, `categories/**`, `docs/UNIFIED_CATALOG.md`, or `docs/UNIFIED_CATALOG.html`.
- Root control-plane files, public documentation, release artifacts, or any permission contract.

Maximum configured fan-out is three spawned workers, excluding the primary session, and only when every worker has a completed task packet and disjoint ownership. Use fewer workers when shared files or handoff overhead dominate. Skill assignment has no numerical quota: select the smallest relevant set.

## Fresh-Context Handoff

Before a subagent starts, copy and complete `.codex/artifact-templates/agent-task-packet.md`. The packet must be sufficient without raw chat history and must include:

- task ID and lifecycle state;
- goal, requirements, acceptance criteria, and architecture boundary;
- allowed sources and inputs used;
- owned, out-of-scope, and forbidden files;
- commands and expected evidence;
- docs path, rollback, approval requirements, and accepted gaps;
- stop conditions and sequential fallback;
- output schema for files touched, commands, evidence, unsupported claims, risks, and next role.

## Universal Stop Conditions

- Ownership or expected evidence is missing.
- Another worker owns the same file, schema, source, generated artifact, or release surface.
- The task needs credentials, private data, external writes, MCP activation, hooks, automation, deployment, Git history changes, or provider calls without explicit approval.
- A source claim cannot be verified or is stale enough to change the decision.
- A command fails outside the declared expected-RED assertion, or an in-scope repair would require changing acceptance, shared ownership, permissions, or another owner's files. The assigned owner may fix ordinary local failures and rerun the targeted check; never treat an unexpected environment/import failure as expected RED.
- Sensitive content would enter prompts, fixtures, docs, logs, or public catalog data.
- The worker would need raw conversation history instead of a fresh-context packet.

## Model And Reasoning Policy

- Use `gpt-5.6-sol` with `high` reasoning for product trade-offs, architecture, implementation, tests, evidence review, and privacy boundaries.
- Use `gpt-5.6-terra` with `medium` reasoning for bounded GitHub research and documentation maintenance.
- Use Terra/medium for unnamed subagents; named agent files override the default by role.
- Preserve the configured effort as the baseline and compare it with one level lower on the same representative cases before changing a durable default.
- Do not use `xhigh`, `max`, Pro mode, persisted reasoning, Programmatic Tool Calling, or API multi-agent beta without measured need and a separate approval boundary.
- Escalate to the parent when uncertainty affects scope, permissions, shared contracts, security, or irreversible decisions.
- Downgrade only for mechanical formatting or deterministic command execution after the semantic decision is settled.

See `.codex/model-reasoning-policy.md`. Current model suitability is `configured_not_behaviorally_verified` until the behavioral workflow in `.codex/agent-eval-workflow.md` runs.

## Activation Boundary

Custom agents and skills are available for manual or parent-agent delegation. This team definition does not start agents, configure GitHub MCP, enable hooks, create automations, run an Agents SDK application, modify GitHub Actions, or perform external writes.
