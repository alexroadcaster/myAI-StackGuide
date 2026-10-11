"""Bounded exposed diagnostics; no runtime, policy, oracle or capture edits."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import sqlite3

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('prospective_diagnostic_runner',ROOT/'evals/plugin-v1/run_final_quality.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
runtime=runner.runtime
original_prepare=runtime.prepare_from_brief
manifest=json.loads((runtime.ASSETS/'catalog.search-manifest.json').read_bytes())
policy=json.loads((runtime.ASSETS/'retrieval-policy.json').read_bytes())
cards=json.loads((runtime.ASSETS/'catalog.snapshot.json').read_bytes())['cards']
verified=runtime.context_pack._cards_from_verified_snapshot(
    json.loads((runtime.ASSETS/'catalog.snapshot.json').read_bytes()),manifest['pins'],expected_count=manifest['row_count'])
def cached_cards(value,pins,*,expected_count):
    assert pins==manifest['pins'] and expected_count==manifest['row_count']
    return verified
runtime.context_pack._cards_from_verified_snapshot=cached_cards
connection=sqlite3.connect((runtime.ASSETS/'catalog.search.sqlite').resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
members={}
for route,member in connection.execute('SELECT route_id,match_category_id FROM taxonomy_route_registry'):
    members.setdefault(route,set()).add(member)
connection.close()
MODES=['current','atoms_route','atoms_required_rrf','atoms_leaf','atoms_leaf_required_rrf','atoms_only_rrf']
def atoms(terms):
    result=[]
    for term in runtime.retrieval._compiled_terms(terms,policy['aliases']):
        # Identifier and versioned alias semantics remain atomic. No stemming.
        if '/' in term:continue
        tokens=re.findall(r'[^\W_]+',term,flags=re.UNICODE)
        if len(tokens)>1:result.extend(tokens)
    return result
def append_unique(original,extra):
    result=copy.deepcopy(original);keys={runtime.retrieval._normalize(t) for t in result}
    for term in extra:
        normalized=runtime.retrieval._normalize(term)
        if normalized not in keys and len(result)<policy['limits']['max_terms_per_variant']:
            result.append(term);keys.add(normalized)
    return result
def prepare(mode,brief,interpretation):
    request=original_prepare(brief,interpretation)
    if mode=='current':return request
    count=request['query_derivation']['original_match_count']
    required=[t for group in interpretation['intent']['required_groups'] for t in group]
    new_atoms=atoms(required)
    if count>=request['catalog_query']['max_cards'] or not new_atoms:return request
    original=interpretation['terms'];route=interpretation['route'];route_terms=route.split('_') if route else []
    relevant_leaf=[]
    if route and 'leaf' in mode:
        wanted={runtime.retrieval._normalize(t) for t in required+new_atoms}
        for member in sorted(members[route]):
            tokens=member.split('_')
            if wanted.intersection(tokens):relevant_leaf.extend(tokens)
    full=append_unique(original,new_atoms+relevant_leaf+route_terms)
    variants=[full]
    if mode.endswith('rrf'):
        required_variant=append_unique(required,new_atoms)
        if mode=='atoms_only_rrf':required_variant=append_unique([],new_atoms)
        if required_variant and required_variant!=full:variants.append(required_variant)
    query=request['catalog_query'];query['variants']=[dict(variant_id='q'+str(n),terms=terms) for n,terms in enumerate(variants,1)]
    runtime.retrieval.validate_query(query,manifest=manifest,policy=policy)
    assert len(variants)+1<=policy['limits']['max_query_variants']
    return request
output=dict(evidence_kind='all45_exposed_development_diagnostic_only',activation=False,
            profiles=MODES,active_pins=manifest['pins'],source_hashes={str(p.relative_to(ROOT)):runner.sha(p) for p in
            [Path(__file__),ROOT/'plugins/myai-stackguide/scripts/recommendation_request.py',ROOT/'plugins/myai-stackguide/scripts/retrieval.py']},suites=[])
for name in ['rank-repair-regression','prospective']:
    plan_path=ROOT/('evals/plugin-v1/final-quality-'+name+'-2026-10-11.json')
    capture_path=ROOT/('evals/plugin-v1/results/cp04-final-quality-'+name+'-2026-10-11/observations.json')
    plan=json.loads(plan_path.read_bytes());capture=json.loads(capture_path.read_bytes());frozen={r['case_id']:r for r in capture['records']}
    for key in ['cards_sha256','taxonomy_sha256','source_sha256']:
        assert plan['pins'][key]==manifest['pins'][key]
    rows=[]
    for case in plan['cases']:
        prior=frozen[case['case_id']]
        routed=[c for c in cards if any(a['category_id'] in members[case['route']] for a in c['classifications'])]
        literal=runner.old.scorer.lexical_baseline(routed,case['terms'],prior['query']['max_candidates'])
        assert literal==prior['baseline']['raw_ranked_ids'],case['case_id']+' original literal order drift'
        row=dict(case_id=case['case_id'],metric_family=case['metric_family'],tags=case['tags'],container_domain_ids=case['container_domain_ids'],baseline=prior['baseline'])
        for mode in MODES:
            runtime.prepare_from_brief=lambda b,i:prepare(mode,b,i)
            captured=[]
            def spy(query,**kwargs):
                result=runtime.retrieval.retrieve(query,**kwargs);captured.append(result);return result
            result=runtime.run(**copy.deepcopy(prior['payload']),retrieve=spy)
            observed=runner.observe(case,result,captured[0]['status'])
            observed.update(query_variants=result['request']['catalog_query']['variants'],original_match_count=result['request']['query_derivation']['original_match_count'],retrieved_hits=captured[0]['retrieved_hits'])
            assert observed['retrieved_hits']<=policy['limits']['max_retrieved_hits']
            row[mode]=observed
        if name=='rank-repair-regression':
            for mode in MODES:assert row[mode]['raw_ranked_ids']==prior['candidate']['raw_ranked_ids'],case['case_id']+' regression '+mode
        rows.append(row)
    semantic=[r for r in rows if r['metric_family']=='semantic'];summary={}
    for mode in ['baseline']+MODES:
        strata={}
        for field,values in [('tags',plan['stratification']['required_case_tags']),('container_domain_ids',plan['stratification']['container_ids'])]:
            for value in values:
                selected=[r for r in semantic if value in r[field]]
                if selected:strata[value]=runner.macro(selected,mode)
        summary[mode]=dict(macro=runner.macro(semantic,mode),failed_cases={r['case_id']:r[mode]['ranking']['ranking'] for r in semantic
            if r[mode]['ranking']['ranking']['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or r[mode]['ranking']['ranking']['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},failed_strata={k:v for k,v in strata.items()
            if v['recall_at_k']<plan['thresholds']['required_stratum_recall_at_12_min'] or v['ndcg_at_k']<plan['thresholds']['required_stratum_ndcg_at_12_min']},hard_failures=sum(len(r[mode]['hard_constraint_violations'])+len(r[mode]['false_exclusions'])+r[mode]['duplicate_canonical_ids'] for r in rows),pack_survival=min(r[mode]['pack_survival'] for r in semantic if r[mode]['pack_survival'] is not None),alias_success=all(r[mode]['alias_success'] for r in rows if r['metric_family']=='identity'))
    output['suites'].append(dict(name=name,plan_sha256=runner.sha(plan_path),capture_sha256=runner.sha(capture_path),summary=summary,records=rows))
    print(name,json.dumps(summary),flush=True)
runtime.prepare_from_brief=original_prepare
destination=ROOT/'work/cp04-final/prospective-repair-diagnostic-results.json'
with destination.open('x',encoding='utf-8',newline='\n') as stream:json.dump(output,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
