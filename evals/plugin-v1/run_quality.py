"""Pinned offline public-catalog observations, separate from the synthetic C8 scorer.

No models, providers, network, index writes, human grades, or held-out tuning.
The CLI first writes a declaration, then requires that exact declaration for capture.
"""

from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import importlib.util
import json
import math
import platform
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import unicodedata
import uuid

ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / 'evals/plugin-v1/quality-plan.json'
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-2026-10-08'
SCRIPT_DIR = ROOT / 'plugins/myai-stackguide/scripts'


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scorer = load_module('cp04_scorer', ROOT / 'evals/plugin-v1/evaluate_retrieval.py')
retrieval = load_module('cp04_retrieval', SCRIPT_DIR / 'retrieval.py')
context_pack = load_module('cp04_context_pack', SCRIPT_DIR / 'context_pack.py')


def make_query(plan, case):
    """Predeclared translation of frozen case fields; no oracle-based term tuning."""
    route, pins = plan['candidate_route'], plan['pins']
    return {
        'schema_version': route['query_schema_version'],
        'query_id': case['case_id'], 'brief_version': 1,
        'source_mode': route['source_mode'], 'retrieval_engine': route['retrieval_engine'],
        'policy_version': pins['retrieval_policy_version'], 'policy_sha256': pins['policy_sha256'],
        'card_schema_version': pins['card_schema_version'],
        'activity_schema_version': pins['activity_schema_version'],
        'index_format_version': pins['index_format_version'],
        'taxonomy_route_id': case['target_category_id'], 'language': case['query_locale'],
        'variants': [{'variant_id': 'q1', 'terms': list(case['query_terms'])}],
        'constraints': {'languages': [], 'deployment': [], 'allowed_licenses': [],
                        'compatibility': [], 'require_no_server': None, 'mandatory_fields': []},
        'max_candidates': route['max_candidates'], 'max_cards': route['max_cards'],
        'max_evidence_bytes': route['max_evidence_bytes'],
    }


def strict_ranking(ids, judgments, k):
    """Unknown grades stay unknown; never compact ranks or assign implicit zero."""
    grades = {item['github_repository_id']: item['grade'] for item in judgments}
    unjudged = [repo_id for repo_id in ids if repo_id not in grades]
    if len(ids) != len(set(ids)):
        return {'valid': False, 'reason': 'duplicate_identity', 'ranking': None,
                'unjudged_ids': unjudged}
    if unjudged:
        return {'valid': False, 'reason': 'incomplete_judgments', 'ranking': None,
                'unjudged_ids': unjudged}
    return {'valid': True, 'reason': None, 'ranking': scorer.ranking_metrics(ids, grades, k),
            'unjudged_ids': []}


def mean(values):
    return sum(values) / len(values) if values else None


def complete_macro(records, method):
    values = [record[method]['ranking']['ranking'] for record in records]
    if not values or any(value is None or value['recall_at_k'] is None or
                         value['ndcg_at_k'] is None for value in values):
        return {'recall_at_12': None, 'ndcg_at_12': None, 'complete': False}
    return {'recall_at_12': mean([value['recall_at_k'] for value in values]),
            'ndcg_at_12': mean([value['ndcg_at_k'] for value in values]), 'complete': True}


def route_members(plan):
    """Read the actual registry once; validate its logical hash before sharing filters."""
    path = ROOT / plan['artifacts']['index_path']
    with sqlite3.connect(path.resolve().as_uri() + '?mode=ro&immutable=1', uri=True) as connection:
        rows = [dict(zip(('route_id', 'route_kind', 'match_category_id', 'match_category_kind'), row))
                for row in connection.execute('SELECT route_id, route_kind, match_category_id, '
                                              'match_category_kind FROM taxonomy_route_registry '
                                              'ORDER BY route_id, match_category_id')]
    manifest = scorer.load_json(ROOT / plan['artifacts']['manifest_path'])
    scorer.require(scorer.digest(rows) == manifest['route_registry']['logical_routes_sha256'],
                   'route registry hash mismatch')
    result = {}
    for row in rows:
        result.setdefault(row['route_id'], set()).add(row['match_category_id'])
    return result, rows


