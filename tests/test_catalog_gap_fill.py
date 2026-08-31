"""Selective collection and gh transport boundaries; fake public data only."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import enrich_catalog as e
import catalog_gap_fill as gaps
import github_cli_transport as transport
from tests.test_catalog_enrichment import FakeAPI


class SelectiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.run = self.base / 'run'
        self.source = self.base / 'source.json'
        data = e.load(ROOT / 'data/catalog_manifest.json')
        self.row = copy.deepcopy(data['repositories'][0])
        self.row.update(id='gh:unit/repo', fullName='unit/repo', githubRepositoryId=None, stars=900,
                        description='Existing curated description', catalogStatus='candidate')
        data['repositories'] = [self.row]
        e.atomic_json(self.source, data)
        e.create_plan(self.run, self.source, ROOT / 'specs/catalog/taxonomy.yaml', ROOT / 'specs/catalog/enrichment-field-contract.json')
        self.api = FakeAPI()

    def test_metadata_only_does_not_fetch_readme_languages_or_history(self):
        result = e.Collector(self.run, self.api).process(self.row['id'], blocks=set())
        self.assertEqual(len(self.api.calls), 1)
        self.assertEqual(set(result['blocks']), {'metadata'})

    def test_successor_rebinds_derived_timestamps_without_refetch_or_counter_reset(self):
        plan = e.load(self.run / 'plan.json')
        plan['createdAt'] = '2020-01-01T00:00:00Z'
        e.atomic_json(self.run / 'plan.json', plan)
        collector = e.Collector(self.run, self.api)
        original = collector.process(self.row['id'], blocks=set())
        root = self.base / 'workspace'
        for target, source in [('data/catalog_manifest.json', self.source),
                               ('specs/catalog/taxonomy.yaml', ROOT / 'specs/catalog/taxonomy.yaml'),
                               ('specs/catalog/enrichment-field-contract.json', ROOT / 'specs/catalog/enrichment-field-contract.json')]:
            path = root / target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(source.read_bytes())
        successor = self.base / 'successor'
        with patch.object(gaps.e, 'ROOT', root):
            gaps.prepare(successor, self.run)
        migrated = e.Collector(successor, self.api)
        self.assertEqual(migrated.verify()['verifiedRecords'], 1)
        self.assertEqual(migrated.state, collector.state)
        self.assertEqual(e.load(migrated.record_path(self.row['id']))['blocks'], original['blocks'])
        self.assertEqual(len(self.api.calls), 1)

    def test_only_missing_language_group_uses_two_calls_and_cached_resume(self):
        result = e.Collector(self.run, self.api).process(self.row['id'], blocks={'languages'})
        self.assertEqual(set(result['blocks']), {'metadata', 'languages'})
        self.assertEqual(len(self.api.calls), 2)
        e.Collector(self.run, self.api).process(self.row['id'], blocks={'languages'})
        self.assertEqual(len(self.api.calls), 2)

    def test_false_and_zero_are_filled_except_star_check(self):
        self.assertFalse(gaps.missing(False))
        self.assertFalse(gaps.missing(0))
        row = {**self.row, 'forks': 0, 'archived': False, 'stars': 0}
        item = gaps.targets(row, e.load(self.run / 'field-contract.json'))
        self.assertNotIn('forks', item['fields'])
        self.assertNotIn('archived', item['fields'])
        self.assertTrue(item['checkStars'])
        self.assertNotIn('description', item['fields'])
        self.assertNotIn('catalogDescription', item['fields'])
        self.assertNotIn('full_name', item['fields'])

    def test_unauthorized_stops_without_content_requests(self):
        self.api.failures['/repos/unit/repo'] = (401, {}, b'{"message":"Bad credentials"}')
        collector = e.Collector(self.run, self.api)
        collector.process(self.row['id'], blocks={'languages'})
        collector.process(self.row['id'], blocks={'languages'})
        self.assertEqual(len(self.api.calls), 1)
        self.assertEqual(collector.state['haltReason'], 'authentication_failed')

    def test_permissions_do_not_masquerade_as_exhausted_quota(self):
        self.api.failures['/repos/unit/repo'] = (403, {'x-ratelimit-remaining': '4999'}, b'{"message":"Resource not accessible"}')
        collector = e.Collector(self.run, self.api)
        result = collector.process(self.row['id'], blocks=set())
        self.assertEqual(result['blocks']['metadata']['reason'], 'permission_denied')
        self.assertEqual(collector.state['retryNotBefore'], 0)

    def test_patch_projection_preserves_filled_description_and_high_stars(self):
        record = e.Collector(self.run, self.api).process(self.row['id'], blocks=set())
        job = object.__new__(gaps.GapFill)
        job.run = self.run
        job.c = e.Collector(self.run, self.api)
        job.config = {'targets': {self.row['id']: gaps.targets(self.row, job.c.contract)}}
        job.state = {'processed': [self.row['id']], 'proposals': {}}
        job.reports()
        edits = e.load(self.run / 'gap-reports/patches.json')['edits']
        self.assertTrue(any(x['field'] == 'githubRepositoryId' for x in edits))
        self.assertFalse(any(x['field'] in ('description', 'stars', 'primaryCategory') for x in edits))
        self.assertEqual(e.load(self.source)['repositories'][0], self.row)

    def test_verified_low_star_correction_is_the_only_nonempty_overwrite(self):
        self.row['stars'] = 100
        data = e.load(self.source)
        data['repositories'] = [self.row]
        e.atomic_json(self.source, data)
        run = self.base / 'low'
        e.create_plan(run, self.source, ROOT / 'specs/catalog/taxonomy.yaml', ROOT / 'specs/catalog/enrichment-field-contract.json')
        collector = e.Collector(run, self.api)
        collector.process(self.row['id'], blocks=set())
        job = object.__new__(gaps.GapFill)
        job.run, job.c = run, collector
        job.config = {'targets': {self.row['id']: gaps.targets(self.row, collector.contract)}}
        job.state = {'processed': [self.row['id']], 'proposals': {}}
        job.reports()
        edits = e.load(run / 'gap-reports/patches.json')['edits']
        star = next(x for x in edits if x['field'] == 'stars')
        self.assertEqual((star['before'], star['after']), (100, 777))


class CLITransportTests(unittest.TestCase):
    def test_payment_replacements_require_sdk_and_compatible_language(self):
        self.assertFalse(gaps.replacement_candidate({'full_name': 'stripe/stripe-react-native', 'description': 'React Native library for Stripe.', 'language': 'TypeScript'}, 'payment_processing_sdks', 'JavaScript'))
        self.assertFalse(gaps.replacement_candidate({'full_name': 'ripple/ripple-client', 'description': 'A UI for a payment network', 'language': 'JavaScript'}, 'payment_processing_sdks', 'JavaScript'))
        self.assertFalse(gaps.replacement_candidate({'full_name': 'someone/awesome-payments', 'description': 'A curated list', 'language': 'Python'}, 'payment_processing_sdks', 'Python'))
        self.assertFalse(gaps.replacement_candidate({'full_name': 'someone/payment-sdk', 'description': 'Payment SDK', 'language': 'Java'}, 'payment_processing_sdks', 'Python'))
        self.assertTrue(gaps.replacement_candidate({'full_name': 'someone/payment-sdk', 'description': 'Payment client library', 'language': 'TypeScript'}, 'payment_processing_sdks', 'JavaScript'))

    def test_only_bounded_public_search_and_rate_endpoints_added(self):
        transport.validate_url(e.API + '/rate_limit')
        transport.validate_url(e.API + '/search/repositories?q=python+is%3Apublic+stars%3A%3E%3D500&per_page=10')
        for url in [e.API + '/user', e.API + '/search/repositories?q=secret',
                    e.API + '/rate_limit?token=x', 'https://other.test/repos/a/b',
                    e.API + '/search/repositories?q=is%3Apublic&per_page=100']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                transport.validate_url(url)

    def test_response_parser_handles_error_and_http2(self):
        code, headers, body = transport.parse_response(b'HTTP/2.0 403 Forbidden\r\nX-Ratelimit-Remaining: 42\r\n\r\n{"message":"Forbidden"}')
        self.assertEqual(code, 403)
        self.assertEqual(headers['x-ratelimit-remaining'], '42')
        self.assertEqual(json.loads(body)['message'], 'Forbidden')

    def test_no_http_response_fails_closed_without_echoing_cli_output(self):
        with self.assertRaisesRegex(RuntimeError, 'no HTTP response'):
            transport.parse_response(b'ghp_fake-secret-not-to-echo')


if __name__ == '__main__':
    unittest.main()
