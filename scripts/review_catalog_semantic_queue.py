"""Resolve CAT-06 review decisions without inventing semantic claims.

Accept only exact upstream descriptions and a minimal observed-language Stack.
Every other requested semantic field receives an explicit unresolved decision.
Replacement search leads are not qualified without repository-level evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import enrich_catalog as e
import catalog_gap_fill as g


def write(path, value):
    e.atomic_json(path, value)


def observed(record, ref):
    return record.get('blocks', {}).get(ref, {}).get('status') == 'observed'


def merge_curation(record, accepted):
    current = record.get('curation') or {'sourceId': record['sourceId'], 'fields': {}, 'evidenceRefs': {}}
    merged = json.loads(json.dumps(current))
    merged.setdefault('fields', {}).update(accepted['fields'])
    merged.setdefault('evidenceRefs', {}).update(accepted['evidenceRefs'])
    merged['sourceId'] = record['sourceId']
    merged['reviewedAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    return merged


def run_review(run, apply=False):
    review_path = run / 'gap-reports' / 'review.json'
    replacement_path = run / 'gap-reports' / 'replacement-proposals.json'
    if not review_path.is_file() or not replacement_path.is_file():
        raise ValueError('CAT-05 reports are required')
    items = e.load(review_path)['items']
    proposals = e.load(replacement_path)['items']
    decisions = []
    fragments = {}
    counts = Counter()

    for item in sorted(items, key=lambda row: row['sourceId']):
        record_path = run / item['evidenceArtifact']
        record = e.load(record_path)
        values = record.get('values', {})
        accepted = {'fields': {}, 'evidenceRefs': {}}
        field_decisions = []
        for field in sorted(item['fields']):
            decision = {'field': field}
            if field == 'catalogDescription':
                description = values.get('catalogDescription')
                metadata_description = record.get('blocks', {}).get('metadata', {}).get('data', {}).get('description')
                if (isinstance(description, str) and description.strip() and description == metadata_description
                        and values.get('descriptionOrigin') == 'upstream' and observed(record, 'metadata')):
                    accepted['fields'].update(catalogDescription=description, descriptionOrigin='upstream')
                    accepted['evidenceRefs'].update(catalogDescription=['metadata'], descriptionOrigin=['metadata'])
                    decision.update(status='accepted_exact_upstream', evidenceRefs=['metadata'])
                    counts['accepted_catalogDescription'] += 1
                else:
                    decision.update(status='unresolved_no_exact_upstream_description')
                    counts['unresolved_catalogDescription'] += 1
            elif field == 'stack':
                language = values.get('language')
                ref = None
                if isinstance(language, str) and language.strip():
                    languages = record.get('blocks', {}).get('languages', {}).get('data', {})
                    if observed(record, 'languages') and language in languages:
                        ref = 'languages'
                    elif observed(record, 'metadata'):
                        ref = 'metadata'
                if ref:
                    stack = [{'technology': language, 'evidenceRefs': [ref]}]
                    accepted['fields']['stack'] = stack
                    accepted['evidenceRefs']['stack'] = [ref]
                    decision.update(status='accepted_minimal_observed_stack', value=stack, evidenceRefs=[ref],
                                    completeness='primary_language_only')
                    counts['accepted_stack'] += 1
                else:
                    decision.update(status='unresolved_no_observed_primary_language')
                    counts['unresolved_stack'] += 1
            else:
                requirement = 'mandatory' if field.startswith('recommendation.') else 'optional_or_contextual'
                decision.update(status='unresolved_requires_source_specific_curator_review', requirement=requirement)
                counts['unresolved_other_semantic'] += 1
            field_decisions.append(decision)
        if accepted['fields']:
            fragments[item['sourceId']] = merge_curation(record, accepted)
        decisions.append({'sourceId': item['sourceId'], 'record': item['evidenceArtifact'],
                          'fieldDecisions': field_decisions,
                          'acceptedFragment': accepted if accepted['fields'] else None})

    replacement_decisions = []
    for ident, proposal in sorted(proposals.items()):
        candidates = []
        for candidate in proposal.get('candidates', []):
            candidates.append({'fullName': candidate.get('fullName'),
                               'githubRepositoryId': candidate.get('githubRepositoryId'),
                               'stars': candidate.get('stars'),
                               'decision': 'rejected_insufficient_functional_evidence',
                               'reason': 'metadata_identity_stars_language_and_description_do_not_prove_same_category_function'})
            counts['replacement_candidates_rejected'] += 1
        replacement_decisions.append({
            'sourceId': ident,
            'excludedFullName': proposal.get('excludedFullName'),
            'candidates': candidates,
            'decision': 'replacement_unresolved_after_candidate_review',
            'nextAction': 'collect_candidate_readme_and_mandatory_card_or_expand_search',
        })
        counts['replacement_items_unresolved'] += 1

    output = run / 'semantic-review' / 'decisions'
    write(output / 'semantic-decisions.json', {'items': decisions})
    write(output / 'replacement-decisions.json', {'items': replacement_decisions})
    curation_dir = output / 'accepted-curation'
    for ident, fragment in fragments.items():
        write(curation_dir / (hashlib.sha256(ident.encode()).hexdigest() + '.json'), fragment)

    if apply:
        def offline(*_):
            raise RuntimeError('CAT-06 application attempted network access')
        collector = e.Collector(run, offline)
        for ident in sorted(fragments):
            collector.process(ident, fragments[ident], blocks=set())
        g.GapFill(run, offline).reports()

    latest = e.load(run / 'gap-reports' / 'summary.json')
    summary = {
        'scope': 'cat06_evidence_bounded_decisions',
        'reviewItems': len(items),
        'semanticFieldDecisions': sum(len(item['fieldDecisions']) for item in decisions),
        'acceptedCurationFragments': len(fragments),
        'decisionCounts': dict(counts),
        'replacementItems': len(replacement_decisions),
        'automaticReplacements': 0,
        'networkCalls': 0,
        'LLMCalls': 0,
        'appliedToCheckpoint': apply,
        'canonicalWritten': False,
        'postApplyGapSummary': latest,
    }
    write(output / 'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    run_review(args.run_dir.resolve(), args.apply)


if __name__ == '__main__':
    main()
