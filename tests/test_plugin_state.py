"""CP-07 state, correction, finalization and publication acceptance.

These tests deliberately distinguish structural contracts from runtime proof.
The black-box runtime class activates only when the assigned CLI exists and
operates exclusively on disposable synthetic project roots.
"""

from __future__ import annotations

import copy
import importlib.util
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
STATE_SCHEMA = ROOT / "specs/artifact/project-artifact-state.schema.json"
PUBLICATION_SCHEMA = ROOT / "specs/artifact/publication-result.schema.json"
STATE_RELATIVE = Path("docs/myai-stackguide/state.json")


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


def schema_matches(schema, instance) -> bool:
    """Small stdlib evaluator for the lifecycle if/then fragment only.

    It intentionally ignores unrelated JSON Schema keywords and external refs;
    the established V-CONTRACT suite owns full Draft 2020-12 validation.
    """
    if schema is True:
        return True
    if schema is False:
        return False
    if not isinstance(schema, dict):
        return True
    if "const" in schema and instance != schema["const"]:
        return False
    if "enum" in schema and instance not in schema["enum"]:
        return False
    expected_type = schema.get("type")
    type_checks = {
        "null": lambda value: value is None,
        "object": lambda value: isinstance(value, dict),
        "array": lambda value: isinstance(value, list),
        "string": lambda value: isinstance(value, str),
        "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
        "boolean": lambda value: isinstance(value, bool),
    }
    if expected_type in type_checks and not type_checks[expected_type](instance):
        return False
    if isinstance(expected_type, list) and not any(type_checks[kind](instance) for kind in expected_type):
        return False
    if isinstance(instance, dict):
        if any(key not in instance for key in schema.get("required", [])):
            return False
        for key, child_schema in schema.get("properties", {}).items():
            if key in instance and not schema_matches(child_schema, instance[key]):
                return False
    if any(not schema_matches(branch, instance) for branch in schema.get("allOf", [])):
        return False
    if "anyOf" in schema and not any(schema_matches(branch, instance) for branch in schema["anyOf"]):
        return False
    if "oneOf" in schema and sum(schema_matches(branch, instance) for branch in schema["oneOf"]) != 1:
        return False
    if "not" in schema and schema_matches(schema["not"], instance):
        return False
    if "if" in schema:
        branch = schema.get("then", {}) if schema_matches(schema["if"], instance) else schema.get("else", {})
        if not schema_matches(branch, instance):
            return False
    return True


class StateContractTests(unittest.TestCase):
    def test_schema_encodes_the_complete_status_phase_intake_matrix(self):
        schema = load_json(STATE_SCHEMA)
        lifecycle = {"allOf": schema["allOf"]}
        valid = {
            ("active", "intake", "asking"),
            ("active", "intake", "ready"),
            ("active", "intake", "cancelled"),
            ("active", "scan", "ready"),
            ("active", "context_review", "ready"),
            ("active", "matching", "ready"),
            ("active", "report", "ready"),
            ("finalized", "report", "ready"),
            ("finalized_incomplete", "intake", "ready"),
            ("finalized_incomplete", "intake", "cancelled"),
            ("finalized_incomplete", "scan", "ready"),
            ("finalized_incomplete", "context_review", "ready"),
            ("finalized_incomplete", "matching", "ready"),
            ("finalized_incomplete", "report", "ready"),
        }
        for status in ("active", "finalized", "finalized_incomplete"):
            for phase in ("intake", "scan", "context_review", "matching", "report"):
                for intake_status in ("asking", "ready", "cancelled"):
                    with self.subTest(status=status, phase=phase, intake_status=intake_status):
                        instance = {
                            "schema_version": "1.1.0",
                            "status": status,
                            "phase": phase,
                            "content_revision": 1,
                            "presentation": {},
                            "scan": None,
                            "intake": {
                                "schema_version": "1.1.0",
                                "status": intake_status,
                                "next_action": (
                                    "answer_question" if intake_status == "asking"
                                    else "resume_or_finalize" if intake_status == "cancelled"
                                    else "review_context"
                                ),
                            },
                            "brief": (
                                {"schema_version": "1.1.0"}
                                if phase in ("context_review", "matching", "report") else None
                            ),
                            "memo": {"schema_version": "2.1.0"} if phase == "report" else None,
                        }
                        self.assertEqual(
                            schema_matches(lifecycle, instance),
                            (status, phase, intake_status) in valid,
                        )
        missing_brief = {
            "schema_version": "1.1.0",
            "status": "active",
            "phase": "matching",
            "content_revision": 1,
            "presentation": {},
            "scan": None,
            "intake": {"schema_version": "1.1.0", "status": "ready", "next_action": "review_context"},
            "brief": None,
            "memo": None,
        }
        missing_memo = copy.deepcopy(missing_brief)
        missing_memo.update(phase="report", brief={})
        self.assertFalse(schema_matches(lifecycle, missing_brief))
        self.assertFalse(schema_matches(lifecycle, missing_memo))

    def test_workspace_contract_names_transition_correction_and_finalization_rules(self):
        contract = (ROOT / "specs/artifact/session-workspace-contract.md").read_text(encoding="utf-8")
        sources = (
            contract
            + compact_json(load_json(STATE_SCHEMA)).decode("utf-8")
            + compact_json(load_json(PUBLICATION_SCHEMA)).decode("utf-8")
        )
        for required in (
            "active",
            "finalized_incomplete",
            "latest valid phase",
            "pre-Brief",
            "post-Brief",
            "state_conflict",
            "history_integrity",
            "render_only",
            "predecessor_run_id",
        ):
            self.assertIn(required, sources)

    def test_publication_result_has_typed_invalid_input_without_a_new_operation(self):
        schema = load_json(PUBLICATION_SCHEMA)
        self.assertEqual(
            schema["properties"]["operation"]["enum"],
            ["commit_and_publish", "render_only"],
        )
        failures = schema["properties"]["failure_reason"]["anyOf"][0]["enum"]
        self.assertIn("invalid_input", failures)
        self.assertIn("message_key", schema["required"])
        self.assertEqual(
            schema["properties"]["message_key"]["anyOf"],
            [{"const": "answer_fully_redacted"}, {"type": "null"}],
        )
        invariants = "\n".join(schema.get("x-invariants", []))
        self.assertIn("invalid_input", invariants)
        self.assertIn("answer_fully_redacted", invariants)
        self.assertIn("no-write outcome", invariants)


