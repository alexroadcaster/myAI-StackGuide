# CP-04 Prospective Source Oracle V3

Status: `authored_pending_source_review`. The source packet is [quality-oracle-v3-source.json](quality-oracle-v3-source.json), schema `cp04_quality_oracle_source_v3`. The exact source/version pins, case definitions, route universes, explicit judgments and unknown coverage live in that packet. This protocol authors a new prospective held-out set; it does not execute retrieval, score a capture, change the catalog, or accept the product. `promotion_ready=false`, `calibrated=false`, `observed_results=false` and `frozen_at=null` remain explicit until the appropriate owner records later evidence.

## Assignment and Evidence Boundary

The Product Planner received an explicit CP-04 assignment to author only these two new eval artifacts. The primary owns active control documents; a later Quality Evaluator owns a separately assigned validator/scorer and capture run. Existing v1/v2 labels, results, schemas and runners remain unchanged. The new nullable relevance field is intentionally a new source contract, not a compatible edit to an old judgment schema.

Sources used:

- `.agents/skills/design-recommendation-evals/SKILL.md`, `.codex/TEAM.md`, `.codex/agent-eval-workflow.md`, `docs/plan/plugin-v1-team-contracts.md`, `EVALS.md`, and `evals/plugin-v1/runner-contract.md` for assignment, evidence levels and evaluation gates.
- Targeted CP-04/R references in `PLAN.md`, `REQUIREMENTS.md`, `docs/PRODUCT_REQUIREMENTS.md` and `docs/V1_ROADMAP.md` for the active product acceptance boundary. These documents do not supply relevance labels.
- The pinned public `catalog.snapshot.json`, `catalog.search-manifest.json`, `retrieval-policy.json`, `data/catalog_manifest.json` and `specs/catalog/taxonomy.yaml` for functional metadata, canonical identities, assignment membership and pins. No SQLite database was opened or queried. The manifest's registry logical hash is retained; exact route membership is reconstructed from all pinned snapshot assignments and checked against the taxonomy node.
- Only `case_id` and `user_goal` projections from `quality-plan.json` and `quality-plan-v2.json` for semantic duplicate avoidance. Only v2 thresholds and predeclared strata boundaries supply acceptance references. No old labels, relevant-ID lists, rankings, result artifacts or experimental captures entered judgment authoring.

The source snapshot date is `2026-09-01`; exact bytes are pinned rather than described as live/current GitHub evidence. The author emitted only selected-route metadata to model context. Local deterministic parsing of public JSON is not whole-catalog model ingestion. No private source/chat, catalog refresh, provider, installation, runtime/configuration change, Git operation or external write is part of this assignment.

Before the first HV3 source freeze or held-out capture, the owner's public-verification requirement authorizes a bounded supplementary qualification of the 29 explicitly unknown assessments. The curator uses only those known public repository identities, upstream README/license/release sources and linked official documentation. The separate `research/cp04-public-qualification-2026-10-08.json` binds the original source packet hash and records exact case/identity/criterion, supported/unsupported/unknown disposition, public source URL, observation date and concise rationale. The prospectively authorized `research/cp04-public-qualification-supplement-2026-10-08.json` covers the same three initial identities for Solidus, Halo and Jeecg with additional criterion-specific primary sources before freeze; it appends evidence without changing the original qualification artifact. The later owner-approved `research/cp04-public-qualification-kubernetes-2026-10-08.json` qualifies one additional known identity, Kubernetes ID 20580498, against the exact existing HV3-13 criteria, bringing the applied qualification boundary to 30 distinct case/identity pairs. All three exact file hashes and every applied criterion pointer/value must be bound before source review. These artifacts preserve catalog facts, classifications, eligibility, query terms and thresholds. The independently reviewed prospective goal-value clarification below is recorded separately. Aggregate distinct quoted excerpts are limited to 25 words per source URL; paraphrases remain clearly source-grounded.

The sequential source-author join must preserve snapshot evidence and bind each added `public_primary_live` evidence entry to the qualification file's exact SHA-256 and local JSON pointer/value. The corresponding record must match the case ID, numeric repository ID and public repository identity. Positive live support requires an explicit supported check for the case's declared core, preferred detail or supporting function; missing or unsupported evidence alone never assigns grade zero. Before freeze, recompute source projection hashes, grade/unknown coverage and all affected source bindings, then independently review the combined source judgments. No ranking or result may be consulted during this join, and post-capture relabeling remains forbidden.

## Prospective Goals and Complete Universes

Every semantic case is held out. There are no V3 development cases. Each of the 14 declared navigation domains contributes one fresh functional task and one leaf route; no container query is needed. Membership includes every primary or secondary assignment to that route, deduplicated by exact positive numeric `github_repository_id`. The numeric universe is sorted and remains unchanged by public qualification; the primary must review and freeze exact bytes before any V3 capture. The functional goal and query contain no owner/full-name identity request or repository-name boost. Languages, frameworks and protocols such as Node.js, Django, Kotlin, JavaScript, REST and GraphQL are functional technology identifiers.

