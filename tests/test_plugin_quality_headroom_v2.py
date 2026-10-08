"""Separate evaluator-layer boundaries; frozen production runner tests stay intact."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HeadroomAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('headroom_adapter_tests', ROOT / 'evals/plugin-v1/measure_quality_headroom_v2.py')
        cls.adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.adapter)

    def test_fixture_paths_cannot_read_public_bundle(self):
        with self.assertRaisesRegex(ValueError, 'isolated fixture'):
            self.adapter.fixture_path('plugins/myai-stackguide/assets/catalog.search.sqlite')

    def test_cap_and_dedupe_failure_is_not_a_capacity_pass(self):
        self.assertFalse(self.adapter.bounds_pass([1, 1], 2))
        self.assertFalse(self.adapter.bounds_pass([1, 2, 3], 2))
        self.assertTrue(self.adapter.bounds_pass([1, 2], 2))

    def test_synthetic_sql_evidence_cannot_assert_production_reader_success(self):
        report = self.adapter.evidence_ceiling()
        self.assertFalse(report['production_reader_accepted'])
        self.assertFalse(report['relevance_claim_allowed'])
        self.assertFalse(report['full_card_pack_capacity_measured'])


if __name__ == '__main__':
    unittest.main()