def baseline_ids(plan, case, cards, members):
    route = members[case['target_category_id']]
    filtered = [card for card in cards if any(item['category_id'] in route
                                             for item in card['classifications'])]
    return scorer.lexical_baseline(filtered, case['query_terms'],
                                   plan['lexical_baseline']['candidate_limit'])


def literal_fields(card, terms):
    normalized = [unicodedata.normalize('NFKC', term).casefold() for term in terms]
    return [field for field, values in scorer._baseline_fields(card).items()
            if any(term in unicodedata.normalize('NFKC', value).casefold()
                   for term in normalized for value in values)]


def baseline_pack(query, ids, cards, plan, run_id):
    """Internal adapter reuses CP-09 packing; this is NOT a C9 FTS5 observation.

    The existing builder accepts only the pinned sqlite_fts5 transport. Its ranking
    input here is declared literal-baseline rank, with rank-monotonic placeholder
    RRF scores, never claimed as an executed BM25/RRF result or C8 capture.
    """
    fusion_k = scorer.load_json(ROOT / plan['artifacts']['policy_path'])['rank_fusion']['k']
    adapter = {
        'schema_version': query['schema_version'], 'run_id': run_id,
        'query_id': query['query_id'], 'query_sha256': scorer.digest(query),
        'brief_version': query['brief_version'], 'source_mode': query['source_mode'],
        'retrieval_engine': query['retrieval_engine'], 'pins': plan['pins'],
        'status': 'ok' if ids else 'no_match', 'reason_codes': [] if ids else ['no_hits'],
        'truncated': len(ids) >= query['max_candidates'],
        'candidates': [
            {'github_repository_id': repo_id, 'rank': rank, 'rrf_score': 1 / (fusion_k + rank),
             'matched_fields': literal_fields(cards[repo_id], query['variants'][0]['terms'])}
            for rank, repo_id in enumerate(ids, 1)],
    }
    return context_pack.build_evidence_pack(
        query, adapter, {repo_id: cards[repo_id] for repo_id in ids},
        pack_id='baseline-' + query['query_id'], max_cards=query['max_cards'],
        max_evidence_bytes=query['max_evidence_bytes'])


def observe_method(ids, pack, case, status='ok'):
    expected = {item['github_repository_id']: item for item in case['judgments']}
    selected = [item['card']['identity']['github_repository_id'] for item in pack['cards']]
    denied = {repo_id for repo_id, item in expected.items() if item['constraint'] == 'denied'}
    allowed = {repo_id for repo_id, item in expected.items() if item['constraint'] == 'allowed'}
    false_excluded = [item['github_repository_id'] for item in pack['exclusions']
                      if item['github_repository_id'] in allowed and
                      set(item['reason_codes']) & {'constraint_mismatch', 'mandatory_fact_unknown',
                                                 'archived', 'unavailable'}]
    relevant = {repo_id for repo_id, item in expected.items() if item['grade'] > 0}
    useful_retrieved = set(ids[:case['k']]) & relevant - denied
    ranking = strict_ranking(ids, case['judgments'], case['k'])
    pack_ranking = strict_ranking(selected, case['judgments'], case['k'])
    if status not in {'ok', 'no_match'}:
        ranking = {'valid': False, 'reason': 'typed_retrieval_failure', 'ranking': None,
                   'unjudged_ids': ranking['unjudged_ids']}
        pack_ranking = {'valid': False, 'reason': 'typed_retrieval_failure', 'ranking': None,
                        'unjudged_ids': pack_ranking['unjudged_ids']}
    return {
        'ranked_ids': ids, 'detailed_card_ids': selected,
        'retrieval_status': status, 'ranking': ranking,
        'pack_ranking': pack_ranking,
        'judged_returned_ids': [repo_id for repo_id in ids if repo_id in expected],
        'judgment_coverage': len(set(ids) & expected.keys()) / len(ids) if ids else None,
        'known_pool_recall_at_12_diagnostic': len(set(ids[:case['k']]) & relevant) / len(relevant)
                                            if relevant else None,
        'known_relevant_top12_retrieved': sorted(useful_retrieved),
        'known_relevant_survived_pack': sorted(useful_retrieved & set(selected)),
        'pack_survival_rate': len(useful_retrieved & set(selected)) / len(useful_retrieved)
                              if useful_retrieved else None,
        'hard_constraint_violations': sorted(set(selected) & denied),
        'false_exclusions': false_excluded,
        'duplicate_canonical_ids': len(ids) - len(set(ids)) + len(selected) - len(set(selected)),
        'evidence_pack_bytes': len(scorer.canonical(pack)),
        'exclusions': pack['exclusions'],
    }


