"""Read-only source/shape checks; no candidate lookup, model or scorer run."""
import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
read=lambda p:json.loads((ROOT/p).read_bytes())
plan=read('evals/plugin-v1/final-quality-host-prospective-2026-10-11.json')
base=read('evals/plugin-v1/final-quality-prospective-2026-10-11.json')
accepted=read('evals/plugin-v1/quality-plan.json')
draft=json.loads((OUT/'goal-authoring-draft.json').read_bytes())
questions=json.loads((OUT/'source-review-questions.json').read_bytes())
contract=read('evals/plugin-v1/host-decision-eval-contract-2026-10-11.json')
assert contract['threshold_source']['sha256']==sha(ROOT/contract['threshold_source']['path'])
assert all(plan[k]==base[k] for k in ('pins','artifacts','thresholds','stratification'))
assert all(plan[k]==accepted[k] for k in ('thresholds','stratification'))
assert plan['goal_draft_sha256']==sha(OUT/'goal-authoring-draft.json')
assert plan['source_questions_sha256']==sha(OUT/'source-review-questions.json')
assert plan['capacity_feasibility_sha256']==sha(OUT/'capacity-feasibility.json')
cards=read(plan['artifacts']['cards_path'])['cards']
by_id={c['identity']['github_repository_id']:c for c in cards}
spec=importlib.util.spec_from_file_location('host_source_route_helpers',ROOT/'evals/plugin-v1/run_quality.py')
helpers=importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
# Only a metadata SELECT of the pinned taxonomy route registry; no MATCH,
# COUNT-based preflight, candidate results or relevance computation.
members,registry=helpers.route_members(plan)
semantic=[c for c in plan['cases'] if c['metric_family']=='semantic']
assert len(semantic)==14 and len(plan['cases'])==15
assert len({c['case_id'] for c in plan['cases']})==15
assert {d for c in semantic for d in c['container_domain_ids']}==set(plan['stratification']['container_ids'])
assert set(plan['stratification']['required_case_tags'])<={t for c in plan['cases'] for t in c['tags']}
prior=[read(p) for p in questions['source_reuse_plans']]
prior_ids={j['github_repository_id'] for p in prior for c in p['cases'] for j in c['judgments']}
prior_goals={c['goal'] for p in prior for c in p['cases']}
all_ids=set()
for case,goal,question in zip(semantic,draft['goals'],questions['questions']):
    for key in ('case_id','route','goal','terms','intent','language','universe_ids'):
        assert case[key]==goal[key]==question[key],(case['case_id'],key)
    assert case['goal'] not in prior_goals
    assert Counter([t for group in case['intent']['required_groups'] for t in group]+case['intent']['context_terms'])==Counter(case['terms'])
    routed={rid for rid,card in by_id.items() if any(a['category_id'] in members[case['route']] for a in card['classifications'])}
    judgments={j['github_repository_id']:j for j in case['judgments']}
    assert set(judgments)==set(case['universe_ids'])==routed
    assert len(judgments)==len(case['judgments'])
    assert set(question['full_routed_universe_ids'])==routed
    assert {row['github_repository_id'] for row in question['source_roles']}==routed
    assert set(case['exposure']['source_seen_ids'])==routed & prior_ids
    assert set(case['exposure']['source_disjoint_ids'])==routed-prior_ids
    for row in question['source_roles']:
        card=by_id[row['github_repository_id']]
        assert 'grade' not in row and row['source_card_sha256']==hashlib.sha256(canonical(card)).hexdigest()
        assert row['full_name']==card['identity']['full_name']
        assert row['descriptions']==card['descriptions'] and row['languages']==card['repository']['languages']
    for rid,j in judgments.items():
        card=by_id[rid]
        assert type(j['grade']) is int and 0<=j['grade']<=3
        assert j['full_name']==card['identity']['full_name']
        assert j['constraint']==('denied' if card['repository']['archived'] or card['repository']['availability']!='available' else 'allowed')
        for evidence in j['evidence']:
            value=card
            for key in evidence['pointer'].strip('/').split('/'):
                value=value[key]
            assert value==evidence['value'] and evidence['source_ref'] in canonical(card).decode()
    positives=sum(j['grade']>0 and j['constraint']!='denied' for j in judgments.values())
    assert positives and min(case['k'],positives)/positives>=plan['thresholds']['required_stratum_recall_at_12_min']
    all_ids|=routed
assert len(all_ids)==205 and sum(len(c['judgments']) for c in semantic)==205
assert all_ids<=prior_ids and questions['source_disjoint_ids']==[]
assert questions['primary_new_clarification_records']==17
assert plan['cases'][-1]['metric_family']=='identity' and plan['cases'][-1]['expected_identity_ids']==base['cases'][-1]['expected_identity_ids']
for path in (OUT/'author_plan.py',Path(__file__)):
    ast.parse(path.read_text(encoding='utf-8'))
paths=[ROOT/'evals/plugin-v1/final-quality-host-prospective-2026-10-11.json',ROOT/'evals/plugin-v1/host-decision-eval-contract-2026-10-11.json',OUT/'goal-authoring-draft.json',OUT/'source-review-questions.json',OUT/'capacity-feasibility.json',OUT/'author_plan.py',Path(__file__)]
value=dict(schema_version='cp04_host_source_authoring_static_receipt_v1',checks='passed',
    semantic_cases=14,alias_regression_cases=1,full_route_judgment_rows=205,semantic_unique_ids=205,source_seen=205,source_disjoint=0,
    unknown_grades=0,primary_new_role_records=17,capacity_cases_passed=14,
    metadata_registry_select=True,count_or_match_or_model_calls=0,
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths},
    remaining_gates=['Independent source-only review','Final architect/schema/hash binding','Producer/runtime/source freeze','Actual native/host/literal capture','Resource owner acceptance','Human acceptance'],
    human_acceptance=False,promotion_ready=False)
with (OUT/'static-validation.json').open('x',encoding='utf-8',newline='\n') as stream:
    json.dump(value,stream,indent=2,ensure_ascii=False);stream.write('\n')
print(json.dumps({k:v for k,v in value.items() if k!='hashes'}))
