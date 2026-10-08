"""Source-first oracle completeness and provenance regressions, never retrieval."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evals/plugin-v1'


class OracleV2Tests(unittest.TestCase):
    def load(self):
        self.assertTrue((DIRECTORY / 'quality-plan-v2.json').is_file(),
                        'prospective complete oracle must exist before retrieval')
        spec = importlib.util.spec_from_file_location('oracle_v2', DIRECTORY / 'build_oracle_v2.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        plan = json.loads((DIRECTORY / 'quality-plan-v2.json').read_text(encoding='utf8'))
        labels = json.loads((DIRECTORY / 'quality-judgments-v2.json').read_text(encoding='utf8'))
        return module, plan, labels

    def test_complete_goal_source_oracle(self):
        module, plan, labels = self.load()
        result = module.validate(plan, labels)
        self.assertEqual(result['heldout_container_count'], 14)
        self.assertGreaterEqual(result['semantic_cases'], 24)
        self.assertGreater(result['explicit_judgments'], 500)
        self.assertEqual(plan['thresholds'], module.load_reference()['thresholds'])

    def test_missing_zero_grade_is_rejected(self):
        module, plan, labels = self.load()
        broken = copy.deepcopy(labels)
        rows = broken['cases'][1]['judgments']
        rows.pop(next(i for i, row in enumerate(rows) if row['grade'] == 0))
        with self.assertRaisesRegex(ValueError, 'complete'):
            module.validate(plan, broken)

    def test_invented_source_evidence_is_rejected(self):
        module, plan, labels = self.load()
        broken = copy.deepcopy(labels)
        broken['cases'][0]['judgments'][0]['evidence'][0]['value'] = 'invented capability'
        with self.assertRaisesRegex(ValueError, 'evidence'):
            module.validate(plan, broken)

    def test_same_category_never_grants_goal_relevance(self):
        module, plan, labels = self.load()
        module.validate(plan, labels)
        case = next(c for c in labels['cases'] if c['case_id'] == 'CP04-V2-H03')
        grades = {j['github_repository_id']: j['grade'] for j in case['judgments']}
        self.assertGreaterEqual(grades[455229168], 2)  # photo/video solution
        self.assertEqual(grades[187961907], 0)  # Android book reader
        self.assertEqual(grades[161012019], 1)  # media server, photo fit unknown

    def test_identity_metrics_are_separate(self):
        _, plan, _ = self.load()
        probes = [c for c in plan['cases'] if c['goal_kind'] == 'exact_identity']
        self.assertEqual(len(probes), 4)
        self.assertTrue(all(c['metric_family'] == 'identity' for c in probes))
        self.assertTrue(all(c['metric_family'] == 'semantic' for c in plan['cases']
                            if c['goal_kind'] != 'exact_identity'))

    def test_archived_source_cannot_be_allowed(self):
        module, plan, labels = self.load()
        row = next(j for c in labels['cases'] for j in c['judgments']
                   if j['full_name'] == 'tenable/terrascan')
        self.assertEqual(row['constraint'], 'denied')
        self.assertEqual(row['grade'], 3)  # topical fit stays distinct
        broken = copy.deepcopy(labels)
        next(j for c in broken['cases'] for j in c['judgments']
             if j['full_name'] == 'tenable/terrascan')['constraint'] = 'allowed'
        with self.assertRaisesRegex(ValueError, 'constraint source'):
            module.validate(plan, broken)

    def test_container_tag_requires_actual_container_query(self):
        _, plan, _ = self.load()
        cases = [c for c in plan['cases'] if 'container_union' in c['tags']]
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]['target_category_id'], 'communications_personal_ops')
        self.assertEqual(len(cases[0]['universe_ids']), 32)


if __name__ == '__main__':
    unittest.main()
