"""Reuse one inference arm; soft priority only after needed required-phrase expansion."""
setup_path=__import__('pathlib').Path(__file__).with_name('prospective-repair-diagnostic.py')
exec(compile(setup_path.read_text(encoding='utf-8').split('output=dict(')[0],str(setup_path),'exec'))
tiny_path=ROOT/'work/cp04-final/prospective-repair-tiny-diagnostic-results.json'
tiny=json.loads(tiny_path.read_bytes());initial=json.loads((ROOT/'work/cp04-final/prospective-repair-diagnostic-results.json').read_bytes())
def triggered(case,observation):
    required=[t for g in case['intent']['required_groups'] for t in g]
    original={runtime.retrieval._normalize(t) for t in case['terms']}
    extra={runtime.retrieval._normalize(t) for t in atoms(required)}-original
    actual={runtime.retrieval._normalize(t) for t in observation['query_variants'][0]['terms']}
    return observation['original_match_count']<12 and bool(extra&actual)
output=dict(evidence_kind='exposed_generic_cascade_reusing_same_one_inference_arm',activation=False,predictions_source_sha256=runner.sha(tiny_path),script_sha256=runner.sha(Path(__file__)),trigger='Original trusted COUNT under max_cards and actual appended atom from a multiword required term',additional_inferences_for_45=0,suites=[],formal=[])
for suite,first in zip(tiny['suites'],initial['suites']):
    name=suite['name'];plan=json.loads((ROOT/('evals/plugin-v1/final-quality-'+name+'-2026-10-11.json')).read_bytes());cases={c['case_id']:c for c in plan['cases']};old={r['case_id']:r for r in first['records']};rows=[]
    for r in suite['records']:
        case=cases[r['case_id']];active=triggered(case,old[r['case_id']]['atoms_leaf'])
        row={k:r[k] for k in ['case_id','metric_family','tags','container_domain_ids','baseline']};row['activated_soft_priority']=active
        row['cascade_pure']=r['tiny_goal'] if active else r['native'];row['cascade_rrf']=r['tiny_goal_rrf'] if active else r['native'];rows.append(row)
    semantic=[r for r in rows if r['metric_family']=='semantic'];summary={}
    for mode in ['cascade_pure','cascade_rrf']:
        strata={}
        for field,values in [('tags',plan['stratification']['required_case_tags']),('container_domain_ids',plan['stratification']['container_ids'])]:
            for value in values:
                selected=[r for r in semantic if value in r[field]]
                if selected:strata[value]=runner.macro(selected,mode)
        summary[mode]=dict(macro=runner.macro(semantic,mode),failed_cases={r['case_id']:r[mode]['ranking']['ranking'] for r in semantic if r[mode]['ranking']['ranking']['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or r[mode]['ranking']['ranking']['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},failed_strata={k:v for k,v in strata.items() if v['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or v['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},hard_failures=sum(len(r[mode]['hard_constraint_violations'])+len(r[mode]['false_exclusions'])+r[mode]['duplicate_canonical_ids'] for r in rows),pack_survival=min(r[mode]['pack_survival'] for r in semantic if r[mode]['pack_survival'] is not None),alias_success=all(r[mode]['alias_success'] for r in rows if r['metric_family']=='identity'))
    output['suites'].append(dict(name=name,summary=summary,activated_count=sum(r['activated_soft_priority'] for r in rows),records=rows));print(name,json.dumps(summary),flush=True)
# Four formal cases: native inputs are byte-identical unless this generic trigger fires.
spec=importlib.util.spec_from_file_location('cascade_model',ROOT/'evals/plugin-v1/run_flashrank_comparison.py')
comparison=importlib.util.module_from_spec(spec);spec.loader.exec_module(comparison);backend=None
formal_path=ROOT/'evals/plugin-v1/results/cp04-final-current-calibration-2026-10-11/cases.json'
for c in json.loads(formal_path.read_bytes()):
    request=prepare('atoms_leaf',copy.deepcopy(c['brief']),copy.deepcopy(c['interpretation']));query=request['catalog_query']
    active=triggered(c['interpretation'],dict(query_variants=query['variants'],original_match_count=request['query_derivation']['original_match_count']))
    runtime.prepare_from_brief=lambda b,i:copy.deepcopy(request)
    result=runtime.run(brief=copy.deepcopy(c['brief']),interpretation=copy.deepcopy(c['interpretation']))
    row=dict(case_id=c['case_id'],activated_soft_priority=active,query_identical=query==c['result']['request']['catalog_query'],query_sha256=runtime.digest(query),goal_sha256=runtime.digest(c['brief']['goal']),profiles={})
    if active:
        if backend is None:backend=comparison.Backend('tiny',dict(comparison.DEFAULTS))
        raw=runtime.retrieval.retrieve(query,run_id=c['brief']['run_id'],index_path=runtime.ASSETS/'catalog.search.sqlite',manifest_path=runtime.ASSETS/'catalog.search-manifest.json',policy_path=runtime.ASSETS/'retrieval-policy.json')
        selection=comparison.previous.rerank_pool(raw,verified,c['brief']['goal'],backend)
        orders={'cascade_pure':selection['ranked_ids'],'cascade_rrf':comparison.fuse_orders(result['raw_ranked_ids'],selection['ranked_ids'],policy['rank_fusion']['k'])}
        for mode,order in orders.items():
            pack=runner.old.baseline_pack(query,order,verified,dict(pins=manifest['pins'],artifacts=dict(policy_path='specs/retrieval/retrieval-policy.json')),c['brief']['run_id'])
            row['profiles'][mode]=dict(pack_identical=pack==c['result']['evidence_pack'],pack_sha256=runtime.digest(pack),selected_ids=[p['card']['identity']['github_repository_id'] for p in pack['cards']])
    else:
        for mode in ['cascade_pure','cascade_rrf']:row['profiles'][mode]=dict(pack_identical=result['evidence_pack']==c['result']['evidence_pack'],pack_sha256=runtime.digest(result['evidence_pack']),selected_ids=result['selected_ids'])
    output['formal'].append(row)
runtime.prepare_from_brief=original_prepare
with (ROOT/'work/cp04-final/prospective-repair-cascade-diagnostic-results.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(output,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
print('formal',json.dumps(output['formal']),flush=True)
