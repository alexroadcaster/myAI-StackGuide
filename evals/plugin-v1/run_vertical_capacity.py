"""CP-11 declared local capacity: exact public bundle and isolated synthetic headroom.

No model, network, installs, production asset writes or production trust overrides.
The synthetic seam is the already accepted shared reader under evaluator fixture
trust. It is deliberately rejected by the production manifest entrypoint.
"""
from __future__ import annotations

import argparse
import copy
import ctypes
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shutil
import sqlite3
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / '.codex-tmp/cp11-capacity-2026-10-17'
ASSETS = ROOT / 'plugins/myai-stackguide/assets'
SYNTHETIC = WORK / 'synthetic-10000'
DECLARATION = WORK / 'declaration.json'
REPORT = ROOT / 'docs/reports/cp11-capacity-2026-10-17.json'
RUN_ID = 'bdd31f78-4b3b-4def-af2b-750af1dadb05'
FILES = ('catalog.search-manifest.json', 'catalog.search.sqlite',
         'catalog.snapshot.json', 'retrieval-policy.json')
SOURCES = (
    'evals/plugin-v1/run_vertical_capacity.py', 'evals/plugin-v1/runner-contract.md',
    'evals/plugin-v1/quality-plan.json', 'evals/plugin-v1/quality-plan-v2.json',
    'evals/plugin-v1/evaluate_retrieval.py',
    'scripts/build_plugin_search_index.py', 'scripts/build_plugin_catalog.py',
    'plugins/myai-stackguide/scripts/retrieval.py',
    'plugins/myai-stackguide/scripts/context_pack.py',
    'plugins/myai-stackguide/scripts/matcher.py',
    'specs/retrieval/catalog-query.schema.json',
    'specs/retrieval/retrieval-result.schema.json',
    'specs/retrieval/evidence-pack.schema.json',
    'tests/test_plugin_retrieval.py', 'tests/fixtures/plugin_contracts.json',
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def exclusive(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open('xb') as stream:
        stream.write(canonical(value) + b'\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


retrieval = module('cp11_capacity_retrieval', 'plugins/myai-stackguide/scripts/retrieval.py')
packs = module('cp11_capacity_packs', 'plugins/myai-stackguide/scripts/context_pack.py')


def peak():
    """Whole-process lifetime peak, not isolated SQLite allocation."""
    from ctypes import wintypes
    require(sys.platform == 'win32', 'declared Windows memory method unavailable')

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
    require(bool(psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters),
                                          counters.cb)), 'memory counter failed')
    return counters.PeakWorkingSetSize


def environment():
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                       r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
        cpu = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
    return dict(python=sys.version, executable=sys.executable, sqlite=sqlite3.sqlite_version,
                platform=platform.platform(), cpu=cpu, logical_cpu_count=os.cpu_count(),
                architecture=platform.machine(), pointer_bits=ctypes.sizeof(ctypes.c_void_p) * 8)


def public_pins():
    manifest = read(ASSETS / FILES[0])
    require(sha(ASSETS / FILES[0]) == retrieval.TRUSTED_MANIFEST_SHA256,
            'packaged manifest differs from production trust anchor')
    require(manifest['row_count'] == 2500, 'actual corpus must contain exactly2500 cards')
    for name, pin in ((FILES[1], 'index_sha256'), (FILES[2], 'cards_sha256'),
                      (FILES[3], 'policy_sha256')):
        require(sha(ASSETS / name) == manifest['pins'][pin], 'packaged bytes mismatch:' + name)
    return manifest


def query(pins, case):
    limits = read(ASSETS / 'retrieval-policy.json')['limits']
    return dict(schema_version='2.1.0', query_id=case['case_id'], brief_version=1,
        source_mode='catalog_only', retrieval_engine='sqlite_fts5',
        policy_version=pins['retrieval_policy_version'], policy_sha256=pins['policy_sha256'],
        card_schema_version=pins['card_schema_version'],
        activity_schema_version=pins['activity_schema_version'],
        index_format_version=pins['index_format_version'],
        taxonomy_route_id=case['target_category_id'], language=case['query_locale'],
        variants=[dict(variant_id='q1', terms=case['query_terms'])],
        constraints=dict(languages=[], deployment=[], allowed_licenses=[], compatibility=[],
                         require_no_server=None, mandatory_fields=[]),
        max_candidates=limits['max_retrieved_hits'], max_cards=limits['max_detailed_cards'],
        max_evidence_bytes=limits['max_evidence_bytes'])


def child(*arguments):
    result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), *arguments],
                            cwd=ROOT, capture_output=True, text=True, timeout=120)
    require(result.returncode == 0, 'capacity child failed:' + result.stderr[:1500] + result.stdout[:500])
    return json.loads(result.stdout)


