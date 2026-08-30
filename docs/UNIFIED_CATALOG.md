# myAI-StackGuide Catalog

Snapshot: 2026-05-23

This file combines all repository categories collected so far: the account fork catalog, the AI/engineering GitHub landscape research, and the business/product GitHub landscape research.

Scores are triage signals from their source artifacts. They are useful for sorting within a source, but they are not due-diligence ratings and are not strictly comparable across every source.

The same repository can appear in more than one category when it is genuinely useful in multiple workflows.

## Summary

- Categories: 42
- Category placements: 351
- Unique repositories: 314
- Sources: `data/repos.csv`, `research/github_curated_recommendations_2026-05-23.json`, `research/github_business_curated_recommendations_2026-05-23.json`

## Product Decision Layer

Use this catalog as a decision aid: start from the work you need to do, narrow to the right category path, then inspect repositories with their caveats in mind.

### When To Use

| Situation | Start With | Decision Output |
|---|---|---|
| You need a shortlist before choosing an AI or automation stack. | Search by workflow, then inspect the matching category and top repositories. | A focused list of projects to read, prototype, or compare. |
| You are deciding what to self-host, buy, fork, or ignore. | Use the business/product categories alongside engineering platform categories. | A decision map for build-versus-buy and adoption planning. |
| You are designing an agentic workflow and need adjacent components. | Move across runtime, tools, memory, retrieval, evals, execution, and UI categories. | A stack-shaped view instead of isolated repository bookmarks. |
| You are auditing a personal fork library or research queue. | Use source groups, scores, categories, and stale metadata caveats. | A cleaner queue of active candidates, references, and archive/delete items. |

### When To Avoid

| Need | Why This Catalog Is Not Enough | Better Next Step |
|---|---|---|
| Security, compliance, legal, or procurement approval. | The catalog is not a security audit, license opinion, vendor review, or production-readiness certification. | Run dedicated code, security, license, and vendor due diligence. |
| Realtime repository rankings. | Stars, forks, update timestamps, and licenses are snapshot metadata and drift quickly. | Refresh from the GitHub API before presenting current claims. |
| An exhaustive market map. | The catalog is curated for practical decision support, not complete market coverage. | Run a scoped research refresh with explicit search queries and inclusion rules. |
| A direct product recommendation for a high-stakes adoption. | Scores are triage signals and are not comparable to hands-on evaluation in your environment. | Prototype the top candidates against your workload, data, permissions, and failure modes. |

### Stack Recipes

| Recipe | Use When | Category Path | Decision Question |
|---|---|---|---|
| Coding Agent Delivery Loop | You want agents to plan, edit, run tools, evaluate changes, and ship safely. | Codex, Claude & Skill Workflows -> Agent Runtime & Orchestration -> MCP & Tool Integrations -> Sandboxed Code Execution -> Evals, Observability & Prompt Ops -> Security, Safety & Supply Chain | Which parts of the loop must be reliable before autonomy increases? |
| RAG Knowledge Product | You need a product that reads documents, retrieves context, remembers decisions, and cites sources. | Documents, OCR & Parsing -> RAG, Retrieval & Search -> Vector DBs & Embedding Infrastructure -> Memory & Context Systems -> Knowledge Graphs -> Evals, Observability & Prompt Ops | Is the bottleneck ingestion quality, retrieval quality, memory, or evaluation? |
| Business Ops Automation Stack | You want to connect internal workflows across leads, support, reporting, and back office. | Automation, Workflows & No-code -> Sales, CRM & Lead Generation -> Customer Support & Success -> Analytics, BI & Reporting -> Accounting, Finance & ERP -> Legal, Contracts & Compliance | Which system owns customer, revenue, and compliance state? |
| Founder Lean Operating System | You need a lightweight startup stack before buying multiple SaaS products. | Market Research & Competitive Intelligence -> Marketing, Growth & SEO -> Sales, CRM & Lead Generation -> Product Management, Roadmaps & Feedback -> Analytics, BI & Reporting -> Automation, Workflows & No-code | What should be self-hosted, bought, or deferred for the next 90 days? |
| Design-To-Prototype Loop | You want to move from product idea to interface, demo, or user-testable prototype. | Design, Brand & UI/UX -> Frontend, UI, Desktop & Browser Automation -> Codex, Claude & Skill Workflows -> Multimodal & Vision Agents -> Developer Tools & CLI | Which artifact is the next decision point: design system, prototype, demo, or production UI? |

### Compare Views

| Compare | Use This View To Decide | Categories |
|---|---|---|
| Agent runtimes vs workflow engines | Whether you need autonomous agent behavior, deterministic orchestration, or both. | Agent Runtime & Orchestration -> Workflow State Machines & Durable Agents |
| RAG vs memory vs knowledge graphs | Whether the problem is retrieval, long-lived context, entity relationships, or source-grounded answers. | RAG, Retrieval & Search -> Memory & Context Systems -> Knowledge Graphs |
| MCP integrations vs no-code automation | Whether agents need programmable tool access or business teams need workflow automation. | MCP & Tool Integrations -> Automation, Workflows & No-code |
| Evals/observability vs security/safety | Whether the immediate risk is quality drift, prompt behavior, unsafe execution, or supply-chain exposure. | Evals, Observability & Prompt Ops -> Security, Safety & Supply Chain |
| Self-hosted suite vs focused tool | Whether to adopt a broad operating platform or combine narrow tools around one workflow. | Operations, Project Management & Internal Tools -> Analytics, BI & Reporting -> Customer Support & Success |

## Category Index

