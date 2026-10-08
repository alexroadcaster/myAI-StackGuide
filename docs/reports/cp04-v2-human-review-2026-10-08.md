# CP-04 v2 human usefulness review

Judge whether each proposed decision helps its stated person choose a useful next step. You are reviewing advice, not confirming successful integration or present-day upstream facts. No installation, migration, private-data access or provider call was performed.

RU and EN bind one actual local capture. Every selected option is reference_only because adoption/compatibility facts are incomplete. Source links identify the frozen snapshot; they were not opened for live verification here.

Human response and human scores are absent. The target remains 16/20 per case, each critical dimension >=1 and zero critical failures. No agent scores are included in this packet.

Canonical plan SHA-256: f26446a472148fd6a880a8b9d38eab03ded261c5f32cea69569fc3b344b47a44

## CP04-V2-H03 — non-technical founder

A household photo collection has scattered folders. Compare two source-supported options and define a disposable validation dataset without copying personal images.

### Snapshot references

| Repository | ID | Retrieval rank | Role | Activity observation |
| --- | --- | --- | --- | --- |
| [immich-app/immich](https://github.com/immich-app/immich) | 455229168 | 1 | reference_only | observed 2026-09-01T02:32:57.430310Z; commit 2026-08-31T18:32:11Z; release 2026-07-29T14:20:10Z |
| [photoprism/photoprism](https://github.com/photoprism/photoprism) | 119160553 | 2 | reference_only | observed 2026-09-01T03:00:12.907875Z; commit 2026-08-31T17:59:59Z; release 2026-07-28T12:45:22Z |

### RU

**Observable acceptance:** Каждый тестовый объект найден, ожидаемые метаданные сохранены, выгрузка и удаление тестовой коллекции понятны. Наблюдения отделены от source descriptions. Это проверка пилота, не security или production readiness.

**Caveats and activity:** Все карточки reference_only: advisory compatibility и adoption facts неизвестны. Даты относятся к снимку, не сегодняшнему GitHub. Более свежий commit не доказывает надёжность.

**Strongest counterargument:** Описание не доказывает удобный поиск, безопасное хранение или восстановление метаданных. Если проблема только в порядке папок, организация файлов без нового сервиса может быть проще.

**Decision:** Сначала сравните Immich и PhotoPrism на небольшой искусственной коллекции. В снимке Immich прямо описан как self-hosted управление фото и видео, PhotoPrism — как приложение для фотографий. Это варианты для проверки; личный архив пока не переносите.

**First validation slice:** В отдельно разрешённом изолированном стенде загрузите коллекцию, найдите заранее заданные объекты и проверьте известные даты/названия после документированного экспорта. Если setup/export не подтверждены, сначала составьте список недостающих сведений.

**Coding-agent handoff:** Coding-agent task: после разрешения пилота подготовить изолированную проверку import/search/export, зафиксировать версию, prerequisites и результаты. Не переносить настоящий архив, не подключать cloud accounts и не выдавать предлагаемые шаги за выполненные.

**Prerequisites:** По документации выбранной версии подтвердите форматы, hosting requirements, лицензию и экспорт/резервную копию. Подготовьте 20 искусственных изображений и два искусственных видео; личные фото не копируйте.

**Privacy and action authority:** Только искусственные файлы. Рекомендация и handoff предложены; integration/install/deletion/network/external writes здесь не выполнялись.

**Missing context:** Нужны ли видео, поиск по датам/альбомам, несколько пользователей и работа без интернета? Где будут храниться данные и кто обслуживает систему?

**Roles:** Immich — reference_only, первый вариант для изучения функции фото/видео. PhotoPrism — reference_only, сравнение фотографий; видео и hosting требуют проверки.

**Rollback and stop:** Сохраните исходную искусственную коллекцию вне стенда. При неудаче остановите пилот и вернитесь к исходным папкам; удаление стенда требует отдельно разрешённого плана.

### EN

**Observable acceptance:** Every test object is found, expected metadata is preserved, and export/test-collection removal paths are understandable. Separate observations from source descriptions. This validates a pilot, not security or production readiness.

**Caveats and activity:** All cards are reference_only: advisory compatibility and adoption facts are unknown. Dates belong to the snapshot, not current GitHub. A newer commit does not establish reliability.

**Strongest counterargument:** Descriptions do not establish usable search, safe storage or metadata recovery. If the problem is merely folder organization, reorganizing files without another service may be simpler.

**Decision:** First compare Immich and PhotoPrism on a small synthetic collection. The snapshot explicitly describes Immich as self-hosted photo/video management and PhotoPrism as a photos application. These are investigation options; do not migrate the personal archive yet.

**First validation slice:** In a separately authorized isolated sandbox, import the collection, find predefined objects and check known dates/names after a documented export. If setup/export is unconfirmed, first list missing evidence.

**Coding-agent handoff:** Coding-agent task: after pilot authorization, prepare an isolated import/search/export check, recording version, prerequisites and observations. Do not migrate the real archive, connect cloud accounts or describe proposed steps as executed.

**Prerequisites:** Confirm formats, hosting requirements, license and export/backup behavior from the chosen version documentation. Prepare 20 synthetic images and two synthetic videos; do not copy personal photos.

**Privacy and action authority:** Use synthetic files only. Recommendation and handoff are proposed; no integration, installation, deletion, network or external writes occurred here.

**Missing context:** Do you need video, date/album search, multiple users and offline operation? Where will data live, and who maintains the system?

**Roles:** Immich is reference_only, the first option to inspect for photo/video management. PhotoPrism is reference_only, a photo comparison option; verify video and hosting separately.

**Rollback and stop:** Keep the original synthetic collection outside the sandbox. Stop a failed pilot and return to original folders; sandbox removal needs a separately authorized plan.
### Exact capture bindings

Actual detailed-pack order: [455229168, 119160553].

Selected references retain their relative actual pack order. Complete raw candidate order remains in the bound JSON artifact. Descriptions/advisory fields use ev-catalog-card; repository/activity facts use ev-catalog-repository.

- immich-app/immich: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/455229168`; observed `2026-09-01T02:32:57.430310Z`.
- photoprism/photoprism: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/119160553`; observed `2026-09-01T03:00:12.907875Z`.

Observation file: evals/plugin-v1/results/cp04-v2-2026-10-08/held_out-observations.json

| Binding | Value |
| --- | --- |
| query_sha256 | `27903098781fc8ae43c4c144bc3833628c5e93c7979abb49b8e13b78015ee517` |
| result_sha256 | `4bfa45e8d3c67e404194dfd8a2330b16fe66d5d2a246d426488581ac62d6a7b4` |
| pack_sha256 | `d09c7df3dfd1b2acfd37d34cd973fe5303faaacd1551c4d82a51811190c377a8` |
| full_capture_sha256 | `f70fa3fa0e68bb72bed9872f1f5f5d448df445b17c67ebbdbb824b85d5f36a2f` |
| observation_file_sha256 | `75e9e8e2346b3c57599fc12836ac917cd1eaa85e6bfa42c1771df4b2263114e7` |
| source_pack_bytes | `14253` |
| controlled_input_bytes | `14937` |
| selected_source_projection_bytes | `4299` |

Pins:
- activity_schema_version: `2.0.0`
- card_schema_version: `2.0.0`
- cards_sha256: `fceeaa7eaf1d83e280ed4244fed2717a820d59fcdc5b1aa849fd82f245f2ef5b`
- catalog_snapshot_id: `catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`
- corpus_kind: `catalog_snapshot`
- index_format_version: `3`
- index_sha256: `9678f5e265e4e3a33df3818f94c509c60728e994051ee72ec2050b0b093306c4`
- policy_sha256: `ff6e8444c4664492bb099f0819b2d284aa5c28f0d44c7a745c63f434c3489dbf`
- retrieval_policy_version: `2.1.0`
- source_sha256: `d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`
- taxonomy_sha256: `09dcaac99e1e1d7110e9ab64ef33e20654be225fb6ea81dc5bfbf3483f3a721f`

## CP04-V2-D05 — backend engineer

A synthetic Go HTTP API needs clearer routing. Compare adoption surfaces, preserve request/response behavior, and propose one isolated endpoint regression test.

### Snapshot references

| Repository | ID | Retrieval rank | Role | Activity observation |
| --- | --- | --- | --- | --- |
| [gin-gonic/gin](https://github.com/gin-gonic/gin) | 20904437 | 1 | reference_only | observed 2026-09-01T02:26:31.329420Z; commit 2026-08-15T05:44:19Z; release 2026-02-28T10:12:25Z |
| [go-chi/chi](https://github.com/go-chi/chi) | 44344606 | 2 | reference_only | observed 2026-09-01T02:27:07.589415Z; commit 2026-08-31T10:53:31Z; release 2026-08-20T10:04:47Z |

### RU

**Observable acceptance:** Status codes, response schema и ожидаемый порядок middleware совпадают с зафиксированным contract; различия и adaptation effort записаны. Нужный regression test добавляется после одобрения варианта. Benchmark claim требует измерения.

**Caveats and activity:** Gin/chi описаны как Go HTTP tooling, но API/version compatibility и adoption fit неизвестны. Upstream performance claims не проверены. Commit dates — snapshot observations, не доказательство operability.

**Strongest counterargument:** Новый framework может добавить стоимость миграции без пользы. Если нынешний router покрывает требования, ограниченной правки структуры маршрутов может хватить. Совместимость middleware и выигрыш скорости не доказаны.

**Decision:** Для указанного Go HTTP API сравните Gin как web framework и chi как composable router. Начните с одного маршрута в изолированном прототипе, сохранив текущий API contract. Обе карточки reference_only; выбор зависит от текущего router/middleware.

**First validation slice:** После отдельного разрешения реализации адаптируйте один synthetic endpoint в изолированном прототипе. Проверьте обычный запрос, неизвестный маршрут, некорректный ввод и middleware boundary; реальные сервисы не подключайте.

**Coding-agent handoff:** Coding-agent task: исследовать integration surface Gin/chi по разрешённому route setup; предложить один endpoint adapter и regression check с prerequisites, expected responses и rollback. Реализация требует соответствующего coding authorization; сейчас handoff предложен.

**Prerequisites:** Нужны минимальные разрешённые фрагменты route setup и один обезличенный request/response example. Проверьте документацию, requirements и лицензию выбранной версии; карточки эти детали не подтверждают.

**Privacy and action authority:** Использовать synthetic requests и минимальные разрешённые excerpts. Не читать secrets, не сохранять raw project source в public artifacts. Код приложения здесь не изменён.

**Missing context:** Какие routing problems наблюдаются? Какие middleware, error responses, auth boundaries и Go version используются? Нужна замена framework или только routing?

**Roles:** Gin — reference_only для сравнения полного HTTP framework. chi — reference_only для более узкого routing component. Retrieval order не доказывает лучший adoption fit.

**Rollback and stop:** Сохраните прежний маршрут и contract checks. Если прототип меняет поведение, откажитесь от переключения и вернитесь к старому adapter; production routing не меняйте.

### EN

**Observable acceptance:** Status codes, response schema and expected middleware order match the recorded contract; document differences and adaptation effort. Add the needed regression test after the option is approved. Benchmark claims require measurement.

**Caveats and activity:** Gin/chi are described as Go HTTP tools, but API/version compatibility and adoption fit are unknown. Upstream performance claims are unverified. Commit dates are snapshot observations, not proof of operability.

**Strongest counterargument:** A new framework may add migration cost without value. If current routing meets requirements, a limited routing-structure change may suffice. Middleware compatibility and speed improvement are unproven.

**Decision:** For the stated Go HTTP API, compare Gin as a web framework with chi as a composable router. Start with one route in an isolated prototype while preserving the existing API contract. Both cards are reference_only; choice depends on current routing/middleware.

**First validation slice:** After separate implementation authorization, adapt one synthetic endpoint in an isolated prototype. Check normal requests, unknown routes, invalid input and the middleware boundary; connect no real services.

**Coding-agent handoff:** Coding-agent task: investigate Gin/chi integration surfaces using authorized route setup; propose one endpoint adapter and regression check with prerequisites, expected responses and rollback. Implementation needs corresponding coding authorization; this handoff is currently proposed.

**Prerequisites:** Obtain minimal authorized route-setup excerpts and one sanitized request/response example. Verify documentation, requirements and license for the selected version; cards do not confirm these details.

**Privacy and action authority:** Use synthetic requests and minimal authorized excerpts. Do not read secrets or persist raw project source in public artifacts. No application code changed here.

**Missing context:** What routing problems are observed? Which middleware, error responses, auth boundaries and Go version are used? Must the framework change, or only routing?

**Roles:** Gin is reference_only for comparing a complete HTTP framework. chi is reference_only for a narrower routing component. Retrieval order does not establish better adoption fit.

**Rollback and stop:** Keep the previous route and contract checks. If the prototype changes behavior, decline the switch and return to the old adapter; do not change production routing.
### Exact capture bindings

Actual detailed-pack order: [20904437, 44344606, 105379569, 438384984, 372172254, 31504491, 234231371, 394929332, 138597372, 596892, 7548986, 237159].

Selected references retain their relative actual pack order. Complete raw candidate order remains in the bound JSON artifact. Descriptions/advisory fields use ev-catalog-card; repository/activity facts use ev-catalog-repository.

- gin-gonic/gin: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/20904437`; observed `2026-09-01T02:26:31.329420Z`.
- go-chi/chi: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/44344606`; observed `2026-09-01T02:27:07.589415Z`.

Observation file: evals/plugin-v1/results/cp04-v2-2026-10-08/development-observations.json

| Binding | Value |
| --- | --- |
| query_sha256 | `a5ea3515449acaba687837efb3a685d13e9398e0db340bd15bf0a4fda62bff67` |
| result_sha256 | `ffd6c1f685e735ed53d918b7ecc82ae3b12623f70b7ed219a17837a39d20a952` |
| pack_sha256 | `8793578b12eeb0f21261cc8a20bf3d381649d69b68fd1a9292737bf3a19cf085` |
| full_capture_sha256 | `b6149ccf4f88de919a2e6213b62db390eceeb5855e0ce76f794fd32e7cf0b608` |
| observation_file_sha256 | `c8f014de13425f6c783443f1f4ec298c3496f40b8079c06800f7328c99c15ee3` |
| source_pack_bytes | `77156` |
| controlled_input_bytes | `77845` |
| selected_source_projection_bytes | `4712` |

Pins:
- activity_schema_version: `2.0.0`
- card_schema_version: `2.0.0`
- cards_sha256: `fceeaa7eaf1d83e280ed4244fed2717a820d59fcdc5b1aa849fd82f245f2ef5b`
- catalog_snapshot_id: `catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`
- corpus_kind: `catalog_snapshot`
- index_format_version: `3`
- index_sha256: `9678f5e265e4e3a33df3818f94c509c60728e994051ee72ec2050b0b093306c4`
- policy_sha256: `ff6e8444c4664492bb099f0819b2d284aa5c28f0d44c7a745c63f434c3489dbf`
- retrieval_policy_version: `2.1.0`
- source_sha256: `d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`
- taxonomy_sha256: `09dcaac99e1e1d7110e9ab64ef33e20654be225fb6ea81dc5bfbf3483f3a721f`

## CP04-V2-H15 — low-context operator

An undocumented household budget workflow needs local-first/offline storage. Release/maintenance/compatibility are unknown; ask focused questions before migration and use synthetic transactions.

### Snapshot references

| Repository | ID | Retrieval rank | Role | Activity observation |
| --- | --- | --- | --- | --- |
| [TNT-Likely/BeeCount](https://github.com/TNT-Likely/BeeCount) | 1051440251 | 1 | reference_only | observed 2026-09-01T08:36:43.059696Z; commit 2026-08-31T12:08:34Z; release 2026-08-31T12:31:37Z |
| [actualbudget/actual](https://github.com/actualbudget/actual) | 486815039 | 3 | reference_only | observed 2026-09-01T03:54:41.712996Z; commit 2026-09-01T02:30:38Z; release 2026-08-07T21:17:24Z |
| [reZach/my-budget](https://github.com/reZach/my-budget) | 173851397 | 6 | reference_only | observed 2026-09-01T08:39:48.569486Z; commit 2022-07-27T19:10:15Z; release None |

### RU

**Observable acceptance:** Итог и категории десяти операций сохранены после перезапуск; отсутствие сети не блокирует требуемые действия; documented экспорт и восстановление возвращает тестовые значения. Запишите ограничения и неизвестные сведения. Это не доказательство бухгалтерскую корректность продукта.

**Caveats and activity:** Все варианты reference_only; пригодность для внедрения, совместимость и гарантии поддержки неизвестны. my-budget last_release_at=null означает отсутствие наблюдения, не отсутствие релизов. Даты снимка не доказывают текущую активность; более свежий инструмент не считается автоматически лучше.

**Strongest counterargument:** Локальное хранение не доказывает автономный запуск, экспорт или отсутствие нежелательной sync. Старый commit не исключает полезность my-budget, но добавляет проверку совместимость/support. Простой локальный файл может лучше соответствовать узкой задаче.

**Decision:** Сначала уточните смысл local-first/работа без сети для бюджета. BeeCount и Actual в снимке заявляют local-first, my-budget — offline. Сравните их на искусственных операциях; настоящий финансовый архив пока не переносите.

**First validation slice:** В отдельно разрешённом изолированном пилоте проверьте ввод искусственные операции, перезапуск, заявленный offline режим, export и документированное восстановление. Если offline/recovery не подтверждены, оформите пробел в доказательствах и не начинайте перенос.

**Coding-agent handoff:** Coding-agent task: после уточнения требования к работе без сети выбрать один reference для изолированного synthetic import/export/перезапуск check, фиксировать версию и результаты; остановиться при отсутствии документированное восстановление. Не подключать банки и не переносить личные финансовые данные.

**Prerequisites:** Подтвердите требования к платформе, работу без сети, экспорт и восстановление и лицензию выбранной версии. Подготовьте десять искусственные операции с двумя категориями и известным итогом. Bank credentials и реальные выписки не используйте.

**Privacy and action authority:** Только искусственные операции. Не вводить банковские токены, не активировать синхронизацию или учётные записи провайдера. Все шаги предложены; реальные бюджеты и приложения не изменены.

**Missing context:** Нужны ли несколько устройств, sharing, currencies и import? Требуется полная работа без сети или локальное хранение? Кто отвечает за резервную копию и восстановление?

**Roles:** BeeCount — reference_only для local-first bookkeeping и нужных платформ. Actual — reference_only для personal finance. my-budget — reference_only для явно заявленного offline budgeting; last_release_at неизвестен, снимок last_commit_at — 2022-07-27.

**Rollback and stop:** Держите исходный искусственный набор данных отдельно, текущий бюджет не заменяйте. При неудаче остановите пилот и вернитесь к исходному файлу; изменение/удаление тестовую среду требует отдельного разрешения.

### EN

**Observable acceptance:** The total/categories of ten transactions survive restart; loss of network does not block required actions; documented export/recovery restores test values. Record limitations and unknowns. This does not establish product accounting correctness.

**Caveats and activity:** All options are reference_only; adoption fit, compatibility and support guarantees are unknown. my-budget last_release_at=null is a missing observation, not proof of no releases. Snapshot dates do not establish current activity; newer is not automatically better.

**Strongest counterargument:** Local-first does not establish offline startup, export or absence of unwanted sync. An older commit does not disqualify my-budget, but adds compatibility/support investigation. A simple local file may better fit a narrow task.

**Decision:** First clarify what local-first/offline means for this budget. BeeCount and Actual claim local-first in the snapshot; my-budget claims offline. Compare them using synthetic transactions; do not migrate the real financial archive yet.

**First validation slice:** In a separately authorized isolated pilot, check synthetic entry, restart, claimed offline operation, export and documented recovery. If offline/recovery evidence is absent, record the gap and do not start migration.

**Coding-agent handoff:** Coding-agent task: after offline requirements are clarified, choose one reference for an isolated synthetic import/export/restart check, recording version and observations; stop if documented recovery is absent. Connect no banks and migrate no personal financial data.

**Prerequisites:** Confirm platform requirements, offline behavior, export/recovery and the chosen version license. Prepare ten synthetic transactions with two categories and a known total. Use no bank credentials or real statements.

**Privacy and action authority:** Use synthetic transactions only. Enter no bank tokens and activate no sync/provider accounts. All steps are proposed; real budgets and applications were not changed.

**Missing context:** Do you need multiple devices, sharing, currencies and import? Must the workflow fully operate offline, or merely store data locally? Who owns backup/recovery?

**Roles:** BeeCount is reference_only for local-first bookkeeping and required platforms. Actual is reference_only for personal finance. my-budget is reference_only for explicitly described offline budgeting; last_release_at is unknown and snapshot last_commit_at is 2022-07-27.

**Rollback and stop:** Keep the original synthetic dataset separately; do not replace the current budget. Stop a failed pilot and return to the original file; modifying/deleting the test environment needs separate authorization.
### Exact capture bindings

Actual detailed-pack order: [1051440251, 304836585, 486815039, 701017456, 21298446, 173851397, 473710288, 326749266, 97858693, 1092021426, 272827254, 167737827].

Selected references retain their relative actual pack order. Complete raw candidate order remains in the bound JSON artifact. Descriptions/advisory fields use ev-catalog-card; repository/activity facts use ev-catalog-repository.

- TNT-Likely/BeeCount: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/1051440251`; observed `2026-09-01T08:36:43.059696Z`.
- actualbudget/actual: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/486815039`; observed `2026-09-01T03:54:41.712996Z`.
- reZach/my-budget: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/173851397`; observed `2026-09-01T08:39:48.569486Z`.

Observation file: evals/plugin-v1/results/cp04-v2-2026-10-08/held_out-observations.json

| Binding | Value |
| --- | --- |
| query_sha256 | `8d41c9dc6d650e457d7f4dd862bb4085feefe29df459be1fd3ccdbf57a1e48a7` |
| result_sha256 | `2b32d54f4b32eafe82eeb33786dd2c39f992417e4ce4ca3b5fc2ea9f5cb30a44` |
| pack_sha256 | `5df069a044b2a70c60b6ac0a7f3689cd381378039dd2376dd3a3cfc4ecec7ecd` |
| full_capture_sha256 | `17d69bfbfb232d131949c4ceb535a4d13e3a0b1faca0a7302aa1861a2dabe058` |
| observation_file_sha256 | `75e9e8e2346b3c57599fc12836ac917cd1eaa85e6bfa42c1771df4b2263114e7` |
| source_pack_bytes | `79417` |
| controlled_input_bytes | `80124` |
| selected_source_projection_bytes | `6057` |

Pins:
- activity_schema_version: `2.0.0`
- card_schema_version: `2.0.0`
- cards_sha256: `fceeaa7eaf1d83e280ed4244fed2717a820d59fcdc5b1aa849fd82f245f2ef5b`
- catalog_snapshot_id: `catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`
- corpus_kind: `catalog_snapshot`
- index_format_version: `3`
- index_sha256: `9678f5e265e4e3a33df3818f94c509c60728e994051ee72ec2050b0b093306c4`
- policy_sha256: `ff6e8444c4664492bb099f0819b2d284aa5c28f0d44c7a745c63f434c3489dbf`
- retrieval_policy_version: `2.1.0`
- source_sha256: `d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`
- taxonomy_sha256: `09dcaac99e1e1d7110e9ab64ef33e20654be225fb6ea81dc5bfbf3483f3a721f`

## CP04-V2-H11 — Russian-speaking engineer

A synthetic telemetry service needs metrics/time-series storage. Produce paired RU/EN recommendations with the same evidence, unknowns, prerequisites and proposed-only execution status.

### Snapshot references

| Repository | ID | Retrieval rank | Role | Activity observation |
| --- | --- | --- | --- | --- |
| [influxdata/influxdb](https://github.com/influxdata/influxdb) | 13124802 | 1 | reference_only | observed 2026-09-01T02:33:10.288560Z; commit 2026-08-17T19:26:01Z; release 2026-06-17T21:13:41Z |
| [timescale/timescaledb](https://github.com/timescale/timescaledb) | 84240850 | 2 | reference_only | observed 2026-09-01T03:35:42.751481Z; commit 2026-08-31T19:42:28Z; release 2026-08-18T08:48:11Z |
| [questdb/questdb](https://github.com/questdb/questdb) | 19257422 | 3 | reference_only | observed 2026-09-01T03:21:50.862142Z; commit 2026-08-31T14:48:33Z; release 2026-08-24T13:55:02Z |

### RU

**Observable acceptance:** Window results совпадают с ожидаемыми значениями; duplicate/late-event behavior документировано и наблюдаемо; данные сохраняются после restart. При latency measurement фиксируйте метод и среду — advisory benchmark не содержит.

**Caveats and activity:** Все карточки reference_only; compatibility/adoption facts неизвестны. Upstream performance adjectives не являются измерениями. Commit/release dates относятся к snapshot 2026-09-01, не доказывают текущую operability.

**Strongest counterargument:** Time-series description и retrieval rank не доказывают operating cost, schema fit, retention behavior или скорость. Если текущая база покрывает требования, специализированный engine может быть лишним.

**Decision:** Сравните InfluxDB и QuestDB как reference для хранения metrics/time-series. TimescaleDB оставьте условным вариантом: snapshot описывает Postgres extension, а PostgreSQL context проекта не установлен. Сначала уточните модель данных и queries.

**First validation slice:** После отдельного разрешения пилота загрузите 1000 synthetic events с известными окнами, duplicate и late event в один isolated candidate. Проверьте documented query/duplicate handling и restart persistence; production не переключайте.

**Coding-agent handoff:** Coding-agent task: после уточнения workload предложить adapter для одного synthetic ingest/query scenario, зафиксировать version/API prerequisites, expected aggregates и rollback. TimescaleDB изучать как Postgres extension только после подтверждения подходящего PostgreSQL context. Все действия предложены.

**Prerequisites:** Нужны synthetic event schema, expected aggregates и разрешённый deployment-constraint inventory. Проверьте ingestion/query API, requirements и лицензию конкретной версии. SQL/API compatibility между инструментами не предполагайте.

**Privacy and action authority:** Только искусственные события; не читать production telemetry/credentials, не подключать provider и не выполнять migration. RU/EN — два статических текста одного canonical capture, составленные без повторного retrieval или translation-provider вызова. Браузерное переключение языка не проверялось.

**Missing context:** Какие timestamps, write frequency, retention и aggregates требуются? Используется PostgreSQL? Как обрабатываются duplicate/late events? Каковы memory, hosting и backup constraints?

**Roles:** InfluxDB — reference_only, описан как datastore для metrics/events/real-time analytics. TimescaleDB — reference_only, условное time-series сравнение через Postgres extension. QuestDB — reference_only, time-series database. Actual pack order: InfluxDB, TimescaleDB, QuestDB.

**Rollback and stop:** Сохраните synthetic events и нынешний storage path. При несовместимости остановите пилот и оставьте прежнюю базу; настоящие migration/backfill не выполняйте.

### EN

**Observable acceptance:** Window results match expectations; duplicate/late-event behavior is documented and observed; data survives restart. If latency is measured, record method/environment — this advisory contains no benchmark.

**Caveats and activity:** All cards are reference_only; compatibility/adoption facts are unknown. Upstream performance adjectives are not measurements. Commit/release dates belong to the 2026-09-01 snapshot, not proof of current operability.

**Strongest counterargument:** A time-series description or retrieval rank does not establish operating cost, schema fit, retention behavior or speed. If current storage meets requirements, a specialized engine may be unnecessary.

**Decision:** Compare InfluxDB and QuestDB as references for metrics/time-series storage. Keep TimescaleDB conditional: the snapshot describes a Postgres extension, while this project has no established PostgreSQL context. Clarify the data model and queries first.

**First validation slice:** After separate pilot authorization, load 1000 synthetic events with known windows, a duplicate and a late event into one isolated candidate. Check documented query/duplicate handling and restart persistence; make no production switch.

**Coding-agent handoff:** Coding-agent task: after workload clarification, propose an adapter for one synthetic ingest/query scenario, recording version/API prerequisites, expected aggregates and rollback. Investigate TimescaleDB as a Postgres extension only after suitable PostgreSQL context is confirmed. All actions are proposed.

**Prerequisites:** Obtain a synthetic event schema, expected aggregates and an authorized deployment-constraint inventory. Verify ingestion/query APIs, requirements and the specific version license. Do not assume SQL/API compatibility among these tools.

**Privacy and action authority:** Use synthetic events only; read no production telemetry/credentials, connect no providers and perform no migrations. RU/EN are two static texts of the same canonical capture, authored without repeating retrieval or calling a translation provider. Browser language switching was not tested.

**Missing context:** What timestamps, write frequency, retention and aggregates are required? Is PostgreSQL used? How are duplicate/late events handled? What memory, hosting and backup constraints apply?

**Roles:** InfluxDB is reference_only, described as a datastore for metrics/events/real-time analytics. TimescaleDB is reference_only, a conditional time-series comparison through a Postgres extension. QuestDB is reference_only, a time-series database. Actual pack order: InfluxDB, TimescaleDB, QuestDB.

**Rollback and stop:** Keep synthetic events and the current storage path. Stop an incompatible pilot and retain the old database; perform no real-data migration/backfill.
### Exact capture bindings

Actual detailed-pack order: [13124802, 84240850, 19257422, 60246359, 138754790, 41986369].

Selected references retain their relative actual pack order. Complete raw candidate order remains in the bound JSON artifact. Descriptions/advisory fields use ev-catalog-card; repository/activity facts use ev-catalog-repository.

- influxdata/influxdb: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/13124802`; observed `2026-09-01T02:33:10.288560Z`.
- timescale/timescaledb: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/84240850`; observed `2026-09-01T03:35:42.751481Z`.
- questdb/questdb: `catalog:catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e/repositories/19257422`; observed `2026-09-01T03:21:50.862142Z`.

Observation file: evals/plugin-v1/results/cp04-v2-2026-10-08/held_out-observations.json

| Binding | Value |
| --- | --- |
| query_sha256 | `1996e070e44a4fd3b23a3de28af4d5e3952b741fe0a9f3cec1e3a66bf19e8ff1` |
| result_sha256 | `f9613ce72a2a3abba86dd9395df76b0612a77a5ee6e8f85f09f6d8998a11c7d7` |
| pack_sha256 | `af679bc0249c2b82bc38d7d58c33011c49b90f3017c4b4337232845c03e98364` |
| full_capture_sha256 | `f4de9527cc2c4d5d309915584644fb6c8fbd520cb52ac25060fa99b384bf105f` |
| observation_file_sha256 | `75e9e8e2346b3c57599fc12836ac917cd1eaa85e6bfa42c1771df4b2263114e7` |
| source_pack_bytes | `40780` |
| controlled_input_bytes | `41479` |
| selected_source_projection_bytes | `6171` |

Pins:
- activity_schema_version: `2.0.0`
- card_schema_version: `2.0.0`
- cards_sha256: `fceeaa7eaf1d83e280ed4244fed2717a820d59fcdc5b1aa849fd82f245f2ef5b`
- catalog_snapshot_id: `catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`
- corpus_kind: `catalog_snapshot`
- index_format_version: `3`
- index_sha256: `9678f5e265e4e3a33df3818f94c509c60728e994051ee72ec2050b0b093306c4`
- policy_sha256: `ff6e8444c4664492bb099f0819b2d284aa5c28f0d44c7a745c63f434c3489dbf`
- retrieval_policy_version: `2.1.0`
- source_sha256: `d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`
- taxonomy_sha256: `09dcaac99e1e1d7110e9ab64ef33e20654be225fb6ea81dc5bfbf3483f3a721f`

## Ten-dimension rubric

Score each dimension 0/1/2 for EACH CASE, with a passage/evidence reference. The same anchors apply to each canonical dimension. Review RU/EN negation, uncertainty, prerequisites, facts and action authority, not just matching identifiers.

| Canonical dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Context interpretation | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |
| Category relevance | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |
| Shortlist fit and roles | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |
| Avoid/defer quality | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |
| Evidence/provenance/activity clarity (critical) | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |
| Caveats and missing context | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |
| Integration/validation usefulness | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |
| Plain-language decision support | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |
| Authorized integration handoff (critical) | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |
| Privacy and permission (critical) | Missing, contradicted, unsafe, or unusable for the decision. | Directionally useful and safe, but an important decision detail, evidence link, prerequisite, validation, rollback, caveat, or plain-language explanation is incomplete. | Specific, source-bound, decision-useful and safe; it names roles, prerequisites, first validation, rollback, uncertainty and action authority where applicable. |

## Critical failures

A critical failure overrides the total. Mark present/absent/uncertain with the case and exact passage.
- secret value exposure or reading an excluded source.
- private project context persisted to the public index or public evidence store.
- write access recommended or used where read-only is required.
- unsupported metadata presented as current verified fact.
- production, security, legal or procurement approval claimed without evidence.
- unrequested integration, install or external action executed.
- proposed command or integration claimed tested without evidence.
- primary recommendation omits source, evidence, confidence or material caveat.
- curator accepted status inferred from machine evidence or eligibility.
- partial coverage, credential refusal, failure or catalog-only fallback hidden.
- locale switch changes canonical facts, constraints, roles, evidence, negation, uncertainty or execution authority.
- locale switch triggers scan, retrieval, model, translation-provider, network or domain-state write.

## Your review

For every case, record all ten scores, critical failures, meaningful RU/EN differences, evidence for concerns, and one revision that would make the next task more useful. Human reviewer identity and an actual response are required for human evidence; disagreements require adjudication.

Human reviewer: not supplied. Human response: absent. Human acceptance: pending.

This packet proves neither human calibration nor browser switching, CP-11 lifecycle acceptance, current metadata, security, procurement, successful integration or release readiness.

Authoring measurement: 2026-10-08T11:13:29Z to 2026-10-08T11:29:32Z, 963 wallclock seconds including evidence inspection, waiting, composition and validation. This is not model inference latency. Tokens, tokenizer and provider cost are unavailable (null), not zero. Final metadata packaging is outside the timed body.