| Case | Domain | Leaf route | Functional goal | IDs | Positive | Unknown |
| --- | --- | --- | --- | ---: | ---: | ---: |
| HV3-01 | Developer Tooling | `package_version_management` | Node.js runtime versions; Windows detail | 11 | 4 | 0 |
| HV3-02 | Software Testing | `load_performance_testing` | Python load testing; plain-Python authoring detail | 27 | 3 | 0 |
| HV3-03 | Files & Media | `document_management_processing` | JavaScript PDF reading | 9 | 1 | 0 |
| HV3-04 | Frontend Development | `graphics_visualization` | Browser 3D rendering | 18 | 2 | 0 |
| HV3-05 | Finance & ERP | `erp_business_suites` | Inventory/stock with purchasing | 6 | 5 | 1 |
| HV3-06 | Content Publishing | `content_management_systems` | Django-native CMS with editorial flexibility | 14 | 2 | 0 |
| HV3-07 | Communication & Personal Productivity | `video_conferencing` | Browser/web conferences | 10 | 6 | 0 |
| HV3-08 | Commerce & Payments | `ecommerce_platforms` | Headless commerce with API detail | 14 | 11 | 3 |
| HV3-09 | Project & Internal Operations | `internal_tools_builders` | Admin over REST/GraphQL; React detail | 12 | 12 | 0 |
| HV3-10 | Data Engineering | `data_processing_compute` | DataFrame/tabular manipulation; Python detail | 13 | 8 | 0 |
| HV3-11 | Databases & Data Tools | `caches_key_value_stores` | Embedded ordered key/value library | 6 | 1 | 0 |
| HV3-12 | Backend Development | `backend_frameworks` | Kotlin web service; async detail | 34 | 5 | 0 |
| HV3-13 | Deployment & Infrastructure | `container_platforms` | Multi-container application definition/execution | 19 | 4 | 8 |
| HV3-14 | Software & Infrastructure Security | `software_supply_chain_security` | Artifact vulnerabilities; dependency/package detail | 20 | 8 | 0 |
| HV3-S01 | Separate diagnostic | `orm_data_access` | Python ORM; async detail; genuine secondary route | 22 | 7 | 0 |

Full IDs are `CP04-HV3-01` through `CP04-HV3-14` and `CP04-HV3-S01`. After the prospective independent-review corrections below, semantic total: 213 records, 72 source-supported positives and 12 unknowns. With the diagnostic: 235 assessments, 234 distinct numeric IDs, 79 positives, 144 reviewed-unrelated and 12 unknowns. The preserved initial source baseline had 59 positives, 147 reviewed-unrelated and 29 unknowns. The separately preserved pre-correction reviewed source had 78 positives, 153 reviewed-unrelated and 4 unknowns. Django's numeric ID appears in two independent case universes; this is not a duplicate within either ranking/universe.

Thin leaves and the dense backend-framework leaf are present under the original v2 stratum references. Query locales include EN and RU; terms use functional language/protocol synonyms and Russian equivalents within the canonical policy term ceiling. Historical aliases retained in public metadata are diagnostic context, not injected identity terms. This set does not independently prove historical alias resolution or RU/EN presentation equivalence. Existing identity and language acceptance gates remain separate.

The snapshot's secondary target assignments all point to standalone categories, so multi-assignment cards in the 14 domain leaves do not prove secondary-route retrieval. HV3-S01 therefore covers the complete 22-ID standalone ORM route, including Django through its actual secondary assignment. It is excluded from the 14-domain semantic macro and reported separately. A canonical ID returned twice in any capture remains a hard failure. Domain coverage through 14 leaves is distinct from executing the original full 111-leaf/14-container deterministic route sweep; that gate is retained and not claimed run here.

Each new goal has an explicit novelty rationale against the 54 v1/v2 user-goal records. It changes the functional task rather than renaming a previous repository request or changing only language/query phrasing. This is an agent source review, not a human similarity rating. The exact prior-goal projection hash is in the source packet; no previous expected grades were used.

## Explicit Judgment Contract

Each routed numeric ID has exactly one judgment in its case, with `relevance_grade`, `assessment_status`, `contribution_rationale`, `unknown_reason`, `denied_by_frozen_constraints`, `adoption_fit`, exact `source_evidence`, `identity_source`, `membership_cohort_source`, `constraint_source` and all original `classifications`.

Every evidence item records its exact file/pointer/value, snapshot evidence reference, source observation date and verification kind. A null source observation date remains null with `observation_date_status=unknown`; the known `source_snapshot_date` is recorded separately and cannot substitute for an observed date. The sole missing snapshot observation date belongs to diagnostic ID 33925906. It remains null even after the separate live README observation resolves that functional assessment to a documented alternate interface. Public-primary qualification records have exact UTC retrieval dates with day granularity; time of day is unknown and is never fabricated. Identity joins and taxonomy placement are provenance; they cannot establish a positive function. Popularity, stars, name recognition, retrieval score and rank have no judgment weight. The source packet stores only bounded public metadata, not full READMEs/private source.

Grades:

