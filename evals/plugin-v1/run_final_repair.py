"""Explicit active-pin successor of the exposed source-qualified regression.

Old cases, source judgments, thresholds, literal scorer and captures stay frozen.
This runner records a prospective repaired-runtime capture, never a fresh holdout.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('repair_original', ROOT/'evals/plugin-v1/run_final_quality.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
BASE = ROOT/'evals/plugin-v1/final-quality-qualified-2026-10-11.json'
runner.PLAN = ROOT/'evals/plugin-v1/final-quality-repair-2026-10-11.json'
runner.OUTPUT = ROOT/'evals/plugin-v1/results/cp04-final-quality-repair-2026-10-11'


def load():
    plan = json.loads(runner.PLAN.read_bytes())
    base = json.loads(BASE.read_bytes())
    if plan['base_qualified_plan_sha256'] != runner.sha(BASE):
        raise ValueError('qualified source freeze mismatch')
    # Artifact identities may rebind; decision data and acceptance may not.
    for key in ('cases', 'thresholds', 'stratification', 'adjacent_gaps', 'current_adoption_notes'):
        if plan[key] != base[key]:
            raise ValueError('frozen acceptance/cases changed: '+key)
    allowed_pins = {'policy_sha256', 'index_sha256'}
    if any(plan['pins'][key] != value for key, value in base['pins'].items() if key not in allowed_pins):
        raise ValueError('non-policy/index corpus pins changed')
    if {k:v for k,v in plan['artifacts'].items() if k!='manifest_sha256'} != {k:v for k,v in base['artifacts'].items() if k!='manifest_sha256'}:
        raise ValueError('artifact paths/count changed')
    for path, digest in plan['source_hashes'].items():
        if runner.sha(ROOT/path) != digest:
            raise ValueError('active source hash mismatch: '+path)
    for label in ('prior_capture', 'source_review'):
        if runner.sha(ROOT/plan[label+'_path']) != plan[label+'_sha256']:
            raise ValueError('historical receipt mismatch: '+label)
    review = json.loads((ROOT/plan['source_review_path']).read_bytes())
    if review.get('approved') is not True or review.get('unresolved') != [] or review['qualified_plan_sha256'] != runner.sha(BASE):
        raise ValueError('source-only review binding incomplete')
    # Validate all original schema/limits against current assets using an in-memory
    # projection; never repin or rewrite the original accepted plan file.
    projected = json.loads((ROOT/'evals/plugin-v1/quality-plan.json').read_bytes())
    projected['pins'] = copy.deepcopy(plan['pins'])
    projected['artifacts'] = copy.deepcopy(plan['artifacts'])
    runner.old.scorer.validate_quality_plan(projected)
    cards = json.loads((ROOT/plan['artifacts']['cards_path']).read_bytes())['cards']
    by_id = {c['identity']['github_repository_id']:c for c in cards}
    members, registry = runner.old.route_members(projected)
    for case in plan['cases']:
        ids = [j['github_repository_id'] for j in case['judgments']]
        if len(ids)!=len(set(ids)) or set(ids)!=set(case['universe_ids']):
            raise ValueError('judgment universe mismatch')
        routed = {rid for rid,c in by_id.items() if any(a['category_id'] in members[case['route']] for a in c['classifications'])}
        if case['metric_family']=='semantic' and set(ids)!=routed:
            raise ValueError('incomplete routed oracle')
        for row in case['judgments']:
            if type(row['grade']) is not int or not 0<=row['grade']<=3:
                raise ValueError('unqualified source grade')
            card=by_id[row['github_repository_id']]
            for evidence in row['evidence']:
                value=card
                for key in evidence['pointer'].strip('/').split('/'):
                    value=value[key]
                if value!=evidence['value'] or evidence['source_ref'] not in runner.old.scorer.canonical(card).decode():
                    raise ValueError('source evidence mismatch')
    return plan,cards,by_id,members,registry


def declaration(plan):
    value=runner.declaration(plan)
    value.update(repair_runner_sha256=runner.sha(Path(__file__)),
        evidence_kind='exposed_source_qualified_development_regression',fresh_unseen_evidence=False,
        candidate='Active repaired Brief intent planner -> trusted C9 FTS5 -> guard -> context_pack',
        base_qualified_plan_sha256=plan['base_qualified_plan_sha256'],
        prior_capture_sha256=plan['prior_capture_sha256'],source_review_sha256=plan['source_review_sha256'],
        commands=['.venv/Scripts/python.exe -B evals/plugin-v1/run_final_repair.py --predeclare',
                  '.venv/Scripts/python.exe -B evals/plugin-v1/run_final_repair.py --run'])
    return value


def compare(plan,summary):
    prior=json.loads((ROOT/plan['prior_capture_path']).read_bytes())['records']
    current=json.loads((runner.OUTPUT/'observations.json').read_bytes())['records']
    rows=[]
    for old,new in zip(prior,current):
        if old['case_id']!=new['case_id'] or old['payload']!=new['payload']:
            raise ValueError('frozen payload/case changed')
        if old['baseline']['raw_ranked_ids']!=new['baseline']['raw_ranked_ids'] or old['baseline']['ranking']!=new['baseline']['ranking']:
            raise ValueError('original literal baseline changed')
        rows.append(dict(case_id=new['case_id'],prior_fts_ids=old['candidate']['raw_ranked_ids'],
            repaired_fts_ids=new['candidate']['raw_ranked_ids'],prior_metrics=old['candidate']['ranking'],
            repaired_metrics=new['candidate']['ranking'],original_literal_unchanged=True,
            previous_query=old['query'],repaired_query=new['query']))
    summary.update(evidence_kind='exposed_source_qualified_development_regression',fresh_unseen_evidence=False,
        promotion_ready=False,regression_gates_pass=all(v is True for v in summary['gates'].values()),
        prior_capture_sha256=plan['prior_capture_sha256'],cases=rows)
    runner.write('repair-conclusion.json',summary)
    return summary


def main():
    parser=argparse.ArgumentParser()
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--predeclare',action='store_true');modes.add_argument('--run',action='store_true')
    args=parser.parse_args()
    try:
        plan,cards,by_id,members,registry=load();declared=declaration(plan)
        if args.predeclare:
            runner.check_freeze(runner.OUTPUT);runner.write('declaration.json',declared)
            print(json.dumps(dict(declared=True,plan_sha256=runner.sha(runner.PLAN))))
            return 0
        if json.loads((runner.OUTPUT/'declaration.json').read_bytes())!=declared:
            raise ValueError('prospective declaration mismatch')
        if (runner.OUTPUT/'observations.json').exists():
            raise ValueError('capture already exists')
        summary=compare(plan,runner.capture(plan,cards,by_id,members,registry))
        print(json.dumps({k:summary[k] for k in ('regression_gates_pass','candidate_macro','original_literal_macro','gates')}))
        return 0 if summary['regression_gates_pass'] else 1
    except (ValueError,KeyError,FileExistsError,FileNotFoundError) as error:
        print(json.dumps(dict(status='invalid_protocol',reason=str(error))))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
