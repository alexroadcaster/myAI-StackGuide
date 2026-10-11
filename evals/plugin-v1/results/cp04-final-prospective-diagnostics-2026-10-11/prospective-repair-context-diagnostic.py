"""Three bounded context-support arms; reuse source-pinned native diagnostic setup."""
import hashlib
setup_path=__import__('pathlib').Path(__file__).with_name('prospective-repair-diagnostic.py')
exec(compile(setup_path.read_text(encoding='utf-8').split('output=dict(')[0],str(setup_path),'exec'))
base_prepare=prepare
MODES=['context_only','atoms_context','phrase_context']
def prepare(mode,brief,interpretation):
    request=base_prepare('atoms_leaf',brief,interpretation)
    required=[t for g in interpretation['intent']['required_groups'] for t in g]
    context=interpretation['intent']['context_terms']
    if request['query_derivation']['original_match_count']>=request['catalog_query']['max_cards'] or not atoms(required) or not context:return request
    extra=context if mode=='context_only' else context+(atoms(required) if mode=='atoms_context' else [t for t in required if atoms([t])])
    q2=append_unique([],extra)
    request['catalog_query']['variants'].append(dict(variant_id='q2',terms=q2))
    runtime.retrieval.validate_query(request['catalog_query'],manifest=manifest,policy=policy)
    return request
output=dict(evidence_kind='exposed_development_diagnostic_only',activation=False,profiles=MODES,source_hashes={str(p.relative_to(ROOT)):runner.sha(p) for p in [Path(__file__),setup_path]},suites=[],formal=[])
for name in ['rank-repair-regression','prospective']:
    plan_path=ROOT/('evals/plugin-v1/final-quality-'+name+'-2026-10-11.json')
    capture_path=ROOT/('evals/plugin-v1/results/cp04-final-quality-'+name+'-2026-10-11/observations.json')
    plan=json.loads(plan_path.read_bytes());capture=json.loads(capture_path.read_bytes());frozen={r['case_id']:r for r in capture['records']}
    rows=[]
    for case in plan['cases']:
        prior=frozen[case['case_id']]
        row=dict(case_id=case['case_id'],metric_family=case['metric_family'],tags=case['tags'],container_domain_ids=case['container_domain_ids'],baseline=prior['baseline'])
        for mode in MODES:
            payload=copy.deepcopy(prior['payload'])
            planned=prepare(mode,payload['brief'],payload['interpretation'])
            if name=='rank-repair-regression':
                assert planned['catalog_query']==prior['query'],case['case_id']+' changed original30 query'
                row[mode]=prior['candidate'];continue
            runtime.prepare_from_brief=lambda b,i:prepare(mode,b,i)
            captured=[]
            def spy(query,**kwargs):
                result=runtime.retrieval.retrieve(query,**kwargs);captured.append(result);return result
            result=runtime.run(**payload,retrieve=spy)
            observed=runner.observe(case,result,captured[0]['status'])
            observed.update(query_variants=result['request']['catalog_query']['variants'],retrieved_hits=captured[0]['retrieved_hits'])
            row[mode]=observed
        rows.append(row)
    semantic=[r for r in rows if r['metric_family']=='semantic'];summary={}
    for mode in MODES:
        strata={}
        for field,values in [('tags',plan['stratification']['required_case_tags']),('container_domain_ids',plan['stratification']['container_ids'])]:
            for value in values:
                selected=[r for r in semantic if value in r[field]]
                if selected:strata[value]=runner.macro(selected,mode)
        summary[mode]=dict(macro=runner.macro(semantic,mode),failed_cases={r['case_id']:r[mode]['ranking']['ranking'] for r in semantic if r[mode]['ranking']['ranking']['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or r[mode]['ranking']['ranking']['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},failed_strata={k:v for k,v in strata.items() if v['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or v['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},hard_failures=sum(len(r[mode]['hard_constraint_violations'])+len(r[mode]['false_exclusions'])+r[mode]['duplicate_canonical_ids'] for r in rows),pack_survival=min(r[mode]['pack_survival'] for r in semantic if r[mode]['pack_survival'] is not None),alias_success=all(r[mode]['alias_success'] for r in rows if r['metric_family']=='identity'))
    output['suites'].append(dict(name=name,plan_sha256=runner.sha(plan_path),capture_sha256=runner.sha(capture_path),summary=summary,records=rows));print(name,json.dumps(summary),flush=True)
formal_path=ROOT/'evals/plugin-v1/results/cp04-final-current-calibration-2026-10-11/cases.json'
for case in json.loads(formal_path.read_bytes()):
    row=dict(case_id=case['case_id'],profiles={})
    for mode in ['atoms_leaf']+MODES:
        runtime.prepare_from_brief=(lambda b,i:base_prepare('atoms_leaf',b,i)) if mode=='atoms_leaf' else (lambda b,i:prepare(mode,b,i))
        result=runtime.run(brief=copy.deepcopy(case['brief']),interpretation=copy.deepcopy(case['interpretation']))
        query=result['request']['catalog_query'];pack=result['evidence_pack']
        old=case['result']
        row['profiles'][mode]=dict(query_identical=query==old['request']['catalog_query'],pack_identical=pack==old['evidence_pack'],query_sha256=runtime.digest(query),pack_sha256=runtime.digest(pack))
    output['formal'].append(row)
runtime.prepare_from_brief=original_prepare
destination=ROOT/'work/cp04-final/prospective-repair-context-diagnostic-results.json'
with destination.open('x',encoding='utf-8',newline='\n') as stream:json.dump(output,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
print('formal',json.dumps(output['formal']),flush=True)
