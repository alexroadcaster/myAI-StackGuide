"""Native SQL ranking screen only; pack/guard evidence requires a successor replay."""
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('screen_runner',ROOT/'evals/plugin-v1/run_final_quality.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
runtime=runner.runtime
original_execute=runtime.retrieval._execute_variant
base=runtime.retrieval.FIELD_WEIGHTS
profiles={'current':base}
for name,upstream,catalog,topics in [('provenance_6_1',6,1,.25),('provenance_9_1',9,1,.25),('upstream_6',6,3,.1),('catalog_1',3,1,.1),('topics_zero',3,3,0)]:
    profiles[name]={**base,'upstream_description':upstream,'catalog_description':catalog,'topics':topics}
prior=json.loads((ROOT/'work/cp04-final/prospective-repair-diagnostic-results.json').read_bytes())
policy=json.loads((runtime.ASSETS/'retrieval-policy.json').read_bytes())
connection=sqlite3.connect((runtime.ASSETS/'catalog.search.sqlite').resolve().as_uri()+'?mode=ro&immutable=1',uri=True);connection.row_factory=sqlite3.Row
output=dict(evidence_kind='SQL_only_exposed_development_screen',activation=False,pack_verified=False,profiles=profiles,source_hashes={str(Path(__file__).relative_to(ROOT)):runner.sha(Path(__file__))},suites=[])
for suite in prior['suites']:
    name=suite['name'];plan=json.loads((ROOT/('evals/plugin-v1/final-quality-'+name+'-2026-10-11.json')).read_bytes());cases={c['case_id']:c for c in plan['cases']};records=[]
    for row in suite['records']:
        case=cases[row['case_id']];record={key:row[key] for key in ['case_id','metric_family','tags','container_domain_ids','baseline']}
        variants=row['atoms_leaf']['query_variants'];assert len(variants)==1
        match=runtime.retrieval.compile_fts5_query(variants[0]['terms'],aliases=policy['aliases'])
        for profile,weights in profiles.items():
            runtime.retrieval.FIELD_WEIGHTS=weights
            ranked=original_execute(connection,match,case['route'],150)
            ids=[r['github_repository_id'] for r in ranked]
            if profile=='current':assert ids==row['atoms_leaf']['raw_ranked_ids'],case['case_id']+' native control drift'
            record[profile]=dict(ranking=runner.rank(ids,case['judgments'],case['k']),raw_ranked_ids=ids,query_variants=variants)
        records.append(record)
    semantic=[r for r in records if r['metric_family']=='semantic'];summary={}
    for profile in profiles:
        strata={}
        for field,values in [('tags',plan['stratification']['required_case_tags']),('container_domain_ids',plan['stratification']['container_ids'])]:
            for value in values:
                selected=[r for r in semantic if value in r[field]]
                if selected:strata[value]=runner.macro(selected,profile)
        summary[profile]=dict(macro=runner.macro(semantic,profile),failed_cases={r['case_id']:r[profile]['ranking']['ranking'] for r in semantic if r[profile]['ranking']['ranking']['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or r[profile]['ranking']['ranking']['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},failed_strata={k:v for k,v in strata.items() if v['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or v['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},alias_success=all(set(cases[r['case_id']].get('expected_identity_ids',[]))<=set(r[profile]['raw_ranked_ids'][:12]) for r in records if r['metric_family']=='identity'))
    output['suites'].append(dict(name=name,summary=summary,records=records));print(name,json.dumps(summary),flush=True)
runtime.retrieval.FIELD_WEIGHTS=base;connection.close()
with (ROOT/'work/cp04-final/prospective-repair-weight-screen-results.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(output,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
