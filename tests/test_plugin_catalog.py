"""CP-06 source-to-RepositoryCardV2 parity tests."""

from __future__ import annotations

from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts" / "build_plugin_catalog.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_plugin_catalog_cp06", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PluginCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.source = json.loads((ROOT / "data" / "catalog_manifest.json").read_text(encoding="utf-8"))
        cls.snapshot = json.loads(cls.builder.OUTPUT.read_text(encoding="utf-8"))
        cls.cards = cls.snapshot["cards"]
        cls.cards_by_id = {card["identity"]["github_repository_id"]: card for card in cls.cards}
        cls.source_by_id = {item["githubRepositoryId"]: item for item in cls.source["repositories"]}

    def test_frozen_inputs_and_snapshot_versions_are_exact(self):
        manifest, taxonomy, freeze = self.builder.validate_frozen_inputs()
        self.assertEqual(manifest["snapshot"], "2026-09-01")
        self.assertEqual(taxonomy["source_sha256"], freeze["cp06Handoff"]["requiredSourceSha256"])
        self.assertEqual(self.snapshot["schema_version"], "2.0.0")
        self.assertEqual(self.snapshot["activity_schema_version"], "2.0.0")
        self.assertEqual(self.snapshot["corpus_kind"], "catalog_snapshot")
        self.assertEqual(self.snapshot["catalog_snapshot_id"], freeze["snapshotId"])

    def test_source_pin_drift_fails_before_output(self):
        before = self.builder.OUTPUT.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "catalog_manifest.json"
            changed.write_bytes((ROOT / "data" / "catalog_manifest.json").read_bytes() + b" ")
            with mock.patch.object(self.builder, "SOURCE", changed):
                with self.assertRaisesRegex(self.builder.PluginCatalogBuildError, "frozen pin mismatch"):
                    self.builder.validate_frozen_inputs()
        self.assertEqual(self.builder.OUTPUT.read_bytes(), before)

    def test_all_numeric_identities_and_lineage_are_lossless(self):
        self.assertEqual(len(self.cards), 2500)
        self.assertEqual(set(self.cards_by_id), set(self.source_by_id))
        self.assertEqual(len(self.cards_by_id), 2500)
        self.assertTrue(all(isinstance(item, int) and 0 < item <= 2**63 - 1 for item in self.cards_by_id))
        for github_repository_id, source in self.source_by_id.items():
            identity = self.cards_by_id[github_repository_id]["identity"]
            self.assertEqual(identity["catalog_record_id"], source["id"])
            self.assertEqual(
                identity["merged_catalog_record_ids"],
                [item for item in source.get("sourceRecordIds", [source["id"]]) if item != source["id"]],
            )
        self.assertEqual(sum(len(card["identity"]["merged_catalog_record_ids"]) for card in self.cards), 10)
        all_lineage = [
            item
            for card in self.cards
            for item in (card["identity"]["catalog_record_id"], *card["identity"]["merged_catalog_record_ids"])
        ]
        self.assertEqual(len(all_lineage), len(set(all_lineage)))

    def test_aliases_cohorts_statuses_and_classifications_match_frozen_counts(self):
        aliases = [alias.casefold() for card in self.cards for alias in card["identity"]["full_name_aliases"]]
        current_names = {card["identity"]["full_name"].casefold() for card in self.cards}
        self.assertEqual(len(aliases), 55)
        self.assertEqual(len(set(aliases)), 55)
        self.assertFalse(set(aliases) & current_names)
        self.assertEqual(Counter(card["catalog"]["membership_cohort"] for card in self.cards),
                         Counter({"baseline": 1624, "cat07a_expansion": 876}))
        self.assertEqual(Counter(card["catalog"]["status"] for card in self.cards),
                         Counter({"candidate": 1987, "accepted": 485, "reference": 25, "benchmark": 3}))
        classifications = [item for card in self.cards for item in card["classifications"]]
        self.assertEqual(len(classifications), 2630)
        self.assertEqual(Counter(item["kind"] for item in classifications),
                         Counter({"category": 2618, "review_bucket": 12}))
        self.assertTrue(all(sum(item["role"] == "primary" for item in card["classifications"]) == 1
                            for card in self.cards))
        self.assertNotIn("container", {item["kind"] for item in classifications})

    def test_descriptions_preserve_nulls_without_fallback(self):
        for github_repository_id, source in self.source_by_id.items():
            descriptions = self.cards_by_id[github_repository_id]["descriptions"]
            expected_upstream = self.builder._clean_scalar(source.get("description"))
            expected_catalog = self.builder._clean_scalar(source.get("catalogDescription"))
            self.assertEqual(descriptions["upstream"], expected_upstream)
            self.assertEqual(descriptions["catalog"], expected_catalog)
            if expected_upstream is None:
                self.assertIsNone(descriptions["upstream"])
            if expected_catalog is None:
                self.assertIsNone(descriptions["catalog"])
        self.assertEqual(sum(card["descriptions"]["upstream"] is not None for card in self.cards), 1614)
        self.assertEqual(sum(card["descriptions"]["catalog"] is not None for card in self.cards), 1555)

    def test_languages_and_reviewed_delivery_values_are_preserved(self):
        magic = next(card for card in self.cards if card["identity"]["full_name"] == "21st-dev/magic-mcp")
        self.assertEqual(magic["repository"]["languages"][0]["scope"], "primary")
        self.assertEqual(magic["repository"]["languages"][0]["name"],
                         self.source_by_id[magic["identity"]["github_repository_id"]]["language"])
        self.assertEqual(max(len(card["repository"]["languages"]) for card in self.cards), 67)
        for name in ("0xPlaygrounds/rig", "1Panel-dev/MaxKB", "actions/runner"):
            source = next(item for item in self.source["repositories"] if item["fullName"] == name)
            card = self.cards_by_id[source["githubRepositoryId"]]
            if isinstance(source.get("form"), dict):
                self.assertEqual(card["delivery"]["form"]["rationale"], source["form"]["rationale"])
            if isinstance(source.get("deployment"), dict):
                self.assertEqual(card["delivery"]["deployment"]["rationale"], source["deployment"]["rationale"])
            if isinstance(source.get("hosting"), dict):
                self.assertEqual(card["delivery"]["hosting"]["rationale"], source["hosting"]["rationale"])

    def test_activity_dates_are_distinct_and_observations_resolve(self):
        missing_observed = []
        for card in self.cards:
            activity = card["activity"]
            event_fields = (
                "created_at", "repository_updated_at", "pushed_at", "last_commit_at",
                "last_release_at", "last_synced_at", "observed_at",
            )
            expected = {field for field in event_fields if activity[field] is not None}
            self.assertEqual(Counter(item["field"] for item in activity["observations"]), Counter(expected))
            evidence_ids = {item["evidence_id"] for item in card["evidence"]}
            self.assertTrue(all(set(item["evidence_refs"]) <= evidence_ids for item in activity["observations"]))
            if activity["observed_at"] is None:
                missing_observed.append(card["identity"]["full_name"])
            if activity["last_commit_at"] is None:
                self.assertIsNone(activity["last_commit_sha"])
                self.assertIsNone(activity["last_commit_branch"])
            else:
                self.assertRegex(activity["last_commit_sha"], r"^[a-f0-9]{40}$")
                self.assertIsNotNone(activity["last_commit_branch"])
        self.assertEqual(len(missing_observed), 5)

    def test_every_card_is_bounded_and_has_exact_public_pins(self):
        expected_pins = {
            "catalog_snapshot_id": self.snapshot["catalog_snapshot_id"],
            "source_sha256": self.snapshot["source_sha256"],
            "taxonomy_sha256": self.snapshot["taxonomy_sha256"],
            "field_contract_sha256": self.snapshot["field_contract_sha256"],
        }
        for card in self.cards:
            self.assertEqual(card["provenance"]["frozen_pins"], expected_pins)
            self.assertLessEqual(len(self.builder.canonical_bytes(card)), 24576)
            evidence_ids = {item["evidence_id"] for item in card["evidence"]}
            self.assertTrue(all(set(item["evidence_refs"]) <= evidence_ids for item in card["repository"]["stack"]))
            keys = set()
            pending = [card]
            while pending:
                value = pending.pop()
                if isinstance(value, dict):
                    keys.update(value)
                    pending.extend(value.values())
                elif isinstance(value, list):
                    pending.extend(value)
            self.assertFalse({"project_context", "user_context", "query", "local_storage"} & keys)

    def test_snapshot_has_deterministic_byte_parity_and_no_sidecar(self):
        rebuilt, report = self.builder.build_snapshot()
        self.assertEqual(self.builder.OUTPUT.read_bytes(), self.builder.canonical_bytes(rebuilt))
        self.assertEqual(report["rejections"], 0)
        self.assertFalse((ROOT / "data" / "plugin_catalog_metadata.json").exists())

    def test_active_schema_covers_frozen_edge_shapes(self):
        schema = json.loads((ROOT / "specs" / "catalog" / "repository-card.schema.json").read_text(encoding="utf-8"))
        pattern = re.compile(schema["$defs"]["catalogRecordId"]["pattern"])
        self.assertTrue(all(pattern.fullmatch(item["id"]) for item in self.source["repositories"]))
        kind_contract = schema["properties"]["classifications"]["items"]["properties"]["kind"]
        self.assertEqual(set(kind_contract["enum"]), {"category", "review_bucket"})
        self.assertGreaterEqual(schema["properties"]["repository"]["properties"]["languages"]["maxItems"], 67)
        self.assertEqual(schema["$defs"]["nullableUrl"]["anyOf"][0]["format"], "uri-reference")

if __name__ == "__main__":
    unittest.main()
