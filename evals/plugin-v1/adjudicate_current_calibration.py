"""Preserve independent grades and conservatively reconcile formal answers."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'evals/plugin-v1/results/cp04-final-current-calibration-2026-10-11'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    product = json.loads((BASE / 'product-review.json').read_bytes())
    quality = json.loads((BASE / 'quality-review.json').read_bytes())
    rubric = json.loads((ROOT / 'evals/plugin-v1/rubric.json').read_bytes())['human']
    observation_sha = sha(BASE / 'observations.json')
    assert product['observations_sha256'] == quality['observations_sha256'] == observation_sha
    q = {(row['case_id'], row['locale']): row for row in quality['records']}
    rows = []
    for case in product['cases']:
        for locale, review in case['locales'].items():
            other = q[(case['case_id'], locale)]
            assert review['answer_sha256'] == other['answer_sha256']
            first = {d['dimension']: d['score'] for d in review['original_scores']}
            second = {d['dimension']: d['score'] for d in other['dimensions']}
            assert set(first) == set(second) == set(rubric['dimensions'])
            differences = {name: abs(first[name] - second[name]) for name in first}
            # The rubric requires agreement on critical pass/fail, not identical scores.
            for name in rubric['critical_dimensions']:
                assert (first[name] >= rubric['critical_dimension_minimum']) == (
                    second[name] >= rubric['critical_dimension_minimum'])
            assert max(differences.values()) <= 1, 'requires explicit further adjudication'
            assert not review['critical_failures'] and not other['critical_failures']
            final = {name: min(first[name], second[name]) for name in first}
            assert sum(final.values()) >= rubric['minimum_total']
            rows.append(dict(case_id=case['case_id'], human_calibration_case_id=case['human_calibration_case_id'],
                             locale=locale, answer_sha256=other['answer_sha256'],
                             product_scores=first, quality_scores=second, final_scores=final,
                             product_total=sum(first.values()), quality_total=sum(second.values()),
                             final_total=sum(final.values()), differences=differences,
                             critical_pass_agreement=True, unresolved=[]))
    assert len(rows) == 8
    output = BASE / 'independent-score-agreement.json'
    assert not output.exists(), 'preserve frozen adjudication'
    result = dict(schema_version='cp04_current_formal_adjudication_v1',
                  reviewer_identities=[product['reviewer'], quality['reviewer']], adjudicator='/root',
                  rule='Conservative minimum of original scores; rubric critical-pass agreement and per-dimension difference <=1.',
                  records=rows, dimension_pairs=80, agreement_passed=True,
                  human_calibration=False, human_acceptance=False, agent_proxy=True, promotion_ready=False,
                  source_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in (
                      Path(__file__), BASE / 'product-review.json', BASE / 'quality-review.json',
                      BASE / 'observations.json', ROOT / 'evals/plugin-v1/rubric.json')})
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(agreement_passed=True, dimension_pairs=80, final_totals=[r['final_total'] for r in rows])))


if __name__ == '__main__':
    main()
