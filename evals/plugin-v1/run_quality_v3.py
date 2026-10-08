"""Fresh held-out V3 evaluator; source execution waits for owner freeze gates."""
from __future__ import annotations
import copy
import argparse
from datetime import datetime, timezone
import json
import platform
import sqlite3
import sys
import uuid
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('quality_v3_development_helpers', ROOT / 'evals/plugin-v1/run_coverage_rerank_v3.py')
coverage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coverage)
scorer = coverage.scorer
spec = importlib.util.spec_from_file_location('quality_v3_source_validator', ROOT/'evals/plugin-v1/validate_oracle_v3.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
OUTPUT=ROOT/'evals/plugin-v1/results/cp04-v3-2026-10-08/held-out'


def supported_ranking(ids, judgments, k):
    """Never interpret returned unknowns as zero or omit unavailable case metrics."""
    by_id = {row['github_repository_id']: row for row in judgments}
    missing = [i for i in ids if i not in by_id]
    unknown = [i for i in ids if i in by_id and by_id[i]['grade'] is None]
    diagnostics = {'unknown_universe_count': sum(r['grade'] is None for r in judgments),
                   'unknown_returned_ids': unknown, 'unjudged_ids': missing}
    if len(ids) != len(set(ids)) or missing or unknown:
        return {'valid': False, 'ranking': None, 'reason': 'duplicate_or_unjudged_or_unknown', **diagnostics}
    known = [row for row in judgments if row['grade'] is not None]
    grades = {row['github_repository_id']: 0 if row['constraint'] == 'denied' else row['grade'] for row in known}
    if not any(grade > 0 for grade in grades.values()):
        return {'valid': False, 'ranking': None, 'reason': 'no_supported_positive_denominator', **diagnostics}
    return {'valid': True, 'ranking': scorer.ranking_metrics(ids, grades, k), 'reason': None, **diagnostics}


def complete_macro(records, arm):
    values = [record[arm]['ranking']['ranking'] for record in records]
    if not values or any(v is None or v['recall_at_k'] is None or v['ndcg_at_k'] is None for v in values):
        return {'complete': False, 'recall_at_12': None, 'ndcg_at_12': None}
    return {'complete': True, 'recall_at_12': sum(v['recall_at_k'] for v in values)/len(values),
            'ndcg_at_12': sum(v['ndcg_at_k'] for v in values)/len(values)}


def validate_freeze_gate(gate, expected_bindings):
    """Owner and independent review bindings must precede the first held-out call."""
    scorer.require(gate.get('accepted') is True and gate.get('independent_review_completed') is True and
                   isinstance(gate.get('reviewer'), str) and gate['reviewer'].strip(), 'held-out source review not accepted')
    for key, value in expected_bindings.items():
        scorer.require(gate.get(key) == value, 'held-out freeze binding mismatch: '+key)


def restore_rank_fidelity(projected_pack, raw_result):
    """Restore actual retrieval provenance after experimental selection transport."""
    pack = copy.deepcopy(projected_pack)
    raw = {row['github_repository_id']: row for row in raw_result['candidates']}
    for item in pack['cards']:
        repo_id = item['card']['identity']['github_repository_id']
        scorer.require(repo_id in raw, 'projection contains nonretrieved ID')
        item['selection_rank'] = item['retrieval_rank']
        item['retrieval_rank'] = raw[repo_id]['rank']
        item['rrf_score'] = raw[repo_id]['rrf_score']
        item['matched_fields'] = copy.deepcopy(raw[repo_id]['matched_fields'])
    return {'transport': 'experimental_pack_projection', 'experimental_notcanonical': True,
            'current_policy_fulfilled': False, 'executed_c9_rrf': False, 'projection': pack}


def normalized_cases(oracle):
    result=[]
    for source in oracle['cases']:
        case=copy.deepcopy(source)
        case['judgments']=[{**row,'grade':row['relevance_grade'],
            'constraint':'denied' if row['denied_by_frozen_constraints'] else
            'unknown' if row['constraint_source']['values']['archived'] is None else 'allowed'} for row in source['judgments']]
        result.append(case)
    return result


def declaration(oracle,plan,cases):
    paths=list(oracle['source_hashes'])+['evals/plugin-v1/quality-oracle-v3-source.json','evals/plugin-v1/oracle-v3-protocol.md',
        'evals/plugin-v1/validate_oracle_v3.py','evals/plugin-v1/run_quality_v3.py','evals/plugin-v1/runner-v3-contract.md',
        'tests/test_plugin_quality_oracle_v3.py','tests/test_plugin_quality_runner_v3.py',
        'evals/plugin-v1/run_quality.py','evals/plugin-v1/evaluate_retrieval.py',
        'evals/plugin-v1/run_quality_v2.py','evals/plugin-v1/run_query_variants_v3.py','evals/plugin-v1/run_coverage_rerank_v3.py',
        'plugins/myai-stackguide/scripts/retrieval.py','plugins/myai-stackguide/scripts/context_pack.py',
        'plugins/myai-stackguide/scripts/matcher.py',plan['artifacts']['index_path']]
    for directory in ('cp04-v2-2026-10-08','cp04-v3-2026-10-08/query-variants-development','cp04-v3-2026-10-08/coverage-rerank-development'):
        paths += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'evals/plugin-v1/results'/directory).glob('*.json')]
    return {'schema_version':'cp04_fresh_declaration_v3','oracle_sha256':scorer.file_sha256(validator.SOURCE),
        'source_hashes':{p:scorer.file_sha256(ROOT/p) for p in sorted(set(paths))},'pins':oracle['bundle_pins'],
        'thresholds':plan['thresholds'],'cases':[{'case_id':c['case_id'],'case_sha256':scorer.digest(c),
            'query':coverage.base.old.make_query(plan,c)} for c in cases],
        'method':{'arms':['control','candidate','baseline'],'candidate':'literal coverage on actual singleOR FTS pool; numericID tie',
            'metric':'source-supported positive non-denied; unknown anywhere returned=>null; all14 semantic cases mandatory',
            'diagnostic':'secondary case reported separately, excluded from macro',
            'pack':'raw canonical pack retained; candidate experimental projection restores original rank/RRF and adds selection_rank',
            'baseline':'unchanged literal-field-or-v1; adapter placeholder provenance explicitly noncanonical',
            'field_difference':'FTS category IDs+titles versus literal titles retained',
            'activation':'current exact runtime hashes with actual raw captures; no shipping rerank activation'},
        'promotion_ready':False,'human_calibrated':False}