- `3`: source explicitly supports the case core and its preferred detail.
- `2`: source explicitly supports core but does not establish the preferred detail.
- `1`: source explicitly states the supporting function declared for that particular case. This is never a fallback for missing description, core evidence, category confidence or source references.
- `0`: the reviewed source states a distinct function or integration interface under the case's declared scope. Missing evidence alone is not grade zero. This means unrelated under the pinned functional scope, not a technical proof that future adapters or undocumented features are impossible.
- `null`: the pinned snapshot plus authorized bounded public-primary evidence cannot determine the declared core or supporting contribution; preferred detail alone cannot establish core. The separate `unknown_reason` identifies the missing fact. A name/category-only record stays unknown; it cannot become a supporting reference merely by placement.

`adoption_fit` stays `unknown` for every record, including grade 3. A positive grade means source-reported functional contribution, not usable installation, project compatibility, security approval, operability, source freshness or adoption acceptance. Source language/topics may support a language/toolkit classification; implementation language alone does not prove a user-facing interface when the preferred detail specifically requires authoring/API behavior.

Windows is a preferred relevance detail in HV3-01, not an invented hard constraint. Consequently the explicitly POSIX Node version manager can have core-only grade 2 while native Windows operability remains unverified. Other technology-specific cores are declared in their case criteria. General JVM framework metadata without explicit Kotlin evidence remains unknown. These distinctions must be reviewed before freeze, not revised after viewing ranks.

## Denominators, Unknown Coverage and Failures

For each case, define the relevance universe as all independently source-supported grades 1 through 3 that are not denied by the frozen constraints. It includes unretrieved IDs. Unknowns, grade zero and independently denied IDs are excluded from this positive denominator. All IDs nevertheless retain explicit assessments; no unassessed route members are allowed. Frozen constraints come from the accepted archived/availability/public defaults, with exact per-ID source facts rather than matcher output supplying denial.

Recall@12 uses that complete positive universe. nDCG@12 uses gain `2**grade - 1` and discount `log2(rank + 1)`, with ideal ranking over the same positive, non-denied universe. A case with no positives has null metrics and a required-case failure. A typed retrieval failure also has null metrics and fails; a valid no-hit result with supported positives scores zero. No failed/null case can disappear from the macro or make the denominator smaller.

Any unknown ID anywhere in either complete raw returned ranking makes ranking metrics null, reports `needs_owner_review` and `no_go`, and emits the exact unknown IDs/positions and raw coverage. Do not silently substitute zero, compact ranks, judge only the top 12, hide baseline unknowns or drop unknown-bearing cases. Returned IDs outside the full route universe are invalid, even below rank 12. Complete raw rankings, both candidate and baseline, are required.

Unknown coverage is reported separately per case and in aggregate: count, exact IDs, universe size, unknown share and disposition. No unknown-share acceptance threshold is invented. Unknowns not returned still limit the conclusion to the supported snapshot functions; the owner must record their disposition before acceptance. A later exact-ID public source qualification, if separately authorized, must preserve snapshot pins and distinguish fresh observations from frozen metadata. That work must precede a newly reviewed freeze/capture; never relabel after ranks are exposed.

No source-supported case has an intrinsic Recall@12 ceiling below 1.0 in this authored set; this is denominator arithmetic, not a retrieval result. All candidate/baseline metrics, rank coverage, exclusions, pack survival, route execution and latency remain unobserved.

## Original Acceptance References

`threshold_refs` links every original v2 threshold to its exact `quality-plan-v2.json` file hash and `/thresholds/...` pointer; `threshold_change=false`. The functional held-out macro remains Recall@12 >= 0.75 and nDCG@12 >= 0.65, with required-stratum minima 0.60/0.50, zero baseline regression, zero hard-constraint violations/false exclusions/duplicate canonical IDs, alias success 1.0 and evidence-pack survival >= 0.90. No value is lowered or reinterpreted by this oracle. The existing performance, deterministic route and human thresholds are retained by reference; this packet does not run or satisfy them.

Use the same source case definitions, query terms, exact route universes, constraints, `k` and source-supported judgments for both routes. Grade evidence-pack survival over supported, independently allowed positives present in the raw top 12; missing/oversized/truncated pack entries remain visible under the existing survival gate. Capture source identity/version pins and complete raw/pack IDs before scoring. Resolve any denominator ambiguity with the primary before capture.

Required strata must be reported separately from the 14-domain macro. The new cases carry source-derived thin/dense, baseline/CAT-07A expansion, locale, dual-description, multi-assignment and genuine secondary-diagnostic tags. Metadata alias presence is not an alias-success result, multi-assignment presence is not secondary-route execution, and the standalone diagnostic cannot inflate the semantic macro. A validator/scorer must fail an absent required gate rather than claim it passed. Human usefulness still requires independent real reviewers; agent judgments do not supply the human rubric score or calibration.

## Reproducibility and Freeze Handoff

Exact-file SHA-256 pins bind snapshot, manifest, source catalog, taxonomy, policy and threshold/old-goal sources. Canonical JSON is sorted keys, compact separators, UTF-8, `ensure_ascii=false`, `allow_nan=false`. Each `query_definition_sha256` covers the exact source object `{case_id,user_goal,graded_criteria,query_locale,query_terms,target_category_id,hard_constraints,k}`. It is not a C9 runtime digest. Each `source_projection_sha256` covers the ordered judgment projection `{id,evidence,classifications,constraint_source,identity_source,membership_cohort_source}`; `source_projection_bytes` records its exact canonical byte count. A builder must reconstruct and verify these values, all source pointers and all memberships before creating capture-ready inputs.

