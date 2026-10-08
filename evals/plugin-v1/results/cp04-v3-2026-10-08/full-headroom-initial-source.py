"""Full synthetic reader/card/pack capacity under an exact isolated trust anchor."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08/full-headroom'
FIXTURE = ROOT / '.codex-tmp/cp04-v2-headroom'
TRUST = 'evals/plugin-v1/results/cp04-v2-2026-10-08/headroom-fixture.json'
OLD_DECLARATION = 'evals/plugin-v1/results/cp04-v2-2026-10-08/headroom-adapter-declaration.json'
# The versioned evidence anchors are checked before accepting their declarations.
TRUST_HASHES = {
    TRUST: 'b9a7f941640a031c6dd7c351d2106955c9c6607014eb8638852764af3acf5293',
    OLD_DECLARATION: 'd6bf32a610fdf873ef98803142fa17c8ed841bd8f415bd78f0d2440cf7a9e622',
}
FIXTURE_NAMES = ('catalog.search-manifest.json', 'catalog.search.sqlite',
                 'catalog.snapshot.json', 'retrieval-policy.json')
RUN_ID = '4ecf43c4-3214-46a0-8d4d-e4f734bddcd0'
SOURCE_PATHS = (
    'evals/plugin-v1/measure_full_headroom_v3.py',
    'evals/plugin-v1/full-headroom-v3-contract.md',
    'tests/test_plugin_full_headroom_v3.py',
    'tests/test_plugin_shared_reader_core.py',
    'tests/test_plugin_retrieval_validation_cache.py',
    'tests/test_plugin_retrieval.py',
    'plugins/myai-stackguide/scripts/retrieval.py',
    'plugins/myai-stackguide/scripts/context_pack.py',
    'plugins/myai-stackguide/scripts/matcher.py',
    'plugins/myai-stackguide/assets/catalog.search-manifest.json',
    'plugins/myai-stackguide/assets/catalog.snapshot.json',
    'plugins/myai-stackguide/assets/catalog.search.sqlite',
    'plugins/myai-stackguide/assets/retrieval-policy.json',
    'tests/fixtures/plugin_retrieval_eval.json',
    'tests/fixtures/plugin_contracts.json',
    TRUST, OLD_DECLARATION,
)


def load_module(name):
    path = ROOT / f'plugins/myai-stackguide/scripts/{name}.py'
    spec = importlib.util.spec_from_file_location(f'full_headroom_{name}', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LOADED_RUNTIME_HASHES = {
    path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    for path in SOURCE_PATHS if path.startswith('plugins/myai-stackguide/scripts/')
}
retrieval = load_module('retrieval')
packs = load_module('context_pack')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(',', ':')).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha256(path):
    hashed = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hashed.update(block)
    return hashed.hexdigest()


def parse_json(raw):
    return json.loads(raw.decode('utf-8'),
                      parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))


def verified_bytes(path, expected_path, expected_hash, expected_bytes):
    """Private byte primitive; entry points supply only frozen fixed anchors."""
    require(Path(path).resolve() == Path(expected_path).resolve(), 'fixed fixture path mismatch')
    require(Path(path).stat().st_size == expected_bytes, 'fixture byte count mismatch')
    raw = Path(path).read_bytes()
    require(len(raw) == expected_bytes and hashlib.sha256(raw).hexdigest() == expected_hash,
            'fixture hash mismatch')
    return raw


def normalize_cards(snapshot, pins, count):
    trusted = packs._cards_from_verified_snapshot(snapshot, pins, expected_count=count)
    require(all(card.get('schema_version') == pins['card_schema_version']
                and card.get('corpus_kind') == pins['corpus_kind']
                for card in trusted.values()), 'card schema/corpus mismatch')
    return trusted


def elapsed_ms(start_ns, end_ns):
    return (end_ns - start_ns) / 1_000_000


def percentile(values, fraction):
    require(bool(values) and 0 < fraction <= 1, 'invalid percentile inputs')
    return sorted(values)[math.ceil(len(values) * fraction) - 1]


def validate_capture(query, result, pack):
    """Guard complete candidate accounting and unchanged native ranking fields."""
    candidates = result['candidates']
    ids = packs._retrieval_candidate_ids(candidates)
    require(len(ids) == len(set(ids)), 'duplicate candidate identity')
    require(len(candidates) <= result['retrieved_hits'] <= query['max_candidates'], 'hit budget exceeded')
    require(result['executed_variants'] == len(query['variants']), 'variant execution incomplete')
    require(len(pack['cards']) <= query['max_cards'], 'card budget exceeded')
    require(len(canonical(pack)) <= query['max_evidence_bytes'], 'evidence bytes exceeded')
    require(len(canonical(query)) + len(canonical(pack)) <= packs.MAX_PLUGIN_INPUT_BYTES,
            'total controlled input bytes exceeded')
    packed = [item['card']['identity']['github_repository_id'] for item in pack['cards']]
    excluded = [item['github_repository_id'] for item in pack['exclusions']]
    require(len(packed) == len(set(packed)) and len(excluded) == len(set(excluded))
            and not set(packed) & set(excluded) and set(packed) | set(excluded) == set(ids),
            'candidate coverage failed')
    by_id = {item['github_repository_id']: item for item in candidates}
    for item in pack['cards']:
        original = by_id[item['card']['identity']['github_repository_id']]
        require(item['retrieval_rank'] == original['rank']
                and item['rrf_score'] == original['rrf_score']
                and item['matched_fields'] == original['matched_fields'], 'raw rank fidelity failed')
    require(all(item['reason_codes'] for item in pack['exclusions']), 'exclusion reason missing')
    return {'candidate_coverage': True, 'raw_rank_fidelity': True,
            'hit_budget': True, 'card_budget': True, 'evidence_bytes': True,
            'total_controlled_input_bytes': True, 'unique_positive_ids': True,
            'complete_variants': True}


def peak_working_set():
    require(sys.platform == 'win32', 'declared Windows memory method unavailable')
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
            'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
            'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    require(bool(psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb)),
            'memory counter unavailable')
    return counters.PeakWorkingSetSize


def environment():
    cpu = platform.processor()
    if sys.platform == 'win32':
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            cpu = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
    require(bool(cpu), 'named CPU unavailable')
    return {'named_cpu': cpu, 'platform': platform.platform(), 'python': sys.version,
            'python_executable': str(Path(sys.executable).resolve()), 'sqlite': sqlite3.sqlite_version,
            'machine': platform.machine() or None, 'python_pointer_bits': ctypes.sizeof(ctypes.c_void_p) * 8,
            'logical_cpu_count': __import__('os').cpu_count()}


def frozen_fixture():
    require(FIXTURE.resolve().is_relative_to(ROOT.resolve()), 'fixture root escapes workspace')
    anchors = {}
    for path, expected_hash in TRUST_HASHES.items():
        raw = (ROOT / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected_hash, 'versioned fixture anchor changed')
        anchors[path] = parse_json(raw)
    trust, old = anchors[TRUST], anchors[OLD_DECLARATION]
    fixed = {f'.codex-tmp/cp04-v2-headroom/{name}' for name in FIXTURE_NAMES}
    require(set(old['fixture_hashes']) == fixed, 'unexpected fixture paths')
    require(all((ROOT / path).resolve().parent == FIXTURE.resolve() for path in fixed),
            'fixture file escapes fixed root')
    require(trust['row_count'] == trust['unique_numeric_ids'] == 10000,
            'exact 10000 identity count required')
    require(trust['cards_bytes'] == 54378585 and trust['index_bytes'] == 8474624,
            'versioned expected bytes changed')
    require(trust['pins']['corpus_kind'] == 'synthetic_fixture', 'synthetic corpus required')
    require(Path(trust['fixture_path']).as_posix().replace('\\', '/') == '.codex-tmp/cp04-v2-headroom',
            'fixed fixture root mismatch')
    return trust, old


def declaration():
    require(all(file_sha256(ROOT / path) == expected for path, expected in LOADED_RUNTIME_HASHES.items()),
            'loaded runtime differs from declared sources')
    trust, old = frozen_fixture()
    plan_path = FIXTURE / 'synthetic-plan.json'
    plan_raw = plan_path.read_bytes()
    require(hashlib.sha256(plan_raw).hexdigest() == trust['synthetic_plan_sha256'], 'synthetic plan hash mismatch')
    plan = parse_json(plan_raw)
    require(plan['pins'] == trust['pins'], 'plan pins mismatch')
    require(len(plan['cases']) == 10 and all(case['split'] == 'development' for case in plan['cases']),
            'frozen ten development cases required')
    hashes = {path: file_sha256(ROOT / path) for path in old['fixture_hashes']}
    require(hashes == old['fixture_hashes'], 'exact fixture hashes mismatch')
    sizes = {path: (ROOT / path).stat().st_size for path in hashes}
    require(sizes['.codex-tmp/cp04-v2-headroom/catalog.snapshot.json'] == trust['cards_bytes']
            and sizes['.codex-tmp/cp04-v2-headroom/catalog.search.sqlite'] == trust['index_bytes'],
            'exact fixture sizes mismatch')
    queries = old['queries']
    require([query['query_id'] for query in queries] == [case['case_id'] for case in plan['cases']],
            'query schedule mismatch')
    for query, case in zip(queries, plan['cases']):
        require(query['variants'] == [{'variant_id': 'q1', 'terms': case['query_terms']}]
                and query['taxonomy_route_id'] == case['target_category_id'], 'query content mismatch')
    thresholds = {name: plan['thresholds'][name] for name in (
        'synthetic_cold_p95_ms_max', 'synthetic_warm_p95_ms_max',
        'peak_memory_bytes_max', 'index_bytes_max')}
    require(list(thresholds.values()) == [500, 200, 256 * 1024 * 1024, 64 * 1024 * 1024],
            'predeclared threshold mismatch')
    declared = {
        'schema_version': 'cp04_full_headroom_declaration_v3',
        'measured_layer': 'shared_full_reader_engine_under_exact_fixture_trust',
        'source_hashes': {path: file_sha256(ROOT / path) for path in SOURCE_PATHS},
        'fixture_hashes': hashes, 'fixture_bytes': sizes, 'pins': trust['pins'],
        'plan_sha256': trust['synthetic_plan_sha256'], 'queries': queries, 'environment': environment(),
        'row_count': 10000, 'samples': {'cold': 30, 'warm': 30, 'discarded_warmup': 1},
        'query_schedule': 'frozen ten v2 synthetic development queries cycled three times',
        'thresholds': thresholds,
        'retrieve_timer': 'manifest/policy validation plus complete _retrieve_verified_bundle including query validation, immutable connection, index hash, cached bundle validation, FTS5 variants, RRF, dedupe, highlights, result construction and connection close',
        'additional_timers_ms': ['fixture_hash', 'json_parse', 'card_normalization', 'card_selection', 'pack', 'serialization_and_guards', 'end_to_end'],
        'cold': 'fresh child process and connection; OS cache not flushed; import/declaration/process startup outside timer',
        'warm': 'same controller process; full card file read, hash, JSON parse and normalization per sample; new immutable connection; one discarded warmup',
        'memory': 'process-lifetime Windows PeakWorkingSetSize; whole parsed 10000-card corpus, raw byte buffers, real pack and evaluator/import allocations included; max controller/child; not isolated SQLite allocation',
        'brief_context_bytes': None, 'tokens': None, 'provider_cost_usd': None,
        'end_to_end_sla_ms': None, 'production_entrypoint_accepted': False,
        'full_card_pack_capacity_measured': False, 'relevance_claim_allowed': False,
        'human_acceptance': False, 'promotion_ready': False,
        'command': '.venv/Scripts/python.exe -B evals/plugin-v1/measure_full_headroom_v3.py --run',
    }
    return declared


def assert_current(declared):
    require(declaration() == declared, 'predeclared source/fixture/environment changed')


def sample(declared, number):
    query = declared['queries'][number % len(declared['queries'])]
    end_to_end = time.perf_counter_ns()
    begin = time.perf_counter_ns()
    raw = {Path(path).name: verified_bytes(ROOT / path, FIXTURE / Path(path).name,
                                          hashed, declared['fixture_bytes'][path])
           for path, hashed in declared['fixture_hashes'].items()}
    marks = {'fixture_hash': elapsed_ms(begin, time.perf_counter_ns())}
    # The index is hashed in blocks by the shared core too; its verified raw buffer
    # stays included in peak memory, then is released before whole-corpus parsing.
    del raw['catalog.search.sqlite']
    begin = time.perf_counter_ns()
    manifest = parse_json(raw['catalog.search-manifest.json'])
    policy = parse_json(raw['retrieval-policy.json'])
    snapshot = parse_json(raw['catalog.snapshot.json'])
    marks['json_parse'] = elapsed_ms(begin, time.perf_counter_ns())
    require(manifest['pins'] == declared['pins'] and manifest['row_count'] == 10000,
            'exact fixture manifest pins/count mismatch')
    require(hashlib.sha256(raw['retrieval-policy.json']).hexdigest() == manifest['pins']['policy_sha256'],
            'fixture policy pins mismatch')
    begin = time.perf_counter_ns()
    trusted = normalize_cards(snapshot, manifest['pins'], 10000)
    marks['card_normalization'] = elapsed_ms(begin, time.perf_counter_ns())
    begin = time.perf_counter_ns()
    retrieval._validate_manifest_policy(manifest, policy)
    result = retrieval._retrieve_verified_bundle(query, run_id=RUN_ID,
        index_path=FIXTURE / 'catalog.search.sqlite', manifest=manifest, policy=policy)
    marks['retrieve'] = elapsed_ms(begin, time.perf_counter_ns())
    require(result['status'] in {'ok', 'no_match'}, 'shared reader returned failure')
    begin = time.perf_counter_ns()
    candidate_ids = packs._retrieval_candidate_ids(result['candidates'])
    supplied = {rid: trusted[rid] for rid in candidate_ids}
    selected = packs._select_verified_cards(trusted, supplied, candidate_ids)
    marks['card_selection'] = elapsed_ms(begin, time.perf_counter_ns())
    begin = time.perf_counter_ns()
    pack = packs._build_evidence_pack_from_trusted_cards(query, result, selected,
        pack_id='full-headroom-' + query['query_id'], max_cards=query['max_cards'],
        max_evidence_bytes=query['max_evidence_bytes'])
    marks['pack'] = elapsed_ms(begin, time.perf_counter_ns())
    begin = time.perf_counter_ns()
    guards = validate_capture(query, result, pack)
    byte_counts = {'query_bytes': len(canonical(query)), 'retrieval_result_bytes': len(canonical(result)),
                   'evidence_pack_bytes': len(canonical(pack))}
    marks['serialization_and_guards'] = elapsed_ms(begin, time.perf_counter_ns())
    marks['end_to_end'] = elapsed_ms(end_to_end, time.perf_counter_ns())
    peak = peak_working_set()
    return {'case_id': query['query_id'], 'sample_index': number,
            'query': query, 'retrieval_result': result, 'evidence_pack': pack,
            'query_sha256': digest(query), 'result_sha256': digest(result), 'pack_sha256': digest(pack),
            'timings_ms': marks, 'peak_memory_bytes': peak, 'card_count': len(trusted),
            'candidate_count': len(candidate_ids), 'retrieved_hits': result['retrieved_hits'],
            'packed_card_count': len(pack['cards']), 'exclusion_count': len(pack['exclusions']),
            'guards': guards, **byte_counts}


def write_exclusive(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open('xb') as stream:
        stream.write(canonical(value))


def measure(declared):
    assert_current(declared)
    cold = []
    for number in range(declared['samples']['cold']):
        child = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()),
                                '--sample', str(number)], cwd=ROOT, capture_output=True,
                               text=True, timeout=60)
        require(child.returncode == 0, 'cold sample failed: ' + child.stdout[:300] + child.stderr[:300])
        cold.append(json.loads(child.stdout))
    sample(declared, 0)
    warm = [sample(declared, number) for number in range(declared['samples']['warm'])]
    assert_current(declared)
    public = retrieval.retrieve(declared['queries'][0], run_id=RUN_ID,
        index_path=FIXTURE / 'catalog.search.sqlite',
        manifest_path=FIXTURE / 'catalog.search-manifest.json',
        policy_path=FIXTURE / 'retrieval-policy.json')
    require(public['status'] == 'index_incompatible', 'production fixed anchor must reject fixture')
    percentiles = {mode: {timer: {suffix: percentile([row['timings_ms'][timer] for row in rows], fraction)
                                for suffix, fraction in (('p50', .5), ('p95', .95))}
                         for timer in rows[0]['timings_ms']}
                   for mode, rows in (('cold', cold), ('warm', warm))}
    peak = max(peak_working_set(), *(row['peak_memory_bytes'] for row in cold + warm))
    thresholds = declared['thresholds']
    gates = {
        'cold_retrieve_p95': percentiles['cold']['retrieve']['p95'] <= thresholds['synthetic_cold_p95_ms_max'],
        'warm_retrieve_p95': percentiles['warm']['retrieve']['p95'] <= thresholds['synthetic_warm_p95_ms_max'],
        'peak_memory_bytes': peak <= thresholds['peak_memory_bytes_max'],
        'index_bytes': (FIXTURE / 'catalog.search.sqlite').stat().st_size <= thresholds['index_bytes_max'],
        'complete_capture_guards': all(all(row['guards'].values()) for row in cold + warm),
    }
    return {'schema_version': 'cp04_full_headroom_result_v3',
            'measured_layer': declared['measured_layer'], 'declaration_sha256': digest(declared),
            'cold_samples': cold, 'warm_samples': warm, 'percentiles_ms': percentiles,
            'peak_memory_bytes': peak, 'environment': declared['environment'], 'row_count': 10000,
            'index_bytes': declared['fixture_bytes']['.codex-tmp/cp04-v2-headroom/catalog.search.sqlite'],
            'cards_bytes': declared['fixture_bytes']['.codex-tmp/cp04-v2-headroom/catalog.snapshot.json'],
            'max_retrieved_hits': max(row['retrieved_hits'] for row in cold + warm),
            'max_candidates': max(row['candidate_count'] for row in cold + warm),
            'max_packed_cards': max(row['packed_card_count'] for row in cold + warm),
            'max_evidence_pack_bytes': max(row['evidence_pack_bytes'] for row in cold + warm),
            'gates': gates, 'verdict': 'synthetic_full_capacity_pass_only' if all(gates.values()) else 'no_go',
            'full_card_pack_capacity_measured': True, 'production_entrypoint_accepted': False,
            'production_negative': public, 'relevance_claim_allowed': False, 'human_acceptance': False,
            'promotion_ready': False, 'brief_context_bytes': None, 'tokens': None,
            'provider_cost_usd': None, 'end_to_end_sla_ms': None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--predeclare', action='store_true')
    modes.add_argument('--run', action='store_true')
    modes.add_argument('--sample', type=int)
    args = parser.parse_args(argv)
    try:
        declared = declaration()
        if args.predeclare:
            write_exclusive('declaration.json', declared)
            print(json.dumps({'declaration_sha256': digest(declared), 'capture_started': False}))
            return 0
        require(parse_json((OUT / 'declaration.json').read_bytes()) == declared, 'declaration mismatch')
        if args.sample is not None:
            require(0 <= args.sample < 30, 'sample index outside declared schedule')
            captured = sample(declared, args.sample)
            assert_current(declared)
            print(json.dumps(captured, ensure_ascii=True, allow_nan=False))
            return 0
        result = measure(declared)
        write_exclusive('performance.json', result)
        print(json.dumps({key: result[key] for key in ('verdict', 'gates', 'peak_memory_bytes', 'percentiles_ms',
                                                      'full_card_pack_capacity_measured')}))
        return 0 if all(result['gates'].values()) else 1
    except (OSError, ValueError, KeyError, sqlite3.DatabaseError, subprocess.SubprocessError) as error:
        failure = {'schema_version': 'cp04_full_headroom_failure_v3',
                   'verdict': 'invalid_input_or_unavailable_check', 'reason': str(error),
                   'full_card_pack_capacity_measured': False, 'promotion_ready': False}
        if args.run:
            # Exclusive failure artifacts preserve earlier failure evidence too.
            write_exclusive('failure.json', failure)
        print(json.dumps(failure))
        return 2


if __name__ == '__main__':
    sys.exit(main())
