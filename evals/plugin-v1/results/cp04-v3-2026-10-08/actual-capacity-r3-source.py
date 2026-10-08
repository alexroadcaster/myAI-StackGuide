"""Pinned production 2500-card retrieval plus separately timed evidence pack."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08'
spec = importlib.util.spec_from_file_location('actual_quality_v3_helpers', ROOT / 'evals/plugin-v1/run_quality_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
s = v2.scorer
old = v2.old


def write(name, value):
    with (OUT / name).open('xb') as f:
        f.write(s.canonical(value))


def declaration():
    plan = s.load_json(v2.PLAN_PATH)
    expected_assets = {key: 'plugins/myai-stackguide/assets/' + name for key, name in (
        ('cards_path', 'catalog.snapshot.json'), ('index_path', 'catalog.search.sqlite'),
        ('manifest_path', 'catalog.search-manifest.json'), ('policy_path', 'retrieval-policy.json'))}
    s.require(all(plan['artifacts'][key] == path for key, path in expected_assets.items()), 'bundled paths required')
    cases = [c for c in plan['cases'] if c['split'] == 'development' and c['metric_family'] == 'semantic']
    s.require(len(cases) == 10, 'ten development cases required')
    manifest = s.load_json(ROOT / plan['artifacts']['manifest_path'])
    s.require(s.file_sha256(ROOT / plan['artifacts']['manifest_path']) == plan['artifacts']['manifest_sha256'], 'manifest mismatch')
    for key, pin in [('cards_path', 'cards_sha256'), ('index_path', 'index_sha256'), ('policy_path', 'policy_sha256')]:
        s.require(s.file_sha256(ROOT / plan['artifacts'][key]) == manifest['pins'][pin], 'public artifact mismatch')
    sources = v2.source_hashes()
    sources['evals/plugin-v1/measure_actual_quality_v3.py'] = s.file_sha256(Path(__file__).resolve())
    return plan, cases, {'schema_version': 'cp04_actual_capacity_declaration_v3', 'sources': sources,
        'pins': manifest['pins'], 'queries': [old.make_query(plan, c) for c in cases],
        'thresholds': plan['thresholds'], 'samples': {'cold': 30, 'warm': 30},
        'method': 'Production retrieve timer only, including trust/index checks; evidence-pack construction separately timed. Source map loading and process/import startup outside timers. Whole-process peak memory includes source-map and pack parsing. No OS cache flush.',
        'cold': 'new child process and connection per sample; exact declaration checked before timing',
        'warm': 'one process/new immutable connection per retrieval; one discarded warmup',
        'command': '.venv/Scripts/python.exe -B evals/plugin-v1/measure_actual_quality_v3.py --run',
        'relevance_claim_allowed': False, 'promotion_ready': False}


def sample(plan, cases, number, by_id):
    query = old.make_query(plan, cases[number % len(cases)])
    start = time.perf_counter_ns()
    result = old.retrieval.retrieve(query, run_id='00000000-0000-4000-8000-000000000004',
        index_path=ROOT / plan['artifacts']['index_path'], manifest_path=ROOT / plan['artifacts']['manifest_path'],
        policy_path=ROOT / plan['artifacts']['policy_path'])
    retrieval_ms = (time.perf_counter_ns() - start)/1_000_000
    s.require(result['status'] in ('ok', 'no_match'), 'retrieval failure')
    start = time.perf_counter_ns()
    pack = old.context_pack.build_evidence_pack(query, result, by_id,
        pack_id='00000000-0000-4000-8000-000000000005', max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
    pack_ms = (time.perf_counter_ns() - start)/1_000_000
    s.require(pack['status'] in ('ready', 'no_match'), 'pack failure')
    return {'case_id': cases[number % len(cases)]['case_id'], 'retrieval_ms': retrieval_ms,
        'pack_ms': pack_ms, 'query_bytes': len(s.canonical(query)), 'pack_bytes': len(s.canonical(pack)),
        'peak_memory_bytes': old.peak_working_set(), 'status': result['status'],
        'candidate_count': len(result['candidates'])}


def cards(plan):
    snapshot = s._load_json_bounded(ROOT / plan['artifacts']['cards_path'], old.context_pack.MAX_SNAPSHOT_BYTES)
    return {c['identity']['github_repository_id']: c for c in snapshot['cards']}


def measure(plan, cases):
    cold = []
    for i in range(30):
        child = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--sample', str(i)],
                               cwd=ROOT, capture_output=True, text=True, timeout=60)
        s.require(child.returncode == 0, 'child sample failed')
        cold.append(json.loads(child.stdout))
    by_id = cards(plan)
    sample(plan, cases, 0, by_id)
    warm = [sample(plan, cases, i, by_id) for i in range(30)]
    percentile = lambda data, key: sorted(c[key] for c in data)[math.ceil(.95*len(data))-1]
    cp95, wp95 = percentile(cold, 'retrieval_ms'), percentile(warm, 'retrieval_ms')
    peak = max(c['peak_memory_bytes'] for c in cold + warm)
    largest = max(c['query_bytes'] + c['pack_bytes'] for c in cold + warm)
    limits = plan['thresholds']
    policy = s.load_json(ROOT / plan['artifacts']['policy_path'])
    gates = {'cold_p95': cp95 <= limits['actual_cold_p95_ms_max'],
             'warm_p95': wp95 <= limits['actual_warm_p95_ms_max'],
             'memory': peak <= limits['peak_memory_bytes_max'],
             'controlled_input': largest <= policy['limits']['max_plugin_input_bytes'],
             'pack_bytes': max(c['pack_bytes'] for c in cold + warm) <= plan['candidate_route']['max_evidence_bytes']}
    return {'schema_version': 'cp04_actual_capacity_result_v3', 'cold': cold, 'warm': warm,
        'cold_p95_ms': cp95, 'warm_p95_ms': wp95, 'cold_pack_p95_ms': percentile(cold, 'pack_ms'),
        'warm_pack_p95_ms': percentile(warm, 'pack_ms'), 'peak_memory_bytes': peak,
        'max_controlled_input_bytes': largest, 'gates': gates,
        'python': platform.python_version(), 'os': platform.platform(), 'sqlite': old.retrieval.sqlite3.sqlite_version,
        'verdict': 'production_retrieval_pack_capacity_only' if all(gates.values()) else 'no_go',
        'relevance_claim_allowed': False, 'promotion_ready': False, 'tokens': None, 'provider_cost_usd': None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--predeclare', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--sample', type=int)
    args = parser.parse_args()
    s.require(sum((args.predeclare, args.run, args.sample is not None)) == 1, 'select one mode')
    plan, cases, declared = declaration()
    if args.predeclare:
        write('actual-capacity-r3-declaration.json', declared)
    else:
        s.require(s.load_json(OUT / 'actual-capacity-r3-declaration.json') == declared, 'declaration mismatch')
        if args.sample is not None:
            print(json.dumps(sample(plan, cases, args.sample, cards(plan))))
        else:
            result = measure(plan, cases)
            result['declaration_sha256'] = s.file_sha256(OUT / 'actual-capacity-r3-declaration.json')
            write('actual-capacity-r3-performance.json', result)
            print(json.dumps({k: result[k] for k in ('cold_p95_ms', 'warm_p95_ms', 'gates', 'verdict')}))
            sys.exit(0 if all(result['gates'].values()) else 1)
