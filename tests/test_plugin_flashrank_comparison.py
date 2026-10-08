"""Selection invariants and public projection; quality is measured by the runner."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('comparison_test', ROOT / 'evals/plugin-v1/run_flashrank_comparison.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ComparisonTests(unittest.TestCase):
    def test_equal_rrf_and_canonical_id_tie_break(self):
        self.assertEqual(runner.fuse_orders([3, 2, 1], [1, 2, 3], 60), [1, 3, 2])

    def test_fusion_rejects_incomplete_duplicate_or_invalid_pools(self):
        for first, second in [([1, 2], [1]), ([1, 1], [1, 1]), ([True], [True])]:
            with self.subTest(first=first), self.assertRaises(ValueError):
                runner.fuse_orders(first, second, 60)

    def test_query_uses_only_frozen_terms_not_goal_or_judgments(self):
        self.assertEqual(runner.compact_query({'query_terms': ['React Native', 'testing'],
                                              'user_goal': 'unrelated private text',
                                              'judgments': [{'secret': 'irrelevant'}]}),
                         'React Native; testing')

    def test_labeled_projection_uses_only_existing_public_fields(self):
        card = {'identity': {'full_name': 'owner/repo', 'full_name_aliases': []},
                'descriptions': {'upstream': 'PUBLIC', 'catalog': None},
                'repository': {'topics': ['search']}, 'classifications': [{'title': 'Tools'}],
                'advisory': {'use_cases': [], 'integration_surface': None, 'best_for': []},
                'private': 'DO NOT SERIALIZE'}
        text = runner.structured_text(card)
        self.assertIn('Repository: owner/repo', text)
        self.assertIn('Upstream description: PUBLIC', text)
        self.assertNotIn('None', text)
        self.assertNotIn('DO NOT SERIALIZE', text)


if __name__ == '__main__':
    unittest.main()
