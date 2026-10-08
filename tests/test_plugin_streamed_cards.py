"""Bounded card selection must validate every byte and every unselected card."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_plugin_retrieval import (
    ROOT, SNAPSHOT_PATH, base_query, canonical_bytes, execute_query, load_runtime_module,
)


class StreamedCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packs = load_runtime_module("context_pack")
        cls.retrieval = load_runtime_module("retrieval")

    def fixture(self):
        pins = {
            "card_schema_version": "2.0.0", "activity_schema_version": "2.0.0",
            "catalog_snapshot_id": "stream-test", "source_sha256": "1" * 64,
            "taxonomy_sha256": "2" * 64, "corpus_kind": "synthetic_fixture",
        }
        snapshot = {
            "schema_version": pins["card_schema_version"],
            "activity_schema_version": pins["activity_schema_version"],
            "catalog_snapshot_id": pins["catalog_snapshot_id"],
            "source_sha256": pins["source_sha256"], "taxonomy_sha256": pins["taxonomy_sha256"],
            "corpus_kind": pins["corpus_kind"], "builder_version": "stream-unit-probe",
            "field_contract_sha256": "3" * 64, "source_snapshot_date": "2026-10-08",
            "cards": [
                {"schema_version": "2.0.0", "corpus_kind": "synthetic_fixture",
                 "identity": {"github_repository_id": number},
                 "text": 'Карта 🙂 "quoted" \\ escaped\n' + str(number)}
                for number in range(1, 5)
            ],
        }
        return snapshot, pins

    def read_fixture(self, raw, pins, *, expected_count=4, candidates=(2,), chunk_bytes=17, max_bytes=None):
        pins = dict(pins)
        pins.setdefault("cards_sha256", hashlib.sha256(raw).hexdigest())
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            path = Path(directory) / "snapshot.json"
            path.write_bytes(raw)
            return self.packs._stream_verified_snapshot_cards(
                path, pins, expected_count=expected_count,
                max_bytes=len(raw) if max_bytes is None else max_bytes,
                candidate_ids=list(candidates), chunk_bytes=chunk_bytes,
            )

    def test_public_path_does_not_allocate_the_whole_snapshot(self):
        # Test setup may parse the pinned fixture; the production read is guarded.
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        cards = {card["identity"]["github_repository_id"]: card for card in snapshot["cards"]}
        query = base_query()
        result = execute_query(self.retrieval, query)
        original_read_bytes = Path.read_bytes

        def reject_snapshot_read(path):
            if path == SNAPSHOT_PATH:
                raise AssertionError("whole-snapshot read must be replaced by bounded streaming")
            return original_read_bytes(path)

        with patch.object(Path, "read_bytes", new=reject_snapshot_read):
            pack = self.packs.build_evidence_pack(
                query, result, cards, pack_id="stream-public-probe",
                max_cards=2, max_evidence_bytes=100000,
            )
        self.assertLessEqual(len(pack["cards"]), 2)

    def test_only_requested_cards_survive_tiny_utf8_and_escape_chunks(self):
        snapshot, pins = self.fixture()
        for ascii_encoding in (False, True):
            raw = json.dumps(snapshot, ensure_ascii=ascii_encoding).encode("utf-8")
            for chunk in (1, 7, 19, 65536):
                with self.subTest(ascii_encoding=ascii_encoding, chunk=chunk):
                    selected = self.read_fixture(raw, pins, candidates=(2, 4), chunk_bytes=chunk)
                    self.assertEqual(set(selected), {2, 4})
                    self.assertEqual(selected[2], snapshot["cards"][1])
                    self.assertEqual(selected[4], snapshot["cards"][3])

    def test_unselected_duplicates_and_invalid_card_fields_fail(self):
        snapshot, pins = self.fixture()
        for mutation in (
            lambda card: card["identity"].update(github_repository_id=1),
            lambda card: card["identity"].update(github_repository_id=True),
            lambda card: card["identity"].update(github_repository_id=0),
            lambda card: card.update(schema_version="9.0.0"),
            lambda card: card.update(corpus_kind="catalog_snapshot"),
        ):
            changed = copy.deepcopy(snapshot)
            mutation(changed["cards"][3])
            with self.subTest(card=changed["cards"][3]), self.assertRaises(ValueError):
                self.read_fixture(canonical_bytes(changed), pins)

    def test_complete_json_utf8_and_nonfinite_values_are_checked(self):
        snapshot, pins = self.fixture()
        raw = canonical_bytes(snapshot)
        bad_inputs = (
            raw[:-1], b"!" + raw, raw + b"garbage", raw + b"{}",
            raw.replace(b'"cards":[', b'"cards":[,', 1),
            raw.replace(b'"cards":[', b'"cards":[NaN,', 1),
            raw.replace(b'"cards":[', b'"cards":[Infinity,', 1),
            raw.replace(b'"cards":[', b'"cards":[1e400,', 1),
            raw.replace(b'"text":', b'"bad":null,"text":', 1)[:-3],
            raw.replace("Карта".encode("utf-8"), b"\xff", 1),
            raw.replace(b'"cards":', b'"cards":[],"cards":', 1),
            raw.replace(b'"builder_version":"stream-unit-probe"', b'"builder_version":[]', 1),
        )
        for changed in bad_inputs:
            with self.subTest(raw=changed[:60]), self.assertRaises((ValueError, UnicodeDecodeError)):
                self.read_fixture(changed, pins)

    def test_count_pins_hash_byte_cap_and_requested_coverage_fail_closed(self):
        snapshot, pins = self.fixture()
        raw = canonical_bytes(snapshot)
        for kwargs in ({"expected_count": 3}, {"expected_count": -1},
                       {"expected_count": True}, {"max_bytes": len(raw) - 1},
                       {"candidates": (99,)}, {"candidates": (True,)}, {"chunk_bytes": 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.read_fixture(raw, pins, **kwargs)
        wrong_hash = dict(pins, cards_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.read_fixture(raw, wrong_hash)
        wrong_pins = dict(pins, taxonomy_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.read_fixture(raw, wrong_pins)

    def test_selected_card_canonical_tampering_is_rejected(self):
        snapshot, pins = self.fixture()
        selected = self.read_fixture(canonical_bytes(snapshot), pins)
        supplied = copy.deepcopy(selected)
        supplied[2]["text"] = "tampered"
        with self.assertRaisesRegex(ValueError, "supplied card does not match"):
            self.packs._select_verified_cards(selected, supplied, [2])

    def test_read_and_working_buffer_bounds_do_not_grow_with_the_cards_array(self):
        snapshot, pins = self.fixture()
        card_template = snapshot["cards"][0]
        snapshot["cards"] = []
        for number in range(1, 301):
            card = copy.deepcopy(card_template)
            card["identity"]["github_repository_id"] = number
            card["text"] = "x" * 2048
            snapshot["cards"].append(card)
        raw = canonical_bytes(snapshot)
        chunk_bytes = 127
        observed = []
        fill = self.packs._SnapshotJSONStream._fill

        def track_read(stream):
            before = stream.byte_count
            fill(stream)
            observed.append((stream.byte_count - before, len(stream.buffer)))

        with patch.object(self.packs._SnapshotJSONStream, "_fill", new=track_read):
            selected = self.read_fixture(raw, pins, expected_count=300,
                                         candidates=(2, 299), chunk_bytes=chunk_bytes)
        self.assertEqual(set(selected), {2, 299})
        self.assertEqual(sum(size for size, _ in observed), len(raw), "complete bytes must be read through EOF")
        self.assertLessEqual(max(size for size, _ in observed), chunk_bytes)
        largest_card = max(len(canonical_bytes(card)) for card in snapshot["cards"])
        self.assertLessEqual(max(size for _, size in observed), largest_card + chunk_bytes)

    def test_nonfinite_unselected_fields_and_unknown_envelope_keys_fail(self):
        snapshot, pins = self.fixture()
        for invalid in (float("nan"), float("inf")):
            changed = copy.deepcopy(snapshot)
            changed["cards"][3]["number"] = invalid
            raw = json.dumps(changed, ensure_ascii=False).encode("utf-8")
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.read_fixture(raw, pins)
        changed = copy.deepcopy(snapshot)
        changed["unknown_metadata"] = "unsupported"
        with self.assertRaisesRegex(ValueError, "incompatible snapshot envelope"):
            self.read_fixture(canonical_bytes(changed), pins)

    def test_wrong_checksum_fails_before_any_json_value_is_decoded(self):
        snapshot, pins = self.fixture()
        pins["cards_sha256"] = "0" * 64
        with patch.object(self.packs._SnapshotJSONStream, "value",
                          side_effect=AssertionError("wrong checksum must fail before JSON decoding")) as decode:
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                self.read_fixture(canonical_bytes(snapshot), pins)
        self.assertEqual(decode.call_count, 0)

    def test_mutation_between_prehash_and_parse_fails_the_second_hash(self):
        snapshot, pins = self.fixture()
        raw = canonical_bytes(snapshot)
        changed = raw.replace(b"stream-unit-probe", b"stream-unit-chang", 1)
        self.assertNotEqual(raw, changed)
        initialize = self.packs._SnapshotJSONStream.__init__

        def mutate_before_parse(stream, handle, *, max_bytes, chunk_bytes):
            Path(handle.name).write_bytes(changed)
            initialize(stream, handle, max_bytes=max_bytes, chunk_bytes=chunk_bytes)

        with patch.object(self.packs._SnapshotJSONStream, "__init__", new=mutate_before_parse):
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                self.read_fixture(raw, pins)


if __name__ == "__main__":
    unittest.main()
