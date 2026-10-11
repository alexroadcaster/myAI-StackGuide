"""Source-bound single-locale display projection of preserved actual model outputs."""
import copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'plugins/myai-stackguide/scripts'))
import answer_presentation as presentation
import recommendation_request as runtime
import audit_final_answers as audit
BASE=ROOT/'evals/plugin-v1/results/cp04-final-answers-repair-2026-10-11'
OUT=ROOT/'evals/plugin-v1/results/cp04-final-answer-projection-portable-2026-10-11'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
if __name__=='__main__':
 if (OUT/'observations.json').exists():raise ValueError('preserve prior projection')
 declaration=json.loads((BASE/'declaration.json').read_bytes())
 archive={'plugins/myai-stackguide/scripts/answer_presentation.py':ROOT/'evals/plugin-v1/results/cp04-final-source-archive-2026-10-11/baseline/answer_presentation.py','plugins/myai-stackguide/skills/myai-stackguide/SKILL.md':ROOT/'evals/plugin-v1/results/cp04-final-source-archive-2026-10-11/baseline/shipped-skill-repair.md'}
 for path,digest in declaration['source_hashes'].items():
  source=ROOT/path
  if sha(source)!=digest:
   source=archive[path]
   if sha(source)!=digest:raise ValueError('capture source archive mismatch')
 captured=json.loads((BASE/'observations.json').read_bytes())
 if captured['declaration_sha256']!=runtime.digest(declaration):raise ValueError('capture declaration mismatch')
 value=copy.deepcopy(captured);rows=[]
 for record in value['records']:
  for locale,item in record['answers'].items():
   raw=item['normalized']['answer_markdown']
   item['normalized']['answer_markdown']=presentation.project_answer_locale(raw,locale)
   item['locale_projection_applied']=item['normalized']['answer_markdown']!=raw
   presentation.validate_locale_planning_binding(record['planning'],item['normalized']['planning_binding'])
   output=OUT/record['case_id']/('answer-'+locale+'.md');output.parent.mkdir(parents=True,exist_ok=True);output.write_text(item['normalized']['answer_markdown']+'\n',encoding='utf-8')
  audit.validate_pair(record)
  rows.append({'case_id':record['case_id'],'words':{lang:len(item['normalized']['answer_markdown'].split()) for lang,item in record['answers'].items()},'locale_projection_applied':{lang:item['locale_projection_applied'] for lang,item in record['answers'].items()}})
 sources=[Path(__file__),Path(presentation.__file__),ROOT/'tests/test_plugin_answer_presentation.py',ROOT/'plugins/myai-stackguide/skills/myai-stackguide/SKILL.md',BASE/'declaration.json',BASE/'observations.json',BASE/'audit.json']+list(archive.values())
 current={'generation_capture_path':str(BASE.relative_to(ROOT)).replace('\\','/'),'generation_capture_sha256':sha(BASE/'observations.json'),'source_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sources},'scope':'Deterministic explicit-section display selection; prior actual8model outputs reused; no new model/retrieval/state/translation calls','raw_capture_immutable':True,'model_calls':0,'human_acceptance':False,'promotion_ready':False}
 value.update(projection_only=True,new_model_calls=0,generation_capture_sha256=current['generation_capture_sha256'],declaration_sha256=runtime.digest(current))
 OUT.mkdir(parents=True,exist_ok=True)
 for name,data in [('declaration.json',current),('observations.json',value),('audit.json',{'objective_contract_passed':True,'capture_archive_sources_verified':True,'cases':rows,'human_acceptance':False,'promotion_ready':False})]:
  (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(rows,ensure_ascii=False))
