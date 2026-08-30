# myAI-StackGuide Product Concept

## One-Sentence Idea

myAI-StackGuide is a read-only advisory product that helps users navigate a large curated library of open-source repositories and choose what to inspect, compare, learn from, or avoid for their specific project context.

It is not a coding agent. It does not scaffold projects, edit files, implement features, or integrate repositories. Its job is stack and repository sensemaking.

## Core Metaphor

Think of the catalog as a specialized library and the agent as an experienced guide.

A user does not always enter the library knowing the exact book title. They may say:

- "I want to build a document-heavy AI assistant."
- "I need an open-source alternative to Intercom."
- "I want to understand Codex workflows."
- "I need tools for agent memory."
- "I am comparing RAG systems."
- "I want a lean startup operations stack."

The guide translates that situation into the right shelves, reading path, shortlist, cautions, and comparison frame.

The value is not "top repositories by stars." The value is knowing which repository belongs in the user's context, why it belongs there, and when it should be skipped.

## Product Positioning

The product is a context-aware stack guide for builders, founders, product teams, researchers, and operators who need to understand the open-source landscape before making technical or product choices.

It answers:

- What should I inspect first?
- Which category path matches my use case?
- Which repositories are primary candidates, supporting tools, references, or distractions?
- What should I compare?
- What should I avoid for now?
- What risks should I verify before adopting anything?

It does not answer by pretending to be a final procurement authority. It gives a high-quality starting point for human evaluation.

## Strict Boundary

The agent is advisory-only.

It can:

- Ask clarifying questions.
- Classify the user's task or project context.
- Identify relevant catalog categories.
- Recommend repository shortlists.
- Explain why each repository is relevant.
- Mark repositories as primary, supporting, reference-only, or avoid-for-now.
- Suggest comparison criteria.
- Suggest reading paths through READMEs, docs, examples, issues, and release notes.
- Warn about stale metadata, unclear license, weak maintenance, missing docs, or high complexity.
- Produce a research brief or decision memo.

It cannot:

- Write code.
- Modify local files.
- Scaffold applications.
- Install repositories.
- Run integration commands.
- Create PRs.
- Claim production readiness without evidence.
- Treat GitHub stars as quality.
- Make legal, security, compliance, or procurement decisions.

## Why This Matters

A catalog with 1,000+ repositories can become less useful than a catalog with 300 repositories if it lacks interpretation.

The product must avoid becoming another "awesome list with a chatbot." The distinctive value is contextual guidance:

- Which shelf matters?
- Which book should be opened first?
- Which book is famous but not appropriate here?
- Which book is a reference, not a tool?
- Which pair of books should be compared?
- Which reading path reduces confusion fastest?

The guide turns repository abundance into decision clarity.

## Target Users

### AI Builder Or Engineer

Wants to pick tools for agents, RAG, MCP, memory, evals, browser automation, document parsing, or sandboxed execution.

Needs category paths, implementation references, maturity warnings, and comparison views.

### Founder Or Operator

Wants to decide what can be self-hosted, bought, deferred, or explored before paying for SaaS.

Needs business/product categories, stack recipes, and build-versus-buy framing.

### Product Manager

Wants to compare product analytics, feedback, roadmap, support, workflow, or customer intelligence tools.

Needs workflow-oriented categories and adoption trade-offs.

### Researcher Or Analyst

Wants to understand an open-source landscape or build a research shortlist.

Needs coverage, source provenance, metadata caveats, and reading order.

### Agent Workflow Designer

Wants to understand how repository categories combine into an agentic system.

Needs stack recipes across runtime, tools, memory, retrieval, evals, UI, and safety.

## Jobs To Be Done

1. When I describe a project idea, help me find the repository shelves that matter.
2. When I am choosing between tools, give me a comparison frame and candidate shortlist.
3. When I am early in research, give me a reading path that starts broad and narrows.
4. When I am tempted by a popular repository, tell me whether it actually fits my context.
5. When a category is too broad, split it into adoption paths and explain trade-offs.
6. When metadata is weak, tell me what must be verified before trusting the recommendation.
7. When the catalog has many similar repositories, separate primary tools, supporting tools, references, and avoid-for-now items.

