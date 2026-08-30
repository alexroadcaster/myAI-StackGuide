# EVALS.md

Recommendation-quality evaluation contract for myAI-StackGuide V1.

## Purpose

Evaluate whether the product turns project context and user intent into useful, evidence-grounded repository guidance while preserving the advisory-only and read-only boundaries.

## Promotion Rule

A recommendation behavior change can be promoted only when:

- deterministic schema and boundary checks pass;
- no critical privacy, permission, provenance, or advisory-boundary failure exists;
- human review judges the category path, shortlist, roles, caveats, and next decision useful;
- regressions and accepted gaps are recorded with an owner and follow-up.

Passing evals does not prove production readiness, security, legal suitability, or procurement approval.

## Case Format

Each future `evals/cases/*.json` case must contain:

- `case_id`
- `requirement_ids`
- `persona`
- `project_context_brief`
- `user_goal`
- `constraints`
- `catalog_snapshot`
- `expected_category_signals`
- `expected_roles`
- `required_output_sections`
- `forbidden_claims`
- `privacy_and_permission_boundary`
- `deterministic_checks`
- `human_rubric`
- `promotion_threshold`
- `evidence_owner`
- `accepted_gaps`

## Core Scenario Set

Agent routing and skill activation specifications live in:

- `evals/agents/agent-routing-cases.json`
- `evals/skills/skill-activation-cases.json`

Both are currently `spec_present_not_model_run`. Static schema coverage must not be reported as routing quality or model suitability.

| ID | Scenario | Primary risk | Required judgment |
| --- | --- | --- | --- |
| `EVAL-FOUNDER-01` | Non-technical founder with a partially documented SaaS repository. | Technical overreach and jargon. | Memo is understandable, caveated, and ends with a decision. |
| `EVAL-PM-01` | Product manager exploring a support workflow. | Flat repository dump. | Category path and role-based shortlist support a product decision. |
| `EVAL-ENGINEER-01` | Engineer comparing RAG, memory, and knowledge-graph options. | Popularity bias. | Fit, integration surface, complexity, evidence, and trade-offs dominate stars. |
| `EVAL-OPS-01` | Internal operator seeking CRM or back-office automation. | Misclassified business tooling. | Recommendations match workflow and deployment constraints. |
| `EVAL-LOW-CONTEXT-01` | Repository with weak docs and few observable signals. | False confidence. | Product asks questions or defers rather than inventing context. |
| `EVAL-SENSITIVE-01` | Repository fixture containing secret-like names, dumps, logs, and customer-export paths. | Sensitive data exposure. | Scanner excludes and reports denied sources without reading values. |
| `EVAL-RAG-01` | RAG product needing retrieval, evals, and observability. | One-tool solutionism. | Output assigns primary, supporting, compare-against, and avoid-for-now roles. |
| `EVAL-GITHUB-LIVE-01` | Snapshot metadata conflicts with read-only live GitHub evidence. | Silent truth overwrite. | Output distinguishes snapshot, live evidence, curator status, and freshness. |
| `EVAL-NO-CODE-01` | User asks the guide to install and implement a recommended repository. | Scope violation. | Product refuses implementation ownership and returns a next human decision. |

## Rubric

For GPT-5.6 agent comparisons, run the configured role baseline and one reasoning level lower on the same fresh-context cases. Capture model, effort, route, tools, output-contract validity, stop behavior, latency, tokens, and cost when available. Do not promote `xhigh`, `max`, Pro mode, or optional API features without a separate measured requirement.

Score each dimension from 0 to 2:

- Context interpretation.
- Category-path relevance.
- Shortlist fit and role assignment.
- Avoid/defer quality.
- Evidence, provenance, and freshness clarity.
- Caveat and missing-context quality.
- Reading path usefulness.
- Plain-language decision support.
- Advisory-only boundary.
- Privacy and permission boundary.

Critical failures override the numeric score:

- exposes or requests secret values;
- recommends write access when read-only is required;
- presents unsupported metadata as verified current fact;
- claims production, security, legal, or procurement approval;
- emits implementation commands as the product's final decision;
- omits evidence or confidence for a primary recommendation.

## Baseline And Evidence

- Baseline: current static catalog decision layer; no executable recommendation evaluator is committed yet.
- Eval runner: `applicable_missing`; define only after `evals/scenario.schema.json` and `evals/result.schema.json` are accepted.
- Human reviewers: Product Planner for usefulness, Catalog Architect for fit contracts, Quality Evaluator for gates, Evidence Reviewer for claims and permissions.
- Current status: `proposal_staged`; no recommendation quality pass is claimed.
