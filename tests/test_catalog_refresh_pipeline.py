"""Offline batch and replacement semantics, including rate stops and restart."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalog_refresh_pipeline as p
import import_catalog_discovery as discovery
from tests import test_catalog_enrichment as fixtures


class MultipleAPI(fixtures.FakeAPI):
    def __init__(self, stars, identities=None):
        super().__init__()
        self.star_map = stars
        self.identities = identities or {name: i + 100 for i, name in enumerate(stars)}

    def __call__(self, url, timeout, max_bytes):
        code, headers, body = super().__call__(url, timeout, max_bytes)
        path = urlsplit(url).path
        if path.count('/') == 3 and code == 200:
            name = '/'.join(path.split('/')[2:4])
            data = json.loads(body)
            data.update(id=self.identities[name], full_name=name,
                        html_url='https://github.com/' + name, stargazers_count=self.star_map[name])
            body = json.dumps(data).encode()
        return code, headers, body


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.run = self.base / 'run'
        self.source = self.base / 'source.json'
        self.pool = self.base / 'pool.json'

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self, names=('unit/a', 'unit/b'), candidates=(), batch_size=25, identities=None):
        repositories = [{'id': 'gh:' + name, 'fullName': name, 'stars': 0,
                         'catalogStatus': 'candidate', 'primaryCategory': 'backend_frameworks',
                         'githubRepositoryId': (identities or {}).get(name)} for name in names]
        p.e.atomic_json(self.source, {'repositories': repositories})
        p.e.atomic_json(self.pool, [{'fullName': name, 'primaryCategory': 'backend_frameworks',
                                   'stars': 1000000} for name in candidates])
        p.e.create_plan(self.run, self.source,
                        ROOT / 'specs/catalog/taxonomy.yaml',
                        ROOT / 'specs/catalog/enrichment-field-contract.json', max_requests=90)
        p.prepare(self.run, [self.pool], batch_size=batch_size)

    def review(self, ident, category='backend_frameworks'):
        review = fixtures.EnrichmentTests.review(self)
        review['sourceId'] = ident
        review['fields']['primaryCategory'] = category
        import hashlib
        p.e.atomic_json(self.run / 'curation' / (hashlib.sha256(ident.encode()).hexdigest() + '.json'), review)

    def test_batch_collects_multiple_unreviewed_cards_and_resume_does_not_refetch(self):
        self.prepare()
        api = MultipleAPI({'unit/a': 500, 'unit/b': 600})
        result = p.Pipeline(self.run, api).batch()
        self.assertEqual(result['processedThisBatch'], 2)
        self.assertEqual(result['reviewQueueSize'], 2)
        self.assertFalse(result['wholeCorpusComplete'])
        self.assertEqual(result['LLMCalls'], 0)
        calls = len(api.calls)
        result = p.Pipeline(self.run, api).batch()
        self.assertEqual(result['processedThisBatch'], 0)
        self.assertEqual(len(api.calls), calls)

    def test_low_star_exclusion_then_candidate_before_next_original_and_automatic_swap(self):
        self.prepare(candidates=['unit/c'])
        self.review('gh-replacement:unit/c')
        api = MultipleAPI({'unit/a': 499, 'unit/b': 600, 'unit/c': 500})
        result = p.Pipeline(self.run, api).batch()
        self.assertEqual(api.calls[:2], [p.e.API + '/repos/unit/a', p.e.API + '/repos/unit/c'])
        self.assertEqual(sum('/unit/a' in u for u in api.calls), 1)
        self.assertEqual(result['resolvedReplacements'], 1)
        projection = p.e.load(self.run / 'reports/active-candidate.json')
        self.assertEqual(len(projection['rows']), 2)
        self.assertEqual(projection['rows'][0]['kind'], 'verified_replacement')
        self.assertEqual(projection['rows'][0]['values']['fullName'], 'unit/c')
        self.assertEqual(p.e.load(self.source)['repositories'][0]['fullName'], 'unit/a')

    def test_unreviewed_candidate_never_swapped_or_overcollected(self):
        self.prepare(names=['unit/a'], candidates=['unit/c', 'unit/d'])
        api = MultipleAPI({'unit/a': 0, 'unit/c': 1000, 'unit/d': 900})
        result = p.Pipeline(self.run, api).batch()
        self.assertEqual(result['replacementCandidates'], 1)
        self.assertEqual(result['resolvedReplacements'], 0)
        self.assertEqual(p.e.load(self.run / 'reports/active-candidate.json')['rows'], [])
        self.assertFalse(any('/unit/d' in u for u in api.calls))
        self.review('gh-replacement:unit/c')
        calls = len(api.calls)
        self.assertEqual(p.Pipeline(self.run, api).batch()['resolvedReplacements'], 1)
        self.assertEqual(len(api.calls), calls)

    def test_historical_candidate_stars_do_not_pass_live_gate(self):
        self.prepare(names=['unit/a'], candidates=['unit/c', 'unit/d'])
        api = MultipleAPI({'unit/a': 0, 'unit/c': 400, 'unit/d': 700})
        result = p.Pipeline(self.run, api).batch()
        self.assertEqual(sum('/unit/c' in u for u in api.calls), 1)
        self.assertEqual(result['replacementCandidates'], 2)
        self.assertEqual(result['resolvedReplacements'], 0)

    def test_category_mismatch_does_not_swap(self):
        self.prepare(names=['unit/a'], candidates=['unit/c'])
        self.review('gh-replacement:unit/c', 'api_graphql_rpc')
        result = p.Pipeline(self.run, MultipleAPI({'unit/a': 0, 'unit/c': 500})).batch()
        self.assertEqual(result['resolvedReplacements'], 0)

    def test_duplicate_numeric_identity_does_not_replace_or_hide_original(self):
        self.prepare(candidates=['unit/c'])
        self.review('gh-replacement:unit/c')
        api = MultipleAPI({'unit/a': 0, 'unit/b': 600, 'unit/c': 600},
                          {'unit/a': 100, 'unit/b': 101, 'unit/c': 101})
        result = p.Pipeline(self.run, api).batch()
        self.assertEqual(result['resolvedReplacements'], 0)
        self.assertEqual(result['inputStates']['identity_review_required'], 1)
        projection = p.e.load(self.run / 'reports/active-candidate.json')
        self.assertEqual(projection['rows'][0]['values']['fullName'], 'unit/b')

    def test_identity_conflict_never_excludes_original(self):
        self.prepare(names=['unit/a'], identities={'unit/a': 444})
        api = MultipleAPI({'unit/a': 0}, {'unit/a': 555})
        result = p.Pipeline(self.run, api).batch()
        self.assertEqual(result['inputStates']['identity_review_required'], 1)
        self.assertFalse(result['wholeCorpusComplete'])
        self.assertEqual(len(p.e.load(self.run / 'reports/active-candidate.json')['rows']), 1)

    def test_quota_stop_has_no_loop_sleep_or_next_repo_requests(self):
        self.prepare()
        api = MultipleAPI({'unit/a': 600, 'unit/b': 700})
        def limited(*args):
            code, headers, body = api(*args)
            headers.update({'x-ratelimit-remaining': '0', 'x-ratelimit-reset': str(int(p.time.time()) + 3600)})
            return code, headers, body
        with patch.object(p.time, 'sleep', side_effect=AssertionError('Must return, not wait')):
            result = p.Pipeline(self.run, limited).batch()
            self.assertEqual(result['stopReason'], 'rate_limit_wait')
            self.assertEqual(len(api.calls), 1)
            p.Pipeline(self.run, limited).batch()
            self.assertEqual(len(api.calls), 1)

    def test_batch_limit_and_resume_reaches_next_untouched_record(self):
        self.prepare(batch_size=1)
        api = MultipleAPI({'unit/a': 600, 'unit/b': 700})
        self.assertEqual(p.Pipeline(self.run, api).batch()['processedThisBatch'], 1)
        self.assertEqual(p.Pipeline(self.run, api).batch()['processedThisBatch'], 1)
        self.assertEqual(sum(u.endswith('/unit/a') for u in api.calls), 1)

    def test_unknown_stars_preserved_as_unknown_and_not_excluded(self):
        self.prepare(names=['unit/a'])
        result = p.Pipeline(self.run, MultipleAPI({'unit/a': None})).batch()
        self.assertEqual(result['inputStates']['needs_review_or_retry'], 1)
        self.assertEqual(p.e.load(self.run / 'reports/exclusion-replacements.json')['items'], [])

    def test_changed_input_or_pool_fails_before_network(self):
        self.prepare()
        self.pool.write_text('[]', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Discovery pool changed'):
            p.Pipeline(self.run)

    def test_manifest_extraction_excludes_dev_dependencies_and_never_claims_review(self):
        content = json.dumps({'dependencies': {'react': '^19'}, 'devDependencies': {'vitest': '*'}})
        record = {'blocks': {'file:package.json': {'status': 'observed',
                            'data': {'excerpt': content, 'path': 'package.json', 'ref': 'abc'}}}}
        hints = p.extracted_hints(record)
        self.assertEqual([f['declaration'] for f in hints['dependencies']], ['react'])
        self.assertEqual(hints['status'], 'source_declarations_not_reviewed_stack')

    def test_aggregator_import_preserves_snapshot_without_live_or_review_claims(self):
        path = self.base / 'ossinsight.json'
        p.e.atomic_json(path, {'data': {'rows': [{'repo_name': 'unit/a', 'stars': '1234'}, {'name': 'collection name'}]}})
        result = discovery.import_snapshot('ossinsight', path,
                    'https://api.ossinsight.io/v1/collections/2/repos/', '2026-08-31T15:00:00Z',
                    'backend_frameworks', {'categories': [{'id': 'backend_frameworks', 'kind': 'category'}]})
        self.assertEqual(result['skippedRows'], 1)
        row = result['repositories'][0]
        self.assertNotIn('stars', row)
        self.assertEqual(row['aggregatorSnapshot']['stars'], 1234)
        self.assertIsNone(row['discovery']['sourceSyncedAt'])
        self.assertIn('not_live', row['discovery']['status'])

    def test_aggregator_import_rejects_credential_url_and_naive_timestamp(self):
        for url, at in [('https://api.ossinsight.io/x?api_key=secret', '2026-08-31T15:00:00Z'),
                        ('https://api.ossinsight.io/x', '2026-08-31T15:00:00')]:
            with self.assertRaises(ValueError):
                discovery.import_snapshot('ossinsight', self.pool, url, at, None, {})

    def test_ecosystems_import_retains_license_and_sync_time(self):
        p.e.atomic_json(self.pool, [{'full_name': 'unit/a', 'stargazers_count': 0, 'last_synced_at': '2025-01-01T00:00:00Z'}])
        result = discovery.import_snapshot('ecosystems', self.pool,
                    'https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/unit%2Fa',
                    '2026-08-31T15:00:00Z', None, {'categories': []})
        row = result['repositories'][0]
        self.assertEqual(row['aggregatorSnapshot']['stars'], 0)
        self.assertEqual(row['discovery']['dataLicense'], 'CC-BY-SA-4.0')
        self.assertNotEqual(row['discovery']['sourceSyncedAt'], row['discovery']['retrievedAt'])


if __name__ == '__main__':
    unittest.main()
