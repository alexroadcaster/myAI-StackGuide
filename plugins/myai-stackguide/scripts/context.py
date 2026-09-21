"""Transient CP-08 topology and bounded context-selection helpers.

Only ``ContextSelectionResult.selection`` is suitable for persistence.  Graphs,
ranked paths, and source excerpts are process-local aids and deliberately have no
serialization helper.
"""

from __future__ import annotations

from collections import deque
import copy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import PurePosixPath
import re
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "1.1.0"
POLICY_VERSION = "1.3.0"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_WORD = re.compile(r"[^\W_][\w.+#-]*", re.UNICODE)


class ContextError(ValueError):
    """A safe, typed context operation failure."""

    def __init__(self, reason: str) -> None:
        super().__init__("context operation failed")
        self.reason = reason


@dataclass(frozen=True, slots=True)
class TopologyNode:
    node_id: str
    kind: str
    relative_path: str | None
    label: str | None
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TopologyEdge:
    source: str
    target: str
    kind: str
    status: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Condensation:
    graph: "TypedTopology"
    members: dict[str, tuple[str, ...]]
    component_of: dict[str, str]


class TypedTopology:
    """Small deterministic directed multigraph implemented with stdlib only."""

    def __init__(self) -> None:
        self.nodes: dict[str, TopologyNode] = {}
        self._edges: set[TopologyEdge] = set()

    @property
    def edges(self) -> tuple[TopologyEdge, ...]:
        return tuple(
            sorted(
                self._edges,
                key=lambda edge: (
                    edge.source,
                    edge.target,
                    edge.kind,
                    edge.status,
                    edge.evidence_refs,
                ),
            )
        )

    def add_node(
        self,
        node_id: str,
        *,
        kind: str,
        relative_path: str | None = None,
        label: str | None = None,
        evidence_refs: Iterable[str] = (),
    ) -> TopologyNode:
        if not isinstance(node_id, str) or not _ID.fullmatch(node_id):
            raise ContextError("invalid_node")
        if not isinstance(kind, str) or not kind or len(kind) > 64:
            raise ContextError("invalid_node")
        if relative_path is not None and (not isinstance(relative_path, str) or not relative_path):
            raise ContextError("invalid_node")
        if label is not None and (not isinstance(label, str) or not label or len(label) > 240):
            raise ContextError("invalid_node")
        refs = tuple(sorted(set(evidence_refs)))
        node = TopologyNode(node_id, kind, relative_path, label, refs)
        existing = self.nodes.get(node_id)
        if existing is not None:
            if (
                existing.kind != kind
                or existing.relative_path != relative_path
                or existing.label != label
            ):
                raise ContextError("node_conflict")
            node = TopologyNode(
                node_id,
                kind,
                relative_path,
                label,
                tuple(sorted(set(existing.evidence_refs) | set(refs))),
            )
        self.nodes[node_id] = node
        return node

    def add_edge(
        self,
        source: str,
        target: str,
        *,
        kind: str,
        status: str = "observed",
        evidence_refs: Iterable[str] = (),
    ) -> TopologyEdge:
        if source not in self.nodes or target not in self.nodes:
            raise ContextError("unknown_node")
        if not isinstance(kind, str) or not kind or len(kind) > 64:
            raise ContextError("invalid_edge")
        if status not in ("observed", "inferred"):
            raise ContextError("invalid_edge")
        edge = TopologyEdge(source, target, kind, status, tuple(sorted(set(evidence_refs))))
        self._edges.add(edge)
        return edge

    def _adjacency(self, *, reverse: bool = False, undirected: bool = False) -> dict[str, set[str]]:
        adjacent = {node_id: set() for node_id in self.nodes}
        for edge in self._edges:
            left, right = (edge.target, edge.source) if reverse else (edge.source, edge.target)
            adjacent[left].add(right)
            if undirected:
                adjacent[right].add(left)
        return adjacent

    @staticmethod
    def _stable_components(components: Iterable[Iterable[str]]) -> tuple[tuple[str, ...], ...]:
        values = [tuple(sorted(component)) for component in components]
        return tuple(sorted(values, key=lambda item: (item[0] if item else "", item)))

    def weak_components(self) -> tuple[tuple[str, ...], ...]:
        adjacent = self._adjacency(undirected=True)
        unseen = set(self.nodes)
        components: list[tuple[str, ...]] = []
        while unseen:
            first = min(unseen)
            queue = deque((first,))
            unseen.remove(first)
            component: list[str] = []
            while queue:
                current = queue.popleft()
                component.append(current)
                for target in sorted(adjacent[current]):
                    if target in unseen:
                        unseen.remove(target)
                        queue.append(target)
            components.append(tuple(component))
        return self._stable_components(components)

    def strong_components(self) -> tuple[tuple[str, ...], ...]:
        adjacent = self._adjacency()
        reverse = self._adjacency(reverse=True)
        visited: set[str] = set()
        finish_order: list[str] = []
        for node_id in sorted(self.nodes):
            if node_id in visited:
                continue
            visited.add(node_id)
            stack: list[tuple[str, bool]] = [(node_id, False)]
            while stack:
                current, exiting = stack.pop()
                if exiting:
                    finish_order.append(current)
                    continue
                stack.append((current, True))
                for target in reversed(sorted(adjacent[current])):
                    if target not in visited:
                        visited.add(target)
                        stack.append((target, False))
        assigned: set[str] = set()
        components: list[tuple[str, ...]] = []
        for node_id in reversed(finish_order):
            if node_id in assigned:
                continue
            assigned.add(node_id)
            component: list[str] = []
            stack = [(node_id, False)]
            while stack:
                current, _ = stack.pop()
                component.append(current)
                for target in reversed(sorted(reverse[current])):
                    if target not in assigned:
                        assigned.add(target)
                        stack.append((target, False))
            components.append(tuple(component))
        return self._stable_components(components)

    def condensation(self) -> Condensation:
        graph = TypedTopology()
        members: dict[str, tuple[str, ...]] = {}
        component_of: dict[str, str] = {}
        for ordinal, component in enumerate(self.strong_components()):
            component_id = f"scc-{ordinal:06d}"
            members[component_id] = component
            graph.add_node(component_id, kind="component", label=",".join(component)[:240])
            for node_id in component:
                component_of[node_id] = component_id
        for edge in self.edges:
            source = component_of[edge.source]
            target = component_of[edge.target]
            if source != target:
                graph.add_edge(
                    source,
                    target,
                    kind=edge.kind,
                    status=edge.status,
                    evidence_refs=edge.evidence_refs,
                )
        return Condensation(graph=graph, members=members, component_of=component_of)

    def topological_generations(self) -> tuple[tuple[tuple[str, ...], ...], ...]:
        condensed = self.condensation()
        adjacent = condensed.graph._adjacency()
        indegree = {node_id: 0 for node_id in condensed.graph.nodes}
        for source in adjacent:
            for target in adjacent[source]:
                indegree[target] += 1
        remaining = set(indegree)
        generations: list[tuple[tuple[str, ...], ...]] = []
        while remaining:
            ready = tuple(sorted(node_id for node_id in remaining if indegree[node_id] == 0))
            if not ready:
                raise ContextError("topology_cycle")
            generations.append(tuple(condensed.members[node_id] for node_id in ready))
            for node_id in ready:
                remaining.remove(node_id)
                for target in adjacent[node_id]:
                    indegree[target] -= 1
        return tuple(generations)

    def bounded_reachable(
        self,
        seeds: Iterable[str],
        *,
        direction: str = "both",
        max_nodes: int = 1024,
    ) -> tuple[str, ...]:
        if direction not in ("ancestors", "descendants", "both") or max_nodes < 1:
            raise ContextError("invalid_traversal")
        seed_values = tuple(sorted(set(seeds)))
        if any(seed not in self.nodes for seed in seed_values):
            raise ContextError("unknown_node")
        forward = self._adjacency()
        reverse = self._adjacency(reverse=True)
        queue = deque(seed_values)
        visited: set[str] = set()
        while queue and len(visited) < max_nodes:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            neighbours: set[str] = set()
            if direction in ("descendants", "both"):
                neighbours.update(forward[current])
            if direction in ("ancestors", "both"):
                neighbours.update(reverse[current])
            for target in sorted(neighbours):
                if target not in visited:
                    queue.append(target)
        return tuple(sorted(visited))


