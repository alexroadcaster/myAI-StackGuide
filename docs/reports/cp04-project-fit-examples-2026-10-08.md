# CP-04 project-specific decision examples — 2026-10-08

Four prospective RU/EN explanations composed from the same frozen actual retrieval captures and synthetic Brief contexts. The candidate composition instruction was explicitly read; evaluator criteria were disclosed. This is observed agent-authored prose, not installed-plugin routing, browser behavior or human acceptance.

## CP04-V2-H03 — non-technical founder

### RU

Сначала изучите Immich: ваша цель — собрать разрозненные семейные фото и видео в самостоятельно размещаемом сервисе, а описание прямо соответствует этому назначению [H03-E1]. Его возможная роль — один сервис управления коллекцией. Уменьшение разрозненности работы — гипотеза; экономия времени не измерена. Цена перехода — настройка, обслуживание и восстановление данных; требования неизвестны.

PhotoPrism — альтернативное приложение для фотографий с AI [H03-E2]. Изучайте его первым, если важнее конкретная задача организации фото с помощью AI. Польза гипотетическая: нужная функция, видео и самостоятельное размещение не подтверждены. Если видео обязательны и поддержка не подтвердится, предпочтение возвращается к Immich. Если достаточно упорядочить папки, новый сервис может не понадобиться.

Неизвестны форматы, нынешнее хранилище, место размещения, ответственный за обслуживание и резервная копия. Оба приложения претендуют на одну роль; ценность совместной установки не показана. Один пилот позволит связать результат и затраты с выбранным приложением. Совместимость пока неизвестна.

Следующий вопрос: обязательна общая работа с видео и фото или важнее конкретная AI-задача? По документации выбранной версии проверьте требования и путь загрузки/восстановления одного искусственного изображения и видео либо наличие названной AI-функции. Результат — «поддерживается», «не поддерживается» или «неизвестно» по каждому требованию. Затем можно предложить изолированный пилот; личные изображения не нужны. Это варианты для изучения, внедрение и проверки не выполнялись.

### EN

Inspect Immich first: your goal is to bring scattered household photos and videos into a self-hosted service, and its description directly matches that purpose [H03-E1]. Its potential role is one collection-management service. Reduced fragmentation is a hypothesis; time savings are unmeasured. The trade-off is setup, maintenance and recovery responsibility; requirements are unknown.

PhotoPrism is an alternative AI-powered photos application [H03-E2]. Inspect it first if a specific AI-assisted photo organization task matters more. Benefit is hypothetical: the required feature, video behavior and self-hosting are unverified. If videos remain essential and support cannot be confirmed, preference returns to Immich. If organizing folders is enough, another service may be unnecessary.

Formats, current storage, hosting location, maintenance owner and backup are unknown. Both applications compete for one role; joint installation value has not been shown. One pilot would attribute results and burden to the chosen application. Compatibility remains unknown.

Next question: is joint photo/video management essential, or is a specific AI task more important? Check chosen-version documentation for requirements and an import/recovery path for one synthetic image and video, or the named AI feature. Record supported, unsupported or unknown per requirement. An isolated pilot can then be proposed; personal images are unnecessary. These are investigation options; integration and proposed checks have not been executed.

## CP04-V2-D05 — backend engineer

### RU

Сначала изучите Chi, если нужна только более понятная маршрутизация Go HTTP API: описание подтверждает лёгкий составной маршрутизатор [D05-E2]. Предполагаемая роль — слой маршрутов API. Возможная польза — яснее организовать маршруты и ограничить область изменения; это гипотеза, усилия не измерены. Риск — оставить более широкие требования нерешёнными.

Gin — альтернативный Go HTTP framework для REST API, веб-приложений и микросервисов [D05-E1]. Изучайте его первым, если нужен более широкий framework: он мог бы занять границу обработки HTTP-запросов, но такая потребность пока неизвестна; переход может затронуть больше кода. Совместимость обработчиков и middleware у обоих неизвестна. Описание не доказывает совместимость Chi с net/http, а заявленное автором Gin ускорение до 40 раз не измерено для вашего API и не сравнивает его с Chi.

Запросы и ответы требуется сохранить. Неизвестны нынешний маршрутизатор, версии, интерфейсы, потребности клиентов и допустимые усилия. Потребность в framework или нарушение контракта endpoint меняют предпочтение Chi. Если нынешний маршрутизатор достаточен, сохраняйте его. Оба кандидата занимают одну границу; польза совместной установки не показана. Один endpoint ограничит риск и позволит оценить переход.

