"""Tokenizer ID correction and batching; model quality is measured separately."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'configured_test', ROOT / 'evals/plugin-v1/run_flashrank_configured.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class NativeTokenizer:
    def __init__(self):
        from tokenizers import Tokenizer, models
        self.value = Tokenizer(models.WordPiece(vocab={'[UNK]': 0, 'search': 1}, unk_token='[UNK]'))


class ConfiguredTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('tokenizers'), 'optional native backend; use isolated CP-04 environment')
    def test_native_token_id_changes_to_pinned_vocab(self):
        tokenizer = NativeTokenizer().value
        corrected = runner.correct_tokenizer(tokenizer, {'[UNK]': 0, 'other': 1, 'search': 2}, 3)
        self.assertEqual(corrected.token_to_id('search'), 2)
        self.assertEqual(corrected.get_vocab_size(), 3)

    @unittest.skipUnless(importlib.util.find_spec('tokenizers'), 'optional native backend; use isolated CP-04 environment')
    def test_mismatched_or_noncontiguous_vocab_rejected(self):
        for vocabulary, size in [({'[UNK]': 0, 'search': 1}, 3),
                                 ({'[UNK]': 0, 'search': 3}, 2)]:
            with self.subTest(vocabulary=vocabulary), self.assertRaises(ValueError):
                runner.correct_tokenizer(NativeTokenizer().value, vocabulary, size)

    def test_batch_cap_keeps_all_passages(self):
        class Request:
            def __init__(self, query, passages):
                self.query, self.passages = query, passages
        class Ranker:
            def __init__(self): self.counts = []
            def rerank(self, request):
                self.counts.append(len(request.passages))
                return [dict(p, score=.5) for p in request.passages]
        ranker = Ranker()
        rows = runner.rank_batches(ranker, Request, 'search', [{'id': i} for i in range(19)], 8)
        self.assertEqual(ranker.counts, [8, 8, 3])
        self.assertEqual([r['id'] for r in rows], list(range(19)))


if __name__ == '__main__': unittest.main()
