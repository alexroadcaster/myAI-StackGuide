"""Bounded actual public capture -> synthetic project writer/publisher join.

No scanner, browser, provider, external integration or C8 provenance activation.
"""
from __future__ import annotations
import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load('cp04_join_runner', ROOT / 'evals/plugin-v1/run_quality_v2.py')
helpers = load('cp04_join_contracts', ROOT / 'tests/test_plugin_contracts.py')
store = load('cp04_join_store', ROOT / 'plugins/myai-stackguide/scripts/state_store.py')
OUTPUT = runner.OUTPUT
PROJECT = ROOT / '.codex-tmp/cp04-v2-join-project'


def validate_capture(capture, pins):
    result, pack, query = capture['retrieval'], capture['candidate_evidence_pack'], capture['query']
    runner.scorer.require(result['pins'] == pack['pins'] == pins, 'capture pins mismatch')
    digest = runner.scorer.digest(query)
    runner.scorer.require(result['query_id'] == pack['query_id'] == query['query_id'] and
                          result['query_sha256'] == pack['query_sha256'] == digest, 'capture query pairing mismatch')
    runner.scorer.require(result['run_id'] == pack['run_id'], 'capture run pairing mismatch')
    contracts = runner.scorer.Contracts()
    contracts.validate('retrieval/catalog-query.schema.json', query)
    contracts.validate('retrieval/retrieval-result.schema.json', result)
    contracts.validate('retrieval/evidence-pack.schema.json', pack)


def replace_run(value, original, actual):
    if isinstance(value, dict):
        return {key: replace_run(item, original, actual) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_run(item, original, actual) for item in value]
    return actual if value == original else value


def joined_state(case, capture, manifest):
    template = helpers.workspace_baseline()
    state = replace_run(template, template['run_id'], capture['retrieval']['run_id'])
    state.update(revision=1, content_revision=1, html_revision=None, scan=None, selection=None,
                 corrections=[], history=[], status='active', phase='report')
    now = store.utc_now()
    state.update(created_at=now, updated_at=now)
    state['index_manifest'] = copy.deepcopy(manifest)
    state['intake']['answers'][0]['sanitized_value'] = case['user_goal']
    state['intake']['answers'][0]['recorded_at'] = now
    state['intake']['questions'][0].update(text='What should improve in this synthetic project?',
        rationale='The frozen goal defines this bounded public comparison.',
        decision_consequence='Compare only the declared capability; adoption remains conditional.',
        answer_examples=[case['user_goal']])
    state['intake']['completion_reason'] = 'Frozen synthetic goal supplied; no private project inspected.'
    brief = state['brief']
    brief.update(goal=case['user_goal'], success_criterion='Review the bounded public capture before adoption.',
                 constraints=copy.deepcopy(capture['query']['constraints']), user_corrections=[],
                 assumptions=['Synthetic project evaluation; no private project scan or implementation.'])
    brief['updated_at'] = now
    brief['details']['problem']['text'] = case['user_goal']
    brief['details']['problem']['limitation'] = 'Frozen synthetic user goal; no inspected customer project.'
    brief['observations'].update(facts=[], inferences=[], evidence=[], gaps=['No private project inspected.'], coverage='partial')
    state['request'].update(query=copy.deepcopy(capture['query']), pack_id=capture['candidate_evidence_pack']['pack_id'],
                            output_intent='decision_report', execution_authorized_by_this_request=False)
    state['retrieval'] = copy.deepcopy(capture['retrieval'])
    state['evidence_pack'] = copy.deepcopy(capture['candidate_evidence_pack'])
    memo = state['memo']
    pack = state['evidence_pack']
    status = 'no_match' if pack['status'] == 'no_match' else 'retrieval_unavailable' if pack['status'] == 'unavailable' else 'conditional_guidance'
    memo.update(status=status, pack_id=pack['pack_id'], pins=copy.deepcopy(pack['pins']),
                summary='Saved actual bounded public retrieval. Adoption fit remains unassessed; no installation or implementation executed.',
                recommendations=[], integration_plan=None, reading_path=[], comparison=[], avoid_defer=[],
                comparison_details=None, avoid_defer_details=[],
                missing_context=['Upstream API, license, integration boundary and project compatibility require verification.'],
                next_action='Inspect source-supported capability and license before proposing a bounded implementation task.',
                category_path=[{'category_id': case['target_category_id'], 'reason': 'Frozen evaluation query route.'}])
    state['presentation'].update(fields=[], default_locale='en', source_locale='en', presentation_revision=1)
    helpers.rebind_presentation(state)
    return state


