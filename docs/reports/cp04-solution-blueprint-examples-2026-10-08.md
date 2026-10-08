# CP-04 solution blueprint examples — 2026-10-08

Two prospective RU/EN blueprints reuse unchanged frozen captures and synthetic contexts. Planning assumptions are explicit; no integration, proposed test or implementation duration was measured.

## CP04-V2-D05

### RU

**Решение и границы**
Для более понятной маршрутизации Go API сначала проверьте, можно ли решить задачу нынешними или стандартными средствами. Если нет, изучите Chi: источник описывает лёгкий составной маршрутизатор [D05-E2]. Его возможная польза — яснее организовать маршруты и облегчить проверку изменений, сохранив запросы и ответы. Это гипотеза, а не измеренная экономия. Gin — альтернатива, если потребуется более широкий HTTP framework [D05-E1]; вместе их устанавливать не предлагается.

**Предлагаемый стек**
Условная схема: клиент → нынешний Go HTTP server → один выбранный маршрутизатор → существующие обработчики → логика и данные проекта. Сохраняются имеющиеся бизнес-правила, проверки доступа и хранилище; новые права на данные маршрутизатору не назначаются. Реальная архитектура неизвестна: перед изменением нужно подтвердить эти границы. Тесты контрактов, CI и staging сохраняются, только если уже есть. Новым компонентом в сценарии становится Chi; Gin не входит в его оценку.

**Техническая работа и польза продукту**
Источник подтверждает назначение маршрутизатора, но не совместимость Chi с net/http, конкретные middleware, функции безопасности или готовое тестовое покрытие. Повторное использование касается основы маршрутизации. Команда всё равно описывает контракт endpoint, адаптирует обработчики, сохраняет авторизацию и бизнес-правила, проверяет интерфейсы данных и ошибки, пишет нужные регрессионные проверки и готовит эксплуатацию. Сначала один искусственный запрос должен дать прежние статус, обязательные заголовки и тело; выход — ожидаемые/полученные значения и расхождения. Так архитектурное изменение связывается с пользой: клиентское поведение остаётся понятным и проверяемым. Измерений скорости нет; заявление Gin «до 40 раз» не является сравнением для этого API.

**Сложность и допущения оценки**
Сложность условно средняя: нужно совместить интерфейсы, сохранить HTTP-контракт и проверки доступа, проверить версию/лицензию и обеспечить откат. Это сценарий для одного опытного Go-инженера и максимум пяти простых маршрутов. Предполагаются совместимые обработчики, допустимая лицензия выбранной версии, готовые контракты, тесты, CI и staging; всё перечисленное требует подтверждения. Перенос авторизации, базы, данных, frontend и бизнес-правил исключён из этой оценки. Один совместимый маршрут может снизить сложность; больше маршрутов, сложные middleware, отсутствие тестов или необходимость миграции требуют пересчёта.

**Приблизительное время**
Ниже экспертный план с низкой уверенностью, не измерение и не обещание срока. Исследование 2–4 часа и один endpoint 4–8 часов вместе образуют первый пилот: 6–12 инженерных часов, или 0.75–1.5 инженерного дня по 8 часов. Условное внедрение в пределах пяти маршрутов, включая этот пилот, — 16–32 часа, или 2–4 инженерных дня. При полной последовательной занятости это примерно 1–2 рабочих дня для пилота и 2–4 для всего указанного объёма. Остаток после пилота — 10–20 часов; пилот повторно не прибавляется. Ожидание доступа, согласований и review неизвестно и добавляется отдельно; фактический срок от начала до конца неизвестен.

**Почему использовать готовое решение**
При достаточных нынешних/стандартных средствах их сохранение предпочтительнее новой зависимости. Chi может избавить от разработки основы маршрутизации, если составная организация действительно нужна, но добавляет интеграцию, фиксацию версии и будущие проверки совместимости. Качество сопровождения upstream неизвестно. Альтернатива с нуля — узкий собственный слой маршрутов того же объёма, не целый framework: команда сама отвечает за крайние случаи, тесты и поддержку. Он оправдан лишь при доказанной потребности, которую существующие варианты не закрывают. Численной экономии или множителя нет. Следующий вопрос: что нужно сверх маршрутизации и можно ли предоставить контракт одного endpoint? После проверки сохраните старые маршруты и предложите обратимый пилот. Внедрение, тесты и deployment не выполнялись.