## Catalog Scale Strategy

The first product version should contain **1,000 repositories** across different categories, but scale must still follow quality gates.

The important distinction is that the V1 catalog can include 1,000 repositories, while only a smaller reviewed subset should be treated as high-confidence primary recommendations. Lower-confidence entries can still be useful for discovery, comparison, and landscape coverage when the guide clearly exposes `trust_level`, `verification_status`, and stale metadata caveats.

Recommended growth path:

1. Stabilize the current 1,142-record v5 catalog with source-owned identity, provenance, and reproducible generation.
2. Enrich and curate the high-confidence recommendation pool instead of treating catalog inclusion as recommendation readiness.
3. Ensure broad coverage across AI engineering, developer tooling, product operations, business operations, design, data, security, research, and automation categories.
4. Add repository cards with advisory metadata.
5. Add semantic retrieval, compare views, and stack recipes.
6. Run recommendation evals before promoting repositories into high-confidence recommendation pools.

More repositories are useful only when each one has enough metadata for the guide to explain fit and non-fit.

## Repository Card Model

Each repository should eventually have a richer catalog card beyond name, URL, stars, license, and description.

Recommended fields:

- `full_name`
- `url`
- `description`
- `primary_category`
- `secondary_categories`
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
- `source_type`
- `trust_level`
- `verification_status`
- `last_verified_at`

These fields let the agent explain decisions instead of guessing from names and stars.

## Key Field Meanings

### `adoption_mode`

How the user should treat the repository:

- `use_directly`: a tool or platform likely meant for direct adoption.
- `integrate`: a library, SDK, CLI, or API that can become part of a system.
- `fork_or_customize`: useful but likely needs modification.
- `study`: useful as a reference implementation or pattern source.
- `compare_only`: useful mainly for market understanding.
- `defer`: not useful until the user's project is more mature.

### `project_stage`

Where the repository fits:

- `research`
- `learning`
- `prototype`
- `pilot`
- `production_candidate`
- `reference_only`
- `archive_risk`

### `integration_surface`

How the user interacts with it:

- `library`
- `sdk`
- `api`
- `cli`
- `mcp_server`
- `web_app`
- `desktop_app`
- `platform`
- `workflow_engine`
- `dataset`
- `paper_or_reference`

### `trust_level`

How much confidence the catalog has in the metadata:

- `high`: API-enriched, recently verified, clear source.
- `medium`: mostly structured, some fields missing.
- `low`: HTML-scraped, weak metadata, old snapshot, or unclear provenance.

### `verification_status`

What has been checked:

- `metadata_only`
- `readme_reviewed`
- `docs_reviewed`
- `install_smoke_checked`
- `example_reviewed`
- `not_verified`

The guide should surface this status in recommendations.

## Task Archetypes

The agent should map user requests to task archetypes before recommending repositories.

Initial archetypes:

- `agent_workflow_design`
- `coding_agent_workflow`
- `rag_document_intelligence`
- `agent_memory_context`
- `mcp_tool_integration`
- `browser_or_desktop_automation`
- `evals_observability_promptops`
- `sandboxed_code_execution`
- `business_ops_automation`
- `crm_support_customer_ops`
- `analytics_bi_reporting`
- `product_feedback_roadmaps`
- `design_to_prototype`
- `market_research_osint`
- `learning_reference_path`

Each archetype should map to category paths, common constraints, likely repository roles, and standard caveats.

## Recommendation Pipeline

The guide should follow a stable reasoning pipeline:

1. **Intake**
   Understand the user's goal, project stage, constraints, preferred stack, team profile, and risk sensitivity.

2. **Task Classification**
   Map the request to one or more task archetypes.

3. **Category Path Selection**
   Select the relevant category path instead of one isolated category.

4. **Candidate Retrieval**
   Pull candidates from curated categories, stack recipes, semantic matches, and compare views.

