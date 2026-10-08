"""Isolated headroom experiment after digest-bound validation-cache change."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08'
spec = importlib.util.spec_from_file_location('cached_headroom_adapter', ROOT / 'evals/plugin-v1/measure_quality_headroom_v2.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
s = a.runner.scorer
r = a.runner.old.retrieval


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open('xb') as f:
        f.write(s.canonical(value))


def declaration():
    plan = s.load_json(a.runner.HEADROOM / 'synthetic-plan.json')
    frozen = s.load_json(a.runner.OUTPUT / 'headroom-adapter-declaration.json')
    fixture = {path: s.file_sha256(a.fixture_path(path)) for path in frozen['fixture_hashes']}
    s.require(fixture == frozen['fixture_hashes'], 'frozen fixture changed')
    sources = {path: s.file_sha256(ROOT / path) for path in (
        'evals/plugin-v1/measure_cached_headroom_v3.py',
        'plugins/myai-stackguide/scripts/retrieval.py',
        'tests/test_plugin_retrieval_validation_cache.py')}
    return plan, {'schema_version': 'cp04_cached_headroom_declaration_v1', 'sources': sources,
        'fixture_hashes': fixture, 'thresholds': plan['thresholds'],
        'queries': [a.runner.old.make_query(plan, case) for case in plan['cases']],
        'samples': {'cold': 30, 'warm': 30},
        'method': 'same v2 adapter operation scope: validation + connection + exact index hash + native compiler/SQL; successful bundle validation cached, hash performed every call; fixture load outside timer',
        'cold': 'new process and connection, full first validation; OS cache not flushed',
        'warm': 'same process, new connection each sample, one discarded warmup',
        'memory': 'process-lifetime peak, no full card parsing; not isolated SQLite allocation',
        'production_reader_accepted': False, 'full_card_pack_capacity_measured': False,
        'relevance_claim_allowed': False, 'promotion_ready': False,
        'command': '.venv/Scripts/python.exe -B evals/plugin-v1/measure_cached_headroom_v3.py --run'}


def sample(plan, number):
    case = plan['cases'][number % len(plan['cases'])]
    query = a.runner.old.make_query(plan, case)
    manifest = s.load_json(a.fixture_path(plan['artifacts']['manifest_path']))
    policy = s.load_json(a.fixture_path(plan['artifacts']['policy_path']))
    index = a.fixture_path(plan['artifacts']['index_path'])
    start = time.perf_counter_ns()
    r.validate_query(query, manifest=manifest, policy=policy)
    s.require(len(query['variants']) == 1, 'single declared variant only')
    with sqlite3.connect(index.as_uri() + '?mode=ro&immutable=1', uri=True) as c:
        r._validate_bundle_cached(c, manifest, policy, index)
        c.row_factory = sqlite3.Row
        compiled = r.compile_fts5_query(query['variants'][0]['terms'], aliases=policy['aliases'])
        rows = r._execute_variant(c, compiled, query['taxonomy_route_id'], query['max_candidates'])
        ids = [row['github_repository_id'] for row in rows]
    c.close()
    elapsed = (time.perf_counter_ns() - start)/1_000_000
    s.require(a.bounds_pass(ids, query['max_candidates']), 'bounds failed')
    return {'case_id': case['case_id'], 'latency_ms': elapsed, 'canonical_ids': ids,
            'bounded': True, 'peak_memory_bytes': a.runner.old.peak_working_set()}


def measure(plan):
    cold = []
    for i in range(30):
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--sample', str(i)],
                                cwd=ROOT, capture_output=True, text=True, timeout=60)
        s.require(result.returncode == 0, 'child sample failed')
        cold.append(json.loads(result.stdout))
    sample(plan, 0)
    warm = [sample(plan, i) for i in range(30)]
    p95 = lambda values: sorted(v['latency_ms'] for v in values)[math.ceil(.95*len(values))-1]
    cold95, warm95 = p95(cold), p95(warm)
    thresholds = plan['thresholds']
    peak = max(row['peak_memory_bytes'] for row in cold + warm)
    index_bytes = a.fixture_path(plan['artifacts']['index_path']).stat().st_size
    gates = {'cold_p95': cold95 <= thresholds['synthetic_cold_p95_ms_max'],
             'warm_p95': warm95 <= thresholds['synthetic_warm_p95_ms_max'],
             'memory': peak <= thresholds['peak_memory_bytes_max'],
             'index_bytes': index_bytes <= thresholds['index_bytes_max']}
    return {'schema_version': 'cp04_cached_headroom_result_v1', 'cold': cold, 'warm': warm,
            'cold_p95_ms': cold95, 'warm_p95_ms': warm95, 'peak_memory_bytes': peak,
            'index_bytes': index_bytes, 'gates': gates,
            'verdict': 'adapter_capacity_pass_only' if all(gates.values()) else 'no_go',
            'production_reader_accepted': False, 'full_card_pack_capacity_measured': False,
            'promotion_ready': False, 'tokens': None, 'provider_cost_usd': None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--predeclare', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--sample', type=int)
    args = parser.parse_args()
    s.require(sum((args.predeclare, args.run, args.sample is not None)) == 1, 'select one mode')
    if args.sample is not None:
        print(json.dumps(sample(s.load_json(a.runner.HEADROOM / 'synthetic-plan.json'), args.sample)))
    else:
        plan, declared = declaration()
        if args.predeclare:
            write('cached-headroom-declaration.json', declared)
        else:
            s.require(s.load_json(OUT / 'cached-headroom-declaration.json') == declared, 'declaration mismatch')
            result = measure(plan)
            result['declaration_sha256'] = s.file_sha256(OUT / 'cached-headroom-declaration.json')
            write('cached-headroom-performance.json', result)
            print(json.dumps({key: result[key] for key in ('cold_p95_ms','warm_p95_ms','gates','verdict')}))
            sys.exit(0 if all(result['gates'].values()) else 1)
