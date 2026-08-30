# myAI-StackGuide

myAI-StackGuide is a myAI Labs product for context-aware open-source stack guidance.

It helps people connect a product or project context to the right open-source repositories, stack recipes, comparison views, and adoption paths.

This repository started as an analysis of a personal GitHub fork collection and grew into a broader landscape catalog. It now combines agentic engineering tools, AI development infrastructure, and business/product operations software into one navigable reference for the myAI-StackGuide product.

The goal is practical: help people in different roles quickly find relevant repositories, understand where they fit, compare options, avoid distractions, and decide what to inspect next.

## What Is Inside

- A current HTML v5 catalog with 77 categories, 1,290 category placements, and 1,142 canonical repositories.
- A standalone interactive artifact with navigation, search, filters, decision views, stack recipes, and repository tables.
- A source-owned `data/catalog_manifest.json` that reproduces the HTML artifact exactly.
- A legacy Markdown snapshot with 42 categories, 351 category placements, and 314 accepted repositories.
- CSV and JSON data files for analysis, automation, or import into other tools.
- Research snapshots for AI/engineering repositories and business/product repositories.
- Category pages generated from the original fork collection.

## Start Here

- [Interactive HTML catalog](docs/UNIFIED_CATALOG.html)
- [Legacy Markdown catalog](docs/UNIFIED_CATALOG.md)
- [myAI-StackGuide product concept](docs/MYAI_STACKGUIDE_PRODUCT_CONCEPT.md)
- [myAI-StackGuide context scanner](docs/MYAI_STACKGUIDE_CONTEXT_SCANNER.md)
- [Product requirements](docs/PRODUCT_REQUIREMENTS.md)
- [V1 roadmap](docs/V1_ROADMAP.md)
- Product decision layer: when to use, when to avoid, stack recipes, and compare views are included below and in the HTML catalog.
- [Methodology](docs/METHODOLOGY.md)
- [Contributing guide](docs/CONTRIBUTING.md)

The HTML file is self-contained. Download or open it locally to use the interactive search and filters.

## Snapshot

| Area | Count |
|---|---:|
| HTML v5 categories | 77 |
| HTML v5 category placements | 1,290 |
| HTML v5 canonical repositories | 1,142 |
| Accepted repositories | 314 |
| Candidate repositories | 813 |
| Reference or benchmark repositories | 15 |
| Original fork catalog repositories | 107 |
| Source research snapshots | 3 |

Current HTML snapshot date: 2026-08-12. The legacy Markdown and dated research inputs retain their 2026-05-23 snapshot boundary.

## Main Category Groups

### AI And Agentic Engineering

For people building AI products, coding agents, RAG systems, memory layers, eval pipelines, and tool-using agents.

Examples:

- Agent Runtime & Orchestration
- Codex, Claude & Skill Workflows
- MCP & Tool Integrations
- RAG, Retrieval & Search
- Memory & Context Systems
- Evals, Observability & Prompt Ops
- Sandboxed Code Execution
- Voice & Realtime Agents
- Multimodal & Vision Agents

### Engineering Platform

For teams that need infrastructure around AI-assisted software delivery.

Examples:

- Developer Tools & CLI
- Frontend, UI, Desktop & Browser Automation
- Cloudflare, Edge & Backend
- Databases, Storage & SQLite
- Documents, OCR & Parsing
- Security, Safety & Supply Chain
- Web Crawling & Data Ingestion
- Workflow State Machines & Durable Agents

### Business And Product Operations

For non-engineering and cross-functional teams using AI to accelerate real business work.

Examples:

- Marketing, Growth & SEO
- Design, Brand & UI/UX
- Sales, CRM & Lead Generation
- Fundraising, Investor Relations & Startup Ops
- Accounting, Finance & ERP
- Legal, Contracts & Compliance
- Analytics, BI & Reporting
- Customer Support & Success
- Product Management, Roadmaps & Feedback
- E-commerce, Payments & Revenue
- HR, Recruiting & People Ops
- Operations, Project Management & Internal Tools
- Automation, Workflows & No-code
- Market Research & Competitive Intelligence

## Product Decision Layer

Use the catalog as a decision aid: start from the work you need to do, narrow to the right category path, then inspect repositories with their caveats in mind.

### When To Use

