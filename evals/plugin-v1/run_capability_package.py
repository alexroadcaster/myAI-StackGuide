"""Prospective comparison of a verified candidate package, without activation."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_plugin_capability_package as builder

spec = importlib.util.spec_from_file_location('cp04_capability_shared', ROOT / 'evals/plugin-v1/run_query_variants_v3.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
OUTPUT = builder.OUTPUT.parent / 'comparison-v2'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(builder.catalog.canonical_bytes(value))


def verified_package(expected_receipt_sha):
    """Trust starts at the predeclared receipt hash, not a self-asserted manifest."""
    folder = builder.OUTPUT
    receipt_bytes = (folder / 'build-receipt.json').read_bytes()
    if builder.sha(receipt_bytes) != expected_receipt_sha:
        raise ValueError('candidate receipt drift')
    receipt = json.loads(receipt_bytes)
    for name, digest in receipt['file_sha256'].items():
        if Path(name).name != name or builder.sha((folder / name).read_bytes()) != digest:
            raise ValueError('candidate package drift')
    snapshot = json.loads((folder / builder.index.CARDS.name).read_bytes())
    manifest = json.loads((folder / builder.index.MANIFEST.name).read_bytes())
    if manifest['pins']['cards_sha256'] != receipt['file_sha256'][builder.index.CARDS.name]:
        raise ValueError('card hash does not match manifest')
    verification = builder.index.verify_sqlite(folder / builder.index.INDEX.name, snapshot['cards'],
        builder.index.logical_rows(snapshot['cards']), manifest)
    cards = base.old.context_pack._cards_from_verified_snapshot(snapshot, manifest['pins'], expected_count=2500)
    return snapshot, manifest, cards, verification


def fixture_pack(query, result, cards, arm):
    """Explicit evaluator seam after byte verification; never canonical trust activation."""
    selected = base.old.context_pack._select_verified_cards(cards, cards,
        [r['github_repository_id'] for r in result['candidates']])
    return base.old.context_pack._build_evidence_pack_from_trusted_cards(query, result, selected,
        pack_id='capability-' + arm + '-' + query['query_id'], max_cards=query['max_cards'],
        max_evidence_bytes=query['max_evidence_bytes'])


def fixture_retrieval(query, manifest, run_id):
    policy = json.loads((builder.OUTPUT / builder.index.PACKAGED_POLICY.name).read_bytes())
    base.old.retrieval._validate_manifest_policy(manifest, policy)
    return base.old.retrieval._retrieve_verified_bundle(query, run_id=run_id,
        index_path=builder.OUTPUT / builder.index.INDEX.name, manifest=manifest, policy=policy)


def literal_result(query, ids, cards, pins, run_id):
    # Literal baseline rank adapter, not observed BM25/RRF; no new production path.
    fusion = json.loads((builder.OUTPUT / builder.index.PACKAGED_POLICY.name).read_bytes())['rank_fusion']['k']
    return dict(schema_version=query['schema_version'], run_id=run_id, query_id=query['query_id'],
        query_sha256=base.scorer.digest(query), brief_version=query['brief_version'],
        source_mode=query['source_mode'], retrieval_engine=query['retrieval_engine'], pins=pins,
        status='ok' if ids else 'no_match', reason_codes=[] if ids else ['no_hits'],
        truncated=len(ids) >= query['max_candidates'], candidates=[dict(github_repository_id=rid,
            rank=rank, rrf_score=1/(fusion+rank), matched_fields=base.old.literal_fields(cards[rid], query['variants'][0]['terms']))
            for rank, rid in enumerate(ids, 1)])


def declaration(plan, cases):
    sources = base.source_hashes(plan)
    for path in (builder.SOURCE, builder.SCHEMA, Path(builder.__file__), Path(__file__),
                 ROOT / 'tests/test_plugin_capability_package.py',
                 ROOT / 'evals/plugin-v1/capability-package-contract.md'):
        sources[path.relative_to(ROOT).as_posix()] = builder.sha(path.read_bytes())
    return dict(schema_version='cp04_capability_comparison_v1', sources=sources,
        receipt_sha256=builder.sha((builder.OUTPUT / 'build-receipt.json').read_bytes()),
        cases=[dict(case_id=c['case_id'], sha256=base.scorer.digest(c)) for c in cases],
        thresholds=plan['thresholds'], arms=['control', 'baseline', 'candidate', 'enriched_literal'],
        scope='ten exposed development cases plus exposed Kotlin coverage diagnostic; no fresh held-out',
        active_bundle_changed=False, promotion_ready=False)


def run(plan, cases, original, original_by_id, members, declared):
    snapshot, manifest, cards, verification = verified_package(declared['receipt_sha256'])
    run_id = str(uuid.uuid4())
    records, captures = [], []
    canonical_rejections = 0
    for case in cases:
        query = base.old.make_query(plan, case)
        row, capture = dict(case_id=case['case_id']), dict(case_id=case['case_id'], query=query)
        for arm in ('control', 'baseline', 'candidate', 'enriched_literal'):
            if arm == 'control':
                details, observed = base.execute(query, plan, original_by_id, case, arm, run_id)
            elif arm == 'baseline':
                ids = base.old.baseline_ids(plan, case, original, members)
                pack = base.old.baseline_pack(query, ids, original_by_id, plan, run_id)
                details = dict(ranked_ids=ids, evidence_pack=pack, transport='literal rank adapter')
                observed = base.observe(ids, pack, case, 'ok' if ids else 'no_match')
            else:
                if arm == 'candidate':
                    public = base.old.retrieval.retrieve(query, run_id=run_id,
                        index_path=builder.OUTPUT / builder.index.INDEX.name,
                        manifest_path=builder.OUTPUT / builder.index.MANIFEST.name,
                        policy_path=builder.OUTPUT / builder.index.PACKAGED_POLICY.name)
                    if public['status'] != 'index_incompatible':
                        raise ValueError('public retrieval accepted unactivated package')
                    result = fixture_retrieval(query, manifest, run_id)
                    if result['status'] != 'ok':
                        raise ValueError('verified candidate retrieval failed: ' + result['status'])
                    # Production pack must reject this unactivated trust anchor.
                    try:
                        base.old.context_pack.build_evidence_pack(query, result, cards,
                            pack_id='negative-' + query['query_id'], max_cards=query['max_cards'],
                            max_evidence_bytes=query['max_evidence_bytes'])
                    except ValueError:
                        canonical_rejections += 1
                    else:
                        raise ValueError('canonical pack accepted unactivated candidate')
                else:
                    ids = base.old.baseline_ids(plan, case, snapshot['cards'], members)
                    result = literal_result(query, ids, cards, manifest['pins'], run_id)
                ids = [r['github_repository_id'] for r in result['candidates']]
                pack = fixture_pack(query, result, cards, arm)
                details = dict(retrieval=result, evidence_pack=pack,
                    transport='observed candidate FTS5' if arm == 'candidate' else 'literal rank adapter')
                observed = base.observe(ids, pack, case, result['status'])
            row[arm], capture[arm] = observed, details
        records.append(row)
        captures.append(capture)
    macros = {arm: base.old.complete_macro(records, arm) for arm in declared['arms']}
    gates = {}
    for arm in ('candidate', 'enriched_literal'):
        for reference in ('control', 'baseline'):
            for metric, threshold in (('recall_at_12', 'candidate_not_worse_than_baseline_recall_delta_min'),
                                      ('ndcg_at_12', 'candidate_not_worse_than_baseline_ndcg_delta_min')):
                a, b = macros[arm][metric], macros[reference][metric]
                gates[arm + '_vs_' + reference + '_' + metric] = a is not None and b is not None and a-b >= plan['thresholds'][threshold]
        gates[arm + '_constraints'] = all(not r[arm]['hard_constraint_violations'] and not r[arm]['false_exclusions'] and
                                        not r[arm]['duplicate_canonical_ids'] for r in records)
        gates[arm + '_valid_ranking'] = all(r[arm]['ranking']['valid'] and r[arm]['retrieval_status'] == 'ok' for r in records)
    old_kotlin = json.loads((ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08/held-out/observations.json').read_bytes())
    kotlin = next(c for c in old_kotlin['captures'] if c['case_id'] == 'CP04-HV3-12')
    result = fixture_retrieval(kotlin['query'], manifest, run_id)
    positive = {f['github_repository_id'] for f in builder.load_source()['facts'][:5]}
    before = [r['github_repository_id'] for r in kotlin['control']['retrieval']['candidates']]
    after = [r['github_repository_id'] for r in result['candidates']]
    regression = dict(case_id='CP04-HV3-12', supported_positives=len(positive),
        before_pool=len(positive & set(before)), after_pool=len(positive & set(after)),
        before_top12=len(positive & set(before[:12])), after_top12=len(positive & set(after[:12])),
        ranking_metrics=None, unknown_universe_retained=True, retrieval_status=result['status'])
    if declaration(plan, cases) != declared:
        raise ValueError('source drift during capture')
    summary = dict(macros=macros, gates=gates, regression=regression, package_verification=verification,
        canonical_unactivated_package_rejections=canonical_rejections, promotion_ready=False,
        development_qualified_arms=[a for a in ('candidate', 'enriched_literal') if all(v for k,v in gates.items() if k.startswith(a+'_'))],
        limitations=['exposed development only', 'old source-based relevance grades retained',
                     'no agent-composed recommendation or fresh human acceptance', 'canonical package unchanged'])
    write(OUTPUT / 'observations.json', dict(declaration_sha256=base.scorer.digest(declared), records=records, captures=captures,
                                            kotlin_query=kotlin['query'], kotlin_retrieval=result))
    write(OUTPUT / 'summary.json', summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--predeclare', action='store_true')
    action.add_argument('--run', action='store_true')
    args = parser.parse_args()
    plan, cases, original, by_id, members = base.load_inputs()
    declared = declaration(plan, cases)
    if args.predeclare:
        verified_package(declared['receipt_sha256'])
        write(OUTPUT / 'declaration.json', declared)
        print(json.dumps({'predeclared': base.scorer.digest(declared)}))
    else:
        saved = json.loads((OUTPUT / 'declaration.json').read_bytes())
        if saved != declared or any((OUTPUT / name).exists() for name in ('observations.json', 'summary.json')):
            raise ValueError('declaration drift or capture already exists')
        run(plan, cases, original, by_id, members, saved)