def execute(plan, case, run_id):
    query = make_query(plan, case)
    artifacts = plan['artifacts']
    start = time.perf_counter_ns()
    result = retrieval.retrieve(query, run_id=run_id,
                                index_path=ROOT / artifacts['index_path'],
                                manifest_path=ROOT / artifacts['manifest_path'],
                                policy_path=ROOT / artifacts['policy_path'])
    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
    return query, result, elapsed_ms


def source_hashes():
    paths = ['evals/plugin-v1/run_quality.py', 'evals/plugin-v1/evaluate_retrieval.py',
             'evals/plugin-v1/runner-contract.md', 'plugins/myai-stackguide/scripts/retrieval.py',
             'plugins/myai-stackguide/scripts/matcher.py',
             'plugins/myai-stackguide/scripts/context_pack.py',
             'specs/retrieval/retrieval-policy.json']
    return {path: scorer.file_sha256(ROOT / path) for path in paths}


def declaration(plan):
    return {
        'schema_version': 'cp04_quality_declaration_v1', 'quality_plan_sha256': scorer.digest(plan),
        'pins': plan['pins'], 'source_hashes': source_hashes(), 'thresholds': plan['thresholds'],
        'query_mapping': 'target_category_id->taxonomy_route_id; exact query_terms in q1 OR; empty hard constraints',
        'baseline': 'literal-field-or-v1; shared taxonomy route and matcher/context_pack; explicit policy candidate cap',
        'unknown_judgments': 'null official ranking/macro; preserve actual ranks and unjudged IDs; no_go',
        'pack_survival': 'known grade>0 non-denied IDs in raw top12 that survive detail pack / same retrieved IDs',
        'alias_success': 'alias target in raw top12; denied alias target excluded from detail pack',
        'strata': 'all frozen required tags and container domains, separately all/development/held_out; missing=null',
        'latency': {'repetitions': plan['scale_protocol']['actual']['repetitions'],
                    'case_schedule': 'round robin in frozen case order',
                    'cold': 'new process/connection each sample; timer surrounds retrieval.retrieve only',
                    'warm': 'one process; discard one warmup; new immutable connection per retrieve call',
                    'percentile': 'nearest rank ceil(p*n); no OS cache flush'},
        'memory': 'Windows GetProcessMemoryInfo PeakWorkingSetSize, process-lifetime peak; null elsewhere',
        'bytes': 'canonical compact sorted-key UTF-8 query and pack; controlled input=query+pack; no Brief/context',
        'tokens': None, 'provider_cost_usd': None, 'human_review': 'not executed',
        'synthetic_headroom': 'not executed; separate CP-11 lane',
        'commands': [
            '.venv/Scripts/python.exe -B evals/plugin-v1/run_quality.py --predeclare --plan-sha256 ' + scorer.digest(plan),
            '.venv/Scripts/python.exe -B evals/plugin-v1/run_quality.py --run --plan-sha256 ' + scorer.digest(plan)],
    }


