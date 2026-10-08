"""One predeclared baseline decomposition; diagnostic, not an acceptance retry."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sqlite3
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08'
spec = importlib.util.spec_from_file_location('cp04_latency_adapter', ROOT / 'evals/plugin-v1/measure_quality_headroom_v2.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
runner = adapter.runner
r = runner.old.retrieval


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open('xb') as stream:
        stream.write(runner.scorer.canonical(value))


def declared():
    plan = runner.scorer.load_json(runner.HEADROOM / 'synthetic-plan.json')
    old = runner.scorer.load_json(runner.OUTPUT / 'headroom-adapter-declaration.json')
    artifacts = {path: runner.scorer.file_sha256(adapter.fixture_path(path))
                 for path in old['fixture_hashes']}
    assert artifacts == old['fixture_hashes'], 'original fixture mismatch'
    return plan, {
        'schema_version': 'cp04_latency_decomposition_declaration_v1',
        'source_hashes': {str(path.relative_to(ROOT)).replace('\\', '/'): runner.scorer.file_sha256(path)
                          for path in (Path(__file__).resolve(), ROOT / 'plugins/myai-stackguide/scripts/retrieval.py')},
        'fixture_hashes': artifacts,
        'queries': [runner.old.make_query(plan, case) for case in plan['cases']],
        'samples': len(plan['cases']),
        'method': 'one sequential sample per development query; connection+checks/hash/compiler/SQL timed separately; no warm/cold p95 acceptance claim; OS cache not flushed',
        'production_reader_accepted': False,
        'full_card_pack_capacity_measured': False,
        'promotion_ready': False,
        'command': '.venv/Scripts/python.exe -B evals/plugin-v1/diagnose_quality_latency_v3.py --run',
    }


def run(plan):
    index = adapter.fixture_path(plan['artifacts']['index_path'])
    manifest = runner.scorer.load_json(adapter.fixture_path(plan['artifacts']['manifest_path']))
    policy = runner.scorer.load_json(adapter.fixture_path(plan['artifacts']['policy_path']))
    observations = []
    for case in plan['cases']:
        query = runner.old.make_query(plan, case)
        timings = {}
        def timed(name, operation):
            started = time.perf_counter_ns()
            value = operation()
            timings[name] = (time.perf_counter_ns() - started) / 1_000_000
            return value
        connection = timed('connection_ms', lambda: sqlite3.connect(index.as_uri() + '?mode=ro&immutable=1', uri=True))
        try:
            timed('query_validation_ms', lambda: r.validate_query(query, manifest=manifest, policy=policy))
            timed('full_bundle_validation_ms', lambda: r._validate_bundle(connection, manifest, policy))
            digest = timed('index_hash_ms', lambda: runner.scorer.file_sha256(index))
            assert digest == manifest['pins']['index_sha256'], 'index mismatch'
            connection.row_factory = sqlite3.Row
            compiled = timed('compiler_ms', lambda: r.compile_fts5_query(query['variants'][0]['terms'], aliases=policy['aliases']))
            rows = timed('sql_ms', lambda: r._execute_variant(connection, compiled, query['taxonomy_route_id'], query['max_candidates']))
            ids = [row['github_repository_id'] for row in rows]
            assert adapter.bounds_pass(ids, query['max_candidates'])
            observations.append({'case_id': case['case_id'], 'candidate_count': len(ids), **timings})
        finally:
            connection.close()
    return {'schema_version': 'cp04_latency_decomposition_result_v1', 'observations': observations,
            'mean_ms': {key: sum(row[key] for row in observations)/len(observations) for key in timings},
            'python': platform.python_version(), 'sqlite': sqlite3.sqlite_version,
            'evidence_ceiling': 'diagnostic_operation_cost_only', 'promotion_ready': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--predeclare', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    assert args.predeclare != args.run, 'select one mode'
    plan, declaration = declared()
    if args.predeclare:
        write('latency-decomposition-declaration.json', declaration)
    else:
        assert runner.scorer.load_json(OUT / 'latency-decomposition-declaration.json') == declaration
        result = run(plan)
        result['declaration_sha256'] = runner.scorer.file_sha256(OUT / 'latency-decomposition-declaration.json')
        write('latency-decomposition.json', result)
        print(json.dumps(result['mean_ms']))