The subsequent validator/scorer assignment should cover duplicate keys/nonfinite values, source/hash/pointer drift, omitted/extra/reordered IDs, missing explicit assessments, null/zero confusion, grade1 without its declared supporting function, unknown returned IDs at every rank, missing/no-positive cases, diagnostic macro contamination, original threshold references, candidate/baseline parity and complete raw ranking/pack coverage. This protocol supplies no fabricated RED or test result. Existing old schemas remain preserved; the nullable source schema and generated V3 runtime/scoring envelope require a separately reviewed structural implementation.

The primary must independently review source validity, denominator semantics, supporting-grade rationales and unknown dispositions before freezing exact bytes. Then hand the reviewed packet to the Quality Evaluator for separately owned validator/scorer work and prospective capture. No labels, queries, universes or thresholds may change after a V3 ranking is exposed. Corrections require a new source version and a fresh genuinely unexposed held-out set when they alter semantic judgments. Reusing old labels/results or calling this artifact a passed/calibrated quality run is unsupported.

Rollback is limited to these two newly authored eval files or their exact task diff; preserve all pre-existing dirty work. No runtime/catalog rollback is needed.

## Initial Snapshot Insufficiencies Retained for Traceability

The following table records the original 29 snapshot unknowns preserved in the initial source baseline. It is historical source coverage, not the current combined unknown list. The initial public-primary join below resolved 22 and retained 7 unknowns; the subsequent authorized supplement resolves three more, leaving 4 unknowns; no human rating or adoption acceptance is inferred. All initial description/topic/language pointers, identities, source references and dates remain in each combined JSON judgment.

| Case | Numeric IDs and public identities | Missing evidence |
| --- | --- | --- |
| HV3-01 | 586920414 `jdx/mise` | Node.js runtime version selection |
| HV3-05 | 1864233 `frappe/erpnext`; 19745004 `odoo/odoo`; 189829392 `ever-co/ever-gauzy`; 304981340 `idurar/idurar-erp-crm` | Stock/inventory operations |
| HV3-06 | 100695 `drupal/drupal`; 75645659 `WordPress/wordpress-develop`; 126178683 `halo-dev/halo` | Django CMS integration beyond mirror/generic metadata |
| HV3-07 | 992325192 `joinly-ai/joinly` | Conferencing transport/service |
| HV3-08 | 1151051 `django-oscar/django-oscar`; 2179920 `woocommerce/woocommerce`; 2884111 `magento/magento2`; 6763587 `PrestaShop/PrestaShop`; 30985840 `solidusio/solidus`; 127988011 `macrozheng/mall`; 131995661 `shopware/shopware`; 234739976 `medusajs/medusa` | Explicit headless commerce backend |
| HV3-09 | 159152904 `jeecgboot/JeecgBoot`; 306829688 `nocobase/nocobase`; 352933140 `ToolJet/ToolJet` | REST/GraphQL admin integration |
| HV3-10 | 17165658 `apache/spark`; 20587599 `apache/flink`; 485548415 `Eventual-Inc/Daft` | DataFrame interface |
| HV3-11 | 437245741 `dragonflydb/dragonfly` | Embedded library versus server |
| HV3-12 | 1148753 `spring-projects/spring-framework`; 6296790 `spring-projects/spring-boot`; 139914932 `quarkusio/quarkus` | Kotlin framework interface |
| HV3-13 | 899787279 `ckreiling/mcp-server-docker` | Multi-container definition/execution commands |
| HV3-S01 | 33925906 `Vincit/objection.js` | Any source-supported Python ORM function; all bounded function fields absent; source evidence observation date also unknown |

Additional review points: grade1 model-asset generation, conferencing installer, admin scaffolding/database UI, columnar interchange/scheduling, container-system assembly, SBOM generation and diagnostic SQL/schema prerequisites are explicit supporting functions, but the primary must accept their case-specific contribution scope before freeze. Alternate-language/function grade0 judgments are limited to stated snapshot scope and do not claim universal incompatibility. Truncated descriptions are retained literally; supplementary topics provide explicit facts where used. The Chinese commerce description is readable source text, not a decoding failure, and no headless fact is inferred from it.

## Bounded Public-Primary Join and Source-Review Handoff

The sequential join reads only [cp04-public-qualification-2026-10-08.json](../../research/cp04-public-qualification-2026-10-08.json), exact SHA-256 `e4cb74f805d9d8f178cc96eb96aff6d48eea2e65543da3653eb9361fde1df239`. The preserved [initial source baseline](results/cp04-v3-2026-10-08/oracle-v3-initial-source.json) has exact SHA-256 `c8d7cdbee232c84df1a136c25f0bcc6b5c2d25b8c243d0d42f38e672d1e07b7b`; it is an authored source artifact, not a ranking/result capture. Both files are bound in `source_hashes`. The research packet binds 29 exact original case/ID/repository pairs and 87 verbatim core/detail/supporting criteria, with 42 primary public URLs and zero quoted words. All snapshot evidence, taxonomy assignments, independent denials, universes, goals, queries, query definition hashes and thresholds remain unchanged.