def write_json(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def percentile(samples, fraction):
    return sorted(samples)[math.ceil(len(samples) * fraction) - 1] if samples else None


def peak_working_set():
    if sys.platform != 'win32':
        return None
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
                'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise OSError('process memory counter unavailable')
    return counters.PeakWorkingSetSize


def measure_performance(plan, run_id):
    count = plan['scale_protocol']['actual']['repetitions']
    cold, warm = [], []
    for index in range(count):
        completed = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()),
                                    '--sample-case', str(index % len(plan['cases'])),
                                    '--plan-sha256', scorer.digest(plan)],
                                   cwd=ROOT, capture_output=True, text=True, timeout=60, check=False)
        scorer.require(completed.returncode == 0, 'cold sample process failed')
        sample = json.loads(completed.stdout)
        scorer.require(sample['status'] in {'ok', 'no_match'},
                       'cold sample retrieval failed')
        cold.append(sample)
    execute(plan, plan['cases'][0], run_id)  # One predeclared discarded warmup.
    for index in range(count):
        case = plan['cases'][index % len(plan['cases'])]
        _, result, elapsed = execute(plan, case, run_id)
        scorer.require(result['status'] in {'ok', 'no_match'},
                       'warm sample retrieval failed')
        warm.append({'case_id': case['case_id'], 'latency_ms': elapsed, 'status': result['status']})
    return {'cold_samples': cold, 'warm_samples': warm,
            'cold_p50_ms': percentile([item['latency_ms'] for item in cold], .50),
            'cold_p95_ms': percentile([item['latency_ms'] for item in cold], .95),
            'warm_p50_ms': percentile([item['latency_ms'] for item in warm], .50),
            'warm_p95_ms': percentile([item['latency_ms'] for item in warm], .95),
            'peak_memory_bytes': peak_working_set(),
            'memory_method': 'GetProcessMemoryInfo PeakWorkingSetSize; lifetime peak includes capture preparation',
            'python': sys.version, 'sqlite': sqlite3.sqlite_version,
            'platform': platform.platform(), 'machine': platform.machine(),
            'processor': platform.processor(), 'os_cache': 'not flushed; prior validation/capture warmed OS cache',
            'index_bytes': (ROOT / plan['artifacts']['index_path']).stat().st_size,
            'synthetic_headroom': None, 'tokens': None, 'provider_cost_usd': None}


def summary(plan, records, performance, registry):
    thresholds = plan['thresholds']
    splits = {split: [record for record in records if record['split'] == split]
              for split in ('development', 'held_out')}
    macros = {split: {method: complete_macro(items, method) for method in ('candidate', 'baseline')}
              for split, items in splits.items()}
    strata = {}
    for split, items in {'all': records, **splits}.items():
        strata[split] = {}
        for kind, values in [('tags', plan['stratification']['required_case_tags']),
                             ('container_domain_ids', plan['stratification']['container_ids'])]:
            strata[split][kind] = {value: {'case_count': len(selected),
                                          'candidate': complete_macro(selected, 'candidate'),
                                          'baseline': complete_macro(selected, 'baseline')}
                                   for value in values
                                   for selected in [[item for item in items if value in item[kind]]]}
    gates = {'candidate_status_matches': all(item['retrieval_status'] ==
                                             plan['candidate_route']['expected_status'] for item in records)}
    held = macros['held_out']
    for metric, threshold in [('recall_at_12', 'held_out_macro_recall_at_12_min'),
                              ('ndcg_at_12', 'held_out_macro_ndcg_at_12_min')]:
        value = held['candidate'][metric]
        base = held['baseline'][metric]
        gates[threshold] = None if value is None else value >= thresholds[threshold]
        delta_key = ('candidate_not_worse_than_baseline_recall_delta_min' if metric == 'recall_at_12'
                     else 'candidate_not_worse_than_baseline_ndcg_delta_min')
        gates[delta_key] = None if value is None or base is None else value - base >= thresholds[delta_key]
    relevant_strata = [value for family in strata['held_out'].values() for value in family.values()]
    gates['held_out_required_strata'] = None if any(not value['candidate']['complete']
                                                   for value in relevant_strata) else all(
        value['candidate']['recall_at_12'] >= thresholds['required_stratum_recall_at_12_min'] and
        value['candidate']['ndcg_at_12'] >= thresholds['required_stratum_ndcg_at_12_min']
        for value in relevant_strata)
    totals = {name: sum(len(item['candidate'][name]) if isinstance(item['candidate'][name], list)
                        else item['candidate'][name] for item in records)
              for name in ('hard_constraint_violations', 'false_exclusions', 'duplicate_canonical_ids')}
    for name, value in totals.items():
        gates[name] = value <= thresholds[name + '_max']
    aliases = [item['candidate_alias_success'] for item in records if item['candidate_alias_success'] is not None]
    survival_n = sum(len(item['candidate']['known_relevant_survived_pack']) for item in records)
    survival_d = sum(len(item['candidate']['known_relevant_top12_retrieved']) for item in records)
    survival = survival_n / survival_d if survival_d else None
    gates['alias_success_rate_min'] = mean(aliases) >= thresholds['alias_success_rate_min'] if aliases else None
    gates['evidence_pack_survival_rate_min'] = survival >= thresholds['evidence_pack_survival_rate_min'] if survival is not None else None
    for measure, threshold in [('cold_p95_ms', 'actual_cold_p95_ms_max'),
                               ('warm_p95_ms', 'actual_warm_p95_ms_max'),
                               ('peak_memory_bytes', 'peak_memory_bytes_max'), ('index_bytes', 'index_bytes_max')]:
        value = performance[measure]
        gates[threshold] = value <= thresholds[threshold] if value is not None else None
    route_counts = {kind: len({row['route_id'] for row in registry if row['route_kind'] == kind})
                    for kind in ('category', 'container', 'review_bucket')}
    gates['container_registry_coverage'] = route_counts['container'] >= thresholds['container_route_coverage_min']
    gates['leaf_registry_coverage'] = route_counts['category'] >= thresholds['leaf_route_coverage_min']
    incomplete = [item['case_id'] for item in records if not item['candidate']['ranking']['valid']
                  or not item['baseline']['ranking']['valid']]
    return {'schema_version': 'cp04_quality_summary_v1', 'quality_plan_sha256': scorer.digest(plan),
            'pins': plan['pins'], 'record_count': len(records), 'macro': macros,
            'strata': strata, 'gates': gates, 'constraint_totals_judged_pool_only': totals,
            'alias_success_rate': mean(aliases), 'evidence_pack_survival_known_pool': survival,
            'survival_numerator': survival_n, 'survival_denominator': survival_d,
            'registry_route_counts': route_counts, 'executed_quality_routes': sorted({item['target_category_id'] for item in records}),
            'incomplete_judgment_cases': incomplete,
            'diagnostic_known_pool_recall': {split: {method: mean([item[method]['known_pool_recall_at_12_diagnostic']
                                                  for item in items]) for method in ('candidate', 'baseline')}
                                               for split, items in splits.items()},
            'failed_gates': [key for key, value in gates.items() if value is False],
            'unmeasured_gates': [key for key, value in gates.items() if value is None],
            'verdict': 'no_go' if incomplete or any(value is not True for value in gates.values()) else 'needs_owner_acceptance',
            'promotion_ready': False, 'human_usefulness': 'not_observed',
            'paired_ru_en_meaning': 'not_observed', 'browser_and_no_call_locale_switch': 'not_observed',
            'state_publication_recovery': 'not_in_this_runner', 'synthetic_10k_headroom': 'not_run',
            'all_leaf_container_runtime_routes': 'not_run; registry counts are structural index evidence',
            'rubric_calibrated': False, 'pool_oracle_human_accepted': False}