def expected_gate(declared):
    return {'oracle_sha256':declared['oracle_sha256'],
        'declaration_sha256':scorer.digest(declared),
        'runtime_sha256':declared['source_hashes']['plugins/myai-stackguide/scripts/retrieval.py'],
        'pack_runtime_sha256':declared['source_hashes']['plugins/myai-stackguide/scripts/context_pack.py']}


def observe(ids,pack,case,status):
    rows=case['judgments'];selected=[i['card']['identity']['github_repository_id'] for i in pack['cards']]
    denied={r['github_repository_id'] for r in rows if r['constraint']=='denied'}
    allowed={r['github_repository_id'] for r in rows if r['constraint']=='allowed'}
    positive={r['github_repository_id'] for r in rows if r['grade'] is not None and r['grade']>0 and r['constraint']!='denied'}
    useful=set(ids[:case['k']])&positive
    ranking=supported_ranking(ids,rows,case['k'])
    if status not in ('ok','no_match'):ranking={**ranking,'valid':False,'ranking':None,'reason':'typed_retrieval_failure'}
    return {'ranked_ids':ids,'detailed_card_ids':selected,'ranking':ranking,'retrieval_status':status,
        'unknown_raw_positions':[{'github_repository_id':i,'rank':rank} for rank,i in enumerate(ids,1) if i in ranking['unknown_returned_ids']],
        'known_relevant_top12_retrieved':sorted(useful),'known_relevant_survived_pack':sorted(useful&set(selected)),
        'hard_constraint_violations':sorted(set(selected)&denied),
        'false_exclusions':[e['github_repository_id'] for e in pack['exclusions'] if e['github_repository_id'] in allowed and
            set(e['reason_codes'])&{'constraint_mismatch','mandatory_fact_unknown','archived','unavailable'}],
        'duplicate_canonical_ids':len(ids)-len(set(ids))+len(selected)-len(set(selected)),
        'pack_survival_rate':len(useful&set(selected))/len(useful) if useful else None,
        'evidence_pack_bytes':len(scorer.canonical(pack)),'exclusions':pack['exclusions']}


