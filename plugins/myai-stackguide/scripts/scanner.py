"""Bounded, read-only CP-08 project scanner.

The scanner never imports project modules, starts subprocesses, installs
dependencies, or opens network connections.  It returns a schema-shaped,
minimized report plus transient topology/path data for ``context.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
import copy
import ctypes
import fnmatch
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import time
import tomllib
from typing import Any, Callable, Iterable, Mapping
import uuid
import xml.etree.ElementTree as ET


SCRIPT_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = SCRIPT_ROOT.parents[2]
DEFAULT_POLICY_PATH = REPOSITORY_ROOT / "specs" / "scanner" / "scan-policy.yaml"
SCHEMA_VERSION = "1.1.0"
POLICY_VERSION = "1.3.0"
POLICY_ID = "local-scan-v1.3"
MODES = ("quick", "standard", "deep")
CHECKPOINT_SCHEMA_VERSION = "1.1.0"
CHECKPOINT_OWNER = "myai-stackguide.scan-checkpoint.v1"
CHECKPOINT_NAME = ".scan-checkpoint.json"
CHECKPOINT_PENDING_NAME = ".scan-checkpoint.pending.json"
MAX_CHECKPOINT_BYTES = 67_108_864
MAX_SUMMARY_BYTES = 4096


def _load_sibling(name: str, path: Path) -> Any:
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("trusted module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


context = _load_sibling("myai_stackguide_context", SCRIPT_ROOT / "context.py")
state_store = _load_sibling("myai_stackguide_state_store", SCRIPT_ROOT / "state_store.py")
TypedTopology = context.TypedTopology
ContextExcerpt = context.ContextExcerpt
TransientContext = context.TransientContext


class ScannerError(RuntimeError):
    """A scanner failure that exposes only a typed reason."""

    def __init__(self, reason: str) -> None:
        super().__init__("scan operation failed")
        self.reason = reason


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate key")
        value[key] = item
    return value


def _read_json(path: Path) -> Any:
    data = path.read_bytes()
    return json.loads(
        data.decode("utf-8", errors="strict"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
    )


def _validate_policy(policy: Any) -> dict[str, Any]:
    if not isinstance(policy, dict):
        raise ScannerError("policy_incompatible")
    required = {
        "schema_version", "policy_id", "platform", "source_access", "network",
        "execute_project", "install_dependencies", "modes", "topology",
        "max_file_bytes", "max_response_bytes", "targeted_context",
        "mode_budget_warning_fraction", "deep_checkpoint", "allowed_filenames",
        "allowed_extensions", "denied_segments", "denied_filename_globs",
        "excluded_output_root", "reject_links", "reject_hardlinks", "reject_ads",
        "classification", "counting", "deadline", "deny_precedes_allow",
        "precedence", "policy_limits_calibrated",
    }
    if set(policy) != required:
        raise ScannerError("policy_incompatible")
    if (
        policy.get("schema_version") != POLICY_VERSION
        or policy.get("policy_id") != POLICY_ID
        or policy.get("platform") != "windows_local_disk"
        or policy.get("source_access") != "bounded_relevant_context"
        or policy.get("network") is not False
        or policy.get("execute_project") is not False
        or policy.get("install_dependencies") is not False
        or policy.get("reject_links") is not True
        or policy.get("reject_hardlinks") is not True
        or policy.get("reject_ads") is not True
        or policy.get("deny_precedes_allow") is not True
        or policy.get("counting") != "attempts_and_consumed_bytes_including_failed_reads"
        or policy.get("deadline") != "monotonic_cooperative"
        or policy.get("max_response_bytes") != 262144
    ):
        raise ScannerError("policy_incompatible")
    for group, keys in (
        ("modes", ("max_files", "max_bytes", "max_seconds")),
        ("topology", ("max_entries", "max_depth", "max_seconds")),
        ("targeted_context", ("max_files", "max_read_bytes", "max_model_context_bytes")),
    ):
        value = policy.get(group)
        if not isinstance(value, dict):
            raise ScannerError("policy_incompatible")
        for mode in MODES:
            row = value.get(mode)
            if not isinstance(row, dict) or any(
                not isinstance(row.get(key), int) or isinstance(row.get(key), bool) or row[key] < 1
                for key in keys
            ):
                raise ScannerError("policy_incompatible")
    if (
        policy["targeted_context"].get("charge_to_scan_budget") is not True
        or policy["targeted_context"].get("persist_excerpts") is not False
        or not isinstance(policy.get("max_file_bytes"), dict)
        or any(not isinstance(policy["max_file_bytes"].get(mode), int) for mode in MODES)
        or not isinstance(policy.get("allowed_filenames"), list)
        or not isinstance(policy.get("allowed_extensions"), list)
        or not isinstance(policy.get("denied_segments"), list)
        or not isinstance(policy.get("denied_filename_globs"), list)
    ):
        raise ScannerError("policy_incompatible")
    return policy


def load_policy(path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Load the accepted JSON-compatible YAML policy with strict identity checks."""

    selected = DEFAULT_POLICY_PATH if path is None else Path(path)
    try:
        policy = _validate_policy(_read_json(selected))
        if selected.resolve(strict=True) != DEFAULT_POLICY_PATH.resolve(strict=True):
            canonical = _validate_policy(_read_json(DEFAULT_POLICY_PATH))
            if policy != canonical:
                raise ScannerError("policy_incompatible")
        return copy.deepcopy(policy)
    except ScannerError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError) as error:
        raise ScannerError("policy_incompatible") from error


_OVERRIDE_FIELDS = {
    "max_files", "max_bytes", "max_seconds", "topology_max_entries",
    "topology_max_depth", "topology_max_seconds", "max_file_bytes",
    "context_max_files", "context_max_read_bytes", "context_max_model_context_bytes",
}


def _effective_policy(policy: dict[str, Any], overrides: Mapping[str, Mapping[str, int]] | None) -> dict[str, Any]:
    result = copy.deepcopy(policy)
    if overrides is None:
        return result
    if not isinstance(overrides, Mapping) or any(mode not in MODES for mode in overrides):
        raise ScannerError("invalid_limit_override")
    locations = {
        "max_files": ("modes", "max_files"),
        "max_bytes": ("modes", "max_bytes"),
        "max_seconds": ("modes", "max_seconds"),
        "topology_max_entries": ("topology", "max_entries"),
        "topology_max_depth": ("topology", "max_depth"),
        "topology_max_seconds": ("topology", "max_seconds"),
        "max_file_bytes": ("max_file_bytes", None),
        "context_max_files": ("targeted_context", "max_files"),
        "context_max_read_bytes": ("targeted_context", "max_read_bytes"),
        "context_max_model_context_bytes": ("targeted_context", "max_model_context_bytes"),
    }
    for mode, values in overrides.items():
        if not isinstance(values, Mapping) or any(key not in _OVERRIDE_FIELDS for key in values):
            raise ScannerError("invalid_limit_override")
        for key, value in values.items():
            group, field = locations[key]
            original = result[group][mode] if field is None else result[group][mode][field]
            if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= original:
                raise ScannerError("invalid_limit_override")
            if field is None:
                result[group][mode] = value
            else:
                result[group][mode][field] = value
    return result


@dataclass(frozen=True, slots=True)
class ScanResult:
    report: dict[str, Any]
    topology: TypedTopology
    eligible_paths: tuple[str, ...]
    observed_paths: tuple[str, ...]
    warnings: tuple[str, ...]
    checkpoints: tuple[dict[str, int], ...]
    policy: dict[str, Any]


@dataclass(slots=True)
class _FileRecord:
    relative_path: str
    size_bytes: int
    kind: str
    disposition: str = "eligible"
    evidence_ref: str | None = None


@dataclass(slots=True)
class _Parsed:
    facts: list[tuple[str, str, int | None, int | None]]
    package_name: str | None = None
    dependencies: tuple[str, ...] = ()
    workspace_declared: bool = False
    api_lines: tuple[int, ...] = ()
    storage_lines: tuple[int, ...] = ()
    deployment: bool = False
    tests: bool = False


_WINDOWS_RESERVED = {
    "con", "prn", "aux", "nul", "clock$",
    *(f"com{value}" for value in range(1, 10)),
    *(f"lpt{value}" for value in range(1, 10)),
}
_GENERATED_SEGMENTS = {
    ".codex-tmp", ".next", ".pytest_cache", ".ruff_cache", ".runtime", ".tmp", ".worktrees",
    ".wrangler", "node_modules", "vendor", "site-packages", "dist", "build", "target", "outputs",
    "coverage", "__pycache__", "logs", "dumps", "exports",
}
_MANIFEST_NAMES = {
    "package.json", "pyproject.toml", "requirements.txt", "cargo.toml", "go.mod",
    "pom.xml", "build.gradle", "pnpm-workspace.yaml",
}
_DOCUMENT_NAMES = {"readme", "readme.md", "readme.rst"}
_SECRET_CONTENT = re.compile(
    rb"(?im)(?:-----BEGIN [A-Z0-9 ]*(?:PRIVATE KEY|SECRET)[A-Z0-9 ]*-----|"
    rb"^[ \t]*(?:api[_-]?key|access[_-]?token|secret|password|credential)[ \t]*[:=][ \t]*[\"']?[^\s\"']{8,})"
)
_SAFE_SYMBOL = re.compile(r"^[A-Za-z0-9@._/+:#-]{1,120}$")
_SENSITIVE_SYMBOL = re.compile(
    r"(?:^(?:ghp_|github_pat_|gh[ousr]_)[A-Za-z0-9_]+|"
    r"(?:^|[._/@:+-])(?:api[_-]?key|access[_-]?key|private[_-]?key|key|secret|token|password|passwd|credential)"
    r"(?:$|[._/@:+-]))",
    re.IGNORECASE,
)
_TOKEN_STYLE_PREFIX = re.compile(r"^(?:sk-(?:proj|live|test)-|pk_(?:live|test)_)", re.IGNORECASE)


def _node_id(kind: str, value: str) -> str:
    digest = hashlib.sha256((kind + "\0" + value).encode("utf-8")).hexdigest()[:20]
    return f"{kind}-{digest}"


def _evidence_id(relative_path: str) -> str:
    return "ev-file-" + hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:20]


def _looks_credential_shaped(value: str) -> bool:
    """Conservatively reject bounded high-entropy token-like identifiers."""

    if len(value) >= 24 and _TOKEN_STYLE_PREFIX.match(value):
        return True
    for segment in re.findall(r"[A-Za-z0-9]+", value):
        if len(segment) >= 32 and re.fullmatch(r"[A-Fa-f0-9]+", segment):
            return True
        if len(segment) < 28:
            continue
        classes = sum((
            any(char.islower() for char in segment),
            any(char.isupper() for char in segment),
            any(char.isdigit() for char in segment),
        ))
        if classes < 2:
            continue
        counts: dict[str, int] = {}
        for char in segment:
            counts[char] = counts.get(char, 0) + 1
        entropy = -sum(
            (count / len(segment)) * math.log2(count / len(segment))
            for count in counts.values()
        )
        if entropy >= 3.7 and len(counts) / len(segment) >= 0.45:
            return True
    return False


