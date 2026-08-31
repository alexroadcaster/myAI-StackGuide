"""Normalize saved public aggregator JSON to a discovery pool, without network.

No aggregator value can pass the live GitHub Stars gate. Source URL, retrieval
time, source sync time and license attribution remain distinct and traceable.
"""
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

import enrich_catalog as e

PROVIDERS = {
    'ossinsight': {'hosts': {'api.ossinsight.io'}, 'license': 'not_verified_do_not_redistribute'},
    'ecosystems': {'hosts': {'repos.ecosyste.ms'}, 'license': 'CC-BY-SA-4.0'},
}


def import_snapshot(provider, path, source_url, retrieved_at, category, taxonomy):
    parsed = urlsplit(source_url)
    if parsed.scheme != 'https' or parsed.hostname not in PROVIDERS[provider]['hosts'] or parsed.username or parsed.password or parsed.fragment:
        raise ValueError('Expected a credential-free official provider URL')
    if any(key in parsed.query.casefold() for key in ('token', 'key', 'mailto', 'email')):
        raise ValueError('Sensitive URL parameters are forbidden')
    if datetime.fromisoformat(retrieved_at.replace('Z', '+00:00')).tzinfo is None:
        raise ValueError('Retrieval time needs an explicit timezone')
    leaves = {c['id'] for c in taxonomy['categories'] if c['kind'] == 'category'}
    if category is not None and category not in leaves:
        raise ValueError('Category hint must be an existing thematic category')
    raw = e.load(path)
    if provider == 'ossinsight':
        rows = raw.get('data', {}).get('rows') if isinstance(raw, dict) else None
    else:
        rows = raw if isinstance(raw, list) else [raw]
    if not isinstance(rows, list):
        raise ValueError('Unexpected provider snapshot shape')
    repositories = {}
    skipped = 0
    for row in rows:
        if not isinstance(row, dict):
            skipped += 1
            continue
        name = row.get('full_name') or row.get('repo_name') or row.get('name')
        if not isinstance(name, str) or not e.NAME.fullmatch(name):
            skipped += 1
            continue
        reported_stars = row.get('stargazers_count', row.get('stars'))
        if isinstance(reported_stars, str) and reported_stars.isdigit():
            reported_stars = int(reported_stars)
        if not isinstance(reported_stars, int) or isinstance(reported_stars, bool) or reported_stars < 0:
            reported_stars = None
        repositories[name.casefold()] = {
            'fullName': name, 'primaryCategory': category,
            'discovery': {'provider': provider, 'sourceUrl': source_url, 'retrievedAt': retrieved_at,
                          'sourceSyncedAt': row.get('last_synced_at'), 'inputSha256': e.sha(path),
                          'dataLicense': PROVIDERS[provider]['license'],
                          'status': 'aggregator_snapshot_not_live_GitHub_or_category_review'},
            'aggregatorSnapshot': {'stars': reported_stars,
                                   'description': e.clean_excerpt(row.get('description') or '')[:2000],
                                   'language': row.get('language'), 'license': row.get('license'),
                                   'pushedAt': row.get('pushed_at'),
                                   'topics': [e.clean_excerpt(x)[:100] for x in row.get('topics', []) if isinstance(x, str)]
                                       if isinstance(row.get('topics'), list) else []}}
    return {'provider': provider, 'scope': 'discovery_only_no_eligibility_decisions',
            'skippedRows': skipped, 'repositories': list(repositories.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=PROVIDERS, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-url', required=True)
    parser.add_argument('--retrieved-at', required=True, help='Actual retrieval time with timezone, not dataset freshness')
    parser.add_argument('--category', help='Optional search scope hint, not curator acceptance')
    parser.add_argument('--taxonomy', type=Path, default=e.ROOT / 'specs/catalog/taxonomy.yaml')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a new output path to preserve the earlier snapshot')
    result = import_snapshot(args.provider, args.input, args.source_url, args.retrieved_at,
                             args.category, e.load(args.taxonomy))
    e.atomic_json(args.output, result)
    print(f"Imported {len(result['repositories'])} discovery candidates; skipped {result['skippedRows']} rows; no network or LLM calls")


if __name__ == '__main__':
    main()
