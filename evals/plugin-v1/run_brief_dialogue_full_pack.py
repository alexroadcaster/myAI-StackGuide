"""Bounded real Codex model stages around the active read-only Brief entry point."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'plugins/myai-stackguide/scripts'))
import recommendation_request as runtime

OUTPUT = ROOT/'evals/plugin-v1/results/cp04-dialogue-full-pack-2026-10-11'
PRIOR = ROOT/'evals/plugin-v1/results/cp04-dialogue-2026-10-11'
CASES = ROOT/'evals/plugin-v1/dialogue-cases-2026-10-11.json'
SOURCES = ROOT/'evals/plugin-v1/dialogue-public-sources-2026-10-11.json'
VOCAB = ROOT/'evals/plugin-v1/dialogue-vocabulary-2026-10-11.json'
SKILL = ROOT/'plugins/myai-stackguide/skills/myai-stackguide/SKILL.md'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def declaration():
    paths = [CASES, SOURCES, VOCAB, SKILL, Path(__file__), Path(runtime.__file__),
        ROOT/'plugins/myai-stackguide/scripts/request_guard.py', ROOT/'plugins/myai-stackguide/scripts/context.py',
        ROOT/'plugins/myai-stackguide/scripts/retrieval.py', ROOT/'plugins/myai-stackguide/scripts/context_pack.py',
        ROOT/'tests/test_plugin_brief_request.py', ROOT/'.codex/config.toml',
        ROOT/'evals/plugin-v1/dialogue-interpretation.schema.json', ROOT/'evals/plugin-v1/dialogue-answer.schema.json',
        OUTPUT/'runtime-skill-before.md', PRIOR/'observations.json', PRIOR/'declaration.json', ROOT/'evals/plugin-v1/run_brief_dialogue.py']
    paths += list((ROOT/'.agents/skills/evaluate-rag').rglob('*'))+list((ROOT/'.agents/skills/write-code-eval').rglob('*'))
    paths += [ROOT/'plugins/myai-stackguide/assets'/n for n in ('catalog.snapshot.json','catalog.search.sqlite','catalog.search-manifest.json','retrieval-policy.json')]
    return dict(schema_version='cp04_brief_dialogue_declaration_v1',
        source_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()},
        model_selection='Inherited repository configuration; no model/effort override',
        expected_model='gpt-6.1-sol', expected_effort='high',
        execution='codex exec --ephemeral --sandbox read-only --json; synthetic conversation history passed between bounded model stages',
        scope='Paired fixed-interpretation replay with complete C9 pack; four RU/EN conversations: real model interpretation, optional question/answer, active C9 retrieval and model explanation. No subagent delegation or state persistence.',
        promotion_ready=False)


def model(case_id, stage, prompt, schema):
    prefix = OUTPUT/case_id/stage
    response = prefix.with_suffix('.response.json')
    if response.exists():
        raise ValueError('preserve prior model response')
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix('.prompt.txt').write_text(prompt, encoding='utf-8')
    binary = shutil.which('codex.cmd') or shutil.which('codex')
    if not binary:
        raise ValueError('Codex CLI unavailable')
    command = [binary, 'exec', '--ephemeral', '--sandbox', 'read-only', '--json', '--output-schema', str(schema),
               '--output-last-message', str(response), '-']
    print('MODEL '+case_id+' '+stage, flush=True)
    started = time.monotonic()
    with prefix.with_suffix('.events.jsonl').open('wb') as out, prefix.with_suffix('.stderr.txt').open('wb') as err:
        result = subprocess.run(command, input=prompt.encode('utf-8'), stdout=out, stderr=err, cwd=ROOT, timeout=240)
    write(prefix.with_suffix('.execution.json'), dict(command=command, exit_code=result.returncode, elapsed_seconds=time.monotonic()-started,
        model_override=False, effort_override=False))
    if result.returncode or not response.exists():
        raise ValueError('Codex stage failed; preserved '+str(prefix.relative_to(ROOT)))
    return json.loads(response.read_text(encoding='utf-8'))


def interpretation_prompt(case, brief, history):
    return ('This is a bounded real model evaluation, not a coding task. Do not use tools, spawn agents, read other files, '
        'write files or access network. The host executes the validated retrieval separately. Interpret the synthetic Brief '
        'using the runtime skill below. Output only the supplied JSON schema. Questions/options must be in '+case['language']+'. '
        'Use English literal terms for public catalog matching. Retain explicit exclusions from the conversation after clarification. '
        'Normalize dependency names to lowercase. For material uncertainty, route/terms/intent must be null and unresolved must contain '
        'a concrete question with alternatives. Do not assume the corpus or essential capabilities when ambiguous. '
        'For a ready request, partition every term exactly once into required_groups or context_terms.\n'
        '<runtime_skill>\n'+SKILL.read_text(encoding='utf-8')+'\n</runtime_skill>\n'
        '<public_vocabulary>\n'+VOCAB.read_text(encoding='utf-8')+'\n</public_vocabulary>\n'
        '<synthetic_conversation>\n'+json.dumps(history, ensure_ascii=False)+'\n</synthetic_conversation>\n'
        '<validated_brief>\n'+json.dumps(brief, ensure_ascii=False)+'\n</validated_brief>')


def capture(saved):
    sources = json.loads(SOURCES.read_bytes())
    cases = json.loads(CASES.read_bytes())['cases']
    records = []
    for case in cases:
        prior_row = json.loads((PRIOR/case['case_id']/'dialogue.json').read_bytes())
        row = copy.deepcopy(prior_row)
        brief = row['brief']
        history = row['history']
        if row['answer'] is not None:
            history = history[:-1]
        interpreted = row['interpretations'][-1]
        bound = dict(interpreted, brief_sha256=runtime.digest(brief), brief_version=brief['brief_version'], language=case['language'])
        outcome = runtime.run(brief, bound, sources['observations'])
        if outcome['status'] != row['requests'][-1]['status']:
            raise ValueError('replayed request drift')
        if outcome.get('selected_ids') != row['requests'][-1].get('selected_ids'):
            raise ValueError('replayed ranking drift')
        row.update(history=history, answer=None, replayed_model_interpretation=True)
        row['requests'][-1] = outcome
        if outcome['status'] == 'ready':
            # Bound model context independently of the 12-card runtime pack ceiling.
            model_cards = outcome['evidence_pack']['cards']
            prompt = ('This is a real model answer evaluation, not implementation. Do not use tools, spawn agents or write files. '
                'Answer in '+case['language']+' using the runtime skill and supplied evidence. Recommend only IDs in the transmitted validated pack; '
                'never recommend excluded products/dependency conflicts. Discuss unknowns conditionally. Host observations below are dated '
                'primary-source reads, distinct from the frozen catalog, and are transient. The answer should help the project owner: '
                'technical work, architecture/data flow, product benefits, complexity drivers, approximate scoped effort with assumptions '
                'or explicit unknown, comparison with equivalent-scope custom development and a concrete first validation. '
                'Do not promise measured savings or compliance. Cite supporting exact URLs. Output the answer JSON schema.\n'
                '<runtime_skill>\n'+SKILL.read_text(encoding='utf-8')+'\n</runtime_skill>\n'
                '<synthetic_conversation>\n'+json.dumps(history, ensure_ascii=False)+'\n</synthetic_conversation>\n'
                '<brief>\n'+json.dumps(brief, ensure_ascii=False)+'\n</brief>\n'
                '<request_and_selection>\n'+json.dumps(dict(request=outcome['request'], selection=outcome['selection']),ensure_ascii=False)+'\n</request_and_selection>\n'
                '<catalog_cards>\n'+json.dumps(model_cards,ensure_ascii=False)+'\n</catalog_cards>\n'
                '<host_public_observations>\n'+json.dumps(sources['source_notes'],ensure_ascii=False)+'\n</host_public_observations>')
            answer = model(case['case_id'], 'answer', prompt, ROOT/'evals/plugin-v1/dialogue-answer.schema.json')
            row['answer'] = answer
            row['transmitted_card_ids'] = [r['card']['identity']['github_repository_id'] for r in model_cards]
            history.append(dict(role='assistant', content=answer['answer_markdown']))
        row['model_input_card_count'] = len(outcome['evidence_pack']['cards']) if outcome['status']=='ready' else 0
        write(OUTPUT/case['case_id']/'dialogue.json', row)
        records.append(row)
    if declaration() != saved:
        raise ValueError('source drift during model capture')
    write(OUTPUT/'observations.json', dict(declaration_sha256=runtime.digest(saved), records=records,
        model_run=True, human_acceptance=False, independent_review=False, promotion_ready=False))
    print('CAPTURED '+str(len(records))+' dialogues',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predeclare',action='store_true')
    args=parser.parse_args()
    declared=declaration()
    if args.predeclare:
        if (OUTPUT/'declaration.json').exists():
            raise ValueError('preserve declaration')
        write(OUTPUT/'declaration.json',declared)
        print(runtime.digest(declared))
    else:
        saved=json.loads((OUTPUT/'declaration.json').read_bytes())
        if saved!=declared or (OUTPUT/'observations.json').exists():
            raise ValueError('declaration drift or existing capture')
        capture(saved)
