"""Compare structured request guards against frozen unguarded development arms."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
import guard_recommendation_request as guard

spec = importlib.util.spec_from_file_location('request_previous', ROOT/'evals/plugin-v1/run_domain_review.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
base, priority, shared, builder = old.base, old.priority, old.shared, old.builder
INPUT = ROOT/'evals/plugin-v1/request-guard-cases-2026-10-11.json'
FACTS = ROOT/'research/cp04-request-dependency-evidence-2026-10-11.json'
OUTPUT = ROOT/'evals/plugin-v1/results/cp04-request-guard-v2-2026-10-11'


def load_facts(cards):
    facts = json.loads(FACTS.read_bytes())['facts']
    for f in facts:
        if cards[f['github_repository_id']]['identity']['full_name'] != f['full_name'] or not f['source_urls']:
            raise ValueError('dependency evidence identity/source mismatch')
    if len({f['github_repository_id'] for f in facts}) != len(facts):
        raise ValueError('duplicate evidence identity')
    return {f['github_repository_id']: f for f in facts}


def declaration():
    parent = json.loads((old.OUTPUT/'declaration.json').read_bytes())
    hashes = dict(parent['source_hashes'])
    for path in (INPUT, FACTS, Path(__file__), Path(guard.__file__),
                 ROOT/'tests/test_plugin_request_guard.py', ROOT/'evals/plugin-v1/request-guard-contract.md',
                 old.OUTPUT/'reviewed-observations.json', old.OUTPUT/'reviewed-summary.json',
                 ROOT/'evals/plugin-v1/source-review-corrections-2026-10-11.json',
                 ROOT/'evals/plugin-v1/results/cp04-request-guard-2026-10-11/failure.json',
                 ROOT/'evals/plugin-v1/results/cp04-request-guard-2026-10-11/declaration.json'):
        hashes[path.relative_to(ROOT).as_posix()] = builder.sha(path.read_bytes())
    for name, digest in hashes.items():
        if builder.sha((ROOT/name).read_bytes()) != digest:
            raise ValueError('frozen source drift: '+name)
    return dict(schema_version='cp04_request_guard_declaration_v1', source_hashes=hashes,
                receipt_sha256=parent['receipt_sha256'], independent_held_out=False, promotion_ready=False)


def capture(declared):
    plan, regressions, original, by_id, members = base.load_inputs()
    evidence = load_facts(by_id)
    manifest, cards, _ = old.previous.verified_package(declared['receipt_sha256'])
    challenges = json.loads(INPUT.read_bytes())['cases']
    original_cases = json.loads(old.previous.INPUT.read_bytes())['cases']
    prior = json.loads((old.OUTPUT/'reviewed-observations.json').read_bytes())
    prior_by = {r['case_id']: r for r in prior['records']}
    run_id, records = str(uuid.uuid4()), []
    for case in original_cases + challenges:
        unresolved = case.get('request_constraints', {}).get('unresolved', [])
        query = None if unresolved else base.old.make_query(plan, case)
        request = guard.prepare(query, case['intent'], **case.get('request_constraints', {}))
        row = dict(case_id=case['case_id'], user_goal=case['user_goal'], request=request, arms={})
        for arm in old.previous.ARMS:
            calls, result_holder = [], []
            def retrieve():
                calls.append(True)
                if arm == 'control':
                    result = base.old.retrieval.retrieve(query, run_id=run_id,
                        index_path=ROOT/plan['artifacts']['index_path'], manifest_path=ROOT/plan['artifacts']['manifest_path'],
                        policy_path=ROOT/plan['artifacts']['policy_path'])
                    if result['status'] not in ('ok', 'no_match'):
                        raise ValueError('retrieval failed: '+result['status'])
                    result_holder.append(result)
                    return [r['github_repository_id'] for r in result['candidates']]
                if arm == 'baseline':
                    return base.old.baseline_ids(plan, case, original, members)
                if arm == 'separated':
                    return priority.previous.separated(case, by_id, cards, members, case['intent'], plan['lexical_baseline']['candidate_limit'])[0]
                return priority.priority_ids(case, by_id, cards, members, case['intent'], plan['lexical_baseline']['candidate_limit'], arm)[0]
            selected = guard.execute(request, retrieve, evidence, limit=query['max_candidates'] if query else plan['candidate_route']['max_candidates'])
            if selected['status'] == 'needs_clarification':
                row['arms'][arm] = dict(selection=selected, retrieval_calls=len(calls), pack_created=False)
                continue
            ids = selected['selected_ids']
            if arm == 'control':
                result = dict(result_holder[0])
                result['candidates'] = guard.filtered_candidates(result['candidates'], ids)
                pack = base.old.context_pack.build_evidence_pack(query, result, {rid: by_id[rid] for rid in ids},
                    pack_id='guard-'+case['case_id'], max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
            elif arm == 'baseline':
                pack = base.old.baseline_pack(query, ids, by_id, plan, run_id)
            else:
                result = shared.literal_result(query, ids, cards, manifest['pins'], run_id)
                pack = shared.fixture_pack(query, result, cards, arm)
            packed = [r['card']['identity']['github_repository_id'] for r in pack['cards']]
            observed = dict(selection=selected, retrieval_calls=len(calls), pack_created=True, packed_ids=packed,
                            evidence_pack_sha256=base.scorer.digest(pack), top12_names=[by_id[r]['identity']['full_name'] for r in ids[:12]])
            if case['case_id'].startswith('CP04-ND-'):
                observed['exact_prior_order'] = ids == prior_by[case['case_id']]['arms'][arm]['ranked_ids']
            else:
                # Independent prior negative labels are used only to score AFTER selection.
                forbidden = prior_by[case['case_id']]['arms'][arm]['known_conflicts_top12']
                observed['known_conflicts_top12'] = old.conflicts(ids, forbidden)
                observed['known_conflicts_pack'] = old.conflicts(packed, forbidden)
                observed['prior_known_conflicts_top12'] = forbidden
            row['arms'][arm] = observed
        records.append(row)
    historical = []
    intents = json.loads(priority.previous.INPUT.read_bytes())['cases']
    for case in regressions:
        query = base.old.make_query(plan, case)
        baseline_ids = base.old.baseline_ids(plan, case, original, members)
        ids, _ = priority.priority_ids(case, by_id, cards, members, intents[case['case_id']], plan['lexical_baseline']['candidate_limit'], 'new_required_first')
        guarded = guard.execute(guard.prepare(query, intents[case['case_id']]), lambda: ids, evidence, limit=query['max_candidates'])['selected_ids']
        pack = shared.fixture_pack(query, shared.literal_result(query, guarded, cards, manifest['pins'], run_id), cards, 'guard-regression')
        historical.append(dict(case_id=case['case_id'], exact_order=guarded == baseline_ids,
            baseline=base.observe(baseline_ids, base.old.baseline_pack(query, baseline_ids, by_id, plan, run_id), case, 'ok'),
            guarded=base.observe(guarded, pack, case, 'ok')))
    summary = dict(original_exact_orders=sum(v['exact_prior_order'] for r in records[:12] for v in r['arms'].values()),
        original_comparisons=60, negative_comparisons=30,
        negative_lists_without_known_conflicts=sum(not v['known_conflicts_top12'] for r in records[12:18] for v in r['arms'].values()),
        negative_packs_without_known_conflicts=sum(not v['known_conflicts_pack'] for r in records[12:18] for v in r['arms'].values()),
        ambiguity_zero_retrieval=sum(v['retrieval_calls']==0 and not v['pack_created'] for r in records[18:] for v in r['arms'].values()),
        ambiguity_comparisons=15, historical_exact_orders=sum(r['exact_order'] for r in historical),
        historical_macros={a:base.old.complete_macro(historical,a) for a in ('baseline','guarded')},
        model_interpretation_evaluated=False, final_answer_evaluated=False, promotion_ready=False)
    if declaration() != declared:
        raise ValueError('source drift during capture')
    shared.write(OUTPUT/'observations.json', dict(declaration_sha256=base.scorer.digest(declared), records=records, historical=historical))
    shared.write(OUTPUT/'summary.json', summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--predeclare', action='store_true')
    actions.add_argument('--run', action='store_true')
    args = parser.parse_args()
    declared = declaration()
    if args.predeclare:
        if (OUTPUT/'declaration.json').exists():
            raise ValueError('preserve prior declaration')
        shared.write(OUTPUT/'declaration.json', declared)
        print(base.scorer.digest(declared))
    else:
        if json.loads((OUTPUT/'declaration.json').read_bytes()) != declared or (OUTPUT/'observations.json').exists():
            raise ValueError('declaration drift or existing capture')
        capture(declared)
