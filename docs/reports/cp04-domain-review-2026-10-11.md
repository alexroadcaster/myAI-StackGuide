# CP-04 expanded top-12 review and adverse request probes — 2026-10-11

Completed a primary-source review of all 129 case/repository pairs (93 unique repositories) in the union top12 of the twelve prior new-domain cases. Added six prospective negative requests and three ambiguous requests, froze all inputs, then re-executed five unchanged methods on 21 cases. No agents were used. The active bundle, policy, trust anchors, candidate facts and ranking algorithms are unchanged.

The main measured result is preservation plus clearer limitations: all 60 original five-arm full orders match their prior capture, and all ten historical literal/conservative orders and complete metrics match. The conservative method has 23 documented-full-capability entries in the first three positions across twelve cases, versus 20 for original literal and 19 for active FTS5. This is a scoped descriptive count, not a complete relevance metric or independent acceptance.

Negative conditions are absent from the current positive-term projection: conservative ranking retains known conflicts in all six negative top12 lists, and five detailed packs. Ambiguous requests were projected to a route by the evaluator; no interview/model was run. Clarification and final recommendation behavior therefore remain unevaluated. Parent CP-04 remains `in_progress / partially_verified / no_go`, `promotion_ready=false`.

## Evidence and interpretation

- [Manual oracle](../../evals/plugin-v1/domain-review-oracle-2026-10-11.json): same-author judgments after the prior capture and before this new capture. Fresh upstream README/official-document reads on 2026-10-11; summaries and links are frozen, upstream pages themselves remain mutable. No code/security/license/readiness audit is implied.
- [New cases](../../evals/plugin-v1/domain-adversarial-cases-2026-10-11.json) and [contract](../../evals/plugin-v1/domain-review-contract.md): six negative and three ambiguity boundary probes. Labels do not rank or filter.
- [Declaration](../../evals/plugin-v1/results/cp04-domain-review-2026-10-11/declaration.json): SHA256 `9f764cb9b570e0657584ee30c5e1617bdf21784e2b1bf4beba8f78df7e7f828e`.
- [Reviewed summary](../../evals/plugin-v1/results/cp04-domain-review-2026-10-11/reviewed-summary.json) and [reviewed compact observations](../../evals/plugin-v1/results/cp04-domain-review-2026-10-11/reviewed-observations.json): query, intent, full ranked IDs, packed IDs, pack hash, positions and conflicts; 727746 bytes. Detailed card payloads are not duplicated.
- Scope is the observed union top12, not the complete routed/ranked pool. New-case official Recall/nDCG remain null. Unknowns retain actual ranks and are not negatives. Grade 2 explicitly does not prove satisfaction of all mandatory conditions.
- Candidate public retrieval again returns `index_incompatible`; canonical evidence-pack construction rejects the candidate. Observations use only the already pinned private evaluation seam.

## Five-method comparison

Counts sum over actual returned slots; several routes return fewer than twelve. Full means documented main capabilities, conditional means useful core with named requirement gaps, supplementary means an assembly/component role. These are not interchangeable.

| Method | Returned slots | Full | Conditional core | Supplementary | Role/requirement conflict | Unknown | Full in top3 | Full first result | Exact prior orders |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Broad required priority (previously rejected) | 114 | 26 | 45 | 22 | 19 | 2 | 23 | 12 | 12/12 |
| Original literal | 114 | 25 | 46 | 22 | 19 | 2 | 20 | 11 | 12/12 |
| Active FTS5 | 113 | 25 | 47 | 19 | 20 | 2 | 19 | 11 | 12/12 |
| Conservative novel-required priority | 114 | 26 | 45 | 22 | 19 | 2 | 23 | 12 | 12/12 |
| Required/context split | 114 | 26 | 45 | 22 | 19 | 2 | 22 | 12 | 12/12 |

The broader method remains rejected by its previous per-case historical regressions. Similar results here do not overturn that decision. Historical original/conservative Recall@12 = 0.8048992673992673 and nDCG@12 = 0.8745552065363883, complete on the ten originally judged development cases only.

## Twelve original cases

Full-capability positions show where all manually documented core requirements occur. Differences within top12, not only the designated target, are visible.