def build_actual():
    """Deterministic source-owned builder writes only the task's new temp DB."""
    builder = module('cp11_capacity_builder', 'scripts/build_plugin_search_index.py')
    snapshot = read(ASSETS / 'catalog.snapshot.json')
    policy = read(ASSETS / 'retrieval-policy.json')
    manifest = public_pins()
    path = WORK / 'actual-build.sqlite'
    require(not path.exists(), 'preserve prior actual build')
    start = time.perf_counter_ns()
    rows = builder.logical_rows(snapshot['cards'])
    routes = builder.logical_routes(snapshot['taxonomy_sha256'])
    builder.build_sqlite(path, snapshot['cards'], rows, snapshot, policy,
        manifest['pins']['cards_sha256'], manifest['pins']['policy_sha256'],
        builder.logical_rows_sha256(rows), routes, builder.logical_routes_sha256(routes))
    return dict(build_ms=(time.perf_counter_ns()-start)/1e6, index_bytes=path.stat().st_size,
        index_sha256=sha(path), byte_equal_packaged=sha(path) == manifest['pins']['index_sha256'],
        logical_rows_sha256=builder.logical_rows_sha256(rows),
        logical_rows_equal_packaged=builder.logical_rows_sha256(rows) == manifest['logical_rows_sha256'],
        process_peak_memory_bytes=peak(), scope='projection + SQLite build/integrity/VACUUM; source parsing excluded; one build')


def synthetic_card(card, replica, pins):
    value = copy.deepcopy(card)
    identity = value['identity']
    rid = 10**12 * (replica+1) + identity['github_repository_id']
    identity.update(github_repository_id=rid, full_name=f'synthetic-headroom/repository-{rid}',
        url=f'https://github.com/synthetic-headroom/repository-{rid}',
        catalog_record_id=f'gh-pending:synthetic-headroom/{rid}',
        full_name_aliases=[], merged_catalog_record_ids=[])
    value['corpus_kind'] = 'synthetic_fixture'
    value['provenance']['frozen_pins'].update(pins)
    for item in value['evidence'] + value['provenance']['sources']:
        item.update(source_kind='synthetic_fixture', source_ref=f'fixture:cp11-capacity/repositories/{rid}')
    return value


