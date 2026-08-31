# Catalog taxonomy v2: exact planning registry

Date: 2026-08-31. Scope: owner-requested category proposal and PLAN update only. Owner: primary curator; single writer and explicit self-review.

**This revision replaces the 88-node taxonomy proposal for future CAT work, not the frozen source or the field contract. No catalog migration or GitHub refresh occurred.**

## Exact structural totals

| Measure | Count |
| --- | ---: |
| old_nodes | 77 |
| retained_old_ids | 75 |
| retired_old_ids | 2 |
| new_ids | 51 |
| total_nodes | 126 |
| containers | 14 |
| thematic_categories | 111 |
| review_queues | 1 |
| assignable | 112 |
| top_level | 76 |
| child_categories | 50 |

**77 - 2 + 51 = 126 nodes = 111 thematic categories + 14 navigation containers + 1 review queue.** There are 76 top-level nodes and 50 children. Compared with v1, add 38 child definitions and convert 11 more existing nodes into containers. All 51 new categories have at least two examples already in the frozen corpus; no new discovery is assumed.

These are exact vocabulary counts, not final populated-category or repository totals. The 77 source groups contain 2,155 memberships across 1,800 records. Final primary/member/parent-union counts follow CAT05-07; do not invent a numeric allocation from incomplete descriptions or sum overlapping groups.

## Categories being split

The source count includes primary and secondary memberships. Each row retains the old ID as a non-assignable container; old members require review and can also move to an existing external domain.

| Old category | Source members | New container | Exact new child labels | Children |
| --- | ---: | --- | --- | ---: |
| Developer Tools & CLI | 76 | Developer Tooling | Code Editors & IDEs; Terminals & Shell Tools; Package & Version Management; Build Systems & Language Toolchains; Code Quality & Static Analysis; Development Environments & Workspaces | 6 |
| Testing, QA & Performance | 38 | Software Testing | Unit & Component Testing; Browser & Mobile Testing; API & Contract Testing; Load & Performance Testing | 4 |
| Files, Media & Asset Processing | 29 | Files & Media | File Management & Synchronization; Media Libraries & Readers; File Upload Infrastructure; Media Processing & Playback; Document Management & Processing | 5 |
| Frontend Frameworks & UI Components | 88 | Frontend Development | Web Application Frameworks; UI Components & Design Systems; Frontend State & Data Management; Forms & Input Validation; Graphics & Data Visualization | 5 |
| Accounting, Finance & ERP | 39 | Finance & ERP | ERP; Accounting & Invoicing; Personal Finance; Financial Market Data & Trading Tools | 4 |
| CMS, Publishing & Knowledge Apps | 20 | Content Publishing | Content Management Systems; Documentation & Static Site Generators | 2 |
| Communications & Personal Ops | 38 | Communication & Personal Productivity | Messaging & Chat; Video Conferencing & Meetings; Scheduling & Personal Productivity | 3 |
| E-commerce, Payments & Revenue | 32 | Commerce & Payments | E-commerce Platforms; Payment Processing & SDKs; Subscription Billing | 3 |
| Operations, Project Management & Internal Tools | 21 | Project & Internal Operations | Project & Task Management; Internal Tools & Admin Builders | 2 |
| Data Ingestion, ETL & CDC | 42 | Data Engineering | Data Ingestion, ETL & CDC; Data Processing & Compute; Data Lakes & Object Storage; Data Catalogs & Lineage | 4 |
| Databases, Storage & Caching | 71 | Databases & Data Tools | Database Engines; Caching & Key-Value Stores; Database Clients & Administration | 3 |
| Backend, BaaS & API Platforms | 71 | Backend Development | Backend Application Frameworks; Backend as a Service | 2 |
| Deployment, Containers & PaaS | 75 | Deployment & Infrastructure | Containers & Kubernetes; Infrastructure as Code & Configuration Management; Application Deployment Platforms; Networking, Proxies & API Gateways | 4 |
| Supply-chain Security & DevSecOps | 62 | Software & Infrastructure Security | Software Supply-chain Security; Infrastructure Security & Detection; Security Testing & Vulnerability Assessment | 3 |