| Case | Original literal full-capability positions | Conservative full-capability positions | Conservative conflicts / unknowns |
| --- | --- | --- | --- |
| CP04-ND-01 | 2 | 1 | curl/curl; clash-verge-rev/clash-verge-rev |
| CP04-ND-02 | 1, 6 | 1, 6 | none |
| CP04-ND-03 | 1, 2, 3, 4 | 1, 2, 3, 4 | httpie/cli; GyulyVGC/sniffnet; sirkirby/unifi-mcp; curl/curl; pi-hole/pi-hole |
| CP04-ND-04 | 1, 2 | 1, 2 | delta-io/delta; apache/iceberg |
| CP04-ND-05 | 1 | 1, 2 | none |
| CP04-ND-06 | 1, 8 | 1, 2 | oomol-lab/open-connector |
| CP04-ND-07 | 1, 2, 3 | 1, 2, 3 | Pimzino/spec-workflow-mcp |
| CP04-ND-08 | 1, 3, 12 | 1, 3, 12 | none |
| CP04-ND-09 | 1, 2 | 1, 2 | searxng/searxng; mrkrsl/web-search-mcp; firecrawl/firecrawl; kagisearch/kagimcp |
| CP04-ND-10 | 1, 9 | 1, 2 | searxng/searxng |
| CP04-ND-11 | 1 | 1 | none |
| CP04-ND-12 | 1, 3 | 1, 3 | parse-community/parse-server; supabase/supabase; nhost/nhost; appwrite/appwrite (unknown); InsForge/InsForge (unknown) |

Useful alternatives include APISIX/Tyk/KrakenD for gateway mediation, JuiceFS for file/object access, Logto for organizations/identity, Hatchet/Inngest for durable execution, Huey for Python tasks with SQLite, Meilisearch for multi-index federation and self-hosted Convex for SQLite-backed reactive apps. This expands the oracle beyond the original designated targets. Actual deployment fit, effort and readiness still require project-specific checks.

Counterevidence retained: BullMQ documents a Python package, so Python requests cannot reject it as Node-only. A final source self-review also found an advertised PostgreSQL alternative: BullMQ was removed from the known-forbidden set for the no-Redis probe and its deployment fit stays unknown. Celery has an experimental local SQLite backend, so excluding Redis/RabbitMQ alone does not establish universal Celery incompatibility. JuiceFS can use local disk, so external-object-storage dependency is not assumed for every deployment. Current MinIO README says this repository is no longer maintained; PocketBase retains pre-1.0 compatibility caveats. These facts do not silently change the dated canonical catalog.

## Negative requests

The [post-capture source correction](../../evals/plugin-v1/source-review-corrections-2026-10-11.json) preserves the original declaration, inputs and raw observations. Reviewed outputs remove BullMQ as a proven negative conflict; rankings and all case-level conflict totals are unchanged because RQ remains. This correction is retrospective and is not disguised as a predeclared judgment. The existing query uses only positive terms and default empty constraints for these probes. It does not consume the forbidden annotations. These are observed request-to-query coverage gaps, not demonstrated bad model answers. Presence in a retrieval list also does not prove a forbidden repository was recommended as compliant.

| Case / negative condition | Active FTS5 known conflicts at actual top12 positions | Conservative known conflicts at actual top12 positions | Conservative conflicts in detailed pack |
| --- | --- | --- | --- |
| CP04-NEG-01: Python tasks with retries; no Redis, Valkey or RabbitMQ. | rq/rq #4 | rq/rq #4 | rq/rq #4 |
| CP04-NEG-02: Python scheduled pipelines with retries; Kubernetes is forbidden. | none | argoproj/argo-workflows #10 | argoproj/argo-workflows #10 |
| CP04-NEG-03: Local SQLite realtime backend; no PostgreSQL or MongoDB service. | supabase/supabase #4; nhost/nhost #6; parse-community/parse-server #7 | parse-community/parse-server #5; supabase/supabase #6; nhost/nhost #7 | parse-community/parse-server #5; supabase/supabase #6; nhost/nhost #7 |
| CP04-NEG-04: B2B SaaS organizations and SSO; PostgreSQL is forbidden. | logto-io/logto #1 | logto-io/logto #2 | logto-io/logto #2 |
| CP04-NEG-05: S3 file storage and metadata; exclude MinIO from consideration. | minio/minio #3 | minio/minio #4 | none |
| CP04-NEG-06: Automatic public/internal HTTPS proxy; Caddy is excluded by project policy. | caddyserver/caddy #3 | caddyserver/caddy #1 | caddyserver/caddy #1 |

