"""One native, source-frozen replay of 45 exposed cases and four formal inputs.

Original literal observations are retained and independently recomputed without
an injected retrieval adapter. No model, source collection or acceptance tuning.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-final-chat-repair-2026-10-11'
PLAN = OUTPUT / 'frozen-plan.json'
PREFIX = 'evals/plugin-v1/'
REG = PREFIX + 'final-quality-rank-repair-regression-2026-10-11.json'
PRO = PREFIX + 'final-quality-prospective-2026-10-11.json'
REG_DIR = PREFIX + 'results/cp04-final-quality-rank-repair-regression-2026-10-11/'
PRO_DIR = PREFIX + 'results/cp04-final-quality-prospective-2026-10-11/'
FORMAL_DIR = PREFIX + 'results/cp04-final-current-calibration-2026-10-11/'
RUNTIME_HASHES = {
    'plugins/myai-stackguide/scripts/recommendation_request.py': '4f45e1c0e17aca09149e94602fbc8d84f2d2a74ce25f53de40b48f5f14c53b56',
    'plugins/myai-stackguide/scripts/retrieval.py': '7d2385c3143b85f9089c422ffa930650bf0dd799ded665416e02e78768f5f6b5',
}
INPUT_HASHES = {
    REG: '56579b4e01eb5a3a353c788c216576973ce9825adf9c2409fd58302dac5d78c6',
    PRO: '37041760032aea200987092c97b49066e824d63cb208d63c3556791257e4833f',
    REG_DIR + 'observations.json': 'd477e7ba974aaebe9a32f5e12009fef25914f78a95417291dfd52cc229922613',
    REG_DIR + 'declaration.json': 'fb3a1ebc7fa40cfddef776f009dff861433c9f0b91f63f30b837b31edefb81e6',
    PRO_DIR + 'observations.json': '258c5baf3b9b37a4841ba50fe53dad5569696e5a2943c21eea10c4fdec9f4639',
    PRO_DIR + 'declaration.json': '0fa7f99acb4ded3b97a3c3456a8f7e80a94b68e80e964fa39b01af3a097a5362',
    PRO_DIR + 'source-independent-review.json': '78351b82df6763e72546c0f342db80133708fc3b695e09dfe6b887adfed77f2d',
    PRO_DIR + 'source-review-questions.json': '2fa87a67566373b85c66a57825d85916888bc04de065d46c76ef7dee9795bc92',
    FORMAL_DIR + 'observations.json': 'bd97758a1ef1de9286c8a9e11b4dd0332f96e1e6fe702ebeafe9d90ca8b033ff',
    FORMAL_DIR + 'declaration.json': '93e180ddf242412e335a6aead40dfeb8fb816a67e67ae70860260c68fd375718',
}
spec = importlib.util.spec_from_file_location('chat_regression_helpers', ROOT / PREFIX / 'run_final_rank_repair_regression.py')
regression = importlib.util.module_from_spec(spec)
spec.loader.exec_module(regression)
runner = regression.runner
runtime = runner.runtime
runner.OUTPUT = OUTPUT


def read(path):
    return json.loads((ROOT / path).read_bytes())


def verify_hashes(hashes):
    for path, digest in hashes.items():
        if runner.sha(ROOT / path) != digest:
            raise ValueError('bound input/source drift: ' + path)


def build_plan():
    verify_hashes(INPUT_HASHES)
    verify_hashes(RUNTIME_HASHES)
    base, prospective = read(REG), read(PRO)
    for key in ('pins', 'artifacts', 'thresholds', 'stratification'):
        if base[key] != prospective[key]:
            raise ValueError('prior accepted tuple differs: ' + key)
    sources = dict(prospective['source_hashes'])
    for path, digest in sources.items():
        if path not in RUNTIME_HASHES and runner.sha(ROOT / path) != digest:
            raise ValueError('unexpected source change: ' + path)
    sources.update(RUNTIME_HASHES)
    sources[PREFIX + 'run_final_chat_repair.py'] = runner.sha(Path(__file__))
    cases = base['cases'] + prospective['cases']
    prior = read(REG_DIR + 'observations.json')['records'] + read(PRO_DIR + 'observations.json')['records']
    if len(cases) != 45 or len({c['case_id'] for c in cases}) != 45:
        raise ValueError('45-case union mismatch')
    for case, row in zip(cases, prior):
        if case['case_id'] != row['case_id'] or runner.old.scorer.digest(case) != row['case_sha256']:
            raise ValueError('original case capture binding mismatch')
        if runner.old.scorer.digest(row['payload']) != row['payload_sha256']:
            raise ValueError('original payload binding mismatch')
    return dict(schema_version='cp04_chat_repair_plan_v1', status='production_source_frozen',
                cases=copy.deepcopy(cases), input_hashes=INPUT_HASHES, source_hashes=sources,
                pins=base['pins'], artifacts=base['artifacts'], thresholds=base['thresholds'],
                stratification=base['stratification'], source_review_refs=base['source_review_refs'],
                suites=base['suites'] + [dict(suite_id='prospective_now_exposed15',
                    case_ids=[c['case_id'] for c in prospective['cases']])],
                production_stability=dict(source_hashes=RUNTIME_HASHES,
                    authority='Root implementation READY FREEZE; observed RED then brief18/retrieval23 GREEN'),
                exposure='All 45 goals, judgments and earlier rankings exposed; regression only.',
                human_acceptance=False, promotion_ready=False, fresh_acceptance=False)


def load(plan):
    if plan != build_plan():
        raise ValueError('frozen plan mismatch')
    verify_hashes(plan['source_hashes'])
    for receipt in plan['source_review_refs']:
        review = regression.read_bound(receipt['path'], receipt['sha256'])
        regression.read_bound(receipt['reviewed_plan_path'], receipt['reviewed_plan_sha256'])
        regression.read_bound(receipt['questions_path'], receipt['questions_sha256'])
        if review.get('approved') is not True or review.get('unresolved') != [] or review[receipt['plan_field']] != receipt['reviewed_plan_sha256'] or review['source_questions_sha256'] != receipt['questions_sha256']:
            raise ValueError('historical source-only review mismatch')
    review = read(PRO_DIR + 'source-independent-review.json')
    if review.get('approved') is not True or review.get('unresolved') != [] or review['prospective_plan_sha256'] != INPUT_HASHES[PRO] or review['source_questions_sha256'] != INPUT_HASHES[PRO_DIR + 'source-review-questions.json']:
        raise ValueError('prospective source-only review mismatch')
    projected = read(PREFIX + 'quality-plan.json')
    for key in ('thresholds', 'stratification'):
        if projected[key] != plan[key]:
            raise ValueError('acceptance drift')
    projected['pins'], projected['artifacts'] = plan['pins'], plan['artifacts']
    runner.old.scorer.validate_quality_plan(projected)
    cards = read(plan['artifacts']['cards_path'])['cards']
    by_id = {c['identity']['github_repository_id']: c for c in cards}
    members, registry = runner.old.route_members(projected)
    for case in plan['cases']:
        routed = {rid for rid, card in by_id.items() if any(a['category_id'] in members[case['route']] for a in card['classifications'])}
        ids = [j['github_repository_id'] for j in case['judgments']]
        if set(ids) != set(case['universe_ids']) or len(ids) != len(set(ids)) or (case['metric_family'] == 'semantic' and set(ids) != routed):
            raise ValueError('oracle universe mismatch')
        for judgment in case['judgments']:
            card = by_id[judgment['github_repository_id']]
            if type(judgment['grade']) is not int or not 0 <= judgment['grade'] <= 3 or (card['repository']['archived'] and judgment['constraint'] != 'denied'):
                raise ValueError('invalid frozen judgment')
            for evidence in judgment['evidence']:
                value = card
                for key in evidence['pointer'].strip('/').split('/'):
                    value = value[key]
                if value != evidence['value'] or evidence['source_ref'] not in runner.old.scorer.canonical(card).decode():
                    raise ValueError('frozen source evidence mismatch')
    return cards, members, registry


def native_capture(payload):
    """Observe real immutable SQLite connections and unchanged native results."""
    traces, raw, connections = [], [], []
    original = runtime.retrieval.sqlite3.connect
    def connect(*args, **kwargs):
        connection = original(*args, **kwargs)
        index = len(connections)
        connections.append(dict(connection=index, database=str(args[0]), uri=kwargs.get('uri', False)))
        connection.set_trace_callback(lambda sql: traces.append(dict(connection=index, sql=sql)))
        return connection
    def spy(query, **kwargs):
        value = runtime.retrieval.retrieve(query, **kwargs)
        raw.append(value)
        return value
    runtime.retrieval.sqlite3.connect = connect
    try:
        result = runtime.run(**copy.deepcopy(payload), retrieve=spy)
    finally:
        runtime.retrieval.sqlite3.connect = original
    matches = [t for t in traces if ' MATCH ' in t['sql'].upper()]
    counts = [t for t in matches if 'SELECT COUNT(*)' in t['sql'].upper()]
    writes = [t for t in traces if t['sql'].lstrip().upper().split(' ', 1)[0] in {'INSERT','UPDATE','DELETE','CREATE','DROP','ALTER','REPLACE','VACUUM','ATTACH'}]
    query = result['request']['catalog_query']
    derivation = result['request'].get('query_derivation')
    gates = dict(one_count=len(counts) == 1, one_ranked_match=len(matches) - len(counts) == 1,
                 one_native_retrieval=len(raw) == 1, no_sql_writes=not writes,
                 immutable_connections=all(c['uri'] and 'mode=ro' in c['database'] and 'immutable=1' in c['database'] for c in connections),
                 intent_preserved=result['request']['intent'] == payload['interpretation']['intent'],
                 aggregate_calls_one=result['aggregate_calls'] == 1, no_persisted_observations=result['observations_persisted'] is False,
                 limits_preserved=query['max_cards'] == 12 and query['max_evidence_bytes'] == 163840,
                 pack_within_budget=len(runner.old.scorer.canonical(result['evidence_pack'])) <= query['max_evidence_bytes'])
    if not all(gates.values()):
        raise ValueError('native boundary/budget drift: ' + json.dumps(gates))
    return result, raw[0], dict(gates=gates, connections=connections, sql_trace=traces,
                                query_derivation=derivation)


def declaration(plan):
    prior = read(REG_DIR + 'observations.json')['records'] + read(PRO_DIR + 'observations.json')['records']
    formal = read(FORMAL_DIR + 'observations.json')['records']
    return dict(schema_version='cp04_chat_repair_declaration_v1', plan_sha256=runner.sha(PLAN),
        source_hashes=plan['source_hashes'], input_hashes=plan['input_hashes'], pins=plan['pins'],
        thresholds=plan['thresholds'], cases=[dict(case_id=r['case_id'],case_sha256=r['case_sha256'],payload_sha256=r['payload_sha256']) for r in prior],
        formal_inputs=[dict(case_id=r['case_id'],payload_sha256=runtime.digest(dict(brief=r['brief'],interpretation=r['interpretation'],public_observations=[]))) for r in formal],
        candidate='Actual runtime.run + native immutable SQLite COUNT/metadata/FTS + guard/pack',
        baseline='Unchanged historical original literal orders, independently recomputed; no transport adapter',
        evidence_limit='Exposed regression; no fresh/human/promotion acceptance', human_acceptance=False, promotion_ready=False)


def capture(plan, cards, members, registry):
    prior = read(REG_DIR + 'observations.json')['records'] + read(PRO_DIR + 'observations.json')['records']
    records, preservation = [], []
    for case, previous in zip(plan['cases'], prior):
        result, raw, trace = native_capture(previous['payload'])
        query = result['request']['catalog_query']
        filtered = [c for c in cards if any(a['category_id'] in members[case['route']] for a in c['classifications'])]
        literal = runner.old.scorer.lexical_baseline(filtered, case['terms'], query['max_candidates'])
        if literal != previous['baseline']['raw_ranked_ids'] or runner.rank(literal, case['judgments'], case['k']) != previous['baseline']['ranking']:
            raise ValueError('original literal order/metric changed: ' + case['case_id'])
        candidate = runner.observe(case, result, raw['status'])
        records.append(dict(case_id=case['case_id'],case_sha256=previous['case_sha256'],
            payload=previous['payload'],payload_sha256=previous['payload_sha256'],
            query=query,query_sha256=runtime.digest(query),split=case['split'],metric_family=case['metric_family'],
            tags=case['tags'],container_domain_ids=case['container_domain_ids'],candidate=candidate,
            baseline=previous['baseline'],baseline_evidence='Historical exact original capture; independently recomputed original literal order/metric',
            candidate_capture=result,candidate_capture_sha256=runtime.digest(result),candidate_raw_result=raw,native_trace=trace))
        preservation.append(dict(case_id=case['case_id'],literal_exact=True,
            candidate_order_exact=candidate['raw_ranked_ids'] == previous['candidate']['raw_ranked_ids'],
            candidate_metric_exact=candidate['ranking'] == previous['candidate']['ranking'],
            selected_ids_exact=result['selected_ids'] == previous['candidate_capture']['selected_ids'],
            evidence_pack_exact=result['evidence_pack'] == previous['candidate_capture']['evidence_pack']))
    runner.write('observations.json',dict(schema_version='cp04_chat_repair_observations_v1',plan_sha256=runner.sha(PLAN),records=records))
    formal_rows = []
    for previous in read(FORMAL_DIR + 'observations.json')['records']:
        payload = dict(brief=previous['brief'],interpretation=previous['interpretation'],public_observations=[])
        result, raw, trace = native_capture(payload)
        before = previous['result']
        formal_rows.append(dict(case_id=previous['case_id'],payload_sha256=runtime.digest(payload),
            query_exact=result['request']['catalog_query'] == before['request']['catalog_query'],
            raw_order_exact=result['raw_ranked_ids'] == before['raw_ranked_ids'],
            selected_ids_exact=result['selected_ids'] == before['selected_ids'],
            evidence_pack_exact=result['evidence_pack'] == before['evidence_pack'],
            full_result_exact=result == before,prior_result_sha256=runtime.digest(before),current_result_sha256=runtime.digest(result),
            answer_binding='Prior actual answers remain bound to prior full result; no new composition or verification on changed inputs',
            result=result,raw_result=raw,native_trace=trace))
    runner.write('formal-identity-comparison.json',dict(records=formal_rows,model_calls=0,human_acceptance=False))
    by_id = {r['case_id']:r for r in records}
    suites = {s['suite_id']:regression.suite_summary([by_id[cid] for cid in s['case_ids']],plan) for s in plan['suites']}
    overall = regression.suite_summary(records, plan)
    old30 = preservation[:30]
    gates = dict(all_suite_gates=all(all(s['gates'].values()) for s in suites.values()),
        aggregate_gates=all(overall['gates'].values()), original_literals_exact=all(p['literal_exact'] for p in preservation),
        old30_order_and_metrics_exact=all(p['candidate_order_exact'] and p['candidate_metric_exact'] for p in old30),
        native_boundaries_all=all(all(r['native_trace']['gates'].values()) for r in records))
    deficits = []
    for case, row in zip(plan['cases'],records):
        if case['metric_family'] != 'semantic':
            continue
        metrics = row['candidate']['ranking']['ranking']
        floors = dict(recall_at_k=plan['thresholds']['required_stratum_recall_at_12_min'],ndcg_at_k=plan['thresholds']['required_stratum_ndcg_at_12_min'])
        if any(metrics[k] < v for k,v in floors.items()):
            deficits.append(dict(case_id=case['case_id'],metrics=metrics,floors=floors,
                positive_top12=row['candidate']['positive_top12_count'],positive_denominator=sum(j['grade'] > 0 and j['constraint'] != 'denied' for j in case['judgments'])))
    conclusion = dict(schema_version='cp04_chat_repair_conclusion_v1',verdict='regression_verified_only' if all(gates.values()) else 'no_go',
        gates=gates,suites=suites,aggregate=overall,per_case_deficits=deficits,preservation=preservation,
        native_case_count=45,formal_identity_case_count=4,native_retrieval_calls=49,model_calls=0,
        source_hashes=plan['source_hashes'],pins=plan['pins'],human_acceptance=False,promotion_ready=False,
        fresh_acceptance=False,prior_failed_captures_retained=True,
        evidence_limit='Actual local native FTS/guard/pack replay of exposed cases; fresh and human acceptance remain open.')
    runner.write('conclusion.json',conclusion)
    runner.write('artifact-hashes.json',{name:runner.sha(OUTPUT/name) for name in ('frozen-plan.json','declaration.json','observations.json','formal-identity-comparison.json','conclusion.json')})
    return conclusion


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--freeze',action='store_true')
    mode.add_argument('--run',action='store_true')
    args = parser.parse_args()
    try:
        if args.freeze:
            plan = build_plan()
            load(plan)
            runner.write('frozen-plan.json',plan)
            runner.write('declaration.json',declaration(plan))
            print(json.dumps(dict(declared=True,cases=45,formal_inputs=4,plan_sha256=runner.sha(PLAN))))
            return 0
        plan = json.loads(PLAN.read_bytes())
        cards,members,registry = load(plan)
        if json.loads((OUTPUT/'declaration.json').read_bytes()) != declaration(plan) or (OUTPUT/'observations.json').exists():
            raise ValueError('capture exists or declaration drift')
        result = capture(plan,cards,members,registry)
        print(json.dumps({k:result[k] for k in ('verdict','gates','per_case_deficits')}))
        return 0 if result['verdict'] == 'regression_verified_only' else 1
    except (ValueError,KeyError,FileExistsError,FileNotFoundError) as error:
        print(json.dumps(dict(status='invalid_protocol',reason=str(error))))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