Standalone addition: **Game Engines** (`game_engines`), supported by the existing Godot and Bevy snapshot records.

## Retired IDs and scope refinements

- Retire `frontend_ui_desktop_browser` (18 source memberships): explicit routes to frontend leaves, application UI, design, mobile/desktop frameworks, computer use, Game Engines, media and communication domains; unresolved applications stay in review.
- Retire `evals_observability_promptops` (21 source memberships): reuse AI Evaluation & Benchmarks, LLM Observability & Tracing, datasets, MCP infrastructure, agent runtime and AI security as supported. The earlier 32-record comparison was a combined evaluation cohort, not this single category.
- Reuse existing IDs for Knowledge & Collaborative Workspaces; Social Publishing & Communities; Graph Databases & Knowledge Graphs; AI Evaluation & Benchmarks; LLM Observability & Tracing; MCP Infrastructure & Tooling. These are refinements, not additional categories.
- Move CI/CD outliers from deployment/developer tools into the existing CI/CD domain; CMS/ORM/API outliers from backend into their domains; vector/search/graph systems from generic databases into their specific domains; analytics and feature flags from observability into existing domains.
- Keep mobile/desktop platform support, CLI, MCP, audio modality and similar cross-cutting capabilities as facets. Do not split every compound name. Retain the sparse dataset/training/governance domains and the empty embedding category; their counts are honest, not evidence of completeness.

## Complete exact list

Every one of the 126 nodes appears once below. Container means navigation only; category means assignable thematic leaf; review_bucket is service-only. IDs remain canonical English identifiers, independent of future RU/EN labels.

