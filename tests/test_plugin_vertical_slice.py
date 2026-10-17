"""CP-11 actual local joins; the authored memo is not model-quality evidence.

The single scenario goes through public CP-07 commands and the packaged FTS5
reader. Every project file is synthetic. Optional CP11_EVIDENCE_ROOT retains
only synthetic state, its HTML projection, history and sanitized observations.
"""

from __future__ import annotations

import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins/myai-stackguide/scripts"
ASSETS = SCRIPTS.parent / "assets"
CASE_PATH = ROOT / "tests/fixtures/plugin_vertical_slice.json"
STATE_REL = Path("docs/myai-stackguide/state.json")
HTML_REL = Path("docs/myai-stackguide/status.html")


def load(path):
    return json.loads(Path(path).read_bytes())


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(compact(value)).hexdigest()


def runtime():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    return tuple(importlib.import_module(name) for name in
                 ("intake", "scanner", "context", "recommendation_request", "retrieval", "context_pack"))


class VerticalSliceTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.case = load(CASE_PATH)
        self.trace = []
        self.captures = []

    def cli(self, project, command, payload=None, state=None):
        """A new isolated Python process exercises persisted restart truth."""
        argv = [sys.executable, "-I", "-B", str(SCRIPTS / "intake.py"),
                command, "--project-root", str(project)]
        if state is not None:
            argv += ["--expected-run-id", state["run_id"],
                     "--expected-revision", str(state["revision"])]
        result = subprocess.run(argv, input=b"" if payload is None else compact(payload),
                                capture_output=True, cwd=ROOT, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        self.assertNotIn(str(project).encode(), result.stdout + result.stderr)
        value = json.loads(result.stdout)
        self.trace.append(dict(command=command, response=value))
        self.assertEqual(value["failure_reason"], None, value)
        self.assertEqual(value["publication_status"], "current", value)
        self.assertEqual(value["html_path"], HTML_REL.as_posix())
        self.assertEqual(value["render_attempts"], 1)
        saved = load(project / STATE_REL)
        self.assertEqual(value["published"]["run_id"], saved["run_id"])
        self.assertEqual(value["published"]["revision"], saved["revision"])
        self.assertEqual(value["published"]["content_revision"], saved["content_revision"])
        if command != "retry-publication":
            self.assertEqual(value["commit_status"], "saved")
            if state is not None:
                self.assertEqual(saved["revision"], state["revision"] + 1)
                self.assertEqual(saved["content_revision"], state["content_revision"] + 1)
        return saved

    def capture(self, brief, native, retrieval, context_pack):
        interpretation = dict(copy.deepcopy(self.case["interpretation"]),
                              brief_sha256=digest(brief), brief_version=brief["brief_version"])
        connection_calls, sql = [], []
        real_connect = retrieval.sqlite3.connect

        def observe_connect(database, *args, **kwargs):
            connection_calls.append(dict(database=str(database), uri=kwargs.get("uri")))
            connection = real_connect(database, *args, **kwargs)
            connection.set_trace_callback(sql.append)
            return connection

        with mock.patch.object(retrieval.sqlite3, "connect", side_effect=observe_connect):
            guarded = native.prepare_from_brief(brief, interpretation)
            self.assertEqual(guarded["status"], "ready")
            query = guarded["catalog_query"]
            # The scenario requests one candidate/card, within canonical ceilings.
            query.update(self.case["request_caps"])
            retrieval.validate_query(query, manifest=load(ASSETS / "catalog.search-manifest.json"),
                                     policy=load(ASSETS / "retrieval-policy.json"))
            result = retrieval.retrieve(query, run_id=brief["run_id"],
                index_path=ASSETS / "catalog.search.sqlite",
                manifest_path=ASSETS / "catalog.search-manifest.json",
                policy_path=ASSETS / "retrieval-policy.json")
        self.assertTrue(connection_calls)
        self.assertTrue(all(item["uri"] is True and item["database"].endswith("?mode=ro&immutable=1")
                            for item in connection_calls))
        self.assertTrue(any("repository_fts MATCH" in statement and "bm25(" in statement for statement in sql))
        self.assertEqual(result["status"], "ok", result)
        expected = self.case["expected"]
        for key in ("source_mode", "retrieval_engine"):
            self.assertEqual(query[key], expected[key])
            self.assertEqual(result[key], expected[key])
        for key in ("card_schema_version", "index_format_version", "retrieval_policy_version"):
            self.assertEqual(result["pins"][key], expected[key])
        for key, value in expected["pins"].items():
            self.assertEqual(result["pins"][key], value)
        self.assertEqual([row["github_repository_id"] for row in result["candidates"]],
                         [expected["github_repository_id"]])
        self.assertTrue(all(type(row["github_repository_id"]) is int for row in result["candidates"]))
        self.assertIn("full_name", result["candidates"][0]["matched_fields"])
        snapshot = load(ASSETS / "catalog.snapshot.json")
        ids = {row["github_repository_id"] for row in result["candidates"]}
        cards = {card["identity"]["github_repository_id"]: card for card in snapshot["cards"]
                 if card["identity"]["github_repository_id"] in ids}
        pack = context_pack.build_evidence_pack(query, result, cards,
                    pack_id=f"cp11-pack-{brief['brief_version']}",
                    max_cards=query["max_cards"], max_evidence_bytes=query["max_evidence_bytes"])
        self.assertEqual(len(pack["cards"]), 1)
        self.assertEqual(pack["cards"][0]["card"]["identity"]["full_name"], expected["full_name"])
        self.assertEqual(pack["cards"][0]["eligibility"]["status"], "reference_only")
        self.assertIsNone(pack["cards"][0]["card"]["advisory"]["integration_surface"])
        request_schema = load(ROOT / "specs/recommendation/recommendation-request.schema.json")
        request = dict(schema_version="1.1.0", run_id=brief["run_id"],
            request_id=f"cp11-request-{brief['brief_version']}", brief_id=brief["brief_id"],
            brief_version=brief["brief_version"], query=query, pack_id=pack["pack_id"],
            output_intent="integration_handoff", execution_authorized_by_this_request=False,
            input_allocation=request_schema["properties"]["input_allocation"]["const"])
        memo = copy.deepcopy(self.case["memo_template"])
        memo.update(run_id=brief["run_id"], memo_id=f"cp11-memo-{brief['brief_version']}",
                    request_id=request["request_id"], brief_version=brief["brief_version"],
                    pack_id=pack["pack_id"], pins=copy.deepcopy(pack["pins"]))
        memo["integration_plan"].update(run_id=brief["run_id"], brief_version=brief["brief_version"],
                                        plan_id=f"cp11-plan-{brief['brief_version']}")
        # These are authored proposals bound to the observed capture, not model output.
        memo["integration_plan"]["evidence_refs"] = ["ev-catalog-card"]
        self.captures.append(dict(brief=copy.deepcopy(brief), brief_sha256=digest(brief), query_sha256=digest(query),
            request=request, retrieval=result, evidence_pack=pack, memo=memo,
            sqlite_connections=[dict(index="catalog.search.sqlite", uri=item["uri"],
                mode="ro", immutable=True) for item in connection_calls],
            sql_route=[statement for statement in sql if "repository_fts MATCH" in statement],
            bytes={"brief": len(compact(brief)), "request": len(compact(request)),
                   "pack": len(compact(pack)), "memo": len(compact(memo))}))
        return dict(request=request, retrieval=result, evidence_pack=pack), dict(memo=memo)

    def ready_context(self, project):
        """Reuse the same real writer/scanner/Brief wiring for failure cases."""
        _, scanner, context, _, _, _ = runtime()
        for name, content in self.case["project_files"].items():
            path = project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        state = self.cli(project, "start")
        state = self.cli(project, "answer", dict(answer_id="cp11-goal",
            question_id=state["intake"]["pending_question_id"], status="answered",
            value=self.case["goal"], ready=True), state)
        session = scanner.ScannerSession(project, state["run_id"])
        scanned = session.scan("standard")
        state = self.cli(project, "commit-scan", dict(report=scanned.report,
            checkpoint=session.export_checkpoint(state["revision"])), state)
        selected = context.select_context(scanned, brief_version=1,
            purpose="Evaluate an isolated invoice regression trial", goal_terms=("invoice", "test"))
        brief = context.build_project_context_brief(scanned.report, state["intake"],
            selected.selection, context.read_selected_context(session, selected), decision="evaluate")
        return self.cli(project, "commit-context", dict(selection=selected.selection, brief=brief), state)

    def test_saved_memo_render_failure_retry_and_newer_correction(self):
        """Publication failure cannot lose a memo or overwrite a newer correction."""
        intake, _, _, native, retrieval, context_pack = runtime()
        store = intake.store
        with tempfile.TemporaryDirectory(prefix="stackguide-cp11-recovery-") as folder:
            project = Path(folder)
            state = self.ready_context(project)
            matching, memo = self.capture(state["brief"], native, retrieval, context_pack)
            state = self.cli(project, "commit-matching", matching, state)
            old_html = (project / HTML_REL).read_bytes()
            intake._ACTIVE_ROOT = project  # Same process-local setup as intake.main, no state mutation.
            with mock.patch.object(store, "render_fixture", side_effect=store.StateError("render_failed")) as render:
                failed = intake.command_commit_memo(project, memo, state["run_id"], state["revision"])
            self.assertEqual(render.call_count, 1)
            self.assertEqual((failed["commit_status"], failed["failure_reason"], failed["retry"]),
                             ("saved", "render_failed", "render_only"))
            saved = load(project / STATE_REL)
            self.assertEqual(saved["memo"], memo["memo"])
            self.assertEqual(failed["saved"]["revision"], state["revision"] + 1)
            self.assertEqual((project / HTML_REL).read_bytes(), old_html)
            stable = (project / STATE_REL).read_bytes()
            saved = self.cli(project, "retry-publication", {}, saved)
            self.assertEqual((project / STATE_REL).read_bytes(), stable)
            self.assertEqual(failed["render_attempts"] + self.trace[-1]["response"]["render_attempts"], 2)
            original_renderer = store.render_fixture

            def newer_correction(captured, **kwargs):
                rendered = original_renderer(captured, **kwargs)
                with mock.patch.object(store, "render_fixture", original_renderer):
                    correction = intake.command_correct(project, dict(correction_id="cp11-render-race",
                        target="goal", value=self.case["correction"]), captured["run_id"], captured["revision"])
                self.assertEqual(correction["publication_status"], "current")
                return rendered

            with mock.patch.object(store, "render_fixture", side_effect=newer_correction):
                superseded = store.publish(project, saved)
            self.assertEqual((superseded["failure_reason"], superseded["retry"]), ("render_superseded", "stop"))
            corrected = load(project / STATE_REL)
            self.assertIsNone(corrected["memo"])
            self.assertEqual(corrected["intake"]["answers"], saved["intake"]["answers"])
            receipt = store.published_receipt(project / "docs/myai-stackguide")
            self.assertEqual(receipt["revision"], corrected["revision"])
            self.assertNotEqual((project / HTML_REL).read_bytes(), old_html)

    def test_checkpoint_crash_window_preserves_saved_answer_and_recovers(self):
        """A checkpoint written before a failed state commit is never restart truth."""
        intake, scanner, _, _, _, _ = runtime()
        with tempfile.TemporaryDirectory(prefix="stackguide-cp11-crash-") as folder:
            project = Path(folder)
            (project / "README.md").write_text("Synthetic checkpoint recovery", encoding="utf-8")
            state = self.cli(project, "start")
            state = self.cli(project, "answer", dict(answer_id="cp11-crash-answer",
                question_id=state["intake"]["pending_question_id"], status="answered",
                value=self.case["goal"], ready=True), state)
            state_bytes, html_bytes = (project / STATE_REL).read_bytes(), (project / HTML_REL).read_bytes()
            session = scanner.ScannerSession(project, state["run_id"])
            report = session.scan("standard")
            payload = dict(report=report.report, checkpoint=session.export_checkpoint(state["revision"]))
            with mock.patch.object(intake.store.LockedStore, "commit", side_effect=RuntimeError("synthetic crash before canonical replace")):
                with self.assertRaisesRegex(RuntimeError, "synthetic crash"):
                    intake.command_commit_scan(project, payload, state["run_id"], state["revision"])
            self.assertEqual((project / STATE_REL).read_bytes(), state_bytes)
            self.assertEqual((project / HTML_REL).read_bytes(), html_bytes)
            checkpoint = project / "docs/myai-stackguide/.scan-checkpoint.json"
            self.assertTrue(checkpoint.is_file())
            # New process exercises the real phase/revision-bound checkpoint loader.
            script = (
                "import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import scanner;"
                "root=Path(sys.argv[2]);state=json.loads((root/'docs/myai-stackguide/state.json').read_bytes());"
                "\ntry:\n scanner.load_checkpoint(root,state['run_id'],state['revision'])"
                "\nexcept scanner.ScannerError as error:\n print(error.reason);sys.exit(1)"
                "\nprint('checkpoint_restored')"
            )
            rejected = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(SCRIPTS), str(project)],
                                      capture_output=True, cwd=ROOT, timeout=20, check=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(rejected.stdout.strip(), b"checkpoint_revision_mismatch")
            self.assertEqual(rejected.stderr, b"")
            self.assertEqual((project / STATE_REL).read_bytes(), state_bytes)
            recovered = self.cli(project, "commit-scan", payload, state)
            self.assertEqual(recovered["intake"]["answers"], state["intake"]["answers"])
            restored = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(SCRIPTS), str(project)],
                                      capture_output=True, cwd=ROOT, timeout=20, check=False)
            self.assertEqual(restored.returncode, 0, restored.stderr.decode("utf-8", "replace"))

    def test_writer_state_budget_rejects_before_replacing_saved_answers(self):
        """Writer byte boundary only; the oversized candidate is not a valid domain payload."""
        intake, _, _, _, _, _ = runtime()
        store = intake.store
        with tempfile.TemporaryDirectory(prefix="stackguide-cp11-state-budget-") as folder:
            project = Path(folder)
            state = self.cli(project, "start")
            state = self.cli(project, "answer", dict(answer_id="cp11-budget-answer",
                question_id=state["intake"]["pending_question_id"], status="answered",
                value=self.case["goal"], ready=True), state)
            output = project / "docs/myai-stackguide"
            before = {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()}
            candidate = copy.deepcopy(state)
            candidate["revision"] += 1
            candidate["content_revision"] += 1
            intake._rebind_presentation(candidate, intake._load_question_bank())
            candidate["intake"]["assumptions"] = ["x" * (store.MAX_STATE_BYTES + 1)]
            self.assertGreater(len(compact(candidate)), store.MAX_STATE_BYTES)
            with store.locked_store(project, create=False) as writer:
                with self.assertRaises(store.StateError) as rejected:
                    writer.commit(candidate, state)
            self.assertEqual(rejected.exception.reason, "storage_limit")
            after = {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()}
            self.assertEqual(after, before)
            self.assertEqual(load(project / STATE_REL)["intake"]["answers"], state["intake"]["answers"])
            self.assertFalse(any("pending" in name for name in after))

    def test_useful_lifecycle(self):
        """Saved answers -> actual FTS5 -> correction -> restart -> immutable History."""
        intake, scanner, context, native, retrieval, context_pack = runtime()
        if str(ROOT / "evals/plugin-v1") not in sys.path:
            sys.path.insert(0, str(ROOT / "evals/plugin-v1"))
        evaluator = importlib.import_module("evaluate_vertical_slice")
        initial_sources = evaluator.source_bindings()
        manifest = load(ASSETS / "catalog.search-manifest.json")
        self.assertEqual(manifest["row_count"], self.case["expected"]["row_count"])
        index_before = hashlib.sha256((ASSETS / "catalog.search.sqlite").read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix="stackguide-cp11-") as folder:
            project = Path(folder)
            for name, content in self.case["project_files"].items():
                destination = project / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(content, encoding="utf-8")
            state = self.cli(project, "start")
            self.assertIsNone(state["brief"])
            self.assertIsNone(state["memo"])
            state = self.cli(project, "answer", dict(answer_id="cp11-goal",
                question_id=state["intake"]["pending_question_id"], status="answered",
                value=self.case["goal"], ready=True), state)
            session = scanner.ScannerSession(project, state["run_id"])
            scanned = session.scan("standard")
            state = self.cli(project, "commit-scan", dict(report=scanned.report,
                checkpoint=session.export_checkpoint(state["revision"])), state)
            selected = context.select_context(scanned, brief_version=1,
                purpose="Evaluate an isolated invoice regression trial", goal_terms=("invoice", "test"))
            transient = context.read_selected_context(session, selected)
            brief = context.build_project_context_brief(scanned.report, state["intake"],
                selected.selection, transient, decision="evaluate")
            state = self.cli(project, "commit-context", dict(selection=selected.selection, brief=brief), state)
            self.assertFalse((project / "docs/myai-stackguide/.scan-checkpoint.json").exists())
            matching, memo = self.capture(state["brief"], native, retrieval, context_pack)
            # Expected first RED: actual seams succeed above; the writer join is missing.
            self.assertTrue(callable(getattr(intake, "command_commit_matching", None)),
                            "CP-11 missing production join: actual retrieval cannot be saved through CP-07")
            self.assertTrue(callable(getattr(intake, "command_commit_memo", None)),
                            "CP-11 missing production join: a matching result cannot become a saved report")
            state = self.cli(project, "commit-matching", matching, state)
            self.assertEqual(state["phase"], "matching")
            self.assertIsNone(state["memo"])
            state = self.cli(project, "commit-memo", memo, state)
            self.assertEqual(state["phase"], "report")
            observations = copy.deepcopy(state["scan"])
            answers = copy.deepcopy(state["intake"]["answers"])
            old_brief_version = state["brief"]["brief_version"]
            state = self.cli(project, "correct", dict(correction_id="cp11-narrow-trial",
                target="goal", value=self.case["correction"]), state)
            self.assertEqual(state["phase"], "context_review")
            self.assertEqual(state["brief"]["brief_version"], old_brief_version + 1)
            self.assertEqual(state["brief"]["goal"], self.case["correction"])
            self.assertEqual(state["scan"], observations)
            self.assertEqual(state["intake"]["answers"], answers)
            for key in ("selection", "request", "retrieval", "evidence_pack", "memo"):
                self.assertIsNone(state[key], key)
            restart_bytes = (project / STATE_REL).read_bytes()
            state = self.cli(project, "retry-publication", {}, state)
            self.assertEqual((project / STATE_REL).read_bytes(), restart_bytes)
            matching, memo = self.capture(state["brief"], native, retrieval, context_pack)
            state = self.cli(project, "commit-matching", matching, state)
            state = self.cli(project, "commit-memo", memo, state)
            self.assertEqual(state["memo"]["integration_plan"]["execution_status"], "not_started")
            state = self.cli(project, "finalize", {}, state)
            self.assertEqual(state["status"], "finalized")
            history_path = project / f"docs/myai-stackguide/runs/{state['run_id']}.json"
            history_bytes = history_path.read_bytes()
            self.assertEqual(history_bytes, (project / STATE_REL).read_bytes())
            final_html = (project / HTML_REL).read_bytes()
            self.assertIn(b'data-locale="ru"', final_html)
            self.assertIn(b'data-locale="en"', final_html)
            self.assertIn(b"37489525", final_html)
            self.assertLessEqual(len(final_html), 5 * 1024 * 1024)
            self.assertLessEqual(len(history_bytes), 2 * 1024 * 1024)
            new_state = self.cli(project, "start")
            self.assertEqual(new_state["predecessor_run_id"], state["run_id"])
            self.assertEqual(new_state["history"], state["history"])
            self.assertEqual(history_path.read_bytes(), history_bytes)
            self.assertEqual(hashlib.sha256((ASSETS / "catalog.search.sqlite").read_bytes()).hexdigest(), index_before)
            for name, content in self.case["project_files"].items():
                self.assertEqual((project / name).read_text(encoding="utf-8"), content)
            if os.environ.get("CP11_EVIDENCE_ROOT"):
                target = Path(os.environ["CP11_EVIDENCE_ROOT"]).resolve()
                self.assertTrue(target.is_relative_to(ROOT / ".codex-tmp"), "evidence stays inside the assigned local lane")
                output = target / "docs/myai-stackguide"
                (output / "runs").mkdir(parents=True, exist_ok=True)
                (output / "state.json").write_bytes(history_bytes)
                (output / "status.html").write_bytes(final_html)
                shutil.copyfile(history_path, output / "runs" / history_path.name)
                (target / "successor-state.json").write_bytes(compact(new_state))
                self.assertEqual(evaluator.source_bindings(), initial_sources)
                artifacts = [STATE_REL.as_posix(), HTML_REL.as_posix(),
                             f"docs/myai-stackguide/runs/{state['run_id']}.json", "successor-state.json"]
                evidence = dict(schema_version="cp11_observed_c9_capture_v1", case_id=self.case["case_id"],
                    case_sha256=hashlib.sha256(CASE_PATH.read_bytes()).hexdigest(),
                    evidence_kind=self.case["evidence_kind"], evidence_ceiling=self.case["evidence_ceiling"],
                    manifest=manifest, captures=self.captures, lifecycle=self.trace, source_sha256=initial_sources,
                    artifact_sha256={name: hashlib.sha256((target / name).read_bytes()).hexdigest() for name in artifacts},
                    history_sha256=hashlib.sha256(history_bytes).hexdigest(), html_sha256=hashlib.sha256(final_html).hexdigest())
                (target / "lifecycle-evidence.json").write_bytes(compact(evidence))


if __name__ == "__main__":
    unittest.main()
