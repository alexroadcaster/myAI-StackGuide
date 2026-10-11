"""Unknown fit and explicit exclusions must remain distinct."""
import importlib.util
import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('domain_review', ROOT/'evals/plugin-v1/run_domain_review.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class DomainReviewContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan, _, _, cls.cards, cls.members = runner.base.load_inputs()
        cls.cases = json.loads(runner.previous.INPUT.read_bytes())['cases']
        cls.oracle = json.loads(runner.ORACLE.read_bytes())
        cls.challenges = json.loads(runner.CHALLENGES.read_bytes())['cases']

    def test_unjudged_candidate_is_not_a_mismatch(self):
        value = runner.assess([11, 22, 33, 44], {'11': 3, '33': 0, '44': None})
        self.assertEqual(value['unknown'], 2)
        self.assertEqual(value['mismatch'], 1)
        self.assertEqual(value['returned'], 4)
        self.assertIsNone(value['official_relevance_metrics'])

    def test_negative_conflicts_keep_original_positions(self):
        forbidden = [dict(github_repository_id=22, full_name='example/queue', source_urls=['https://github.com/example/queue'], basis='explicit exclusion')]
        self.assertEqual(runner.conflicts([11, 33, 22], forbidden)[0]['rank'], 3)
        self.assertEqual(runner.conflicts([11, 33], forbidden), [])

    def test_source_join_cannot_silently_change_identity(self):
        oracle = copy.deepcopy(self.oracle)
        oracle['cases'][0]['assessments'][0]['full_name'] = 'wrong/identity'
        with self.assertRaisesRegex(ValueError, 'invalid source-joined judgment'):
            runner.validate(oracle, self.challenges, self.cases, self.cards, self.members)

    def test_negative_annotations_do_not_filter_or_change_projection(self):
        runner.validate(self.oracle, self.challenges, self.cases, self.cards, self.members)
        case = self.challenges[-4]  # Explicit Caddy exclusion, paired with ND-01.
        original = self.cases[0]
        q = runner.base.old.make_query(self.plan, case)
        old = runner.base.old.make_query(self.plan, original)
        self.assertEqual(q['variants'], old['variants'])
        self.assertEqual(q['constraints'], old['constraints'])
        self.assertNotIn('forbidden', q)


if __name__ == '__main__':
    unittest.main()
