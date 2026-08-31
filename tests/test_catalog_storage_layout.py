"""Current source/evidence and fresh-run behavior without retired task packages."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import enrich_catalog as enrichment
import build_catalog as legacy_builder


class StorageLayoutTests(unittest.TestCase):
    def test_legacy_generation_preserves_custom_ignore_rules_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.gitignore'
            original = b'# User-owned rules\r\n.codex-tmp/\r\n/work/\r\nlocal-only/\r\n'
            path.write_bytes(original)
            with patch.object(legacy_builder, 'ROOT', Path(directory)):
                legacy_builder.write_gitignore()
            self.assertEqual(path.read_bytes(), original)

    def test_fresh_cli_plan_uses_current_taxonomy_and_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / 'run'
            with patch.object(sys, 'argv', ['enrich_catalog.py', 'plan', '--run-dir', str(run)]), contextlib.redirect_stdout(io.StringIO()):
                enrichment.main()
            plan = enrichment.load(run / 'plan.json')
            self.assertEqual(Path(plan['pins']['taxonomy.json']['origin']), ROOT / 'specs/catalog/taxonomy.yaml')
            self.assertEqual(enrichment.Collector(run).verify()['verifiedRecords'], 0)

    def test_canonical_evidence_resolves_to_retained_public_records(self):
        manifest = enrichment.load(ROOT / 'data/catalog_manifest.json')
        checked = 0
        for repo in manifest['repositories']:
            reference = repo.get('provenance', {}).get('evidenceArtifact')
            if not reference:
                continue
            path = (ROOT / reference).resolve()
            self.assertTrue(path.is_relative_to(ROOT / 'data/catalog-evidence'))
            record = enrichment.load(path)
            self.assertEqual(record['sourceId'], repo['id'])
            self.assertEqual(record['values']['githubRepositoryId'], repo['githubRepositoryId'])
            self.assertEqual(record['values']['stars'], repo['stars'])
            checked += 1
        self.assertGreater(checked, 0)
        self.assertTrue((ROOT / manifest['enrichment']['verifiedReplacement']['evidenceRun'] / 'replacement-decision.json').is_file())


if __name__ == '__main__':
    unittest.main()
