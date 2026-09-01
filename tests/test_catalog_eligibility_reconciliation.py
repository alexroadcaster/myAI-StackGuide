"""Focused CAT-07 eligibility and taxonomy reconciliation checks."""
from __future__ import annotations

import sys
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import reconcile_catalog_eligibility as cat07


class CatalogEligibilityTests(unittest.TestCase):
    def record(self, **values):
        base = {
            "stars": 1000,
            "githubRepositoryId": 10,
            "fullName": "example/repo",
            "identityStatus": "resolved",
            "availability": "available",
            "catalogStatus": "candidate",
        }
        base.update(values)
        return {"values": base, "missingMandatory": []}

    def test_below_threshold_is_excluded_without_exception(self):
        result = cat07.classify_root(self.record(stars=499))
        self.assertEqual(result["disposition"], "excluded_below_star_threshold")
        self.assertFalse(result["eligible"])

    def test_unknown_stars_remain_pending(self):
        result = cat07.classify_root(self.record(stars=None))
        self.assertEqual(result["disposition"], "pending_unresolved_stars")

    def test_unresolved_recommendation_field_keeps_high_star_record(self):
        record = self.record()
        record["missingMandatory"] = ["recommendation.bestFor"]
        result = cat07.classify_root(record)
        self.assertEqual(result["disposition"], "catalog_included_recommendation_pending")
        self.assertTrue(result["eligible"])
        self.assertFalse(result["recommendationReady"])

    def test_numeric_overlay_can_resolve_identity_but_not_invent_review_fields(self):
        record = self.record(stars=None, githubRepositoryId=None, identityStatus=None, availability=None)
        record["missingMandatory"] = ["githubRepositoryId", "identityStatus", "stars", "stack", "reviewStatus"]
        resolution = {
            "status": "resolved_by_numeric_repository_id",
            "values": {
                "githubRepositoryId": 10,
                "fullName": "moved/repo",
                "url": "https://github.com/moved/repo",
                "identityStatus": "resolved",
                "availability": "available",
                "stars": 2000,
                "language": "Python",
            },
        }
        result = cat07.classify_root(record, resolution)
        self.assertEqual(result["disposition"], "catalog_included_recommendation_pending")
        self.assertTrue(result["eligible"])
        self.assertEqual(result["missingMandatory"], ["reviewStatus"])

    def test_container_count_is_distinct_union(self):
        taxonomy = {"categories": [
            {"id": "parent", "label": "Parent", "kind": "container", "parent_id": None},
            {"id": "a", "label": "A", "kind": "category", "parent_id": "parent"},
            {"id": "b", "label": "B", "kind": "category", "parent_id": "parent"},
            {"id": "empty", "label": "Empty", "kind": "category", "parent_id": None},
        ]}
        source = {"one": {"primaryCategory": "a", "secondaryCategories": ["b"]}}
        counts = cat07.category_counts(taxonomy, source, {"one"}, {})
        self.assertEqual(counts["containerDistinctUnions"]["parent"]["distinctRepositoryCount"], 1)
        self.assertIn("empty", counts["emptyThematicLeaves"])

    def test_request_log_audit_reports_unmatched_transport_start(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requests.jsonl"
            rows = [
                {"attempt": 1, "phase": "start"},
                {"attempt": 1, "phase": "finish"},
                {"attempt": 2, "phase": "start"},
            ]
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            audit = cat07.request_log_audit(path)
        self.assertEqual(audit["unmatchedAttempts"], [2])
        self.assertEqual(audit["duplicatePhaseAttempts"], 0)


if __name__ == "__main__":
    unittest.main()