def capture(plan, declared):
    cards = scorer._load_json_bounded(ROOT / plan['artifacts']['cards_path'], 16 * 1024 * 1024)['cards']
    cards_by_id = {card['identity']['github_repository_id']: card for card in cards}
    members, registry = route_members(plan)
    run_id = str(uuid.uuid4())
    records, captures = [], []
    for case in plan['cases']:
        query, result, elapsed_ms = execute(plan, case, run_id)
        ids = [item['github_repository_id'] for item in result['candidates']]
        pack = context_pack.build_evidence_pack(query, result, {repo_id: cards_by_id[repo_id] for repo_id in ids},
                      pack_id='candidate-' + case['case_id'], max_cards=query['max_cards'],
                      max_evidence_bytes=query['max_evidence_bytes'])
        literal_ids = baseline_ids(plan, case, cards, members)
        literal_pack = baseline_pack(query, literal_ids, cards_by_id, plan, run_id)
        alias_ids = [repo_id for repo_id, card in cards_by_id.items() if case['expected_alias'] and
                     case['expected_alias'].casefold() in [alias.casefold() for alias in card['identity']['full_name_aliases']]]
        denied = {item['github_repository_id'] for item in case['judgments'] if item['constraint'] == 'denied'}
        def alias_ok(method_ids, method_pack):
            selected = {item['card']['identity']['github_repository_id'] for item in method_pack['cards']}
            return float(all(repo_id in method_ids[:case['k']] and
                             (repo_id not in selected if repo_id in denied else True)
                             for repo_id in alias_ids)) if alias_ids else None
        records.append({'case_id': case['case_id'], 'case_sha256': scorer.digest(case),
                        'split': case['split'], 'tags': case['tags'],
                        'container_domain_ids': case['container_domain_ids'],
                        'target_category_id': case['target_category_id'],
                        'judgment_pool_ids': case['judgment_pool_ids'],
                        'query_sha256': scorer.digest(query), 'retrieval_status': result['status'],
                        'latency_ms': elapsed_ms, 'query_bytes': len(scorer.canonical(query)),
                        'controlled_input_bytes': len(scorer.canonical(query)) + len(scorer.canonical(pack)),
                        'candidate': observe_method(ids, pack, case, result['status']),
                        'baseline': observe_method(literal_ids, literal_pack, case,
                                                   'ok' if literal_ids else 'no_match'),
                        'alias_target_ids': alias_ids,
                        'candidate_alias_success': alias_ok(ids, pack),
                        'baseline_alias_success': alias_ok(literal_ids, literal_pack)})
        captures.append({'case_id': case['case_id'], 'query': query, 'retrieval': result,
                         'candidate_evidence_pack': pack, 'baseline_ranked_ids': literal_ids,
                         'baseline_evidence_pack': literal_pack,
                         'baseline_transport': 'literal adapter, NOT observed C9 retrieval or RRF scoring'})
    observation = {'schema_version': 'cp04_quality_observation_v1',
                   'evidence_kind': 'observed_offline_public_catalog_diagnostic', 'run_id': run_id,
                   'captured_at': datetime.now(timezone.utc).isoformat(),
                   'declaration_sha256': scorer.digest(declared), 'quality_plan_sha256': scorer.digest(plan),
                   'pins': plan['pins'], 'records': records, 'captures': captures,
                   'promotion_ready': False}
    write_json('observations.json', observation)
    performance = measure_performance(plan, run_id)
    write_json('performance.json', performance)
    report = summary(plan, records, performance, registry)
    write_json('summary.json', report)
    write_json('artifact-hashes.json', {name: scorer.file_sha256(OUTPUT / name) for name in
                                       ('declaration.json', 'observations.json', 'performance.json', 'summary.json')})
    return report