Следующий вопрос: что нужно сверх маршрутов? Для одного endpoint зафиксируйте контракт и проверьте интерфейсы выбранной версии. Затем предложите изолированный тест: искусственный запрос должен сохранить статус, обязательные заголовки и тело. Выход — таблица совпадений/расхождений и нужные адаптации. Это варианты для изучения; внедрение и тест не выполнялись.

### EN

Inspect Chi first if clearer Go HTTP API routing is the only need: its description confirms a lightweight composable router [D05-E2]. Its proposed role is the API routing layer. Clearer routes and a focused change are potential benefits, not measured improvements or effort savings. Its trade-off is leaving broader requirements unresolved.

Gin is an alternative Go HTTP framework for REST APIs, web applications and microservices [D05-E1]. Inspect it first if a broader framework is needed: it could occupy the HTTP request-handling boundary, but that need is unknown; adoption may affect more code. Handler/middleware compatibility is unknown for both. The description does not prove Chi's net/http compatibility; Gin's source-reported 40-times speed claim is neither measured for your API nor a comparison with Chi.

Requests and responses must be preserved. Current router, versions, interfaces, client needs and allowable effort are unknown. A framework requirement or endpoint-contract failure reverses the Chi preference. Keep the current router if sufficient. Both candidates occupy one boundary; joint installation benefit is unproven. One endpoint limits risk and makes adoption effort assessable.

Next question: what is needed beyond routing? Freeze one endpoint contract and check chosen-version interfaces. Then propose an isolated test: a synthetic request must preserve status, required headers and body. Output a match/mismatch table and required adaptations. These are investigation options; integration and the test have not been executed.

## CP04-V2-H15 — low-context operator

### RU

Для домашнего бюджета пока нельзя выбрать победителя: неизвестны устройство и обязательные действия без сети. Если нужен настольный бюджет без подключения, сначала изучите my-budget: каталог прямо описывает offline-приложение на Electron [H15-E3]. Его роль — одно приложение бюджета; возможная польза — вести учёт без подключения. Это гипотеза: фактическая работа, совместимость и восстановление неизвестны. Требования платформы и поддержку версии нужно проверить; обязательный мобильный/web-доступ или провал offline-проверки меняют выбор.

BeeCount описан как local-first учёт на iOS/Android/Web с вариантами синхронизации [H15-E1]. Для обязательного ввода на этих устройствах это более явное соответствие, чем описание Actual или настольная роль my-budget. Польза нескольких устройств гипотетическая; нужная синхронизация добавит настройку и восстановление. Если достаточно одного компьютера без сети, предпочтение исчезает. Синхронизация не включается.

Actual — local-first приложение личных финансов [H15-E2], альтернатива для той же роли домашнего бюджета. Возможное соответствие общим задачам финансов — гипотеза; описание не подтверждает нужные устройства, функции или offline-поведение. Выберите другой вариант, если обязательное действие не поддерживается. Local-first не гарантирует работу без сети. Для my-budget commit в снимке датирован 2022-07-27, release неизвестен: это повод проверить поддержку, а не отвергнуть приложение.

Неизвестны задачи бюджета, форматы обмена и резервная копия. Все три занимают одну роль; совместная установка не обоснована. Один пилот позволит связать результат с выбранным приложением. Следующий вопрос: какие устройства обязательны; без сети нужен просмотр или также ввод и повторное открытие? После проверки требований версии предложите искусственные операции с известной суммой: ввод без сети, закрытие/открытие, сверка, документированные выгрузка/восстановление. Выход — поддерживается/не поддерживается/неизвестно по каждому действию. При неудаче сохраните текущий учёт и тестовые данные. Это варианты для изучения; перенос реальных финансов и пилот не выполнялись.

### EN

No household-budget winner is justified yet: required devices and disconnected tasks are unknown. If disconnected desktop budgeting is required, inspect my-budget first: the catalog explicitly describes an offline Electron application [H15-E3]. Its role is one budgeting application; disconnected bookkeeping is a hypothetical benefit. Actual behavior, compatibility and recovery are unknown. Check platform prerequisites and version support; required mobile/web access or a failed offline check reverses preference.

BeeCount is described as local-first bookkeeping on iOS/Android/Web with sync options [H15-E1]. Required entry on those devices is a clearer fit than Actual’s description or my-budget’s proposed desktop role. Cross-device benefit is hypothetical; required sync adds setup/recovery work. If one disconnected computer suffices, the preference disappears. Sync is not enabled.

