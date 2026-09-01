"""CP-06 SQLite FTS5 package and logical-parity tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts" / "build_plugin_search_index.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_plugin_search_index_cp06", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PluginSearchIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.snapshot = json.loads(cls.builder.CARDS.read_text(encoding="utf-8"))
        cls.manifest = json.loads(cls.builder.MANIFEST.read_text(encoding="utf-8"))
        cls.rows = cls.builder.logical_rows(cls.snapshot["cards"])

    def connection(self):
        return self.builder._read_only_connection(self.builder.INDEX)

    def test_package_check_rebuilds_logical_content_and_passes(self):
        report = self.builder.check_package()
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["rows"], 2500)
        self.assertEqual(report["classifications"], 2630)
        self.assertTrue(report["read_only_write_rejected"])

    def test_manifest_pins_exact_package_bytes_and_v2_tuple(self):
        pins = self.manifest["pins"]
        self.assertEqual(self.manifest["schema_version"], "2.0.0")
        self.assertEqual(pins["card_schema_version"], "2.0.0")
        self.assertEqual(pins["activity_schema_version"], "2.0.0")
        self.assertEqual(pins["retrieval_policy_version"], "2.0.0")
        self.assertEqual(pins["index_format_version"], 2)
        self.assertEqual(pins["cards_sha256"], self.builder._sha256(self.builder.CARDS.read_bytes()))
        self.assertEqual(pins["policy_sha256"], self.builder._sha256(self.builder.PACKAGED_POLICY.read_bytes()))
        self.assertEqual(pins["index_sha256"], self.builder._sha256(self.builder.INDEX.read_bytes()))
        self.assertEqual(self.builder.PACKAGED_POLICY.read_bytes(), self.builder.POLICY_SOURCE.read_bytes())

    def test_sqlite_contract_rows_and_logical_hash_are_exact(self):
        connection = self.connection()
        try:
            self.assertEqual(connection.execute("PRAGMA application_id").fetchone()[0], self.builder.APPLICATION_ID)
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 2)
            self.assertEqual(connection.execute("PRAGMA page_size").fetchone()[0], 4096)
            self.assertEqual(connection.execute("PRAGMA quick_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            columns = tuple(item[1] for item in connection.execute(
                "PRAGMA table_info(repository_search_rows)"
            ).fetchall())
            self.assertEqual(columns, ("github_repository_id", *self.builder.FTS_COLUMNS))
            rows = [dict(zip(columns, row)) for row in connection.execute(
                f"SELECT {', '.join(columns)} FROM repository_search_rows ORDER BY github_repository_id"
            )]
            self.assertEqual(rows, self.rows)
            self.assertEqual(self.builder.logical_rows_sha256(rows), self.manifest["logical_rows_sha256"])
            self.assertEqual(connection.execute("SELECT count(*) FROM repository_search_rows").fetchone()[0], 2500)
            self.assertEqual(connection.execute("SELECT count(*) FROM repository_fts").fetchone()[0], 2500)
            self.assertEqual(connection.execute("SELECT count(*) FROM repository_classifications").fetchone()[0], 2630)
        finally:
            connection.close()

    def test_alias_and_catalog_description_searches_are_field_specific(self):
        connection = self.connection()
        try:
            alias_ids = {row[0] for row in connection.execute(
                "SELECT rowid FROM repository_fts WHERE repository_fts MATCH ?",
                ('full_name_aliases : "alist-org/alist"',),
            )}
            self.assertIn(323965659, alias_ids)
            description_ids = {row[0] for row in connection.execute(
                "SELECT rowid FROM repository_fts WHERE repository_fts MATCH ?",
                ('catalog_description : "document based question answering"',),
            )}
            upstream_ids = {row[0] for row in connection.execute(
                "SELECT rowid FROM repository_fts WHERE repository_fts MATCH ?",
                ('upstream_description : "document based question answering"',),
            )}
            self.assertIn(691347156, description_ids)
            self.assertNotIn(691347156, upstream_ids)
        finally:
            connection.close()

    def test_policy_weights_follow_exact_fts_column_order(self):
        policy = json.loads(self.builder.POLICY_SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(tuple(policy["field_weights"]), self.builder.FTS_COLUMNS)
        self.assertEqual(tuple(policy["field_weights"].values()), (5.0, 5.0, 3.0, 3.0, 3.0, 1.0, 3.0, 3.0, 2.0))

    def test_immutable_connection_rejects_write(self):
        connection = self.connection()
        try:
            with self.assertRaisesRegex(sqlite3.OperationalError, "readonly"):
                connection.execute("DELETE FROM repository_search_rows WHERE github_repository_id = -1")
        finally:
            connection.close()

    def test_content_drift_fails_fts_integrity_check(self):
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "catalog.search.sqlite"
            shutil.copyfile(self.builder.INDEX, changed)
            connection = sqlite3.connect(changed)
            try:
                connection.execute("DELETE FROM repository_search_rows WHERE github_repository_id = 323965659")
                connection.commit()
                with self.assertRaises(sqlite3.DatabaseError):
                    connection.execute("INSERT INTO repository_fts(repository_fts, rank) VALUES ('integrity-check', 1)")
            finally:
                connection.close()

    def test_corrupt_index_is_rejected_without_rebuild(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupt = Path(directory) / "catalog.search.sqlite"
            raw = self.builder.INDEX.read_bytes()
            corrupt.write_bytes(raw[: len(raw) // 2])
            with self.assertRaises((sqlite3.DatabaseError, self.builder.PluginSearchIndexBuildError)):
                self.builder.verify_sqlite(corrupt, self.snapshot["cards"], self.rows, self.manifest)
        self.assertEqual(self.builder.INDEX.read_bytes(), raw)

    def test_no_sqlite_sidecars_or_legacy_metadata_sidecar_are_packaged(self):
        for suffix in ("-wal", "-shm", "-journal"):
            self.assertFalse(Path(str(self.builder.INDEX) + suffix).exists())
        self.assertFalse((ROOT / "data" / "plugin_catalog_metadata.json").exists())


if __name__ == "__main__":
    unittest.main()
