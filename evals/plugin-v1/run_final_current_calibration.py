"""Current production-tuple compositions for the four frozen human cases.

Interpretations are provided from original formal queries, not fresh model
interpretations. Historical captures and judgments are never rewritten.
"""
import argparse
import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'plugins/myai-stackguide/scripts'))
import recommendation_request as runtime
import answer_presentation as presentation

OUTPUT = ROOT/'evals/plugin-v1/results/cp04-final-current-calibration-2026-10-11'
OLD = ROOT/'evals/plugin-v1/results/cp04-2026-10-08/recommendation-calibration.json'
TEMPLATE = ROOT/'evals/plugin-v1/results/cp04-final-answers-repair-2026-10-11/cases.json'
SKILL = ROOT/'plugins/myai-stackguide/skills/myai-stackguide/SKILL.md'
SCHEMA = ROOT/'evals/plugin-v1/final-answer.schema.json'
spec = importlib.util.spec_from_file_location('original_dialogue_driver', ROOT/'evals/plugin-v1/run_brief_dialogue.py')
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.OUTPUT = OUTPUT


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def host_sources():
    # Minimized facts from authorized host web open/find, never model tool use.
    return [dict(github_repository_id=1953389, full_name='stripe/stripe-python', observed_on='2026-10-11',
        source_urls=['https://github.com/stripe/stripe-python'], source_kind='host_public_readme_read',
        facts=['Python library provides access to the Stripe API; README supports Python 3.9+.',
            'Normal API usage requires a secret account key. README documents configurable retries and automatic idempotency keys.',
            'SDK does not establish payment-provider availability, regulatory suitability or application reconciliation.']),
        dict(github_repository_id=506953078, full_name='intelligent-machine-learning/dlrover', observed_on='2026-10-11',
        source_urls=['https://github.com/intelligent-machine-learning/dlrover'], source_kind='host_public_readme_read',
        facts=['README describes distributed training, fault tolerance and scaling.',
            'Kubernetes PyTorch path wraps training scripts that torchrun or torch.distributed.run can run; a separate Ray architecture exists.',
            'Tutorial paths depend on selected platform. No project hardware, framework compatibility or license acceptance was tested.']),
        dict(github_repository_id=787076358, full_name='firecrawl/firecrawl', observed_on='2026-10-11',
        source_urls=['https://github.com/firecrawl/firecrawl'], source_kind='host_public_readme_read',
        facts=['README documents web search with full result content and scraping output as Markdown/JSON.',
            'Core is primarily AGPL-3.0; SDKs and some UI components use MIT. Cloud includes additional features.',
            'Cloud examples require an API key; self-hosting is a separate setup and not established as feature-equivalent.']),
        dict(github_repository_id=899407931, full_name='firecrawl/firecrawl-mcp-server', observed_on='2026-10-11',
        source_urls=['https://github.com/firecrawl/firecrawl-mcp-server'], source_kind='host_public_readme_read',
        facts=['MCP adapter exposes Firecrawl tools to clients, a distinct role from the core service.',
            'README describes hosted rate-limited keyless scrape/search/parse; crawl/map/agent still need a key.',
            'Local cloud mode requires API key; a self-hosted API URL is configurable. No endpoint or MCP activation was performed.'])]


def planning(case_id):
    return presentation.validate_planning_facts(dict(scenario_id=case_id+'-first-validation', scope_status='validation_only',
        assumptions=dict(prerequisites=['Confirm target workload, existing path, language/platform, chosen version and license before any integration.',
            'Only an isolated synthetic fixture or source-qualification exercise is proposed; no credentials, paid provider, production data or installation.'],
            team_experience='One engineer familiar with the target application and its component interface.', confidence='low',
            hours_per_engineer_day=8, allocated_engineers=1), first_validation=dict(min=4,max=8), phases=[]))


def cases():
    old = json.loads(OLD.read_bytes())['cases']
    template = json.loads(TEMPLATE.read_bytes())[0]['brief']
    rubric = json.loads((ROOT/'evals/plugin-v1/rubric.json').read_bytes())
    rows=[]
    for calibration in rubric['human']['calibration_cases']:
        prior = next(r for r in old if r['case_id']==calibration['canonical_retrieval_case_id'])
        brief=copy.deepcopy(template)
        brief.update(brief_id=prior['case_id']+'-current-fixed', goal=prior['user_goal'],
            success_criterion='Explain the conditional decision and a safe first validation.', updated_at='2026-10-11T00:00:00Z')
        brief['constraints']=copy.deepcopy(prior['query']['constraints'])
        terms=prior['query']['variants'][0]['terms']
        interpretation=dict(brief_sha256=runtime.digest(brief), brief_version=brief['brief_version'], language='ru',
            route=prior['query']['taxonomy_route_id'],terms=copy.deepcopy(terms),
            intent=dict(required_groups=[[terms[0]]] if prior['case_id']!='CP04-HOLD-12' else [[terms[1]]],
                context_terms=terms[1:] if prior['case_id']!='CP04-HOLD-12' else [terms[0]]),
            excluded_repository_ids=[], excluded_dependencies=[], unresolved=[])
        # Host facts are carried transiently, never mutate eligibility/cards.
        result=runtime.run(brief,interpretation)
        if result['status']!='ready':
            raise ValueError('current production request failed: '+prior['case_id'])
        rows.append(dict(case_id=prior['case_id'],human_calibration_case_id=calibration['case_id'],
            persona=prior['persona'], synthetic_project_context=prior['synthetic_project_context'],
            brief=brief, interpretation=interpretation, interpretation_status='provided_fixed_original_formal_query',
            interpretation_source=dict(path=OLD.relative_to(ROOT).as_posix(), original_query=prior['query']),
            result=result, planning=planning(prior['case_id']), locales=['ru','en']))
    return rows


