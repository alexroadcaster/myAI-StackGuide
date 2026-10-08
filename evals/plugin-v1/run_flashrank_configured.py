"""Correct model vocabulary and bound CPU inference in a new development packet."""
from __future__ import annotations

import importlib.util
import importlib.metadata
import json
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'flashrank_previous', ROOT / 'evals/plugin-v1/run_flashrank_development.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)

CONFIG = {'tokenizer': 'WordPiece_from_pinned_vocab_txt', 'batch_size': 8,
          'intra_op_num_threads': 4, 'execution_provider': 'CPUExecutionProvider',
          'enable_cpu_mem_arena': False, 'enable_mem_pattern': False,
          'max_pair_tokens': 512}


def correct_tokenizer(tokenizer, vocabulary, expected_size):
    """Install the native WordPiece model, preserving normalization/postprocessing."""
    previous.require(len(vocabulary) == expected_size and
                     set(vocabulary.values()) == set(range(expected_size)), 'model vocabulary mismatch')
    from tokenizers import models
    tokenizer.model = models.WordPiece(vocab=vocabulary, unk_token='[UNK]',
                                       continuing_subword_prefix='##', max_input_chars_per_word=100)
    previous.require(tokenizer.get_vocab_size() == expected_size and
                     all(tokenizer.token_to_id(token) == value for token, value in vocabulary.items()),
                     'native tokenizer ID mismatch')
    return tokenizer


def rank_batches(ranker, request_type, query, passages, batch_size):
    """Reuse FlashRank inference while bounding each ONNX input batch."""
    previous.require(type(batch_size) is int and batch_size > 0, 'invalid batch size')
    rows = []
    for offset in range(0, len(passages), batch_size):
        rows.extend(ranker.rerank(request_type(query=query, passages=passages[offset:offset + batch_size])))
    return rows


class ConfiguredBackend:
    """Retain FlashRank scoring; correct native vocabulary and explicit CPU session."""
    def __init__(self):
        previous.require(importlib.metadata.version('FlashRank') == previous.FLASHRANK_VERSION,
                         'FlashRank version drift')
        previous.model_receipt()
        from flashrank import Ranker, RerankRequest
        import onnxruntime as ort

        class LocalRanker(Ranker):
            def __init__(self):
                # Avoid creating a default large session before the configured one.
                self.logger = logging.getLogger('cp04.configured_flashrank')
                self.model_dir = previous.CACHE / previous.MODEL
                self.llm_model = None
                options = ort.SessionOptions()
                options.intra_op_num_threads = CONFIG['intra_op_num_threads']
                options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                options.enable_cpu_mem_arena = CONFIG['enable_cpu_mem_arena']
                options.enable_mem_pattern = CONFIG['enable_mem_pattern']
                self.session = ort.InferenceSession(str(self.model_dir / previous.MODEL_FILE),
                                                   sess_options=options,
                                                   providers=[CONFIG['execution_provider']])
                self.tokenizer = self._get_tokenizer(CONFIG['max_pair_tokens'])
                config = json.loads((self.model_dir / 'config.json').read_text(encoding='utf-8'))
                vocabulary = self._load_vocab(self.model_dir / 'vocab.txt')
                self.tokenizer = correct_tokenizer(self.tokenizer, vocabulary, config['vocab_size'])
                previous.require(self.tokenizer.token_to_id('[PAD]') == config['pad_token_id'] and
                                 self.tokenizer.token_to_id('[CLS]') == 101 and
                                 self.tokenizer.token_to_id('[SEP]') == 102, 'special token mismatch')

        self.request = RerankRequest
        self.ranker = LocalRanker()

    def rank(self, query, passages):
        rows = rank_batches(self.ranker, self.request, query, passages, CONFIG['batch_size'])
        return [dict(row, score=float(row['score'])) for row in rows]


original_declaration = previous.declaration


def declaration(base, plan, cases):
    value = original_declaration(base, plan, cases)
    for name in ('evals/plugin-v1/run_flashrank_configured.py',
                 'evals/plugin-v1/flashrank-configured-contract.md',
                 'tests/test_plugin_flashrank_configured.py'):
        value['source_hashes'][name] = previous.file_hash(ROOT / name)
    value['configuration'] = CONFIG
    value['method'] += '; corrected native WordPiece; bounded batches; explicit CPU session'
    return value


def main(argv=None):
    # Wire only this process's experimental harness; old files/receipts stay frozen.
    previous.OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-flashrank-2026-10-08/configured'
    previous.FlashRankBackend = ConfiguredBackend
    previous.declaration = declaration
    return previous.main(argv)


if __name__ == '__main__':
    raise SystemExit(main())
