"""One native profile: required atoms, pinned ancestor words, selected/leaf words."""
setup_path=__import__('pathlib').Path(__file__).with_name('prospective-repair-diagnostic.py')
exec(compile(setup_path.read_text(encoding='utf-8').split('output=dict(')[0],str(setup_path),'exec'))
parents={}
for card in cards:
    for category in card['classifications']:
        key=category['category_id'];value=category['parent_id']
        if key in parents:assert parents[key]==value,'ambiguous pinned parent'
        parents[key]=value
def hierarchy_prepare(brief,interpretation):
    request=original_prepare(brief,interpretation);query=request['catalog_query']
    required=[t for g in interpretation['intent']['required_groups'] for t in g]
    if request['status']!='ready' or request['query_derivation']['original_match_count']>=query['max_cards'] or not atoms(required):return request
    original=interpretation['terms'];route=interpretation['route'];extra=[];visited=set();ancestor=parents.get(route)
    for term in required:
        extra.extend(dict(word=w,source_kind='original_required_term',source=term) for w in atoms([term]))
    while ancestor is not None:
        assert ancestor not in visited and ancestor in members,'invalid pinned ancestry';visited.add(ancestor)
        extra.extend(dict(word=w,source_kind='pinned_classification_parent_id',source=ancestor) for w in ancestor.split('_'))
        ancestor=parents.get(ancestor)
    if route:
        wanted={runtime.retrieval._normalize(t) for t in required+atoms(required)}
        for member in sorted(members[route]):
            if wanted.intersection(member.split('_')):
                extra.extend(dict(word=w,source_kind='pinned_taxonomy_route_member',source=member) for w in member.split('_'))
        extra.extend(dict(word=w,source_kind='selected_pinned_taxonomy_route_id',source=route) for w in route.split('_'))
    full=copy.deepcopy(original);keys={runtime.retrieval._normalize(t) for t in full};origins=[]
    for item in extra:
        key=runtime.retrieval._normalize(item['word'])
        if key not in keys and len(full)<policy['limits']['max_terms_per_variant']:
            full.append(item['word']);keys.add(key);origins.append(item)
    query['variants']=[dict(variant_id='q1',terms=full)]
    request['diagnostic_hierarchy_origins']=origins
    runtime.retrieval.validate_query(query,manifest=manifest,policy=policy)
    return request
output=dict(evidence_kind='one_native_source_hierarchy_exposed_diagnostic',activation=False,profiles=['required_atoms_ancestor_leaf'],source_hashes={str(p.relative_to(ROOT)):runner.sha(p) for p in [Path(__file__),setup_path,ROOT/'plugins/myai-stackguide/scripts/recommendation_request.py',ROOT/'plugins/myai-stackguide/scripts/retrieval.py']},pins=manifest['pins'],suites=[],formal=[])
for name in ['rank-repair-regression','prospective']:
    plan_path=ROOT/('evals/plugin-v1/final-quality-'+name+'-2026-10-11.json');plan=json.loads(plan_path.read_bytes())
    capture_path=ROOT/('evals/plugin-v1/results/cp04-final-quality-'+name+'-2026-10-11/observations.json');frozen={r['case_id']:r for r in json.loads(capture_path.read_bytes())['records']};rows=[]
    for case in plan['cases']:
        prior=frozen[case['case_id']]
        routed=[c for c in cards if any(v['category_id'] in members[case['route']] for v in c['classifications'])]
        assert runner.old.scorer.lexical_baseline(routed,case['terms'],prior['query']['max_candidates'])==prior['baseline']['raw_ranked_ids']
        runtime.prepare_from_brief=hierarchy_prepare;captured=[]
        def spy(q,**kw):
            raw=runtime.retrieval.retrieve(q,**kw);captured.append(raw);return raw
        result=runtime.run(**copy.deepcopy(prior['payload']),retrieve=spy);observed=runner.observe(case,result,captured[0]['status'])
        row={k:prior[k] for k in ['case_id','metric_family','tags','container_domain_ids','baseline']}
        row.update(candidate=observed,query=result['request']['catalog_query'],original_match_count=result['request']['query_derivation']['original_match_count'],added_word_origins=result['request'].get('diagnostic_hierarchy_origins',[]),native_c9=captured[0],original_candidate_order_identical=observed['raw_ranked_ids']==prior['candidate']['raw_ranked_ids'])
        rows.append(row)
    semantic=[r for r in rows if r['metric_family']=='semantic'];macro=runner.macro(semantic,'candidate');baseline=runner.macro(semantic,'baseline');strata={}
    for field,values in [('tags',plan['stratification']['required_case_tags']),('container_domain_ids',plan['stratification']['container_ids'])]:
        for value in values:
            selected=[r for r in semantic if value in r[field]]
            if selected:strata[value]=runner.macro(selected,'candidate')
    summary=dict(macro=macro,baseline_macro=baseline,macro_floor_pass=macro['recall_at_k']>=plan['thresholds']['held_out_macro_recall_at_12_min'] and macro['ndcg_at_k']>=plan['thresholds']['held_out_macro_ndcg_at_12_min'],literal_nonregression=all(macro[k]>=baseline[k] for k in macro),failed_cases={r['case_id']:r['candidate']['ranking']['ranking'] for r in semantic if r['candidate']['ranking']['ranking']['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or r['candidate']['ranking']['ranking']['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},failed_strata={k:v for k,v in strata.items() if v['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or v['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},hard_failures=sum(len(r['candidate']['hard_constraint_violations'])+len(r['candidate']['false_exclusions'])+r['candidate']['duplicate_canonical_ids'] for r in rows),pack_survival=min(r['candidate']['pack_survival'] for r in semantic if r['candidate']['pack_survival'] is not None),alias_success=all(r['candidate']['alias_success'] for r in rows if r['metric_family']=='identity'),original_literal_orders_preserved=len(rows),original_candidate_orders_preserved=sum(r['original_candidate_order_identical'] for r in rows))
    output['suites'].append(dict(name=name,plan_sha256=runner.sha(plan_path),capture_sha256=runner.sha(capture_path),summary=summary,records=rows));print(name,json.dumps(summary),flush=True)
formal_path=ROOT/'evals/plugin-v1/results/cp04-final-current-calibration-2026-10-11/cases.json'
for c in json.loads(formal_path.read_bytes()):
    runtime.prepare_from_brief=hierarchy_prepare
    result=runtime.run(brief=copy.deepcopy(c['brief']),interpretation=copy.deepcopy(c['interpretation']))
    output['formal'].append(dict(case_id=c['case_id'],query_identical=result['request']['catalog_query']==c['result']['request']['catalog_query'],pack_identical=result['evidence_pack']==c['result']['evidence_pack'],query=result['request']['catalog_query'],query_sha256=runtime.digest(result['request']['catalog_query']),pack_sha256=runtime.digest(result['evidence_pack']),added_word_origins=result['request'].get('diagnostic_hierarchy_origins',[])))
runtime.prepare_from_brief=original_prepare
with (ROOT/'work/cp04-final/prospective-repair-hierarchy-diagnostic-results.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(output,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
print('formal',json.dumps([{k:v for k,v in r.items() if k in ['case_id','query_identical','pack_identical','added_word_origins']} for r in output['formal']]),flush=True)
