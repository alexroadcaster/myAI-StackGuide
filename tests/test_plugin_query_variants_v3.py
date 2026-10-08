"""Development-ablation integrity tests; synthetic assertions are not quality evidence."""
import copy
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class QueryVariantsV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('query_variants_v3_test', ROOT / 'evals/plugin-v1/run_query_variants_v3.py')
        cls.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runner)

    def test_only_exact_ten_development_cases(self):
        plan, cases, *_ = self.runner.load_inputs()
        self.assertEqual([c['case_id'] for c in cases], self.runner.EXPECTED_CASES)
        self.assertTrue(all(c['split'] == 'development' and c['metric_family'] == 'semantic' for c in cases))
        with self.assertRaises(ValueError):
            self.runner.validate_partitions([])
        self.assertEqual(plan['thresholds'], self.runner.old.scorer.load_json(self.runner.old.PLAN_PATH)['thresholds'])

    def test_disjoint_nonempty_exact_term_partition(self):
        with self.assertRaises(ValueError):
            self.runner.validate_partition(['a'], [[], ['a']])
        with self.assertRaises(ValueError):
            self.runner.validate_partition(['a'], [['a'], ['a']])
        _, cases, *_ = self.runner.load_inputs()
        for case in cases:
            self.runner.validate_partitions([case], require_complete=False)
        case = copy.deepcopy(cases[0])
        case['query_terms'].append('injected')
        with self.assertRaisesRegex(ValueError, 'exact term partition'):
            self.runner.validate_partitions([case], require_complete=False)

    def test_candidate_changes_variants_only_and_baseline_union_is_unchanged(self):
        plan, cases, *_ = self.runner.load_inputs()
        for case in cases:
            control, candidate = self.runner.queries(plan, case)
            expected = self.runner.old.make_query(plan, case)
            self.assertEqual(control, expected)
            self.assertEqual({k: v for k, v in candidate.items() if k != 'variants'}, {k: v for k, v in control.items() if k != 'variants'})
            self.assertEqual(set(t for v in candidate['variants'] for t in v['terms']), set(control['variants'][0]['terms']))
            self.assertEqual(control['max_candidates'], plan['candidate_route']['max_candidates'])
            policy = self.runner.old.scorer.load_json(ROOT / plan['artifacts']['policy_path'])
            manifest = self.runner.old.scorer.load_json(ROOT / plan['artifacts']['manifest_path'])
            self.runner.old.retrieval.validate_query(candidate, manifest=manifest, policy=policy)

    def test_denied_raw_rank_retention_and_unjudged_null(self):
        rows = [{'github_repository_id': 1, 'grade': 3, 'constraint': 'denied'}, {'github_repository_id': 2, 'grade': 3, 'constraint': 'allowed'}]
        observed = self.runner.v2.constrained_ranking([1, 2], rows, 12)
        self.assertAlmostEqual(observed['ranking']['ndcg_at_k'], 1 / math.log2(3))
        self.assertIsNone(self.runner.v2.constrained_ranking([1, 3], rows, 12)['ranking'])

    def test_exclusive_output_and_escape_rejection(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            target = Path(directory)
            self.runner.write_json('capture.json', {'safe': True}, output=target)
            with self.assertRaises(FileExistsError):
                self.runner.write_json('capture.json', {}, output=target)
            with self.assertRaises(ValueError):
                self.runner.write_json('../escape.json', {}, output=target)

    def test_source_change_invalidates_declaration(self):
        declared = {'safe': 1}
        self.runner.validate_declaration(declared, declared)
        with self.assertRaisesRegex(ValueError, 'declaration drift'):
            self.runner.validate_declaration(declared, {'safe': 2})

    def test_historical_equivalence_checks_fields_scores_and_pack_ids(self):
        retrieval = {'status': 'ok', 'candidates': [{'github_repository_id': 1, 'rank': 1, 'rrf_score': .1, 'variant_ranks': [], 'matched_fields': ['topics'], 'missing_facts': []}], 'executed_variants': 1, 'retrieved_hits': 1, 'truncated': False}
        pack = {'cards': [{'card': {'identity': {'github_repository_id': 1}}}], 'exclusions': []}
        current = self.runner.equivalence_projection(retrieval, pack)
        changed = copy.deepcopy(retrieval)
        changed['candidates'][0]['matched_fields'] = ['full_name']
        self.assertNotEqual(current, self.runner.equivalence_projection(changed, pack))


if __name__ == '__main__':
    unittest.main()
