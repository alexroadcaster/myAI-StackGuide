"""Black-box CP-07 intake, preflight, correction, and publication CLI."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import sqlite3
import sys
from typing import Any
import uuid


SCRIPT_ROOT = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_ROOT.parent
ASSETS = PLUGIN_ROOT / "assets"
MAX_INPUT_BYTES = 8192
COMMIT_SCAN_INPUT_BYTES = 2_500_000
COMMIT_CONTEXT_INPUT_BYTES = 32_768
APPLICATION_ID = 1297695049
TRUSTED_MANIFEST_SHA256 = "9cbb259aac4c75707814a3eb4f6811214146539d13a36f32aaae9e2ef072f8c8"


def _load_trusted(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("trusted module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


store = _load_trusted("myai_stackguide_state_store", SCRIPT_ROOT / "state_store.py")
sanitizer = _load_trusted("myai_stackguide_sanitize", SCRIPT_ROOT / "sanitize.py")
scanner = _load_trusted("myai_stackguide_scanner", SCRIPT_ROOT / "scanner.py")
context = scanner.context


COMMANDS = {
    "preflight", "start", "resume", "answer", "correct", "cancel", "finalize",
    "retry-publication", "commit-scan", "commit-context",
}


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _read_payload(command: str) -> dict[str, Any]:
    limit = {
        "commit-scan": COMMIT_SCAN_INPUT_BYTES,
        "commit-context": COMMIT_CONTEXT_INPUT_BYTES,
    }.get(command, MAX_INPUT_BYTES)
    data = sys.stdin.buffer.read(limit + 1)
    if len(data) > limit:
        raise ValueError("oversized input")
    if not data:
        return {}
    value = json.loads(
        data.decode("utf-8", errors="strict"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
    )
    if not isinstance(value, dict):
        raise ValueError("input must be an object")
    return value


def _parse_cli(argv: list[str]) -> tuple[str, str, str | None, int | None]:
    if not argv or argv[0] not in COMMANDS:
        raise ValueError("invalid command")
    command = argv[0]
    values: dict[str, str] = {}
    index = 1
    while index < len(argv):
        key = argv[index]
        if key not in ("--project-root", "--expected-run-id", "--expected-revision") or key in values:
            raise ValueError("invalid argument")
        if index + 1 >= len(argv):
            raise ValueError("missing argument")
        values[key] = argv[index + 1]
        index += 2
    if "--project-root" not in values:
        raise ValueError("missing root")
    revision: int | None = None
    if "--expected-revision" in values:
        raw = values["--expected-revision"]
        if not raw.isascii() or not raw.isdigit():
            raise ValueError("invalid revision")
        revision = int(raw)
        if not 0 <= revision <= 1_000_000:
            raise ValueError("invalid revision")
    run_id = values.get("--expected-run-id")
    if run_id is not None:
        try:
            if str(uuid.UUID(run_id)) != run_id.lower():
                raise ValueError("invalid run")
        except (ValueError, AttributeError) as error:
            raise ValueError("invalid run") from error
    return command, values["--project-root"], run_id, revision


def _preflight_result(
    reason: str | None,
    *,
    python_implementation: str | None,
    python_version: str | None,
    sqlite_version: str | None,
    fts5_available: bool | None,
    root_valid: bool,
    pins: dict[str, Any] | None = None,
) -> dict[str, Any]:
    actions = {
        None: "continue",
        "invalid_input": "provide_valid_input",
        "python_unsupported": "use_supported_python",
        "invalid_root": "select_valid_project_root",
        "fts5_unavailable": "use_supported_python",
        "index_missing": "use_compatible_package",
        "index_corrupt": "use_compatible_package",
        "index_incompatible": "use_compatible_package",
        "unavailable": "stop",
    }
    return {
        "schema_version": "1.0.0",
        "status": "ready" if reason is None else "blocked",
        "observed_at": store.utc_now(),
        "python": {"implementation": python_implementation, "version": python_version},
        "sqlite": {"version": sqlite_version, "fts5_available": fts5_available},
        "root_ref": "selected-project" if root_valid else None,
        "pins": pins if reason is None else None,
        "reason_codes": [] if reason is None else [reason],
        "next_action": actions[reason],
    }


def _load_json_file(path: Path) -> Any:
    data = path.read_bytes()
    return json.loads(
        data.decode("utf-8", errors="strict"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _probe_fts5() -> bool:
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE VIRTUAL TABLE fts_probe USING fts5(value)")
        connection.execute("INSERT INTO fts_probe(value) VALUES (?)", ("probe",))
        return connection.execute(
            "SELECT count(*) FROM fts_probe WHERE fts_probe MATCH ?", ("probe",)
        ).fetchone()[0] == 1
    finally:
        connection.close()


def _check_package() -> dict[str, Any]:
    manifest_path = ASSETS / "catalog.search-manifest.json"
    index_path = ASSETS / "catalog.search.sqlite"
    cards_path = ASSETS / "catalog.snapshot.json"
    policy_path = ASSETS / "retrieval-policy.json"
    required = (manifest_path, index_path, cards_path, policy_path)
    if any(not path.is_file() for path in required):
        raise FileNotFoundError
    manifest = _load_json_file(manifest_path)
    policy = _load_json_file(policy_path)
    snapshot = _load_json_file(cards_path)
    if not isinstance(manifest, dict) or not isinstance(policy, dict) or not isinstance(snapshot, dict):
        raise ValueError("invalid package JSON")
    if _sha256_file(manifest_path) != TRUSTED_MANIFEST_SHA256:
        raise RuntimeError("untrusted manifest")
    uri = index_path.resolve(strict=True).as_uri() + "?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        if connection.execute("PRAGMA quick_check").fetchone() != ("ok",):
            raise sqlite3.DatabaseError("quick check")
        if connection.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise sqlite3.DatabaseError("integrity check")
        application_id = connection.execute("PRAGMA application_id").fetchone()[0]
        user_version = connection.execute("PRAGMA user_version").fetchone()[0]
        row_count = connection.execute("SELECT count(*) FROM repository_search_rows").fetchone()[0]
        fts_count = connection.execute("SELECT count(*) FROM repository_fts").fetchone()[0]
        metadata_cursor = connection.execute("SELECT * FROM bundle_metadata WHERE singleton = 1")
        columns = [item[0] for item in metadata_cursor.description]
        metadata_row = metadata_cursor.fetchone()
        if metadata_row is None:
            raise sqlite3.DatabaseError("metadata")
        metadata = dict(zip(columns, metadata_row))
    finally:
        connection.close()
    pins = manifest.get("pins")
    exact_pin_keys = {
        "catalog_snapshot_id", "source_sha256", "cards_sha256", "index_sha256",
        "policy_sha256", "taxonomy_sha256", "card_schema_version",
        "activity_schema_version", "index_format_version", "retrieval_policy_version",
        "corpus_kind",
    }
    compatible = (
        manifest.get("schema_version") == "2.0.0"
        and isinstance(pins, dict)
        and set(pins) == exact_pin_keys
        and pins.get("card_schema_version") == "2.0.0"
        and pins.get("activity_schema_version") == "2.0.0"
        and pins.get("retrieval_policy_version") == "2.1.0"
        and pins.get("index_format_version") == 2
        and pins.get("corpus_kind") == "catalog_snapshot"
        and manifest.get("index_file") == "catalog.search.sqlite"
        and manifest.get("cards_file") == "catalog.snapshot.json"
        and manifest.get("policy_file") == "retrieval-policy.json"
        and manifest.get("contains_project_context") is False
        and manifest.get("read_only_runtime") is True
        and manifest.get("row_count") == 2500
        and application_id == APPLICATION_ID
        and user_version == 2
        and row_count == fts_count == manifest.get("row_count")
        and policy.get("schema_version") == "2.1.0"
        and policy.get("source_mode") == "catalog_only"
        and policy.get("retrieval_engine") == "sqlite_fts5"
        and policy.get("runtime_index_access") == "read_only"
        and policy.get("automatic_index_build") is False
        and policy.get("full_catalog_prompt_fallback") is False
        and snapshot.get("schema_version") == "2.0.0"
        and snapshot.get("activity_schema_version") == "2.0.0"
        and snapshot.get("catalog_snapshot_id") == pins.get("catalog_snapshot_id")
        and snapshot.get("source_sha256") == pins.get("source_sha256")
        and snapshot.get("taxonomy_sha256") == pins.get("taxonomy_sha256")
        and snapshot.get("corpus_kind") == pins.get("corpus_kind")
        and isinstance(snapshot.get("cards"), list)
        and len(snapshot["cards"]) == manifest.get("row_count")
        and _sha256_file(cards_path) == pins.get("cards_sha256")
        and _sha256_file(index_path) == pins.get("index_sha256")
        and _sha256_file(policy_path) == pins.get("policy_sha256")
        and metadata.get("schema_version") == "2.0.0"
        and metadata.get("catalog_snapshot_id") == pins.get("catalog_snapshot_id")
        and metadata.get("source_sha256") == pins.get("source_sha256")
        and metadata.get("taxonomy_sha256") == pins.get("taxonomy_sha256")
        and metadata.get("cards_sha256") == pins.get("cards_sha256")
        and metadata.get("policy_sha256") == pins.get("policy_sha256")
        and metadata.get("card_schema_version") == "2.0.0"
        and metadata.get("activity_schema_version") == "2.0.0"
        and metadata.get("retrieval_policy_version") == "2.1.0"
        and metadata.get("index_format_version") == 2
        and metadata.get("corpus_kind") == "catalog_snapshot"
        and metadata.get("row_count") == 2500
        and metadata.get("logical_rows_sha256") == manifest.get("logical_rows_sha256")
        and metadata.get("tokenizer") == policy.get("tokenizer") == "unicode61"
        and metadata.get("normalization") == policy.get("normalization")
    )
    if not compatible:
        raise RuntimeError("incompatible package")
    return manifest


def run_preflight(payload: dict[str, Any], raw_root: str) -> tuple[dict[str, Any], Path | None, dict[str, Any] | None]:
    if payload:
        return _preflight_result(
            "invalid_input", python_implementation=None, python_version=None,
            sqlite_version=None, fts5_available=None, root_valid=False,
        ), None, None
    implementation = platform.python_implementation()
    version = ".".join(str(value) for value in sys.version_info[:3])
    if implementation != "CPython" or sys.version_info[:2] != (3, 14):
        return _preflight_result(
            "python_unsupported", python_implementation=implementation, python_version=version,
            sqlite_version=None, fts5_available=None, root_valid=False,
        ), None, None
    try:
        project_root = store.validate_project_root(raw_root)
    except store.StateError:
        return _preflight_result(
            "invalid_root", python_implementation=implementation, python_version=version,
            sqlite_version=None, fts5_available=None, root_valid=False,
        ), None, None
    sqlite_version = sqlite3.sqlite_version
    try:
        available = _probe_fts5()
    except sqlite3.Error:
        available = False
    if not available:
        return _preflight_result(
            "fts5_unavailable", python_implementation=implementation, python_version=version,
            sqlite_version=sqlite_version, fts5_available=False, root_valid=True,
        ), project_root, None
    try:
        manifest = _check_package()
    except FileNotFoundError:
        reason = "index_missing"
        manifest = None
    except PermissionError:
        reason = "unavailable"
        manifest = None
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, sqlite3.DatabaseError):
        reason = "index_corrupt"
        manifest = None
    except OSError:
        reason = "unavailable"
        manifest = None
    except RuntimeError:
        reason = "index_incompatible"
        manifest = None
    else:
        return _preflight_result(
            None, python_implementation=implementation, python_version=version,
            sqlite_version=sqlite_version, fts5_available=True, root_valid=True,
            pins=manifest["pins"],
        ), project_root, manifest
    return _preflight_result(
        reason, python_implementation=implementation, python_version=version,
        sqlite_version=sqlite_version, fts5_available=True, root_valid=True,
    ), project_root, manifest


def _publication_failure(
    reason: str,
    *,
    operation: str = "commit_and_publish",
    current: dict[str, Any] | None = None,
    message_key: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.1.0",
        "operation_id": str(uuid.uuid4()),
        "operation": operation,
        "commit_status": "not_attempted" if operation == "render_only" else "not_saved",
        "saved": None,
        "current": current,
        "published": None,
        "publication_status": "not_attempted",
        "failure_reason": reason,
        "message_key": message_key,
        "render_attempts": 0,
        "retry": "stop",
        "html_path": "docs/myai-stackguide/status.html",
    }


def _publication_success(state: dict[str, Any], *, operation: str, commit_status: str) -> dict[str, Any]:
    publication = store.publish(_ACTIVE_ROOT, state)
    return {
        "schema_version": "1.1.0",
        "operation_id": str(uuid.uuid4()),
        "operation": operation,
        "commit_status": commit_status,
        "saved": store.state_stamp(state),
        "current": publication["current"],
        "published": publication["published"],
        "publication_status": publication["publication_status"],
        "failure_reason": publication["failure_reason"],
        "message_key": None,
        "render_attempts": publication["render_attempts"],
        "retry": publication["retry"],
        "html_path": "docs/myai-stackguide/status.html",
    }


def _load_question_bank() -> dict[str, Any]:
    bank = _load_json_file(ASSETS / "question-bank.json")
    if (
        not isinstance(bank, dict)
        or set(bank) != {"schema_version", "default_locale", "questions"}
        or bank.get("schema_version") != "1.0.0"
        or bank.get("default_locale") not in ("ru", "en")
        or not isinstance(bank.get("questions"), list)
        or len(bank["questions"]) != 10
    ):
        raise store.StateError("state_incompatible")
    for ordinal, question in enumerate(bank["questions"], start=1):
        if not isinstance(question, dict) or question.get("ordinal") != ordinal:
            raise store.StateError("state_incompatible")
    return bank


def _question(bank: dict[str, Any], ordinal: int) -> dict[str, Any]:
    source = bank["questions"][ordinal - 1]
    localized = source[bank["default_locale"]]
    return {
        "question_id": source["question_id"],
        "ordinal": ordinal,
        "text": localized["text"],
        "rationale": localized["rationale"],
        "decision_consequence": localized["decision_consequence"],
        "answer_examples": list(localized["answer_examples"]),
        "topics": list(source["topics"]),
    }


_FIELD_POINTER = re.compile(
    r"^/(?:intake/questions/[0-9]+/(?:text|rationale|decision_consequence|answer_examples/[0-9]+)|intake/(?:completion_reason|assumptions/[0-9]+|answers/[0-9]+/sanitized_value)|brief/(?:goal|success_criterion|assumptions/[0-9]+)|brief/details/(?:problem|target_user|workflow|current_behavior|target_behavior|baseline|scope)/(?:text|limitation)|brief/details/non_goals/[0-9]+/(?:text|limitation)|brief/details/constraint_notes/[0-9]+/(?:claim/text|claim/limitation|consequence)|brief/details/tensions/[0-9]+/(?:detail|next_decision)|brief/observations/(?:facts/[0-9]+/value|inferences/[0-9]+/statement|gaps/[0-9]+/(?:detail|next_check))|scan/summary/(?:facts/[0-9]+/value|inferences/[0-9]+/statement|gaps/[0-9]+/(?:detail|next_check))|corrections/[0-9]+/sanitized_correction|memo/(?:summary|next_action|comparison/[0-9]+|avoid_defer/[0-9]+|missing_context/[0-9]+|reading_path/[0-9]+/purpose|category_path/[0-9]+/reason)|memo/recommendations/[0-9]+/(?:fit_rationale|caveats/[0-9]+|next_checks/[0-9]+)|memo/comparison_details/(?:scope|selection_rationale|strongest_counterargument|reconsider_when|next_decision|cells/[0-9]+/(?:claim/text|claim/limitation|next_check))|memo/avoid_defer_details/[0-9]+/(?:rationale|revisit_when)|memo/integration_plan/(?:goal|integration_surface|prerequisites/[0-9]+|risks/[0-9]+|rollback/[0-9]+|unresolved_questions/[0-9]+)|memo/integration_plan/steps/[0-9]+/(?:action|prerequisites/[0-9]+|acceptance)|memo/integration_plan/first_validation/(?:goal|success_criterion)|memo/integration_plan/handoff/(?:goal|scope|non_goals/[0-9]+|stop_conditions/[0-9]+)|memo/integration_plan/details/(?:validation_input|expected_behavior|widen_when|diagram/(?:nodes/[0-9]+/label|edges/[0-9]+/label)|prerequisite_checks/[0-9]+/(?:detail|next_check)))$"
)


def _narrative_fields(state: dict[str, Any]) -> dict[str, str]:
    found: dict[str, str] = {}

    def visit(value: Any, pointer: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key != "presentation":
                    visit(child, pointer + "/" + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, pointer + "/" + str(index))
        elif isinstance(value, str) and _FIELD_POINTER.fullmatch(pointer):
            found[pointer] = value

    visit(state)
    return found


def _json_string_hash(value: str) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _pointer_value(state: dict[str, Any], pointer: str) -> Any:
    value: Any = state
    for component in pointer.strip("/").split("/"):
        value = value[int(component)] if isinstance(value, list) else value[component]
    return value


def _fixed_translations(state: dict[str, Any], bank: dict[str, Any]) -> dict[str, tuple[str, str]]:
    translations: dict[str, tuple[str, str]] = {}
    by_id = {question["question_id"]: question for question in bank["questions"]}
    for index, question in enumerate(state["intake"]["questions"]):
        source = by_id.get(question["question_id"])
        if not source:
            continue
        for field in ("text", "rationale", "decision_consequence"):
            translations[f"/intake/questions/{index}/{field}"] = (source["ru"][field], source["en"][field])
        for example_index in range(len(question["answer_examples"])):
            translations[f"/intake/questions/{index}/answer_examples/{example_index}"] = (
                source["ru"]["answer_examples"][example_index],
                source["en"]["answer_examples"][example_index],
            )
    reason = state["intake"].get("completion_reason")
    if reason == "Контекста достаточно для перехода к проверке проекта.":
        translations["/intake/completion_reason"] = (
            reason, "The available context is sufficient to proceed to project review."
        )
    elif reason == "Достигнут предел из десяти вопросов; оставшиеся неизвестные сохраняются явно.":
        translations["/intake/completion_reason"] = (
            reason, "The ten-question limit was reached; remaining unknowns stay explicit."
        )
    return translations


def _rebind_presentation(state: dict[str, Any], bank: dict[str, Any], *, initial: bool = False) -> None:
    current = state.get("presentation") or {}
    fields = _narrative_fields(state)
    retained: dict[str, dict[str, Any]] = {}
    for entry in current.get("fields", []):
        pointer = entry.get("field_pointer") if isinstance(entry, dict) else None
        if pointer in fields and entry.get("source_sha256") == _json_string_hash(fields[pointer]):
            copied = copy.deepcopy(entry)
            copied["source_content_revision"] = state["content_revision"]
            retained[pointer] = copied
    for pointer, (ru_text, en_text) in _fixed_translations(state, bank).items():
        if pointer not in fields or fields[pointer] != ru_text:
            continue
        retained[pointer] = {
            "field_pointer": pointer,
            "source_locale": "ru",
            "source_sha256": _json_string_hash(ru_text),
            "source_content_revision": state["content_revision"],
            "evidence_refs": [],
            "canonical_literals": [],
            "ru": {"status": "available", "text": ru_text},
            "en": {"status": "available", "text": en_text},
        }
    entries = [retained[key] for key in sorted(retained)]
    coverage: dict[str, dict[str, Any]] = {}
    for locale in ("ru", "en"):
        available = sum(entry[locale]["status"] == "available" for entry in entries)
        coverage[locale] = {
            "status": "complete" if available == len(fields) else "partial",
            "required_fields": len(fields),
            "available_fields": available,
        }
    brief = state.get("brief")
    memo = state.get("memo")
    plan = memo.get("integration_plan") if isinstance(memo, dict) else None
    state["presentation"] = {
        "schema_version": "1.1.0",
        "run_id": state["run_id"],
        "default_locale": current.get("default_locale", bank["default_locale"]),
        "source_locale": current.get("source_locale", "ru"),
        "presentation_revision": 1 if initial else current.get("presentation_revision", 0) + 1,
        "source_content_revision": state["content_revision"],
        "brief_id": brief.get("brief_id") if isinstance(brief, dict) else None,
        "brief_version": brief.get("brief_version") if isinstance(brief, dict) else None,
        "memo_id": memo.get("memo_id") if isinstance(memo, dict) else None,
        "plan_id": plan.get("plan_id") if isinstance(plan, dict) else None,
        "fields": entries,
        "coverage": coverage,
    }


def _prior_html_revision(locked: Any, new_revision: int, run_id: str) -> int | None:
    receipt = store.published_receipt(locked.root)
    if receipt and receipt["run_id"] == run_id and receipt["revision"] < new_revision:
        return receipt["revision"]
    return None


def _new_state(bank: dict[str, Any], history: list[dict[str, Any]], predecessor: str | None, manifest: dict[str, Any]) -> dict[str, Any]:
    run_id = str(uuid.uuid4())
    now = store.utc_now()
    first = _question(bank, 1)
    state = {
        "schema_version": "1.1.0",
        "owner_marker": "myai-stackguide.state.v1",
        "run_id": run_id,
        "predecessor_run_id": predecessor,
        "revision": 1,
        "content_revision": 1,
        "status": "active",
        "phase": "intake",
        "created_at": now,
        "updated_at": now,
        "intake": {
            "schema_version": "1.1.0",
            "run_id": run_id,
            "status": "asking",
            "questions_asked": 1,
            "answers": [],
            "pending_question_id": first["question_id"],
            "next_action": "answer_question",
            "assumptions": [],
            "questions": [first],
            "completion_reason": None,
        },
        "brief": None,
        "selection": None,
        "request": None,
        "index_manifest": manifest,
        "retrieval": None,
        "evidence_pack": None,
        "memo": None,
        "corrections": [],
        "html_revision": None,
        "history": copy.deepcopy(history),
        "storage_policy_version": store.STORAGE_POLICY_VERSION,
        "presentation": {},
        "scan": None,
    }
    _rebind_presentation(state, bank, initial=True)
    return state


def _expected(state: dict[str, Any], run_id: str | None, revision: int | None) -> None:
    if run_id is None or revision is None:
        raise store.StateError("invalid_input")
    if state["run_id"] != run_id or state["revision"] != revision:
        raise store.StateError("state_conflict")


def _invalidate(state: dict[str, Any]) -> None:
    for key in ("selection", "request", "retrieval", "evidence_pack", "memo"):
        state[key] = None


def _advance_revision(state: dict[str, Any], locked: Any, bank: dict[str, Any]) -> None:
    state["revision"] += 1
    state["content_revision"] += 1
    state["updated_at"] = store.utc_now()
    state["html_revision"] = _prior_html_revision(locked, state["revision"], state["run_id"])
    _rebind_presentation(state, bank)


def _validate_empty(payload: dict[str, Any]) -> None:
    if payload:
        raise store.StateError("invalid_input")


def _validate_answer_payload(payload: dict[str, Any]) -> None:
    if set(payload) != {"answer_id", "question_id", "status", "value", "ready"}:
        raise store.StateError("invalid_input")
    if not isinstance(payload["answer_id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", payload["answer_id"]):
        raise store.StateError("invalid_input")
    if not isinstance(payload["question_id"], str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", payload["question_id"]):
        raise store.StateError("invalid_input")
    if payload["status"] not in ("answered", "skipped") or not isinstance(payload["ready"], bool):
        raise store.StateError("invalid_input")
    if payload["status"] == "answered" and not isinstance(payload["value"], str):
        raise store.StateError("invalid_input")
    if payload["status"] == "skipped" and payload["value"] is not None:
        raise store.StateError("invalid_input")


def _answer_value(payload: dict[str, Any]) -> tuple[str | None, bool]:
    if payload["status"] == "skipped":
        return None, False
    return sanitizer.sanitize_text(payload["value"], max_code_points=2000)


def command_start(project_root: Path, payload: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    _validate_empty(payload)
    bank = _load_question_bank()
    with store.locked_store(project_root, create=True) as locked:
        previous = locked.load(required=False)
        history: list[dict[str, Any]] = []
        predecessor: str | None = None
        if previous is not None:
            if previous["schema_version"] != "1.1.0":
                raise store.StateError("state_incompatible")
            if previous["status"] == "active":
                raise store.StateError("state_conflict")
            locked.ensure_history(previous)
            history = copy.deepcopy(previous["history"])
            predecessor = previous["run_id"]
            scanner.remove_checkpoint_locked(locked.root, run_id=previous["run_id"])
        state = _new_state(bank, history, predecessor, manifest)
        locked.commit(state, previous)
    return _publication_success(state, operation="commit_and_publish", commit_status="saved")


def command_answer(project_root: Path, payload: dict[str, Any], run_id: str | None, revision: int | None) -> dict[str, Any]:
    _validate_answer_payload(payload)
    if payload["status"] == "skipped" and payload["ready"]:
        raise store.StateError("invalid_input")
    value, redacted = _answer_value(payload)
    bank = _load_question_bank()
    with store.locked_store(project_root, create=False) as locked:
        current = locked.load(required=True, writable=True)
        assert current is not None
        existing = next((item for item in current["intake"]["answers"] if item["answer_id"] == payload["answer_id"]), None)
        if existing is not None:
            expected_ready = payload["ready"] or (
                existing["ordinal"] == 10
                and any(item["status"] == "answered" for item in current["intake"]["answers"])
            )
            same = (
                run_id is not None
                and revision is not None
                and current["run_id"] == run_id
                and current["revision"] == revision + 1
                and existing["expected_state_revision"] == revision
                and existing["question_id"] == payload["question_id"]
                and existing["status"] == payload["status"]
                and existing["sanitized_value"] == value
                and existing["redaction_applied"] == redacted
                and (current["intake"]["status"] == "ready") == expected_ready
            )
            if not same:
                raise store.StateError("state_conflict")
            state = current
        else:
            _expected(current, run_id, revision)
            if current["status"] != "active" or current["phase"] != "intake" or current["intake"]["status"] not in ("asking", "ready"):
                raise store.StateError("state_conflict")
            intake = current["intake"]
            if intake["pending_question_id"] != payload["question_id"]:
                raise store.StateError("state_conflict")
            question = next(item for item in intake["questions"] if item["question_id"] == payload["question_id"])
            state = copy.deepcopy(current)
            answer = {
                "schema_version": "1.1.0",
                "run_id": state["run_id"],
                "answer_id": payload["answer_id"],
                "question_id": payload["question_id"],
                "ordinal": question["ordinal"],
                "answer_revision": 1,
                "expected_state_revision": current["revision"],
                "status": payload["status"],
                "sanitized_value": value,
                "redaction_applied": redacted,
                "recorded_at": store.utc_now(),
                "last_correction_id": None,
            }
            state["intake"]["answers"].append(answer)
            answered_exists = any(item["status"] == "answered" for item in state["intake"]["answers"])
            if (payload["ready"] or state["intake"]["questions_asked"] == 10) and answered_exists:
                state["intake"].update(
                    status="ready", pending_question_id=None,
                    next_action="review_context",
                    completion_reason=(
                        "Контекста достаточно для перехода к проверке проекта."
                        if payload["ready"] else
                        "Достигнут предел из десяти вопросов; оставшиеся неизвестные сохраняются явно."
                    ),
                )
            elif state["intake"]["questions_asked"] == 10:
                state["intake"].update(
                    status="cancelled", pending_question_id=None,
                    next_action="resume_or_finalize", completion_reason=None,
                )
            else:
                ordinal = state["intake"]["questions_asked"] + 1
                question = _question(bank, ordinal)
                state["intake"]["questions"].append(question)
                state["intake"]["questions_asked"] = ordinal
                state["intake"]["pending_question_id"] = question["question_id"]
                state["intake"]["status"] = "asking"
                state["intake"]["next_action"] = "answer_question"
                state["intake"]["completion_reason"] = None
            _advance_revision(state, locked, bank)
            locked.commit(state, current)
    return _publication_success(state, operation="commit_and_publish", commit_status="saved")


def command_cancel(project_root: Path, payload: dict[str, Any], run_id: str | None, revision: int | None) -> dict[str, Any]:
    _validate_empty(payload)
    bank = _load_question_bank()
    with store.locked_store(project_root, create=False) as locked:
        current = locked.load(required=True, writable=True)
        assert current is not None
        if current["intake"]["status"] == "cancelled" and current["status"] == "active":
            state = current
        else:
            _expected(current, run_id, revision)
            if current["status"] != "active" or current["phase"] != "intake" or current["intake"]["status"] not in ("asking", "ready"):
                raise store.StateError("state_conflict")
            state = copy.deepcopy(current)
            pending = state["intake"]["pending_question_id"]
            if pending is not None:
                state["intake"]["questions"] = [
                    item for item in state["intake"]["questions"] if item["question_id"] != pending
                ]
                state["intake"]["questions_asked"] = len(state["intake"]["questions"])
            state["intake"].update(
                status="cancelled", pending_question_id=None,
                next_action="resume_or_finalize", completion_reason=None,
            )
            _advance_revision(state, locked, bank)
            locked.commit(state, current)
    return _publication_success(state, operation="commit_and_publish", commit_status="saved")


def command_resume(project_root: Path, payload: dict[str, Any], run_id: str | None, revision: int | None) -> dict[str, Any]:
    _validate_empty(payload)
    bank = _load_question_bank()
    with store.locked_store(project_root, create=False) as locked:
        current = locked.load(required=True, writable=True)
        assert current is not None
        if current["status"] == "active" and current["phase"] == "intake" and current["intake"]["status"] == "asking":
            _expected(current, run_id, revision)
            state = current
        else:
            _expected(current, run_id, revision)
            if current["status"] != "active" or current["phase"] != "intake" or current["intake"]["status"] != "cancelled":
                raise store.StateError("state_conflict")
            state = copy.deepcopy(current)
            ordinal = state["intake"]["questions_asked"] + 1
            if ordinal > 10:
                if any(item["status"] == "answered" for item in state["intake"]["answers"]):
                    state["intake"].update(
                        status="ready", pending_question_id=None, next_action="review_context",
                        completion_reason="Достигнут предел из десяти вопросов; оставшиеся неизвестные сохраняются явно.",
                    )
                else:
                    state = current
            else:
                question = _question(bank, ordinal)
                state["intake"]["questions"].append(question)
                state["intake"].update(
                    status="asking", questions_asked=ordinal,
                    pending_question_id=question["question_id"], next_action="answer_question",
                    completion_reason=None,
                )
            if state is not current:
                _advance_revision(state, locked, bank)
                locked.commit(state, current)
    return _publication_success(state, operation="commit_and_publish", commit_status="saved")


def _validate_commit_scan_payload(project_root: Path, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if set(payload) != {"report", "checkpoint"} or not isinstance(payload.get("report"), dict):
        raise store.StateError("invalid_input")
    try:
        checkpoint = scanner._validate_checkpoint_envelope(payload.get("checkpoint"))
    except scanner.ScannerError as error:
        raise store.StateError("invalid_input") from error
    report = payload["report"]
    required = {
        "schema_version", "run_id", "policy_version", "mode", "status", "classification",
        "manifest", "summary", "reason_codes",
    }
    if (
        set(report) != required
        or report.get("schema_version") != scanner.SCHEMA_VERSION
        or report.get("policy_version") != scanner.POLICY_VERSION
        or report.get("mode") not in scanner.MODES
        or report.get("status") not in ("complete", "partial", "cancelled", "unavailable")
        or report != checkpoint.get("last_report")
        or report.get("run_id") != checkpoint.get("run_id")
    ):
        raise store.StateError("invalid_input")
    try:
        scanner.ScannerSession.from_checkpoint(
            project_root,
            report["run_id"],
            checkpoint,
            limit_overrides=checkpoint["session"]["limit_overrides"] or None,
        )
    except scanner.ScannerError as error:
        raise store.StateError("invalid_input") from error
    return report, checkpoint


def command_commit_scan(project_root: Path, payload: dict[str, Any], run_id: str | None, revision: int | None) -> dict[str, Any]:
    report, checkpoint = _validate_commit_scan_payload(project_root, payload)
    bank = _load_question_bank()
    with store.locked_store(project_root, create=False) as locked:
        current = locked.load(required=True, writable=True)
        assert current is not None
        immediate_retry = (
            run_id is not None
            and revision is not None
            and current["run_id"] == run_id
            and current["revision"] == revision + 1
            and current.get("scan") == report
            and checkpoint["expected_state_revision"] == revision
            and checkpoint["committed_state_revision"] == current["revision"]
        )
        if immediate_retry:
            state = current
            try:
                persisted = scanner.read_checkpoint_locked(locked.root)
            except scanner.ScannerError as error:
                raise store.StateError("state_conflict") from error
            if (
                persisted.get("checkpoint_id") != checkpoint.get("checkpoint_id")
                or store.canonical_json_bytes(persisted) != store.canonical_json_bytes(checkpoint)
            ):
                raise store.StateError("state_conflict")
        else:
            _expected(current, run_id, revision)
            if (
                current["status"] != "active"
                or current["phase"] not in ("intake", "scan")
                or current["intake"]["status"] != "ready"
                or report["run_id"] != current["run_id"]
                or checkpoint["expected_state_revision"] != current["revision"]
                or checkpoint["committed_state_revision"] != current["revision"] + 1
            ):
                raise store.StateError("state_conflict")
            state = copy.deepcopy(current)
            state["scan"] = copy.deepcopy(report)
            state["phase"] = "scan"
            state["intake"]["next_action"] = "review_context"
            _invalidate(state)
            _advance_revision(state, locked, bank)
            scanner.write_checkpoint_locked(locked.root, checkpoint)
            locked.commit(state, current)
    return _publication_success(state, operation="commit_and_publish", commit_status="saved")


def _validate_commit_context_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if set(payload) != {"selection", "brief"}:
        raise store.StateError("invalid_input")
    try:
        selection = context.validate_context_selection(payload.get("selection"))
        brief = context.validate_project_context_brief(payload.get("brief"))
    except context.ContextError as error:
        raise store.StateError("invalid_input") from error
    return selection, brief


def command_commit_context(project_root: Path, payload: dict[str, Any], run_id: str | None, revision: int | None) -> dict[str, Any]:
    selection, brief = _validate_commit_context_payload(payload)
    bank = _load_question_bank()
    with store.locked_store(project_root, create=False) as locked:
        current = locked.load(required=True, writable=True)
        assert current is not None
        immediate_retry = (
            run_id is not None
            and revision is not None
            and current["run_id"] == run_id
            and current["revision"] == revision + 1
            and current.get("selection") == selection
            and current.get("brief") == brief
        )
        if immediate_retry:
            state = current
        else:
            _expected(current, run_id, revision)
            scan = current.get("scan")
            if (
                current["status"] != "active"
                or current["phase"] not in ("scan", "context_review")
                or current["intake"]["status"] != "ready"
                or not isinstance(scan, dict)
                or selection["run_id"] != current["run_id"]
                or brief["run_id"] != current["run_id"]
                or selection["brief_version"] != brief["brief_version"]
                or selection["mode"] != scan.get("mode")
                or selection["scan_policy_version"] != scan.get("policy_version")
                or brief["observations"] != scan.get("summary")
            ):
                raise store.StateError("state_conflict")
            try:
                policy = scanner.load_policy()
                scanner.validate_scan_report(scan, policy)
            except scanner.ScannerError as error:
                raise store.StateError("state_conflict") from error
            try:
                checkpoint = scanner.read_checkpoint_locked(locked.root)
                if (
                    checkpoint.get("run_id") != current["run_id"]
                    or checkpoint.get("last_report") != scan
                ):
                    raise store.StateError("state_conflict")
                scanner.ScannerSession.from_checkpoint(
                    project_root,
                    current["run_id"],
                    checkpoint,
                    limit_overrides=checkpoint["session"]["limit_overrides"] or None,
                )
            except scanner.ScannerError as error:
                raise store.StateError("state_conflict") from error
            try:
                context.validate_context_commit(
                    selection,
                    brief,
                    scan,
                    current,
                    policy,
                    canonical_brief=current.get("brief"),
                    scan_records=checkpoint["session"]["records"],
                )
            except context.ContextError as error:
                raise store.StateError("invalid_input") from error
            state = copy.deepcopy(current)
            _invalidate(state)
            state["selection"] = copy.deepcopy(selection)
            state["brief"] = copy.deepcopy(brief)
            state["phase"] = "context_review"
            state["intake"]["status"] = "ready"
            state["intake"]["pending_question_id"] = None
            state["intake"]["next_action"] = "review_context"
            _advance_revision(state, locked, bank)
            locked.commit(state, current)
        scanner.remove_checkpoint_locked(locked.root, run_id=state["run_id"])
    return _publication_success(state, operation="commit_and_publish", commit_status="saved")


def _validate_correction_payload(payload: dict[str, Any]) -> str:
    pre = {"correction_id", "answer_id", "value", "ready"}
    post = {"correction_id", "target", "value"}
    if set(payload) == pre:
        branch = "pre"
        if not isinstance(payload["answer_id"], str) or not isinstance(payload["ready"], bool):
            raise store.StateError("invalid_input")
    elif set(payload) == post:
        branch = "post"
        if payload["target"] not in {
            "goal", "success_criterion", "constraints", "project_stage", "assumption",
            "observation_interpretation", "context_details",
        }:
            raise store.StateError("invalid_input")
    else:
        raise store.StateError("invalid_input")
    if not isinstance(payload["correction_id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", payload["correction_id"]):
        raise store.StateError("invalid_input")
    if not isinstance(payload["value"], str):
        raise store.StateError("invalid_input")
    return branch


def command_correct(project_root: Path, payload: dict[str, Any], run_id: str | None, revision: int | None) -> dict[str, Any]:
    branch = _validate_correction_payload(payload)
    value, redacted = sanitizer.sanitize_text(
        payload["value"], max_code_points=2000 if branch == "pre" else 1000
    )
    bank = _load_question_bank()
    with store.locked_store(project_root, create=False) as locked:
        current = locked.load(required=True, writable=True)
        assert current is not None
        if current["status"] != "active":
            raise store.StateError("state_conflict")
        if current["brief"] is None:
            if branch != "pre":
                raise store.StateError("invalid_input")
            answer = next((item for item in current["intake"]["answers"] if item["answer_id"] == payload["answer_id"]), None)
            if answer is None:
                raise store.StateError("state_conflict")
            if answer.get("last_correction_id") == payload["correction_id"]:
                immediate_retry = (
                    run_id is not None
                    and revision is not None
                    and current["run_id"] == run_id
                    and current["revision"] == revision + 1
                    and answer["expected_state_revision"] == revision
                    and answer["schema_version"] == "1.1.0"
                    and answer["status"] == "answered"
                    and answer["sanitized_value"] == value
                    and answer["redaction_applied"] == redacted
                )
                if not immediate_retry:
                    raise store.StateError("state_conflict")
                state = current
            else:
                _expected(current, run_id, revision)
                state = copy.deepcopy(current)
                changed = next(item for item in state["intake"]["answers"] if item["answer_id"] == payload["answer_id"])
                changed.update(
                    schema_version="1.1.0",
                    answer_revision=changed["answer_revision"] + 1,
                    expected_state_revision=current["revision"],
                    status="answered", sanitized_value=value,
                    redaction_applied=redacted, recorded_at=store.utc_now(),
                    last_correction_id=payload["correction_id"],
                )
                if payload["ready"]:
                    pending = state["intake"]["pending_question_id"]
                    if pending is not None:
                        state["intake"]["questions"] = [
                            item for item in state["intake"]["questions"] if item["question_id"] != pending
                        ]
                        state["intake"]["questions_asked"] = len(state["intake"]["questions"])
                    state["intake"].update(
                        status="ready", pending_question_id=None, next_action="review_context",
                        completion_reason="Контекста достаточно для перехода к проверке проекта.",
                    )
                state["phase"] = "intake"
                _invalidate(state)
                _advance_revision(state, locked, bank)
                locked.commit(state, current)
        else:
            if branch != "post":
                raise store.StateError("invalid_input")
            previous_event = next((item for item in current["corrections"] if item["correction_id"] == payload["correction_id"]), None)
            if previous_event is not None:
                immediate_retry = (
                    run_id is not None
                    and revision is not None
                    and current["run_id"] == run_id
                    and current["revision"] == revision + 1
                    and previous_event.get("expected_state_revision") == revision
                    and previous_event.get("schema_version") == "1.1.0"
                    and previous_event["target"] == payload["target"]
                    and previous_event["sanitized_correction"] == value
                )
                if not immediate_retry:
                    raise store.StateError("state_conflict")
                state = current
            else:
                _expected(current, run_id, revision)
                state = copy.deepcopy(current)
                brief = state["brief"]
                assert isinstance(brief, dict)
                from_version = brief["brief_version"]
                target = payload["target"]
                try:
                    brief = context.apply_brief_correction(
                        brief, target, value, payload["correction_id"]
                    )
                except context.ContextError as error:
                    reason = "storage_limit" if error.reason == "brief_too_large" else "invalid_input"
                    raise store.StateError(reason) from error
                brief["brief_version"] = from_version + 1
                brief["updated_at"] = store.utc_now()
                try:
                    context.validate_project_context_brief(brief)
                except context.ContextError as error:
                    reason = "storage_limit" if error.reason == "brief_too_large" else "invalid_input"
                    raise store.StateError(reason) from error
                state["brief"] = brief
                invalidates = [
                    "selection", "request", "retrieval_result", "evidence_pack", "recommendation_memo"
                ]
                state["corrections"].append({
                    "schema_version": "1.1.0",
                    "run_id": state["run_id"],
                    "correction_id": payload["correction_id"],
                    "expected_state_revision": current["revision"],
                    "from_brief_version": from_version,
                    "to_brief_version": from_version + 1,
                    "target": target,
                    "sanitized_correction": value,
                    "recorded_at": store.utc_now(),
                    "invalidates": invalidates,
                    "observed_facts_mutated": False,
                })
                state["phase"] = "context_review"
                state["intake"]["status"] = "ready"
                state["intake"]["pending_question_id"] = None
                state["intake"]["next_action"] = "review_context"
                _invalidate(state)
                _advance_revision(state, locked, bank)
                locked.commit(state, current)
    return _publication_success(state, operation="commit_and_publish", commit_status="saved")


def command_finalize(project_root: Path, payload: dict[str, Any], run_id: str | None, revision: int | None) -> dict[str, Any]:
    _validate_empty(payload)
    bank = _load_question_bank()
    with store.locked_store(project_root, create=False) as locked:
        current = locked.load(required=True, writable=True)
        assert current is not None
        if current["status"] in ("finalized", "finalized_incomplete"):
            _expected(current, run_id, revision)
            locked.ensure_history(current)
            state = current
        else:
            _expected(current, run_id, revision)
            state = copy.deepcopy(current)
            complete = (
                state["phase"] == "report"
                and state["intake"]["status"] == "ready"
                and state["memo"] is not None
            )
            state["status"] = "finalized" if complete else "finalized_incomplete"
            if not complete and state["phase"] == "intake" and state["intake"]["status"] == "asking":
                pending = state["intake"]["pending_question_id"]
                state["intake"]["questions"] = [
                    item for item in state["intake"]["questions"] if item["question_id"] != pending
                ]
                state["intake"]["questions_asked"] = len(state["intake"]["questions"])
                state["intake"].update(
                    status="cancelled", pending_question_id=None,
                    next_action="resume_or_finalize", completion_reason=None,
                )
            state["revision"] += 1
            state["content_revision"] += 1
            state["updated_at"] = store.utc_now()
            state["html_revision"] = _prior_html_revision(locked, state["revision"], state["run_id"])
            if len(state["history"]) >= 100:
                raise store.StateError("storage_limit")
            state["history"].append({
                "run_id": state["run_id"],
                "final_revision": state["revision"],
                "status": state["status"],
            })
            _rebind_presentation(state, bank)
            data = store.canonical_json_bytes(store.validate_state(state, writable=True))
            destination = locked.root / "runs" / f"{state['run_id']}.json"
            if destination.exists() and store._validate_regular_file(destination, max_bytes=store.MAX_STATE_BYTES) != data:
                raise store.StateError("history_integrity")
            locked.commit(state, current)
            locked.ensure_history(state, data)
        scanner.remove_checkpoint_locked(locked.root, run_id=state["run_id"])
    return _publication_success(state, operation="commit_and_publish", commit_status="saved")


def command_retry(project_root: Path, payload: dict[str, Any], run_id: str | None, revision: int | None) -> dict[str, Any]:
    _validate_empty(payload)
    with store.locked_store(project_root, create=False) as locked:
        state = locked.load(required=True)
        assert state is not None
        _expected(state, run_id, revision)
    return _publication_success(state, operation="render_only", commit_status="not_attempted")


_ACTIVE_ROOT: Path


def main(argv: list[str]) -> int:
    global _ACTIVE_ROOT
    command = "start"
    operation = "commit_and_publish"
    try:
        command, raw_root, run_id, revision = _parse_cli(argv)
        operation = "render_only" if command == "retry-publication" else "commit_and_publish"
        try:
            payload = _read_payload(command)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            if command == "preflight":
                result = _preflight_result(
                    "invalid_input", python_implementation=None, python_version=None,
                    sqlite_version=None, fts5_available=None, root_valid=False,
                )
            else:
                result = _publication_failure("invalid_input", operation=operation)
            _emit(result)
            return 0
        preflight, project_root, manifest = run_preflight(payload if command == "preflight" else {}, raw_root)
        if command == "preflight":
            _emit(preflight)
            return 0
        if preflight["status"] != "ready" or project_root is None or manifest is None:
            _emit(_publication_failure("state_incompatible", operation=operation))
            return 0
        _ACTIVE_ROOT = project_root
        if command == "start":
            result = command_start(project_root, payload, manifest)
        elif command == "answer":
            result = command_answer(project_root, payload, run_id, revision)
        elif command == "cancel":
            result = command_cancel(project_root, payload, run_id, revision)
        elif command == "resume":
            result = command_resume(project_root, payload, run_id, revision)
        elif command == "correct":
            result = command_correct(project_root, payload, run_id, revision)
        elif command == "commit-scan":
            result = command_commit_scan(project_root, payload, run_id, revision)
        elif command == "commit-context":
            result = command_commit_context(project_root, payload, run_id, revision)
        elif command == "finalize":
            result = command_finalize(project_root, payload, run_id, revision)
        else:
            result = command_retry(project_root, payload, run_id, revision)
    except sanitizer.SanitizationError as error:
        result = _publication_failure(
            "invalid_input", operation=operation, message_key=error.message_key
        )
    except store.StateError as error:
        reason = error.reason
        if reason == "invalid_root":
            reason = "state_write_failed"
        result = _publication_failure(reason, operation=operation)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError, IndexError):
        result = _publication_failure("state_invalid", operation=operation)
    _emit(result)
    return 0


def _emit(value: dict[str, Any]) -> None:
    data = store.canonical_json_bytes(value)
    if len(data) > 8191 or sanitizer.contains_named_canary(data):
        data = store.canonical_json_bytes(_publication_failure("state_invalid"))
    sys.stdout.buffer.write(data + b"\n")
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