| Situation | Start with | Decision output |
|---|---|---|
| You need a shortlist before choosing an AI or automation stack. | Search by workflow, then inspect the matching category and top repositories. | A focused list of projects to read, prototype, or compare. |
| You are deciding what to self-host, buy, fork, or ignore. | Use the business/product categories alongside engineering platform categories. | A decision map for build-versus-buy and adoption planning. |
| You are designing an agentic workflow and need adjacent components. | Move across runtime, tools, memory, retrieval, evals, execution, and UI categories. | A stack-shaped view instead of isolated repository bookmarks. |
| You are auditing a personal fork library or research queue. | Use source groups, scores, categories, and stale metadata caveats. | A cleaner queue of active candidates, references, and archive/delete items. |

### When To Avoid

| Need | Why this catalog is not enough | Better next step |
|---|---|---|
| Security, compliance, legal, or procurement approval. | The catalog is not a security audit, license opinion, vendor review, or production-readiness certification. | Run dedicated code, security, license, and vendor due diligence. |
| Realtime repository rankings. | Stars, forks, update timestamps, and licenses are snapshot metadata and drift quickly. | Refresh from the GitHub API before presenting current claims. |
| An exhaustive market map. | The catalog is curated for practical decision support, not complete market coverage. | Run a scoped research refresh with explicit search queries and inclusion rules. |
| A direct product recommendation for a high-stakes adoption. | Scores are triage signals and are not comparable to hands-on evaluation in your environment. | Prototype the top candidates against your workload, data, permissions, and failure modes. |

### Stack Recipes

| Recipe | Use when | Category path | Decision question |
|---|---|---|---|
| Coding Agent Delivery Loop | You want agents to plan, edit, run tools, evaluate changes, and ship safely. | Codex, Claude & Skill Workflows -> Agent Runtime & Orchestration -> MCP & Tool Integrations -> Sandboxed Code Execution -> Evals, Observability & Prompt Ops -> Security, Safety & Supply Chain | Which parts of the loop must be reliable before autonomy increases? |
| RAG Knowledge Product | You need a product that reads documents, retrieves context, remembers decisions, and cites sources. | Documents, OCR & Parsing -> RAG, Retrieval & Search -> Vector DBs & Embedding Infrastructure -> Memory & Context Systems -> Knowledge Graphs -> Evals, Observability & Prompt Ops | Is the bottleneck ingestion quality, retrieval quality, memory, or evaluation? |
| Business Ops Automation Stack | You want to connect internal workflows across leads, support, reporting, and back office. | Automation, Workflows & No-code -> Sales, CRM & Lead Generation -> Customer Support & Success -> Analytics, BI & Reporting -> Accounting, Finance & ERP -> Legal, Contracts & Compliance | Which system owns customer, revenue, and compliance state? |
| Founder Lean Operating System | You need a lightweight startup stack before buying multiple SaaS products. | Market Research & Competitive Intelligence -> Marketing, Growth & SEO -> Sales, CRM & Lead Generation -> Product Management, Roadmaps & Feedback -> Analytics, BI & Reporting -> Automation, Workflows & No-code | What should be self-hosted, bought, or deferred for the next 90 days? |
| Design-To-Prototype Loop | You want to move from product idea to interface, demo, or user-testable prototype. | Design, Brand & UI/UX -> Frontend, UI, Desktop & Browser Automation -> Codex, Claude & Skill Workflows -> Multimodal & Vision Agents -> Developer Tools & CLI | Which artifact is the next decision point: design system, prototype, demo, or production UI? |

### Compare Views

| Compare | Use this view to decide | Categories |
|---|---|---|
| Agent runtimes vs workflow engines | Whether you need autonomous agent behavior, deterministic orchestration, or both. | Agent Runtime & Orchestration -> Workflow State Machines & Durable Agents |
| RAG vs memory vs knowledge graphs | Whether the problem is retrieval, long-lived context, entity relationships, or source-grounded answers. | RAG, Retrieval & Search -> Memory & Context Systems -> Knowledge Graphs |
| MCP integrations vs no-code automation | Whether agents need programmable tool access or business teams need workflow automation. | MCP & Tool Integrations -> Automation, Workflows & No-code |
| Evals/observability vs security/safety | Whether the immediate risk is quality drift, prompt behavior, unsafe execution, or supply-chain exposure. | Evals, Observability & Prompt Ops -> Security, Safety & Supply Chain |
| Self-hosted suite vs focused tool | Whether to adopt a broad operating platform or combine narrow tools around one workflow. | Operations, Project Management & Internal Tools -> Analytics, BI & Reporting -> Customer Support & Success |

