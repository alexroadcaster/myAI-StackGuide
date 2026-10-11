"""Newly frozen functional queries with explicit mixed source exposure.

Reuse the source-validated active bundle and frozen scorer/thresholds. Thirteen
leaf pools are disjoint from the original184 only; communications and the alias
probe are explicitly exposed. Source-only review precedes declaration/capture.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('independent_repair',ROOT/'evals/plugin-v1/run_final_repair.py')
repair=importlib.util.module_from_spec(spec);spec.loader.exec_module(repair)
runner=repair.runner
REPAIR_PLAN=runner.PLAN
PLAN=ROOT/'evals/plugin-v1/final-quality-independent-2026-10-11.json'
OUTPUT=ROOT/'evals/plugin-v1/results/cp04-final-quality-independent-2026-10-11'
QUESTIONS=OUTPUT/'source-review-questions.json'


def load():
    # All active bundle, accepted-policy, source review, corpus, route and
    # historical-input checks remain enforced in the reusable repair loader.
    runner.PLAN=REPAIR_PLAN
    base,cards,by_id,members,registry=repair.load()
    runner.PLAN=PLAN;runner.OUTPUT=OUTPUT
    plan=json.loads(PLAN.read_bytes())
    if plan['base_repair_plan_sha256']!=runner.sha(REPAIR_PLAN):
        raise ValueError('stable repair plan binding mismatch')
    for key in ('pins','artifacts','thresholds','stratification'):
        if plan[key]!=base[key]:
            raise ValueError('active tuple or accepted settings changed: '+key)
    for path,digest in plan['source_hashes'].items():
        if runner.sha(ROOT/path)!=digest:
            raise ValueError('source hash mismatch: '+path)
    old=json.loads((ROOT/'evals/plugin-v1/final-quality-qualified-2026-10-11.json').read_bytes())
    seen={j['github_repository_id'] for c in old['cases'] for j in c['judgments']}
    semantic=[c for c in plan['cases'] if c['metric_family']=='semantic']
    if len(semantic)!=14 or len(plan['cases'])!=15 or len({c['case_id'] for c in plan['cases']})!=15:
        raise ValueError('independent coverage/identity mismatch')
    if {d for c in semantic for d in c['container_domain_ids']}!=set(plan['stratification']['container_ids']):
        raise ValueError('container strata missing')
    if not set(plan['stratification']['required_case_tags'])<={t for c in plan['cases'] for t in c['tags']}:
        raise ValueError('required tags missing')
    for case in plan['cases']:
        ids=[j['github_repository_id'] for j in case['judgments']]
        routed={rid for rid,c in by_id.items() if any(a['category_id'] in members[case['route']] for a in c['classifications'])}
        if len(ids)!=len(set(ids)) or set(ids)!=set(case['universe_ids']):
            raise ValueError('judgment identities invalid')
        if case['metric_family']=='semantic' and set(ids)!=routed:
            raise ValueError('full routed oracle missing')
        if case['metric_family']=='semantic':
            exposure=case['exposure']
            if set(exposure['ids_seen_in_original184'])!=set(ids)&seen:
                raise ValueError('source exposure misclassified')
            if exposure['unseen_claim']=='disjoint_from_original184_only' and set(ids)&seen:
                raise ValueError('exposed source mislabeled unseen')
            if 'container_union' in case['tags'] and not any(r['route_id']==case['route'] and r['route_kind']=='container' for r in registry):
                raise ValueError('false container-union tag')
            if 'secondary_dedupe' in case['tags'] and not any(len(by_id[rid]['classifications'])>1 for rid in ids):
                raise ValueError('false secondary placement tag')
        for row in case['judgments']:
            if type(row['grade']) is not int or not 0<=row['grade']<=3:
                raise ValueError('unresolved role oracle')
            card=by_id[row['github_repository_id']]
            if card['repository']['archived'] and row['constraint']!='denied':
                raise ValueError('archived default oracle error')
            for evidence in row['evidence']:
                value=card
                for key in evidence['pointer'].strip('/').split('/'):
                    value=value[key]
                if value!=evidence['value'] or evidence['source_ref'] not in runner.old.scorer.canonical(card).decode():
                    raise ValueError('source evidence mismatch')
        if case['metric_family']=='semantic':
            positives=sum(j['grade']>0 and j['constraint']!='denied' for j in case['judgments'])
            if not positives or min(case['k'],positives)/positives<plan['thresholds']['required_stratum_recall_at_12_min']:
                raise ValueError('mathematically infeasible recall design')
    if sum(len(c['judgments']) for c in semantic)!=205:
        raise ValueError('source scope changed')
    return plan,cards,by_id,members,registry


def review_binding(path):
    review=json.loads(path.read_bytes())
    if not review.get('reviewer') or review.get('approved') is not True or review.get('unresolved')!=[]:
        raise ValueError('independent source review not complete')
    if review.get('source_questions_sha256')!=runner.sha(QUESTIONS) or review.get('independent_plan_sha256')!=runner.sha(PLAN):
        raise ValueError('independent review hash mismatch')
    return runner.sha(path)


def declaration(plan,review_path,review_sha):
    value=runner.declaration(plan)
    value.update(independent_runner_sha256=runner.sha(Path(__file__)),review_path=review_path.as_posix(),
        source_review_sha256=review_sha,source_questions_sha256=runner.sha(QUESTIONS),
        evidence_kind='newly_frozen_functional_queries_mixed_source_exposure',
        exposure=plan['independent_scope'],globally_unseen_repositories=False,
        candidate='Stable repaired Brief intent planner -> trusted FTS5 -> guard -> context_pack',
        commands=['python -B evals/plugin-v1/run_final_independent.py --predeclare --review '+review_path.as_posix(),
                  'python -B evals/plugin-v1/run_final_independent.py --run --review '+review_path.as_posix()])
    return value


def main():
    parser=argparse.ArgumentParser();modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--predeclare',action='store_true');modes.add_argument('--run',action='store_true')
    parser.add_argument('--review',required=True);args=parser.parse_args()
    try:
        review_path=Path(args.review)
        resolved=(ROOT/review_path).resolve()
        if not resolved.is_relative_to(ROOT) or resolved.stat().st_size>2*1024*1024:
            raise ValueError('invalid source receipt path/size')
        plan,cards,by_id,members,registry=load();review_sha=review_binding(resolved)
        declared=declaration(plan,review_path,review_sha)
        if args.predeclare:
            runner.check_freeze(OUTPUT);runner.write('declaration.json',declared)
            print(json.dumps(dict(declared=True,plan_sha256=runner.sha(PLAN),review_sha256=review_sha)))
            return 0
        if json.loads((OUTPUT/'declaration.json').read_bytes())!=declared:
            raise ValueError('prospective source/runtime declaration changed')
        if (OUTPUT/'observations.json').exists():
            raise ValueError('capture already exists')
        summary=runner.capture(plan,cards,by_id,members,registry)
        records=json.loads((OUTPUT/'observations.json').read_bytes())['records']
        new=[r for r in records if r['metric_family']=='semantic' and not next(c for c in plan['cases'] if c['case_id']==r['case_id'])['exposure']['ids_seen_in_original184']]
        seen=[r for r in records if r['metric_family']=='semantic' and r not in new]
        summary.update(evidence_kind='newly_frozen_functional_queries_mixed_source_exposure',
            source_exposure=plan['independent_scope'],globally_unseen_repositories=False,
            disjoint_source_13case_macro=runner.macro(new,'candidate'),seen_source_new_goal_macro=runner.macro(seen,'candidate'),
            source_review_sha256=review_sha,retrieval_gates_pass=all(v is True for v in summary['gates'].values()),
            promotion_ready=False,acceptance_limit='Numerical grades remain quality-owner agent judgments. Independent review approves source facts/coverage/goal relevance only. Broader historical exposure possible; human usefulness and browser acceptance remain open.')
        runner.write('independent-conclusion.json',summary)
        print(json.dumps({k:summary[k] for k in ('retrieval_gates_pass','candidate_macro','original_literal_macro','gates')}))
        return 0 if summary['retrieval_gates_pass'] else 1
    except (ValueError,KeyError,FileExistsError,FileNotFoundError) as error:
        print(json.dumps(dict(status='invalid_protocol',reason=str(error))))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
