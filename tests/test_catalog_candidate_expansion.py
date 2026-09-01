"""Focused CP-03.CAT-07A expansion pipeline checks."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import expand_catalog_candidate as cat07a


class CatalogCandidateExpansionTests(unittest.TestCase):
    def taxonomy(self):
        return {
            "categories": [
                {
                    "id": "embeddings_reranking",
                    "label": "Embeddings & Reranking",
                    "kind": "category",
                    "parent_id": None,
                },
                {
                    "id": "testing_tools",
                    "label": "Testing Tools",
                    "kind": "category",
                    "parent_id": "testing",
                },
                {
                    "id": "testing",
                    "label": "Testing",
                    "kind": "container",
                    "parent_id": None,
                },
            ]
        }

    def manifest_categories(self):
        return [
            {
                "key": "embeddings_reranking",
                "title": "Embeddings & Reranking",
                "description": "Embedding models, semantic encoders, rerankers and retrieval scoring.",
                "kind": "category",
            },
            {
                "key": "testing_tools",
                "title": "Testing Tools",
                "description": "Software test runners and developer testing utilities.",
                "kind": "category",
            },
        ]

    def metadata(self, **overrides):
        row = {
            "id": 1001,
            "full_name": "example/embed-kit",
            "html_url": "https://github.com/example/embed-kit",
            "private": False,
            "visibility": "public",
            "archived": False,
            "disabled": False,
            "fork": False,
            "stargazers_count": 900,
            "forks_count": 30,
            "subscribers_count": 12,
            "size": 400,
            "default_branch": "main",
            "language": "Python",
            "description": "Embedding and reranking toolkit",
            "topics": ["embeddings", "reranking"],
            "homepage": "",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2026-08-31T00:00:00Z",
            "pushed_at": "2026-08-30T00:00:00Z",
            "license": {"spdx_id": "Apache-2.0", "name": "Apache License 2.0", "url": "https://api.github.com/licenses/apache-2.0"},
        }
        row.update(overrides)
        return row

    def observations(self):
        return {
            "metadata": {"status": "observed", "observedAt": "2026-09-01T00:00:00Z", "url": "https://api.github.com/repos/example/embed-kit"},
            "languages": {"status": "observed", "observedAt": "2026-09-01T00:00:01Z", "data": {"Python": 100}},
            "head_commit": {"status": "observed", "observedAt": "2026-09-01T00:00:02Z", "data": {"sha": "a" * 40, "date": "2026-08-30T00:00:00Z", "branch": "main"}},
            "release": {"status": "source_absent", "observedAt": "2026-09-01T00:00:03Z", "url": "https://api.github.com/repos/example/embed-kit/releases/latest"},
        }

    def test_query_map_covers_every_leaf_and_prioritizes_soft_floor(self):
        result = cat07a.build_query_map(
            self.taxonomy(), self.manifest_categories(),
            {"embeddings_reranking": 0, "testing_tools": 4},
            base_included=1624, target_included=2500,
        )
        self.assertEqual({r["categoryId"] for r in result["routes"]}, {"embeddings_reranking", "testing_tools"})
        self.assertEqual(result["routes"][0]["categoryId"], "embeddings_reranking")
        self.assertEqual(result["requiredAdditions"], 876)
        self.assertTrue(all(route["queries"] for route in result["routes"]))
        self.assertTrue(all(route["sourceMappings"] == ["github_rest_search"] for route in result["routes"]))
        self.assertTrue(all(query["perPage"] <= 30 and query["maxPages"] <= 3 for route in result["routes"] for query in route["queries"]))
        embedding_route = next(route for route in result["routes"] if route["categoryId"] == "embeddings_reranking")
        self.assertEqual(embedding_route["topicTerms"], ["embeddings", "reranking"])
        self.assertEqual(embedding_route["queries"][0]["routeType"], "category_topic")
        self.assertTrue(embedding_route["queries"][0]["metadataBound"])
        self.assertIn('"embeddings" in:name', embedding_route["queries"][0]["query"])
        self.assertNotIn("description", embedding_route["queries"][0]["query"])
        self.assertNotIn("readme", embedding_route["queries"][0]["query"])

    def test_zero_leaf_topic_seed_must_be_specific_and_source_owned(self):
        with self.assertRaisesRegex(ValueError, "Unsafe zero-leaf topic seed"):
            cat07a.build_query_map(
                self.taxonomy(), self.manifest_categories(),
                {"embeddings_reranking": 0, "testing_tools": 4}, 1624, 2500,
                zero_leaf_topic_seeds={"embeddings_reranking": ["ai"]},
            )

    def test_hard_gate_rejects_private_archived_low_star_and_duplicates(self):
        route = cat07a.build_query_map(
            self.taxonomy(), self.manifest_categories(),
            {"embeddings_reranking": 0, "testing_tools": 4}, 1624, 2500,
        )["routes"][0]
        registry = cat07a.IdentityRegistry(ids={1001}, names={"known/repo"}, aliases={"old/repo"})
        cases = [
            (self.metadata(id=1002, private=True), "not_public"),
            (self.metadata(id=1002, archived=True), "archived"),
            (self.metadata(id=1002, stargazers_count=499), "below_minimum_stars"),
            (self.metadata(), "duplicate_numeric_id"),
            (self.metadata(id=1002, full_name="KNOWN/REPO"), "duplicate_name_or_alias"),
            (self.metadata(id=1002, full_name="old/repo"), "duplicate_name_or_alias"),
        ]
        for metadata, reason in cases:
            with self.subTest(reason=reason):
                decision = cat07a.classify_metadata(metadata, route, registry)
                self.assertFalse(decision["eligible"])
                self.assertIn(reason, decision["reasons"])

    def test_metadata_without_route_evidence_requires_semantic_review(self):
        route = cat07a.build_query_map(
            self.taxonomy(), self.manifest_categories(),
            {"embeddings_reranking": 0, "testing_tools": 4}, 1624, 2500,
        )["routes"][0]
        decision = cat07a.classify_metadata(
            self.metadata(id=1002, full_name="example/unrelated", html_url="https://github.com/example/unrelated", description="A generic utility", topics=[]),
            route, cat07a.IdentityRegistry(),
        )
        self.assertFalse(decision["eligible"])
        self.assertEqual(decision["status"], "semantic_review_required")

    def test_semantically_bound_topic_passes_but_unrelated_single_term_does_not(self):
        route = cat07a.build_query_map(
            self.taxonomy(), self.manifest_categories(),
            {"embeddings_reranking": 0, "testing_tools": 4}, 1624, 2500,
        )["routes"][0]
        route["topicTerms"] = ["embeddings"]
        topic_only = self.metadata(
            id=1002, full_name="example/unrelated", html_url="https://github.com/example/unrelated",
            description="A generic utility", topics=["embeddings"],
        )
        self.assertTrue(cat07a.classify_metadata(topic_only, route, cat07a.IdentityRegistry())["eligible"])
        route["topicTerms"] = []
        self.assertFalse(cat07a.classify_metadata(topic_only, route, cat07a.IdentityRegistry())["eligible"])
        supported = self.metadata(
            id=1003, full_name="example/embedder", html_url="https://github.com/example/embedder",
            description="Semantic vector embeddings", topics=["embeddings"],
        )
        self.assertTrue(cat07a.classify_metadata(supported, route, cat07a.IdentityRegistry())["eligible"])

    def test_core_card_preserves_source_absent_release_without_inventing_date(self):
        route = cat07a.build_query_map(
            self.taxonomy(), self.manifest_categories(),
            {"embeddings_reranking": 0, "testing_tools": 4}, 1624, 2500,
        )["routes"][0]
        card = cat07a.build_core_card(
            self.metadata(), route, self.observations(),
            discovery_refs=["embeddings_reranking:q1:p1"],
        )
        self.assertEqual(card["primaryCategory"], "embeddings_reranking")
        self.assertIsNone(card["activity"]["lastReleaseAt"])
        self.assertEqual(card["fieldObservations"]["activity.lastReleaseAt"]["status"], "source_absent")
        self.assertEqual(card["recommendationStatus"], "downstream_backlog_not_inclusion_gate")
        self.assertTrue(card["coreFieldGatePassed"])

    def test_exact_target_moves_additional_qualified_cards_to_overflow(self):
        cards = [
            {"githubRepositoryId": 1, "fullName": "one/repo", "primaryCategory": "testing_tools", "coreFieldGatePassed": True},
            {"githubRepositoryId": 2, "fullName": "two/repo", "primaryCategory": "testing_tools", "coreFieldGatePassed": True},
        ]
        frozen = cat07a.freeze_exact_target(cards, base_included=2499, target_included=2500)
        self.assertEqual(len(frozen["acceptedAdditions"]), 1)
        self.assertEqual(len(frozen["qualifiedOverflow"]), 1)
        self.assertEqual(frozen["finalIncluded"], 2500)

    def test_expanded_counts_preserve_base_alias_category_placements(self):
        taxonomy = {
            "categories": [
                {"id": "embeddings_reranking", "label": "Embeddings", "kind": "category"},
                {"id": "testing_tools", "label": "Testing", "kind": "category"},
            ]
        }
        base_source = {
            "root": {"primaryCategory": "testing_tools", "secondaryCategories": []},
            "alias": {"primaryCategory": "embeddings_reranking", "secondaryCategories": []},
        }
        accepted = [{
            "sourceId": "gh-expansion:42", "primaryCategory": "testing_tools",
            "secondaryCategories": [],
        }]
        counts = cat07a.expanded_category_counts(
            taxonomy, base_source, {"root"}, {"alias": "root"}, accepted,
        )
        self.assertEqual(
            counts["thematicLeafCounts"]["embeddings_reranking"]["repositorySourceIds"],
            ["root"],
        )
        self.assertEqual(counts["thematicLeafCounts"]["testing_tools"]["repositoryCount"], 2)

    def test_freeze_uses_coverage_then_category_balanced_round_robin(self):
        cards = [
            {"githubRepositoryId": 1, "fullName": "a/one", "primaryCategory": "testing_tools", "coreFieldGatePassed": True, "selectionKey": [1, 1, 1, 1]},
            {"githubRepositoryId": 2, "fullName": "a/two", "primaryCategory": "testing_tools", "coreFieldGatePassed": True, "selectionKey": [1, 1, 2, 2]},
            {"githubRepositoryId": 3, "fullName": "b/one", "primaryCategory": "embeddings_reranking", "coreFieldGatePassed": True, "selectionKey": [0, 1, 1, 3]},
            {"githubRepositoryId": 4, "fullName": "b/two", "primaryCategory": "embeddings_reranking", "coreFieldGatePassed": True, "selectionKey": [0, 1, 2, 4]},
            {"githubRepositoryId": 5, "fullName": "c/one", "primaryCategory": "full_leaf", "coreFieldGatePassed": True, "selectionKey": [2, 1, 1, 5]},
        ]
        frozen = cat07a.freeze_exact_target(
            cards, base_included=2497, target_included=2500,
            base_leaf_counts={"embeddings_reranking": 9, "testing_tools": 9, "full_leaf": 20},
        )
        selected = [card["githubRepositoryId"] for card in frozen["acceptedAdditions"]]
        self.assertEqual(selected[:2], [3, 1])
        self.assertEqual(selected[2], 4)

    def test_exact_target_rejects_duplicate_candidate_identity(self):
        cards = [
            {"githubRepositoryId": 1, "fullName": "one/repo", "primaryCategory": "testing_tools", "coreFieldGatePassed": True},
            {"githubRepositoryId": 1, "fullName": "renamed/repo", "primaryCategory": "testing_tools", "coreFieldGatePassed": True},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate numeric"):
            cat07a.freeze_exact_target(cards, base_included=2498, target_included=2500)


if __name__ == "__main__":
    unittest.main()
