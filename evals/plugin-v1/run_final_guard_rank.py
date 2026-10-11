"""Current Brief/C9 regression for previously exposed exclusions and ambiguity."""
import copy,hashlib,json,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'plugins/myai-stackguide/scripts'))
import recommendation_request as runtime
INPUT=ROOT/'evals/plugin-v1/request-guard-cases-2026-10-11.json'
FACTS=ROOT/'research/cp04-request-dependency-evidence-2026-10-11.json'
OUT=ROOT/'evals/plugin-v1/results/cp04-final-guard-rank-2026-10-11'
if __name__=='__main__':
 if (OUT/'observations.json').exists():raise ValueError('preserve prior capture')
 template=json.loads((ROOT/'evals/plugin-v1/results/cp04-final-answers-repair-2026-10-11/cases.json').read_bytes())[0]['brief']
 facts=json.loads(FACTS.read_bytes())['facts']
 rows=[]
 sources=[INPUT,FACTS,Path(__file__),Path(runtime.__file__),runtime.ASSETS/'retrieval-policy.json',runtime.ASSETS/'catalog.search-manifest.json']
 declaration={'evidence_kind':'exposed_current_Brief_C9_regression','source_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'cases':json.loads(INPUT.read_bytes())['cases'],'thresholds':{'known_conflicts_max':0,'unresolved_retrieval_calls_max':0}}
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'declaration.json').write_text(json.dumps(declaration,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 for c in declaration['cases']:
  b=copy.deepcopy(template);b.update(brief_id=c['case_id'],run_id=str(uuid.uuid5(uuid.NAMESPACE_URL,c['case_id'])),goal=c['user_goal']);b['observations']['run_id']=b['run_id']
  b['constraints']={k:[] for k in ('languages','deployment','allowed_licenses','compatibility','mandatory_fields')};b['constraints']['require_no_server']=None
  constraints=c['request_constraints'];unresolved=constraints['unresolved']
  i=dict(brief_sha256=runtime.digest(b),brief_version=b['brief_version'],language=c['query_locale'],route=None if unresolved else c['target_category_id'],terms=None if unresolved else c['query_terms'],intent=None if unresolved else c['intent'],**constraints)
  r=runtime.run(b,i,facts)
  if unresolved:passed=r['status']=='needs_clarification' and r['retrieval_calls']==0 and r['evidence_pack'] is None
  else:
   selected=set(r['selected_ids']);denied=set(constraints['excluded_repository_ids'])|{x['github_repository_id'] for x in r['selection']['excluded']}
   passed=r['status']=='ready' and not selected&denied
  rows.append({'case_id':c['case_id'],'payload':{'brief':b,'interpretation':i,'public_observations':facts},'capture':r,'passed':passed})
 v={'declaration_sha256':runtime.digest(declaration),'records':rows,'passed':all(r['passed'] for r in rows),'negative_cases':sum(not c['request_constraints']['unresolved'] for c in declaration['cases']),'ambiguity_cases':sum(bool(c['request_constraints']['unresolved']) for c in declaration['cases']),'human_acceptance':False}
 (OUT/'observations.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v[k] for k in ('passed','negative_cases','ambiguity_cases')}));raise SystemExit(0 if v['passed'] else 1)