| Category | Repos | Source groups | Scope |
|---|---:|---|---|
| [Agent Runtime & Orchestration](#agent_runtime_orchestration) | 15 | Account fork catalog, AI/engineering research | Frameworks and systems for running agents, coordinating workflows, and composing autonomous software teams. |
| [Codex, Claude & Skill Workflows](#codex_claude_workflows) | 22 | Account fork catalog, AI/engineering research | Codex/Claude setups, skills, harnesses, prompt packs, and AI coding workflow methods. |
| [MCP & Tool Integrations](#mcp_integrations) | 17 | Account fork catalog, AI/engineering research | Model Context Protocol servers and connectors for external services, IDEs, knowledge systems, and productivity tools. |
| [RAG, Retrieval & Search](#rag_retrieval_search) | 11 | Account fork catalog, AI/engineering research | Retrieval-augmented generation, semantic retrieval, vector search, sparse search, and agent search layers. |
| [Memory & Context Systems](#memory_context_systems) | 13 | Account fork catalog, AI/engineering research | Long-term memory, context management, context retrieval, and reusable agent memory stores. |
| [Knowledge Graphs](#knowledge_graphs) | 6 | Account fork catalog, AI/engineering research | Graph-backed memory, knowledge graph construction, graph retrieval, and entity/relation systems for AI agents. |
| [Evals, Observability & Prompt Ops](#evals_observability_promptops) | 8 | Account fork catalog, AI/engineering research | Evaluation, tracing, prompt management, observability, metrics, and quality gates for LLM applications. |
| [Documents, OCR & Parsing](#document_ocr_parsing) | 8 | Account fork catalog, AI/engineering research | PDF/OCR/document parsing, document-to-markdown conversion, and content extraction for agent workflows. |
| [Cloudflare, Edge & Backend](#cloudflare_edge_backend) | 10 | Account fork catalog, AI/engineering research | Cloudflare Workers, edge runtimes, backend platforms, serverless systems, and deployment infrastructure. |
| [Databases, Storage & SQLite](#database_storage_sqlite) | 12 | Account fork catalog, AI/engineering research | Databases, SQLite extensions, storage engines, query systems, and data persistence layers. |
| [Frontend, UI, Desktop & Browser Automation](#frontend_ui_desktop_browser) | 14 | Account fork catalog, AI/engineering research | Frontend frameworks, desktop apps, UI layers, design tools, browser automation, and visual agent interfaces. |
| [Developer Tools & CLI](#developer_tools_cli) | 17 | Account fork catalog, AI/engineering research | CLI tools, code assistants, log tools, LSP integrations, OpenAPI wrappers, and developer workflow utilities. |
| [Learning, Guides & Awesome Lists](#learning_references_awesome) | 15 | Account fork catalog, AI/engineering research | Curated lists, tutorials, guides, examples, and structured learning resources. |
| [Research, Papers & Science](#research_papers_science) | 7 | Account fork catalog, AI/engineering research | Research projects, paper implementations, arXiv tooling, experiments, and scientific/research workflows. |
| [Security, Safety & Supply Chain](#security_safety_supply_chain) | 9 | Account fork catalog, AI/engineering research | Security scanners, safe execution systems, supply-chain checks, and isolation/sandboxing tools. |
| [Communications & Personal Ops](#communications_personal_ops) | 9 | Account fork catalog, AI/engineering research | Messaging, personal productivity, career ops, and communication automation connected to agents. |
| [Uncategorized / Needs Review](#uncategorized_review) | 1 | Account fork catalog | Useful but weakly described repositories that need manual review before public positioning. |
| [Agent Protocols & Interoperability](#agent_protocols_interop) | 5 | AI/engineering research | Protocols and interoperability layers for agent-to-agent, app-to-agent, or UI-to-agent communication. |
| [Sandboxed Code Execution](#sandboxed_code_execution) | 5 | AI/engineering research | Hosted or local sandboxes, code interpreters, notebooks, and secure execution environments for agents. |
| [Voice & Realtime Agents](#voice_realtime_agents) | 5 | AI/engineering research | Realtime voice, audio, telephony, and conversational media agents. |
| [Multimodal & Vision Agents](#multimodal_vision_agents) | 5 | AI/engineering research | Vision-language, computer-use, screenshot, video, and multimodal agent systems. |
| [Local LLM Inference & Routing](#local_llm_inference_routing) | 6 | AI/engineering research | Local model serving, LLM gateways, routers, proxy layers, and inference orchestration. |
| [Vector DBs & Embedding Infrastructure](#vector_databases_embedding_infra) | 6 | AI/engineering research | Vector databases, embedding stores, ANN indexes, and retrieval storage infrastructure beyond SQLite-only tools. |
| [Agentic Code Review & SWE](#agentic_code_review_swe) | 5 | AI/engineering research | SWE agents, coding benchmarks, code review automation, and repo-scale software engineering assistants. |
| [Web Crawling & Data Ingestion](#web_crawling_data_ingestion) | 5 | AI/engineering research | Crawling, scraping, browser extraction, and web-to-agent data ingestion. |
| [Workflow State Machines & Durable Agents](#workflow_state_machines_durable_agents) | 6 | AI/engineering research | Durable workflows, state machines, background jobs, and long-running agent process control. |
| [Benchmarks, Simulation & Synthetic Data](#benchmarks_simulation_synthetic_data) | 5 | AI/engineering research | Benchmarks, synthetic data generation, simulation environments, and scenario generation for agent testing. |
| [Marketing, Growth & SEO](#marketing_growth_seo) | 8 | Business/product research | Marketing automation, SEO, growth analytics, attribution, campaigns, and product-led growth tooling. |
| [Content, Social & Community](#content_social_community) | 7 | Business/product research | CMS, publishing, newsletters, social scheduling, community platforms, and content operations. |
| [Design, Brand & UI/UX](#design_brand_uiux) | 9 | Business/product research | Design systems, prototyping, whiteboards, diagrams, UI builders, brand assets, and design workflow tools. |
| [Sales, CRM & Lead Generation](#sales_crm_lead_generation) | 5 | Business/product research | CRM, lead management, outbound pipelines, enrichment, sales workflows, and account management. |
| [Fundraising, Investor Relations & Startup Ops](#fundraising_investor_relations) | 6 | Business/product research | Investor CRM, fundraising pipelines, pitch/deck workflows, cap tables, donation systems, startup operating systems, and venture research. |
| [Accounting, Finance & ERP](#accounting_finance_erp) | 10 | Business/product research | Bookkeeping, invoicing, accounting, ERP, budgeting, expenses, and finance back-office systems. |
| [Legal, Contracts & Compliance](#legal_contracts_compliance) | 8 | Business/product research | Contracts, document automation, e-signature, privacy, governance, compliance, and policy operations. |
| [Analytics, BI & Reporting](#analytics_bi_reporting) | 5 | Business/product research | Dashboards, BI, metrics stores, product analytics, reporting, and executive visibility. |
| [Customer Support & Success](#customer_support_success) | 7 | Business/product research | Helpdesk, live chat, ticketing, customer success, knowledge support, and support automation. |
| [Product Management, Roadmaps & Feedback](#product_management_feedback) | 5 | Business/product research | Feature requests, roadmap planning, feedback collection, issue triage, changelogs, and product discovery. |
| [E-commerce, Payments & Revenue](#ecommerce_payments_revenue) | 10 | Business/product research | Commerce platforms, checkout, payments, billing, subscriptions, pricing, and revenue operations. |
| [HR, Recruiting & People Ops](#hr_recruiting_people_ops) | 7 | Business/product research | Recruiting, applicant tracking, HRIS, payroll-adjacent workflows, employee operations, and team directories. |
| [Operations, Project Management & Internal Tools](#operations_project_management) | 5 | Business/product research | Project management, internal tools, admin panels, task systems, workflows, and operational command centers. |
| [Automation, Workflows & No-code](#automation_workflows_nocode) | 6 | Business/product research | Workflow builders, no-code/low-code automation, integrations, scheduling, and internal process automation. |
| [Market Research & Competitive Intelligence](#market_research_competitive_intel) | 6 | Business/product research | Research, web monitoring, trend detection, OSINT, scraping, social listening, and competitive intelligence. |

## Categories

### Agent Runtime & Orchestration
<a id="agent_runtime_orchestration"></a>

Frameworks and systems for running agents, coordinating workflows, and composing autonomous software teams.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [langflow-ai/langflow](https://github.com/langflow-ai/langflow) | 148690 | 2026-05-23 | 97.5 | AI/engineering research | Langflow is a powerful tool for building and deploying AI-powered agents and workflows. |
| [langgenius/dify](https://github.com/langgenius/dify) | 142347 | 2026-05-23 | 97.3 | AI/engineering research | Production-ready platform for agentic workflow development. |
| [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | 137466 | 2026-05-23 | 97.1 | AI/engineering research | The agent engineering platform. |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | 69279 | 2026-05-23 | 96.0 (A) | Account fork catalog | An open-source long-horizon SuperAgent harness that researches, codes, and creates. With the help of sandboxes, memories, tools, skill, subagents and message gateway,... |
| [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | 52016 | 2026-05-23 | 92.4 | AI/engineering research | Framework for orchestrating role-playing, autonomous AI agents. By fostering collaborative intelligence, CrewAI empowers agents to work together seamlessly, tackling c... |
| [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | 104432 | 2026-04-11 | 91.3 (A) | Account fork catalog | A complete AI agency at your fingertips - From frontend wizards to Reddit community ninjas, from whimsy injectors to reality checkers. Each agent is a specialized expe... |
| [agno-agi/agno](https://github.com/agno-agi/agno) | 40310 | 2026-05-23 | 91.2 | AI/engineering research | Build, run, and manage agent platforms. |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 32760 | 2026-05-23 | 90.2 | AI/engineering research | Build resilient agents. |
| [microsoft/autogen](https://github.com/microsoft/autogen) | 58316 | 2026-05-23 | 89.2 | AI/engineering research | A programming framework for agentic AI |
| [elizaOS/eliza](https://github.com/elizaOS/eliza) | 18438 | 2026-05-23 | 87.9 (A) | Account fork catalog | Open source agentic operating system |
| [GetStream/Vision-Agents](https://github.com/GetStream/Vision-Agents) | 7838 | 2026-05-23 | 87.3 (A) | Account fork catalog | Open Vision Agents by Stream. Build voice and vision agents quickly with any model or video provider. Uses Stream's edge network for ultra-low latency. |
| [moazbuilds/claudeclaw](https://github.com/moazbuilds/claudeclaw) | 1125 | 2026-05-18 | 75.9 (B) | Account fork catalog | A lightweight, open-source OpenClaw version built into your Claude Code. |
| [collaborator-ai/collab-public](https://github.com/collaborator-ai/collab-public) | 2504 | 2026-04-14 | 72.6 (B) | Account fork catalog | Collaborator is a place to create with agents |
| [ninjahawk/hollow-agentOS](https://github.com/ninjahawk/hollow-agentOS) | 256 | 2026-05-12 | 67.9 (C) | Account fork catalog | Hollow is an open-sourced self-modifying agentic system for consumer hardware |
| [hmldns/nautex](https://github.com/hmldns/nautex) | 79 | 2026-03-30 | 64.9 (C) | Account fork catalog | MCP server for guiding Coding Agents via end-to-end requirements to implementation plan pipeline |

### Codex, Claude & Skill Workflows
<a id="codex_claude_workflows"></a>

Codex/Claude setups, skills, harnesses, prompt packs, and AI coding workflow methods.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | 203666 | 2026-05-21 | 100.0 (A) | Account fork catalog | An agentic skills framework & software development methodology that works. |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | 188775 | 2026-05-20 | 99.7 (A) | Account fork catalog | The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and bey... |
| [github/spec-kit](https://github.com/github/spec-kit) | 105214 | 2026-05-22 | 97.6 (A) | Account fork catalog | 💫 Toolkit to help you get started with Spec-Driven Development |
| [anthropics/skills](https://github.com/anthropics/skills) | 139638 | 2026-05-23 | 97.2 | AI/engineering research | Public repository for Agent Skills |
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | 125950 | 2026-05-23 | 96.7 | AI/engineering research | Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster by executing routine tasks, explaining complex... |
| [garrytan/gstack](https://github.com/garrytan/gstack) | 101108 | 2026-05-22 | 96.7 (A) | Account fork catalog | Use Garry Tan's exact Claude Code setup: 23 opinionated tools that serve as CEO, Designer, Eng Manager, Release Manager, Doc Engineer, and QA |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 102030 | 2026-05-23 | 95.7 | AI/engineering research | Skills for Real Engineers. Straight from my .claude directory. |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 63946 | 2026-05-12 | 93.2 (A) | Account fork catalog | 🪨 why use many token when few token do trick — Claude Code skill that cuts 65% of tokens by talking like caveman |
| [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | 54538 | 2026-05-23 | 92.7 | AI/engineering research | from vibe coding to agentic engineering - practice makes claude perfect |
| [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) | 39660 | 2026-05-23 | 91.1 | AI/engineering research | 📄 Configuration files that enhance Cursor AI editor experience with custom rules and behaviors |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | 12681 | 2026-05-23 | 89.8 (A) | Account fork catalog | Open source repository of plugins primarily intended for knowledge workers to use in Claude Cowork |
| [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | 47918 | 2026-05-23 | 89.7 (A) | Account fork catalog | Breakthrough Method for Agile Ai Driven Development |
| [BloopAI/vibe-kanban](https://github.com/BloopAI/vibe-kanban) | 26451 | 2026-04-24 | 89.2 (A) | Account fork catalog | Get 10X more out of Claude Code, Codex or any coding agent |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 22817 | 2026-05-23 | 88.4 | AI/engineering research | A curated collection of 1000+ agent skills from official dev teams and the community, compatible with Claude Code, Codex, Gemini CLI, Cursor, and more. |
| [gsd-build/gsd-2](https://github.com/gsd-build/gsd-2) | 7742 | 2026-05-22 | 87.2 (A) | Account fork catalog | A powerful meta-prompting, context engineering and spec-driven development system that enables agents to work for long periods of time autonomously without losing trac... |
| [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | 32595 | 2026-01-02 | 83.3 (B) | Account fork catalog | Agent skills for Obsidian. Teach your agent to use Markdown, Bases, JSON Canvas, and use the CLI. |
| [anthropics/prompt-eng-interactive-tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) | 35878 | 2026-03-01 | 82.4 (B) | Account fork catalog | Anthropic's Interactive Prompt Engineering Tutorial |
| [PleasePrompto/ductor](https://github.com/PleasePrompto/ductor) | 377 | 2026-05-17 | 76.8 (B) | Account fork catalog | Control Claude Code, Codex CLI and Gemini CLI from Telegram. Live streaming, persistent memory, cron jobs, webhooks, Docker sandboxing. |
| [vudovn/ag-kit](https://github.com/vudovn/ag-kit) | 7507 | 2026-05-13 | 76.4 (B) | Account fork catalog |  |
| [aboul3ata/lazyweb-skill](https://github.com/aboul3ata/lazyweb-skill) | 352 | 2026-03-26 | 70.3 (B) | Account fork catalog | Design with evidence, not vibes. Lazyweb skills for AI coding agents. |
| [bassimeledath/dispatch](https://github.com/bassimeledath/dispatch) | 391 | 2026-04-06 | 65.7 (C) | Account fork catalog | A Claude Code skill that 10x's your effective context window by dispatching tasks to background AI workers. |
| [nicelight/memobank_BMAD_SDD](https://github.com/nicelight/memobank_BMAD_SDD) | 2 | 2026-05-21 | 50.0 (D) | Account fork catalog |  |

### MCP & Tool Integrations
<a id="mcp_integrations"></a>

Model Context Protocol servers and connectors for external services, IDEs, knowledge systems, and productivity tools.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 86124 | 2026-05-23 | 94.9 | AI/engineering research | Model Context Protocol Servers |
| [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 41231 | 2026-05-23 | 91.3 | AI/engineering research | Chrome DevTools for coding agents |
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | 87641 | 2026-05-23 | 91.2 | AI/engineering research | A collection of MCP servers. |
| [ComposioHQ/composio](https://github.com/ComposioHQ/composio) | 28406 | 2026-05-23 | 89.5 | AI/engineering research | Composio powers 1000+ toolkits, tool search, context management, authentication, and a sandboxed workbench to help you build AI agents that turn intent into action. |
| [czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp) | 21202 | 2026-05-23 | 88.1 | AI/engineering research | A MCP for Claude Desktop / Claude Code / Windsurf / Cursor to build n8n workflows for you |
| [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) | 2765 | 2026-05-18 | 84.2 (B) | Account fork catalog | A Model Context Protocol server for searching and analyzing arXiv papers |
| [modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry) | 6849 | 2026-05-23 | 82.6 | AI/engineering research | A community driven registry service for Model Context Protocol (MCP) servers. |
| [PleasePrompto/notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp) | 2533 | 2026-05-01 | 81.4 (B) | Account fork catalog | MCP server for NotebookLM - Let your AI agents (Claude Code, Codex) research documentation directly with grounded, citation-backed answers from Gemini. Persistent auth... |
| [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian) | 5251 | 2026-04-10 | 80.3 (B) | Account fork catalog | MCP server for Atlassian tools (Confluence, Jira) |
| [jacob-bd/notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli) | 4541 | 2026-05-22 | 77.0 (B) | Account fork catalog |  |
| [atlassian/atlassian-mcp-server](https://github.com/atlassian/atlassian-mcp-server) | 723 | 2026-04-14 | 73.0 (B) | Account fork catalog | Remote MCP Server that securely connects Jira and Confluence with your LLM, IDE, or agent platform of choice. |
| [mnemox-ai/idea-reality-mcp](https://github.com/mnemox-ai/idea-reality-mcp) | 697 | 2026-03-11 | 72.9 (B) | Account fork catalog | Pre-build reality check for AI coding agents. Scans GitHub, HN, npm, PyPI, Product Hunt. MCP server. 290+ stars. |
| [makenotion/claude-code-notion-plugin](https://github.com/makenotion/claude-code-notion-plugin) | 388 | 2026-01-22 | 62.0 (C) | Account fork catalog | Connect Claude Code to Notion via this Plugin |
| [aashari/mcp-server-atlassian-jira](https://github.com/aashari/mcp-server-atlassian-jira) | 70 | 2026-02-22 | 59.4 (C) | Account fork catalog | Node.js/TypeScript MCP server for Atlassian Jira. Equips AI systems (LLMs) with tools to list/get projects, search/get issues (using JQL/ID), and view dev info (commit... |
| [cvzi/telegram-bot-cloudflare](https://github.com/cvzi/telegram-bot-cloudflare) | 476 | 2024-07-13 | 59.0 (C) | Account fork catalog | A minimal example of a Telegram Bot on Cloudflare Workers |
| [Tritlo/lsp-mcp](https://github.com/Tritlo/lsp-mcp) | 124 | 2025-03-22 | 54.0 (D) | Account fork catalog | An MCP server that lets you interact with LSP servers |
| [hetaoBackend/mcp-github-trending](https://github.com/hetaoBackend/mcp-github-trending) | 49 | 2025-04-01 | 50.7 (D) | Account fork catalog | MCP server for getting github trending repos & developers |

### RAG, Retrieval & Search
<a id="rag_retrieval_search"></a>

Retrieval-augmented generation, semantic retrieval, vector search, sparse search, and agent search layers.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [infiniflow/ragflow](https://github.com/infiniflow/ragflow) | 81085 | 2026-05-20 | 95.9 (A) | Account fork catalog | RAGFlow is a leading open-source Retrieval-Augmented Generation (RAG) engine that fuses cutting-edge RAG with Agent capabilities to create a superior context layer for... |
| [pathwaycom/pathway](https://github.com/pathwaycom/pathway) | 63250 | 2026-05-23 | 93.4 | AI/engineering research | Python ETL framework for stream processing, real-time analytics, LLM pipelines, and RAG. |
| [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) | 35611 | 2026-05-22 | 92.8 (A) | Account fork catalog | [EMNLP2025] "LightRAG: Simple and Fast Retrieval-Augmented Generation" |
| [run-llama/llama_index](https://github.com/run-llama/llama_index) | 49612 | 2026-05-23 | 92.2 | AI/engineering research | LlamaIndex is the leading document agent and OCR platform |
| [HKUDS/RAG-Anything](https://github.com/HKUDS/RAG-Anything) | 20545 | 2026-05-21 | 91.6 (A) | Account fork catalog | "RAG-Anything: All-in-One RAG Framework" |
| [microsoft/graphrag](https://github.com/microsoft/graphrag) | 33178 | 2026-05-23 | 90.3 | AI/engineering research | A modular graph-based Retrieval-Augmented Generation (RAG) system |
| [VectifyAI/PageIndex](https://github.com/VectifyAI/PageIndex) | 32027 | 2026-05-23 | 90.1 | AI/engineering research | 📑 PageIndex: Document Index for Vectorless, Reasoning-based RAG |
| [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | 25352 | 2026-05-23 | 89.0 | AI/engineering research | Open-source AI orchestration framework for building context-engineered, production-ready LLM applications. Design modular pipelines and agent workflows with explicit c... |
| [airweave-ai/airweave](https://github.com/airweave-ai/airweave) | 6353 | 2026-05-22 | 85.5 (A) | Account fork catalog | Open-source context retrieval layer for AI agents |
| [weaviate/Verba](https://github.com/weaviate/Verba) | 7707 | 2026-05-22 | 83.2 | AI/engineering research | Retrieval Augmented Generation (RAG) chatbot powered by Weaviate |
| [naver/splade](https://github.com/naver/splade) | 995 | 2024-05-03 | 52.9 (D) | Account fork catalog | SPLADE: sparse neural search (SIGIR21, SIGIR22) |

### Memory & Context Systems
<a id="memory_context_systems"></a>

Long-term memory, context management, context retrieval, and reusable agent memory stores.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [mem0ai/mem0](https://github.com/mem0ai/mem0) | 56504 | 2026-05-23 | 95.3 (A), 92.8 | Account fork catalog, AI/engineering research | Universal memory layer for AI Agents |
| [MemPalace/mempalace](https://github.com/MemPalace/mempalace) | 52707 | 2026-05-23 | 95.0 (A), 92.5 | Account fork catalog, AI/engineering research | The best-benchmarked open-source AI memory system. And it's free. |
| [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 77628 | 2026-05-23 | 94.4 | AI/engineering research | Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and injects relevant context back into... |
| [lobehub/lobehub](https://github.com/lobehub/lobehub) | 77592 | 2026-05-23 | 94.4 | AI/engineering research | 🤯 LobeHub is your Chief Agent Operator, organizing your agents into 7×24 operations by hiring, scheduling, and reporting on your entire AI team. |
| [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory) | 22659 | 2026-05-23 | 91.2 (A) | Account fork catalog | Memory engine and app that is extremely fast, scalable. The Memory API for the AI era. |
| [volcengine/OpenViking](https://github.com/volcengine/OpenViking) | 24548 | 2026-05-23 | 88.8 | AI/engineering research | OpenViking is an open-source context database designed specifically for AI Agents(such as openclaw). OpenViking unifies the management of context (memory, resources, a... |
| [gastownhall/beads](https://github.com/gastownhall/beads) | 24037 | 2026-05-22 | 88.1 (A) | Account fork catalog | Beads - A memory upgrade for your coding agent |
| [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | 9352 | 2026-05-22 | 87.9 (A) | Account fork catalog | Self-evolving memory OS for LLM & AI Agents: ultra-persistent memory, hybrid-retrieval, and cross-task skill reuse, with 35.24% token savings |
| [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) | 16677 | 2026-05-23 | 86.9 | AI/engineering research | #1 Persistent memory for AI coding agents based on real-world benchmarks |
| [Tencent/TencentDB-Agent-Memory](https://github.com/Tencent/TencentDB-Agent-Memory) | 3883 | 2026-05-20 | 80.4 (B) | Account fork catalog | TencentDB Agent Memory delivers fully local long-term memory for AI Agents via a 4-tier progressive pipeline, with zero external API dependencies. |
| [andrewyng/context-hub](https://github.com/andrewyng/context-hub) | 13321 | 2026-04-29 | 78.5 (B) | Account fork catalog |  |
| [EverMind-AI/MSA](https://github.com/EverMind-AI/MSA) | 3448 | 2025-10-29 | 66.2 (C) | Account fork catalog | Memory Sparse Attention - A scalable, end-to-end trainable latent-memory framework for 100M-token contexts. |
| [memstate-ai/memstate-mcp](https://github.com/memstate-ai/memstate-mcp) | 2 | 2026-03-12 | 43.8 (D) | Account fork catalog |  |

### Knowledge Graphs
<a id="knowledge_graphs"></a>

Graph-backed memory, knowledge graph construction, graph retrieval, and entity/relation systems for AI agents.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [safishamsi/graphify](https://github.com/safishamsi/graphify) | 52264 | 2026-05-22 | 95.0 (A) | Account fork catalog | AI coding assistant skill (Claude Code, Codex, OpenCode, Cursor, Gemini CLI, and more). Turn any folder of code, SQL schemas, R scripts, shell scripts, docs, papers, i... |
| [getzep/graphiti](https://github.com/getzep/graphiti) | 26416 | 2026-05-23 | 92.5 (A), 89.2 | Account fork catalog, AI/engineering research | Build Real-Time Knowledge Graphs for AI Agents |
| [abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus) | 39862 | 2026-05-23 | 91.1 | AI/engineering research | GitNexus: The Zero-Server Code Intelligence Engine - GitNexus is a client-side knowledge graph creator that runs entirely in your browser. Drop in a GitHub repo or ZIP... |
| [microsoft/graphrag](https://github.com/microsoft/graphrag) | 33178 | 2026-05-23 | 90.3 | AI/engineering research | A modular graph-based Retrieval-Augmented Generation (RAG) system |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 32760 | 2026-05-23 | 90.2 | AI/engineering research | Build resilient agents. |
| [neo4j-labs/llm-graph-builder](https://github.com/neo4j-labs/llm-graph-builder) | 4700 | 2026-05-23 | 82.9 (B), 77.1 | Account fork catalog, AI/engineering research | Neo4j graph construction from unstructured data using LLMs |

### Evals, Observability & Prompt Ops
<a id="evals_observability_promptops"></a>

Evaluation, tracing, prompt management, observability, metrics, and quality gates for LLM applications.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | 27773 | 2026-05-23 | 86.9 (A), 89.4 | Account fork catalog, AI/engineering research | 🪢 Open source LLM engineering platform: LLM Observability, metrics, evals, prompt management, playground, datasets. Integrates with OpenTelemetry, Langchain, OpenAI SD... |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | 21529 | 2026-05-23 | 88.2 | AI/engineering research | Test your prompts, agents, and RAGs. Red teaming/pentesting/vulnerability scanning for AI. Compare performance of GPT, Claude, Gemini, DeepSeek, and more. Simple decla... |
| [comet-ml/opik](https://github.com/comet-ml/opik) | 19359 | 2026-05-23 | 87.7 | AI/engineering research | Debug, evaluate, and monitor your LLM applications, RAG systems, and agentic workflows with comprehensive tracing, automated evaluations, and production-ready dashboards. |
| [confident-ai/deepeval](https://github.com/confident-ai/deepeval) | 15653 | 2026-05-23 | 86.6 | AI/engineering research | The LLM Evaluation Framework |
| [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) | 9804 | 2026-05-23 | 84.4 | AI/engineering research | AI Observability & Evaluation |
| [Giskard-AI/giskard-oss](https://github.com/Giskard-AI/giskard-oss) | 5364 | 2026-05-23 | 81.5 | AI/engineering research | 🐢 Open-Source Evaluation & Testing library for LLM Agents |
| [vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas) | 14025 | 2026-01-31 | 80.2 (B) | Account fork catalog | Supercharge Your LLM Application Evaluations 🚀 |
| [sernote/audit-prompt-caching](https://github.com/sernote/audit-prompt-caching) | 56 | 2026-05-08 | 58.4 (C) | Account fork catalog |  |

### Documents, OCR & Parsing
<a id="document_ocr_parsing"></a>

PDF/OCR/document parsing, document-to-markdown conversion, and content extraction for agent workflows.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | 124773 | 2026-05-23 | 91.9 (A), 96.6 | Account fork catalog, AI/engineering research | Python tool for converting files and office documents to Markdown. |
| [opendatalab/MinerU](https://github.com/opendatalab/MinerU) | 64613 | 2026-05-23 | 95.0 (A), 93.5 | Account fork catalog, AI/engineering research | Transforms complex documents like PDFs and Office docs into LLM-ready markdown/JSON for your Agentic workflows. |
| [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | 78411 | 2026-05-19 | 93.2 (A) | Account fork catalog | Turn any PDF or image document into structured data for your AI. A powerful, lightweight OCR toolkit that bridges the gap between images/PDFs and LLMs. Supports 100+ l... |
| [VectifyAI/PageIndex](https://github.com/VectifyAI/PageIndex) | 32027 | 2026-05-23 | 90.1 | AI/engineering research | 📑 PageIndex: Document Index for Vectorless, Reasoning-based RAG |
| [datalab-to/marker](https://github.com/datalab-to/marker) | 35362 | 2026-05-23 | 86.8 | AI/engineering research | Convert PDF to markdown + JSON quickly with high accuracy |
| [Unstructured-IO/unstructured](https://github.com/Unstructured-IO/unstructured) | 14764 | 2026-05-23 | 86.3 | AI/engineering research | Convert documents to structured data effortlessly. Unstructured is open-source ETL solution for transforming complex documents into clean, structured formats for langu... |
| [getomni-ai/zerox](https://github.com/getomni-ai/zerox) | 12231 | 2026-05-23 | 65.4 | AI/engineering research | OCR & Document Extraction using vision models |
| [aimclub/documentor](https://github.com/aimclub/documentor) | 45 | 2026-03-04 | 59.6 (C) | Account fork catalog | Document parsing library that extracts structured content |

### Cloudflare, Edge & Backend
<a id="cloudflare_edge_backend"></a>

Cloudflare Workers, edge runtimes, backend platforms, serverless systems, and deployment infrastructure.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [InsForge/InsForge](https://github.com/InsForge/InsForge) | 10513 | 2026-05-23 | 88.3 (A) | Account fork catalog | The all-in-one, open-source backend platform for agentic coding. InsForge gives your coding agent database, auth, storage, compute, hosting, and AI gateway to ship ful... |
| [cloudflare/agents](https://github.com/cloudflare/agents) | 4953 | 2026-05-23 | 86.3 (A), 81.1 | Account fork catalog, AI/engineering research | Build and deploy AI Agents on Cloudflare |
| [cloudflare/moltworker](https://github.com/cloudflare/moltworker) | 9897 | 2026-05-09 | 84.6 (B) | Account fork catalog | Run OpenClaw, (formerly Moltbot, formerly Clawdbot) on Cloudflare Workers |
| [cloudflare/workerd](https://github.com/cloudflare/workerd) | 8240 | 2026-05-23 | 83.5 | AI/engineering research | The JavaScript / Wasm runtime that powers Cloudflare Workers |
| [cloudflare/cloudflare-docs](https://github.com/cloudflare/cloudflare-docs) | 4743 | 2026-05-23 | 82.9 (B) | Account fork catalog | Cloudflare’s documentation |
| [cloudflare/workers-sdk](https://github.com/cloudflare/workers-sdk) | 4085 | 2026-05-23 | 80.1 | AI/engineering research | ⛅️ Home to Wrangler, the CLI for Cloudflare Workers® |
| [cloudflare/templates](https://github.com/cloudflare/templates) | 1965 | 2026-05-23 | 72.9 | AI/engineering research | Templates for Cloudflare Workers |
| [raulvidis/hermes-cloudflare](https://github.com/raulvidis/hermes-cloudflare) | 19 | 2026-05-22 | 61.0 (C) | Account fork catalog | Cloudflare Browser Rendering plugin for hermes-agent — crawl, scrape, extract content from web pages |
| [cloudflare/workers-ai-provider](https://github.com/cloudflare/workers-ai-provider) | 114 | 2026-05-03 | 42.9 | AI/engineering research | A Workers AI provider for the vercel AI SDK |
| [dpny518/llm-worker](https://github.com/dpny518/llm-worker) | 0 | 2026-03-24 | 34.8 (E) | Account fork catalog |  |

### Databases, Storage & SQLite
<a id="database_storage_sqlite"></a>

Databases, SQLite extensions, storage engines, query systems, and data persistence layers.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [supabase/supabase](https://github.com/supabase/supabase) | 102907 | 2026-05-23 | 95.7 | AI/engineering research | The Postgres development platform. Supabase gives you a dedicated Postgres database to build your web, mobile, and AI applications. |
| [redis/redis](https://github.com/redis/redis) | 74513 | 2026-05-23 | 94.2 | AI/engineering research | For developers, who are building real-time data-driven applications, Redis is the preferred, fastest, and most feature-rich cache, data structure server, and document... |
| [milvus-io/milvus](https://github.com/milvus-io/milvus) | 44417 | 2026-05-23 | 91.7 | AI/engineering research | Milvus is a high-performance, cloud-native vector database built for scalable vector ANN search |
| [qdrant/qdrant](https://github.com/qdrant/qdrant) | 31522 | 2026-05-23 | 90.0 | AI/engineering research | Qdrant - High-performance, massive-scale Vector Database and Vector Search Engine for the next generation of AI. Also available in the cloud https://cloud.qdrant.io/ |
| [chroma-core/chroma](https://github.com/chroma-core/chroma) | 28065 | 2026-05-23 | 89.4 | AI/engineering research | Search infrastructure for AI |
| [asg017/sqlite-vec](https://github.com/asg017/sqlite-vec) | 7627 | 2026-05-18 | 87.9 (A) | Account fork catalog | A vector search SQLite extension that runs anywhere! |
| [mindsdb/minds-platform](https://github.com/mindsdb/minds-platform) | 39201 | 2026-05-21 | 87.2 (A) | Account fork catalog | Platform dedicated to building an open foundation for applied Artificial Intelligence, designed for people seeking production-ready AI systems they can truly control,... |
| [weaviate/weaviate](https://github.com/weaviate/weaviate) | 16229 | 2026-05-23 | 86.8 | AI/engineering research | Weaviate is an open-source vector database that stores both objects and vectors, allowing for the combination of vector search with structured filtering with the fault... |
| [lancedb/lancedb](https://github.com/lancedb/lancedb) | 10382 | 2026-05-23 | 84.6 | AI/engineering research | Developer-friendly OSS embedded retrieval library for multimodal AI. Search More; Manage Less. |
| [get-convex/convex-backend](https://github.com/get-convex/convex-backend) | 11673 | 2026-05-22 | 83.7 (B) | Account fork catalog | The open-source reactive database for app developers |
| [serenedb/serenedb](https://github.com/serenedb/serenedb) | 520 | 2026-05-23 | 77.3 (B) | Account fork catalog | The First Real-Time Search Analytics Database |
| [asg017/sqlite-lembed](https://github.com/asg017/sqlite-lembed) | 256 | 2024-10-01 | 51.7 (D) | Account fork catalog | A SQLite extension for generating text embeddings from GGUF models using llama.cpp |

### Frontend, UI, Desktop & Browser Automation
<a id="frontend_ui_desktop_browser"></a>

Frontend frameworks, desktop apps, UI layers, design tools, browser automation, and visual agent interfaces.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [openclaw/openclaw](https://github.com/openclaw/openclaw) | 374135 | 2026-05-23 | 100.0 | AI/engineering research | Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞 |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | 95203 | 2026-05-23 | 97.2 (A) | Account fork catalog | 🌐 Make websites accessible for AI agents. Automate tasks online with ease. |
| [microsoft/playwright](https://github.com/microsoft/playwright) | 89271 | 2026-05-23 | 95.0 | AI/engineering research | Playwright is a framework for Web Testing and Automation. It allows testing Chromium, Firefox and WebKit with a single API. |
| [nexu-io/open-design](https://github.com/nexu-io/open-design) | 50390 | 2026-05-23 | 93.1 (A) | Account fork catalog | 🎨 Local-first, open-source Claude Design alternative. ⚡ 19 Skills · ✨ 71 brand-grade Design Systems 🖼 Generate web · desktop · mobile prototypes · slides · images · vi... |
| [siddharthvaddem/openscreen](https://github.com/siddharthvaddem/openscreen) | 36965 | 2026-05-22 | 93.0 (A) | Account fork catalog | Create stunning demos for free. Open-source, no subscriptions, no watermarks, and free for commercial use. An alternative to Screen Studio. |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 29688 | 2026-05-18 | 92.9 (A) | Account fork catalog | The design language that makes your AI harness better at design. |
| [bytedance/UI-TARS-desktop](https://github.com/bytedance/UI-TARS-desktop) | 35035 | 2026-05-18 | 92.8 (A) | Account fork catalog | The Open-Source Multimodal AI Agent Stack: Connecting Cutting-Edge AI Models and Agent Infra |
| [gradio-app/gradio](https://github.com/gradio-app/gradio) | 42663 | 2026-05-23 | 92.5 (A) | Account fork catalog | Build and share delightful machine learning apps, all in Python. 🌟 Star to support our work! |
| [CopilotKit/CopilotKit](https://github.com/CopilotKit/CopilotKit) | 31692 | 2026-05-23 | 91.4 (A), 90.0 | Account fork catalog, AI/engineering research | The Frontend Stack for Agents & Generative UI. React + Angular. Makers of the AG-UI Protocol |
| [expo/expo](https://github.com/expo/expo) | 49611 | 2026-05-23 | 90.8 (A) | Account fork catalog | An open-source framework for making universal native apps with React. Expo runs on Android, iOS, and the web. |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | 34062 | 2026-05-23 | 90.4 | AI/engineering research | Browser automation CLI for AI agents |
| [nesquena/hermes-webui](https://github.com/nesquena/hermes-webui) | 8371 | 2026-05-22 | 88.3 (A) | Account fork catalog | Hermes WebUI: The best way to use Hermes Agent from the web or from your phone! |
| [simular-ai/Agent-S](https://github.com/simular-ai/Agent-S) | 11580 | 2026-05-23 | 85.2 | AI/engineering research | Agent S: an open agentic framework that uses computers like a human |
| [assistant-ui/assistant-ui](https://github.com/assistant-ui/assistant-ui) | 10198 | 2026-05-23 | 84.6 | AI/engineering research | Typescript/React Library for AI Chat💬🚀 |

### Developer Tools & CLI
<a id="developer_tools_cli"></a>

CLI tools, code assistants, log tools, LSP integrations, OpenAPI wrappers, and developer workflow utilities.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | 125950 | 2026-05-23 | 96.7 | AI/engineering research | Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster by executing routine tasks, explaining complex... |
| [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | 104516 | 2026-05-23 | 95.8 | AI/engineering research | An open-source AI agent that brings the power of Gemini directly into your terminal. |
| [upstash/context7](https://github.com/upstash/context7) | 55928 | 2026-05-22 | 95.2 (A) | Account fork catalog | Context7 Platform -- Up-to-date code documentation for LLMs and AI code editors |
| [openai/codex](https://github.com/openai/codex) | 84832 | 2026-05-23 | 94.8 | AI/engineering research | Lightweight coding agent that runs in your terminal |
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | 74631 | 2026-05-23 | 94.2 | AI/engineering research | 🙌 OpenHands: AI-Driven Development |
| [cline/cline](https://github.com/cline/cline) | 62212 | 2026-05-23 | 93.3 | AI/engineering research | Autonomous coding agent as an SDK, IDE extension, or CLI assistant. |
| [Aider-AI/aider](https://github.com/Aider-AI/aider) | 45202 | 2026-05-23 | 91.7 | AI/engineering research | aider is AI pair programming in your terminal |
| [continuedev/continue](https://github.com/continuedev/continue) | 33335 | 2026-05-23 | 90.3 | AI/engineering research | ⏩ Source-controlled AI checks, enforceable in CI. Powered by the open-source Continue CLI |
| [sirmalloc/ccstatusline](https://github.com/sirmalloc/ccstatusline) | 9669 | 2026-05-20 | 88.8 (A) | Account fork catalog | 🚀 Beautiful highly customizable statusline for Claude Code CLI with powerline support, themes, and more. |
| [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 10274 | 2026-05-23 | 87.3 (A) | Account fork catalog | OpenVINO™ is an open source toolkit for optimizing and deploying AI inference |
| [microsoft/playwright-cli](https://github.com/microsoft/playwright-cli) | 10625 | 2026-05-07 | 86.6 (A) | Account fork catalog | CLI for common Playwright actions. Record and generate Playwright code, inspect selectors and take screenshots. |
| [vakovalskii/codbash](https://github.com/vakovalskii/codbash) | 212 | 2026-05-20 | 74.7 (B) | Account fork catalog | Termius-style browser dashboard for Claude Code & Codex sessions. View, search, resume, tag, and manage all your AI coding sessions. |
| [EvilFreelancer/openapi-to-cli](https://github.com/EvilFreelancer/openapi-to-cli) | 227 | 2026-04-07 | 68.7 (C) | Account fork catalog | Turns any OpenAPI/Swagger API into an CLI with set of commands. One CLI command per endpoint. |
| [Exocija/ZetaLib](https://github.com/Exocija/ZetaLib) | 753 | 2026-04-21 | 68.1 (C) | Account fork catalog | 🌙 ZetaLib - The only AI Library you need |
| [syabro/snitchmd](https://github.com/syabro/snitchmd) | 95 | 2026-05-14 | 60.3 (C) | Account fork catalog |  |
| [alenazaharovaux/share](https://github.com/alenazaharovaux/share) | 35 | 2026-03-01 | 56.9 (C) | Account fork catalog | Shared knowledge |
| [NailShakurov/logzip](https://github.com/NailShakurov/logzip) | 10 | 2026-04-24 | 56.3 (C) | Account fork catalog | Compress logs for LLM analysis — Rust-powered, Python API. 40-60% token savings. |

### Learning, Guides & Awesome Lists
<a id="learning_references_awesome"></a>

Curated lists, tutorials, guides, examples, and structured learning resources.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [microsoft/generative-ai-for-beginners](https://github.com/microsoft/generative-ai-for-beginners) | 111298 | 2026-05-23 | 96.1 | AI/engineering research | 21 Lessons, Get Started Building with Generative AI |
| [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 111555 | 2026-05-09 | 94.5 (A) | Account fork catalog | 100+ AI Agent & RAG apps you can actually run — clone, customize, ship. |
| [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) | 38452 | 2026-05-23 | 93.9 (A) | Account fork catalog | Installable GitHub library of 1,400+ agentic skills for Claude Code, Cursor, Codex CLI, Gemini CLI, Antigravity, and more. Includes installer CLI, bundles, workflows,... |
| [patchy631/ai-engineering-hub](https://github.com/patchy631/ai-engineering-hub) | 35192 | 2026-05-23 | 90.5 | AI/engineering research | In-depth tutorials on LLMs, RAGs and real-world AI agent applications. |
| [aishwaryanr/awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide) | 26830 | 2026-05-23 | 89.2 | AI/engineering research | A one stop repository for generative AI research updates, interview resources, notebooks and much more! |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 22817 | 2026-05-23 | 88.4 | AI/engineering research | A curated collection of 1000+ agent skills from official dev teams and the community, compatible with Claude Code, Codex, Gemini CLI, Cursor, and more. |
| [NirDiamant/GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents) | 22183 | 2026-05-23 | 88.3 | AI/engineering research | 50+ tutorials and implementations for Generative AI Agent techniques, from basic conversational bots to complex multi-agent systems. |
| [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) | 74896 | 2025-12-20 | 85.6 (A) | Account fork catalog | 🐙 Guides, papers, lessons, notebooks and resources for prompt engineering, context engineering, RAG, and AI Agents. |
| [x1xhlol/system-prompts-and-models-of-ai-tools](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools) | 138137 | 2025-10-02 | 84.8 (B) | Account fork catalog | FULL Augment Code, Claude Code, Cluely, CodeBuddy, Comet, Cursor, Devin AI, Junie, Kiro, Leap.new, Lovable, Manus, NotionAI, Orchids.app, Perplexity, Poke, Qoder, Repl... |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | 61401 | 2026-04-21 | 84.3 (B) | Account fork catalog | A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows |
| [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) | 62159 | 2025-06-29 | 81.9 (B) | Account fork catalog | Bash is all you need - A nano claude code–like 「agent harness」, built from 0 to 1 |
| [microsoft/ai-agents-for-beginners](https://github.com/microsoft/ai-agents-for-beginners) | 65258 | 2025-12-17 | 81.8 (B) | Account fork catalog | 12 Lessons to Get Started Building AI Agents |
| [ombharatiya/ai-system-design-guide](https://github.com/ombharatiya/ai-system-design-guide) | 574 | 2026-05-16 | 73.4 (B) | Account fork catalog | AI system design guide for engineers building production AI systems and evals. |
| [e2b-dev/awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) | 27972 | 2026-05-23 | 69.4 | AI/engineering research | A list of AI autonomous agents |
| [josix/awesome-claude-md](https://github.com/josix/awesome-claude-md) | 325 | 2026-04-16 | 65.1 (C) | Account fork catalog | Curated collection of exemplary claude.md files and onboarding patterns from public GitHub projects. Includes analyses, best practices, and templates to help developer... |

### Research, Papers & Science
<a id="research_papers_science"></a>

Research projects, paper implementations, arXiv tooling, experiments, and scientific/research workflows.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [hpcaitech/ColossalAI](https://github.com/hpcaitech/ColossalAI) | 41391 | 2026-05-23 | 91.3 | AI/engineering research | Making large AI models cheaper, faster and more accessible |
| [microsoft/autogen](https://github.com/microsoft/autogen) | 58316 | 2026-05-23 | 89.2 | AI/engineering research | A programming framework for agentic AI |
| [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V) | 25209 | 2026-05-23 | 88.9 | AI/engineering research | A Pocket-Sized MLLM for Ultra-Efficient Image and Video Understanding on Your Phone |
| [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | 19280 | 2026-05-23 | 87.6 | AI/engineering research | SWE-agent takes a GitHub issue and tries to automatically fix it, using your LM of choice. It can also be employed for offensive cybersecurity or competitive coding ch... |
| [karpathy/autoresearch](https://github.com/karpathy/autoresearch) | 82873 | 2026-03-09 | 85.4 (A) | Account fork catalog | AI agents running research on single-GPU nanochat training automatically |
| [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench) | 4998 | 2026-05-23 | 77.4 | AI/engineering research | SWE-bench: Can Language Models Resolve Real-world Github Issues? |
| [google-research/reasoning-bank](https://github.com/google-research/reasoning-bank) | 369 | 2026-05-19 | 67.8 (C) | Account fork catalog |  |

### Security, Safety & Supply Chain
<a id="security_safety_supply_chain"></a>

Security scanners, safe execution systems, supply-chain checks, and isolation/sandboxing tools.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [nanocoai/nanoclaw](https://github.com/nanocoai/nanoclaw) | 29305 | 2026-05-18 | 92.9 (A) | Account fork catalog | A lightweight alternative to OpenClaw that runs in containers for security. Connects to WhatsApp, Telegram, Slack, Discord, Gmail and other messaging apps,, has memory... |
| [KeygraphHQ/shannon](https://github.com/KeygraphHQ/shannon) | 43555 | 2026-05-23 | 91.6 | AI/engineering research | Shannon Lite is an autonomous, white-box AI pentester for web applications and APIs. It analyzes your source code, identifies attack vectors, and executes real exploit... |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | 21529 | 2026-05-23 | 88.2 | AI/engineering research | Test your prompts, agents, and RAGs. Red teaming/pentesting/vulnerability scanning for AI. Compare performance of GPT, Claude, Gemini, DeepSeek, and more. Simple decla... |
| [analysis-tools-dev/static-analysis](https://github.com/analysis-tools-dev/static-analysis) | 14565 | 2026-05-23 | 86.3 | AI/engineering research | ⚙️ A curated list of static analysis (SAST) tools and linters for all programming languages, config files, build tools, and more. The focus is on tools which improve c... |
| [alibaba/OpenSandbox](https://github.com/alibaba/OpenSandbox) | 10781 | 2026-05-23 | 84.8 | AI/engineering research | Secure, Fast, and Extensible Sandbox runtime for AI agents. |
| [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | 7068 | 2026-05-23 | 82.8 | AI/engineering research | 754 structured cybersecurity skills for AI agents · Mapped to 5 frameworks: MITRE ATT&CK, NIST CSF 2.0, MITRE ATLAS, D3FEND & NIST AI RMF · agentskills.io standard · W... |
| [perplexityai/bumblebee](https://github.com/perplexityai/bumblebee) | 699 | 2026-05-23 | 79.1 (B) | Account fork catalog | Read-only developer endpoint scanner for on-disk package, extension, and developer-tool metadata, built to check exposure to known software supply-chain compromises. |
| [princezuda/safestclaw](https://github.com/princezuda/safestclaw) | 276 | 2026-05-18 | 75.7 (B) | Account fork catalog | Safestclaw is the alternative to openclaw.. You can naturally chat with it via text and voice, and you can choose not to use a language model., By default it picks up... |
| [protectai/rebuff](https://github.com/protectai/rebuff) | 1487 | 2026-05-22 | 55.3 | AI/engineering research | LLM Prompt Injection Detector |

### Communications & Personal Ops
<a id="communications_personal_ops"></a>

Messaging, personal productivity, career ops, and communication automation connected to agents.

Source groups: Account fork catalog, AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | 189377 | 2026-05-23 | 98.7 | AI/engineering research | Fair-code workflow automation platform with native AI capabilities. Combine visual building with custom code, self-host or cloud, 400+ integrations. |
| [santifer/career-ops](https://github.com/santifer/career-ops) | 46812 | 2026-05-22 | 94.6 (A) | Account fork catalog | AI-powered job search system built on Claude Code. 14 skill modes, Go dashboard, PDF generation, batch processing. |
| [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) | 58070 | 2026-05-23 | 93.0 | AI/engineering research | ⭐AI-driven public opinion & trend monitor with multi-platform aggregation, RSS, and smart alerts.🎯 告别信息过载，你的 AI 舆情监控助手与热点筛选工具！聚合多平台热点 + RSS 订阅，支持关键词精准筛选。AI 智能筛选新闻 + AI... |
| [zhayujie/CowAgent](https://github.com/zhayujie/CowAgent) | 44741 | 2026-05-23 | 91.7 | AI/engineering research | CowAgent (chatgpt-on-wechat) 是基于大模型的超级AI助理，能主动思考和任务规划、访问操作系统和外部资源、创造和执行Skills、通过长期记忆和知识库不断成长，比OpenClaw更轻量和便捷。同时支持微信、飞书、钉钉、企微、QQ、公众号、网页等接入，可选择DeepSeek/OpenAI/Claude/Gem... |
| [czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp) | 21202 | 2026-05-23 | 88.1 | AI/engineering research | A MCP for Claude Desktop / Claude Code / Windsurf / Cursor to build n8n workflows for you |
| [enescingoz/awesome-n8n-templates](https://github.com/enescingoz/awesome-n8n-templates) | 22405 | 2026-05-23 | 84.6 | AI/engineering research | 280+ free n8n automation templates — ready-to-use workflows for Gmail, Telegram, Slack, Discord, WhatsApp, Google Drive, Notion, OpenAI, and more. AI agents, RAG chatb... |
| [chenhg5/cc-connect](https://github.com/chenhg5/cc-connect) | 10253 | 2026-05-23 | 84.6 | AI/engineering research | Bridge local AI coding agents (Claude Code, Cursor, Gemini CLI, Codex) to messaging platforms (Feishu/Lark, DingTalk, Slack, Telegram, Discord, LINE, WeChat Work). Cha... |
| [GeiserX/Telegram-Archive](https://github.com/GeiserX/Telegram-Archive) | 123 | 2026-05-23 | 72.7 (B) | Account fork catalog | Own your Telegram history. Automated, incremental backups with a local web viewer that feels just like the real app. Docker-ready and supports public chat sharing |
| [blqke/beepctl](https://github.com/blqke/beepctl) | 44 | 2026-03-23 | 62.8 (C) | Account fork catalog | CLI for Beeper Desktop API - unified messaging from your terminal. Give your AI agents the power to chat across all your messaging platforms. |

### Uncategorized / Needs Review
<a id="uncategorized_review"></a>

Useful but weakly described repositories that need manual review before public positioning.

Source groups: Account fork catalog

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [f/deeper](https://github.com/f/deeper) | 73 | 2026-02-23 | 55.6 (C) | Account fork catalog |  |

### Agent Protocols & Interoperability
<a id="agent_protocols_interop"></a>

Protocols and interoperability layers for agent-to-agent, app-to-agent, or UI-to-agent communication.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 86124 | 2026-05-23 | 94.9 | AI/engineering research | Model Context Protocol Servers |
| [a2aproject/A2A](https://github.com/a2aproject/A2A) | 23932 | 2026-05-23 | 88.7 | AI/engineering research | Agent2Agent (A2A) is an open protocol enabling communication and interoperability between opaque agentic applications. |
| [ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui) | 13763 | 2026-05-23 | 86.0 | AI/engineering research | AG-UI: the Agent-User Interaction Protocol. Bring Agents into Frontend Applications. |
| [modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry) | 6849 | 2026-05-23 | 82.6 | AI/engineering research | A community driven registry service for Model Context Protocol (MCP) servers. |
| [CopilotKit/generative-ui](https://github.com/CopilotKit/generative-ui) | 717 | 2026-05-22 | 63.0 | AI/engineering research | Generative UI examples for: AG-UI, A2UI/Open-JSON-UI, and MCP Apps. |

### Sandboxed Code Execution
<a id="sandboxed_code_execution"></a>

Hosted or local sandboxes, code interpreters, notebooks, and secure execution environments for agents.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [daytonaio/daytona](https://github.com/daytonaio/daytona) | 72469 | 2026-05-23 | 94.0 | AI/engineering research | Daytona is a Secure and Elastic Infrastructure for Running AI-Generated Code |
| [ComposioHQ/composio](https://github.com/ComposioHQ/composio) | 28406 | 2026-05-23 | 89.5 | AI/engineering research | Composio powers 1000+ toolkits, tool search, context management, authentication, and a sandboxed workbench to help you build AI agents that turn intent into action. |
| [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | 12334 | 2026-05-23 | 85.5 | AI/engineering research | Open-source, secure environment with real-world tools for enterprise-grade agents. |
| [alibaba/OpenSandbox](https://github.com/alibaba/OpenSandbox) | 10781 | 2026-05-23 | 84.8 | AI/engineering research | Secure, Fast, and Extensible Sandbox runtime for AI agents. |
| [QwenLM/Qwen-Agent](https://github.com/QwenLM/Qwen-Agent) | 16384 | 2026-05-23 | 78.1 | AI/engineering research | Agent framework and applications built upon Qwen>=3.0, featuring Function Calling, MCP, Code Interpreter, RAG, Chrome extension, etc. |

### Voice & Realtime Agents
<a id="voice_realtime_agents"></a>

Realtime voice, audio, telephony, and conversational media agents.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [mudler/LocalAI](https://github.com/mudler/LocalAI) | 46427 | 2026-05-23 | 91.9 | AI/engineering research | LocalAI is the open-source AI engine. Run any model - LLMs, vision, voice, image, video - on any hardware. No GPU required. |
| [jamiepine/voicebox](https://github.com/jamiepine/voicebox) | 27862 | 2026-05-23 | 85.7 | AI/engineering research | The open-source AI voice studio. Clone, dictate, create. |
| [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat) | 12438 | 2026-05-23 | 85.5 | AI/engineering research | Open Source framework for voice and multimodal conversational AI |
| [livekit/agents](https://github.com/livekit/agents) | 10604 | 2026-05-23 | 84.7 | AI/engineering research | A framework for building realtime voice AI agents 🤖🎙️📹 |
| [vocodedev/vocode-core](https://github.com/vocodedev/vocode-core) | 3750 | 2026-05-21 | 59.7 | AI/engineering research | 🤖 Build voice-based LLM agents. Modular + open source. |

### Multimodal & Vision Agents
<a id="multimodal_vision_agents"></a>

Vision-language, computer-use, screenshot, video, and multimodal agent systems.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [oobabooga/textgen](https://github.com/oobabooga/textgen) | 47204 | 2026-05-23 | 92.0 | AI/engineering research | Open-source desktop app for local LLMs. Text, vision, tool-calling, OpenAI/Anthropic-compatible API. 100% private. |
| [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V) | 25209 | 2026-05-23 | 88.9 | AI/engineering research | A Pocket-Sized MLLM for Ultra-Efficient Image and Video Understanding on Your Phone |
| [simular-ai/Agent-S](https://github.com/simular-ai/Agent-S) | 11580 | 2026-05-23 | 85.2 | AI/engineering research | Agent S: an open agentic framework that uses computers like a human |
| [microsoft/OmniParser](https://github.com/microsoft/OmniParser) | 24797 | 2026-05-23 | 85.1 | AI/engineering research | A simple screen parsing tool towards pure vision based GUI agent |
| [landing-ai/vision-agent](https://github.com/landing-ai/vision-agent) | 5284 | 2026-05-23 | 72.6 | AI/engineering research | This tool has been deprecated. Use Agentic Document Extraction instead. |

### Local LLM Inference & Routing
<a id="local_llm_inference_routing"></a>

Local model serving, LLM gateways, routers, proxy layers, and inference orchestration.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [ollama/ollama](https://github.com/ollama/ollama) | 172104 | 2026-05-23 | 98.2 | AI/engineering research | Get up and running with Kimi-K2.5, GLM-5, MiniMax, DeepSeek, gpt-oss, Qwen, Gemma and other models. |
| [open-webui/open-webui](https://github.com/open-webui/open-webui) | 138343 | 2026-05-23 | 97.1 | AI/engineering research | User-friendly AI Interface (Supports Ollama, OpenAI API, ...) |
| [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | 112451 | 2026-05-23 | 96.1 | AI/engineering research | LLM inference in C/C++ |
| [vllm-project/vllm](https://github.com/vllm-project/vllm) | 80797 | 2026-05-23 | 94.5 | AI/engineering research | A high-throughput and memory-efficient inference and serving engine for LLMs |
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | 48012 | 2026-05-23 | 92.0 | AI/engineering research | Python SDK, Proxy Server (AI Gateway) to call 100+ LLM APIs in OpenAI (or native) format, with cost tracking, guardrails, loadbalancing and logging. [Bedrock, Azure, O... |
| [lm-sys/FastChat](https://github.com/lm-sys/FastChat) | 39481 | 2026-05-23 | 87.3 | AI/engineering research | An open platform for training, serving, and evaluating large language models. Release repo for Vicuna and Chatbot Arena. |

### Vector DBs & Embedding Infrastructure
<a id="vector_databases_embedding_infra"></a>

Vector databases, embedding stores, ANN indexes, and retrieval storage infrastructure beyond SQLite-only tools.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [milvus-io/milvus](https://github.com/milvus-io/milvus) | 44417 | 2026-05-23 | 91.7 | AI/engineering research | Milvus is a high-performance, cloud-native vector database built for scalable vector ANN search |
| [facebookresearch/faiss](https://github.com/facebookresearch/faiss) | 40114 | 2026-05-23 | 91.2 | AI/engineering research | A library for efficient similarity search and clustering of dense vectors. |
| [qdrant/qdrant](https://github.com/qdrant/qdrant) | 31522 | 2026-05-23 | 90.0 | AI/engineering research | Qdrant - High-performance, massive-scale Vector Database and Vector Search Engine for the next generation of AI. Also available in the cloud https://cloud.qdrant.io/ |
| [chroma-core/chroma](https://github.com/chroma-core/chroma) | 28065 | 2026-05-23 | 89.4 | AI/engineering research | Search infrastructure for AI |
| [weaviate/weaviate](https://github.com/weaviate/weaviate) | 16229 | 2026-05-23 | 86.8 | AI/engineering research | Weaviate is an open-source vector database that stores both objects and vectors, allowing for the combination of vector search with structured filtering with the fault... |
| [lancedb/lancedb](https://github.com/lancedb/lancedb) | 10382 | 2026-05-23 | 84.6 | AI/engineering research | Developer-friendly OSS embedded retrieval library for multimodal AI. Search More; Manage Less. |

### Agentic Code Review & SWE
<a id="agentic_code_review_swe"></a>

SWE agents, coding benchmarks, code review automation, and repo-scale software engineering assistants.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | 74631 | 2026-05-23 | 94.2 | AI/engineering research | 🙌 OpenHands: AI-Driven Development |
| [Aider-AI/aider](https://github.com/Aider-AI/aider) | 45202 | 2026-05-23 | 91.7 | AI/engineering research | aider is AI pair programming in your terminal |
| [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | 19280 | 2026-05-23 | 87.6 | AI/engineering research | SWE-agent takes a GitHub issue and tries to automatically fix it, using your LM of choice. It can also be employed for offensive cybersecurity or competitive coding ch... |
| [langchain-ai/open-swe](https://github.com/langchain-ai/open-swe) | 9840 | 2026-05-23 | 84.4 | AI/engineering research | An Open-Source Asynchronous Coding Agent |
| [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench) | 4998 | 2026-05-23 | 77.4 | AI/engineering research | SWE-bench: Can Language Models Resolve Real-world Github Issues? |

### Web Crawling & Data Ingestion
<a id="web_crawling_data_ingestion"></a>

Crawling, scraping, browser extraction, and web-to-agent data ingestion.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 123306 | 2026-05-23 | 96.6 | AI/engineering research | 🔥 Search, scrape, and clean the web for AI agents. |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | 95207 | 2026-05-23 | 95.3 | AI/engineering research | 🌐 Make websites accessible for AI agents. Automate tasks online with ease. |
| [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | 66121 | 2026-05-23 | 93.6 | AI/engineering research | 🚀🤖 Crawl4AI: Open-source LLM Friendly Web Crawler & Scraper. Don't be shy, join here: https://discord.gg/jP8KfhDhyN |
| [ArchiveBox/ArchiveBox](https://github.com/ArchiveBox/ArchiveBox) | 27529 | 2026-05-23 | 89.4 | AI/engineering research | 🗃 Open source self-hosted web archiving. Takes URLs/browser history/bookmarks/Pocket/Pinboard/etc., saves HTML, JS, PDFs, media, and more... |
| [ScrapeGraphAI/Scrapegraph-ai](https://github.com/ScrapeGraphAI/Scrapegraph-ai) | 25773 | 2026-05-23 | 89.0 | AI/engineering research | Python scraper based on AI |

### Workflow State Machines & Durable Agents
<a id="workflow_state_machines_durable_agents"></a>

Durable workflows, state machines, background jobs, and long-running agent process control.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 32760 | 2026-05-23 | 90.2 | AI/engineering research | Build resilient agents. |
| [activepieces/activepieces](https://github.com/activepieces/activepieces) | 22369 | 2026-05-23 | 88.3 | AI/engineering research | AI Agents & MCPs & AI Workflow Automation • (~400 MCP servers for AI agents) • AI Automation / AI Agent with MCPs • AI Workflows & AI Agents • MCPs for AI Agents |
| [temporalio/temporal](https://github.com/temporalio/temporal) | 20456 | 2026-05-23 | 87.9 | AI/engineering research | Temporal service |
| [dagger/dagger](https://github.com/dagger/dagger) | 15857 | 2026-05-23 | 86.7 | AI/engineering research | Automation engine to build, test and ship any codebase. Runs locally, in CI, or directly in the cloud |
| [hatchet-dev/hatchet](https://github.com/hatchet-dev/hatchet) | 7205 | 2026-05-23 | 82.9 | AI/engineering research | 🪓 An orchestration engine for background tasks, AI agents, and durable workflows |
| [inngest/inngest](https://github.com/inngest/inngest) | 5394 | 2026-05-23 | 81.5 | AI/engineering research | The leading workflow orchestration platform. Run stateful step functions and AI workflows on serverless, servers, or the edge. |

### Benchmarks, Simulation & Synthetic Data
<a id="benchmarks_simulation_synthetic_data"></a>

Benchmarks, synthetic data generation, simulation environments, and scenario generation for agent testing.

Source groups: AI/engineering research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [faker-js/faker](https://github.com/faker-js/faker) | 15331 | 2026-05-23 | 86.5 | AI/engineering research | Generate massive amounts of fake data in the browser and node.js |
| [Farama-Foundation/Gymnasium](https://github.com/Farama-Foundation/Gymnasium) | 11929 | 2026-05-23 | 85.3 | AI/engineering research | An API standard for single-agent reinforcement learning environments, with popular reference environments and related utilities (formerly Gym) |
| [sdv-dev/SDV](https://github.com/sdv-dev/SDV) | 3493 | 2026-05-22 | 79.4 | AI/engineering research | Synthetic data generation for tabular data |
| [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench) | 4998 | 2026-05-23 | 77.4 | AI/engineering research | SWE-bench: Can Language Models Resolve Real-world Github Issues? |
| [gretelai/gretel-synthetics](https://github.com/gretelai/gretel-synthetics) | 679 | 2026-05-21 | 57.7 | AI/engineering research | Synthetic data generators for structured and unstructured text, featuring differentially private learning. |

### Marketing, Growth & SEO
<a id="marketing_growth_seo"></a>

Marketing automation, SEO, growth analytics, attribution, campaigns, and product-led growth tooling.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [umami-software/umami](https://github.com/umami-software/umami) | 36802 | 2026-05-22 | 90.4 | Business/product research | Umami is a modern, privacy-focused analytics platform. An open-source alternative to Google Analytics, Mixpanel and Amplitude. |
| [PostHog/posthog](https://github.com/PostHog/posthog) | 34657 | 2026-05-23 | 90.1 | Business/product research | 🦔 PostHog is an all-in-one developer platform for building successful products. We offer product analytics, web analytics, session replay, error tracking, feature flag... |
| [plausible/analytics](https://github.com/plausible/analytics) | 26424 | 2026-05-22 | 88.8 | Business/product research | Open source, privacy-first web analytics. Lightweight, cookie-free Google Analytics alternative. Self-hosted or cloud. |
| [matomo-org/matomo](https://github.com/matomo-org/matomo) | 21534 | 2026-05-22 | 87.8 | Business/product research | Empowering People Ethically 🚀 — Matomo is hiring! Join us → https://matomo.org/jobs Matomo is the leading open-source alternative to Google Analytics, giving you compl... |
| [mautic/mautic](https://github.com/mautic/mautic) | 9726 | 2026-05-22 | 83.8 | Business/product research | Mautic: Open Source Marketing Automation Software. |
| [growthbook/growthbook](https://github.com/growthbook/growthbook) | 7802 | 2026-05-23 | 82.7 | Business/product research | Open Source Feature Flags, Experimentation, and Product Analytics |
| [Countly/countly-server](https://github.com/Countly/countly-server) | 5866 | 2026-05-22 | 81.3 | Business/product research | Countly is a privacy-first, AI-powered analytics and engagement platform for understanding and optimizing customer journeys across digital applications, from desktop a... |
| [Openpanel-dev/openpanel](https://github.com/Openpanel-dev/openpanel) | 5800 | 2026-05-13 | 81.2 | Business/product research | OpenPanel is an open-source web and product analytics platform, an open-source alternative to Mixpanel with optional self-hosting. |

### Content, Social & Community
<a id="content_social_community"></a>

CMS, publishing, newsletters, social scheduling, community platforms, and content operations.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [usememos/memos](https://github.com/usememos/memos) | 60015 | 2026-05-16 | 92.9 | Business/product research | Open-source, self-hosted note-taking tool built for quick capture. Markdown-native, lightweight, and fully yours. |
| [TryGhost/Ghost](https://github.com/TryGhost/Ghost) | 53641 | 2026-05-23 | 92.3 | Business/product research | Independent technology for modern publishing, memberships, subscriptions and newsletters. |
| [mastodon/mastodon](https://github.com/mastodon/mastodon) | 49967 | 2026-05-23 | 92.0 | Business/product research | Your self-hosted, globally interconnected microblogging community |
| [discourse/discourse](https://github.com/discourse/discourse) | 47082 | 2026-05-23 | 91.7 | Business/product research | A platform for community discussion. Free, open, simple. |
| [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) | 30632 | 2026-05-22 | 89.5 | Business/product research | 📨 The ultimate agentic social media scheduling tool 🤖 |
| [inovector/mixpost](https://github.com/inovector/mixpost) | 3268 | 2026-03-16 | 69.6 | Business/product research | 📅 Schedule, 📢 publish, and ⚡ manage your social media content on your server. No subscriptions, no limits. (Buffer alternative) |
| [trypostit/trypost](https://github.com/trypostit/trypost) | 132 | 2026-05-22 | 62.4 | Business/product research | Open-source Social Media Scheduling. Contribute to trypostit/trypost development by creating an account on GitHub. |

### Design, Brand & UI/UX
<a id="design_brand_uiux"></a>

Design systems, prototyping, whiteboards, diagrams, UI builders, brand assets, and design workflow tools.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw) | 123893 | 2026-05-22 | 96.5 | Business/product research | Virtual whiteboard for sketching hand-drawn like diagrams |
| [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | 114912 | 2026-05-23 | 96.1 | Business/product research | A set of beautifully-designed, accessible components and a code distribution platform. Works with your favorite frameworks. Open Source. Open Code. |
| [storybookjs/storybook](https://github.com/storybookjs/storybook) | 90067 | 2026-05-23 | 94.9 | Business/product research | Storybook is the industry standard workshop for building, documenting, and testing UI components in isolation |
| [nexu-io/open-design](https://github.com/nexu-io/open-design) | 50457 | 2026-05-23 | 92.0 | Business/product research | 🎨 Local-first, open-source Claude Design alternative. ⚡ 19 Skills · ✨ 71 brand-grade Design Systems 🖼 Generate web · desktop · mobile pro… |
| [penpot/penpot](https://github.com/penpot/penpot) | 48275 | 2026-05-23 | 91.8 | Business/product research | Penpot: The open-source design tool for design and code collaboration |
| [tldraw/tldraw](https://github.com/tldraw/tldraw) | 47179 | 2026-05-22 | 91.7 | Business/product research | very good whiteboard infinite canvas SDK. Contribute to tldraw/tldraw development by creating an account on GitHub. |
| [bradtraversy/design-resources-for-developers](https://github.com/bradtraversy/design-resources-for-developers) | 65707 | 2026-04-13 | 89.6 | Business/product research | Curated list of design and UI resources from stock photos, web templates, CSS frameworks, UI libraries, tools and much more |
| [OpenCoworkAI/open-codesign](https://github.com/OpenCoworkAI/open-codesign) | 6336 | 2026-05-23 | 81.7 | Business/product research | Open-source Claude Design alternative. One-click import your Claude Code / Codex API key. Prompt → prototype / slides / PDF. Multi-model (Claude, GPT, Gemini, Kimi, GL... |
| [Vrun-design/openflowkit](https://github.com/Vrun-design/openflowkit) | 556 | 2026-05-13 | 69.5 | Business/product research | 100% Free, Open-source local-first AI diagramming for architecture diagrams and flowcharts with animated exports. |

### Sales, CRM & Lead Generation
<a id="sales_crm_lead_generation"></a>

CRM, lead management, outbound pipelines, enrichment, sales workflows, and account management.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [twentyhq/twenty](https://github.com/twentyhq/twenty) | 46065 | 2026-05-23 | 91.6 | Business/product research | The open alternative to Salesforce, designed for AI. |
| [frappe/erpnext](https://github.com/frappe/erpnext) | 34909 | 2026-05-23 | 90.2 | Business/product research | Free and Open Source Enterprise Resource Planning (ERP) |
| [monicahq/monica](https://github.com/monicahq/monica) | 24670 | 2026-03-30 | 84.7 | Business/product research | Personal CRM. Remember everything about your friends, family and business relationships. |
| [EspoCRM/EspoCRM](https://github.com/EspoCRM/EspoCRM) | 2975 | 2026-05-23 | 77.9 | Business/product research | EspoCRM – Open Source CRM Application. Contribute to espocrm/espocrm development by creating an account on GitHub. |
| [salesagility/SuiteCRM](https://github.com/salesagility/SuiteCRM) | 5455 | 2026-03-19 | 72.2 | Business/product research | SuiteCRM - Open source CRM for the world. Contribute to SuiteCRM/SuiteCRM development by creating an account on GitHub. |

### Fundraising, Investor Relations & Startup Ops
<a id="fundraising_investor_relations"></a>

Investor CRM, fundraising pipelines, pitch/deck workflows, cap tables, donation systems, startup operating systems, and venture research.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB) | 67984 | 2026-05-20 | 93.5 | Business/product research | Financial data platform for analysts, quants and AI agents. |
| [impress-org/givewp](https://github.com/impress-org/givewp) | 365 | 2026-05-19 | 67.4 | Business/product research | GiveWP - The #1 Donation Plugin for WordPress. Easily accept donations and fundraise using your WordPress website. |
| [houdiniproject/houdini](https://github.com/houdiniproject/houdini) | 231 | 2026-05-19 | 65.2 | Business/product research | Free and open source fundraising infrastructure for nonprofits and NGOs |
| [Open-Cap-Table-Coalition/Open-Cap-Format-OCF](https://github.com/Open-Cap-Table-Coalition/Open-Cap-Format-OCF) | 179 | 2026-05-20 | 63.9 | Business/product research | Open Cap Format (OCF) - The Open Source Company Capitalization Data Standard. OCF can be used to structure and track the complex data structures necessary to build and... |
| [wc-donation/wc-donation-platform](https://github.com/wc-donation/wc-donation-platform) | 62 | 2026-05-23 | 58.7 | Business/product research | Donation Platform for WooCommerce unleashes the power of WooCommerce for your online fundraising, crowdfunding & crowdsponsoring |
| [captableinc/captable](https://github.com/captableinc/captable) | 806 | 2025-06-04 | 57.6 | Business/product research | #1 Open-Source Captable, an alternative to Carta, Pully, Angelist and others. |

### Accounting, Finance & ERP
<a id="accounting_finance_erp"></a>

Bookkeeping, invoicing, accounting, ERP, budgeting, expenses, and finance back-office systems.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [frappe/erpnext](https://github.com/frappe/erpnext) | 34909 | 2026-05-23 | 90.2 | Business/product research | Free and Open Source Enterprise Resource Planning (ERP) |
| [actualbudget/actual](https://github.com/actualbudget/actual) | 26594 | 2026-05-23 | 88.8 | Business/product research | A local-first personal finance app. Contribute to actualbudget/actual development by creating an account on GitHub. |
| [odoo/odoo](https://github.com/odoo/odoo) | 51371 | 2026-04-22 | 88.4 | Business/product research | Odoo. Open Source Apps To Grow Your Business. Contribute to odoo/odoo development by creating an account on GitHub. |
| [firefly-iii/firefly-iii](https://github.com/firefly-iii/firefly-iii) | 23372 | 2026-05-21 | 88.2 | Business/product research | Firefly III: a personal finances manager. Contribute to firefly-iii/firefly-iii development by creating an account on GitHub. |
| [aureuserp/aureuserp](https://github.com/aureuserp/aureuserp) | 10611 | 2026-05-21 | 84.2 | Business/product research | Free and Open Source ERP platform |
| [idurar/idurar-erp-crm](https://github.com/idurar/idurar-erp-crm) | 8415 | 2026-05-12 | 83.1 | Business/product research | Free Open Source ERP CRM Software Accounting Invoicing \| Node Js React |
| [Dolibarr/dolibarr](https://github.com/Dolibarr/dolibarr) | 7233 | 2026-05-23 | 82.3 | Business/product research | Dolibarr ERP CRM is a modern software package to manage your company or foundation's activity (contacts, suppliers, invoices, orders, sto… |
| [ever-co/ever-gauzy](https://github.com/ever-co/ever-gauzy) | 3700 | 2026-05-22 | 79.0 | Business/product research | Ever® Gauzy™ - Open Business Management Platform (ERP/CRM/HRM/ATS/PM) - https://gauzy.co |
| [maybe-finance/maybe](https://github.com/maybe-finance/maybe) | 54134 | 2025-07-24 | 78.6 | Business/product research | The personal finance app for everyone. Contribute to maybe-finance/maybe development by creating an account on GitHub. |
| [invoiceplane/InvoicePlane](https://github.com/invoiceplane/InvoicePlane) | 3051 | 2026-05-23 | 78.0 | Business/product research | A self-hosted open source application for managing your invoices, clients and payments. - InvoicePlane/InvoicePlane |

### Legal, Contracts & Compliance
<a id="legal_contracts_compliance"></a>

Contracts, document automation, e-signature, privacy, governance, compliance, and policy operations.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [docusealco/docuseal](https://github.com/docusealco/docuseal) | 16893 | 2026-05-18 | 86.6 | Business/product research | Open source DocuSign alternative. Create, fill, and sign digital documents ✍️ |
| [prowler-cloud/prowler](https://github.com/prowler-cloud/prowler) | 13863 | 2026-05-23 | 85.6 | Business/product research | Prowler is the world’s most widely used open-source cloud security platform that automates security and compliance across any cloud envir… |
| [documenso/documenso](https://github.com/documenso/documenso) | 12929 | 2026-05-22 | 85.2 | Business/product research | The Open Source DocuSign Alternative. Contribute to documenso/documenso development by creating an account on GitHub. |
| [OpenSignLabs/OpenSign](https://github.com/OpenSignLabs/OpenSign) | 6424 | 2026-05-22 | 81.7 | Business/product research | 🔥 The free & Open Source DocuSign alternative |
| [opengovsg/FormSG](https://github.com/opengovsg/FormSG) | 352 | 2026-05-22 | 67.3 | Business/product research | Form builder for the Singapore Government. Contribute to opengovsg/FormSG development by creating an account on GitHub. |
| [accordproject/template-archive](https://github.com/accordproject/template-archive) | 345 | 2026-05-23 | 67.2 | Business/product research | Smart Legal Contracts & Templating System. Contribute to accordproject/template-archive development by creating an account on GitHub. |
| [Open-Cap-Table-Coalition/Open-Cap-Format-OCF](https://github.com/Open-Cap-Table-Coalition/Open-Cap-Format-OCF) | 179 | 2026-05-20 | 63.9 | Business/product research | Open Cap Format (OCF) - The Open Source Company Capitalization Data Standard. OCF can be used to structure and track the complex data structures necessary to build and... |
| [gorkem-bwl/atlas](https://github.com/gorkem-bwl/atlas) | 156 | 2026-05-22 | 63.2 | Business/product research | Self-hosted business platform with CRM, HRM, invoices, projects, e-signatures, calendar, drive, docs, drawing, and tasks. Multi-tenant, 5… |

### Analytics, BI & Reporting
<a id="analytics_bi_reporting"></a>

Dashboards, BI, metrics stores, product analytics, reporting, and executive visibility.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [grafana/grafana](https://github.com/grafana/grafana) | 73953 | 2026-05-23 | 93.9 | Business/product research | The open and composable observability and data visualization platform. Visualize metrics, logs, and traces from multiple sources like Prometheus, Loki, Elasticsearch,... |
| [apache/superset](https://github.com/apache/superset) | 72965 | 2026-05-23 | 93.9 | Business/product research | Apache Superset is a Data Visualization and Data Exploration Platform |
| [metabase/metabase](https://github.com/metabase/metabase) | 47421 | 2026-05-23 | 91.7 | Business/product research | The easy-to-use open source Business Intelligence and Embedded Analytics tool that lets everyone work with data :bar_chart: |
| [PostHog/posthog](https://github.com/PostHog/posthog) | 34657 | 2026-05-23 | 90.1 | Business/product research | 🦔 PostHog is an all-in-one developer platform for building successful products. We offer product analytics, web analytics, session replay, error tracking, feature flag... |
| [getredash/redash](https://github.com/getredash/redash) | 28591 | 2026-05-01 | 85.4 | Business/product research | Make Your Company Data Driven. Connect to any data source, easily visualize, dashboard and share your data. |

### Customer Support & Success
<a id="customer_support_success"></a>

Helpdesk, live chat, ticketing, customer success, knowledge support, and support automation.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [chatwoot/chatwoot](https://github.com/chatwoot/chatwoot) | 29666 | 2026-05-23 | 89.4 | Business/product research | Open-source live-chat, email support, omni-channel desk. An alternative to Intercom, Zendesk, Salesforce Service Cloud etc. 🔥💬 |
| [zammad/zammad](https://github.com/zammad/zammad) | 5627 | 2026-05-21 | 81.1 | Business/product research | Zammad is a web based open source helpdesk/customer support system. |
| [freescout-helpdesk/freescout](https://github.com/freescout-helpdesk/freescout) | 4277 | 2026-05-23 | 79.7 | Business/product research | FreeScout — Free self-hosted help desk & shared mailbox (Zendesk / Help Scout alternative) - freescout-help-desk/freescout |
| [frappe/helpdesk](https://github.com/frappe/helpdesk) | 3153 | 2026-05-21 | 78.2 | Business/product research | Modern, Streamlined, Free and Open Source Customer Service Software |
| [uvdesk/community-skeleton](https://github.com/uvdesk/community-skeleton) | 18679 | 2025-09-19 | 73.3 | Business/product research | UVdesk Open Source Community Helpdesk is a comprehensive ticketing support system designed for everyone, offering robust features to streamline customer support and co... |
| [helpyio/helpy](https://github.com/helpyio/helpy) | 2482 | 2023-03-08 | 58.2 | Business/product research | Helpy is a modern, open source helpdesk customer support application. Features include knowledgebase, community discussions and support tickets integrated with email. |
| [crisp-im/crisp-sdk-web](https://github.com/crisp-im/crisp-sdk-web) | 52 | 2026-04-21 | 54.1 | Business/product research | :package: Include the Crisp chat widget from using frameworks such as React, VueJS, Angular... |

### Product Management, Roadmaps & Feedback
<a id="product_management_feedback"></a>

Feature requests, roadmap planning, feedback collection, issue triage, changelogs, and product discovery.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [makeplane/plane](https://github.com/makeplane/plane) | 49602 | 2026-05-19 | 91.9 | Business/product research | 🔥🔥🔥 Open-source Jira, Linear, Monday, and ClickUp alternative. Plane is a modern project management platform to manage tasks, sprints, docs, and triage. |
| [getfider/fider](https://github.com/getfider/fider) | 4324 | 2026-05-22 | 79.8 | Business/product research | Open platform to collect and prioritize feedback. Contribute to getfider/fider development by creating an account on GitHub. |
| [logchimp/logchimp](https://github.com/logchimp/logchimp) | 1091 | 2026-05-21 | 72.9 | Business/product research | 🔥 🔥 🔥 Open Source Canny, ProductBoard, UserJot Alternative. Track your customers feedback to build better products with LogChimp. ⭐️ Star to support our work! |
| [QuackbackIO/quackback](https://github.com/QuackbackIO/quackback) | 101 | 2026-05-21 | 61.1 | Business/product research | Open source alternative to Canny, UserVoice, Productboard |
| [rowyio/roadmap](https://github.com/rowyio/roadmap) | 265 | 2023-01-26 | 47.1 | Business/product research | Roadmap voting app for sharing product plan and get customer feedback. - buildship-ai/roadmap |

### E-commerce, Payments & Revenue
<a id="ecommerce_payments_revenue"></a>

Commerce platforms, checkout, payments, billing, subscriptions, pricing, and revenue operations.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [medusajs/medusa](https://github.com/medusajs/medusa) | 33888 | 2026-05-22 | 90.0 | Business/product research | The world's most flexible commerce platform. Contribute to medusajs/medusa development by creating an account on GitHub. |
| [bagisto/bagisto](https://github.com/bagisto/bagisto) | 26891 | 2026-05-20 | 88.9 | Business/product research | Free and open source laravel eCommerce platform. Contribute to bagisto/bagisto development by creating an account on GitHub. |
| [saleor/saleor](https://github.com/saleor/saleor) | 22920 | 2026-05-22 | 88.1 | Business/product research | Saleor Core: the high performance, composable, headless commerce API. |
| [calcom/cal.com](https://github.com/calcom/cal.com) | 44405 | 2026-04-22 | 87.6 | Business/product research | Scheduling infrastructure for absolutely everyone. - calcom/cal.diy |
| [spree/spree](https://github.com/spree/spree) | 15429 | 2026-05-23 | 86.1 | Business/product research | Open-source headless eCommerce platform with REST API, TypeScript SDK, and Next.js storefront for cross-border, B2B or marketplace eComme… |
| [woocommerce/woocommerce](https://github.com/woocommerce/woocommerce) | 10306 | 2026-05-22 | 84.1 | Business/product research | A customizable, open-source ecommerce platform built on WordPress. Build any commerce solution you can imagine. |
| [Sylius/Sylius](https://github.com/Sylius/Sylius) | 8474 | 2026-05-23 | 83.1 | Business/product research | Headless open-source eCommerce platform on top of PHP/Symfony/API Platform |
| [vendure-ecommerce/vendure](https://github.com/vendure-ecommerce/vendure) | 8147 | 2026-05-22 | 82.9 | Business/product research | Open source headless commerce framework built with TypeScript, NestJS, React and GraphQL - vendurehq/vendure |
| [btcpayserver/btcpayserver](https://github.com/btcpayserver/btcpayserver) | 7578 | 2026-05-19 | 82.6 | Business/product research | Accept Bitcoin payments. Free, open-source & self-hosted, Bitcoin payment processor. |
| [KillBill/killbill](https://github.com/KillBill/killbill) | 5550 | 2026-05-22 | 81.0 | Business/product research | Open-Source Subscription Billing & Payments Platform - killbill/killbill |

### HR, Recruiting & People Ops
<a id="hr_recruiting_people_ops"></a>

Recruiting, applicant tracking, HRIS, payroll-adjacent workflows, employee operations, and team directories.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [frappe/hrms](https://github.com/frappe/hrms) | 7999 | 2026-05-23 | 82.8 | Business/product research | Open Source HR and Payroll Software. Contribute to frappe/hrms development by creating an account on GitHub. |
| [ever-co/ever-gauzy](https://github.com/ever-co/ever-gauzy) | 3700 | 2026-05-22 | 79.0 | Business/product research | Ever® Gauzy™ - Open Business Management Platform (ERP/CRM/HRM/ATS/PM) - https://gauzy.co |
| [horilla/horilla-hr](https://github.com/horilla/horilla-hr) | 1226 | 2026-05-23 | 73.5 | Business/product research | Horilla is a free and open source HR and CRM software. |
| [opencats/OpenCATS](https://github.com/opencats/OpenCATS) | 681 | 2026-05-20 | 70.5 | Business/product research | Open-source applicant tracking system (ATS) and recruitment CRM for staffing agencies and hiring teams. |
| [profilecity/vidur](https://github.com/profilecity/vidur) | 428 | 2026-04-07 | 64.5 | Business/product research | [WIP] OpenSource ATS. Contribute to profilecity/vidur development by creating an account on GitHub. |
| [reqcore-inc/reqcore](https://github.com/reqcore-inc/reqcore) | 29 | 2026-05-23 | 55.0 | Business/product research | The open-source applicant tracking system. Contribute to reqcore-inc/reqcore development by creating an account on GitHub. |
| [freeats/freeats](https://github.com/freeats/freeats) | 46 | 2025-06-09 | 43.5 | Business/product research | Contribute to freeats/freeats development by creating an account on GitHub. |

### Operations, Project Management & Internal Tools
<a id="operations_project_management"></a>

Project management, internal tools, admin panels, task systems, workflows, and operational command centers.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [makeplane/plane](https://github.com/makeplane/plane) | 49602 | 2026-05-19 | 91.9 | Business/product research | 🔥🔥🔥 Open-source Jira, Linear, Monday, and ClickUp alternative. Plane is a modern project management platform to manage tasks, sprints, docs, and triage. |
| [appsmithorg/appsmith](https://github.com/appsmithorg/appsmith) | 39887 | 2026-05-22 | 90.8 | Business/product research | Platform to build admin panels, internal tools, and dashboards. Integrates with 25+ databases and any API. |
| [ToolJet/ToolJet](https://github.com/ToolJet/ToolJet) | 37930 | 2026-05-22 | 90.6 | Business/product research | ToolJet is the open-source foundation of ToolJet AI - the enterprise app generation platform for building internal tools, dashboard, business applications, workflows a... |
| [Budibase/budibase](https://github.com/Budibase/budibase) | 27943 | 2026-05-22 | 89.1 | Business/product research | AI agents, automations and apps that run your operations. Model agnostic. |
| [taigaio/taiga](https://github.com/taigaio/taiga) | 559 | 2023-12-13 | 50.8 | Business/product research | Taiga is a free and open-source project management for cross-functional agile teams. - kaleidos-ventures/taiga |

### Automation, Workflows & No-code
<a id="automation_workflows_nocode"></a>

Workflow builders, no-code/low-code automation, integrations, scheduling, and internal process automation.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | 189383 | 2026-05-23 | 98.6 | Business/product research | Fair-code workflow automation platform with native AI capabilities. Combine visual building with custom code, self-host or cloud, 400+ integrations. |
| [huginn/huginn](https://github.com/huginn/huginn) | 49320 | 2026-05-23 | 91.9 | Business/product research | Create agents that monitor and act on your behalf. Your agents are standing by! |
| [NaiboWang/EasySpider](https://github.com/NaiboWang/EasySpider) | 43857 | 2026-05-22 | 91.3 | Business/product research | A visual no-code/code-free web crawler/spider易采集：一个可视化浏览器自动化测试/数据采集/网页爬虫软件，可以无代码图形化的设计和执行爬虫任务。别名：ServiceWrapper面向Web应用的智能化服务封装系统。 |
| [activepieces/activepieces](https://github.com/activepieces/activepieces) | 22369 | 2026-05-23 | 88.0 | Business/product research | AI Agents & MCPs & AI Workflow Automation • (~400 MCP servers for AI agents) • AI Automation / AI Agent with MCPs • AI Workflows & AI Agents • MCPs for AI Agents |
| [windmill-labs/windmill](https://github.com/windmill-labs/windmill) | 16557 | 2026-05-22 | 86.5 | Business/product research | Open-source developer platform to power your entire infra and turn scripts into webhooks, workflows and UIs. Fastest workflow engine (13x vs Airflow). Open-source alte... |
| [automatisch/automatisch](https://github.com/automatisch/automatisch) | 13851 | 2026-02-11 | 76.8 | Business/product research | The open source Zapier alternative. Build workflow automation without spending time and money. |

### Market Research & Competitive Intelligence
<a id="market_research_competitive_intel"></a>

Research, web monitoring, trend detection, OSINT, scraping, social listening, and competitive intelligence.

Source groups: Business/product research

| Repository | Stars | Updated | Score | Source | Description |
|---|---:|---|---:|---|---|
| [mendableai/firecrawl](https://github.com/mendableai/firecrawl) | 123326 | 2026-05-23 | 96.5 | Business/product research | 🔥 Search, scrape, and clean the web for AI agents. - firecrawl/firecrawl |
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | 124781 | 2026-04-20 | 92.8 | Business/product research | Python tool for converting files and office documents to Markdown. |
| [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) | 58076 | 2026-05-23 | 92.7 | Business/product research | ⭐AI-driven public opinion & trend monitor with multi-platform aggregation, RSS, and smart alerts.🎯 告别信息过载，你的 AI 舆情监控助手与热点筛选工具！聚合多平台热点 + RSS 订阅，支持关键词精准筛选。AI 智能筛选新闻 + AI... |
| [lissy93/web-check](https://github.com/lissy93/web-check) | 33156 | 2026-05-23 | 89.9 | Business/product research | 🕵️‍♂️ All-in-one OSINT tool for analysing any website |
| [dgtlmoon/changedetection.io](https://github.com/dgtlmoon/changedetection.io) | 31672 | 2026-05-23 | 89.7 | Business/product research | Best and simplest tool for website change detection, web page monitoring, and website change alerts. Perfect for tracking content changes, price drops, restock alerts,... |
| [ArchiveBox/ArchiveBox](https://github.com/ArchiveBox/ArchiveBox) | 27529 | 2026-05-22 | 89.0 | Business/product research | 🗃 Open source self-hosted web archiving. Takes URLs/browser history/bookmarks/Pocket/Pinboard/etc., saves HTML, JS, PDFs, media, and more... |
