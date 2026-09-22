"""Build a bounded public evidence pack from one validated retrieval result."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any
import uuid


MAX_QUERY_BYTES = 8192
MAX_EVIDENCE_BYTES = 163840
MAX_PLUGIN_INPUT_BYTES = 204800
MAX_CARDS = 12
MAX_MANIFEST_BYTES = 65536
MAX_SNAPSHOT_BYTES = 32 * 1024 * 1024
ASSETS = Path(__file__).resolve().parent.parent / "assets"
MANIFEST_PATH = ASSETS / "catalog.search-manifest.json"
SNAPSHOT_PATH = ASSETS / "catalog.snapshot.json"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
PIN_KEYS = {
    "catalog_snapshot_id", "source_sha256", "cards_sha256", "index_sha256",
    "policy_sha256", "taxonomy_sha256", "card_schema_version",
    "activity_schema_version", "index_format_version",
    "retrieval_policy_version", "corpus_kind",
}
MANIFEST_KEYS = {
    "schema_version", "pins", "builder_version", "sqlite_version", "built_at",
    "source_snapshot_date", "row_count", "index_file", "cards_file",
    "policy_file", "contains_project_context", "read_only_runtime",
    "logical_rows_sha256", "route_registry",
}
ROUTE_REGISTRY_KEYS = {
    "schema_version", "table_name", "route_count", "route_member_count",
    "logical_routes_sha256",
}
TRUSTED_MANIFEST_SHA256 = (
    "1d090b0e2e56f4c7cd38276d0d8b08be2436e0c75b77649cf00d32c13cb9497f"
)
TRUSTED_ROUTE_REGISTRY_SHA256 = (
    "25682afda8d95ef295b337cfe32025438c9e5f65e7c37fcc87ff2ca82495cb55"
)
TRUSTED_PRODUCTION_CARD_PINS = {
    "catalog_snapshot_id": "catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e",
    "source_sha256": "d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e",
    "cards_sha256": "fceeaa7eaf1d83e280ed4244fed2717a820d59fcdc5b1aa849fd82f245f2ef5b",
    "taxonomy_sha256": "09dcaac99e1e1d7110e9ab64ef33e20654be225fb6ea81dc5bfbf3483f3a721f",
    "card_schema_version": "2.0.0",
    "activity_schema_version": "2.0.0",
    "corpus_kind": "catalog_snapshot",
}
TRUSTED_SYNTHETIC_PINS = {
    "catalog_snapshot_id": "fixture-catalog-2",
    "source_sha256": "d487719a3299ca76a52d9f7bf5f89cfd1323c65c6777b0d5e4c65adcc381fed5",
    "cards_sha256": "d955adc033ff103d03496fcd1b22d6bdd9a9f7562be57c1b5de004ecc0e3b76f",
    "index_sha256": "ab9dbb9a03701785ecdc76b1b17718a4a7ed7a62b03da044aa6e8fcbf0208063",
    "policy_sha256": "ff6e8444c4664492bb099f0819b2d284aa5c28f0d44c7a745c63f434c3489dbf",
    "taxonomy_sha256": "09dcaac99e1e1d7110e9ab64ef33e20654be225fb6ea81dc5bfbf3483f3a721f",
    "card_schema_version": "2.0.0",
    "activity_schema_version": "2.0.0",
    "index_format_version": 3,
    "retrieval_policy_version": "2.1.0",
    "corpus_kind": "synthetic_fixture",
}
REASON_ORDER = (
    "constraint_mismatch", "mandatory_fact_unknown", "archived", "unavailable",
    "duplicate_identity", "insufficient_evidence", "context_budget",
    "candidate_budget", "invalid_query", "fts5_unavailable", "index_missing",
    "index_corrupt", "index_incompatible", "no_hits", "cancelled",
)


def _load_sibling(name: str):
    path = Path(__file__).resolve().with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"stackguide_{name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"trusted sibling unavailable: {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


matcher = _load_sibling("matcher")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _query_sha256(query: Any) -> str:
    return hashlib.sha256(_canonical_bytes(query)).hexdigest()


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_uuid(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def _ordered_reasons(reasons) -> list[str]:
    values = set(reasons)
    return [reason for reason in REASON_ORDER if reason in values]


def _trusted_manifest_pins() -> dict[str, Any]:
    try:
        size = MANIFEST_PATH.stat().st_size
        if not 2 <= size <= MAX_MANIFEST_BYTES:
            raise ValueError("invalid catalog manifest size")
        raw = MANIFEST_PATH.read_bytes()
    except OSError as error:
        raise ValueError("catalog manifest unavailable") from error
    if hashlib.sha256(raw).hexdigest() != TRUSTED_MANIFEST_SHA256:
        raise ValueError("catalog manifest trust anchor mismatch")
    try:
        manifest = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("catalog manifest malformed") from error
    if not isinstance(manifest, dict) or set(manifest) != MANIFEST_KEYS:
        raise ValueError("catalog manifest shape mismatch")
    pins = manifest.get("pins")
    route_registry = manifest.get("route_registry")
    if (
        manifest.get("schema_version") != "2.1.0"
        or manifest.get("builder_version") != "2.0.0"
        or not isinstance(manifest.get("sqlite_version"), str)
        or not manifest["sqlite_version"]
        or not isinstance(manifest.get("built_at"), str)
        or not manifest["built_at"]
        or manifest.get("source_snapshot_date") != "2026-09-01"
        or manifest.get("row_count") != 2500
        or manifest.get("index_file") != "catalog.search.sqlite"
        or manifest.get("cards_file") != "catalog.snapshot.json"
        or manifest.get("policy_file") != "retrieval-policy.json"
        or manifest.get("contains_project_context") is not False
        or manifest.get("read_only_runtime") is not True
        or not isinstance(manifest.get("logical_rows_sha256"), str)
        or SHA256_RE.fullmatch(manifest["logical_rows_sha256"]) is None
        or not isinstance(pins, dict)
        or set(pins) != PIN_KEYS
        or pins.get("index_format_version") != 3
        or pins.get("retrieval_policy_version") != "2.1.0"
        or any(pins.get(name) != value for name, value in TRUSTED_PRODUCTION_CARD_PINS.items())
        or any(
            not isinstance(pins.get(name), str) or SHA256_RE.fullmatch(pins[name]) is None
            for name in (
                "source_sha256", "cards_sha256", "index_sha256",
                "policy_sha256", "taxonomy_sha256",
            )
        )
        or not isinstance(route_registry, dict)
        or set(route_registry) != ROUTE_REGISTRY_KEYS
        or route_registry.get("schema_version") != "1.0.0"
        or route_registry.get("table_name") != "taxonomy_route_registry"
        or route_registry.get("route_count") != 126
        or route_registry.get("route_member_count") != 162
        or route_registry.get("logical_routes_sha256") != TRUSTED_ROUTE_REGISTRY_SHA256
    ):
        raise ValueError("catalog manifest identity mismatch")
    return pins


def _base_pack(query: dict[str, Any], result: dict[str, Any], pack_id: str) -> dict[str, Any]:
    return {
        "schema_version": "2.1.0",
        "run_id": result["run_id"],
        "pack_id": pack_id,
        "query_id": query["query_id"],
        "query_sha256": _query_sha256(query),
        "brief_version": query["brief_version"],
        "pins": result.get("pins"),
        "status": "unavailable",
        "cards": [],
        "exclusions": [],
        "truncated": bool(result.get("truncated", False)),
        "reason_codes": [],
    }


def _validate_inputs(
    query: Any,
    result: Any,
    cards_by_id: Any,
    pack_id: Any,
    max_cards: Any,
    max_evidence_bytes: Any,
) -> tuple[int, int]:
    if not isinstance(query, dict) or not isinstance(result, dict) or not isinstance(cards_by_id, dict):
        raise ValueError("pack inputs must be objects")
    if not isinstance(pack_id, str) or ID_RE.fullmatch(pack_id) is None:
        raise ValueError("invalid pack id")
    if not _is_int(max_cards) or not 1 <= max_cards <= MAX_CARDS:
        raise ValueError("invalid card budget")
    if not _is_int(max_evidence_bytes) or not 1024 <= max_evidence_bytes <= MAX_EVIDENCE_BYTES:
        raise ValueError("invalid evidence budget")
    query_bytes = _canonical_bytes(query)
    if len(query_bytes) > MAX_QUERY_BYTES:
        raise ValueError("query byte budget exceeded")
    required_query = {
        "query_id", "brief_version", "max_cards", "max_evidence_bytes", "constraints",
    }
    if not required_query.issubset(query):
        raise ValueError("incomplete query")
    if (
        not isinstance(query["query_id"], str)
        or ID_RE.fullmatch(query["query_id"]) is None
        or not _is_int(query["brief_version"])
        or not _is_int(query["max_cards"])
        or not 1 <= query["max_cards"] <= MAX_CARDS
        or not _is_int(query["max_evidence_bytes"])
        or not 1024 <= query["max_evidence_bytes"] <= MAX_EVIDENCE_BYTES
    ):
        raise ValueError("invalid query binding")
    if (
        result.get("schema_version") != "2.1.0"
        or not _valid_uuid(result.get("run_id"))
        or result.get("query_id") != query["query_id"]
        or result.get("query_sha256") != _query_sha256(query)
        or result.get("brief_version") != query["brief_version"]
        or result.get("source_mode") != "catalog_only"
        or result.get("retrieval_engine") != "sqlite_fts5"
        or result.get("status") not in {
            "ok", "no_match", "retrieval_unavailable", "index_incompatible",
            "invalid_query", "cancelled",
        }
        or not isinstance(result.get("candidates"), list)
        or not isinstance(result.get("reason_codes"), list)
    ):
        raise ValueError("retrieval result does not bind to query")
    if result["status"] in {"ok", "no_match"} and not isinstance(result.get("pins"), dict):
        raise ValueError("successful retrieval must pin its bundle")
    pins = result.get("pins")
    if pins is not None and (
        not isinstance(pins, dict)
        or set(pins) != PIN_KEYS
        or any(
            not isinstance(pins.get(name), str) or SHA256_RE.fullmatch(pins[name]) is None
            for name in (
                "source_sha256", "cards_sha256", "index_sha256",
                "policy_sha256", "taxonomy_sha256",
            )
        )
    ):
        raise ValueError("invalid retrieval pins")
    if isinstance(pins, dict) and (
        pins.get("policy_sha256") != query.get("policy_sha256")
        or pins.get("retrieval_policy_version") != query.get("policy_version")
        or pins.get("card_schema_version") != query.get("card_schema_version")
        or pins.get("activity_schema_version") != query.get("activity_schema_version")
        or pins.get("index_format_version") != query.get("index_format_version")
    ):
        raise ValueError("retrieval pins do not bind to query")
    return min(max_cards, query["max_cards"], MAX_CARDS), min(
        max_evidence_bytes, query["max_evidence_bytes"], MAX_EVIDENCE_BYTES
    )


def _trusted_cards(
    pins: dict[str, Any],
    cards_by_id: dict[Any, Any],
    candidate_ids: list[int],
) -> dict[int, dict[str, Any]]:
    corpus_kind = pins["corpus_kind"]
    if corpus_kind == "catalog_snapshot":
        if pins != _trusted_manifest_pins():
            raise ValueError("retrieval pins do not match trusted catalog manifest")
        try:
            size = SNAPSHOT_PATH.stat().st_size
            if not 2 <= size <= MAX_SNAPSHOT_BYTES:
                raise ValueError("invalid catalog snapshot size")
            raw = SNAPSHOT_PATH.read_bytes()
            if hashlib.sha256(raw).hexdigest() != pins["cards_sha256"]:
                raise ValueError("catalog snapshot hash mismatch")
            snapshot = json.loads(
                raw.decode("utf-8"),
                parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("catalog snapshot unavailable") from error
        if (
            not isinstance(snapshot, dict)
            or snapshot.get("schema_version") != pins["card_schema_version"]
            or snapshot.get("activity_schema_version") != pins["activity_schema_version"]
            or snapshot.get("catalog_snapshot_id") != pins["catalog_snapshot_id"]
            or snapshot.get("source_sha256") != pins["source_sha256"]
            or snapshot.get("taxonomy_sha256") != pins["taxonomy_sha256"]
            or snapshot.get("corpus_kind") != "catalog_snapshot"
            or not isinstance(snapshot.get("cards"), list)
            or len(snapshot["cards"]) != 2500
        ):
            raise ValueError("catalog snapshot identity mismatch")
        trusted: dict[int, dict[str, Any]] = {}
        for card in snapshot["cards"]:
            identity = card.get("identity") if isinstance(card, dict) else None
            repository_id = identity.get("github_repository_id") if isinstance(identity, dict) else None
            if not _is_int(repository_id) or repository_id < 1 or repository_id in trusted:
                raise ValueError("catalog snapshot card identity mismatch")
            trusted[repository_id] = card
        output: dict[int, dict[str, Any]] = {}
        for repository_id in candidate_ids:
            supplied = cards_by_id.get(repository_id)
            pinned = trusted.get(repository_id)
            if (
                not isinstance(supplied, dict)
                or pinned is None
                or _canonical_bytes(supplied) != _canonical_bytes(pinned)
            ):
                raise ValueError("supplied card does not match pinned catalog snapshot")
            output[repository_id] = pinned
        return output

    if corpus_kind == "synthetic_fixture":
        if pins != TRUSTED_SYNTHETIC_PINS:
            raise ValueError("untrusted synthetic fixture pins")
        if set(cards_by_id) != {900000001}:
            raise ValueError("synthetic fixture corpus mismatch")
        supplied = cards_by_id.get(900000001)
        identity = supplied.get("identity") if isinstance(supplied, dict) else None
        if (
            not isinstance(supplied, dict)
            or not isinstance(identity, dict)
            or identity.get("github_repository_id") != 900000001
            or supplied.get("schema_version") != "2.0.0"
            or supplied.get("corpus_kind") != "synthetic_fixture"
            or hashlib.sha256(_canonical_bytes([supplied])).hexdigest() != pins["cards_sha256"]
        ):
            raise ValueError("synthetic fixture card hash mismatch")
        if any(repository_id != 900000001 for repository_id in candidate_ids):
            raise ValueError("synthetic fixture candidate mismatch")
        return {900000001: supplied}

    raise ValueError("unsupported evidence corpus")


def _exclusion(repository_id: int, reasons) -> dict[str, Any]:
    ordered = _ordered_reasons(reasons)
    if not ordered:
        ordered = ["unavailable"]
    return {"github_repository_id": repository_id, "reason_codes": ordered[:8]}


def _serialized_size(pack: dict[str, Any]) -> int:
    return len(_canonical_bytes(pack))


def build_evidence_pack(
    query,
    retrieval_result,
    cards_by_id,
    *,
    pack_id,
    max_cards,
    max_evidence_bytes,
):
    """Select primary then reference candidates under the actual compact-byte cap."""
    card_limit, evidence_limit = _validate_inputs(
        query, retrieval_result, cards_by_id, pack_id, max_cards, max_evidence_bytes
    )
    pack = _base_pack(query, retrieval_result, pack_id)
    status = retrieval_result["status"]
    if status == "no_match":
        pack["status"] = "no_match"
        pack["reason_codes"] = _ordered_reasons(retrieval_result["reason_codes"] or ["no_hits"])
        if _serialized_size(pack) > evidence_limit:
            raise ValueError("evidence envelope exceeds requested budget")
        return pack
    if status != "ok":
        pack["status"] = "unavailable"
        pack["reason_codes"] = _ordered_reasons(retrieval_result["reason_codes"] or ["unavailable"])
        if _serialized_size(pack) > evidence_limit:
            raise ValueError("evidence envelope exceeds requested budget")
        return pack

    candidates = retrieval_result["candidates"]
    candidate_ids: list[int] = []
    for expected_rank, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            raise ValueError("invalid retrieval candidate")
        repository_id = candidate.get("github_repository_id")
        if not _is_int(repository_id) or repository_id < 1 or candidate.get("rank") != expected_rank:
            raise ValueError("invalid retrieval candidate")
        candidate_ids.append(repository_id)
    trusted_cards = _trusted_cards(retrieval_result["pins"], cards_by_id, candidate_ids)
    seen_ids: set[int] = set()
    duplicate_ids: set[int] = set()
    normalized: list[tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]] = []
    expected_rank = 1
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("invalid retrieval candidate")
        repository_id = candidate.get("github_repository_id")
        if (
            not _is_int(repository_id)
            or repository_id < 1
            or candidate.get("rank") != expected_rank
            or not isinstance(candidate.get("rrf_score"), (int, float))
            or isinstance(candidate.get("rrf_score"), bool)
            or not 0 < candidate["rrf_score"] <= 1
            or not isinstance(candidate.get("matched_fields"), list)
            or not candidate["matched_fields"]
            or len(candidate["matched_fields"]) != len(set(candidate["matched_fields"]))
        ):
            raise ValueError("invalid retrieval candidate")
        expected_rank += 1
        if repository_id in seen_ids:
            duplicate_ids.add(repository_id)
        seen_ids.add(repository_id)
        card = trusted_cards.get(repository_id)
        eligibility = None
        if isinstance(card, dict):
            identity = card.get("identity")
            if (
                isinstance(identity, dict)
                and identity.get("github_repository_id") == repository_id
            ):
                eligibility = matcher.match_candidate(card, query)
            else:
                card = None
        else:
            card = None
        normalized.append((candidate, card, eligibility))

    fixed_exclusions: dict[int, dict[str, Any]] = {}
    selectable: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for candidate, card, eligibility in normalized:
        repository_id = candidate["github_repository_id"]
        if repository_id in duplicate_ids:
            fixed_exclusions[repository_id] = _exclusion(repository_id, ["duplicate_identity"])
        elif card is None or eligibility is None:
            fixed_exclusions[repository_id] = _exclusion(repository_id, ["unavailable"])
        elif eligibility["status"] == "blocked":
            fixed_exclusions[repository_id] = _exclusion(
                repository_id, eligibility["reason_codes"] or ["constraint_mismatch"]
            )
        else:
            selectable.append((candidate, card, eligibility))

    selectable.sort(key=lambda item: (
        0 if item[2]["status"] == "primary_eligible" else 1,
        item[0]["rank"],
    ))
    packed_ids: set[int] = set()
    dynamic_exclusions: dict[int, dict[str, Any]] = {}
    for candidate, card, eligibility in selectable:
        repository_id = candidate["github_repository_id"]
        if len(pack["cards"]) >= card_limit:
            dynamic_exclusions[repository_id] = _exclusion(repository_id, ["candidate_budget"])
            continue
        record = {
            "card": card,
            "retrieval_rank": candidate["rank"],
            "eligibility": eligibility,
            "rrf_score": candidate["rrf_score"],
            "matched_fields": candidate["matched_fields"],
        }
        tentative_cards = [*pack["cards"], record]
        tentative_exclusions = {
            **fixed_exclusions,
            **dynamic_exclusions,
        }
        for future_candidate, _, _ in selectable:
            future_id = future_candidate["github_repository_id"]
            if future_id != repository_id and future_id not in packed_ids and future_id not in tentative_exclusions:
                tentative_exclusions[future_id] = _exclusion(future_id, ["candidate_budget"])
        tentative = dict(pack)
        tentative["status"] = "ready"
        tentative["cards"] = tentative_cards
        tentative["exclusions"] = []
        tentative_seen: set[int] = set()
        for candidate_item in candidates:
            candidate_id = candidate_item["github_repository_id"]
            if candidate_id in tentative_exclusions and candidate_id not in tentative_seen:
                tentative["exclusions"].append(tentative_exclusions[candidate_id])
                tentative_seen.add(candidate_id)
        tentative["reason_codes"] = _ordered_reasons(
            reason
            for item in tentative["exclusions"]
            for reason in item["reason_codes"]
        )
        if _serialized_size(tentative) <= evidence_limit:
            pack["cards"].append(record)
            packed_ids.add(repository_id)
        else:
            dynamic_exclusions[repository_id] = _exclusion(repository_id, ["context_budget"])

    all_exclusions = {**fixed_exclusions, **dynamic_exclusions}
    pack["exclusions"] = []
    exclusion_seen: set[int] = set()
    for candidate in candidates:
        candidate_id = candidate["github_repository_id"]
        if candidate_id in all_exclusions and candidate_id not in exclusion_seen:
            pack["exclusions"].append(all_exclusions[candidate_id])
            exclusion_seen.add(candidate_id)
    pack["reason_codes"] = _ordered_reasons(
        reason for item in pack["exclusions"] for reason in item["reason_codes"]
    )
    pack["truncated"] = bool(pack["truncated"] or any(
        reason in {"candidate_budget", "context_budget"}
        for item in pack["exclusions"] for reason in item["reason_codes"]
    ))
    if pack["cards"]:
        pack["status"] = "ready"
    elif any("context_budget" in item["reason_codes"] for item in pack["exclusions"]):
        pack["status"] = "unavailable"
        if "context_budget" not in pack["reason_codes"]:
            pack["reason_codes"].append("context_budget")
    else:
        pack["status"] = "no_match"
        if not pack["reason_codes"]:
            pack["reason_codes"] = ["no_hits"]

    size = _serialized_size(pack)
    if size > evidence_limit or len(_canonical_bytes(query)) + size > MAX_PLUGIN_INPUT_BYTES:
        raise ValueError("no schema-shaped evidence pack fits the requested budget")
    covered = packed_ids | set(all_exclusions)
    if covered != seen_ids or packed_ids & set(all_exclusions):
        raise ValueError("candidate coverage invariant failed")
    return pack
