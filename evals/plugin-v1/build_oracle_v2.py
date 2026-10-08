"""Materialize manually source-assessed judgments; never import/query retrieval.

The explicit assessments below were authored from bounded route projections before
any v2 ranking. Description/topic evidence supports retrieval relevance only;
adoption compatibility, correctness, performance and operational fit stay unknown.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CARDS_PATH = 'plugins/myai-stackguide/assets/catalog.snapshot.json'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_reference():
    return json.loads((HERE / 'quality-plan.json').read_text(encoding='utf8'))


# id suffix, leaf, user goal, literal query, explicit grade assessments by public name.
# Each assessment is a human-readable source interpretation, not a token predicate.
ASSESSMENTS = [
 ('H01','editors_ides','Compare code editors for collaborative multi-user editing.', ['collaborative','multiplayer','code editor'],
  {'zed-industries/zed':(3,'Explicit multiplayer code editor addresses collaboration.'), 'neovim/neovim':(1,'Extensibility is useful for an editor comparison; collaborative editing is unobserved.'), 'helix-editor/helix':(1,'Modal editing is explicit, but collaboration is unobserved.'), 'vim/vim':(1,'Official editor identity offers a comparison reference; collaboration evidence is absent.'), 'microsoft/vscode':(1,'Editor product identity is retained; collaboration details are absent.'), 'VSCodium/vscodium':(1,'VS Code binary distribution can inform editor comparison, but no collaboration capability is stated.')}),
 ('H02','api_contract_testing','Choose local HTTP API doubles so tests can run without a remote account.', ['local','mock APIs','HTTP services'],
  {'mockoon/mockoon':(3,'Explicit local mock APIs with no account or remote deployment.'), 'wiremock/wiremock':(2,'Explicit HTTP service mocking, account/deployment requirements unknown.'), 'mock-server/mockserver-monorepo':(2,'Explicit HTTP(S) mock server and failure injection.'), 'stoplightio/prism':(2,'Explicit OpenAPI-driven mocking server.'), 'mswjs/msw':(2,'Explicit JavaScript API mocking.'), 'pact-foundation/pact-python':(1,'Mock service supports contract tests, a narrower supporting workflow.'), 'pact-foundation/pact-js':(1,'Contract testing is adjacent; local double deployment is unspecified.')}),
 ('H03','media_libraries_readers','Replace scattered photo folders with a self-hosted photo and video management service.', ['self-hosted','photo','video management'],
  {'immich-app/immich':(3,'Explicit self-hosted photo and video management solution.'), 'photoprism/photoprism':(2,'Explicit photos application; hosting and video coverage require verification.'), 'jellyfin/jellyfin':(1,'Explicit media server/API, but photo-management workflow is unobserved.')}),
 ('H04','forms_validation','Validate structured TypeScript application data and preserve type inference.', ['TypeScript','schema validation','type inference'],
  {'colinhacks/zod':(3,'Explicit TypeScript schema validation with static type inference.'), 'ajv-validator/ajv':(2,'Explicit JSON Schema/JTD validation, TypeScript inference is unobserved.'), 'TanStack/form':(1,'Type-safe form state is adjacent to data validation, not a general schema validator.'), 'react-hook-form/react-hook-form':(1,'Explicit form validation supports the UI boundary but general data schemas are unobserved.'), 'jaredpalmer/formik':(1,'React forms are a supporting UI workflow, schema capability unspecified.')}),
 ('H05','accounting_invoicing','Compare text-based command-line bookkeeping with double-entry reporting for a synthetic local ledger.', ['command line','double-entry','plain text'],
  {'ledger/ledger':(3,'Explicit double-entry accounting with command-line reporting.'), 'howeyc/ledger':(3,'Explicit command-line double-entry accounting.'), 'plaintextaccounting/hledger':(2,'Explicit plain-text accounting with CLI; double-entry details require verification.'), 'ad-si/Transity':(2,'Explicit command-line plain-text accounting.'), 'beancount/beancount':(2,'Explicit double-entry accounting from text files; CLI reporting unobserved.'), 'beancount/fava':(1,'Web interface for Beancount is supporting, not the command-line core.'), 'Gnucash/gnucash':(1,'Double-entry accounting is explicit, CLI/text workflow unspecified.'), 'plaintextaccounting/plaintextaccounting':(1,'Plain-text accounting portal informs reading but is not an accounting engine.'), 'arrobalytics/django-ledger':(1,'Double-entry engine is explicit but framework embedding differs from a CLI ledger.')}),
 ('H06','documentation_site_generators','Publish maintainable project documentation as a website, comparing generators and documentation-focused tooling.', ['documentation','websites','Markdown'],
  {'facebook/docusaurus':(3,'Explicit maintainable documentation websites.'), 'mkdocs/mkdocs':(2,'Explicit Markdown project documentation.'), 'slatedocs/slate':(2,'Explicit static API documentation.'), 'withastro/starlight':(2,'Explicit documentation websites with Astro.'), 'squidfunk/mkdocs-material':(2,'Documentation purpose is explicit; generation mechanics unobserved.'), 'vuejs/vitepress':(1,'Static site generation supports delivery, documentation-specific behavior unobserved.'), 'jekyll/jekyll':(1,'Static site generation is supporting; blog-oriented rather than documentation-specific.')}),
 ('H07','scheduling_personal_productivity','Aggregate calendars from multiple providers and expose scheduling context through MCP.', ['calendar sync','Calendar','MCP'],
  {'ridafkih/keeper.sh':(3,'Explicit aggregation/sync/control across Google, Outlook, iCloud and CalDAV/ICS with MCP.'), 'taylorwilsdon/google_workspace_mcp':(2,'Explicit Calendar via Workspace MCP; multi-provider synchronization unobserved.'), 'calcom/cal.diy':(1,'Scheduling infrastructure is adjacent; aggregation/MCP unobserved.'), 'mattt/iMCP':(1,'Personal reminders and contacts MCP is supporting context, calendar aggregation unobserved.')}),
 ('H08','payment_processing_sdks','Add a Node.js server adapter for Stripe payments; compare browser components and samples as supporting references.', ['Node.js','Stripe API','payments'],
  {'stripe/stripe-node':(3,'Explicit Node.js library for Stripe API.'), 'stripe/react-stripe-js':(1,'React Stripe components support frontend work, not the Node server adapter.'), 'stripe/stripe-js':(1,'Browser loading wrapper is supporting, not the server adapter.'), 'stripe-samples/checkout-one-time-payments':(1,'Checkout example informs validation, language and server abstraction unobserved.'), 'juspay/hyperswitch':(1,'Composable payments platform is an architectural comparison, Stripe Node adapter unobserved.')}),
 ('H09','project_task_management','Compare software for agile sprint planning, issue tracking and project roadmaps.', ['agile','sprints','issue tracking'],
  {'opf/openproject':(3,'Explicit agile planning, issue tracking and roadmaps.'), 'makeplane/plane':(3,'Explicit tasks, sprints, docs and triage.'), 'kaleidos-ventures/taiga':(2,'Explicit cross-functional agile project management.'), 'wekan/wekan':(1,'Kanban is supporting planning, sprint/roadmap coverage unspecified.'), 'kanboard/kanboard':(1,'Kanban project management is supporting, sprint/roadmap coverage unspecified.'), 'Leantime/leantime':(1,'Goals-focused project management is adjacent, agile mechanics unspecified.'), 'mattermost-community/focalboard':(1,'Trello/Asana alternative supports task-workflow comparison, sprint mechanics unobserved.')}),
 ('H10','data_ingestion_connectors','Move API, database and file data into a warehouse using reusable ingestion components.', ['ELT','data movement','data loading'],
  {'airbytehq/airbyte':(3,'Explicit API/database/file movement into warehouses and lakes.'), 'meltano/meltano':(2,'Explicit declarative data integration and API integrations.'), 'dlt-hub/dlt':(2,'Explicit Python data loading library.'), 'jitsucom/jitsu':(2,'Explicit ingestion engine and real-time data pipelines.'), 'apache/seatunnel':(2,'Explicit distributed data integration tool.'), 'redpanda-data/connect':(1,'Stream processing is supporting; warehouse ingestion interfaces unspecified.'), 'mage-ai/mage-ai':(1,'Data workflow orchestration supports pipelines, connector coverage unobserved.'), 'snowplow/snowplow':(1,'Customer data infrastructure is adjacent; connector/warehouse details absent.'), 'rudderlabs/rudder-server':(1,'Segment alternative is adjacent customer-data infrastructure, connector details absent.')}),
 ('H11','database_engines','Хранить метрики и временные ряды, сравнить специализированные движки с аналитическими базами.', ['метрики','time-series','real-time analytics'],
  {'questdb/questdb':(3,'Explicit time-series database.'), 'timescale/timescaledb':(3,'Explicit time-series database as a Postgres extension.'), 'influxdata/influxdb':(3,'Explicit datastore for metrics, events and real-time analytics.'), 'ClickHouse/ClickHouse':(2,'Explicit real-time analytics database, time-series specialization unobserved.'), 'duckdb/duckdb':(1,'In-process analytical SQL is a comparison reference; streaming time-series operations unobserved.'), 'pingcap/tidb':(1,'Transactions and analytics are explicit; metrics/time-series focus unobserved.')}),
 ('H12','baas_platforms','Reduce custom backend plumbing with a platform that explicitly supplies authentication and storage.', ['auth','storage','backend platform'],
  {'appwrite/appwrite':(3,'Explicit Auth, Storage, Functions and other backend services.'), 'InsForge/InsForge':(3,'Explicit database, auth, storage and compute platform.'), 'pocketbase/pocketbase':(1,'Single-file realtime backend is relevant comparison; auth/storage capabilities absent in description.'), 'supabase/supabase':(1,'Dedicated Postgres platform is supporting storage context; auth capability absent in description.'), 'nhost/nhost':(1,'Firebase alternative with GraphQL is a backend comparison; auth/storage details unobserved.'), 'parse-community/parse-server':(1,'Node/Express server is a backend comparison; auth/storage details unobserved.'), 'get-convex/convex-backend':(1,'Reactive app database is supporting storage, auth/platform services unspecified.')}),
 ('H13','application_paas','Deploy applications on owned servers with a PaaS-style lifecycle instead of hand-managing each process.', ['self-hostable','PaaS','Docker'],
  {'coollabsio/coolify':(3,'Explicit self-hostable PaaS on own servers for applications and databases.'), 'dokku/dokku':(3,'Explicit Docker-powered PaaS and application lifecycle.'), 'caprover/caprover':(3,'Explicit PaaS with automated Docker/nginx.'), 'Dokploy/dokploy':(2,'Explicit Vercel/Heroku alternative; owned-server details unobserved.'), 'railwayapp/nixpacks':(1,'App-to-Docker-image build is a supporting prerequisite, not a deployment lifecycle.'), 'Unitech/pm2':(1,'Node process manager supports one runtime, broader PaaS lifecycle absent.')}),
 ('H14','infrastructure_security','Find security checks for infrastructure-as-code before provisioning, distinguishing cluster/runtime monitoring.', ['Infrastructure as Code','before provisioning','build-time'],
  {'tenable/terrascan':(3,'Explicit IaC security/compliance checks before provisioning.'), 'bridgecrewio/checkov':(3,'Explicit build-time IaC misconfiguration checks.'), 'aquasecurity/kube-bench':(1,'Deployed Kubernetes benchmark checks are downstream support.'), 'FairwindsOps/polaris':(1,'Cluster best-practice validation is downstream support.'), 'kubescape/kubescape':(1,'Kubernetes IDE/CI/cluster scanning is adjacent; IaC preprovisioning scope unobserved.'), 'prowler-cloud/prowler':(1,'Cloud security/compliance is broad support; preprovision IaC details absent.'), 'cloudquery/cloudquery':(1,'Cloud inventory/security data pipelines support investigation rather than preprovision checks.')}),
 ('H15','personal_finance','Compare local-first or offline household finance applications; avoid substituting market trading engines.', ['local-first','offline','personal finance'],
  {'actualbudget/actual':(3,'Explicit local-first personal finance application.'), 'reZach/my-budget':(3,'Explicit offline cross-platform budgeting application.'), 'TNT-Likely/BeeCount':(3,'Explicit local-first multi-platform bookkeeping.'), 'mayswind/ezbookkeeping':(2,'Explicit self-hosted personal finance/bookkeeping app, offline behavior unobserved.'), 'budgetzero/budgetzero':(2,'Explicit self-hosted zero-based budgeting, offline behavior unobserved.'), 'Tanq16/ExpenseOwl':(2,'Explicit self-hosted expense tracking, offline behavior unobserved.'), 'firefly-iii/firefly-iii':(1,'Personal finance manager, locality unobserved.'), 'moneymanagerex/moneymanagerex':(1,'Money management application, locality unobserved.'), 'range-of-motion/budget':(1,'Finance purpose is explicit but product detail insufficient.'), 'teelur/budget-board':(1,'Monthly spending/financial goals, locality unobserved.'), 'jameskokoska/Cashew':(1,'Budget/purchase management, locality unobserved.'), 'TheAxelander/OpenBudgeteer':(1,'Bucket budgeting app, locality unobserved.'), 'simonwep/ocular':(1,'Budget tracking app, locality unobserved.'), 'serversideup/financial-freedom':(1,'Budget/privacy focus, locality unobserved.'), 'ananthakumaran/paisa':(1,'Personal finance manager, locality unobserved.'), 'maybe-finance/maybe':(1,'Personal finance app, locality unobserved.'), 'RIP-Comm/sossoldi':(1,'Wealth/personal finance app, locality unobserved.'), 'whisper-money/whisper-money':(1,'Personal-finance purpose, locality unobserved.'), 'ellite/Wallos':(1,'Self-hostable subscription expenses are a narrower support workflow.'), 'kevinschaich/mintable':(1,'Personal-finance automation and privacy are stated, locality unobserved.')}),
 ('H16','data_catalogs_lineage','Build a data-platform metadata context over warehouse tables and APIs; distinguish media tags and generic metadata utilities.', ['data catalog','lineage','metadata'],
  {'apache/gravitino':(3,'Explicit data catalog and federated metadata lake.'), 'marmotdata/marmot':(3,'Explicit catalog of tables/topics/queues/APIs exposed to agents.'), 'MarquezProject/marquez':(3,'Explicit data-ecosystem metadata collection and visualization.'), 'amundsen-io/amundsen':(2,'Metadata-driven productivity for data analysts/engineers.'), 'OpenLineage/OpenLineage':(2,'Explicit lineage metadata collection standard.'), 'opendatadiscovery/odd-platform':(2,'Explicit data discovery/observability platform.'), 'open-metadata/OpenMetadata':(2,'Explicit data context and business semantics platform.'), 'datahub-project/datahub':(2,'Explicit context platform for data/AI stack.'), 'apache/polaris':(2,'Explicit Apache Iceberg catalog.'), 'frictionlessdata/datapackage':(1,'Dataset specifications support metadata interchange, not a running catalog.'), 'reata/sqllineage':(1,'SQL lineage analysis supports the context pipeline.'), 'datavane/datavines':(1,'Metadata management/data quality is adjacent observability.'), 'elementary-data/dbt-data-reliability':(1,'Captures metadata/artifacts/test results for dbt, supporting observability.'), 'elementary-data/elementary':(1,'dbt-native observability supports the context pipeline.'), 'apache/ossie':(1,'Semantic metadata interchange specification is supporting.'), '642933588/jiron-cloud':(1,'Chinese description explicitly lists metadata and data-quality management; architecture details unobserved.'), 'rsyi/whale':(1,'Warehouse CLI workspace is adjacent, metadata catalog unobserved.')}),
 ('D01','browser_mobile_testing','Compare tools for cross-engine browser regression testing across Chromium, Firefox and WebKit.', ['browser','testing','Chromium','WebKit'],
  {'microsoft/playwright':(3,'Explicit Chromium/Firefox/WebKit testing with one API.'), 'SeleniumHQ/selenium':(2,'Explicit browser automation framework; named engine coverage unobserved.'), 'cypress-io/cypress':(2,'Explicit browser testing; named engine coverage unobserved.'), 'yashaka/selene':(2,'Explicit web UI browser tests in Python.'), 'gemini-testing/testplane':(2,'Explicit browser test runner based on mocha/wdio.'), 'symfony/panther':(2,'Explicit PHP/Symfony browser testing.'), 'apache/groovy-geb':(2,'Explicit browser automation.'), 'seleniumbase/SeleniumBase':(2,'Explicit web automation/testing APIs.'), 'hardkoded/puppeteer-sharp':(1,'Headless Chrome .NET is single-engine supporting context.'), 'serenity-js/serenity-js':(1,'Acceptance-testing architecture supports existing browser runners.'), 'bug0inc/passmark':(1,'Playwright-based regression library is supporting.'), 'NoriSte/ui-testing-best-practices':(1,'UI-testing reading material, not a runner.'), 'dsheiko/puppetry':(1,'Puppeteer/Jest web testing is supporting, cross-engine coverage unobserved.')}),
 ('D02','browser_mobile_testing','Verify a React Native mobile application with integration tests or a mobile automation API.', ['React Native','mobile app','integration test'],
  {'pixielabs/cavy':(3,'Explicit React Native integration-test framework.'), 'callstack/agent-device':(2,'Explicit mobile automation/verification through CLI/MCP/Node API, React Native support unobserved.'), 'microsoft/HydraLab':(1,'Cloud testing purpose, mobile/framework detail unobserved.'), 'testsigmahq/testsigma':(1,'Broad quality platform supports comparison, mobile-specific detail unobserved.')}),
 ('D03','ui_component_libraries','Compare reusable React UI component collections for a web application; do not confuse icons or tooling with components.', ['React','component library','UI'],
  {'mui/material-ui':(3,'Explicit comprehensive React component library.'), 'primefaces/primereact':(3,'Explicit React UI component library.'), 'mantinedev/mantine':(3,'Explicit fully featured React components.'), 'ant-design/ant-design':(3,'Explicit enterprise React UI library.'), 'microsoft/fluentui':(3,'Explicit React component collection.'), 'heroui-inc/heroui':(3,'Explicit React UI library.'), 'radix-ui/primitives':(2,'Explicit accessible UI components, framework detail unobserved.'), 'shadcn-ui/ui':(2,'Explicit accessible components with framework flexibility.'), 'chakra-ui/chakra-ui':(2,'Explicit SaaS component system, framework detail unobserved.'), 'adobe/react-spectrum':(1,'Adaptive accessible UX tools, component/framework details sparse.'), 'TanStack/table':(1,'Headless React tables are a narrower supporting component.'), 'Jpisnice/shadcn-ui-mcp-server':(1,'Component context MCP supports development rather than supplying runtime UI.'), '21st-dev/magic-mcp':(1,'Search/generation of React/Tailwind components supports discovery, not a runtime library.')}),
 ('D04','ui_component_libraries','Introduce a workflow for building, documenting and testing UI components in isolation.', ['UI components','isolation','testing'],
  {'storybookjs/storybook':(3,'Explicit isolated component building/documentation/testing workshop.'), 'shadcn-ui/ui':(1,'Component code distribution supports source access, isolation testing unobserved.'), 'Jpisnice/shadcn-ui-mcp-server':(1,'Component structure/usage context supports authoring, isolation tests unobserved.')}),
 ('D05','backend_frameworks','Modernize a Go HTTP API with a reusable web framework or composable router.', ['Go','HTTP','router'],
  {'gin-gonic/gin':(3,'Explicit Go HTTP framework and REST APIs.'), 'go-chi/chi':(3,'Explicit composable Go HTTP router.'), 'labstack/echo':(2,'Explicit Go web framework.'), 'gofiber/fiber':(2,'Explicit Go web framework inspired by Express.')}),
 ('D06','backend_frameworks','Compare .NET web application frameworks including opinionated enterprise scaffolding.', ['.NET','web framework','ASP.NET'],
  {'dotnet/aspnetcore':(3,'Explicit cross-platform .NET web framework.'), 'abpframework/abp':(3,'Explicit ASP.NET Core enterprise framework, modules and scaffolding.')}),
 ('D07','file_upload_infrastructure','Recover interrupted large-file uploads using a resumable transfer protocol, not a general file manager.', ['resumable','upload','protocol'],
  {'tus/tusd':(3,'Explicit resumable upload protocol reference server.'), 'tus/tus-js-client':(3,'Explicit JavaScript resumable upload client.'), 'ankitpokhrel/tus-php':(3,'Explicit PHP resumable upload server/client.'), 'tus/tus-resumable-upload-protocol':(2,'Explicit resumable-upload protocol specification, not a complete implementation.'), 'error311/FileRise':(2,'Explicit resumable uploads in a file-management application, protocol compatibility unknown.'), 'pionl/laravel-chunk-upload':(1,'Chunk upload supports recovery design, resumability not asserted.'), 'moxiecode/plupload':(1,'Chunked upload supports transfer design, resumability not asserted.'), 'peinhu/AetherUpload-Laravel':(1,'Large-file upload supports transfer design, resumability unobserved.')}),
 ('D08','file_upload_infrastructure','Add a browser JavaScript upload widget with a React integration where possible.', ['browser','JavaScript','uploader','React'],
  {'transloadit/uppy':(3,'Explicit web-browser file uploader.'), 'pqina/filepond':(3,'Explicit JavaScript upload library.'), 'moxiecode/plupload':(3,'Explicit JavaScript uploader API and multiple-selection/progress-related transfer features.'), 'rpldy/react-uploady':(3,'Explicit React upload components/hooks.'), 'pqina/react-filepond':(3,'Explicit React adapter for FilePond.'), 'elninotech/uppload':(2,'Explicit JavaScript image uploader/editor.'), 'danielm/uploader':(2,'Explicit jQuery uploader with queues, progress and drag/drop.'), 'dropzone/dropzone':(1,'Drag/drop image previews support widget UX; upload transport detail unobserved.'), 'react-dropzone/react-dropzone':(1,'React drag/drop zone supports selection, not transport.'), 'pqina/vue-filepond':(1,'Vue adapter is a framework comparison rather than React fit.'), 'dai-siki/vue-image-crop-upload':(1,'Vue image uploader is a framework comparison.'), 'node-formidable/formidable':(1,'Server multipart parser is a supporting backend prerequisite.'), 'expressjs/multer':(1,'Server multipart middleware is supporting transport.'), 'richardgirges/express-fileupload':(1,'Express upload middleware supports server transport.')}),
 ('D09','data_catalogs_lineage','Extract EXIF and media tags from local image/audio/video files; avoid data-warehouse catalog platforms.', ['Exif','metadata','image','audio'],
  {'drewnoakes/metadata-extractor':(3,'Explicit image/video/audio metadata extraction.'), 'drewnoakes/metadata-extractor-dotnet':(3,'Explicit image/video/audio metadata extraction in .NET.'), 'ianare/exif-py':(3,'Explicit Python EXIF extraction from images.'), 'MikeKovarik/exifr':(3,'Explicit JavaScript EXIF reading.'), 'exiftool/exiftool':(2,'Explicit meta information reader/writer.'), 'tinytag/tinytag':(2,'Explicit audio metadata reading.'), 'Borewit/music-metadata':(3,'Explicit audio/video file/stream tag extraction.'), 'MediaArea/MediaInfoLib':(2,'Explicit technical/tag data display for audio/video.'), 'Zeugma440/atldotnet':(2,'Explicit audio metadata reading/editing.'), 'photostructure/exiftool-vendored.js':(2,'Explicit Node access to ExifTool.'), 'apache/tika':(2,'Explicit extraction from many file types; media-specific tag coverage unobserved.'), 'sandreas/tone':(1,'Audio metadata tag editing/dumping supports the pipeline.'), 'deckerst/aves':(1,'Android gallery/metadata explorer is supporting UI.'), 'tropy/tropy':(1,'Research photo management is supporting workflow.'), 'mdhiggins/sickbeard_mp4_automator':(1,'Media conversion/tagging supports processing, extraction API unobserved.')}),
 ('D10','personal_finance','Evaluate portfolio optimization libraries for quantitative research, distinguishing budgeting and live broker execution.', ['portfolio','optimization','risk'],
  {'PyPortfolio/PyPortfolioOpt':(3,'Explicit Python portfolio optimization algorithms.'), 'dcajasn/Riskfolio-Lib':(3,'Explicit Python portfolio optimization.'), 'fmilthaler/FinQuant':(2,'Explicit portfolio management/analysis/optimization.'), 'ranaroussi/quantstats':(1,'Portfolio analytics supports validation, optimization unobserved.'), 'bashtage/arch':(1,'Statistical ARCH modeling supports research rather than portfolio allocation.'), 'google/tf-quant-finance':(1,'Quant-finance library is broad supporting research.'), 'domokane/FinancePy':(1,'Derivative pricing/risk is adjacent supporting research.')}),
]

IDENTITIES = [('I01','api_contract_testing','mock-server/mockserver','mock-server/mockserver-monorepo'),
              ('I02','accounting_invoicing','simonmichael/hledger','plaintextaccounting/hledger'),
              ('I03','scheduling_personal_productivity','calcom/cal.com','calcom/cal.diy'),
              ('I04','ui_component_libraries','heroui-inc/heroui','heroui-inc/heroui')]

# Literal OR compiler does not split phrases. Intent terms/synonyms are declared
# prospectively from the goals and observed source vocabulary, never from ranks.
INTENT_TERMS = {
 'H01':['collaborative','multiplayer','editor','editing'],
 'H02':['local','mock','mocking','HTTP','APIs'],
 'H03':['self-hosted','photo','photos','video','management'],
 'H04':['TypeScript','schema','validation','inference'],
 'H05':['CLI','command','line','double-entry','accounting','bookkeeping','text'],
 'H06':['documentation','docs','Markdown','static','website','websites'],
 'H07':['calendar','calendars','sync','scheduling','MCP'],
 'H08':['Node.js','Stripe','API','payment','payments'],
 'H09':['agile','sprint','sprints','issue','issues','roadmap','roadmaps'],
 'H10':['ELT','ingestion','loading','warehouse','warehouses','integration','pipeline','pipelines'],
 'H11':['metrics','metric','метрики','time-series','analytics','datastore'],
 'H12':['auth','authentication','storage','backend','platform','database'],
 'H13':['self-hosted','self-hostable','PaaS','Docker','applications','deploy'],
 'H14':['infrastructure','code','provisioning','security','misconfigurations','compliance'],
 'H15':['local-first','offline','personal','finance','budgeting','bookkeeping','expenses'],
 'H16':['catalog','catalogs','lineage','metadata','warehouse','tables','APIs'],
 'D01':['browser','testing','automation','Chromium','WebKit','Firefox'],
 'D02':['React Native','mobile','integration','testing','verification'],
 'D03':['React','UI','component','components','library','libraries'],
 'D04':['component','components','isolation','isolated','documenting','testing'],
 'D05':['Go','HTTP','router','routing','web','framework','frameworks'],
 'D06':['.NET','dotnet','ASP.NET','web','framework','enterprise'],
 'D07':['resumable','upload','uploads','protocol','chunk','chunked'],
 'D08':['browser','JavaScript','uploader','upload','uploading','React'],
 'D09':['Exif','metadata','image','images','audio','video','tags'],
 'D10':['portfolio','portfolios','optimization','optimisation','allocation','risk']}

# Independent pre-capture source review: supporting contributions missed in draft.
for suffix, leaf, goal, terms, assessments in ASSESSMENTS:
    if suffix=='H15': assessments['firefly-iii/data-importer']=(1,'Explicit Firefly III data import supports household-finance migration/validation, locality unobserved.')
    if suffix=='H16': assessments['macbre/sql-metadata']=(1,'Explicit query metadata extraction supports SQL/table-context processing, running catalog absent.')
    if suffix=='D03':
        assessments['carbon-design-system/carbon']=(1,'Explicit design system supports UI consistency; React runtime/components are unobserved.')
        assessments['elastic/eui']=(1,'Explicit UI framework supports design comparison; React/runtime coverage is sparse.')
    if suffix=='H07': assessments['jlumbroso/passage-of-time-mcp']=(1,'Explicit time calculation and temporal awareness supports calendar reasoning, synchronization absent.')


def in_route(card, route):
    return any(x['category_id']==route or x.get('parent_id')==route for x in card['classifications'])


def source_constraint(card):
    repository=card['repository']
    if repository['archived'] is True or repository['availability']!='available' or repository['visibility']!='public':
        return 'denied'
    if repository['archived'] is not False:
        return 'unknown'
    return 'allowed'


def source_projection(case, cards):
    """Bounded per-case source review input, not the full persisted proof matrix."""
    return {'goal':case['graded_criteria'], 'cards':[
        {'github_repository_id':card['identity']['github_repository_id'],
         'full_name':card['identity']['full_name'], 'aliases':card['identity']['full_name_aliases'],
         'descriptions':card['descriptions'],
         'constraints':{key:card['repository'][key] for key in ['archived','availability','visibility']},
         'activity':{key:card['activity'][key] for key in ['last_release_at','last_commit_at','observed_at']}}
        for card in cards]}


def make_query(plan, case):
    route, pins = plan['candidate_route'], plan['pins']
    return {'schema_version': route['query_schema_version'], 'query_id': case['case_id'],
            'brief_version': 1, 'source_mode': route['source_mode'], 'retrieval_engine': route['retrieval_engine'],
            'policy_version': pins['retrieval_policy_version'], 'policy_sha256': pins['policy_sha256'],
            'card_schema_version': pins['card_schema_version'], 'activity_schema_version': pins['activity_schema_version'],
            'index_format_version': pins['index_format_version'], 'taxonomy_route_id': case['target_category_id'],
            'language': case['query_locale'], 'variants': [{'variant_id':'q1','terms':case['query_terms']}],
            'constraints': {'languages': [], 'deployment': [], 'allowed_licenses': [], 'compatibility': [],
                            'require_no_server': None, 'mandatory_fields': []},
            'max_candidates': route['max_candidates'], 'max_cards': route['max_cards'],
            'max_evidence_bytes': route['max_evidence_bytes']}


def pointer(card, path):
    value = card
    for part in path.strip('/').split('/'):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def build():
    old = load_reference()
    plan = {key:copy.deepcopy(old[key]) for key in ['pins','artifacts','candidate_route','default_constraints',
            'lexical_baseline','thresholds','stratification','scale_protocol','language_protocol','human_protocol','rubric_sha256']}
    cards = json.loads((ROOT / CARDS_PATH).read_text(encoding='utf8'))['cards']
    plan.update(schema_version='cp04_quality_plan_v2', plan_id='cp04-public-catalog-quality-v2',
                status='design_frozen_execution_pending', evidence_owner='quality_evaluator',
                acceptance_owner='product_planner', judgments_path='evals/plugin-v1/quality-judgments-v2.json',
                source_hashes={path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                               for path in [CARDS_PATH, old['artifacts']['manifest_path'],old['artifacts']['policy_path'],
                                            old['artifacts']['index_path'],'specs/catalog/taxonomy.yaml','evals/plugin-v1/quality-plan.json']},
                cases=[], split_policy={'development_count':10,'held_out_count':16,'identity_probe_count':4,
                                       'freeze_before_capture':True,'held_out_tuning_forbidden':True,
                                       'adjudication':'source_review_before_first_v2_ranking'},
                relevance_protocol={'positive_grade_min':1,'grade3':'explicit core goal and specific requested capability',
                                    'grade2':'explicit core function with a requested detail unobserved',
                                    'grade1':'explicit adjacent/supporting function or sparse source requiring verification',
                                    'grade0':'assessed described function outside goal; no source-supported direct or supporting contribution',
                                    'adoption_fit':'unknown unless separately assessed; never implied by relevance',
                                    'acceptance_metric':'constrained original-rank gain: topical grade >0 and constraint != denied',
                                    'denied_gain':0,'denied_rank_positions':'retained; never compact ranks',
                                    'unconditional_topical_metrics':'mandatory parallel diagnostics including denied positives',
                                    'identity_excluded_from_semantic_macros':True,
                                    'zero_relevance_is_not_proof_of_upstream_absence':True},
                calibration_case_ids=['CP04-V2-H03','CP04-V2-D05','CP04-V2-H15','CP04-V2-H11'])
    labels = {'schema_version':'cp04_source_judgments_v2', 'source_hashes':copy.deepcopy(plan['source_hashes']),
              'cards_sha256':plan['pins']['cards_sha256'],
              'evidence_kind':'agent_source_assessment_not_human_calibration', 'cases':[]}
    rows = ASSESSMENTS + [(suffix,leaf,'Resolve exactly '+alias+' to its canonical numeric identity.',[alias],
                           {name:(3,'Exact current/historical source identity, no substitute identity allowed.')})
                          for suffix,leaf,alias,name in IDENTITIES]
    for suffix, leaf, goal, terms, explicit in rows:
        if suffix in INTENT_TERMS: terms=INTENT_TERMS[suffix]
        if suffix=='H07': leaf='communications_personal_ops'
        route_cards = sorted([c for c in cards if in_route(c,leaf)],
                             key=lambda c:c['identity']['github_repository_id'])
        unknown_names = set(explicit)-{c['identity']['full_name'] for c in route_cards}
        if unknown_names:
            raise ValueError('unknown reviewed name '+str(unknown_names))
        case_id = 'CP04-V2-'+suffix
        identity = suffix.startswith('I')
        is_container=leaf in plan['stratification']['container_ids']
        parent = leaf if is_container else next(x['parent_id'] for x in route_cards[0]['classifications'] if x['category_id']==leaf)
        tags = ['lexical_ru' if suffix=='H11' else 'lexical_en']
        if is_container: tags+=['container_union']
        tags += ['thin_leaf'] if len(route_cards)<=10 else ['dense_leaf'] if len(route_cards)>=30 else []
        tags += sorted({'expansion_cohort' if c['catalog']['membership_cohort']=='cat07a_expansion'
                        else c['catalog']['membership_cohort']+'_cohort' for c in route_cards})
        if any(c['descriptions']['catalog'] and c['descriptions']['upstream'] for c in route_cards): tags += ['dual_descriptions']
        if any(len(c['classifications'])>1 for c in route_cards): tags += ['secondary_dedupe']
        if any(c['activity']['last_release_at'] is None for c in route_cards): tags += ['activity_unknown']
        alias = next((a for s,l,a,n in IDENTITIES if s==suffix), None)
        if alias and any(alias in c['identity']['full_name_aliases'] for c in route_cards): tags += ['historical_alias']
        case = {'case_id':case_id,'split':'held_out' if suffix.startswith('H') else 'development' if suffix.startswith('D') else 'identity_probe',
                'metric_family':'identity' if identity else 'semantic','goal_kind':'exact_identity' if identity else 'functional_alternative',
                'requirement_ids':['R06','R12','R14'], 'persona':'synthetic engineer',
                'synthetic_project_context':'Hypothetical bounded local project. No private source, customer data or credentials. '+goal,
                'user_goal':goal,'query_locale':'ru' if suffix=='H11' else 'en','query_terms':terms,
                'target_category_id':leaf,'container_domain_ids':[parent], 'tags':sorted(set(tags)),
                'leaf_card_count':len(route_cards),'leaf_band':'thin' if len(route_cards)<=10 else 'dense' if len(route_cards)>=30 else 'middle',
                'k':12,'expected_alias':alias,'expected_identity_ids':[],
                'universe_ids':[c['identity']['github_repository_id'] for c in route_cards],
                'universe_definition':'All distinct pinned card IDs matching leaf classification or container descendant placement, including secondary placements; no lexical/filter/output preselection.',
                'graded_criteria':{'required_function':goal,'assessment_method':'Explicit reviewed per-name source capability assessments; no query substring or category-membership grading.'},
                'accepted_gaps':['Source descriptions establish topical retrieval relevance, not adoption/production fit.','Agent-authored judgments need independent source review and human usefulness calibration.']}
        judgments=[]
        for card in route_cards:
            name=card['identity']['full_name']; rid=card['identity']['github_repository_id']
            description=card['descriptions']['upstream'] or card['descriptions']['catalog']
            if name in explicit: grade, reason=explicit[name]
            elif identity: grade,reason=0,'Different numeric repository identity; not the requested alias/current identity.'
            elif not description: grade,reason=1,'Source descriptions absent: function is unknown; retain a weak verification reference, not a proven alternative.'
            else: grade,reason=0,'Reviewed source describes a different function from this goal: '+description+'. No direct or supporting goal capability is evidenced; this does not prove upstream lacks that capability.'
            paths=['/identity/full_name','/descriptions/upstream','/descriptions/catalog',
                   '/repository/archived','/repository/availability','/repository/visibility',
                   '/activity/last_release_at','/activity/last_commit_at','/activity/observed_at']
            if identity: paths+=['/identity/full_name_aliases']
            source_ref=card['provenance']['sources'][0]['source_ref']
            judgments.append({'github_repository_id':rid,'full_name':name,'grade':grade,'constraint':source_constraint(card),
                              'rationale':reason,'adoption_fit':'unknown','judgment_basis':'explicit_source_assessment',
                              'evidence':[{'pointer':p,'value':pointer(card,p),'source_ref':source_ref} for p in paths],
                              'membership_cohort':card['catalog']['membership_cohort']})
        positives=[j['github_repository_id'] for j in judgments if j['grade']>0 and j['constraint']!='denied']
        case['expected_relevant_ids']=positives
        case['relevant_count']=len(positives)
        case['intrinsic_recall_at_12_ceiling']=min(12,len(positives))/len(positives) if positives else None
        if identity: case['expected_identity_ids']=[j['github_repository_id'] for j in judgments if j['grade']==3]
        case['query_sha256']=digest(make_query(plan,case))
        plan['cases'].append(case)
        labels['cases'].append({'case_id':case_id,'universe_ids':case['universe_ids'],
                                'goal_sha256':digest(case['graded_criteria']),'judgments':judgments})
    # User-facing calibration contexts are declared before any result is viewed.
    contexts={'CP04-V2-H03':('non-technical founder','A household photo collection has scattered folders. Compare two source-supported options and define a disposable validation dataset without copying personal images.'),
              'CP04-V2-D05':('backend engineer','A synthetic Go HTTP API needs clearer routing. Compare adoption surfaces, preserve request/response behavior, and propose one isolated endpoint regression test.'),
              'CP04-V2-H15':('low-context operator','An undocumented household budget workflow needs local-first/offline storage. Release/maintenance/compatibility are unknown; ask focused questions before migration and use synthetic transactions.'),
              'CP04-V2-H11':('Russian-speaking engineer','A synthetic telemetry service needs metrics/time-series storage. Produce paired RU/EN recommendations with the same evidence, unknowns, prerequisites and proposed-only execution status.')}
    for case in plan['cases']:
        if case['case_id'] in contexts:
            case['persona'],case['synthetic_project_context']=contexts[case['case_id']]
            case['calibration_acceptance']=['decision and strongest counterargument','source facts separate from unknowns',
                                            'first bounded validation slice with prerequisites and rollback',
                                            'copyable coding handoff preserves authorization and proposed-only status']
        selected=[card for card in cards if card['identity']['github_repository_id'] in case['universe_ids']]
        case['source_projection_bytes']=len(canonical(source_projection(case,selected)))
        case['source_projection_sha256']=digest(source_projection(case,selected))
    labels['plan_sha256']=digest(plan)
    return plan,labels


def validate(plan,labels):
    cards=json.loads((ROOT / CARDS_PATH).read_text(encoding='utf8'))['cards']
    byid={c['identity']['github_repository_id']:c for c in cards}
    if labels['plan_sha256']!=digest(plan): raise ValueError('plan hash mismatch')
    if plan['thresholds']!=load_reference()['thresholds']: raise ValueError('acceptance weakening')
    if plan['source_hashes']!=labels['source_hashes']: raise ValueError('source hash mismatch')
    for path,expected in plan['source_hashes'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected: raise ValueError('source pin mismatch')
    if len({c['case_id'] for c in plan['cases']})!=len(plan['cases']): raise ValueError('duplicate case')
    labelcases={c['case_id']:c for c in labels['cases']}
    if len(labelcases)!=len(labels['cases']) or set(labelcases)!={c['case_id'] for c in plan['cases']}: raise ValueError('complete cases required')
    total=0
    for case in plan['cases']:
        universe=sorted(rid for rid,card in byid.items() if in_route(card,case['target_category_id']))
        lc=labelcases[case['case_id']]
        rows=lc['judgments']; ids=[j['github_repository_id'] for j in rows]
        if universe!=case['universe_ids'] or universe!=lc['universe_ids'] or universe!=ids: raise ValueError('complete routed judgments required')
        if case['query_sha256']!=digest(make_query(plan,case)): raise ValueError('query hash mismatch')
        if lc['goal_sha256']!=digest(case['graded_criteria']): raise ValueError('goal hash mismatch')
        if case['source_projection_bytes']>204800: raise ValueError('projection budget exceeded')
        selected=[card for card in cards if card['identity']['github_repository_id'] in case['universe_ids']]
        projection=source_projection(case,selected)
        if case['source_projection_bytes']!=len(canonical(projection)) or case['source_projection_sha256']!=digest(projection): raise ValueError('projection byte/hash mismatch')
        for row in rows:
            if type(row['grade']) is not int or row['grade'] not in range(4): raise ValueError('invalid grade')
            if row['constraint'] not in ['allowed','denied','unknown'] or not row['rationale']: raise ValueError('invalid rationale/constraint')
            if not row['evidence']: raise ValueError('missing evidence')
            card=byid[row['github_repository_id']]
            if row['constraint']!=source_constraint(card): raise ValueError('constraint source mismatch')
            ref=card['provenance']['sources'][0]['source_ref']
            for ev in row['evidence']:
                if ev['value']!=pointer(card,ev['pointer']) or ev['source_ref']!=ref: raise ValueError('source evidence mismatch')
        total+=len(rows)
    held={d for c in plan['cases'] if c['split']=='held_out' for d in c['container_domain_ids']}
    if held!=set(plan['stratification']['container_ids']): raise ValueError('heldout container coverage incomplete')
    tags={t for c in plan['cases'] for t in c['tags']}
    if not set(plan['stratification']['required_case_tags']).issubset(tags): raise ValueError('required strata missing')
    return {'plan_sha256':digest(plan),'judgments_sha256':digest(labels),'heldout_container_count':len(held),
            'semantic_cases':sum(c['metric_family']=='semantic' for c in plan['cases']),
            'explicit_judgments':total,'maximum_projection_bytes':max(c['source_projection_bytes'] for c in plan['cases']),
            'quality_observed':False,'human_calibrated':False}


if __name__=='__main__':
    import sys
    if '--check' in sys.argv:
        plan=json.loads((HERE/'quality-plan-v2.json').read_text(encoding='utf8'))
        labels=json.loads((HERE/'quality-judgments-v2.json').read_text(encoding='utf8'))
        print(json.dumps(validate(plan,labels),sort_keys=True))
    else:
        plan,labels=build(); validate(plan,labels)
        for name,content in [('quality-plan-v2.json',plan),('quality-judgments-v2.json',labels)]:
            (HERE/name).write_bytes(canonical(content)+b'\n')
        print(json.dumps(validate(plan,labels),sort_keys=True))