Every added evidence entry is `source_kind=public_primary_live`, points to `/records/N/requirement_checks/M`, stores that entire check object, and copies its exact source URL and `observed_at`. Its observation granularity is a UTC day (`2026-10-08`); it is not an exact timestamp, source update date or repository activity verification. Research `metadata_gaps.observation_timestamp_semantics` owns that meaning. Historical snapshot dates are not overwritten. Live public function assertions do not prove installed behavior, license suitability, a verified repository numeric-ID lookup, a verified release/commit, source currency beyond the retrieved page, security or adoption fit.

At the initial-join stage, the source author reviewed all 29 record sets against the existing criteria. Sixteen supported core checks produce fifteen grade 3 and one grade 2 assessment. Explicit DataFrame-to-table interchange produces one grade 1 supporting contribution. Five explicit alternate-function/interface checks produce grade 0. Seven remain unknown; supported preferred detail alone does not make them positive. An unsupported React detail does not turn the unresolved admin/API core into grade 0. Public assertions about an under-development interface remain functional source evidence with their development caveat, not operational readiness.

| Case | Numeric ID / public identity | Initial → first-join grade | Source-grounded disposition |
| --- | --- | --- | --- |
| CP04-HV3-01 | 586920414 `jdx/mise` | null → 3 | README explicitly installs and selects different Node.js versions per project. |
| CP04-HV3-05 | 1864233 `frappe/erpnext` | null → 3 | README Order Management explicitly tracks inventory levels and replenishes stock. |
| CP04-HV3-05 | 19745004 `odoo/odoo` | null → 3 | README explicitly includes Warehouse Management among integrated ERP applications; this supports stock/warehouse management at a documented feature level. |
| CP04-HV3-05 | 189829392 `ever-co/ever-gauzy` | null → 2 | README explicitly lists ERP inventory, supply chain and production management. |
| CP04-HV3-05 | 304981340 `idurar/idurar-erp-crm` | null → null | README feature list covers invoices, payments, quotes and customers; a later broad description names inventory under Fair-Code. Inventory implementation scope is unresolved between these sections. |
| CP04-HV3-06 | 100695 `drupal/drupal` | null → 0 | Official core requirements establish PHP and its extensions. The inspected product is not a Django-based CMS; interoperability with Django was not evaluated. |
| CP04-HV3-06 | 75645659 `WordPress/wordpress-develop` | null → 0 | Upstream development README explicitly documents PHP test suites and WordPress core development. This is an alternate PHP stack, not a Django-based CMS. |
| CP04-HV3-06 | 126178683 `halo-dev/halo` | null → null | README establishes a website-building CMS but does not state Django-based implementation. Gradle file names alone were not used to determine incompatibility. |
| CP04-HV3-07 | 992325192 `joinly-ai/joinly` | null → 0 | README describes an AI participant joining Zoom, Google Meet or Teams using meeting URLs. This is an assistant for existing conferences, not a video/web conferencing service. |
| CP04-HV3-08 | 1151051 `django-oscar/django-oscar` | null → null | README establishes Django commerce and a separate API extension; it does not explicitly establish this repository as a headless backend. |
| CP04-HV3-08 | 2179920 `woocommerce/woocommerce` | null → 3 | Official Store API documentation explicitly supports headless cart interaction with cart tokens. |
| CP04-HV3-08 | 2884111 `magento/magento2` | null → 3 | Official docs explicitly describe Magento Open Source as the backend service for a separate PWA storefront in a headless architecture. |
| CP04-HV3-08 | 6763587 `PrestaShop/PrestaShop` | null → null | README establishes an e-commerce platform. Native REST data access in official docs does not by itself establish a complete headless commerce backend. |
| CP04-HV3-08 | 30985840 `solidusio/solidus` | null → null | README explicitly permits solidus_core with a custom frontend, admin and API; the exact headless-backend criterion is not explicitly established by this source. |
| CP04-HV3-08 | 127988011 `macrozheng/mall` | null → null | Chinese README distinguishes frontend applications and backend commerce interfaces, but does not explicitly identify the system as a headless backend. |
| CP04-HV3-08 | 131995661 `shopware/shopware` | null → 3 | README explicitly identifies Shopware 6 as an open headless commerce platform. |
| CP04-HV3-08 | 234739976 `medusajs/medusa` | null → 3 | Official architecture explicitly identifies Medusa as headless commerce with storefronts consuming its API routes. |
| CP04-HV3-09 | 159152904 `jeecgboot/JeecgBoot` | null → null | README establishes internal business-system generation and a separated Vue/Spring stack. Swagger tooling alone does not confirm the required API integration function. |
| CP04-HV3-09 | 306829688 `nocobase/nocobase` | null → 3 | Official documentation describes registering pages and blocks, calling backend APIs and mounting components in the visual configuration interface for the business-system builder. |
| CP04-HV3-09 | 352933140 `ToolJet/ToolJet` | null → 3 | README explicitly describes building internal admin panels and operational apps on existing databases, APIs and SaaS systems. |
| CP04-HV3-10 | 17165658 `apache/spark` | null → 3 | README explicitly includes Spark SQL for DataFrames and pandas API on Spark for data-analysis workloads. |
| CP04-HV3-10 | 20587599 `apache/flink` | null → 1 | Official from_pandas API explicitly converts a pandas DataFrame into a PyFlink Table, contributing DataFrame-ecosystem processing support without proving the core library criterion. |
| CP04-HV3-10 | 485548415 `Eventual-Inc/Daft` | null → 3 | Official DataFrame reference defines a table with typed columns and rows and provides select/filter/aggregation and column manipulation methods. |
| CP04-HV3-11 | 437245741 `dragonflydb/dragonfly` | null → 0 | README describes a Redis/Memcached replacement configured with a connection port and bind address and evaluated as a server. This is a server deployment surface, not an embedded storage library. |
| CP04-HV3-12 | 1148753 `spring-projects/spring-framework` | null → 3 | Official docs explicitly support Kotlin coroutines in Spring MVC/WebFlux controllers and functional web APIs. |
| CP04-HV3-12 | 6296790 `spring-projects/spring-boot` | null → 3 | Official Kotlin Support docs describe Boot support through Spring Framework and provide web application examples. |
| CP04-HV3-12 | 139914932 `quarkusio/quarkus` | null → 3 | Official Kotlin guide explicitly supplies first-class Kotlin support and REST resource/client extensions. |
| CP04-HV3-13 | 899787279 `ckreiling/mcp-server-docker` | null → 3 | README documents docker_compose plan/apply and an application example deploying WordPress with a supporting MySQL container. |
| CP04-HV3-S01 | 33925906 `Vincit/objection.js` | null → 0 | README explicitly identifies a Node.js ORM and relational query builder, with TypeScript support. The requested Python ORM integration is incompatible with this documented interface. |

