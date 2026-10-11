"""Objective capture checks; semantic usefulness requires explicit review."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'evals/plugin-v1/results'


def audit(name):
    folder = RESULTS / name
    declaration = json.loads((folder / 'declaration.json').read_bytes())
    for source, expected in declaration['source_hashes'].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == expected, source
    observations = json.loads((folder / 'observations.json').read_bytes())
    rows = []
    usage = {'input_tokens': 0, 'cached_input_tokens': 0, 'output_tokens': 0}
    calls = 0
    for path in folder.glob('CP04-*/*.events.jsonl'):
        calls += 1
        for line in path.read_text(encoding='utf-8').splitlines():
            event = json.loads(line)
            if event.get('type') == 'item.completed':
                assert event['item']['type'] in ('agent_message', 'reasoning'), event
            if event.get('type') == 'turn.completed':
                for key in usage:
                    usage[key] += event['usage'].get(key, 0)
    for row in observations['records']:
        answer = row['answer']
        request = row['requests'][-1]
        excluded = request['request']['exclusions']
        recommended = answer['recommended_ids']
        assert set(recommended) <= set(row['transmitted_card_ids'])
        assert not set(recommended) & set(excluded['repository_ids'])
        assert not set(request['selected_ids']) & set(excluded['repository_ids'])
        if 'queue' in row['case_id']:
            assert set(excluded['dependencies']) == {'redis', 'valkey', 'rabbitmq', 'kubernetes'}
            assert not set(request['request']['catalog_query']['variants'][0]['terms']) & set(excluded['dependencies'])
        else:
            assert row['requests'][0]['status'] == 'needs_clarification'
            assert row['requests'][0]['retrieval_calls'] == 0
            assert row['interpretations'][0]['route'] is None
            assert 79317191 in excluded['repository_ids']
            assert row['brief']['brief_version'] == 2
        rows.append(dict(case_id=row['case_id'], recommendations=recommended,
            literal_newline_escapes=answer['answer_markdown'].count('\\n'),
            questions=len(row['requests'][0].get('questions', [])),
            transmitted_cards=len(row['transmitted_card_ids']),
            pack_cards=len(request['evidence_pack']['cards']),
            selected_ids=request['selected_ids']))
    return dict(name=name, cases=rows, model_calls=calls, usage=usage,
        source_hashes_verified=True, tool_items=0, semantic_verdict='explicit_self_review_required')


if __name__ == '__main__':
    before = audit('cp04-dialogue-2026-10-11')
    after = audit('cp04-dialogue-full-pack-2026-10-11')
    for left, right in zip(before['cases'], after['cases']):
        assert left['case_id'] == right['case_id']
        assert left['selected_ids'] == right['selected_ids']
    output = RESULTS / 'cp04-dialogue-full-pack-2026-10-11/audit.json'
    output.write_text(json.dumps(dict(before=before, after=after,
        ranking_preserved=True, promotion_ready=False), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    report = ROOT / 'docs/reports/cp04-brief-dialogue-2026-10-11.md'
    marker = '\n## Captured comparison\n'
    text = report.read_text(encoding='utf-8').split(marker)[0]
    text += marker + '\n| Case | Six-card answer | Complete-pack answer | Clarifying questions before retrieval |\n| --- | --- | --- | --- |\n'
    links = []
    for left, right in zip(before['cases'], after['cases']):
        text += f"| {left['case_id']} | {left['recommendations']} | {right['recommendations']} | {right['questions']} |\n"
        row_path = RESULTS / after['name'] / right['case_id'] / 'dialogue.json'
        row = json.loads(row_path.read_bytes())
        transcript = row_path.with_name('transcript.md')
        sections = ['# '+right['case_id'], 'Presentation-only transcript. Raw dialogue.json is authoritative; literal newline escapes are expanded for reading.']
        for message in row['history']:
            content = message['content']
            if isinstance(content, list):
                content = '\n\n'.join(q['question']+'\n\n'+ '\n'.join('- '+option for option in q['options']) for q in content)
            sections += ['## '+message['role'], content.replace('\\n', '\n')]
        transcript.write_text('\n\n'.join(sections)+'\n', encoding='utf-8')
        links.append(f"[Full {right['case_id']} transcript](../../{transcript.relative_to(ROOT).as_posix()})")
    text += '\n\n'+'\n\n'.join(links)+'\n'
    text += f"\nObserved model calls: baseline {before['model_calls']}; paired answer replay {after['model_calls']}. Usage (input/cached input/output): baseline {before['usage']}; replay {after['usage']}. Cached input is a subset of input, not an additional token total. No dollar cost or comparative speed claim is inferred.\n"
    report.write_text(text, encoding='utf-8')
    print(output.relative_to(ROOT))
