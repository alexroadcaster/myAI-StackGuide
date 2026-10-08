"""Regressions against versioned captured examples, never ignored local fixtures."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / 'evals/plugin-v1/results/cp04-v2-2026-10-08'


class SolutionBlueprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('blueprint_eval',
            ROOT / 'evals/plugin-v1/evaluate_solution_blueprint.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.example = json.loads((LANE / 'solution-blueprint-explanations.json').read_text(encoding='utf-8'))
        cls.source = json.loads((LANE / 'project-fit-explanations.json').read_text(encoding='utf-8'))
        cls.acceptance = json.loads((LANE / 'owner-format-acceptance.json').read_text(encoding='utf-8'))

    def evaluate(self, data):
        return self.module.evaluate(data, self.source, self.acceptance)

    def invalid(self, data, category):
        result = self.evaluate(data)
        self.assertEqual(result['verdict'], 'invalid_contract')
        self.assertIn(category, {item['category'] for item in result['issues']})
        self.assertFalse(result['promotion_ready'])
        return result

    def rebind(self, record):
        for locale in ('ru', 'en'):
            for key in self.module.BINDING_KEYS:
                record['presentation_bindings'][locale][key] = copy.deepcopy(record[key])

    def test_accepted_d05_h15_contract_with_explicit_evidence_ceiling(self):
        result = self.evaluate(self.example)
        self.assertEqual(result['verdict'], 'contract_verified_only', result)
        self.assertEqual(result['case_count'], 2)
        self.assertIsNone(result['case_observations'][1]['full_scoped_adoption_engineer_hours'])
        self.assertTrue(result['owner_format_accepted'])
        self.assertTrue(result['semantic_review_required'])
        for key in ('promotion_ready', 'human_calibrated', 'estimate_calibrated', 'installed_runtime_verified'):
            self.assertFalse(result[key])
        self.assertIn('architecture_complexity_locale_semantics_unverified', result['limitations'])

    def test_duplicate_pilot_phase_is_rejected(self):
        data = copy.deepcopy(self.example)
        data['records'][0]['integration_phases'].append(copy.deepcopy(data['records'][0]['integration_phases'][1]))
        result = self.evaluate(data)
        self.assertEqual(result['verdict'], 'invalid_contract')
        self.assertIn('phase_identity', {item['category'] for item in result['issues']})

    def test_pilot_cannot_be_counted_twice_or_omitted_from_full_adoption(self):
        for mode in ('duplicate', 'omitted'):
            with self.subTest(mode=mode):
                data = copy.deepcopy(self.example)
                ids = data['records'][0]['time_estimate']['full_scoped_adoption']['included_phases']
                ids.append('one_endpoint_pilot') if mode == 'duplicate' else ids.remove('one_endpoint_pilot')
                self.invalid(data, 'phase_identity')

    def test_arithmetic_units_calendar_and_remaining_are_independent_gates(self):
        mutations = (('first_validation', 'effort_engineer_hours', [7, 12]),
                     ('full_scoped_adoption', 'effort_engineer_days_8h', [3, 4]),
                     ('first_validation', 'elapsed_working_days_excluding_waits', [2, 3]),
                     ('remaining_after_pilot', 'effort_engineer_hours', [16, 32]))
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                data = copy.deepcopy(self.example)
                data['records'][0]['time_estimate'][section][key] = value
                self.invalid(data, 'estimate_arithmetic')
        data = copy.deepcopy(self.example)
        data['records'][0]['time_estimate']['hours_per_engineer_day'] = 6
        self.invalid(data, 'estimate_arithmetic')
        data = copy.deepcopy(self.example)
        data['records'][0]['time_estimate']['first_validation']['measured_calendar_days'] = [1, 2]
        self.invalid(data, 'estimate_boundary')

    def test_nan_bool_zero_and_reversed_phase_ranges_are_rejected(self):
        for value in ([float('nan'), 4], [True, 4], [0, 4], [5, 4]):
            with self.subTest(value_type=type(value[0]).__name__):
                data = copy.deepcopy(self.example)
                data['records'][0]['integration_phases'][0]['effort_engineer_hours'] = value
                self.invalid(data, 'estimate_range')
        data = copy.deepcopy(self.example)
        data['records'][0]['integration_phases'][0]['effort_engineer_hours'] = [10 ** 400, 10 ** 401]
        self.invalid(data, 'estimate_range')

    def test_different_consistent_conditional_forecast_is_valid(self):
        data = copy.deepcopy(self.example)
        record = data['records'][0]
        record['decision'] = 'Inspect current routing before a conditional single-router pilot.'
        for phase in record['integration_phases']:
            phase['effort_engineer_hours'] = [bound * 2 for bound in phase['effort_engineer_hours']]
        for section in ('first_validation', 'full_scoped_adoption', 'remaining_after_pilot'):
            summary = record['time_estimate'][section]
            for key in ('effort_engineer_hours', 'effort_engineer_days_8h'):
                summary[key] = [bound * 2 for bound in summary[key]]
            if 'elapsed_working_days_excluding_waits' in summary:
                summary['elapsed_working_days_excluding_waits'] = [math.ceil(bound / 8) for bound in summary['effort_engineer_hours']]
        self.rebind(record)
        self.assertNotEqual(data, self.example)
        self.assertEqual(self.evaluate(data)['verdict'], 'contract_verified_only')

    def test_partial_h15_cannot_invent_full_adoption_or_actual_waits(self):
        for key, value in (('full_scoped_adoption', self.example['records'][0]['time_estimate']['full_scoped_adoption']),
                           ('actual_start_to_finish_working_days', [1, 2]), ('external_waiting_working_days', [1, 2])):
            with self.subTest(key=key):
                data = copy.deepcopy(self.example)
                data['records'][1]['time_estimate'][key] = copy.deepcopy(value)
                self.invalid(data, 'estimate_boundary')

    def test_missing_assumptions_and_sections_cannot_pass(self):
        for key, value in (('hypothetical_assumptions', []), ('technical', {}), ('reuse_custom_current_comparison', [])):
            with self.subTest(key=key):
                data = copy.deepcopy(self.example)
                data['records'][0][key] = value
                self.invalid(data, 'required_structure')

    def test_source_unknown_scope_cannot_become_confirmed(self):
        data = copy.deepcopy(self.example)
        data['records'][1]['confirmed_constraints'].append('One device and import format confirmed.')
        data['records'][1]['unknowns'] = {}
        self.invalid(data, 'context_binding')

    def test_wrong_repository_provenance_and_role_inflation_are_rejected(self):
        for mode in ('wrong_owner', 'role', 'adoption_fit', 'capability'):
            with self.subTest(mode=mode):
                data = copy.deepcopy(self.example)
                record = data['records'][0]
                if mode == 'wrong_owner':
                    record['canonical_roles'][0]['evidence_refs'] = copy.deepcopy(record['canonical_roles'][1]['evidence_refs'])
                elif mode == 'capability':
                    record['evidence_labels'][0]['capability_binding']['source_ref'] = 'data:not-owned'
                else:
                    record['canonical_roles'][0][mode] = 'primary_candidate' if mode == 'role' else 'verified'
                self.rebind(record)
                self.invalid(data, 'provenance_ownership')

    def test_both_locales_equal_but_stale_against_canonical_are_rejected(self):
        data = copy.deepcopy(self.example)
        for locale in ('ru', 'en'):
            data['records'][0]['presentation_bindings'][locale]['time_estimate']['scope'] = 'Stale assumption.'
        self.invalid(data, 'presentation_binding')
        data = copy.deepcopy(self.example)
        for locale in ('ru', 'en'):
            data['records'][0]['presentation_bindings'][locale]['time_estimate']['team_size'] = True
        self.invalid(data, 'presentation_binding')

    def test_locale_inequality_and_optional_architecture_binding_are_rejected(self):
        data = copy.deepcopy(self.example)
        data['records'][0]['presentation_bindings']['ru']['selected_ids'].reverse()
        self.invalid(data, 'presentation_binding')
        data = copy.deepcopy(self.example)
        record = data['records'][0]
        for locale in ('ru', 'en'):
            record['presentation_bindings'][locale]['architecture'] = {'status': 'stale'}
        self.invalid(data, 'presentation_binding')

    def test_same_role_alternatives_cannot_be_jointly_adopted(self):
        data = copy.deepcopy(self.example)
        data['records'][0]['stack'][-1]['state'] = 'proposed_new_conditional'
        self.invalid(data, 'alternative_joint_adoption')
        data = copy.deepcopy(self.example)
        data['records'][0]['stack'][-1]['state'] = 'installed'
        self.invalid(data, 'stack_state')

    def test_executed_promotion_benefit_and_privacy_flags_cannot_be_forged(self):
        for key in ('executed', 'promotion_ready', 'project_benefit_measured', 'delivery_commitment'):
            with self.subTest(key=key):
                data = copy.deepcopy(self.example)
                data['records'][0][key] = True
                result = self.invalid(data, 'execution_boundary')
                self.assertEqual(result['issues'][0]['pointer'], '/records/0/' + key)
        data = copy.deepcopy(self.example)
        data['private_payload'] = 'SYNTHETIC_PRIVATE_CANARY'
        result = self.invalid(data, 'privacy_boundary')
        self.assertNotIn('SYNTHETIC_PRIVATE_CANARY', json.dumps(result))

    def test_case_versions_and_explicit_authority_pins_fail_independently(self):
        data = copy.deepcopy(self.example)
        data['records'][1]['case_id'] = data['records'][0]['case_id']
        self.invalid(data, 'case_identity')
        data = copy.deepcopy(self.example)
        data['schema_version'] = 'legacy'
        self.invalid(data, 'unsupported_version')
        data = copy.deepcopy(self.example)
        data['instruction_sha256'] = '0' * 64
        self.invalid(data, 'trusted_pin_mismatch')
        data = copy.deepcopy(self.example)
        del data['action_state']
        self.invalid(data, 'required_structure')
        source = copy.deepcopy(self.source)
        source['records'][0]['persona'] = 'Forged source'
        result = self.module.evaluate(self.example, source, self.acceptance)
        self.assertEqual(result['issues'][0]['category'], 'trusted_pin_mismatch')

    def test_cli_bounds_and_sanitizes_invalid_inputs(self):
        with tempfile.TemporaryDirectory(prefix='blueprint-eval-', dir=ROOT / '.codex-tmp') as directory:
            candidate = Path(directory) / 'candidate.json'
            for raw, category in ((b'x' * (self.module.MAX_INPUT_BYTES + 1), 'input_limit'),
                                  (b'{"schema_version":NaN}', 'input_json'),
                                  (b'{"schema_version":1,"schema_version":2}', 'input_json')):
                candidate.write_bytes(raw)
                process = subprocess.run([sys.executable, '-B', str(ROOT / 'evals/plugin-v1/evaluate_solution_blueprint.py'),
                    '--blueprints', str(candidate)], cwd=ROOT, capture_output=True, text=True, timeout=30)
                self.assertEqual(process.returncode, 2, process.stdout)
                receipt = json.loads(process.stdout)
                self.assertEqual(receipt['issues'][0]['category'], category)
                self.assertFalse(receipt['promotion_ready'])

    def test_cli_reports_specific_contract_failure_without_example_hash_gate(self):
        with tempfile.TemporaryDirectory(prefix='blueprint-eval-', dir=ROOT / '.codex-tmp') as directory:
            candidate = Path(directory) / 'candidate.json'
            data = copy.deepcopy(self.example)
            data['records'][0]['integration_phases'].append(copy.deepcopy(data['records'][0]['integration_phases'][1]))
            candidate.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            process = subprocess.run([sys.executable, '-B', str(ROOT / 'evals/plugin-v1/evaluate_solution_blueprint.py'),
                '--blueprints', str(candidate), '--instruction', str(ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08/live-verification-instruction-baseline.md')], cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertEqual(process.returncode, 1)
            receipt = json.loads(process.stdout)
            self.assertEqual(receipt['issues'][0]['category'], 'phase_identity')
            self.assertEqual(set(receipt['input_byte_hashes']), {'blueprints', 'source', 'acceptance', 'instruction'})


if __name__ == '__main__':
    unittest.main()
