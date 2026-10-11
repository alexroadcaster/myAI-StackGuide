"""Materialize pre-ranking source-role judgments; no runtime/model/SQL imports."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PLAN = ROOT/'evals/plugin-v1/final-quality-host-prospective-2026-10-11.json'
CONTRACT = ROOT/'evals/plugin-v1/host-decision-eval-contract-2026-10-11.json'
read = lambda p: json.loads((ROOT/p).read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
canonical = lambda v: json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
old_paths = ['evals/plugin-v1/final-quality-rank-repair-regression-2026-10-11.json','evals/plugin-v1/final-quality-prospective-2026-10-11.json']
old_plans = [read(p) for p in old_paths]
base = old_plans[-1]
cards = read(base['artifacts']['cards_path'])['cards']
by_id = {c['identity']['github_repository_id']:c for c in cards}
prior_ids = {j['github_repository_id'] for p in old_plans for c in p['cases'] for j in c['judgments']}
routes = {}
for p in old_plans:
    for c in p['cases']:
        routes.setdefault(c['route'],c)

# Required purposes differ from all prior 45 semantic/identity goals. Explicit
# positive groups below are independently authored for these purposes. Remaining
# IDs have individually inspected, source-described different primary workflows;
# zero means task-relative unrelated role, never inferred feature absence.
SPECS = [
 ('code_quality','Automatically rewrite Python source into a consistent formatting style; standalone formatters are primary and hook/aggregate tooling can run them. Diagnostic-only and other-language tooling has a different primary workflow.',
  ['Python','formatting','rewrite'],[['Python'],['formatting']],['rewrite'],'en',
  {3:[125266328,523043277],2:[],1:[17689377,304830226]},
  'Automatic formatting replaces source diagnostics as the required action.'),
 ('unit_component_testing','Exercise rendered React component behavior through DOM queries and simulated user interactions in isolated tests; DOM utilities are primary and JavaScript test runners support execution. Pure-function-only language stacks are different integration roles.',
  ['React','DOM','interaction testing'],[['React'],['DOM']],['interaction testing'],'en',
  {3:[125863507],2:[128396076],1:[84009,1451352,15062869,26820798,434708679]},
  'Rendered user-facing component behavior replaces pure JavaScript function testing and browser-engine E2E automation.'),
 ('file_management_sync','Offer a browser interface for people to upload, inspect and download existing server files; file-browser/file-serving implementations are preferred and cloud file suites are alternative hosts. Device synchronization alone or terminal explorers are distinct primary workflows.',
  ['browser','files','upload','download'],[['browser'],['files']],['upload','download'],'en',
  {3:[42332863,188700274],2:[4999959,5550552,60243197,323965659],1:[895547074]},
  'Human browser file handling replaces continuous two-device synchronization.'),
 ('frontend_state_data','Cache and refresh remote server-query results for React views, including shared request state; server-query tooling is primary while general stores and immutable-update helpers support custom integration. Routing is a separate application responsibility.',
  ['React','server state','query cache'],[['React'],['server state']],['query cache'],'en',
  {3:[207645083],2:[123732482],1:[36535156,115720575,180328715,286867459,304120355,685274424]},
  'Remote request caching and invalidation replaces shared local component state.'),
 ('financial_market_tools','Provide market-data access for a read-only research notebook or assistant, without placing orders or running strategy backtests. Data APIs and source-documented data tools are primary; analysis interfaces or strategy engines are alternatives/supporting consumers with explicit provider prerequisites.',
  ['market data','research','read only'],[['market data']],['research','read only'],'en',
  {3:[91253698,944516885],2:[849406496,995562554,1034736943,963828488],1:[31522041,91629816,816848129,896144595,1081891045,1131513930,1195329660]},
  'Read-only data acquisition replaces historical strategy evaluation. Role evidence does not authorize trading.'),
 ('documentation_site_generators','Publish a personal chronological blog from text/Markdown posts as static pages. General static/blog generators are primary; documentation engines can host prose as alternatives, while API-reference-specific generators support a different publication structure.',
  ['static blog','Markdown','posts'],[['static blog']],['Markdown','posts'],'en',
  {3:[65252,11180687],2:[94911145,260338399],1:[15830664,50617428,614933136]},
  'Chronological personal posts replace API-reference publication and versioned product manuals.'),
 ('communications_personal_ops','Для личного non-production прототипа индивидуального консультанта нужен scheduling application с интерфейсом выбора времени встречи. Calendar data/sync и time helpers могут поддержать workflow; chat, видеозвонки и transcription имеют другую основную роль.',
  ['appointment scheduling','personal','calendar'],[['appointment scheduling']],['personal','calendar'],'ru',
  {3:[350360184],2:[],1:[943286066,973788136,1003342581,1121557390]},
  'Appointment selection/booking application replaces calendar synchronization, video rooms and asynchronous team text.'),
 ('payment_processing_sdks','Embed a Stripe payment-entry interface in an existing browser/React application. Browser Stripe.js/Elements components are primary, checkout samples demonstrate a workflow, and server API clients support the required backend. Other processors have a different integration target.',
  ['Stripe','browser','payment form'],[['Stripe'],['browser']],['payment form'],'en',
  {3:[221280225,235391869],2:[202768861],1:[1953389,2471804,20545279]},
  'Browser payment collection UI replaces the Python Stripe server API-client requirement.'),
 ('project_task_management','Нужна готовая kanban board для перемещения карточек задач между рабочими колонками. Board applications предпочтительны; широкие project platforms являются альтернативами, backend и existing-platform connectors — supporting components. Sprint planning и time reports не являются целью.',
  ['kanban','задачи','task cards'],[['kanban']],['задачи','task cards'],'ru',
  {3:[16089035,16238673,301793434],2:[6899875,29745084,159556794,568098118,583598619],1:[357894794,897809208,1030580992]},
  'Visual task movement through columns replaces sprint planning and labor/time accounting.'),
 ('data_processing_compute','Continuously process arriving event records into updated derived results; documented stream-processing engines are preferred, general distributed compute is an alternative, and tabular/columnar tooling supports batch preparation or data interchange without being an established streaming engine.',
  ['stream processing','events','continuous'],[['stream processing']],['events','continuous'],'en',
  {3:[20587599,455655192,571186647],2:[17165658],1:[858127,5349565,24528468,28782747,51905353,71932349,166515022,263727855,485548415]},
  'Processing continuously arriving records replaces local finite DataFrame batches.'),
 ('caches_key_value_stores','Embed a durable ordered key-value storage library inside a native application process; an embedded ordered map is primary, distributed persistent key-value services are alternative architectures, and cache servers serve a different primary deployment role.',
  ['embedded','ordered','key value','storage'],[['embedded'],['ordered']],['key value','storage'],'en',
  {3:[23405758],2:[11225014,48833910],1:[156018,437245741,775743011]},
  'Embedded durable ordered storage replaces a runtime caching-server requirement.'),
 ('backend_frameworks','Implement a Ruby application that renders HTML templates and processes web forms on the server; a Ruby MVC/view stack is primary and a Ruby-application inspection bridge can support development. Other implementation-language web frameworks are different integration roles.',
  ['Ruby','HTML templates','forms'],[['Ruby'],['HTML templates']],['forms'],'en',
  {3:[8514],2:[],1:[952098631]},
  'Server-rendered HTML/form workflow replaces Go REST routing and Python long-lived WebSocket handling.'),
 ('infrastructure_automation','Define a reproducible local development shell with declaratively selected packages. Nix package/shell definitions are primary and Nix resource lookup supports authoring; remote fleet configuration, cloud provisioning and general SSH/provider bridges have different primary workflows.',
  ['development shell','packages','reproducible'],[['development shell']],['packages','reproducible'],'en',
  {3:[4542716],2:[],1:[951693330]},
  'Local package/shell environment replaces repeated infrastructure provisioning/configuration.'),
 ('software_supply_chain_security','Detect accidentally committed credentials or secret strings in source before sharing changes. Source secret scanners are primary, source-analysis tools support a broader review, and dependency inventories/signing or package-vulnerability tools target other supply-chain concerns.',
  ['secrets','credentials','source code'],[['secrets'],['credentials']],['source code'],'en',
  {3:[77726177,119190187,239106765],2:[180687624],1:[227803815,950213855,63625434,131129792]},
  'Credential/string leak detection replaces dependency SBOM/vulnerability inventory and web/IaC security scanning.'),
]
FRESH = {
123732482:('https://github.com/reduxjs/redux-toolkit','RTK Query is included for data fetching and caching as part of Redux Toolkit.','Redux/application wiring and actual invalidation behavior require project validation.'),
94911145:('https://github.com/facebook/docusaurus','Documentation-oriented website framework includes a blog alongside documentation.','Chronological blog fit remains an alternative to dedicated/general static blog generation.'),
188700274:('https://github.com/9001/copyparty','File server provides a browser interface and resumable uploads plus file-serving protocols.','Authentication, deployment and required file-management features not validated in a live instance.'),
125863507:('https://github.com/testing-library/react-testing-library','React DOM testing utilities; README illustrates DOM queries, rendered components and simulated user actions.','Runner/DOM environment and React version compatibility require validation.'),
207645083:('https://github.com/TanStack/query/blob/main/docs/framework/react/overview.md','Fetching, caching, synchronizing and updating server state; documents shared requests, background updates and invalidation.','Project/version compatibility and local execution not checked.'),
221280225:('https://github.com/stripe/react-stripe-js','React components wrap Stripe.js and Stripe Elements.','Provider/browser/account prerequisites remain conditional; no payment executed.'),
235391869:('https://github.com/stripe/stripe-js','Loads Stripe.js in a browser; README links payment acceptance and documents a null result in a server environment.','Publishable key, remote Stripe script and backend/provider configuration remain conditional.'),
8514:('https://github.com/rails/rails','README documents Ruby MVC, HTML/ERB templates via Action View and HTTP controller responses.','No claim of project compatibility or actual form implementation.'),
4542716:('https://github.com/NixOS/nixpkgs/blob/master/doc/build-helpers/special/mkshell.section.md','pkgs.mkShell works with nix-shell/nix develop and includes declared executable packages/build dependencies.','Requires Nix tooling; no reproducible build or OS compatibility measured.'),
350360184:('https://github.com/calcom/cal.diy','Community scheduling application intended for individual self-hosters; enterprise features removed.','README recommends personal non-production use and advanced self-hosting knowledge; no booking execution.'),
944516885:('https://github.com/financial-datasets/mcp-server','MCP tools retrieve statements, current/historical stock prices and market news.','Financial Datasets API access/account/key and data permissions require separate verification.'),
91253698:('https://github.com/ccxt/ccxt','Public exchange APIs expose tickers, order books, price feeds and OHLCV separately from private trading endpoints.','Provider conditions/rate limits and actual data access not validated; trading not authorized.'),
995562554:('https://github.com/alpacahq/alpaca-mcp-server','Official MCP offers real-time market data alongside trading; current README warns v2 tool/schema changes.','Credentials/account required; no provider/tool execution; source role only.'),
963828488:('https://github.com/ariadng/metatrader-mcp-server','README documents current bid/ask, symbols and recent/historical OHLCV candle tools alongside trading operations.','MetaTrader/account prerequisites, market-data-only enforcement and exact tool compatibility remain unverified.'),
951693330:('https://github.com/utensils/mcp-nixos','NixOS resource MCP provides surrounding Nix resource lookup.','Resource bridge is not the package builder or shell engine.'),
17165658:('https://spark.apache.org/docs/latest/streaming/index.html','Structured Streaming incrementally updates results from arriving streams using Dataset/DataFrame APIs.','Batch/micro-batch architecture and execution prerequisites require evaluation; no latency claim adopted.'),
23405758:('https://github.com/google/leveldb','Embedded ordered key-value storage library; README describes persistent key/value storage.','Language binding, recovery guarantees and actual application suitability not validated.'),
}


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
        f.write('\n')


def main():
    goals,cases,questions,capacity = [],[],[],[]
    all_ids=set()
    for number,(route,goal,terms,groups,context,language,positive,novelty) in enumerate(SPECS,1):
        previous=routes[route]
        case_id=f'HOST-PROSPECTIVE-HOLD-{number:02}'
        goal_record=dict(case_id=case_id,route=route,goal=goal,terms=terms,language=language,
            intent=dict(required_groups=groups,context_terms=context),universe_ids=previous['universe_ids'],
            novelty=novelty,prior_source_case_id=previous['case_id'])
        goals.append(goal_record)
        case=copy.deepcopy(previous)
        case.update({k:v for k,v in goal_record.items() if k not in ('novelty','prior_source_case_id')})
        case['tags']=[t for t in case['tags'] if t not in ('lexical_ru','lexical_en')]
        case['tags'].append('lexical_ru' if any(any('\u0400'<=ch<='\u04ff' for ch in term) for term in terms) else 'lexical_en')
        case['constraints']=dict(languages=[],deployment=[],allowed_licenses=[],compatibility=[],require_no_server=None,mandatory_fields=[])
        case['excluded_repository_ids']=[]
        case['excluded_dependencies']=[]
        case['goal_novelty']=novelty
        case['exposure']=dict(new_functional_goal=True,source_seen_ids=sorted(set(case['universe_ids']) & prior_ids),
            source_disjoint_ids=sorted(set(case['universe_ids'])-prior_ids),globally_unseen_repositories=False,
            author_has_seen_prior_method_failure_history=True,author_has_not_seen_new_host_model_or_rank_outputs=True,
            source_role_reuse='Previous primary-source qualification and exact pinned public cards; new task-relative numerical judgments.')
        grades={rid:grade for grade,ids in positive.items() for rid in ids}
        assert set(grades) <= set(case['universe_ids'])
        source_rows=[]
        for j in case['judgments']:
            rid=j['github_repository_id']; card=by_id[rid]; grade=grades.get(rid,0)
            j['grade']=grade
            # New goals do not inherit task-specific Go-language exclusions from
            # an old case. Default pinned archive/availability policy remains.
            j['constraint']='denied' if card['repository']['archived'] or card['repository']['availability']!='available' else 'allowed'
            factual=card['descriptions']['upstream'] or card['descriptions']['catalog'] or 'Source role remains qualified by retained primary clarification.'
            j['rationale']=f"{j['full_name']}: {factual} Task-relative grade {grade}: " + {
                3:'documented component directly supplies the required functional role.',
                2:'source-backed alternative architecture or relevant component with explicit integration differences.',
                1:'source-backed surrounding component or data/tool workflow supports part of the goal; required capability is not thereby established.',
                0:'established primary workflow differs from the required component. This is not a claim that upstream lacks every auxiliary feature.'}[grade]
            fresh=[]
            if rid in FRESH:
                url,fact,limit=FRESH[rid]
                fresh=[dict(primary_url=url,source_read='built_in_public_web_2026-10-11',factual_role=fact,limitations=limit)]
                j['primary_role_clarifications']=j.get('primary_role_clarifications',[])+fresh
            source_rows.append(dict(github_repository_id=rid,full_name=j['full_name'],primary_url=card['identity']['url'],
                descriptions=card['descriptions'],languages=card['repository']['languages'],archived=card['repository']['archived'],
                availability=card['repository']['availability'],source_card_sha256=hashlib.sha256(canonical(card)).hexdigest(),
                primary_role_clarifications=j.get('primary_role_clarifications',[]),evidence=j['evidence'],
                source_exposure='Identity and pinned card previously exposed; goal-specific source clarification noted separately.'))
        positives=sum(j['grade']>0 and j['constraint']!='denied' for j in case['judgments'])
        assert positives and min(case['k'],positives)/positives >= base['thresholds']['required_stratum_recall_at_12_min']
        capacity.append(dict(case_id=case_id,positive_denominator=positives,k=case['k'],recall_ceiling=min(case['k'],positives)/positives,feasible=True))
        cases.append(case); all_ids.update(case['universe_ids'])
        questions.append(dict(**goal_record,full_routed_universe_ids=case['universe_ids'],source_roles=source_rows,constraints=case['constraints'],
            review_scope='Grade-free identity/role/provenance/full-universe/goal novelty/intent validation; numerical grades and rankings excluded.'))
    alias=copy.deepcopy(routes['api_graphql_rpc']); alias['case_id']='HOST-PROSPECTIVE-ALIAS-01'
    alias['exposure']=dict(new_functional_goal=False,historical_alias_regression=True,globally_unseen_repositories=False)
    cases.append(alias)
    draft=dict(schema_version='cp04_host_goal_draft_v1',goals=goals,ranking_or_model_calls=0,
        independent_new_goals=True,globally_unseen_repositories=False)
    write(OUT/'goal-authoring-draft.json',draft)
    packet=dict(schema_version='cp04_host_prospective_source_questions_v1',questions=questions,
        semantic_unique_ids=len(all_ids),source_seen_ids=sorted(all_ids & prior_ids),source_disjoint_ids=sorted(all_ids-prior_ids),
        primary_new_clarification_records=len(FRESH),source_reuse_plans={p:sha(ROOT/p) for p in old_paths},
        goal_draft_sha256=sha(OUT/'goal-authoring-draft.json'),unknown_features='Remain unknown; grade zero requires a source-established different primary workflow, not absence of a feature.',
        human_acceptance=False,promotion_ready=False,model_or_rank_calls=0)
    write(OUT/'source-review-questions.json',packet)
    write(OUT/'capacity-feasibility.json',dict(cases=capacity,computed_before_new_model_or_rank_capture=True))
    plan={k:copy.deepcopy(base[k]) for k in ('pins','artifacts','thresholds','stratification')}
    plan.update(schema_version='cp04_host_prospective_plan_v1',plan_id='cp04-host-prospective-2026-10-11',
        status='source_authored_outer_contract_and_independent_review_pending',cases=cases,
        goal_draft_sha256=sha(OUT/'goal-authoring-draft.json'),source_questions_sha256=sha(OUT/'source-review-questions.json'),
        capacity_feasibility_sha256=sha(OUT/'capacity-feasibility.json'),source_hashes={},production_stability=None,
        prospective_scope=dict(functionally_new_goals=14,alias_regression_probes=1,semantic_unique_ids=len(all_ids),
            source_seen_count=len(all_ids & prior_ids),source_disjoint_count=len(all_ids-prior_ids),globally_unseen_repositories=False),
        eval_contract_path=str(CONTRACT.relative_to(ROOT)).replace('\\','/'),outer_contract_binding=None,
        public_sources=[dict(github_repository_id=rid,primary_url=v[0],factual_role=v[1],limitations=v[2]) for rid,v in FRESH.items()],
        authoring='Source-first new functional goals/numeric role judgments before new semantic pipeline outputs. Previous native method/profile/failures known.',
        adjacent_gaps=['Host semantic ordering not captured','Outer contract/schema/producer not frozen','Independent source-only review pending','Human usefulness not accepted','Installed/browser/state integration separate'],
        promotion_ready=False,human_acceptance=False)
    write(PLAN,plan)
    print(json.dumps(dict(cases=len(cases),semantic_unique_ids=len(all_ids),seen=len(all_ids&prior_ids),disjoint=len(all_ids-prior_ids),unknown_grades=0,capacity=capacity,plan_sha256=sha(PLAN))))


if __name__=='__main__':
    main()
