"""Development-only FlashRank selection; canonical C9 retrieval is unchanged.

Preparation downloads only public model artifacts after explicit owner approval.
Capture uses local hashed files, exposed development cases and unchanged C9.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import platform
import re
import statistics
import sys
import time
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[2]
MODEL = 'ms-marco-MultiBERT-L-12'
MODEL_FILE = 'flashrank-MultiBERT-L12_Q.onnx'
MODEL_FILES = {MODEL_FILE, 'config.json', 'tokenizer_config.json',
               'special_tokens_map.json', 'tokenizer.json', 'vocab.txt'}
FLASHRANK_VERSION = '0.2.10'
CACHE = ROOT / 'work/cp04-flashrank-models'
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-flashrank-2026-10-08/development-v2'
RU_GOALS = [
    'Сравнить инструменты регрессионного тестирования браузеров Chromium, Firefox и WebKit.',
    'Проверить приложение React Native интеграционными тестами или API автоматизации мобильных приложений.',
    'Выбрать коллекцию готовых компонентов React для веб-приложения; отличать компоненты от иконок и инструментов разработки.',
    'Внедрить разработку, документирование и тестирование UI-компонентов в изоляции.',
    'Модернизировать HTTP API на Go с помощью веб-фреймворка или модульного маршрутизатора.',
    'Сравнить веб-фреймворки .NET, включая готовый каркас корпоративного приложения.',
    'Возобновлять прерванную загрузку больших файлов с помощью протокола передачи, а не файлового менеджера.',
    'Добавить браузерный JavaScript-компонент загрузки файлов, желательно с интеграцией React.',
    'Извлекать EXIF и медиатеги локальных изображений, аудио и видео; исключить каталоги хранилищ аналитических данных.',
    'Выбрать библиотеку оптимизации инвестиционного портфеля для количественных исследований; отличать бюджетирование и подключение к брокеру.',
]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def shared():
    spec = importlib.util.spec_from_file_location(
        'flashrank_shared_v3', ROOT / 'evals/plugin-v1/run_query_variants_v3.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public_text(card):
    """Project only owned public search fields; never serialize a private Brief."""
    values = [card['identity']['full_name'], *card['identity']['full_name_aliases'],
              card['descriptions']['upstream'], card['descriptions']['catalog'],
              *card['repository']['topics'],
              *(item['title'] for item in card['classifications']),
              *card['advisory']['use_cases'], card['advisory']['integration_surface'],
              *card['advisory']['best_for']]
    return '\n'.join(value for value in values if isinstance(value, str) and value)


def rerank_pool(result, by_id, query, backend):
    """Validate complete permutation and scores; preserve all raw C9 evidence."""
    policy = json.loads((ROOT / 'specs/retrieval/retrieval-policy.json').read_text(encoding='utf-8'))
    require(isinstance(query, str) and query.strip() and
            len(query.encode('utf-8')) <= policy['limits']['max_request_bytes'], 'query budget')
    require(result['status'] in {'ok', 'no_match'}, 'unavailable retrieval')
    ids = [item['github_repository_id'] for item in result['candidates']]
    require(len(ids) <= policy['limits']['max_retrieved_hits'] and
            all(type(i) is int and i > 0 and i in by_id for i in ids) and
            len(ids) == len(set(ids)), 'invalid fetched identity set')
    require((result['status'] == 'no_match') == (not ids), 'status/pool mismatch')
    require(all(by_id[i]['identity']['github_repository_id'] == i for i in ids), 'card identity mismatch')
    passages = [{'id': i, 'text': public_text(by_id[i])} for i in ids]
    expected = {p['id']: p['text'] for p in passages}
    # FlashRank mutates passages by adding scores and sorting; isolate its inputs.
    rows = backend.rank(query, copy.deepcopy(passages)) if passages else []
    require(isinstance(rows, list) and len(rows) == len(ids), 'incomplete model permutation')
    scores = {}
    for row in rows:
        require(isinstance(row, dict) and type(row.get('id')) is int and
                row['id'] in expected and row['id'] not in scores, 'model identity mismatch')
        require(row.get('text') == expected[row['id']], 'model public projection changed')
        score = row.get('score')
        require(type(score) in (int, float) and math.isfinite(score), 'invalid model score')
        scores[row['id']] = float(score)
    return {'transport': 'experimental_selection_adapter', 'executed_c9_rrf': False,
            'ranked_ids': sorted(ids, key=lambda i: (-scores[i], i)),
            'scores': {str(i): scores[i] for i in ids},
            'projection_sha256': digest(passages), 'query_sha256': digest(query),
            'promotion_ready': False}


def write_json(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def public_get(url, target, limit):
    """GET-only public artifact retrieval; fixed callers, no auth or private inputs."""
    request = urllib.request.Request(url, headers={'User-Agent': 'StackGuide-CP04-public-model-pilot'})
    with urllib.request.urlopen(request, timeout=60) as response, target.open('xb') as stream:
        total = 0
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            require(total <= limit, 'public artifact byte ceiling')
            stream.write(chunk)


def unpack_model_archive(archive, destination):
    """Validate all paths, but extract only the six model files, not Mac metadata."""
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        require(sum(e.file_size for e in entries) <= 256 * 1024 * 1024, 'unpacked model ceiling')
        for entry in entries:
            relative = Path(entry.filename)
            require(not relative.is_absolute() and '..' not in relative.parts and
                    relative.parts and relative.parts[0] in {MODEL, '__MACOSX'} and
                    '\\' not in entry.filename and ':' not in entry.filename and
                    (entry.external_attr >> 16) & 0o170000 != 0o120000, 'unsafe model archive')
        selected = [e for e in entries if e.filename in {f'{MODEL}/{name}' for name in MODEL_FILES}]
        require(len(selected) == len(MODEL_FILES) and len({e.filename for e in selected}) == len(selected),
                'incomplete or duplicate model archive')
        for entry in selected:
            target = destination / entry.filename
            require(target.resolve().is_relative_to(destination.resolve()), 'model extraction escape')
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(entry) as source, target.open('xb') as stream:
                while chunk := source.read(1024 * 1024):
                    stream.write(chunk)


def prepare_model():
    """Explicit setup only: pin HF revision and safely unpack a bounded model zip."""
    CACHE.mkdir(parents=True, exist_ok=True)
    require(not (CACHE / 'model-receipt.json').exists(), 'model already prepared')
    # A complete archive may be reused after a setup-only extraction failure.
    if not (CACHE / 'upstream-metadata.json').exists():
        public_get('https://huggingface.co/api/models/prithivida/flashrank',
                   CACHE / 'upstream-metadata.json', 1024 * 1024)
    metadata = json.loads((CACHE / 'upstream-metadata.json').read_text(encoding='utf-8'))
    revision = metadata['sha']
    require(re.fullmatch(r'[a-f0-9]{40}', revision) is not None, 'invalid upstream revision')
    url = f'https://huggingface.co/prithivida/flashrank/resolve/{revision}/{MODEL}.zip'
    archive = CACHE / f'{MODEL}.zip'
    if not archive.exists():
        public_get(url, archive, 192 * 1024 * 1024)
    require(archive.stat().st_size <= 192 * 1024 * 1024, 'archive size ceiling')
    unpack_model_archive(archive, CACHE)
    directory = CACHE / MODEL
    require((directory / MODEL_FILE).is_file(), 'missing ONNX model')
    receipt = {'schema_version': 'cp04_model_receipt_v1', 'model': MODEL,
               'source_url': url, 'repository_revision': revision,
               'observed_at': datetime.now(timezone.utc).isoformat(),
               'upstream_license': metadata.get('cardData', {}).get('license'),
               'license_scope': 'upstream model repository metadata; not adoption approval',
               'archive_sha256': file_hash(archive),
               'files': {p.relative_to(directory).as_posix(): file_hash(p)
                         for p in sorted(directory.rglob('*')) if p.is_file()}}
    with (CACHE / 'model-receipt.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, sort_keys=True, indent=2)
    return receipt


def model_receipt():
    receipt = json.loads((CACHE / 'model-receipt.json').read_text(encoding='utf-8'))
    require(receipt['model'] == MODEL and MODEL_FILE in receipt['files'], 'model receipt mismatch')
    actual = {p.relative_to(CACHE / MODEL).as_posix(): file_hash(p)
              for p in sorted((CACHE / MODEL).rglob('*')) if p.is_file()}
    require(actual == receipt['files'], 'local model file hash drift')
    return receipt


class FlashRankBackend:
    """Existing library, with automatic downloading disabled at inference time."""
    def __init__(self):
        require(importlib.metadata.version('FlashRank') == FLASHRANK_VERSION, 'FlashRank version drift')
        model_receipt()
        from flashrank import Ranker, RerankRequest

        class LocalRanker(Ranker):
            def _prepare_model_dir(self, model_name):
                require((self.model_dir / MODEL_FILE).is_file(), 'model unavailable; no automatic download')

        self.request = RerankRequest
        self.ranker = LocalRanker(model_name=MODEL, cache_dir=str(CACHE), max_length=512)

    def rank(self, query, passages):
        rows = self.ranker.rerank(self.request(query=query, passages=passages))
        # ONNX returns NumPy scalar scores; normalize only at the library seam.
        return [dict(row, score=float(row['score'])) for row in rows]


def declaration(base, plan, cases):
    paths = set(base.source_hashes(plan)) | {
        'evals/plugin-v1/run_flashrank_development.py',
        'evals/plugin-v1/flashrank-development-contract.md',
        'tests/test_plugin_flashrank_development.py',
    }
    packages = dict(sorted((dist.metadata['Name'], dist.version)
                           for dist in importlib.metadata.distributions()))
    return {'schema_version': 'cp04_flashrank_declaration_v1',
            'source_hashes': {p: file_hash(ROOT / p) for p in sorted(paths)},
            'pins': plan['pins'], 'thresholds': plan['thresholds'],
            'cases': [{'case_id': c['case_id'], 'case_sha256': digest(c),
                       'en_query': c['user_goal'], 'ru_query': RU_GOALS[n]}
                      for n, c in enumerate(cases)],
            'model_receipt': model_receipt(), 'packages': packages,
            'python': sys.version, 'platform': platform.platform(),
            'method': 'unchanged single-OR FTS pool; public fields; complete score-desc ID-asc permutation; 512-token pair limit',
            'held_out': 'not_run; exposed development only', 'promotion_ready': False}


def capture(base, plan, cases, cards, by_id, members, declared):
    require(not any((OUTPUT / n).exists() for n in ('observations.json', 'summary.json')), 'capture already exists')
    import psutil
    process = psutil.Process()
    start = time.perf_counter()
    backend = FlashRankBackend()
    startup_ms = (time.perf_counter() - start) * 1000
    historical = json.loads((ROOT / 'evals/plugin-v1/results/cp04-v2-2026-10-08/development-observations.json').read_text(encoding='utf-8'))
    prior = {c['case_id']: c for c in historical['captures']}
    run_id = str(uuid.uuid4())
    records, captures, latencies = [], [], []
    for n, case in enumerate(cases):
        query = base.old.make_query(plan, case)
        detail, control = base.execute(query, plan, by_id, case, 'flashrank-control', run_id)
        raw = copy.deepcopy(detail['retrieval'])
        row = {'case_id': case['case_id'], 'control': control}
        selections = {}
        for locale, goal in (('en', case['user_goal']), ('ru', RU_GOALS[n])):
            start = time.perf_counter()
            selection = rerank_pool(raw, by_id, goal, backend)
            elapsed = (time.perf_counter() - start) * 1000
            latencies.append(elapsed)
            pack = base.old.baseline_pack(query, selection['ranked_ids'], by_id, plan, run_id)
            observation = base.observe(selection['ranked_ids'], pack, case, raw['status'])
            row['candidate' if locale == 'en' else 'candidate_ru'] = observation
            selection.update({'evidence_pack': pack, 'query_language': locale,
                              'elapsed_ms': elapsed, 'controlled_input_bytes':
                              len(canonical(query)) + len(canonical(pack)) + len(goal.encode('utf-8'))})
            policy = base.scorer.load_json(ROOT / plan['artifacts']['policy_path'])
            require(selection['controlled_input_bytes'] <= policy['limits']['max_plugin_input_bytes'], 'input byte cap')
            selections[locale] = selection
        ids = base.old.baseline_ids(plan, case, cards, members)
        pack = base.old.baseline_pack(query, ids, by_id, plan, run_id)
        row['baseline'] = base.observe(ids, pack, case, 'ok' if ids else 'no_match')
        row['historical_control_equivalent'] = base.equivalence_projection(raw, detail['evidence_pack']) == base.equivalence_projection(prior[case['case_id']]['retrieval'], prior[case['case_id']]['candidate_evidence_pack'])
        row['historical_literal_equivalent'] = ids == prior[case['case_id']]['baseline_ranked_ids']
        require(raw == detail['retrieval'], 'raw C9 mutation')
        records.append(row)
        captures.append({'case_id': case['case_id'], 'control': detail, 'selection': selections,
                         'literal_baseline_ids': ids, 'literal_evidence_pack': pack})
        print(json.dumps({'case_id': case['case_id'], 'inference_ms_en_ru': [selections[l]['elapsed_ms'] for l in ('en', 'ru')]}), flush=True)
    require(declared == declaration(base, plan, cases), 'source/model/environment drift')
    summary = base.summarize(plan, records)
    ru_records = [dict(r, candidate=r['candidate_ru']) for r in records]
    summary['russian_goal_comparison'] = base.summarize(plan, ru_records)
    summary['development_candidate_worth_heldout_review'] = (
        summary['development_candidate_worth_heldout_review'] and
        summary['russian_goal_comparison']['development_candidate_worth_heldout_review'])
    summary['verdict'] = 'development_candidate_only' if summary['development_candidate_worth_heldout_review'] else 'development_no_go'
    summary['schema_version'] = 'cp04_flashrank_summary_v1'
    summary['resources'] = {'model_startup_ms': startup_ms,
                            'inference_samples': len(latencies),
                            'inference_median_ms': statistics.median(latencies),
                            'inference_p95_ms': sorted(latencies)[math.ceil(.95 * len(latencies)) - 1],
                            'peak_working_set_bytes': process.memory_info().peak_wset,
                            'method': 'single process Windows peak working set including model; 20 sequential case/locale durations, not repeated capacity acceptance',
                            'resource_acceptance': False}
    write_json('observations.json', {'schema_version': 'cp04_flashrank_observation_v1',
               'run_id': run_id, 'declaration_sha256': digest(declared), 'records': records,
               'captures': captures, 'promotion_ready': False})
    write_json('summary.json', summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare-model', action='store_true')
    mode.add_argument('--predeclare', action='store_true')
    mode.add_argument('--run-development', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.prepare_model:
            receipt = prepare_model()
            print(json.dumps({'status': 'model_prepared', 'revision': receipt['repository_revision'],
                              'license': receipt['upstream_license']}))
            return 0
        base = shared()
        plan, cases, cards, by_id, members = base.load_inputs()
        declared = declaration(base, plan, cases)
        if args.predeclare:
            write_json('declaration.json', declared)
            print(json.dumps({'status': 'predeclared', 'sha256': digest(declared)}))
            return 0
        saved = json.loads((OUTPUT / 'declaration.json').read_text(encoding='utf-8'))
        require(saved == declared, 'declaration drift')
        summary = capture(base, plan, cases, cards, by_id, members, saved)
        print(json.dumps({key: summary[key] for key in ('verdict', 'macro', 'failed_gates', 'resources')}))
        return 0 if summary['development_candidate_worth_heldout_review'] else 1
    except (ValueError, OSError, KeyError, TypeError, ImportError, RuntimeError, AttributeError) as error:
        print(json.dumps({'status': 'invalid_input_or_unavailable', 'error_type': type(error).__name__,
                          'message': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
