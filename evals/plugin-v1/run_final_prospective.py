"""One prospective capture of new functional goals after source-only review.

Repository identities have mixed exposure. The already captured production
regression provides compatibility checks, never observations for these goals.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('prospective_regression', ROOT / 'evals/plugin-v1/run_final_rank_repair_regression.py')
regression = importlib.util.module_from_spec(spec)
spec.loader.exec_module(regression)
runner = regression.runner
BASE_PLAN = regression.PLAN
PLAN = ROOT / 'evals/plugin-v1/final-quality-prospective-2026-10-11.json'
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-final-quality-prospective-2026-10-11'
QUESTIONS = OUTPUT / 'source-review-questions.json'
DRAFT = OUTPUT / 'goal-authoring-draft.json'


def load():
    # The production loader enforces canonical policy, all source and artifact
    # hashes, historical receipts, and corpus contracts. It performs no ranking.
    runner.PLAN, runner.OUTPUT = BASE_PLAN, regression.OUTPUT
    base, cards, by_id, members, registry = regression.load()
    runner.PLAN, runner.OUTPUT = PLAN, OUTPUT
    plan = json.loads(PLAN.read_bytes())
    if plan['base_regression_plan_sha256'] != runner.sha(BASE_PLAN):
        raise ValueError('production compatibility plan mismatch')
    for key in ('pins', 'artifacts', 'thresholds', 'stratification', 'production_stability'):
        if plan[key] != base[key]:
            raise ValueError('stable acceptance/tuple mismatch: ' + key)
    required = set(base['source_hashes']) | {'evals/plugin-v1/run_final_prospective.py'}
    if not required <= set(plan['source_hashes']):
        raise ValueError('prospective source freeze incomplete')
    for path, digest in plan['source_hashes'].items():
        if runner.sha(ROOT / path) != digest:
            raise ValueError('prospective source hash mismatch: ' + path)
    if runner.sha(DRAFT) != plan['goal_draft_sha256'] or runner.sha(QUESTIONS) != plan['source_questions_sha256']:
        raise ValueError('pre-ranking source/goal draft changed')
    draft = json.loads(DRAFT.read_bytes())['goals']
    semantic = [c for c in plan['cases'] if c['metric_family'] == 'semantic']
    if len(semantic) != 14 or len(plan['cases']) != 15 or len({c['case_id'] for c in plan['cases']}) != 15:
        raise ValueError('case identity/coverage mismatch')
    if {v for c in semantic for v in c['container_domain_ids']} != set(plan['stratification']['container_ids']):
        raise ValueError('container coverage incomplete')
    if not set(plan['stratification']['required_case_tags']) <= {v for c in plan['cases'] for v in c['tags']}:
        raise ValueError('required tags missing')
    seen = {j['github_repository_id'] for c in base['cases'] for j in c['judgments']}
    questions = json.loads(QUESTIONS.read_bytes())['questions']
    all_ids = set()
    for case, authored, question in zip(semantic, draft, questions):
        for key in ('case_id', 'route', 'goal', 'terms', 'intent', 'language', 'universe_ids'):
            if case[key] != authored[key]:
                raise ValueError('initial prospective goal changed: ' + key)
        if question['case_id'] != case['case_id'] or question['full_routed_universe_ids'] != case['universe_ids']:
            raise ValueError('source question/oracle mismatch')
        ids = {j['github_repository_id'] for j in case['judgments']}
        routed = {rid for rid, card in by_id.items() if any(a['category_id'] in members[case['route']] for a in card['classifications'])}
        if ids != routed or ids != set(case['universe_ids']) or len(ids) != len(case['judgments']):
            raise ValueError('incomplete full-route oracle')
        all_ids |= ids
        if set(case['exposure']['source_seen_ids']) != ids & seen or set(case['exposure']['source_disjoint_ids']) != ids - seen:
            raise ValueError('source exposure classification mismatch')
        if case['exposure']['globally_unseen_repositories'] is not False:
            raise ValueError('invalid global novelty claim')
        if 'container_union' in case['tags'] and not any(r['route_id'] == case['route'] and r['route_kind'] == 'container' for r in registry):
            raise ValueError('invalid union tag')
        if 'secondary_dedupe' in case['tags'] and not any(len(by_id[rid]['classifications']) > 1 for rid in ids):
            raise ValueError('invalid secondary tag')
        flattened = [term for group in case['intent']['required_groups'] for term in group] + case['intent']['context_terms']
        if sorted(flattened) != sorted(case['terms']):
            raise ValueError('intent partition mismatch')
        positives = sum(j['grade'] > 0 and j['constraint'] != 'denied' for j in case['judgments'])
        if not positives or min(case['k'], positives) / positives < plan['thresholds']['required_stratum_recall_at_12_min']:
            raise ValueError('mathematically infeasible oracle capacity')
    if len(all_ids) != 244 or sum(len(c['judgments']) for c in semantic) != 244 or len(all_ids & seen) != 85 or len(all_ids - seen) != 159:
        raise ValueError('approved source scope changed')
    for case in plan['cases']:
        for row in case['judgments']:
            if type(row['grade']) is not int or not 0 <= row['grade'] <= 3:
                raise ValueError('unknown/invalid grade')
            card = by_id[row['github_repository_id']]
            if card['identity']['full_name'] != row['full_name']:
                raise ValueError('source identity mismatch')
            if card['repository']['archived'] and row['constraint'] != 'denied':
                raise ValueError('archived default oracle error')
            for evidence in row['evidence']:
                value = card
                for key in evidence['pointer'].strip('/').split('/'):
                    value = value[key]
                if value != evidence['value'] or evidence['source_ref'] not in runner.old.scorer.canonical(card).decode():
                    raise ValueError('source evidence mismatch')
    return plan, cards, by_id, members, registry


def review_binding(path):
    review = json.loads(path.read_bytes())
    if not review.get('reviewer') or review.get('approved') is not True or review.get('unresolved') != []:
        raise ValueError('source-only independent review incomplete')
    if review.get('source_questions_sha256') != runner.sha(QUESTIONS) or review.get('prospective_plan_sha256') != runner.sha(PLAN):
        raise ValueError('source review binding mismatch')
    return runner.sha(path)


def declaration(plan, review_path, review_sha):
    value = runner.declaration(plan)
    value.update(prospective_runner_sha256=runner.sha(Path(__file__)), review_path=review_path.as_posix(),
        source_review_sha256=review_sha, source_questions_sha256=runner.sha(QUESTIONS),
        evidence_kind='prospective_new_functional_goals_mixed_source_exposure', source_exposure=plan['prospective_scope'],
        globally_unseen_repositories=False, human_acceptance=False,
        candidate='Stable source-text weighting and COUNT-derived canonical route vocabulary; one q1 ranked capture',
        count_scope='One native read-only COUNT per preparation; no ranked rows during preflight. Original literal scorer keeps the original case terms.',
        commands=['python -B evals/plugin-v1/run_final_prospective.py --predeclare --review ' + review_path.as_posix(),
                  'python -B evals/plugin-v1/run_final_prospective.py --run --review ' + review_path.as_posix()])
    return value


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--predeclare', action='store_true')
    modes.add_argument('--run', action='store_true')
    parser.add_argument('--review', required=True)
    args = parser.parse_args()
    try:
        review_path = Path(args.review)
        resolved = (ROOT / review_path).resolve()
        if not resolved.is_relative_to(ROOT) or resolved.stat().st_size > 2 * 1024 * 1024:
            raise ValueError('invalid review path/size')
        plan, cards, by_id, members, registry = load()
        review_sha = review_binding(resolved)
        declared = declaration(plan, review_path, review_sha)
        if args.predeclare:
            runner.check_freeze(OUTPUT)
            runner.write('declaration.json', declared)
            print(json.dumps(dict(declared=True, plan_sha256=runner.sha(PLAN), source_review_sha256=review_sha, cases=15)))
            return 0
        if json.loads((OUTPUT / 'declaration.json').read_bytes()) != declared:
            raise ValueError('prospective declaration changed')
        if (OUTPUT / 'observations.json').exists():
            raise ValueError('capture already exists')
        summary = runner.capture(plan, cards, by_id, members, registry)
        records = json.loads((OUTPUT / 'observations.json').read_bytes())['records']
        unseen_cases = {c['case_id'] for c in plan['cases'] if c['metric_family'] == 'semantic' and not c['exposure']['source_seen_ids']}
        semantic = [r for r in records if r['metric_family'] == 'semantic']
        passed = all(v is True for v in summary['gates'].values())
        summary.update(verdict='prospective_local_retrieval_verified' if passed else 'no_go', retrieval_gates_pass=passed,
            evidence_kind='prospective_new_functional_goals_mixed_source_exposure', source_exposure=plan['prospective_scope'],
            disjoint_source_10case_macro=runner.macro([r for r in semantic if r['case_id'] in unseen_cases], 'candidate'),
            seen_source_4newgoal_macro=runner.macro([r for r in semantic if r['case_id'] not in unseen_cases], 'candidate'),
            source_review_sha256=review_sha, globally_unseen_repositories=False, promotion_ready=False, human_acceptance=False,
            acceptance_limit='New goals frozen before their first ranked capture, after ranker calibration on other goals. Mixed source exposure is explicit. Agent-authored full-route oracle and source-only review are local retrieval evidence; human usefulness, model interpretation, browser behavior and publication recovery are separate gates.')
        runner.write('prospective-conclusion.json', summary)
        print(json.dumps({k: summary[k] for k in ('verdict', 'retrieval_gates_pass', 'candidate_macro', 'original_literal_macro', 'gates')}))
        return 0 if passed else 1
    except (ValueError, KeyError, FileExistsError, FileNotFoundError) as error:
        print(json.dumps(dict(status='invalid_protocol', reason=str(error))))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
