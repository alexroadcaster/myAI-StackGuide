import copy
import importlib.util
import inspect
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "plugins" / "myai-stackguide" / "scripts"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "plugin_contracts.json"


def load_runtime_module(name):
    path = SCRIPT_DIR / f"{name}.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(f"stackguide_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MatchingRuntimeContractTests(unittest.TestCase):
    module_path = SCRIPT_DIR / "matcher.py"

    def test_planned_matcher_module_exists(self):
        self.assertTrue(
            self.module_path.is_file(),
            "CP-09 expected RED: missing plugins/myai-stackguide/scripts/matcher.py",
        )

    @unittest.skipUnless(module_path.is_file(), "planned matcher runtime is absent")
    def test_public_api_and_segment_safe_pointer_coverage(self):
        runtime = load_runtime_module("matcher")
        expected = {
            "evidence_pointer_covers": ["source_pointer", "target_pointer"],
            "match_candidate": ["card", "query"],
        }
        for name, parameters in expected.items():
            with self.subTest(name=name):
                self.assertTrue(callable(getattr(runtime, name, None)))
                self.assertEqual(
                    list(inspect.signature(getattr(runtime, name)).parameters),
                    parameters,
                )

        covers = runtime.evidence_pointer_covers
        self.assertTrue(covers("/repository/license", "/repository/license/spdx"))
        self.assertTrue(covers("/repository/license/spdx", "/repository/license/spdx"))
        self.assertFalse(covers("/", "/repository/license/spdx"))
        self.assertFalse(covers("/repository/lic", "/repository/license/spdx"))
        self.assertFalse(covers("/repository/topics", "/repository/license/spdx"))
        self.assertFalse(covers("/advisory", "/repository/license/spdx"))

    @unittest.skipUnless(module_path.is_file(), "planned matcher runtime is absent")
    def test_matcher_preserves_pass_fail_unknown_separation(self):
        runtime = load_runtime_module("matcher")
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["positive"]
        query = fixture["retrieval/catalog-query.schema.json"]
        card = fixture["retrieval/evidence-pack.schema.json"]["cards"][0]["card"]

        eligible = runtime.match_candidate(card, query)
        self.assertEqual(eligible["status"], "primary_eligible")
        self.assertTrue(all(item["outcome"] == "pass" for item in eligible["checks"]))

        mismatch = copy.deepcopy(query)
        mismatch["constraints"]["allowed_licenses"] = ["Apache-2.0"]
        blocked = runtime.match_candidate(card, mismatch)
        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("constraint_mismatch", blocked["reason_codes"])

        unknown_card = copy.deepcopy(card)
        unknown_card["repository"]["license"] = None
        unknown = runtime.match_candidate(unknown_card, query)
        self.assertEqual(unknown["status"], "reference_only")
        self.assertIn("mandatory_fact_unknown", unknown["reason_codes"])
        self.assertTrue(unknown["required_verifications"])

    @unittest.skipUnless(module_path.is_file(), "planned matcher runtime is absent")
    def test_archived_unavailable_and_unknown_mandatory_facts_are_distinct(self):
        runtime = load_runtime_module("matcher")
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["positive"]
        query = fixture["retrieval/catalog-query.schema.json"]
        card = fixture["retrieval/evidence-pack.schema.json"]["cards"][0]["card"]

        hard_failures = (
            ("archived", lambda value: value["repository"].update(archived=True)),
            (
                "unavailable",
                lambda value: value["repository"].update(availability="unavailable"),
            ),
        )
        for reason, mutate in hard_failures:
            changed = copy.deepcopy(card)
            mutate(changed)
            result = runtime.match_candidate(changed, query)
            with self.subTest(reason=reason):
                self.assertEqual(result["status"], "blocked")
                self.assertIn(reason, result["reason_codes"])
                field = "availability" if reason == "unavailable" else reason
                check = next(item for item in result["checks"] if item["field"] == field)
                self.assertEqual(check["outcome"], "fail")

        unknown_mutations = (
            ("license", lambda value: value["repository"].update(license=None)),
            ("deployment", lambda value: value["delivery"].update(deployment=None)),
            ("language", lambda value: value["repository"].update(languages=[])),
            ("compatibility", lambda value: value["advisory"].update(compatibility=[])),
            ("no_server", lambda value: value["delivery"].update(requires_server=None)),
        )
        for field, mutate in unknown_mutations:
            changed = copy.deepcopy(card)
            mutate(changed)
            result = runtime.match_candidate(changed, query)
            with self.subTest(field=field):
                self.assertEqual(result["status"], "reference_only")
                self.assertIn("mandatory_fact_unknown", result["reason_codes"])
                check = next(item for item in result["checks"] if item["field"] == field)
                self.assertEqual(check["outcome"], "unknown")
                self.assertTrue(result["required_verifications"])

    @unittest.skipUnless(module_path.is_file(), "planned matcher runtime is absent")
    def test_pointer_coverage_rejects_root_siblings_and_prefix_collisions(self):
        runtime = load_runtime_module("matcher")
        cases = (
            ("/", "/repository/license", False),
            ("/repository", "/repository/license", True),
            ("/repository/lic", "/repository/license", False),
            ("/repository/licensee", "/repository/license", False),
            ("/repository/license/spdx", "/repository/license", False),
            ("/repository/topics", "/repository/license", False),
            ("/delivery/license", "/repository/license", False),
            ("/repository/", "/repository/license", False),
            ("/repository//license", "/repository/license", False),
        )
        for source, target, expected in cases:
            with self.subTest(source=source, target=target):
                self.assertIs(runtime.evidence_pointer_covers(source, target), expected)

        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["positive"]
        query = fixture["retrieval/catalog-query.schema.json"]
        card = copy.deepcopy(
            fixture["retrieval/evidence-pack.schema.json"]["cards"][0]["card"]
        )
        for evidence in card["evidence"]:
            evidence["fields"] = ["/repository/lic"]
        result = runtime.match_candidate(card, query)
        license_check = next(
            item for item in result["checks"] if item["field"] == "license"
        )
        self.assertEqual(license_check["outcome"], "unknown")
        self.assertEqual(license_check["evidence_refs"], [])
        self.assertEqual(result["status"], "reference_only")


if __name__ == "__main__":
    unittest.main()
