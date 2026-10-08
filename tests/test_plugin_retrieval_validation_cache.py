"""Digest-bound validation reuse must preserve the read-only retrieval boundary."""

import copy
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_plugin_retrieval import (
    INDEX_PATH,
    MANIFEST_PATH,
    POLICY_PATH,
    ROOT,
    base_query,
    execute_query,
    load_runtime_module,
)


class RetrievalValidationCacheTests(unittest.TestCase):
    def setUp(self):
        self.runtime = load_runtime_module("retrieval")
        self.manifest, _ = self.runtime._load_json_bytes(MANIFEST_PATH, max_bytes=65536)
        self.policy, _ = self.runtime._load_json_bytes(POLICY_PATH, max_bytes=65536)

    def test_repeated_retrieval_validates_once_but_hashes_every_call(self):
        query = base_query()
        run_id = "a3b53122-bdeb-46e0-98ed-67520a3fb251"
        with patch.object(self.runtime, "_validate_bundle", wraps=self.runtime._validate_bundle) as validate:
            with patch.object(self.runtime, "_sha256_file", wraps=self.runtime._sha256_file) as digest:
                first = execute_query(self.runtime, query, run_id=run_id)
                second = execute_query(self.runtime, query, run_id=run_id)
        self.assertEqual(first["status"], "ok")
        self.assertEqual(first, second)
        self.assertEqual(digest.call_count, 2, "every request must hash physical index bytes")
        self.assertEqual(validate.call_count, 1, "identical trusted bytes should reuse successful full validation")

    def test_changed_and_corrupt_index_fail_after_cache_fill(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            index_path = Path(directory) / "copied.sqlite"
            original = INDEX_PATH.read_bytes()
            index_path.write_bytes(original)
            self.assertEqual(execute_query(self.runtime, base_query(), index_path=index_path)["status"], "ok")
            with closing(sqlite3.connect(index_path)) as connection:
                connection.execute("PRAGMA user_version = 999")
            changed = execute_query(self.runtime, base_query(), index_path=index_path)
            self.assertEqual((changed["status"], changed["reason_codes"]),
                             ("index_incompatible", ["index_incompatible"]))
            index_path.write_bytes(original[:4096])
            corrupt = execute_query(self.runtime, base_query(), index_path=index_path)
            self.assertEqual((corrupt["status"], corrupt["reason_codes"]),
                             ("retrieval_unavailable", ["index_corrupt"]))

    def test_cache_key_binds_complete_manifest_and_policy(self):
        with closing(sqlite3.connect(INDEX_PATH.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)) as connection:
            with patch.object(self.runtime, "_validate_bundle", wraps=self.runtime._validate_bundle) as validate:
                self.runtime._validate_bundle_cached(connection, self.manifest, self.policy, INDEX_PATH)
                changed_manifest = copy.deepcopy(self.manifest)
                changed_manifest["builder_version"] = "distinct-test-validation-context"
                self.runtime._validate_bundle_cached(connection, changed_manifest, self.policy, INDEX_PATH)
                changed_policy = copy.deepcopy(self.policy)
                changed_policy["calibration_status"] = "distinct-test-validation-context"
                self.runtime._validate_bundle_cached(connection, self.manifest, changed_policy, INDEX_PATH)
        self.assertEqual(validate.call_count, 3, "other fixture or policy contents cannot reuse validation")

    def test_failed_validation_is_not_cached(self):
        full_validation = self.runtime._validate_bundle
        calls = []

        def fail_first(connection, manifest, policy):
            calls.append(None)
            if len(calls) == 1:
                raise ValueError("declared validation failure")
            return full_validation(connection, manifest, policy)

        with closing(sqlite3.connect(INDEX_PATH.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)) as connection:
            with patch.object(self.runtime, "_validate_bundle", side_effect=fail_first):
                with self.assertRaisesRegex(ValueError, "declared validation failure"):
                    self.runtime._validate_bundle_cached(connection, self.manifest, self.policy, INDEX_PATH)
                self.runtime._validate_bundle_cached(connection, self.manifest, self.policy, INDEX_PATH)
                self.runtime._validate_bundle_cached(connection, self.manifest, self.policy, INDEX_PATH)
        self.assertEqual(len(calls), 2)

    def test_byte_hash_mismatch_does_not_create_a_validation_receipt(self):
        wrong_manifest = copy.deepcopy(self.manifest)
        wrong_manifest["pins"]["index_sha256"] = "0" * 64
        with closing(sqlite3.connect(INDEX_PATH.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)) as connection:
            with patch.object(self.runtime, "_validate_bundle", wraps=self.runtime._validate_bundle) as validate:
                for _ in range(2):
                    with self.assertRaisesRegex(ValueError, "index byte hash mismatch"):
                        self.runtime._validate_bundle_cached(connection, wrong_manifest, self.policy, INDEX_PATH)
        self.assertEqual(validate.call_count, 2)
        self.assertEqual(len(self.runtime._BUNDLE_VALIDATION_CACHE), 0)

    def test_cache_is_bounded_and_eviction_requires_full_validation(self):
        with closing(sqlite3.connect(INDEX_PATH.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)) as connection:
            with patch.object(self.runtime, "_validate_bundle", wraps=self.runtime._validate_bundle) as validate:
                self.runtime._validate_bundle_cached(connection, self.manifest, self.policy, INDEX_PATH)
                for number in range(self.runtime._BUNDLE_VALIDATION_CACHE_LIMIT):
                    other_manifest = copy.deepcopy(self.manifest)
                    other_manifest["builder_version"] = f"bounded-test-context-{number}"
                    self.runtime._validate_bundle_cached(connection, other_manifest, self.policy, INDEX_PATH)
                self.assertLessEqual(len(self.runtime._BUNDLE_VALIDATION_CACHE), self.runtime._BUNDLE_VALIDATION_CACHE_LIMIT)
                before = validate.call_count
                self.runtime._validate_bundle_cached(connection, self.manifest, self.policy, INDEX_PATH)
                self.assertEqual(validate.call_count, before + 1)

    def test_direct_validator_remains_uncached(self):
        with closing(sqlite3.connect(INDEX_PATH.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)) as connection:
            statements = []
            connection.set_trace_callback(statements.append)
            self.runtime._validate_bundle(connection, self.manifest, self.policy)
            self.runtime._validate_bundle(connection, self.manifest, self.policy)
        self.assertEqual(sum(sql.upper() == "PRAGMA INTEGRITY_CHECK" for sql in statements), 2)


if __name__ == "__main__":
    unittest.main()
