"""Fail-closed acceptance invariants for the prospective final CP04 runner."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('final_quality', ROOT/'evals/plugin-v1/run_final_quality.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class FinalQuality(unittest.TestCase):
    def test_unknown_grade_invalidates_ranking_even_if_not_returned(self):
        result = runner.rank([1], [{'github_repository_id': 1, 'grade': 3},
                                 {'github_repository_id': 2, 'grade': None}], 12)
        self.assertIsNone(result['ranking'])

    def test_failed_stratum_cannot_be_masked_by_macro(self):
        self.assertFalse(runner.strata_pass([{'recall_at_k': .99, 'ndcg_at_k': .99},
                                            {'recall_at_k': .59, 'ndcg_at_k': .99}], .6, .5))

    def test_missing_stratum_stays_unknown(self):
        self.assertIsNone(runner.strata_pass([None], .6, .5))

    def test_baseline_must_share_exact_query(self):
        with self.assertRaisesRegex(ValueError, 'baseline binding'):
            runner.check_baseline_binding({'variants': [1]}, {'variants': [2]})

    def test_existing_capture_prevents_retroactive_freeze(self):
        with patch.object(Path, 'exists', return_value=True):
            root = Path('synthetic-output')
            with self.assertRaisesRegex(ValueError, 'retroactive'):
                runner.check_freeze(root)


if __name__ == '__main__':
    unittest.main()
