"""Freeze and compare two required-feature priority modes without activation."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import rank_requirement_priority as ranker

spec = importlib.util.spec_from_file_location('priority_previous', ROOT / 'evals/plugin-v1/run_capability_context.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
shared, base = previous.shared, previous.base
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-requirement-priority-2026-10-11'
ORACLE = ROOT / 'evals/plugin-v1/quality-oracle-v3-source.json'
ARMS = ('control', 'baseline', 'separated', *ranker.MODES)


def priority_ids(case, original, enriched, members, intent, limit, mode):
    route = members[case['target_category_id']]
    fields = {rid: base.scorer._baseline_fields(c) for rid,c in original.items()
              if any(p['category_id'] in route for p in c['classifications'])}
    extra = {}
    for rid in fields:
        before, after = original[rid]['advisory']['use_cases'], enriched[rid]['advisory']['use_cases']
        if after[:len(before)] != before:
            raise ValueError('candidate capability lineage mismatch')
        extra[rid] = after[len(before):]
    rows = ranker.rank_cards(fields, extra, case['query_terms'], intent, limit=limit, mode=mode)
    return [r['github_repository_id'] for r in rows], rows


def declaration(plan, cases, intents):
    value = previous.declaration(plan, cases, intents)
    for path in (Path(__file__), Path(ranker.__file__), ORACLE,
                 ROOT / 'evals/plugin-v1/requirement-priority-contract.md',
                 ROOT / 'tests/test_plugin_requirement_priority.py', previous.OUTPUT / 'observations.json'):
        value['source_hashes'][path.relative_to(ROOT).as_posix()] = shared.builder.sha(path.read_bytes())
    value.update(schema_version='cp04_requirement_priority_declaration_v1', arms=ARMS,
                 selection='all non-regression gates, improve exposed Kotlin top12; highest count, tie conservative')
    return value


def observe_selection(query, ids, cards, manifest, case, run_id, arm, trace):
    result = shared.literal_result(query, ids, cards, manifest['pins'], run_id)
    pack = shared.fixture_pack(query, result, cards, arm)
    return dict(ranked_ids=ids, ranking_trace=trace, evidence_pack=pack,
                transport='literal rank adapter; placeholder rank scores, not BM25/RRF observation'), base.observe(ids, pack, case, result['status'])


def capture(plan, cases, original, original_by_id, members, intents, declared):
    snapshot, manifest, cards, verification = shared.verified_package(declared['candidate_receipt_sha256'])
    limit = plan['lexical_baseline']['candidate_limit']
    run_id, records, captures = str(uuid.uuid4()), [], []
    for case in cases:
        query = base.old.make_query(plan, case)
        row, packet = dict(case_id=case['case_id']), dict(case_id=case['case_id'], intent=intents[case['case_id']])
        for arm in ARMS:
            if arm == 'control':
                details, record = base.execute(query, plan, original_by_id, case, arm, run_id)
            elif arm == 'baseline':
                ids = base.old.baseline_ids(plan, case, original, members)
                pack = base.old.baseline_pack(query, ids, original_by_id, plan, run_id)
                details = dict(ranked_ids=ids, evidence_pack=pack, transport='original literal rank adapter')
                record = base.observe(ids, pack, case, 'ok' if ids else 'no_match')
            else:
                if arm == 'separated':
                    ids, trace = previous.separated(case, original_by_id, cards, members, intents[case['case_id']], limit)
                else:
                    ids, trace = priority_ids(case, original_by_id, cards, members, intents[case['case_id']], limit, arm)
                details, record = observe_selection(query, ids, cards, manifest, case, run_id, arm, trace)
            packet[arm], row[arm] = details, record
        records.append(row)
        captures.append(packet)
    macros = {arm: base.old.complete_macro(records, arm) for arm in ARMS}
    historical = json.loads((previous.OUTPUT / 'observations.json').read_bytes())
    old_rows = {r['case_id']:r for r in historical['records']}
    equivalence = all(r['baseline']['ranked_ids']==old_rows[r['case_id']]['baseline']['ranked_ids'] and
                      r['separated']['ranked_ids']==old_rows[r['case_id']]['separated']['ranked_ids'] for r in records)
    gates = {}
    for arm in ranker.MODES:
        g = dict(historical_baseline_and_separated_equivalence=equivalence)
        for metric in ('recall','ndcg'):
            g['macro_' + metric] = macros[arm][metric+'_at_12'] >= macros['baseline'][metric+'_at_12']
            g['every_case_' + metric] = all(r[arm]['ranking']['ranking'][metric+'_at_k'] >=
                r['baseline']['ranking']['ranking'][metric+'_at_k'] for r in records)
        g['constraints_identity_status'] = all(not r[arm]['hard_constraint_violations'] and not r[arm]['false_exclusions']
            and not r[arm]['duplicate_canonical_ids'] and r[arm]['ranking']['valid'] and r[arm]['retrieval_status']=='ok' for r in records)
        g['pack_survival'] = all((r[arm]['pack_survival_rate'] or 0) >= plan['thresholds']['evidence_pack_survival_rate_min'] for r in records)
        gates[arm] = g
    old_kotlin = json.loads((ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08/held-out/observations.json').read_bytes())
    query = next(c['query'] for c in old_kotlin['captures'] if c['case_id']=='CP04-HV3-12')
    case = dict(case_id='CP04-HV3-12', query_terms=query['variants'][0]['terms'], target_category_id=query['taxonomy_route_id'])
    kotlin_oracle = next(c for c in json.loads(ORACLE.read_bytes())['cases'] if c['case_id']==case['case_id'])
    positives = set(kotlin_oracle['source_supported_positive_ids'])
    kotlin, coverage = {}, {}
    for arm in ('baseline','separated',*ranker.MODES):
        trace = None
        if arm == 'baseline':
            ids = base.old.baseline_ids(plan, case, original, members)
            pack = base.old.baseline_pack(query, ids, original_by_id, plan, run_id)
        else:
            if arm == 'separated':
                ids, trace = previous.separated(case, original_by_id, cards, members, intents[case['case_id']], limit)
            else:
                ids, trace = priority_ids(case, original_by_id, cards, members, intents[case['case_id']], limit, arm)
            result = shared.literal_result(query, ids, cards, manifest['pins'], run_id)
            pack = shared.fixture_pack(query, result, cards, arm)
        selected = {r['card']['identity']['github_repository_id'] for r in pack['cards']}
        coverage[arm] = dict(pool=len(positives & set(ids)), top12=len(positives & set(ids[:case.get('k', query['max_cards'])])),
            packed_positives=sorted(positives & selected), ranks={cards[rid]['identity']['full_name']:ids.index(rid)+1 if rid in ids else None for rid in sorted(positives)})
        kotlin[arm] = dict(ranked_ids=ids, trace=trace, evidence_pack=pack)
    passing = [arm for arm in ranker.MODES if all(gates[arm].values()) and coverage[arm]['top12'] > coverage['separated']['top12']]
    selected = sorted(passing, key=lambda arm:(-coverage[arm]['top12'], ranker.MODES.index(arm)))[0] if passing else None
    if base.scorer.digest(declaration(plan, cases, intents)) != base.scorer.digest(declared):
        raise ValueError('declaration drift')
    summary = dict(macros=macros, gates=gates, kotlin_known_positive_count=len(positives), kotlin=coverage,
        selected_development_mode=selected, promotion_ready=False, package_verification=verification,
        exact_baseline_orders={arm:sum(r[arm]['ranked_ids']==r['baseline']['ranked_ids'] for r in records) for arm in ranker.MODES},
        per_case_metrics=[dict(case_id=r['case_id'], **{a:r[a]['ranking']['ranking'] for a in ARMS}) for r in records])
    shared.write(OUTPUT / 'observations.json', dict(declaration_sha256=base.scorer.digest(declared), records=records, captures=captures,
                                                  kotlin_query=query, kotlin=kotlin))
    shared.write(OUTPUT / 'summary.json', summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='per_case_metrics'}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--predeclare', action='store_true')
    action.add_argument('--run', action='store_true')
    args = parser.parse_args()
    plan,cases,original,by_id,members = base.load_inputs()
    intents = json.loads(previous.INPUT.read_bytes())['cases']
    declared = declaration(plan,cases,intents)
    if args.predeclare:
        shared.write(OUTPUT/'declaration.json', declared)
        print(json.dumps({'predeclared':base.scorer.digest(declared)}))
    else:
        saved = json.loads((OUTPUT/'declaration.json').read_bytes())
        if base.scorer.digest(saved)!=base.scorer.digest(declared) or (OUTPUT/'observations.json').exists():
            raise ValueError('declaration drift or existing capture')
        capture(plan,cases,original,by_id,members,intents,saved)