Active FTS5 has known conflicts in 5/6 negative top12 lists and 4/6 packs; original literal and all three candidate methods have conflicts in 6/6 lists and 5/6 packs. Absence of Argo from the active FTS5 top12 is a ranking effect, not evidence that the Kubernetes prohibition was consumed. Only the listed known conflicts are judged; other dependencies can still be unknown.

## Ambiguous requests

| Request | Clarification required | What was observed |
| --- | --- | --- |
| Need search for my application. | Search application-owned records or the external web? Which API/corpus constraints apply? | Retrieval under an evaluator-supplied route; clarification/model routing not evaluated |
| Need federation for the project. | User/identity federation, multi-index search, or another federation? | Retrieval under an evaluator-supplied route; clarification/model routing not evaluated |
| Need workflow support. | Durable business execution, agent state, data pipelines, or development specifications? | Retrieval under an evaluator-supplied route; clarification/model routing not evaluated |

Next implementation must preserve negative product/dependency conditions through query construction and distinguish documented conflict from unknown dependency. It must also clarify materially ambiguous goals before committing to a route. Then rerun these probes and the original regressions, and evaluate actual source-supported user explanations. This report authorizes no new runtime contract or activation.

## Verification

- New evaluator tests: `python -m unittest discover -s tests -p test_plugin_domain_review.py` — 4/4 passed after a semantic RED (missing judgment incorrectly became grade 0) and correction. A second intermediate check had a test-side query-key error; corrected it to the actual `variants` contract.
- `python evals/plugin-v1/run_domain_review.py --predeclare` — succeeded before capture.
- `python evals/plugin-v1/run_domain_review.py --run` — succeeded: 105 five-arm case observations, ten two-arm historical regressions, exact original orders, candidate guards and logical bundle verification.
- `python scripts/build_plugin_search_index.py --check` — passed: unchanged 2,500 cards, 2,630 classifications, 126 routes/162 members and exact active policy/card pins.
- Product-Agent OS `validate_control_plane.py .` — passed with no errors or missing files.
- Independent arithmetic/hash/identity/link check (`work/cp04-domain-review/verify.py`) — passed: all frozen source hashes, 60 old orders, 45 paired projected probe orders, ten historical orders, all129 identity joins and reviewed summary counts.
- `git diff --check` — passed, with the existing RUNLOG line-ending warning.
- Explicit same-author self-review; no independent reviewer/model run, actual natural-language query construction, RU/EN equivalence, final-answer usefulness or adoption acceptance.
- Rollback is limited to the new eval files/results/report and this turn's control references. Preserve all previous dirty work and immutable captures.

## Complete assessed union

Grades: **3** documented main requirements, **2** conditionally useful core, **1** supplementary/assembly, **0** documented mismatch/conflict, **unknown** unverified mandatory fit.

### CP04-ND-01