Actual is a local-first personal finance application [H15-E2], an alternative for the same household-budget role. General finance fit is hypothetical; required devices, features and offline behavior are unverified. Reverse preference if a mandatory task fails. Local-first does not guarantee disconnected operation. For my-budget, the snapshot commit is dated 2022-07-27 and release is unknown: check support rather than rejecting it.

Budget tasks, exchange formats and backup are unknown. All three occupy one role; joint installation is unsupported. One pilot would attribute results to one application. Next question: which devices are mandatory; must disconnected use support viewing only, or entry/reopening too? After checking version requirements, propose synthetic transactions with a known total: disconnected entry, close/reopen, reconciliation, documented export/recovery. Output supported/unsupported/unknown per task. On failure retain current bookkeeping and test data. These are investigation options; real-finance migration and the pilot have not been executed.

## CP04-V2-H11 — Russian-speaking engineer

### RU

Начните с изучения InfluxDB, если главное — хранить метрики и события: описание прямо совпадает с этой задачей [H11-E1]. Его предполагаемая роль — хранилище за границей приёма данных и запросов. Соответствие нужной аналитике — гипотеза; интерфейсы, эксплуатация и восстановление неизвестны. Победителя для внедрения пока выбрать нельзя: Brief не определяет запросы и нынешнюю базу.

QuestDB описан как база временных рядов [H11-E3], альтернатива на той же границе. Возможная польза — анализ временных окон, если обязательные запросы поддерживаются; это гипотеза. Предпочтите его InfluxDB, если одинаковая проверка покажет лучшее соответствие запросам и правилам событий. Описание этого не доказывает; адаптация интерфейсов и обслуживание неизвестны. Провал обязательного сценария меняет предпочтение любого кандидата.

TimescaleDB — база временных рядов в форме расширения Postgres [H11-E2]. Изучайте его первым только при подтверждённых существующем совместимом PostgreSQL и разрешении на расширения. Тогда он мог бы использовать существующее хранилище и часть его эксплуатации; выгода и совместимость неизвестны. Brief не подтверждает PostgreSQL. Отсутствие, несовместимая версия, запрет расширений или провал сценария меняют выбор.

Неизвестны схема, частота записи, срок хранения, агрегаты, допустимая задержка и правила дубликатов/поздних событий. Скорость, нагрузка и стоимость не сравнивались. Если нынешняя база достаточна, сохраняйте её. Все три — альтернативы одному хранилищу; польза совместной установки не показана. Один пилот позволит связать результат с движком.

Следующий вопрос: есть ли PostgreSQL и разрешены ли расширения; какой оконный агрегат и правила событий обязательны? Зафиксируйте подтверждено/отсутствует/неизвестно и разрешено/запрещено/неизвестно. Проверьте документацию версии, затем предложите искусственные события с известным агрегатом, дубликатом и поздним событием. Выход — ожидаемые/полученные значения, обработка каждого события и сохранность после перезапуска. При несовпадении сохраните нынешнюю базу и тестовые данные. Это варианты для изучения; подключение, миграция и проверки не выполнялись.

### EN

Inspect InfluxDB first if metrics/events are the priority: its description directly matches that task [H11-E1]. Its proposed role is storage behind ingestion and queries. Fit to required analytics is hypothetical; interfaces, operation and recovery are unknown. No adoption winner is justified: the Brief does not define queries or current storage.

QuestDB is described as a time-series database [H11-E3], an alternative at the same boundary. Time-window analysis is a potential benefit if required queries are supported, not an observed result. Prefer it over InfluxDB if the same check shows better query/event-rule fit. Descriptions do not prove that; interface adaptation and upkeep are unknown. Failure of a mandatory scenario reverses any candidate preference.

TimescaleDB is a time-series database packaged as a Postgres extension [H11-E2]. Inspect it first only with confirmed existing compatible PostgreSQL and extension permission. It could reuse existing storage and part of its operation; benefit and compatibility are unknown. The Brief does not establish PostgreSQL. Absence, incompatible versions, forbidden extensions or workload failure reverses preference.

Schema, write rate, retention, aggregates, acceptable latency and duplicate/late-event rules are unknown. Speed, load and cost were not compared. Keep current storage if sufficient. All three are alternatives for one datastore; joint installation value is unproven. One pilot attributes results to an engine.

Next question: is PostgreSQL present and are extensions allowed; which window aggregate and event rules are mandatory? Record confirmed/absent/unknown and allowed/forbidden/unknown. Check version documentation, then propose synthetic events with a known aggregate, duplicate and late event. Output expected/observed values, handling per event and restart persistence. On mismatch retain current storage and test data. These are investigation options; connection, migration and checks have not been executed.

## Evidence and action boundary

