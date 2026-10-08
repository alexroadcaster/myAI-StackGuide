"""Prospectively frozen query-composition ablation over exposed V2 development only."""
from __future__ import annotations

import argparse
import copy
from contextlib import closing
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import platform
import sqlite3
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('cp04_v3_shared_v2', ROOT / 'evals/plugin-v1/run_quality_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
old = v2.old
scorer = old.scorer
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-v3-2026-10-08/query-variants-development'
EXPECTED_CASES = ['CP04-V2-D' + str(i).zfill(2) for i in range(1, 11)]
# Development intent only. No terms are added, repeated, dropped or label-derived.
PARTITIONS = {
    'CP04-V2-D01': [['browser', 'Chromium', 'WebKit', 'Firefox'], ['testing', 'automation']],
    'CP04-V2-D02': [['React Native', 'mobile'], ['integration', 'testing', 'verification']],
    'CP04-V2-D03': [['React'], ['UI', 'component', 'components', 'library', 'libraries']],
    'CP04-V2-D04': [['isolation', 'isolated'], ['component', 'components', 'documenting', 'testing']],
    'CP04-V2-D05': [['Go'], ['HTTP', 'router', 'routing', 'web', 'framework', 'frameworks']],
    'CP04-V2-D06': [['.NET', 'dotnet', 'ASP.NET'], ['web', 'framework', 'enterprise']],
    'CP04-V2-D07': [['resumable', 'protocol', 'chunk', 'chunked'], ['upload', 'uploads']],
    'CP04-V2-D08': [['browser', 'JavaScript', 'React'], ['uploader', 'upload', 'uploading']],
    'CP04-V2-D09': [['Exif', 'image', 'images', 'audio', 'video'], ['metadata', 'tags']],
    'CP04-V2-D10': [['optimization', 'optimisation', 'allocation'], ['portfolio', 'portfolios', 'risk']],
}


def validate_partition(terms, groups):
    """Enforce exact original literal terms before any retrieval side effects."""
    scorer.require(isinstance(terms, list) and terms and len(terms) == len(set(terms)), 'invalid original terms')
    scorer.require(isinstance(groups, list) and len(groups) == 2 and
                   all(isinstance(group, list) and group for group in groups), 'nonempty two groups required')
    joined = [term for group in groups for term in group]
    scorer.require(len(joined) == len(set(joined)) and len(joined) == len(terms) and
                   set(joined) == set(terms), 'exact term partition required')


def validate_partitions(cases, *, require_complete=True):
    scorer.require(bool(cases), 'empty development cases')
    ids = [case['case_id'] for case in cases]
    scorer.require(len(ids) == len(set(ids)), 'duplicate development case')
    if require_complete:
        scorer.require(ids == EXPECTED_CASES, 'exact ten development cases required')
    for case in cases:
        scorer.require(case['case_id'] in PARTITIONS and case['split'] == 'development' and
                       case['metric_family'] == 'semantic', 'nondevelopment case')
        validate_partition(case['query_terms'], PARTITIONS[case['case_id']])


def load_inputs():
    # Reuse pure validators/functions, never old declaration source-code hash gates.
    plan = scorer.load_json(ROOT / 'evals/plugin-v1/quality-plan-v2.json')
    oracle = scorer._load_json_bounded(ROOT / 'evals/plugin-v1/quality-judgments-v2.json', 16 * 1024 * 1024)
    frozen = scorer.load_json(old.PLAN_PATH)
    scorer.validate_quality_plan(frozen)
    v2.validate_frozen_settings(plan, frozen)
    scorer.require(oracle['plan_sha256'] == scorer.digest(plan), 'oracle plan mismatch')
    for source in (plan, oracle):
        for path, digest in source['source_hashes'].items():
            resolved = (ROOT / path).resolve()
            scorer.require(resolved.is_relative_to(ROOT) and scorer.file_sha256(resolved) == digest,
                           'frozen source artifact drift')
    cards = scorer._load_json_bounded(ROOT / plan['artifacts']['cards_path'], 16 * 1024 * 1024)['cards']
    by_id = {card['identity']['github_repository_id']: card for card in cards}
    with closing(sqlite3.connect((ROOT / plan['artifacts']['index_path']).resolve().as_uri() + '?mode=ro&immutable=1', uri=True)) as connection:
        registry = [dict(zip(('route_id', 'route_kind', 'match_category_id', 'match_category_kind'), row))
                    for row in connection.execute('SELECT route_id, route_kind, match_category_id, match_category_kind FROM taxonomy_route_registry ORDER BY route_id, match_category_id')]
    scorer.require(scorer.digest(registry) == scorer.load_json(ROOT / plan['artifacts']['manifest_path'])['route_registry']['logical_routes_sha256'], 'route registry hash mismatch')
    members = {}
    for row in registry:
        members.setdefault(row['route_id'], set()).add(row['match_category_id'])
    cases = [copy.deepcopy(case) for case in plan['cases'] if case['split'] == 'development']
    judgments = {case['case_id']: case for case in oracle['cases']}
    validate_partitions(cases)
    for case in cases:
        routed = {repo_id for repo_id, card in by_id.items() if any(
            row['category_id'] in members[case['target_category_id']] for row in card['classifications'])}
        v2.validate_case_universe(case, judgments[case['case_id']], routed)
        case['judgments'] = judgments[case['case_id']]['judgments']
        for row in case['judgments']:
            for evidence in row['evidence']:
                card = by_id[row['github_repository_id']]
                scorer.require(v2.pointer_value(card, evidence['pointer']) == evidence['value'] and
                               evidence['source_ref'] in scorer.canonical(card).decode('utf-8'), 'source evidence mismatch')
        control, candidate = queries(plan, case)
        scorer.require(scorer.digest(control) == case['query_sha256'], 'frozen query drift')
        manifest = scorer.load_json(ROOT / plan['artifacts']['manifest_path'])
        policy = scorer.load_json(ROOT / plan['artifacts']['policy_path'])
        for query in (control, candidate):
            old.retrieval.validate_query(query, manifest=manifest, policy=policy)
    return plan, cases, cards, by_id, members


def queries(plan, case):
    validate_partition(case['query_terms'], PARTITIONS[case['case_id']])
    control = old.make_query(plan, case)
    candidate = copy.deepcopy(control)
    candidate['variants'] = [{'variant_id': name, 'terms': list(terms)} for name, terms in
                             zip(('q1', 'q2'), PARTITIONS[case['case_id']])]
    return control, candidate


def source_hashes(plan):
    paths = list(plan['source_hashes']) + [
        'evals/plugin-v1/quality-plan-v2.json', 'evals/plugin-v1/quality-judgments-v2.json',
        'evals/plugin-v1/run_quality.py', 'evals/plugin-v1/run_quality_v2.py',
        'evals/plugin-v1/evaluate_retrieval.py', 'evals/plugin-v1/run_query_variants_v3.py',
        'evals/plugin-v1/query-variants-v3-contract.md', 'tests/test_plugin_query_variants_v3.py',
        'plugins/myai-stackguide/scripts/retrieval.py', 'plugins/myai-stackguide/scripts/context_pack.py',
        'plugins/myai-stackguide/scripts/matcher.py', 'specs/retrieval/retrieval-policy.json',
        'evals/plugin-v1/results/cp04-v2-2026-10-08/development-observations.json',
        'evals/plugin-v1/results/cp04-v2-2026-10-08/held_out-observations.json',
    ]
    return {path: scorer.file_sha256(ROOT / path) for path in sorted(set(paths))}


def declaration(plan, cases):
    return {'schema_version': 'cp04_query_variants_declaration_v3', 'pins': plan['pins'],
            'source_hashes': source_hashes(plan), 'thresholds': plan['thresholds'],
            'thresholds_sha256': scorer.digest(plan['thresholds']), 'partitions': PARTITIONS,
            'cases': [{ 'case_id': c['case_id'], 'case_sha256': scorer.digest(c),
                       'queries': {arm: query for arm, query in zip(('control', 'candidate'), queries(plan, c))},
                       'literal_terms': c['query_terms']} for c in cases],
            'method': {'arms': ['single_or_fts_control', 'two_variant_equal_rrf', 'literal-field-or-v1'],
                       'literal_unchanged': plan['lexical_baseline'],
                       'denominator': 'V2 positive non-denied full routed universe, original ranks',
                       'source_gate': 'current exact source bytes, not historical source-code equality',
                       'partition_order': 'intent then context; allocation remains production policy',
                       'field_difference': 'FTS category labels include IDs/titles; literal titles only; retained',
                       'development_selection': 'compare macro recall/nDCG against control AND literal; no promotion',
                       'latency': 'single sequential retrieve duration per arm; no capacity benchmark'},
            'promotion_ready': False, 'held_out': 'not_run', 'tokens': None, 'provider_cost_usd': None}


def validate_declaration(saved, current):
    scorer.require(saved == current, 'declaration drift; do not capture changed source')


def write_json(name, value, *, output=OUTPUT):
    scorer.require(Path(name).name == name and name.endswith('.json'), 'output name escape')
    output.mkdir(parents=True, exist_ok=True)
    with (output / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def equivalence_projection(result, pack):
    return {'retrieval': {key: result[key] for key in
            ('status', 'candidates', 'executed_variants', 'retrieved_hits', 'truncated')},
            'pack_ids': [item['card']['identity']['github_repository_id'] for item in pack['cards']],
            'exclusions': pack['exclusions']}


def observe(ids, pack, case, status):
    record = old.observe_method(ids, pack, case, status)
    record['raw_unconditional_ranking_diagnostic'] = copy.deepcopy(record['ranking'])
    if status in {'ok', 'no_match'}:
        record['ranking'] = v2.constrained_ranking(ids, case['judgments'], case['k'])
    return record


def execute(query, plan, by_id, case, arm, run_id):
    start = time.perf_counter_ns()
    result = old.retrieval.retrieve(query, run_id=run_id,
        **{key: ROOT / plan['artifacts'][key] for key in ('index_path', 'manifest_path', 'policy_path')})
    elapsed = (time.perf_counter_ns() - start) / 1_000_000
    ids = [row['github_repository_id'] for row in result['candidates']]
    pack = old.context_pack.build_evidence_pack(query, result, {repo_id: by_id[repo_id] for repo_id in ids},
        pack_id='v3-' + arm + '-' + case['case_id'], max_cards=query['max_cards'],
        max_evidence_bytes=query['max_evidence_bytes'])
    return {'query': query, 'retrieval': result, 'evidence_pack': pack, 'elapsed_ms': elapsed,
            'query_bytes': len(scorer.canonical(query)),
            'controlled_input_bytes': len(scorer.canonical(query)) + len(scorer.canonical(pack))}, observe(ids, pack, case, result['status'])


def summarize(plan, records):
    macros = {arm: old.complete_macro(records, arm) for arm in ('control', 'candidate', 'baseline')}
    gates = {}
    for other in ('control', 'baseline'):
        for metric, threshold in [('recall_at_12', 'candidate_not_worse_than_baseline_recall_delta_min'),
                                  ('ndcg_at_12', 'candidate_not_worse_than_baseline_ndcg_delta_min')]:
            a, b = macros['candidate'][metric], macros[other][metric]
            gates['candidate_vs_' + other + '_' + metric] = None if a is None or b is None else a-b >= plan['thresholds'][threshold]
    for arm in ('control', 'candidate', 'baseline'):
        gates[arm + '_valid_ranking_and_status'] = all(r[arm]['ranking']['valid'] and r[arm]['retrieval_status']=='ok' for r in records)
        for name in ('hard_constraint_violations', 'false_exclusions', 'duplicate_canonical_ids'):
            total = sum(len(r[arm][name]) if isinstance(r[arm][name], list) else r[arm][name] for r in records)
            gates[arm + '_' + name] = total <= plan['thresholds'][name + '_max']
        n = sum(len(r[arm]['known_relevant_survived_pack']) for r in records)
        d = sum(len(r[arm]['known_relevant_top12_retrieved']) for r in records)
        gates[arm + '_pack_survival'] = n/d >= plan['thresholds']['evidence_pack_survival_rate_min'] if d else None
    gates['historical_control_equivalence'] = all(r['historical_control_equivalent'] for r in records)
    gates['historical_literal_equivalence'] = all(r['historical_literal_equivalent'] for r in records)
    passed = bool(records) and len(records)==len(EXPECTED_CASES) and all(v is True for v in gates.values())
    return {'schema_version': 'cp04_query_variants_summary_v3', 'record_count': len(records), 'macro': macros,
            'gates': gates, 'failed_gates': [k for k,v in gates.items() if v is False],
            'development_candidate_worth_heldout_review': passed, 'promotion_ready': False,
            'verdict': 'development_candidate_only' if passed else 'development_no_go',
            'held_out': 'not_run; proposed future cases are not sealed', 'human_calibration': False,
            'per_case': [{ 'case_id': r['case_id'], **{arm: r[arm]['ranking'] for arm in ('control','candidate','baseline')}} for r in records]}


def capture(plan, cases, cards, by_id, members, declared):
    # Preflight exclusive targets before any retrieval and preserve all historical outputs.
    scorer.require(not any((OUTPUT / name).exists() for name in ('development-observations.json', 'development-summary.json')), 'capture output already exists')
    historical = scorer._load_json_bounded(ROOT / 'evals/plugin-v1/results/cp04-v2-2026-10-08/development-observations.json', 32*1024*1024)
    historical_captures = {c['case_id']: c for c in historical['captures']}
    run_id, records, captures = str(uuid.uuid4()), [], []
    for case in cases:
        control, candidate = queries(plan, case)
        row = {'case_id': case['case_id'], 'case_sha256': scorer.digest(case)}
        details = {'case_id': case['case_id']}
        for arm, query in (('control', control), ('candidate', candidate)):
            details[arm], row[arm] = execute(query, plan, by_id, case, arm, run_id)
        baseline_ids = old.baseline_ids(plan, case, cards, members)
        baseline_pack = old.baseline_pack(control, baseline_ids, by_id, plan, run_id)
        row['baseline'] = observe(baseline_ids, baseline_pack, case, 'ok' if baseline_ids else 'no_match')
        details['baseline'] = {'terms': list(case['query_terms']), 'ranked_ids': baseline_ids,
                              'evidence_pack': baseline_pack, 'transport': 'literal adapter, no observed BM25',
                              'matched_fields': {str(i): old.literal_fields(by_id[i], case['query_terms']) for i in baseline_ids}}
        previous = historical_captures[case['case_id']]
        row['historical_control_equivalent'] = equivalence_projection(details['control']['retrieval'], details['control']['evidence_pack']) == equivalence_projection(previous['retrieval'], previous['candidate_evidence_pack'])
        row['historical_literal_equivalent'] = baseline_ids == previous['baseline_ranked_ids'] and [c['card']['identity']['github_repository_id'] for c in baseline_pack['cards']] == [c['card']['identity']['github_repository_id'] for c in previous['baseline_evidence_pack']['cards']] and baseline_pack['exclusions'] == previous['baseline_evidence_pack']['exclusions']
        policy = scorer.load_json(ROOT / plan['artifacts']['policy_path'])
        for arm in ('control', 'candidate'):
            d = details[arm]
            scorer.require(d['controlled_input_bytes'] <= policy['limits']['max_plugin_input_bytes'] and
                           row[arm]['evidence_pack_bytes'] <= candidate['max_evidence_bytes'], 'controlled input cap')
        records.append(row)
        captures.append(details)
    validate_declaration(declared, declaration(plan, cases))
    observation = {'schema_version': 'cp04_query_variants_observation_v3', 'evidence_kind': 'observed_offline_public_catalog',
        'captured_at': datetime.now(timezone.utc).isoformat(), 'run_id': run_id, 'pins': plan['pins'],
        'declaration_sha256': scorer.digest(declared), 'records': records, 'captures': captures,
        'environment': {'python': sys.version, 'sqlite': sqlite3.sqlite_version, 'platform': platform.platform()},
        'promotion_ready': False, 'tokens': None, 'provider_cost_usd': None}
    summary = summarize(plan, records)
    summary['declaration_sha256'] = scorer.digest(declared)
    write_json('development-observations.json', observation)
    write_json('development-summary.json', summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    flags = parser.add_mutually_exclusive_group(required=True)
    flags.add_argument('--predeclare', action='store_true')
    flags.add_argument('--run-development', action='store_true')
    args = parser.parse_args(argv)
    try:
        plan, cases, cards, by_id, members = load_inputs()
        declared = declaration(plan, cases)
        if args.predeclare:
            write_json('declaration.json', declared)
            print(json.dumps({'status':'predeclared', 'declaration_sha256':scorer.digest(declared)}))
            return 0
        saved = scorer.load_json(OUTPUT / 'declaration.json')
        validate_declaration(saved, declared)
        summary = capture(plan, cases, cards, by_id, members, declared)
        print(json.dumps({k:summary[k] for k in ('verdict','macro','failed_gates','development_candidate_worth_heldout_review')}))
        return 0 if summary['development_candidate_worth_heldout_review'] else 1
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'status':'invalid_input_or_unavailable', 'error_type':type(error).__name__, 'message':str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