After that initial join, the seven remaining unknowns were `304981340` (ERP inventory feature scope unresolved), `126178683` (Django core not established), `1151051`, `6763587`, `30985840`, `127988011` (headless commerce core not established), and `159152904` (admin/API integration core not established). Each has exact qualified source evidence and an explicit missing-core rationale. The owner must review their disposition; no unknown-share threshold or automatic waiver is introduced.

The five new zeros rely on explicitly documented PHP CMS, existing-conference assistant, cache server and Node.js ORM interfaces. They do not arise from absent evidence or the mere `unsupported` enum. Interface-specific assessment remains distinct from proving all conceivable integrations impossible.

### Supporting Grade-1 Scope Review

The original 14 supporting decisions are unchanged. The source author reviewed their literal metadata functions against the declared case supporting scope; independent primary/Astra review is still required. One newly qualified supporting contribution is added for Flink, giving 15 total. No supporting grade is assigned because a description, core fact or provenance is missing.

| Case / ID | Supporting contribution explicitly stated in source | Scope boundary |
| --- | --- | --- |
| HV3-04 / 1301140808 | Procedural animation-ready image-to-3D model generation | Renderer assets, not the rendering library |
| HV3-07 / 120541771 | Conferencing-system BASH installer | Deployment support, not conferencing transport |
| HV3-09 / 88464704 | Vue admin template/dashboard | Admin UI scaffold, not a demonstrated API adapter |
| HV3-09 / 101394335 | Enterprise React scaffold with admin/dashboard topics | UI foundation, not API integration proof |
| HV3-09 / 108761645 | Spreadsheet/no-code database UI with automatic API topics | Data administration foundation, not a dedicated React admin interface |
| HV3-09 / 206509491 | Spreadsheet-like browser database management | Data administration foundation, not an API adapter |
| HV3-10 / 28782747 | Parallel scheduling with pandas/NumPy ecosystem topics | Computation support, not a directly documented DataFrame interface |
| HV3-10 / 51905353 | Columnar interchange and in-memory analytics toolbox | Data representation/interchange support |
| HV3-10 / 20587599 (new) | Official `from_pandas` conversion of pandas DataFrame into PyFlink Table | DataFrame-ecosystem interchange support; core remains unestablished; development docs are not a release pin |
| HV3-13 / 7691631 | Container-based system assembly | Runtime foundation, not application-level multi-container declaration |
| HV3-14 / 262126497 | SBOM generation from images/filesystems | Inventory prerequisite, not vulnerability detection |
| HV3-S01 / 159271175 | Python database toolkit and SQL topic | SQL-access prerequisite, no ORM interface inferred from identity |
| HV3-S01 / 193160679 | Type-safe SQL code generation with Python topic | Client/code-generation prerequisite, no ORM runtime proof |
| HV3-S01 / 399495186 | SQL database tooling in Python | SQL-access prerequisite, no ORM interface inferred from identity |
| HV3-S01 / 667110339 | Database diagram editor and SQL generator | Schema/SQL prerequisite, no Python ORM runtime contribution |

The combined source is `authored_pending_source_review`, `frozen_at=null`, with no captures, model ratings, human ratings, observed ranking metrics or promotion claim. Source projection hashes/counts are recomputed after the join; independent review and source-contract validation must pass before a formal hash freeze. Rollback restores only the combined-source/protocol join against the preserved initial source bytes and the pre-join protocol diff, leaving research, runtime and other owners' files intact. The next role is the primary independent source reviewer, then the separately assigned Quality Evaluator after acceptance; this handoff does not authorize scoring or capture.

