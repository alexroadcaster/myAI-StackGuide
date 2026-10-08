"""Enrichment identity, provenance and preservation of existing public facts."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('source_test', ROOT / 'evals/plugin-v1/run_source_coverage_comparison.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.cards = [{'identity': {'github_repository_id': 1, 'full_name': 'owner/repo'},
                       'descriptions': {'upstream': 'Original'}, 'advisory': {'use_cases': []}}]
        self.facts = [{'github_repository_id': 1, 'full_name': 'owner/repo',
                       'capability': 'Kotlin support', 'source_url': 'https://example.org/docs',
                       'observed_on': '2026-10-08', 'scope': 'core', 'limitations': 'Integration unverified'}]

    def test_adds_capability_without_mutating_original_or_upstream(self):
        baseline = copy.deepcopy(self.cards)
        value = runner.enriched_cards(self.cards, self.facts)
        self.assertEqual(self.cards, baseline)
        self.assertEqual(value[0]['descriptions'], baseline[0]['descriptions'])
        self.assertIn('Kotlin support', value[0]['advisory']['use_cases'])

    def test_missing_provenance_unknown_or_mismatched_identity_rejected(self):
        for change in [{'source_url': ''}, {'github_repository_id': 2}, {'full_name': 'other/repo'}, {'scope': ''}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                runner.enriched_cards(self.cards, [dict(self.facts[0], **change)])


if __name__ == '__main__':
    unittest.main()
