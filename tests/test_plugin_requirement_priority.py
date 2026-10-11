"""Priority must change positions without rewarding context or partial evidence."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import rank_requirement_priority as ranker


class RequirementPriorityTests(unittest.TestCase):
    terms = ['Kotlin', 'server', 'async']
    intent = {'required_groups': [['Kotlin']], 'context_terms': ['server', 'async']}

    def test_novel_required_evidence_reaches_top_before_limit(self):
        fields = {1: {'name': ['server async'], 'description': ['server async']},
                  2: {'description': ['server']}, 3: {'description': []}}
        rows = ranker.rank_cards(fields, {3: ['Kotlin']}, self.terms, self.intent,
                                 limit=1, mode='new_required_first')
        self.assertEqual([r['github_repository_id'] for r in rows], [3])

    def test_all_supported_requirements_outrank_context_density(self):
        fields = {1: {'name': ['server async'], 'description': ['server async']},
                  2: {'description': ['Kotlin']}}
        rows = ranker.rank_cards(fields, {}, self.terms, self.intent, limit=12, mode='all_required_first')
        self.assertEqual([r['github_repository_id'] for r in rows], [2, 1])

    def test_context_only_addition_does_not_change_conservative_order(self):
        fields = {1: {'description': ['Kotlin server']}, 2: {'description': ['server']}}
        rows = ranker.rank_cards(fields, {2: ['async']}, self.terms, self.intent,
                                 limit=12, mode='new_required_first')
        self.assertEqual([r['github_repository_id'] for r in rows], [1, 2])

    def test_partial_requirement_cannot_gain_priority(self):
        intent = {'required_groups': [['Kotlin'], ['server']], 'context_terms': ['async']}
        rows = ranker.rank_cards({1: {'description': ['async']}, 2: {'description': ['async']}},
                                 {2: ['Kotlin']}, self.terms, intent, limit=12, mode='new_required_first')
        self.assertEqual([r['github_repository_id'] for r in rows], [1, 2])

    def test_prior_order_retained_when_no_new_requirement(self):
        fields = {3: {'description': ['Kotlin']}, 1: {'description': ['Kotlin']}}
        rows = ranker.rank_cards(fields, {}, self.terms, self.intent, limit=12, mode='new_required_first')
        self.assertEqual([r['github_repository_id'] for r in rows], [1, 3])

    def test_invalid_mode_and_limit_rejected(self):
        with self.assertRaises(ValueError):
            ranker.rank_cards({}, {}, self.terms, self.intent, limit=12, mode='untrusted')
        with self.assertRaises(ValueError):
            ranker.rank_cards({}, {}, self.terms, self.intent, limit=True, mode='new_required_first')


if __name__ == '__main__':
    unittest.main()