def summarize(oracle,plan,records):
    semantic=[r for r in records if r['include_in_14_domain_macro']]
    thresholds=plan['thresholds'];arms={}
    for arm in ('control','candidate','baseline'):
        macro=complete_macro(semantic,arm);gates={}
        for metric,threshold in [('recall_at_12','held_out_macro_recall_at_12_min'),('ndcg_at_12','held_out_macro_ndcg_at_12_min')]:
            value=macro[metric];gates[threshold]=None if value is None else value>=thresholds[threshold]
            reference=complete_macro(semantic,'baseline')[metric]
            delta='candidate_not_worse_than_baseline_'+('recall' if metric=='recall_at_12' else 'ndcg')+'_delta_min'
            gates[delta]=None if value is None or reference is None else value-reference>=thresholds[delta]
        strata={}
        for kind,values in [('container_domain_ids',oracle['coverage']['container_domain_ids']),
            ('tags', ['thin_leaf','dense_leaf','baseline_cohort','expansion_cohort','dual_descriptions','lexical_en','lexical_ru'])]:
            strata[kind]={v:complete_macro([r for r in semantic if v in r[kind]],arm) for v in values}
        gates['required_source_strata']=all(s['complete'] and s['recall_at_12']>=thresholds['required_stratum_recall_at_12_min'] and
            s['ndcg_at_12']>=thresholds['required_stratum_ndcg_at_12_min'] for family in strata.values() for s in family.values())
        gates['complete_semantic_cases']=len(semantic)==oracle['split_policy']['held_out_semantic_case_count']
        gates['complete_observed_cases']=len(records)==len(oracle['cases'])
        gates['valid_all_raw_rankings_and_status']=all(r[arm]['ranking']['valid'] and r[arm]['retrieval_status'] in ('ok','no_match') for r in records)
        for name in ('hard_constraint_violations','false_exclusions','duplicate_canonical_ids'):
            total=sum(len(r[arm][name]) if isinstance(r[arm][name],list) else r[arm][name] for r in records)
            gates[name]=total<=thresholds[name+'_max']
        n=sum(len(r[arm]['known_relevant_survived_pack']) for r in records);d=sum(len(r[arm]['known_relevant_top12_retrieved']) for r in records)
        gates['pack_survival']=n/d>=thresholds['evidence_pack_survival_rate_min'] if d else None
        gates['evidence_budgets']=all(r[arm]['evidence_pack_bytes']<=plan['candidate_route']['max_evidence_bytes'] and
            r[arm]['controlled_input_bytes']<=oracle['policy_refs']['limits']['value']['max_plugin_input_bytes'] for r in records)
        arms[arm]={'macro':macro,'strata':strata,'gates':gates,'failed_gates':[k for k,v in gates.items() if v is False],
            'unmeasured_gates':[k for k,v in gates.items() if v is None],
            'source_supported_semantic_verdict':'semantic_pass_needs_owner_acceptance' if all(v is True for v in gates.values()) else 'no_go',
            'pack_survival_rate':n/d if d else None}
    return {'schema_version':'cp04_fresh_summary_v3','arms':arms,'record_count':len(records),'semantic_case_count':len(semantic),
        'diagnostic_records':[r for r in records if not r['include_in_14_domain_macro']],
        'unknown_universe_total':sum(len(c['unknown_ids']) for c in oracle['cases']),
        'broader_gaps':['human calibration/usefulness','browser/RU-EN meaning/no-call switch','state/publication recovery',
            'alias identity probes','container semantic queries','full deterministic route sweep','actual/synthetic capacity'],
        'product_quality_verdict':'no_go','promotion_ready':False,'human_calibrated':False}


