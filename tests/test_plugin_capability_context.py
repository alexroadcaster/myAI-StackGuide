"""Required capabilities and project context have distinct enrichment effects."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import rank_capability_context as ranker


class CapabilityContextTests(unittest.TestCase):
    intent = {'required_groups': [['mobile'], ['testing']], 'context_terms': ['React']}
    terms = ['mobile', 'testing', 'React']

    def test_context_only_additions_preserve_baseline_order(self):
        fields = {1: {'description': ['mobile testing']}, 2: {'description': ['testing']}}
        result = ranker.rank_cards(fields, {2: ['React testing']}, self.terms, self.intent, limit=12)
        self.assertEqual([r['github_repository_id'] for r in result], [1, 2])
        self.assertEqual(result[1]['requirement_states'], ['unknown', 'original_lexical_support'])
        self.assertEqual(result[1]['new_context_bonus'], 0)

    def test_new_required_evidence_can_promote_candidate(self):
        fields = {1: {'description': ['mobile testing']}, 2: {'description': ['React']}}
        result = ranker.rank_cards(fields, {2: ['mobile testing']}, self.terms, self.intent, limit=12)
        self.assertEqual(result[0]['github_repository_id'], 2)
        self.assertEqual(result[0]['requirement_bonus'], 2)

    def test_no_enrichment_is_exact_baseline_and_ties_use_id(self):
        fields = {9: {'name': ['React'], 'description': ['mobile testing']},
                  3: {'name': ['React'], 'description': ['mobile testing']}}
        result = ranker.rank_cards(fields, {}, self.terms, self.intent, limit=12)
        self.assertEqual([r['github_repository_id'] for r in result], [3, 9])
        self.assertEqual([r['score'] for r in result], [3, 3])

    def test_missing_requirement_prevents_partial_promotion(self):
        result = ranker.rank_cards({1: {'description': ['React']}}, {1: ['mobile']},
                                  self.terms, self.intent, limit=12)
        self.assertEqual(result[0]['requirement_bonus'], 0)
        self.assertIn('unknown', result[0]['requirement_states'])

    def test_terms_cannot_be_added_repeated_or_dropped(self):
        for intent in ({'required_groups': [['mobile']], 'context_terms': ['React']},
                       {'required_groups': [['mobile', 'React']], 'context_terms': ['React', 'testing']},
                       {'required_groups': [['mobile', 'testing', 'extra']], 'context_terms': ['React']}):
            with self.assertRaises(ValueError):
                ranker.rank_cards({}, {}, self.terms, intent, limit=12)

    def test_synonyms_cannot_multiply_requirement_bonus(self):
        intent = {'required_groups': [['upload', 'uploads']], 'context_terms': ['React']}
        result = ranker.rank_cards({1: {'description': ['React']}}, {1: ['upload uploads']},
                                  ['upload', 'uploads', 'React'], intent, limit=12)
        self.assertEqual(result[0]['requirement_bonus'], 1)


if __name__ == '__main__':
    unittest.main()