def load_contract_helpers():
    spec = importlib.util.spec_from_file_location(
        "stackguide_plugin_contract_helpers",
        ROOT / "tests/test_plugin_contracts.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(ENTRY_POINT.is_file(), "CP-07 runtime entry point is not implemented")
class StateRuntimeTests(unittest.TestCase):
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
        completed = subprocess.run(
            argv,
            input=b"" if payload is None else compact_json(payload),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            timeout=20,
            check=False,
        )
        self.assertLessEqual(len(completed.stdout), 8192)
        try:
            outcome = json.loads(completed.stdout.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            self.fail(f"{command} did not return one strict UTF-8 JSON object: {error}")
        self.assertIsInstance(outcome, dict)
        combined = completed.stdout.decode("utf-8") + completed.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(str(project_root), combined)
        return completed, outcome

    def state_path(self, project_root: Path) -> Path:
        return project_root / STATE_RELATIVE

    def start(self, project_root: Path) -> dict:
        completed, outcome = self.run_cli(project_root, "start")
        self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8", errors="replace"))
        self.assertEqual(outcome["commit_status"], "saved")
        return load_json(self.state_path(project_root))

    def test_expected_revision_conflict_and_render_only_retry_never_mutate_state(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp07-state-") as directory:
            project_root = Path(directory)
            state = self.start(project_root)
            state_path = self.state_path(project_root)
            stable = state_path.read_bytes()
            question_id = state["intake"]["pending_question_id"]
            payload = {
                "answer_id": "answer-stale-revision",
                "question_id": question_id,
                "status": "answered",
                "value": "Synthetic stale revision",
                "ready": False,
            }
            _, conflict = self.run_cli(
                project_root,
                "answer",
                payload,
                state["run_id"],
                state["revision"] + 1,
            )
            self.assertEqual(conflict["commit_status"], "not_saved")
            self.assertEqual(conflict["failure_reason"], "state_conflict")
            self.assertEqual(state_path.read_bytes(), stable)

            html_path = project_root / "docs/myai-stackguide/status.html"
            if html_path.is_file():
                html_path.unlink()
            _, retry = self.run_cli(
                project_root,
                "retry-publication",
                expected_run_id=state["run_id"],
                expected_revision=state["revision"],
            )
            self.assertEqual(retry["operation"], "render_only")
            self.assertEqual(retry["commit_status"], "not_attempted")
            self.assertEqual(retry["publication_status"], "current")
            self.assertEqual(retry["render_attempts"], 1)
            self.assertEqual(state_path.read_bytes(), stable)
            self.assertTrue(html_path.is_file())

    def test_incomplete_finalization_is_immutable_idempotent_and_predecessor_linked(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp07-finalize-") as directory:
            project_root = Path(directory)
            state = self.start(project_root)
            run_id = state["run_id"]
            _, outcome = self.run_cli(
                project_root,
                "finalize",
                expected_run_id=run_id,
                expected_revision=state["revision"],
            )
            self.assertEqual(outcome["commit_status"], "saved")
            finalized = load_json(self.state_path(project_root))
            self.assertEqual(finalized["status"], "finalized_incomplete")
            self.assertEqual(finalized["phase"], "intake")
            self.assertEqual(finalized["intake"]["status"], "cancelled")
            history_path = project_root / f"docs/myai-stackguide/runs/{run_id}.json"
            self.assertEqual(history_path.read_bytes(), self.state_path(project_root).read_bytes())
            state_bytes = self.state_path(project_root).read_bytes()
            history_bytes = history_path.read_bytes()

            self.run_cli(
                project_root,
                "finalize",
                expected_run_id=run_id,
                expected_revision=finalized["revision"],
            )
            self.assertEqual(self.state_path(project_root).read_bytes(), state_bytes)
            self.assertEqual(history_path.read_bytes(), history_bytes)

            correction = {
                "correction_id": "correction-after-finalize",
                "answer_id": "answer-does-not-exist",
                "value": "Must not mutate terminal state",
                "ready": False,
            }
            _, rejected = self.run_cli(
                project_root,
                "correct",
                correction,
                run_id,
                finalized["revision"],
            )
            self.assertEqual(rejected["commit_status"], "not_saved")
            self.assertEqual(self.state_path(project_root).read_bytes(), state_bytes)

            history_path.write_bytes(b"{}")
            _, integrity = self.run_cli(
                project_root,
                "finalize",
                expected_run_id=run_id,
                expected_revision=finalized["revision"],
            )
            self.assertEqual(integrity["failure_reason"], "history_integrity")
            self.assertEqual(self.state_path(project_root).read_bytes(), state_bytes)
            self.assertEqual(history_path.read_bytes(), b"{}")

        with tempfile.TemporaryDirectory(prefix="stackguide-cp07-predecessor-") as directory:
            project_root = Path(directory)
            original = self.start(project_root)
            self.run_cli(project_root, "finalize", expected_run_id=original["run_id"],
                         expected_revision=original["revision"])
            old_history = (project_root / f"docs/myai-stackguide/runs/{original['run_id']}.json").read_bytes()
            replacement = self.start(project_root)
            self.assertNotEqual(replacement["run_id"], original["run_id"])
            self.assertEqual(replacement["predecessor_run_id"], original["run_id"])
            self.assertEqual(
                (replacement["status"], replacement["phase"], replacement["intake"]["status"]),
                ("active", "intake", "asking"),
            )
            self.assertEqual(
                (project_root / f"docs/myai-stackguide/runs/{original['run_id']}.json").read_bytes(),
                old_history,
            )

    def test_post_brief_correction_preserves_observations_and_invalidates_downstream(self):
        helpers = load_contract_helpers()
        with tempfile.TemporaryDirectory(prefix="stackguide-cp07-post-brief-") as directory:
            project_root = Path(directory)
            output_root = project_root / "docs/myai-stackguide"
            output_root.mkdir(parents=True)
            state = helpers.workspace_baseline()
            state.update(status="active", phase="context_review", revision=7, content_revision=3,
                         html_revision=None, corrections=[])
            state["intake"]["next_action"] = "review_context"
            state["index_manifest"] = load_json(PLUGIN_ROOT / "assets/catalog.search-manifest.json")
            for key in ("selection", "request", "retrieval", "evidence_pack", "memo"):
                state[key] = None
            state["brief"]["user_corrections"] = []
            helpers.rebind_presentation(state)
            helpers.check_bundle(state)
            self.state_path(project_root).write_bytes(compact_json(state))
            scan_before = compact_json(state["scan"])
            manifest_before = compact_json(state["index_manifest"])
            brief_version = state["brief"]["brief_version"]
            payload = {
                "correction_id": "correction-post-brief-1",
                "target": "goal",
                "value": "Updated synthetic goal",
            }
            _, outcome = self.run_cli(
                project_root,
                "correct",
                payload,
                state["run_id"],
                state["revision"],
            )
            self.assertEqual(outcome["commit_status"], "saved")
            corrected = load_json(self.state_path(project_root))
            self.assertEqual(corrected["phase"], "context_review")
            self.assertEqual(corrected["brief"]["brief_version"], brief_version + 1)
            self.assertEqual(corrected["brief"]["goal"], "Updated synthetic goal")
            self.assertEqual(corrected["brief"]["user_corrections"], ["correction-post-brief-1"])
            self.assertEqual(corrected["intake"]["next_action"], "review_context")
            self.assertEqual(compact_json(corrected["scan"]), scan_before)
            self.assertEqual(compact_json(corrected["index_manifest"]), manifest_before)
            for key in ("selection", "request", "retrieval", "evidence_pack", "memo"):
                self.assertIsNone(corrected[key])
            event = corrected["corrections"][-1]
            self.assertEqual(event["from_brief_version"], brief_version)
            self.assertEqual(event["to_brief_version"], brief_version + 1)
            self.assertFalse(event["observed_facts_mutated"])
            self.assertEqual(
                event["invalidates"],
                ["selection", "request", "retrieval_result", "evidence_pack", "recommendation_memo"],
            )


if __name__ == "__main__":
    unittest.main()