@dataclass(frozen=True, slots=True)
class ContextSelectionResult:
    selection: dict[str, Any]
    ranked_paths: tuple[str, ...]
    remaining_budget: dict[str, int]


@dataclass(frozen=True, slots=True)
class ContextExcerpt:
    relative_path: str
    text: str
    line_start: int | None
    line_end: int | None


@dataclass(frozen=True, slots=True)
class TransientContext:
    items: tuple[ContextExcerpt, ...]
    bytes_read: int
    model_context_bytes: int
    truncated: bool
    reason_codes: tuple[str, ...]
    counters: dict[str, int]


def _terms(value: str | Iterable[str]) -> tuple[str, ...]:
    values = (value,) if isinstance(value, str) else tuple(value)
    return tuple(sorted({match.group(0).casefold() for item in values for match in _WORD.finditer(item)}))


def _path_priority(path: str) -> int:
    name = path.rsplit("/", 1)[-1].casefold()
    if name in {
        "package.json", "pyproject.toml", "cargo.toml", "go.mod", "pom.xml",
        "build.gradle", "compose.yaml", "docker-compose.yml", "pnpm-workspace.yaml",
    }:
        return 0
    if name.startswith("readme"):
        return 1
    if "/test" in f"/{path.casefold()}" or name.startswith("test"):
        return 4
    if PurePosixPath(path).suffix.casefold() in {".md", ".mdx", ".rst", ".adoc", ".txt"}:
        return 3
    return 2