| Этап | Инженерные часы | Дни по 8 часов |
| --- | ---: | ---: |
| Уточнение и предпосылки | 2–4 | 0.25–0.5 |
| Пилот одного endpoint | 4–8 | 0.5–1 |
| Оставшиеся маршруты | 4–8 | 0.5–1 |
| Регрессии, staging, откат | 6–12 | 0.75–1.5 |
| **Пилот, включая уточнение** | **6–12** | **0.75–1.5** |
| **Всего: условные пять маршрутов, включая пилот** | **16–32** | **2–4** |

| Состав стека | Роль |
| --- | --- |
| Нынешний Go HTTP server, обработчики, бизнес-правила и данные — где есть | Сохраняемые компоненты проекта; подтвердить реальные границы |
| Chi — условно новый | Только основа маршрутизации |
| Тесты контрактов, CI, staging — предполагаются доступными | Сохраняемые проверки; наличие неизвестно |
| Gin | Альтернатива, не член этого стека |

### EN

**Decision and scope**
For clearer Go API routing, first check whether current or standard/native facilities can solve the problem. If they cannot, inspect Chi: the source describes a lightweight composable router [D05-E2]. Potential value is clearer route organization and easier change review while preserving requests and responses. This is a hypothesis, not measured savings. Gin is an alternative if a broader HTTP framework is needed [D05-E1]; joint installation is not proposed.

**Proposed stack**
Conditional flow: client → current Go HTTP server → one chosen router → existing handlers → project logic and data. Existing business rules, authorization checks and storage remain; the router receives no new data authority. Actual architecture is unknown, so verify these boundaries before changing them. Contract tests, CI and staging are retained only if present. Chi is the proposed new component in this scenario; Gin is outside its estimate.

**Technical work and product benefit**
The source supports router positioning, not Chi net/http compatibility, specific middleware, security features or supplied test coverage. Reuse covers a routing foundation. The team still defines endpoint contracts, adapts handlers, preserves authorization/business rules, checks data interfaces and errors, adds necessary regression checks and prepares operations. First, one synthetic request must produce the previous status, required headers and body; output expected/observed values and mismatches. This connects architecture work to a product hypothesis: client behavior remains understandable and verifiable. Speed is unmeasured; Gin's up-to-40-times claim is not a comparison for this API.

**Complexity and estimate assumptions**
Complexity is conditionally medium: align interfaces, preserve HTTP contracts and access checks, verify version/license and provide rollback. The scenario assumes one experienced Go engineer and at most five simple routes. Compatible handlers, an acceptable selected-version license, existing contracts, tests, CI and staging are all hypothetical prerequisites requiring confirmation. Authorization, database, stored-data, frontend and business-rule migration are excluded from this estimate. One compatible route may lower complexity; more routes, complex middleware, missing tests or migration needs require re-estimation.

**Approximate time**
The phase table is an expert plan with low confidence, not measurement or a delivery promise. Discovery at 2–4 hours plus one endpoint at 4–8 hours makes the first pilot 6–12 engineer-hours, or 0.75–1.5 eight-hour engineer-days. Conditional adoption within five routes, including that pilot, is 16–32 hours, or 2–4 engineer-days. With sequential full allocation, allow approximately 1–2 working days for the pilot and 2–4 for the whole stated scope. Remaining work after the pilot is 10–20 hours; do not add the pilot twice. Access, approval and review waits are unknown and additional; actual start-to-finish time is unknown.

**Why reuse**
Retain current/native facilities if sufficient rather than adding a dependency. Chi may avoid building a routing foundation if composition is needed, but introduces integration, version pinning and future compatibility checks. Upstream maintenance quality is unknown. Building from scratch means a narrow project-owned routing layer of equivalent scope, not an entire framework: the team owns edge behavior, tests and maintenance. Justify it only for demonstrated needs existing options cannot cover. No numeric savings or multiplier is claimed. Next question: what is needed beyond routing, and can one endpoint contract be supplied? Then retain old routes and propose a reversible pilot. Integration, tests and deployment have not been executed.

| Phase | Engineer-hours | Eight-hour engineer-days |
| --- | ---: | ---: |
| Discovery and prerequisites | 2–4 | 0.25–0.5 |
| One-endpoint pilot | 4–8 | 0.5–1 |
| Remaining routes | 4–8 | 0.5–1 |
| Regression, staging, rollback | 6–12 | 0.75–1.5 |
| **Pilot, including discovery** | **6–12** | **0.75–1.5** |
| **Total: hypothetical five routes, including pilot** | **16–32** | **2–4** |

