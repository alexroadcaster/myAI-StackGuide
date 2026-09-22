import copy
import hashlib
import importlib.util
import inspect
import json
import shutil
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "plugins" / "myai-stackguide" / "scripts"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "plugin_contracts.json"
ASSET_DIR = ROOT / "plugins" / "myai-stackguide" / "assets"
INDEX_PATH = ASSET_DIR / "catalog.search.sqlite"
MANIFEST_PATH = ASSET_DIR / "catalog.search-manifest.json"
POLICY_PATH = ASSET_DIR / "retrieval-policy.json"
SNAPSHOT_PATH = ASSET_DIR / "catalog.snapshot.json"


def load_runtime_module(name):
    path = SCRIPT_DIR / f"{name}.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(f"stackguide_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha256(value):
    payload = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def base_query():
    query = copy.deepcopy(
        json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["positive"][
            "retrieval/catalog-query.schema.json"
        ]
    )
    query["taxonomy_route_id"] = None
    query["constraints"] = {
        "languages": [],
        "deployment": [],
        "allowed_licenses": [],
        "compatibility": [],
        "require_no_server": None,
        "mandatory_fields": [],
    }
    return query


def execute_query(runtime, query, **overrides):
    return runtime.retrieve(
        query,
        run_id=overrides.get("run_id", str(uuid.uuid4())),
        index_path=overrides.get("index_path", INDEX_PATH),
        manifest_path=overrides.get("manifest_path", MANIFEST_PATH),
        policy_path=overrides.get("policy_path", POLICY_PATH),
    )


class RetrievalRuntimeContractTests(unittest.TestCase):
    module_path = SCRIPT_DIR / "retrieval.py"

    def test_planned_retrieval_module_exists(self):
        self.assertTrue(
            self.module_path.is_file(),
            "CP-09 expected RED: missing plugins/myai-stackguide/scripts/retrieval.py",
        )

    @unittest.skipUnless(module_path.is_file(), "planned retrieval runtime is absent")
    def test_public_api_and_query_canonicalization(self):
        runtime = load_runtime_module("retrieval")
        expected = {
            "validate_query": ["query", "manifest", "policy"],
            "canonical_query_sha256": ["query"],
            "compile_fts5_query": ["terms", "aliases"],
            "retrieve": [
                "query",
                "run_id",
                "index_path",
                "manifest_path",
                "policy_path",
            ],
        }
        for name, parameters in expected.items():
            with self.subTest(name=name):
                self.assertTrue(callable(getattr(runtime, name, None)))
                self.assertEqual(
                    list(inspect.signature(getattr(runtime, name)).parameters),
                    parameters,
                )

        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        query = fixture["positive"]["retrieval/catalog-query.schema.json"]
        self.assertEqual(runtime.canonical_query_sha256(query), canonical_sha256(query))
        scoped = copy.deepcopy(query)
        scoped["taxonomy_route_id"] = "coding_agents_devex"
        self.assertNotEqual(
            runtime.canonical_query_sha256(scoped),
            runtime.canonical_query_sha256(query),
        )
        run_id = fixture["positive"]["retrieval/retrieval-result.schema.json"]["run_id"]
        result = runtime.retrieve(
            query,
            run_id=run_id,
            index_path=ROOT / "plugins/myai-stackguide/assets/catalog.search.sqlite",
            manifest_path=ROOT
            / "plugins/myai-stackguide/assets/catalog.search-manifest.json",
            policy_path=ROOT / "plugins/myai-stackguide/assets/retrieval-policy.json",
        )
        self.assertEqual(result["run_id"], run_id)

    @unittest.skipUnless(module_path.is_file(), "planned retrieval runtime is absent")
    def test_validation_and_literal_alias_compilation_fail_closed(self):
        runtime = load_runtime_module("retrieval")
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        query = copy.deepcopy(fixture["positive"]["retrieval/catalog-query.schema.json"])
        manifest = fixture["positive"]["retrieval/index-manifest.schema.json"]
        policy = json.loads(
            (ROOT / "plugins/myai-stackguide/assets/retrieval-policy.json").read_text(
                encoding="utf-8"
            )
        )

        for mutation in (
            lambda value: value.pop("taxonomy_route_id"),
            lambda value: value.update(schema_version="2.0.0"),
            lambda value: value.update(index_format_version=2),
            lambda value: value.update(taxonomy_route_id="not-a-canonical-route"),
        ):
            bad = copy.deepcopy(query)
            mutation(bad)
            with self.subTest(query=bad), self.assertRaises(ValueError):
                runtime.validate_query(bad, manifest=manifest, policy=policy)

        aliases = policy["aliases"]
        self.assertEqual(
            runtime.compile_fts5_query(
                ["c++", ".net", "full-text search"], aliases=aliases
            ),
            '"cplusplus" OR "dotnet" OR "fulltext"',
        )
        self.assertEqual(
            runtime.compile_fts5_query(['x" OR *'], aliases=aliases),
            '"x"" OR *"',
        )

    @unittest.skipUnless(module_path.is_file(), "planned retrieval runtime is absent")
    def test_retrieve_rejects_non_uuid_run_id_before_returning_a_result(self):
        runtime = load_runtime_module("retrieval")
        query = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["positive"][
            "retrieval/catalog-query.schema.json"
        ]
        with self.assertRaises(ValueError):
            runtime.retrieve(
                query,
                run_id="not-a-uuid",
                index_path=ROOT / "plugins/myai-stackguide/assets/catalog.search.sqlite",
                manifest_path=ROOT
                / "plugins/myai-stackguide/assets/catalog.search-manifest.json",
                policy_path=ROOT / "plugins/myai-stackguide/assets/retrieval-policy.json",
            )


class RetrievalAcceptanceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load_runtime_module("retrieval")
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        cls.cards_by_id = {
            card["identity"]["github_repository_id"]: card
            for card in cls.snapshot["cards"]
        }
        cls.taxonomy = json.loads(
            (ROOT / "data" / "catalog_manifest.json").read_text(encoding="utf-8")
        )["categories"]

    def test_all_126_routes_match_only_source_owned_memberships(self):
        categories = {item["key"]: item for item in self.taxonomy}

        def descends_from(category_id, container_id):
            parent_id = categories[category_id]["parentId"]
            while parent_id is not None:
                if parent_id == container_id:
                    return True
                parent_id = categories[parent_id]["parentId"]
            return False

        expected_route_members = {}
        for route_id, category in categories.items():
            if category["kind"] == "container":
                expected_route_members[route_id] = {
                    candidate_id
                    for candidate_id, candidate in categories.items()
                    if candidate["kind"] != "container"
                    and descends_from(candidate_id, route_id)
                }
            else:
                expected_route_members[route_id] = {route_id}

        connection = sqlite3.connect(INDEX_PATH.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
        try:
            registry_rows = connection.execute(
                "SELECT route_id, route_kind, match_category_id, match_category_kind "
                "FROM taxonomy_route_registry ORDER BY route_id, match_category_id"
            ).fetchall()
        finally:
            connection.close()
        actual_route_members = {}
        actual_kinds = {}
        for route_id, route_kind, member_id, member_kind in registry_rows:
            actual_route_members.setdefault(route_id, set()).add(member_id)
            actual_kinds[route_id] = route_kind
            self.assertEqual(member_kind, categories[member_id]["kind"])

        self.assertEqual(len(actual_route_members), 126)
        self.assertEqual(len(registry_rows), 162)
        self.assertEqual(
            {kind: sum(value == kind for value in actual_kinds.values()) for kind in set(actual_kinds.values())},
            {"category": 111, "container": 14, "review_bucket": 1},
        )
        self.assertEqual(actual_route_members, expected_route_members)

        classifications = {
            repository_id: {item["category_id"] for item in card["classifications"]}
            for repository_id, card in self.cards_by_id.items()
        }
        expected_ids_by_route = {
            route_id: {
                repository_id
                for repository_id, assigned in classifications.items()
                if assigned & member_ids
            }
            for route_id, member_ids in expected_route_members.items()
        }
        for route_id in sorted(expected_ids_by_route):
            expected_ids = expected_ids_by_route[route_id]
            self.assertTrue(expected_ids, route_id)
            selected_id = min(expected_ids)
            query = base_query()
            query["taxonomy_route_id"] = route_id
            query["variants"] = [{
                "variant_id": "q1",
                "terms": [self.cards_by_id[selected_id]["identity"]["full_name"]],
            }]
            query["max_candidates"] = 12
            result = execute_query(self.runtime, query)
            with self.subTest(route_id=route_id, kind=actual_kinds[route_id]):
                self.assertEqual(result["status"], "ok")
                result_ids = [item["github_repository_id"] for item in result["candidates"]]
                self.assertIn(selected_id, result_ids)
                self.assertEqual(len(result_ids), len(set(result_ids)))
                self.assertTrue(all(isinstance(item, int) and item > 0 for item in result_ids))
                self.assertTrue(set(result_ids) <= expected_ids)

    def test_secondary_assignment_and_container_overlap_dedupe_by_numeric_id(self):
        secondary = next(
            (card, item)
            for card in self.snapshot["cards"]
            for item in card["classifications"]
            if item["role"] == "secondary"
        )
        card, assignment = secondary
        repository_id = card["identity"]["github_repository_id"]
        query = base_query()
        query["taxonomy_route_id"] = assignment["category_id"]
        query["variants"] = [{"variant_id": "q1", "terms": [card["identity"]["full_name"]]}]
        result = execute_query(self.runtime, query)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            [item["github_repository_id"] for item in result["candidates"]].count(repository_id),
            1,
        )

        parents = {
            item["key"]: item["parentId"] for item in self.taxonomy
        }
        container_id = parents[assignment["category_id"]]
        if container_id is not None:
            query["taxonomy_route_id"] = container_id
            container_result = execute_query(self.runtime, query)
            self.assertEqual(
                [item["github_repository_id"] for item in container_result["candidates"]].count(repository_id),
                1,
            )

    def test_absent_but_syntactically_valid_route_has_no_unscoped_fallback(self):
        query = base_query()
        query["taxonomy_route_id"] = "absent_but_valid_route"
        result = execute_query(self.runtime, query)
        self.assertEqual(result["status"], "invalid_query")
        self.assertEqual(result["executed_variants"], 0)
        self.assertEqual(result["retrieved_hits"], 0)
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["reason_codes"], ["invalid_query"])

    def test_rrf_k60_bm25_variant_order_ties_and_allocation(self):
        for terms, cap, expected_counts in (
            (["open source"], 9, [9]),
            (["open source", "open source"], 9, [5, 4]),
            (["spree/spree", "open source", "open source"], 7, [1, 3, 3]),
        ):
            query = base_query()
            query["variants"] = [
                {"variant_id": f"q{index}", "terms": [term]}
                for index, term in enumerate(terms, start=1)
            ]
            query["max_candidates"] = cap
            result = execute_query(self.runtime, query)
            counts = {item["variant_id"]: 0 for item in query["variants"]}
            for candidate in result["candidates"]:
                expected_score = 0.0
                for variant_rank in candidate["variant_ranks"]:
                    counts[variant_rank["variant_id"]] += 1
                    expected_score += 1.0 / (60 + variant_rank["rank"])
                self.assertAlmostEqual(candidate["rrf_score"], expected_score, places=15)
            with self.subTest(variants=len(terms), cap=cap):
                self.assertEqual(result["retrieved_hits"], cap)
                self.assertEqual(list(counts.values()), expected_counts)
                if len(terms) > 1 and len(set(terms)) < len(terms):
                    self.assertLess(len(result["candidates"]), result["retrieved_hits"])
                    self.assertTrue(
                        any(len(item["variant_ranks"]) > 1 for item in result["candidates"])
                    )

            for variant_id in counts:
                ranks = sorted(
                    (
                        rank["rank"],
                        rank["bm25"],
                        candidate["github_repository_id"],
                    )
                    for candidate in result["candidates"]
                    for rank in candidate["variant_ranks"]
                    if rank["variant_id"] == variant_id
                )
                self.assertEqual([item[0] for item in ranks], list(range(1, len(ranks) + 1)))
                self.assertEqual(
                    [(item[1], item[2]) for item in ranks],
                    sorted((item[1], item[2]) for item in ranks),
                )

        query = base_query()
        query["variants"] = [
            {"variant_id": "q1", "terms": ["spree/spree"]},
            {"variant_id": "q2", "terms": ["bitcoin/bitcoin"]},
        ]
        query["max_candidates"] = 2
        tied = execute_query(self.runtime, query)
        self.assertEqual(tied["retrieved_hits"], 2)
        self.assertEqual(len(tied["candidates"]), 2)
        self.assertEqual(
            [item["github_repository_id"] for item in tied["candidates"]],
            sorted(item["github_repository_id"] for item in tied["candidates"]),
        )
        self.assertAlmostEqual(tied["candidates"][0]["rrf_score"], 1.0 / 61)
        self.assertEqual(
            tied["candidates"][0]["rrf_score"], tied["candidates"][1]["rrf_score"]
        )

        query = base_query()
        query["variants"] = [
            {"variant_id": f"q{index}", "terms": ["open source"]}
            for index in range(1, 4)
        ]
        query["max_candidates"] = 150
        capped = execute_query(self.runtime, query)
        self.assertEqual(capped["retrieved_hits"], 150)
        self.assertLessEqual(capped["retrieved_hits"], 150)
        self.assertLessEqual(len(capped["candidates"]), 150)

    def test_matched_fields_keep_name_alias_and_descriptions_separate(self):
        cases = (
            ("spree/spree", 3314, ["full_name"]),
            ("alist-org/alist", 323965659, ["full_name_aliases"]),
            ("headless ecommerce platform", 3314, ["upstream_description"]),
            ("document based question answering", 691347156, ["catalog_description"]),
        )
        for term, repository_id, expected_fields in cases:
            query = base_query()
            query["variants"] = [{"variant_id": "q1", "terms": [term]}]
            query["max_candidates"] = 10
            result = execute_query(self.runtime, query)
            candidate = next(
                item for item in result["candidates"]
                if item["github_repository_id"] == repository_id
            )
            with self.subTest(term=term):
                self.assertEqual(candidate["matched_fields"], expected_fields)

    def test_runtime_failure_classes_are_explicit_and_entrypoint_is_read_only(self):
        query = base_query()
        original_hashes = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (INDEX_PATH, MANIFEST_PATH, POLICY_PATH)
        }
        original_names = {path.name for path in ASSET_DIR.iterdir()}
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            missing = execute_query(
                self.runtime, query, index_path=directory / "missing.sqlite"
            )
            self.assertEqual((missing["status"], missing["reason_codes"]),
                             ("retrieval_unavailable", ["index_missing"]))

            bad_manifest = directory / "bad-manifest.json"
            bad_manifest.write_text("{", encoding="utf-8")
            corrupt_manifest = execute_query(
                self.runtime, query, manifest_path=bad_manifest
            )
            self.assertEqual(corrupt_manifest["reason_codes"], ["index_corrupt"])

            incompatible_manifest = directory / "incompatible-manifest.json"
            changed_manifest = copy.deepcopy(self.manifest)
            changed_manifest["builder_version"] = "9.9.9"
            incompatible_manifest.write_text(json.dumps(changed_manifest), encoding="utf-8")
            incompatible = execute_query(
                self.runtime, query, manifest_path=incompatible_manifest
            )
            self.assertEqual((incompatible["status"], incompatible["reason_codes"]),
                             ("index_incompatible", ["index_incompatible"]))

            bad_policy = directory / "bad-policy.json"
            bad_policy.write_text("[]", encoding="utf-8")
            corrupt_policy = execute_query(self.runtime, query, policy_path=bad_policy)
            self.assertEqual(corrupt_policy["reason_codes"], ["index_corrupt"])

            incompatible_policy = directory / "incompatible-policy.json"
            changed_policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
            changed_policy["calibration_status"] = "tampered"
            incompatible_policy.write_text(json.dumps(changed_policy), encoding="utf-8")
            policy_result = execute_query(
                self.runtime, query, policy_path=incompatible_policy
            )
            self.assertEqual(policy_result["reason_codes"], ["index_incompatible"])

            corrupt_index = directory / "corrupt.sqlite"
            raw_index = INDEX_PATH.read_bytes()
            corrupt_index.write_bytes(raw_index[:4096])
            corrupt_result = execute_query(self.runtime, query, index_path=corrupt_index)
            self.assertEqual(corrupt_result["reason_codes"], ["index_corrupt"])

            incompatible_index = directory / "incompatible.sqlite"
            shutil.copyfile(INDEX_PATH, incompatible_index)
            connection = sqlite3.connect(incompatible_index)
            try:
                connection.execute("PRAGMA user_version = 999")
                connection.commit()
            finally:
                connection.close()
            incompatible_result = execute_query(
                self.runtime, query, index_path=incompatible_index
            )
            self.assertEqual(incompatible_result["reason_codes"], ["index_incompatible"])
            self.assertFalse(any(path.name.endswith(("-wal", "-shm", "-journal"))
                                 for path in directory.iterdir()))

        self.assertEqual(original_names, {path.name for path in ASSET_DIR.iterdir()})
        self.assertEqual(
            original_hashes,
            {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (INDEX_PATH, MANIFEST_PATH, POLICY_PATH)
            },
        )


