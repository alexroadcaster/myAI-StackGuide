"""Synthetic tests of successor protocol boundaries; not retrieval quality evidence."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class QualityRunnerV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'evals/plugin-v1/run_quality_v2.py'
        spec = importlib.util.spec_from_file_location('quality_v2_tests', path)
        cls.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runner)

    def setUp(self):
        self.case = {'case_id': 'DEV-X', 'split': 'development', 'target_category_id': 'leaf',
                     'universe_ids': [1, 2], 'metric_family': 'semantic', 'goal_kind': 'functional_alternative',
                     'query_terms': ['testing'], 'query_locale': 'en', 'k': 12,
                     'tags': [], 'container_domain_ids': [], 'expected_alias': None}
        self.rows = [{'github_repository_id': item, 'grade': grade, 'constraint': 'allowed',
                      'rationale': 'Synthetic source assessment.',
                      'evidence': [{'pointer': '/descriptions/upstream', 'value': 'test', 'source_ref': 'snapshot'}]}
                     for item, grade in [(1, 3), (2, 0)]]
        self.oracle_case = {'case_id': 'DEV-X', 'universe_ids': [1, 2], 'judgments': self.rows}

    def test_complete_universe_is_required_even_if_all_returned_ids_judged(self):
        incomplete = copy.deepcopy(self.oracle_case)
        incomplete['judgments'].pop()
        with self.assertRaisesRegex(ValueError, 'judgment universe'):
            self.runner.validate_case_universe(self.case, incomplete, {1, 2})

    def test_universe_cannot_omit_secondary_route_members(self):
        with self.assertRaisesRegex(ValueError, 'routed universe'):
            self.runner.validate_case_universe(self.case, self.oracle_case, {1, 2, 3})

    def test_duplicate_and_boolean_grades_are_invalid(self):
        for rows in [self.rows + [self.rows[0]], [{**self.rows[0], 'grade': True}, self.rows[1]]]:
            with self.assertRaises(ValueError):
                self.runner.validate_case_universe(self.case, {**self.oracle_case, 'judgments': rows}, {1, 2})

    def test_source_rationale_and_evidence_cannot_be_missing(self):
        rows = copy.deepcopy(self.rows)
        rows[0]['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'source evidence'):
            self.runner.validate_case_universe(self.case, {**self.oracle_case, 'judgments': rows}, {1, 2})

    def test_unjudged_returned_identity_remains_null(self):
        observed = self.runner.old.observe_method([1, 9], {'cards': [], 'exclusions': []},
                                                 {**self.case, 'judgments': self.rows})
        self.assertIsNone(observed['ranking']['ranking'])
        self.assertEqual(observed['ranking']['unjudged_ids'], [9])

    def test_zero_hit_and_typed_error_have_distinct_metrics(self):
        case = {**self.case, 'judgments': self.rows}
        pack = {'cards': [], 'exclusions': []}
        no_hit = self.runner.old.observe_method([], pack, case, 'no_match')
        failed = self.runner.old.observe_method([], pack, case, 'unavailable')
        self.assertEqual(no_hit['ranking']['ranking']['recall_at_k'], 0)
        self.assertIsNone(failed['ranking']['ranking'])

    def test_exact_identity_probe_does_not_enter_semantic_macro(self):
        records = [{'case_id': 'semantic', 'metric_family': 'semantic'},
                   {'case_id': 'probe', 'metric_family': 'identity'}]
        self.assertEqual(self.runner.semantic_records(records), records[:1])

    def test_denied_identity_lookup_and_adoption_are_separate(self):
        case = {**self.case, 'expected_identity_ids': [1], 'judgments': [{**self.rows[0], 'constraint': 'denied'}, self.rows[1]]}
        report = self.runner.identity_observation([1], {'cards': [], 'exclusions': []}, case)
        self.assertEqual(report['raw_exact_identity_success'], 1)
        self.assertEqual(report['denied_identity_in_pack'], [])
        self.assertEqual(report['allowed_exact_identity_pack_success'], None)

    def test_denied_hits_keep_rank_positions_with_zero_constrained_gain(self):
        rows = [{**self.rows[0], 'constraint': 'denied'}, {**self.rows[1], 'grade': 3}]
        report = self.runner.constrained_ranking([1, 2], rows, 12)['ranking']
        self.assertEqual(report['recall_at_k'], 1)
        self.assertAlmostEqual(report['ndcg_at_k'], 1 / __import__('math').log2(3))
        self.assertLess(report['ndcg_at_k'], 1, 'Denied rank1 must not compact allowed rank2 into rank1.')

    def test_frozen_thresholds_cannot_be_weakened(self):
        old = self.runner.scorer.load_json(self.runner.old.PLAN_PATH)
        candidate = copy.deepcopy(old)
        candidate['thresholds']['held_out_macro_recall_at_12_min'] = .5
        with self.assertRaisesRegex(ValueError, 'frozen thresholds'):
            self.runner.validate_frozen_settings(candidate, old)

    def test_provenance_tuple_cannot_drift(self):
        old = self.runner.scorer.load_json(self.runner.old.PLAN_PATH)
        candidate = copy.deepcopy(old)
        candidate['pins']['cards_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'frozen pins'):
            self.runner.validate_frozen_settings(candidate, old)

    def test_output_is_exclusive_and_contained(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            with patch.object(self.runner, 'OUTPUT', Path(directory)):
                self.runner.write_json('capture.json', {'safe': True})
                with self.assertRaises(FileExistsError):
                    self.runner.write_json('capture.json', {'safe': False})
                with self.assertRaisesRegex(ValueError, 'output name'):
                    self.runner.write_json('../escape.json', {})

    def test_heldout_gate_binds_declaration_and_development_bytes(self):
        declared = {'schema_version': 'synthetic-declaration'}
        gate = {'accepted': True, 'reviewer': 'synthetic-owner',
                'declaration_sha256': self.runner.scorer.digest(declared),
                'development_observations_sha256': 'a' * 64,
                'oracle_review_sha256': 'b' * 64}
        self.runner.validate_heldout_gate(gate, declared, 'a' * 64)
        with self.assertRaisesRegex(ValueError, 'development capture'):
            self.runner.validate_heldout_gate(gate, declared, 'c' * 64)
        with self.assertRaisesRegex(ValueError, 'review acceptance'):
            self.runner.validate_heldout_gate({**gate, 'accepted': False}, declared, 'a' * 64)

    def test_macro_cannot_skip_unmeasured_cases(self):
        good = {'ranking': {'ranking': {'recall_at_k': 1, 'ndcg_at_k': 1}}}
        bad = {'ranking': {'ranking': None}}
        report = self.runner.old.complete_macro([{'candidate': good}, {'candidate': bad}], 'candidate')
        self.assertFalse(report['complete'])
        self.assertIsNone(report['recall_at_12'])

    def test_alias_failure_cannot_be_diluted_by_non_alias_identity_success(self):
        plan = self.runner.scorer.load_json(self.runner.old.PLAN_PATH)
        records = [{'metric_family': 'identity', 'expected_alias': 'old/name', 'tags': ['historical_alias'],
                    'candidate_identity': {'raw_exact_identity_success': 0, 'denied_identity_in_pack': []}},
                   {'metric_family': 'identity', 'expected_alias': 'current/name', 'tags': [],
                    'candidate_identity': {'raw_exact_identity_success': 1, 'denied_identity_in_pack': []}}]
        for index, record in enumerate(records):
            record.update({'case_id': str(index), 'baseline_identity': {}, 'retrieval_status': 'ok'})
        plan['cases'] = [{'case_id': str(index)} for index in range(2)]
        base = {'gates': {}, 'failed_gates': [], 'unmeasured_gates': []}
        with patch.object(self.runner.old, 'summary', return_value=base):
            report = self.runner.summarize(plan, records, [])
        self.assertEqual(report['alias_success_rate'], 0)
        self.assertEqual(report['exact_identity_success_rate'], .5)
        self.assertIn('alias_success_rate_min', report['failed_gates'])

    def test_synthetic_card_schema_identity_and_provenance_are_distinct(self):
        original = self.runner.scorer._load_json_bounded(ROOT / 'plugins/myai-stackguide/assets/catalog.snapshot.json', 16 * 1024 * 1024)['cards'][0]
        pins = {'source_sha256': 'a' * 64, 'catalog_snapshot_id': 'synthetic-test'}
        replica = self.runner.synthetic_card(original, 0, pins)
        contracts = self.runner.scorer.Contracts()
        contracts.validate('catalog/repository-card.schema.json', replica)
        self.assertNotEqual(replica['identity']['github_repository_id'], original['identity']['github_repository_id'])
        self.assertEqual(replica['corpus_kind'], 'synthetic_fixture')
        self.assertTrue(all(row['source_kind'] == 'synthetic_fixture' for row in replica['evidence']))
        self.assertEqual(original['corpus_kind'], 'catalog_snapshot')

    def test_join_refuses_cross_capture_pack_identity_before_writer(self):
        spec = importlib.util.spec_from_file_location('cp04_join_test', ROOT / 'evals/plugin-v1/capture_quality_join_v2.py')
        join = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(join)
        capture = {'query': {'query_id': 'query-A'}, 'retrieval': {'pins': {'index_sha256': 'a' * 64}},
                   'candidate_evidence_pack': {'pins': {'index_sha256': 'b' * 64}}}
        with self.assertRaisesRegex(ValueError, 'capture pins'):
            join.validate_capture(capture, {'index_sha256': 'a' * 64})


if __name__ == '__main__':
    unittest.main()
