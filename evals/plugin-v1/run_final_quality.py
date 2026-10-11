"""One prospective source-pinned Brief/FTS vs original-literal evaluation.

No model, network, state writer, rank tuning, catalog update or C8 relabeling.
The additive declaration and observations are exclusively created.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT/'evals/plugin-v1/final-quality-2026-10-11.json'
OUTPUT = ROOT/'evals/plugin-v1/results/cp04-final-quality-2026-10-11'
sys.path.insert(0, str(ROOT/'plugins/myai-stackguide/scripts'))
import recommendation_request as runtime

_spec = importlib.util.spec_from_file_location('final_old_helpers', ROOT/'evals/plugin-v1/run_quality.py')
old = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(old)


def rank(ids, judgments, k):
    unknown = [j['github_repository_id'] for j in judgments if j['grade'] is None]
    if unknown:
        return {'ranking': None, 'valid': False, 'reason': 'incomplete_routed_oracle', 'unknown_ids': unknown}
    constrained = [{**j, 'grade': 0 if j['constraint'] == 'denied' else j['grade']} for j in judgments]
    return old.strict_ranking(ids, constrained, k)

def strata_pass(values, recall, ndcg):
    if not values or any(v is None for v in values):
        return None
    return all(v['recall_at_k'] >= recall and v['ndcg_at_k'] >= ndcg for v in values)

def check_baseline_binding(query, baseline):
    if query != baseline:
        raise ValueError('baseline binding mismatch')

def check_freeze(output):
    if (output/'observations.json').exists():
        raise ValueError('retroactive freeze forbidden')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT/name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def load():
    plan = json.loads(PLAN.read_bytes())
    prior = json.loads((ROOT/'evals/plugin-v1/quality-plan.json').read_bytes())
    old.scorer.validate_quality_plan(prior)
    for key in ('pins', 'artifacts', 'thresholds', 'stratification'):
        if plan[key] != prior[key]:
            raise ValueError('accepted setting changed: '+key)
    for path, digest in plan['source_hashes'].items():
        if sha(ROOT/path) != digest:
            raise ValueError('source hash mismatch: '+path)
    cards = json.loads((ROOT/plan['artifacts']['cards_path']).read_bytes())['cards']
    by_id = {c['identity']['github_repository_id']: c for c in cards}
    members, registry = old.route_members(prior)
    semantic = [c for c in plan['cases'] if c['metric_family'] == 'semantic']
    if set(plan['stratification']['container_ids']) != {v for c in semantic for v in c['container_domain_ids']}:
        raise ValueError('missing container coverage')
    if not set(plan['stratification']['required_case_tags']) <= {v for c in plan['cases'] for v in c['tags']}:
        raise ValueError('missing tag coverage')
    if len({c['case_id'] for c in plan['cases']}) != len(plan['cases']):
        raise ValueError('duplicate case')
    for case in plan['cases']:
        routed = {rid for rid,c in by_id.items() if any(a['category_id'] in members[case['route']] for a in c['classifications'])}
        ids = [j['github_repository_id'] for j in case['judgments']]
        if len(ids) != len(set(ids)) or set(ids) != set(case['universe_ids']):
            raise ValueError('invalid judgment identity coverage')
        if case['metric_family'] == 'semantic' and set(ids) != routed:
            raise ValueError('incomplete declared routed universe')
        for row in case['judgments']:
            if row['grade'] is not None and (type(row['grade']) is not int or not 0<=row['grade']<=3):
                raise ValueError('invalid grade')
            card = by_id[row['github_repository_id']]
            for ev in row['evidence']:
                value = card
                for key in ev['pointer'].strip('/').split('/'):
                    value = value[key]
                if value != ev['value'] or ev['source_ref'] not in old.scorer.canonical(card).decode():
                    raise ValueError('source evidence mismatch')
    return plan, cards, by_id, members, registry


def make_payload(case):
    unknown = dict(text=None,kind='unknown',evidence_refs=[],answer_ids=[],limitation='Synthetic project fixture; not established.')
    details = {name:copy.deepcopy(unknown) for name in runtime.context._DETAIL_FIELDS}
    details.update(non_goals=[],constraint_notes=[],tensions=[])
    brief = dict(schema_version='1.1.0',run_id=str(uuid.uuid5(uuid.NAMESPACE_URL,case['case_id'])),
        brief_id=case['case_id'],brief_version=1,goal=case['goal'],decision='evaluate',project_stage='prototype',
        success_criterion='Identify useful components and first validation; retain caveats.',constraints=case['constraints'],
        observations={'run_id':str(uuid.uuid5(uuid.NAMESPACE_URL,case['case_id']))},assumptions=[],user_corrections=[],context_status='preliminary',
        updated_at='2026-10-11T00:00:00Z',details=details)
    interpretation = dict(brief_sha256=runtime.digest(brief),brief_version=1,language=case['language'],
        route=case['route'],terms=case['terms'],intent=case['intent'],excluded_repository_ids=case['excluded_repository_ids'],
        excluded_dependencies=case['excluded_dependencies'],unresolved=[])
    runtime.prepare_from_brief(brief, interpretation)
    return dict(brief=brief,interpretation=interpretation,public_observations=[])


def declaration(plan):
    paths = ['evals/plugin-v1/run_final_quality.py','tests/test_plugin_final_quality.py',
        'evals/plugin-v1/run_quality.py','evals/plugin-v1/evaluate_retrieval.py',
        'plugins/myai-stackguide/scripts/recommendation_request.py',
        'plugins/myai-stackguide/scripts/request_guard.py','plugins/myai-stackguide/scripts/retrieval.py',
        'plugins/myai-stackguide/scripts/context.py','plugins/myai-stackguide/scripts/context_pack.py',
        'plugins/myai-stackguide/scripts/matcher.py']
    return dict(schema_version='cp04_final_declaration_v1',plan_file_sha256=sha(PLAN),
        plan_canonical_sha256=old.scorer.digest(plan),source_hashes={p:sha(ROOT/p) for p in paths},
        asset_hashes=plan['source_hashes'],pins=plan['pins'],thresholds=plan['thresholds'],
        cases=[dict(case_id=c['case_id'],case_sha256=old.scorer.digest(c),payload_sha256=old.scorer.digest(make_payload(c))) for c in plan['cases']],
        candidate='Active recommendation_request.run -> unchanged trusted C9 FTS5 -> guard -> context_pack',
        baseline='Original literal-field-or-v1, injected transport adapter, exact same prepared query/route/constraints/guard/pack; placeholder RRF only for transport.',
        grading='Full routed oracle; any unknown grade invalidates whole case and official macro, including unretrieved unknowns. No ranked exposure before freeze.',
        commands=['.venv/Scripts/python.exe -B evals/plugin-v1/run_final_quality.py --predeclare',
                  '.venv/Scripts/python.exe -B evals/plugin-v1/run_final_quality.py --run'],
        promotion_ready=False,prior_failed_held_out_retained=True)


def macro(rows, method):
    values = [r[method]['ranking']['ranking'] for r in rows]
    if not values or any(v is None or v['recall_at_k'] is None or v['ndcg_at_k'] is None for v in values):
        return None
    return dict(recall_at_k=sum(v['recall_at_k'] for v in values)/len(values),
        ndcg_at_k=sum(v['ndcg_at_k'] for v in values)/len(values))


def observe(case, result, retrieval_status):
    ids=result.get('raw_ranked_ids',[]); pack=result.get('evidence_pack')
    selected=[c['card']['identity']['github_repository_id'] for c in pack['cards']] if pack else []
    judgments={j['github_repository_id']:j for j in case['judgments']}
    positives={rid for rid,j in judgments.items() if j['grade'] is not None and j['grade']>0 and j['constraint']!='denied'}
    denied={rid for rid,j in judgments.items() if j['constraint']=='denied'}
    allowed={rid for rid,j in judgments.items() if j['constraint']=='allowed'}
    survival=set(ids[:case['k']]) & positives
    false=[e['github_repository_id'] for e in (pack['exclusions'] if pack else []) if e['github_repository_id'] in allowed and
        set(e['reason_codes']) & {'constraint_mismatch','mandatory_fact_unknown','archived','unavailable'}]
    ranking=rank(ids,case['judgments'],case['k'])
    if retrieval_status not in ('ok','no_match'):
        ranking=dict(ranking=None,valid=False,reason='typed_retrieval_failure')
    return dict(ranking=ranking,status=retrieval_status,status_ok=retrieval_status=='ok',
        raw_ranked_ids=ids,packed_ids=selected,hard_constraint_violations=sorted(set(selected)&denied),
        false_exclusions=false,duplicate_canonical_ids=len(ids)-len(set(ids))+len(selected)-len(set(selected)),
        positive_top12_count=len(survival),positive_survived_count=len(survival&set(selected)),
        pack_survival=None if any(j['grade'] is None for j in judgments.values()) or not survival else len(survival&set(selected))/len(survival),
        alias_success=set(case.get('expected_identity_ids',[]))<=set(ids[:case['k']]) if case['metric_family']=='identity' else None,
        controlled_pack_bytes=len(old.scorer.canonical(pack)) if pack else None)


def capture(plan,cards,by_id,members,registry):
    records=[]
    fusion_k=json.loads((ROOT/plan['artifacts']['policy_path']).read_bytes())['rank_fusion']['k']
    for case in plan['cases']:
        payload=make_payload(case); query=runtime.prepare_from_brief(payload['brief'],payload['interpretation'])['catalog_query']
        candidate_raw=[]
        def spy(q, **kwargs):
            check_baseline_binding(query,q)
            raw=runtime.retrieval.retrieve(q,**kwargs);candidate_raw.append(raw);return raw
        candidate=runtime.run(**payload,retrieve=spy)
        filtered=[c for c in cards if any(a['category_id'] in members[case['route']] for a in c['classifications'])]
        literal_ids=old.scorer.lexical_baseline(filtered,case['terms'],query['max_candidates'])
        baseline_raw=[]
        def literal(q, **kwargs):
            check_baseline_binding(query,q)
            raw=dict(schema_version=q['schema_version'],run_id=payload['brief']['run_id'],query_id=q['query_id'],
                query_sha256=runtime.digest(q),brief_version=q['brief_version'],source_mode=q['source_mode'],
                retrieval_engine=q['retrieval_engine'],pins=plan['pins'],status='ok' if literal_ids else 'no_match',
                reason_codes=[] if literal_ids else ['no_hits'],truncated=len(literal_ids)>=q['max_candidates'],
                candidates=[dict(github_repository_id=rid,rank=n,rrf_score=1/(fusion_k+n),
                    matched_fields=old.literal_fields(by_id[rid],case['terms'])) for n,rid in enumerate(literal_ids,1)])
            baseline_raw.append(raw);return raw
        baseline=runtime.run(**payload,retrieve=literal)
        records.append(dict(case_id=case['case_id'],case_sha256=old.scorer.digest(case),payload=payload,
            payload_sha256=old.scorer.digest(payload),query=query,query_sha256=runtime.digest(query),
            split=case['split'],metric_family=case['metric_family'],tags=case['tags'],container_domain_ids=case['container_domain_ids'],
            candidate=observe(case,candidate,candidate_raw[0]['status']),baseline=observe(case,baseline,baseline_raw[0]['status']),
            candidate_capture=candidate,baseline_capture=baseline,candidate_raw_result=candidate_raw[0],
            candidate_capture_sha256=runtime.digest(candidate),baseline_capture_sha256=runtime.digest(baseline),
            baseline_binding_sha256=runtime.digest(query)))
    write('observations.json',dict(schema_version='cp04_final_observations_v1',plan_sha256=sha(PLAN),records=records))
    semantic=[r for r in records if r['metric_family']=='semantic']; thresholds=plan['thresholds']
    candidate=macro(semantic,'candidate');baseline=macro(semantic,'baseline');strata={}
    for field,values in [('tags',plan['stratification']['required_case_tags']),('container_domain_ids',plan['stratification']['container_ids'])]:
        for value in values:
            rows=[r for r in semantic if value in r[field]]
            if value=='historical_alias':continue
            strata[value]=dict(case_ids=[r['case_id'] for r in rows],candidate=macro(rows,'candidate'),baseline=macro(rows,'baseline'))
    gates={}
    for metric,key in [('recall_at_k','held_out_macro_recall_at_12_min'),('ndcg_at_k','held_out_macro_ndcg_at_12_min')]:
        gates[key]=candidate[metric]>=thresholds[key] if candidate else None
        gates['baseline_non_regression_'+metric]=candidate[metric]>=baseline[metric] if candidate and baseline else None
    gates['required_strata']=strata_pass([s['candidate'] for s in strata.values()],thresholds['required_stratum_recall_at_12_min'],thresholds['required_stratum_ndcg_at_12_min'])
    for key in ('hard_constraint_violations','false_exclusions','duplicate_canonical_ids'):
        total=sum(len(r['candidate'][key]) if isinstance(r['candidate'][key],list) else r['candidate'][key] for r in records)
        gates[key]=total<=thresholds[key+'_max']
    aliases=[r['candidate']['alias_success'] for r in records if r['metric_family']=='identity']
    gates['alias_success_rate_min']=sum(aliases)/len(aliases)>=thresholds['alias_success_rate_min'] if aliases else None
    survivor_count=sum(r['candidate']['positive_survived_count'] for r in semantic)
    positive_count=sum(r['candidate']['positive_top12_count'] for r in semantic)
    survival=survivor_count/positive_count if positive_count and all(r['candidate']['pack_survival'] is not None for r in semantic) else None
    gates['evidence_pack_survival_rate_min']=survival>=thresholds['evidence_pack_survival_rate_min'] if survival is not None else None
    gates['all_statuses_match']=all(r['candidate']['status_ok'] for r in records)
    counts={kind:len({row['route_id'] for row in registry if row['route_kind']==kind}) for kind in ('container','category')}
    gates['container_registry_coverage']=counts['container']>=thresholds['container_route_coverage_min']
    gates['leaf_registry_coverage']=counts['category']>=thresholds['leaf_route_coverage_min']
    summary=dict(schema_version='cp04_final_summary_v1',verdict='no_go',promotion_ready=False,
        evidence_kind='observed_local_brief_retrieval_source_judged_agent_proxy',plan_sha256=sha(PLAN),
        candidate_macro=candidate,original_literal_macro=baseline,strata=strata,gates=gates,
        incomplete_oracle_cases=[r['case_id'] for r in semantic if not r['candidate']['ranking']['valid']],
        measured_route_case_count=len(records),registry_counts=counts,
        known_pool_survival_diagnostic=dict(numerator=survivor_count,denominator=positive_count),
        official_pack_survival=survival,adjacent_gaps=plan['adjacent_gaps'],
        interpretation_limit='Preauthored interpretation evaluates deterministic Brief/FTS wiring, not real host interpretation/model behavior. Source sparse facts and all unknowns retained. Human acceptance absent; prior failed held-out is not waived.',
        first_capture_at=datetime.now(timezone.utc).isoformat())
    write('summary.json',summary)
    write('artifact-hashes.json',{name:sha(OUTPUT/name) for name in ('declaration.json','observations.json','summary.json')})
    return summary


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--predeclare',action='store_true');group.add_argument('--run',action='store_true')
    args=parser.parse_args()
    try:
        plan,cards,by_id,members,registry=load();declared=declaration(plan)
        if args.predeclare:
            check_freeze(OUTPUT);write('declaration.json',declared)
            print(json.dumps(dict(declared=True,plan_sha256=sha(PLAN),case_count=len(plan['cases']))));return 0
        if json.loads((OUTPUT/'declaration.json').read_bytes()) != declared:
            raise ValueError('frozen declaration mismatch')
        if (OUTPUT/'observations.json').exists():raise ValueError('capture already exists')
        summary=capture(plan,cards,by_id,members,registry)
        print(json.dumps({k:summary[k] for k in ('verdict','candidate_macro','original_literal_macro','gates','incomplete_oracle_cases')}));return 1
    except (ValueError,KeyError,FileExistsError,FileNotFoundError) as exc:
        print(json.dumps(dict(status='invalid_protocol',reason=str(exc))));return 2


if __name__=='__main__':
    raise SystemExit(main())
