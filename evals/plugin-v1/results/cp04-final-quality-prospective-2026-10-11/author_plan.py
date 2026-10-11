"""Materialize explicit source-first judgments; never query a search index.

Scores below were assigned by the quality owner from public roles and bounded
primary-source clarifications before prospective ranked exposure. This script
only joins those explicit assignments to frozen provenance and route IDs.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'evals/plugin-v1/final-quality-rank-repair-regression-2026-10-11.json'
PLAN = ROOT / 'evals/plugin-v1/final-quality-prospective-2026-10-11.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


# Exact identity groups, not grades inferred from keywords or retrieved order.
GROUPS = [
 {3: [523043277], 2: [1222504,304830226], 1: [10353211,17689377,125266328], 0: [6093316,6731432,11061773,75104123,671654508]},
 {3: [84009,1451352,15062869,26820798,434708679], 1: [125863507,128396076], 0: [6247705,12332444,29102367,37489525,39840932,83229186]},
 {3: [14712850], 2: [4999959,5550552,60243197,578822531], 1: [42332863,188700274,323965659,410749029,663900193,895547074]},
 {3: [123732482,180328715,286867459,304120355], 2: [36535156,685274424], 1: [115720575,207645083], 0: [165670309]},
 {3: [31522041,91629816,816848129], 2: [896144595], 1: [91253698,849406496,944516885,963828488,995562554,1034736943,1081891045,1131513930,1195329660]},
 {3: [94911145], 2: [50617428], 1: [65252,11180687,12820537,15830664,260338399,614933136]},
 {3: [26661222,35866694,37448451,43160685], 2: [39487546], 1: [31670053,79585104,110445107,144494851,575865240,731190011,898004429,951958279,960342594,965085580,973788136,1168978399], 0: [684382,15225670,120541771,253182958,326059244,350360184,372296109,928857407,943286066,945223589,992325192,1003342581,1121557390,1143312686,1173545104]},
 {3: [464415161,516192901,650344440,666069735,764642350,883769819], 2: [6325420,611669523,1153120067,1203556545], 1: [7239495,11901762,17388759,18471236,114730000,175471189,621902641,932308018,978384239,1034520943], 0: [19971572,22337952,27529089,139323243,373845609,374072543,493550477,919664598]},
 {3: [6899875,16238673,29745084], 1: [16089035,159556794,301793434,357894794,568098118,583598619,897809208,1030580992]},
 {3: [858127,24528468,28782747,263727855,485548415], 2: [5349565,17165658,166515022], 1: [20587599,51905353,71932349,455655192,571186647]},
 {3: [138754790], 2: [176278485,19257422,60246359,84240850,480217156], 1: [927442,13124802,16563587,19816070,24494032,41986369,105944401,143344440,436658287], 0: [108110,206417,206424,4044891,6452529,28449431,114187903,235075339,422821402]},
 {3: [138597372,160919119,435625572], 1: [596892,1864194,4164482], 0: [8514,237159,458058,1148753,1863329,2609642,6296790,7548986,11551538,16072585,17620347,20904437,31504491,40136600,40772809,44344606,69495170,75505125,78452015,80945428,105379569,124230204,139914932,234231371,372172254,394929332,438384984,952098631]},
 {3: [29207621,37912398,42408804,65214191,128791889], 2: [19537979,26783295,74175805,112944063,180481986], 1: [569041,3544424,48378947,519895363], 0: [20619036,721767116,970267776]},
 {3: [11457947,180687624,262126497], 2: [5663857,45247496,267054247,565629124,1244911834], 1: [59531400,63625434,131129792,227803815,272963353,302670797,335952417,950213855], 0: [77726177,119190187,239106765,1062952726]},
]

# Task-relative source roles. A supporting score never establishes an unknown
# required feature. Zero denotes a documented different primary workflow,
# never an assertion that a feature is absent upstream.
ROLES = [
 {3:'Python lint and formatting implementation directly checks the requested source.',2:'Repository-analysis platform/aggregator with primary-source documented Python analysis; setup and scope differ from a standalone linter.',1:'Duplicate detection, hook orchestration or Python formatting supports source review; it is not a complete lint implementation.',0:'TypeScript definitions, shell analysis or JavaScript/web toolchain has a different source-language role from Python lint.'},
 {3:'JavaScript/Node unit testing framework can exercise isolated functions.',1:'DOM/React component testing utility supports a larger JavaScript testing workflow; component interaction differs from pure function isolation.',0:'Go, Java/JVM, Python or C++ test library targets a different application-language integration.'},
 {3:'Continuous file synchronization engine directly addresses the two-device folder goal.',2:'Server-backed synchronization or manual peer transfer is an alternative architecture; clients/server setup or lack of continuous automation remains a limit.',1:'File manager, file-serving protocol or filesystem bridge supports handling files but does not establish automatic folder synchronization.'},
 {3:'React-compatible application state store/toolkit addresses shared local component state.',2:'General state store requires adapter/application wiring; it supports the intended local state architecture.',1:'Immutable update helper or server-state/query cache supports a distinct part of state handling; complete shared-local-store fit is not claimed.',0:'Routing/full-stack navigation is a different primary application role.'},
 {3:'Documented historical backtesting implementation directly supports strategy research; data permissions and operability remain unverified.',2:'Historical AI backtesting is documented but model/data credentials and research prerequisites remain conditional.',1:'Market analysis, data access or execution bridge supports research context only; offline/synthetic backtesting and authority to place trades are not established.'},
 {3:'Documentation generator has documented version snapshots and independent version navigation.',2:'Documentation theme documents a version selector with external mike; extra version-deployment tooling is required.',1:'Prose/static documentation generation supports a manually arranged or companion version-publication workflow; built-in multi-version navigation is not established.'},
 {3:'Persistent text/team messaging application directly supports asynchronous team discussion.',2:'Collaboration client needs a messaging backend and deployment wiring.',1:'Messaging SDK, homeserver, bridge or history/agent connector supports team-text architecture but is not a complete team-host application.',0:'Live conferencing/meeting assistant, scheduling/time, personal-device or fitness-data tool has a different documented primary workflow; optional chat absence is not asserted.'},
 {3:'Usage metering and usage-based billing/pricing infrastructure directly supports collecting usage and calculating charges.',2:'Subscription/payment billing or in-app billing infrastructure is an alternative requiring usage calculation/integration validation.',1:'Payment adapter, invoice/accounting/PSA or billing UI supports a downstream stage; a metering API is not established by this role.',0:'App-store receipt/IAP, invoice OCR, energy/time tracking or hosting-provider/Pterodactyl billing targets a different primary workflow from usage-event SaaS billing.'},
 {3:'Primary documentation explicitly supports task/work-item time entries, effort estimation or timesheets.',1:'Project/task platform or Jira connector supports work-item context; built-in time tracking and reporting remain unproven for this task.'},
 {3:'Python tabular/DataFrame processing implementation supports batch transforms; local execution or bindings are documented where metadata was ambiguous.',2:'Distributed/SQL analytical compute is an alternative with deployment or API differences.',1:'Columnar interchange, streaming or distributed orchestration supports adjacent processing stages; a complete local batch DataFrame implementation is not inferred.'},
 {3:'In-process analytical SQL database directly supports the preferred embedded analytics architecture.',2:'Embedded general SQL or server-side analytical/time-series SQL is an alternative; embedding or analytical scope differs.',1:'General/distributed SQL or multi-model/metrics database supports a distinct architecture needing service or capability validation.',0:'Document, mobile object, key-value or distributed NoSQL primary storage has a different role from embedded local-file SQL analytics; optional query capabilities are not declared absent.'},
 {3:'Python ASGI framework has documented WebSocket handlers/connection APIs.',1:'Python HTTP/framework host supports related application context; realtime companion configuration and WebSocket compatibility remain conditional.',0:'Documented Ruby, JavaScript/TypeScript, PHP, Java/JVM, .NET, Go, Rust or Kotlin stack is a different primary language from the requested Python application.'},
 {3:'Application/edge proxy or load balancer directly supports the reverse-proxy architecture; HTTPS configuration still requires validation.',2:'API gateway or service mesh is an alternative with extra deployment or configuration scope.',1:'NAT reverse tunnel, HTTP request client or traffic monitor supports exposure/validation/diagnostics rather than a full HTTPS application proxy.',0:'DNS ad-blocking, outbound-proxy GUI or UniFi device-management connector has a different primary operational role.'},
 {3:'SBOM generation, composition analysis or combined inventory/vulnerability scanning directly supports dependency review.',2:'Dependency/package vulnerability or developer-package metadata scanner covers a relevant part of the task; complete SBOM production is not universally established.',1:'Provenance/signing/security health or source-analysis component supports another supply-chain step; dependency inventory/vulnerability coverage is not inferred.',0:'Credential scanning or MCP-service threat scanning addresses another primary threat surface; it does not establish dependency inventory.'},
]

# Bounded public reads for consequential ambiguities only. Remaining identities,
# descriptions and languages retain dated snapshot provenance. No stars,
# security/readiness, compatible versions or current operational claims added.
CLARIFICATIONS = [
 (1222504,'https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/scanners/sonarscanner-for-python','Official Python scanner analyzes Python source using a SonarQube Server connection.','Server setup is required; not standalone lint or tested compatibility.'),
 (304830226,'https://megalinter.io/latest/descriptors/python_ruff/','Official MegaLinter descriptor includes Python Ruff lint integration.','Aggregator configuration and pinned linter versions remain unverified.'),
 (5550552,'https://github.com/owncloud/core','README describes server-side file storage/sync/sharing and DAV.','Server/core needs clients; current licensing/adoption not certified.'),
 (60243197,'https://docs.nextcloud.com/server/latest/user_manual/en/files/desktop_mobile_sync.html','Desktop clients synchronize local folders through Nextcloud server.','A server plus clients is required; mobile two-way behavior differs and version compatibility is unverified.'),
 (286867459,'https://github.com/pmndrs/jotai','README describes primitive/flexible atomic React state management.','Missing frozen descriptions are qualified only for functional role.'),
 (685274424,'https://github.com/TanStack/store','README describes immutable reactive store with React and other framework adapters.','Adapter/application setup and compatibility not tested.'),
 (31522041,'https://www.vnpy.com/docs/cn/community/app/cta_backtester.html','Official Chinese documentation identifies CTA strategy backtesting/research with historical data.','Chinese text read for role, not transliterated; data feeds may need permissions; local operability untested.'),
 (91629816,'https://github.com/freqtrade/freqtrade','README explicitly describes strategy backtesting and dry-run/simulation facilities.','Research role does not authorize exchange access or trade placement.'),
 (816848129,'https://github.com/whchien/ai-trader','README and About identify Backtrader-powered strategy backtesting.','Datasets, execution readiness and claimed performance not verified.'),
 (896144595,'https://github.com/virattt/ai-hedge-fund','README documents historical backtesting and fake-money research with model/data key prerequisites.','API keys/provider costs are not authorized or used; adoption is conditional.'),
 (1081891045,'https://github.com/HKUDS/AI-Trader','README identifies automated agent trading.','Historical offline/synthetic backtesting unproven; retained only as research/execution-context component.'),
 (94911145,'https://docusaurus.io/docs/versioning','Official documentation describes independently navigable versioned documentation snapshots.','Deployment/version configuration not exercised.'),
 (50617428,'https://squidfunk.github.io/mkdocs-material/setup/setting-up-versioning/','Official versioning guide uses external mike and a version selector.','Requires companion tooling; no standalone native versioning claim for MkDocs.'),
 (15830664,'https://squidfunk.github.io/mkdocs-material/setup/setting-up-versioning/','Version-deployment companion mike can support a MkDocs documentation workflow.','Core MkDocs native multi-version navigation remains unproven.'),
 (764642350,'https://github.com/hexclave/hexclave','README explicitly lists payments/subscriptions and usage metering with credits.','Broad user infrastructure; current security, deployment and integration unknown.'),
 (516192901,'https://github.com/uselotus/lotus','README describes SaaS pricing/billing and usage-based or per-seat models.','Operational freshness and actual self-hosting not verified.'),
 (6899875,'https://github.com/opf/openproject','README/About explicitly includes work-item time tracking.','Edition/installation/version prerequisites not tested.'),
 (16238673,'https://docs.kanboard.org/v1/user/time_tracking/','Official documentation shows manual task estimates/spent hours and subtask timers/record breakdown.','Task totals and timer behavior differ; reporting usefulness not human-reviewed.'),
 (29745084,'https://github.com/Leantime/docs/blob/master/using-leantime/timesheets.md','Official docs show task Start Work timer and entries in timesheets.','Current installation, edition and API compatibility not tested.'),
 (29745084,'https://support.leantime.io/en/article/how-to-track-time-in-leantime-hwbo4x/','Official support describes timesheet views and manual per-task/client time entries.','Documentation role confirmation only.'),
 (263727855,'https://github.com/pola-rs/polars','README confirms Python DataFrame bindings despite Rust implementation metadata.','Architecture-specific extras and runtime performance unverified.'),
 (28782747,'https://docs.dask.org/en/stable/dataframe.html','Official Dask DataFrame uses Python/pandas and supports laptop as well as distributed tabular processing.','No actual benchmark or cluster run.'),
 (485548415,'https://github.com/Eventual-Inc/Daft','README documents Python-native processing starting locally.','AI/multimodal emphasis does not imply provider authorization.'),
 (485548415,'https://docs.daft.ai/en/stable/quickstart/','Official quickstart exposes Python DataFrame loading/processing and local execution path.','Correct linked URL used after an obsolete .html path was inaccessible; no actual execution.'),
 (176278485,'https://www.sqlite.org/about.html','Official About describes an in-process, serverless transactional SQL library.','General SQL rather than dedicated analytical-file engine.'),
 (480217156,'https://github.com/GreptimeTeam/greptimedb','README documents columnar observability database with SQL over metrics/logs/traces.','Server-side architecture, not established embedded local-file replacement.'),
 (138597372,'https://starlette.dev/websockets/','Official WebSocket API documents accepting, sending, receiving and closing ASGI connections.','Current starlette.dev replaces inaccessible starlette.io link; server extension support remains conditional.'),
 (160919119,'https://fastapi.tiangolo.com/advanced/websockets/','Official documentation shows Python WebSocket endpoints and message handling.','Long-lived production operation/scaling not tested.'),
 (435625572,'https://docs.litestar.dev/latest/usage/websockets.html','Official documentation includes ASGI WebSocket handlers.','Compatibility and connection lifecycle behavior not exercised.'),
 (596892,'https://flask.palletsprojects.com/en/stable/async-await/','Official async guide describes WSGI worker limits and recommends ASGI/Quart for mainly async/WebSocket workloads.','Flask remains a related HTTP host, not a proven native WebSocket handler.'),
 (29207621,'https://caddyserver.com/docs/quick-starts/reverse-proxy','Official quickstart documents reverse proxy with client-side and backend HTTPS.','Certificate trust, permissions and deployed configuration remain untested.'),
 (37912398,'https://nginx.org/en/docs/http/ngx_http_proxy_module.html','Official proxy module forwards HTTP/HTTPS to upstream services.','TLS/server deployment configuration and live behavior not tested.'),
 (11457947,'https://github.com/DependencyTrack/dependency-track','README explicitly uses SBOM for component/supply-chain risk analysis.','Version lifecycle/installation remains conditional; no runtime scan.'),
 (267054247,'https://github.com/anchore/grype','README explicitly scans Syft SBOM for vulnerabilities.','Vulnerability DB completeness and scan operation not tested.'),
]


def main():
    if (OUT / 'observations.json').exists() or PLAN.exists():
        raise ValueError('prospective authoring cannot overwrite a plan/capture')
    base = json.loads(BASE.read_bytes())
    draft = json.loads((OUT / 'goal-authoring-draft.json').read_bytes())
    cards = json.loads((ROOT / base['artifacts']['cards_path']).read_bytes())['cards']
    by_id = {c['identity']['github_repository_id']:c for c in cards}
    seen = {j['github_repository_id'] for c in base['cases'] for j in c['judgments']}
    live = {}
    for rid,url,fact,limit in CLARIFICATIONS:
        live.setdefault(rid,[]).append(dict(primary_url=url, source_read='built_in_public_web_2026-10-11', factual_role=fact, limitations=limit))
    cases, questions, capacity = [], [], []
    for index, goal in enumerate(draft['goals']):
        ids = goal['universe_ids']
        grades = {rid:grade for grade,values in GROUPS[index].items() for rid in values}
        assert set(grades) == set(ids) and len(grades) == sum(map(len,GROUPS[index].values()))
        judgments, roles = [], []
        for rid in ids:
            card = by_id[rid]
            grade = grades[rid]
            ref = card['provenance']['sources'][0]['source_ref']
            evidence = []
            for pointer in ('/identity/full_name','/descriptions','/repository/languages','/repository/archived','/repository/availability','/repository/visibility','/activity/last_release_at','/activity/last_commit_at','/activity/observed_at'):
                value = card
                for key in pointer.strip('/').split('/'):
                    value = value[key]
                evidence.append(dict(pointer=pointer,value=value,source_ref=ref))
            constraint = 'denied' if card['repository']['archived'] or card['repository']['availability'] != 'available' else 'allowed'
            rationale = card['identity']['full_name'] + ': ' + ROLES[index][grade]
            judgments.append(dict(github_repository_id=rid,full_name=card['identity']['full_name'],grade=grade,constraint=constraint,
                rationale=rationale,evidence=evidence,primary_role_clarifications=live.get(rid,[]),
                adoption_limitations='Task-relative component role only. Unknown required features are not negative absence claims. Current operability, license suitability, security, provider prerequisites and human usefulness remain unverified.'))
            roles.append(dict(github_repository_id=rid,full_name=card['identity']['full_name'],primary_url=card['identity']['url'],
                descriptions=card['descriptions'],source_languages=card['repository']['languages'],archive=card['repository']['archived'],
                availability=card['repository']['availability'],constraint_expectation=constraint,source_ref=ref,
                role_relative_to_goal=ROLES[index][grade],primary_clarifications=live.get(rid,[]),
                evidence_limit='Different primary role is not upstream feature absence; supporting role is not verified full-fit or adoption.'))
        tags = ['lexical_' + goal['language'],'activity_unknown']
        if len(ids) <= base['stratification']['thin_leaf_max_cards']:
            tags.append('thin_leaf')
        if len(ids) >= base['stratification']['dense_leaf_min_cards']:
            tags.append('dense_leaf')
        if any(by_id[r]['catalog']['membership_cohort'] == 'baseline' for r in ids):
            tags.append('baseline_cohort')
        if any(by_id[r]['catalog']['membership_cohort'] == 'cat07a_expansion' for r in ids):
            tags.append('expansion_cohort')
        if any(by_id[r]['descriptions']['upstream'] is not None and by_id[r]['descriptions']['catalog'] is not None for r in ids):
            tags.append('dual_descriptions')
        if any(len(by_id[r]['classifications']) > 1 for r in ids):
            tags.append('secondary_dedupe')
        if goal['route'] == 'communications_personal_ops':
            tags.append('container_union')
        exposure = dict(new_functional_goal_before_first_rank=True, source_seen_ids=sorted(set(ids)&seen),
            source_disjoint_ids=sorted(set(ids)-seen), prior_exposure_reference='Both source-qualified15 and independent15 now exposed after calibration.',
            globally_unseen_repositories=False, broader_history='Possible prior catalog/history exposure; not claimed globally unseen.',
            known_ranker_profile=True, goal_selection='Functional goal chosen before prospective ranks, independent of known missed vocabulary in previous goals.')
        case = {k:copy.deepcopy(goal[k]) for k in ('case_id','route','goal','terms','language','intent','universe_ids')}
        case.update(split='held_out',metric_family='semantic',container_domain_ids=[base['stratification']['container_ids'][index]],
            constraints=copy.deepcopy(base['cases'][0]['constraints']), excluded_repository_ids=[],excluded_dependencies=[],judgments=judgments,tags=tags,k=12,exposure=exposure)
        positive_count = sum(j['grade'] > 0 and j['constraint'] != 'denied' for j in judgments)
        ceiling = min(12,positive_count)/positive_count
        capacity.append(dict(case_id=case['case_id'],allowed_positive_count=positive_count,recall_at_12_ceiling=ceiling,
            stratum_threshold=base['thresholds']['required_stratum_recall_at_12_min'],feasible=ceiling>=base['thresholds']['required_stratum_recall_at_12_min'],ranked_exposure=False))
        questions.append(dict(case_id=case['case_id'],goal=case['goal'],route=case['route'],container_domain_ids=case['container_domain_ids'],
            terms=case['terms'],intent=case['intent'],language=case['language'],constraints=case['constraints'],tags=tags,
            full_routed_universe_ids=ids,exposure=exposure,grade_free_roles=roles))
        cases.append(case)
    alias = copy.deepcopy(base['cases'][-1])
    alias['case_id'] = 'PROSPECTIVE-ALIAS-01'
    alias['exposure'] = dict(new_functional_goal_before_first_rank=False,source_seen_ids=alias['universe_ids'],globally_unseen_repositories=False,
        scope='Exposed historical identity regression; excluded from semantic macro.')
    cases.append(alias)
    assert all(c['feasible'] for c in capacity)
    assert sum(len(c['judgments']) for c in cases[:-1]) == 244
    assert sum(len(c['exposure']['source_seen_ids']) for c in cases[:-1]) == 85
    assert sum(len(c['exposure']['source_disjoint_ids']) for c in cases[:-1]) == 159
    scope = dict(new_semantic_goals=14,identity_regression_probes=1,semantic_source_judgments=244,semantic_unique_ids=244,
        prior_two_suites_unique_ids=len(seen),source_disjoint_ids=159,source_seen_ids=85,disjoint_leaf_goal_cases=10,seen_new_goal_cases=4,
        role_unknown_grades=0,unresolved_required_feature_adoption='Retained per judgment; not converted to feature-absence negatives.',
        functional_goal_independence=True,globally_unseen_repositories=False,ranked_capture_count_at_authoring=0,
        source_clarification_records=len(CLARIFICATIONS),source_clarified_unique_ids=len(live))
    packet = dict(schema_version='cp04_prospective_source_review_questions_v1',scope=scope,questions=questions,
        identity_probe={k:v for k,v in alias.items() if k!='judgments'},capacity_feasibility=capacity,
        goal_draft_sha256=sha(OUT/'goal-authoring-draft.json'),
        read_failures_retained=['Daft old .html quickstart URL inaccessible; linked trailing-slash quickstart succeeded.',
            'Starlette old .io WebSocket URL inaccessible; current .dev official API succeeded.',
            'Leantime guessed source directory URL inaccessible; official docs/support confirm role instead.'],
        review_request='Read grade-free packet only. Validate full route universes, identity/provenance, primary role facts, real functional goal/intent partition, capacity/exposure and archive expectations. Do not approve numerical grades, ranked retrieval, human usefulness or promotion.',
        preserved_source_limits=['Mattermost video caveats from prior qualification do not change text-chat role.',
            'Archived cards retain deny expectations under frozen policy, including Dendrite.',
            'Provider/trading integrations are research context only; no credentials, remote operation or trade authorization.',
            'No current whole-corpus GitHub refresh; unclarified facts retain dated snapshot evidence.'])
    write(OUT/'source-review-questions.json',packet)
    write(OUT/'capacity-feasibility.json',dict(evidence_kind='pre_rank_oracle_capacity',cases=capacity,all_feasible=True,ranking_seen=False))
    plan = dict(schema_version='cp04_final_quality_design_v1',plan_id='cp04-final-quality-prospective-2026-10-11',
        evidence_owner='quality_evaluator',acceptance_owner='product_planner',status='production_source_frozen',
        authoring='New functional goals and complete source-first role grades frozen before their first ranked capture after ranker calibration on other goals.10 leaf universes159 IDs disjoint from prior two suites;4 new goals85 seen sources. No global repository novelty or human acceptance claim.',
        base_regression_plan_sha256=sha(BASE),goal_draft_sha256=sha(OUT/'goal-authoring-draft.json'),
        source_questions_sha256=sha(OUT/'source-review-questions.json'),capacity_feasibility_sha256=sha(OUT/'capacity-feasibility.json'),
        cases=cases,prospective_scope=scope,adjacent_gaps=copy.deepcopy(base['adjacent_gaps']),public_sources=CLARIFICATIONS,
        production_stability=copy.deepcopy(base['production_stability']),promotion_ready=False,human_acceptance=False)
    for key in ('pins','artifacts','thresholds','stratification'):
        plan[key] = copy.deepcopy(base[key])
    paths = set(base['source_hashes']) | {'evals/plugin-v1/run_final_prospective.py'}
    plan['source_hashes'] = {p:sha(ROOT/p) for p in sorted(paths)}
    write(PLAN,plan)
    print(json.dumps(dict(plan_sha256=sha(PLAN),questions_sha256=sha(OUT/'source-review-questions.json'),
        runner_sha256=sha(ROOT/'evals/plugin-v1/run_final_prospective.py'),scope=scope,capacity=capacity)))


if __name__ == '__main__':
    main()
