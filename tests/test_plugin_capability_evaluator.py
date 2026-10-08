"""A candidate fixture must be pinned before private reader/pack entry."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('capability_eval_test', ROOT / 'evals/plugin-v1/run_capability_package.py')
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


class CapabilityTrustTests(unittest.TestCase):
    def test_unpinned_receipt_rejected(self):
        with self.assertRaisesRegex(ValueError, 'receipt drift'):
            evaluator.verified_package('0' * 64)

    def test_changed_card_bytes_rejected_before_normalization(self):
        folder = evaluator.builder.OUTPUT
        receipt_sha = evaluator.builder.sha((folder / 'build-receipt.json').read_bytes())
        temporary_root = ROOT / '.codex-tmp'
        temporary_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            candidate = Path(directory) / 'candidate'
            shutil.copytree(folder, candidate)
            with (candidate / 'catalog.snapshot.json').open('ab') as stream:
                stream.write(b' ')
            with mock.patch.object(evaluator.builder, 'OUTPUT', candidate):
                with self.assertRaisesRegex(ValueError, 'package drift'):
                    evaluator.verified_package(receipt_sha)


if __name__ == '__main__':
    unittest.main()
