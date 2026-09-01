import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import apply_catalog_candidate as application
import build_catalog_html as html_builder


class CatalogCandidateApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if application.sha(application.MANIFEST) == application.INPUTS["manifest"][1]:
            cls.payload, cls.report = application.build_candidate()
        else:
            cls.payload = html_builder.load_manifest()
            reconciliation = cls.payload["enrichment"]["canonicalReconciliation"]
            cls.report = {
                "additionCount": reconciliation["acceptedAdditions"],
                "overflowReserved": reconciliation["qualifiedOverflowReserved"],
                "reviewDecisions": cls.payload["taxonomyMigration"]["cat08ReviewDecisions"],
                "canonicalArchivedBaselineRepositories": sum(
                    item.get("archived") is True for item in cls.payload["repositories"][:1624]
                ),
                "templateBehaviorChange": "search_description_fallback_and_aliases",
                "sourceVisualCssLayoutChanged": False,
                "browserVerified": False,
            }
        cls.by_id = {item["id"]: item for item in cls.payload["repositories"]}
        cls.projection = html_builder.presentation_projection(cls.payload)
        cls.projected_by_id = {item["id"]: item for item in cls.projection["repositories"]}

    def test_exact_frozen_membership_and_taxonomy_counts(self):
        summary = self.payload["summary"]
        self.assertEqual(2500, summary["canonicalRepositories"])
        self.assertEqual(126, summary["categories"])
        self.assertEqual(111, summary["thematicCategories"])
        self.assertEqual(14, summary["navigationContainers"])
        self.assertEqual(876, self.report["additionCount"])
        self.assertEqual(7, self.report["overflowReserved"])

    def test_review_and_placement_reconciliation(self):
        summary = self.payload["summary"]
        self.assertEqual(12, summary["reviewRepositories"])
        self.assertEqual(2488, summary["thematicRepositories"])
        self.assertEqual(2618, summary["thematicPlacements"])
        self.assertEqual(2630, summary["placements"])
        self.assertEqual(application.REVIEW_SOURCE_IDS, {
            item["sourceId"] for item in self.report["reviewDecisions"]
        })

    def test_alias_assignments_are_folded_into_canonical_identity(self):
        mindsdb = self.by_id["gh-pending:mindsdb/minds-platform"]
        self.assertEqual("rag_knowledge_apps", mindsdb["primaryCategory"])
        self.assertNotIn("uncategorized_review", mindsdb.get("secondaryCategories", []))
        self.assertIn("gh-1500:mindsdb/mindsdb", mindsdb["sourceRecordIds"])
        self.assertEqual("mindsdb/mindshub", mindsdb["fullName"].casefold())
        self.assertIn("mindsdb/minds-platform", [item.casefold() for item in mindsdb["aliases"]])
        self.assertIn("mindsdb/mindsdb", [item.casefold() for item in mindsdb["aliases"]])

    def test_structured_stack_and_audit_evidence_remain_source_owned(self):
        source = self.by_id["gh-expansion:704543233"]
        projected = self.projected_by_id[source["id"]]
        self.assertIsInstance(source["stack"][0], dict)
        self.assertEqual(["Rust"], projected["stack"])
        self.assertIn("fieldObservations", source)
        self.assertNotIn("fieldObservations", projected)
        self.assertNotIn("eligibility", projected)

    def test_description_fallback_keeps_audit_identity_source_only(self):
        source = self.by_id["gh-expansion:704543233"]
        projected = self.projected_by_id[source["id"]]
        self.assertNotIn("description", source)
        self.assertEqual(source["catalogDescription"], projected["description"])
        self.assertIn("githubRepositoryId", source)
        self.assertIn("provenance", source)
        self.assertIn("classification", source)
        self.assertNotIn("githubRepositoryId", projected)
        self.assertNotIn("provenance", projected)
        self.assertNotIn("classification", projected)

    def test_projection_omits_unused_top_level_audit_data(self):
        self.assertNotIn("taxonomyMigration", self.projection)
        self.assertNotIn("catalogEligibilityPolicy", self.projection)
        self.assertNotIn("canonicalReconciliation", self.projection["enrichment"])
        html = html_builder.page(self.payload)
        self.assertNotIn("cat08ReviewDecisions", html)
        self.assertNotIn(".codex-tmp/catalog-refresh", html)

    def test_template_design_source_is_unchanged(self):
        observed = hashlib.sha256(application.TEMPLATE.read_bytes()).hexdigest()
        self.assertEqual(application.INPUTS["template"][1], observed)
        self.assertEqual("search_description_fallback_and_aliases", self.report["templateBehaviorChange"])
        self.assertFalse(self.report["sourceVisualCssLayoutChanged"])
        self.assertFalse(self.report["browserVerified"])

    def test_overflow_cards_are_not_canonical_members(self):
        expansion_path = application.INPUTS["expansionCandidate"][0]
        if not expansion_path.exists():
            self.assertEqual(7, self.report["overflowReserved"])
            return
        expansion = json.loads(expansion_path.read_text(encoding="utf-8"))
        canonical_ids = set(self.by_id)
        self.assertTrue({item["id"] for item in expansion["qualifiedOverflow"]}.isdisjoint(canonical_ids))

    def test_archived_state_is_preserved_not_hidden(self):
        canonical = sum(item.get("archived") is True for item in self.payload["repositories"][:1624])
        self.assertEqual(19, canonical)
        self.assertEqual(19, self.report["canonicalArchivedBaselineRepositories"])
        self.assertFalse(any(item.get("archived") is True for item in self.payload["repositories"][1624:]))

    def test_review_moves_respect_functional_leaf_scope(self):
        self.assertEqual("agent_runtime_orchestration", self.by_id["gh:deepseek-ai/deepseek-harness"]["primaryCategory"])
        self.assertEqual("rag_knowledge_apps", self.by_id["gh:hkuds/deeptutor"]["primaryCategory"])
        self.assertEqual("learning_reference_resources", self.by_id["gh:liyupi/yu-ai-agent"]["primaryCategory"])
        self.assertEqual("uncategorized_review", self.by_id["gh:homeassistant-ai/ha-mcp"]["primaryCategory"])
        self.assertEqual("uncategorized_review", self.by_id["gh-1700:joooook/12306-mcp"]["primaryCategory"])

    def test_addition_legacy_fields_are_explicit_unknowns(self):
        addition = self.by_id["gh-expansion:704543233"]
        self.assertEqual("unknown", addition["form"])
        self.assertEqual(["unknown"], addition["deployment"])
        self.assertEqual("unknown", addition["hosting"])
        self.assertEqual("unknown", addition["difficulty"])
        self.assertEqual("unknown", addition["activity"]["activityBand"])

    def test_presentation_field_order_is_deterministic(self):
        self.assertIsInstance(html_builder.PRESENTATION_REPOSITORY_FIELDS, tuple)
        expected_order = [
            field
            for field in html_builder.PRESENTATION_REPOSITORY_FIELDS
            if field in self.payload["repositories"][0]
        ]
        self.assertEqual(expected_order, list(self.projection["repositories"][0]))

    def test_candidate_hashes_are_stable_across_python_hash_seeds(self):
        command = (
            "import hashlib,sys;sys.path.insert(0,'scripts');"
            "import build_catalog_html as b;"
            "p=b.load_manifest();"
            "print(hashlib.sha256(b.canonical_json(p).encode()).hexdigest()+' '+hashlib.sha256(b.page(p).encode()).hexdigest())"
        )
        outputs = []
        for seed in ("1", "2"):
            environment = {**os.environ, "PYTHONHASHSEED": seed}
            completed = subprocess.run(
                [sys.executable, "-B", "-c", command],
                cwd=ROOT,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            outputs.append(completed.stdout.strip())
        self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main()
