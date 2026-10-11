"""Independently recompute documented conflicts; never trust selection labels."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / 'evals/plugin-v1/results/cp04-final-guard-2026-10-11/observations.json'
FACTS = ROOT / 'research/cp04-request-dependency-evidence-2026-10-11.json'


def audit(capture, facts):
    by_id = {f['github_repository_id']: f for f in facts}
    rows = []
    for row in capture['records']:
        interpretation = row['payload']['interpretation']
        result = row['capture']
        if interpretation['unresolved']:
            passed = result['retrieval_calls'] == 0 and result['evidence_pack'] is None and result['status'] == 'needs_clarification'
            rows.append(dict(case_id=row['case_id'], clarification_passed=passed, passed=passed))
            continue
        forbidden = set(interpretation['excluded_dependencies'])
        denied = set(interpretation['excluded_repository_ids'])
        # A documented conflict exists only when every known mode requires at
        # least one forbidden dependency. Missing facts remain unknown.
        conflicts = {rid for rid, fact in by_id.items() if forbidden and fact['alternatives'] and
                     all(any(dep in forbidden for dep in mode) for mode in fact['alternatives'])}
        blocked = denied | conflicts
        selected = set(result['selected_ids'])
        pack_ids = {entry['card']['identity']['github_repository_id'] for entry in result['evidence_pack']['cards']}
        raw = set(result['raw_ranked_ids'])
        violations = sorted((selected | pack_ids) & blocked)
        unknown = sorted(rid for rid in selected if forbidden and rid not in by_id)
        annotated = set(result['selection']['verification_required'])
        rows.append(dict(case_id=row['case_id'], independently_denied_ids=sorted(blocked),
                         blocked_raw_ids=sorted(raw & blocked), violations=violations,
                         unknown_selected_ids=unknown, unknowns_annotated=set(unknown) <= annotated,
                         passed=not violations and set(unknown) <= annotated and pack_ids <= selected))
    return dict(records=rows, passed=all(r['passed'] for r in rows),
                positive_control_blocked_hits=sum(len(r.get('blocked_raw_ids', [])) for r in rows),
                evidence_scope='Independent source-fact recomputation on exposed structured Brief cases; no natural-language interpretation or model proof',
                human_acceptance=False)


if __name__ == '__main__':
    result = audit(json.loads(CAPTURE.read_bytes()), json.loads(FACTS.read_bytes())['facts'])
    result['source_hashes'] = {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (Path(__file__), CAPTURE, FACTS)}
    output = CAPTURE.parent / 'independent-conflict-audit.json'
    if output.exists():
        raise ValueError('preserve prior audit')
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'], positive_control_blocked_hits=result['positive_control_blocked_hits'])))
    raise SystemExit(0 if result['passed'] else 1)