def build_synthetic():
    """Same CP04 isolated fixture method; no source/production CHECK is changed."""
    builder = module('cp11_capacity_projection', 'scripts/build_plugin_search_index.py')
    manifest = public_pins()
    source = read(ASSETS / 'catalog.snapshot.json')
    require(not SYNTHETIC.exists(), 'preserve prior synthetic fixture')
    SYNTHETIC.mkdir()
    source_hash = digest(dict(method='four-distinct-id-copies/cp11-capacity-v1',
                              source_cards_sha256=manifest['pins']['cards_sha256']))
    identity_pins = dict(source_sha256=source_hash, catalog_snapshot_id='synthetic-cp11-' + source_hash)
    envelope = {key: value for key, value in source.items() if key != 'cards'}
    envelope.update(identity_pins, corpus_kind='synthetic_fixture', builder_version='cp11-capacity-v1')
    start = time.perf_counter_ns()
    rows, classifications = [], []
    with (SYNTHETIC / 'catalog.snapshot.json').open('xb') as stream:
        stream.write(b'{')
        for index, key in enumerate(sorted([*envelope, 'cards'])):
            if index:
                stream.write(b',')
            stream.write(canonical(key) + b':')
            if key != 'cards':
                stream.write(canonical(envelope[key]))
                continue
            stream.write(b'[')
            for replica in range(4):
                for card in source['cards']:
                    value = synthetic_card(card, replica, identity_pins)
                    if rows:
                        stream.write(b',')
                    stream.write(canonical(value))
                    rows.append(builder.project_card(value))
                    classifications.extend((value['identity']['github_repository_id'], item['category_id'],
                        item['role'], item['kind']) for item in value['classifications'])
            stream.write(b']')
        stream.write(b'}')
    rows.sort(key=lambda row: row['github_repository_id'])
    require(len(rows) == len({row['github_repository_id'] for row in rows}) == 10000,
            'synthetic identity count mismatch')
    path = SYNTHETIC / 'catalog.search.sqlite'
    shutil.copyfile(ASSETS / path.name, path)
    shutil.copyfile(ASSETS / 'retrieval-policy.json', SYNTHETIC / 'retrieval-policy.json')
    pins = manifest['pins']
    pins.update(identity_pins, corpus_kind='synthetic_fixture', cards_sha256=sha(SYNTHETIC / 'catalog.snapshot.json'))
    logical_hash = builder.logical_rows_sha256(rows)
    with sqlite3.connect(path) as connection:
        cursor = connection.execute('SELECT * FROM bundle_metadata')
        columns = [item[0] for item in cursor.description]
        metadata = dict(zip(columns, cursor.fetchone()))
        schema = connection.execute("SELECT sql FROM sqlite_master WHERE name='bundle_metadata'").fetchone()[0]
        require('row_count = 2500' in schema and "corpus_kind = 'catalog_snapshot'" in schema,
                'unrecognized isolated metadata schema')
        schema = schema.replace('row_count = 2500', 'row_count = 10000').replace(
            "corpus_kind = 'catalog_snapshot'", "corpus_kind = 'synthetic_fixture'")
        connection.execute('DROP TABLE bundle_metadata')
        connection.execute(schema)
        metadata.update({key: pins[key] for key in ('catalog_snapshot_id', 'source_sha256', 'cards_sha256', 'corpus_kind')})
        metadata.update(row_count=10000, logical_rows_sha256=logical_hash)
        connection.execute('INSERT INTO bundle_metadata VALUES (' + ','.join('?' for _ in columns) + ')',
                           [metadata[key] for key in columns])
        connection.execute('DELETE FROM repository_classifications')
        connection.execute('DELETE FROM repository_search_rows')
        connection.executemany('INSERT INTO repository_search_rows VALUES (?,?,?,?,?,?,?,?,?,?)',
            [tuple(row[key] for key in ('github_repository_id', *builder.FTS_COLUMNS)) for row in rows])
        connection.executemany('INSERT INTO repository_classifications VALUES (?,?,?,?)', classifications)
        connection.execute("INSERT INTO repository_fts(repository_fts) VALUES ('rebuild')")
        connection.commit()
        connection.execute('VACUUM')
        require(connection.execute('PRAGMA integrity_check').fetchone() == ('ok',), 'synthetic integrity failed')
    pins['index_sha256'] = sha(path)
    manifest.update(row_count=10000, logical_rows_sha256=logical_hash)
    exclusive(SYNTHETIC / 'catalog.search-manifest.json', manifest)
    return dict(build_ms=(time.perf_counter_ns()-start)/1e6, index_bytes=path.stat().st_size,
        cards_bytes=(SYNTHETIC / 'catalog.snapshot.json').stat().st_size,
        process_peak_memory_bytes=peak(), scope='synthetic transformation/streamed serialization + copied DB rebuild/integrity/VACUUM; one build',
        unique_numeric_ids=len(rows), corpus_kind='synthetic_fixture', relevance_claim_allowed=False)


def source_hashes():
    paths = set(SOURCES)
    paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT/'specs').rglob('*.schema.json')
        if path.relative_to(ROOT).as_posix() not in {
            'specs/catalog/capability-enrichment.schema.json',
            'specs/retrieval/candidate-decision.schema.json'})
    paths.update(('evals/result.schema.json', 'evals/scenario.schema.json'))
    return {path: sha(ROOT / path) for path in sorted(paths)}