| Stack member | Role |
| --- | --- |
| Current Go HTTP server, handlers, business rules and data — where present | Retained project components; verify real boundaries |
| Chi — conditionally new | Routing foundation only |
| Contract tests, CI, staging — hypothetically available | Retained checks; presence unknown |
| Gin | Alternative, not a member of this stack |

## CP04-V2-H15

### RU

**Решение и стек**
Для домашнего бюджета сначала определите устройства, обязательные действия без сети и данные для импорта. Пока полный стек и срок внедрения неизвестны. Условный стек проверки — одно приложение, одно выбранное устройство, десять искусственных операций и проверяемый путь хранения/выгрузки. Нынешний учёт и исходные записи остаются авторитетными; переключение данных не предлагается.

**Три альтернативы одной роли**
BeeCount описан как local-first учёт на iOS/Android/Web с вариантами синхронизации [H15-E1]; Actual — local-first приложение личных финансов [H15-E2]; my-budget — offline-бюджет на Electron [H15-E3]. При обязательных мобильных/web-устройствах изучайте BeeCount; при настольной работе без сети — my-budget; Actual рассматривайте для общего сценария личных финансов. Все предпочтения условны. Local-first не гарантирует нужное offline-поведение. Вместе приложения не образуют полезный стек: они претендуют на одно место бюджета.

**Покрытие, архитектура и сложность**
Предлагаемая связь — человек → одно приложение → подтверждённое хранилище/выгрузка. Возможная польза — вести нужный бюджет на нужном устройстве без подключения; это гипотеза. Источники подтверждают назначение приложений, не нужные финансовые правила, импорт, восстановление или совместимость. Команда проверяет версию, лицензию, поддержку, правильность расчётов и резервную копию; будущие миграция, обучение и интеграции требуют отдельного плана. Сложность полной задачи неизвестна. Уточнение условно простое; один пилот — средней сложности из-за установки, offline-сохранения и восстановления. Несколько устройств, синхронизация, неподдерживаемый формат импорта или отсутствующая документация меняют оценку.

**Время и выбор против разработки с нуля**
Только для условной проверки: один опытный инженер, доступный пользователь, одно устройство и документированные установка/выгрузка/восстановление. Уточнение 2–4 часа плюс искусственный пилот 4–8 часов — 6–12 инженерных часов, 0.75–1.5 дня по 8 часов, примерно 1–2 рабочих дня полной занятости без ожиданий. Уверенность низкая; срок полной миграции и ожидания неизвестны. Сохраните нынешний/local/native учёт, если он достаточен. Готовое приложение может заменить создание основы учёта, но не проверки данных и обслуживание. Собственная реализация тех же действий добавит модель операций, расчёты, сохранение, восстановление, UI и тесты; численной экономии нет. Следующий вопрос — устройства, offline-действия и формат импорта. Затем предложите сверку искусственных сумм, повторное открытие без сети и документированное восстановление. При неудаче сохраните нынешний учёт. Реальные данные, синхронизация и пилот не задействованы.

| Этап | Инженерные часы | Дни по 8 часов |
| --- | ---: | ---: |
| Уточнение объёма | 2–4 | 0.25–0.5 |
| Условный искусственный пилот | 4–8 | 0.5–1 |
| **Пилот, включая уточнение** | **6–12** | **0.75–1.5** |
| **Полное внедрение/миграция** | **Неизвестно** | **Неизвестно** |

### EN

**Decision and stack**
For household budgeting, first define required devices, disconnected tasks and data to import. The complete stack and adoption timeline are unknown. A conditional validation stack is one app, one selected device, ten synthetic transactions and a verifiable storage/export path. Current bookkeeping and original records remain authoritative; no data-authority switch is proposed.

**Three alternatives for one role**
BeeCount is described as local-first bookkeeping on iOS/Android/Web with sync options [H15-E1]; Actual as a local-first personal finance app [H15-E2]; my-budget as offline Electron budgeting [H15-E3]. Inspect BeeCount for mandatory mobile/web devices, my-budget for disconnected desktop use, and Actual for general personal finance. All preferences are conditional. Local-first does not guarantee required offline behavior. Together they are not a justified stack: they compete for one budgeting slot.