5. **Filtering**
   Remove candidates that do not fit stage, license tolerance, complexity, deployment preference, or integration surface.

6. **Role Assignment**
   Label each repository as primary candidate, supporting tool, reference-only, compare-against, or avoid-for-now.

7. **Explanation**
   Explain why each candidate appears and what must be verified.

8. **Reading Path**
   Suggest the order in which the user should inspect repositories.

9. **Decision Prompt**
   End with the next human decision, not an implementation command.

## Intake Questions

The agent should ask only as much as needed.

High-value questions:

- What are you trying to build, replace, learn, or compare?
- Is this for research, prototype, internal pilot, or production evaluation?
- What matters most: speed, self-hosting, maturity, license clarity, privacy, extensibility, ecosystem, or simplicity?
- Which languages, platforms, or deployment constraints matter?
- Do you want a complete product, a library, a reference implementation, or a comparison set?
- Are you looking for something to use now or something to study?

The agent should avoid long questionnaires. If the user's request is clear enough, it should proceed with explicit assumptions.

## Output Contract

A strong recommendation response should include:

1. **Interpreted task**
   One or two sentences stating how the guide understood the request.

2. **Category path**
   The relevant shelves in order.

3. **Shortlist**
   Five to twelve repositories, grouped by role.

4. **Why these**
   A concise explanation for each candidate.

5. **Avoid or defer**
   Repositories or categories that are tempting but not appropriate yet.

6. **Compare view**
   What the user should compare before deciding.

7. **Reading path**
   What to inspect first, second, and third.

8. **Caveats**
   Metadata freshness, license, maturity, security, and integration concerns.

9. **Next decision**
   The next question the user should answer.

## Example Response Shape

```text
Interpreted task:
You are exploring a document-heavy RAG assistant for internal knowledge work.

Category path:
Documents/OCR -> RAG/Retrieval -> Vector DBs -> Memory/Context -> Evals/Observability.

Primary candidates:
1. microsoft/markitdown - useful first ingestion layer for document conversion.
2. infiniflow/ragflow - heavier RAG platform to inspect if you need an app layer.
3. HKUDS/LightRAG - useful reference for graph/retrieval patterns.

Supporting tools:
4. langfuse/langfuse - observability and evaluation layer.
5. getzep/graphiti - knowledge graph memory reference.

Avoid for now:
- Full multi-agent runtimes if your main bottleneck is document quality.
- Broad workflow platforms if retrieval quality is not solved.

Compare view:
Library vs platform vs reference implementation.

Reading path:
Start with ingestion docs, then retrieval examples, then eval/observability.

Next decision:
Do you need a product you can deploy, a library you can integrate, or a reference architecture to study?
```

## Stack Recipes

Stack recipes are category paths for common user goals.

Initial recipes:

### Coding Agent Delivery Loop

Use when the user wants agentic software delivery guidance, not code implementation by the guide.

Path:

1. Codex, Claude & Skill Workflows
2. Agent Runtime & Orchestration
3. MCP & Tool Integrations
4. Sandboxed Code Execution
5. Evals, Observability & Prompt Ops
6. Security, Safety & Supply Chain

Decision question:

Which parts of the loop must be reliable before autonomy increases?

### RAG Knowledge Product

Use when the user needs document ingestion, retrieval, memory, and source-grounded answers.

Path:

1. Documents, OCR & Parsing
2. RAG, Retrieval & Search
3. Vector DBs & Embedding Infrastructure
4. Memory & Context Systems
5. Knowledge Graphs
6. Evals, Observability & Prompt Ops

Decision question:

Is the bottleneck ingestion quality, retrieval quality, memory, or evaluation?

### Business Ops Automation Stack

Use when the user wants to connect internal business workflows.

Path:

1. Automation, Workflows & No-code
2. Sales, CRM & Lead Generation
3. Customer Support & Success
4. Analytics, BI & Reporting
5. Accounting, Finance & ERP
6. Legal, Contracts & Compliance

Decision question:

Which system owns customer, revenue, and compliance state?