def _safe_symbol(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value if (
        _SAFE_SYMBOL.fullmatch(value)
        and not _SENSITIVE_SYMBOL.search(value)
        and not _looks_credential_shaped(value)
    ) else None


def _is_reparse(path: Path, info: os.stat_result | None = None) -> bool:
    try:
        info = path.lstat() if info is None else info
    except OSError as error:
        raise ScannerError("containment_unsupported") from error
    attributes = getattr(info, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _contained(root: Path, candidate: Path) -> bool:
    try:
        root_value = os.path.normcase(str(root.resolve(strict=True)))
        candidate_value = os.path.normcase(str(candidate.resolve(strict=True)))
        return os.path.commonpath((root_value, candidate_value)) == root_value
    except (OSError, RuntimeError, ValueError):
        return False


def _validate_relative(value: str) -> bool:
    if (
        not isinstance(value, str) or not value or len(value) > 240 or "\\" in value
        or ":" in value or "//" in value or value.startswith("/")
        or any(ord(char) < 32 or ord(char) == 127 or char in '<>|?*' for char in value)
    ):
        return False
    parts = PurePosixPath(value).parts
    if not parts or any(part in ("", ".", "..") or part.endswith((".", " ")) for part in parts):
        return False
    return not any(part.split(".", 1)[0].casefold() in _WINDOWS_RESERVED for part in parts)


def _path_disposition(relative_path: str, policy: dict[str, Any]) -> tuple[bool, str]:
    if not _validate_relative(relative_path):
        return False, "unsafe_path"
    folded_parts = tuple(part.casefold() for part in PurePosixPath(relative_path).parts)
    output_parts = tuple(part.casefold() for part in PurePosixPath(policy["excluded_output_root"]).parts)
    if folded_parts[: len(output_parts)] == output_parts:
        return False, "generated"
    denied = {value.casefold() for value in policy["denied_segments"]}
    if any(part in denied for part in folded_parts):
        return False, "generated" if any(part in _GENERATED_SEGMENTS for part in folded_parts) else "sensitive"
    name = folded_parts[-1]
    if any(fnmatch.fnmatchcase(name, pattern.casefold()) for pattern in policy["denied_filename_globs"]):
        return False, "sensitive"
    allowed_names = {value.casefold() for value in policy["allowed_filenames"]}
    suffix = PurePosixPath(name).suffix.casefold()
    if name not in allowed_names and suffix not in {value.casefold() for value in policy["allowed_extensions"]}:
        return False, "unsupported"
    return True, "eligible"


def _windows_final_path(file_descriptor: int) -> str | None:
    if os.name != "nt":
        return None
    try:
        import msvcrt
        from ctypes import wintypes

        handle = msvcrt.get_osfhandle(file_descriptor)
        buffer = ctypes.create_unicode_buffer(32768)
        function = ctypes.windll.kernel32.GetFinalPathNameByHandleW
        function.argtypes = (wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD)
        function.restype = wintypes.DWORD
        length = function(wintypes.HANDLE(handle), buffer, len(buffer), 0)
        if length <= 0 or length >= len(buffer):
            raise OSError("final path unavailable")
        value = buffer.value
        if value.startswith("\\\\?\\UNC\\"):
            value = "\\\\" + value[8:]
        elif value.startswith("\\\\?\\"):
            value = value[4:]
        return value
    except (AttributeError, ImportError, OSError, ValueError) as error:
        raise ScannerError("containment_unsupported") from error


def _same_identity(left: os.stat_result, right: os.stat_result) -> bool:
    return (
        left.st_dev,
        left.st_ino,
        left.st_size,
        getattr(left, "st_mtime_ns", int(left.st_mtime * 1_000_000_000)),
    ) == (
        right.st_dev,
        right.st_ino,
        right.st_size,
        getattr(right, "st_mtime_ns", int(right.st_mtime * 1_000_000_000)),
    )


def _guarded_read(root: Path, path: Path, max_bytes: int) -> tuple[str, str | None, int]:
    """Return (status, decoded text, consumed bytes) without leaking content."""

    descriptor: int | None = None
    try:
        before = path.lstat()
        if _is_reparse(path, before) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            return "excluded_sources", None, 0
        if not _contained(root, path):
            return "containment_unsupported", None, 0
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        opened = os.fstat(descriptor)
        if not _same_identity(before, opened) or opened.st_nlink != 1:
            return "changed_file", None, 0
        final_path = _windows_final_path(descriptor)
        if final_path is not None:
            root_value = os.path.normcase(str(root))
            final_value = os.path.normcase(str(Path(final_path)))
            if os.path.commonpath((root_value, final_value)) != root_value:
                return "containment_unsupported", None, 0
        chunks: list[bytes] = []
        consumed = 0
        while consumed < max_bytes:
            chunk = os.read(descriptor, min(65536, max_bytes - consumed))
            if not chunk:
                break
            chunks.append(chunk)
            consumed += len(chunk)
        data = b"".join(chunks)
        after_handle = os.fstat(descriptor)
        after_path = path.lstat()
        if not _same_identity(opened, after_handle) or not _same_identity(opened, after_path):
            return "changed_file", None, consumed
        if opened.st_size > max_bytes:
            return "budget_reached", None, consumed
        if b"\x00" in data[:8192]:
            return "encoding_error", None, consumed
        if _SECRET_CONTENT.search(data):
            return "excluded_sources", None, consumed
        try:
            return "read", data.decode("utf-8-sig", errors="strict"), consumed
        except UnicodeDecodeError:
            return "encoding_error", None, consumed
    except FileNotFoundError:
        return "changed_file", None, 0
    except ScannerError as error:
        return error.reason, None, 0
    except (OSError, ValueError):
        return "containment_unsupported", None, 0
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def _dependency_names(value: Any) -> tuple[str, ...]:
    if isinstance(value, dict):
        values = value.keys()
    elif isinstance(value, list):
        values = value
    else:
        return ()
    return tuple(sorted({symbol for item in values if (symbol := _safe_symbol(item)) is not None}))[:64]


def _parse_json(text: str) -> dict[str, Any]:
    value = json.loads(text, object_pairs_hook=_strict_object, parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
    if not isinstance(value, dict):
        raise ValueError("manifest object required")
    return value


def _parse_manifest(relative_path: str, text: str) -> _Parsed:
    name = PurePosixPath(relative_path).name.casefold()
    facts: list[tuple[str, str, int | None, int | None]] = []
    package_name: str | None = None
    dependencies: tuple[str, ...] = ()
    workspace = False
    if name == "package.json":
        value = _parse_json(text)
        package_name = _safe_symbol(value.get("name"))
        dependency_values: set[str] = set()
        for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            dependency_values.update(_dependency_names(value.get(key)))
        dependencies = tuple(sorted(dependency_values))[:64]
        workspace = isinstance(value.get("workspaces"), (list, dict))
    elif name in ("pyproject.toml", "cargo.toml"):
        value = tomllib.loads(text)
        if name == "pyproject.toml":
            project = value.get("project") if isinstance(value.get("project"), dict) else {}
            poetry = value.get("tool", {}).get("poetry", {}) if isinstance(value.get("tool"), dict) else {}
            package_name = _safe_symbol(project.get("name")) or _safe_symbol(poetry.get("name"))
            dependencies = _dependency_names(project.get("dependencies"))
        else:
            package = value.get("package") if isinstance(value.get("package"), dict) else {}
            package_name = _safe_symbol(package.get("name"))
            dependencies = _dependency_names(value.get("dependencies"))
            workspace = isinstance(value.get("workspace"), dict)
    elif name == "requirements.txt":
        names: set[str] = set()
        for line in text.splitlines()[:4096]:
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "-")):
                continue
            match = re.match(r"([A-Za-z0-9_.-]+)", stripped)
            if match and (symbol := _safe_symbol(match.group(1))) is not None:
                names.add(symbol)
        dependencies = tuple(sorted(names))[:64]
    elif name == "go.mod":
        module_match = re.search(r"(?m)^\s*module\s+([^\s]+)", text)
        package_name = _safe_symbol(module_match.group(1)) if module_match else None
        dependencies = tuple(sorted({
            symbol for match in re.finditer(r"(?m)^\s*([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)\s+v", text)
            if (symbol := _safe_symbol(match.group(1))) is not None
        }))[:64]
    elif name == "pom.xml":
        if re.search(r"<!\s*(?:DOCTYPE|ENTITY)", text, re.IGNORECASE):
            raise ValueError("unsafe xml")
        root = ET.fromstring(text)
        artifact = next((element.text for element in root.iter() if element.tag.rsplit("}", 1)[-1] == "artifactId" and element.text), None)
        package_name = _safe_symbol(artifact)
        dependencies = tuple(sorted({
            symbol for element in root.iter()
            if element.tag.rsplit("}", 1)[-1] == "artifactId" and (symbol := _safe_symbol(element.text)) is not None
        }))[:64]
    elif name == "build.gradle":
        dependencies = tuple(sorted({
            symbol for match in re.finditer(r"['\"]([A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+):", text)
            if (symbol := _safe_symbol(match.group(1))) is not None
        }))[:64]
    elif name == "pnpm-workspace.yaml":
        workspace = bool(re.search(r"(?m)^\s*packages\s*:", text))
    for dependency in dependencies[:24]:
        facts.append(("dependency", dependency, None, None))
    return _Parsed(
        facts=facts,
        package_name=package_name,
        dependencies=dependencies,
        workspace_declared=workspace,
    )


_API_SIGNATURE = re.compile(
    r"(?:@(?:app|router)\.(?:get|post|put|patch|delete)|\b(?:app|router)\.(?:get|post|put|patch|delete)\s*\(|"
    r"\bMap(?:Get|Post|Put|Patch|Delete)\s*\(|@(?:Get|Post|Put|Patch|Delete)Mapping\b|http\.HandleFunc\s*\()"
)
_STORAGE_SIGNATURE = re.compile(
    r"\b(?:sqlite3?|postgres(?:ql)?|redis|mongodb?|sqlalchemy|prisma|typeorm|entityframework)\b",
    re.IGNORECASE,
)


def _parse_source(relative_path: str, text: str) -> _Parsed:
    api_lines: list[int] = []
    storage_lines: list[int] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if len(api_lines) < 8 and _API_SIGNATURE.search(line):
            api_lines.append(line_number)
        if len(storage_lines) < 8 and _STORAGE_SIGNATURE.search(line):
            storage_lines.append(line_number)
        if len(api_lines) >= 8 and len(storage_lines) >= 8:
            break
    folded = relative_path.casefold()
    return _Parsed(
        facts=[],
        api_lines=tuple(api_lines),
        storage_lines=tuple(storage_lines),
        deployment=PurePosixPath(folded).name in ("dockerfile", "compose.yaml", "docker-compose.yml"),
        tests=bool(re.search(r"(?:^|/)(?:tests?|spec)(?:/|$)|(?:^|/)(?:test_|.*[._-](?:test|spec)\.)", folded)),
    )


def _parse_file(relative_path: str, kind: str, text: str) -> _Parsed:
    if kind == "manifest":
        return _parse_manifest(relative_path, text)
    return _parse_source(relative_path, text)


def _directory_disposition(relative_path: str, policy: dict[str, Any]) -> tuple[bool, str]:
    if not _validate_relative(relative_path):
        return False, "unsafe_path"
    parts = tuple(part.casefold() for part in PurePosixPath(relative_path).parts)
    output = tuple(part.casefold() for part in PurePosixPath(policy["excluded_output_root"]).parts)
    if parts[: len(output)] == output:
        return False, "generated"
    denied = {value.casefold() for value in policy["denied_segments"]}
    if any(part in denied for part in parts):
        return False, "generated" if any(part in _GENERATED_SEGMENTS for part in parts) else "sensitive"
    return True, "eligible"


_LANGUAGE_BY_SUFFIX = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".go": "Go", ".rs": "Rust", ".java": "Java", ".cs": "C#",
    ".cpp": "C++", ".c": "C", ".h": "C/C++", ".sql": "SQL",
}
_REASON_ORDER = (
    "no_eligible_files", "budget_reached", "topology_incomplete", "monorepo_detected",
    "oversized_project", "excluded_sources", "encoding_error", "changed_file", "cancelled",
    "containment_unsupported",
)