def main():
    try:
        plan = runner.scorer.load_json(runner.PLAN_PATH)
        observations_path = OUTPUT / 'development-observations.json'
        observations = runner.scorer._load_json_bounded(observations_path, 16 * 1024 * 1024)
        declared = runner.scorer.load_json(OUTPUT / 'declaration.json')
        runner.scorer.require(observations['declaration_sha256'] == runner.scorer.digest(declared) and
                              observations['plan_sha256'] == runner.scorer.digest(plan), 'join observation provenance mismatch')
        calibration = [case for case in plan['cases'] if case['split'] == 'development' and
                       case['case_id'] in plan['calibration_case_ids']]
        runner.scorer.require(len(calibration) == 1, 'expected one predeclared development calibration case')
        case = calibration[0]
        capture = next(item for item in observations['captures'] if item['case_id'] == case['case_id'])
        declaration = {'schema_version': 'cp04_actual_writer_join_declaration_v2', 'case_id': case['case_id'],
            'plan_sha256': runner.scorer.digest(plan), 'observation_file_sha256': runner.scorer.file_sha256(observations_path),
            'query_sha256': runner.scorer.digest(capture['query']), 'result_sha256': runner.scorer.digest(capture['retrieval']),
            'pack_sha256': runner.scorer.digest(capture['candidate_evidence_pack']), 'pins': plan['pins'],
            'source_hashes': {path: runner.scorer.file_sha256(ROOT / path) for path in
                ('evals/plugin-v1/capture_quality_join_v2.py', 'tests/test_plugin_contracts.py',
                 'tests/fixtures/plugin_contracts.json', 'plugins/myai-stackguide/scripts/state_store.py',
                 'plugins/myai-stackguide/scripts/render_report.py')},
            'scope': 'actual public producer capture -> synthetic Brief -> offline schema/relations -> owned locked writer -> HTML publication -> read resume',
            'commands': ['.venv/Scripts/python.exe -B evals/plugin-v1/capture_quality_join_v2.py'],
            'proposed_advice': 'conditional guidance with no adoption recommendations or executed integration',
            'browser_observed': False, 'cp11_complete': False, 'human_acceptance': False}
        runner.write_json('join-declaration.json', declaration)
        validate_capture(capture, plan['pins'])
        manifest = runner.scorer.load_json(ROOT / plan['artifacts']['manifest_path'])
        state = joined_state(case, capture, manifest)
        runner.scorer.Contracts().validate('artifact/project-artifact-state.schema.json', state)
        helpers.check_bundle(state)
        runner.scorer.require(not PROJECT.exists(), 'preserve existing joined project')
        PROJECT.mkdir(parents=True)
        with store.locked_store(PROJECT, create=True) as locked:
            saved_bytes = locked.commit(state, None)
        publication = store.publish(PROJECT, state)
        with store.locked_store(PROJECT, create=False) as locked:
            resumed = locked.load(required=True, writable=True)
            saved_path = locked.state_path
        runner.scorer.require(resumed == state, 'saved state changed or failed resume')
        root = store.output_root(PROJECT, create=False)
        receipt = store.published_receipt(root)
        artifacts = {path.name: runner.scorer.file_sha256(path) for path in root.iterdir() if path.is_file()}
        report = {'schema_version': 'cp04_actual_writer_join_result_v2', 'case_id': case['case_id'],
            'declaration_sha256': runner.scorer.digest(declaration), 'project_fixture': str(PROJECT.relative_to(ROOT)),
            'saved_state_sha256': runner.scorer.file_sha256(saved_path), 'saved_bytes': len(saved_bytes),
            'saved_revision': state['revision'], 'saved_content_revision': state['content_revision'],
            'publication': publication, 'published_receipt': receipt, 'artifact_hashes': artifacts,
            'exact_query_result_pack_preserved': all(runner.scorer.digest(state[key]) == declaration[hash_key]
                 for key, hash_key in [('retrieval', 'result_sha256'), ('evidence_pack', 'pack_sha256')]) and
                 runner.scorer.digest(state['request']['query']) == declaration['query_sha256'],
            'schema_and_relations_validated': True, 'read_resume_identical': resumed == state,
            'canonical_repository_ids': [entry['card']['identity']['github_repository_id'] for entry in state['evidence_pack']['cards']],
            'sanitized_trace': ['Read predeclared development capture.', 'Validated exact public query/result/pack schema and pins.',
                                'Created synthetic Brief/conditional memo.', 'Validated state schema and cross-document relations.',
                                'LockedStore.commit(new_state, previous=None).', 'state_store.publish(project, captured_state).',
                                'LockedStore.load(writable=True); compared exact saved state.'],
            'verdict': 'measured_local_join' if publication['publication_status'] == 'current' else 'no_go',
            'human_acceptance': False, 'cp11_complete': False, 'browser_observed': False,
            'saved_published_failure_recovery': 'not exercised by this bounded join', 'promotion_ready': False}
        runner.write_json('join-result.json', report)
        print(json.dumps({'verdict': report['verdict'], 'case_id': case['case_id'],
                          'publication_status': publication['publication_status'], 'promotion_ready': False}))
        return 0 if report['verdict'] == 'measured_local_join' else 1
    except (OSError, ValueError, KeyError, store.StateError) as error:
        report = {'schema_version': 'cp04_actual_writer_join_failure_v2', 'verdict': 'invalid_input_or_join_failure',
                  'error_type': type(error).__name__, 'reason': str(error), 'promotion_ready': False}
        if not (OUTPUT / 'join-failure.json').exists():
            runner.write_json('join-failure.json', report)
        print(json.dumps(report))
        return 2


if __name__ == '__main__':
    sys.exit(main())