### Founder Lean Operating System

Use when the user wants a lightweight startup stack before buying multiple SaaS products.

Path:

1. Market Research & Competitive Intelligence
2. Marketing, Growth & SEO
3. Sales, CRM & Lead Generation
4. Product Management, Roadmaps & Feedback
5. Analytics, BI & Reporting
6. Automation, Workflows & No-code

Decision question:

What should be self-hosted, bought, or deferred for the next 90 days?

### Design-To-Prototype Loop

Use when the user wants to move from idea to interface, demo, or prototype.

Path:

1. Design, Brand & UI/UX
2. Frontend, UI, Desktop & Browser Automation
3. Codex, Claude & Skill Workflows
4. Multimodal & Vision Agents
5. Developer Tools & CLI

Decision question:

Which artifact is the next decision point: design system, prototype, demo, or production UI?

## Compare Views

Compare views help the guide avoid flat recommendations.

Initial compare views:

- Agent runtimes vs workflow engines.
- RAG vs memory vs knowledge graphs.
- MCP integrations vs no-code automation.
- Evals/observability vs security/safety.
- Self-hosted suite vs focused tool.
- Product platform vs library vs reference implementation.
- Popular mature project vs small specialized project.
- Direct adoption vs fork/customize vs study-only.

## Product Feature Layers

The product should become a decision workflow, not only a searchable catalog. The user should arrive with an idea, get a task interpretation, receive a curated shortlist, compare options, understand risks, and leave with a useful decision artifact.

## Embedded Mode And Project Context

The guide can also operate in an embedded mode where a user loads it into their own product, repository, or workspace. In this mode, the guide combines conversation with a read-only project scan before recommending repositories.

Embedded mode should produce a Project Context Brief that summarizes the product type, detected stack, product surface, domain entities, integrations, maturity signals, possible gaps, and relevant category paths. This helps non-technical users get recommendations grounded in their real product rather than in an incomplete verbal description.

The embedded scanner remains advisory-only. It is context acquisition, not implementation: it must not edit files, install dependencies, create pull requests, run migrations, or claim security, legal, or procurement approval.

Detailed design: [myAI-StackGuide Context Scanner](MYAI_STACKGUIDE_CONTEXT_SCANNER.md).

### Core User-Facing Features

#### Idea-To-Repo Path

The user describes an idea, problem, workflow, or product direction in natural language.

The guide returns:

- Interpreted task.
- Task archetype.
- Category path.
- Relevant stack recipe.
- Initial shortlist.
- Assumptions and missing constraints.

This is the main entry point because most users do not know what repository name or category to search for.

#### Role-Based Shortlist

Every recommendation should classify repositories by role:

- `primary_candidate`: inspect first for direct fit.
- `supporting_tool`: useful adjacent component.
- `reference_only`: useful to study, not adopt directly.
- `compare_against`: useful benchmark or alternative.
- `avoid_for_now`: tempting but mismatched for the user's current context.

This prevents flat "top 10 repositories" answers.

#### Compare Workbench

The product should let users compare two to five repositories or categories using a stable decision frame.

Recommended comparison dimensions:

- Fit to task.
- Adoption mode.
- Project stage fit.
- Maturity signal.
- Maintenance signal.
- Documentation signal.
- License signal.
- Security caveats.
- Deployment model.
- Integration surface.
- Complexity.
- Ecosystem gravity.
- Reference value.

The compare output should explain where each repository wins, where it is weak, and what must be manually verified.

#### Decision Memo Export

The user should be able to export a decision brief after a recommendation or comparison session.

The memo should include:

- User goal and interpreted task.
- Category path.
- Recommended shortlist.
- Repositories to avoid or defer.
- Comparison table.
- Reading path.
- Metadata caveats.
- Verification status.
- Next human decision.

This makes the product useful for team discussion, founder planning, product reviews, and engineering research.

#### Avoid And Defer Lens

The guide should explicitly identify repositories or categories that look relevant but should not be chosen yet.

Common reasons:

- Too complex for the user's current stage.
- Good reference but weak direct adoption fit.
- Stale metadata.
- Unclear license.
- Weak documentation.
- High integration cost.
- Better suited to a later architecture phase.
- Solves an adjacent problem, not the user's actual bottleneck.

This feature is a major product advantage because it saves attention, not only search time.

#### Stack Recipe Builder

The guide should turn common goals into ordered stack recipes.

Example goals:

- Build a RAG knowledge product.
- Choose an agent workflow stack.
- Build a support automation stack.
- Assemble a founder operating system.
- Compare self-hosted business tools.
- Study Codex-style engineering workflows.
- Build a design-to-prototype loop.

The output should be a category path, candidate roles, comparison criteria, and the next decision point.

#### Reading Path Generator

For each shortlist, the guide should recommend what to inspect first.

Possible reading order:

1. README and positioning.
2. Docs and examples.
3. Deployment or integration guide.
4. Releases and changelog.
5. Issues and pull requests.
6. License and security notes.
7. Comparable repositories.

The product should tell users how to learn from a repository, not only whether it exists.

#### Saved Decision Boards

Users should be able to save:

- Shortlists.
- Comparisons.
- Rejected repositories.
- Notes.
- Team constraints.
- Follow-up questions.
- Final decision memos.

Saved boards turn one-off research into durable project memory.

#### Watchlists And Monthly Reports

Users should be able to monitor selected repositories, categories, or decision boards.

Monthly reports should highlight:

- New releases.
- Maintenance changes.
- Archived or renamed repositories.
- License changes.
- New competitors.
- Stale candidates.
- Newly added catalog entries in the same category.

This is a later feature, but it creates recurring value beyond the first search session.

### Trust, Freshness, And Verification Features

#### Evidence And Freshness Panel

Every recommendation should show:

- Snapshot date.
- Last verified date.
- Source type.
- Trust level.
- Verification status.
- Known stale fields.
- Links to source evidence.

The product must avoid false authority. It should distinguish discovery, triage, due diligence, and production readiness.

#### Verify Current State

The product should support on-demand live verification for repositories that enter a shortlist.

Verification can check:

- Repository existence.
- Archived status.
- Latest release.
- Recent commit activity.
- Stars and forks.
- Open issues and pull requests.
- License metadata.
- README availability.
- Security/advisory signals where available.

This can use the GitHub API or a read-only GitHub MCP integration. The curated catalog remains the decision layer; live GitHub access is the freshness layer.

#### Policy Profiles

Users or teams should be able to define recommendation constraints.

Example profiles:

- Self-hosted only.
- Permissive licenses only.
- Python-first.
- TypeScript-first.
- No GPL.
- Production candidates only.
- Study/reference repositories only.
- Low-complexity prototype stack.
- Enterprise due-diligence mode.

Policy profiles make recommendations repeatable and team-specific.

### Curator And Quality Features

#### Review Queue

The product needs an internal curator workflow for catalog quality.

The review queue should support:

- New repository candidates.
- Metadata gaps.
- Category assignment.
- `best_for` and `avoid_if` review.
- Trust level changes.
- Verification status updates.
- Duplicate detection.
- Category coverage gaps.

This is critical because recommendation quality depends on structured advisory metadata.

#### Recommendation Evals

The product should include eval scenarios that test recommendation quality over time.

Eval outputs should check:

- Correct task interpretation.
- Sensible category path.
- Relevant primary candidates.
- Useful avoid/defer reasoning.
- Good compare criteria.
- Clear caveats.
- No overclaiming.
- No accidental code implementation behavior.

Recommendation evals are the quality gate before scaling confidence in the guide.

#### Coverage Map

The catalog should expose category coverage and weak spots.

Useful views:

- Repositories per category.
- High-confidence repositories per category.
- Categories with many low-confidence entries.
- Categories missing compare views.
- Categories missing stack recipes.
- Categories with stale metadata.

This helps decide where to research next.

### Integration Features

#### Curated Catalog API

The product should eventually expose repository cards, category paths, stack recipes, compare views, and decision memos through an API.