def predeclare():
    require(not DECLARATION.exists() and not REPORT.exists(), 'preserve prior declaration/report')
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'test-temp').mkdir(exist_ok=True)
    public = public_pins()
    actual_build = child('--build', 'actual')
    synthetic_build = child('--build', 'synthetic')
    plan = read(ROOT / 'evals/plugin-v1/quality-plan-v2.json')
    cases = [{key: item[key] for key in ('case_id', 'target_category_id', 'query_locale', 'query_terms')}
             for item in plan['cases'] if item['split'] == 'development']
    require(len(cases) == 10, 'expected ten frozen development workloads')
    value = dict(schema_version='cp11_capacity_declaration_v1', created_at=datetime.now(timezone.utc).isoformat(),
        sources=source_hashes(), environment=environment(), actual_manifest=public,
        native_schema_set_sha256=contracts().schema_set_sha256,
        actual_assets={name: dict(sha256=sha(ASSETS/name), bytes=(ASSETS/name).stat().st_size) for name in FILES},
        synthetic_assets={name: dict(sha256=sha(SYNTHETIC/name), bytes=(SYNTHETIC/name).stat().st_size) for name in FILES},
        synthetic_manifest=read(SYNTHETIC/FILES[0]), actual_build=actual_build, synthetic_build=synthetic_build,
        cases=cases, samples=dict(cold=30, warm=30, discarded_warmup=1),
        thresholds=read(ROOT/'evals/plugin-v1/quality-plan.json')['thresholds'],
        query_derivation='Only the ten frozen development query terms/routes/locales are reused; active production manifest supplies current pins. No judgments or held-out cases used or tuned.',
        timer='perf_counter_ns around production retrieve (actual), or exact-fixture manifest/policy validation + shared _retrieve_verified_bundle (synthetic); startup/imports outside timer',
        pack_timer='separate complete streamed snapshot verification, candidate retention, shared pack assembly and serialization; no total-path latency threshold',
        memory='Windows GetProcessMemoryInfo PeakWorkingSetSize, maximum across child and dedicated warm worker; includes source/declaration/pack/schema validation allocations; build processes separately recorded',
        cold='new process and immutable connection for each sample',
        warm='one dedicated process per corpus, new immutable connection each sample after one discarded warmup',
        os_cache='not flushed; build, hash validation and other local work warm the cache',
        percentiles='nearest rank ceil(p*n); mixed ten-query schedule cycles three times',
        commands=[r'C:\Python314\python.exe -B evals/plugin-v1/run_vertical_capacity.py --predeclare',
                  r'C:\Python314\python.exe -B evals/plugin-v1/run_vertical_capacity.py --run'],
        environment_setup="PYTHONPATH=.venv/Lib/site-packages; TEMP=.codex-tmp/cp11-capacity-2026-10-17/test-temp",
        tokens=None, provider_cost_usd=None, relevance_claim_allowed=False, promotion_ready=False)
    exclusive(DECLARATION, value)
    return dict(declaration_path=DECLARATION.relative_to(ROOT).as_posix(), declaration_sha256=sha(DECLARATION),
                actual_build=actual_build, synthetic_build=synthetic_build)


def current():
    declared = read(DECLARATION)
    require(declared['sources'] == source_hashes(), 'source changed after declaration')
    require(declared['environment'] == environment(), 'runtime changed after declaration')
    for folder, key in ((ASSETS, 'actual_assets'), (SYNTHETIC, 'synthetic_assets')):
        for name in FILES:
            require(sha(folder/name) == declared[key][name]['sha256'] and
                    (folder/name).stat().st_size == declared[key][name]['bytes'], 'asset changed:' + name)
    return declared


