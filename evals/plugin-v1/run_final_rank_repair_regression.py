"""One source-pinned replay of two exposed CP-04 suites.

The old plans, judgments, literal orders and failures remain immutable. Active
source/asset hashes are explicitly rebound in a new plan after production is
stable. A passing replay proves regression only, never fresh or human acceptance.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / 'evals/plugin-v1/final-quality-rank-repair-regression-2026-10-11.json'
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-final-quality-rank-repair-regression-2026-10-11'
REQUIRED_SOURCES = {
    'evals/plugin-v1/run_final_rank_repair_regression.py',
    'evals/plugin-v1/run_final_quality.py', 'evals/plugin-v1/run_quality.py',
    'evals/plugin-v1/evaluate_retrieval.py', 'evals/plugin-v1/quality-plan.json',
    'evals/plugin-v1/rubric.json', 'specs/retrieval/retrieval-policy.json',
    'plugins/myai-stackguide/scripts/recommendation_request.py',
    'plugins/myai-stackguide/scripts/retrieval.py',
    'plugins/myai-stackguide/scripts/request_guard.py',
    'plugins/myai-stackguide/scripts/context.py',
    'plugins/myai-stackguide/scripts/context_pack.py',
    'plugins/myai-stackguide/scripts/matcher.py',
}
spec = importlib.util.spec_from_file_location('rank_repair_capture', ROOT / 'evals/plugin-v1/run_final_quality.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.PLAN, runner.OUTPUT = PLAN, OUTPUT


def read_bound(path, digest):
    resolved = (ROOT / path).resolve()
    if not resolved.is_relative_to(ROOT) or runner.sha(resolved) != digest:
        raise ValueError('historical/current input hash mismatch: ' + path)
    return json.loads(resolved.read_bytes())


def load():
    plan = json.loads(PLAN.read_bytes())
    if plan['status'] != 'production_source_frozen' or plan['production_stability'] is None:
        raise ValueError('production stability has not been bound')
    required = REQUIRED_SOURCES | {plan['artifacts'][key] for key in ('manifest_path', 'cards_path', 'index_path', 'policy_path')}
    if not required <= set(plan['source_hashes']):
        raise ValueError('active source freeze incomplete')
    expected_cases = []
    base = None
    for suite in plan['suites']:
        source = read_bound(suite['plan_path'], suite['plan_sha256'])
        prior = read_bound(suite['capture_path'], suite['capture_sha256'])
        if [c['case_id'] for c in source['cases']] != suite['case_ids']:
            raise ValueError('suite case order changed')
        if [r['case_id'] for r in prior['records']] != suite['case_ids']:
            raise ValueError('prior capture identity/order mismatch')
        expected_cases.extend(source['cases'])
        if base is None:
            base = source
        for key in ('thresholds', 'stratification'):
            if plan[key] != source[key]:
                raise ValueError('frozen acceptance changed: ' + key)
    if plan['cases'] != expected_cases or len(expected_cases) != 30:
        raise ValueError('frozen union cases/grades/queries changed')
    if len({c['case_id'] for c in expected_cases}) != 30:
        raise ValueError('duplicate case identity')
    for key, value in base['pins'].items():
        if key not in {'policy_sha256', 'index_sha256'} and plan['pins'][key] != value:
            raise ValueError('non-policy/index corpus pin changed')
    for key, value in base['artifacts'].items():
        if key != 'manifest_sha256' and plan['artifacts'][key] != value:
            raise ValueError('artifact path/count changed')
    for receipt in plan['source_review_refs']:
        review = read_bound(receipt['path'], receipt['sha256'])
        if review.get('approved') is not True or review.get('unresolved') != []:
            raise ValueError('source review incomplete')
        if review[receipt['plan_field']] != receipt['reviewed_plan_sha256']:
            raise ValueError('source review plan mismatch')
        read_bound(receipt['reviewed_plan_path'], receipt['reviewed_plan_sha256'])
        read_bound(receipt['questions_path'], receipt['questions_sha256'])
        if review['source_questions_sha256'] != receipt['questions_sha256']:
            raise ValueError('source review questions mismatch')
    for path, digest in plan['source_hashes'].items():
        if runner.sha(ROOT / path) != digest:
            raise ValueError('active source hash mismatch: ' + path)
    for path, digest in plan['production_stability']['source_hashes'].items():
        if plan['source_hashes'].get(path) != digest:
            raise ValueError('production stability binding mismatch')
    projected = json.loads((ROOT / 'evals/plugin-v1/quality-plan.json').read_bytes())
    if projected['thresholds'] != plan['thresholds'] or projected['stratification'] != plan['stratification']:
        raise ValueError('accepted thresholds/stratification changed')
    projected['pins'] = copy.deepcopy(plan['pins'])
    projected['artifacts'] = copy.deepcopy(plan['artifacts'])
    runner.old.scorer.validate_quality_plan(projected)
    cards = json.loads((ROOT / plan['artifacts']['cards_path']).read_bytes())['cards']
    by_id = {c['identity']['github_repository_id']: c for c in cards}
    members, registry = runner.old.route_members(projected)
    for case in plan['cases']:
        ids = [j['github_repository_id'] for j in case['judgments']]
        routed = {rid for rid, c in by_id.items() if any(a['category_id'] in members[case['route']] for a in c['classifications'])}
        if len(ids) != len(set(ids)) or set(ids) != set(case['universe_ids']):
            raise ValueError('invalid oracle identities')
        if case['metric_family'] == 'semantic' and set(ids) != routed:
            raise ValueError('incomplete routed oracle')
        for row in case['judgments']:
            if type(row['grade']) is not int or not 0 <= row['grade'] <= 3:
                raise ValueError('unqualified role grade')
            card = by_id[row['github_repository_id']]
            if card['repository']['archived'] and row['constraint'] != 'denied':
                raise ValueError('archive oracle error')
            for evidence in row['evidence']:
                value = card
                for key in evidence['pointer'].strip('/').split('/'):
                    value = value[key]
                if value != evidence['value'] or evidence['source_ref'] not in runner.old.scorer.canonical(card).decode():
                    raise ValueError('source evidence mismatch')
    return plan, cards, by_id, members, registry


def suite_summary(rows, plan):
    semantic = [r for r in rows if r['metric_family'] == 'semantic']
    thresholds = plan['thresholds']
    candidate, literal = runner.macro(semantic, 'candidate'), runner.macro(semantic, 'baseline')
    strata = {}
    for field, values in [('tags', plan['stratification']['required_case_tags']), ('container_domain_ids', plan['stratification']['container_ids'])]:
        for value in values:
            if value == 'historical_alias':
                continue
            subset = [r for r in semantic if value in r[field]]
            strata[value] = dict(case_ids=[r['case_id'] for r in subset], candidate=runner.macro(subset, 'candidate'), baseline=runner.macro(subset, 'baseline'))
    gates = {}
    for metric, key in [('recall_at_k', 'held_out_macro_recall_at_12_min'), ('ndcg_at_k', 'held_out_macro_ndcg_at_12_min')]:
        gates[key] = candidate[metric] >= thresholds[key] if candidate else None
        gates['baseline_non_regression_' + metric] = candidate[metric] >= literal[metric] if candidate and literal else None
    gates['required_strata'] = runner.strata_pass([s['candidate'] for s in strata.values()], thresholds['required_stratum_recall_at_12_min'], thresholds['required_stratum_ndcg_at_12_min'])
    for key in ('hard_constraint_violations', 'false_exclusions', 'duplicate_canonical_ids'):
        total = sum(len(r['candidate'][key]) if isinstance(r['candidate'][key], list) else r['candidate'][key] for r in rows)
        gates[key] = total <= thresholds[key + '_max']
    aliases = [r['candidate']['alias_success'] for r in rows if r['metric_family'] == 'identity']
    gates['alias_success_rate_min'] = sum(aliases) / len(aliases) >= thresholds['alias_success_rate_min'] if aliases else None
    survived = sum(r['candidate']['positive_survived_count'] for r in semantic)
    positives = sum(r['candidate']['positive_top12_count'] for r in semantic)
    survival = survived / positives if positives and all(r['candidate']['pack_survival'] is not None for r in semantic) else None
    gates['evidence_pack_survival_rate_min'] = survival >= thresholds['evidence_pack_survival_rate_min'] if survival is not None else None
    gates['all_statuses_match'] = all(r['candidate']['status_ok'] for r in rows)
    return dict(candidate_macro=candidate, original_literal_macro=literal, strata=strata, gates=gates,
                official_pack_survival=survival, pack_counts=dict(numerator=survived, denominator=positives))


def compare(plan, summary):
    current = json.loads((OUTPUT / 'observations.json').read_bytes())['records']
    by_id = {r['case_id']: r for r in current}
    suites, changes = {}, []
    for suite in plan['suites']:
        prior = read_bound(suite['capture_path'], suite['capture_sha256'])['records']
        rows = [by_id[cid] for cid in suite['case_ids']]
        suites[suite['suite_id']] = suite_summary(rows, plan)
        for old, new in zip(prior, rows):
            if old['payload'] != new['payload'] or old['case_sha256'] != new['case_sha256']:
                raise ValueError('frozen payload/case changed')
            for field in ('raw_ranked_ids', 'ranking'):
                if old['baseline'][field] != new['baseline'][field]:
                    raise ValueError('original literal order/metrics changed')
            changes.append(dict(case_id=new['case_id'], suite_id=suite['suite_id'], prior_fts_ids=old['candidate']['raw_ranked_ids'],
                current_fts_ids=new['candidate']['raw_ranked_ids'], prior_metrics=old['candidate']['ranking'], current_metrics=new['candidate']['ranking'],
                original_literal_unchanged=True, previous_query=old['query'], current_query=new['query'],
                query_derivation=new['candidate_capture']['request'].get('query_derivation'), ranked_retrieval_calls=new['candidate_capture']['retrieval_calls']))
    passed = all(v is True for v in summary['gates'].values()) and all(v is True for s in suites.values() for v in s['gates'].values())
    summary.update(verdict='regression_verified_only' if passed else 'no_go', evidence_kind='exposed_two_suite_development_regression',
        regression_gates_pass=passed, suite_summaries=suites, comparisons=changes, fresh_unseen_evidence=False,
        human_acceptance=False, promotion_ready=False,
        acceptance_limit='Prior failures remain frozen. All30 goals/judgments are exposed. Legacy held_out threshold names are compatibility labels, not a fresh holdout claim. Prospective acceptance and human/browser checks remain open.')
    runner.write('regression-conclusion.json', summary)
    return summary


def declaration(plan):
    value = runner.declaration(plan)
    value.update(regression_runner_sha256=runner.sha(Path(__file__)), suites=plan['suites'], source_review_refs=plan['source_review_refs'],
        production_stability=plan['production_stability'], evidence_kind='exposed_two_suite_development_regression',
        fresh_unseen_evidence=False, human_acceptance=False,
        candidate='Stable source-text weighting and native COUNT conditional canonical-route vocabulary -> trusted C9 -> guard -> pack',
        count_scope='Read-only aggregate COUNT during query preparation; no ranked rows from preflight. Ranked captures contain one q1. Original literal scorer uses unchanged original case terms.',
        commands=['python -B evals/plugin-v1/run_final_rank_repair_regression.py --predeclare', 'python -B evals/plugin-v1/run_final_rank_repair_regression.py --run'])
    return value


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--predeclare', action='store_true')
    modes.add_argument('--run', action='store_true')
    args = parser.parse_args()
    try:
        plan, cards, by_id, members, registry = load()
        declared = declaration(plan)
        if args.predeclare:
            runner.check_freeze(OUTPUT)
            runner.write('declaration.json', declared)
            print(json.dumps(dict(declared=True, plan_sha256=runner.sha(PLAN), cases=30)))
            return 0
        if json.loads((OUTPUT / 'declaration.json').read_bytes()) != declared:
            raise ValueError('prospective declaration changed')
        if (OUTPUT / 'observations.json').exists():
            raise ValueError('capture already exists')
        summary = compare(plan, runner.capture(plan, cards, by_id, members, registry))
        print(json.dumps({k: summary[k] for k in ('verdict', 'regression_gates_pass', 'candidate_macro', 'original_literal_macro', 'gates')}))
        return 0 if summary['regression_gates_pass'] else 1
    except (ValueError, KeyError, FileExistsError, FileNotFoundError) as error:
        print(json.dumps(dict(status='invalid_protocol', reason=str(error))))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