### Authorized Three-Record Supplement Before Freeze

The separately owned [supplementary qualification](../../research/cp04-public-qualification-supplement-2026-10-08.json) has exact SHA-256 `f4c9ef11d1e76aa6d8c691ca10b1c307877f4ff480fdf285580387a8374ceac3`. Its three records preserve the same initial baseline hash, identities and all nine verbatim criteria. The source author appended nine exact `public_primary_live` check pointers/values and this file pin without editing the original `e4cb74f...f239` qualification, its 87 evidence bindings or the initial `c8d7cdbe...7b7b` source baseline.

| Case / ID | First join → final prospective grade | Decisive primary-source rationale |
| --- | --- | --- |
| HV3-06 / 126178683 `halo-dev/halo` | null → 0 | Official architecture explicitly defines a Spring Boot Java Web application; this is a documented alternate implementation for the Django core. Ease-of-use support cannot overcome that core mismatch. Exact primary indexed content supports the architecture fact; direct open failed and the indexed crawl was three weeks earlier. No successful direct fetch or verified current release is claimed. |
| HV3-08 / 30985840 `solidusio/solidus` | null → 3 | Official extension guide explicitly documents a headless commerce solution with separate storefronts using REST/GraphQL; core is supported by documented decoupling, not API presence alone. |
| HV3-09 / 159152904 `jeecgboot/JeecgBoot` | null → 2 | English upstream README explicitly documents internal-business builders and unified RESTful/JWT client integration. The documented frontend is Vue, so React detail remains unsupported. Explicit core support gives grade 2 rather than grade 0 or supporting-only grade 1. |

At the pre-correction supplement stage, source coverage was 78 positives, 153 reviewed-unrelated and 4 unknowns across the same 235 case assessments/234 distinct numeric identities. Relative to the original 29 unknowns, 19 became positive and 6 explicitly unrelated; 4 remained unknown. That stage bound 96 added public criterion evidence entries, covering exactly the original 29 case/identity pairs. All original 14 grade-1 assessments remained unchanged; the single new Flink interchange assessment was the fifteenth. No criterion, goal, query, universe, classification, denial, threshold, baseline nonregression gate or query-definition hash changed during either historical join. The later prospective correction changes only the explicitly assigned goal value and nine HV3-13 dispositions described below.

Four qualified unknowns retained through the prospective correction:

- `304981340` `idurar/idurar-erp-crm`: conflicting inventory feature scope remains unresolved.
- `1151051` `django-oscar/django-oscar`: separate REST extension is documented, but the headless commerce core is not established.
- `6763587` `PrestaShop/PrestaShop`: native REST data access is documented, but the headless commerce core is not established.
- `127988011` `macrozheng/mall`: commerce API interfaces are documented, but the headless commerce core is not established.

Unknowns, historical null observation date for snapshot ID 33925906, day-only public observation dates, Halo's indexed-source/direct-fetch gap, unverified activity/license/numeric-ID lookup, and under-development interface caveats remain explicit provenance/evidence limits. No additional discovery, catalog refresh, ranking exposure, human rating or capture occurred in source authoring. Both public artifacts and the snapshot evidence remain distinguishable and hash-bound. The source remains `authored_pending_source_review` with `frozen_at=null`; independent primary/Astra source review is the next gate before any formal source freeze or held-out capture.

The initial independent review identified the HV3-06 goal/core mismatch and the HV3-13 cluster-scope exclusion defect. The owner selected the bounded prospective corrections recorded below before any source freeze or ranking exposure.

## Prospective Independent-Review Corrections Before First Freeze

The authorized source-only [initial independent review](results/cp04-v3-2026-10-08/source-independent-review-initial.json), SHA-256 `eb5f57b62866029c6c65d99c66495a1ea85546d73050b8e47b69b94dd7a031d4`, records two P2 findings. It contains source findings rather than ranking output. The [reviewed pre-correction source](results/cp04-v3-2026-10-08/oracle-v3-reviewed-before-correction-source.json), SHA-256 `478c5d8449ffddcfc9db457f52c9f2d4ab1bee0e93dcbedde2bb7c26833e1786`, and initial `c8d7cdbe...7b7b` baseline remain immutable. The source packet records `prospective_revision=1` in its review disposition, not a schema-shape change. These corrections remain pending focused independent review.

For HV3-06 the owner selected a native-Django synthetic goal, matching its unchanged declared Django-based core:

| Field | Prior reviewed value | Prospective value |
| --- | --- | --- |
| `user_goal` | Integrate a CMS with a Django application, preferring editorial flexibility or ease of use. | Reuse a Django-native CMS in a Django application, preferring editorial flexibility or ease of use. |
| `query_definition_sha256` | `a87c6668674b3fdf3549f6598f3ca25580ee5f4bd3b4f3a07eda2c896304507c` | `629992a9b4b0fa5452ccd84427f7af01ea69f6005a7da652b8cc34268d262d4a` |

Core/detail/supporting criteria, query terms, locale, route universe, constraints and all HV3-06 judgments remain unchanged. Alternate PHP/Java/Node grades apply only to this native-framework core. They do not establish a general rejection of CMS API interoperability with Django. The synthetic intent was clarified before first freeze; no ranking informed the choice.

