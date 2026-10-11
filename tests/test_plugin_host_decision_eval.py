"""Synthetic outer-observer regression, without native/model execution."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'host_decision_observer_tests', ROOT / 'evals/plugin-v1/run_final_host_decision.py')
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)


class HostDecisionObserverTests(unittest.TestCase):
    def observe(self, reason, constraint='allowed'):
        # Zero-fit allowed IDs still need truthful hard exclusions. A positive
        # packed peer ensures this test does not depend on Recall/survival failure.
        case = dict(metric_family='semantic', k=12, judgments=[
            dict(github_repository_id=1, grade=0, constraint=constraint),
            dict(github_repository_id=2, grade=3, constraint='allowed')])
        result = dict(decision_receipt=dict(decision_order=[2,1]),
            decision_pack=dict(cards=[dict(card=dict(identity=dict(github_repository_id=2)))],
                exclusions=[dict(github_repository_id=1, reason_codes=[reason])]))
        return observer.host_observe(case, result)

    def test_allowed_zero_fit_product_exclusion_is_false(self):
        result = self.observe('explicit_product_exclusion')
        self.assertEqual(result['false_exclusions'], [1])
        self.assertEqual(result['ranking']['ranking']['recall_at_k'], 1)
        self.assertEqual(result['pack_survival'], 1)

    def test_allowed_zero_fit_dependency_conflict_is_false(self):
        result = self.observe('documented_dependency_conflict')
        self.assertEqual(result['false_exclusions'], [1])
        self.assertEqual(result['ranking']['ranking']['recall_at_k'], 1)
        self.assertEqual(result['pack_survival'], 1)

    def test_denied_identity_hard_exclusions_are_not_false(self):
        for reason in ('explicit_product_exclusion','documented_dependency_conflict'):
            with self.subTest(reason=reason):
                self.assertEqual(self.observe(reason, 'denied')['false_exclusions'], [])


if __name__ == '__main__':
    unittest.main()
