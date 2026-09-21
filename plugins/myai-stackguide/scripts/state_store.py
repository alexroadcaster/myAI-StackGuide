"""Single CP-07 state writer, immutable history, and publication boundary."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
from typing import Any, Callable, Iterator
import uuid


OUTPUT_RELATIVE = Path("docs") / "myai-stackguide"
STATE_NAME = "state.json"
HTML_NAME = "status.html"
LOCK_NAME = ".state.lock"
PREVIOUS_NAME = "state.previous.json"
STATE_PENDING = ".state.pending.json"
PREVIOUS_PENDING = ".previous.pending.json"
RUN_PENDING = ".run.pending.json"
HTML_PENDING = ".status.pending.html"

MAX_STATE_BYTES = 2_097_152
MAX_HTML_BYTES = 5_242_880
MAX_TOTAL_BYTES = 268_435_456
MAX_FILE_ENTRIES = 128
MAX_HISTORY = 100
LOCK_WAIT_SECONDS = 2.0

STATE_OWNER = "myai-stackguide.state.v1"
HTML_OWNER = "myai-stackguide.status.v1"
_HTML_MARKER_PREFIX = b"<!--MYAI_STACKGUIDE_STATUS_V1 "
_HTML_MARKER_SUFFIX = b" -->"


class StateError(RuntimeError):
    """Typed safe failure. Its message is deliberately not externally emitted."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        raise StateError("state_invalid") from error


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def strict_json_bytes(data: bytes) -> Any:
    try:
        text = data.decode("utf-8", errors="strict")
        return json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise StateError("state_invalid") from error


def _contains_canary(data: bytes) -> bool:
    return any(
        value in data
        for value in (
            b"STACKGUIDE_TEST_TOKEN=STACKGUIDE_TEST_SECRET_7f4c2a90",
            b"STACKGUIDE_TEST_SECRET_7f4c2a90",
            b"-----BEGIN STACKGUIDE TEST SECRET-----",
            b"-----END STACKGUIDE TEST SECRET-----",
        )
    )


def _is_reparse(path: Path) -> bool:
    try:
        stat_result = path.lstat()
    except OSError as error:
        raise StateError("state_write_failed") from error
    attributes = getattr(stat_result, "st_file_attributes", 0)
    reparse = getattr(__import__("stat"), "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(attributes & reparse)


def validate_project_root(raw_root: str | os.PathLike[str]) -> Path:
    """Return an existing canonical local directory without exposing it in errors."""

    try:
        supplied = Path(raw_root)
        if not supplied.is_absolute():
            supplied = Path.cwd() / supplied
        root = supplied.resolve(strict=True)
        if not root.is_dir() or _is_reparse(root):
            raise StateError("invalid_root")
        if os.name == "nt" and str(root).startswith("\\\\"):
            raise StateError("invalid_root")
        return root
    except StateError:
        raise
    except (OSError, RuntimeError, ValueError, TypeError) as error:
        raise StateError("invalid_root") from error


def _ensure_plain_directory(path: Path, *, create: bool) -> None:
    if path.exists():
        if not path.is_dir() or _is_reparse(path):
            raise StateError("state_invalid")
        return
    if not create:
        raise StateError("state_invalid")
    try:
        path.mkdir()
    except OSError as error:
        raise StateError("state_write_failed") from error
    if not path.is_dir() or _is_reparse(path):
        raise StateError("state_invalid")


def output_root(project_root: Path, *, create: bool) -> Path:
    docs = project_root / "docs"
    _ensure_plain_directory(docs, create=create)
    output = docs / "myai-stackguide"
    _ensure_plain_directory(output, create=create)
    try:
        if os.path.commonpath((str(project_root), str(output.resolve(strict=True)))) != str(project_root):
            raise StateError("state_invalid")
    except (OSError, ValueError) as error:
        raise StateError("state_invalid") from error
    return output


def _validate_regular_file(path: Path, *, max_bytes: int) -> bytes:
    try:
        if _is_reparse(path) or not path.is_file():
            raise StateError("state_invalid")
        info = path.stat()
        if info.st_nlink != 1 or info.st_size > max_bytes:
            raise StateError("state_invalid")
        return path.read_bytes()
    except StateError:
        raise
    except OSError as error:
        raise StateError("state_write_failed") from error


def state_stamp(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": state["run_id"],
        "revision": state["revision"],
        "content_revision": state.get("content_revision", state["revision"]),
    }


def _valid_uuid(value: Any) -> bool:
    try:
        return isinstance(value, str) and str(uuid.UUID(value)) == value.lower()
    except (ValueError, AttributeError):
        return False


def _valid_timestamp(value: Any) -> bool:
    return isinstance(value, str) and bool(
        re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value)
    )