The user-facing labels H03-E1 etc. resolve below to the exact source descriptions preserved in the JSON packet. The frozen snapshot was observed on 2026-09-01; commit/release dates remain separate per repository in `source_projection.reference_options`. No upstream refresh was performed. Descriptive performance language is not a benchmark.

All ten source roles remain `reference_only`, with `adoption_fit=unknown`: these are options to inspect, not components verified for this project. Conditional inspection preference does not change catalog status or eligibility. All proposed architecture placements are conditional; compatibility and measured project benefit remain unknown. No complementary set has been demonstrated.

The same canonical selected IDs/order, roles, source refs, pins, query/result/pack/capture bindings and proposed action state bind both locales. The JSON contains those full exact bindings; hashes are not repeated for every case in this report. All integrations and validation tasks are `proposed_not_executed`; `human_response=null`, `human_calibrated=false`, `promotion_ready=false`.

| Case | Evidence label | Repository and canonical ID | Capability source field |
| --- | --- | --- | --- |
| CP04-V2-H03 | H03-E1 | [immich-app/immich](https://github.com/immich-app/immich) — 455229168 | `/descriptions/upstream` |
| CP04-V2-H03 | H03-E2 | [photoprism/photoprism](https://github.com/photoprism/photoprism) — 119160553 | `/descriptions/upstream` |
| CP04-V2-D05 | D05-E1 | [gin-gonic/gin](https://github.com/gin-gonic/gin) — 20904437 | `/descriptions/upstream` |
| CP04-V2-D05 | D05-E2 | [go-chi/chi](https://github.com/go-chi/chi) — 44344606 | `/descriptions/upstream` |
| CP04-V2-H15 | H15-E1 | [TNT-Likely/BeeCount](https://github.com/TNT-Likely/BeeCount) — 1051440251 | `/descriptions/catalog` |
| CP04-V2-H15 | H15-E2 | [actualbudget/actual](https://github.com/actualbudget/actual) — 486815039 | `/descriptions/upstream` |
| CP04-V2-H15 | H15-E3 | [reZach/my-budget](https://github.com/reZach/my-budget) — 173851397 | `/descriptions/catalog` |
| CP04-V2-H11 | H11-E1 | [influxdata/influxdb](https://github.com/influxdata/influxdb) — 13124802 | `/descriptions/upstream` |
| CP04-V2-H11 | H11-E2 | [timescale/timescaledb](https://github.com/timescale/timescaledb) — 84240850 | `/descriptions/upstream` |
| CP04-V2-H11 | H11-E3 | [questdb/questdb](https://github.com/questdb/questdb) — 19257422 | `/descriptions/upstream` |

BeeCount and my-budget retain null upstream descriptions; their capabilities here come from catalog descriptions. Actual retains a null catalog description and uses its upstream description. No missing description is filled or relabeled.

## Reproducibility and review

- Candidate instruction: `plugins/myai-stackguide/skills/myai-stackguide/SKILL.md`, SHA-256 `21ff59a7cb0465ab6f8307b29427096d369f2470d231ba410a8de95707d6246e`. Final rationale paragraph was reread after the explicit insufficient-evidence sentence.
- Prospective baseline: `evals/plugin-v1/results/cp04-v2-2026-10-08/project-fit-baseline.json`, SHA-256 `0d59ad368e2b98e22334cac7ae5d6d1b86a75f4d51a15c6145cddbe2b37ced18`; its old hashes and qualitative criteria remain unchanged.
- Input projection: `evals/plugin-v1/results/cp04-v2-2026-10-08/recommendation-calibration.json`, SHA-256 `c71f2799c86ebd725545825715f8dc32441f33a31f03f132dc52311f59a99377`. Only synthetic context, canonical goal/options and exact capture bindings support the new composition. One exploratory print unintentionally included historical presentation; prior ratings were not read or used.
- Loaded role: `product_planner`, configured `gpt-6.1-sol` / `high`; no configuration change or model suitability comparison. Inference latency, token usage and cost are unavailable, not zero.
- Self-review checks source scope, hypotheses, conditional choice, decisive unknown, role/action boundaries and paired meaning; independent Astra review is next. No numeric regrading or frozen retrieval tuning.

The explanation packet has its own schema version; it does not alter C8/C9 contracts. CP-04 retains `in_progress` / `partially_verified` / `no_go`. Independent static comparison and human usefulness calibration remain separate gates; browser, actual project compatibility, integration and release readiness are unproven. Rollback is removal of these two new artifacts under primary ownership coordination, preserving baseline/captures and unrelated work.
