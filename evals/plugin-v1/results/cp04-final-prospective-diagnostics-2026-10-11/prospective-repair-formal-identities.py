"""Four formal query/pack identities for the bounded planner and SQL profiles."""
setup_path=__import__('pathlib').Path(__file__).with_name('prospective-repair-diagnostic.py')
exec(compile(setup_path.read_text(encoding='utf-8').split('output=dict(')[0],str(setup_path),'exec'))
original_execute=runtime.retrieval._execute_variant
weights=json.loads((ROOT/'work/cp04-final/prospective-repair-weight-screen-results.json').read_bytes())['profiles']
profiles=[(mode,mode,None) for mode in MODES]+[('weights_'+name,'atoms_leaf',weight) for name,weight in weights.items() if name!='current']
source=ROOT/'evals/plugin-v1/results/cp04-final-current-calibration-2026-10-11/cases.json'
output=dict(evidence_kind='exposed_formal_query_pack_identity_diagnostic',activation=False,source_sha256=runner.sha(source),script_sha256=runner.sha(Path(__file__)),records=[])
for case in json.loads(source.read_bytes()):
    row=dict(case_id=case['case_id'],profiles={})
    for name,mode,weight in profiles:
        def execute(*args,**kwargs):
            saved=runtime.retrieval.FIELD_WEIGHTS
            try:
                if weight is not None:runtime.retrieval.FIELD_WEIGHTS=weight
                return original_execute(*args,**kwargs)
            finally:runtime.retrieval.FIELD_WEIGHTS=saved
        runtime.retrieval._execute_variant=execute
        runtime.prepare_from_brief=lambda b,i:prepare(mode,b,i)
        result=runtime.run(brief=copy.deepcopy(case['brief']),interpretation=copy.deepcopy(case['interpretation']))
        query=result['request']['catalog_query'];pack=result['evidence_pack'];old=case['result']
        row['profiles'][name]=dict(query_identical=query==old['request']['catalog_query'],pack_identical=pack==old['evidence_pack'],query_sha256=runtime.digest(query),pack_sha256=runtime.digest(pack),selected_ids=result['selected_ids'],raw_ranked_ids=result['raw_ranked_ids'])
    output['records'].append(row);print(case['case_id'],json.dumps({n:{k:v for k,v in r.items() if k.endswith('identical')} for n,r in row['profiles'].items()}),flush=True)
runtime.prepare_from_brief=original_prepare;runtime.retrieval._execute_variant=original_execute
with (ROOT/'work/cp04-final/prospective-repair-formal-identities-results.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(output,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
