"""Build and verify the immutable CP-06 SQLite FTS5 package."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_plugin_catalog as catalog_builder  # noqa: E402


ASSETS = ROOT / "plugins" / "myai-stackguide" / "assets"
CARDS = ASSETS / "catalog.snapshot.json"
INDEX = ASSETS / "catalog.search.sqlite"
MANIFEST = ASSETS / "catalog.search-manifest.json"
PACKAGED_POLICY = ASSETS / "retrieval-policy.json"
POLICY_SOURCE = ROOT / "specs" / "retrieval" / "retrieval-policy.json"
SOURCE_SCHEMA = ROOT / "data" / "catalog_manifest.schema.json"

INDEX_FORMAT_VERSION = 2
MANIFEST_SCHEMA_VERSION = "2.0.0"
APPLICATION_ID = 1297695049
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


class PluginSearchIndexBuildError(ValueError):
    """Raised when the CP-06 package cannot be built or verified safely."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PluginSearchIndexBuildError(message)


def _load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            PluginSearchIndexBuildError(f"non-finite JSON number in {path}: {value}")
        ),
    )


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _array_text(values: list[str]) -> str:
    return json.dumps(values, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def load_policy() -> tuple[dict[str, Any], bytes]:
    raw = POLICY_SOURCE.read_bytes()
    policy = json.loads(raw.decode("utf-8"))
    _require(policy["schema_version"] == "2.0.0", "retrieval policy must be v2")
    _require(policy["retrieval_engine"] == "sqlite_fts5", "retrieval engine mismatch")
    _require(policy["tokenizer"] == "unicode61", "tokenizer mismatch")
    _require(tuple(policy["field_weights"]) == FTS_COLUMNS, "policy/search column order mismatch")
    _require(policy["automatic_index_build"] is False, "runtime index build must remain disabled")
    _require(policy["full_catalog_prompt_fallback"] is False, "full-catalog fallback must remain disabled")
    return policy, raw


def project_card(card: dict[str, Any]) -> dict[str, Any]:
    category_labels: list[str] = []
    for classification in card["classifications"]:
        for value in (classification["category_id"], classification["title"]):
            if value not in category_labels:
                category_labels.append(value)
    return {
        "github_repository_id": card["identity"]["github_repository_id"],
        "full_name": card["identity"]["full_name"],
        "full_name_aliases": _array_text(card["identity"]["full_name_aliases"]),
        "upstream_description": card["descriptions"]["upstream"] or "",
        "catalog_description": card["descriptions"]["catalog"] or "",
        "topics": _array_text(card["repository"]["topics"]),
        "category_labels": _array_text(category_labels),
        "use_cases": _array_text(card["advisory"]["use_cases"]),
        "integration_surface": card["advisory"]["integration_surface"] or "",
        "best_for": _array_text(card["advisory"]["best_for"]),
    }


def logical_rows(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [project_card(card) for card in cards]
    rows.sort(key=lambda row: row["github_repository_id"])
    _require(len(rows) == 2500, "logical row count mismatch")
    _require(len({row["github_repository_id"] for row in rows}) == len(rows), "duplicate logical row ID")
    return rows


def logical_rows_sha256(rows: list[dict[str, Any]]) -> str:
    return _sha256(catalog_builder.canonical_bytes(rows))


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(f"""
        PRAGMA application_id = {APPLICATION_ID};
        PRAGMA user_version = {INDEX_FORMAT_VERSION};
        PRAGMA page_size = 4096;
        PRAGMA auto_vacuum = NONE;
        PRAGMA journal_mode = DELETE;

        CREATE TABLE bundle_metadata (
            singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
            schema_version TEXT NOT NULL CHECK (schema_version = '2.0.0'),
            catalog_snapshot_id TEXT NOT NULL,
            source_sha256 TEXT NOT NULL CHECK (length(source_sha256) = 64),
            source_schema_sha256 TEXT NOT NULL CHECK (length(source_schema_sha256) = 64),
            taxonomy_sha256 TEXT NOT NULL CHECK (length(taxonomy_sha256) = 64),
            field_contract_sha256 TEXT NOT NULL CHECK (length(field_contract_sha256) = 64),
            cards_sha256 TEXT NOT NULL CHECK (length(cards_sha256) = 64),
            policy_sha256 TEXT NOT NULL CHECK (length(policy_sha256) = 64),
            card_schema_version TEXT NOT NULL CHECK (card_schema_version = '2.0.0'),
            activity_schema_version TEXT NOT NULL CHECK (activity_schema_version = '2.0.0'),
            retrieval_policy_version TEXT NOT NULL CHECK (retrieval_policy_version = '2.0.0'),
            index_format_version INTEGER NOT NULL CHECK (index_format_version = 2),
            corpus_kind TEXT NOT NULL CHECK (corpus_kind = 'catalog_snapshot'),
            row_count INTEGER NOT NULL CHECK (row_count = 2500),
            logical_rows_sha256 TEXT NOT NULL CHECK (length(logical_rows_sha256) = 64),
            fts_columns_json TEXT NOT NULL,
            fts_weights_json TEXT NOT NULL,
            tokenizer TEXT NOT NULL CHECK (tokenizer = 'unicode61'),
            normalization TEXT NOT NULL
        ) STRICT;

        CREATE TABLE repository_search_rows (
            github_repository_id INTEGER PRIMARY KEY CHECK (github_repository_id > 0),
            full_name TEXT NOT NULL,
            full_name_aliases TEXT NOT NULL,
            upstream_description TEXT NOT NULL,
            catalog_description TEXT NOT NULL,
            topics TEXT NOT NULL,
            category_labels TEXT NOT NULL,
            use_cases TEXT NOT NULL,
            integration_surface TEXT NOT NULL,
            best_for TEXT NOT NULL
        ) STRICT;

        CREATE TABLE repository_classifications (
            github_repository_id INTEGER NOT NULL,
            category_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('primary', 'secondary')),
            kind TEXT NOT NULL CHECK (kind IN ('category', 'review_bucket')),
            PRIMARY KEY (github_repository_id, category_id),
            FOREIGN KEY (github_repository_id) REFERENCES repository_search_rows(github_repository_id)
        ) STRICT, WITHOUT ROWID;

        CREATE INDEX repository_classifications_category
            ON repository_classifications(category_id, github_repository_id);

        CREATE VIRTUAL TABLE repository_fts USING fts5(
            full_name,
            full_name_aliases,
            upstream_description,
            catalog_description,
            topics,
            category_labels,
            use_cases,
            integration_surface,
            best_for,
            content=repository_search_rows,
            content_rowid=github_repository_id,
            tokenize='unicode61'
        );
    """)


def build_sqlite(
    path: Path,
    cards: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    snapshot: dict[str, Any],
    policy: dict[str, Any],
    cards_sha256: str,
    policy_sha256: str,
    logical_sha256: str,
) -> None:
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        _create_schema(connection)
        connection.executemany(
            "INSERT INTO repository_search_rows VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [tuple(row[key] for key in ("github_repository_id", *FTS_COLUMNS)) for row in rows],
        )
        connection.executemany(
            "INSERT INTO repository_classifications VALUES (?, ?, ?, ?)",
            [
                (
                    card["identity"]["github_repository_id"],
                    classification["category_id"],
                    classification["role"],
                    classification["kind"],
                )
                for card in cards
                for classification in card["classifications"]
            ],
        )
        connection.execute(
            "INSERT INTO bundle_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                1,
                MANIFEST_SCHEMA_VERSION,
                snapshot["catalog_snapshot_id"],
                snapshot["source_sha256"],
                catalog_builder.file_sha256(SOURCE_SCHEMA),
                snapshot["taxonomy_sha256"],
                snapshot["field_contract_sha256"],
                cards_sha256,
                policy_sha256,
                snapshot["schema_version"],
                snapshot["activity_schema_version"],
                policy["schema_version"],
                INDEX_FORMAT_VERSION,
                snapshot["corpus_kind"],
                len(rows),
                logical_sha256,
                _array_text(list(FTS_COLUMNS)),
                json.dumps(policy["field_weights"], ensure_ascii=False, separators=(",", ":")),
                policy["tokenizer"],
                policy["normalization"],
            ),
        )
        connection.execute("INSERT INTO repository_fts(repository_fts) VALUES ('rebuild')")
        connection.commit()
        connection.execute("INSERT INTO repository_fts(repository_fts, rank) VALUES ('integrity-check', 1)")
        _require(connection.execute("PRAGMA quick_check").fetchone()[0] == "ok", "SQLite quick_check failed")
        _require(connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "SQLite integrity_check failed")
        connection.commit()
        connection.execute("VACUUM")
    finally:
        connection.close()
    for suffix in ("-wal", "-shm", "-journal"):
        _require(not Path(str(path) + suffix).exists(), f"unexpected SQLite sidecar: {path.name}{suffix}")


def _read_only_connection(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)


def verify_sqlite(
    path: Path,
    cards: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    manifest: dict[str, Any],
    *,
    verify_write_rejection: bool = True,
) -> dict[str, Any]:
    connection = _read_only_connection(path)
    try:
        _require(connection.execute("PRAGMA application_id").fetchone()[0] == APPLICATION_ID, "application_id mismatch")
        _require(connection.execute("PRAGMA user_version").fetchone()[0] == INDEX_FORMAT_VERSION, "user_version mismatch")
        _require(connection.execute("PRAGMA page_size").fetchone()[0] == 4096, "page_size mismatch")
        _require(connection.execute("PRAGMA quick_check").fetchone()[0] == "ok", "read-only quick_check failed")
        _require(connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "read-only integrity_check failed")
        columns = tuple(item[1] for item in connection.execute("PRAGMA table_info(repository_search_rows)").fetchall())
        _require(columns == ("github_repository_id", *FTS_COLUMNS), "search-row columns mismatch")
        db_rows = [dict(zip(columns, row)) for row in connection.execute(
            f"SELECT {', '.join(columns)} FROM repository_search_rows ORDER BY github_repository_id"
        )]
        _require(db_rows == rows, "logical row parity mismatch")
        _require(logical_rows_sha256(db_rows) == manifest["logical_rows_sha256"], "logical row hash mismatch")
        _require(connection.execute("SELECT count(*) FROM repository_fts").fetchone()[0] == len(cards), "FTS row count mismatch")
        _require(connection.execute("SELECT count(*) FROM repository_classifications").fetchone()[0] == 2630,
                 "classification row count mismatch")
        metadata_cursor = connection.execute("SELECT * FROM bundle_metadata WHERE singleton = 1")
        metadata_row = metadata_cursor.fetchone()
        _require(metadata_row is not None, "missing bundle metadata")
        metadata = dict(zip((item[0] for item in metadata_cursor.description), metadata_row))
        policy, _ = load_policy()
        first_card = cards[0]
        expected_metadata = {
            "singleton": 1,
            "schema_version": "2.0.0",
            "catalog_snapshot_id": manifest["pins"]["catalog_snapshot_id"],
            "source_sha256": manifest["pins"]["source_sha256"],
            "source_schema_sha256": catalog_builder.file_sha256(SOURCE_SCHEMA),
            "taxonomy_sha256": manifest["pins"]["taxonomy_sha256"],
            "field_contract_sha256": first_card["provenance"]["frozen_pins"]["field_contract_sha256"],
            "cards_sha256": manifest["pins"]["cards_sha256"],
            "policy_sha256": manifest["pins"]["policy_sha256"],
            "card_schema_version": manifest["pins"]["card_schema_version"],
            "activity_schema_version": manifest["pins"]["activity_schema_version"],
            "retrieval_policy_version": manifest["pins"]["retrieval_policy_version"],
            "index_format_version": manifest["pins"]["index_format_version"],
            "corpus_kind": manifest["pins"]["corpus_kind"],
            "row_count": manifest["row_count"],
            "logical_rows_sha256": manifest["logical_rows_sha256"],
            "fts_columns_json": _array_text(list(FTS_COLUMNS)),
            "fts_weights_json": json.dumps(policy["field_weights"], ensure_ascii=False, separators=(",", ":")),
            "tokenizer": policy["tokenizer"],
            "normalization": policy["normalization"],
        }
        _require(metadata == expected_metadata, "SQLite bundle metadata/pin mismatch")

        alias_id = connection.execute(
            "SELECT rowid FROM repository_fts WHERE repository_fts MATCH ?",
            ('full_name_aliases : "alist-org/alist"',),
        ).fetchone()
        _require(alias_id == (323965659,), f"alias smoke mismatch: {alias_id}")
        description_ids = {row[0] for row in connection.execute(
            "SELECT rowid FROM repository_fts WHERE repository_fts MATCH ?",
            ('catalog_description : "document based question answering"',),
        ).fetchall()}
        _require(691347156 in description_ids, "catalog-description smoke did not find 1Panel-dev/MaxKB")
        weighted = connection.execute(
            "SELECT bm25(repository_fts, 5, 5, 3, 3, 3, 1, 3, 3, 2) "
            "FROM repository_fts WHERE repository_fts MATCH ? LIMIT 1",
            ('catalog_description : "document based question answering"',),
        ).fetchone()
        _require(weighted is not None and isinstance(weighted[0], float), "weighted BM25 smoke failed")

        if verify_write_rejection:
            try:
                connection.execute("DELETE FROM repository_search_rows WHERE github_repository_id = -1")
            except sqlite3.OperationalError as error:
                _require("readonly" in str(error).casefold(), f"unexpected read-only error: {error}")
            else:
                raise PluginSearchIndexBuildError("immutable read-only connection accepted a write")
    finally:
        connection.close()
    return {
        "rows": len(rows),
        "classifications": 2630,
        "alias_search_github_repository_id": 323965659,
        "catalog_description_search_github_repository_id": 691347156,
        "sqlite_version": sqlite3.sqlite_version,
        "read_only_write_rejected": verify_write_rejection,
    }


def _manifest(
    snapshot: dict[str, Any],
    policy: dict[str, Any],
    cards_sha256: str,
    policy_sha256: str,
    index_sha256: str,
    logical_sha256: str,
    built_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "pins": {
            "catalog_snapshot_id": snapshot["catalog_snapshot_id"],
            "source_sha256": snapshot["source_sha256"],
            "cards_sha256": cards_sha256,
            "index_sha256": index_sha256,
            "policy_sha256": policy_sha256,
            "taxonomy_sha256": snapshot["taxonomy_sha256"],
            "card_schema_version": snapshot["schema_version"],
            "activity_schema_version": snapshot["activity_schema_version"],
            "index_format_version": INDEX_FORMAT_VERSION,
            "retrieval_policy_version": policy["schema_version"],
            "corpus_kind": snapshot["corpus_kind"],
        },
        "builder_version": catalog_builder.BUILDER_VERSION,
        "sqlite_version": sqlite3.sqlite_version,
        "built_at": built_at,
        "source_snapshot_date": snapshot["source_snapshot_date"],
        "row_count": len(snapshot["cards"]),
        "index_file": INDEX.name,
        "cards_file": CARDS.name,
        "policy_file": PACKAGED_POLICY.name,
        "contains_project_context": False,
        "read_only_runtime": True,
        "logical_rows_sha256": logical_sha256,
    }


def build_package(*, built_at: str | None = None) -> dict[str, Any]:
    snapshot, catalog_report = catalog_builder.build_snapshot()
    policy, policy_bytes = load_policy()
    cards_bytes = catalog_builder.canonical_bytes(snapshot)
    rows = logical_rows(snapshot["cards"])
    logical_sha256 = logical_rows_sha256(rows)
    cards_sha256 = _sha256(cards_bytes)
    policy_sha256 = _sha256(policy_bytes)
    built_at = built_at or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    staging_parent = ROOT / ".codex-tmp"
    staging_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cp06-package-", dir=staging_parent) as directory:
        staging = Path(directory)
        staged_cards = staging / CARDS.name
        staged_policy = staging / PACKAGED_POLICY.name
        staged_index = staging / INDEX.name
        staged_manifest = staging / MANIFEST.name
        staged_cards.write_bytes(cards_bytes)
        staged_policy.write_bytes(policy_bytes)
        build_sqlite(
            staged_index,
            snapshot["cards"],
            rows,
            snapshot,
            policy,
            cards_sha256,
            policy_sha256,
            logical_sha256,
        )
        index_sha256 = _sha256(staged_index.read_bytes())
        manifest = _manifest(
            snapshot,
            policy,
            cards_sha256,
            policy_sha256,
            index_sha256,
            logical_sha256,
            built_at,
        )
        staged_manifest.write_bytes(catalog_builder.canonical_bytes(manifest))
        verify_sqlite(staged_index, snapshot["cards"], rows, manifest)

        ASSETS.mkdir(parents=True, exist_ok=True)
        for staged, output in (
            (staged_cards, CARDS),
            (staged_policy, PACKAGED_POLICY),
            (staged_index, INDEX),
            (staged_manifest, MANIFEST),
        ):
            os.replace(staged, output)

    return {
        "status": "ok",
        "mode": "written",
        **catalog_report,
        "cards_sha256": cards_sha256,
        "policy_sha256": policy_sha256,
        "index_sha256": index_sha256,
        "logical_rows_sha256": logical_sha256,
        "index_bytes": INDEX.stat().st_size,
        "sqlite_version": sqlite3.sqlite_version,
    }


def check_package() -> dict[str, Any]:
    snapshot, catalog_report = catalog_builder.build_snapshot()
    expected_cards = catalog_builder.canonical_bytes(snapshot)
    _require(CARDS.exists() and CARDS.read_bytes() == expected_cards, "catalog snapshot byte parity failed")
    policy, policy_bytes = load_policy()
    _require(PACKAGED_POLICY.exists() and PACKAGED_POLICY.read_bytes() == policy_bytes,
             "packaged policy is not byte-identical to accepted source")
    _require(INDEX.exists() and MANIFEST.exists(), "missing CP-06 package artifact")
    manifest = _load_json(MANIFEST)
    rows = logical_rows(snapshot["cards"])
    expected_pins = {
        "catalog_snapshot_id": snapshot["catalog_snapshot_id"],
        "source_sha256": snapshot["source_sha256"],
        "cards_sha256": _sha256(expected_cards),
        "index_sha256": _sha256(INDEX.read_bytes()),
        "policy_sha256": _sha256(policy_bytes),
        "taxonomy_sha256": snapshot["taxonomy_sha256"],
        "card_schema_version": "2.0.0",
        "activity_schema_version": "2.0.0",
        "index_format_version": 2,
        "retrieval_policy_version": "2.0.0",
        "corpus_kind": "catalog_snapshot",
    }
    _require(manifest.get("schema_version") == "2.0.0", "manifest version mismatch")
    _require(manifest.get("pins") == expected_pins, "manifest pin mismatch")
    _require(manifest.get("row_count") == 2500, "manifest row count mismatch")
    _require(manifest.get("logical_rows_sha256") == logical_rows_sha256(rows), "manifest logical hash mismatch")
    verification = verify_sqlite(INDEX, snapshot["cards"], rows, manifest)
    return {
        "status": "ok",
        "mode": "checked",
        **catalog_report,
        **verification,
        "cards_sha256": expected_pins["cards_sha256"],
        "policy_sha256": expected_pins["policy_sha256"],
        "index_sha256": expected_pins["index_sha256"],
        "logical_rows_sha256": manifest["logical_rows_sha256"],
        "index_bytes": INDEX.stat().st_size,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify checked-in cards/index/manifest/policy")
    parser.add_argument("--built-at", help="explicit RFC3339 UTC build timestamp for reproducible packaging")
    args = parser.parse_args(argv)
    report = check_package() if args.check else build_package(built_at=args.built_at)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (catalog_builder.PluginCatalogBuildError, PluginSearchIndexBuildError, sqlite3.Error) as error:
        print(f"CP-06 index build failed: {error}", file=sys.stderr)
        raise SystemExit(1)
