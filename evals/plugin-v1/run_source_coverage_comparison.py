"""Source-qualified enrichment ablation on an in-memory copy of the public index."""
from __future__ import annotations

import copy
import importlib.util
import argparse
import json
import sqlite3
import uuid
from datetime import date
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('source_comparison', ROOT / 'evals/plugin-v1/run_flashrank_comparison.py')
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)
previous = comparison.previous
FACTS = ROOT / 'research/cp04-search-capability-enrichment-2026-10-08.json'
OUTPUT = comparison.OUTPUT / 'source-coverage-v2'


def enriched_cards(cards, facts):
    """Only enrich a copy; exact identity joins and source-qualified facts required."""
    result = copy.deepcopy(cards)
    by_id = {c['identity']['github_repository_id']: c for c in result}
    previous.require(len(by_id) == len(result), 'duplicate card IDs')
    seen = set()
    for fact in facts:
        i = fact['github_repository_id']
        previous.require(type(i) is int and i > 0 and i in by_id and i not in seen, 'fact identity mismatch')
        seen.add(i)
        previous.require(by_id[i]['identity']['full_name'] == fact['full_name'], 'fact name mismatch')
        url = urlparse(fact['source_url'])
        previous.require(url.scheme == 'https' and url.hostname and not url.username and not url.password,
                         'public HTTPS source required')
        date.fromisoformat(fact['observed_on'])
        for field in ('capability', 'scope', 'limitations'):
            previous.require(isinstance(fact[field], str) and fact[field].strip() and
                             len(fact[field].encode('utf-8')) <= 2048, 'fact field required/bounded')
        if fact['capability'] not in by_id[i]['advisory']['use_cases']:
            by_id[i]['advisory']['use_cases'].append(fact['capability'])
    return result


def declaration(base, plan, facts):
    sources = base.source_hashes(plan)
    for path in ['evals/plugin-v1/run_source_coverage_comparison.py',
                 'tests/test_plugin_source_coverage_comparison.py',
                 'evals/plugin-v1/run_flashrank_comparison.py', 'evals/plugin-v1/run_flashrank_configured.py',
                 'evals/plugin-v1/run_flashrank_development.py', 'evals/plugin-v1/flashrank-comparison-contract.md',
                 FACTS.relative_to(ROOT).as_posix(), 'scripts/build_plugin_search_index.py',
                 'evals/plugin-v1/results/cp04-v3-2026-10-08/held-out/observations.json',
                 'evals/plugin-v1/quality-oracle-v3-source.json']:
        sources[path] = previous.file_hash(ROOT / path)
    return {'schema_version': 'cp04_enrichment_comparison_v1', 'sources': sources,
            'facts_sha256': previous.digest(facts), 'pins': plan['pins'],
            'method': 'read-only immutable original copied to :memory:; use_cases only; rebuild temporary FTS; identical compiled query/route/weights/cap; packs use original pinned cards, enrichment stays separate',
            'scope': 'ten exposed development cases and one exposed Kotlin regression; no fresh held-out',
            'promotion_ready': False}


