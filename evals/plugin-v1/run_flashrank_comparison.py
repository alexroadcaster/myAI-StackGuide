"""Bounded ready-model ablation; no canonical runtime or historical capture writes."""
from __future__ import annotations

import importlib.util
import importlib.metadata
import argparse
import copy
import json
import logging
import math
import statistics
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('comparison_previous', ROOT / 'evals/plugin-v1/run_flashrank_configured.py')
configured = importlib.util.module_from_spec(spec)
spec.loader.exec_module(configured)
previous = configured.previous
MODELS = {'tiny': ('ms-marco-TinyBERT-L-2-v2', 'flashrank-TinyBERT-L-2-v2.onnx'),
          'mini': ('ms-marco-MiniLM-L-12-v2', 'flashrank-MiniLM-L-12-v2_Q.onnx')}
CACHE = ROOT / 'work/cp04-small-models'
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-flashrank-comparison-v2-2026-10-08'
INPUTS = ['goal_plain', 'terms_plain', 'terms_labels', 'ru_goal_plain']
DEFAULTS = {'batch': 8, 'threads': 4, 'max_length': 512, 'arena': False, 'memory_pattern': False}
NATIVE_PUBLIC_TEXT = previous.public_text


def fuse_orders(first, second, k):
    """Experimental equal RRF over identical complete pools; never overwrite C9."""
    previous.require(type(k) is int and k > 0, 'invalid RRF k')
    for ids in (first, second):
        previous.require(all(type(i) is int and i > 0 for i in ids) and len(ids) == len(set(ids)),
                         'invalid fusion identity set')
    previous.require(set(first) == set(second), 'fusion pools differ')
    scores = {i: 0.0 for i in first}
    for ids in (first, second):
        for rank, i in enumerate(ids, 1):
            scores[i] += 1 / (k + rank)
    return sorted(scores, key=lambda i: (-scores[i], i))


def structured_text(card):
    """Label the same nine public fields without asserting new capabilities."""
    fields = [('Repository', card['identity']['full_name']),
              ('Historical names', card['identity']['full_name_aliases']),
              ('Upstream description', card['descriptions']['upstream']),
              ('Catalog description', card['descriptions']['catalog']),
              ('Topics', card['repository']['topics']),
              ('Categories', [c['title'] for c in card['classifications']]),
              ('Use cases', card['advisory']['use_cases']),
              ('Integration surface', card['advisory']['integration_surface']),
              ('Best for', card['advisory']['best_for'])]
    rows = []
    for label, value in fields:
        values = value if isinstance(value, list) else [value]
        text = '; '.join(v for v in values if isinstance(v, str) and v)
        if text:
            rows.append(label + ': ' + text)
    return '\n'.join(rows)


def compact_query(case):
    """Use frozen request terms; no labels, oracle values or inferred capabilities."""
    return '; '.join(case['query_terms'])


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def prepare(key):
    """Reuse the reviewed GET-only bounded wrapper with this experiment's cache."""
    name, filename = MODELS[key]
    directory = CACHE / key
    directory.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((previous.CACHE / 'upstream-metadata.json').read_text(encoding='utf-8'))
    revision = metadata['sha']
    previous.require(revision == '858a1ac046a05663a35367eac852d7f76feeefdd', 'model revision mismatch')
    url = f'https://huggingface.co/prithivida/flashrank/resolve/{revision}/{name}.zip'
    archive = directory / (name + '.zip')
    if not archive.exists():
        previous.public_get(url, archive, 64 * 1024 * 1024)
    required = {filename, 'config.json', 'tokenizer_config.json', 'special_tokens_map.json', 'tokenizer.json'}
    import zipfile
    with zipfile.ZipFile(archive) as bundle:
        if f'{name}/vocab.txt' in bundle.namelist():
            required.add('vocab.txt')
    old_model, old_files = previous.MODEL, previous.MODEL_FILES
    try:
        previous.MODEL, previous.MODEL_FILES = name, required
        previous.unpack_model_archive(archive, directory)
    finally:
        previous.MODEL, previous.MODEL_FILES = old_model, old_files
    receipt = {'model': name, 'source_url': url, 'revision': revision,
               'upstream_license': metadata.get('cardData', {}).get('license'),
               'license_scope': 'model repository metadata; not adoption approval',
               'archive_sha256': previous.file_hash(archive),
               'files': {p.name: previous.file_hash(p) for p in sorted((directory / name).iterdir()) if p.is_file()}}
    write(directory / 'model-receipt.json', receipt)
    return receipt


