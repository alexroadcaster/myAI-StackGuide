"""Exact-trust and complete-pack instrumentation without ignored scale fixtures."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / 'evals/plugin-v1/measure_full_headroom_v3.py'


def load_module():
    spec = importlib.util.spec_from_file_location('full_headroom_v3_test', MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FullHeadroomV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = load_module()
        fixture = json.loads((ROOT / 'tests/fixtures/plugin_retrieval_eval.json').read_text(encoding='utf-8'))
        cls.record = fixture['records'][0]
        contracts = json.loads((ROOT / 'tests/fixtures/plugin_contracts.json').read_text(encoding='utf-8'))
        cls.query = contracts['positive']['retrieval/catalog-query.schema.json']

    def test_exact_bytes_reject_hash_size_and_path_mismatch(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as folder:
            path = Path(folder) / 'pinned.json'
            raw = b'{"safe":true}'
            path.write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()
            self.assertEqual(self.h.verified_bytes(path, path, digest, len(raw)), raw)
            for expected_path, expected_hash, size in (
                (path.with_name('other.json'), digest, len(raw)),
                (path, '0' * 64, len(raw)), (path, digest, len(raw) + 1),
            ):
                with self.subTest(expected_path=expected_path, size=size):
                    with self.assertRaises(ValueError):
                        self.h.verified_bytes(path, expected_path, expected_hash, size)

    def test_normalization_rejects_duplicate_identity_wrong_corpus_and_schema(self):
        card = copy.deepcopy(self.record['evidence_pack']['cards'][0]['card'])
        pins = self.record['retrieval']['pins']
        snapshot = dict(schema_version=pins['card_schema_version'],
                        activity_schema_version=pins['activity_schema_version'],
                        catalog_snapshot_id=pins['catalog_snapshot_id'],
                        source_sha256=pins['source_sha256'], taxonomy_sha256=pins['taxonomy_sha256'],
                        corpus_kind=pins['corpus_kind'], cards=[card])
        self.assertEqual(len(self.h.normalize_cards(snapshot, pins, 1)), 1)
        for mutate in ('duplicate', 'corpus', 'schema'):
            changed = copy.deepcopy(snapshot)
            expected = 1
            if mutate == 'duplicate':
                changed['cards'].append(copy.deepcopy(card))
                expected = 2
            elif mutate == 'corpus':
                changed['cards'][0]['corpus_kind'] = 'catalog_snapshot'
            else:
                changed['cards'][0]['schema_version'] = '1.0.0'
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                self.h.normalize_cards(changed, pins, expected)

    def test_canonical_card_selection_rejects_tampering(self):
        card = copy.deepcopy(self.record['evidence_pack']['cards'][0]['card'])
        rid = card['identity']['github_repository_id']
        forged = copy.deepcopy(card)
        forged['identity']['full_name'] = 'forged/card'
        with self.assertRaisesRegex(ValueError, 'supplied card does not match'):
            self.h.packs._select_verified_cards({rid: card}, {rid: forged}, [rid])

    def test_guard_preserves_denied_coverage_and_detects_fake_score_or_missing_exclusion(self):
        query, result, pack = copy.deepcopy(self.query), copy.deepcopy(self.record['retrieval']), copy.deepcopy(self.record['evidence_pack'])
        query['max_candidates'] = 150
        self.h.validate_capture(query, result, pack)
        rid = result['candidates'][0]['github_repository_id']
        denied = copy.deepcopy(pack)
        denied['cards'] = []
        denied['exclusions'] = [{'github_repository_id': rid, 'reason_codes': ['constraint_mismatch']}]
        self.h.validate_capture(query, result, denied)
        missing = copy.deepcopy(denied)
        missing['exclusions'] = []
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.h.validate_capture(query, result, missing)
        forged = copy.deepcopy(pack)
        forged['cards'][0]['rrf_score'] = .9
        with self.assertRaisesRegex(ValueError, 'raw rank'):
            self.h.validate_capture(query, result, forged)

    def test_real_pack_denies_constraint_and_keeps_original_rank(self):
        query = copy.deepcopy(self.query)
        query['constraints']['allowed_licenses'] = ['GPL-3.0-only']
        result = copy.deepcopy(self.record['retrieval'])
        result['query_sha256'] = self.h.digest(query)
        card = self.record['evidence_pack']['cards'][0]['card']
        rid = card['identity']['github_repository_id']
        pack = self.h.packs._build_evidence_pack_from_trusted_cards(
            query, result, {rid: card}, pack_id='test-denied',
            max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
        self.assertEqual(pack['cards'], [])
        self.assertIn('constraint_mismatch', pack['exclusions'][0]['reason_codes'])
        self.h.validate_capture(query, result, pack)

    def test_request_budgets_and_nanosecond_units(self):
        query = copy.deepcopy(self.query)
        query['max_evidence_bytes'] = 1024
        with self.assertRaisesRegex(ValueError, 'evidence bytes'):
            self.h.validate_capture(query, self.record['retrieval'], self.record['evidence_pack'])
        query = copy.deepcopy(self.query)
        query['max_candidates'] = 0
        with self.assertRaisesRegex(ValueError, 'hit budget'):
            self.h.validate_capture(query, self.record['retrieval'], self.record['evidence_pack'])
        self.assertEqual(self.h.elapsed_ms(1_000_000, 3_500_000), 2.5)
        self.assertEqual(self.h.percentile(list(range(1, 31)), .95), 29)
        self.assertEqual(self.h.percentile(list(range(1, 31)), .5), 15)


if __name__ == '__main__':
    unittest.main()
