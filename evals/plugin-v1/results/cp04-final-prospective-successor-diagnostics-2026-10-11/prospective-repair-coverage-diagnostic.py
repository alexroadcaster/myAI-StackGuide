"""One source-pinned lexical coverage formula; preserve native C9 ranking verbatim."""
from fractions import Fraction
setup_path=__import__('pathlib').Path(__file__).with_name('prospective-repair-diagnostic.py')
exec(compile(setup_path.read_text(encoding='utf-8').split('output=dict(')[0],str(setup_path),'exec'))
native_path=ROOT/'work/cp04-final/prospective-repair-tiny-diagnostic-results.json'
pool_path=ROOT/'work/cp04-final/prospective-repair-diagnostic-results.json'
native=json.loads(native_path.read_bytes());pools=json.loads(pool_path.read_bytes())
assert native['active_pins']==manifest['pins']==pools['active_pins']
for file,key in [('catalog.snapshot.json','cards_sha256'),('catalog.search.sqlite','index_sha256'),('retrieval-policy.json','policy_sha256')]:
    assert runner.sha(runtime.ASSETS/file)==manifest['pins'][key]
source_hashes={path.replace('\\','/'):digest for path,digest in pools['source_hashes'].items()}
for path in ['plugins/myai-stackguide/scripts/recommendation_request.py','plugins/myai-stackguide/scripts/retrieval.py']:
    assert runner.sha(ROOT/path)==source_hashes[path]
runtime.retrieval._validate_manifest_policy(manifest,policy)
def lexemes(text):
    return set(re.findall(r'[^\W_]+',runtime.retrieval._normalize(text),flags=re.UNICODE))
def functional_sources(card):
    values={
        '/descriptions/upstream':card['descriptions']['upstream'],
        '/descriptions/catalog':card['descriptions']['catalog'],
        '/repository/topics':card['repository']['topics'],
        '/advisory/use_cases':card['advisory']['use_cases'],
        '/advisory/integration_surface':card['advisory']['integration_surface'],
        '/advisory/best_for':card['advisory']['best_for']}
    return {path:set().union(*(lexemes(t) for t in (value if isinstance(value,list) else [value]) if isinstance(t,str))) for path,value in values.items()}
source_tokens={rid:functional_sources(card) for rid,card in verified.items()}
def score(card_id,groups):
    sources=source_tokens[card_id];available=set().union(*sources.values());group_scores=[];details=[]
    for group in groups:
        alternatives=[]
        for term in group:
            required=lexemes(term);matched=required&available
            fraction=Fraction(len(matched),len(required)) if required else Fraction(0)
            alternatives.append(dict(term=term,required_lexemes=sorted(required),matched_lexemes=sorted(matched),coverage=float(fraction),matching_source_paths={t:sorted(path for path,tokens in sources.items() if t in tokens) for t in sorted(matched)}))
        best=max((Fraction(len(a['matched_lexemes']),len(a['required_lexemes'])) if a['required_lexemes'] else Fraction(0) for a in alternatives),default=Fraction(0))
        group_scores.append(best);details.append(dict(alternatives=alternatives,group_coverage=float(best)))
    total=sum(group_scores,Fraction(0))/len(group_scores) if group_scores else Fraction(0)
    return total,dict(score=float(total),exact_fraction=str(total),groups=details)
def trigger(case,pool):
    required=[term for group in case['intent']['required_groups'] for term in group]
    original={runtime.retrieval._normalize(t) for t in case['terms']}
    added={runtime.retrieval._normalize(t) for t in atoms(required)}-original
    actual={runtime.retrieval._normalize(t) for t in pool['query_variants'][0]['terms']}
    return pool['original_match_count']<policy['limits']['max_detailed_cards'] and bool(added&actual)