def validate_state(state: Any, *, writable: bool = False) -> dict[str, Any]:
    if not isinstance(state, dict):
        raise StateError("state_invalid")
    required = {
        "schema_version", "owner_marker", "run_id", "predecessor_run_id", "revision",
        "status", "phase", "created_at", "updated_at", "intake", "brief", "selection",
        "request", "index_manifest", "retrieval", "evidence_pack", "memo", "corrections",
        "html_revision", "history", "storage_policy_version",
    }
    if not required <= state.keys():
        raise StateError("state_invalid")
    allowed = required | {"content_revision", "presentation", "scan"}
    if set(state) - allowed:
        raise StateError("state_invalid")
    version = state.get("schema_version")
    if version not in ("1.0.0", "1.1.0"):
        raise StateError("state_incompatible")
    if writable and version != "1.1.0":
        raise StateError("state_incompatible")
    if state.get("owner_marker") != STATE_OWNER or state.get("storage_policy_version") != "1.0.0":
        raise StateError("state_invalid")
    if not _valid_uuid(state.get("run_id")):
        raise StateError("state_invalid")
    predecessor = state.get("predecessor_run_id")
    if predecessor is not None and (not _valid_uuid(predecessor) or predecessor == state["run_id"]):
        raise StateError("state_invalid")
    revision = state.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or not 1 <= revision <= 1_000_000:
        raise StateError("state_invalid")
    if not _valid_timestamp(state.get("created_at")) or not _valid_timestamp(state.get("updated_at")):
        raise StateError("state_invalid")
    if version == "1.0.0":
        if any(key in state for key in ("content_revision", "presentation", "scan")):
            raise StateError("state_invalid")
    else:
        if not {"content_revision", "presentation", "scan"} <= state.keys():
            raise StateError("state_invalid")
        content_revision = state.get("content_revision")
        if not isinstance(content_revision, int) or isinstance(content_revision, bool) or not 1 <= content_revision <= revision:
            raise StateError("state_invalid")
        presentation = state.get("presentation")
        if not isinstance(presentation, dict):
            raise StateError("state_invalid")
        if (
            presentation.get("schema_version") != "1.1.0"
            or presentation.get("run_id") != state["run_id"]
            or presentation.get("source_content_revision") != content_revision
            or presentation.get("default_locale") not in ("ru", "en")
        ):
            raise StateError("state_invalid")
    intake = state.get("intake")
    if not isinstance(intake, dict) or intake.get("run_id") != state["run_id"]:
        raise StateError("state_invalid")
    if version == "1.1.0" and intake.get("schema_version") != "1.1.0":
        raise StateError("state_invalid")
    questions = intake.get("questions", [])
    answers = intake.get("answers")
    if not isinstance(questions, list) or not isinstance(answers, list) or len(questions) > 10 or len(answers) > 10:
        raise StateError("state_invalid")
    if intake.get("questions_asked") != len(questions):
        raise StateError("state_invalid")
    if [item.get("ordinal") for item in questions if isinstance(item, dict)] != list(range(1, len(questions) + 1)):
        raise StateError("state_invalid")
    ledger = {item.get("question_id"): item for item in questions if isinstance(item, dict)}
    if len(ledger) != len(questions):
        raise StateError("state_invalid")
    answer_questions: set[str] = set()
    answer_ids: set[str] = set()
    for answer in answers:
        if not isinstance(answer, dict) or answer.get("run_id") != state["run_id"]:
            raise StateError("state_invalid")
        answer_version = answer.get("schema_version")
        answer_base = {
            "schema_version", "run_id", "answer_id", "question_id", "ordinal",
            "answer_revision", "expected_state_revision", "status", "sanitized_value",
            "redaction_applied", "recorded_at",
        }
        expected_answer_keys = answer_base | ({"last_correction_id"} if answer_version == "1.1.0" else set())
        if answer_version not in ("1.0.0", "1.1.0") or set(answer) != expected_answer_keys:
            raise StateError("state_invalid")
        answer_revision = answer.get("answer_revision")
        expected_answer_revision = answer.get("expected_state_revision")
        if (
            not isinstance(answer_revision, int)
            or isinstance(answer_revision, bool)
            or not 1 <= answer_revision <= 10_000
            or not isinstance(expected_answer_revision, int)
            or isinstance(expected_answer_revision, bool)
            or not 0 <= expected_answer_revision < revision
            or not _valid_timestamp(answer.get("recorded_at"))
            or not isinstance(answer.get("redaction_applied"), bool)
        ):
            raise StateError("state_invalid")
        status_value = answer.get("status")
        sanitized_value = answer.get("sanitized_value")
        if status_value == "answered":
            if not isinstance(sanitized_value, str) or not 1 <= len(sanitized_value) <= 2_000:
                raise StateError("state_invalid")
        elif status_value == "skipped":
            if sanitized_value is not None:
                raise StateError("state_invalid")
        else:
            raise StateError("state_invalid")
        if answer_version == "1.1.0":
            marker = answer.get("last_correction_id")
            valid_marker = isinstance(marker, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", marker))
            if (answer_revision == 1 and marker is not None) or (answer_revision >= 2 and not valid_marker):
                raise StateError("state_invalid")
        question_id = answer.get("question_id")
        if question_id not in ledger or ledger[question_id].get("ordinal") != answer.get("ordinal"):
            raise StateError("state_invalid")
        if question_id in answer_questions or answer.get("answer_id") in answer_ids:
            raise StateError("state_invalid")
        answer_questions.add(question_id)
        answer_ids.add(answer.get("answer_id"))
    pending = intake.get("pending_question_id")
    if pending is not None and (pending not in ledger or pending in answer_questions):
        raise StateError("state_invalid")
    if set(ledger) != answer_questions | ({pending} if pending is not None else set()):
        raise StateError("state_invalid")
    intake_status = intake.get("status")
    expected_action = {
        "asking": "answer_question",
        "cancelled": "resume_or_finalize",
    }.get(intake_status)
    if expected_action and intake.get("next_action") != expected_action:
        raise StateError("state_invalid")
    if intake_status == "asking" and pending is None:
        raise StateError("state_invalid")
    if intake_status in ("ready", "cancelled") and pending is not None:
        raise StateError("state_invalid")
    if intake_status == "ready" and (
        not any(answer.get("status") == "answered" for answer in answers)
        or not intake.get("completion_reason")
    ):
        raise StateError("state_invalid")
    status, phase = state.get("status"), state.get("phase")
    if status not in ("active", "finalized", "finalized_incomplete") or phase not in (
        "intake", "scan", "context_review", "matching", "report"
    ):
        raise StateError("state_invalid")
    if status == "active":
        if phase != "intake" and intake_status != "ready":
            raise StateError("state_invalid")
    elif status == "finalized":
        if phase != "report" or intake_status != "ready" or state.get("memo") is None:
            raise StateError("state_invalid")
    elif phase == "intake" and intake_status not in ("ready", "cancelled"):
        raise StateError("state_invalid")
    if phase in ("context_review", "matching", "report") and state.get("brief") is None:
        raise StateError("state_invalid")
    if phase == "report" and state.get("memo") is None:
        raise StateError("state_invalid")
    html_revision = state.get("html_revision")
    if html_revision is not None and (
        not isinstance(html_revision, int)
        or html_revision < 1
        or (version == "1.1.0" and html_revision >= revision)
        or (version == "1.0.0" and html_revision > revision)
    ):
        raise StateError("state_invalid")
    history = state.get("history")
    if not isinstance(history, list) or len(history) > MAX_HISTORY:
        raise StateError("state_invalid")
    seen_runs: set[str] = set()
    for entry in history:
        if (
            not isinstance(entry, dict)
            or set(entry) != {"run_id", "final_revision", "status"}
            or not _valid_uuid(entry.get("run_id"))
            or entry.get("run_id") in seen_runs
            or entry.get("status") not in ("finalized", "finalized_incomplete")
            or not isinstance(entry.get("final_revision"), int)
        ):
            raise StateError("state_invalid")
        seen_runs.add(entry["run_id"])
    data = canonical_json_bytes(state)
    if len(data) > MAX_STATE_BYTES or _contains_canary(data):
        raise StateError("storage_limit" if len(data) > MAX_STATE_BYTES else "state_invalid")
    return state


class _FileLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle: Any = None

    def __enter__(self) -> "_FileLock":
        if self.path.exists():
            _validate_regular_file(self.path, max_bytes=64)
        try:
            self.handle = self.path.open("a+b")
            if self.handle.tell() == 0:
                self.handle.write(b"\0")
                self.handle.flush()
                os.fsync(self.handle.fileno())
            deadline = time.monotonic() + LOCK_WAIT_SECONDS
            while True:
                try:
                    self.handle.seek(0)
                    if os.name == "nt":
                        import msvcrt

                        msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return self
                except (OSError, BlockingIOError):
                    if time.monotonic() >= deadline:
                        raise StateError("state_busy")
                    time.sleep(0.05)
        except StateError:
            self.__exit__(None, None, None)
            raise
        except OSError as error:
            self.__exit__(None, None, None)
            raise StateError("state_write_failed") from error

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self.handle is None:
            return
        try:
            self.handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            self.handle.close()
            self.handle = None


def _inventory(root: Path) -> tuple[int, int]:
    count = 0
    total = 0
    stack = [root]
    while stack:
        directory = stack.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError as error:
            raise StateError("state_write_failed") from error
        for entry in entries:
            path = Path(entry.path)
            if entry.is_symlink() or _is_reparse(path):
                raise StateError("state_invalid")
            if entry.is_dir(follow_symlinks=False):
                stack.append(path)
            elif entry.is_file(follow_symlinks=False):
                count += 1
                if count > MAX_FILE_ENTRIES:
                    raise StateError("storage_limit")
                try:
                    total += entry.stat(follow_symlinks=False).st_size
                except OSError as error:
                    raise StateError("state_write_failed") from error
                if total > MAX_TOTAL_BYTES:
                    raise StateError("storage_limit")
            else:
                raise StateError("state_invalid")
    return count, total


def _prospective(root: Path, writes: list[tuple[Path, int]]) -> None:
    count, total = _inventory(root)
    new_count = count
    new_total = total
    for path, size in writes:
        if path.exists():
            try:
                old = path.stat().st_size
            except OSError as error:
                raise StateError("state_write_failed") from error
            new_total += max(0, size - old)
        else:
            new_count += 1
            new_total += size
    if new_count > MAX_FILE_ENTRIES or new_total > MAX_TOTAL_BYTES:
        raise StateError("storage_limit")


def _write_synced(path: Path, data: bytes) -> None:
    try:
        with path.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as error:
        raise StateError("state_write_failed") from error


class LockedStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    @property
    def state_path(self) -> Path:
        return self.root / STATE_NAME

    def load(self, *, required: bool = True, writable: bool = False) -> dict[str, Any] | None:
        if not self.state_path.exists():
            if required:
                raise StateError("state_invalid")
            return None
        data = _validate_regular_file(self.state_path, max_bytes=MAX_STATE_BYTES)
        state = strict_json_bytes(data)
        return validate_state(state, writable=writable)

    def commit(self, new_state: dict[str, Any], previous: dict[str, Any] | None) -> bytes:
        validate_state(new_state, writable=True)
        data = canonical_json_bytes(new_state)
        pending = self.root / STATE_PENDING
        writes = [(pending, len(data)), (self.state_path, len(data))]
        previous_data: bytes | None = None
        if previous is not None:
            previous_data = canonical_json_bytes(validate_state(previous))
            previous_path = self.root / PREVIOUS_NAME
            previous_pending = self.root / PREVIOUS_PENDING
            if previous_path.exists():
                validate_state(strict_json_bytes(_validate_regular_file(previous_path, max_bytes=MAX_STATE_BYTES)))
            if previous_pending.exists():
                validate_state(strict_json_bytes(_validate_regular_file(previous_pending, max_bytes=MAX_STATE_BYTES)))
            writes.extend(((previous_pending, len(previous_data)), (previous_path, len(previous_data))))
        if pending.exists():
            validate_state(strict_json_bytes(_validate_regular_file(pending, max_bytes=MAX_STATE_BYTES)))
        _prospective(self.root, writes)
        if previous_data is not None:
            previous_pending = self.root / PREVIOUS_PENDING
            _write_synced(previous_pending, previous_data)
            try:
                os.replace(previous_pending, self.root / PREVIOUS_NAME)
            except OSError as error:
                raise StateError("state_write_failed") from error
        _write_synced(pending, data)
        try:
            os.replace(pending, self.state_path)
        except OSError as error:
            raise StateError("state_write_failed") from error
        return data

    def ensure_history(self, state: dict[str, Any], data: bytes | None = None) -> None:
        if state.get("status") not in ("finalized", "finalized_incomplete"):
            raise StateError("history_integrity")
        validate_state(state)
        data = data if data is not None else canonical_json_bytes(state)
        runs = self.root / "runs"
        _ensure_plain_directory(runs, create=True)
        existing_runs = [path for path in runs.iterdir() if path.is_file() and path.suffix == ".json"]
        destination = runs / f"{state['run_id']}.json"
        if destination.exists():
            existing = _validate_regular_file(destination, max_bytes=MAX_STATE_BYTES)
            if existing != data:
                raise StateError("history_integrity")
            return
        if len(existing_runs) >= MAX_HISTORY:
            raise StateError("storage_limit")
        pending = self.root / RUN_PENDING
        if pending.exists():
            pending_state = strict_json_bytes(_validate_regular_file(pending, max_bytes=MAX_STATE_BYTES))
            validate_state(pending_state)
        _prospective(self.root, [(pending, len(data)), (destination, len(data))])
        _write_synced(pending, data)
        try:
            os.link(pending, destination)
            pending.unlink()
        except FileExistsError:
            if _validate_regular_file(destination, max_bytes=MAX_STATE_BYTES) != data:
                raise StateError("history_integrity")
        except OSError:
            try:
                with destination.open("xb") as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                pending.unlink(missing_ok=True)
            except FileExistsError:
                if _validate_regular_file(destination, max_bytes=MAX_STATE_BYTES) != data:
                    raise StateError("history_integrity")
            except OSError as error:
                raise StateError("state_write_failed") from error


@contextmanager
def locked_store(project_root: Path, *, create: bool) -> Iterator[LockedStore]:
    root = output_root(project_root, create=create)
    lock_path = root / LOCK_NAME
    with _FileLock(lock_path):
        yield LockedStore(root)


def published_receipt(root: Path) -> dict[str, Any] | None:
    path = root / HTML_NAME
    if not path.exists():
        return None
    data = _validate_regular_file(path, max_bytes=MAX_HTML_BYTES)
    if _contains_canary(data) or not data.startswith(_HTML_MARKER_PREFIX):
        return None
    end = data.find(_HTML_MARKER_SUFFIX, len(_HTML_MARKER_PREFIX))
    if end < 0:
        return None
    try:
        metadata = strict_json_bytes(data[len(_HTML_MARKER_PREFIX):end])
    except StateError:
        return None
    if not isinstance(metadata, dict) or metadata.get("owner") != HTML_OWNER:
        return None
    required = {"run_id", "revision", "content_revision", "presentation_revision", "generated_at"}
    if set(metadata) != required | {"owner"} or not _valid_uuid(metadata.get("run_id")):
        return None
    if not all(isinstance(metadata.get(key), int) and metadata[key] >= 1 for key in (
        "revision", "content_revision", "presentation_revision"
    )) or metadata["content_revision"] > metadata["revision"] or not _valid_timestamp(metadata.get("generated_at")):
        return None
    return {
        "run_id": metadata["run_id"],
        "revision": metadata["revision"],
        "content_revision": metadata["content_revision"],
        "presentation_revision": metadata["presentation_revision"],
        "generated_at": metadata["generated_at"],
        "html_sha256": hashlib.sha256(data).hexdigest(),
    }


def render_fixture(state: dict[str, Any]) -> bytes:
    """A deterministic CP-07 boundary fixture, intentionally not the CP-10 UI."""

    validate_state(state)
    presentation = state.get("presentation") or {}
    metadata = {
        "owner": HTML_OWNER,
        **state_stamp(state),
        "presentation_revision": presentation.get("presentation_revision", 1),
        "generated_at": state["updated_at"],
    }
    marker = _HTML_MARKER_PREFIX + canonical_json_bytes(metadata) + _HTML_MARKER_SUFFIX
    safe_status = html.escape(str(state["status"]), quote=True)
    safe_phase = html.escape(str(state["phase"]), quote=True)
    body = (
        "<!doctype html><html lang=\"ru\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>myAI-StackGuide</title></head><body>"
        "<main><h1>myAI-StackGuide</h1>"
        "<p>This is a saved local session snapshot. The full desktop renderer is supplied by CP-10.</p>"
        f"<p>State: {safe_status}; phase: {safe_phase}; revision: {state['revision']}.</p>"
        "<p>Answers and project files are managed through Codex, not this HTML.</p>"
        "</main></body></html>"
    ).encode("utf-8")
    data = marker + b"\n" + body
    if len(data) > MAX_HTML_BYTES or _contains_canary(data):
        raise StateError("render_failed")
    return data


def publish(project_root: Path, captured: dict[str, Any]) -> dict[str, Any]:
    """Render committed state, then lock/recheck and atomically publish it."""

    captured_stamp = state_stamp(captured)
    try:
        rendered = render_fixture(captured)
    except StateError:
        root = output_root(project_root, create=False)
        previous = published_receipt(root)
        return {
            "publication_status": "stale" if previous else "unavailable",
            "failure_reason": "render_failed",
            "published": previous,
            "current": captured_stamp,
            "render_attempts": 1,
            "retry": "render_only",
        }
    try:
        with locked_store(project_root, create=False) as store:
            current = store.load(required=True)
            assert current is not None
            current_stamp = state_stamp(current)
            previous = published_receipt(store.root)
            if current_stamp != captured_stamp:
                return {
                    "publication_status": "superseded",
                    "failure_reason": "render_superseded",
                    "published": previous,
                    "current": current_stamp,
                    "render_attempts": 1,
                    "retry": "stop",
                }
            html_path = store.root / HTML_NAME
            if html_path.exists() and previous is None:
                raise StateError("html_write_failed")
            pending = store.root / HTML_PENDING
            if pending.exists():
                pending_data = _validate_regular_file(pending, max_bytes=MAX_HTML_BYTES)
                if not pending_data.startswith(_HTML_MARKER_PREFIX):
                    raise StateError("html_write_failed")
            _prospective(store.root, [(pending, len(rendered)), (html_path, len(rendered))])
            try:
                with pending.open("wb") as handle:
                    handle.write(rendered)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(pending, html_path)
            except OSError as error:
                raise StateError("html_write_failed") from error
            published = published_receipt(store.root)
            if published is None or {key: published[key] for key in captured_stamp} != captured_stamp:
                raise StateError("html_write_failed")
            return {
                "publication_status": "current",
                "failure_reason": None,
                "published": published,
                "current": current_stamp,
                "render_attempts": 1,
                "retry": "none",
            }
    except StateError as error:
        try:
            root = output_root(project_root, create=False)
            previous = published_receipt(root)
        except StateError:
            previous = None
        return {
            "publication_status": "stale" if previous else "unavailable",
            "failure_reason": "html_write_failed" if error.reason != "render_superseded" else error.reason,
            "published": previous,
            "current": captured_stamp,
            "render_attempts": 1,
            "retry": "render_only",
        }
