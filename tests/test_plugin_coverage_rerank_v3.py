"""Pool-limited coverage adapter boundaries, not held-out quality acceptance."""
import copy
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CoverageRerankV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('coverage_v3_tests', ROOT / 'evals/plugin-v1/run_coverage_rerank_v3.py')
        cls.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runner)

    def card(self, repo_id=1):
        return {'identity': {'github_repository_id': repo_id, 'full_name': 'owner/tool', 'full_name_aliases': []},
                'descriptions': {'upstream': 'React React uploader', 'catalog': 'React uploader'},
                'repository': {'topics': ['React', 'react', 'upload']}, 'classifications': [{'title':'Widgets'}],
                'advisory': {'use_cases': [], 'integration_surface': None, 'best_for': []}}

    def test_coverage_counts_distinct_term_field_pairs_not_occurrences(self):
        self.assertEqual(self.runner.coverage_score(self.card(), ['React','upload']), 6)
        self.assertEqual(self.runner.coverage_score(self.card(), ['Ｒｅａｃｔ']), 3)

    def test_pool_subset_cap_numeric_tie_and_no_append(self):
        cards = {i:self.card(i) for i in (1,2,3)}
        result = {'status':'ok','candidates':[{'github_repository_id':2},{'github_repository_id':1}]}
        original = copy.deepcopy(result)
        order, scores = self.runner.rerank_pool(result, cards, ['React'], 150)
        self.assertEqual(order,[1,2])
        self.assertNotIn(3,order)
        self.assertEqual(result,original)
        with self.assertRaises(ValueError):self.runner.rerank_pool(result,cards,['React'],1)
        with self.assertRaises(ValueError):self.runner.rerank_pool(result,cards,['React'],151)
        with self.assertRaises(ValueError):self.runner.rerank_pool({'status':'ok','candidates':[{'github_repository_id':1},{'github_repository_id':1}]},cards,['React'],150)

    def test_unjudged_null_and_denied_rank_kept(self):
        rows=[{'github_repository_id':1,'grade':3,'constraint':'denied'},{'github_repository_id':2,'grade':3,'constraint':'allowed'}]
        ranking=self.runner.base.v2.constrained_ranking([1,2],rows,12)
        self.assertAlmostEqual(ranking['ranking']['ndcg_at_k'],1/math.log2(3))
        self.assertIsNone(self.runner.base.v2.constrained_ranking([1,3],rows,12)['ranking'])

    def test_actual_fields_math_matches_unchanged_literal_baseline(self):
        plan,cases,cards,by_id,members=self.runner.base.load_inputs()
        for case in cases:
            pool=[c['identity']['github_repository_id'] for c in cards if any(x['category_id'] in members[case['target_category_id']] for x in c['classifications'])]
            ordered=sorted(pool,key=lambda i:(-self.runner.coverage_score(by_id[i],case['query_terms']),i))
            positive=[i for i in ordered if self.runner.coverage_score(by_id[i],case['query_terms'])>0]
            self.assertEqual(positive[:plan['lexical_baseline']['candidate_limit']],self.runner.base.old.baseline_ids(plan,case,cards,members))

    def test_adapter_transport_cannot_claim_c9_execution(self):
        envelope=self.runner.selection_envelope([2,1],{2:3,1:2})
        self.assertEqual(envelope['transport'],'experimental_selection_adapter')
        self.assertFalse(envelope['executed_c9_rrf'])
        self.assertNotIn('rrf_score',envelope)
        self.assertNotIn('bm25',envelope)

    def test_only_development_and_exclusive_output(self):
        _,cases,*_=self.runner.base.load_inputs()
        self.assertEqual([c['case_id'] for c in cases],self.runner.base.EXPECTED_CASES)
        self.assertTrue(all(c['metric_family']=='semantic' for c in cases))
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output=Path(directory)
            self.runner.base.write_json('receipt.json',{},output=output)
            with self.assertRaises(FileExistsError):self.runner.base.write_json('receipt.json',{},output=output)


if __name__=='__main__':unittest.main()
