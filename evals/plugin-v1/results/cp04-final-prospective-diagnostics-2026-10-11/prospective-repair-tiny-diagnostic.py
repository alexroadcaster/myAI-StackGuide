"""Authorized cached TinyBERT: one full Brief-goal arm; native and equal RRF controls."""
import math
import statistics
import time
setup_path=__import__('pathlib').Path(__file__).with_name('prospective-repair-diagnostic.py')
exec(compile(setup_path.read_text(encoding='utf-8').split('output=dict(')[0],str(setup_path),'exec'))
spec=importlib.util.spec_from_file_location('prospective_existing_model',ROOT/'evals/plugin-v1/run_flashrank_comparison.py')
comparison=importlib.util.module_from_spec(spec);spec.loader.exec_module(comparison)
import psutil
model_receipt=comparison.receipt('tiny')
assert model_receipt['files']['flashrank-TinyBERT-L-2-v2.onnx']=='a2b09fb0de692c052a55f4165c9461377b4a31115673b7adb428503d69109196'
start=time.perf_counter();backend=comparison.Backend('tiny',dict(comparison.DEFAULTS));startup_ms=(time.perf_counter()-start)*1000
process=psutil.Process()
prior=json.loads((ROOT/'work/cp04-final/prospective-repair-diagnostic-results.json').read_bytes())
output=dict(evidence_kind='cached_local_ONNX_exposed_development_diagnostic',activation=False,model_receipt=model_receipt,settings=comparison.DEFAULTS,startup_ms=startup_ms,active_pins=manifest['pins'],source_hashes={str(p.relative_to(ROOT)):runner.sha(p) for p in [Path(__file__),setup_path,ROOT/'evals/plugin-v1/run_flashrank_comparison.py',ROOT/'evals/plugin-v1/run_flashrank_configured.py',ROOT/'evals/plugin-v1/run_flashrank_development.py']},suites=[],score_semantics='Native C9 result retained verbatim; neural/fused order is experimental soft selection only; existing diagnostic packing adapter does not execute C9 BM25/RRF.')
for suite in prior['suites']:
    name=suite['name'];plan_path=ROOT/('evals/plugin-v1/final-quality-'+name+'-2026-10-11.json');plan=json.loads(plan_path.read_bytes())
    frozen_path=ROOT/('evals/plugin-v1/results/cp04-final-quality-'+name+'-2026-10-11/observations.json');frozen={r['case_id']:r for r in json.loads(frozen_path.read_bytes())['records']}
    expected={r['case_id']:r for r in suite['records']};rows=[]
    for case in plan['cases']:
        payload=copy.deepcopy(frozen[case['case_id']]['payload'])
        start=time.perf_counter();request=prepare('atoms_leaf',payload['brief'],payload['interpretation']);query=request['catalog_query']
        raw=runtime.retrieval.retrieve(query,run_id=payload['brief']['run_id'],index_path=runtime.ASSETS/'catalog.search.sqlite',manifest_path=runtime.ASSETS/'catalog.search-manifest.json',policy_path=runtime.ASSETS/'retrieval-policy.json')
        c9_ms=(time.perf_counter()-start)*1000
        runtime.prepare_from_brief=lambda b,i:copy.deepcopy(request)
        control=runtime.run(**payload,retrieve=lambda q,**kw:copy.deepcopy(raw))
        ids=control['raw_ranked_ids'];assert ids==expected[case['case_id']]['atoms_leaf']['raw_ranked_ids']
        goal=payload['brief']['goal'];before=process.memory_info();start=time.perf_counter()
        selection=comparison.previous.rerank_pool(raw,verified,goal,backend)
        inference_ms=(time.perf_counter()-start)*1000;after=process.memory_info()
        orders={'native':ids,'tiny_goal':selection['ranked_ids'],'tiny_goal_rrf':comparison.fuse_orders(ids,selection['ranked_ids'],policy['rank_fusion']['k'])}
        row=dict(case_id=case['case_id'],metric_family=case['metric_family'],tags=case['tags'],container_domain_ids=case['container_domain_ids'],baseline=frozen[case['case_id']]['baseline'],native_c9=raw,experimental_selection=selection,goal_sha256=runtime.digest(goal),c9_count_plus_retrieve_ms=c9_ms,inference_ms=inference_ms,inference_process_rss_before=before.rss,inference_process_rss_after=after.rss,process_peak_wset_after=getattr(after,'peak_wset',None))
        for mode,order in orders.items():
            if mode=='native':result=control
            else:
                chosen=runtime.request_guard.select(request,order,{r['github_repository_id']:r for r in payload['public_observations']},limit=query['max_candidates'])
                # Reuse the explicitly experimental pack adapter; original raw C9 scores remain above.
                pack=runner.old.baseline_pack(query,chosen['selected_ids'],verified,plan,payload['brief']['run_id'])
                result=dict(raw_ranked_ids=order,evidence_pack=pack)
            row[mode]=runner.observe(case,result,raw['status'])
        rows.append(row)
    semantic=[r for r in rows if r['metric_family']=='semantic'];summary={}
    for mode in ['native','tiny_goal','tiny_goal_rrf']:
        strata={}
        for field,values in [('tags',plan['stratification']['required_case_tags']),('container_domain_ids',plan['stratification']['container_ids'])]:
            for value in values:
                selected=[r for r in semantic if value in r[field]]
                if selected:strata[value]=runner.macro(selected,mode)
        summary[mode]=dict(macro=runner.macro(semantic,mode),failed_cases={r['case_id']:r[mode]['ranking']['ranking'] for r in semantic if r[mode]['ranking']['ranking']['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or r[mode]['ranking']['ranking']['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},failed_strata={k:v for k,v in strata.items() if v['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or v['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},hard_failures=sum(len(r[mode]['hard_constraint_violations'])+len(r[mode]['false_exclusions'])+r[mode]['duplicate_canonical_ids'] for r in rows),pack_survival=min(r[mode]['pack_survival'] for r in semantic if r[mode]['pack_survival'] is not None),alias_success=all(r[mode]['alias_success'] for r in rows if r['metric_family']=='identity'))
    output['suites'].append(dict(name=name,plan_sha256=runner.sha(plan_path),capture_sha256=runner.sha(frozen_path),summary=summary,records=rows));print(name,json.dumps(summary),flush=True)
runtime.prepare_from_brief=original_prepare
assert comparison.receipt('tiny')==model_receipt
timings=[r['inference_ms'] for s in output['suites'] for r in s['records']]
output['inference_resources']=dict(samples=len(timings),median_ms=statistics.median(timings),p95_nearest_rank_ms=sorted(timings)[math.ceil(.95*len(timings))-1],max_ms=max(timings),peak_process_wset= max(r['process_peak_wset_after'] or 0 for s in output['suites'] for r in s['records']),measurement_scope='Single sequential inference sample per unchanged case; process peak includes interpreter/model/runtime. C9 COUNT and retrieval latency separately recorded; no repeated performance grid.')
with (ROOT/'work/cp04-final/prospective-repair-tiny-diagnostic-results.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(output,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
print('resources',json.dumps(output['inference_resources']),flush=True)
