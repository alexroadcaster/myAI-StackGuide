"""Source-pinned successor CP04 offline runner. Synthetic C8 remains separate."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import importlib.util
import json
import platform
import shutil
import sqlite3
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('cp04_frozen_helpers', ROOT / 'evals/plugin-v1/run_quality.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
scorer = old.scorer
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-v2-2026-10-08'
PLAN_PATH = ROOT / 'evals/plugin-v1/quality-plan-v2.json'
JUDGMENTS_PATH = ROOT / 'evals/plugin-v1/quality-judgments-v2.json'
HEADROOM = ROOT / '.codex-tmp/cp04-v2-headroom'


def validate_case_universe(case, oracle_case, routed_ids):
    """Require full source-authored coverage, including secondary assignments."""
    require = scorer.require
    universe = case['universe_ids']
    require(all(type(item) is int and item > 0 for item in universe) and
            len(universe) == len(set(universe)), 'invalid universe identities')
    require(set(universe) == set(routed_ids), 'routed universe mismatch')
    require(oracle_case['case_id'] == case['case_id'] and
            oracle_case['universe_ids'] == universe, 'oracle universe mismatch')
    rows = oracle_case['judgments']
    ids = [item['github_repository_id'] for item in rows]
    require(len(ids) == len(set(ids)) and set(ids) == set(universe), 'judgment universe incomplete/duplicate')
    for item in rows:
        require(type(item['grade']) is int and 0 <= item['grade'] <= 3, 'invalid grade')
        require(item['constraint'] in {'allowed', 'denied', 'unknown'}, 'invalid constraint')
        require(isinstance(item.get('rationale'), str) and item['rationale'].strip() and
                isinstance(item.get('evidence'), list) and item['evidence'], 'missing source evidence')
        for evidence in item['evidence']:
            require(isinstance(evidence.get('pointer'), str) and evidence['pointer'].startswith('/') and
                    'value' in evidence and isinstance(evidence.get('source_ref'), str) and
                    evidence['source_ref'], 'invalid source evidence')


def validate_frozen_settings(plan, frozen):
    for key in ('thresholds', 'pins', 'artifacts', 'candidate_route', 'lexical_baseline', 'scale_protocol'):
        scorer.require(plan[key] == frozen[key], 'frozen ' + key + ' changed')


def semantic_records(records):
    return [item for item in records if item['metric_family'] == 'semantic']


def constrained_ranking(ids, judgments, k):
    """Denied hits retain raw rank positions but have zero constrained gain."""
    constrained = [{**row, 'grade': 0 if row['constraint'] == 'denied' else row['grade']} for row in judgments]
    return old.strict_ranking(ids, constrained, k)


def identity_observation(ids, pack, case):
    targets = set(case.get('expected_identity_ids', []))
    denied = {row['github_repository_id'] for row in case['judgments'] if row['constraint'] == 'denied'}
    allowed = {row['github_repository_id'] for row in case['judgments'] if row['constraint'] == 'allowed'}
    packed = {row['card']['identity']['github_repository_id'] for row in pack['cards']}
    return {'target_ids': sorted(targets),
            'raw_exact_identity_success': float(targets <= set(ids[:case['k']])) if targets else None,
            'denied_identity_in_pack': sorted(targets & denied & packed),
            'allowed_exact_identity_pack_success': float(targets & allowed <= packed)
                if targets & allowed else None}


def write_json(name, value):
    scorer.require(Path(name).name == name and name.endswith('.json'), 'invalid output name')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def pointer_value(value, pointer):
    for part in pointer.lstrip('/').split('/'):
        key = part.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def load_protocol(plan_path, judgments_path):
    frozen = scorer.load_json(old.PLAN_PATH)
    scorer.validate_quality_plan(frozen)  # Existing source/index/manifest/policy validation.
    plan = scorer._load_json_bounded(plan_path, 4 * 1024 * 1024)
    oracle = scorer._load_json_bounded(judgments_path, 16 * 1024 * 1024)
    validate_frozen_settings(plan, frozen)
    scorer.require(oracle['plan_sha256'] == scorer.digest(plan), 'oracle plan digest mismatch')
    for source in (plan, oracle):
        scorer.require(source.get('source_hashes'), 'missing oracle source hashes')
        for path, digest in source['source_hashes'].items():
            resolved = (ROOT / path).resolve()
            scorer.require(resolved.is_relative_to(ROOT), 'oracle source path escape')
            scorer.require(scorer.file_sha256(resolved) == digest, 'oracle source digest mismatch')
        scorer.require(source['source_hashes'].get(plan['artifacts']['cards_path']) == plan['pins']['cards_sha256'],
                       'oracle card digest mismatch')
    cards = scorer._load_json_bounded(ROOT / plan['artifacts']['cards_path'], 16 * 1024 * 1024)['cards']
    cards_by_id = {card['identity']['github_repository_id']: card for card in cards}
    members, registry = old.route_members(plan)
    cases = plan['cases']
    case_ids = [case['case_id'] for case in cases]
    oracle_ids = [case['case_id'] for case in oracle['cases']]
    scorer.require(len(case_ids) == len(set(case_ids)) and len(oracle_ids) == len(set(oracle_ids)) and
                   set(case_ids) == set(oracle_ids), 'case coverage mismatch')
    oracles = {item['case_id']: item for item in oracle['cases']}
    attached = copy.deepcopy(plan)
    for case in attached['cases']:
        scorer.require(case['metric_family'] in {'identity', 'semantic'}, 'invalid metric family')
        scorer.require(case['goal_kind'] in {'exact_identity', 'functional_alternative', 'supporting_component'},
                       'invalid goal kind')
        scorer.require(case['split'] in {'development', 'held_out', 'identity_probe'}, 'invalid split')
        scorer.require(case['k'] == plan['candidate_route']['max_cards'], 'metric k changed')
        routed = {repo_id for repo_id, card in cards_by_id.items() if any(
            row['category_id'] in members[case['target_category_id']] for row in card['classifications'])}
        oracle_case = oracles[case['case_id']]
        validate_case_universe(case, oracle_case, routed)
        for row in oracle_case['judgments']:
            card = cards_by_id[row['github_repository_id']]
            for evidence in row['evidence']:
                scorer.require(pointer_value(card, evidence['pointer']) == evidence['value'],
                               'source evidence value mismatch')
                scorer.require(evidence['source_ref'] in scorer.canonical(card).decode('utf-8'),
                               'source reference not in card')
        case['judgments'] = oracle_case['judgments']
        case['judgment_pool_ids'] = case['universe_ids']
        case.setdefault('expected_alias', None)
        query = old.make_query(plan, case)
        if 'query_sha256' in case:
            scorer.require(case['query_sha256'] == scorer.digest(query), 'frozen query digest mismatch')
        if case['metric_family'] == 'identity':
            scorer.require(case.get('expected_identity_ids') and
                           set(case['expected_identity_ids']) <= routed, 'identity target missing/outside route')
    for split in ('held_out',):
        selected = [case for case in cases if case['split'] == split and case['metric_family'] == 'semantic']
        scorer.require(selected, 'missing semantic split')
        for field, expected in [('container_domain_ids', plan['stratification']['container_ids']),
                                ('tags', plan['stratification']['required_case_tags'])]:
            found = {value for case in selected for value in case[field]}
            # Alias identity is a separately scored lookup requirement, not semantic alternatives.
            expected = [value for value in expected if value != 'historical_alias']
            scorer.require(set(expected) <= found, split + ' strata coverage incomplete: ' + field)
    return plan, oracle, attached, cards, cards_by_id, members, registry


def source_hashes():
    result = old.source_hashes()
    for path in ('evals/plugin-v1/run_quality_v2.py', 'evals/plugin-v1/runner-v2-contract.md',
                 'tests/test_plugin_quality_runner_v2.py', 'scripts/build_plugin_search_index.py',
                 'scripts/build_plugin_catalog.py', 'evals/plugin-v1/capture_quality_join_v2.py',
                 'evals/plugin-v1/oracle-v2-protocol.md', 'evals/plugin-v1/build_oracle_v2.py'):
        result[path] = scorer.file_sha256(ROOT / path)
    return result


def declaration(plan, oracle, plan_path, judgments_path):
    return {'schema_version': 'cp04_quality_declaration_v2', 'quality_plan_sha256': scorer.digest(plan),
            'judgments_sha256': scorer.digest(oracle), 'plan_file_sha256': scorer.file_sha256(plan_path),
            'judgments_file_sha256': scorer.file_sha256(judgments_path), 'pins': plan['pins'],
            'source_hashes': source_hashes(), 'thresholds': plan['thresholds'],
            'case_hashes': {case['case_id']: scorer.digest(case) for case in plan['cases']},
            'query_hashes': {case['case_id']: scorer.digest(old.make_query(plan, case)) for case in plan['cases']},
            'split_sha256': scorer.digest([(case['case_id'], case['split'], case['metric_family']) for case in plan['cases']]),
            'thresholds_sha256': scorer.digest(plan['thresholds']),
            'method': {'semantic': 'raw ranks/full universe grade>0 AND non-denied; denied gains zero without rank compaction; unconditional diagnostic retained',
                       'identity': 'separate exact identity success; denied adoption independent',
                       'detail': 'same matcher/pack; eligible-only metrics diagnostic, no substitution',
                       'unknown': 'reject incomplete universe before capture; unjudged returned=null/no_go',
                       'survival': 'grade>0 non-denied raw top12 IDs surviving detail pack/same retrieved IDs',
                       'latency': '30 new-process + 30 same-process, timer retrieve only, nearest-rank; OS cache not flushed',
                       'routes': 'all126 registry routes executed separately; semantic metrics exclude route probes',
                       'synthetic': '4 deterministic copies of actual2500 search rows, distinct positiveIDs; isolated metadata/pins; capacity only'},
            'method_sha256': scorer.digest({'runner': source_hashes()['evals/plugin-v1/run_quality_v2.py'],
                                            'baseline': plan['lexical_baseline'], 'scale': plan['scale_protocol']}),
            'tokens': None, 'provider_cost_usd': None, 'promotion_ready': False,
            'commands': ['.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v2.py ' + flag
                         for flag in ('--predeclare', '--run-development', '--run-held-out --gate <owner-accepted gate.json>',
                                      '--measure-actual', '--route-coverage', '--measure-headroom', '--summarize')]}


def validate_heldout_gate(gate, declared, development_hash):
    scorer.require(gate.get('accepted') is True and isinstance(gate.get('reviewer'), str) and gate['reviewer'],
                   'held-out review acceptance missing')
    scorer.require(gate.get('declaration_sha256') == scorer.digest(declared), 'held-out declaration mismatch')
    scorer.require(gate.get('development_observations_sha256') == development_hash, 'development capture mismatch')
    digest = gate.get('oracle_review_sha256')
    scorer.require(isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest),
                   'oracle review digest missing')


def observe(plan, case, cards, by_id, members, run_id):
    query, result, elapsed = old.execute(plan, case, run_id)
    ids = [row['github_repository_id'] for row in result['candidates']]
    pack = old.context_pack.build_evidence_pack(query, result, {item: by_id[item] for item in ids},
        pack_id='v2-' + case['case_id'], max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
    baseline = old.baseline_ids(plan, case, cards, members)
    baseline_pack = old.baseline_pack(query, baseline, by_id, plan, run_id)
    record = {key: case[key] for key in ('case_id', 'split', 'tags', 'container_domain_ids', 'target_category_id',
                   'metric_family', 'goal_kind', 'universe_ids')}
    record['expected_alias'] = case.get('expected_alias')
    record.update({'case_sha256': scorer.digest(case), 'query_sha256': scorer.digest(query),
                   'retrieval_status': result['status'], 'latency_ms': elapsed,
                   'query_bytes': len(scorer.canonical(query)),
                   'controlled_input_bytes': len(scorer.canonical(query)) + len(scorer.canonical(pack)),
                   'candidate': old.observe_method(ids, pack, case, result['status']),
                   'baseline': old.observe_method(baseline, baseline_pack, case, 'ok' if baseline else 'no_match'),
                   'candidate_identity': identity_observation(ids, pack, case),
                   'baseline_identity': identity_observation(baseline, baseline_pack, case),
                   'candidate_alias_success': None})
    if case.get('expected_alias'):
        record['candidate_alias_success'] = record['candidate_identity']['raw_exact_identity_success']
    for method, detailed in [('candidate', pack), ('baseline', baseline_pack)]:
        record[method]['raw_unconditional_ranking_diagnostic'] = copy.deepcopy(record[method]['ranking'])
        if record[method]['retrieval_status'] in {'ok', 'no_match'}:
            record[method]['ranking'] = constrained_ranking(record[method]['ranked_ids'], case['judgments'], case['k'])
        allowed = [row for row in case['judgments'] if row['constraint'] == 'allowed']
        allowed_ids = {row['github_repository_id'] for row in allowed}
        selected = [row['card']['identity']['github_repository_id'] for row in detailed['cards']]
        # Raw ranks are preserved; this separate diagnostic explicitly evaluates allowed IDs only.
        record[method]['eligible_pack_ranking_diagnostic'] = old.strict_ranking(
            [item for item in selected if item in allowed_ids], allowed, case['k'])
    capture = {'case_id': case['case_id'], 'query': query, 'retrieval': result,
               'candidate_evidence_pack': pack, 'baseline_ranked_ids': baseline,
               'baseline_evidence_pack': baseline_pack,
               'baseline_transport': 'literal adapter; not observed C9 BM25/RRF'}
    return record, capture


def summarize(plan, records, registry, performance=None):
    performance = performance or {key: None for key in ('cold_p95_ms', 'warm_p95_ms', 'peak_memory_bytes', 'index_bytes')}
    semantic_plan = copy.deepcopy(plan)
    semantic_plan['stratification']['required_case_tags'] = [tag for tag in plan['stratification']['required_case_tags']
                                                           if tag != 'historical_alias']
    report = old.summary(semantic_plan, semantic_records(records), performance, registry)
    report['quality_plan_sha256'] = scorer.digest(plan)
    report['historical_alias_stratum'] = 'identity_probe only; exact alias success gate separately enforced'
    report.update({'schema_version': 'cp04_quality_summary_v2', 'record_count': len(records),
                   'semantic_case_count': len(semantic_records(records)),
                   'identity_case_count': len(records) - len(semantic_records(records)),
                   'identity_probes': [{key: row[key] for key in ('case_id', 'candidate_identity', 'baseline_identity')}
                                       for row in records if row['metric_family'] == 'identity'],
                   'oracle': 'full routed universe, agent source-authored; not human accepted'})
    exact_success = [row['candidate_identity']['raw_exact_identity_success'] for row in records
                     if row['metric_family'] == 'identity']
    report['exact_identity_success_rate'] = old.mean(exact_success) if exact_success and all(v is not None for v in exact_success) else None
    alias_success = [row['candidate_identity']['raw_exact_identity_success'] for row in records
                     if 'historical_alias' in row.get('tags', [])]
    alias = old.mean(alias_success) if alias_success and all(v is not None for v in alias_success) else None
    report['alias_success_rate'] = alias
    report['gates']['alias_success_rate_min'] = alias >= plan['thresholds']['alias_success_rate_min'] if alias is not None else None
    report['gates']['identity_adoption_constraints'] = not any(row['candidate_identity']['denied_identity_in_pack'] for row in records)
    report['gates']['complete_expected_cases'] = {row['case_id'] for row in records} == {row['case_id'] for row in plan['cases']}
    report['gates']['all_record_status_matches'] = all(row['retrieval_status'] ==
        next((case.get('expected_status', plan['candidate_route']['expected_status']) for case in plan['cases']
              if case['case_id'] == row['case_id'])) for row in records)
    report['failed_gates'] = [key for key, value in report['gates'].items() if value is False]
    report['unmeasured_gates'] = [key for key, value in report['gates'].items() if value is None]
    report['verdict'] = 'no_go' if report['failed_gates'] or report['unmeasured_gates'] else 'needs_owner_acceptance'
    return report


def capture_split(plan, attached, oracle, declared, cards, by_id, members, registry, split):
    records, captures = [], []
    run_id = str(uuid.uuid4())
    for case in attached['cases']:
        if case['split'] == split or (split == 'development' and case['split'] == 'identity_probe'):
            record, capture = observe(plan, case, cards, by_id, members, run_id)
            records.append(record)
            captures.append(capture)
    observation = {'schema_version': 'cp04_quality_observation_v2', 'split': split, 'run_id': run_id,
                   'evidence_kind': 'observed_offline_public_catalog', 'captured_at': datetime.now(timezone.utc).isoformat(),
                   'declaration_sha256': scorer.digest(declared), 'plan_sha256': scorer.digest(plan),
                   'judgments_sha256': scorer.digest(oracle), 'pins': plan['pins'], 'records': records, 'captures': captures,
                   'promotion_ready': False}
    write_json(split + '-observations.json', observation)
    report = summarize(plan, records, registry)
    report['phase'] = split + '_provisional'
    write_json(split + '-summary.json', report)
    return report


def performance(plan, cases, plan_path, judgments_path, synthetic=False):
    count = plan['scale_protocol']['headroom' if synthetic else 'actual']['repetitions']
    scorer.require(count == 30, 'sample count changed')
    samples = []
    for index in range(count):
        args = [sys.executable, '-B', str(Path(__file__).resolve()), '--sample-case',
                str(index % len(cases)), '--plan', str(plan_path), '--judgments', str(judgments_path)]
        if synthetic:
            args.append('--synthetic-sample')
        proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=60)
        scorer.require(proc.returncode == 0, 'cold sample failed: ' + proc.stdout[:300])
        samples.append(json.loads(proc.stdout))
    old.execute(plan, cases[0], str(uuid.uuid4()))
    warm = []
    for index in range(count):
        case = cases[index % len(cases)]
        _, result, elapsed = old.execute(plan, case, str(uuid.uuid4()))
        warm.append({'case_id': case['case_id'], 'latency_ms': elapsed, 'status': result['status'],
                     'candidate_count': len(result['candidates'])})
    cold_peaks = [item['peak_memory_bytes'] for item in samples if item['peak_memory_bytes'] is not None]
    peak = old.peak_working_set()
    named_cpu = None
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
                named_cpu = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
        except OSError:
            pass
    report = {'cold_samples': samples, 'warm_samples': warm,
              'peak_memory_bytes': max(cold_peaks + ([peak] if peak is not None else []), default=None),
              'memory_method': 'max controller/child GetProcessMemoryInfo process-lifetime peak',
              'python': sys.version, 'sqlite': sqlite3.sqlite_version, 'platform': platform.platform(),
              'processor': platform.processor(), 'named_cpu': named_cpu,
              'os_cache': 'not flushed; prior validation/capture warmed OS cache',
              'index_bytes': (ROOT / plan['artifacts']['index_path']).stat().st_size,
              'tokens': None, 'provider_cost_usd': None, 'synthetic_capacity_only': synthetic,
              'all_sample_statuses_valid': all(row['status'] in {'ok', 'no_match'} for row in samples + warm)}
    for label, data in [('cold', samples), ('warm', warm)]:
        for suffix, fraction in [('p50', .5), ('p95', .95)]:
            report[label + '_' + suffix + '_ms'] = old.percentile([row['latency_ms'] for row in data], fraction)
    prefix = 'synthetic' if synthetic else 'actual'
    report['gates'] = {label + '_p95_ms': report[label + '_p95_ms'] <= plan['thresholds'][prefix + '_' + label + '_p95_ms_max']
                       for label in ('cold', 'warm')}
    for name in ('peak_memory_bytes', 'index_bytes'):
        report['gates'][name] = report[name] <= plan['thresholds'][name + '_max'] if report[name] is not None else None
    report['failed_gates'] = [name for name, value in report['gates'].items() if value is False]
    report['unmeasured_gates'] = [name for name, value in report['gates'].items() if value is None]
    report['verdict'] = 'no_go' if report['failed_gates'] or report['unmeasured_gates'] or not report['all_sample_statuses_valid'] else 'measured_local'
    return report


def route_coverage(plan, attached, registry):
    template = attached['cases'][0]
    records = []
    for route in sorted({row['route_id'] for row in registry}):
        case = {**template, 'case_id': 'route-' + route, 'target_category_id': route,
                'query_terms': ['a'], 'query_locale': 'en'}
        query, result, elapsed = old.execute(plan, case, str(uuid.uuid4()))
        ids = [row['github_repository_id'] for row in result['candidates']]
        records.append({'route_id': route, 'status': result['status'], 'reason_codes': result['reason_codes'],
                        'query_sha256': scorer.digest(query), 'latency_ms': elapsed, 'candidate_count': len(ids),
                        'canonical_ids': ids, 'no_duplicate_ids': len(ids) == len(set(ids)),
                        'bounded': len(ids) <= query['max_candidates']})
    return {'schema_version': 'cp04_runtime_route_coverage_v2', 'semantic_quality': False,
            'expected_routes': len({row['route_id'] for row in registry}), 'records': records,
            'all_passed': all(row['status'] in {'ok', 'no_match'} and row['bounded'] and row['no_duplicate_ids']
                              for row in records), 'pins': plan['pins']}


def synthetic_card(card, replica, synthetic_pins):
    """Copied text is synthetic workload; changed identities cannot claim GitHub facts."""
    result = copy.deepcopy(card)
    repo_id = 10**12 * (replica + 1) + card['identity']['github_repository_id']
    identity = result['identity']
    identity['github_repository_id'] = repo_id
    identity['full_name'] = 'synthetic-headroom/repository-' + str(repo_id)
    identity['url'] = 'https://github.com/' + identity['full_name']
    identity['catalog_record_id'] = 'gh-pending:synthetic-headroom/' + str(repo_id)
    identity['full_name_aliases'] = []
    identity['merged_catalog_record_ids'] = []
    result['corpus_kind'] = 'synthetic_fixture'
    result['provenance']['frozen_pins'].update(synthetic_pins)
    for evidence in result['evidence'] + result['provenance']['sources']:
        evidence['source_kind'] = 'synthetic_fixture'
        evidence['source_ref'] = 'fixture:cp04-v2-headroom/repositories/' + str(repo_id)
    return result


def build_headroom(plan):
    """Build ONLY an isolated synthetic fixture; reuse the source-owned card projection."""
    scorer.require(not HEADROOM.exists(), 'preserve existing synthetic fixture')
    HEADROOM.mkdir(parents=True)
    sys.path.insert(0, str(ROOT / 'scripts'))
    builder = old.load_module('cp04_headroom_projection', ROOT / 'scripts/build_plugin_search_index.py')
    snapshot = scorer._load_json_bounded(ROOT / plan['artifacts']['cards_path'], 16 * 1024 * 1024)
    synthetic_source = scorer.digest({'method': 'four-card-copies/distinct-numeric-ids/v2',
                                     'source_cards_sha256': plan['pins']['cards_sha256']})
    synthetic_pins = {'source_sha256': synthetic_source, 'catalog_snapshot_id': 'synthetic-cp04-v2-' + synthetic_source}
    cards = [synthetic_card(card, replica, synthetic_pins) for replica in range(4) for card in snapshot['cards']]
    expected_count = plan['scale_protocol']['headroom']['row_count']
    scorer.require(len(cards) == expected_count == 10000, 'synthetic row count mismatch')
    rows = sorted([builder.project_card(card) for card in cards], key=lambda row: row['github_repository_id'])
    ids = {row['github_repository_id'] for row in rows}
    scorer.require(len(ids) == expected_count, 'synthetic identity collision')
    snapshot.update(synthetic_pins)
    snapshot.update({'corpus_kind': 'synthetic_fixture', 'cards': cards, 'builder_version': 'cp04-synthetic-headroom-v2'})
    (HEADROOM / 'catalog.snapshot.json').write_bytes(scorer.canonical(snapshot))
    source_index = ROOT / plan['artifacts']['index_path']
    fixture_index = HEADROOM / 'catalog.search.sqlite'
    shutil.copyfile(source_index, fixture_index)
    manifest = copy.deepcopy(scorer.load_json(ROOT / plan['artifacts']['manifest_path']))
    policy_file = HEADROOM / 'retrieval-policy.json'
    shutil.copyfile(ROOT / plan['artifacts']['policy_path'], policy_file)
    pins = manifest['pins']
    pins.update(synthetic_pins)
    pins.update({'cards_sha256': scorer.file_sha256(HEADROOM / 'catalog.snapshot.json'), 'corpus_kind': 'synthetic_fixture'})
    logical_sha = builder.logical_rows_sha256(rows)
    with sqlite3.connect(fixture_index) as connection:
        metadata_cursor = connection.execute('SELECT * FROM bundle_metadata')
        columns = [row[0] for row in metadata_cursor.description]
        metadata = dict(zip(columns, metadata_cursor.fetchone()))
        schema = connection.execute("SELECT sql FROM sqlite_master WHERE name='bundle_metadata'").fetchone()[0]
        scorer.require("row_count = 2500" in schema and "corpus_kind = 'catalog_snapshot'" in schema,
                       'unrecognized fixture metadata schema')
        schema = schema.replace('row_count = 2500', 'row_count = 10000').replace(
            "corpus_kind = 'catalog_snapshot'", "corpus_kind = 'synthetic_fixture'")
        connection.execute('DROP TABLE bundle_metadata')
        connection.execute(schema)
        metadata.update({key: pins[key] for key in ('catalog_snapshot_id', 'source_sha256', 'cards_sha256', 'corpus_kind')})
        metadata.update({'row_count': expected_count, 'logical_rows_sha256': logical_sha})
        connection.execute('INSERT INTO bundle_metadata VALUES (' + ','.join('?' for _ in columns) + ')',
                           [metadata[key] for key in columns])
        connection.execute('DELETE FROM repository_classifications')
        connection.execute('DELETE FROM repository_search_rows')
        connection.executemany('INSERT INTO repository_search_rows VALUES (' + ','.join('?' for _ in range(10)) + ')',
                               [tuple(row[key] for key in ('github_repository_id', *builder.FTS_COLUMNS)) for row in rows])
        connection.executemany('INSERT INTO repository_classifications VALUES (?,?,?,?)',
                               [(card['identity']['github_repository_id'], item['category_id'], item['role'], item['kind'])
                                for card in cards for item in card['classifications']])
        connection.execute("INSERT INTO repository_fts(repository_fts) VALUES ('rebuild')")
        connection.commit()
        connection.execute('VACUUM')
        scorer.require(connection.execute('PRAGMA integrity_check').fetchone() == ('ok',), 'synthetic index integrity failure')
        scorer.require(connection.execute('SELECT count(*) FROM repository_fts').fetchone() == (expected_count,), 'synthetic FTS row mismatch')
    pins['index_sha256'] = scorer.file_sha256(fixture_index)
    manifest.update({'row_count': expected_count, 'logical_rows_sha256': logical_sha})
    (HEADROOM / 'catalog.search-manifest.json').write_bytes(scorer.canonical(manifest))
    synthetic_plan = copy.deepcopy(plan)
    synthetic_plan['pins'] = pins
    synthetic_plan['artifacts'].update({'index_path': str(fixture_index.relative_to(ROOT)).replace('\\', '/'),
        'manifest_path': str((HEADROOM / 'catalog.search-manifest.json').relative_to(ROOT)).replace('\\', '/'),
        'cards_path': str((HEADROOM / 'catalog.snapshot.json').relative_to(ROOT)).replace('\\', '/'),
        'policy_path': str(policy_file.relative_to(ROOT)).replace('\\', '/'), 'catalog_row_count': expected_count})
    synthetic_plan['cases'] = [case for case in synthetic_plan['cases'] if case['split'] == 'development']
    (HEADROOM / 'synthetic-plan.json').write_bytes(scorer.canonical(synthetic_plan))
    return synthetic_plan, {'schema_version': 'cp04_synthetic_headroom_fixture_v2', 'row_count': expected_count,
        'unique_numeric_ids': len(ids), 'pins': pins, 'source_public_cards_sha256': plan['pins']['cards_sha256'],
        'generator_source_sha256': scorer.file_sha256(Path(__file__)),
        'projection_source_sha256': scorer.file_sha256(ROOT / 'scripts/build_plugin_search_index.py'),
        'public_assets_unchanged': scorer.file_sha256(source_index) == plan['pins']['index_sha256'],
        'fixture_path': str(HEADROOM.relative_to(ROOT)), 'relevance_claim_allowed': False,
        'synthetic_plan_sha256': scorer.digest(synthetic_plan),
        'schema_scope': 'RepositoryCardV2 projections; isolated metadata exact row/corpus CHECK substitution only',
        'cards_bytes': (HEADROOM / 'catalog.snapshot.json').stat().st_size, 'index_bytes': fixture_index.stat().st_size}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for flag in ('predeclare', 'run-development', 'run-held-out', 'measure-actual', 'route-coverage', 'measure-headroom', 'summarize'):
        group.add_argument('--' + flag, action='store_true')
    group.add_argument('--sample-case', type=int)
    parser.add_argument('--synthetic-sample', action='store_true')
    parser.add_argument('--plan', type=Path, default=PLAN_PATH)
    parser.add_argument('--judgments', type=Path, default=JUDGMENTS_PATH)
    parser.add_argument('--gate', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.sample_case is not None:
            declared = scorer.load_json(OUTPUT / 'declaration.json')
            scorer.require(source_hashes() == declared['source_hashes'], 'sample source digest mismatch')
            plan = scorer.load_json(HEADROOM / 'synthetic-plan.json' if args.synthetic_sample else args.plan)
            if args.synthetic_sample:
                fixture = scorer.load_json(OUTPUT / 'headroom-fixture.json')
                scorer.require(scorer.digest(plan) == fixture['synthetic_plan_sha256'], 'synthetic sample plan mismatch')
            else:
                scorer.require(scorer.digest(plan) == declared['quality_plan_sha256'], 'sample plan digest mismatch')
            cases = plan['cases'] if args.synthetic_sample else [row for row in plan['cases'] if row['split'] == 'development']
            scorer.require(0 <= args.sample_case < len(cases), 'invalid sample case')
            _, result, elapsed = old.execute(plan, cases[args.sample_case], str(uuid.uuid4()))
            print(json.dumps({'case_id': cases[args.sample_case]['case_id'], 'status': result['status'],
                              'latency_ms': elapsed, 'candidate_count': len(result['candidates']),
                              'peak_memory_bytes': old.peak_working_set()}))
            return 0 if result['status'] in {'ok', 'no_match'} else 1
        plan, oracle, attached, cards, by_id, members, registry = load_protocol(args.plan, args.judgments)
        declared = declaration(plan, oracle, args.plan, args.judgments)
        if args.predeclare:
            write_json('declaration.json', declared)
            print(json.dumps({'declaration_sha256': scorer.digest(declared), 'quality_observed': False}))
            return 0
        stored = scorer.load_json(OUTPUT / 'declaration.json')
        scorer.require(stored == declared, 'predeclared protocol/source digest mismatch')
        if args.run_held_out:
            scorer.require(args.gate is not None, 'held-out owner gate required')
            validate_heldout_gate(scorer.load_json(args.gate), declared,
                                 scorer.file_sha256(OUTPUT / 'development-observations.json'))
        if args.run_development or args.run_held_out:
            split = 'held_out' if args.run_held_out else 'development'
            scorer.require(not (OUTPUT / (split + '-observations.json')).exists(), 'preserve existing capture')
            report = capture_split(plan, attached, oracle, declared, cards, by_id, members, registry, split)
        elif args.route_coverage:
            report = route_coverage(plan, attached, registry)
            write_json('route-coverage.json', report)
        elif args.measure_actual:
            cases = [case for case in attached['cases'] if case['split'] == 'development']
            report = performance(plan, cases, args.plan, args.judgments)
            write_json('performance.json', report)
        elif args.measure_headroom:
            synthetic, fixture = build_headroom(plan)
            write_json('headroom-fixture.json', fixture)
            report = performance(synthetic, synthetic['cases'], args.plan, args.judgments, synthetic=True)
            report['fixture'] = fixture
            write_json('headroom-performance.json', report)
        else:
            all_records = [row for split in ('development', 'held_out') for row in
                           scorer._load_json_bounded(OUTPUT / (split + '-observations.json'), 16 * 1024 * 1024)['records']]
            for split in ('development', 'held_out'):
                observed = scorer._load_json_bounded(OUTPUT / (split + '-observations.json'), 16 * 1024 * 1024)
                scorer.require(observed['declaration_sha256'] == scorer.digest(declared) and
                               observed['plan_sha256'] == scorer.digest(plan) and observed['judgments_sha256'] == scorer.digest(oracle),
                               'capture provenance mismatch')
            report = summarize(plan, all_records, registry, scorer.load_json(OUTPUT / 'performance.json'))
            routes = scorer.load_json(OUTPUT / 'route-coverage.json')
            headroom = scorer.load_json(OUTPUT / 'headroom-performance.json')
            report['gates']['runtime_all_routes'] = routes['all_passed'] and len(routes['records']) == len(members)
            report['all_leaf_container_runtime_routes'] = 'observed separately; no semantic quality claim'
            report['synthetic_10k_headroom'] = headroom['verdict']
            for name, value in headroom['gates'].items():
                report['gates']['headroom_' + name] = value
            report['failed_gates'] = [key for key, value in report['gates'].items() if value is False]
            report['unmeasured_gates'] = [key for key, value in report['gates'].items() if value is None]
            report['verdict'] = 'no_go' if report['failed_gates'] or report['unmeasured_gates'] else 'needs_owner_acceptance'
            write_json('summary.json', report)
            hashes = {path.name: scorer.file_sha256(path) for path in OUTPUT.glob('*.json')}
            write_json('runner-artifact-hashes.json', hashes)
        print(json.dumps({'verdict': report.get('verdict', 'measured_local'), 'promotion_ready': False,
                          'failed_gates': report.get('failed_gates', []), 'record_count': report.get('record_count')}))
        return 1 if report.get('verdict') == 'no_go' or report.get('all_passed') is False or report.get('all_sample_statuses_valid') is False else 0
    except (OSError, ValueError, KeyError, TypeError, IndexError, sqlite3.DatabaseError, subprocess.SubprocessError) as error:
        print(json.dumps({'verdict': 'invalid_input_or_unavailable_check', 'error_type': type(error).__name__,
                          'reason': str(error), 'promotion_ready': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
