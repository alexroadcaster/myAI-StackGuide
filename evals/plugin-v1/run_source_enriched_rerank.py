"""Composition diagnostic on exposed Kotlin regression; never a fresh held-out."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('enriched_composition', ROOT / 'evals/plugin-v1/run_source_coverage_comparison.py')
enrichment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enrichment)
comparison = enrichment.comparison
previous = comparison.previous
OUTPUT = comparison.OUTPUT / 'enriched-kotlin-rerank'


def declaration():
    paths = [
        'evals/plugin-v1/run_source_enriched_rerank.py',
        'evals/plugin-v1/run_source_coverage_comparison.py',
        'evals/plugin-v1/run_flashrank_comparison.py',
        'evals/plugin-v1/run_flashrank_configured.py',
        'evals/plugin-v1/run_flashrank_development.py',
        'evals/plugin-v1/quality-oracle-v3-source.json',
        'plugins/myai-stackguide/assets/catalog.snapshot.json',
        enrichment.FACTS.relative_to(ROOT).as_posix(),
        (enrichment.OUTPUT / 'observations.json').relative_to(ROOT).as_posix(),
        (enrichment.OUTPUT / 'declaration.json').relative_to(ROOT).as_posix()]
    oracle = json.loads((ROOT / paths[5]).read_text(encoding='utf-8'))
    case = next(c for c in oracle['cases'] if c['case_id'] == 'CP04-HV3-12')
    return {'schema_version': 'cp04_enriched_composition_v1', 'sources': {p: previous.file_hash(ROOT/p) for p in paths},
            'goal': case['user_goal'], 'model': comparison.receipt('tiny'), 'settings': comparison.DEFAULTS,
            'rrf_k': json.loads((ROOT/'specs/retrieval/retrieval-policy.json').read_text(encoding='utf-8'))['rank_fusion']['k'],
            'method': 'TinyBERT EN goal/plain projection on original versus source-enriched pools/cards; equal RRF diagnostic; exact permutations',
            'metrics': 'supported-positive coverage only; unknowns retained; no macro or promotion', 'promotion_ready': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    flags = parser.add_mutually_exclusive_group(required=True)
    flags.add_argument('--predeclare', action='store_true')
    flags.add_argument('--run', action='store_true')
    args = parser.parse_args()
    declared = declaration()
    if args.predeclare:
        comparison.write(OUTPUT / 'declaration.json', declared)
        print(json.dumps({'predeclared': previous.digest(declared)}))
        return
    previous.require(json.loads((OUTPUT/'declaration.json').read_text(encoding='utf-8')) == declared, 'declaration drift')
    previous.require(not (OUTPUT/'observations.json').exists(), 'capture exists')
    cards = json.loads((ROOT/'plugins/myai-stackguide/assets/catalog.snapshot.json').read_text(encoding='utf-8'))['cards']
    facts = json.loads(enrichment.FACTS.read_text(encoding='utf-8'))['facts']
    original = {c['identity']['github_repository_id']: c for c in cards}
    enriched = {c['identity']['github_repository_id']: c for c in enrichment.enriched_cards(cards, facts)}
    observed = json.loads((enrichment.OUTPUT/'observations.json').read_text(encoding='utf-8'))
    oracle = json.loads((ROOT/'evals/plugin-v1/quality-oracle-v3-source.json').read_text(encoding='utf-8'))
    case = next(c for c in oracle['cases'] if c['case_id']=='CP04-HV3-12')
    positives = set(case['source_supported_positive_ids'])
    backend = comparison.Backend('tiny', declared['settings'])
    results = {}
    for arm, lookup in [('before', original), ('after', enriched)]:
        pool = observed[arm+'_ids'][case['case_id']]
        passages = [{'id': i, 'text': comparison.NATIVE_PUBLIC_TEXT(lookup[i])} for i in pool]
        start = time.perf_counter()
        rows = backend.rank(declared['goal'], copy.deepcopy(passages))
        elapsed = (time.perf_counter()-start)*1000
        previous.require(len(rows)==len(pool) and {r['id'] for r in rows}==set(pool), 'model permutation mismatch')
        by_id = {r['id']: r for r in rows}
        import math
        previous.require(all(by_id[p['id']]['text']==p['text'] and math.isfinite(by_id[p['id']]['score']) for p in passages), 'model text/score drift')
        ranked = sorted(pool, key=lambda i:(-by_id[i]['score'], i))
        orders = {'fts': pool, 'neural': ranked, 'rrf': comparison.fuse_orders(pool, ranked, declared['rrf_k'])}
        results[arm] = {'inference_ms': elapsed, 'orders': orders,
                        'supported_positive_top12': {a: len(positives & set(ids[:12])) for a,ids in orders.items()},
                        'scores': {str(i): by_id[i]['score'] for i in pool},
                        'unknown_returned_count': sum(1 for r in case['judgments'] if r['relevance_grade'] is None and r['github_repository_id'] in pool)}
    previous.require(declared==declaration(), 'source/model drift')
    comparison.write(OUTPUT/'observations.json', {'declaration_sha256': previous.digest(declared), 'results': results,
                                                 'known_positive_ids': sorted(positives), 'promotion_ready': False})
    print(json.dumps({a: r['supported_positive_top12'] for a,r in results.items()}))


if __name__ == '__main__':
    main()
