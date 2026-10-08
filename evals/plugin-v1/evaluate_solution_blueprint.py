"""Deterministic captured solution format checks; no semantic quality verdict.

Metadata references are data, never paths to open. The pinned source packet owns
project/capture facts; this two-case profile owns only deterministic format rules.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
LANE = 'evals/plugin-v1/results/cp04-v2-2026-10-08/'
SOURCE_PATH = LANE + 'project-fit-explanations.json'
INSTRUCTION_PATH = 'plugins/myai-stackguide/skills/myai-stackguide/SKILL.md'
SOURCE_SHA256 = '32e7f42a8535d32ab429a42b0d3c176060b73e5232ebf3f7a995f9937ab46856'
SOURCE_CANONICAL_SHA256 = '4e011ab3603883afd7997de94f76ef98f7f0d96fdc793ed695ce32a30c4617cf'
ACCEPTANCE_SHA256 = 'cb7dfae5f5083e2f272cde564739997e3bd2566576739aad1d7ffff6ed57db6a'
ACCEPTANCE_CANONICAL_SHA256 = '9c7ddda01fae6f8c802776ec648d9e7b20bb325f987ed236737235f572e232d1'
INSTRUCTION_SHA256 = '5f55458d649183e4869c7571cde3d19dfae55b7a19bf573008ea3eb4b1f26148'
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_ISSUES = 32
PROFILE = {'CP04-V2-D05': ('discover', 'one_endpoint_pilot', False),
           'CP04-V2-H15': ('scope_discovery', 'synthetic_app_validation', True)}
CONTEXT_KEYS = ('synthetic_context', 'persona', 'confirmed_goals', 'confirmed_constraints',
                'unknowns', 'source_projection', 'selected_ids', 'capture_binding')
BINDING_KEYS = ('selected_ids', 'canonical_roles', 'capture_binding', 'hypothetical_assumptions',
                'time_estimate', 'integration_phases', 'action_state')
STACK_STATES = {'retained_if_present', 'retained_hypothetically_available',
                'proposed_new_conditional', 'alternative_not_joint_install',
                'proposed_validation_fixture', 'unknown_prerequisite'}
FALSE_FLAGS = {'human_calibrated', 'promotion_ready', 'estimate_calibrated',
               'installed_runtime_verified', 'project_benefit_measured', 'executed',
               'measured', 'delivery_commitment', 'binding_delivery', 'actual_elapsed_measured'}
PRIVATE_KEYS = {'raw_project_context', 'raw_source', 'private_payload', 'secrets', 'credentials', 'api_key'}
POINTER_KEYS = set(CONTEXT_KEYS + BINDING_KEYS) | FALSE_FLAGS | PRIVATE_KEYS | {
    'records', 'stack', 'architecture', 'complexity', 'product', 'technical', 'authoring_protocol',
    'time_estimate', 'integration_phases', 'first_validation', 'full_scoped_adoption',
    'remaining_after_pilot', 'discovery_only', 'effort_engineer_hours', 'effort_engineer_days_8h',
    'elapsed_working_days_excluding_waits', 'human_response', 'action_state', 'presentation_bindings', 'ru', 'en'}


class ContractError(ValueError):
    def __init__(self, category, pointer):
        self.category, self.pointer = category, pointer
        super().__init__(category)


def require(condition, category, pointer):
    if not condition:
        raise ContractError(category, pointer)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def same(actual, expected):
    """Canonical JSON equality preserves bool/number distinctions in bindings."""
    return canonical(actual) == canonical(expected)


def text(value, pointer):
    require(isinstance(value, str) and bool(value.strip()), 'required_structure', pointer)


def strings(value, pointer):
    require(isinstance(value, list) and bool(value), 'required_structure', pointer)
    for index, item in enumerate(value):
        text(item, pointer + '/' + str(index))


def obj(value, keys, pointer):
    require(isinstance(value, dict), 'required_structure', pointer)
    for key in keys:
        require(key in value, 'required_structure', pointer + '/' + key)


def boundary(value, pointer='', depth=0, exact=True):
    """Bound traversal and reject structured authority/privacy inflation.

    Unknown object keys are never echoed into diagnostic pointers. This cannot
    detect secrets or contradictory claims embedded in otherwise valid prose.
    """
    require(depth <= 32, 'input_limit', pointer)
    if isinstance(value, dict):
        for key, item in value.items():
            child_exact = exact and key in POINTER_KEYS
            child = pointer + '/' + key if child_exact else pointer
            if key in FALSE_FLAGS:
                require(item is False, 'execution_boundary', child)
            if key == 'action_state':
                require(item == 'proposed_not_executed', 'execution_boundary', child)
            if key == 'human_response':
                require(item is None, 'execution_boundary', child)
            if key in PRIVATE_KEYS:
                require(item is None or item == '' or item == [], 'privacy_boundary', pointer)
            # Ordinary names are traversed without incorporating arbitrary keys.
            boundary(item, child, depth + 1, child_exact)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            boundary(item, pointer + '/' + str(index) if exact else pointer, depth + 1, exact)
    elif isinstance(value, float):
        require(math.isfinite(value), 'estimate_range', pointer)


def positive(value, pointer):
    require(type(value) in (int, float), 'estimate_range', pointer)
    try:
        valid = math.isfinite(value) and value > 0
    except OverflowError:
        valid = False
    require(valid, 'estimate_range', pointer)


def range_value(value, pointer):
    require(isinstance(value, list) and len(value) == 2, 'estimate_range', pointer)
    for index, bound in enumerate(value):
        positive(bound, pointer + '/' + str(index))
    require(value[0] <= value[1], 'estimate_range', pointer)
    return value


def equal_range(actual, expected, pointer):
    bounds = range_value(actual, pointer)
    require(all(math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9) for a, b in zip(bounds, expected)),
            'estimate_arithmetic', pointer)


def phase_ids(value, known, pointer):
    strings(value, pointer)
    require(len(value) == len(set(value)) and set(value) <= known, 'phase_identity', pointer)
    return value


def estimates(record, pointer):
    discovery, pilot, partial = PROFILE[record['case_id']]
    phases = record['integration_phases']
    require(isinstance(phases, list) and bool(phases), 'required_structure', pointer + '/integration_phases')
    by_id = {}
    for index, phase in enumerate(phases):
        path = pointer + '/integration_phases/' + str(index)
        obj(phase, ('phase_id', 'labels', 'effort_engineer_hours', 'purpose', 'exit'), path)
        text(phase['phase_id'], path + '/phase_id')
        require(phase['phase_id'] not in by_id, 'phase_identity', path + '/phase_id')
        obj(phase['labels'], ('ru', 'en'), path + '/labels')
        for locale in ('ru', 'en'):
            text(phase['labels'][locale], path + '/labels/' + locale)
        for key in ('purpose', 'exit'):
            text(phase[key], path + '/' + key)
        by_id[phase['phase_id']] = range_value(phase['effort_engineer_hours'], path + '/effort_engineer_hours')
    path = pointer + '/time_estimate'
    time = record['time_estimate']
    required = ('kind', 'confidence', 'scope', 'team_size', 'hours_per_engineer_day', 'aggregation',
                'first_validation', 'full_scoped_adoption', 'elapsed_rounding',
                'external_waiting_working_days', 'actual_start_to_finish_working_days', 'waiting_note')
    obj(time, required, path)
    require(set(time) <= set(required) | {'remaining_after_pilot', 'discovery_only'}, 'estimate_boundary', path)
    require(time['kind'] == 'expert_assumption_not_measured_or_binding', 'estimate_boundary', path + '/kind')
    for key in ('confidence', 'scope', 'aggregation', 'elapsed_rounding', 'waiting_note'):
        text(time[key], path + '/' + key)
    require(type(time['team_size']) is int and time['team_size'] == 1, 'estimate_boundary', path + '/team_size')
    positive(time['hours_per_engineer_day'], path + '/hours_per_engineer_day')
    require(time['hours_per_engineer_day'] == 8, 'estimate_arithmetic', path + '/hours_per_engineer_day')
    for key in ('external_waiting_working_days', 'actual_start_to_finish_working_days'):
        require(time[key] is None, 'estimate_boundary', path + '/' + key)

    def summary(value, ids, name, elapsed=False):
        p = path + '/' + name
        obj(value, ('effort_engineer_hours', 'effort_engineer_days_8h'), p)
        keys = {'effort_engineer_hours', 'effort_engineer_days_8h'}
        if name in ('first_validation', 'full_scoped_adoption'):
            keys.add('included_phases')
        if elapsed:
            keys.add('elapsed_working_days_excluding_waits')
        require(set(value) == keys, 'estimate_boundary', p)
        expected = [sum(by_id[item][axis] for item in ids) for axis in (0, 1)]
        equal_range(value['effort_engineer_hours'], expected, p + '/effort_engineer_hours')
        equal_range(value['effort_engineer_days_8h'], [bound / 8 for bound in expected], p + '/effort_engineer_days_8h')
        if elapsed:
            equal_range(value.get('elapsed_working_days_excluding_waits'),
                        [math.ceil(bound / 8) for bound in expected], p + '/elapsed_working_days_excluding_waits')
        return expected

    first = time['first_validation']
    obj(first, ('included_phases',), path + '/first_validation')
    first_ids = phase_ids(first['included_phases'], set(by_id), path + '/first_validation/included_phases')
    require(set(first_ids) == {discovery, pilot}, 'phase_identity', path + '/first_validation/included_phases')
    first_hours = summary(first, first_ids, 'first_validation', True)
    full = time['full_scoped_adoption']
    if partial:
        require(full is None and time.get('remaining_after_pilot') is None,
                'estimate_boundary', path + '/full_scoped_adoption')
        require(set(by_id) == set(first_ids), 'phase_identity', pointer + '/integration_phases')
        summary(time.get('discovery_only'), [discovery], 'discovery_only')
        full_hours = None
    else:
        obj(full, ('included_phases',), path + '/full_scoped_adoption')
        ids = phase_ids(full['included_phases'], set(by_id), path + '/full_scoped_adoption/included_phases')
        require(set(ids) == set(by_id), 'phase_identity', path + '/full_scoped_adoption/included_phases')
        full_hours = summary(full, ids, 'full_scoped_adoption', True)
        remaining = [item for item in ids if item not in first_ids]
        require(bool(remaining), 'phase_identity', path + '/remaining_after_pilot')
        summary(time.get('remaining_after_pilot'), remaining, 'remaining_after_pilot')
    return {'case_id': record['case_id'], 'phase_ids': list(by_id),
            'first_validation_engineer_hours': first_hours, 'full_scoped_adoption_engineer_hours': full_hours,
            'full_scope_unknown': partial, 'pilot_count_in_first_validation': first_ids.count(pilot)}


def record_contract(record, source, pointer):
    obj(record, CONTEXT_KEYS + ('case_id', 'stack', 'technical', 'architecture', 'product',
        'problem_coverage', 'complexity', 'time_estimate', 'integration_phases',
        'hypothetical_assumptions', 'presentation', 'presentation_bindings',
        'canonical_roles', 'evidence_labels', 'decision', 'reuse_custom_current_comparison',
        'decisive_next_question', 'rollback', 'action_state', 'compatibility', 'project_benefit_measured'), pointer)
    for key in CONTEXT_KEYS:
        require(same(record[key], source[key]), 'context_binding', pointer + '/' + key)
    require(record['compatibility'] == 'unknown', 'execution_boundary', pointer + '/compatibility')
    proposals = source['proposals']
    roles = [{'github_repository_id': item['github_repository_id'], 'role': item['canonical_role'],
              **{key: item[key] for key in ('adoption_fit', 'source_refs', 'evidence_refs')}} for item in proposals]
    labels = [{key: item[key] for key in ('evidence_label', 'github_repository_id',
                                         'capability_source_field', 'capability_binding')} for item in proposals]
    for key, expected in (('canonical_roles', roles), ('evidence_labels', labels)):
        require(same(record[key], expected), 'provenance_ownership', pointer + '/' + key)
    for key in ('decision', 'decisive_next_question', 'rollback'):
        text(record[key], pointer + '/' + key)
    strings(record['hypothetical_assumptions'], pointer + '/hypothetical_assumptions')
    shapes = {'technical': ('source_supported_coverage', 'proposed_work', 'unsupported_claims'),
              'architecture': ('status', 'proposed_flow', 'data_ownership', 'boundary'),
              'product': ('confirmed_goal', 'benefit_hypothesis', 'validation_output'),
              'problem_coverage': ('reuse_covers', 'remaining_project_work'),
              'complexity': ('level', 'status', 'drivers', 'higher_or_reestimate_if')}
    for section, keys in shapes.items():
        obj(record[section], keys, pointer + '/' + section)
        for key in keys:
            value = record[section][key]
            (strings if isinstance(value, list) else text)(value, pointer + '/' + section + '/' + key)
    require(record['architecture']['status'] in {'conditional_not_observed', 'not_settled_conditional'},
            'execution_boundary', pointer + '/architecture/status')
    require(record['complexity']['status'] == 'expert_planning_assumption', 'estimate_boundary', pointer + '/complexity/status')
    if PROFILE[record['case_id']][2]:
        require(record['complexity']['level'] == 'unknown_for_full_adoption', 'estimate_boundary', pointer + '/complexity/level')
    options = {item['github_repository_id']: item for item in source['source_projection']['reference_options']}
    proposed = 0
    used = set()
    require(isinstance(record['stack'], list) and bool(record['stack']), 'required_structure', pointer + '/stack')
    for index, item in enumerate(record['stack']):
        path = pointer + '/stack/' + str(index)
        obj(item, ('member', 'state', 'role'), path)
        text(item['member'], path + '/member'); text(item['role'], path + '/role')
        require(isinstance(item['state'], str) and item['state'] in STACK_STATES, 'stack_state', path + '/state')
        repo_id = item.get('github_repository_id')
        if repo_id is not None:
            require(type(repo_id) is int and repo_id in options and repo_id not in used, 'provenance_ownership', path + '/github_repository_id')
            require(item['member'] == options[repo_id]['full_name'], 'provenance_ownership', path + '/member')
            used.add(repo_id)
        proposed += item['state'] == 'proposed_new_conditional'
    require(proposed <= 1, 'alternative_joint_adoption', pointer + '/stack')
    comparisons = record['reuse_custom_current_comparison']
    require(isinstance(comparisons, list) and len(comparisons) >= 3, 'required_structure', pointer + '/reuse_custom_current_comparison')
    for index, item in enumerate(comparisons):
        path = pointer + '/reuse_custom_current_comparison/' + str(index)
        keys = ('option', 'same_scope', 'advantage', 'remaining_cost', 'condition')
        obj(item, keys, path)
        for key in keys:
            text(item[key], path + '/' + key)
    require(len({item['option'] for item in comparisons}) == len(comparisons),
            'required_structure', pointer + '/reuse_custom_current_comparison')
    observation = estimates(record, pointer)
    obj(record['presentation'], ('ru', 'en'), pointer + '/presentation')
    obj(record['presentation_bindings'], ('ru', 'en'), pointer + '/presentation_bindings')
    for locale in ('ru', 'en'):
        sections = record['presentation'][locale]
        require(isinstance(sections, list) and bool(sections), 'required_structure', pointer + '/presentation/' + locale)
        for index, item in enumerate(sections):
            path = pointer + '/presentation/' + locale + '/' + str(index)
            obj(item, ('title', 'body'), path)
            text(item['title'], path + '/title'); text(item['body'], path + '/body')
        binding = record['presentation_bindings'][locale]
        obj(binding, BINDING_KEYS, pointer + '/presentation_bindings/' + locale)
        for key in BINDING_KEYS:
            require(same(binding.get(key), record[key]), 'presentation_binding', pointer + '/presentation_bindings/' + locale + '/' + key)
        for key in ('architecture', 'complexity'):
            if any(key in record['presentation_bindings'][loc] for loc in ('ru', 'en')):
                require(same(binding.get(key), record[key]), 'presentation_binding', pointer + '/presentation_bindings/' + locale + '/' + key)
    return observation


def evaluate(data, source, acceptedpins):
    """Pure validation: no file, source URL, instruction or provider access."""
    result = {'schema_version': 'cp04_solution_blueprint_eval_v1', 'verdict': 'invalid_contract',
              'semantic_review_required': True, 'promotion_ready': False, 'human_calibrated': False,
              'estimate_calibrated': False, 'installed_runtime_verified': False,
              'owner_format_accepted': False, 'issues': [], 'case_observations': [],
              'limitations': ['natural_language_meaning_privacy_usefulness_and_estimates_unverified']}
    try:
        boundary(data)
        obj(data, ('schema_version', 'task_id', 'action_state', 'human_response', 'human_calibrated',
                   'promotion_ready', 'limitations'), '')
        require(data['task_id'] == 'CP-04', 'case_identity', '/task_id')
        strings(data['limitations'], '/limitations')
        obj(source, ('schema_version',), '')
        obj(acceptedpins, ('schema_version',), '')
        require(source['schema_version'] == 'cp04_project_fit_explanation_packet_v1' and
                data['schema_version'] == 'cp04_solution_blueprint_explanation_packet_v1' and
                acceptedpins['schema_version'] == 'cp04_owner_format_acceptance_v1',
                'unsupported_version', '/schema_version')
        for value in (data, source, acceptedpins):
            require(len(canonical(value)) <= MAX_INPUT_BYTES, 'input_limit', '')
        require(sha(canonical(source)) == SOURCE_CANONICAL_SHA256 and
                sha(canonical(acceptedpins)) == ACCEPTANCE_CANONICAL_SHA256,
                'trusted_pin_mismatch', '')
        result['owner_format_accepted'] = acceptedpins['acceptance_status'] == 'owner_accepted_format'
        require(data.get('instruction_file') == INSTRUCTION_PATH and data.get('instruction_sha256') == INSTRUCTION_SHA256 and
                data.get('input_file') == SOURCE_PATH and data.get('input_sha256') == SOURCE_SHA256,
                'trusted_pin_mismatch', '/instruction_sha256')
        pins = data.get('source_file_sha256', {})
        require(pins.get(INSTRUCTION_PATH) == INSTRUCTION_SHA256 and pins.get(SOURCE_PATH) == SOURCE_SHA256,
                'trusted_pin_mismatch', '/source_file_sha256')
        records = data.get('records')
        require(isinstance(records, list) and len(records) == len(PROFILE), 'case_identity', '/records')
        ids = [item.get('case_id') if isinstance(item, dict) else None for item in records]
        require(all(isinstance(item, str) for item in ids) and set(ids) == set(PROFILE) and len(ids) == len(set(ids)),
                'case_identity', '/records')
        source_records = {item['case_id']: item for item in source['records']}
        for index, record in enumerate(records):
            try:
                result['case_observations'].append(record_contract(record, source_records[record['case_id']], '/records/' + str(index)))
                if any(key not in record['presentation_bindings'][locale] for key in ('architecture', 'complexity') for locale in ('ru', 'en')):
                    result['limitations'].append('architecture_complexity_locale_semantics_unverified')
            except ContractError as error:
                result['issues'].append({'category': error.category, 'pointer': error.pointer})
    except ContractError as error:
        result['issues'].append({'category': error.category, 'pointer': error.pointer})
    except (TypeError, ValueError, KeyError, AttributeError, RecursionError):
        result['issues'].append({'category': 'required_structure', 'pointer': ''})
    result['issues'] = result['issues'][:MAX_ISSUES]
    result['limitations'] = sorted(set(result['limitations']))
    result['case_count'] = len(result['case_observations'])
    if not result['issues']:
        result['verdict'] = 'contract_verified_only'
    return result


def read_input(path, label, json_input=True):
    try:
        with Path(path).open('rb') as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
        require(len(raw) <= MAX_INPUT_BYTES, 'input_limit', '/' + label)
        if not json_input:
            return raw, None

        def pairs(items):
            output = {}
            for key, value in items:
                require(key not in output, 'input_json', '/' + label)
                output[key] = value
            return output

        def constant(value):
            raise ContractError('input_json', '/' + label)

        return raw, json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    except ContractError:
        raise
    except (UnicodeError, ValueError, RecursionError):
        raise ContractError('input_json', '/' + label) from None
    except OSError:
        raise ContractError('input_io', '/' + label) from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in (('blueprints', LANE + 'solution-blueprint-explanations.json'),
                          ('source', SOURCE_PATH), ('acceptance', LANE + 'owner-format-acceptance.json'),
                          ('instruction', INSTRUCTION_PATH)):
        parser.add_argument('--' + name, default=str(ROOT / default))
    parser.add_argument('--output')
    args = parser.parse_args(argv)
    receipt = {'verdict': 'invalid_input', 'semantic_review_required': True,
               'promotion_ready': False, 'human_calibrated': False, 'estimate_calibrated': False,
               'installed_runtime_verified': False, 'issues': [], 'input_byte_hashes': {}}
    code = 2
    try:
        inputs = {}
        for label in ('blueprints', 'source', 'acceptance', 'instruction'):
            raw, value = read_input(getattr(args, label), label, label != 'instruction')
            receipt['input_byte_hashes'][label] = sha(raw)
            inputs[label] = value
        for label, expected in (('source', SOURCE_SHA256), ('acceptance', ACCEPTANCE_SHA256), ('instruction', INSTRUCTION_SHA256)):
            require(receipt['input_byte_hashes'][label] == expected, 'trusted_pin_mismatch', '/' + label)
        hashes = receipt['input_byte_hashes']
        receipt = evaluate(inputs['blueprints'], inputs['source'], inputs['acceptance'])
        receipt['input_byte_hashes'] = hashes
        code = 0 if receipt['verdict'] == 'contract_verified_only' else 1
    except ContractError as error:
        receipt['issues'] = [{'category': error.category, 'pointer': error.pointer}]
    receipt['evaluator_source_hashes'] = {path: sha((ROOT / path).read_bytes()) for path in
        ('evals/plugin-v1/evaluate_solution_blueprint.py', 'evals/plugin-v1/solution-blueprint-eval-contract.md',
         'tests/test_plugin_solution_blueprint_eval.py')}
    if args.output:
        try:
            with Path(args.output).open('x', encoding='utf-8', newline='\n') as stream:
                json.dump(receipt, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
                stream.write('\n')
        except OSError:
            receipt['verdict'] = 'invalid_input'
            receipt['issues'] = [{'category': 'input_io', 'pointer': '/output'}]
            code = 2
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return code


if __name__ == '__main__':
    sys.exit(main())