def measurement_amendment(plan):
    """Bind a narrow timing-control repair to the untouched original captures."""
    original = scorer._load_json_bounded(OUTPUT / 'declaration.json', 1024 * 1024)
    observed = scorer._load_json_bounded(OUTPUT / 'observations.json', 16 * 1024 * 1024)
    scorer.require(observed['declaration_sha256'] == scorer.digest(original),
                   'original capture declaration mismatch')
    scorer.require(original['quality_plan_sha256'] == observed['quality_plan_sha256'] == scorer.digest(plan),
                   'original capture plan mismatch')
    scorer.require(original['pins'] == observed['pins'] == plan['pins'], 'original capture pins mismatch')
    current_hashes = source_hashes()
    allowed_changes = {'evals/plugin-v1/run_quality.py', 'evals/plugin-v1/runner-contract.md'}
    scorer.require(all(current_hashes[path] == digest for path, digest in original['source_hashes'].items()
                       if path not in allowed_changes), 'capture-producing runtime changed')
    return {
        'schema_version': 'cp04_measurement_amendment_v1',
        'reason': 'valid no_match is timed; frozen expected_status=ok still fails quality status gate',
        'original_observations_sha256': scorer.file_sha256(OUTPUT / 'observations.json'),
        'original_declaration_sha256': scorer.digest(original),
        'capture_producing_source_hashes': original['source_hashes'],
        'measurement_source_hashes': current_hashes,
        'quality_plan_sha256': scorer.digest(plan), 'pins': plan['pins'],
        'measurement': original['latency'], 'accepted_sample_statuses': ['ok', 'no_match'],
        'rankings_packs_queries': 'reuse original exact bytes; never recapture or overwrite',
        'command': '.venv/Scripts/python.exe -B evals/plugin-v1/run_quality.py --resume-measurement --plan-sha256 ' + scorer.digest(plan),
    }


