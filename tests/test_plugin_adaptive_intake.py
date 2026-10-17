"""Host-selected questions use the canonical bank and a revision-bound ledger."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/myai-stackguide/scripts"))
import intake


class AdaptiveIntakeTests(unittest.TestCase):
    def test_host_selects_decision_changing_gap_and_retry_cannot_change_it(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            intake._ACTIVE_ROOT = project
            manifest = json.loads((intake.ASSETS / "catalog.search-manifest.json").read_bytes())
            intake.command_start(project, {}, manifest)
            path = project / "docs/myai-stackguide/state.json"
            state = json.loads(path.read_bytes())
            payload = dict(answer_id="goal-answer", question_id="goal", status="answered",
                           value="Evaluate a local test runner for an existing Python project.",
                           ready=False, next_question_id="deployment")
            try:
                receipt = intake.command_answer(project, payload, state["run_id"], state["revision"])
            except intake.store.StateError as error:
                self.fail(f"Canonical host-selected question must be accepted: {error.reason}")
            self.assertEqual(receipt["publication_status"], "current")
            saved = json.loads(path.read_bytes())
            self.assertEqual(saved["intake"]["pending_question_id"], "deployment")
            self.assertEqual(saved["intake"]["questions"][-1]["ordinal"], 2)
            before = path.read_bytes()
            intake.command_answer(project, payload, state["run_id"], state["revision"])
            self.assertEqual(path.read_bytes(), before)
            changed = dict(payload, next_question_id="current_stack")
            with self.assertRaises(intake.store.StateError) as conflict:
                intake.command_answer(project, changed, state["run_id"], state["revision"])
            self.assertEqual(conflict.exception.reason, "state_conflict")
            self.assertEqual(path.read_bytes(), before)

    def test_unknown_or_already_asked_question_cannot_replace_saved_answer(self):
        for selected in ("untrusted_question", "goal"):
            with self.subTest(selected=selected), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                intake._ACTIVE_ROOT = project
                manifest = json.loads((intake.ASSETS / "catalog.search-manifest.json").read_bytes())
                intake.command_start(project, {}, manifest)
                path = project / "docs/myai-stackguide/state.json"
                before = path.read_bytes()
                state = json.loads(before)
                with self.assertRaises(intake.store.StateError):
                    intake.command_answer(project, dict(answer_id="a", question_id="goal",
                        status="answered", value="Synthetic goal", ready=False,
                        next_question_id=selected), state["run_id"], state["revision"])
                self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