Автоматический HTTPS для публичного и внутреннего сервиса

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [curl/curl](https://github.com/curl/curl) | 0 | Documented role or required primary database conflicts with the goal. HTTP/URL client for sending requests; not a server-side API gateway. |
| [TykTechnologies/tyk](https://github.com/TykTechnologies/tyk) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. API gateway with request/response mediation, rate limits and quotas. |
| [Kong/kong](https://github.com/Kong/kong) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. API gateway; documented rate-limit and request/response transformation plugins. |
| [caddyserver/caddy](https://github.com/caddyserver/caddy) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. HTTPS server/reverse proxy with public automatic certificates and managed internal CA. |
| [nginx/nginx](https://github.com/nginx/nginx) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. HTTP server and reverse proxy; TLS configuration and request limiting. Automatic internal CA not confirmed. |
| [traefik/traefik](https://github.com/traefik/traefik) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Container-aware reverse proxy with dynamic Docker/Kubernetes configuration. |
| [fatedier/frp](https://github.com/fatedier/frp) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Reverse tunnel exposes services behind NAT; documented TLS setup uses certificate files. |
| [envoyproxy/envoy](https://github.com/envoyproxy/envoy), [official feature documentation](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/rate_limit_filter) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Edge/service proxy with documented HTTP rate-limit filter; response transformation not verified here. |
| [krakend/krakend-ce](https://github.com/krakend/krakend-ce) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Declarative API gateway with rate limits and content transformation; live route updates not verified. |
| [haproxy/haproxy](https://github.com/haproxy/haproxy) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. TCP/HTTP load balancer and reverse proxy; automatic certificate lifecycle not confirmed. |
| [apache/apisix](https://github.com/apache/apisix) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. API gateway with hot configuration, rewrite plugins, rate limiting and container/bare-metal deployment. |
| [clash-verge-rev/clash-verge-rev](https://github.com/clash-verge-rev/clash-verge-rev) | 0 | Documented role or required primary database conflicts with the goal. Desktop GUI for local proxy profiles/system proxy/TUN; not an application API gateway. |

### CP04-ND-02

Прокси для контейнеров с обновлением маршрутов без перезапуска

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [TykTechnologies/tyk](https://github.com/TykTechnologies/tyk) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. API gateway with request/response mediation, rate limits and quotas. |
| [Kong/kong](https://github.com/Kong/kong) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. API gateway; documented rate-limit and request/response transformation plugins. |
| [traefik/traefik](https://github.com/traefik/traefik) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Container-aware reverse proxy with dynamic Docker/Kubernetes configuration. |
| [istio/istio](https://github.com/istio/istio) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Kubernetes-oriented service mesh with proxies and control-plane traffic management. |
| [krakend/krakend-ce](https://github.com/krakend/krakend-ce) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Declarative API gateway with rate limits and content transformation; live route updates not verified. |
| [apache/apisix](https://github.com/apache/apisix) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. API gateway with hot configuration, rewrite plugins, rate limiting and container/bare-metal deployment. |

### CP04-ND-03

Ограничение частоты API-запросов и преобразование ответов

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [curl/curl](https://github.com/curl/curl) | 0 | Documented role or required primary database conflicts with the goal. HTTP/URL client for sending requests; not a server-side API gateway. |
| [httpie/cli](https://github.com/httpie/cli) | 0 | Documented role or required primary database conflicts with the goal. HTTP/URL client for sending requests; not a server-side API gateway. |
| [TykTechnologies/tyk](https://github.com/TykTechnologies/tyk) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. API gateway with request/response mediation, rate limits and quotas. |
| [pi-hole/pi-hole](https://github.com/pi-hole/pi-hole) | 0 | Documented role or required primary database conflicts with the goal. DNS filtering/ad blocking and DHCP; not HTTP API response mediation. |
| [Kong/kong](https://github.com/Kong/kong) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. API gateway; documented rate-limit and request/response transformation plugins. |
| [caddyserver/caddy](https://github.com/caddyserver/caddy) | 1 | Supplementary component or solution requiring substantial assembly for this goal. HTTPS server/reverse proxy with public automatic certificates and managed internal CA. |
| [nginx/nginx](https://github.com/nginx/nginx) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. HTTP server and reverse proxy; TLS configuration and request limiting. Automatic internal CA not confirmed. |
| [traefik/traefik](https://github.com/traefik/traefik) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Container-aware reverse proxy with dynamic Docker/Kubernetes configuration. |
| [fatedier/frp](https://github.com/fatedier/frp) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Reverse tunnel exposes services behind NAT; documented TLS setup uses certificate files. |
| [envoyproxy/envoy](https://github.com/envoyproxy/envoy), [official feature documentation](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/rate_limit_filter) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Edge/service proxy with documented HTTP rate-limit filter; response transformation not verified here. |
| [istio/istio](https://github.com/istio/istio) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Kubernetes-oriented service mesh with proxies and control-plane traffic management. |
| [krakend/krakend-ce](https://github.com/krakend/krakend-ce) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Declarative API gateway with rate limits and content transformation; live route updates not verified. |
| [apache/apisix](https://github.com/apache/apisix) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. API gateway with hot configuration, rewrite plugins, rate limiting and container/bare-metal deployment. |
| [GyulyVGC/sniffnet](https://github.com/GyulyVGC/sniffnet) | 0 | Documented role or required primary database conflicts with the goal. Network traffic monitoring application; not an API gateway. |
| [clash-verge-rev/clash-verge-rev](https://github.com/clash-verge-rev/clash-verge-rev) | 0 | Documented role or required primary database conflicts with the goal. Desktop GUI for local proxy profiles/system proxy/TUN; not an application API gateway. |
| [sirkirby/unifi-mcp](https://github.com/sirkirby/unifi-mcp) | 0 | Documented role or required primary database conflicts with the goal. MCP tools for managing UniFi systems; not an application API gateway. |

### CP04-ND-04

S3-хранилище файлов с каталогами и метаданными

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [ceph/ceph](https://github.com/ceph/ceph) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Distributed object, block and file storage; requested S3/filer details not verified in this read. |
| [seaweedfs/seaweedfs](https://github.com/seaweedfs/seaweedfs) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Distributed file/object storage with filer metadata and S3 endpoint; weed mini offers a single-process mode. |
| [minio/minio](https://github.com/minio/minio) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. S3-compatible object store. Current README states that this repository is no longer maintained; directory/filer semantics not verified. |
| [apache/iceberg](https://github.com/apache/iceberg) | 0 | Documented role or required primary database conflicts with the goal. Analytical table format/library on storage; does not replace the requested object-storage server. |
| [delta-io/delta](https://github.com/delta-io/delta) | 0 | Documented role or required primary database conflicts with the goal. Analytical table format/library on storage; does not replace the requested object-storage server. |
| [treeverse/lakeFS](https://github.com/treeverse/lakeFS) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Versioning layer over existing object storage; useful supplementary component. |
| [juicedata/juicefs](https://github.com/juicedata/juicefs) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. POSIX filesystem with metadata service and S3 gateway; storage can be local disk or object storage. |

### CP04-ND-05

Единая идентификация с федерацией пользователей и правами доступа

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [keycloak/keycloak](https://github.com/keycloak/keycloak) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Identity provider with user federation and fine-grained authorization. |
| [privacyidea/privacyidea](https://github.com/privacyidea/privacyidea) | 1 | Supplementary component or solution requiring substantial assembly for this goal. MFA service supplementing existing LDAP/AD/SQL identities; not a complete federation/permission system. |
| [ory/hydra](https://github.com/ory/hydra) | 1 | Supplementary component or solution requiring substantial assembly for this goal. OAuth/OIDC server that delegates user login/consent to an existing identity provider/application. |
| [oauth2-proxy/oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Authentication reverse proxy delegating to existing IdPs; not an organization identity authority. |
| [nextauthjs/next-auth](https://github.com/nextauthjs/next-auth) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Application OAuth/OIDC authentication library; enterprise identity authority/authorization needs assembly. |
| [ory/keto](https://github.com/ory/keto) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Authorization decision/permission service; user authentication/federation requires separate components. |
| [ory/kratos](https://github.com/ory/kratos) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. User identity/login/recovery service; OIDC/access policy uses additional Ory services. |
| [goauthentik/authentik](https://github.com/goauthentik/authentik) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Self-hosted identity provider supporting SAML, OIDC, LDAP and RADIUS; B2B organization isolation not verified. |
| [supertokens/supertokens-core](https://github.com/supertokens/supertokens-core) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Authentication/session service with social login, roles, SSO and multi-tenancy; federation-policy combination not fully verified. |
| [zitadel/zitadel](https://github.com/zitadel/zitadel) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Identity platform with SSO, SCIM and multiple tenant organizations; specific user-federation authorization combination needs verification. |
| [supabase/auth](https://github.com/supabase/auth) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. JWT authentication and external identity login; row permissions require integration with the wider Postgres stack. |
| [permitio/opal](https://github.com/permitio/opal) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Policy/data synchronization for authorization engines; not a full identity provider. |
| [cerbos/cerbos](https://github.com/cerbos/cerbos) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Authorization decision/permission service; user authentication/federation requires separate components. |
| [logto-io/logto](https://github.com/logto-io/logto) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Identity platform with external IdP connectors, enterprise SSO, organizations and organization RBAC; local setup requires PostgreSQL. |
| [ory/polis](https://github.com/ory/polis) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Enterprise SSO and SCIM directory synchronization; organization isolation not established by this read. |
| [openfga/openfga](https://github.com/openfga/openfga) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Authorization decision/permission service; user authentication/federation requires separate components. |
| [better-auth/better-auth](https://github.com/better-auth/better-auth) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. TypeScript authentication/authorization framework with multi-tenant plugins; isolated organization behavior requires verification. |

### CP04-ND-06

Идентификация B2B SaaS с изолированными организациями

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [ory/hydra](https://github.com/ory/hydra) | 1 | Supplementary component or solution requiring substantial assembly for this goal. OAuth/OIDC server that delegates user login/consent to an existing identity provider/application. |
| [authelia/authelia](https://github.com/authelia/authelia) | 1 | Supplementary component or solution requiring substantial assembly for this goal. SSO/MFA companion for reverse proxies; SaaS organization isolation not verified. |
| [oauth2-proxy/oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Authentication reverse proxy delegating to existing IdPs; not an organization identity authority. |
| [goauthentik/authentik](https://github.com/goauthentik/authentik) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Self-hosted identity provider supporting SAML, OIDC, LDAP and RADIUS; B2B organization isolation not verified. |
| [zitadel/zitadel](https://github.com/zitadel/zitadel) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Identity platform with SSO, SCIM and multiple tenant organizations; specific user-federation authorization combination needs verification. |
| [casdoor/casdoor](https://github.com/casdoor/casdoor) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Identity/SSO platform with organizations and documented SQLite all-in-one setup; organization isolation semantics need checking. |
| [logto-io/logto](https://github.com/logto-io/logto) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Identity platform with external IdP connectors, enterprise SSO, organizations and organization RBAC; local setup requires PostgreSQL. |
| [ory/polis](https://github.com/ory/polis) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Enterprise SSO and SCIM directory synchronization; organization isolation not established by this read. |
| [better-auth/better-auth](https://github.com/better-auth/better-auth) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. TypeScript authentication/authorization framework with multi-tenant plugins; isolated organization behavior requires verification. |
| [oomol-lab/open-connector](https://github.com/oomol-lab/open-connector) | 0 | Documented role or required primary database conflicts with the goal. SaaS action/OAuth connector infrastructure for agents, not app-user organization identity management. |

### CP04-ND-07

Долгие бизнес-процессы с восстановлением после сбоев

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [kestra-io/kestra](https://github.com/kestra-io/kestra) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Scheduled/event YAML orchestration across languages; exact durable replay/recovery semantics not verified. |
| [temporalio/temporal](https://github.com/temporalio/temporal) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Durable workflow runtime with failure recovery and retries. |
| [inngest/inngest](https://github.com/inngest/inngest) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Durable step execution with persisted state, recovery, retries and event/cron triggers. |
| [activepieces/activepieces](https://github.com/activepieces/activepieces) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Connector/business automation platform; durable replay/failure recovery not verified here. |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Stateful agent/workflow library with persistent durable execution and resumption; requires application integration. |
| [hatchet-dev/hatchet](https://github.com/hatchet-dev/hatchet) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Durable task/workflow service with Python SDK, retries and cron; persistence uses PostgreSQL. |
| [Pimzino/spec-workflow-mcp](https://github.com/Pimzino/spec-workflow-mcp) | 0 | Documented role or required primary database conflicts with the goal. Development specification/approval/task workflow tool, not a durable business execution runtime. |

### CP04-ND-08

Python-пайплайны с повторными попытками и расписанием

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [celery/celery](https://github.com/celery/celery) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Python task queue; RabbitMQ/Redis feature-complete backends and experimental local SQLite are documented. |
| [coleifer/huey](https://github.com/coleifer/huey) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Python task queue with retries, cron and pipelines; SQLite, filesystem and memory backends are documented alternatives to Redis. |
| [rq/rq](https://github.com/rq/rq) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Python task queue requiring Redis or Valkey. |
| [apache/airflow](https://github.com/apache/airflow) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Python workflow authoring/scheduling/monitoring; exact retries not checked in this read. |
| [Bogdanp/dramatiq](https://github.com/Bogdanp/dramatiq) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Python background task queue with RabbitMQ/Redis transports documented; broker-free deployment not verified. |
| [argoproj/argo-workflows](https://github.com/argoproj/argo-workflows) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Container workflow engine implemented as Kubernetes CRDs; requires Kubernetes. |
| [dagster-io/dagster](https://github.com/dagster-io/dagster) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Python data-asset/pipeline orchestration; retries not verified in this read. |
| [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Python pipeline orchestration with scheduling, caching and retries; supports local Python execution. |
| [taskforcesh/bullmq](https://github.com/taskforcesh/bullmq) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Redis-backed task queue; current README also documents a Python package, so Node-only rejection would be incorrect. |
| [temporalio/sdk-python](https://github.com/temporalio/sdk-python) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Python SDK for fault-tolerant workflows; requires a Temporal runtime. |
| [windmill-labs/windmill](https://github.com/windmill-labs/windmill) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Script/job/flow orchestration including Python; PostgreSQL-backed queue/database. |
| [hatchet-dev/hatchet](https://github.com/hatchet-dev/hatchet) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Durable task/workflow service with Python SDK, retries and cron; persistence uses PostgreSQL. |

### CP04-ND-09

Поиск товаров с опечатками и фасетными фильтрами

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [elastic/elasticsearch](https://github.com/elastic/elasticsearch) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Full-text search/analytics engine; exact requested typo/facet/federation configuration not checked. |
| [quickwit-oss/tantivy](https://github.com/quickwit-oss/tantivy) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Rust full-text search library with facets; API/server/distributed serving requires assembly. |
| [vespa-engine/vespa](https://github.com/vespa-engine/vespa) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Search/recommendation/aggregation platform; requested typo and federation details not verified. |
| [typesense/typesense](https://github.com/typesense/typesense) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Application search engine with typo tolerance, facets and federated collections in one HTTP request. |
| [meilisearch/meilisearch](https://github.com/meilisearch/meilisearch), [official feature documentation](https://www.meilisearch.com/docs/capabilities/multi_search/getting_started/federated_search) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Application search engine with typo tolerance, facets and documented federated multi-index search. |
| [opensearch-project/OpenSearch](https://github.com/opensearch-project/OpenSearch), [official feature documentation](https://docs.opensearch.org/latest/query-dsl/term/fuzzy/) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Application full-text search engine with documented fuzzy matching; complete requested facet/federation combination not verified. |
| [searxng/searxng](https://github.com/searxng/searxng) | 0 | Documented role or required primary database conflicts with the goal. External web/provider search or metasearch tool; not serving the application-owned inventory index requested here. |
| [quickwit-oss/quickwit](https://github.com/quickwit-oss/quickwit) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Full-text search and aggregation engine focused on logs/traces; application-search requirements need verification. |
| [zincsearch/zincsearch](https://github.com/zincsearch/zincsearch) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Full-text search server with aggregation; requested typo/federation behavior not verified. |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 0 | Documented role or required primary database conflicts with the goal. Web search/crawl/extraction infrastructure; not the requested inventory search serving engine. |
| [kagisearch/kagimcp](https://github.com/kagisearch/kagimcp) | 0 | Documented role or required primary database conflicts with the goal. External web/provider search or metasearch tool; not serving the application-owned inventory index requested here. |
| [zilliztech/claude-context](https://github.com/zilliztech/claude-context) | 0 | Documented role or required primary database conflicts with the goal. Codebase semantic search for coding agents; different corpus from the requested ecommerce index. |
| [mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp) | 0 | Documented role or required primary database conflicts with the goal. External web/provider search or metasearch tool; not serving the application-owned inventory index requested here. |
| [serenedb/serenedb](https://github.com/serenedb/serenedb) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Search and analytics database; exact requested application-search features not verified. |

### CP04-ND-10

Общий поиск по нескольким коллекциям приложения

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [elastic/elasticsearch](https://github.com/elastic/elasticsearch) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Full-text search/analytics engine; exact requested typo/facet/federation configuration not checked. |
| [scrapy/scrapy](https://github.com/scrapy/scrapy) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Web crawling/extraction library; useful ingestion component, needs separate indexing and search serving. |
| [quickwit-oss/tantivy](https://github.com/quickwit-oss/tantivy) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Rust full-text search library with facets; API/server/distributed serving requires assembly. |
| [vespa-engine/vespa](https://github.com/vespa-engine/vespa) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Search/recommendation/aggregation platform; requested typo and federation details not verified. |
| [apify/crawlee](https://github.com/apify/crawlee) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Web crawling/extraction library; useful ingestion component, needs separate indexing and search serving. |
| [typesense/typesense](https://github.com/typesense/typesense) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Application search engine with typo tolerance, facets and federated collections in one HTTP request. |
| [meilisearch/meilisearch](https://github.com/meilisearch/meilisearch), [official feature documentation](https://www.meilisearch.com/docs/capabilities/multi_search/getting_started/federated_search) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Application search engine with typo tolerance, facets and documented federated multi-index search. |
| [adbar/trafilatura](https://github.com/adbar/trafilatura) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Web crawling/extraction library; useful ingestion component, needs separate indexing and search serving. |
| [opensearch-project/OpenSearch](https://github.com/opensearch-project/OpenSearch), [official feature documentation](https://docs.opensearch.org/latest/query-dsl/term/fuzzy/) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Application full-text search engine with documented fuzzy matching; complete requested facet/federation combination not verified. |
| [searxng/searxng](https://github.com/searxng/searxng) | 0 | Documented role or required primary database conflicts with the goal. External web/provider search or metasearch tool; not serving the application-owned inventory index requested here. |
| [quickwit-oss/quickwit](https://github.com/quickwit-oss/quickwit) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Full-text search and aggregation engine focused on logs/traces; application-search requirements need verification. |
| [zincsearch/zincsearch](https://github.com/zincsearch/zincsearch) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Full-text search server with aggregation; requested typo/federation behavior not verified. |
| [perplexityai/modelcontextprotocol](https://github.com/perplexityai/modelcontextprotocol) | 0 | Documented role or required primary database conflicts with the goal. External web/provider search or metasearch tool; not serving the application-owned inventory index requested here. |
| [Aas-ee/open-webSearch](https://github.com/Aas-ee/open-webSearch) | 0 | Documented role or required primary database conflicts with the goal. External web/provider search or metasearch tool; not serving the application-owned inventory index requested here. |
| [mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp) | 0 | Documented role or required primary database conflicts with the goal. External web/provider search or metasearch tool; not serving the application-owned inventory index requested here. |
| [serenedb/serenedb](https://github.com/serenedb/serenedb) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Search and analytics database; exact requested application-search features not verified. |

### CP04-ND-11

REST и GraphQL поверх существующей SQL-базы с администрированием

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [directus/directus](https://github.com/directus/directus) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Wraps SQL databases with REST/GraphQL and administration; licensing conditions require a separate adoption check. |
| [strapi/strapi](https://github.com/strapi/strapi) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. CMS content modeling with REST/GraphQL/admin and SQL backends; direct wrapping of an untouched existing schema not verified. |
| [statamic/cms](https://github.com/statamic/cms) | 1 | Supplementary component or solution requiring substantial assembly for this goal. Laravel flat-first CMS; not a verified existing-SQL REST/GraphQL wrapper. |
| [keystonejs/keystone](https://github.com/keystonejs/keystone) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Schema-defined GraphQL/backend with management UI; REST and direct existing-SQL wrapping not verified. |
| [payloadcms/payload](https://github.com/payloadcms/payload) | 2 | Core solution is conditionally useful; the facts below name unverified requested details. This is not full hard-requirement satisfaction. Application CMS/backend and admin with database adapters; direct existing-SQL wrapping not verified. |

### CP04-ND-12

Небольшой backend с SQLite и подписками на изменения

| Repository / primary source | Grade | Assessment |
| --- | --- | --- |
| [parse-community/parse-server](https://github.com/parse-community/parse-server) | 0 | Documented role or required primary database conflicts with the goal. App backend requiring MongoDB or PostgreSQL/PostGIS; required SQLite backend conflicts with documented prerequisites. |
| [appwrite/appwrite](https://github.com/appwrite/appwrite) | unknown | Mandatory SQLite support is unverified; fit remains unknown. Backend platform with authentication, databases and realtime; required SQLite backend not confirmed. |
| [supabase/supabase](https://github.com/supabase/supabase) | 0 | Documented role or required primary database conflicts with the goal. Postgres backend platform with auth, APIs and realtime; documented primary database conflicts with the requested SQLite backend. |
| [nhost/nhost](https://github.com/nhost/nhost) | 0 | Documented role or required primary database conflicts with the goal. PostgreSQL/Hasura backend platform; primary database conflicts with the requested SQLite backend. |
| [pocketbase/pocketbase](https://github.com/pocketbase/pocketbase) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Embedded SQLite backend with realtime, users, files and API; pre-1.0 compatibility caveat remains. |
| [get-convex/convex-backend](https://github.com/get-convex/convex-backend) | 3 | Requested main capabilities are documented; deployment quality/readiness is not assessed. Reactive app database/backend with documented self-hosted SQLite support; platform compatibility needs adoption testing. |
| [InsForge/InsForge](https://github.com/InsForge/InsForge) | unknown | Mandatory SQLite support is unverified; fit remains unknown. Backend platform for agent-built apps; required SQLite and exact realtime contract not confirmed. |