def select_context(
    scan_result: Any,
    *,
    brief_version: int,
    purpose: str,
    goal_terms: str | Iterable[str] = (),
) -> ContextSelectionResult:
    """Build a v1.1 references-only request from a transient scan result."""

    report = getattr(scan_result, "report", None)
    topology = getattr(scan_result, "topology", None)
    policy = getattr(scan_result, "policy", None)
    eligible_paths = tuple(getattr(scan_result, "eligible_paths", ()))
    observed_paths = tuple(getattr(scan_result, "observed_paths", ()))
    if (
        not isinstance(report, dict)
        or not isinstance(policy, dict)
        or not hasattr(topology, "nodes")
        or not callable(getattr(topology, "bounded_reachable", None))
    ):
        raise ContextError("invalid_scan_result")
    if (
        not isinstance(brief_version, int)
        or isinstance(brief_version, bool)
        or not 1 <= brief_version <= 1_000_000
    ):
        raise ContextError("invalid_brief_version")
    if not isinstance(purpose, str) or not purpose.strip() or len(purpose) > 500:
        raise ContextError("invalid_purpose")
    mode = report.get("mode")
    if mode not in ("quick", "standard", "deep"):
        raise ContextError("invalid_scan_result")
    context_limit = policy["targeted_context"][mode]
    mode_limit = policy["modes"][mode]
    counters = report["manifest"]["counters"]
    remaining_files = max(0, mode_limit["max_files"] - counters["file_attempts"])
    remaining_bytes = max(0, mode_limit["max_bytes"] - counters["bytes_consumed"])
    remaining_time_ms = max(0, mode_limit["max_seconds"] * 1000 - counters["elapsed_ms"])
    max_files = min(context_limit["max_files"], remaining_files)
    max_read_bytes = min(context_limit["max_read_bytes"], remaining_bytes)
    if max_files < 1 or max_read_bytes < 1 or remaining_time_ms < 1:
        raise ContextError("budget_reached")

    terms = _terms(goal_terms)
    seeds: list[str] = []
    for node_id, node in topology.nodes.items():
        haystack = " ".join(value for value in (node.label, node.relative_path) if value).casefold()
        if terms and any(term in haystack for term in terms):
            seeds.append(node_id)
    related_nodes = set(topology.bounded_reachable(seeds, max_nodes=4096)) if seeds else set()
    related_paths = {
        node.relative_path for node_id, node in topology.nodes.items()
        if node_id in related_nodes and node.relative_path
    }

    def rank(path: str) -> tuple[int, int, int, int, str, str]:
        folded = path.casefold()
        matches = sum(term in folded for term in terms)
        return (
            0 if matches else 1,
            _path_priority(path),
            -matches,
            0 if path in related_paths else 1,
            folded,
            path,
        )

    # The complete read ledger remains transient/private in ScanResult and the
    # restart checkpoint.  The 4 KiB public summary is intentionally only a
    # minimized sample and must not constrain task-specific source selection.
    scan_backed_paths = set(observed_paths)
    if not scan_backed_paths:
        report_evidence = {
            item.get("evidence_id") for item in report.get("summary", {}).get("evidence", [])
            if isinstance(item, dict)
        }
        scan_backed_paths = {
            item.get("relative_path") for item in report.get("manifest", {}).get("files", [])
            if isinstance(item, dict)
            and item.get("disposition") == "read"
            and item.get("evidence_ref") in report_evidence
        }
    ranked = tuple(sorted(set(eligible_paths) & scan_backed_paths, key=rank))
    # Automatic whole-file selection keeps a useful minimum model share per
    # source.  Callers may still use the higher policy ceiling with explicit
    # line ranges when they can pack smaller excerpts safely.
    automatic_files = max(1, context_limit["max_model_context_bytes"] // 4096)
    selected = ranked[:min(max_files, automatic_files)]
    if not selected:
        raise ContextError("no_eligible_sources")
    run_id = report.get("run_id")
    digest = hashlib.sha256(
        (str(run_id) + "\0" + str(brief_version) + "\0" + purpose.strip() + "\0" + "\0".join(selected)).encode("utf-8")
    ).hexdigest()[:24]
    selection = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "brief_version": brief_version,
        "selection_id": f"selection-{digest}",
        "mode": mode,
        "root_ref": "selected-project",
        "purpose": purpose.strip(),
        "requested_sources": [
            {"relative_path": path, "line_start": None, "line_end": None} for path in selected
        ],
        "max_read_bytes": max_read_bytes,
        "max_model_context_bytes": min(context_limit["max_model_context_bytes"], max_read_bytes),
        "authorization_scope": "existing_user_host_permissions",
        "content_delivery": "transient_host_context",
        "persistence": "references_only",
        "scan_policy_version": POLICY_VERSION,
        "charge_to_scan_budget": True,
    }
    while selected and len(json.dumps(selection, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > 8192:
        selected = selected[:-1]
        selection["requested_sources"] = [
            {"relative_path": path, "line_start": None, "line_end": None} for path in selected
        ]
    if not selected:
        raise ContextError("selection_too_large")
    digest = hashlib.sha256(
        (str(run_id) + "\0" + str(brief_version) + "\0" + purpose.strip() + "\0" + "\0".join(selected)).encode("utf-8")
    ).hexdigest()[:24]
    selection["selection_id"] = f"selection-{digest}"
    remaining = {
        "file_attempts": remaining_files,
        "bytes": remaining_bytes,
        "selected_files": len(selected),
        "selected_read_bytes": max_read_bytes,
    }
    return ContextSelectionResult(selection=selection, ranked_paths=ranked, remaining_budget=remaining)


def read_selected_context(
    session: Any,
    result: ContextSelectionResult,
    *,
    cancel: Any = None,
) -> TransientContext:
    """Read selected content through the originating scanner's guarded seam."""

    if not isinstance(result, ContextSelectionResult) or not hasattr(session, "read_sources"):
        raise ContextError("invalid_selection")
    value = session.read_sources(result.selection, cancel=cancel)
    required = ("items", "bytes_read", "model_context_bytes", "truncated", "reason_codes", "counters")
    if not all(hasattr(value, field) for field in required):
        raise ContextError("invalid_scan_result")
    return TransientContext(
        items=tuple(
            item if isinstance(item, ContextExcerpt) else ContextExcerpt(
                item.relative_path, item.text, item.line_start, item.line_end
            )
            for item in value.items
        ),
        bytes_read=value.bytes_read,
        model_context_bytes=value.model_context_bytes,
        truncated=value.truncated,
        reason_codes=tuple(value.reason_codes),
        counters=dict(value.counters),
    )


_SELECTION_KEYS = {
    "schema_version", "run_id", "brief_version", "selection_id", "mode", "root_ref",
    "purpose", "requested_sources", "max_read_bytes", "max_model_context_bytes",
    "authorization_scope", "content_delivery", "persistence", "scan_policy_version",
    "charge_to_scan_budget",
}
_BRIEF_KEYS = {
    "schema_version", "run_id", "brief_id", "brief_version", "goal", "decision",
    "project_stage", "success_criterion", "constraints", "observations", "assumptions",
    "user_corrections", "context_status", "updated_at", "details",
}
_DETAIL_FIELDS = (
    "problem", "target_user", "workflow", "current_behavior", "target_behavior", "baseline", "scope"
)
_CONSTRAINT_KEYS = {
    "languages", "deployment", "allowed_licenses", "compatibility", "require_no_server",
    "mandatory_fields",
}
_RELATIVE_PATH = re.compile(r"^(?!/)(?!.*(?:^|/)\.{1,2}(?:/|$))(?!.*//)[^\\:\x00-\x1f\x7f<>|?*]+$")
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")
_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def validate_context_selection(selection: Any, scan_report: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Validate the references-only persisted selection shape and optional scan join."""

    if not isinstance(selection, dict) or set(selection) != _SELECTION_KEYS:
        raise ContextError("invalid_selection")
    mode = selection.get("mode")
    limits = {
        "quick": (16, 1_048_576, 24_576),
        "standard": (64, 8_388_608, 49_152),
        "deep": (256, 67_108_864, 65_536),
    }
    if mode not in limits:
        raise ContextError("invalid_selection")
    max_files, max_read, max_model = limits[mode]
    sources = selection.get("requested_sources")
    if (
        selection.get("schema_version") != SCHEMA_VERSION
        or not isinstance(selection.get("run_id"), str)
        or _UUID.fullmatch(selection["run_id"]) is None
        or selection.get("scan_policy_version") != POLICY_VERSION
        or selection.get("root_ref") != "selected-project"
        or selection.get("authorization_scope") != "existing_user_host_permissions"
        or selection.get("content_delivery") != "transient_host_context"
        or selection.get("persistence") != "references_only"
        or selection.get("charge_to_scan_budget") is not True
        or not isinstance(selection.get("purpose"), str)
        or not 1 <= len(selection["purpose"]) <= 500
        or not isinstance(selection.get("brief_version"), int)
        or isinstance(selection.get("brief_version"), bool)
        or not 1 <= selection["brief_version"] <= 1_000_000
        or not isinstance(selection.get("selection_id"), str)
        or not _ID.fullmatch(selection["selection_id"])
        or not isinstance(sources, list)
        or not 1 <= len(sources) <= max_files
        or not isinstance(selection.get("max_read_bytes"), int)
        or isinstance(selection.get("max_read_bytes"), bool)
        or not 1 <= selection["max_read_bytes"] <= max_read
        or not isinstance(selection.get("max_model_context_bytes"), int)
        or isinstance(selection.get("max_model_context_bytes"), bool)
        or not 1 <= selection["max_model_context_bytes"] <= max_model
        or selection["max_model_context_bytes"] > selection["max_read_bytes"]
    ):
        raise ContextError("invalid_selection")
    paths: set[str] = set()
    for source in sources:
        if (
            not isinstance(source, dict)
            or set(source) != {"relative_path", "line_start", "line_end"}
            or not isinstance(source.get("relative_path"), str)
            or len(source["relative_path"]) > 240
            or _RELATIVE_PATH.fullmatch(source["relative_path"]) is None
            or source["relative_path"] in paths
        ):
            raise ContextError("invalid_selection")
        start, end = source["line_start"], source["line_end"]
        if (start is None) != (end is None) or (
            start is not None
            and (
                not isinstance(start, int) or isinstance(start, bool) or not 1 <= start <= 10_000_000
                or not isinstance(end, int) or isinstance(end, bool) or not start <= end <= 10_000_000
            )
        ):
            raise ContextError("invalid_selection")
        paths.add(source["relative_path"])
    if scan_report is not None and (
        not isinstance(scan_report, Mapping)
        or selection.get("run_id") != scan_report.get("run_id")
        or mode != scan_report.get("mode")
        or selection.get("scan_policy_version") != scan_report.get("policy_version")
    ):
        raise ContextError("selection_scan_mismatch")
    data = json.dumps(selection, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(data) > 8192:
        raise ContextError("selection_too_large")
    return selection


def _validate_constraints(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != _CONSTRAINT_KEYS:
        raise ContextError("invalid_constraints")
    rules = (
        ("languages", 8, 64), ("allowed_licenses", 12, 80), ("compatibility", 12, 160),
    )
    for key, maximum, length in rules:
        items = value.get(key)
        if (
            not isinstance(items, list) or len(items) > maximum or len(items) != len(set(items))
            or any(not isinstance(item, str) or not 1 <= len(item) <= length for item in items)
        ):
            raise ContextError("invalid_constraints")
    deployment = value.get("deployment")
    mandatory = value.get("mandatory_fields")
    if (
        not isinstance(deployment, list) or len(deployment) > 3 or len(deployment) != len(set(deployment))
        or any(item not in ("local", "self_hosted", "cloud") for item in deployment)
        or value.get("require_no_server") not in (True, False, None)
        or not isinstance(mandatory, list) or len(mandatory) > 5 or len(mandatory) != len(set(mandatory))
        or any(item not in ("license", "deployment", "language", "compatibility", "no_server") for item in mandatory)
    ):
        raise ContextError("invalid_constraints")
    return value


def _claim(text: str | None, kind: str, *, evidence_refs: Iterable[str] = (), answer_ids: Iterable[str] = (), limitation: str | None = None) -> dict[str, Any]:
    refs = list(dict.fromkeys(evidence_refs))[:12]
    answers = list(dict.fromkeys(answer_ids))[:10]
    if kind == "unknown":
        return {
            "text": None, "kind": "unknown", "evidence_refs": [], "answer_ids": [],
            "limitation": limitation or "This detail was not established by the bounded scan or saved intake.",
        }
    if not isinstance(text, str) or not text or len(text) > 700 or (not refs and not answers):
        raise ContextError("invalid_claim")
    return {
        "text": text, "kind": kind, "evidence_refs": refs, "answer_ids": answers,
        "limitation": limitation,
    }


def _answer_map(intake_state: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    intake = intake_state.get("intake") if isinstance(intake_state.get("intake"), dict) else intake_state
    answers = intake.get("answers") if isinstance(intake, Mapping) else None
    if not isinstance(answers, list):
        raise ContextError("invalid_intake")
    result: dict[str, dict[str, Any]] = {}
    for answer in answers:
        if not isinstance(answer, dict) or not isinstance(answer.get("question_id"), str):
            raise ContextError("invalid_intake")
        if answer.get("status") == "answered" and isinstance(answer.get("sanitized_value"), str):
            result[answer["question_id"]] = answer
    return result


def _answer_claim(answers: Mapping[str, dict[str, Any]], question_id: str, limitation: str) -> dict[str, Any]:
    answer = answers.get(question_id)
    if answer is None:
        return _claim(None, "unknown", limitation=limitation)
    return _claim(answer["sanitized_value"][:700], "user_statement", answer_ids=(answer["answer_id"],))


def _stage(value: str | None) -> str:
    folded = (value or "").casefold()
    if any(token in folded for token in ("prototype", "прототип")):
        return "prototype"
    if any(token in folded for token in ("product", "продукт", "working", "работающ")):
        return "product"
    if any(token in folded for token in ("empty", "пуст")):
        return "empty"
    if any(token in folded for token in ("idea", "иде")):
        return "idea"
    return "unknown"


def build_project_context_brief(
    scan_report: Mapping[str, Any],
    intake_state: Mapping[str, Any],
    selection: Mapping[str, Any],
    transient_context: TransientContext,
    *,
    decision: str = "evaluate",
    constraints: Mapping[str, Any] | None = None,
    updated_at: str | None = None,
) -> dict[str, Any]:
    """Compose a v1.1 Brief without copying transient source excerpts."""

    if not isinstance(scan_report, Mapping) or scan_report.get("schema_version") != SCHEMA_VERSION:
        raise ContextError("invalid_scan_report")
    validate_context_selection(dict(selection), scan_report)
    if decision not in ("build", "replace", "compare", "learn", "evaluate"):
        raise ContextError("invalid_decision")
    if not isinstance(transient_context, TransientContext):
        raise ContextError("invalid_transient_context")
    requested = {item["relative_path"] for item in selection["requested_sources"]}
    if any(item.relative_path not in requested for item in transient_context.items):
        raise ContextError("invalid_transient_context")
    answers = _answer_map(intake_state)
    observations = copy.deepcopy(scan_report.get("summary"))
    if not isinstance(observations, dict) or observations.get("run_id") != scan_report.get("run_id"):
        raise ContextError("invalid_scan_report")
    canonical_constraints = dict(constraints) if constraints is not None else {
        "languages": [], "deployment": [], "allowed_licenses": [], "compatibility": [],
        "require_no_server": None, "mandatory_fields": [],
    }
    _validate_constraints(canonical_constraints)
    goal_answer = answers.get("goal")
    success_answer = answers.get("success")
    if (
        goal_answer is not None and len(goal_answer["sanitized_value"]) > 1000
        or success_answer is not None and len(success_answer["sanitized_value"]) > 700
    ):
        raise ContextError("intake_value_too_large")
    goal = goal_answer["sanitized_value"] if goal_answer else "Goal remains unknown pending user review."
    success = success_answer["sanitized_value"] if success_answer else "Success criterion remains unknown pending user review."
    evidence_refs = [
        item["evidence_id"] for item in observations.get("evidence", [])
        if item.get("relative_path") in requested
    ][:12]
    if evidence_refs:
        current = _claim(
            f"Bounded scan observed {len(observations.get('facts', []))} structured project fact(s).",
            "observed", evidence_refs=evidence_refs,
            limitation="This count reflects bounded observed evidence, not complete project behavior.",
        )
    else:
        current = _claim(None, "unknown", limitation="No project evidence was retained by the bounded scan.")
    details = {
        "problem": _answer_claim(answers, "goal", "The problem was not established in saved intake."),
        "target_user": _claim(None, "unknown", limitation="The target user was not established in saved intake."),
        "workflow": _answer_claim(answers, "integration_surface", "The workflow was not established in saved intake."),
        "current_behavior": current,
        "target_behavior": _answer_claim(answers, "success", "The target behavior was not established in saved intake."),
        "baseline": _claim(None, "unknown", limitation="No baseline was established."),
        "scope": _answer_claim(answers, "operating_constraints", "The scope was not established in saved intake."),
        "non_goals": [], "constraint_notes": [], "tensions": [],
    }
    now = updated_at or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if not isinstance(now, str) or _TIMESTAMP.fullmatch(now) is None:
        raise ContextError("invalid_timestamp")
    digest = hashlib.sha256(
        (str(scan_report.get("run_id")) + "\0" + observations.get("summary_id", "") + "\0" + selection["selection_id"]).encode("utf-8")
    ).hexdigest()[:24]
    intake = intake_state.get("intake") if isinstance(intake_state.get("intake"), dict) else intake_state
    assumptions = list(intake.get("assumptions", [])) if isinstance(intake, Mapping) else []
    brief = {
        "schema_version": SCHEMA_VERSION,
        "run_id": scan_report["run_id"],
        "brief_id": f"brief-{digest}",
        "brief_version": selection["brief_version"],
        "goal": goal,
        "decision": decision,
        "project_stage": _stage(answers.get("project_stage", {}).get("sanitized_value")),
        "success_criterion": success,
        "constraints": canonical_constraints,
        "observations": observations,
        "assumptions": assumptions[:12],
        "user_corrections": [],
        "context_status": (
            "partial" if scan_report.get("status") != "complete" or transient_context.truncated
            else "reviewed" if transient_context.items else "preliminary"
        ),
        "updated_at": now,
        "details": details,
    }
    return validate_project_context_brief(brief)


def validate_project_context_brief(brief: Any) -> dict[str, Any]:
    """Validate the persisted v1.1 Brief boundary without source excerpts."""

    if not isinstance(brief, dict) or set(brief) != _BRIEF_KEYS:
        raise ContextError("invalid_brief")
    if (
        brief.get("schema_version") != SCHEMA_VERSION
        or not isinstance(brief.get("run_id"), str) or _UUID.fullmatch(brief["run_id"]) is None
        or not isinstance(brief.get("brief_id"), str) or _ID.fullmatch(brief["brief_id"]) is None
        or not isinstance(brief.get("brief_version"), int) or isinstance(brief.get("brief_version"), bool)
        or not 1 <= brief["brief_version"] <= 1_000_000
        or brief.get("decision") not in ("build", "replace", "compare", "learn", "evaluate")
        or brief.get("project_stage") not in ("idea", "empty", "prototype", "product", "unknown")
        or not isinstance(brief.get("goal"), str) or not 1 <= len(brief["goal"]) <= 1000
        or not isinstance(brief.get("success_criterion"), str) or not 1 <= len(brief["success_criterion"]) <= 700
        or brief.get("context_status") not in ("preliminary", "reviewed", "partial")
        or not isinstance(brief.get("updated_at"), str) or _TIMESTAMP.fullmatch(brief["updated_at"]) is None
        or not isinstance(brief.get("observations"), dict)
        or brief["observations"].get("run_id") != brief.get("run_id")
    ):
        raise ContextError("invalid_brief")
    _validate_constraints(brief.get("constraints"))
    details = brief.get("details")
    if not isinstance(details, dict) or set(details) != set(_DETAIL_FIELDS) | {"non_goals", "constraint_notes", "tensions"}:
        raise ContextError("invalid_brief")
    for field in _DETAIL_FIELDS:
        claim = details[field]
        if not isinstance(claim, dict) or set(claim) != {"text", "kind", "evidence_refs", "answer_ids", "limitation"}:
            raise ContextError("invalid_brief")
        kind = claim.get("kind")
        if kind == "unknown":
            if claim.get("text") is not None or claim.get("evidence_refs") != [] or claim.get("answer_ids") != [] or not claim.get("limitation"):
                raise ContextError("invalid_brief")
        elif kind not in ("observed", "user_statement", "inference") or not isinstance(claim.get("text"), str) or not claim["text"] or not (claim.get("evidence_refs") or claim.get("answer_ids")):
            raise ContextError("invalid_brief")
    if not isinstance(details["non_goals"], list) or not isinstance(details["constraint_notes"], list) or not isinstance(details["tensions"], list):
        raise ContextError("invalid_brief")
    if not isinstance(brief.get("assumptions"), list) or len(brief["assumptions"]) > 12 or not isinstance(brief.get("user_corrections"), list) or len(brief["user_corrections"]) > 20:
        raise ContextError("invalid_brief")
    data = json.dumps(brief, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(data) > 16_384:
        raise ContextError("brief_too_large")
    return brief


def validate_context_commit(
    selection: Mapping[str, Any],
    brief: Mapping[str, Any],
    scan_report: Mapping[str, Any],
    intake_state: Mapping[str, Any],
    policy: Mapping[str, Any],
    *,
    canonical_brief: Mapping[str, Any] | None = None,
    scan_records: Iterable[Mapping[str, Any]] | None = None,
) -> None:
    """Bind a context commit to saved scan evidence, budgets, and intake facts."""

    validate_context_selection(dict(selection), scan_report)
    validate_project_context_brief(dict(brief))
    mode = selection["mode"]
    try:
        mode_limits = policy["modes"][mode]
        context_limits = policy["targeted_context"][mode]
        manifest = scan_report["manifest"]
        counters = manifest["counters"]
        files = manifest["files"]
        evidence = scan_report["summary"]["evidence"]
    except (KeyError, TypeError) as error:
        raise ContextError("scan_detail_unavailable") from error
    integer_counters = ("file_attempts", "bytes_consumed", "elapsed_ms")
    if (
        not all(
            isinstance(counters.get(key), int)
            and not isinstance(counters.get(key), bool)
            and counters[key] >= 0
            for key in integer_counters
        )
        or not isinstance(files, list)
        or not isinstance(evidence, list)
    ):
        raise ContextError("scan_detail_unavailable")
    remaining_files = mode_limits["max_files"] - counters["file_attempts"]
    remaining_bytes = mode_limits["max_bytes"] - counters["bytes_consumed"]
    remaining_ms = mode_limits["max_seconds"] * 1000 - counters["elapsed_ms"]
    if (
        remaining_files < len(selection["requested_sources"])
        or remaining_bytes < selection["max_read_bytes"]
        or remaining_ms <= 0
        or len(selection["requested_sources"]) > context_limits["max_files"]
        or selection["max_read_bytes"] > context_limits["max_read_bytes"]
        or selection["max_model_context_bytes"] > context_limits["max_model_context_bytes"]
        or selection["max_model_context_bytes"] > selection["max_read_bytes"]
    ):
        raise ContextError("selection_budget_exceeded")
    manifest_by_path: dict[str, Mapping[str, Any]] = {}
    for item in files:
        if not isinstance(item, Mapping) or not isinstance(item.get("relative_path"), str):
            raise ContextError("scan_detail_unavailable")
        manifest_by_path[item["relative_path"]] = item
    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    for item in evidence:
        if not isinstance(item, Mapping) or not isinstance(item.get("evidence_id"), str):
            raise ContextError("scan_detail_unavailable")
        evidence_by_id[item["evidence_id"]] = item
    selected_paths = {item["relative_path"] for item in selection["requested_sources"]}
    checkpoint_by_path: dict[str, Mapping[str, Any]] = {}
    if scan_records is not None:
        try:
            for item in scan_records:
                if not isinstance(item, Mapping) or not isinstance(item.get("relative_path"), str):
                    raise ContextError("scan_detail_unavailable")
                checkpoint_by_path[item["relative_path"]] = item
        except TypeError as error:
            raise ContextError("scan_detail_unavailable") from error
    for path in selected_paths:
        item = checkpoint_by_path.get(path) if checkpoint_by_path else manifest_by_path.get(path)
        if item is None or item.get("disposition") != "read":
            raise ContextError("selection_not_scan_backed")
        evidence_ref = item.get("evidence_ref")
        resolved = evidence_by_id.get(evidence_ref)
        if not isinstance(evidence_ref, str) or _ID.fullmatch(evidence_ref) is None:
            raise ContextError("selection_not_scan_backed")
        if resolved is not None and (
            resolved.get("relative_path") != path
            or resolved.get("content_persisted") is not False
        ):
            raise ContextError("selection_not_scan_backed")
        if not checkpoint_by_path and resolved is None:
            raise ContextError("selection_not_scan_backed")

    intake = intake_state.get("intake") if isinstance(intake_state.get("intake"), Mapping) else intake_state
    answers = intake.get("answers") if isinstance(intake, Mapping) else None
    if not isinstance(answers, list):
        raise ContextError("invalid_intake")
    saved_answers = {
        item["answer_id"]: item
        for item in answers
        if isinstance(item, Mapping)
        and item.get("status") == "answered"
        and isinstance(item.get("answer_id"), str)
        and isinstance(item.get("sanitized_value"), str)
    }
    by_question = {item["question_id"]: item for item in saved_answers.values()}
    if canonical_brief is None:
        goal = by_question.get("goal", {}).get("sanitized_value", "Goal remains unknown pending user review.")
        success = by_question.get("success", {}).get("sanitized_value", "Success criterion remains unknown pending user review.")
        assumptions = intake.get("assumptions")
        corrections: list[str] = []
    else:
        validate_project_context_brief(dict(canonical_brief))
        goal = canonical_brief["goal"]
        success = canonical_brief["success_criterion"]
        assumptions = canonical_brief["assumptions"]
        corrections = canonical_brief["user_corrections"]
    if (
        brief["goal"] != goal
        or brief["success_criterion"] != success
        or brief["assumptions"] != assumptions
        or brief["user_corrections"] != corrections
    ):
        raise ContextError("brief_intake_mismatch")

    def validate_claim(claim: Any, *, require_selected_evidence: bool) -> None:
        if not isinstance(claim, Mapping):
            raise ContextError("invalid_brief")
        refs = claim.get("evidence_refs")
        answer_ids = claim.get("answer_ids")
        kind = claim.get("kind")
        if not isinstance(refs, list) or not isinstance(answer_ids, list):
            raise ContextError("invalid_brief")
        if any(ref not in evidence_by_id for ref in refs) or any(answer_id not in saved_answers for answer_id in answer_ids):
            raise ContextError("brief_reference_unresolved")
        if require_selected_evidence and any(
            evidence_by_id[ref].get("relative_path") not in selected_paths for ref in refs
        ):
            raise ContextError("brief_reference_unresolved")
        if (
            kind == "observed" and (not refs or answer_ids)
            or kind == "user_statement" and (not answer_ids or refs)
            or kind == "inference" and not (refs or answer_ids)
            or kind == "unknown" and (refs or answer_ids)
            or kind not in ("observed", "user_statement", "inference", "unknown")
        ):
            raise ContextError("brief_reference_unresolved")

    observations = brief["observations"]
    fact_ids = {item.get("fact_id") for item in observations.get("facts", []) if isinstance(item, Mapping)}
    for fact in observations.get("facts", []):
        if not isinstance(fact, Mapping) or any(ref not in evidence_by_id for ref in fact.get("evidence_refs", [])):
            raise ContextError("brief_reference_unresolved")
    for inference in observations.get("inferences", []):
        if not isinstance(inference, Mapping) or any(item not in fact_ids for item in inference.get("basis_fact_ids", [])):
            raise ContextError("brief_reference_unresolved")
    details = brief["details"]
    for field in _DETAIL_FIELDS:
        validate_claim(details[field], require_selected_evidence=True)
    for claim in details["non_goals"]:
        validate_claim(claim, require_selected_evidence=True)
    for note in details["constraint_notes"]:
        if not isinstance(note, Mapping) or "claim" not in note:
            raise ContextError("invalid_brief")
        validate_claim(note["claim"], require_selected_evidence=True)


def apply_brief_correction(brief: Mapping[str, Any], target: str, value: str, correction_id: str) -> dict[str, Any]:
    """Apply one sanitized correction without mutating observed scan facts."""

    corrected = copy.deepcopy(validate_project_context_brief(dict(brief)))
    if not isinstance(correction_id, str) or _ID.fullmatch(correction_id) is None or not isinstance(value, str) or not value:
        raise ContextError("invalid_correction")
    if target in ("goal", "success_criterion"):
        maximum = 1000 if target == "goal" else 700
        if len(value) > maximum:
            raise ContextError("invalid_correction")
        corrected[target] = value
    elif target == "project_stage":
        if value not in ("idea", "empty", "prototype", "product", "unknown"):
            raise ContextError("invalid_correction")
        corrected[target] = value
    elif target == "assumption":
        if len(value) > 400:
            raise ContextError("invalid_correction")
        if value not in corrected["assumptions"]:
            if len(corrected["assumptions"]) >= 12:
                raise ContextError("brief_too_large")
            corrected["assumptions"].append(value)
    elif target == "constraints":
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError) as error:
            raise ContextError("invalid_constraints") from error
        corrected["constraints"] = copy.deepcopy(_validate_constraints(parsed))
    elif target in ("observation_interpretation", "context_details"):
        if target == "observation_interpretation":
            field, text = "current_behavior", value
        else:
            try:
                parsed = json.loads(value)
            except (json.JSONDecodeError, TypeError) as error:
                raise ContextError("invalid_correction") from error
            if not isinstance(parsed, dict) or set(parsed) != {"field", "text"} or parsed.get("field") not in _DETAIL_FIELDS or not isinstance(parsed.get("text"), str):
                raise ContextError("invalid_correction")
            field, text = parsed["field"], parsed["text"].strip()
        if not text or len(text) > 700:
            raise ContextError("invalid_correction")
        existing = corrected["details"][field]
        refs = existing.get("evidence_refs", [])
        answer_ids = existing.get("answer_ids", [])
        if not refs and not answer_ids:
            refs = [item["evidence_id"] for item in corrected["observations"].get("evidence", [])[:12]]
        if not refs and not answer_ids:
            raise ContextError("correction_basis_missing")
        corrected["details"][field] = _claim(
            text, "inference", evidence_refs=refs, answer_ids=answer_ids,
            limitation="User-corrected interpretation; observed scan facts remain unchanged.",
        )
    else:
        raise ContextError("invalid_correction")
    if correction_id not in corrected["user_corrections"]:
        if len(corrected["user_corrections"]) >= 20:
            raise ContextError("brief_too_large")
        corrected["user_corrections"].append(correction_id)
    return corrected