_CHECKPOINT_KEYS = {
    "schema_version", "owner_marker", "checkpoint_id", "run_id", "root_ref",
    "root_fingerprint", "policy_id", "policy_version", "policy_sha256",
    "expected_state_revision", "committed_state_revision", "mode", "last_report", "session",
}
_CHECKPOINT_SESSION_KEYS = {
    "pending_dirs", "depth_deferred", "candidate_files", "records",
    "read_paths", "excluded_counts", "oversized", "service_root_count", "workspace_declared", "reasons", "warnings",
    "checkpoints", "last_checkpoint_files", "last_checkpoint_bytes", "visited_entries",
    "file_attempts", "bytes_consumed", "active_seconds", "topology_seconds",
    "topology_complete", "limit_overrides",
}


def validate_scan_report(report: Any, policy: Mapping[str, Any]) -> dict[str, Any]:
    """Validate that a report is the minimized shape produced by this scanner."""

    report_keys = {
        "schema_version", "run_id", "policy_version", "mode", "status", "classification",
        "manifest", "summary", "reason_codes",
    }
    if not isinstance(report, dict) or set(report) != report_keys:
        raise ScannerError("invalid_report")
    manifest = report.get("manifest")
    summary = report.get("summary")
    if (
        report.get("schema_version") != SCHEMA_VERSION
        or report.get("policy_version") != POLICY_VERSION
        or report.get("mode") not in MODES
        or report.get("status") not in ("complete", "partial", "cancelled", "unavailable")
        or report.get("classification") not in ("idea_or_empty", "compact", "standard", "large_or_monorepo")
        or not isinstance(manifest, dict)
        or not isinstance(summary, dict)
        or set(manifest) != {"schema_version", "run_id", "policy_version", "mode", "root_ref", "files", "counters", "excluded_counts"}
        or set(summary) != {"schema_version", "run_id", "summary_id", "content_class", "coverage", "facts", "inferences", "gaps", "evidence"}
        or manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("root_ref") != "selected-project"
        or summary.get("schema_version") != "1.0.0"
        or summary.get("coverage") not in ("complete", "partial")
        or manifest.get("run_id") != report.get("run_id")
        or summary.get("run_id") != report.get("run_id")
        or manifest.get("mode") != report.get("mode")
        or manifest.get("policy_version") != report.get("policy_version")
        or summary.get("content_class") != "minimized_project_context"
        or not isinstance(report.get("reason_codes"), list)
        or any(reason not in _REASON_ORDER for reason in report["reason_codes"])
        or len(report["reason_codes"]) != len(set(report["reason_codes"]))
    ):
        raise ScannerError("invalid_report")
    counters = manifest.get("counters")
    excluded_counts = manifest.get("excluded_counts")
    if (
        not isinstance(counters, dict)
        or set(counters) != {"visited_entries", "file_attempts", "bytes_consumed", "elapsed_ms", "eligible_files", "manifest_count", "service_roots", "workspace_declared", "topology_complete", "budget_reached"}
        or any(
            not isinstance(counters[key], int) or isinstance(counters[key], bool) or counters[key] < 0
            for key in ("visited_entries", "file_attempts", "bytes_consumed", "elapsed_ms", "eligible_files", "manifest_count", "service_roots")
        )
        or not isinstance(counters.get("workspace_declared"), bool)
        or not isinstance(counters.get("topology_complete"), bool)
        or not isinstance(counters.get("budget_reached"), bool)
        or not isinstance(excluded_counts, dict)
        or set(excluded_counts) != {"sensitive", "generated", "unsupported", "unsafe_path"}
        or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in excluded_counts.values())
    ):
        raise ScannerError("invalid_report")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) > 500:
        raise ScannerError("invalid_report")
    seen_paths: set[str] = set()
    manifest_by_path: dict[str, dict[str, Any]] = {}
    for item in files:
        path = item.get("relative_path") if isinstance(item, dict) else None
        allowed, _ = _path_disposition(path, dict(policy)) if isinstance(path, str) else (False, "unsafe_path")
        if (
            not allowed or path in seen_paths
            or set(item) != {"relative_path", "size_bytes", "kind", "disposition", "evidence_ref"}
            or not isinstance(item.get("size_bytes"), int) or isinstance(item.get("size_bytes"), bool)
            or not 0 <= item["size_bytes"] <= 4_194_304
            or item.get("kind") not in ("manifest", "document", "source")
            or item.get("disposition") not in ("eligible", "read", "unparseable", "changed", "unread")
        ):
            raise ScannerError("invalid_report")
        seen_paths.add(path)
        manifest_by_path[path] = item
    evidence = summary.get("evidence")
    facts = summary.get("facts")
    inferences = summary.get("inferences")
    gaps = summary.get("gaps")
    if not all(isinstance(value, list) for value in (evidence, facts, inferences, gaps)):
        raise ScannerError("invalid_report")
    evidence_ids: set[str] = set()
    for item in evidence:
        path = item.get("relative_path") if isinstance(item, dict) else None
        evidence_id = item.get("evidence_id") if isinstance(item, dict) else None
        if (
            not isinstance(item, dict)
            or set(item) != {"evidence_id", "kind", "relative_path", "line_start", "line_end", "answer_id", "content_persisted"}
            or path is None
            or not _path_disposition(path, dict(policy))[0]
            or item.get("kind") not in ("project_manifest", "project_source", "project_document")
            or item.get("line_start") is not None
            or item.get("line_end") is not None
            or item.get("answer_id") is not None
            or item.get("content_persisted") is not False
            or path not in manifest_by_path
            or manifest_by_path[path].get("disposition") != "read"
            or manifest_by_path[path].get("evidence_ref") != evidence_id
            or not isinstance(evidence_id, str)
            or re.fullmatch(r"ev-[a-z0-9][a-z0-9_-]{0,76}", evidence_id) is None
            or evidence_id in evidence_ids
        ):
            raise ScannerError("invalid_report")
        evidence_ids.add(evidence_id)
    fixed_facts = {
        "API surface signature observed", "Storage integration signature observed",
        "Deployment configuration observed", "Test surface observed",
    }
    fact_ids: set[str] = set()
    for item in facts:
        if not isinstance(item, dict) or set(item) != {"fact_id", "kind", "value", "evidence_refs"}:
            raise ScannerError("invalid_report")
        kind, value = item.get("kind"), item.get("value")
        if (
            kind not in ("language", "framework", "storage", "dependency", "capability", "integration", "topology")
            or not isinstance(value, str)
            or not value
            or (kind in ("dependency", "framework", "language") and _safe_symbol(value) is None)
            or (kind in ("storage", "capability", "integration", "topology") and value not in fixed_facts)
            or not set(item.get("evidence_refs", ())).issubset(evidence_ids)
            or not item.get("evidence_refs")
            or item.get("fact_id") in fact_ids
        ):
            raise ScannerError("invalid_report")
        fact_ids.add(item["fact_id"])
    for item in inferences:
        if (
            not isinstance(item, dict)
            or set(item) != {"inference_id", "statement", "confidence", "basis_fact_ids"}
            or not isinstance(item.get("statement"), str)
            or re.fullmatch(r"Observed topology contains \d+ weak component\(s\); missing edges remain unknown\.", item["statement"]) is None
            or not set(item.get("basis_fact_ids", ())).issubset(fact_ids)
        ):
            raise ScannerError("invalid_report")
    allowed_gaps = {
        "coverage_partial": (
            "The bounded scan did not observe every policy-relevant source.",
            "Review reason codes and explicitly continue with a permitted higher mode only if useful.",
        ),
        "topology_partial": (
            "Unvisited areas and absent edges remain unknown.",
            "Continue the same run within the next explicit cumulative mode budget.",
        ),
    }
    if any(
        not isinstance(item, dict)
        or set(item) != {"code", "detail", "next_check"}
        or item.get("code") not in allowed_gaps
        or (item.get("detail"), item.get("next_check")) != allowed_gaps[item["code"]]
        for item in gaps
    ):
        raise ScannerError("invalid_report")
    data = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(data) > policy["max_response_bytes"] or state_store._contains_canary(data):
        raise ScannerError("invalid_report")
    return report