def one(declared, corpus, number, contracts):
    folder = ASSETS if corpus == 'actual' else SYNTHETIC
    manifest = declared[corpus + '_manifest']
    policy = read(folder / 'retrieval-policy.json')
    q = query(manifest['pins'], declared['cases'][number % 10])
    start = time.perf_counter_ns()
    if corpus == 'actual':
        result = retrieval.retrieve(q, run_id=RUN_ID, index_path=folder/FILES[1],
            manifest_path=folder/FILES[0], policy_path=folder/FILES[3])
    else:
        # Exact folder, complete-file hashes and bytes are checked in current().
        # Neither the production anchor nor its entrypoint is replaced.
        retrieval._validate_manifest_policy(manifest, policy)
        result = retrieval._retrieve_verified_bundle(q, run_id=RUN_ID,
            index_path=folder/FILES[1], manifest=manifest, policy=policy)
    elapsed = (time.perf_counter_ns()-start)/1e6
    require(result['status'] in ('ok', 'no_match'), 'retrieval failed:' + result['status'])
    ids = packs._retrieval_candidate_ids(result['candidates'])
    start = time.perf_counter_ns()
    cards = packs._stream_verified_snapshot_cards(folder/FILES[2], manifest['pins'],
        expected_count=manifest['row_count'], max_bytes=declared[corpus+'_assets'][FILES[2]]['bytes'],
        candidate_ids=ids)
    pack = packs._build_evidence_pack_from_trusted_cards(q, result, cards,
        pack_id='cp11-capacity-pack', max_cards=q['max_cards'], max_evidence_bytes=q['max_evidence_bytes'])
    serialized = dict(query=len(canonical(q)), result=len(canonical(result)), pack=len(canonical(pack)))
    pack_ms = (time.perf_counter_ns()-start)/1e6
    for schema, instance in (('catalog-query', q), ('retrieval-result', result), ('evidence-pack', pack)):
        contracts.validate('retrieval/' + schema + '.schema.json', instance)
    packed = [item['card']['identity']['github_repository_id'] for item in pack['cards']]
    excluded = [item['github_repository_id'] for item in pack['exclusions']]
    require(set(packed).isdisjoint(excluded) and set(packed) | set(excluded) == set(ids), 'candidate coverage mismatch')
    require(len(ids) == len(set(ids)) and len(ids) <= result['retrieved_hits'] <= q['max_candidates'], 'candidate cap/dedupe failed')
    require(result['executed_variants'] == len(q['variants']), 'variant count mismatch')
    require(len(packed) <= q['max_cards'] and serialized['pack'] <= q['max_evidence_bytes'] and
        serialized['query']+serialized['pack'] <= policy['limits']['max_plugin_input_bytes'], 'serialized cap failed')
    return dict(sample_index=number, case_id=q['query_id'], retrieve_ms=elapsed, pack_ms=pack_ms,
        status=result['status'], retrieved_hits=result['retrieved_hits'], candidate_count=len(ids),
        detailed_cards=len(packed), exclusions=len(excluded), serialized_bytes=serialized,
        query_sha256=digest(q), result_sha256=digest(result), pack_sha256=digest(pack),
        validated_card_count=manifest['row_count'], retained_card_count=len(cards),
        peak_memory_bytes=peak(), native_schema_validation=True, coverage_and_budgets=True)


def contracts():
    return module('cp11_capacity_schema', 'evals/plugin-v1/evaluate_retrieval.py').Contracts()


def route_probes(declared):
    snapshot = read(ASSETS/'catalog.snapshot.json')
    result = []
    for term, rid, field in (('alist-org/alist', 323965659, 'full_name_aliases'),
                             ('extracts metadata and text', 206427, 'catalog_description')):
        card = next(c for c in snapshot['cards'] if c['identity']['github_repository_id'] == rid)
        q = query(declared['actual_manifest']['pins'], dict(case_id='CP11-PROBE-'+field,
            target_category_id=None, query_locale='en', query_terms=[term]))
        captured = retrieval.retrieve(q, run_id=RUN_ID, index_path=ASSETS/FILES[1],
            manifest_path=ASSETS/FILES[0], policy_path=ASSETS/FILES[3])
        matched = next((c for c in captured['candidates'] if c['github_repository_id'] == rid), None)
        require(matched and field in matched['matched_fields'], 'required route probe failed:' + field)
        if field == 'catalog_description':
            require(card['catalog']['membership_cohort'] == 'cat07a_expansion',
                    'catalog description lacks CAT07A expansion lineage')
        result.append(dict(term=term, expected_numeric_id=rid, expected_field=field, query=q,
            retrieval_result=captured, actual_matched=matched, provenance=card['provenance'],
            catalog=card['catalog'], descriptions=card['descriptions'], passed=True))
    return result


