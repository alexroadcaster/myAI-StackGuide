"""Fresh scoring/projection boundaries tested with synthetic data only."""
import importlib.util
import math
from pathlib import Path
import unittest
import tempfile

ROOT = Path(__file__).resolve().parents[1]


class QualityRunnerV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('test_fresh_v3_runner', ROOT/'evals/plugin-v1/run_quality_v3.py')
        cls.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runner)

    def rows(self):
        return [{'github_repository_id':1,'grade':3,'constraint':'denied'},
                {'github_repository_id':2,'grade':3,'constraint':'allowed'},
                {'github_repository_id':3,'grade':None,'constraint':'allowed'}]

    def test_unknown_returned_and_unjudged_are_null_not_zero(self):
        for ids in ([2,3],[2,99]):
            self.assertIsNone(self.runner.supported_ranking(ids,self.rows(),12)['ranking'])

    def test_denied_raw_rank_and_unreturned_unknown_diagnostic(self):
        row = self.runner.supported_ranking([1,2],self.rows(),12)
        self.assertEqual(row['unknown_universe_count'],1)
        self.assertEqual(row['ranking']['recall_at_k'],1)
        self.assertAlmostEqual(row['ranking']['ndcg_at_k'],1/math.log2(3))

    def test_macro_cannot_omit_one_unknown_case(self):
        records=[{'control':{'ranking':self.runner.supported_ranking([2],self.rows(),12)}},
                 {'control':{'ranking':self.runner.supported_ranking([3],self.rows(),12)}}]
        self.assertIsNone(self.runner.complete_macro(records,'control')['recall_at_12'])
        self.assertFalse(self.runner.complete_macro([], 'control')['complete'])

    def test_no_supported_positives_is_unavailable(self):
        rows=[{'github_repository_id':1,'grade':0,'constraint':'allowed'}]
        self.assertIsNone(self.runner.supported_ranking([1],rows,12)['ranking'])

    def test_freeze_gate_rejects_changed_oracle_or_unreviewed_source(self):
        bindings={'oracle_sha256':'a'*64,'runtime_sha256':'b'*64}
        gate={**bindings,'accepted':True,'reviewer':'independent-source-reviewer','independent_review_completed':True}
        self.runner.validate_freeze_gate(gate,bindings)
        with self.assertRaises(ValueError):self.runner.validate_freeze_gate({**gate,'oracle_sha256':'c'*64},bindings)
        with self.assertRaises(ValueError):self.runner.validate_freeze_gate({**gate,'independent_review_completed':False},bindings)

    def test_projection_preserves_actual_rank_and_rrf_and_marks_noncanonical(self):
        pack={'cards':[{'card':{'identity':{'github_repository_id':2}},'retrieval_rank':1,'rrf_score':.99,'matched_fields':['topics']}]}
        raw={'candidates':[{'github_repository_id':2,'rank':9,'rrf_score':.014,'matched_fields':['catalog_description']}]}
        envelope=self.runner.restore_rank_fidelity(pack,raw)
        row=envelope['projection']['cards'][0]
        self.assertEqual((row['selection_rank'],row['retrieval_rank'],row['rrf_score']),(1,9,.014))
        self.assertTrue(envelope['experimental_notcanonical'])
        self.assertFalse(envelope['current_policy_fulfilled'])
        self.assertEqual(pack['cards'][0]['rrf_score'],.99)

    def test_exclusive_outputs_and_diagnostic_macro_exclusion(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            self.runner.coverage.base.write_json('safe.json',{},output=Path(directory))
            with self.assertRaises(FileExistsError):self.runner.coverage.base.write_json('safe.json',{},output=Path(directory))
            with self.assertRaises(ValueError):self.runner.coverage.base.write_json('../escape.json',{},output=Path(directory))
        rows=self.rows();valid=self.runner.supported_ranking([2],rows,12)
        records=[{'include_in_14_domain_macro':True,'control':{'ranking':valid}},
                 {'include_in_14_domain_macro':False,'control':{'ranking':self.runner.supported_ranking([3],rows,12)}}]
        macro=self.runner.complete_macro([r for r in records if r['include_in_14_domain_macro']],'control')
        self.assertTrue(macro['complete'])


if __name__=='__main__':unittest.main()