def receipt(key):
    name, filename = MODELS[key]
    value = json.loads((CACHE / key / 'model-receipt.json').read_text(encoding='utf-8'))
    actual = {p.name: previous.file_hash(p) for p in sorted((CACHE / key / name).iterdir()) if p.is_file()}
    previous.require(value['model'] == name and actual == value['files'] and filename in actual,
                     'model file drift')
    return value


class Backend:
    def __init__(self, key, settings):
        previous.require(importlib.metadata.version('FlashRank') == previous.FLASHRANK_VERSION, 'library drift')
        receipt(key)
        from flashrank import Ranker, RerankRequest
        import onnxruntime as ort
        name, filename = MODELS[key]
        class LocalRanker(Ranker):
            def __init__(self):
                self.logger = logging.getLogger('cp04.comparison')
                self.model_dir = CACHE / key / name
                self.llm_model = None
                options = ort.SessionOptions()
                options.intra_op_num_threads = settings['threads']
                options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                options.enable_cpu_mem_arena = settings['arena']
                options.enable_mem_pattern = settings['memory_pattern']
                self.session = ort.InferenceSession(str(self.model_dir / filename), sess_options=options,
                                                   providers=['CPUExecutionProvider'])
                self.tokenizer = self._get_tokenizer(settings['max_length'])
                config = json.loads((self.model_dir / 'config.json').read_text(encoding='utf-8'))
                previous.require(self.tokenizer.get_vocab_size() == config['vocab_size'], 'native vocabulary size mismatch')
                if (self.model_dir / 'vocab.txt').exists():
                    vocab = self._load_vocab(self.model_dir / 'vocab.txt')
                    previous.require(all(self.tokenizer.token_to_id(t) == i for t, i in vocab.items()),
                                     'native vocabulary ID mismatch; do not silently repair a new model')
                previous.require(self.tokenizer.token_to_id('[PAD]') == config['pad_token_id'] and
                                 self.tokenizer.token_to_id('[CLS]') == 101 and
                                 self.tokenizer.token_to_id('[SEP]') == 102, 'special token mismatch')
        self.ranker, self.request, self.settings = LocalRanker(), RerankRequest, settings

    def rank(self, query, passages):
        # Stable length buckets reduce dynamic-padding work and retain every ID.
        if self.settings.get('length_buckets', False):
            passages = sorted(passages, key=lambda p: (len(self.ranker.tokenizer.encode(query, p['text']).ids), p['id']))
        return [dict(r, score=float(r['score'])) for r in
                configured.rank_batches(self.ranker, self.request, query, passages, self.settings['batch'])]


def declaration(base, plan, cases):
    paths = set(base.source_hashes(plan)) | {
        'evals/plugin-v1/run_flashrank_comparison.py', 'tests/test_plugin_flashrank_comparison.py',
        'evals/plugin-v1/flashrank-comparison-contract.md',
        'evals/plugin-v1/run_flashrank_configured.py', 'evals/plugin-v1/run_flashrank_development.py',
        'evals/plugin-v1/results/cp04-flashrank-2026-10-08/configured/observations.json',
        'evals/plugin-v1/results/cp04-flashrank-2026-10-08/configured/summary.json'}
    return {'schema_version': 'cp04_ready_comparison_v1', 'promotion_ready': False,
            'sources': {p: previous.file_hash(ROOT / p) for p in sorted(paths)},
            'model_receipts': {key: receipt(key) for key in MODELS},
            'packages': dict(sorted((d.metadata['Name'], d.version) for d in importlib.metadata.distributions())),
            'settings': DEFAULTS, 'inputs': INPUTS,
            'rrf_k': base.scorer.load_json(ROOT / plan['artifacts']['policy_path'])['rank_fusion']['k'],
            'performance': {'model': 'tiny', 'input': 'terms_labels', 'repeats': 3,
                            'grid': [[4, 2, False], [8, 2, False], [4, 4, False], [8, 4, False], [8, 4, True]]},
            'cases': [{'id': c['case_id'], 'sha256': previous.digest(c), 'en': c['user_goal'],
                       'ru': previous.RU_GOALS[n], 'compact': compact_query(c)} for n, c in enumerate(cases)],
            'thresholds': plan['thresholds'], 'pins': plan['pins'],
            'method': 'same frozen EN lexical pools; goal/terms/public labels; pure and equal RRF; direct RU diagnostic; no translation execution',
            'held_out': 'not_run; exposed development only'}