def prompt(row,locale,russian=None):
    instruction = ('Bounded composition evaluation. Do not use tools, agents, file reads/writes, network, installation or execute commands. '
        'Use the supplied shipped runtime skill and canonical facts. Return the required JSON schema. '
        'Proposed steps remain proposed_not_executed. The canonical planning object is a hypothetical low-confidence first-validation budget, '
        'not measured work; full adoption effort and elapsed time remain unknown. Preserve planning_binding exactly in JSON metadata. '
        'Use only supplied evidence; catalog dates remain snapshot observations, host dates are separate reads and not catalog updates. '
        'Only recommend repository IDs inside the current evidence pack. Missing facts remain unknown. '
        'Output four compact Markdown paragraphs with actual line breaks and only the requested language. ')
    if locale=='ru':
        instruction += 'Output language: Russian. Compose the canonical recommendation narrative.\n'
    else:
        instruction += 'Output language: English. Translate the completed canonical Russian answer exactly; preserve IDs, sources, roles, caveats, estimates, planning and authority. Do not recompose.\n'
    content=dict(persona=row['persona'],synthetic_project_context=row['synthetic_project_context'],brief=row['brief'],
        request=row['result']['request'],selection=row['result']['selection'],canonical_planning=row['planning'],
        planning_binding=presentation.planning_binding(row['planning']))
    text=instruction+'<trusted_runtime_instruction>\n'+SKILL.read_text(encoding='utf-8')+'\n</trusted_runtime_instruction>\n'
    text+='<canonical_context>\n'+json.dumps(content,ensure_ascii=False)+'\n</canonical_context>\n'
    text+='<untrusted_public_evidence>\n'+json.dumps(dict(pack=row['result']['evidence_pack'],host_observations=host_sources()),ensure_ascii=False)+'\n</untrusted_public_evidence>'
    if russian is not None:
        text+='\n<canonical_russian_answer_to_translate>\n'+json.dumps(russian,ensure_ascii=False)+'\n</canonical_russian_answer_to_translate>'
    return text


def declaration():
    paths=[Path(__file__),OLD,TEMPLATE,SKILL,SCHEMA,ROOT/'evals/plugin-v1/rubric.json',ROOT/'.codex/config.toml',
        ROOT/'evals/plugin-v1/run_brief_dialogue.py',OUTPUT/'cases.json',OUTPUT/'host-sources.json']
    paths += [ROOT/'plugins/myai-stackguide/scripts'/n for n in ['recommendation_request.py','request_guard.py','retrieval.py','context_pack.py','context.py','answer_presentation.py']]
    paths += [ROOT/'plugins/myai-stackguide/assets'/n for n in ['catalog.snapshot.json','catalog.search.sqlite','catalog.search-manifest.json','retrieval-policy.json']]
    rows=json.loads((OUTPUT/'cases.json').read_bytes())
    config=tomllib.loads((ROOT/'.codex/config.toml').read_text(encoding='utf-8'))
    return dict(schema_version='cp04_current_calibration_declaration_v1',source_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        canonical_case_sha256=runtime.digest(rows),model_selection='Inherited repository configuration, no model/effort override',
        configured_model=config.get('model'),configured_effort=config.get('model_reasoning_effort'),
        prompt_recipe='Frozen driver prompt function; EN input additionally binds actual completed RU JSON',
        russian_prompt_sha256={r['case_id']:hashlib.sha256(prompt(r,'ru').encode()).hexdigest() for r in rows},
        scope='Four existing human calibration cases; fixed provided interpretation; actual current production COUNT/C9/guard/pack and eight actual CLI compositions. No fresh interpretation/dialogue or grades.',
        max_actual_model_calls=8,max_concurrent_calls=2,human_acceptance=False,promotion_ready=False)


