"""Frozen top-12 review and request/projection probes; no ranking activation."""
import argparse
import importlib.util
import json
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('domain_review_previous', ROOT/'evals/plugin-v1/run_new_domain_scenarios.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
base, shared, priority, builder = previous.base, previous.shared, previous.priority, previous.builder
ORACLE = ROOT/'evals/plugin-v1/domain-review-oracle-2026-10-11.json'
CHALLENGES = ROOT/'evals/plugin-v1/domain-adversarial-cases-2026-10-11.json'
OUTPUT = ROOT/'evals/plugin-v1/results/cp04-domain-review-2026-10-11'


def assess(ids, judgments):
    """Describe inspected positions, not full-universe Recall or nDCG."""
    grades = [judgments.get(str(rid)) for rid in ids[:12]]
    return dict(returned=len(grades), full_capabilities=grades.count(3),
                conditional_core=grades.count(2), supplementary=grades.count(1),
                mismatch=grades.count(0), unknown=grades.count(None),
                official_relevance_metrics=None)


def conflicts(ids, forbidden):
    """Only explicit exclusions or documented conflicts establish a violation."""
    lookup = {r['github_repository_id']: r for r in forbidden}
    return [dict(rank=rank, **lookup[rid]) for rank, rid in enumerate(ids[:12], 1) if rid in lookup]


def validate(oracle, challenges, old_cases, cards, members):
    names = {rid: c['identity']['full_name'] for rid, c in cards.items()}
    old_top = json.loads((previous.OUTPUT/'top12.json').read_bytes())
    expected = {c['case_id']: {r['github_repository_id'] for a in c['arms'].values() for r in a['top12']} for c in old_top['cases']}
    if {c['case_id'] for c in oracle['cases']} != set(expected):
        raise ValueError('oracle cases drift')
    for c in oracle['cases']:
        if {r['github_repository_id'] for r in c['assessments']} != expected[c['case_id']]:
            raise ValueError('oracle must cover exactly the old union top12')
        for r in c['assessments']:
            if names[r['github_repository_id']] != r['full_name'] or r['grade'] not in (None, 0, 1, 2, 3) or not r['source_urls']:
                raise ValueError('invalid source-joined judgment')
    if len(challenges) != 9 or len({c['case_id'] for c in challenges}) != 9:
        raise ValueError('expected nine unique challenges')
    for c in challenges:
        priority.previous.ranker.validate_intent(c['query_terms'], c['intent'])
        if c['target_category_id'] not in members:
            raise ValueError('unknown route')
        for r in c['challenge'].get('forbidden', []):
            if names[r['github_repository_id']] != r['full_name'] or not r['basis'] or not r['source_urls']:
                raise ValueError('invalid negative source join')
    if len(old_cases) != 12:
        raise ValueError('expected twelve original scenarios')


def declaration(plan, cases, oracle, challenges, cards, members):
    validate(oracle, challenges, cases, cards, members)
    parent = json.loads((previous.OUTPUT/'declaration.json').read_bytes())
    if previous.declaration(plan, cases, cards, members) != parent:
        raise ValueError('previous frozen candidate/input drift')
    hashes = dict(parent['source_hashes'])
    for path in (ORACLE, CHALLENGES, Path(__file__), ROOT/'tests/test_plugin_domain_review.py',
                 ROOT/'evals/plugin-v1/domain-review-contract.md', previous.OUTPUT/'observations.json',
                 previous.OUTPUT/'top12.json', previous.OUTPUT/'declaration.json'):
        hashes[path.relative_to(ROOT).as_posix()] = builder.sha(path.read_bytes())
    return dict(schema_version='cp04_domain_review_declaration_v1', source_hashes=hashes,
                receipt_sha256=parent['receipt_sha256'], arms=list(previous.ARMS),
                oracle_scope=oracle['scope'], independent_held_out=False, promotion_ready=False)


def run_arm(plan, case, arm, original, by_id, members, cards, manifest, run_id):
    query = base.old.make_query(plan, case)
    if arm == 'control':
        result = base.old.retrieval.retrieve(query, run_id=run_id,
            index_path=ROOT/plan['artifacts']['index_path'],
            manifest_path=ROOT/plan['artifacts']['manifest_path'],
            policy_path=ROOT/plan['artifacts']['policy_path'])
        ids = [r['github_repository_id'] for r in result['candidates']]
        pack = base.old.context_pack.build_evidence_pack(query, result, {rid: by_id[rid] for rid in ids},
            pack_id='domain-review-'+case['case_id'], max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
        status = result['status']
    elif arm == 'baseline':
        ids = base.old.baseline_ids(plan, case, original, members)
        pack = base.old.baseline_pack(query, ids, by_id, plan, run_id)
        status = 'literal_adapter'
    else:
        if arm == 'separated':
            ids, _ = priority.previous.separated(case, by_id, cards, members, case['intent'], plan['lexical_baseline']['candidate_limit'])
        else:
            ids, _ = priority.priority_ids(case, by_id, cards, members, case['intent'], plan['lexical_baseline']['candidate_limit'], arm)
        result = shared.literal_result(query, ids, cards, manifest['pins'], run_id)
        pack = shared.fixture_pack(query, result, cards, arm)
        status = 'literal_adapter'
    packed = [r['card']['identity']['github_repository_id'] for r in pack['cards']]
    return ids, packed, status, query, pack


def capture(plan, cases, oracle, challenges, original, by_id, members, regressions, declared):
    manifest, cards, verification = previous.verified_package(declared['receipt_sha256'])
    run_id = str(uuid.uuid4())
    prior = json.loads((previous.OUTPUT/'observations.json').read_bytes())
    prior_rows = {r['case_id']: r for r in prior['records']}
    judges = {c['case_id']: {str(r['github_repository_id']): r['grade'] for r in c['assessments']} for c in oracle['cases']}
    records = []
    for case in cases + challenges:
        row = dict(case_id=case['case_id'], user_goal=case['user_goal'], challenge=case.get('challenge'), arms={})
        for arm in previous.ARMS:
            ids, packed, status, query, pack = run_arm(plan, case, arm, original, by_id, members, cards, manifest, run_id)
            judgment = judges.get(case['case_id'], {})
            record = dict(status=status, ranked_ids=ids, packed_ids=packed, query=query,
                intent=case['intent'], top12=[dict(rank=i, github_repository_id=rid,
                    full_name=by_id[rid]['identity']['full_name'], grade=judgment.get(str(rid))) for i, rid in enumerate(ids[:12], 1)],
                assessment=assess(ids, judgment), evidence_pack_sha256=base.scorer.digest(pack))
            if case['case_id'] in prior_rows:
                record['exact_prior_order'] = ids == prior_rows[case['case_id']][arm]['ranked_ids']
            else:
                challenge = case['challenge']
                if challenge['kind'] == 'negative':
                    record['known_conflicts_top12'] = conflicts(ids, challenge['forbidden'])
                    record['known_conflicts_pack'] = conflicts(packed, challenge['forbidden'])
                    record['known_alternative_ranks'] = {str(r): ids.index(r)+1 if r in ids else None for r in challenge['known_alternatives']}
                    record['negative_condition_consumed'] = False
                else:
                    record['clarification_evaluated'] = False
            row['arms'][arm] = record
        records.append(row)
    intents = json.loads(priority.previous.INPUT.read_bytes())['cases']
    regression_rows = []
    for case in regressions:
        baseline_ids = base.old.baseline_ids(plan, case, original, members)
        query = base.old.make_query(plan, case)
        baseline_pack = base.old.baseline_pack(query, baseline_ids, by_id, plan, run_id)
        ids, _ = priority.priority_ids(case, by_id, cards, members, intents[case['case_id']], plan['lexical_baseline']['candidate_limit'], 'new_required_first')
        result = shared.literal_result(query, ids, cards, manifest['pins'], run_id)
        pack = shared.fixture_pack(query, result, cards, 'regression')
        regression_rows.append(dict(case_id=case['case_id'], exact_order=ids == baseline_ids,
            baseline=base.observe(baseline_ids, baseline_pack, case, 'ok'),
            new_required_first=base.observe(ids, pack, case, 'ok')))
    rejection = base.old.retrieval.retrieve(base.old.make_query(plan, cases[0]), run_id=run_id,
        index_path=previous.PACKAGE/builder.index.INDEX.name, manifest_path=previous.PACKAGE/builder.index.MANIFEST.name,
        policy_path=previous.PACKAGE/builder.index.PACKAGED_POLICY.name)
    if rejection['status'] != 'index_incompatible':
        raise ValueError('candidate guard failed')
    try:
        base.old.context_pack.build_evidence_pack(query, result, cards, pack_id='domain-negative',
            max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
    except ValueError:
        pack_rejected = True
    else:
        raise ValueError('public pack accepted unactivated candidate')
    if declaration(plan, cases, oracle, challenges, by_id, members) != declared:
        raise ValueError('input drift during capture')
    summary = dict(case_count=len(records), reviewed_original_cases=12, source_repositories=len(oracle['sources']),
        reviewed_pairs=sum(len(c['assessments']) for c in oracle['cases']), negative_cases=6, ambiguous_cases=3,
        arms={}, historical_regressions=dict(exact_orders=sum(r['exact_order'] for r in regression_rows), cases=len(regression_rows),
            macros={a: base.old.complete_macro(regression_rows, a) for a in ('baseline', 'new_required_first')}),
        candidate_public_rejected=rejection['status'], candidate_public_pack_rejected=pack_rejected,
        package_verification=verification,
        official_relevance_metrics=None, independent_held_out=False, promotion_ready=False,
        model_run=False, negative_projection_supported=False, ambiguity_routing_evaluated=False)
    for arm in previous.ARMS:
        reviewed = [r['arms'][arm] for r in records[:12]]
        neg = [r['arms'][arm] for r in records if r['challenge'] and r['challenge']['kind'] == 'negative']
        summary['arms'][arm] = dict(exact_prior_orders=sum(r['exact_prior_order'] for r in reviewed),
            totals={k: sum(r['assessment'][k] for r in reviewed) for k in ('returned', 'full_capabilities', 'conditional_core', 'supplementary', 'mismatch', 'unknown')},
            negative_cases_with_known_conflict_top12=sum(bool(r['known_conflicts_top12']) for r in neg),
            negative_cases_with_known_conflict_pack=sum(bool(r['known_conflicts_pack']) for r in neg),
            negative_conflict_slots_top12=sum(len(r['known_conflicts_top12']) for r in neg))
    shared.write(OUTPUT/'observations.json', dict(run_id=run_id, declaration_sha256=base.scorer.digest(declared),
        records=records, historical_regressions=regression_rows))
    shared.write(OUTPUT/'summary.json', summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--predeclare', action='store_true')
    actions.add_argument('--run', action='store_true')
    args = parser.parse_args()
    plan, regressions, original, by_id, members = base.load_inputs()
    cases = json.loads(previous.INPUT.read_bytes())['cases']
    oracle = json.loads(ORACLE.read_bytes())
    challenges = json.loads(CHALLENGES.read_bytes())['cases']
    declared = declaration(plan, cases, oracle, challenges, by_id, members)
    if args.predeclare:
        if (OUTPUT/'declaration.json').exists():
            raise ValueError('do not overwrite a declaration')
        shared.write(OUTPUT/'declaration.json', declared)
        print(json.dumps(dict(predeclared=base.scorer.digest(declared))))
    else:
        saved = json.loads((OUTPUT/'declaration.json').read_bytes())
        if saved != declared or (OUTPUT/'observations.json').exists():
            raise ValueError('declaration drift or existing capture')
        capture(plan, cases, oracle, challenges, original, by_id, members, regressions, saved)
