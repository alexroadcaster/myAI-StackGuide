"""Preserve independent current-answer scores and reconcile conservatively.

This is an agent-proxy evidence check. It never records human acceptance.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'evals/plugin-v1/results/cp04-final-host-calibration-allocation-2026-10-11'
WORK = ROOT / 'work/cp04-final'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    product_path = WORK / 'host-allocation-answer-product-review.json'
    quality_path = WORK / 'host-allocation-answer-quality-review.json'
    observation_path = BASE / 'observations.json'
    rubric_path = ROOT / 'evals/plugin-v1/rubric.json'
    rubric = json.loads(rubric_path.read_bytes())['human']
    sources = [Path(__file__), product_path, quality_path, observation_path, rubric_path]
    reviews = [json.loads(path.read_bytes()) for path in (product_path, quality_path)]
    expected = {(row['case_id'], locale)
                for row in json.loads(observation_path.read_bytes())['records']
                for locale in ('ru', 'en')}
    assert len(expected) == 8
    indexed = []
    for review in reviews:
        assert review['observations_sha256'] == sha(observation_path)
        assert review['human_acceptance'] is False
        rows = review['records']
        mapping = {(row['case_id'], row['locale']): row for row in rows}
        assert len(rows) == len(mapping) == 8 and set(mapping) == expected
        indexed.append(mapping)
    results, failures = [], []
    for case_id, locale in sorted(expected):
        path = BASE / case_id / ('answer-' + locale + '.md')
        sources.append(path)
        scores = []
        for mapping in indexed:
            row = mapping[(case_id, locale)]
            # Product binds normalized narrative text and its exported file
            # separately; Quality's answer hash binds the exported file.
            assert row.get('answer_file_sha256', row['answer_sha256']) == sha(path)
            values = {dimension['dimension']: dimension['score'] for dimension in row['dimensions']}
            assert len(row['dimensions']) == len(values) == 10
            assert set(values) == set(rubric['dimensions'])
            assert all(type(value) is int and value in (0, 1, 2) for value in values.values())
            assert sum(values.values()) == row['total']
            if row['critical_failures']:
                failures.append(case_id + '/' + locale + ':critical_failure')
            scores.append(values)
        difference = {name: abs(scores[0][name] - scores[1][name]) for name in scores[0]}
        final = {name: min(scores[0][name], scores[1][name]) for name in scores[0]}
        critical_agreement = all(
            (scores[0][name] >= rubric['critical_dimension_minimum']) ==
            (scores[1][name] >= rubric['critical_dimension_minimum'])
            for name in rubric['critical_dimensions'])
        if not critical_agreement or max(difference.values()) > 1:
            failures.append(case_id + '/' + locale + ':requires_explicit_adjudication')
        if sum(final.values()) < rubric['minimum_total'] or any(
                final[name] < rubric['critical_dimension_minimum'] for name in rubric['critical_dimensions']):
            failures.append(case_id + '/' + locale + ':rubric_floor')
        results.append(dict(case_id=case_id, locale=locale, answer_sha256=sha(path),
                            product_scores=scores[0], quality_scores=scores[1],
                            final_scores=final, product_total=sum(scores[0].values()),
                            quality_total=sum(scores[1].values()), final_total=sum(final.values()),
                            differences=difference, critical_pass_agreement=critical_agreement))
    result = dict(schema_version='cp04_host_formal_adjudication_v1', adjudicator='/root',
                  rule='Conservative minimum; critical-pass agreement and dimension difference <=1.',
                  records=results, dimension_pairs=80, failures=failures,
                  agreement_passed=not failures, human_calibration=False,
                  human_acceptance=False, agent_proxy=True, promotion_ready=False,
                  source_hashes={path.relative_to(ROOT).as_posix(): sha(path) for path in sources})
    with (WORK / 'host-allocation-answer-score-agreement.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(dict(agreement_passed=not failures, dimension_pairs=80,
                         totals=[row['final_total'] for row in results], failures=failures)))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