**Coverage, architecture and complexity**
Proposed flow: person → one app → verified storage/export. Required budgeting on the required device without a connection is a hypothetical benefit. Sources establish application positioning, not required financial rules, imports, recovery or compatibility. The team checks version, license, support, calculation correctness and backup; future migration, training and integrations need separate planning. Full-task complexity is unknown. Discovery is conditionally low; one pilot is medium because setup, disconnected persistence and recovery need checking. Multiple devices, sync, unsupported imports or missing documentation change the estimate.

**Time and reuse versus custom work**
For validation only: one experienced engineer, an available operator, one device and documented setup/export/recovery. Discovery at 2–4 hours plus a synthetic pilot at 4–8 is 6–12 engineer-hours, 0.75–1.5 eight-hour engineer-days, approximately 1–2 fully allocated working days excluding waits. Confidence is low; full migration time and waits are unknown. Retain current/local/native bookkeeping if sufficient. An app may reuse a bookkeeping foundation, but not remove data checks or upkeep. Equivalent custom tasks add a transaction model, calculations, persistence, recovery, UI and tests; no numeric savings are established. Next question: devices, offline tasks and import format. Then propose synthetic-total reconciliation, disconnected reopening and documented recovery. On failure retain current bookkeeping. Real data, sync and the pilot have not been used.

| Phase | Engineer-hours | Eight-hour engineer-days |
| --- | ---: | ---: |
| Scope discovery | 2–4 | 0.25–0.5 |
| Conditional synthetic pilot | 4–8 | 0.5–1 |
| **Pilot, including discovery** | **6–12** | **0.75–1.5** |
| **Full adoption/migration** | **Unknown** | **Unknown** |

## Evidence, estimates and review boundary

Full descriptions, source/evidence refs, selected IDs/order, roles, pins and capture bindings are retained exactly in the JSON. RU/EN metadata binds the same assumptions, phase ranges, units and proposed action state. Phase lower/upper effort bounds sum directly; engineer-days equal hours divided by eight. Pilot elapsed working bounds round up only under full allocation; unknown waits are additional and actual start-to-finish time remains unknown.

| Label | Frozen source |
| --- | --- |
| D05-E1 | [gin-gonic/gin](https://github.com/gin-gonic/gin) — 20904437, `/descriptions/upstream` |
| D05-E2 | [go-chi/chi](https://github.com/go-chi/chi) — 44344606, `/descriptions/upstream` |
| H15-E1 | [TNT-Likely/BeeCount](https://github.com/TNT-Likely/BeeCount) — 1051440251, `/descriptions/catalog` |
| H15-E2 | [actualbudget/actual](https://github.com/actualbudget/actual) — 486815039, `/descriptions/upstream` |
| H15-E3 | [reZach/my-budget](https://github.com/reZach/my-budget) — 173851397, `/descriptions/catalog` |

All five canonical roles remain `reference_only`; adoption fit and compatibility are unknown. Source observation and commit/release dates remain independent. BeeCount/my-budget keep null upstream descriptions; Actual keeps a null catalog description. Frozen snapshot evidence is not live verification.

- Explicitly read candidate instruction: `plugins/myai-stackguide/skills/myai-stackguide/SKILL.md`, SHA-256 `5f55458d649183e4869c7571cde3d19dfae55b7a19bf573008ea3eb4b1f26148`.
- Frozen prospective baseline: `evals/plugin-v1/results/cp04-v2-2026-10-08/solution-blueprint-baseline.json`, SHA-256 `7142f6c6cf825433ec50a2597b0e22964a79ec7b77822674faf7e31df489f8e5`.
- Frozen input: `evals/plugin-v1/results/cp04-v2-2026-10-08/project-fit-explanations.json`, SHA-256 `32e7f42a8535d32ab429a42b0d3c176060b73e5232ebf3f7a995f9937ab46856`.

New agent-authored composition follows the explicitly read solution paragraph with disclosed task criteria; it is not blind routing or installed activation evidence. Loaded role is product_planner, `gpt-6.1-sol` / `high`; model suitability was not evaluated. Inference latency, tokens and cost are unavailable. All integration/check steps are `proposed_not_executed`; `human_response=null`, `human_calibrated=false`, `promotion_ready=false`. CP-04 stays `in_progress` / `partially_verified` / `no_go`.

One oversized Windows authoring command failed before execution with launcher error 206; the bounded repair wrote only these two owned files. Source bindings, estimate arithmetic, paired metadata and Markdown text are statically checked; no suites/captures ran. Those checks do not verify estimate accuracy, compatibility, browser switching, project integration or human usefulness.

Independent Astra review is next. Prior explanation artifacts remain frozen. Rollback affects only these two new files under primary coordination.