def run():
    require(not REPORT.exists(), 'preserve prior capacity report')
    declared = current()
    rows, summaries = {}, {}
    for corpus in ('actual', 'synthetic'):
        cold = [child('--sample', corpus, str(number)) for number in range(30)]
        warm_result = child('--warm', corpus)
        warm = warm_result['samples']
        rows[corpus] = dict(cold=cold, warm=warm)
        percentile = lambda series, fraction: sorted(series)[math.ceil(len(series)*fraction)-1]
        summary = {name + '_' + p: percentile([item['retrieve_ms'] for item in samples], fraction)
            for name, samples in (('cold', cold), ('warm', warm)) for p, fraction in (('p50_ms', .5), ('p95_ms', .95))}
        summary.update(peak_memory_bytes=max(item['peak_memory_bytes'] for item in cold+warm),
            index_bytes=declared[corpus+'_assets'][FILES[1]]['bytes'],
            serialized_bytes_max={key:max(item['serialized_bytes'][key] for item in cold+warm) for key in ('query', 'result', 'pack')})
        limits = declared['thresholds']
        summary['gates'] = dict(cold=summary['cold_p95_ms'] <= limits[corpus+'_cold_p95_ms_max'],
            warm=summary['warm_p95_ms'] <= limits[corpus+'_warm_p95_ms_max'],
            peak_memory=summary['peak_memory_bytes'] <= limits['peak_memory_bytes_max'],
            index_bytes=summary['index_bytes'] <= limits['index_bytes_max'],
            native_schema_and_budgets=all(item['native_schema_validation'] and item['coverage_and_budgets'] for item in cold+warm))
        summaries[corpus] = summary
    probes = route_probes(declared)
    synthetic_query = query(declared['synthetic_manifest']['pins'], declared['cases'][0])
    rejected = retrieval.retrieve(synthetic_query, run_id=RUN_ID, index_path=SYNTHETIC/FILES[1],
        manifest_path=SYNTHETIC/FILES[0], policy_path=SYNTHETIC/FILES[3])
    require(rejected['status'] == 'index_incompatible', 'production unexpectedly accepts synthetic fixture')
    current()
    passed = all(all(summary['gates'].values()) for summary in summaries.values())
    value = dict(schema_version='cp11_capacity_result_v1', created_at=datetime.now(timezone.utc).isoformat(),
        declaration=declared, declaration_sha256=sha(DECLARATION), samples=rows, summaries=summaries,
        superseded_attempts=read(WORK/'superseded-source-repair.json')
            if (WORK/'superseded-source-repair.json').exists() else [],
        route_probes=probes, production_rejects_synthetic=rejected, public_assets_unchanged=True,
        c8_contract_conflict=dict(status='outside_capacity_lane_parent_owns_actual_capture', actual_capture_scored=False,
            reason='Accepted evals/result.schema.json requires evidence_kind=synthetic_contract_capture; evals/scenario.schema.json requires corpus_kind=synthetic_fixture, case_set_id=cp04-c9-synthetic-compatibility-v2 and split=grader_contract_not_held_out. Actual catalog_snapshot C9 output cannot be relabeled synthetic. Native C9 schema validation here is separate from C8 scorer compatibility.',
            next_owner='Parent CP11 evaluator owns the separately scoped actual-catalog capture adapter and additive source-card validation callback. This capacity report neither executes nor judges that scorer lane.'),
        tokens=None, provider_cost_usd=None, model_calls=0, network_calls=0,
        relevance_claim_allowed=False, lifecycle_claim_allowed=False, promotion_ready=False,
        verdict='capacity_pass_only' if passed else 'capacity_no_go',
        limitations=['Mixed ten-query workload, not a per-query or worst-case SLA.',
            'OS caches were not flushed; process startup/imports excluded from retrieve timer.',
            'One build per corpus; build peaks recorded separately from reader-process ceiling.',
            'Synthetic duplicate text proves headroom only, not growth, recall or usefulness.',
            'No lifecycle, browser, model, installed-product or production acceptance.'])
    exclusive(REPORT, value)
    print(json.dumps(dict(verdict=value['verdict'], summaries=summaries, report=REPORT.relative_to(ROOT).as_posix())))
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    flags = parser.add_mutually_exclusive_group(required=True)
    flags.add_argument('--predeclare', action='store_true')
    flags.add_argument('--run', action='store_true')
    flags.add_argument('--build', choices=('actual', 'synthetic'))
    flags.add_argument('--sample', nargs=2, metavar=('CORPUS', 'INDEX'))
    flags.add_argument('--warm', choices=('actual', 'synthetic'))
    args = parser.parse_args()
    if args.predeclare:
        print(json.dumps(predeclare()))
    elif args.build:
        print(json.dumps(build_actual() if args.build == 'actual' else build_synthetic()))
    elif args.sample:
        corpus, number = args.sample
        require(corpus in ('actual', 'synthetic') and 0 <= int(number) < 30, 'invalid sample')
        declared = current()
        print(json.dumps(one(declared, corpus, int(number), contracts())))
    elif args.warm:
        declared, validator = current(), contracts()
        one(declared, args.warm, 0, validator)
        samples = [one(declared, args.warm, index, validator) for index in range(30)]
        current()
        print(json.dumps(dict(samples=samples)))
    else:
        return run()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
