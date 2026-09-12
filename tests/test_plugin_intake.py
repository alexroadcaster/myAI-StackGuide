"""CP-07 black-box intake and preflight acceptance.

The runtime class is skipped only while the assigned ``intake.py`` entry point
does not exist.  Contract checks still run without the plugin implementation or
third-party JSON Schema packages.  Runtime checks use only synthetic project
roots and the named non-secret canaries from the accepted sanitizer contract.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "myai-stackguide"
ENTRY_POINT = PLUGIN_ROOT / "scripts" / "intake.py"
STATE_RELATIVE = Path("docs/myai-stackguide/state.json")
PREFLIGHT_SCHEMA = ROOT / "specs/runtime/runtime-preflight-result.schema.json"
LITERAL = "STACKGUIDE_TEST_SECRET_7f4c2a90"
ASSIGNMENT = "STACKGUIDE_TEST_TOKEN=" + LITERAL
BLOCK = "-----BEGIN STACKGUIDE TEST SECRET-----\n" + LITERAL + "\n-----END STACKGUIDE TEST SECRET-----"


def load_json(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )


def compact_json(value) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def resolve_contract_ref(reference: str) -> tuple[Path, str]:
    bases = {
        "https://myai-stackguide.invalid/contracts/v1/": ROOT / "specs",
        "https://myai-stackguide.invalid/contracts/v2/": ROOT / "specs",
    }
    for base, directory in bases.items():
        if reference.startswith(base):
            location, _, fragment = reference[len(base) :].partition("#")
            return directory / Path(location), fragment
    raise AssertionError(f"non-local contract reference: {reference}")


def assert_refs_resolve(test: unittest.TestCase, schema: dict) -> None:
    def visit(value):
        if isinstance(value, dict):
            reference = value.get("$ref")
            if reference and not reference.startswith("#"):
                path, fragment = resolve_contract_ref(reference)
                test.assertTrue(path.is_file(), reference)
                target = load_json(path)
                if fragment:
                    test.assertTrue(fragment.startswith("/"), reference)
                    for raw in fragment.lstrip("/").split("/"):
                        key = raw.replace("~1", "/").replace("~0", "~")
                        test.assertIsInstance(target, dict, reference)
                        test.assertIn(key, target, reference)
                        target = target[key]
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(schema)


class IntakeContractTests(unittest.TestCase):
    def test_intake_keeps_the_accepted_next_action_vocabulary(self):
        schema = load_json(ROOT / "specs/intake/intake-state.schema.json")
        self.assertEqual(
            schema["properties"]["next_action"]["enum"],
            [
                "answer_question",
                "review_context",
                "proceed_with_assumptions",
                "clarification_required",
                "resume_or_finalize",
            ],
        )
        invariants = "\n".join(schema.get("x-invariants", []))
        for required in (
            "exactly one pending question at ordinal 1",
            "ready may occur before ten questions only after at least one accepted answer",
            "no state asks an eleventh question",
        ):
            self.assertIn(required, invariants)

    def test_sanitizer_contract_is_exact_and_claim_bounded(self):
        schema = load_json(ROOT / "specs/intake/interview-answer.schema.json")
        contract = schema["x-sanitizer-contract"]
        self.assertEqual(
            contract,
            {
                "contract_version": "1.0.0",
                "named_synthetic_canaries": {
                    "literal": LITERAL,
                    "assignment": ASSIGNMENT,
                    "block_begin": "-----BEGIN STACKGUIDE TEST SECRET-----",
                    "block_end": "-----END STACKGUIDE TEST SECRET-----",
                },
                "case_sensitive": True,
                "match_order": "longest_first",
                "replacement": "[REDACTED]",
                "collapse_adjacent_redactions_separated_only_by_whitespace": True,
                "line_endings": "lf",
                "outer_whitespace": "trim",
                "max_code_points": 2000,
                "oversize_behavior": "invalid_input_no_commit_no_truncate",
                "empty_or_fully_redacted_behavior": "invalid_input_no_commit_pending_unchanged",
                "fully_redacted_message_key": "answer_fully_redacted",
            },
        )
        invariants = "\n".join(schema.get("x-invariants", []))
        self.assertIn("only the named synthetic canaries", invariants)
        self.assertIn("not a general secret detector", invariants)
        self.assertIn("stdout, stderr", invariants)
        self.assertEqual(schema["properties"]["schema_version"]["enum"], ["1.0.0", "1.1.0"])
        self.assertIn("last_correction_id", schema["properties"])
        conditional = compact_json(schema["allOf"][-1]).decode("utf-8")
        self.assertIn('"const":"1.1.0"', conditional)
        self.assertIn('"required":["last_correction_id"]', conditional)
        self.assertIn('"properties":{"last_correction_id":false}', conditional)

        fixtures = load_json(ROOT / "tests/fixtures/plugin_contracts.json")
        legacy = fixtures["positive"]["intake/interview-answer.schema.json"]
        active = fixtures["workspace_positive"]["intake/interview-answer.schema.json"]
        self.assertEqual(legacy["schema_version"], "1.0.0")
        self.assertNotIn("last_correction_id", legacy)
        self.assertEqual(active["schema_version"], "1.1.0")
        self.assertEqual(active["answer_revision"], 1)
        self.assertIsNone(active["last_correction_id"])
        for container in (
            fixtures["workspace_positive"]["intake/intake-state.schema.json"],
            fixtures["workspace_positive"]["artifact/project-artifact-state.schema.json"]["intake"],
        ):
            self.assertTrue(container["answers"])
            self.assertTrue(all(answer["schema_version"] == "1.1.0" for answer in container["answers"]))
            self.assertTrue(all("last_correction_id" in answer for answer in container["answers"]))

    @unittest.skipUnless(PREFLIGHT_SCHEMA.is_file(), "CP-07-C1 preflight schema not handed off yet")
    def test_preflight_contract_is_local_resolvable_and_fail_closed(self):
        schema = load_json(PREFLIGHT_SCHEMA)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["schema_version"]["const"], "1.0.0")
        self.assertEqual(schema["properties"]["status"]["enum"], ["ready", "blocked"])
        self.assertEqual(
            set(schema["properties"]["reason_codes"]["items"]["enum"]),
            {
                "invalid_input",
                "python_unsupported",
                "invalid_root",
                "fts5_unavailable",
                "index_missing",
                "index_corrupt",
                "index_incompatible",
                "unavailable",
            },
        )
        self.assertEqual(
            set(schema["properties"]["next_action"]["enum"]),
            {
                "continue",
                "provide_valid_input",
                "select_valid_project_root",
                "use_supported_python",
                "use_compatible_package",
                "stop",
            },
        )
        pins = schema["properties"]["pins"]["anyOf"]
        self.assertIn(
            {
                "$ref": "https://myai-stackguide.invalid/contracts/v2/retrieval/index-manifest.schema.json#/properties/pins"
            },
            pins,
        )
        assert_refs_resolve(self, schema)
        contract_text = compact_json(schema).decode("utf-8")
        for reason, action in (
            ("invalid_input", "provide_valid_input"),
            ("python_unsupported", "use_supported_python"),
            ("invalid_root", "select_valid_project_root"),
            ("fts5_unavailable", "use_supported_python"),
            ("index_missing", "use_compatible_package"),
            ("index_corrupt", "use_compatible_package"),
            ("index_incompatible", "use_compatible_package"),
            ("unavailable", "stop"),
        ):
            self.assertIn(reason, contract_text)
            self.assertIn(action, contract_text)


@unittest.skipUnless(ENTRY_POINT.is_file(), "CP-07 runtime entry point is not implemented")
class IntakeRuntimeTests(unittest.TestCase):
    maxDiff = None

    def run_cli(
        self,
        project_root: Path,
        command: str,
        payload=None,
        expected_run_id: str | None = None,
        expected_revision: int | None = None,
    ) -> tuple[subprocess.CompletedProcess, dict]:
        argv = [
            sys.executable,
            "-I",
            "-B",
            str(ENTRY_POINT),
            command,
            "--project-root",
            str(project_root),
        ]
        if expected_run_id is not None:
            argv.extend(["--expected-run-id", expected_run_id])
        if expected_revision is not None:
            argv.extend(["--expected-revision", str(expected_revision)])
        stdin = b"" if payload is None else compact_json(payload)
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            argv,
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
            env=environment,
            timeout=20,
            check=False,
        )
        self.assertLessEqual(len(completed.stdout), 8192)
        try:
            result = json.loads(completed.stdout.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            self.fail(f"{command} did not return one strict UTF-8 JSON object: {error}")
        self.assertIsInstance(result, dict)
        serialized = completed.stdout.decode("utf-8") + completed.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(str(project_root), serialized)
        return completed, result

    def state_path(self, project_root: Path) -> Path:
        return project_root / STATE_RELATIVE

    def assert_no_canary(self, project_root: Path, completed: subprocess.CompletedProcess) -> None:
        needles = (LITERAL.encode(), ASSIGNMENT.encode(), BLOCK.encode())
        for payload in (completed.stdout, completed.stderr):
            for needle in needles:
                self.assertNotIn(needle, payload)
        output_root = project_root / "docs/myai-stackguide"
        if output_root.exists():
            for path in output_root.rglob("*"):
                if path.is_file():
                    data = path.read_bytes()
                    for needle in needles:
                        self.assertNotIn(needle, data, str(path.relative_to(project_root)))

    def assert_publication(self, value: dict) -> None:
        self.assertEqual(
            set(value),
            {
                "schema_version",
                "operation_id",
                "operation",
                "commit_status",
                "saved",
                "current",
                "published",
                "publication_status",
                "failure_reason",
                "message_key",
                "render_attempts",
                "retry",
                "html_path",
            },
        )
        self.assertEqual(value["schema_version"], "1.1.0")
        self.assertEqual(value["html_path"], "docs/myai-stackguide/status.html")

    def start(self, project_root: Path) -> tuple[dict, dict]:
        completed, outcome = self.run_cli(project_root, "start")
        self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8", errors="replace"))
        self.assert_publication(outcome)
        self.assertEqual(outcome["commit_status"], "saved")
        state = load_json(self.state_path(project_root))
        self.assertEqual((state["status"], state["phase"], state["intake"]["status"]),
                         ("active", "intake", "asking"))
        self.assertEqual(state["intake"]["questions_asked"], 1)
        self.assertEqual(len(state["intake"]["questions"]), 1)
        self.assertEqual(state["intake"]["questions"][0]["ordinal"], 1)
        self.assertEqual(state["intake"]["pending_question_id"],
                         state["intake"]["questions"][0]["question_id"])
        self.assertEqual(state["intake"]["next_action"], "answer_question")
        return outcome, state

    def test_preflight_first_failure_and_actual_ready_tuple(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp07-intake-") as directory:
            project_root = Path(directory) / "project"
            project_root.mkdir()
            completed, blocked = self.run_cli(project_root, "preflight", {"unexpected": LITERAL})
            self.assertEqual(blocked["status"], "blocked")
            self.assertEqual(blocked["reason_codes"], ["invalid_input"])
            self.assertEqual(blocked["next_action"], "provide_valid_input")
            self.assertIsNone(blocked["pins"])
            self.assertFalse(self.state_path(project_root).exists())
            self.assert_no_canary(project_root, completed)

            missing_root = project_root / "missing"
            _, invalid_root = self.run_cli(missing_root, "preflight")
            self.assertEqual(invalid_root["status"], "blocked")
            self.assertEqual(invalid_root["reason_codes"], ["invalid_root"])
            self.assertEqual(invalid_root["next_action"], "select_valid_project_root")
            self.assertIsNone(invalid_root["pins"])
            self.assertFalse(missing_root.exists())

            completed, ready = self.run_cli(project_root, "preflight")
            self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(ready["status"], "ready")
            self.assertEqual(ready["reason_codes"], [])
            self.assertEqual(ready["next_action"], "continue")
            self.assertEqual(ready["python"]["implementation"], "CPython")
            self.assertTrue(ready["python"]["version"].startswith("3.14."))
            self.assertTrue(ready["sqlite"]["fts5_available"])
            self.assertEqual(ready["root_ref"], "selected-project")
            manifest = load_json(PLUGIN_ROOT / "assets/catalog.search-manifest.json")
            self.assertEqual(ready["pins"], manifest["pins"])
            self.assertFalse(self.state_path(project_root).exists())

    def test_cancel_resume_and_ten_question_ceiling(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp07-intake-") as directory:
            project_root = Path(directory)
            _, state = self.start(project_root)
            run_id, revision = state["run_id"], state["revision"]
            _, cancelled = self.run_cli(project_root, "cancel", expected_run_id=run_id,
                                        expected_revision=revision)
            self.assert_publication(cancelled)
            state = load_json(self.state_path(project_root))
            self.assertEqual(state["intake"]["status"], "cancelled")
            self.assertIsNone(state["intake"]["pending_question_id"])
            self.assertEqual(state["intake"]["next_action"], "resume_or_finalize")

            _, resumed = self.run_cli(project_root, "resume", expected_run_id=run_id,
                                      expected_revision=state["revision"])
            self.assert_publication(resumed)
            state = load_json(self.state_path(project_root))
            self.assertEqual(state["intake"]["status"], "asking")
            self.assertIsNotNone(state["intake"]["pending_question_id"])
            stable = self.state_path(project_root).read_bytes()
            _, replay = self.run_cli(project_root, "resume", expected_run_id=run_id,
                                     expected_revision=state["revision"])
            self.assert_publication(replay)
            self.assertEqual(self.state_path(project_root).read_bytes(), stable)

            while state["intake"]["status"] == "asking":
                question_id = state["intake"]["pending_question_id"]
                ordinal = state["intake"]["questions_asked"]
                self.assertLessEqual(ordinal, 10)
                payload = {
                    "answer_id": f"answer-{ordinal}",
                    "question_id": question_id,
                    "status": "answered",
                    "value": f"Synthetic answer {ordinal}",
                    "ready": False,
                }
                _, outcome = self.run_cli(project_root, "answer", payload, run_id, state["revision"])
                self.assert_publication(outcome)
                state = load_json(self.state_path(project_root))
            self.assertEqual(state["intake"]["status"], "ready")
            self.assertEqual(state["intake"]["questions_asked"], 10)
            self.assertEqual(len(state["intake"]["questions"]), 10)
            self.assertEqual([item["ordinal"] for item in state["intake"]["questions"]], list(range(1, 11)))
            self.assertIsNone(state["intake"]["pending_question_id"])

    def test_sanitizer_redacts_only_named_patterns_and_rejects_empty_or_oversize(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp07-sanitize-") as directory:
            project_root = Path(directory)
            _, state = self.start(project_root)
            run_id = state["run_id"]
            question_id = state["intake"]["pending_question_id"]
            raw = f"  Keep\r\n{ASSIGNMENT} \t {LITERAL}\r\n{BLOCK}\r\nstackguide_test_secret_7f4c2a90  "
            payload = {
                "answer_id": "answer-redacted",
                "question_id": question_id,
                "status": "answered",
                "value": raw,
                "ready": True,
            }
            completed, outcome = self.run_cli(project_root, "answer", payload, run_id, state["revision"])
            self.assert_publication(outcome)
            self.assert_no_canary(project_root, completed)
            state = load_json(self.state_path(project_root))
            answer = state["intake"]["answers"][0]
            self.assertEqual(answer["schema_version"], "1.1.0")
            self.assertEqual(answer["answer_revision"], 1)
            self.assertIsNone(answer["last_correction_id"])
            self.assertEqual(answer["sanitized_value"], "Keep\n[REDACTED]\nstackguide_test_secret_7f4c2a90")
            self.assertTrue(answer["redaction_applied"])
            self.assertEqual(state["intake"]["status"], "ready")
            saved = self.state_path(project_root).read_bytes()

            replay_completed, replay = self.run_cli(project_root, "answer", payload, run_id, 1)
            self.assert_publication(replay)
            self.assertEqual(self.state_path(project_root).read_bytes(), saved)
            self.assert_no_canary(project_root, replay_completed)
            conflicting = dict(payload, value="different synthetic value")
            _, conflict = self.run_cli(project_root, "answer", conflicting, run_id, state["revision"])
            self.assert_publication(conflict)
            self.assertEqual(conflict["failure_reason"], "state_conflict")
            self.assertEqual(conflict["commit_status"], "not_saved")
            self.assertEqual(self.state_path(project_root).read_bytes(), saved)

        with tempfile.TemporaryDirectory(prefix="stackguide-cp07-reject-") as directory:
            project_root = Path(directory)
            _, state = self.start(project_root)
            base = self.state_path(project_root).read_bytes()
            common = {
                "answer_id": "answer-rejected",
                "question_id": state["intake"]["pending_question_id"],
                "status": "answered",
                "ready": False,
            }
            completed, rejected = self.run_cli(
                project_root,
                "answer",
                dict(common, value=LITERAL),
                state["run_id"],
                state["revision"],
            )
            self.assert_publication(rejected)
            self.assertEqual(rejected["failure_reason"], "invalid_input")
            self.assertEqual(rejected["message_key"], "answer_fully_redacted")
            self.assertEqual(rejected["commit_status"], "not_saved")
            self.assertEqual(self.state_path(project_root).read_bytes(), base)
            self.assert_no_canary(project_root, completed)

            _, oversize = self.run_cli(
                project_root,
                "answer",
                dict(common, answer_id="answer-oversize", value="я" * 2001),
                state["run_id"],
                state["revision"],
            )
            self.assert_publication(oversize)
            self.assertEqual(oversize["failure_reason"], "invalid_input")
            self.assertIsNone(oversize["message_key"])
            self.assertEqual(self.state_path(project_root).read_bytes(), base)

    def test_pre_brief_correction_has_bounded_immediate_replay_semantics(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp07-correct-") as directory:
            project_root = Path(directory)
            _, state = self.start(project_root)
            run_id = state["run_id"]
            question_id = state["intake"]["pending_question_id"]
            answer_payload = {
                "answer_id": "answer-correctable",
                "question_id": question_id,
                "status": "answered",
                "value": "Initial synthetic goal",
                "ready": False,
            }
            self.run_cli(project_root, "answer", answer_payload, run_id, state["revision"])
            before = load_json(self.state_path(project_root))
            original = dict(before["intake"]["answers"][0])
            self.assertEqual(original["schema_version"], "1.1.0")
            self.assertEqual(original["answer_revision"], 1)
            self.assertIsNone(original["last_correction_id"])
            first_payload = {
                "correction_id": "correction-pre-brief-1",
                "answer_id": original["answer_id"],
                "value": "Corrected synthetic goal",
                "ready": False,
            }
            first_expected_revision = before["revision"]
            _, outcome = self.run_cli(
                project_root, "correct", first_payload, run_id, first_expected_revision
            )
            self.assert_publication(outcome)
            after_first = load_json(self.state_path(project_root))
            corrected_first = after_first["intake"]["answers"][0]
            self.assertEqual(corrected_first["answer_id"], original["answer_id"])
            self.assertEqual(corrected_first["question_id"], original["question_id"])
            self.assertEqual(corrected_first["ordinal"], original["ordinal"])
            self.assertEqual(corrected_first["answer_revision"], original["answer_revision"] + 1)
            self.assertEqual(corrected_first["expected_state_revision"], first_expected_revision)
            self.assertEqual(corrected_first["last_correction_id"], first_payload["correction_id"])
            self.assertEqual(corrected_first["sanitized_value"], first_payload["value"])
            self.assertEqual(after_first["revision"], first_expected_revision + 1)
            self.assertEqual(after_first["content_revision"], before["content_revision"] + 1)
            self.assertEqual(after_first["phase"], "intake")
            self.assertIsNone(after_first["brief"])
            self.assertEqual(after_first["corrections"], [])
            for key in ("selection", "request", "retrieval", "evidence_pack", "memo"):
                self.assertIsNone(after_first[key])

            first_bytes = self.state_path(project_root).read_bytes()
            self.run_cli(
                project_root, "correct", first_payload, run_id, first_expected_revision
            )
            self.assertEqual(self.state_path(project_root).read_bytes(), first_bytes)
            _, conflict = self.run_cli(
                project_root,
                "correct",
                dict(first_payload, value="Conflicting correction"),
                run_id,
                first_expected_revision,
            )
            self.assertEqual(conflict["failure_reason"], "state_conflict")
            self.assertEqual(self.state_path(project_root).read_bytes(), first_bytes)

            second_payload = {
                "correction_id": "correction-pre-brief-2",
                "answer_id": original["answer_id"],
                "value": "Second corrected synthetic goal",
                "ready": False,
            }
            second_expected_revision = after_first["revision"]
            _, second_outcome = self.run_cli(
                project_root, "correct", second_payload, run_id, second_expected_revision
            )
            self.assert_publication(second_outcome)
            after_second = load_json(self.state_path(project_root))
            corrected_second = after_second["intake"]["answers"][0]
            self.assertEqual(corrected_second["answer_revision"], original["answer_revision"] + 2)
            self.assertEqual(corrected_second["expected_state_revision"], second_expected_revision)
            self.assertEqual(corrected_second["last_correction_id"], second_payload["correction_id"])
            self.assertEqual(corrected_second["sanitized_value"], second_payload["value"])
            self.assertEqual(after_second["revision"], second_expected_revision + 1)
            self.assertEqual(after_second["content_revision"], before["content_revision"] + 2)
            self.assertEqual(after_second["corrections"], [])

            answer_schema = load_json(ROOT / "specs/intake/interview-answer.schema.json")
            self.assertEqual(
                set(corrected_second),
                set(answer_schema["required"]) | {"last_correction_id"},
            )
            current_state = compact_json(after_second)
            self.assertNotIn(original["sanitized_value"].encode("utf-8"), current_state)
            self.assertNotIn(first_payload["value"].encode("utf-8"), current_state)

            second_bytes = self.state_path(project_root).read_bytes()
            self.run_cli(
                project_root, "correct", second_payload, run_id, second_expected_revision
            )
            self.assertEqual(self.state_path(project_root).read_bytes(), second_bytes)

            _, stale = self.run_cli(
                project_root, "correct", first_payload, run_id, first_expected_revision
            )
            self.assertEqual(stale["failure_reason"], "state_conflict")
            self.assertEqual(stale["commit_status"], "not_saved")
            self.assertEqual(self.state_path(project_root).read_bytes(), second_bytes)


if __name__ == "__main__":
    unittest.main()