| No. | ID | Exact label | Kind | Parent | New ID |
| ---: | --- | --- | --- | --- | --- |
| 1 | `coding_agents_devex` | Coding Agents & Developer Experience | category | - | no |
| 2 | `developer_tools_cli_general` | Developer Tooling | container | - | no |
| 3 | `editors_ides` | Code Editors & IDEs | category | Developer Tooling | yes |
| 4 | `terminals_shells` | Terminals & Shell Tools | category | Developer Tooling | yes |
| 5 | `package_version_management` | Package & Version Management | category | Developer Tooling | yes |
| 6 | `build_systems_toolchains` | Build Systems & Language Toolchains | category | Developer Tooling | yes |
| 7 | `code_quality` | Code Quality & Static Analysis | category | Developer Tooling | yes |
| 8 | `development_environments` | Development Environments & Workspaces | category | Developer Tooling | yes |
| 9 | `evals_benchmarks` | AI Evaluation & Benchmarks | category | - | no |
| 10 | `market_research_competitive_intel` | Market Research & Competitive Intelligence | category | - | no |
| 11 | `observability_monitoring` | Observability, Monitoring & Telemetry | category | - | no |
| 12 | `observability_llmops` | LLM Observability & Tracing | category | - | no |
| 13 | `prompt_context_engineering` | Prompt & Context Engineering | category | - | no |
| 14 | `research_papers_science` | Research, Papers & Science | category | - | no |
| 15 | `testing_qa` | Software Testing | container | - | no |
| 16 | `unit_component_testing` | Unit & Component Testing | category | Software Testing | yes |
| 17 | `browser_mobile_testing` | Browser & Mobile Testing | category | Software Testing | yes |
| 18 | `api_contract_testing` | API & Contract Testing | category | Software Testing | yes |
| 19 | `load_performance_testing` | Load & Performance Testing | category | Software Testing | yes |
| 20 | `agent_protocols_interop` | Agent Protocols & Interoperability | category | - | no |
| 21 | `agent_runtime_orchestration` | Agent Runtime & Orchestration | category | - | no |
| 22 | `automation_workflows_nocode` | Automation, Workflows & No-code | category | - | no |
| 23 | `browser_computer_use` | Browser & Computer Use | category | - | no |
| 24 | `mcp_integrations` | MCP Infrastructure & Tooling | category | - | no |
| 25 | `multi_agent_frameworks` | Multi-Agent Frameworks | category | - | no |
| 26 | `sandboxed_code_execution` | Sandboxed Code Execution | category | - | no |
| 27 | `workflow_state_machines_durable_agents` | Workflow State Machines & Durable Agents | category | - | no |
| 28 | `ai_application_ui` | AI Application UI & Chat UI | category | - | no |
| 29 | `email_notifications` | Email, Notifications & Delivery | category | - | no |
| 30 | `files_media_storage` | Files & Media | container | - | no |
| 31 | `file_management_sync` | File Management & Synchronization | category | Files & Media | yes |
| 32 | `media_libraries_readers` | Media Libraries & Readers | category | Files & Media | yes |
| 33 | `file_upload_infrastructure` | File Upload Infrastructure | category | Files & Media | yes |
| 34 | `media_processing_playback` | Media Processing & Playback | category | Files & Media | yes |
| 35 | `document_management_processing` | Document Management & Processing | category | Files & Media | yes |
| 36 | `frontend_frameworks_ui` | Frontend Development | container | - | no |
| 37 | `frontend_web_frameworks` | Web Application Frameworks | category | Frontend Development | yes |
| 38 | `ui_component_libraries` | UI Components & Design Systems | category | Frontend Development | yes |
| 39 | `frontend_state_data` | Frontend State & Data Management | category | Frontend Development | yes |
| 40 | `forms_validation` | Forms & Input Validation | category | Frontend Development | yes |
| 41 | `graphics_visualization` | Graphics & Data Visualization | category | Frontend Development | yes |
| 42 | `low_code_ai_builders` | Low-code / No-code AI Builders | category | - | no |
| 43 | `mobile_desktop_frameworks` | Mobile & Desktop App Frameworks | category | - | no |
| 44 | `accounting_finance_erp` | Finance & ERP | container | - | no |
| 45 | `erp_business_suites` | ERP | category | Finance & ERP | yes |
| 46 | `accounting_invoicing` | Accounting & Invoicing | category | Finance & ERP | yes |
| 47 | `personal_finance` | Personal Finance | category | Finance & ERP | yes |
| 48 | `financial_market_tools` | Financial Market Data & Trading Tools | category | Finance & ERP | yes |
| 49 | `analytics_bi_reporting` | Analytics, BI & Reporting | category | - | no |
| 50 | `cms_content_knowledge` | Content Publishing | container | - | no |
| 51 | `content_management_systems` | Content Management Systems | category | Content Publishing | yes |
| 52 | `documentation_site_generators` | Documentation & Static Site Generators | category | Content Publishing | yes |
| 53 | `collaboration_knowledge` | Knowledge & Collaborative Workspaces | category | - | no |
| 54 | `communications_personal_ops` | Communication & Personal Productivity | container | - | no |
| 55 | `messaging_chat` | Messaging & Chat | category | Communication & Personal Productivity | yes |
| 56 | `video_conferencing` | Video Conferencing & Meetings | category | Communication & Personal Productivity | yes |
| 57 | `scheduling_personal_productivity` | Scheduling & Personal Productivity | category | Communication & Personal Productivity | yes |
| 58 | `content_social_community` | Social Publishing & Communities | category | - | no |
| 59 | `customer_support_success` | Customer Support & Success | category | - | no |
| 60 | `design_brand_uiux` | Design, Brand & UI/UX | category | - | no |
| 61 | `ecommerce_payments_revenue` | Commerce & Payments | container | - | no |
| 62 | `ecommerce_platforms` | E-commerce Platforms | category | Commerce & Payments | yes |
| 63 | `payment_processing_sdks` | Payment Processing & SDKs | category | Commerce & Payments | yes |
| 64 | `subscription_billing` | Subscription Billing | category | Commerce & Payments | yes |
| 65 | `fundraising_investor_relations` | Fundraising, Investor Relations & Startup Ops | category | - | no |
| 66 | `hr_recruiting_people_ops` | HR, Recruiting & People Ops | category | - | no |
| 67 | `legal_contracts_compliance` | Legal, Contracts & Compliance | category | - | no |
| 68 | `marketing_growth_seo` | Marketing, Growth & SEO | category | - | no |
| 69 | `operations_project_management` | Project & Internal Operations | container | - | no |
| 70 | `project_task_management` | Project & Task Management | category | Project & Internal Operations | yes |
| 71 | `internal_tools_builders` | Internal Tools & Admin Builders | category | Project & Internal Operations | yes |
| 72 | `product_management_feedback` | Product Management, Roadmaps & Feedback | category | - | no |
| 73 | `sales_crm_lead_generation` | Sales, CRM & Lead Generation | category | - | no |
| 74 | `data_ingestion_etl_cdc` | Data Engineering | container | - | no |
| 75 | `data_ingestion_connectors` | Data Ingestion, ETL & CDC | category | Data Engineering | yes |
| 76 | `data_processing_compute` | Data Processing & Compute | category | Data Engineering | yes |
| 77 | `data_lakes_object_storage` | Data Lakes & Object Storage | category | Data Engineering | yes |
| 78 | `data_catalogs_lineage` | Data Catalogs & Lineage | category | Data Engineering | yes |
| 79 | `databases_storage_caching` | Databases & Data Tools | container | - | no |
| 80 | `database_engines` | Database Engines | category | Databases & Data Tools | yes |
| 81 | `caches_key_value_stores` | Caching & Key-Value Stores | category | Databases & Data Tools | yes |
| 82 | `database_clients_admin` | Database Clients & Administration | category | Databases & Data Tools | yes |
| 83 | `datasets_synthetic_labeling` | Datasets, Synthetic Data & Labeling | category | - | no |
| 84 | `document_ai_ocr_parsing` | Document AI, OCR & Parsing | category | - | no |
| 85 | `knowledge_graphs` | Graph Databases & Knowledge Graphs | category | - | no |
| 86 | `memory_context_systems` | Memory & Context Systems | category | - | no |
| 87 | `rag_knowledge_apps` | RAG Frameworks & Knowledge Apps | category | - | no |
| 88 | `search_hybrid_retrieval` | Search & Hybrid Retrieval | category | - | no |
| 89 | `vector_databases_search` | Vector Databases & Vector Search | category | - | no |
| 90 | `web_crawling_data_ingestion` | Web Crawling & Data Ingestion | category | - | no |
| 91 | `api_graphql_rpc` | APIs, GraphQL, RPC & Schemas | category | - | no |
| 92 | `auth_identity_access` | Authentication, Identity & Access | category | - | no |
| 93 | `backend_baas_api` | Backend Development | container | - | no |
| 94 | `backend_frameworks` | Backend Application Frameworks | category | Backend Development | yes |
| 95 | `baas_platforms` | Backend as a Service | category | Backend Development | yes |
| 96 | `ci_cd_release` | CI/CD, Release & Delivery | category | - | no |
| 97 | `deployment_containers_paas` | Deployment & Infrastructure | container | - | no |
| 98 | `container_platforms` | Containers & Kubernetes | category | Deployment & Infrastructure | yes |
| 99 | `infrastructure_automation` | Infrastructure as Code & Configuration Management | category | Deployment & Infrastructure | yes |
| 100 | `application_paas` | Application Deployment Platforms | category | Deployment & Infrastructure | yes |
| 101 | `network_proxies_gateways` | Networking, Proxies & API Gateways | category | Deployment & Infrastructure | yes |
| 102 | `feature_flags_config` | Feature Flags & Configuration | category | - | no |
| 103 | `mlops_tracking_registry` | MLOps, Experiment Tracking & Registry | category | - | no |
| 104 | `orm_data_access` | ORM, Query Builders & Data Access | category | - | no |
| 105 | `queues_streaming_messaging` | Queues, Streaming & Messaging | category | - | no |
| 106 | `distributed_training_acceleration` | Distributed Training & Acceleration | category | - | no |
| 107 | `embeddings_reranking` | Embeddings & Reranking | category | - | no |
| 108 | `foundation_models` | Foundation Model Implementations | category | - | no |
| 109 | `inference_model_serving` | Inference Engines & Model Serving | category | - | no |
| 110 | `llm_gateways_routing_caching` | LLM Gateways, Routing & Caching | category | - | no |
| 111 | `training_finetuning_alignment` | Training, Fine-tuning & Alignment | category | - | no |
| 112 | `edge_on_device_ai` | Edge & On-device AI | category | - | no |
| 113 | `image_video_generation` | Image & Video Generation | category | - | no |
| 114 | `speech_voice_audio` | Speech, Voice & Audio AI | category | - | no |
| 115 | `vision_multimodal` | Vision & Multimodal AI | category | - | no |
| 116 | `uncategorized_review` | Uncategorized / Needs Review | review_bucket | - | no |
| 117 | `learning_reference_resources` | Learning, Research & Curated Lists | category | - | no |
| 118 | `research_agents_deep_research` | Research Agents & Deep Research | category | - | no |
| 119 | `robotics_embodied_ai` | Robotics & Embodied AI | category | - | no |
| 120 | `ai_security_guardrails_redteam` | AI Security, Guardrails & Red Teaming | category | - | no |
| 121 | `governance_policy_compliance` | Governance, Policy & Compliance | category | - | no |
| 122 | `supply_chain_devsecops` | Software & Infrastructure Security | container | - | no |
| 123 | `software_supply_chain_security` | Software Supply-chain Security | category | Software & Infrastructure Security | yes |
| 124 | `infrastructure_security` | Infrastructure Security & Detection | category | Software & Infrastructure Security | yes |
| 125 | `security_testing` | Security Testing & Vulnerability Assessment | category | Software & Infrastructure Security | yes |
| 126 | `game_engines` | Game Engines | category | - | yes |

