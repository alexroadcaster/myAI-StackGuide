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

    def strict_payload(self):
        payload = copy.deepcopy(self.payload)
        payload.setdefault("enrichment", {})["canonicalReconciliation"] = {"task": "CP-03.CAT-08"}
        for index, repository in enumerate(payload["repositories"], start=1):
            repository["githubRepositoryId"] = index
            repository["aliases"] = []
        return payload

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

    def test_all_migrated_placements_resolve(self):
        warnings = self.builder.integrity_warnings(self.payload)
        self.assertEqual(warnings["unresolvedPlacementCount"], 0)
        self.assertEqual(warnings["unresolvedPlacementRepositoryKeys"], [])

    def test_container_primary_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload['repositories'][0]['primaryCategory'] = 'frontend_frameworks_ui'
        with self.assertRaisesRegex(self.builder.CatalogContractError, 'navigation container'):
            self.builder.validate_payload(payload)

    def test_parent_union_drift_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        parent = next(c for c in payload['categories'] if c['kind'] == 'container')
        parent['descendantRepoIds'].pop()
        with self.assertRaisesRegex(self.builder.CatalogContractError, 'descendant union mismatch'):
            self.builder.validate_payload(payload)

    def test_membership_drift_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        category = next(c for c in payload['categories'] if c['repoIds'])
        category['repoIds'].pop()
        with self.assertRaisesRegex(self.builder.CatalogContractError, 'membership/declaration mismatch'):
            self.builder.validate_payload(payload)

    def test_unknown_use_case_category_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload['useCases'][0]['categories'].append('local_llm_inference_routing')
        with self.assertRaisesRegex(self.builder.CatalogContractError, 'use case references'):
            self.builder.validate_payload(payload)

    def test_duplicate_repository_identity_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["repositories"][1]["id"] = payload["repositories"][0]["id"]
        with self.assertRaisesRegex(self.builder.CatalogContractError, "duplicate repository ids"):
            self.builder.validate_payload(payload)

    def test_duplicate_numeric_github_identity_is_rejected(self):
        payload = self.strict_payload()
        payload["repositories"][1]["githubRepositoryId"] = payload["repositories"][0]["githubRepositoryId"]
        with self.assertRaisesRegex(self.builder.CatalogContractError, "duplicate GitHub repository ids"):
            self.builder.validate_payload(payload)

    def test_alias_collision_with_canonical_name_is_rejected(self):
        payload = self.strict_payload()
        payload["repositories"][0]["aliases"] = [payload["repositories"][1]["fullName"]]
        with self.assertRaisesRegex(self.builder.CatalogContractError, "alias collides"):
            self.builder.validate_payload(payload)

    def test_malformed_structured_stack_is_rejected(self):
        payload = self.strict_payload()
        payload["repositories"][0]["stack"] = [{"technology": "Python", "evidenceRefs": "metadata"}]
        with self.assertRaisesRegex(self.builder.CatalogContractError, "invalid structured stack"):
            self.builder.validate_payload(payload)

    def test_malformed_reviewed_presentation_wrapper_is_rejected(self):
        payload = self.strict_payload()
        payload["repositories"][0]["deployment"] = {"value": ["Docker"]}
        with self.assertRaisesRegex(self.builder.CatalogContractError, "value and rationale"):
            self.builder.presentation_projection(payload)

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
        actual = self.builder.OUTPUT.read_bytes().decode("utf-8")
        self.assertEqual(expected, actual)

    def test_generated_outputs_live_under_docs(self):
        self.assertEqual(self.builder.OUTPUT, ROOT / "docs" / "UNIFIED_CATALOG.html")
        self.assertFalse((ROOT / "UNIFIED_CATALOG.html").exists())
        self.assertFalse((ROOT / "UNIFIED_CATALOG.md").exists())


if __name__ == "__main__":
    unittest.main()
