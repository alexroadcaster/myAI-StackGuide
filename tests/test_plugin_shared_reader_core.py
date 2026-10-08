"""Characterize public bytes before extracting shared post-trust execution cores."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tests.test_plugin_retrieval import (
    INDEX_PATH, MANIFEST_PATH, POLICY_PATH, ROOT, SNAPSHOT_PATH,
    base_query, canonical_bytes, canonical_sha256, execute_query, load_runtime_module,
)


RUN_ID = "d64946ce-de48-48b3-81a3-de9950887828"
PACK_ID = "core-characterization-pack"
# Observed at retrieval f5c2b386 / context_pack 3fa33b8f before this extraction.
BASELINES = (
    ("backend_baas_api", [["http", "web"], ["Go", "framework"]],
     "df303c3790cf7eaf7d87a51208cae8cb4383b3d60fe4a486b3f7790223d438aa",
     "630eeb63ecf412dee1e5da41efc3e5e275162298721384931e51153b2612fa9a"),
    ("files_media_storage", [["photos", "video"], ["self-hosted"]],
     "0f8130689f4657ac8995a8351c0e9efd70a2905892d44a6b240d36611f0c6115",
     "9a17f0b5d2f83b94820850fe9d889bee9d4233fcde847c294e2f9d6d697ed4bd"),
)


def scoped_query(route, terms):
    query = base_query()
    query["query_id"] = "core-characterization-" + route
    query["taxonomy_route_id"] = route
    query["variants"] = [
        {"variant_id": f"q{number}", "terms": values}
        for number, values in enumerate(terms, start=1)
    ]
    query.update(max_candidates=20, max_cards=2, max_evidence_bytes=100000)
    return query


class SharedReaderCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retrieval = load_runtime_module("retrieval")
        cls.packs = load_runtime_module("context_pack")
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        cls.snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        cls.cards = {card["identity"]["github_repository_id"]: card for card in cls.snapshot["cards"]}

    def public_result(self, query):
        return execute_query(self.retrieval, query, run_id=RUN_ID)

    def public_pack(self, query, result, cards=None):
        return self.packs.build_evidence_pack(
            query, result, self.cards if cards is None else cards,
            pack_id=PACK_ID, max_cards=2, max_evidence_bytes=100000,
        )

    def test_public_result_and_pack_preserve_observed_baseline_bytes(self):
        for route, terms, result_hash, pack_hash in BASELINES:
            with self.subTest(route=route):
                query = scoped_query(route, terms)
                result = self.public_result(query)
                self.assertEqual(canonical_sha256(result), result_hash)
                self.assertEqual(canonical_sha256(self.public_pack(query, result)), pack_hash)

    def test_public_reader_rejects_different_synthetic_manifest(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["pins"]["corpus_kind"] = "synthetic_fixture"
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            manifest_path = Path(directory) / "synthetic-manifest.json"
            manifest_path.write_bytes(canonical_bytes(manifest))
            result = execute_query(self.retrieval, scoped_query(*BASELINES[0][:2]),
                                   run_id=RUN_ID, manifest_path=manifest_path)
        self.assertEqual((result["status"], result["reason_codes"]),
                         ("index_incompatible", ["index_incompatible"]))

    def test_public_pack_rejects_forged_cards_and_wrong_pins(self):
        query = scoped_query(*BASELINES[0][:2])
        result = self.public_result(query)
        repository_id = result["candidates"][0]["github_repository_id"]
        cards = dict(self.cards)
        cards[repository_id] = copy.deepcopy(cards[repository_id])
        cards[repository_id]["identity"]["full_name"] = "forged/card"
        with self.assertRaisesRegex(ValueError, "supplied card does not match"):
            self.public_pack(query, result, cards)
        wrong_result = copy.deepcopy(result)
        wrong_result["pins"]["index_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "pins do not match trusted"):
            self.public_pack(query, wrong_result)

    def test_shared_cores_preserve_complete_public_result_and_pack_bytes(self):
        trusted = self.packs._cards_from_verified_snapshot(
            self.snapshot, self.manifest["pins"], expected_count=self.manifest["row_count"]
        )
        for route, terms, _, _ in BASELINES:
            with self.subTest(route=route):
                query = scoped_query(route, terms)
                public_result = self.public_result(query)
                core_result = self.retrieval._retrieve_verified_bundle(
                    query, run_id=RUN_ID, index_path=INDEX_PATH,
                    manifest=self.manifest, policy=self.policy,
                )
                self.assertEqual(canonical_bytes(core_result), canonical_bytes(public_result))
                candidate_ids = [item["github_repository_id"] for item in core_result["candidates"]]
                selected = self.packs._select_verified_cards(trusted, self.cards, candidate_ids)
                core_pack = self.packs._build_evidence_pack_from_trusted_cards(
                    query, core_result, selected, pack_id=PACK_ID,
                    max_cards=2, max_evidence_bytes=100000,
                )
                self.assertEqual(canonical_bytes(core_pack), canonical_bytes(self.public_pack(query, public_result)))
                self.assertLessEqual(len(core_pack["cards"]), query["max_cards"])
                self.assertLessEqual(len(canonical_bytes(core_pack)), query["max_evidence_bytes"])
                packed = {item["card"]["identity"]["github_repository_id"] for item in core_pack["cards"]}
                excluded = {item["github_repository_id"] for item in core_pack["exclusions"]}
                self.assertFalse(packed & excluded)
                self.assertEqual(packed | excluded, set(candidate_ids))

    def test_verified_snapshot_rejects_duplicate_identity_wrong_pin_and_forged_join(self):
        duplicate_snapshot = dict(self.snapshot)
        duplicate_snapshot["cards"] = list(self.snapshot["cards"])
        duplicate_snapshot["cards"][1] = duplicate_snapshot["cards"][0]
        with self.assertRaisesRegex(ValueError, "card identity mismatch"):
            self.packs._cards_from_verified_snapshot(duplicate_snapshot, self.manifest["pins"], expected_count=self.manifest["row_count"])
        wrong_pins = dict(self.manifest["pins"])
        wrong_pins["taxonomy_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "snapshot identity mismatch"):
            self.packs._cards_from_verified_snapshot(self.snapshot, wrong_pins, expected_count=self.manifest["row_count"])
        trusted = self.packs._cards_from_verified_snapshot(self.snapshot, self.manifest["pins"], expected_count=self.manifest["row_count"])
        repository_id = next(iter(trusted))
        forged = copy.deepcopy(trusted[repository_id])
        forged["identity"]["full_name"] = "forged/card"
        with self.assertRaisesRegex(ValueError, "supplied card does not match"):
            self.packs._select_verified_cards(trusted, {repository_id: forged}, [repository_id])

    def test_shared_reader_preserves_no_hit_and_invalid_query_outcomes(self):
        query = scoped_query(*BASELINES[0][:2])
        query["variants"] = [{"variant_id": "q1", "terms": ["cp04nomatchingliteralzz"]}]
        for change, expected_status in (({}, "no_match"),
                                        ({"max_candidates": self.policy["limits"]["max_retrieved_hits"] + 1}, "invalid_query"),
                                        ({"taxonomy_route_id": "absent_but_valid_route"}, "invalid_query")):
            with self.subTest(change=change):
                changed = copy.deepcopy(query)
                changed.update(change)
                public = self.public_result(changed)
                core = self.retrieval._retrieve_verified_bundle(
                    changed, run_id=RUN_ID, index_path=INDEX_PATH,
                    manifest=self.manifest, policy=self.policy,
                )
                self.assertEqual(core["status"], expected_status)
                self.assertEqual(canonical_bytes(core), canonical_bytes(public))
                core_pack = self.packs._build_evidence_pack_from_trusted_cards(
                    changed, core, {}, pack_id=PACK_ID, max_cards=2, max_evidence_bytes=100000,
                )
                self.assertEqual(canonical_bytes(core_pack), canonical_bytes(self.public_pack(changed, public)))

    def test_shared_pack_preserves_identity_exclusion_and_binding_validation(self):
        query = scoped_query(*BASELINES[0][:2])
        result = self.public_result(query)
        trusted = self.packs._trusted_cards(
            result["pins"], self.cards,
            [item["github_repository_id"] for item in result["candidates"]],
        )
        repository_id = result["candidates"][0]["github_repository_id"]
        changed = dict(trusted)
        changed[repository_id] = copy.deepcopy(changed[repository_id])
        changed[repository_id]["identity"]["github_repository_id"] = repository_id + 1
        pack = self.packs._build_evidence_pack_from_trusted_cards(
            query, result, changed, pack_id=PACK_ID, max_cards=2, max_evidence_bytes=100000,
        )
        exclusion = next(item for item in pack["exclusions"] if item["github_repository_id"] == repository_id)
        self.assertEqual(exclusion["reason_codes"], ["unavailable"])
        wrong_result = copy.deepcopy(result)
        wrong_result["query_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "does not bind to query"):
            self.packs._build_evidence_pack_from_trusted_cards(
                query, wrong_result, trusted, pack_id=PACK_ID, max_cards=2, max_evidence_bytes=100000,
            )


if __name__ == "__main__":
    unittest.main()