def _validate_checkpoint_envelope(checkpoint: Any) -> dict[str, Any]:
    if not isinstance(checkpoint, dict) or set(checkpoint) != _CHECKPOINT_KEYS:
        raise ScannerError("checkpoint_invalid")
    session = checkpoint.get("session")
    report = checkpoint.get("last_report")
    if (
        checkpoint.get("schema_version") != CHECKPOINT_SCHEMA_VERSION
        or checkpoint.get("owner_marker") != CHECKPOINT_OWNER
        or checkpoint.get("root_ref") != "selected-project"
        or checkpoint.get("mode") not in MODES
        or not isinstance(session, dict)
        or set(session) != _CHECKPOINT_SESSION_KEYS
        or not isinstance(report, dict)
        or not isinstance(checkpoint.get("policy_id"), str)
        or not 1 <= len(checkpoint["policy_id"]) <= 128
        or not isinstance(checkpoint.get("policy_version"), str)
        or not 1 <= len(checkpoint["policy_version"]) <= 32
        or not isinstance(checkpoint.get("expected_state_revision"), int)
        or isinstance(checkpoint.get("expected_state_revision"), bool)
        or not 1 <= checkpoint["expected_state_revision"] < 1_000_000
        or checkpoint.get("committed_state_revision") != checkpoint["expected_state_revision"] + 1
        or not isinstance(checkpoint.get("root_fingerprint"), str)
        or re.fullmatch(r"[0-9a-f]{64}", checkpoint["root_fingerprint"]) is None
        or not isinstance(checkpoint.get("policy_sha256"), str)
        or re.fullmatch(r"[0-9a-f]{64}", checkpoint["policy_sha256"]) is None
    ):
        raise ScannerError("checkpoint_invalid")
    try:
        if str(uuid.UUID(checkpoint.get("run_id"))) != checkpoint["run_id"].casefold():
            raise ValueError
        data = json.dumps(
            checkpoint, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (ValueError, TypeError, AttributeError) as error:
        raise ScannerError("checkpoint_invalid") from error
    if len(data) > MAX_CHECKPOINT_BYTES or state_store._contains_canary(data):
        raise ScannerError("checkpoint_invalid")
    try:
        validate_scan_report(report, load_policy())
    except ScannerError as error:
        raise ScannerError("checkpoint_invalid") from error
    expected_id = "checkpoint-" + ScannerSession._checkpoint_digest(checkpoint)[:32]
    if checkpoint.get("checkpoint_id") != expected_id:
        raise ScannerError("checkpoint_invalid")
    return checkpoint


class ScannerSession:
    """One transient run/root scanner with cumulative mode counters."""

    def __init__(
        self,
        project_root: str | os.PathLike[str],
        run_id: str,
        *,
        policy_path: str | os.PathLike[str] | None = None,
        clock: Callable[[], float] = time.monotonic,
        limit_overrides: Mapping[str, Mapping[str, int]] | None = None,
    ) -> None:
        try:
            normalized_run_id = str(uuid.UUID(run_id))
            if normalized_run_id != run_id.casefold():
                raise ValueError("non-canonical UUID")
        except (ValueError, AttributeError, TypeError) as error:
            raise ScannerError("invalid_run_id") from error
        try:
            root = state_store.validate_project_root(project_root)
        except Exception as error:
            raise ScannerError("containment_unsupported") from error
        self.root = root
        self.run_id = normalized_run_id
        self.policy = _effective_policy(load_policy(policy_path), limit_overrides)
        self._limit_overrides = (
            {mode: dict(values) for mode, values in limit_overrides.items()}
            if limit_overrides is not None else {}
        )
        self.clock = clock
        self.topology = TypedTopology()
        self.topology.add_node("project", kind="project", label="selected-project")
        self._pending_dirs: list[tuple[Path, str, int]] = [(root, "", 0)]
        self._depth_deferred: dict[str, tuple[Path, int]] = {}
        self._visited_paths: set[str] = set()
        self._candidate_files: dict[str, tuple[Path, int, str]] = {}
        self._records: dict[str, _FileRecord] = {}
        self._read_paths: set[str] = set()
        self._excluded: dict[str, set[str]] = {
            "sensitive": set(), "generated": set(), "unsupported": set(), "unsafe_path": set(),
        }
        self._excluded_count_offsets = {
            "sensitive": 0, "generated": 0, "unsupported": 0, "unsafe_path": 0,
        }
        self._oversized: set[str] = set()
        self._facts: dict[tuple[str, str], set[str]] = {}
        self._evidence: dict[str, dict[str, Any]] = {}
        self._package_nodes: dict[str, set[str]] = {}
        self._pending_dependencies: list[tuple[str, str, tuple[str, ...]]] = []
        self._service_roots: set[str] = set()
        self._service_root_count_offset = 0
        self._workspace_declared = False
        self._reasons: set[str] = set()
        self._warnings: set[str] = set()
        self._checkpoints: list[dict[str, int]] = []
        self._last_checkpoint_files = 0
        self._last_checkpoint_bytes = 0
        self._visited_entries = 0
        self._file_attempts = 0
        self._bytes_consumed = 0
        self._active_seconds = 0.0
        self._topology_seconds = 0.0
        self._topology_complete = False
        self._mode: str | None = None
        self._last_report: dict[str, Any] | None = None

    def _root_fingerprint(self) -> str:
        return hashlib.sha256(
            (self.run_id + "\0" + str(self.root).casefold()).encode("utf-8")
        ).hexdigest()

    def _policy_fingerprint(self) -> str:
        data = json.dumps(
            self.policy, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _checkpoint_digest(checkpoint: Mapping[str, Any]) -> str:
        unsigned = {key: value for key, value in checkpoint.items() if key != "checkpoint_id"}
        data = json.dumps(
            unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def export_checkpoint(self, expected_state_revision: int) -> dict[str, Any]:
        """Return a minimized restart checkpoint; persistence belongs to CP-07."""

        if (
            not isinstance(expected_state_revision, int)
            or isinstance(expected_state_revision, bool)
            or not 1 <= expected_state_revision < 1_000_000
            or self._mode is None
            or self._last_report is None
        ):
            raise ScannerError("checkpoint_invalid")

        def relative_path(path: Path) -> str:
            try:
                value = path.relative_to(self.root).as_posix()
            except ValueError as error:
                raise ScannerError("checkpoint_invalid") from error
            if value == ".":
                return ""
            if not _validate_relative(value):
                raise ScannerError("checkpoint_invalid")
            return value

        retained_records = tuple(
            sorted(
                (
                    record for record in self._records.values()
                    if record.disposition != "eligible" or record.evidence_ref is not None
                ),
                key=lambda item: (item.relative_path.casefold(), item.relative_path),
            )
        )
        retained_record_paths = {record.relative_path for record in retained_records}
        exceptional_read_paths = {
            path for path in self._read_paths
            if path in self._records and self._records[path].disposition == "unread"
        }
        session = {
            "pending_dirs": [
                {"relative_path": relative_path(path), "depth": depth}
                for path, _, depth in sorted(
                    self._pending_dirs, key=lambda item: (item[1].casefold(), item[1], item[2])
                )
            ],
            "depth_deferred": [
                {"relative_path": key, "depth": value[1]}
                for key, value in sorted(self._depth_deferred.items(), key=lambda item: (item[0].casefold(), item[0]))
            ],
            "candidate_files": [
                {"relative_path": key, "size_bytes": value[1], "kind": value[2]}
                for key, value in sorted(self._candidate_files.items(), key=lambda item: (item[0].casefold(), item[0]))
                if key not in retained_record_paths
            ],
            "records": [
                {
                    "relative_path": item.relative_path,
                    "size_bytes": item.size_bytes,
                    "kind": item.kind,
                    "disposition": item.disposition,
                    "evidence_ref": item.evidence_ref,
                }
                for item in retained_records
            ],
            "read_paths": sorted(exceptional_read_paths, key=lambda item: (item.casefold(), item)),
            "excluded_counts": self._excluded_counts(),
            "oversized": sorted(self._oversized, key=lambda item: (item.casefold(), item)),
            "service_root_count": self._service_root_count_offset + len(self._service_roots),
            "workspace_declared": self._workspace_declared,
            "reasons": sorted(self._reasons),
            "warnings": sorted(self._warnings),
            "checkpoints": copy.deepcopy(self._checkpoints),
            "last_checkpoint_files": self._last_checkpoint_files,
            "last_checkpoint_bytes": self._last_checkpoint_bytes,
            "visited_entries": self._visited_entries,
            "file_attempts": self._file_attempts,
            "bytes_consumed": self._bytes_consumed,
            "active_seconds": self._active_seconds,
            "topology_seconds": self._topology_seconds,
            "topology_complete": self._topology_complete,
            "limit_overrides": copy.deepcopy(self._limit_overrides),
        }
        checkpoint: dict[str, Any] = {
            "schema_version": CHECKPOINT_SCHEMA_VERSION,
            "owner_marker": CHECKPOINT_OWNER,
            "checkpoint_id": "",
            "run_id": self.run_id,
            "root_ref": "selected-project",
            "root_fingerprint": self._root_fingerprint(),
            "policy_id": self.policy["policy_id"],
            "policy_version": self.policy["schema_version"],
            "policy_sha256": self._policy_fingerprint(),
            "expected_state_revision": expected_state_revision,
            "committed_state_revision": expected_state_revision + 1,
            "mode": self._mode,
            "last_report": copy.deepcopy(self._last_report),
            "session": session,
        }
        checkpoint["checkpoint_id"] = "checkpoint-" + self._checkpoint_digest(checkpoint)[:32]
        _validate_checkpoint_envelope(checkpoint)
        return checkpoint

    @classmethod
    def from_checkpoint(
        cls,
        project_root: str | os.PathLike[str],
        run_id: str,
        checkpoint: dict[str, Any],
        *,
        policy_path: str | os.PathLike[str] | None = None,
        clock: Callable[[], float] = time.monotonic,
        limit_overrides: Mapping[str, Mapping[str, int]] | None = None,
    ) -> "ScannerSession":
        """Restore a session after validating its root, run, policy, and digest."""

        _validate_checkpoint_envelope(checkpoint)
        session = cls(
            project_root, run_id, policy_path=policy_path, clock=clock, limit_overrides=limit_overrides
        )
        if checkpoint["run_id"] != session.run_id:
            raise ScannerError("checkpoint_run_mismatch")
        if checkpoint["root_fingerprint"] != session._root_fingerprint():
            raise ScannerError("checkpoint_root_mismatch")
        if (
            checkpoint["policy_id"] != session.policy["policy_id"]
            or checkpoint["policy_version"] != session.policy["schema_version"]
            or checkpoint["policy_sha256"] != session._policy_fingerprint()
        ):
            raise ScannerError("checkpoint_policy_mismatch")
        if checkpoint["session"].get("limit_overrides") != session._limit_overrides:
            raise ScannerError("checkpoint_policy_mismatch")
        if (
            checkpoint["last_report"].get("run_id") != checkpoint["run_id"]
            or checkpoint["last_report"].get("mode") != checkpoint["mode"]
            or checkpoint["last_report"].get("policy_version") != checkpoint["policy_version"]
        ):
            raise ScannerError("checkpoint_invalid")
        data = checkpoint["session"]

        try:
            pending_items = data["pending_dirs"] + data["depth_deferred"]
            if any(
                not isinstance(item, dict)
                or set(item) != {"relative_path", "depth"}
                or not isinstance(item.get("depth"), int)
                or isinstance(item.get("depth"), bool)
                or not 0 <= item["depth"] <= 50
                or (
                    item.get("relative_path") != ""
                    and not _directory_disposition(item.get("relative_path"), session.policy)[0]
                )
                for item in pending_items
            ):
                raise ScannerError("checkpoint_invalid")
            candidate_paths: set[str] = set()
            candidate_items: dict[str, dict[str, Any]] = {}
            for item in data["candidate_files"]:
                path = item.get("relative_path") if isinstance(item, dict) else None
                if (
                    not isinstance(item, dict)
                    or set(item) != {"relative_path", "size_bytes", "kind"}
                    or not isinstance(path, str)
                    or not _path_disposition(path, session.policy)[0]
                    or path in candidate_paths
                    or not isinstance(item.get("size_bytes"), int)
                    or isinstance(item.get("size_bytes"), bool)
                    or item["size_bytes"] < 0
                    or item.get("kind") not in ("manifest", "document", "source")
                ):
                    raise ScannerError("checkpoint_invalid")
                candidate_paths.add(path)
                candidate_items[path] = item
            record_paths: set[str] = set()
            for item in data["records"]:
                path = item.get("relative_path") if isinstance(item, dict) else None
                if (
                    not isinstance(item, dict)
                    or set(item) != {"relative_path", "size_bytes", "kind", "disposition", "evidence_ref"}
                    or not isinstance(path, str)
                    or not _path_disposition(path, session.policy)[0]
                    or path in record_paths
                    or not isinstance(item.get("size_bytes"), int)
                    or isinstance(item.get("size_bytes"), bool)
                    or item["size_bytes"] < 0
                    or item.get("kind") not in ("manifest", "document", "source")
                    or item.get("disposition") not in ("eligible", "read", "unparseable", "changed", "unread")
                    or (
                        item.get("disposition") == "read"
                        and item.get("evidence_ref") != _evidence_id(path)
                    )
                    or (
                        item.get("disposition") != "read"
                        and item.get("evidence_ref") is not None
                    )
                    or (
                        item.get("evidence_ref") is not None
                        and (
                            not isinstance(item.get("evidence_ref"), str)
                            or re.fullmatch(r"ev-[a-z0-9][a-z0-9_-]{0,76}", item["evidence_ref"]) is None
                        )
                    )
                ):
                    raise ScannerError("checkpoint_invalid")
                if path in candidate_paths:
                    candidate = candidate_items[path]
                    if (
                        candidate["size_bytes"] != item["size_bytes"]
                        or candidate["kind"] != item["kind"]
                    ):
                        raise ScannerError("checkpoint_invalid")
                record_paths.add(path)
            inventory_paths = candidate_paths | record_paths
            if (
                not isinstance(data["read_paths"], list)
                or not set(data["read_paths"]).issubset(inventory_paths)
                or not isinstance(data["oversized"], list)
                or not set(data["oversized"]).issubset(inventory_paths)
                or not isinstance(data["excluded_counts"], dict)
                or set(data["excluded_counts"]) != {"sensitive", "generated", "unsupported", "unsafe_path"}
                or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in data["excluded_counts"].values())
                or not isinstance(data["service_root_count"], int)
                or isinstance(data["service_root_count"], bool)
                or data["service_root_count"] < 0
                or not isinstance(data["workspace_declared"], bool)
                or not isinstance(data["topology_complete"], bool)
                or any(reason not in _REASON_ORDER for reason in data["reasons"])
                or any(warning not in {"files_80_percent", "bytes_80_percent", "time_80_percent", "topology_entries_80_percent", "topology_time_80_percent"} for warning in data["warnings"])
                or not isinstance(data["checkpoints"], list)
                or any(
                    not isinstance(item, dict)
                    or set(item) != {"file_attempts", "bytes_consumed", "elapsed_ms"}
                    or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in item.values())
                    for item in data["checkpoints"]
                )
            ):
                raise ScannerError("checkpoint_invalid")
            for key in (
                "last_checkpoint_files", "last_checkpoint_bytes", "visited_entries", "file_attempts", "bytes_consumed"
            ):
                if not isinstance(data[key], int) or isinstance(data[key], bool) or data[key] < 0:
                    raise ScannerError("checkpoint_invalid")
            for key in ("active_seconds", "topology_seconds"):
                if not isinstance(data[key], (int, float)) or isinstance(data[key], bool) or not math.isfinite(data[key]) or data[key] < 0:
                    raise ScannerError("checkpoint_invalid")
        except (KeyError, TypeError, ValueError) as error:
            raise ScannerError("checkpoint_invalid") from error

        def local_path(value: str) -> Path:
            if value == "":
                return session.root
            if not _validate_relative(value):
                raise ScannerError("checkpoint_invalid")
            path = session.root.joinpath(*PurePosixPath(value).parts)
            return path

        try:
            session._pending_dirs = [
                (local_path(item["relative_path"]), item["relative_path"], item["depth"])
                for item in data["pending_dirs"]
            ]
            session._depth_deferred = {
                item["relative_path"]: (local_path(item["relative_path"]), item["depth"])
                for item in data["depth_deferred"]
            }
            session._visited_paths = set()
            session._candidate_files = {
                item["relative_path"]: (
                    local_path(item["relative_path"]), item["size_bytes"], item["kind"]
                )
                for item in data["candidate_files"]
            }
            for item in data["records"]:
                existing_candidate = session._candidate_files.get(item["relative_path"])
                if existing_candidate is not None and (
                    existing_candidate[1] != item["size_bytes"]
                    or existing_candidate[2] != item["kind"]
                ):
                    raise ScannerError("checkpoint_invalid")
                session._candidate_files[item["relative_path"]] = (
                    local_path(item["relative_path"]), item["size_bytes"], item["kind"]
                )
            ceiling = session.policy["max_file_bytes"][checkpoint["mode"]]
            session._records = {
                relative_path: _FileRecord(relative_path, size, kind)
                for relative_path, (_, size, kind) in session._candidate_files.items()
                if size <= ceiling
            }
            for item in data["records"]:
                existing = session._records.get(item["relative_path"])
                if (
                    existing is None
                    or item["size_bytes"] != existing.size_bytes
                    or item["kind"] != existing.kind
                ):
                    raise ScannerError("checkpoint_invalid")
                session._records[item["relative_path"]] = _FileRecord(
                    item["relative_path"], item["size_bytes"], item["kind"],
                    item["disposition"], item["evidence_ref"],
                )
            session._read_paths = set(data["read_paths"]) | {
                item["relative_path"] for item in data["records"]
                if item["disposition"] in ("read", "unparseable", "changed")
            }
            session._excluded = {
                "sensitive": set(), "generated": set(), "unsupported": set(), "unsafe_path": set(),
            }
            session._oversized = set(data["oversized"])
            session._excluded_count_offsets = dict(data["excluded_counts"])
            session._excluded_count_offsets["unsupported"] -= len(session._oversized)
            if any(
                not isinstance(value, int) or isinstance(value, bool) or value < 0
                for value in session._excluded_count_offsets.values()
            ):
                raise ScannerError("checkpoint_invalid")
            summary = checkpoint["last_report"]["summary"]
            session._facts = {
                (item["kind"], item["value"]): set(item["evidence_refs"])
                for item in summary["facts"]
            }
            session._evidence = {
                item["evidence_id"]: copy.deepcopy(item) for item in summary["evidence"]
            }
            session._package_nodes = {}
            session._pending_dependencies = []
            session._service_roots = set()
            session._service_root_count_offset = data["service_root_count"]
            session._workspace_declared = data["workspace_declared"]
            session._reasons = set(data["reasons"])
            session._warnings = set(data["warnings"])
            session._checkpoints = copy.deepcopy(data["checkpoints"])
            session._last_checkpoint_files = data["last_checkpoint_files"]
            session._last_checkpoint_bytes = data["last_checkpoint_bytes"]
            session._visited_entries = data["visited_entries"]
            session._file_attempts = data["file_attempts"]
            session._bytes_consumed = data["bytes_consumed"]
            session._active_seconds = float(data["active_seconds"])
            session._topology_seconds = float(data["topology_seconds"])
            session._topology_complete = False
            session._mode = checkpoint["mode"]
            session._last_report = copy.deepcopy(checkpoint["last_report"])
            topology = TypedTopology()
            topology.add_node("project", kind="project", label="selected-project")
            session.topology = topology
            session._reasons.add("topology_incomplete")
        except ScannerError:
            raise
        except (KeyError, TypeError, ValueError, context.ContextError) as error:
            raise ScannerError("checkpoint_invalid") from error
        return session

    def _cancelled(self, cancel: Callable[[], bool] | None) -> bool:
        if cancel is None:
            return False
        try:
            return bool(cancel())
        except Exception:
            return True

    def _elapsed(self, call_start: float) -> float:
        try:
            return self._active_seconds + max(0.0, float(self.clock()) - call_start)
        except Exception as error:
            raise ScannerError("clock_unavailable") from error

    def _mark_excluded(self, category: str, relative_path: str) -> None:
        target = category if category in self._excluded else "unsafe_path"
        self._excluded[target].add(relative_path)

    def _refresh_eligibility(self, mode: str) -> None:
        ceiling = self.policy["max_file_bytes"][mode]
        self._oversized.clear()
        for relative_path, (_, size, kind) in self._candidate_files.items():
            if size > ceiling:
                self._oversized.add(relative_path)
                self._records.pop(relative_path, None)
            elif relative_path not in self._records:
                self._records[relative_path] = _FileRecord(relative_path, size, kind)

    def _walk(
        self,
        mode: str,
        *,
        call_start: float,
        cancel: Callable[[], bool] | None,
    ) -> None:
        limits = self.policy["topology"][mode]
        topology_started = self.clock()

        def finish_topology_timer() -> None:
            self._topology_seconds += max(0.0, float(self.clock()) - topology_started)

        while self._pending_dirs:
            if self._cancelled(cancel):
                self._reasons.add("cancelled")
                finish_topology_timer()
                return
            if self._visited_entries >= limits["max_entries"]:
                self._reasons.update(("budget_reached", "topology_incomplete"))
                finish_topology_timer()
                return
            if self._elapsed(call_start) >= self.policy["modes"][mode]["max_seconds"]:
                self._reasons.update(("budget_reached", "topology_incomplete"))
                finish_topology_timer()
                return
            if self._topology_seconds + max(0.0, self.clock() - topology_started) >= limits["max_seconds"]:
                self._reasons.update(("budget_reached", "topology_incomplete"))
                finish_topology_timer()
                return
            directory, relative_directory, depth = self._pending_dirs.pop()
            try:
                info = directory.lstat()
                if _is_reparse(directory, info) or not stat.S_ISDIR(info.st_mode) or not _contained(self.root, directory):
                    self._mark_excluded("unsafe_path", relative_directory or "unsafe-root")
                    self._reasons.update(("containment_unsupported", "topology_incomplete"))
                    continue
                entries: list[os.DirEntry[str]] = []
                has_unvisited = False
                with os.scandir(directory) as iterator:
                    for entry in iterator:
                        relative_path = entry.name if not relative_directory else f"{relative_directory}/{entry.name}"
                        if relative_path in self._visited_paths:
                            continue
                        has_unvisited = True
                        if self._visited_entries + len(entries) >= limits["max_entries"]:
                            break
                        entries.append(entry)
                if has_unvisited and not entries:
                    self._pending_dirs.append((directory, relative_directory, depth))
                    self._reasons.update(("budget_reached", "topology_incomplete"))
                    finish_topology_timer()
                    return
                entries.sort(key=lambda item: (item.name.casefold(), item.name))
                processed_names: set[str] = set()
                for entry in entries:
                    relative_path = entry.name if not relative_directory else f"{relative_directory}/{entry.name}"
                    processed_names.add(relative_path)
                    self._visited_paths.add(relative_path)
                    self._visited_entries += 1
                    try:
                        # On Windows ``DirEntry.stat().st_nlink`` can be zero even
                        # for an ordinary file.  A fresh path lstat returns the
                        # link count used by the guarded open/identity check.
                        entry_info = Path(entry.path).lstat()
                    except OSError:
                        self._mark_excluded("unsafe_path", relative_path)
                        self._reasons.update(("containment_unsupported", "topology_incomplete"))
                        continue
                    path = Path(entry.path)
                    if entry.is_symlink() or _is_reparse(path, entry_info):
                        self._mark_excluded("unsafe_path", relative_path)
                        self._reasons.add("containment_unsupported")
                        continue
                    if stat.S_ISDIR(entry_info.st_mode):
                        allowed, category = _directory_disposition(relative_path, self.policy)
                        if not allowed:
                            self._mark_excluded(category, relative_path)
                            continue
                        if depth + 1 > limits["max_depth"]:
                            self._depth_deferred[relative_path] = (path, depth + 1)
                            self._reasons.update(("budget_reached", "topology_incomplete"))
                            continue
                        self._pending_dirs.append((path, relative_path, depth + 1))
                        continue
                    if not stat.S_ISREG(entry_info.st_mode) or entry_info.st_nlink != 1:
                        self._mark_excluded("unsafe_path", relative_path)
                        self._reasons.add("containment_unsupported")
                        continue
                    allowed, category = _path_disposition(relative_path, self.policy)
                    if not allowed:
                        self._mark_excluded(category, relative_path)
                        continue
                    name = PurePosixPath(relative_path).name.casefold()
                    if name in _MANIFEST_NAMES:
                        kind = "manifest"
                    elif name in _DOCUMENT_NAMES or PurePosixPath(name).suffix in (".md", ".rst", ".txt"):
                        kind = "document"
                    else:
                        kind = "source"
                    self._candidate_files[relative_path] = (path, entry_info.st_size, kind)
                if len(processed_names) < 1 and has_unvisited:
                    self._pending_dirs.append((directory, relative_directory, depth))
                elif has_unvisited:
                    # Re-open on continuation; already visited names are skipped safely.
                    try:
                        with os.scandir(directory) as check:
                            if any(
                                (entry.name if not relative_directory else f"{relative_directory}/{entry.name}")
                                not in self._visited_paths for entry in check
                            ):
                                self._pending_dirs.append((directory, relative_directory, depth))
                    except OSError:
                        self._reasons.update(("containment_unsupported", "topology_incomplete"))
            except OSError:
                self._reasons.update(("containment_unsupported", "topology_incomplete"))
        self._topology_complete = (
            not self._depth_deferred and "topology_incomplete" not in self._reasons
        )
        finish_topology_timer()

    def _activate_depth_deferred(self, mode: str) -> None:
        max_depth = self.policy["topology"][mode]["max_depth"]
        for relative_path in sorted(tuple(self._depth_deferred), key=lambda item: (item.casefold(), item)):
            path, depth = self._depth_deferred[relative_path]
            if depth <= max_depth:
                self._pending_dirs.append((path, relative_path, depth))
                del self._depth_deferred[relative_path]
        if self._depth_deferred:
            self._reasons.update(("budget_reached", "topology_incomplete"))

    def _add_fact(self, kind: str, value: str, evidence_ref: str) -> None:
        if value and len(value) <= 240:
            self._facts.setdefault((kind, value), set()).add(evidence_ref)

    def _add_topology_for_parse(self, record: _FileRecord, parsed: _Parsed) -> None:
        evidence_ref = record.evidence_ref
        assert evidence_ref is not None
        parent = str(PurePosixPath(record.relative_path).parent)
        if parent == ".":
            parent = "root"
        if record.kind == "manifest" and PurePosixPath(record.relative_path).name.casefold() in _MANIFEST_NAMES:
            manifest_node = _node_id("manifest", record.relative_path)
            self.topology.add_node(
                manifest_node, kind="manifest", relative_path=record.relative_path,
                label=PurePosixPath(record.relative_path).name, evidence_refs=(evidence_ref,),
            )
            self.topology.add_edge("project", manifest_node, kind="contains", evidence_refs=(evidence_ref,))
            service_node = _node_id("service", parent)
            self.topology.add_node(
                service_node, kind="service", relative_path=None if parent == "root" else parent,
                label=parent, evidence_refs=(evidence_ref,),
            )
            self.topology.add_edge(service_node, manifest_node, kind="declares", evidence_refs=(evidence_ref,))
            self._service_roots.add(parent)
            if parsed.package_name:
                package_node = _node_id(
                    "package", record.relative_path + "\0" + parsed.package_name
                )
                self.topology.add_node(
                    package_node, kind="package", relative_path=record.relative_path,
                    label=parsed.package_name, evidence_refs=(evidence_ref,),
                )
                self.topology.add_edge(service_node, package_node, kind="contains", evidence_refs=(evidence_ref,))
                self._package_nodes.setdefault(
                    parsed.package_name.casefold(), set()
                ).add(package_node)
            self._pending_dependencies.append((service_node, evidence_ref, parsed.dependencies))
        if parsed.api_lines:
            api_node = _node_id("api", record.relative_path)
            self.topology.add_node(api_node, kind="api", relative_path=record.relative_path, label="api-surface", evidence_refs=(evidence_ref,))
            self.topology.add_edge("project", api_node, kind="exposes", status="inferred", evidence_refs=(evidence_ref,))
            self._add_fact("capability", "API surface signature observed", evidence_ref)
        if parsed.storage_lines:
            storage_node = _node_id("storage", record.relative_path)
            self.topology.add_node(storage_node, kind="storage", relative_path=record.relative_path, label="storage-surface", evidence_refs=(evidence_ref,))
            self.topology.add_edge("project", storage_node, kind="uses_storage", status="inferred", evidence_refs=(evidence_ref,))
            self._add_fact("storage", "Storage integration signature observed", evidence_ref)
        if parsed.deployment:
            deploy_node = _node_id("deployment", record.relative_path)
            self.topology.add_node(deploy_node, kind="deployment", relative_path=record.relative_path, label="deployment-surface", evidence_refs=(evidence_ref,))
            self.topology.add_edge("project", deploy_node, kind="deploys", evidence_refs=(evidence_ref,))
            self._add_fact("integration", "Deployment configuration observed", evidence_ref)
        if parsed.tests:
            test_node = _node_id("test", record.relative_path)
            self.topology.add_node(test_node, kind="test", relative_path=record.relative_path, label="test-surface", evidence_refs=(evidence_ref,))
            self.topology.add_edge(test_node, "project", kind="tests", evidence_refs=(evidence_ref,))
            self._add_fact("capability", "Test surface observed", evidence_ref)

    def _link_dependencies(self) -> None:
        for service_node, evidence_ref, dependencies in self._pending_dependencies:
            for dependency in dependencies:
                targets = self._package_nodes.get(dependency.casefold(), set())
                if len(targets) == 1:
                    target = next(iter(targets))
                    self.topology.add_edge(
                        service_node, target, kind="depends_on", status="observed", evidence_refs=(evidence_ref,)
                    )
                elif len(targets) > 1:
                    self._reasons.add("topology_incomplete")

    def _record_checkpoint(self) -> None:
        checkpoint = self.policy["deep_checkpoint"]
        if (
            self._file_attempts - self._last_checkpoint_files >= checkpoint["max_files_between_checkpoints"]
            or self._bytes_consumed - self._last_checkpoint_bytes >= checkpoint["max_bytes_between_checkpoints"]
        ):
            self._checkpoints.append({
                "file_attempts": self._file_attempts,
                "bytes_consumed": self._bytes_consumed,
                "elapsed_ms": int(self._active_seconds * 1000),
            })
            self._last_checkpoint_files = self._file_attempts
            self._last_checkpoint_bytes = self._bytes_consumed

    def _read_inventory(
        self,
        mode: str,
        *,
        call_start: float,
        cancel: Callable[[], bool] | None,
    ) -> None:
        limits = self.policy["modes"][mode]
        per_file = self.policy["max_file_bytes"][mode]
        for relative_path in sorted(self._records, key=lambda item: (item.casefold(), item)):
            if relative_path in self._read_paths:
                continue
            if self._cancelled(cancel):
                self._reasons.add("cancelled")
                return
            if self._file_attempts >= limits["max_files"]:
                self._reasons.add("budget_reached")
                return
            if self._bytes_consumed >= limits["max_bytes"] or self._elapsed(call_start) >= limits["max_seconds"]:
                self._reasons.add("budget_reached")
                return
            record = self._records[relative_path]
            path, _, _ = self._candidate_files[relative_path]
            remaining = limits["max_bytes"] - self._bytes_consumed
            read_limit = min(per_file, remaining)
            self._file_attempts += 1
            status, text, consumed = _guarded_read(self.root, path, read_limit)
            self._bytes_consumed += consumed
            if status == "read" and text is not None:
                self._read_paths.add(relative_path)
                try:
                    parsed = _parse_file(relative_path, record.kind, text)
                except (ValueError, TypeError, ET.ParseError, tomllib.TOMLDecodeError, json.JSONDecodeError):
                    record.disposition = "unparseable"
                    self._reasons.add("encoding_error")
                    continue
                evidence_ref = _evidence_id(relative_path)
                record.disposition = "read"
                record.evidence_ref = evidence_ref
                self._evidence[evidence_ref] = {
                    "evidence_id": evidence_ref,
                    "kind": {
                        "manifest": "project_manifest",
                        "document": "project_document",
                        "source": "project_source",
                    }[record.kind],
                    "relative_path": relative_path,
                    "line_start": None,
                    "line_end": None,
                    "answer_id": None,
                    "content_persisted": False,
                }
                for kind, value, _, _ in parsed.facts:
                    self._add_fact(kind, value, evidence_ref)
                suffix = PurePosixPath(relative_path).suffix.casefold()
                language = _LANGUAGE_BY_SUFFIX.get(suffix)
                if language:
                    self._add_fact("language", language, evidence_ref)
                self._workspace_declared = self._workspace_declared or parsed.workspace_declared
                self._add_topology_for_parse(record, parsed)
            else:
                if status != "budget_reached":
                    self._read_paths.add(relative_path)
                record.disposition = {
                    "changed_file": "changed",
                    "encoding_error": "unparseable",
                }.get(status, "unread")
                if status in ("budget_reached", "changed_file", "encoding_error", "containment_unsupported"):
                    self._reasons.add(status)
                elif status == "excluded_sources":
                    self._reasons.add("excluded_sources")
                    self._mark_excluded("sensitive", relative_path)
            if mode == "deep":
                self._record_checkpoint()
            if status == "budget_reached":
                return
        self._link_dependencies()

    def _excluded_counts(self) -> dict[str, int]:
        return {
            "sensitive": self._excluded_count_offsets["sensitive"] + len(self._excluded["sensitive"]),
            "generated": self._excluded_count_offsets["generated"] + len(self._excluded["generated"]),
            "unsupported": self._excluded_count_offsets["unsupported"] + len(self._excluded["unsupported"] | self._oversized),
            "unsafe_path": self._excluded_count_offsets["unsafe_path"] + len(self._excluded["unsafe_path"]),
        }

    def _counters(self, mode: str) -> dict[str, Any]:
        limits = self.policy["modes"][mode]
        topology = self.policy["topology"][mode]
        budget_reached = (
            "budget_reached" in self._reasons
            or self._file_attempts >= limits["max_files"]
            or self._bytes_consumed >= limits["max_bytes"]
            or self._active_seconds >= limits["max_seconds"]
            or self._visited_entries >= topology["max_entries"]
        )
        return {
            "visited_entries": self._visited_entries,
            "file_attempts": self._file_attempts,
            "bytes_consumed": self._bytes_consumed,
            "elapsed_ms": int(self._active_seconds * 1000),
            "eligible_files": len(self._records),
            "manifest_count": sum(
                PurePosixPath(path).name.casefold() in _MANIFEST_NAMES for path in self._records
            ),
            "service_roots": self._service_root_count_offset + len(self._service_roots),
            "workspace_declared": self._workspace_declared,
            "topology_complete": self._topology_complete and not self._pending_dirs and not self._depth_deferred,
            "budget_reached": budget_reached,
        }

    def _update_warnings(self, mode: str, counters: dict[str, Any]) -> None:
        self._warnings.clear()
        fraction = self.policy["mode_budget_warning_fraction"]
        limits = self.policy["modes"][mode]
        topology = self.policy["topology"][mode]
        if counters["file_attempts"] >= limits["max_files"] * fraction:
            self._warnings.add("files_80_percent")
        if counters["bytes_consumed"] >= limits["max_bytes"] * fraction:
            self._warnings.add("bytes_80_percent")
        if counters["elapsed_ms"] >= limits["max_seconds"] * 1000 * fraction:
            self._warnings.add("time_80_percent")
        if counters["visited_entries"] >= topology["max_entries"] * fraction:
            self._warnings.add("topology_entries_80_percent")
        if self._topology_seconds >= topology["max_seconds"] * fraction:
            self._warnings.add("topology_time_80_percent")

    def _classification(self, counters: dict[str, Any]) -> str:
        classification = self.policy["classification"]
        monorepo = self._workspace_declared or counters["service_roots"] >= classification["monorepo_min_service_roots"]
        incomplete = not counters["topology_complete"] or counters["budget_reached"] or "containment_unsupported" in self._reasons
        if monorepo:
            self._reasons.add("monorepo_detected")
            return "large_or_monorepo"
        if incomplete:
            return "large_or_monorepo"
        if counters["eligible_files"] == 0:
            self._reasons.add("no_eligible_files")
            return "idea_or_empty"
        if (
            counters["eligible_files"] <= classification["compact_max_eligible_files"]
            and counters["manifest_count"] <= classification["compact_max_manifests"]
        ):
            return "compact"
        if (
            counters["eligible_files"] <= classification["standard_max_eligible_files"]
            and counters["manifest_count"] <= classification["standard_max_manifests"]
            and counters["service_roots"] <= classification["standard_max_service_roots"]
        ):
            return "standard"
        self._reasons.add("oversized_project")
        return "large_or_monorepo"

    def _summary(self, status: str, classification: str) -> dict[str, Any]:
        facts: list[dict[str, Any]] = []
        for ordinal, ((kind, value), refs) in enumerate(
            sorted(self._facts.items(), key=lambda item: (item[0][0], item[0][1].casefold(), item[0][1]))[:64]
        ):
            facts.append({
                "fact_id": f"fact-{ordinal:04d}-{hashlib.sha256((kind + value).encode()).hexdigest()[:12]}",
                "kind": kind,
                "value": value,
                "evidence_refs": sorted(refs)[:8],
            })
        inferences: list[dict[str, Any]] = []
        topology_fact_ids = [item["fact_id"] for item in facts if item["kind"] in ("topology", "dependency", "integration")]
        components = self.topology.weak_components()
        if components and facts:
            basis = topology_fact_ids or [facts[0]["fact_id"]]
            inferences.append({
                "inference_id": "inference-topology-components",
                "statement": f"Observed topology contains {len(components)} weak component(s); missing edges remain unknown.",
                "confidence": "medium" if status == "complete" else "low",
                "basis_fact_ids": basis[:16],
            })
        gaps: list[dict[str, str]] = []
        if status != "complete":
            gaps.append({
                "code": "coverage_partial",
                "detail": "The bounded scan did not observe every policy-relevant source.",
                "next_check": "Review reason codes and explicitly continue with a permitted higher mode only if useful.",
            })
        if not self._topology_complete:
            gaps.append({
                "code": "topology_partial",
                "detail": "Unvisited areas and absent edges remain unknown.",
                "next_check": "Continue the same run within the next explicit cumulative mode budget.",
            })
        evidence = [self._evidence[key] for key in sorted(self._evidence)[:80]]
        allowed_evidence = {item["evidence_id"] for item in evidence}
        facts = [item for item in facts if set(item["evidence_refs"]).issubset(allowed_evidence)]
        fact_ids = {item["fact_id"] for item in facts}
        inferences = [item for item in inferences if set(item["basis_fact_ids"]).issubset(fact_ids)]
        summary = {
            "schema_version": "1.0.0",
            "run_id": self.run_id,
            "summary_id": f"summary-{self.run_id}",
            "content_class": "minimized_project_context",
            "coverage": "complete" if status == "complete" else "partial",
            "facts": facts,
            "inferences": inferences,
            "gaps": gaps[:32],
            "evidence": evidence,
        }
        while len(json.dumps(summary, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > MAX_SUMMARY_BYTES:
            referenced = {
                ref for fact in summary["facts"] for ref in fact["evidence_refs"]
            }
            removable_evidence = [
                index
                for index, item in enumerate(summary["evidence"])
                if item["evidence_id"] not in referenced
            ]
            if removable_evidence:
                summary["evidence"].pop(removable_evidence[-1])
            elif summary["inferences"]:
                summary["inferences"].pop()
            elif summary["facts"]:
                removed = summary["facts"].pop()
                referenced = {ref for fact in summary["facts"] for ref in fact["evidence_refs"]}
                summary["evidence"] = [item for item in summary["evidence"] if item["evidence_id"] in referenced]
                summary["inferences"] = [
                    item for item in summary["inferences"] if removed["fact_id"] not in item["basis_fact_ids"]
                ]
            elif summary["evidence"]:
                summary["evidence"].pop()
            else:
                break
        return summary

    def _build_report(self, mode: str) -> dict[str, Any]:
        counters = self._counters(mode)
        self._update_warnings(mode, counters)
        if not counters["topology_complete"]:
            self._reasons.add("topology_incomplete")
        excluded = self._excluded_counts()
        if any(excluded.values()):
            self._reasons.add("excluded_sources")
        classification = self._classification(counters)
        if "cancelled" in self._reasons:
            status = "cancelled"
        elif self._reasons.intersection({
            "budget_reached", "topology_incomplete", "excluded_sources", "encoding_error",
            "changed_file", "containment_unsupported",
        }):
            status = "partial"
        else:
            status = "complete"
        summary = self._summary(status, classification)
        evidence_paths = {
            item["relative_path"] for item in summary["evidence"]
            if item.get("relative_path") is not None
        }
        ordered_records = sorted(
            self._records.values(),
            key=lambda item: (
                0 if item.relative_path in evidence_paths else 1,
                item.relative_path.casefold(),
                item.relative_path,
            ),
        )
        files = [
            {
                "relative_path": record.relative_path,
                "size_bytes": min(record.size_bytes, 4194304),
                "kind": record.kind,
                "disposition": record.disposition,
                "evidence_ref": record.evidence_ref,
            }
            for record in ordered_records[:500]
        ]
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_id,
            "policy_version": POLICY_VERSION,
            "mode": mode,
            "root_ref": "selected-project",
            "files": files,
            "counters": counters,
            "excluded_counts": excluded,
        }
        report = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_id,
            "policy_version": POLICY_VERSION,
            "mode": mode,
            "status": status,
            "classification": classification,
            "manifest": manifest,
            "summary": summary,
            "reason_codes": [reason for reason in _REASON_ORDER if reason in self._reasons],
        }
        while len(json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > self.policy["max_response_bytes"]:
            if manifest["files"] and manifest["files"][-1]["relative_path"] not in evidence_paths:
                manifest["files"].pop()
            elif report["summary"]["inferences"]:
                report["summary"]["inferences"].pop()
            elif report["summary"]["facts"]:
                report["summary"]["facts"].pop()
            else:
                raise ScannerError("response_limit")
        return report

    def scan(
        self,
        mode: str | None = None,
        *,
        material_gap: bool = False,
        explicit_confirmation: bool = False,
        cancel: Callable[[], bool] | None = None,
    ) -> ScanResult:
        """Run or explicitly continue this session under cumulative ceilings."""

        selected = "standard" if mode is None else mode
        if selected not in MODES:
            raise ScannerError("invalid_mode")
        if self._mode is not None:
            if MODES.index(selected) < MODES.index(self._mode):
                raise ScannerError("mode_regression")
            if selected == "deep" and self._mode != "deep":
                visible_gap = bool(
                    self._last_report
                    and self._last_report.get("status") in ("partial", "cancelled")
                    and self._last_report.get("summary", {}).get("gaps")
                )
                if not material_gap or not visible_gap:
                    raise ScannerError("deep_requires_material_gap")
                if not explicit_confirmation:
                    raise ScannerError("deep_requires_confirmation")
        elif selected == "deep":
            raise ScannerError("deep_requires_material_gap")
        if self._mode is not None and MODES.index(selected) > MODES.index(self._mode):
            self._reasons.discard("budget_reached")
            self._reasons.discard("topology_incomplete")
            self._reasons.discard("cancelled")
        self._mode = selected
        self._activate_depth_deferred(selected)
        call_start = self.clock()
        try:
            self._refresh_eligibility(selected)
            if self._pending_dirs:
                self._topology_complete = False
                self._walk(selected, call_start=call_start, cancel=cancel)
            self._refresh_eligibility(selected)
            if "cancelled" not in self._reasons:
                self._read_inventory(selected, call_start=call_start, cancel=cancel)
        finally:
            try:
                self._active_seconds += max(0.0, float(self.clock()) - call_start)
            except Exception as error:
                raise ScannerError("clock_unavailable") from error
        if selected == "deep" and (
            not self._checkpoints
            or self._checkpoints[-1]["file_attempts"] != self._file_attempts
            or self._checkpoints[-1]["bytes_consumed"] != self._bytes_consumed
        ):
            self._checkpoints.append({
                "file_attempts": self._file_attempts,
                "bytes_consumed": self._bytes_consumed,
                "elapsed_ms": int(self._active_seconds * 1000),
            })
        report = self._build_report(selected)
        self._last_report = copy.deepcopy(report)
        return ScanResult(
            report=report,
            topology=self.topology,
            eligible_paths=tuple(sorted(self._records, key=lambda item: (item.casefold(), item))),
            observed_paths=tuple(sorted(
                (
                    item.relative_path for item in self._records.values()
                    if item.disposition == "read" and item.evidence_ref is not None
                ),
                key=lambda item: (item.casefold(), item),
            )),
            warnings=tuple(sorted(self._warnings)),
            checkpoints=tuple(copy.deepcopy(self._checkpoints)),
            policy=copy.deepcopy(self.policy),
        )

    @staticmethod
    def _truncate_utf8(text: str, max_bytes: int) -> tuple[str, int, bool]:
        data = text.encode("utf-8")
        if len(data) <= max_bytes:
            return text, len(data), False
        data = data[:max_bytes]
        while data:
            try:
                value = data.decode("utf-8", errors="strict")
                return value, len(data), True
            except UnicodeDecodeError as error:
                data = data[: error.start]
        return "", 0, True

    def read_sources(
        self,
        selection: dict[str, Any],
        *,
        cancel: Callable[[], bool] | None = None,
    ) -> TransientContext:
        """Read a validated references-only selection into transient memory."""

        if not isinstance(selection, dict) or self._mode is None:
            raise ScannerError("invalid_selection")
        exact_keys = {
            "schema_version", "run_id", "brief_version", "selection_id", "mode", "root_ref",
            "purpose", "requested_sources", "max_read_bytes", "max_model_context_bytes",
            "authorization_scope", "content_delivery", "persistence", "scan_policy_version",
            "charge_to_scan_budget",
        }
        if (
            set(selection) != exact_keys
            or selection.get("schema_version") != SCHEMA_VERSION
            or selection.get("scan_policy_version") != POLICY_VERSION
            or selection.get("run_id") != self.run_id
            or selection.get("mode") != self._mode
            or selection.get("root_ref") != "selected-project"
            or selection.get("authorization_scope") != "existing_user_host_permissions"
            or selection.get("content_delivery") != "transient_host_context"
            or selection.get("persistence") != "references_only"
            or selection.get("charge_to_scan_budget") is not True
            or not isinstance(selection.get("requested_sources"), list)
        ):
            raise ScannerError("invalid_selection")
        context_limit = self.policy["targeted_context"][self._mode]
        max_read_bytes = selection.get("max_read_bytes")
        max_model_bytes = selection.get("max_model_context_bytes")
        if (
            not isinstance(max_read_bytes, int) or isinstance(max_read_bytes, bool)
            or not 1 <= max_read_bytes <= context_limit["max_read_bytes"]
            or not isinstance(max_model_bytes, int) or isinstance(max_model_bytes, bool)
            or not 1 <= max_model_bytes <= context_limit["max_model_context_bytes"]
            or len(selection["requested_sources"]) > context_limit["max_files"]
        ):
            raise ScannerError("invalid_selection")
        seen_paths: set[str] = set()
        for item in selection["requested_sources"]:
            if (
                not isinstance(item, dict) or set(item) != {"relative_path", "line_start", "line_end"}
                or item.get("relative_path") not in self._records
                or item["relative_path"] in seen_paths
            ):
                raise ScannerError("invalid_selection")
            start, end = item.get("line_start"), item.get("line_end")
            if (start is None) != (end is None) or (
                start is not None
                and (
                    not isinstance(start, int) or isinstance(start, bool) or start < 1
                    or not isinstance(end, int) or isinstance(end, bool) or end < start
                )
            ):
                raise ScannerError("invalid_selection")
            seen_paths.add(item["relative_path"])

        limits = self.policy["modes"][self._mode]
        call_start = self.clock()
        items: list[ContextExcerpt] = []
        reasons: set[str] = set()
        bytes_read = 0
        model_bytes = 0
        truncated = False
        try:
            total_requests = len(selection["requested_sources"])
            for request_index, requested in enumerate(selection["requested_sources"]):
                if self._cancelled(cancel):
                    reasons.add("cancelled")
                    truncated = True
                    break
                if (
                    self._file_attempts >= limits["max_files"]
                    or self._bytes_consumed >= limits["max_bytes"]
                    or bytes_read >= max_read_bytes
                    or self._elapsed(call_start) >= limits["max_seconds"]
                ):
                    reasons.add("budget_reached")
                    truncated = True
                    break
                relative_path = requested["relative_path"]
                path, _, _ = self._candidate_files[relative_path]
                global_remaining = limits["max_bytes"] - self._bytes_consumed
                selection_remaining = max_read_bytes - bytes_read
                read_limit = min(self.policy["max_file_bytes"][self._mode], global_remaining, selection_remaining)
                if read_limit < 1:
                    reasons.add("budget_reached")
                    truncated = True
                    break
                self._file_attempts += 1
                status, text, consumed = _guarded_read(self.root, path, read_limit)
                self._bytes_consumed += consumed
                bytes_read += consumed
                if status != "read" or text is None:
                    reason = status if status in {
                        "budget_reached", "changed_file", "encoding_error", "containment_unsupported"
                    } else "excluded_sources"
                    reasons.add(reason)
                    truncated = True
                    if reason in ("changed_file", "encoding_error", "containment_unsupported"):
                        self._reasons.add(reason)
                    continue
                lines = text.splitlines(keepends=True)
                requested_start = requested["line_start"]
                requested_end = requested["line_end"]
                if requested_start is None:
                    excerpt_text = text
                    line_start = 1 if lines else None
                    line_end = len(lines) if lines else None
                else:
                    excerpt_text = "".join(lines[requested_start - 1 : requested_end])
                    line_start = requested_start
                    line_end = min(requested_end, len(lines)) if lines else requested_start
                remaining_model = max_model_bytes - model_bytes
                if remaining_model < 1:
                    reasons.add("budget_reached")
                    truncated = True
                    break
                remaining_requests = total_requests - request_index
                fair_model_share = max(1, remaining_model // remaining_requests)
                excerpt_text, encoded_size, clipped = self._truncate_utf8(
                    excerpt_text, fair_model_share
                )
                if clipped:
                    truncated = True
                    reasons.add("budget_reached")
                if excerpt_text:
                    items.append(ContextExcerpt(relative_path, excerpt_text, line_start, line_end))
                    model_bytes += encoded_size
        finally:
            try:
                self._active_seconds += max(0.0, float(self.clock()) - call_start)
            except Exception as error:
                raise ScannerError("clock_unavailable") from error
        counters = {
            "file_attempts": self._file_attempts,
            "bytes_consumed": self._bytes_consumed,
            "elapsed_ms": int(self._active_seconds * 1000),
        }
        reason_order = ("budget_reached", "cancelled", "changed_file", "encoding_error", "excluded_sources", "containment_unsupported")
        return TransientContext(
            items=tuple(items),
            bytes_read=bytes_read,
            model_context_bytes=model_bytes,
            truncated=truncated,
            reason_codes=tuple(reason for reason in reason_order if reason in reasons),
            counters=counters,
        )


def write_checkpoint_locked(output_root: Path, checkpoint: dict[str, Any]) -> None:
    """Persist a validated private checkpoint while CP-07 holds the state lock."""

    _validate_checkpoint_envelope(checkpoint)
    data = state_store.canonical_json_bytes(checkpoint)
    destination = output_root / CHECKPOINT_NAME
    pending = output_root / CHECKPOINT_PENDING_NAME
    for existing in (destination, pending):
        if existing.exists():
            try:
                previous = state_store.strict_json_bytes(
                    state_store._validate_regular_file(existing, max_bytes=MAX_CHECKPOINT_BYTES)
                )
                if previous.get("owner_marker") != CHECKPOINT_OWNER:
                    raise ScannerError("checkpoint_invalid")
            except (AttributeError, ScannerError, state_store.StateError) as error:
                raise state_store.StateError("state_invalid") from error
    state_store._prospective(output_root, [(pending, len(data)), (destination, len(data))])
    state_store._write_synced(pending, data)
    try:
        os.replace(pending, destination)
    except OSError as error:
        raise state_store.StateError("state_write_failed") from error


def read_checkpoint_locked(output_root: Path) -> dict[str, Any]:
    """Read and validate the owned checkpoint while CP-07 holds the state lock."""

    path = output_root / CHECKPOINT_NAME
    if not path.exists():
        raise ScannerError("checkpoint_missing")
    try:
        value = state_store.strict_json_bytes(
            state_store._validate_regular_file(path, max_bytes=MAX_CHECKPOINT_BYTES)
        )
    except state_store.StateError as error:
        raise ScannerError("checkpoint_invalid") from error
    return _validate_checkpoint_envelope(value)


def remove_checkpoint_locked(output_root: Path, *, run_id: str | None = None) -> None:
    """Remove only owned checkpoint files while CP-07 holds the state lock."""

    for path in (output_root / CHECKPOINT_NAME, output_root / CHECKPOINT_PENDING_NAME):
        if not path.exists():
            continue
        try:
            value = state_store.strict_json_bytes(
                state_store._validate_regular_file(path, max_bytes=MAX_CHECKPOINT_BYTES)
            )
            if value.get("owner_marker") != CHECKPOINT_OWNER:
                raise ScannerError("checkpoint_invalid")
            if run_id is not None and value.get("run_id") != run_id:
                raise ScannerError("checkpoint_run_mismatch")
            path.unlink()
        except ScannerError:
            raise
        except (OSError, AttributeError, state_store.StateError) as error:
            raise state_store.StateError("state_write_failed") from error


def load_checkpoint(
    project_root: str | os.PathLike[str],
    run_id: str,
    state_revision: int,
    *,
    policy_path: str | os.PathLike[str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    limit_overrides: Mapping[str, Mapping[str, int]] | None = None,
) -> ScannerSession:
    """Load a committed checkpoint and bind it to the current state revision."""

    if not isinstance(state_revision, int) or isinstance(state_revision, bool):
        raise ScannerError("checkpoint_revision_mismatch")
    try:
        root = state_store.output_root(state_store.validate_project_root(project_root), create=False)
    except state_store.StateError as error:
        raise ScannerError("checkpoint_missing") from error
    checkpoint = read_checkpoint_locked(root)
    if checkpoint["committed_state_revision"] != state_revision:
        raise ScannerError("checkpoint_revision_mismatch")
    restored_overrides = limit_overrides
    if restored_overrides is None:
        restored_overrides = checkpoint["session"].get("limit_overrides") or None
    return ScannerSession.from_checkpoint(
        project_root,
        run_id,
        checkpoint,
        policy_path=policy_path,
        clock=clock,
        limit_overrides=restored_overrides,
    )


def scan_project(
    project_root: str | os.PathLike[str],
    *,
    run_id: str | None = None,
    mode: str | None = None,
    policy_path: str | os.PathLike[str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    limit_overrides: Mapping[str, Mapping[str, int]] | None = None,
    cancel: Callable[[], bool] | None = None,
) -> ScanResult:
    """One-shot convenience; deep remains unavailable without a prior gap."""

    session = ScannerSession(
        project_root,
        run_id or str(uuid.uuid4()),
        policy_path=policy_path,
        clock=clock,
        limit_overrides=limit_overrides,
    )
    return session.scan(mode, cancel=cancel)