def run(key, base, plan, cases, cards, by_id, members, declared, perf=None):
    import psutil
    settings = dict(DEFAULTS)
    if perf:
        settings.update(batch=perf[0], threads=perf[1], length_buckets=perf[2])
    folder = OUTPUT / (key if not perf else f'tiny-b{perf[0]}-t{perf[1]}-buckets{int(perf[2])}')
    previous.require(not folder.exists(), 'capture exists; preserve evidence')
    start = time.perf_counter()
    backend = Backend(key, settings)
    startup = (time.perf_counter() - start) * 1000
    controls = json.loads((ROOT / 'evals/plugin-v1/results/cp04-flashrank-2026-10-08/configured/observations.json').read_text(encoding='utf-8'))
    historical = {r['case_id']: r for r in controls['captures']}
    observations, arms, timings, coverage = [], {}, {}, []
    run_id = str(uuid.uuid4())
    for n, case in enumerate(cases):
        query = base.old.make_query(plan, case)
        detail, control = base.execute(query, plan, by_id, case, 'small-model-control', run_id)
        raw = detail['retrieval']
        original = historical[case['case_id']]
        previous.require(base.equivalence_projection(raw, detail['evidence_pack']) ==
                         base.equivalence_projection(original['control']['retrieval'], original['control']['evidence_pack']),
                         'historical control changed')
        ids = [c['github_repository_id'] for c in raw['candidates']]
        positives = {r['github_repository_id'] for r in case['judgments'] if r['grade'] > 0 and r['constraint'] != 'denied'}
        coverage.append({'case_id': case['case_id'], 'pool_size': len(ids), 'positive_count': len(positives),
                         'positive_in_pool': len(positives & set(ids)), 'missing_positive_ids': sorted(positives-set(ids))})
        literal_ids = base.old.baseline_ids(plan, case, cards, members)
        previous.require(literal_ids == original['literal_baseline_ids'], 'historical literal changed')
        literal_pack = base.old.baseline_pack(query, literal_ids, by_id, plan, run_id)
        baseline = base.observe(literal_ids, literal_pack, case, 'ok' if literal_ids else 'no_match')
        capture = {'case_id': case['case_id'], 'pool_ids': ids, 'selections': {}}
        for input_arm in (('terms_labels',) if perf else INPUTS):
            text = previous.RU_GOALS[n] if input_arm.startswith('ru') else (case['user_goal'] if input_arm.startswith('goal') else compact_query(case))
            projector = structured_text if input_arm.endswith('labels') else NATIVE_PUBLIC_TEXT
            previous.public_text = projector
            latencies = []
            try:
                for _ in range(3 if perf else 1):
                    start = time.perf_counter()
                    selection = previous.rerank_pool(raw, by_id, text, backend)
                    latencies.append((time.perf_counter() - start) * 1000)
            finally:
                previous.public_text = NATIVE_PUBLIC_TEXT
            token_lengths = [len(backend.ranker.tokenizer.encode(text, projector(by_id[i])).ids) for i in ids]
            # No heuristic score mixing; fusion uses ranks on exactly the same IDs.
            for kind in ('pure', 'rrf'):
                arm = input_arm + '_' + kind
                ranked = selection['ranked_ids'] if kind == 'pure' else fuse_orders(ids, selection['ranked_ids'], declared['rrf_k'])
                pack = base.old.baseline_pack(query, ranked, by_id, plan, run_id)
                previous.require(len(previous.canonical(query)) + len(previous.canonical(pack)) + len(text.encode('utf-8')) <=
                                 base.scorer.load_json(ROOT / plan['artifacts']['policy_path'])['limits']['max_plugin_input_bytes'], 'input cap')
                record = {'case_id': case['case_id'], 'control': control, 'baseline': baseline,
                          'candidate': base.observe(ranked, pack, case, raw['status']),
                          'historical_control_equivalent': True, 'historical_literal_equivalent': True}
                arms.setdefault(arm, []).append(record)
                capture['selections'][arm] = {'ranked_ids': ranked, 'pack_sha256': previous.digest(pack),
                                              'pack_ids': [c['card']['identity']['github_repository_id'] for c in pack['cards']],
                                              'observation': record['candidate'], 'inference_ms': latencies,
                                              'query_sha256': previous.digest(text),
                                              'projection_sha256': selection['projection_sha256']}
                timings.setdefault(arm, []).extend(latencies)
            capture['selections'][input_arm+'_pure'].update(scores=selection['scores'],
                                                           max_encoded_pair_tokens=max(token_lengths, default=0))
        observations.append(capture)
        print(json.dumps({'model': key, 'case': case['case_id'], 'pool': len(ids), 'last_ms': latencies}), flush=True)
    previous.require(declared == declaration(base, plan, cases), 'source/environment/model drift')
    summaries = {}
    for arm, records in arms.items():
        summary = base.summarize(plan, records)
        durations = timings[arm]
        summary['inference_median_ms'] = statistics.median(durations)
        summary['inference_p95_ms'] = sorted(durations)[math.ceil(.95*len(durations))-1]
        summaries[arm] = summary
    resources = {'startup_ms': startup, 'peak_working_set_bytes': psutil.Process().memory_info().peak_wset,
                 'capacity_acceptance': False, 'samples_per_arm': len(next(iter(timings.values()))),
                 'method': 'separate process per model/settings; complete ten pools; repeats share process; not final capacity acceptance'}
    write(folder / 'observations.json', {'declaration_sha256': previous.digest(declared), 'captures': observations,
                                        'coverage': coverage, 'promotion_ready': False})
    write(folder / 'summary.json', {'model': key, 'settings': settings, 'arms': summaries, 'resources': resources,
                                   'declaration_sha256': previous.digest(declared), 'promotion_ready': False})
    print(json.dumps({'model': key, 'resources': resources, 'quality': {a:s['macro']['candidate'] for a,s in summaries.items()}}))
    return 0  # Capture completion, not promotion acceptance; per-arm verdicts retained.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', choices=MODELS)
    parser.add_argument('--predeclare', action='store_true')
    parser.add_argument('--run', choices=MODELS)
    parser.add_argument('--perf', type=int, choices=range(5))
    args = parser.parse_args()
    previous.require(sum((bool(args.prepare), args.predeclare, bool(args.run), args.perf is not None)) == 1, 'select one action')
    if args.prepare:
        print(json.dumps(prepare(args.prepare)))
        return 0
    base = previous.shared()
    plan, cases, cards, by_id, members = base.load_inputs()
    declared = declaration(base, plan, cases)
    if args.predeclare:
        write(OUTPUT / 'declaration.json', declared)
        print(json.dumps({'predeclared': previous.digest(declared)}))
        return 0
    saved = json.loads((OUTPUT / 'declaration.json').read_text(encoding='utf-8'))
    previous.require(saved == declared, 'declaration drift')
    return run(args.run or 'tiny', base, plan, cases, cards, by_id, members, saved,
               perf=declared['performance']['grid'][args.perf] if args.perf is not None else None)


if __name__ == '__main__':
    raise SystemExit(main())
