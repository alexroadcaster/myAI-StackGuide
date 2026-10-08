"""Runner acceptance tests; synthetic units do not measure product quality."""

import copy
import importlib.util
import io
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class QualityRunnerAvailability(unittest.TestCase):
    def test_offline_quality_runner_exists(self):
        self.assertTrue((ROOT / 'evals/plugin-v1/run_quality.py').is_file(),
                        'CP-04 expected RED: offline public-catalog runner is absent')


class QualityRunnerContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('quality_runner', ROOT / 'evals/plugin-v1/run_quality.py')
        cls.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runner)
        cls.plan = cls.runner.scorer.load_json(ROOT / 'evals/plugin-v1/quality-plan.json')

    def test_query_mapping_preserves_frozen_terms_and_pins_without_inferred_constraints(self):
        before = copy.deepcopy(self.plan)
        case = self.plan['cases'][-1]
        query = self.runner.make_query(self.plan, case)
        self.assertEqual(query['taxonomy_route_id'], case['target_category_id'])
        self.assertEqual(query['variants'], [{'variant_id': 'q1', 'terms': case['query_terms']}])
        self.assertEqual(query['policy_sha256'], self.plan['pins']['policy_sha256'])
        self.assertEqual(query['max_candidates'], self.plan['candidate_route']['max_candidates'])
        self.assertEqual(query['constraints']['mandatory_fields'], [])
        self.assertEqual(self.plan, before)
        manifest = self.runner.scorer.load_json(ROOT / self.plan['artifacts']['manifest_path'])
        policy = self.runner.scorer.load_json(ROOT / self.plan['artifacts']['policy_path'])
        self.runner.retrieval.validate_query(query, manifest=manifest, policy=policy)

    def test_unknown_anywhere_in_full_raw_rank_stays_null_not_zero(self):
        judgments = [{'github_repository_id': repo_id, 'grade': 3} for repo_id in range(1, 13)]
        observed = self.runner.strict_ranking(list(range(1, 14)), judgments, 12)
        self.assertFalse(observed['valid'])
        self.assertIsNone(observed['ranking'])
        self.assertEqual(observed['unjudged_ids'], [13])

    def test_complete_pool_uses_original_rank_and_unretrieved_denominator(self):
        judgments = [{'github_repository_id': 1, 'grade': 3},
                     {'github_repository_id': 2, 'grade': 2},
                     {'github_repository_id': 3, 'grade': 0}]
        report = self.runner.strict_ranking([3, 1], judgments, 12)
        self.assertTrue(report['valid'])
        self.assertEqual(report['ranking']['recall_at_k'], .5)
        self.assertLess(report['ranking']['ndcg_at_k'], 1)
        self.assertFalse(self.runner.strict_ranking([1, 1], judgments, 12)['valid'])

    def test_official_macro_does_not_drop_incomplete_cases(self):
        records = [{'candidate': {'ranking': {'ranking': {'recall_at_k': 1, 'ndcg_at_k': 1}}}},
                   {'candidate': {'ranking': {'ranking': None}}}]
        self.assertEqual(self.runner.complete_macro(records, 'candidate'),
                         {'recall_at_12': None, 'ndcg_at_12': None, 'complete': False})
        self.assertFalse(self.runner.complete_macro([], 'candidate')['complete'])
        zero_relevant = [{'candidate': {'ranking': {'ranking':
                            {'recall_at_k': None, 'ndcg_at_k': None}}}}]
        self.assertFalse(self.runner.complete_macro(zero_relevant, 'candidate')['complete'])

    def test_typed_failure_remains_null_while_valid_no_match_is_zero(self):
        case = {'k': 12, 'judgments': [{'github_repository_id': 1, 'grade': 3,
                                     'constraint': 'allowed'}]}
        pack = {'cards': [], 'exclusions': []}
        failed = self.runner.observe_method([], pack, case, 'retrieval_unavailable')
        self.assertIsNone(failed['ranking']['ranking'])
        self.assertEqual(failed['ranking']['reason'], 'typed_retrieval_failure')
        no_match = self.runner.observe_method([], pack, case, 'no_match')
        self.assertEqual(no_match['ranking']['ranking']['recall_at_k'], 0)

    def test_baseline_shares_route_and_includes_secondary_assignments(self):
        def card(repo_id, category, role):
            return {'identity': {'github_repository_id': repo_id, 'full_name': 'test/editor',
                                 'full_name_aliases': []},
                    'descriptions': {'upstream': None, 'catalog': None},
                    'repository': {'topics': []},
                    'classifications': [{'category_id': category, 'title': category, 'role': role}],
                    'advisory': {'use_cases': [], 'integration_surface': None, 'best_for': []}}
        case = {'target_category_id': 'wanted', 'query_terms': ['editor']}
        cards = [card(3, 'other', 'primary'), card(2, 'wanted', 'secondary'), card(1, 'wanted', 'primary')]
        self.assertEqual(self.runner.baseline_ids(self.plan, case, cards, {'wanted': {'wanted'}}), [1, 2])

    def test_constraints_and_budget_exclusions_are_separate_and_survival_uses_useful_top12(self):
        case = {'k': 12, 'judgments': [
            {'github_repository_id': 1, 'grade': 3, 'constraint': 'allowed'},
            {'github_repository_id': 2, 'grade': 2, 'constraint': 'allowed'},
            {'github_repository_id': 3, 'grade': 3, 'constraint': 'denied'}]}
        pack = {'cards': [{'card': {'identity': {'github_repository_id': 1}}}],
                'exclusions': [{'github_repository_id': 2, 'reason_codes': ['candidate_budget']},
                               {'github_repository_id': 3, 'reason_codes': ['archived']}]}
        report = self.runner.observe_method([1, 2, 3, 99], pack, case)
        self.assertEqual(report['pack_survival_rate'], .5)
        self.assertEqual(report['false_exclusions'], [])
        self.assertEqual(report['hard_constraint_violations'], [])
        self.assertEqual(report['ranking']['unjudged_ids'], [99])
        pack['exclusions'][0]['reason_codes'] = ['constraint_mismatch']
        self.assertEqual(self.runner.observe_method([1, 2, 3], pack, case)['false_exclusions'], [2])

    def test_execute_calls_owned_actual_runtime_and_times_its_call(self):
        case = self.plan['cases'][0]
        with patch.object(self.runner.retrieval, 'retrieve', return_value={'status': 'no_match'}) as mocked:
            query, result, elapsed = self.runner.execute(self.plan, case, 'synthetic-unit-id')
        self.assertEqual(result['status'], 'no_match')
        self.assertGreaterEqual(elapsed, 0)
        self.assertEqual(mocked.call_args.args, (query,))
        self.assertEqual(mocked.call_args.kwargs['index_path'], ROOT / self.plan['artifacts']['index_path'])

    def test_nearest_rank_percentiles_and_declaration_are_explicit(self):
        self.assertEqual(self.runner.percentile(list(range(1, 31)), .95), 29)
        self.assertIsNone(self.runner.percentile([], .95))
        declared = self.runner.declaration(self.plan)
        self.assertEqual(declared['latency']['repetitions'], 30)
        self.assertIsNone(declared['tokens'])
        self.assertIsNone(declared['provider_cost_usd'])
        self.assertIn('no_go', declared['unknown_judgments'])
        self.assertEqual(declared['pins'], self.plan['pins'])

    def test_valid_no_match_sample_is_measured_without_masking_quality_mismatch(self):
        query = self.runner.make_query(self.plan, self.plan['cases'][0])
        with patch.object(self.runner, 'execute', return_value=(query, {'status': 'no_match'}, 1.0)), \
                patch.object(self.runner, 'peak_working_set', return_value=1024), \
                patch('sys.stdout', new_callable=io.StringIO):
            code = self.runner.main(['--sample-case', '0', '--plan-sha256',
                                     self.runner.scorer.digest(self.plan)])
        self.assertEqual(code, 0, 'valid zero-hit runtime result is a measurable latency sample')

        case = self.plan['cases'][12]
        observed = self.runner.observe_method([], {'cards': [], 'exclusions': []}, case, 'no_match')
        record = {'case_id': case['case_id'], 'split': 'held_out', 'tags': case['tags'],
                  'container_domain_ids': case['container_domain_ids'],
                  'target_category_id': case['target_category_id'], 'retrieval_status': 'no_match',
                  'candidate': observed, 'baseline': observed, 'candidate_alias_success': None}
        performance = {'cold_p95_ms': 1, 'warm_p95_ms': 1, 'peak_memory_bytes': 1024, 'index_bytes': 1024}
        report = self.runner.summary(self.plan, [record], performance, [])
        self.assertFalse(report['gates']['candidate_status_matches'])
        self.assertEqual(report['verdict'], 'no_go')

    def test_measurement_amendment_separates_capture_and_measurement_sources(self):
        amendment = self.runner.measurement_amendment(self.plan)
        original = self.runner.scorer.load_json(self.runner.OUTPUT / 'declaration.json')
        self.assertEqual(amendment['capture_producing_source_hashes'], original['source_hashes'])
        self.assertNotEqual(amendment['capture_producing_source_hashes']['evals/plugin-v1/run_quality.py'],
                            amendment['measurement_source_hashes']['evals/plugin-v1/run_quality.py'])
        forged = self.runner.source_hashes()
        forged['plugins/myai-stackguide/scripts/retrieval.py'] = '0' * 64
        with patch.object(self.runner, 'source_hashes', return_value=forged), \
                self.assertRaisesRegex(ValueError, 'capture-producing runtime changed'):
            self.runner.measurement_amendment(self.plan)

    def test_resume_rejects_modified_observations_before_measurement_or_write(self):
        amendment = self.runner.measurement_amendment(self.plan)
        with patch.object(Path, 'exists', return_value=False), \
                patch.object(self.runner.scorer, 'file_sha256', return_value='0' * 64), \
                patch.object(self.runner, 'measure_performance') as measure, \
                patch.object(self.runner, 'write_json') as write, \
                self.assertRaisesRegex(ValueError, 'frozen observations changed'):
            self.runner.resume_measurement(self.plan, amendment)
        measure.assert_not_called()
        write.assert_not_called()


if __name__ == '__main__':
    unittest.main()
