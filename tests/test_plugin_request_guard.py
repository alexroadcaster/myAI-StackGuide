"""Observable exclusions, unknown alternatives and clarification boundaries."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import guard_recommendation_request as guard

QUERY = {'max_candidates': 150}


class RequestGuard(unittest.TestCase):
    def test_filtered_transport_ranks_remain_valid_without_mutating_scores(self):
        rows = [dict(github_repository_id=i, rank=i, score=1/i) for i in (1, 2, 3)]
        filtered = guard.filtered_candidates(rows, [1, 3])
        self.assertEqual([r['rank'] for r in filtered], [1, 2])
        self.assertEqual(filtered[1]['score'], rows[2]['score'])
        self.assertEqual(rows[2]['rank'], 3)

    def test_explicit_product_exclusion_refills_without_reordering(self):
        request = guard.prepare(QUERY, {}, excluded_repository_ids=[2])
        result = guard.select(request, [1, 2, 3, 4], {}, limit=3)
        self.assertEqual(result['selected_ids'], [1, 3, 4])
        self.assertEqual(result['excluded'][0]['github_repository_id'], 2)

    def test_all_documented_modes_conflict_but_missing_facts_stay_unknown(self):
        request = guard.prepare(QUERY, {}, excluded_dependencies=['redis', 'valkey'])
        evidence = {2: {'alternatives': [['redis'], ['valkey']], 'source_urls': ['https://github.com/rq/rq']}}
        result = guard.select(request, [1, 2, 3], evidence, limit=3)
        self.assertEqual(result['selected_ids'], [1, 3])
        self.assertEqual(result['verification_required'], [1, 3])

    def test_available_alternative_is_conditional_and_not_full_compliance(self):
        request = guard.prepare(QUERY, {}, excluded_dependencies=['redis'])
        evidence = {2: {'alternatives': [['redis'], ['sqlite']], 'source_urls': ['https://github.com/coleifer/huey']}}
        result = guard.select(request, [2], evidence, limit=1)
        self.assertEqual(result['selected_ids'], [2])
        self.assertEqual(result['conditional_configuration_ids'], [2])
        self.assertEqual(result['verification_required'], [2])

    def test_clarification_stops_before_retrieval(self):
        request = guard.prepare(None, None, unresolved=[dict(dimension='corpus', question='Own data or web?', options=['own_data', 'web'])])
        called = []
        result = guard.execute(request, lambda: called.append(True), {}, limit=12)
        self.assertEqual(result['status'], 'needs_clarification')
        self.assertEqual(called, [])

    def test_no_exclusions_preserves_exact_order(self):
        request = guard.prepare(QUERY, {})
        self.assertEqual(guard.select(request, [3, 1, 2], {}, limit=3)['selected_ids'], [3, 1, 2])

    def test_unsourced_dependency_fact_cannot_establish_conflict(self):
        request = guard.prepare(QUERY, {}, excluded_dependencies=['redis'])
        with self.assertRaisesRegex(ValueError, 'unsourced'):
            guard.select(request, [2], {2: {'alternatives': [['redis']], 'source_urls': []}}, limit=1)


if __name__ == '__main__':
    unittest.main()