class ContextPackRuntimeContractTests(unittest.TestCase):
    module_path = SCRIPT_DIR / "context_pack.py"

    def test_planned_context_pack_module_exists(self):
        self.assertTrue(
            self.module_path.is_file(),
            "CP-09 expected RED: missing plugins/myai-stackguide/scripts/context_pack.py",
        )

    @unittest.skipUnless(module_path.is_file(), "planned context-pack runtime is absent")
    def test_public_api_and_budget_arguments(self):
        runtime = load_runtime_module("context_pack")
        function = getattr(runtime, "build_evidence_pack", None)
        self.assertTrue(callable(function))
        self.assertEqual(
            list(inspect.signature(function).parameters),
            [
                "query",
                "retrieval_result",
                "cards_by_id",
                "pack_id",
                "max_cards",
                "max_evidence_bytes",
            ],
        )

        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["positive"]
        query = fixture["retrieval/catalog-query.schema.json"]
        result = fixture["retrieval/retrieval-result.schema.json"]
        expected_pack = fixture["retrieval/evidence-pack.schema.json"]
        cards = {
            item["card"]["identity"]["github_repository_id"]: item["card"]
            for item in expected_pack["cards"]
        }
        pack = function(
            query,
            result,
            cards,
            pack_id=expected_pack["pack_id"],
            max_cards=12,
            max_evidence_bytes=163840,
        )
        self.assertEqual(pack["pack_id"], expected_pack["pack_id"])
        self.assertEqual(pack["run_id"], result["run_id"])
        self.assertLessEqual(len(pack["cards"]), 12)
        self.assertEqual(pack["query_sha256"], canonical_sha256(query))
        self.assertIn("exclusions", pack)
        self.assertEqual(pack["cards"][0]["eligibility"]["status"], "primary_eligible")
        self.assertLessEqual(
            len(
                json.dumps(
                    pack,
                    ensure_ascii=False,
                    allow_nan=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ),
            163840,
        )

    @unittest.skipUnless(module_path.is_file(), "planned context-pack runtime is absent")
    def test_rejects_tampered_supplied_card_instead_of_trusting_numeric_id(self):
        runtime = load_runtime_module("context_pack")
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["positive"]
        query = fixture["retrieval/catalog-query.schema.json"]
        result = fixture["retrieval/retrieval-result.schema.json"]
        expected_pack = fixture["retrieval/evidence-pack.schema.json"]
        cards = {
            item["card"]["identity"]["github_repository_id"]: copy.deepcopy(item["card"])
            for item in expected_pack["cards"]
        }
        first_card = next(iter(cards.values()))
        first_card["descriptions"]["catalog"] = "tampered-untrusted-card"

        with self.assertRaises(ValueError):
            runtime.build_evidence_pack(
                query,
                result,
                cards,
                pack_id=expected_pack["pack_id"],
                max_cards=12,
                max_evidence_bytes=163840,
            )


class ContextPackAcceptanceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load_runtime_module("context_pack")
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        cls.cards_by_id = {
            card["identity"]["github_repository_id"]: card
            for card in cls.snapshot["cards"]
        }

    def result_for(self, query, repository_ids):
        return {
            "schema_version": "2.1.0",
            "run_id": str(uuid.uuid4()),
            "query_id": query["query_id"],
            "query_sha256": canonical_sha256(query),
            "brief_version": query["brief_version"],
            "source_mode": "catalog_only",
            "retrieval_engine": "sqlite_fts5",
            "pins": copy.deepcopy(self.manifest["pins"]),
            "status": "ok",
            "executed_variants": 1,
            "retrieved_hits": len(repository_ids),
            "candidates": [
                {
                    "github_repository_id": repository_id,
                    "rank": rank,
                    "rrf_score": 1.0 / (60 + rank),
                    "variant_ranks": [
                        {"variant_id": "q1", "rank": rank, "bm25": -1.0}
                    ],
                    "matched_fields": ["full_name"],
                    "missing_facts": [],
                }
                for rank, repository_id in enumerate(repository_ids, start=1)
            ],
            "truncated": False,
            "reason_codes": [],
        }

    def test_every_unique_candidate_is_packed_or_excluded_once(self):
        query = base_query()
        statuses = {
            repository_id: self.runtime.matcher.match_candidate(card, query)["status"]
            for repository_id, card in self.cards_by_id.items()
        }
        reference_ids = [
            repository_id for repository_id, status in statuses.items()
            if status == "reference_only"
        ][:4]
        blocked_id = next(
            repository_id for repository_id, status in statuses.items()
            if status == "blocked"
        )
        candidate_ids = [reference_ids[0], blocked_id, *reference_ids[1:]]
        result = self.result_for(query, candidate_ids)
        pack = self.runtime.build_evidence_pack(
            query,
            result,
            {repository_id: self.cards_by_id[repository_id] for repository_id in set(candidate_ids)},
            pack_id="pack-accounting",
            max_cards=2,
            max_evidence_bytes=163840,
        )
        packed_ids = {
            item["card"]["identity"]["github_repository_id"] for item in pack["cards"]
        }
        excluded_ids = {item["github_repository_id"] for item in pack["exclusions"]}
        self.assertFalse(packed_ids & excluded_ids)
        self.assertEqual(packed_ids | excluded_ids, set(candidate_ids))
        self.assertEqual(len(pack["cards"]), 2)
        self.assertTrue(
            all(item["eligibility"]["status"] == "reference_only" for item in pack["cards"])
        )
        self.assertEqual(len(pack["exclusions"]), len(candidate_ids) - 2)
        blocked = next(
            item for item in pack["exclusions"]
            if item["github_repository_id"] == blocked_id
        )
        self.assertTrue(set(blocked["reason_codes"]) & {"archived", "unavailable"})
        self.assertTrue(
            any("candidate_budget" in item["reason_codes"] for item in pack["exclusions"])
        )

    def test_duplicate_identity_is_excluded_once_not_packed(self):
        query = base_query()
        repository_id = 3314
        result = self.result_for(query, [repository_id, repository_id])
        pack = self.runtime.build_evidence_pack(
            query,
            result,
            {repository_id: self.cards_by_id[repository_id]},
            pack_id="pack-duplicate",
            max_cards=12,
            max_evidence_bytes=163840,
        )
        self.assertEqual(pack["cards"], [])
        self.assertEqual(pack["exclusions"], [{
            "github_repository_id": repository_id,
            "reason_codes": ["duplicate_identity"],
        }])

    def test_rejects_retrieval_result_with_forged_manifest_pins(self):
        query = base_query()
        repository_id = 3314
        cards = {repository_id: self.cards_by_id[repository_id]}
        for pin_name in ("index_sha256", "cards_sha256", "taxonomy_sha256"):
            result = self.result_for(query, [repository_id])
            result["pins"][pin_name] = "0" * 64
            with self.subTest(pin_name=pin_name), self.assertRaises(ValueError):
                self.runtime.build_evidence_pack(
                    query,
                    result,
                    cards,
                    pack_id=f"pack-forged-{pin_name}",
                    max_cards=12,
                    max_evidence_bytes=163840,
                )

    def test_small_byte_budget_uses_exact_compact_utf8_and_combined_cap(self):
        query = base_query()
        query["language"] = "ru"
        query["variants"] = [{"variant_id": "q1", "terms": ["локальный поиск"]}]
        repository_id = 3314
        result = self.result_for(query, [repository_id])
        cards = {repository_id: self.cards_by_id[repository_id]}
        pack = self.runtime.build_evidence_pack(
            query,
            result,
            cards,
            pack_id="pack-small-utf8",
            max_cards=12,
            max_evidence_bytes=2048,
        )
        serialized = canonical_bytes(pack)
        query_serialized = canonical_bytes(query)
        self.assertGreater(len(query_serialized), len(query_serialized.decode("utf-8")))
        self.assertLessEqual(len(serialized), 2048)
        self.assertLessEqual(len(query_serialized) + len(serialized), 204800)
        self.assertEqual(
            {item["github_repository_id"] for item in pack["exclusions"]},
            {repository_id},
        )
        self.assertIn("context_budget", pack["reason_codes"])

    def test_card_and_evidence_caps_use_lower_request_selected_limits(self):
        query = base_query()
        query["max_cards"] = 3
        query["max_evidence_bytes"] = 120000
        repository_ids = list(self.cards_by_id)[:8]
        result = self.result_for(query, repository_ids)
        pack = self.runtime.build_evidence_pack(
            query,
            result,
            {repository_id: self.cards_by_id[repository_id] for repository_id in repository_ids},
            pack_id="pack-lower-caps",
            max_cards=2,
            max_evidence_bytes=100000,
        )
        self.assertLessEqual(len(pack["cards"]), 2)
        self.assertLessEqual(len(canonical_bytes(pack)), 100000)
        covered = {
            item["card"]["identity"]["github_repository_id"] for item in pack["cards"]
        } | {item["github_repository_id"] for item in pack["exclusions"]}
        self.assertEqual(covered, set(repository_ids))


if __name__ == "__main__":
    unittest.main()