output=dict(evidence_kind='one_fixed_lexical_coverage_exposed_feasibility',activation=False,model_calls=0,score_semantics='Mean over mandatory groups of max alternative-term Unicode lexeme coverage in pinned non-taxonomy functional public text; descending exact fraction then native RRF ordinal. Lexical support only; no feature fit.',pins=manifest['pins'],source_hashes={str(p.relative_to(ROOT)):runner.sha(p) for p in [Path(__file__),setup_path,native_path,pool_path]},suites=[])
for suite,pool_suite in zip(native['suites'],pools['suites']):
    name=suite['name'];plan_path=ROOT/('evals/plugin-v1/final-quality-'+name+'-2026-10-11.json');plan=json.loads(plan_path.read_bytes());cases={c['case_id']:c for c in plan['cases']}
    capture_path=ROOT/('evals/plugin-v1/results/cp04-final-quality-'+name+'-2026-10-11/observations.json');frozen={r['case_id']:r for r in json.loads(capture_path.read_bytes())['records']};pool_rows={r['case_id']:r for r in pool_suite['records']};rows=[]
    for prior in suite['records']:
        case=cases[prior['case_id']];pool=pool_rows[prior['case_id']]['atoms_leaf'];ids=prior['native']['raw_ranked_ids'];raw=copy.deepcopy(prior['native_c9']);raw_sha=runtime.digest(raw)
        assert ids==pool['raw_ranked_ids']==[r['github_repository_id'] for r in raw['candidates']]
        routed=[c for c in cards if any(a['category_id'] in members[case['route']] for a in c['classifications'])]
        assert runner.old.scorer.lexical_baseline(routed,case['terms'],policy['limits']['max_retrieved_hits'])==prior['baseline']['raw_ranked_ids']
        active=trigger(case,pool);support={rid:score(rid,case['intent']['required_groups']) for rid in ids}
        position={rid:n for n,rid in enumerate(ids)}
        decision=sorted(ids,key=lambda rid:(-support[rid][0],position[rid])) if active else list(ids)
        assert set(decision)==set(ids) and len(decision)==len(ids)
        row={k:prior[k] for k in ['case_id','metric_family','tags','container_domain_ids','baseline']}
        row.update(native=prior['native'],native_c9=raw,native_c9_sha256=raw_sha,activated=active,coverage_scores={str(rid):support[rid][1] for rid in ids},decision_order=decision)
        if active:
            payload=copy.deepcopy(frozen[case['case_id']]['payload']);request=prepare('atoms_leaf',payload['brief'],payload['interpretation']);query=request['catalog_query']
            assert runtime.digest(query)==raw['query_sha256']
            chosen=runtime.request_guard.select(request,decision,{r['github_repository_id']:r for r in payload['public_observations']},limit=query['max_candidates'])
            pack=runner.old.baseline_pack(query,chosen['selected_ids'],verified,plan,payload['brief']['run_id'])
            row['candidate']=runner.observe(case,dict(raw_ranked_ids=decision,evidence_pack=pack),raw['status'])
            row['experimental_pack_sha256']=runtime.digest(pack)
        else:row['candidate']=copy.deepcopy(prior['native'])
        assert runtime.digest(raw)==raw_sha
        rows.append(row)
    semantic=[r for r in rows if r['metric_family']=='semantic'];macro=runner.macro(semantic,'candidate');baseline=runner.macro(semantic,'baseline');strata={}
    for field,values in [('tags',plan['stratification']['required_case_tags']),('container_domain_ids',plan['stratification']['container_ids'])]:
        for value in values:
            selected=[r for r in semantic if value in r[field]]
            if selected:strata[value]=runner.macro(selected,'candidate')
    summary=dict(macro=macro,baseline_macro=baseline,macro_floor_pass=macro['recall_at_k']>=plan['thresholds']['held_out_macro_recall_at_12_min'] and macro['ndcg_at_k']>=plan['thresholds']['held_out_macro_ndcg_at_12_min'],literal_nonregression=all(macro[k]>=baseline[k] for k in macro),failed_cases={r['case_id']:r['candidate']['ranking']['ranking'] for r in semantic if r['candidate']['ranking']['ranking']['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or r['candidate']['ranking']['ranking']['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},failed_strata={k:v for k,v in strata.items() if v['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or v['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},hard_failures=sum(len(r['candidate']['hard_constraint_violations'])+len(r['candidate']['false_exclusions'])+r['candidate']['duplicate_canonical_ids'] for r in rows),pack_survival=min(r['candidate']['pack_survival'] for r in semantic if r['candidate']['pack_survival'] is not None),alias_success=all(r['candidate']['alias_success'] for r in rows if r['metric_family']=='identity'),original_literal_orders_preserved=len(rows),activated_count=sum(r['activated'] for r in rows))
    output['suites'].append(dict(name=name,plan_sha256=runner.sha(plan_path),capture_sha256=runner.sha(capture_path),summary=summary,records=rows));print(name,json.dumps(summary),flush=True)
with (ROOT/'work/cp04-final/prospective-repair-coverage-results.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(output,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