The new [Kubernetes qualification](../../research/cp04-public-qualification-kubernetes-2026-10-08.json), SHA-256 `0490bb1c287c4ff6b14dd14971c07f6e29619fb794ffb1a8be9be857f8486ce3`, preserves the original baseline binding and exact HV3-13 core/detail/supporting criteria. Its three whole check objects are appended at `/records/0/requirement_checks/0`, `/records/0/requirement_checks/1` and `/records/0/requirement_checks/2`, with their exact public URLs and UTC retrieval date `2026-10-08`. Snapshot evidence and prior rationales remain retained separately.

| Case / ID | Reviewed → prospective grade | Decisive source fact and scope |
| --- | --- | --- |
| HV3-13 / 20580498 `kubernetes/kubernetes` | 0 → 2 | Official Pods documentation explicitly describes multiple cooperating application containers, Pod specifications/templates, and execution through `kubectl apply` and workload controllers. This supports the application-level multi-container core. Docker is preferred, not mandatory; the README's Docker source-build prerequisite does not establish a Docker-facing application interface, so preferred detail stays unknown. |

The source author audited every remaining HV3-13 zero for the same cluster-exclusion defect. The owner approved eight conservative zero-to-unknown corrections. Source metadata for these exact repositories does not establish either the required application-level core or the declared supporting assembly contribution; cluster affiliation alone cannot justify zero. No positive grade is inherited from upstream Kubernetes, and absence of explicit evidence is not treated as unrelatedness.

| HV3-13 numeric ID / identity | Reviewed → prospective grade | Exact unresolved contribution |
| --- | --- | --- |
| 43723161 `helm/helm` | 0 → null | Package-management metadata does not determine the application multi-container declaration/execution surface or declared assembly support. |
| 56353740 `kubernetes/minikube` | 0 → null | Local Kubernetes hosting does not establish the exact application core or supporting assembly surface in bounded metadata. |
| 135516270 `k3s-io/k3s` | 0 → null | Lightweight Kubernetes metadata is too sparse; qualified upstream functions are not automatically inherited. |
| 148545807 `kubernetes-sigs/kind` | 0 → null | Local test-cluster metadata does not determine application declaration/execution or assembly contribution. |
| 179063508 `k3d-io/k3d` | 0 → null | Running Kubernetes inside Docker does not by itself establish the declared application-level core or support. |
| 900130551 `Flux159/mcp-server-kubernetes` | 0 → null | Generic Kubernetes management commands do not specify the application operations required by the criterion. |
| 953587943 `rohitg00/kubectl-mcp-server` | 0 → null | Generic MCP-server metadata does not specify application commands or the supporting assembly contribution. |
| 1137865761 `skyhook-io/radar` | 0 → null | Helm/GitOps plus monitoring/audit UI metadata prevents monitoring-only exclusion but does not establish the exact application core or support. |

Seven zeros retain explicit distinct functions: Prometheus monitoring-cluster management (68964263), PostgreSQL-cluster provisioning/operation (83363132, 91074692, 468311851), image-layer inspection (133251103), macOS VM execution (269336148), and Windows virtualization in a container (743140652). Three previous positives remain unchanged: container-system assembly support (7691631, grade 1), Docker multi-container definition/execution (15045751, grade 3), and explicit `docker_compose` plan/apply application operations (899787279, grade 3). This yields HV3-13 coverage of 19 IDs: 4 positive, 7 reviewed-unrelated and 8 unknown.

Current aggregate coverage is 79 positive, 144 reviewed-unrelated and 12 unknown assessments. The complete 14-domain semantic set has 213 records, 72 positives and 12 unknowns; the separate 22-ID diagnostic has 7 positives and no unknowns. All 15 supporting-grade judgments are unchanged. The combined packet binds 99 public criterion evidence objects across 30 qualified case/identity pairs. The original 29-pair qualification and supplement remain immutable; the eight new unknowns have snapshot evidence and conservative audit provenance, not a fabricated public qualification.

The twelve current unknowns consist of the four qualified gaps listed above and these eight audited HV3-13 identities. Their exact existing criteria, known public URLs and missing-fact reasons are provided in the authorized minimal [cluster qualification input](results/cp04-v3-2026-10-08/cluster-qualification-input.json), SHA-256 `b64ff3df0b47e7c46ef29a1034ef4fdaa12b50691a7ea1444753a188264a9982`. It is bounded source-research input, not a capture or ranking artifact. The owner plans exact-ID public-primary qualification before final freeze; this does not authorize repository discovery, catalog refresh, source-label changes after capture, or automatic adoption claims.

All snapshot/classification/identity/cohort/constraint bindings, route universes, query terms, schema version and original threshold references remain unchanged. Only HV3-06's goal value and corresponding query-definition digest change; only Kubernetes receives three new public check objects; eight reviewed zeros become explicit unknowns with retained prior rationales. Source projections and coverage are recomputed. The source remains `authored_pending_source_review`, `frozen_at=null`, `promotion_ready=false`, with all `adoption_fit=unknown`. Focused primary/Astra source review is the next gate; qualification of the eight gaps must precede any later owner freeze and held-out capture.
