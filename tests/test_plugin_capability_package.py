"""Source ownership and compatibility of an isolated enrichment package."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_plugin_capability_package as builder


class CapabilityPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original, _ = builder.catalog.build_snapshot()
        cls.source = builder.load_source()

    def test_precise_provenance_and_preserved_metadata(self):
        before = copy.deepcopy(self.original)
        enriched = builder.enrich(before, self.source)
        self.assertEqual(before, self.original)
        old = {c['identity']['github_repository_id']: c for c in before['cards']}
        changed = {f['github_repository_id'] for f in self.source['facts']}
        for card in enriched['cards']:
            rid = card['identity']['github_repository_id']
            for key in ('identity', 'catalog', 'repository', 'activity', 'delivery'):
                self.assertEqual(card[key], old[rid][key])
            if rid not in changed:
                self.assertEqual(card, old[rid])
                continue
            self.assertEqual(card['advisory']['eligibility'], old[rid]['advisory']['eligibility'])
            field = '/advisory/use_cases/' + str(len(old[rid]['advisory']['use_cases']))
            evidence = [e for e in card['evidence'] if field in e['fields']]
            self.assertEqual(len(evidence), 1)
            self.assertEqual(evidence[0]['source_kind'], 'upstream_document')
            self.assertFalse(any('/advisory' in e['fields'] for e in card['evidence']))
        self.assertNotEqual(enriched['catalog_snapshot_id'], before['catalog_snapshot_id'])

    def test_reject_bad_identity_duplicate_and_untrusted_source(self):
        for mutation in ('name', 'duplicate', 'url', 'overflow'):
            source = copy.deepcopy(self.source)
            if mutation == 'name':
                source['facts'][0]['full_name'] = 'wrong/name'
            elif mutation == 'duplicate':
                source['facts'].append(copy.deepcopy(source['facts'][0]))
            elif mutation == 'url':
                source['facts'][0]['source_url'] = 'https://example.com/untrusted'
            else:
                source['facts'][0]['capability'] = 'x' * 601
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                builder.enrich(self.original, source)

    def test_deterministic_complete_card_schema(self):
        first = builder.enrich(self.original, self.source)
        self.assertEqual(builder.catalog.canonical_bytes(first),
                         builder.catalog.canonical_bytes(builder.enrich(self.original, self.source)))
        self.assertEqual(len(first['cards']), 2500)
        builder.validate_cards(first['cards'])


if __name__ == '__main__':
    unittest.main()