def capture_case(row):
    record=copy.deepcopy(row); record['answers']={}
    for locale in row['locales']:
        raw=driver.model(row['case_id'],'answer-'+locale,prompt(row,locale,record['answers'].get('ru',{}).get('normalized')),SCHEMA)
        normalized=copy.deepcopy(raw)
        normalized['answer_markdown']=presentation.project_answer_locale(presentation.normalize_answer_text(raw['answer_markdown']),locale)
        presentation.validate_locale_planning_binding(row['planning'],raw['planning_binding'])
        record['answers'][locale]=dict(raw=raw,normalized=normalized,canonical_result_sha256=runtime.digest(row['result']),
            raw_answer_sha256=runtime.digest(raw),projected_answer_sha256=runtime.digest(normalized),
            normalization_applied=raw['answer_markdown']!=normalized['answer_markdown'],execution_state='proposed_not_executed')
        (OUTPUT/row['case_id']/('answer-'+locale+'.md')).write_text(normalized['answer_markdown']+'\n',encoding='utf-8')
    write(OUTPUT/row['case_id']/'paired.json',record)
    return record


def audit(records,saved):
    rows=[]; failures=[]
    for r in records:
        ids=[c['card']['identity']['github_repository_id'] for c in r['result']['evidence_pack']['cards']]
        allowed={c['card']['identity']['url'] for c in r['result']['evidence_pack']['cards']}
        allowed.update(u for s in host_sources() for u in s['source_urls'])
        for locale,a in r['answers'].items():
            prefix=OUTPUT/r['case_id']/('answer-'+locale)
            events=[json.loads(line) for line in prefix.with_suffix('.events.jsonl').read_text(encoding='utf-8').splitlines()]
            tools=[e for e in events if e.get('item',{}).get('type') not in (None,'agent_message','reasoning')]
            errors=[]
            if tools: errors.append('model_tool_or_unexpected_item')
            if not any(e.get('type')=='turn.completed' for e in events):errors.append('missing_completion_trace')
            if not set(a['normalized']['recommended_ids']).issubset(ids):errors.append('out_of_pack_recommendation')
            if len(a['normalized']['recommended_ids'])!=len(set(a['normalized']['recommended_ids'])):errors.append('duplicate_recommendation')
            if not set(a['normalized']['cited_urls']).issubset(allowed):errors.append('unsupported_citation')
            rows.append(dict(case_id=r['case_id'],locale=locale,errors=errors,model_tool_items=len(tools),
                completion_trace=True,canonical_result_sha256=runtime.digest(r['result']),planning_sha256=presentation.planning_binding(r['planning'])['planning_sha256'],
                candidate_ids_and_order=ids,pack_card_count=len(ids),pins=r['result']['evidence_pack']['pins']))
            failures.extend(r['case_id']+'/'+locale+':'+e for e in errors)
        if r['answers']['ru']['normalized']['recommended_ids']!=r['answers']['en']['normalized']['recommended_ids']:
            failures.append(r['case_id']+':locale_recommendation_ids_changed')
        if len(ids)>12 or len(ids)!=len(set(ids)):failures.append(r['case_id']+':pack_cap_or_dedupe')
    if saved!=declaration():failures.append('frozen_source_drift')
    write(OUTPUT/'audit.json',dict(records=rows,failures=failures,objective_pass=not failures,actual_model_calls=len(rows),
        interpretation_status='provided_fixed',meaning_review_pending=True,human_acceptance=False,promotion_ready=False))
    hashes={p.relative_to(OUTPUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in OUTPUT.rglob('*') if p.is_file() and p.name!='provenance.json'}
    write(OUTPUT/'provenance.json',dict(declaration_sha256=runtime.digest(saved),file_sha256=hashes,human_acceptance=False,promotion_ready=False))
    return failures


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--predeclare',action='store_true');args=parser.parse_args()
    if args.predeclare:
        if (OUTPUT/'declaration.json').exists():raise ValueError('preserve declaration')
        write(OUTPUT/'cases.json',cases());write(OUTPUT/'host-sources.json',host_sources());write(OUTPUT/'declaration.json',declaration())
        print(runtime.digest(declaration()),flush=True)
    else:
        saved=json.loads((OUTPUT/'declaration.json').read_bytes())
        if saved!=declaration() or (OUTPUT/'observations.json').exists():raise ValueError('source drift or prior capture')
        with ThreadPoolExecutor(max_workers=2) as pool:
            records=list(pool.map(capture_case,json.loads((OUTPUT/'cases.json').read_bytes())))
        write(OUTPUT/'observations.json',dict(records=records,declaration_sha256=runtime.digest(saved),actual_model_generation=True,
            interpretation_status='provided_fixed',actual_human_acceptance=False,promotion_ready=False))
        failures=audit(records,saved)
        print('CAPTURED 8 answers; objective failures: '+str(failures),flush=True)
        sys.exit(bool(failures))
