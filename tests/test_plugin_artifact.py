"""CP-10-A shell acceptance through the existing publication boundary."""

import copy
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins/myai-stackguide/scripts"
sys.path.insert(0, str(SCRIPTS))
import intake
import state_store as store
import render_report


class ArtifactShell(unittest.TestCase):
    def setUp(self):
        assets = SCRIPTS.parent / "assets"
        bank = json.loads((assets / "question-bank.json").read_text(encoding="utf-8"))
        manifest = json.loads((assets / "catalog.search-manifest.json").read_text(encoding="utf-8"))
        self.state = intake._new_state(bank, [], None, manifest)

    def test_saved_start_publishes_eight_views_without_memo(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            with store.locked_store(project, create=True) as writer:
                writer.commit(self.state, None)
            before = (project / store.OUTPUT_RELATIVE / store.STATE_NAME).read_bytes()
            result = store.publish(project, self.state)
            self.assertEqual(result["publication_status"], "current")
            html = (project / store.OUTPUT_RELATIVE / store.HTML_NAME).read_text(encoding="utf-8")
            for view in ("goal", "questions", "scan", "context", "options", "compare", "integration", "history"):
                self.assertIn(f'id="{view}"', html)
            self.assertIn('<noscript>', html)
            self.assertIn('data-locale="en"', html)
            self.assertEqual(before, (project / store.OUTPUT_RELATIVE / store.STATE_NAME).read_bytes())

    def test_saved_language_and_no_js_have_all_visible_sections(self):
        class Sections(HTMLParser):
            def __init__(self):
                super().__init__()
                self.sections = []

            def handle_starttag(self, tag, attrs):
                if tag == "section":
                    self.sections.append(dict(attrs))

        for locale in ("ru", "en"):
            self.state["presentation"]["default_locale"] = locale
            before = copy.deepcopy(self.state)
            rendered = store.render_fixture(self.state).decode("utf-8")
            self.assertIn(f'<html lang="{locale}">', rendered)
            parser = Sections()
            parser.feed(rendered)
            self.assertEqual(len(parser.sections), 8)
            self.assertTrue(all("hidden" not in section for section in parser.sections))
            self.assertNotIn("{{", rendered)
            self.assertEqual(before, self.state)

    def test_dictionary_gaps_fail_and_markup_is_escaped(self):
        with tempfile.TemporaryDirectory() as directory:
            assets = Path(directory)
            (assets / "locales").mkdir()
            for locale in ("ru", "en"):
                (assets / "locales" / f"{locale}.json").write_text('{}', encoding="utf-8")
            with self.assertRaises(ValueError):
                render_report.load_locales(assets)
        dictionaries = render_report.load_locales()
        hostile = '</script><img src=x onerror=alert(1)>'
        dictionaries["ru"]["goal"] = hostile
        with patch.object(render_report, "load_locales", return_value=dictionaries):
            result = render_report.render_report(self.state).decode("utf-8")
        self.assertNotIn(hostile, result)
        self.assertIn('&lt;/script&gt;&lt;img', result)
        self.assertNotIn('<script src=', result)
        self.assertNotIn('fetch(', result)
        self.assertNotIn('localStorage', result)

    def test_failure_preserves_html_and_late_render_cannot_replace_it(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            with store.locked_store(project, create=True) as writer:
                writer.commit(self.state, None)
            store.publish(project, self.state)
            path = project / store.OUTPUT_RELATIVE / store.HTML_NAME
            original_html = path.read_bytes()
            with patch.object(store, "render_fixture", side_effect=store.StateError("render_failed")):
                failed = store.publish(project, self.state)
            self.assertEqual(failed["retry"], "render_only")
            self.assertEqual(path.read_bytes(), original_html)
            original_renderer = store.render_fixture

            def advance_during_render(captured):
                rendered = original_renderer(captured)
                newer = copy.deepcopy(captured)
                newer["revision"] += 1
                with store.locked_store(project, create=False) as writer:
                    writer.commit(newer, captured)
                return rendered

            with patch.object(store, "render_fixture", side_effect=advance_during_render):
                late = store.publish(project, self.state)
            self.assertEqual(late["failure_reason"], "render_superseded")
            self.assertEqual(path.read_bytes(), original_html)

    def test_isolated_cli_start_uses_real_renderer(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [sys.executable, "-I", "-B", str(SCRIPTS / "intake.py"), "start", "--project-root", directory],
                capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8"))
            self.assertEqual(json.loads(completed.stdout)["publication_status"], "current")
            rendered = (Path(directory) / store.OUTPUT_RELATIVE / store.HTML_NAME).read_text(encoding="utf-8")
            self.assertIn('id="integration"', rendered)

    def test_committed_brief_and_scan_populate_first_four_views(self):
        corpus = json.loads((ROOT / "tests/fixtures/plugin_contracts.json").read_text(encoding="utf-8"))
        state = corpus["workspace_positive"]["artifact/project-artifact-state.schema.json"]
        markup = store.render_fixture(state).decode("utf-8")
        self.assertIn("Добавить локальный полнотекстовый поиск без сервиса.", markup)
        self.assertIn("What should improve in this project?", markup)
        self.assertIn("Add local search to a small Python project.", markup)
        self.assertIn("pyproject.toml", markup)
        self.assertIn("A narrow adapter may fit the existing project.", markup)
        self.assertIn("ev-project-manifest", markup)
        self.assertNotIn("Detailed content for this view is not implemented yet", markup.split('id="context"')[1].split("</section>")[0])

    def test_partial_scan_and_missing_translation_remain_explicit(self):
        corpus = json.loads((ROOT / "tests/fixtures/plugin_contracts.json").read_text(encoding="utf-8"))
        state = copy.deepcopy(corpus["workspace_positive"]["artifact/project-artifact-state.schema.json"])
        state["scan"]["status"] = "partial"
        state["scan"]["manifest"]["counters"]["topology_complete"] = False
        state["scan"]["reason_codes"] = ["topology_incomplete"]
        state["presentation"]["fields"] = [
            field for field in state["presentation"]["fields"] if field["field_pointer"] != "/brief/goal"
        ]
        markup = store.render_fixture(state).decode("utf-8")
        self.assertIn("topology_incomplete", markup)
        self.assertIn("Add local full-text search without a service.", markup)
        self.assertIn("data-source-lang=", markup)
        self.assertIn("data-translation-missing=", markup)
        state = copy.deepcopy(corpus["workspace_positive"]["artifact/project-artifact-state.schema.json"])
        forged = next(field for field in state["presentation"]["fields"]
                      if field["field_pointer"] == "/brief/goal")
        forged["source_sha256"] = "0" * 64
        with self.assertRaises(store.StateError) as error:
            store.render_fixture(state)
        self.assertEqual(error.exception.reason, "render_failed")

    def test_options_compare_integration_project_saved_sources(self):
        corpus = json.loads((ROOT / "tests/fixtures/plugin_contracts.json").read_text(encoding="utf-8"))
        state = copy.deepcopy(corpus["workspace_positive"]["artifact/project-artifact-state.schema.json"])
        memo = state["memo"]
        memo["comparison_details"] = {
            "scope": "Compare local search with no change.", "include_no_change": True,
            "cells": [{"criterion": "deployment", "github_repository_id": 900000001,
                       "baseline": False, "claim": {"kind": "inference", "text": "Local deployment may fit.",
                       "evidence_refs": ["ev-public-fit"], "answer_ids": [], "limitation": "API unverified."},
                       "next_check": "Check the package API."}],
            "selection_rationale": "Try one bounded adapter.",
            "strongest_counterargument": "The current lookup may suffice.",
            "reconsider_when": "If the API cannot fit.", "next_decision": "Approve a small experiment.",
        }
        plan = memo["integration_plan"]
        plan["details"]["diagram"] = {
            "status": "proposed", "nodes": [
                {"component_id": "existing", "label": "Existing lookup", "change": "reuse", "evidence_refs": ["ev-public-fit"]},
                {"component_id": "adapter", "label": "Search adapter", "change": "add", "evidence_refs": []},
            ], "edges": [{"from_component_id": "existing", "to_component_id": "adapter",
                         "label": "Proposed lookup call", "status": "proposed"}],
        }
        plan["details"]["validation_input"] = "One synthetic local record"
        plan["details"]["expected_behavior"] = "Return that record without network access"
        plan["details"]["widen_when"] = "Only after the first lookup is verified"
        markup = store.render_fixture(state).decode("utf-8")
        panels = {view: markup.split(f'id="{view}"', 1)[1].split("</section>", 1)[0]
                  for view in ("options", "compare", "integration")}
        for panel in panels.values():
            self.assertNotIn('data-i18n="pending_view"', panel)
        self.assertIn("stackguide-fixtures/embedded-search", panels["options"])
        self.assertIn("ev-public-fit", panels["options"])
        self.assertIn("The current lookup may suffice.", panels["compare"])
        self.assertIn("Proposed lookup call", panels["integration"])
        self.assertIn("One synthetic local record", panels["integration"])
        for value in ("stackguide-fixtures/embedded-search", "900000001", "ev-public-fit",
                      "The current lookup may suffice.", "Proposed lookup call",
                      "One synthetic local record", "not_executed", "separate_user_implementation_request"):
            self.assertIn(value, markup)
        self.assertIn('id="coding-handoff"', markup)
        state["presentation"]["default_locale"] = "en"
        english = store.render_fixture(state).decode("utf-8")
        self.assertIn('<html lang="en">', english)
        self.assertIn('data-i18n="candidate_roles">Candidate roles and evidence', english)
        self.assertIn('data-i18n="decision_matrix">Decision matrix', english)

    def test_missing_memo_keeps_c_views_unavailable(self):
        markup = store.render_fixture(self.state).decode("utf-8")
        for view in ("options", "compare", "integration"):
            panel = markup.split(f'id="{view}"', 1)[1].split("</section>", 1)[0]
            self.assertIn('data-i18n="missing"', panel)
        self.assertIn('data-i18n="no_memo"', markup.split('id="options"', 1)[1].split("</section>", 1)[0])

    def test_blocked_and_unassigned_pack_cards_are_not_promoted(self):
        corpus = json.loads((ROOT / "tests/fixtures/plugin_contracts.json").read_text(encoding="utf-8"))
        state = copy.deepcopy(corpus["workspace_positive"]["artifact/project-artifact-state.schema.json"])
        original = state["evidence_pack"]["cards"][0]
        original["eligibility"]["status"] = "blocked"
        extra = copy.deepcopy(original)
        extra["card"]["identity"]["github_repository_id"] = 900000002
        extra["card"]["identity"]["full_name"] = "stackguide-fixtures/unassigned"
        extra["eligibility"]["github_repository_id"] = 900000002
        state["evidence_pack"]["cards"].append(extra)
        markup = store.render_fixture(state).decode("utf-8")
        options = markup.split('id="options"', 1)[1].split("</section>", 1)[0]
        self.assertIn('data-i18n="blocked_candidate"', options)
        self.assertIn("stackguide-fixtures/unassigned", options)
        self.assertIn('data-i18n="unassigned_card"', options)


if __name__ == "__main__":
    unittest.main()
