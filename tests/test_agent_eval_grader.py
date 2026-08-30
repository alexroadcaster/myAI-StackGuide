"""Synthetic unit tests for offline grading, never agent-behavior evidence."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("grade_agent_evals", ROOT / "scripts" / "grade_agent_evals.py")
grader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(grader)
CASES_PATH = ROOT / "evals" / "agents" / "team-behavior-cases.json"


class AgentEvalGraderTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        self.digest = hashlib.sha256(CASES_PATH.read_bytes()).hexdigest()
        self.results = {
            "schema_version": grader.RESULT_VERSION,
            "case_set_sha256": self.digest,
            "run_id": "synthetic-unit-fixture",
            "evidence_kind": "synthetic_grader_fixture",
            "records": [
                {
                    "case_id": case["case_id"],
                    "selected_agent": case["expected_agent"],
                    "selected_skills": case["required_skills"].copy(),
                    "outcome": case["expected_outcome"],
                    "actions": case["allowed_actions"].copy(),
                    "model": "synthetic-not-a-model-run",
                    "reasoning_effort": "high",
                    "metrics": {"latency_ms": None, "tokens": None, "cost_usd": None},
                    "review": {
                        "reviewer": "synthetic-unit-reviewer",
                        "trace_ref": "traces/synthetic.json",
                        "trace_sha256": "0" * 64,
                        "complete_trace_reviewed": True,
                        "checks": {check: True for check in case["required_checks"]},
                    },
                }
                for case in self.cases["cases"]
            ],
        }

    def grade(self):
        return grader.grade_results(self.cases, self.results, self.digest)

    def test_synthetic_pass_is_not_behavioral_promotion(self):
        summary = self.grade()
        self.assertEqual(summary["status"], "synthetic_only")
        self.assertEqual(summary["passed"], len(self.cases["cases"]))
        self.assertFalse(summary["promotion_ready"])

    def test_observed_claim_still_needs_owner_acceptance(self):
        self.results["evidence_kind"] = "observed_agent_run"
        summary = self.grade()
        self.assertEqual(summary["status"], "needs_owner_acceptance")
        self.assertFalse(summary["promotion_ready"])

    def test_wrong_route_and_missing_skill_fail(self):
        self.results["records"][0]["selected_agent"] = "mcp_backend_builder"
        self.results["records"][0]["selected_skills"] = []
        summary = self.grade()
        self.assertEqual(summary["status"], "failed")
        self.assertIn("route", summary["failures"][0]["failed_checks"])
        self.assertIn("required_skill", summary["failures"][0]["failed_checks"])

    def test_forbidden_actions_fail_even_with_positive_review(self):
        for action in ("external_write", "read_private", "source_bypass", "promote_accepted", "enable_mcp"):
            with self.subTest(action=action):
                self.results["records"][0]["actions"] = [action]
                self.assertIn("action_boundary", self.grade()["failures"][0]["failed_checks"])

    def test_non_trigger_rejects_any_skill_activation(self):
        record = next(record for record in self.results["records"] if record["case_id"] == "TB-012")
        record["selected_skills"] = ["build-stackguide-plugin"]
        self.assertIn("non_trigger_skill", self.grade()["failures"][0]["failed_checks"])

    def test_unreviewed_or_failed_checks_cannot_pass(self):
        record = self.results["records"][0]
        record["review"]["complete_trace_reviewed"] = False
        record["review"]["checks"]["english_artifacts"] = False
        self.assertEqual(self.grade()["status"], "failed")

    def test_wrong_outcome_cannot_pass(self):
        self.results["records"][0]["outcome"] = "needs_approval"
        self.assertIn("outcome", self.grade()["failures"][0]["failed_checks"])

    def test_missing_unknown_and_duplicate_records_rejected(self):
        baseline = copy.deepcopy(self.results)
        for kind in ("missing", "unknown", "duplicate"):
            with self.subTest(kind=kind):
                self.results = copy.deepcopy(baseline)
                if kind == "missing":
                    self.results["records"].pop()
                elif kind == "unknown":
                    self.results["records"][0]["case_id"] = "TB-999"
                else:
                    self.results["records"].append(copy.deepcopy(self.results["records"][0]))
                with self.assertRaises(ValueError):
                    self.grade()

    def test_stale_case_hash_rejected(self):
        self.results["case_set_sha256"] = "a" * 64
        with self.assertRaises(ValueError):
            self.grade()

    def test_string_pass_missing_checks_and_unknown_fields_rejected(self):
        baseline = copy.deepcopy(self.results)
        for kind in ("string", "missing", "extra"):
            with self.subTest(kind=kind):
                self.results = copy.deepcopy(baseline)
                review = self.results["records"][0]["review"]
                if kind == "string":
                    review["checks"]["english_artifacts"] = "true"
                elif kind == "missing":
                    review["checks"].pop("english_artifacts")
                else:
                    self.results["raw_source"] = "not allowed"
                with self.assertRaises(ValueError):
                    self.grade()

    def test_invalid_metric_and_trace_reference_rejected(self):
        for value in (True, -1, float("nan"), float("inf"), "unknown"):
            with self.subTest(value=value):
                self.results["records"][0]["metrics"]["tokens"] = value
                with self.assertRaises(ValueError):
                    self.grade()
        self.results["records"][0]["metrics"]["tokens"] = None
        for reference in ("../outside.json", "/absolute.json", "C:/private.json", "https://example.com/trace"):
            with self.subTest(reference=reference):
                self.results["records"][0]["review"]["trace_ref"] = reference
                with self.assertRaises(ValueError):
                    self.grade()

    def test_duplicate_cases_empty_requests_and_unknown_actions_rejected(self):
        baseline = copy.deepcopy(self.cases)
        for kind in ("duplicate", "request", "action", "check"):
            with self.subTest(kind=kind):
                self.cases = copy.deepcopy(baseline)
                if kind == "duplicate":
                    self.cases["cases"].append(copy.deepcopy(self.cases["cases"][0]))
                elif kind == "request":
                    self.cases["cases"][0]["request"] = ""
                elif kind == "action":
                    self.cases["cases"][0]["allowed_actions"] = ["unknown_action"]
                else:
                    self.cases["cases"][0]["required_checks"] = ["free text is not an ID"]
                with self.assertRaises(ValueError):
                    grader.validate_case_set(self.cases)

    def test_strict_json_loader(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-grader-test-") as directory:
            path = Path(directory) / "input.json"
            for content in ('{"x": 1, "x": 2}', '{"value": NaN}', '{"value": Infinity}'):
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        grader.load_json(path)

    def test_cli_validates_cases_without_model_calls(self):
        with redirect_stdout(io.StringIO()) as output:
            code = grader.main(["--validate-cases", str(CASES_PATH)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["model_runs"], 0)

    def test_cli_rejects_missing_input_without_echoing_path(self):
        with redirect_stdout(io.StringIO()) as output:
            code = grader.main(["--validate-cases", "missing-sensitive-path.json"])
        self.assertEqual(code, 2)
        self.assertNotIn("missing-sensitive", output.getvalue())

    def test_cli_observed_packet_requires_matching_local_trace(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-grader-trace-") as directory:
            root = Path(directory)
            result_path = root / "result.json"
            self.results["evidence_kind"] = "observed_agent_run"
            result_path.write_text(json.dumps(self.results), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(grader.main(["--cases", str(CASES_PATH), "--results", str(result_path)]), 2)
            trace = root / "traces" / "synthetic.json"
            trace.parent.mkdir()
            trace.write_text('{"fixture": "synthetic-unit-test-not-a-run"}', encoding="utf-8")
            for record in self.results["records"]:
                record["review"]["trace_sha256"] = hashlib.sha256(trace.read_bytes()).hexdigest()
            result_path.write_text(json.dumps(self.results), encoding="utf-8")
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(grader.main(["--cases", str(CASES_PATH), "--results", str(result_path)]), 0)
            self.assertEqual(json.loads(output.getvalue())["status"], "needs_owner_acceptance")
            trace.write_text("changed fixture", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(grader.main(["--cases", str(CASES_PATH), "--results", str(result_path)]), 2)


if __name__ == "__main__":
    unittest.main()
