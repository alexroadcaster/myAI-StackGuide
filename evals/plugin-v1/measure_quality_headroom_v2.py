"""Isolated synthetic10000 capacity through existing native query primitives only."""
import importlib.util
import argparse
import json
import platform
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('cp04_headroom_runner', ROOT / 'evals/plugin-v1/run_quality_v2.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def fixture_path(path):
    resolved = (ROOT / path).resolve()
    runner.scorer.require(resolved.is_relative_to(runner.HEADROOM), 'isolated fixture path required')
    return resolved


def bounds_pass(ids, limit):
    return len(ids) <= limit and len(ids) == len(set(ids))


def evidence_ceiling():
    return {'measured_layer': 'isolated manifest/policy/bundle validation + native compiler + bounded FTS5 SQL',
            'production_reader_accepted': False, 'full_card_pack_capacity_measured': False,
            'relevance_claim_allowed': False, 'c8_capture': False, 'promotion_ready': False,
            'production_entry_point': 'retained index_incompatible; hard trusted manifest remains enforced'}


def declaration(plan):
    sources = runner.source_hashes()
    for path in ('evals/plugin-v1/measure_quality_headroom_v2.py', 'tests/test_plugin_quality_headroom_v2.py'):
        sources[path] = runner.scorer.file_sha256(ROOT / path)
    artifacts = {path: runner.scorer.file_sha256(fixture_path(path)) for path in
                 (plan['artifacts'][key] for key in ('index_path', 'manifest_path', 'policy_path', 'cards_path'))}
    return {'schema_version': 'cp04_headroom_adapter_declaration_v2', 'source_hashes': sources,
            'fixture_hashes': artifacts, 'plan_sha256': runner.scorer.digest(plan),
            'original_headroom_failure_sha256': runner.scorer.file_sha256(runner.OUTPUT / 'headroom-failure.json'),
            'queries': [runner.old.make_query(plan, case) for case in plan['cases']],
            'thresholds': plan['thresholds'], 'samples': {'cold': 30, 'warm': 30},
            'timing': 'perf_counter_ns includes immutable connection, metadata validation, physical index hash, native compile and bounded SQL; excludes fixture card-file hash and process/import startup',
            'cold': 'new process/connection each; OS cache not flushed',
            'warm': 'same process; new connection each sample; one discarded warmup',
            'memory': 'max controller/child process-lifetime PeakWorkingSetSize; includes card file hash reads, no full card JSON parsing',
            'bytes': 'exact query and SQL sample result JSON; no detailed pack or model context',
            'tokens': None, 'provider_cost_usd': None, **evidence_ceiling(),
            'commands': ['.venv/Scripts/python.exe -B evals/plugin-v1/measure_quality_headroom_v2.py --predeclare',
                         '.venv/Scripts/python.exe -B evals/plugin-v1/measure_quality_headroom_v2.py --run']}


def sample(plan, case):
    """Existing SQL compiler/executor, without production manifest entry-point replacement."""
    query = runner.old.make_query(plan, case)
    manifest = runner.scorer.load_json(fixture_path(plan['artifacts']['manifest_path']))
    policy = runner.scorer.load_json(fixture_path(plan['artifacts']['policy_path']))
    index_path = fixture_path(plan['artifacts']['index_path'])
    begin = time.perf_counter_ns()
    runner.old.retrieval._validate_manifest_policy(manifest, policy)
    runner.old.retrieval.validate_query(query, manifest=manifest, policy=policy)
    runner.scorer.require(len(query['variants']) == 1, 'adapter supports the declared single OR variant only')
    with sqlite3.connect(index_path.as_uri() + '?mode=ro&immutable=1', uri=True) as connection:
        runner.old.retrieval._validate_bundle(connection, manifest, policy)
        runner.scorer.require(runner.scorer.file_sha256(index_path) == manifest['pins']['index_sha256'], 'fixture index digest mismatch')
        connection.row_factory = sqlite3.Row
        compiled = runner.old.retrieval.compile_fts5_query(query['variants'][0]['terms'], aliases=policy['aliases'])
        rows = runner.old.retrieval._execute_variant(connection, compiled, query['taxonomy_route_id'], query['max_candidates'])
        ids = [row['github_repository_id'] for row in rows]
    elapsed = (time.perf_counter_ns() - begin) / 1_000_000
    runner.scorer.require(bounds_pass(ids, query['max_candidates']), 'synthetic SQL bounds or dedupe failed')
    report = {'case_id': case['case_id'], 'query_sha256': runner.scorer.digest(query), 'query_bytes': len(runner.scorer.canonical(query)),
              'status': 'ok' if ids else 'no_match', 'latency_ms': elapsed, 'canonical_ids': ids,
              'candidate_count': len(ids), 'peak_memory_bytes': runner.old.peak_working_set(),
              'bounded': True, 'index_row_count': manifest['row_count']}
    report['serialized_result_bytes'] = len(runner.scorer.canonical(report))
    return report


def measure(plan):
    cold, warm = [], []
    for index in range(30):
        proc = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--sample-case', str(index % len(plan['cases']))],
                              cwd=ROOT, capture_output=True, text=True, timeout=60)
        runner.scorer.require(proc.returncode == 0, 'adapter cold sample failed: ' + proc.stdout[:250])
        cold.append(json.loads(proc.stdout))
    sample(plan, plan['cases'][0])
    for index in range(30):
        warm.append(sample(plan, plan['cases'][index % len(plan['cases'])]))
    report = {'schema_version': 'cp04_headroom_adapter_performance_v2', **evidence_ceiling(),
              'cold_samples': cold, 'warm_samples': warm,
              'peak_memory_bytes': max([item['peak_memory_bytes'] for item in cold + warm if item['peak_memory_bytes'] is not None], default=None),
              'index_bytes': fixture_path(plan['artifacts']['index_path']).stat().st_size,
              'synthetic_cards_file_bytes': fixture_path(plan['artifacts']['cards_path']).stat().st_size,
              'os_cache': 'not flushed; fixture construction and validation warmed cache',
              'python': sys.version, 'sqlite': sqlite3.sqlite_version, 'platform': platform.platform(),
              'named_cpu': runner.scorer.load_json(runner.OUTPUT / 'performance.json')['named_cpu'],
              'tokens': None, 'provider_cost_usd': None, 'row_count': 10000}
    for name, data in [('cold', cold), ('warm', warm)]:
        for suffix, fraction in [('p50', .5), ('p95', .95)]:
            report[name + '_' + suffix + '_ms'] = runner.old.percentile([row['latency_ms'] for row in data], fraction)
    report['gates'] = {name + '_p95_ms': report[name + '_p95_ms'] <= plan['thresholds']['synthetic_' + name + '_p95_ms_max']
                       for name in ('cold', 'warm')}
    for name in ('peak_memory_bytes', 'index_bytes'):
        report['gates'][name] = report[name] <= plan['thresholds'][name + '_max'] if report[name] is not None else None
    report['verdict'] = 'measured_fixture_sql_layer' if all(value is True for value in report['gates'].values()) else 'no_go'
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--predeclare', action='store_true')
    group.add_argument('--run', action='store_true')
    group.add_argument('--sample-case', type=int)
    args = parser.parse_args(argv)
    try:
        plan = runner.scorer.load_json(runner.HEADROOM / 'synthetic-plan.json')
        declared = declaration(plan)
        if args.predeclare:
            runner.write_json('headroom-adapter-declaration.json', declared)
            print(json.dumps({'declaration_sha256': runner.scorer.digest(declared), **evidence_ceiling()}))
            return 0
        runner.scorer.require(runner.scorer.load_json(runner.OUTPUT / 'headroom-adapter-declaration.json') == declared,
                              'predeclared adapter source/fixture mismatch')
        if args.sample_case is not None:
            runner.scorer.require(0 <= args.sample_case < len(plan['cases']), 'invalid sample case')
            print(json.dumps(sample(plan, plan['cases'][args.sample_case])))
            return 0
        result = measure(plan)
        result['declaration_sha256'] = runner.scorer.digest(declared)
        runner.write_json('headroom-adapter-performance.json', result)
        print(json.dumps({'verdict': result['verdict'], 'cold_p95_ms': result['cold_p95_ms'],
                          'warm_p95_ms': result['warm_p95_ms'], **evidence_ceiling()}))
        return 1 if result['verdict'] == 'no_go' else 0
    except (OSError, ValueError, KeyError, sqlite3.DatabaseError, subprocess.SubprocessError) as error:
        print(json.dumps({'verdict': 'invalid_input_or_unavailable_check', 'reason': str(error), **evidence_ceiling()}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