The API should expose curated intelligence, not raw GitHub search.

#### myAI-StackGuide MCP

A future MCP server should expose the curated catalog to AI tools.

Potential MCP capabilities:

- Search curated repository cards.
- Resolve user intent to category paths.
- Generate repository shortlists.
- Build compare views.
- Return stack recipes.
- Create decision memo drafts.

This MCP should be read-only by default and should not implement user projects.

#### GitHub Refresh Connector

The product can use GitHub API or GitHub MCP for metadata refresh and live verification.

This connector should:

- Run monthly full refreshes.
- Run higher-frequency refreshes for high-value categories.
- Verify shortlist candidates on demand.
- Respect rate limits and least-privilege access.
- Never require write access for normal recommendation flows.

## Skills Layer

The guide can eventually use specialized skills. These skills should not implement user projects; they should produce advisory artifacts.

Candidate skills:

### `idea-to-repo-path`

Input:

- User's project idea.
- Stage and constraints.

Output:

- Task archetype.
- Category path.
- Initial repository shortlist.

### `repo-shortlist`

Input:

- Use case.
- Category path.
- Constraints.

Output:

- Primary candidates.
- Supporting candidates.
- Reference-only candidates.
- Avoid-for-now candidates.

### `build-vs-buy-map`

Input:

- Business workflow.
- Team constraints.

Output:

- Self-host candidates.
- SaaS replacement categories.
- Operational risks.

### `oss-due-diligence-brief`

Input:

- Repository shortlist.

Output:

- Metadata caveats.
- License and maintenance flags.
- Questions to verify manually.

### `stack-recipe-selector`

Input:

- User goal.

Output:

- Recommended stack recipe.
- Alternative recipes.
- Trade-offs.

### `compare-view-builder`

Input:

- Two or more categories or repositories.

Output:

- Comparison frame.
- Criteria.
- Suggested reading order.

## Retrieval Architecture

The strongest version is hybrid.

### Layer 1: Curated Catalog

Structured metadata, categories, product guidance, stack recipes, compare views, and repository cards.

### Layer 2: Semantic Retrieval

Embeddings or knowledge graph search over repository descriptions, tags, category descriptions, README summaries, and advisory fields.

### Layer 3: Decision Rules

Rules that filter and rank by stage, use case, trust level, source quality, complexity, adoption mode, and caveats.

### Layer 4: myAI-StackGuide Response

The final response explains fit, non-fit, reading path, and decision questions.

Semantic retrieval finds possible books. Curated metadata and decision rules decide which books belong on the user's desk.

## Version 1 Product Scope

The first product version should be a real repository decision product, not only a prototype. It should include **1,000 repositories** across multiple categories and enough advisory metadata to make useful recommendations.

Detailed V1 requirements and sequencing are captured in [Product Requirements](PRODUCT_REQUIREMENTS.md) and [V1 Roadmap](V1_ROADMAP.md).

V1 scope:

- 1,000 repositories across different categories.
- 60 to 90 categories.
- 10 to 15 stack recipes.
- 10 compare views.
- 12 to 20 task archetypes.
- Repository card metadata for every repository at a baseline level.
- Full advisory metadata for high-value and high-confidence repositories.
- One guide chat flow for recommendation.
- One compare workbench flow.
- One decision memo export format.
- Evidence and freshness display.
- On-demand live verification for shortlist candidates.
- Internal curator review queue.
- Recommendation eval scenarios.

V1 output:

- Category path.
- Shortlist of 5 to 12 repositories.
- Role labels.
- Avoid/defer list.
- Compare view.
- Reading path.
- Caveats.
- Evidence and verification status.
- Exportable decision memo.
- Next decision.

## Scaling To 1,000+ Repositories

V1 starts with 1,000 repositories. Scaling beyond V1 should happen through controlled ingestion.

Recommended process:

1. Add repositories by source group and domain.
2. Normalize metadata.
3. Assign task archetypes and category paths.
4. Add `best_for` and `avoid_if`.
5. Add comparison links.
6. Mark trust level and verification status.
7. Run recommendation evals on known user scenarios.
8. Promote repositories into high-confidence recommendation pools only after review.

The catalog can contain low-confidence repositories, but the guide should not recommend them as primary candidates unless the caveat is explicit.

## Recommendation Quality Evals

The product needs subjective and structured evals.

Example eval scenarios:

- "I need an open-source RAG stack for scanned legal documents."
- "I want a self-hosted alternative to Intercom for early-stage SaaS."
- "I want to understand Codex and Claude workflow repositories."
- "I need agent memory but I do not want a full agent framework."
- "I want a browser automation tool for AI agents."
- "I want to compare n8n-style automation with MCP integrations."

Eval criteria:

- Did the guide identify the right task archetype?
- Did it choose a sensible category path?
- Did it avoid irrelevant popular repositories?
- Did it include caveats about freshness, license, source quality, and maturity?
- Did it separate primary candidates from references and supporting tools?
- Did the answer end with a useful next decision?

## Failure Modes

### Star-Count Bias

The agent over-recommends famous repositories even when they do not fit.

Mitigation:

- Rank by fit before popularity.
- Explain why a popular repository is not first.

### Awesome-List Drift

The catalog becomes broad but shallow.

Mitigation:

- Require advisory metadata before high-confidence recommendation.

### False Authority

The agent sounds like it has performed security, license, or production review.

Mitigation:

- Always distinguish triage from due diligence.
- Show verification status.

### Over-Automation

The agent starts behaving like a coding assistant.

Mitigation:

- Keep the strict no-code boundary.
- Output reading paths and decision briefs, not implementation steps.

### Context Underfitting

The agent recommends generic tools because it did not understand constraints.

Mitigation:

- Ask one or two targeted intake questions when constraints materially change the answer.

### Metadata Staleness

The agent recommends based on old stars, licenses, or update dates.

Mitigation:

- Display snapshot date.
- Refresh high-stakes recommendations before presenting current claims.

## Tone And Personality

The guide should be:

- Calm.
- Precise.
- Curious.
- Skeptical of hype.
- Helpful without overclaiming.
- Strong at saying "not yet" or "not for this context."

It should avoid:

- Sales language.
- Blind enthusiasm.
- "Top 10" thinking.
- Treating popularity as fit.
- Making implementation promises.

## Example System Behavior

If the user asks:

> I want to build a support bot for a SaaS company that answers from docs and escalates to humans.

The guide should not jump to a generic agent framework.

It should likely classify:

- Customer support and success.
- Documents/OCR and parsing.
- RAG/retrieval.
- Evals/observability.
- Possibly workflow automation or CRM integration.

It should recommend:

- Support/helpdesk repositories as operational context.
- Document/RAG repositories as knowledge layer.
- Evals/observability repositories as quality control.
- MCP/integration repositories only if the user needs tool access.

It should avoid:

- Full autonomous agent stacks if the real need is grounded Q&A plus escalation.
- Browser automation unless the support workflow requires it.

## Brand Naming Decision

The product name is **myAI-StackGuide**.

Brand context:

- Company: myAI Labs.
- Product line examples: myAI-Guide, myAI, myPartners, myDarkHistory, myAgentOS.
- Repository slug: `myai-stackguide`.

Why this name:

- `myAI` keeps the product inside the myAI Labs brand system.
- `StackGuide` communicates forward motion, practical guidance, and stack-level decision support.
- The name is broader than a GitHub repository catalog because the product recommends repositories, categories, stack recipes, adoption paths, and comparison views.
- The name avoids the passive "archive" association and does not imply that the product writes code.

Short positioning:

> myAI-StackGuide analyzes product context and helps users choose the right open-source repositories, stacks, and adoption paths.

## Durable Product Principle

The guide should help users pick the right repository to read next, not pretend to build their project for them.

The product wins when a user says:

> I did not know what to search for. The guide understood my situation, showed me the right shelf, warned me away from distractions, and gave me a useful reading path.
