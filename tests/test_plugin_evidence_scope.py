"""Actual multi-card scoped evidence join plus adversarial ownership checks."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EvidenceScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('cp04_evidence_scope_contracts', ROOT / 'tests/test_plugin_contracts.py')
        cls.helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.helper)
        snapshot = json.loads((ROOT / 'plugins/myai-stackguide/assets/catalog.snapshot.json').read_text(encoding='utf-8'))
        cls.cards = snapshot['cards'][:2]
        observations = json.loads((ROOT / 'evals/plugin-v1/results/cp04-v2-2026-10-08/development-observations.json').read_text(encoding='utf-8'))
        cls.calibration = next(item for item in observations['captures'] if item['case_id'] == 'CP04-V2-D05')
        spec = importlib.util.spec_from_file_location('cp04_evidence_scope_matcher',
            ROOT / 'plugins/myai-stackguide/scripts/matcher.py')
        cls.matcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.matcher)

    def setUp(self):
        self.state = {'scan': None, 'brief': None,
                      'evidence_pack': {'cards': [{'card': copy.deepcopy(card)} for card in self.cards]}}

    def test_actual_two_cards_accept_repeated_local_evidence_ids(self):
        evidence = self.helper.canonical_evidence(self.state)
        for card in self.cards:
            self.assertEqual(self.helper.resolve_evidence(evidence, 'ev-catalog-card',
                owner=card['identity']['github_repository_id']), card['evidence'][0])

    def test_actual_cards_use_source_owned_ancestor_evidence_fields(self):
        for card in self.cards:
            self.helper.check_card(card)

    def test_public_commit_observation_cannot_borrow_push_source_field(self):
        card = copy.deepcopy(self.cards[0])
        observation = next(item for item in card['activity']['observations'] if item['field'] == 'last_commit_at')
        observation['source_field'] = 'activity.pushedAt'
        with self.assertRaisesRegex(ValueError, 'activity source-field conflation'):
            self.helper.check_card(card)

    def test_public_activity_cannot_claim_arbitrary_source_field(self):
        card = copy.deepcopy(self.cards[0])
        card['activity']['observations'][0]['source_field'] = 'activity.inventedTimestamp'
        with self.assertRaisesRegex(ValueError, 'activity source-field conflation'):
            self.helper.check_card(card)

    def test_actual_d05_missing_advisory_stays_unknown_reference_only(self):
        for entry in self.calibration['candidate_evidence_pack']['cards']:
            self.assertEqual(entry['eligibility']['status'], 'reference_only')
            self.helper.check_eligibility(entry['eligibility'], entry['card'], self.calibration['query'])

    def test_missing_advisory_cannot_be_forged_as_pass_or_primary(self):
        entry = copy.deepcopy(self.calibration['candidate_evidence_pack']['cards'][0])
        eligibility = entry['eligibility']
        next(item for item in eligibility['checks'] if item['field'] == 'advisory_evidence')['outcome'] = 'pass'
        eligibility.update(status='primary_eligible', reason_codes=[], required_verifications=[])
        with self.assertRaisesRegex(ValueError, 'unsupported advisory_evidence outcome'):
            self.helper.check_eligibility(eligibility, entry['card'], self.calibration['query'])

    def test_unknown_advisory_cannot_reference_invented_source(self):
        entry = copy.deepcopy(self.calibration['candidate_evidence_pack']['cards'][0])
        next(item for item in entry['eligibility']['checks'] if item['field'] == 'advisory_evidence')['evidence_refs'] = ['ev-invented']
        with self.assertRaisesRegex(ValueError, 'unresolved eligibility evidence'):
            self.helper.check_eligibility(entry['eligibility'], entry['card'], self.calibration['query'])

    def test_complete_sourced_advisory_is_not_replaced_by_catalog_stage(self):
        state = self.helper.workspace_baseline()
        card = state['evidence_pack']['cards'][0]['card']
        card['catalog']['evidence_stage'] = 'identity_validated'
        query = state['request']['query']
        eligibility = self.matcher.match_candidate(card, query)
        self.assertEqual(eligibility['status'], 'primary_eligible')
        self.helper.check_eligibility(eligibility, card, query)

    def test_complete_unsourced_advisory_stays_unknown_and_cannot_promote(self):
        for missing_source in ('partial_coverage', 'unknown_verification'):
            with self.subTest(missing_source=missing_source):
                state = self.helper.workspace_baseline()
                card = state['evidence_pack']['cards'][0]['card']
                evidence = card['evidence'][0]
                if missing_source == 'partial_coverage':
                    evidence['fields'].remove('/advisory/use_cases')
                else:
                    evidence['verification'] = 'unknown'
                query = state['request']['query']
                eligibility = self.matcher.match_candidate(card, query)
                check = next(item for item in eligibility['checks'] if item['field'] == 'advisory_evidence')
                self.assertEqual(check['outcome'], 'unknown')
                self.assertEqual(eligibility['status'], 'reference_only')
                self.assertIn('insufficient_evidence', eligibility['reason_codes'])
                self.helper.check_eligibility(eligibility, card, query)
                wrong_reason = copy.deepcopy(eligibility)
                wrong_reason['reason_codes'] = ['mandatory_fact_unknown']
                with self.assertRaisesRegex(ValueError, 'unknown facts need concrete next checks'):
                    self.helper.check_eligibility(wrong_reason, card, query)
                check['outcome'] = 'pass'
                eligibility['status'] = 'primary_eligible'
                with self.assertRaisesRegex(ValueError, 'unsupported advisory_evidence outcome'):
                    self.helper.check_eligibility(eligibility, card, query)

    def test_missing_advisory_cannot_claim_only_source_coverage_reason(self):
        entry = copy.deepcopy(self.calibration['candidate_evidence_pack']['cards'][0])
        entry['eligibility']['reason_codes'] = ['insufficient_evidence']
        with self.assertRaisesRegex(ValueError, 'unknown facts need concrete next checks'):
            self.helper.check_eligibility(entry['eligibility'], entry['card'], self.calibration['query'])

    def test_ancestor_coverage_cannot_accept_sibling_or_root_fields(self):
        for forbidden in ('/catalogue', '/'):
            card = copy.deepcopy(self.cards[0])
            card['evidence'][0]['fields'] = [forbidden]
            with self.assertRaisesRegex(ValueError, 'catalog acceptance provenance'):
                self.helper.check_card(card)

    def test_arbitrary_public_source_ref_forgery_stays_rejected_by_pinned_card_check(self):
        path = ROOT / 'plugins/myai-stackguide/scripts/context_pack.py'
        spec = importlib.util.spec_from_file_location('cp04_scope_pinned_cards', path)
        pack = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pack)
        pins = json.loads((ROOT / 'plugins/myai-stackguide/assets/catalog.search-manifest.json').read_text(encoding='utf-8'))['pins']
        forged = copy.deepcopy(self.cards[0])
        forged['evidence'][0]['source_ref'] = 'https://github.com/unowned/forged'
        repo_id = forged['identity']['github_repository_id']
        with self.assertRaisesRegex(ValueError, 'supplied card does not match pinned'):
            pack._trusted_cards(pins, {repo_id: forged}, [repo_id])

    def test_presentation_binding_uses_allowed_field_owner_and_rejects_wrong_owner(self):
        state = self.helper.workspace_baseline()
        first = state['evidence_pack']['cards'][0]['card']
        second = copy.deepcopy(first)
        second['identity']['github_repository_id'] += 1
        second['evidence'][0]['evidence_id'] = 'only-other-owner'
        state['evidence_pack']['cards'].append({'card': second})
        recommendation = state['memo']['recommendations'][0]
        recommendation['evidence_refs'] = ['only-other-owner']
        text = recommendation['fit_rationale']
        state['presentation']['fields'] = [{'field_pointer': '/memo/recommendations/0/fit_rationale',
            'source_locale': 'en', 'source_sha256': self.helper.digest(text), 'source_content_revision': state['content_revision'],
            'evidence_refs': ['only-other-owner'], 'canonical_literals': self.helper.field_literals(state, text),
            'en': {'status': 'available', 'text': text}, 'ru': {'status': 'unavailable', 'text': None}}]
        self.helper.rebind_presentation(state)
        with self.assertRaisesRegex(ValueError, 'unresolved evidence'):
            self.helper.check_workspace(state)

    def test_unowned_public_reference_is_ambiguous_even_if_payloads_identical(self):
        self.state['evidence_pack']['cards'][1]['card']['evidence'][0] = copy.deepcopy(self.cards[0]['evidence'][0])
        evidence = self.helper.canonical_evidence(self.state)
        with self.assertRaisesRegex(ValueError, 'ambiguous evidence'):
            self.helper.resolve_evidence(evidence, 'ev-catalog-card')

    def test_wrong_repository_cannot_borrow_another_cards_evidence(self):
        second = self.state['evidence_pack']['cards'][1]['card']
        second['evidence'][0]['evidence_id'] = 'only-second-card'
        evidence = self.helper.canonical_evidence(self.state)
        with self.assertRaisesRegex(ValueError, 'unresolved evidence'):
            self.helper.resolve_evidence(evidence, 'only-second-card', owner=self.cards[0]['identity']['github_repository_id'])

    def test_duplicate_within_one_card_is_invalid_even_if_identical(self):
        self.state['evidence_pack']['cards'][0]['card']['evidence'].append(copy.deepcopy(self.cards[0]['evidence'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate card evidence'):
            self.helper.canonical_evidence(self.state)

    def test_contradictory_project_evidence_still_fails(self):
        first = {'evidence_id': 'project-ref', 'relative_path': 'src/a.py'}
        self.state['scan'] = {'summary': {'facts': [], 'evidence': [first]}}
        self.state['brief'] = {'observations': {'facts': [], 'evidence': [{**first, 'relative_path': 'src/b.py'}]}}
        with self.assertRaisesRegex(ValueError, 'contradictory duplicate evidence'):
            self.helper.canonical_evidence(self.state)

    def test_project_only_resolution_cannot_use_public_source(self):
        evidence = self.helper.canonical_evidence(self.state)
        with self.assertRaisesRegex(ValueError, 'unresolved evidence'):
            self.helper.resolve_evidence(evidence, 'ev-catalog-card', project_only=True)

    def test_allowlisted_presentation_owner_is_numeric_not_prose(self):
        self.state['memo'] = {'recommendations': [{'github_repository_id': self.cards[0]['identity']['github_repository_id'],
            'fit_rationale': 'Mentions the other repository; ownership stays explicit.'}],
            'avoid_defer_details': [{'github_repository_id': self.cards[1]['identity']['github_repository_id']}],
            'comparison_details': {'cells': [{'baseline': False, 'github_repository_id': self.cards[1]['identity']['github_repository_id']}]}}
        self.assertEqual(self.helper.field_evidence_owner(self.state, '/memo/recommendations/0/fit_rationale'),
                         self.cards[0]['identity']['github_repository_id'])
        self.assertEqual(self.helper.field_evidence_owner(self.state, '/memo/avoid_defer_details/0/reason/text'),
                         self.cards[1]['identity']['github_repository_id'])
        self.assertIsNone(self.helper.field_evidence_owner(self.state, '/memo/summary'))

    def test_owned_claim_cannot_use_wrong_repository_evidence(self):
        self.state['evidence_pack']['cards'][1]['card']['evidence'][0]['evidence_id'] = 'only-second-card'
        claim = {'kind': 'observed', 'evidence_refs': ['only-second-card'], 'answer_ids': []}
        with self.assertRaisesRegex(ValueError, 'unresolved evidence'):
            self.helper.check_claim(claim, self.helper.canonical_evidence(self.state), set(),
                                    allow_public=True, owner=self.cards[0]['identity']['github_repository_id'])


if __name__ == '__main__':
    unittest.main()
