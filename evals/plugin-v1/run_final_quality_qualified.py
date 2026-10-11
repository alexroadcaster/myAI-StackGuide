"""Reviewed source-qualified replay, preserving the exposed original experiment.

The unchanged runtime, query and original literal baseline are executed again.
Only source-backed oracle corrections may differ; this is regression evidence.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('qualified_original', ROOT/'evals/plugin-v1/run_final_quality.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
BASE = runner.PLAN
runner.PLAN = ROOT/'evals/plugin-v1/final-quality-qualified-2026-10-11.json'
runner.OUTPUT = ROOT/'evals/plugin-v1/results/cp04-final-quality-qualified-2026-10-11'
QUESTIONS = runner.OUTPUT/'source-questions.json'
REVIEW_SCHEMA = 'cp04_source_qualification_review_v1'


def verify_scope(plan):
    base = json.loads(BASE.read_bytes())
    if plan['base_plan_sha256'] != runner.sha(BASE):
        raise ValueError('original freeze mismatch')
    if len(plan['cases']) != len(base['cases']):
        raise ValueError('case coverage changed')
    allowed_rows = {j['github_repository_id'] for j in json.loads(QUESTIONS.read_bytes())['questions']}
    allowed_archived = {12820537, 79585104, 29261473}
    for old, new in zip(base['cases'], plan['cases']):
        if runner.make_payload(old) != runner.make_payload(new):
            raise ValueError('case query/Brief/constraints changed')
        previous = {j['github_repository_id']: j for j in old['judgments']}
        current = {j['github_repository_id']: j for j in new['judgments']}
        if set(previous) != set(current):
            raise ValueError('judgment universe changed')
        for rid, row in current.items():
            if row != previous[rid] and rid not in allowed_rows | allowed_archived:
                raise ValueError('unapproved judgment scope')
        for key in set(old) - {'judgments'}:
            if old[key] != new[key]:
                raise ValueError('case settings changed')
    for key in ('pins','artifacts','thresholds','stratification'):
        if base[key] != plan[key]:
            raise ValueError('accepted settings changed')


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--predeclare', action='store_true')
    mode.add_argument('--run', action='store_true')
    parser.add_argument('--review', required=True)
    args = parser.parse_args()
    try:
        path = (ROOT/args.review).resolve()
        if not path.is_relative_to(ROOT) or path.stat().st_size > 2*1024*1024:
            raise ValueError('invalid review path/size')
        review = json.loads(path.read_bytes())
        if review.get('schema_version') != REVIEW_SCHEMA or not review.get('reviewer') or review.get('approved') is not True or review.get('unresolved') != []:
            raise ValueError('independent source review incomplete/unapproved')
        if review.get('source_questions_sha256') != runner.sha(QUESTIONS) or review.get('qualified_plan_sha256') != runner.sha(runner.PLAN):
            raise ValueError('review input binding mismatch')
        plan, cards, by_id, members, registry = runner.load()
        verify_scope(plan)
        declared = runner.declaration(plan)
        declared.update(source_review_path=str(path.relative_to(ROOT)).replace('\\','/'),
            source_review_sha256=runner.sha(path),qualification_runner_sha256=runner.sha(Path(__file__)),
            exposure='Source-qualified replay of already-exposed original cases; no new unseen or promotion evidence.',
            commands=['.venv/Scripts/python.exe -B evals/plugin-v1/run_final_quality_qualified.py --predeclare --review '+args.review,
                      '.venv/Scripts/python.exe -B evals/plugin-v1/run_final_quality_qualified.py --run --review '+args.review])
        if args.predeclare:
            runner.check_freeze(runner.OUTPUT)
            runner.write('declaration.json',declared)
            print(json.dumps(dict(declared=True,plan_sha256=runner.sha(runner.PLAN),review_sha256=runner.sha(path))))
            return 0
        if json.loads((runner.OUTPUT/'declaration.json').read_bytes()) != declared:
            raise ValueError('qualified declaration mismatch')
        if (runner.OUTPUT/'observations.json').exists():
            raise ValueError('qualified capture already exists')
        summary = runner.capture(plan,cards,by_id,members,registry)
        summary.update(evidence_kind='observed_source_qualified_exposed_regression',
            fresh_unseen_evidence=False,source_review_sha256=runner.sha(path),
            snapshot_fit_not_current_adoption=True,current_adoption_notes=plan['current_adoption_notes'])
        runner.write('qualified-conclusion.json',summary)
        print(json.dumps({k:summary[k] for k in ('verdict','candidate_macro','original_literal_macro','gates','incomplete_oracle_cases')}))
        return 1
    except (ValueError,KeyError,FileExistsError,FileNotFoundError) as exc:
        print(json.dumps(dict(status='invalid_protocol',reason=str(exc))))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
