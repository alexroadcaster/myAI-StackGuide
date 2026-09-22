"""Bounded, read-only SQLite FTS5 retrieval for the local StackGuide bundle."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
from typing import Any
import unicodedata
import uuid


TRUSTED_MANIFEST_SHA256 = "1d090b0e2e56f4c7cd38276d0d8b08be2436e0c75b77649cf00d32c13cb9497f"
APPLICATION_ID = 1297695049
INDEX_FORMAT_VERSION = 3
MANIFEST_SCHEMA_VERSION = "2.1.0"
POLICY_VERSION = "2.1.0"
CARD_SCHEMA_VERSION = "2.0.0"
ACTIVITY_SCHEMA_VERSION = "2.0.0"
ROUTE_REGISTRY_SCHEMA_VERSION = "1.0.0"
ROUTE_REGISTRY_TABLE = "taxonomy_route_registry"
MAX_QUERY_BYTES = 8192
MAX_FETCHED_HITS = 150
MAX_CARDS = 12
MAX_EVIDENCE_BYTES = 163840
RRF_K = 60
FTS_COLUMNS = (
    "full_name",
    "full_name_aliases",
    "upstream_description",
    "catalog_description",
    "topics",
    "category_labels",
    "use_cases",
    "integration_surface",
    "best_for",
)
FIELD_WEIGHTS = {
    "full_name": 5.0,
    "full_name_aliases": 5.0,
    "upstream_description": 3.0,
    "catalog_description": 3.0,
    "topics": 3.0,
    "category_labels": 1.0,
    "use_cases": 3.0,
    "integration_surface": 3.0,
    "best_for": 2.0,
}
QUERY_KEYS = {
    "schema_version", "query_id", "brief_version", "source_mode",
    "retrieval_engine", "policy_version", "policy_sha256",
    "card_schema_version", "activity_schema_version", "index_format_version",
    "taxonomy_route_id", "language", "variants", "constraints",
    "max_candidates", "max_cards", "max_evidence_bytes",
}
CONSTRAINT_KEYS = {
    "languages", "deployment", "allowed_licenses", "compatibility",
    "require_no_server", "mandatory_fields",
}
MANIFEST_KEYS = {
    "schema_version", "pins", "builder_version", "sqlite_version", "built_at",
    "source_snapshot_date", "row_count", "index_file", "cards_file",
    "policy_file", "contains_project_context", "read_only_runtime",
    "logical_rows_sha256", "route_registry",
}
PIN_KEYS = {
    "catalog_snapshot_id", "source_sha256", "cards_sha256", "index_sha256",
    "policy_sha256", "taxonomy_sha256", "card_schema_version",
    "activity_schema_version", "index_format_version",
    "retrieval_policy_version", "corpus_kind",
}
POLICY_KEYS = {
    "schema_version", "policy_id", "source_mode", "retrieval_engine",
    "tokenizer", "normalization", "query_grammar", "variant_operator",
    "prefix_queries", "model_supplied_sql", "field_weights", "rank_fusion",
    "limits", "aliases", "snapshot_max_age_days", "unknown_mandatory_fact",
    "runtime_index_access", "on_index_error", "full_catalog_prompt_fallback",
    "automatic_index_build", "bytes_encoding", "serialization",
    "calibration_status", "schema_guard_changes_require_version_review",
    "variant_hit_allocation", "card_selection", "hashing",
}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
ROUTE_RE = re.compile(r"^[a-z][a-z0-9_]{0,99}$")
VARIANT_RE = re.compile(r"^q[1-3]$")
FORBIDDEN_TERM_RE = re.compile(r'["\\*^:{}()\x00-\x1f\x7f]')


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_query_sha256(query):
    """Return the replay digest of the complete canonical query."""
    return hashlib.sha256(_canonical_bytes(query)).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json_bytes(path: Path, *, max_bytes: int) -> tuple[dict[str, Any], bytes]:
    size = path.stat().st_size
    if size < 2 or size > max_bytes:
        raise ValueError("invalid JSON asset size")
    raw = path.read_bytes()
    value = json.loads(
        raw.decode("utf-8"),
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    if not isinstance(value, dict):
        raise ValueError("JSON asset must be an object")
    return value, raw


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validated_run_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("run_id must be a canonical UUID")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as error:
        raise ValueError("run_id must be a canonical UUID") from error
    if str(parsed) != value:
        raise ValueError("run_id must be a canonical UUID")
    return value


def _normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _unique_strings(value: Any, *, maximum: int, max_chars: int, allowed=None) -> bool:
    if not isinstance(value, list) or len(value) > maximum:
        return False
    normalized: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not (1 <= len(item) <= max_chars):
            return False
        if allowed is not None and item not in allowed:
            return False
        token = _normalize(item)
        if token in normalized:
            return False
        normalized.add(token)
    return True


def _validate_manifest_policy(manifest: Any, policy: Any) -> None:
    if not isinstance(manifest, dict) or set(manifest) != MANIFEST_KEYS:
        raise ValueError("invalid manifest shape")
    pins = manifest.get("pins")
    route = manifest.get("route_registry")
    if not isinstance(pins, dict) or set(pins) != PIN_KEYS:
        raise ValueError("invalid manifest pins")
    if not isinstance(route, dict) or set(route) != {
        "schema_version", "table_name", "route_count", "route_member_count",
        "logical_routes_sha256",
    }:
        raise ValueError("invalid route registry manifest")
    if (
        manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION
        or pins.get("card_schema_version") != CARD_SCHEMA_VERSION
        or pins.get("activity_schema_version") != ACTIVITY_SCHEMA_VERSION
        or pins.get("retrieval_policy_version") != POLICY_VERSION
        or pins.get("index_format_version") != INDEX_FORMAT_VERSION
        or pins.get("corpus_kind") not in {"catalog_snapshot", "synthetic_fixture"}
        or manifest.get("index_file") != "catalog.search.sqlite"
        or manifest.get("cards_file") != "catalog.snapshot.json"
        or manifest.get("policy_file") != "retrieval-policy.json"
        or manifest.get("contains_project_context") is not False
        or manifest.get("read_only_runtime") is not True
        or not _is_int(manifest.get("row_count"))
        or manifest["row_count"] < 0
        or route.get("schema_version") != ROUTE_REGISTRY_SCHEMA_VERSION
        or route.get("table_name") != ROUTE_REGISTRY_TABLE
        or not _is_int(route.get("route_count"))
        or route["route_count"] < 1
        or not _is_int(route.get("route_member_count"))
        or route["route_member_count"] < 1
        or not isinstance(route.get("logical_routes_sha256"), str)
        or SHA256_RE.fullmatch(route["logical_routes_sha256"]) is None
    ):
        raise ValueError("incompatible manifest")
    for name in (
        "source_sha256", "cards_sha256", "index_sha256", "policy_sha256",
        "taxonomy_sha256",
    ):
        if not isinstance(pins.get(name), str) or SHA256_RE.fullmatch(pins[name]) is None:
            raise ValueError("invalid manifest hash")

    if not isinstance(policy, dict) or set(policy) != POLICY_KEYS:
        raise ValueError("invalid policy shape")
    limits = policy.get("limits")
    fusion = policy.get("rank_fusion")
    if (
        policy.get("schema_version") != POLICY_VERSION
        or policy.get("source_mode") != "catalog_only"
        or policy.get("retrieval_engine") != "sqlite_fts5"
        or policy.get("tokenizer") != "unicode61"
        or policy.get("normalization") != "nfkc_casefold_versioned_aliases"
        or policy.get("query_grammar") != "quoted_literal_terms_only"
        or policy.get("variant_operator") != "OR"
        or policy.get("prefix_queries") is not False
        or policy.get("model_supplied_sql") is not False
        or policy.get("runtime_index_access") != "read_only"
        or policy.get("on_index_error") != "explicit_failure"
        or policy.get("full_catalog_prompt_fallback") is not False
        or policy.get("automatic_index_build") is not False
        or policy.get("field_weights") != FIELD_WEIGHTS
        or not isinstance(limits, dict)
        or limits.get("max_query_variants") != 3
        or limits.get("max_terms_per_variant") != 8
        or limits.get("max_term_chars") != 64
        or limits.get("max_retrieved_hits") != MAX_FETCHED_HITS
        or limits.get("max_detailed_cards") != MAX_CARDS
        or limits.get("max_evidence_bytes") != MAX_EVIDENCE_BYTES
        or limits.get("max_request_bytes") != MAX_QUERY_BYTES
        or not isinstance(fusion, dict)
        or fusion.get("method") != "rrf"
        or fusion.get("k") != RRF_K
        or fusion.get("variant_weights") != "equal"
        or fusion.get("dedupe_key") != "github_repository_id"
        or fusion.get("tie_breaker") != "github_repository_id_ascending"
        or fusion.get("compare_raw_bm25_across_variants") is not False
    ):
        raise ValueError("incompatible retrieval policy")
    if pins["policy_sha256"] is None:
        raise ValueError("missing policy pin")


def validate_query(query, *, manifest, policy):
    """Validate a closed bounded query against the active manifest and policy."""
    _validate_manifest_policy(manifest, policy)
    if not isinstance(query, dict) or set(query) != QUERY_KEYS:
        raise ValueError("invalid query shape")
    try:
        query_bytes = _canonical_bytes(query)
    except (TypeError, ValueError) as error:
        raise ValueError("query is not canonical JSON") from error
    if len(query_bytes) > min(MAX_QUERY_BYTES, policy["limits"]["max_request_bytes"]):
        raise ValueError("query byte budget exceeded")
    pins = manifest["pins"]
    if (
        query.get("schema_version") != MANIFEST_SCHEMA_VERSION
        or not isinstance(query.get("query_id"), str)
        or ID_RE.fullmatch(query["query_id"]) is None
        or not _is_int(query.get("brief_version"))
        or not 1 <= query["brief_version"] <= 1_000_000
        or query.get("source_mode") != "catalog_only"
        or query.get("retrieval_engine") != "sqlite_fts5"
        or query.get("policy_version") != POLICY_VERSION
        or query.get("policy_sha256") != pins["policy_sha256"]
        or query.get("card_schema_version") != CARD_SCHEMA_VERSION
        or query.get("activity_schema_version") != ACTIVITY_SCHEMA_VERSION
        or query.get("index_format_version") != INDEX_FORMAT_VERSION
        or query.get("language") not in {"ru", "en", "mixed"}
    ):
        raise ValueError("incompatible query pins")
    route_id = query.get("taxonomy_route_id")
    if route_id is not None and (
        not isinstance(route_id, str) or ROUTE_RE.fullmatch(route_id) is None
    ):
        raise ValueError("invalid taxonomy route")

    variants = query.get("variants")
    if not isinstance(variants, list) or not 1 <= len(variants) <= 3:
        raise ValueError("invalid query variants")
    variant_ids: set[str] = set()
    for variant in variants:
        if not isinstance(variant, dict) or set(variant) != {"variant_id", "terms"}:
            raise ValueError("invalid query variant")
        variant_id = variant.get("variant_id")
        terms = variant.get("terms")
        if (
            not isinstance(variant_id, str)
            or VARIANT_RE.fullmatch(variant_id) is None
            or variant_id in variant_ids
            or not isinstance(terms, list)
            or not 1 <= len(terms) <= 8
        ):
            raise ValueError("invalid query variant")
        variant_ids.add(variant_id)
        normalized_terms: set[str] = set()
        for term in terms:
            if (
                not isinstance(term, str)
                or not 1 <= len(term) <= 64
                or FORBIDDEN_TERM_RE.search(term) is not None
                or not _normalize(term)
            ):
                raise ValueError("invalid query term")
            normalized = _normalize(term)
            if normalized in normalized_terms:
                raise ValueError("duplicate query term")
            normalized_terms.add(normalized)

    constraints = query.get("constraints")
    if not isinstance(constraints, dict) or set(constraints) != CONSTRAINT_KEYS:
        raise ValueError("invalid constraints")
    if (
        not _unique_strings(constraints["languages"], maximum=8, max_chars=64)
        or not _unique_strings(
            constraints["deployment"], maximum=3, max_chars=11,
            allowed={"local", "self_hosted", "cloud"},
        )
        or not _unique_strings(constraints["allowed_licenses"], maximum=12, max_chars=80)
        or not _unique_strings(constraints["compatibility"], maximum=12, max_chars=160)
        or (
            constraints["require_no_server"] is not None
            and not isinstance(constraints["require_no_server"], bool)
        )
        or not _unique_strings(
            constraints["mandatory_fields"], maximum=5, max_chars=13,
            allowed={"license", "deployment", "language", "compatibility", "no_server"},
        )
    ):
        raise ValueError("invalid constraints")
    for name, ceiling in (
        ("max_candidates", MAX_FETCHED_HITS),
        ("max_cards", MAX_CARDS),
        ("max_evidence_bytes", MAX_EVIDENCE_BYTES),
    ):
        value = query.get(name)
        minimum = 1024 if name == "max_evidence_bytes" else 1
        if not _is_int(value) or not minimum <= value <= min(ceiling, policy["limits"][{
            "max_candidates": "max_retrieved_hits",
            "max_cards": "max_detailed_cards",
            "max_evidence_bytes": "max_evidence_bytes",
        }[name]]):
            raise ValueError("invalid query budget")
    return None


def _alias_pairs(aliases: Any) -> list[tuple[str, str]]:
    if not isinstance(aliases, list):
        raise ValueError("invalid aliases")
    pairs: list[tuple[str, str]] = []
    seen: dict[str, str] = {}
    for entry in aliases:
        if not isinstance(entry, dict) or set(entry) != {"canonical", "terms"}:
            raise ValueError("invalid aliases")
        canonical = entry.get("canonical")
        terms = entry.get("terms")
        if not isinstance(canonical, str) or not _normalize(canonical) or not isinstance(terms, list):
            raise ValueError("invalid aliases")
        target = _normalize(canonical)
        for term in terms:
            if not isinstance(term, str) or not _normalize(term):
                raise ValueError("invalid aliases")
            source = _normalize(term)
            prior = seen.get(source)
            if prior is not None and prior != target:
                raise ValueError("ambiguous aliases")
            seen[source] = target
    pairs.extend(sorted(seen.items(), key=lambda item: (-len(item[0]), item[0])))
    return pairs


def _boundary_replace(value: str, source: str, target: str) -> str:
    start = 0
    output: list[str] = []
    while True:
        index = value.find(source, start)
        if index < 0:
            output.append(value[start:])
            break
        end = index + len(source)
        left_ok = index == 0 or not (value[index - 1].isalnum() or value[index - 1] == "_")
        right_ok = end == len(value) or not (value[end].isalnum() or value[end] == "_")
        if left_ok and right_ok:
            output.append(value[start:index])
            output.append(target)
            start = end
        else:
            output.append(value[start:end])
            start = end
    return "".join(output)


def _compiled_terms(terms: Any, aliases: Any) -> list[str]:
    if not isinstance(terms, list) or not 1 <= len(terms) <= 8:
        raise ValueError("invalid terms")
    pairs = _alias_pairs(aliases)
    compiled: list[str] = []
    seen: set[str] = set()
    for term in terms:
        if not isinstance(term, str) or not 1 <= len(term) <= 64:
            raise ValueError("invalid term")
        literal = " ".join(unicodedata.normalize("NFKC", term).split())
        value = _normalize(literal)
        if not literal or not value:
            raise ValueError("invalid term")
        replaced = False
        for source, target in pairs:
            updated = _boundary_replace(value, source, target)
            replaced = replaced or updated != value
            value = updated
        output = value if replaced else literal
        dedupe_key = _normalize(output)
        if dedupe_key not in seen:
            compiled.append(output)
            seen.add(dedupe_key)
    if not compiled:
        raise ValueError("empty compiled query")
    return compiled


def compile_fts5_query(terms, *, aliases):
    """Compile model text into an OR of quoted FTS5 literal phrases."""
    return " OR ".join('"' + value.replace('"', '""') + '"' for value in _compiled_terms(terms, aliases))


def _failure(query: Any, run_id: str, status: str, reason: str, pins=None) -> dict[str, Any]:
    run_id = _validated_run_id(run_id)
    query_id = query.get("query_id") if isinstance(query, dict) else None
    brief_version = query.get("brief_version") if isinstance(query, dict) else None
    if not isinstance(query_id, str) or ID_RE.fullmatch(query_id) is None:
        query_id = "invalid-query"
    if not _is_int(brief_version) or not 1 <= brief_version <= 1_000_000:
        brief_version = 1
    try:
        digest = canonical_query_sha256(query)
    except (TypeError, ValueError):
        digest = canonical_query_sha256({})
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": run_id,
        "query_id": query_id,
        "query_sha256": digest,
        "brief_version": brief_version,
        "source_mode": "catalog_only",
        "retrieval_engine": "sqlite_fts5",
        "pins": pins,
        "status": status,
        "executed_variants": 0,
        "retrieved_hits": 0,
        "candidates": [],
        "truncated": False,
        "reason_codes": [reason],
    }


def _validate_bundle(connection: sqlite3.Connection, manifest: dict[str, Any], policy: dict[str, Any]) -> None:
    if connection.execute("PRAGMA application_id").fetchone() != (APPLICATION_ID,):
        raise ValueError("application id mismatch")
    if connection.execute("PRAGMA user_version").fetchone() != (INDEX_FORMAT_VERSION,):
        raise ValueError("index format mismatch")
    if connection.execute("PRAGMA quick_check").fetchone() != ("ok",):
        raise sqlite3.DatabaseError("quick check failed")
    if connection.execute("PRAGMA integrity_check").fetchone() != ("ok",):
        raise sqlite3.DatabaseError("integrity check failed")
    search_columns = tuple(row[1] for row in connection.execute("PRAGMA table_info(repository_search_rows)"))
    if search_columns != ("github_repository_id", *FTS_COLUMNS):
        raise ValueError("search columns mismatch")
    route_columns = tuple(row[1] for row in connection.execute("PRAGMA table_info(taxonomy_route_registry)"))
    if route_columns != ("route_id", "route_kind", "match_category_id", "match_category_kind"):
        raise ValueError("route columns mismatch")
    table_row = connection.execute("PRAGMA table_list(taxonomy_route_registry)").fetchone()
    if table_row is None or table_row[4] != 1 or table_row[5] != 1:
        raise ValueError("route table compatibility mismatch")

    row_count = connection.execute("SELECT count(*) FROM repository_search_rows").fetchone()[0]
    fts_count = connection.execute("SELECT count(*) FROM repository_fts").fetchone()[0]
    route_rows = [
        dict(zip(
            ("route_id", "route_kind", "match_category_id", "match_category_kind"),
            row,
        ))
        for row in connection.execute(
            "SELECT route_id, route_kind, match_category_id, match_category_kind "
            "FROM taxonomy_route_registry ORDER BY route_id, match_category_id"
        )
    ]
    route_count = connection.execute(
        "SELECT count(DISTINCT route_id) FROM taxonomy_route_registry"
    ).fetchone()[0]
    route_hash = hashlib.sha256(_canonical_bytes(route_rows)).hexdigest()
    route_manifest = manifest["route_registry"]
    if (
        row_count != manifest["row_count"]
        or fts_count != row_count
        or route_count != route_manifest["route_count"]
        or len(route_rows) != route_manifest["route_member_count"]
        or route_hash != route_manifest["logical_routes_sha256"]
    ):
        raise ValueError("bundle row compatibility mismatch")

    cursor = connection.execute("SELECT * FROM bundle_metadata WHERE singleton = 1")
    row = cursor.fetchone()
    if row is None:
        raise sqlite3.DatabaseError("missing bundle metadata")
    metadata = dict(zip((item[0] for item in cursor.description), row))
    pins = manifest["pins"]
    expected = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "catalog_snapshot_id": pins["catalog_snapshot_id"],
        "source_sha256": pins["source_sha256"],
        "taxonomy_sha256": pins["taxonomy_sha256"],
        "cards_sha256": pins["cards_sha256"],
        "policy_sha256": pins["policy_sha256"],
        "card_schema_version": CARD_SCHEMA_VERSION,
        "activity_schema_version": ACTIVITY_SCHEMA_VERSION,
        "retrieval_policy_version": POLICY_VERSION,
        "index_format_version": INDEX_FORMAT_VERSION,
        "corpus_kind": pins["corpus_kind"],
        "row_count": manifest["row_count"],
        "logical_rows_sha256": manifest["logical_rows_sha256"],
        "route_count": route_manifest["route_count"],
        "route_member_count": route_manifest["route_member_count"],
        "logical_routes_sha256": route_manifest["logical_routes_sha256"],
        "fts_columns_json": json.dumps(list(FTS_COLUMNS), ensure_ascii=False, separators=(",", ":")),
        "fts_weights_json": json.dumps(FIELD_WEIGHTS, ensure_ascii=False, separators=(",", ":")),
        "tokenizer": "unicode61",
        "normalization": policy["normalization"],
    }
    for name, value in expected.items():
        if metadata.get(name) != value:
            raise ValueError("bundle metadata mismatch")


def _execute_variant(
    connection: sqlite3.Connection,
    match_query: str,
    route_id: str | None,
    limit: int,
) -> list[sqlite3.Row]:
    highlights = ", ".join(
        f"highlight(repository_fts, {index}, char(1), char(2)) AS h{index}"
        for index in range(len(FTS_COLUMNS))
    )
    weights = ", ".join(str(FIELD_WEIGHTS[name]) for name in FTS_COLUMNS)
    sql = (
        "SELECT repository_fts.rowid AS github_repository_id, "
        f"bm25(repository_fts, {weights}) AS score, {highlights} "
        "FROM repository_fts "
        "WHERE repository_fts MATCH ? "
    )
    parameters: list[Any] = [match_query]
    if route_id is not None:
        sql += (
            "AND EXISTS ("
            "SELECT 1 FROM repository_classifications AS rc "
            "JOIN taxonomy_route_registry AS tr "
            "ON tr.match_category_id = rc.category_id "
            "WHERE rc.github_repository_id = repository_fts.rowid AND tr.route_id = ?"
            ") "
        )
        parameters.append(route_id)
    sql += "ORDER BY score ASC, github_repository_id ASC LIMIT ?"
    parameters.append(limit)
    return connection.execute(sql, parameters).fetchall()


def retrieve(query, *, run_id, index_path, manifest_path, policy_path):
    """Execute bounded FTS5 variants and return one schema-shaped result."""
    run_id = _validated_run_id(run_id)
    index_path = Path(index_path)
    manifest_path = Path(manifest_path)
    policy_path = Path(policy_path)
    if not manifest_path.is_file() or not index_path.is_file() or not policy_path.is_file():
        return _failure(query, run_id, "retrieval_unavailable", "index_missing")
    try:
        manifest, manifest_bytes = _load_json_bytes(manifest_path, max_bytes=65536)
        policy, policy_bytes = _load_json_bytes(policy_path, max_bytes=65536)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return _failure(query, run_id, "retrieval_unavailable", "index_corrupt")
    if hashlib.sha256(manifest_bytes).hexdigest() != TRUSTED_MANIFEST_SHA256:
        return _failure(query, run_id, "index_incompatible", "index_incompatible")
    try:
        _validate_manifest_policy(manifest, policy)
    except ValueError:
        return _failure(query, run_id, "index_incompatible", "index_incompatible")
    pins = manifest["pins"]
    try:
        validate_query(query, manifest=manifest, policy=policy)
    except (TypeError, ValueError):
        return _failure(query, run_id, "invalid_query", "invalid_query", pins=pins)
    if hashlib.sha256(policy_bytes).hexdigest() != pins["policy_sha256"]:
        return _failure(query, run_id, "index_incompatible", "index_incompatible", pins=pins)

    uri = index_path.resolve().as_uri() + "?mode=ro&immutable=1"
    connection: sqlite3.Connection | None = None
    executed = 0
    retrieved_hits = 0
    try:
        connection = sqlite3.connect(uri, uri=True)
        _validate_bundle(connection, manifest, policy)
        if _sha256_file(index_path) != pins["index_sha256"]:
            raise ValueError("index byte hash mismatch")
        connection.row_factory = sqlite3.Row
        route_id = query["taxonomy_route_id"]
        if route_id is not None:
            exists = connection.execute(
                "SELECT 1 FROM taxonomy_route_registry WHERE route_id = ? LIMIT 1",
                (route_id,),
            ).fetchone()
            if exists is None:
                return _failure(query, run_id, "invalid_query", "invalid_query", pins=pins)

        candidates: dict[int, dict[str, Any]] = {}
        remaining = query["max_candidates"]
        variants = query["variants"]
        for offset, variant in enumerate(variants):
            allocation = math.ceil(remaining / (len(variants) - offset))
            match_query = compile_fts5_query(variant["terms"], aliases=policy["aliases"])
            rows = _execute_variant(connection, match_query, route_id, allocation)
            executed += 1
            retrieved_hits += len(rows)
            remaining -= len(rows)
            for rank, row in enumerate(rows, start=1):
                repository_id = row["github_repository_id"]
                matched_fields = [
                    name for index, name in enumerate(FTS_COLUMNS)
                    if "\x01" in row[f"h{index}"]
                ]
                if not matched_fields:
                    raise sqlite3.DatabaseError("FTS match without a matched field")
                item = candidates.setdefault(repository_id, {
                    "github_repository_id": repository_id,
                    "rrf_score": 0.0,
                    "variant_ranks": [],
                    "matched_fields": set(),
                    "missing_facts": [],
                })
                item["rrf_score"] += 1.0 / (RRF_K + rank)
                item["variant_ranks"].append({
                    "variant_id": variant["variant_id"],
                    "rank": rank,
                    "bm25": min(float(row["score"]), 0.0),
                })
                item["matched_fields"].update(matched_fields)
            if remaining <= 0:
                break
    except sqlite3.OperationalError as error:
        reason = "fts5_unavailable" if "fts5" in str(error).casefold() else "index_corrupt"
        return _failure(query, run_id, "retrieval_unavailable", reason, pins=pins)
    except sqlite3.DatabaseError:
        return _failure(query, run_id, "retrieval_unavailable", "index_corrupt", pins=pins)
    except (OSError, ValueError, KeyError, TypeError):
        return _failure(query, run_id, "index_incompatible", "index_incompatible", pins=pins)
    finally:
        if connection is not None:
            connection.close()

    if not candidates:
        result = _failure(query, run_id, "no_match", "no_hits", pins=pins)
        result["executed_variants"] = executed
        result["retrieved_hits"] = retrieved_hits
        return result
    ordered = sorted(
        candidates.values(),
        key=lambda item: (-item["rrf_score"], item["github_repository_id"]),
    )
    output_candidates: list[dict[str, Any]] = []
    for rank, item in enumerate(ordered, start=1):
        output_candidates.append({
            "github_repository_id": item["github_repository_id"],
            "rank": rank,
            "rrf_score": item["rrf_score"],
            "variant_ranks": item["variant_ranks"],
            "matched_fields": [name for name in FTS_COLUMNS if name in item["matched_fields"]],
            "missing_facts": item["missing_facts"],
        })
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": run_id,
        "query_id": query["query_id"],
        "query_sha256": canonical_query_sha256(query),
        "brief_version": query["brief_version"],
        "source_mode": "catalog_only",
        "retrieval_engine": "sqlite_fts5",
        "pins": pins,
        "status": "ok",
        "executed_variants": executed,
        "retrieved_hits": retrieved_hits,
        "candidates": output_candidates,
        "truncated": retrieved_hits >= query["max_candidates"],
        "reason_codes": [],
    }
