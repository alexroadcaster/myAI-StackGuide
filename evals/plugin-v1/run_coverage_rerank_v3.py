"""Development-only literal coverage reranking of actual bounded FTS hits."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import uuid
import unicodedata
import platform
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('coverage_shared_query_v3',ROOT/'evals/plugin-v1/run_query_variants_v3.py')
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
scorer=base.scorer
OUTPUT=ROOT/'evals/plugin-v1/results/cp04-v3-2026-10-08/coverage-rerank-development'


def coverage_score(card,terms):
    """Same normalization and distinct term/field pairs as frozen literal baseline."""
    normalized=[unicodedata.normalize('NFKC',term).casefold() for term in terms]
    return sum(any(term in unicodedata.normalize('NFKC',value).casefold() for value in values)
               for values in scorer._baseline_fields(card).values() for term in normalized)


def rerank_pool(result,by_id,terms,cap):
    ceiling=scorer.load_json(ROOT/'specs/retrieval/retrieval-policy.json')['limits']['max_retrieved_hits']
    scorer.require(type(cap) is int and 1<=cap<=ceiling,'pool cap')
    ids=[row['github_repository_id'] for row in result['candidates']]
    scorer.require(result['status'] in {'ok','no_match'} and len(ids)<=cap and len(ids)==len(set(ids)),'invalid fetched pool')
    scorer.require(all(type(i) is int and i>0 and i in by_id for i in ids),'unknown pool identity')
    scorer.require(terms and len(terms)<=8 and len(terms)==len(set(terms)),'invalid original terms')
    scores={i:coverage_score(by_id[i],terms) for i in ids}
    return sorted(ids,key=lambda i:(-scores[i],i)),scores


def selection_envelope(ids,scores):
    return {'transport':'experimental_selection_adapter','executed_c9_rrf':False,
            'ranking_method':'literal distinct term-field coverage, numeric ID ascending ties',
            'ranked_ids':ids,'coverage_scores':{str(i):scores[i] for i in ids},
            'pack_adapter':'existing literal adapter placeholders are selection transport, never observed BM25/RRF'}


def declaration(plan,cases):
    paths=list(base.source_hashes(plan)) + [
        'evals/plugin-v1/run_coverage_rerank_v3.py','evals/plugin-v1/coverage-rerank-v3-contract.md',
        'tests/test_plugin_coverage_rerank_v3.py']
    paths += [str(p.relative_to(ROOT)).replace('\\','/') for p in base.OUTPUT.glob('*.json')]
    return {'schema_version':'cp04_coverage_rerank_declaration_v3','source_hashes':{p:scorer.file_sha256(ROOT/p) for p in sorted(set(paths))},
        'pins':plan['pins'],'thresholds':plan['thresholds'],'literal_baseline':plan['lexical_baseline'],
        'cases':[{'case_id':c['case_id'],'case_sha256':scorer.digest(c),'query':base.old.make_query(plan,c)} for c in cases],
        'method':{'candidate_pool':'only actual single-OR FTS fetched IDs, no fallback or appended IDs',
            'score':'count distinct original query term-field pairs using scorer._baseline_fields; NFKC casefold substring',
            'tie_breaker':'github_repository_id ascending, no BM25 secondary score',
            'zero_coverage':'retain fetched zero-coverage IDs at end, never invent topical grades',
            'missing_pool_risk':'literal-only IDs absent from bounded FTS hits cannot be recovered',
            'field_difference':'FTS category_labels IDs+titles, literal titles only; unchanged and disclosed',
            'raw_result':'preserved actual C9 BM25/RRF result; separate experimental order and transport',
            'metric':'unchanged V2 constrained original ranks; unjudged=null; no alias/identity macro inflation',
            'selection':'no regression against control AND literal macro recall/nDCG; safety/budget must pass'},
        'held_out':'not_run; no sealed prospective cases','promotion_ready':False,'tokens':None,'provider_cost_usd':None}


def capture(plan,cases,cards,by_id,members,declared):
    scorer.require(not any((OUTPUT/n).exists() for n in ('development-observations.json','development-summary.json')),'capture output already exists')
    historical=scorer._load_json_bounded(ROOT/'evals/plugin-v1/results/cp04-v2-2026-10-08/development-observations.json',32*1024*1024)
    previous={c['case_id']:c for c in historical['captures']}
    run_id=str(uuid.uuid4());records=[];captures=[]
    for case in cases:
        query=base.old.make_query(plan,case)
        detail,control=base.execute(query,plan,by_id,case,'coverage-control',run_id)
        raw_result=copy.deepcopy(detail['retrieval'])
        ids,scores=rerank_pool(raw_result,by_id,case['query_terms'],query['max_candidates'])
        candidate_pack=base.old.baseline_pack(query,ids,by_id,plan,run_id)
        baseline_ids=base.old.baseline_ids(plan,case,cards,members)
        baseline_pack=base.old.baseline_pack(query,baseline_ids,by_id,plan,run_id)
        row={'case_id':case['case_id'],'case_sha256':scorer.digest(case),'control':control,
             'literal_top12_ids_outside_fetched_pool':[i for i in baseline_ids[:case['k']] if i not in scores],
             'candidate':base.observe(ids,candidate_pack,case,'ok' if ids else 'no_match'),
             'baseline':base.observe(baseline_ids,baseline_pack,case,'ok' if baseline_ids else 'no_match'),
             'historical_control_equivalent':base.equivalence_projection(raw_result,detail['evidence_pack'])==base.equivalence_projection(previous[case['case_id']]['retrieval'],previous[case['case_id']]['candidate_evidence_pack']),
             'historical_literal_equivalent':baseline_ids==previous[case['case_id']]['baseline_ranked_ids'] and [c['card']['identity']['github_repository_id'] for c in baseline_pack['cards']]==[c['card']['identity']['github_repository_id'] for c in previous[case['case_id']]['baseline_evidence_pack']['cards']] and baseline_pack['exclusions']==previous[case['case_id']]['baseline_evidence_pack']['exclusions']}
        envelope=selection_envelope(ids,scores)
        envelope.update({'evidence_pack':candidate_pack,'query':query,
                         'matched_fields':{str(i):base.old.literal_fields(by_id[i],case['query_terms']) for i in ids},
                         'controlled_input_bytes':len(scorer.canonical(query))+len(scorer.canonical(candidate_pack))})
        policy=scorer.load_json(ROOT/plan['artifacts']['policy_path'])
        scorer.require(envelope['controlled_input_bytes']<=policy['limits']['max_plugin_input_bytes'] and row['candidate']['evidence_pack_bytes']<=query['max_evidence_bytes'],'controlled input cap')
        scorer.require(raw_result==detail['retrieval'] and set(ids)=={r['github_repository_id'] for r in raw_result['candidates']},'raw result or pool modified')
        captures.append({'case_id':case['case_id'],'control':detail,'candidate':envelope,
                         'baseline':{'ranked_ids':baseline_ids,'evidence_pack':baseline_pack,'transport':'literal adapter',
                                     'original_terms':case['query_terms'],
                                     'matched_fields':{str(i):base.old.literal_fields(by_id[i],case['query_terms']) for i in baseline_ids}}})
        records.append(row)
    base.validate_declaration(declared,declaration(plan,cases))
    observation={'schema_version':'cp04_coverage_rerank_observation_v3','evidence_kind':'observed_offline_public_catalog',
        'captured_at':datetime.now(timezone.utc).isoformat(),'run_id':run_id,'pins':plan['pins'],
        'declaration_sha256':scorer.digest(declared),'records':records,'captures':captures,'promotion_ready':False,
        'environment':{'python':sys.version,'sqlite':sqlite3.sqlite_version,'platform':platform.platform()},
        'tokens':None,'provider_cost_usd':None}
    summary=base.summarize(plan,records)
    summary.update({'schema_version':'cp04_coverage_rerank_summary_v3','declaration_sha256':scorer.digest(declared),
                    'candidate_transport':'experimental_selection_adapter; unchanged raw C9 result retained',
                    'candidate_pool_subset_verified':True,'capacity':'not_benchmarked'})
    base.write_json('development-observations.json',observation,output=OUTPUT)
    base.write_json('development-summary.json',summary,output=OUTPUT)
    return summary


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);flags=parser.add_mutually_exclusive_group(required=True)
    flags.add_argument('--predeclare',action='store_true');flags.add_argument('--run-development',action='store_true')
    args=parser.parse_args(argv)
    try:
        plan,cases,cards,by_id,members=base.load_inputs();declared=declaration(plan,cases)
        if args.predeclare:
            base.write_json('declaration.json',declared,output=OUTPUT)
            print(json.dumps({'status':'predeclared','declaration_sha256':scorer.digest(declared)}));return 0
        base.validate_declaration(scorer.load_json(OUTPUT/'declaration.json'),declared)
        summary=capture(plan,cases,cards,by_id,members,declared)
        print(json.dumps({k:summary[k] for k in ('verdict','macro','failed_gates','development_candidate_worth_heldout_review')}))
        return 0 if summary['development_candidate_worth_heldout_review'] else 1
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps({'status':'invalid_input_or_unavailable','error_type':type(error).__name__,'message':str(error)}));return 2


if __name__=='__main__':raise SystemExit(main())
