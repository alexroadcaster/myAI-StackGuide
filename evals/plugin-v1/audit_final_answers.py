"""Objective answer-contract checks; semantic usefulness is reviewed separately."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/'evals/plugin-v1/results/cp04-final-answers-2026-10-11'


def validate_pair(record):
    result=record['result']
    digest=hashlib.sha256(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    cards={r['card']['identity']['github_repository_id'] for r in result['evidence_pack']['cards']}
    excluded=set(result['request']['exclusions']['repository_ids'])
    excluded.update(r['github_repository_id'] for r in result['selection']['excluded'])
    projections=list(record['answers'].values())
    if set(record['answers']) != {'ru','en'}:
        raise ValueError('missing locale projection')
    for projection in projections:
        answer=projection['normalized']
        recommended=set(answer['recommended_ids'])
        if len(recommended)!=len(answer['recommended_ids']) or not recommended<=cards or recommended&excluded:
            raise ValueError('recommendation outside pack or explicitly excluded')
        if projection['canonical_result_sha256']!=digest:
            raise ValueError('stale canonical result')
        if answer['planning_binding']!=projections[0]['normalized']['planning_binding']:
            raise ValueError('planning binding changed across locale')
        if answer['recommended_ids']!=projections[0]['normalized']['recommended_ids']:
            raise ValueError('canonical recommendation changed across locale')
        text=answer['answer_markdown']
        if any(str(rid) in text for rid in cards|excluded) or 'reference_only' in text:
            raise ValueError('internal recommendation metadata leaked into explanation')
        allowed=set()
        def urls(value):
            if isinstance(value,dict):
                for child in value.values(): urls(child)
            elif isinstance(value,list):
                for child in value: urls(child)
            elif isinstance(value,str) and value.startswith('https://'):
                allowed.add(value)
        urls(result)
        visible=set(url.rstrip('.,;') for url in re.findall(r'https://[^\s<>\)\]\}]+',text))
        if not (set(answer['cited_urls'])|visible)<=allowed:
            raise ValueError('citation not present in supplied evidence')
    return True


def audit():
    declaration = json.loads((OUTPUT/'declaration.json').read_bytes())
    for relative, sha in declaration['source_hashes'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==sha, relative
    capture=json.loads((OUTPUT/'observations.json').read_bytes())
    digest=lambda value: hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    assert capture['declaration_sha256']==digest(declaration), 'capture declaration binding'
    frozen=json.loads((OUTPUT/'cases.json').read_bytes())
    assert [r['case_id'] for r in capture['records']]==[r['case_id'] for r in frozen], 'case coverage/order'
    rows=[]
    expected_event_paths=[]
    for record, original in zip(capture['records'],frozen):
        assert {key:record[key] for key in original}==original, 'canonical case mutation'
        validate_pair(record)
        row=dict(case_id=record['case_id'],canonical_result_sha256=next(iter(record['answers'].values()))['canonical_result_sha256'],locales={})
        for locale, value in record['answers'].items():
            prefix=OUTPUT/record['case_id']/('answer-'+locale)
            for suffix in ('.response.json','.events.jsonl','.execution.json','.prompt.txt','.stderr.txt'):
                assert prefix.with_suffix(suffix).is_file(), 'missing stage receipt '+suffix
            assert json.loads(prefix.with_suffix('.response.json').read_bytes())==value['raw'], 'raw response binding'
            receipt=json.loads(prefix.with_suffix('.execution.json').read_bytes())
            assert receipt['exit_code']==0 and not receipt['model_override'] and not receipt['effort_override'], 'model receipt'
            expected_event_paths.append(prefix.with_suffix('.events.jsonl'))
            text=value['normalized']['answer_markdown']
            row['locales'][locale]=dict(recommended_ids=value['normalized']['recommended_ids'],
                words=len(text.split()),characters=len(text),normalization_applied=value['normalization_applied'])
            (OUTPUT/record['case_id']/('answer-'+locale+'.md')).write_text(text+'\n',encoding='utf-8')
        rows.append(row)
    usage={'input_tokens':0,'cached_input_tokens':0,'output_tokens':0}
    tool_items=[]
    for path in expected_event_paths:
        completed=0
        for line in path.read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type') in ('item.completed','item.started') and event['item']['type'] not in ('agent_message','reasoning'):
                tool_items.append(dict(path=path.name,type=event['item']['type']))
            if event.get('type')=='turn.completed':
                completed+=1
                for key in usage:
                    usage[key]+=event['usage'].get(key,0)
        assert completed==1, 'missing or duplicate model completion'
    assert not tool_items, tool_items
    value=dict(cases=rows,source_hashes_verified=True,tool_items=tool_items,usage=usage,
        objective_contract_passed=True,human_acceptance=False,promotion_ready=False)
    (OUTPUT/'audit.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(value,ensure_ascii=False))


if __name__=='__main__':
    audit()
