"""New challenge targets must be source joined and reachable through their route."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('new_domains',ROOT/'evals/plugin-v1/run_new_domain_scenarios.py')
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class NewDomainContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,_,_,cls.cards,cls.members=runner.base.load_inputs()
        cls.cases=json.loads(runner.INPUT.read_bytes())['cases']
        cls.facts=json.loads(runner.SOURCE.read_bytes())['facts']

    def test_positive_must_belong_to_declared_route(self):
        cases=copy.deepcopy(self.cases)
        cases[0]['target_category_id']='baas_platforms'
        with self.assertRaisesRegex(ValueError,'target outside route'):
            runner.validate_cases(cases,self.cards,self.members,self.facts)

    def test_source_identity_and_intents_valid(self):
        runner.validate_cases(self.cases,self.cards,self.members,self.facts)

    def test_unknown_results_keep_actual_rank(self):
        result=runner.coverage([9,8,7],{'cards':[]},7)
        self.assertEqual(result['target_rank'],3)
        self.assertEqual(result['top12_unjudged_ids'],[9,8])
        self.assertIsNone(result['relevance_metrics'])


if __name__=='__main__':
    unittest.main()
