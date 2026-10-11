"""Compare saved independent first passes and bridge exact portable records."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'evals/plugin-v1/results/cp04-final-answer-projection-2026-10-11'
NEW = ROOT / 'evals/plugin-v1/results/cp04-final-answer-projection-portable-2026-10-11'

if __name__ == '__main__':
    product = json.loads((OLD / 'product-review.json').read_bytes())
    quality = json.loads((OLD / 'quality-review.json').read_bytes())
    original = json.loads((OLD / 'observations.json').read_bytes())
    portable = json.loads((NEW / 'observations.json').read_bytes())
    assert original['records'] == portable['records'], 'portable identity mismatch'
    q = {(r['case_id'], r['locale']): r for r in quality['records']}
    rows = []
    for case in product['cases']:
        for locale, review in case['locales'].items():
            other = q[(case['case_id'], locale)]
            assert review['answer_sha256'] == other['answer_sha256']
            first = {d['dimension']: d['score'] for d in review['original_scores']}
            second = {d['dimension']: d['score'] for d in other['dimensions']}
            assert first.keys() == second.keys()
            diffs = {name: abs(first[name] - second[name]) for name in first}
            critical = review['critical_dimension_scores']
            assert all(first[name] == second[name] for name in critical)
            assert max(diffs.values()) <= 1
            assert not review['critical_failures'] and not other['critical_failures']
            rows.append(dict(case_id=case['case_id'], locale=locale,
                             product_total=review['original_total'], quality_total=other['total'],
                             dimension_differences=diffs, critical_agreement=True,
                             answer_sha256=review['answer_sha256']))
    result = dict(evidence_kind='Saved independent agent first passes; exact portable identity bridge',
                  cases=rows, dimension_pairs=sum(len(r['dimension_differences']) for r in rows),
                  agreement_passed=True, human_acceptance=False, human_calibration=False,
                  promotion_ready=False,
                  source_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (Path(__file__), OLD / 'product-review.json', OLD / 'quality-review.json',
                                           OLD / 'observations.json', NEW / 'observations.json')})
    output = NEW / 'independent-score-agreement.json'
    if output.exists():
        raise ValueError('preserve prior agreement')
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(agreement_passed=True, cases=len(rows), dimension_pairs=result['dimension_pairs'])))