## Decisions for all 77 source categories

| Old ID | Members / primary / missing description | Decision | Rationale |
| --- | --- | --- | --- |
| `coding_agents_devex` | 97 / 86 / 3 | retain_id_refine_scope_and_redistribute | General editors without an agent-centric purpose, shell tools and ordinary release automation. |
| `developer_tools_cli_general` | 76 / 75 / 40 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `evals_benchmarks` | 10 / 9 / 0 | retain_id_refine_scope_and_redistribute | Generic synthetic-data generators belong to Datasets; telemetry-first tools belong to LLM Observability; MCP inspectors belong to MCP Infrastructure & Tooling. |
| `evals_observability_promptops` | 21 / 19 / 9 | retire_and_redistribute | Mixed legacy category duplicates existing or newly defined domains; explicit per-record migration, not a one-to-one alias. |
| `market_research_competitive_intel` | 13 / 10 / 0 | retain_without_split | Keep market/competitive business research; generic crawling infrastructure has an existing category. |
| `observability_monitoring` | 43 / 30 / 25 | retain_id_refine_scope_and_redistribute | Product analytics/BI, feature flags and LLM-specialized tracing as a primary function. |
| `observability_llmops` | 2 / 2 / 0 | retain_id_refine_scope_and_redistribute | General infrastructure telemetry and primarily evaluation-only frameworks; multi-function tools may retain evaluation as secondary. |
| `prompt_context_engineering` | 4 / 3 / 0 | retain_without_split | Keep prompt/structured-output/context composition tools; persistent memory and retrieval have existing categories. |
| `research_papers_science` | 9 / 8 / 1 | retain_without_split | Keep scientific workflow/paper tooling; distinguish research-agent applications and educational reference lists. |
| `testing_qa` | 38 / 35 / 30 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `agent_protocols_interop` | 30 / 22 / 0 | retain_without_split | Keep non-MCP interoperability infrastructure; protocol support alone is a facet, not primary eligibility. |
| `agent_runtime_orchestration` | 63 / 59 / 0 | retain_without_split | Keep general agent execution; use multi-agent and durable execution categories only when those are the principal capability. |
| `automation_workflows_nocode` | 27 / 17 / 10 | retain_without_split | Keep general automation/integration builders; low-code/no-code is a form facet, not another split. |
| `browser_computer_use` | 33 / 20 / 5 | retain_without_split | Keep agent browser/computer task execution; test-first frameworks use Software Testing leaves. |
| `mcp_integrations` | 240 / 106 / 8 | retain_id_refine_scope_and_redistribute | MCP infrastructure stays here; domain connectors use the evidenced functional primary plus protocol=mcp. |
| `multi_agent_frameworks` | 15 / 15 / 0 | retain_without_split | Keep explicit agent-team coordination; do not split teams/swarms into new categories. |
| `sandboxed_code_execution` | 10 / 7 / 0 | retain_without_split | Keep restricted code execution for agents; full developer workspaces and container engines are distinct. |
| `workflow_state_machines_durable_agents` | 8 / 5 / 0 | retain_without_split | Keep persistent workflow/state-machine execution; route ETL-specific orchestration to its demonstrated domain. |
| `ai_application_ui` | 11 / 11 / 0 | retain_without_split | Keep AI/agent-facing application UIs; generic components and internal admin builders remain separate. |
| `email_notifications` | 19 / 18 / 17 | retain_without_split | Keep email/notification delivery infrastructure; social/community publishing and human chat are distinct. |
| `files_media_storage` | 29 / 29 / 22 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `frontend_frameworks_ui` | 88 / 84 / 66 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `frontend_ui_desktop_browser` | 18 / 18 / 0 | retire_and_redistribute | Mixed legacy category duplicates existing or newly defined domains; explicit per-record migration, not a one-to-one alias. |
| `low_code_ai_builders` | 2 / 2 / 0 | retain_without_split | Keep AI-specific visual builders; distinguish general business automation and internal admin builders. |
| `mobile_desktop_frameworks` | 36 / 35 / 15 | retain_id_refine_scope_and_redistribute | Finished utilities, music players, terminals, remote-desktop products and database SDKs without a framework role. |
| `accounting_finance_erp` | 39 / 34 / 6 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `analytics_bi_reporting` | 9 / 7 / 0 | retain_id_refine_scope_and_redistribute | Operational host/application telemetry and general data processing engines. |
| `cms_content_knowledge` | 20 / 19 / 18 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `collaboration_knowledge` | 26 / 16 / 17 | retain_id_refine_scope_and_redistribute | CMS publishing, docs-site generators, chat/conferencing and file-storage infrastructure. |
| `communications_personal_ops` | 38 / 32 / 13 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `content_social_community` | 18 / 17 / 0 | retain_id_refine_scope_and_redistribute | General CMS/blog backends, transactional email, internal chat and marketing analytics. |
| `customer_support_success` | 7 / 7 / 0 | retain_without_split | Keep customer-facing support/ticketing workflows; generic chat is not automatically customer support. |
| `design_brand_uiux` | 17 / 16 / 0 | retain_id_refine_scope_and_redistribute | Reusable UI components and chart/graphics engines; classify these by their development function. |
| `ecommerce_payments_revenue` | 32 / 32 / 21 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `fundraising_investor_relations` | 6 / 6 / 0 | retain_without_split | Keep fundraising/investor workflows; do not turn general startup operations into this primary. |
| `hr_recruiting_people_ops` | 11 / 10 / 0 | retain_without_split | Keep recruiting/people workflows; individual reminders and generic calendars use personal productivity. |
| `legal_contracts_compliance` | 9 / 8 / 0 | retain_without_split | Keep legal documents/contracts/e-signature workflows; machine policy enforcement belongs to Governance. |
| `marketing_growth_seo` | 12 / 12 / 0 | retain_without_split | Keep marketing/campaign/search-optimization outcomes; BI and publishing infrastructure have separate domains. |
| `operations_project_management` | 21 / 20 / 13 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `product_management_feedback` | 5 / 5 / 0 | retain_without_split | Keep product discovery/feedback/roadmap outcomes; delivery boards and project tasks use Project Management. |
| `sales_crm_lead_generation` | 5 / 5 / 0 | retain_without_split | Keep the sales/CRM workflow; no tiny separate lead-generation category from five members. |
| `data_ingestion_etl_cdc` | 42 / 40 / 37 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `databases_storage_caching` | 71 / 70 / 39 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `datasets_synthetic_labeling` | 3 / 3 / 0 | retain_without_split | Keep one dataset preparation/evaluation domain: only three current members; no one-example synthetic-data category. |
| `document_ai_ocr_parsing` | 18 / 14 / 4 | retain_without_split | Keep extraction/OCR/layout ingestion engines; document repositories and office workflows are distinct. |
| `knowledge_graphs` | 10 / 7 / 0 | retain_id_refine_scope_and_redistribute | Vector-only search, generic relational engines and mere graph visualization. |
| `memory_context_systems` | 29 / 22 / 2 | retain_without_split | Keep durable agent memory/context stores; avoid duplicating graph/vector engines and prompt utilities. |
| `rag_knowledge_apps` | 55 / 51 / 13 | retain_without_split | Keep end-to-end RAG application frameworks; retrieval engines and human knowledge workspaces remain separate. |
| `search_hybrid_retrieval` | 34 / 22 / 18 | retain_without_split | Keep general full-text/hybrid retrieval engines; vector-first and graph-first systems retain specific primaries. |
| `vector_databases_search` | 9 / 4 / 0 | retain_without_split | Keep vector-first engines/indexes/extensions; vector support alone does not reclassify a general database. |
| `web_crawling_data_ingestion` | 17 / 12 / 0 | retain_without_split | Keep web acquisition/extraction infrastructure; generic ETL and domain research agents remain separate. |
| `api_graphql_rpc` | 35 / 33 / 25 | retain_without_split | Keep API protocol/schema/client-generation primitives; server applications and API testing have separate domains. |
| `auth_identity_access` | 27 / 27 / 25 | retain_id_refine_scope_and_redistribute | Keep the coherent identity/access domain; protocol/policy kind are facets, not a reason for tiny leaves. |
| `backend_baas_api` | 71 / 70 / 52 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `ci_cd_release` | 1 / 1 / 0 | retain_id_refine_scope_and_redistribute | Local compilers/bundlers, package managers and general application PaaS. |
| `deployment_containers_paas` | 75 / 71 / 55 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |
| `feature_flags_config` | 16 / 10 / 15 | retain_without_split | Keep application feature/config control; system configuration belongs to infrastructure automation. |
| `mlops_tracking_registry` | 22 / 19 / 20 | retain_without_split | Keep experiment/model lifecycle operations; generic CI/CD, telemetry and model serving retain own categories. |
| `orm_data_access` | 22 / 20 / 21 | retain_without_split | Keep application data access libraries; database clients/admin integrations and engines are separate. |
| `queues_streaming_messaging` | 36 / 28 / 28 | retain_without_split | Keep async brokers/queues/event transport; compute processing and human chat are different domains. |
| `distributed_training_acceleration` | 2 / 2 / 0 | retain_without_split | Retain the two-member model-training compute domain; no further split. |
| `embeddings_reranking` | 0 / 0 / 0 | retain_without_split | Retain the currently empty domain, marked empty; inspect misplaced embedding tools without inventing members. |
| `foundation_models` | 15 / 14 / 0 | retain_without_split | Keep model implementations; task/modality-specific engines use evidenced specific categories. |
| `inference_model_serving` | 61 / 42 / 26 | retain_without_split | Keep execution/serving engines; gateway routing and model training are different responsibilities. |
| `llm_gateways_routing_caching` | 5 / 5 / 0 | retain_without_split | Keep LLM-provider gateway operations; generic networking and ordinary KV caches remain separate. |
| `training_finetuning_alignment` | 3 / 3 / 0 | retain_without_split | Keep the three-member training/adaptation domain; no separate one-example optimization leaves. |
| `edge_on_device_ai` | 4 / 4 / 0 | retain_without_split | Keep purpose-built device/embedded execution; platform support alone is a deployment facet. |
| `image_video_generation` | 15 / 15 / 0 | retain_without_split | Keep generative media models/tools; modality is a facet, ordinary playback/conversion routes to Files & Media. |
| `speech_voice_audio` | 18 / 17 / 0 | retain_without_split | Keep the audio-AI domain; ASR/TTS/realtime support are capabilities until a later evidence-backed revision. |
| `vision_multimodal` | 9 / 7 / 0 | retain_without_split | Keep vision/perception and multimodal inference pipelines; media generation and generic graphics are distinct. |
| `uncategorized_review` | 43 / 43 / 1 | retain_without_split | Service queue only. Keep unresolved records visible; never count this as a thematic or accepted classification. |
| `learning_reference_resources` | 69 / 67 / 0 | retain_without_split | Keep educational/reference resources separated from adoptable implementation projects; reference form also remains explicit. |
| `research_agents_deep_research` | 7 / 6 / 0 | retain_without_split | Keep research-agent products; implementation purpose differs from papers, lists and market-specific research. |
| `robotics_embodied_ai` | 6 / 6 / 0 | retain_without_split | Keep embodied control/simulation; game engines and generic computer use remain separate. |
| `ai_security_guardrails_redteam` | 25 / 22 / 0 | retain_without_split | Keep AI-specific runtime safety and adversarial evaluation; general vulnerability tooling is separate. |
| `governance_policy_compliance` | 1 / 0 / 0 | retain_id_refine_scope_and_redistribute | Retain the existing sparse domain and inspect policy engines in security; do not add small new leaves. |
| `supply_chain_devsecops` | 62 / 52 / 38 | split_into_container_and_children | Different integration decisions need distinct functional leaves; reuse existing domains for outliers. |

