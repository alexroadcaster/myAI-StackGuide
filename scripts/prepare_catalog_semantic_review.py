"""Build compact, deterministic CAT-06 review packets from CAT-05 evidence.

This script performs no network or LLM calls and accepts no semantic value or
replacement. It reduces the saved evidence to bounded review inputs and keeps
unresolved factual fields separate from curator-owned semantic decisions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


SEMANTIC_SOURCE_PREFIX = 'curator:'
WORD = re.compile(r'[a-z0-9]+')
STOP = {'and', 'the', 'for', 'with', 'tools', 'tool', 'platform', 'management'}


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def compact_text(value, limit=2400):
    if not isinstance(value, str):
        return None
    value = ' '.join(value.split())
    return value[:limit] if value else None


def chunks(items, size):
    for offset in range(0, len(items), size):
        yield items[offset:offset + size]


def category_tokens(label):
    return sorted({word for word in WORD.findall((label or '').casefold()) if word not in STOP and len(word) > 2})


def replacement_signals(candidate, category_label, source_language):
    haystack = ' '.join(str(candidate.get(key) or '') for key in ('fullName', 'description')).casefold()
    tokens = category_tokens(category_label)
    return {
        'samePrimaryLanguage': bool(source_language and candidate.get('language') == source_language),
        'categoryLabelTokensMatched': [token for token in tokens if token in haystack],
        'categoryLabelTokensTotal': len(tokens),
        'semanticFitDecision': 'review_required',
    }


def build(run: Path, output: Path, batch_size: int, replacement_batch_size: int):
    report = run / 'gap-reports'
    required = [run / 'input.json', run / 'taxonomy.json', run / 'field-contract.json',
                report / 'review.json', report / 'replacement-proposals.json', report / 'summary.json']
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ValueError('Missing CAT-05 input: ' + ', '.join(missing))
    if batch_size < 1 or replacement_batch_size < 1:
        raise ValueError('Batch sizes must be positive')

    source = {row['id']: row for row in load(run / 'input.json')['repositories']}
    taxonomy = {row['id']: row for row in load(run / 'taxonomy.json')['categories']}
    contract = load(run / 'field-contract.json')
    semantic_fields = {row['id'] for row in contract['fields']
                       if row.get('source', '').startswith(SEMANTIC_SOURCE_PREFIX)}
    review_items = load(report / 'review.json')['items']
    packets = []
    fact_gaps = []

    for item in sorted(review_items, key=lambda row: row['sourceId']):
        ident = item['sourceId']
        record_path = run / item['evidenceArtifact']
        record = load(record_path)
        hint_path = run / 'extracted' / record_path.name
        hints = load(hint_path) if hint_path.is_file() else {}
        values = record.get('values', {})
        source_row = source[ident]
        category_id = values.get('primaryCategory') or source_row.get('primaryCategory')
        category = taxonomy.get(category_id, {})
        semantic_missing = sorted(set(item['fields']) & semantic_fields)
        factual_missing = sorted(set(item['fields']) - semantic_fields)
        observed_refs = sorted(key for key, block in record.get('blocks', {}).items()
                               if block.get('status') == 'observed')
        readme = record.get('blocks', {}).get('readme', {}).get('data', {}).get('excerpt')
        packets.append({
            'sourceId': ident,
            'fullName': values.get('fullName') or source_row['fullName'],
            'category': {'id': category_id, 'label': category.get('label')},
            'stars': values.get('stars'),
            'semanticFieldsNeedingReview': semantic_missing,
            'currentSemanticValues': {field: values.get(field) for field in sorted(semantic_fields)
                                      if values.get(field) not in (None, '', [], {})},
            'evidence': {
                'observedRefs': observed_refs,
                'upstreamDescription': compact_text(hints.get('upstreamDescription'), 1000),
                'readmeExcerpt': compact_text(readme, 2400),
                'dependencyDeclarations': hints.get('dependencies', [])[:20],
                'primaryLanguage': values.get('language'),
                'languages': values.get('languages'),
                'topics': values.get('topics'),
                'licenseSpdx': values.get('license.spdx'),
                'archived': values.get('archived'),
                'lastCommitAt': values.get('activity.lastCommitAt'),
            },
            'decision': {
                'status': 'review_required',
                'automaticAcceptance': False,
                'requiredEvidenceRefsMustBeObserved': True,
            },
        })
        if factual_missing:
            fact_gaps.append({'sourceId': ident, 'fullName': source_row['fullName'],
                              'fields': factual_missing, 'record': item['evidenceArtifact']})

    proposals = load(report / 'replacement-proposals.json')['items']
    replacement_packets = []
    for ident, proposal in sorted(proposals.items()):
        source_row = source[ident]
        category_id = source_row.get('primaryCategory')
        category_label = taxonomy.get(category_id, {}).get('label')
        record_name = hashlib.sha256(ident.encode()).hexdigest() + '.json'
        record = load(run / 'records' / record_name)
        source_language = record.get('values', {}).get('language')
        candidates = []
        for candidate in proposal.get('candidates', []):
            candidates.append({**candidate,
                               'signals': replacement_signals(candidate, category_label, source_language),
                               'automaticAcceptance': False})
        replacement_packets.append({
            'sourceId': ident,
            'excludedFullName': proposal.get('excludedFullName'),
            'observedStars': record.get('values', {}).get('stars'),
            'category': {'id': category_id, 'label': category_label},
            'sourceLanguage': source_language,
            'candidates': candidates,
            'decision': 'review_required' if candidates else 'expanded_search_required',
            'automaticReplacement': False,
        })

    semantic_dir = output / 'semantic-batches'
    replacement_dir = output / 'replacement-batches'
    for index, batch in enumerate(chunks(packets, batch_size), 1):
        write_json(semantic_dir / f'batch-{index:04d}.json', {'items': batch})
    for index, batch in enumerate(chunks(replacement_packets, replacement_batch_size), 1):
        write_json(replacement_dir / f'batch-{index:04d}.json', {'items': batch})
    write_json(output / 'factual-gaps.json', {'items': fact_gaps})

    semantic_counts = Counter(field for packet in packets for field in packet['semanticFieldsNeedingReview'])
    summary = {
        'scope': 'cat06_review_packets_no_automatic_semantic_acceptance',
        'sourceRun': str(run),
        'pins': {str(path.relative_to(run)): sha(path) for path in required},
        'semanticReviewItems': len(packets),
        'semanticBatches': (len(packets) + batch_size - 1) // batch_size,
        'semanticFieldCounts': dict(semantic_counts.most_common()),
        'factualGapItems': len(fact_gaps),
        'replacementReviewItems': len(replacement_packets),
        'replacementBatches': (len(replacement_packets) + replacement_batch_size - 1) // replacement_batch_size,
        'replacementItemsWithCandidates': sum(bool(item['candidates']) for item in replacement_packets),
        'expandedSearchRequired': sum(not item['candidates'] for item in replacement_packets),
        'networkCalls': 0,
        'LLMCalls': 0,
        'automaticSemanticAcceptances': 0,
        'automaticReplacements': 0,
        'canonicalWritten': False,
    }
    write_json(output / 'summary.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--batch-size', type=int, default=10)
    parser.add_argument('--replacement-batch-size', type=int, default=20)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    output = args.output_dir.resolve() if args.output_dir else run / 'semantic-review'
    print(json.dumps(build(run, output, args.batch_size, args.replacement_batch_size), ensure_ascii=False))


if __name__ == '__main__':
    main()