## How This Helps Different Roles

### Founder Or CEO

Use the catalog to map what can be built, automated, or self-hosted before buying another SaaS tool.

Example workflows:

- Compare open-source CRM, analytics, support, and finance options before selecting a startup stack.
- Find fundraising and investor-relations tools for cap tables, research, donations, or investor analysis.
- Identify AI agent platforms that can automate internal research, reporting, or operations.
- Build a shortlist for "what should we self-host, buy, or ignore?"

Useful entry points:

- Marketing, Growth & SEO
- Sales, CRM & Lead Generation
- Fundraising, Investor Relations & Startup Ops
- Accounting, Finance & ERP
- Automation, Workflows & No-code

### Product Manager

Use the catalog to discover tools for feedback, analytics, roadmaps, experimentation, and customer understanding.

Example workflows:

- Search for "feedback", "roadmap", "analytics", or "feature flags".
- Compare product analytics tools with BI and reporting tools.
- Find repositories that support AI-powered discovery, summarization, or workflow automation.
- Build a product ops stack around customer feedback, metrics, and changelogs.

Useful entry points:

- Product Management, Roadmaps & Feedback
- Analytics, BI & Reporting
- Marketing, Growth & SEO
- Customer Support & Success
- Evals, Observability & Prompt Ops

### Engineer Or AI Builder

Use the catalog as a decision map for agent architecture and implementation choices.

Example workflows:

- Search for "RAG", "memory", "MCP", "sandbox", "evals", "workflow", or "vector database".
- Compare agent orchestration frameworks before starting a prototype.
- Find tools for code execution, browser automation, document parsing, and secure sandboxing.
- Build a reference stack for AI agents that can read documents, call tools, browse the web, and run code.

Useful entry points:

- Agent Runtime & Orchestration
- MCP & Tool Integrations
- RAG, Retrieval & Search
- Memory & Context Systems
- Sandboxed Code Execution
- Developer Tools & CLI

### Designer Or Creative Technologist

Use the catalog to find tools for design systems, whiteboards, UI generation, prototyping, and AI-assisted design workflows.

Example workflows:

- Search for "design", "whiteboard", "prototype", "UI", or "components".
- Compare open-source design and diagramming tools.
- Find repositories that help turn prompts into interfaces or design artifacts.
- Combine design tools with frontend, browser automation, and AI coding workflows.

Useful entry points:

- Design, Brand & UI/UX
- Frontend, UI, Desktop & Browser Automation
- Codex, Claude & Skill Workflows
- Multimodal & Vision Agents

### Marketing Or Growth Lead

Use the catalog to assemble an AI-friendly growth stack with analytics, SEO, content, campaigns, and automation.

Example workflows:

- Search for "SEO", "analytics", "campaign", "newsletter", or "social".
- Compare privacy-first analytics tools and product analytics platforms.
- Find content and community platforms that can be paired with AI content workflows.
- Use workflow automation tools to connect lead capture, CRM, reporting, and notifications.

Useful entry points:

- Marketing, Growth & SEO
- Content, Social & Community
- Analytics, BI & Reporting
- Automation, Workflows & No-code
- Market Research & Competitive Intelligence

### Sales, Support, And Customer Success

Use the catalog to find systems for CRM, helpdesk, live chat, ticketing, and customer workflow automation.

Example workflows:

- Search for "CRM", "helpdesk", "ticket", "support", or "live chat".
- Compare open-source alternatives to Salesforce, Intercom, Zendesk, or Help Scout.
- Connect support systems with AI summarization, routing, and internal knowledge tools.
- Build a customer operations stack before committing to expensive enterprise software.

Useful entry points:

- Sales, CRM & Lead Generation
- Customer Support & Success
- Product Management, Roadmaps & Feedback
- Automation, Workflows & No-code

### Finance, Legal, And Operations

Use the catalog to discover tools for accounting, invoicing, ERP, document signing, compliance, and operational automation.

Example workflows:

- Search for "invoice", "ERP", "accounting", "contract", "signature", or "compliance".
- Find open-source tools for finance back office and lightweight operations.
- Pair document signing or compliance tools with AI document parsing and workflow automation.
- Build an internal operating system around finance, legal, support, and project management.

Useful entry points:

- Accounting, Finance & ERP
- Legal, Contracts & Compliance
- Operations, Project Management & Internal Tools
- Documents, OCR & Parsing
- Workflow State Machines & Durable Agents

### Researcher, Analyst, Or Educator

Use the catalog to find reference projects, research tools, benchmarks, papers, and structured learning paths.

Example workflows:

- Search for "benchmark", "papers", "simulation", "synthetic data", or "awesome".
- Find agent benchmarks and evaluation tools.
- Explore AI learning repositories and curated lists.
- Build teaching material around real repositories instead of abstract examples.

Useful entry points:

- Research, Papers & Science
- Benchmarks, Simulation & Synthetic Data
- Learning, Guides & Awesome Lists
- Market Research & Competitive Intelligence

## Example Searches

The HTML catalog search works across category names, repository names, descriptions, language, license, and source.

Try:

- `posthog`
- `privacy analytics`
- `invoice`
- `DocuSign alternative`
- `vector database`
- `MCP`
- `sandbox`
- `roadmap`
- `social media`
- `agent memory`

## Repository Structure

```text
.
|-- docs/
|   |-- UNIFIED_CATALOG.html
|   |-- UNIFIED_CATALOG.md
|   |-- MYAI_STACKGUIDE_PRODUCT_CONCEPT.md
|   |-- MYAI_STACKGUIDE_CONTEXT_SCANNER.md
|   |-- PRODUCT_REQUIREMENTS.md
|   |-- V1_ROADMAP.md
|   |-- METHODOLOGY.md
|   `-- CONTRIBUTING.md
|-- data/
|   |-- catalog_manifest.json
|   |-- catalog_manifest.schema.json
|   |-- source_repos.csv
|   |-- repos.csv
|   |-- repos.json
|   `-- categories.json
|-- templates/
|   `-- unified_catalog.html
|-- LICENSE
|-- research/
|   |-- github_curated_recommendations_2026-05-23.*
|   |-- github_business_curated_recommendations_2026-05-23.*
|   `-- github_search_candidates_2026-05-23.*
|-- categories/
|-- scripts/
|   |-- build_catalog.py
|   |-- build_unified_catalog.py
|   |-- build_catalog_html.py
|   |-- research_github_landscape.py
|   `-- research_github_business_landscape_html.py
|-- tests/
`-- .agents/
```

## Data Files

- `data/source_repos.csv` is the original working CSV.
- `data/catalog_manifest.json` is the canonical source for the current standalone HTML catalog.
- `data/catalog_manifest.schema.json` defines the stable top-level v5 manifest contract.
- `data/repos.csv` is the generated catalog from the original fork collection.
- `data/repos.json` is the JSON version of that generated catalog.
- `data/categories.json` contains the original category definitions and counts.
- `research/github_curated_recommendations_2026-05-23.*` contains AI/engineering GitHub research.
- `research/github_business_curated_recommendations_2026-05-23.*` contains business/product GitHub research.
- `docs/UNIFIED_CATALOG.md` is the legacy GitHub-readable catalog generated from the dated inputs.
- `docs/UNIFIED_CATALOG.html` is generated from the current manifest and HTML template.

## Regenerate

```bash
python scripts/build_catalog.py
python scripts/build_unified_catalog.py
python scripts/build_catalog_html.py
python scripts/build_catalog_html.py --check
```

## Scoring And Ratings

Scores are triage signals, not objective quality ratings.

The catalog uses public GitHub metadata such as stars, update timestamps, descriptions, and license fields. Scores help sort candidates inside a research snapshot, but they should not replace technical review, security review, license review, or product fit analysis.

## Caveats

- Stars and update timestamps are snapshots and will drift over time.
- Some repositories appear in more than one category because they support multiple workflows.
- Some descriptions come from upstream GitHub metadata and may be incomplete.
- Inclusion does not imply endorsement by, or affiliation with, upstream maintainers.
- This is a discovery and decision-support catalog, not a benchmark or procurement recommendation.