def capture(oracle,plan,cases,cards,by_id,declared):
    scorer.require(not any((OUTPUT/n).exists() for n in ('observations.json','summary.json')),'fresh output already exists')
    records=[];captures=[];run_id=str(uuid.uuid4())
    for case in cases:
        query=coverage.base.old.make_query(plan,case)
        detail, _=coverage.base.execute(query,plan,by_id,{**case,'judgments':[r for r in case['judgments'] if r['grade'] is not None]},'fresh-control',run_id)
        raw=detail['retrieval'];raw_ids=[r['github_repository_id'] for r in raw['candidates']]
        candidate_ids,scores=coverage.rerank_pool(raw,by_id,case['query_terms'],query['max_candidates']) if raw['status'] in ('ok','no_match') else ([],{})
        adapter=copy.deepcopy(raw);adapter['candidates']=[{**next(r for r in raw['candidates'] if r['github_repository_id']==i),'rank':rank} for rank,i in enumerate(candidate_ids,1)]
        projected=coverage.base.old.context_pack.build_evidence_pack(query,adapter,{i:by_id[i] for i in raw_ids},
            pack_id='fresh-selection-'+case['case_id'],max_cards=query['max_cards'],max_evidence_bytes=query['max_evidence_bytes'])
        candidate=restore_rank_fidelity(projected,raw)
        routed=[card for card in cards if card['identity']['github_repository_id'] in case['universe_ids']]
        literal=scorer.lexical_baseline(routed,case['query_terms'],query['max_candidates'])
        literal_pack=coverage.base.old.baseline_pack(query,literal,by_id,plan,run_id)
        row={k:case[k] for k in ('case_id','include_in_14_domain_macro','container_domain_ids','tags')}
        for arm,ids,pack,status in [('control',raw_ids,detail['evidence_pack'],raw['status']),
                                  ('candidate',candidate_ids,candidate['projection'],raw['status']),
                                  ('baseline',literal,literal_pack,'ok' if literal else 'no_match')]:
            row[arm]=observe(ids,pack,case,status)
            row[arm]['controlled_input_bytes']=len(scorer.canonical(query))+len(scorer.canonical(pack))
        records.append(row)
        captures.append({'case_id':case['case_id'],'case_sha256':scorer.digest(case),'query':query,'control':detail,
            'candidate':{**candidate,'coverage_scores':scores,'ranked_ids':candidate_ids,'raw_c9_result_sha256':scorer.digest(raw)},
            'baseline':{'ranked_ids':literal,'evidence_pack':literal_pack,'transport':'experimental_literal_adapter_notcanonical','executed_c9_rrf':False}})
    coverage.base.validate_declaration(declared,declaration(oracle,plan,cases))
    observation={'schema_version':'cp04_fresh_observation_v3','captured_at':datetime.now(timezone.utc).isoformat(),
        'run_id':run_id,'evidence_kind':'observed_offline_public_catalog','declaration_sha256':scorer.digest(declared),
        'pins':oracle['bundle_pins'],'records':records,'captures':captures,'promotion_ready':False,
        'environment':{'python':sys.version,'sqlite':sqlite3.sqlite_version,'platform':platform.platform()},'tokens':None,'provider_cost_usd':None}
    summary=summarize(oracle,plan,records);summary['declaration_sha256']=scorer.digest(declared)
    coverage.base.write_json('observations.json',observation,output=OUTPUT)
    coverage.base.write_json('summary.json',summary,output=OUTPUT)
    return summary


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);flags=parser.add_mutually_exclusive_group(required=True)
    flags.add_argument('--predeclare',action='store_true');flags.add_argument('--capture',action='store_true')
    parser.add_argument('--gate',type=Path);args=parser.parse_args(argv)
    try:
        oracle,plan,cards,by_id=validator.load_source();cases=normalized_cases(oracle)
        # Production query validation before declaration, without retrieval.
        manifest=scorer.load_json(ROOT/plan['artifacts']['manifest_path']);policy=scorer.load_json(ROOT/plan['artifacts']['policy_path'])
        for case in cases:coverage.base.old.retrieval.validate_query(coverage.base.old.make_query(plan,case),manifest=manifest,policy=policy)
        declared=declaration(oracle,plan,cases)
        if args.predeclare:
            coverage.base.write_json('declaration.json',declared,output=OUTPUT)
            print(json.dumps({'status':'predeclared','declaration_sha256':scorer.digest(declared)}));return 0
        scorer.require(args.gate is not None,'owner gate required')
        saved=scorer.load_json(OUTPUT/'declaration.json');coverage.base.validate_declaration(saved,declared)
        gate=scorer.load_json(args.gate);validate_freeze_gate(gate,expected_gate(declared))
        review=(ROOT/gate['independent_review_path']).resolve()
        scorer.require(review.is_relative_to(ROOT) and scorer.file_sha256(review)==gate['independent_review_sha256'],'independent review artifact mismatch')
        summary=capture(oracle,plan,cases,cards,by_id,declared)
        print(json.dumps({'arms':{k:{'macro':v['macro'],'verdict':v['source_supported_semantic_verdict'],'failed_gates':v['failed_gates']} for k,v in summary['arms'].items()},'promotion_ready':False}))
        return 0 if any(a['source_supported_semantic_verdict']=='semantic_pass_needs_owner_acceptance' for a in summary['arms'].values()) else 1
    except (ValueError,KeyError,OSError,TypeError,IndexError) as error:
        print(json.dumps({'status':'invalid_or_unavailable','error_type':type(error).__name__,'message':str(error)}));return 2


if __name__ == '__main__':
    raise SystemExit(main())