def run(base, plan, cases, cards, by_id, facts, declared):
    spec = importlib.util.spec_from_file_location('enrichment_builder', ROOT / 'scripts/build_plugin_search_index.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    policy = base.scorer.load_json(ROOT / plan['artifacts']['policy_path'])
    previous.require(tuple(policy['field_weights']) == builder.FTS_COLUMNS and
                     all(base.old.retrieval.FIELD_WEIGHTS[k] == v for k,v in policy['field_weights'].items()),
                     'canonical field projection/weight mismatch')
    source_path = ROOT / plan['artifacts']['index_path']
    source = sqlite3.connect(source_path.resolve().as_uri()+'?mode=ro&immutable=1', uri=True)
    memory = sqlite3.connect(':memory:')
    source.backup(memory)
    source.close()
    memory.row_factory = sqlite3.Row
    updated = enriched_cards(cards, facts)
    updated_by_id = {c['identity']['github_repository_id']: c for c in updated}
    old_packet = json.loads((ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08/held-out/observations.json').read_text(encoding='utf-8'))
    regression = next(c for c in old_packet['captures'] if c['case_id'] == 'CP04-HV3-12')
    queries = {c['case_id']: base.old.make_query(plan, c) for c in cases}
    queries['CP04-HV3-12'] = regression['query']
    def search(query):
        previous.require(len(query['variants']) == 1, 'single variant diagnostic only')
        expression = base.old.retrieval.compile_fts5_query(query['variants'][0]['terms'], aliases=policy['aliases'])
        return [r['github_repository_id'] for r in base.old.retrieval._execute_variant(
            memory, expression, query['taxonomy_route_id'], query['max_candidates'])]
    before = {key: search(q) for key,q in queries.items()}
    previous.require(before['CP04-HV3-12'] == [r['github_repository_id'] for r in regression['control']['retrieval']['candidates']],
                     'temporary baseline differs from frozen production retrieval')
    for fact in facts:
        i = fact['github_repository_id']
        row = builder.project_card(updated_by_id[i])
        memory.execute('UPDATE repository_search_rows SET use_cases=? WHERE github_repository_id=?', (row['use_cases'], i))
    memory.execute("INSERT INTO repository_fts(repository_fts) VALUES('rebuild')")
    after = {key: search(q) for key,q in queries.items()}
    memory.close()
    historical = json.loads((ROOT / 'evals/plugin-v1/results/cp04-flashrank-2026-10-08/configured/observations.json').read_text(encoding='utf-8'))
    previous_pools = {c['case_id']: c['control']['retrieval']['candidates'] for c in historical['captures']}
    records = []
    run_id = str(uuid.uuid4())
    for case in cases:
        cid = case['case_id']
        previous.require(before[cid] == [r['github_repository_id'] for r in previous_pools[cid]], 'development baseline differs')
        results = {}
        # The temporary enriched cards have no accepted bundle pins. Validate the
        # selection against original pinned cards; never pass modified cards as
        # though they belonged to the canonical snapshot or disable its guard.
        for arm, ids, lookup in [('before', before[cid], by_id), ('after', after[cid], by_id)]:
            pack = base.old.baseline_pack(queries[cid], ids, lookup, plan, run_id)
            results[arm] = base.observe(ids, pack, case, 'ok' if ids else 'no_match')
        records.append({'case_id': cid, **results})
    # Exposed regression: only supported-positive coverage, no unknown-to-zero metrics.
    oracle = json.loads((ROOT / 'evals/plugin-v1/quality-oracle-v3-source.json').read_text(encoding='utf-8'))
    kotlin = next(c for c in oracle['cases'] if c['case_id'] == 'CP04-HV3-12')
    positives = set(kotlin['source_supported_positive_ids'])
    regression_rows = [{'full_name': f['full_name'], 'github_repository_id': f['github_repository_id'],
                        'before_rank': before['CP04-HV3-12'].index(f['github_repository_id'])+1 if f['github_repository_id'] in before['CP04-HV3-12'] else None,
                        'after_rank': after['CP04-HV3-12'].index(f['github_repository_id'])+1 if f['github_repository_id'] in after['CP04-HV3-12'] else None} for f in facts]
    previous.require(declared == declaration(base, plan, facts), 'source drift')
    summary = {'promotion_ready': False, 'development_macros': {a: base.old.complete_macro(records, a) for a in ('before','after')},
               'regression': {'case_id': 'CP04-HV3-12', 'positive_count': len(positives),
                              'before_supported_positive_pool': len(positives & set(before['CP04-HV3-12'])),
                              'after_supported_positive_pool': len(positives & set(after['CP04-HV3-12'])),
                              'before_supported_positive_top12': len(positives & set(before['CP04-HV3-12'][:12])),
                              'after_supported_positive_top12': len(positives & set(after['CP04-HV3-12'][:12])),
                              'ranks': regression_rows, 'metrics': None, 'reason': 'exposed regression; unresolved universe unknowns retained'},
               'source_index_unchanged': previous.file_hash(source_path) == plan['pins']['index_sha256']}
    comparison.write(OUTPUT / 'observations.json', {'declaration_sha256': previous.digest(declared),
                                                  'before_ids': before, 'after_ids': after, 'records': records})
    comparison.write(OUTPUT / 'summary.json', summary)
    print(json.dumps(summary))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    flags = parser.add_mutually_exclusive_group(required=True)
    flags.add_argument('--predeclare', action='store_true')
    flags.add_argument('--run', action='store_true')
    args = parser.parse_args()
    base = previous.shared()
    plan, cases, cards, by_id, members = base.load_inputs()
    facts = json.loads(FACTS.read_text(encoding='utf-8'))['facts']
    enriched_cards(cards, facts)  # Identity/provenance preflight before declaration.
    declared = declaration(base, plan, facts)
    if args.predeclare:
        comparison.write(OUTPUT / 'declaration.json', declared)
        print(json.dumps({'predeclared': previous.digest(declared)}))
    else:
        saved = json.loads((OUTPUT / 'declaration.json').read_text(encoding='utf-8'))
        previous.require(saved == declared, 'declaration drift')
        previous.require(not (OUTPUT / 'observations.json').exists(), 'capture exists')
        run(base, plan, cases, cards, by_id, facts, saved)


if __name__ == '__main__':
    main()
