import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts" / "build_catalog_html.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_catalog_html_v5", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CatalogV5PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.payload = cls.builder.load_manifest()

    def test_manifest_schema_matches_builder_contract(self):
        schema = json.loads(self.builder.SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], self.payload["schemaVersion"])
        self.assertEqual(set(schema["required"]), self.builder.REQUIRED_TOP_LEVEL_FIELDS)

    def test_summary_counts_match_source_collections(self):
        summary = self.payload["summary"]
        self.assertEqual(summary["canonicalRepositories"], len(self.payload["repositories"]))
        self.assertEqual(summary["categories"], len(self.payload["categories"]))
        self.assertEqual(summary["placements"], len(self.payload["placements"]))
        self.assertEqual(summary["stackRecipes"], len(self.payload["stackRecipes"]))
        self.assertEqual(summary["compatibilityEdges"], len(self.payload["compatibility"]))

    def test_manifest_identity_is_unique(self):
        repository_ids = [item["id"] for item in self.payload["repositories"]]
        repository_names = [item["fullName"].casefold() for item in self.payload["repositories"]]
        category_keys = [item["key"] for item in self.payload["categories"]]
        self.assertEqual(len(repository_ids), len(set(repository_ids)))
        self.assertEqual(len(repository_names), len(set(repository_names)))
        self.assertEqual(len(category_keys), len(set(category_keys)))

    def test_preserved_unresolved_placement_keys_are_explicit(self):
        warnings = self.builder.integrity_warnings(self.payload)
        self.assertEqual(warnings["unresolvedPlacementCount"], 18)
        self.assertEqual(len(warnings["unresolvedPlacementRepositoryKeys"]), 14)

    def test_duplicate_repository_identity_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["repositories"][1]["id"] = payload["repositories"][0]["id"]
        with self.assertRaisesRegex(self.builder.CatalogContractError, "duplicate repository ids"):
            self.builder.validate_payload(payload)

    def test_summary_count_drift_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["summary"]["canonicalRepositories"] += 1
        with self.assertRaisesRegex(self.builder.CatalogContractError, "summary count mismatch"):
            self.builder.validate_payload(payload)

    def test_unsafe_script_sequence_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["title"] = "unsafe </script> boundary"
        with self.assertRaisesRegex(self.builder.CatalogContractError, "unsafe closing script"):
            self.builder.validate_payload(payload)

    def test_generated_html_matches_checked_in_artifact_exactly(self):
        expected = self.builder.page(self.payload)
        actual = self.builder.OUTPUT.read_text(encoding="utf-8")
        self.assertEqual(expected, actual)

    def test_generated_outputs_live_under_docs(self):
        self.assertEqual(self.builder.OUTPUT, ROOT / "docs" / "UNIFIED_CATALOG.html")
        self.assertFalse((ROOT / "UNIFIED_CATALOG.html").exists())
        self.assertFalse((ROOT / "UNIFIED_CATALOG.md").exists())


if __name__ == "__main__":
    unittest.main()