## Execution and acceptance

1. CAT-02: this exact vocabulary and all 77 ID dispositions are prepared; retain v1 as historical evidence. This is not semantic acceptance of all repository assignments.
2. CAT-03/04: pin input, field-contract and taxonomy-v2 digests in collector checkpoints; reject resume on a changed vocabulary unless an explicit migration is supplied. Implement locally, then prove one actual repository and labeled error fixtures. Containers/retired IDs are invalid final primaries.
3. CAT-05/06: collect all field groups per repository and review all 1,800 input records. Revisit all 150 v1 suggestions, especially targets now converted to containers; preserve 58 missing-description flags. Resolve the 43 external category references, primary/secondary semantics, query/navigation meanings and consumer mappings.
4. CAT-07: verify identities, apply the unchanged Stars/completeness rules and compute final leaf counts and distinct parent unions. Count 0 is valid for an unused defined category; do not fabricate membership or silently delete definitions.
5. CAT-08/09/10: source/schema/consumer migration, static HTML generation, verification and exact-version handoff. CP-06 cards/index remain separately owned; 458 ID-format gaps and the unsupported candidate version are not fixed by this taxonomy proposal.

The collector may propose only registered IDs or an explicit unresolved review decision. A new functional gap requires a versioned taxonomy amendment with multiple supporting examples; it must not cause automatic category creation or silent forced placement.

## Artifacts, verification and rollback

- [Current machine-readable taxonomy projection](../../specs/catalog/taxonomy.yaml)
- [Historical preparation and application evidence](../reports/catalog-refresh-history.md)
- [Current refresh commands and storage ownership](../CATALOG_REFRESH.md)

The original registry CSV, 77 before/after dispositions, 1,800 review routes,
150 provisional assignment flags and preparation verification are retained in
the local archive documented in the history. They are historical task artifacts,
not active build inputs. The current manifest owns assignments; CAT-06 still
owns semantic review.

Focused checks cover counts/IDs/labels, parent integrity, source-category coverage, multiple existing examples, valid leaf routes, pending record coverage and preserved source/v1 bytes. No broad product tests, network or browser check is appropriate to this planning edit. Rollback: review only this revision and the PLAN/RUNLOG delta against the new run baseline. Preserve previous dirty work and both proposals; no Git reset or deletion is authorized.
