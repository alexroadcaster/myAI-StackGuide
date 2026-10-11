"""Capture a frozen required-capability/context ranking experiment."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import rank_capability_context as ranker

spec = importlib.util.spec_from_file_location('capability_context_shared', ROOT / 'evals/plugin-v1/run_capability_package.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
base = shared.base
INPUT = ROOT / 'evals/plugin-v1/capability-context-intents.json'
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-capability-context-2026-10-11'
ARMS = ('control', 'baseline', 'enriched_literal', 'separated')


def separated(case, original, enriched, members, intent):
    route = members[case['target_category_id']]
    fields = {rid: base.scorer._baseline_fields(card) for rid, card in original.items()
              if any(c['category_id'] in route for c in card['classifications'])}
    extra = {}
    for rid in fields:
        before = original[rid]['advisory']['use_cases']
        after = enriched[rid]['advisory']['use_cases']
        if after[:len(before)] != before:
            raise ValueError('candidate does not preserve original capabilities')
        extra[rid] = after[len(before):]
    rows = ranker.rank_cards(fields, extra, case['query_terms'], intent, limit=150)
    return [r['github_repository_id'] for r in rows], rows


def declaration(plan, cases, intents):
    sources = base.source_hashes(plan)
    for p in (Path(__file__), Path(ranker.__file__), Path(shared.__file__), INPUT,
              ROOT / 'evals/plugin-v1/capability-context-contract.md', ROOT / 'tests/test_plugin_capability_context.py'):
        sources[p.relative_to(ROOT).as_posix()] = shared.builder.sha(p.read_bytes())
    old_decl = json.loads((shared.OUTPUT / 'declaration.json').read_bytes())
    snapshot, manifest, cards, verification = shared.verified_package(old_decl['receipt_sha256'])
    for case in cases:
        ranker.validate_intent(case['query_terms'], intents[case['case_id']])
    return dict(schema_version='cp04_capability_context_declaration_v1', source_hashes=sources,
        candidate_receipt_sha256=old_decl['receipt_sha256'], candidate_pins=manifest['pins'],
        intents=intents, cases=[{'case_id': c['case_id'], 'sha256': base.scorer.digest(c)} for c in cases],
        thresholds=plan['thresholds'], arms=ARMS, promotion_ready=False)


def capture(plan, cases, original, original_by_id, members, intents, declared):
    snapshot, manifest, cards, verification = shared.verified_package(declared['candidate_receipt_sha256'])
    records, captures = [], []
    run_id = str(uuid.uuid4())
    for case in cases:
        q = base.old.make_query(plan, case)
        row, details = {'case_id': case['case_id']}, {'case_id': case['case_id'], 'intent': intents[case['case_id']]}
        for arm in ARMS:
            if arm == 'control':
                packet, observed = base.execute(q, plan, original_by_id, case, arm, run_id)
            else:
                traces = None
                if arm == 'separated':
                    ids, traces = separated(case, original_by_id, cards, members, intents[case['case_id']])
                else:
                    ids = base.old.baseline_ids(plan, case, original if arm == 'baseline' else snapshot['cards'], members)
                if arm == 'baseline':
                    pack = base.old.baseline_pack(q, ids, original_by_id, plan, run_id)
                else:
                    result = shared.literal_result(q, ids, cards, manifest['pins'], run_id)
                    pack = shared.fixture_pack(q, result, cards, arm)
                packet = {'ranked_ids': ids, 'ranking_trace': traces, 'evidence_pack': pack,
                          'transport': 'literal selection adapter; no observed BM25/RRF'}
                observed = base.observe(ids, pack, case, 'ok' if ids else 'no_match')
            row[arm], details[arm] = observed, packet
        records.append(row)
        captures.append(details)
    macros = {arm: base.old.complete_macro(records, arm) for arm in ARMS}
    gates = {}
    for metric in ('recall', 'ndcg'):
        key = metric + '_at_12'
        gates['macro_' + metric] = macros['separated'][key] >= macros['baseline'][key]
        gates['every_case_' + metric] = all(r['separated']['ranking']['ranking'][metric+'_at_k'] >=
            r['baseline']['ranking']['ranking'][metric+'_at_k'] for r in records)
    gates['valid_status_rankings'] = all(r['separated']['ranking']['valid'] and r['separated']['retrieval_status']=='ok' for r in records)
    gates['constraints_and_identity'] = all(not r['separated']['hard_constraint_violations'] and
        not r['separated']['false_exclusions'] and not r['separated']['duplicate_canonical_ids'] for r in records)
    gates['pack_survival'] = all((r['separated']['pack_survival_rate'] or 0) >= plan['thresholds']['evidence_pack_survival_rate_min'] for r in records)
    historical = json.loads((shared.OUTPUT / 'observations.json').read_bytes())
    historical_by_id = {r['case_id']: r for r in historical['records']}
    gates['original_baseline_equivalence'] = all(r['baseline']['ranked_ids'] == historical_by_id[r['case_id']]['baseline']['ranked_ids'] for r in records)
    old = json.loads((ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08/held-out/observations.json').read_bytes())
    kotlin_query = next(c['query'] for c in old['captures'] if c['case_id']=='CP04-HV3-12')
    kotlin_case = dict(case_id='CP04-HV3-12', query_terms=kotlin_query['variants'][0]['terms'], target_category_id=kotlin_query['taxonomy_route_id'])
    kotlin_baseline = base.old.baseline_ids(plan, kotlin_case, original, members)
    kotlin_ids, trace = separated(kotlin_case, original_by_id, cards, members, intents['CP04-HV3-12'])
    positives = {f['github_repository_id'] for f in shared.builder.load_source()['facts'] if f['github_repository_id'] in {1148753,6296790,40136600,124230204,139914932}}
    regression = {'scope':'exposed Kotlin known-positive coverage only', 'positive_count':len(positives),
        'baseline_pool':len(positives & set(kotlin_baseline)), 'separated_pool':len(positives & set(kotlin_ids)),
        'baseline_top12':len(positives & set(kotlin_baseline[:12])), 'separated_top12':len(positives & set(kotlin_ids[:12]))}
    current = declaration(plan, cases, intents)
    if base.scorer.digest(current) != base.scorer.digest(declared):
        raise ValueError('declaration drift')
    summary = dict(macros=macros, gates=gates, development_nonregression=all(gates.values()),
        exact_baseline_orders=sum(r['separated']['ranked_ids']==r['baseline']['ranked_ids'] for r in records),
        regression=regression, package_verification=verification, promotion_ready=False)
    shared.write(OUTPUT / 'observations.json', dict(declaration_sha256=base.scorer.digest(declared), records=records,
        captures=captures, kotlin=dict(query=kotlin_query, intent=intents['CP04-HV3-12'], ranked_ids=kotlin_ids, trace=trace)))
    shared.write(OUTPUT / 'summary.json', summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--predeclare', action='store_true')
    action.add_argument('--run', action='store_true')
    args = parser.parse_args()
    plan, cases, original, by_id, members = base.load_inputs()
    intents = json.loads(INPUT.read_bytes())['cases']
    declared = declaration(plan, cases, intents)
    if args.predeclare:
        shared.write(OUTPUT / 'declaration.json', declared)
        print(json.dumps({'predeclared': base.scorer.digest(declared)}))
    else:
        saved = json.loads((OUTPUT / 'declaration.json').read_bytes())
        if base.scorer.digest(saved) != base.scorer.digest(declared) or (OUTPUT / 'observations.json').exists():
            raise ValueError('declaration drift or existing capture')
        capture(plan, cases, original, by_id, members, intents, saved)
