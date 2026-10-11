# CP-04 prospective new-domain challenge — 2026-10-11

Twelve new scenarios were frozen before capture and run without agents or changes to the ranking algorithms. Source-qualified target top12 coverage and evidence-pack coverage increase from 11/12 to 12/12. Keycloak moves from rank21 to1. The conservative mode preserves exact original literal orders in all ten re-executed, fully judged historical development cases. Parent remains `in_progress / partially_verified / no_go`, `promotion_ready=false`.

## Twelve new scenarios

Each upstream README was inspected on 2026-10-11. One useful target is confirmed per scenario; the alternatives remain unjudged, not negatives. Source descriptions are paraphrases. Terms and requirement partitions were manually authored and frozen before running; no post-capture tuning occurred.

| Scenario | Useful target and upstream source | Active FTS rank | Original literal rank | Separated rank | New required priority rank | Broad priority rank |
|---|---|---:|---:|---:|---:|---:|
| CP04-ND-01 — Автоматический HTTPS для публичного и внутреннего сервиса | [caddyserver/caddy](https://github.com/caddyserver/caddy) | 3 | 2 | 1 | 1 | 1 |
| CP04-ND-02 — Прокси для контейнеров с обновлением маршрутов без перезапуска | [traefik/traefik](https://github.com/traefik/traefik) | 1 | 1 | 1 | 1 | 1 |
| CP04-ND-03 — Ограничение частоты API-запросов и преобразование ответов | [Kong/kong](https://github.com/Kong/kong) | 4 | 3 | 1 | 1 | 1 |
| CP04-ND-04 — S3-хранилище файлов с каталогами и метаданными | [seaweedfs/seaweedfs](https://github.com/seaweedfs/seaweedfs) | 1 | 1 | 1 | 1 | 1 |
| CP04-ND-05 — Единая идентификация с федерацией пользователей и правами доступа | [keycloak/keycloak](https://github.com/keycloak/keycloak) | 21 | 21 | 9 | 1 | 1 |
| CP04-ND-06 — Идентификация B2B SaaS с изолированными организациями | [zitadel/zitadel](https://github.com/zitadel/zitadel) | 5 | 8 | 2 | 1 | 1 |
| CP04-ND-07 — Долгие бизнес-процессы с восстановлением после сбоев | [temporalio/temporal](https://github.com/temporalio/temporal) | 2 | 2 | 2 | 1 | 1 |
| CP04-ND-08 — Python-пайплайны с повторными попытками и расписанием | [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) | 1 | 1 | 1 | 1 | 1 |
| CP04-ND-09 — Поиск товаров с опечатками и фасетными фильтрами | [meilisearch/meilisearch](https://github.com/meilisearch/meilisearch) | 2 | 2 | 2 | 2 | 2 |
| CP04-ND-10 — Общий поиск по нескольким коллекциям приложения | [typesense/typesense](https://github.com/typesense/typesense) | 4 | 9 | 2 | 1 | 1 |
| CP04-ND-11 — REST и GraphQL поверх существующей SQL-базы с администрированием | [directus/directus](https://github.com/directus/directus) | 1 | 1 | 1 | 1 | 1 |
| CP04-ND-12 — Небольшой backend с SQLite и подписками на изменения | [pocketbase/pocketbase](https://github.com/pocketbase/pocketbase) | 1 | 1 | 1 | 1 | 1 |

Every target survives detailed evidence packing under separated and both priority modes. Active FTS and original literal both miss Keycloak in top12 and in the pack. Six target ranks improve versus original literal; six remain unchanged; none decline. Eleven selected targets rank first and Meilisearch ranks second. Typesense leads the typo-tolerant search scenario, but this is an unjudged alternative rather than a proven error: its upstream README also describes typo tolerance. A selected target is not assumed uniquely best.

## Historical regression result

The ten historical cases were executed again against the new 24-fact candidate. The conservative mode retains all ten full original literal orders, Recall@12 `0.8048992673992673` and nDCG@12 `0.8745552065363883`. Historical complete judgments support these metrics only for the ten old cases. No full Recall/nDCG/precision is calculated for the twelve new cases.

## Reproducibility and boundaries

The [source registry](../../research/cp04-new-domain-capabilities-2026-10-11.json) preserves the original twelve dated facts and adds twelve newly inspected GitHub README facts. The [scenarios](../../evals/plugin-v1/new-domain-scenarios-2026-10-11.json), [contract](../../evals/plugin-v1/new-domain-contract.md), [runner](../../evals/plugin-v1/run_new_domain_scenarios.py) and unchanged rankers are bound by the [declaration](../../evals/plugin-v1/results/cp04-new-domains-2026-10-11/declaration.json). Declaration SHA256: `670f6332aba0adcad915530b4de0ffa04888b4efb39bfab2f5e8485388450f4f`.

The isolated candidate has 2,500 cards, 2,630 classifications and 126 routes / 162 route members. Logical SQLite parity, card hashes and immutable-write rejection pass. Active assets and anchors are unchanged. Public retrieval rejects the candidate as `index_incompatible`; public packing also rejects it. Candidate packing uses the disclosed private evaluation seam only after receipt/file hash verification. Literal rank adapters use placeholder transport scores, not observed BM25/RRF scores. Active FTS executes the actual public reader.

The unchanged builder retains the historical `cp04-capability-2026-10-08-` snapshot-ID prefix. Its content hash, new input observation dates, declaration and build receipt identify this new candidate; the original catalog metadata has not been refreshed. No current full-catalog freshness claim follows.

Commands run:

```powershell
python -m unittest discover -s tests -p test_plugin_new_domains.py
python evals/plugin-v1/run_new_domain_scenarios.py --build
python evals/plugin-v1/run_new_domain_scenarios.py --predeclare
python evals/plugin-v1/run_new_domain_scenarios.py --run
```

Three contract tests pass after an observed RED/GREEN for a target incorrectly assigned to a taxonomy route. Source identity and requirement partitions validate; unknown results retain their actual ranks and unknown grades. Capture exits successfully. Build receipt and declaration are exclusive-write artifacts; earlier captures are preserved.

Additional verification passed: `python scripts/build_plugin_search_index.py --check`
confirms unchanged active bundle parity; the Product-Agent OS
`validate_control_plane.py .` reports no errors or missing files. Explicit
post-capture checks recompute the frozen declaration and receipt/file hashes,
verify all sixty new-case identity orders and coverage arithmetic, confirm
compact top12 rows, parse both new Python files and resolve report links.

Results: [compact summary](../../evals/plugin-v1/results/cp04-new-domains-2026-10-11/summary.json), [top12 names and assessments](../../evals/plugin-v1/results/cp04-new-domains-2026-10-11/top12.json), [full observations](../../evals/plugin-v1/results/cp04-new-domains-2026-10-11/observations.json). Full observations contain five-arm detailed cards, evidence and traces and are about4.06MiB; use the compact files for inspection.

## Explicit self-review and next gate

This is a same-author prospective challenge, not independent held-out or human acceptance. Scenarios use concrete technical terms aligned with known upstream capabilities and were authored after source inspection, so target coverage can be optimistic. Unknown peers are not proven unsuitable; no graded adversarial negative set or semantic-negation test was added. Ranking checks lexical support, not verified fulfillment of every architectural/product requirement.

The broad mode is shown for comparison only and remains rejected on the previous per-case regressions. New scenario results do not reverse that decision. No model or provider ran, and this does not test Russian natural-language query formulation, rich project-specific recommendation explanations, runtime activation, integration effort or installation. Next: independently assess the top12 alternatives, representative ambiguous/negative/constraint cases and end-user explanations before promotion. Rollback only this challenge unit; preserve prior work, active assets and all frozen observations.
