"""Exact-trust and complete-pack instrumentation without ignored scale fixtures."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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

    def stream_fixture(self):
        card = copy.deepcopy(self.record['evidence_pack']['cards'][0]['card'])
        other = copy.deepcopy(card)
        other['identity']['github_repository_id'] += 1
        pins = dict(self.record['retrieval']['pins'])
        snapshot = {key: pins[key] for key in ('card_schema_version', 'activity_schema_version',
                    'catalog_snapshot_id', 'source_sha256', 'taxonomy_sha256', 'corpus_kind')}
        snapshot['schema_version'] = snapshot.pop('card_schema_version')
        snapshot.update(cards=[card, other], builder_version='unit-only',
                        field_contract_sha256='1' * 64, source_snapshot_date='2026-10-08')
        return snapshot, pins

    def read_stream_fixture(self, snapshot, pins, *, count=2, candidates=None):
        raw = self.h.canonical(snapshot)
        pins = dict(pins, cards_sha256=hashlib.sha256(raw).hexdigest())
        if candidates is None:
            candidates = [snapshot['cards'][0]['identity']['github_repository_id']]
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as folder:
            path = Path(folder) / 'snapshot.json'
            path.write_bytes(raw)
            return self.h.stream_candidate_cards(path, pins, count, len(raw), candidates)

    def test_bounded_hash_guard_has_no_whole_file_read_and_fails_closed(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as folder:
            path = Path(folder) / 'pinned.json'
            raw = b'x' * 8193
            path.write_bytes(raw)
            hashed = hashlib.sha256(raw).hexdigest()
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('whole read forbidden')):
                self.h.verified_file(path, path, hashed, len(raw))
                for expected_path, expected_hash, size in (
                    (path.with_name('other'), hashed, len(raw)),
                    (path, '0' * 64, len(raw)), (path, hashed, len(raw) + 1)):
                    with self.subTest(expected_path=expected_path, size=size), self.assertRaises(ValueError):
                        self.h.verified_file(path, expected_path, expected_hash, size)

    def test_stream_validated_count_differs_from_retained_count(self):
        snapshot, pins = self.stream_fixture()
        selected, receipt = self.read_stream_fixture(snapshot, pins)
        self.assertEqual(receipt, {'validated_card_count': 2, 'retained_card_count': 1})
        self.assertEqual(list(selected), [snapshot['cards'][0]['identity']['github_repository_id']])
        for mutation in ('duplicate', 'schema', 'corpus', 'missing_requested', 'count'):
            changed = copy.deepcopy(snapshot)
            count, candidates = 2, None
            if mutation == 'duplicate':
                changed['cards'][1]['identity'] = copy.deepcopy(changed['cards'][0]['identity'])
            elif mutation == 'schema':
                changed['cards'][1]['schema_version'] = '9.0.0'
            elif mutation == 'corpus':
                changed['cards'][1]['corpus_kind'] = 'catalog_snapshot'
            elif mutation == 'missing_requested':
                candidates = [99]
            else:
                count = 3
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.read_stream_fixture(changed, pins, count=count, candidates=candidates)

    def test_hash_failure_prevents_shared_parser_construction(self):
        snapshot, pins = self.stream_fixture()
        raw = self.h.canonical(snapshot)
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as folder:
            path = Path(folder) / 'snapshot.json'
            path.write_bytes(raw)
            with patch.object(self.h.packs, '_SnapshotJSONStream', side_effect=AssertionError('parser reached')):
                with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                    self.h.stream_candidate_cards(path, dict(pins, cards_sha256='0' * 64), 2, len(raw), [])

    def test_prior_fidelity_recomputes_canonical_hashes_and_detects_changed_payload(self):
        row = {'query': self.query, 'retrieval_result': self.record['retrieval'],
               'evidence_pack': self.record['evidence_pack']}
        expected = {key: self.h.digest(row[field]) for key, field in
                    (('query_sha256', 'query'), ('result_sha256', 'retrieval_result'),
                     ('pack_sha256', 'evidence_pack'))}
        self.h.validate_prior_fidelity(row, expected)
        changed = copy.deepcopy(row)
        changed['retrieval_result']['candidates'][0]['rrf_score'] = .9
        with self.assertRaisesRegex(ValueError, 'prior capture fidelity'):
            self.h.validate_prior_fidelity(changed, expected)


if __name__ == '__main__':
    unittest.main()