def resume_measurement(plan, amendment):
    scorer.require(not (OUTPUT / 'performance.json').exists() and not (OUTPUT / 'summary.json').exists(),
                   'completed measurement already exists')
    observed = scorer._load_json_bounded(OUTPUT / 'observations.json', 16 * 1024 * 1024)
    scorer.require(scorer.file_sha256(OUTPUT / 'observations.json') ==
                   amendment['original_observations_sha256'], 'frozen observations changed')
    performance = measure_performance(plan, observed['run_id'])
    performance['measurement_amendment_sha256'] = scorer.digest(amendment)
    performance['original_observations_sha256'] = amendment['original_observations_sha256']
    write_json('performance.json', performance)
    _, registry = route_members(plan)
    report = summary(plan, observed['records'], performance, registry)
    report['measurement_amendment_sha256'] = scorer.digest(amendment)
    report['original_observations_sha256'] = amendment['original_observations_sha256']
    write_json('summary.json', report)
    write_json('artifact-hashes.json', {name: scorer.file_sha256(OUTPUT / name) for name in
                                       ('declaration.json', 'observations.json', 'measurement-amendment.json',
                                        'performance.json', 'summary.json')})
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--predeclare', action='store_true')
    group.add_argument('--run', action='store_true')
    group.add_argument('--predeclare-measurement-amendment', action='store_true')
    group.add_argument('--resume-measurement', action='store_true')
    group.add_argument('--sample-case', type=int, help=argparse.SUPPRESS)
    parser.add_argument('--plan-sha256', required=True)
    args = parser.parse_args(argv)
    try:
        plan = scorer.load_json(PLAN_PATH)
        scorer.require(scorer.digest(plan) == args.plan_sha256, 'quality plan digest mismatch')
        if args.sample_case is not None:
            scorer.require(0 <= args.sample_case < len(plan['cases']), 'invalid sample case')
            case = plan['cases'][args.sample_case]
            _, result, elapsed = execute(plan, case, str(uuid.uuid4()))
            print(json.dumps({'case_id': case['case_id'], 'status': result['status'],
                              'latency_ms': elapsed, 'peak_memory_bytes': peak_working_set()}))
            return 0 if result['status'] in {'ok', 'no_match'} else 1
        scorer.validate_quality_plan(plan)
        declared = declaration(plan)
        if args.predeclare:
            write_json('declaration.json', declared)
            print(json.dumps({'declaration_sha256': scorer.digest(declared),
                              'quality_plan_sha256': scorer.digest(plan), 'quality_observed': False}))
            return 0
        if args.predeclare_measurement_amendment:
            amendment = measurement_amendment(plan)
            write_json('measurement-amendment.json', amendment)
            print(json.dumps({'amendment_sha256': scorer.digest(amendment),
                              'original_observations_sha256': amendment['original_observations_sha256']}))
            return 0
        if args.resume_measurement:
            stored_amendment = scorer._load_json_bounded(OUTPUT / 'measurement-amendment.json', 1024 * 1024)
            scorer.require(stored_amendment == measurement_amendment(plan), 'measurement amendment mismatch')
            report = resume_measurement(plan, stored_amendment)
            print(json.dumps({'verdict': report['verdict'], 'promotion_ready': False,
                              'record_count': report['record_count'], 'failed_gates': report['failed_gates'],
                              'unmeasured_gates': report['unmeasured_gates']}))
            return 1 if report['verdict'] == 'no_go' else 0
        stored = scorer._load_json_bounded(OUTPUT / 'declaration.json', 1024 * 1024)
        scorer.require(stored == declared, 'predeclared protocol/source digest mismatch')
        scorer.require(not (OUTPUT / 'observations.json').exists(), 'capture already exists; preserve frozen results')
        report = capture(plan, declared)
        print(json.dumps({'verdict': report['verdict'], 'promotion_ready': False,
                          'record_count': report['record_count'], 'failed_gates': report['failed_gates'],
                          'unmeasured_gates': report['unmeasured_gates']}))
        return 1 if report['verdict'] == 'no_go' else 0
    except (OSError, ValueError, KeyError, sqlite3.DatabaseError, subprocess.SubprocessError) as error:
        print(json.dumps({'verdict': 'invalid_input_or_unavailable_check', 'error_type': type(error).__name__,
                          'reason': str(error), 'promotion_ready': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
