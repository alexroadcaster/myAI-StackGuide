"""CP-08 bounded scanner and transient-context acceptance tests.

The suite exercises only disposable synthetic project roots.  It verifies the
public producer seam; CP-07 remains the sole state writer and currently has no
scan/context commit command for an integration assertion here.
"""

from __future__ import annotations

import importlib
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "myai-stackguide" / "scripts"
SCANNER_PATH = SCRIPTS / "scanner.py"
CONTEXT_PATH = SCRIPTS / "context.py"
POLICY_PATH = ROOT / "specs" / "scanner" / "scan-policy.yaml"
RUN_ID = "11111111-1111-4111-8111-111111111111"
CANARY = "STACKGUIDE_TEST_SECRET_7f4c2a90"


def load_runtime():
    if not (SCANNER_PATH.is_file() and CONTEXT_PATH.is_file()):
        return None, None
    scripts = str(SCRIPTS)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    scanner = importlib.import_module("scanner")
    return scanner, scanner.context


SCANNER, CONTEXT = load_runtime()


def write(root: Path, relative_path: str, content: str | bytes = "# synthetic\n") -> Path:
    path = root / Path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    return path


def serialized(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@unittest.skipUnless(SCANNER is not None and CONTEXT is not None, "CP-08 runtime is not implemented")
class PluginScannerTests(unittest.TestCase):
    maxDiff = None

    def session(self, root: Path, **kwargs):
        return SCANNER.ScannerSession(root, RUN_ID, **kwargs)

    def test_policy_consumption_default_and_explicit_modes(self):
        policy = SCANNER.load_policy(POLICY_PATH)
        self.assertEqual((policy["schema_version"], policy["policy_id"]), ("1.3.0", "local-scan-v1.3"))
        self.assertEqual(
            policy["modes"],
            {
                "quick": {"max_files": 2_000, "max_bytes": 268_435_456, "max_seconds": 120},
                "standard": {"max_files": 30_000, "max_bytes": 2_147_483_648, "max_seconds": 1_200},
                "deep": {"max_files": 100_000, "max_bytes": 8_589_934_592, "max_seconds": 4_000},
            },
        )
        self.assertEqual(
            policy["topology"],
            {
                "quick": {"max_entries": 50_000, "max_depth": 20, "max_seconds": 20},
                "standard": {"max_entries": 250_000, "max_depth": 40, "max_seconds": 90},
                "deep": {"max_entries": 1_000_000, "max_depth": 50, "max_seconds": 300},
            },
        )
        self.assertEqual(policy["max_file_bytes"], {"quick": 1_048_576, "standard": 2_097_152, "deep": 4_194_304})
        self.assertEqual(
            policy["targeted_context"],
            {
                "quick": {"max_files": 16, "max_read_bytes": 1_048_576, "max_model_context_bytes": 24_576},
                "standard": {"max_files": 64, "max_read_bytes": 8_388_608, "max_model_context_bytes": 49_152},
                "deep": {"max_files": 256, "max_read_bytes": 67_108_864, "max_model_context_bytes": 65_536},
                "charge_to_scan_budget": True,
                "persist_excerpts": False,
            },
        )
        self.assertEqual(policy["mode_budget_warning_fraction"], 0.8)
        self.assertEqual(
            policy["deep_checkpoint"],
            {"max_files_between_checkpoints": 2_000, "max_bytes_between_checkpoints": 268_435_456},
        )
        self.assertEqual(
            (policy["network"], policy["execute_project"], policy["install_dependencies"]),
            (False, False, False),
        )

        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-modes-") as directory:
            project = Path(directory)
            write(project, "README.md", "Synthetic project")
            default = self.session(project).scan()
            explicit = self.session(project).scan("quick")
            self.assertEqual(default.report["mode"], "standard")
            self.assertEqual(explicit.report["mode"], "quick")
            self.assertEqual(default.report["schema_version"], "1.1.0")
            self.assertEqual(default.report["policy_version"], "1.3.0")
            self.assertNotIn("standard", serialized(explicit.report))
            with self.assertRaises(SCANNER.ScannerError) as captured:
                self.session(project).scan("deep")
            self.assertEqual(captured.exception.reason, "deep_requires_material_gap")
            self.assertEqual(str(captured.exception), "scan operation failed")

    def test_cumulative_progression_is_bounded_and_never_automatic(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-cumulative-") as directory:
            project = Path(directory)
            for index in range(3):
                write(project, f"src/{index}.py", f"VALUE = {index}\n")
            session = self.session(
                project,
                limit_overrides={
                    "quick": {"max_files": 1},
                    "standard": {"max_files": 2},
                    "deep": {"max_files": 3},
                },
            )
            quick = session.scan("quick")
            standard = session.scan("standard")
            deep = session.scan(
                "deep", material_gap=True, explicit_confirmation=True
            )

            results = (quick, standard, deep)
            self.assertEqual([item.report["mode"] for item in results], ["quick", "standard", "deep"])
            self.assertEqual([item.report["manifest"]["counters"]["file_attempts"] for item in results], [1, 2, 3])
            self.assertTrue(all(item.report["run_id"] == RUN_ID for item in results))
            self.assertEqual(quick.report["status"], "partial")
            self.assertIn("budget_reached", quick.report["reason_codes"])
            self.assertNotEqual(quick.report["classification"], "idea_or_empty")
            self.assertEqual(standard.report["status"], "partial")
            self.assertIn("budget_reached", standard.report["reason_codes"])
            self.assertEqual(deep.report["status"], "complete")
            self.assertNotIn("budget_reached", deep.report["reason_codes"])
            self.assertLessEqual(len(serialized(deep.report).encode("utf-8")), 262_144)

            direct = self.session(
                project,
                limit_overrides={"quick": {"max_files": 1}, "deep": {"max_files": 3}},
            )
            direct_quick = direct.scan("quick")
            with self.assertRaises(SCANNER.ScannerError) as missing_gap:
                direct.scan("deep", material_gap=False, explicit_confirmation=True)
            self.assertEqual(missing_gap.exception.reason, "deep_requires_material_gap")
            with self.assertRaises(SCANNER.ScannerError) as missing_confirmation:
                direct.scan("deep", material_gap=True)
            self.assertEqual(missing_confirmation.exception.reason, "deep_requires_confirmation")
            direct_deep = direct.scan(
                "deep", material_gap=True, explicit_confirmation=True
            )
            self.assertEqual(
                (
                    direct_quick.report["manifest"]["counters"]["file_attempts"],
                    direct_deep.report["manifest"]["counters"]["file_attempts"],
                ),
                (1, 3),
            )
            self.assertEqual(direct_deep.report["run_id"], direct_quick.report["run_id"])

            standard_direct = self.session(
                project,
                limit_overrides={"standard": {"max_files": 1}, "deep": {"max_files": 3}},
            )
            standard_partial = standard_direct.scan("standard")
            self.assertEqual(standard_partial.report["status"], "partial")
            self.assertIn("budget_reached", standard_partial.report["reason_codes"])
            with self.assertRaises(SCANNER.ScannerError) as standard_unconfirmed:
                standard_direct.scan(
                    "deep", material_gap=True, explicit_confirmation=False
                )
            self.assertEqual(
                standard_unconfirmed.exception.reason, "deep_requires_confirmation"
            )
            standard_deep = standard_direct.scan(
                "deep", material_gap=True, explicit_confirmation=True
            )
            self.assertEqual(
                (
                    standard_partial.report["manifest"]["counters"]["file_attempts"],
                    standard_deep.report["manifest"]["counters"]["file_attempts"],
                ),
                (1, 3),
            )
            self.assertLessEqual(
                standard_partial.report["manifest"]["counters"]["bytes_consumed"],
                standard_deep.report["manifest"]["counters"]["bytes_consumed"],
            )
            self.assertEqual(
                standard_deep.report["run_id"], standard_partial.report["run_id"]
            )

    def test_topology_is_deterministic_and_condenses_cycles_before_generations(self):
        def graph():
            topology = CONTEXT.TypedTopology()
            for node_id, kind, path in (
                ("service-api", "service", "apps/api"),
                ("service-worker", "service", "apps/worker"),
                ("storage", "storage", "src/storage.py"),
                ("detached", "service", "apps/detached"),
            ):
                topology.add_node(node_id, kind=kind, relative_path=path, evidence_refs=(f"ev-{node_id}",))
            topology.add_edge("service-api", "service-worker", kind="depends_on", evidence_refs=("ev-edge-a",))
            topology.add_edge("service-worker", "service-api", kind="depends_on", evidence_refs=("ev-edge-b",))
            topology.add_edge("service-worker", "storage", kind="persists_to", evidence_refs=("ev-edge-c",))
            return topology

        first = graph()
        second = graph()
        self.assertEqual(first.weak_components(), second.weak_components())
        self.assertEqual(first.strong_components(), second.strong_components())
        self.assertEqual(
            {frozenset(component) for component in first.weak_components()},
            {frozenset(("service-api", "service-worker", "storage")), frozenset(("detached",))},
        )
        self.assertIn(frozenset(("service-api", "service-worker")), {frozenset(c) for c in first.strong_components()})
        condensation = first.condensation()
        cycle_id = condensation.component_of["service-api"]
        self.assertEqual(cycle_id, condensation.component_of["service-worker"])
        self.assertNotEqual(cycle_id, condensation.component_of["storage"])
        generations = first.topological_generations()
        self.assertEqual(generations, second.topological_generations())
        self.assertIn(("service-api", "service-worker"), generations[0])
        self.assertIn(("detached",), generations[0])
        self.assertIn(("storage",), generations[1])

    def test_goal_selection_uses_stable_path_ties_and_keeps_source_transient(self):
        marker = "GOAL_RELEVANT_SOURCE_MARKER"
        second_marker = "SECOND_GOAL_RELEVANT_SOURCE_MARKER"
        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-selection-") as directory:
            project = Path(directory)
            write(project, "README.md", "Synthetic search service")
            write(project, "src/a/search.py", f"{marker} = 'alpha search'\n" + "x = 'padding'\n" * 3000)
            write(project, "src/b/search.py", f"{second_marker} = 'beta search'\n")
            write(project, "src/z/unrelated.py", "UNRELATED = True\n")
            session = self.session(project)
            scan = session.scan("quick")
            before = scan.report["manifest"]["counters"].copy()
            selected = CONTEXT.select_context(
                scan,
                brief_version=1,
                purpose="Inspect the search integration surface",
                goal_terms=("search",),
            )
            self.assertIn("src/a/search.py", selected.ranked_paths)
            self.assertIn("src/b/search.py", selected.ranked_paths)
            self.assertLess(selected.ranked_paths.index("src/a/search.py"), selected.ranked_paths.index("src/b/search.py"))
            self.assertEqual(selected.selection["persistence"], "references_only")
            self.assertTrue(selected.selection["charge_to_scan_budget"])
            self.assertEqual(selected.remaining_budget["file_attempts"], 2_000 - before["file_attempts"])
            self.assertEqual(selected.remaining_budget["bytes"], 268_435_456 - before["bytes_consumed"])
            self.assertEqual(
                selected.remaining_budget["selected_files"],
                len(selected.selection["requested_sources"]),
            )
            self.assertLessEqual(selected.remaining_budget["selected_files"], 16)
            self.assertLessEqual(selected.remaining_budget["selected_read_bytes"], 1_048_576)
            self.assertNotIn(marker, serialized(scan.report))
            self.assertNotIn(marker, serialized(selected.selection))

            transient = CONTEXT.read_selected_context(session, selected)
            delivered = "\n".join(item.text for item in transient.items)
            self.assertIn(marker, delivered)
            self.assertIn(second_marker, delivered)
            self.assertGreaterEqual(len(transient.items), 2)
            self.assertGreater(transient.counters["file_attempts"], before["file_attempts"])
            self.assertGreater(transient.bytes_read, 0)
            self.assertLessEqual(transient.model_context_bytes, 24_576)
            self.assertNotIn("text", selected.selection)
            self.assertNotIn("excerpt", serialized(selected.selection).lower())

    def test_sensitive_sources_encoding_errors_and_project_code_never_leak_or_execute(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-sensitive-") as directory:
            project = Path(directory)
            marker = project / "PROJECT_CODE_EXECUTED"
            payload = (
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('executed')\n"
                "import socket, subprocess, sys\n"
                "socket.create_connection(('127.0.0.1', 9))\n"
                "subprocess.run([sys.executable, '-m', 'pip', 'install', 'stackguide-never-install'])\n"
            )
            write(project, "setup.py", payload)
            write(project, "src/worker.py", payload)
            write(project, "src/canary.py", f"api_key = {CANARY!r}\n")
            write(project, "src/bad.py", b"\xff\xfe\x00")
            write(project, ".env", f"TOKEN={CANARY}\n")
            write(project, "secrets/credentials.json", f'{{"token":"{CANARY}"}}')
            write(project, "logs/debug.txt", CANARY)
            write(project, "docs/myai-stackguide/state.json", f'{{"raw":"{CANARY}"}}')

            result = self.session(project).scan("standard")
            output = serialized(result.report)
            self.assertFalse(marker.exists())
            self.assertNotIn(CANARY, output)
            self.assertNotIn(str(project), output)
            self.assertNotIn("credentials.json", result.eligible_paths)
            self.assertNotIn("debug.txt", result.eligible_paths)
            self.assertNotIn("docs/myai-stackguide/state.json", result.eligible_paths)
            canary_record = next(
                item for item in result.report["manifest"]["files"]
                if item["relative_path"] == "src/canary.py"
            )
            self.assertEqual(canary_record["disposition"], "unread")
            self.assertIsNone(canary_record["evidence_ref"])
            self.assertGreater(result.report["manifest"]["excluded_counts"]["sensitive"], 0)
            self.assertGreater(result.report["manifest"]["excluded_counts"]["generated"], 0)
            self.assertIn("excluded_sources", result.report["reason_codes"])
            self.assertIn("encoding_error", result.report["reason_codes"])

    def test_supported_links_and_hardlinks_cannot_escape_selected_root(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-links-") as directory:
            outer = Path(directory)
            project = outer / "project"
            project.mkdir()
            outside = write(outer, "outside.py", f"VALUE = {CANARY!r}\n")
            write(project, "src/safe.py", "SAFE = True\n")
            attempted: list[str] = []
            try:
                os.link(outside, project / "src/hardlink.py")
                attempted.append("src/hardlink.py")
            except OSError:
                pass
            try:
                os.symlink(outside, project / "src/symlink.py")
                attempted.append("src/symlink.py")
            except OSError:
                pass
            if not attempted:
                self.skipTest("this filesystem permits neither test hardlinks nor test symlinks")

            result = self.session(project).scan("standard")
            for relative_path in attempted:
                self.assertNotIn(relative_path, result.eligible_paths)
            self.assertIn("src/safe.py", result.eligible_paths)
            self.assertNotIn(CANARY, serialized(result.report))
            self.assertGreater(result.report["manifest"]["excluded_counts"]["unsafe_path"], 0)

    def test_reviewer_regressions_for_continuation_merging_and_minimization(self):
        class StepClock:
            def __init__(self, step: float = 0.2) -> None:
                self.value = 0.0
                self.step = step

            def __call__(self) -> float:
                self.value += self.step
                return self.value

        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-topology-time-") as directory:
            project = Path(directory)
            for index in range(10):
                write(project, f"services/{index}/main.py", f"SERVICE = {index}\n")
            session = self.session(
                project,
                clock=StepClock(),
                limit_overrides={
                    "quick": {"topology_max_seconds": 1},
                    "standard": {"topology_max_seconds": 1},
                },
            )
            quick = session.scan("quick")
            quick_entries = quick.report["manifest"]["counters"]["visited_entries"]
            self.assertIn("topology_incomplete", quick.report["reason_codes"])
            standard = session.scan("standard")
            self.assertEqual(
                standard.report["manifest"]["counters"]["visited_entries"],
                quick_entries,
                "continuation must not reset an already exhausted cumulative topology-time budget",
            )
            self.assertIn("topology_incomplete", standard.report["reason_codes"])

        for continuation in ("standard", "deep"):
            with self.subTest(depth_continuation=continuation), tempfile.TemporaryDirectory(
                prefix=f"stackguide-cp08-depth-{continuation}-"
            ) as directory:
                project = Path(directory)
                write(project, "a/b/deep.py", "DEEP = True\n")
                session = self.session(
                    project,
                    limit_overrides={
                        "quick": {"topology_max_depth": 1},
                        continuation: {"topology_max_depth": 4},
                    },
                )
                quick = session.scan("quick")
                self.assertNotIn("a/b/deep.py", quick.eligible_paths)
                self.assertIn("topology_incomplete", quick.report["reason_codes"])
                continued = session.scan(
                    continuation,
                    material_gap=continuation == "deep",
                    explicit_confirmation=continuation == "deep",
                )
                self.assertIn("a/b/deep.py", continued.eligible_paths)

        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-manifest-merge-") as directory:
            project = Path(directory)
            write(project, "package.json", '{"name":"root-js","dependencies":{}}')
            write(project, "pyproject.toml", '[project]\nname = "root-python"\ndependencies = []\n')
            result = self.session(project).scan("standard")
            manifest_evidence = {
                item["evidence_ref"] for item in result.report["manifest"]["files"]
                if item["relative_path"] in {"package.json", "pyproject.toml"}
            }
            self.assertEqual(len(manifest_evidence), 2)
            root_services = [
                node for node in result.topology.nodes.values()
                if node.kind == "service" and node.label == "root"
            ]
            self.assertEqual(len(root_services), 1)
            self.assertEqual(set(root_services[0].evidence_refs), manifest_evidence)

        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-join-order-") as directory:
            project = Path(directory)
            source_root = project / "src"
            source_root.mkdir()
            for index in range(501):
                (source_root / f"f{index:04d}.py").touch()
            result = self.session(project).scan("standard")
            manifest = result.report["manifest"]
            evidence = result.report["summary"]["evidence"]
            self.assertGreater(manifest["counters"]["eligible_files"], 500)
            manifest_by_ref = {
                item["evidence_ref"]: item["relative_path"]
                for item in manifest["files"]
                if item["evidence_ref"] is not None
            }
            evidence_by_ref = {
                item["evidence_id"]: item for item in evidence
            }
            joined_refs = set(manifest_by_ref) & set(evidence_by_ref)
            self.assertGreater(len(joined_refs), 1)
            manifest_order = [
                item["evidence_ref"] for item in manifest["files"]
                if item["evidence_ref"] in joined_refs
            ]
            evidence_order = [
                item["evidence_id"] for item in evidence
                if item["evidence_id"] in joined_refs
            ]
            self.assertNotEqual(manifest_order, evidence_order)
            for evidence_ref in joined_refs:
                self.assertEqual(
                    evidence_by_ref[evidence_ref]["relative_path"],
                    manifest_by_ref[evidence_ref],
                )
                self.assertFalse(evidence_by_ref[evidence_ref]["content_persisted"])
            selected = CONTEXT.select_context(
                result,
                brief_version=1,
                purpose="Select scan-backed sources despite reordered evidence",
                goal_terms=("src",),
            )
            self.assertTrue(selected.ranked_paths)
            self.assertTrue(
                set(selected.ranked_paths)
                <= set(result.observed_paths)
            )
            self.assertGreater(
                len(selected.ranked_paths),
                len(joined_refs),
                "targeted selection must not be capped by the minimized public evidence sample",
            )

        tokens = (
            "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            "sk-proj-ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        )
        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-token-minimization-") as directory:
            project = Path(directory)
            write(project, "README.md", "Synthetic dependency project")
            write(
                project,
                "package.json",
                serialized({"name": "root-app", "dependencies": {token: "1.0.0" for token in tokens}}),
            )
            for index, token in enumerate(tokens):
                write(
                    project,
                    f"packages/internal-{index}/package.json",
                    serialized({"name": token, "version": "1.0.0"}),
                )
            result = self.session(project).scan("standard")
            report_text = serialized(result.report)
            for token in tokens:
                with self.subTest(hostile_manifest_token=token):
                    self.assertNotIn(token, report_text)
                    self.assertTrue(
                        all(token not in fact["value"] for fact in result.report["summary"]["facts"])
                    )
                    self.assertTrue(
                        all(node.label is None or token not in node.label for node in result.topology.nodes.values())
                    )
            with self.assertRaises(CONTEXT.ContextError) as captured:
                CONTEXT.select_context(
                    result,
                    brief_version=1_000_001,
                    purpose="Reject out-of-contract Brief versions",
                    goal_terms=("dependency",),
                )
            self.assertEqual(captured.exception.reason, "invalid_brief_version")

    def test_checkpoint_resume_identity_and_brief_references_only(self):
        limits = {"quick": {"max_files": 1}, "deep": {"max_files": 4}}
        source_marker = "SOURCE_ONLY_BRIEF_MARKER_91d2"
        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-checkpoint-") as directory:
            project = Path(directory)
            write(project, "README.md", "Synthetic checkpoint project")
            write(project, "src/a.py", "A = 1\n")
            write(project, "src/b.py", f"VALUE = {source_marker!r}\n")
            write(project, "src/c.py", f"api_key = {CANARY!r}\n")
            write(project, "secrets/hidden.py", "IGNORED = True\n")
            session = self.session(project, limit_overrides=limits)
            quick = session.scan("quick")
            checkpoint = session.export_checkpoint(expected_state_revision=7)
            checkpoint_text = serialized(checkpoint)
            checkpoint_schema = json.loads(
                (ROOT / "specs/scanner/scanner-restart-checkpoint.schema.json").read_text(encoding="utf-8")
            )
            checkpoint_session_schema = checkpoint_schema["$defs"]["session"]
            self.assertEqual(
                set(checkpoint["session"]),
                set(checkpoint_session_schema["required"]),
            )
            self.assertEqual(
                set(checkpoint_session_schema["required"]),
                set(checkpoint_session_schema["properties"]),
            )
            legacy_checkpoint = json.loads(checkpoint_text)
            legacy_checkpoint["policy_id"] = "local-scan-v1.1"
            legacy_checkpoint["policy_version"] = "1.1.0"
            legacy_checkpoint["last_report"]["policy_version"] = "1.1.0"
            legacy_checkpoint["last_report"]["manifest"]["policy_version"] = "1.1.0"
            with self.assertRaises(SCANNER.ScannerError) as legacy_policy:
                SCANNER.ScannerSession.from_checkpoint(
                    project, RUN_ID, legacy_checkpoint, limit_overrides=limits
                )
            self.assertEqual(legacy_policy.exception.reason, "checkpoint_invalid")
            legacy_sidecar = json.loads(checkpoint_text)
            legacy_sidecar["schema_version"] = "1.0.0"
            with self.assertRaises(SCANNER.ScannerError) as legacy_schema:
                SCANNER.ScannerSession.from_checkpoint(
                    project, RUN_ID, legacy_sidecar, limit_overrides=limits
                )
            self.assertEqual(legacy_schema.exception.reason, "checkpoint_invalid")
            self.assertNotIn(CANARY, checkpoint_text)
            self.assertNotIn(source_marker, checkpoint_text)
            self.assertNotIn("excerpt", checkpoint_text.casefold())
            self.assertNotIn("raw_source", checkpoint_text)
            self.assertNotIn('"topology":', checkpoint_text)
            self.assertNotIn("secrets/hidden.py", checkpoint_text)
            output_root = project / "docs/myai-stackguide"
            self.assertFalse(output_root.exists(), "export_checkpoint must remain pure until CP-07 commit-scan")

            restored = SCANNER.ScannerSession.from_checkpoint(
                project, RUN_ID, checkpoint, limit_overrides=limits
            )
            restored_quick = restored.scan("quick")
            for key in ("visited_entries", "file_attempts", "bytes_consumed"):
                self.assertEqual(
                    restored_quick.report["manifest"]["counters"][key],
                    quick.report["manifest"]["counters"][key],
                )
            continued = restored.scan(
                "deep", material_gap=True, explicit_confirmation=True
            )
            self.assertGreaterEqual(
                continued.report["manifest"]["counters"]["file_attempts"],
                quick.report["manifest"]["counters"]["file_attempts"],
            )

            with tempfile.TemporaryDirectory(prefix="stackguide-cp08-wrong-root-") as other:
                with self.assertRaises(SCANNER.ScannerError) as wrong_root:
                    SCANNER.ScannerSession.from_checkpoint(
                        Path(other), RUN_ID, checkpoint, limit_overrides=limits
                    )
                self.assertEqual(wrong_root.exception.reason, "checkpoint_root_mismatch")
            with self.assertRaises(SCANNER.ScannerError) as wrong_run:
                SCANNER.ScannerSession.from_checkpoint(
                    project,
                    "22222222-2222-4222-8222-222222222222",
                    checkpoint,
                    limit_overrides=limits,
                )
            self.assertEqual(wrong_run.exception.reason, "checkpoint_run_mismatch")
            with self.assertRaises(SCANNER.ScannerError) as wrong_policy:
                SCANNER.ScannerSession.from_checkpoint(project, RUN_ID, checkpoint)
            self.assertEqual(wrong_policy.exception.reason, "checkpoint_policy_mismatch")

        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-large-checkpoint-") as directory:
            project = Path(directory)
            source_root = project / "src"
            source_root.mkdir()
            for index in range(5_501):
                (source_root / f"f{index:04d}.py").touch()
            session = self.session(project)
            quick = session.scan("quick")
            self.assertEqual(quick.report["status"], "partial")
            deep = session.scan(
                "deep", material_gap=True, explicit_confirmation=True
            )
            checkpoint = session.export_checkpoint(expected_state_revision=7)
            self.assertLessEqual(
                len(serialized(checkpoint).encode("utf-8")), 67_108_864
            )
            checkpoint_inventory = {
                item["relative_path"]
                for item in checkpoint["session"]["candidate_files"]
            } | {
                item["relative_path"] for item in checkpoint["session"]["records"]
            }
            self.assertGreater(len(checkpoint_inventory), 5_500)
            self.assertGreater(len(checkpoint["session"]["records"]), 5_500)
            self.assertEqual(checkpoint["session"]["read_paths"], [])
            self.assertEqual(
                sum(
                    item["disposition"] == "read"
                    for item in checkpoint["session"]["records"]
                ),
                deep.report["manifest"]["counters"]["file_attempts"],
            )

            restored = SCANNER.ScannerSession.from_checkpoint(
                project, RUN_ID, checkpoint
            )
            roundtrip = restored.export_checkpoint(expected_state_revision=7)
            for key in ("candidate_files", "records", "read_paths"):
                self.assertEqual(roundtrip["session"][key], checkpoint["session"][key])
            for key in (
                "visited_entries",
                "file_attempts",
                "bytes_consumed",
                "active_seconds",
                "topology_seconds",
            ):
                self.assertEqual(roundtrip["session"][key], checkpoint["session"][key])
            self.assertEqual(roundtrip["last_report"], checkpoint["last_report"])

        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-brief-") as directory:
            project = Path(directory)
            write(project, "README.md", "Synthetic API integration")
            write(project, "src/api.py", f"{source_marker} = True\n@app.get('/items')\ndef items():\n    return []\n")
            session = self.session(project)
            scan = session.scan("standard")
            selected = CONTEXT.select_context(
                scan,
                brief_version=1,
                purpose="Build a referenced project Brief",
                goal_terms=("api", "integration"),
            )
            transient = CONTEXT.read_selected_context(session, selected)
            self.assertIn(source_marker, "\n".join(item.text for item in transient.items))
            fixtures = json.loads(
                (ROOT / "tests/fixtures/plugin_contracts.json").read_text(encoding="utf-8")
            )
            intake = fixtures["workspace_positive"]["intake/intake-state.schema.json"]
            brief = CONTEXT.build_project_context_brief(
                scan.report,
                intake,
                selected.selection,
                transient,
                decision="evaluate",
                updated_at="2026-09-21T12:00:00Z",
            )
            brief_text = serialized(brief)
            self.assertEqual(brief["observations"], scan.report["summary"])
            self.assertIsInstance(brief["observations"]["facts"], list)
            self.assertIsInstance(brief["observations"]["inferences"], list)
            self.assertEqual(brief["user_corrections"], [])
            self.assertTrue(all(not item["content_persisted"] for item in brief["observations"]["evidence"]))
            self.assertNotIn(source_marker, brief_text)
            self.assertNotIn(CANARY, brief_text)
            self.assertNotIn("raw_source", brief_text)
            self.assertNotIn('"excerpt"', brief_text.casefold())
            self.assertEqual(selected.selection["persistence"], "references_only")

    def test_checkpoint_scales_to_100k_and_restores_in_fresh_process(self):
        with tempfile.TemporaryDirectory(prefix="stackguide-cp08-100k-checkpoint-") as directory:
            project = Path(directory)
            write(project, "README.md", "Synthetic checkpoint capacity fixture")
            session = self.session(project)
            initial = session.scan("standard")

            records = {}
            candidates = {}
            read_paths = set()
            for index in range(100_000):
                relative_path = f"src/f{index:06d}.py"
                evidence_ref = SCANNER._evidence_id(relative_path)
                records[relative_path] = SCANNER._FileRecord(
                    relative_path, 1, "source", "read", evidence_ref
                )
                candidates[relative_path] = (project / relative_path, 1, "source")
                read_paths.add(relative_path)

            session._records = records
            session._candidate_files = candidates
            session._read_paths = read_paths
            session._mode = "deep"
            session._file_attempts = 100_000
            session._bytes_consumed = 100_000
            session._visited_entries = 100_001
            session._checkpoints = [
                {
                    "file_attempts": value,
                    "bytes_consumed": value,
                    "elapsed_ms": value,
                }
                for value in range(2_000, 100_001, 2_000)
            ]
            session._last_checkpoint_files = 100_000
            session._last_checkpoint_bytes = 100_000
            report = json.loads(serialized(initial.report))
            report["mode"] = "deep"
            report["status"] = "partial"
            report["classification"] = "large_or_monorepo"
            report["manifest"]["mode"] = "deep"
            report["manifest"]["files"] = []
            report["manifest"]["counters"].update(
                visited_entries=100_001,
                file_attempts=100_000,
                bytes_consumed=100_000,
                eligible_files=100_000,
                budget_reached=True,
                topology_complete=False,
            )
            report["summary"]["coverage"] = "partial"
            report["summary"]["facts"] = []
            report["summary"]["inferences"] = []
            report["summary"]["evidence"] = []
            report["summary"]["gaps"] = [{
                "code": "coverage_partial",
                "detail": "The bounded scan did not observe every policy-relevant source.",
                "next_check": "Review reason codes and explicitly continue with a permitted higher mode only if useful.",
            }]
            report["reason_codes"] = ["budget_reached", "topology_incomplete"]
            session._last_report = report

            checkpoint = session.export_checkpoint(expected_state_revision=7)
            checkpoint_bytes = len(serialized(checkpoint).encode("utf-8"))
            self.assertGreater(checkpoint_bytes, 2_097_152)
            self.assertLessEqual(checkpoint_bytes, SCANNER.MAX_CHECKPOINT_BYTES)
            output_root = project / "docs/myai-stackguide"
            output_root.mkdir(parents=True)
            SCANNER.write_checkpoint_locked(output_root, checkpoint)

            del session, records, candidates, read_paths, checkpoint
            gc.collect()
            child_code = (
                "import json,sys; from pathlib import Path; "
                f"sys.path.insert(0,{str(SCRIPTS)!r}); import scanner; "
                "root=Path(sys.argv[1]); out=Path(sys.argv[2]); run_id=sys.argv[3]; "
                "checkpoint=scanner.read_checkpoint_locked(out); "
                "restored=scanner.ScannerSession.from_checkpoint(root,run_id,checkpoint); "
                "print(json.dumps({'schema_version':checkpoint['schema_version'],"
                "'file_attempts':restored._file_attempts,'records':len(restored._records)}))"
            )
            completed = subprocess.run(
                [sys.executable, "-B", "-c", child_code, str(project), str(output_root), RUN_ID],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=120,
            )
            self.assertEqual(
                completed.returncode,
                0,
                completed.stderr.decode("utf-8", errors="replace"),
            )
            restored = json.loads(completed.stdout.decode("utf-8"))
            self.assertEqual(
                restored,
                {"schema_version": "1.1.0", "file_attempts": 100_000, "records": 100_000},
            )


if __name__ == "__main__":
    unittest.main()
