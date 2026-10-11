"""Actual local resource profile; supplied native order is a resource fixture only.

No model call or relevance claim. Native timings retain their own ceilings;
added local work and whole local latency are published independently.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plugins/myai-stackguide/scripts'))
import recommendation_decision as decision

spec = importlib.util.spec_from_file_location('native_resource', ROOT / 'evals/plugin-v1/measure_final_chat_request.py')
resource = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resource)
OUT = ROOT / 'evals/plugin-v1/results/cp04-final-host-resource-2026-10-11/resource-check.json'
CASES = ROOT / 'evals/plugin-v1/results/cp04-final-chat-repair-2026-10-11/observations.json'


def sample():
    payload = next(r['payload'] for r in json.loads(CASES.read_bytes())['records']
                   if r['case_id'] == 'PROSPECTIVE-HOLD-07')
    timings = {}
    original_prepare = decision.native.prepare_from_brief
    original_retrieve = decision.native.retrieval.retrieve

    def prepare(*args, **kwargs):
        start = time.perf_counter()
        result = original_prepare(*args, **kwargs)
        timings['prepare_count_ms'] = (time.perf_counter() - start) * 1000
        return result

    def retrieve(*args, **kwargs):
        start = time.perf_counter()
        result = original_retrieve(*args, **kwargs)
        timings['c9_ms'] = (time.perf_counter() - start) * 1000
        return result

    decision.native.prepare_from_brief = prepare
    decision.native.retrieval.retrieve = retrieve
    start = time.perf_counter()
    try:
        session = decision.prepare(**payload, wrapper_bytes=2048)
    finally:
        decision.native.prepare_from_brief = original_prepare
        decision.native.retrieval.retrieve = original_retrieve
    if isinstance(session, dict):
        raise ValueError('resource prepare failure: ' + json.dumps(session))
    prepared = time.perf_counter()
    order = [c['github_repository_id'] for c in session.preview_request['candidates']]
    result = decision.finalize(session, order)
    done = time.perf_counter()
    if 'decision_pack' not in result:
        raise ValueError('resource finalization failure: ' + json.dumps(result))
    ledger = decision.ledger_bytes(session, result['decision_receipt'], result['decision_pack'])
    return dict(native_ms=sum(timings.values()), **timings,
                outer_prepare_ms=(prepared-start)*1000-sum(timings.values()),
                finalize_ms=(done-prepared)*1000, total_local_ms=(done-start)*1000,
                status=result['decision_pack']['status'], ledger_bytes=ledger,
                supplied_order='Native identity order resource fixture; not a model or quality capture')


def percentile(rows, key, fraction=.95):
    return sorted(r[key] for r in rows)[math.ceil(len(rows)*fraction)-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cold-sample', action='store_true')
    args = parser.parse_args()
    if args.cold_sample:
        value = sample()
        value['peak_working_set_bytes'] = resource.peak()
        print(json.dumps(value))
        return
    if OUT.exists():
        raise ValueError('Preserve existing resource capture')
    cold = []
    for _ in range(30):
        proc = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--cold-sample'],
                              capture_output=True, text=True, check=True, cwd=ROOT)
        cold.append(json.loads(proc.stdout.strip()))
    sample()
    warm = [sample() for _ in range(30)]
    limits = json.loads((ROOT/'evals/plugin-v1/quality-plan.json').read_bytes())['thresholds']
    value = dict(scope='Full local native/preview/receipt/guard/pack ledger; no host inference',
                 python=platform.python_version(), platform=platform.platform(),
                 processor=platform.processor(),
                 cold_definition='30 new processes/connections; process launch excluded; OS cache not flushed',
                 warm_definition='Same process after discarded warmup',
                 cold_samples=cold, warm_samples=warm,
                 cold_native_p95_ms=percentile(cold, 'native_ms'),
                 warm_native_p95_ms=percentile(warm, 'native_ms'),
                 cold_total_local_p95_ms=percentile(cold, 'total_local_ms'),
                 warm_total_local_p95_ms=percentile(warm, 'total_local_ms'),
                 peak_memory_bytes=max([r['peak_working_set_bytes'] for r in cold]+[resource.peak()]),
                 index_bytes=(decision.native.ASSETS/'catalog.search.sqlite').stat().st_size,
                 host_walltime=None, remote_memory_bytes=None, cost=None,
                 unavailable_reason='Resource fixture invokes no host model; actual host/full-path evidence belongs to frozen quality capture',
                 total_local_latency_owner_review='pending; native-only thresholds do not establish outer latency acceptance',
                 human_acceptance=False, promotion_ready=False)
    value['gates'] = dict(cold_native_p95=value['cold_native_p95_ms']<=limits['actual_cold_p95_ms_max'],
                          warm_native_p95=value['warm_native_p95_ms']<=limits['actual_warm_p95_ms_max'],
                          peak_memory=value['peak_memory_bytes']<=limits['peak_memory_bytes_max'],
                          index_bytes=value['index_bytes']<=limits['index_bytes_max'],
                          statuses=all(r['status'] in ('ready','limited','no_eligible') for r in cold+warm),
                          shared_ledger=all(r['ledger_bytes']<=163840 for r in cold+warm))
    paths = [Path(__file__), Path(decision.__file__), Path(decision.native.__file__),
             Path(decision.native.retrieval.__file__), CASES,
             ROOT/'specs/retrieval/candidate-decision.schema.json',
             ROOT/'specs/retrieval/candidate-decision-contract.md']
    paths += [decision.native.ASSETS/name for name in
              ('catalog.search.sqlite','catalog.search-manifest.json','catalog.snapshot.json','retrieval-policy.json')]
    value['source_hashes'] = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:value[k] for k in ('cold_native_p95_ms','warm_native_p95_ms',
          'cold_total_local_p95_ms','warm_total_local_p95_ms','peak_memory_bytes','gates')}))
    if not all(value['gates'].values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
