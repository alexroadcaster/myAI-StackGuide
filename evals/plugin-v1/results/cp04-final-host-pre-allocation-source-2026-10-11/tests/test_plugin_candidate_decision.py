"""Behavioral checks for the separately versioned transient host decision boundary."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'plugins/myai-stackguide/scripts'))
import recommendation_decision as decision
from test_plugin_brief_request import brief, interpretation
import test_plugin_contracts as contracts


class CandidateDecision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = brief()
        cls.i = interpretation(cls.b)
        cls.session = decision.prepare(cls.b, cls.i)
        if not isinstance(cls.session, decision.DecisionSession):
            raise AssertionError(cls.session)
        broad = copy.deepcopy(cls.i)
        broad.update(route=None, terms=['api'], intent=dict(required_groups=[['api']], context_terms=[]), excluded_repository_ids=[])
        cls.broad = decision.prepare(cls.b, broad)
        if not isinstance(cls.broad, decision.DecisionSession):
            raise AssertionError(cls.broad)

    def fresh(self, broad=False):
        return copy.deepcopy(self.broad if broad else self.session)

    def order(self, session):
        return [r['github_repository_id'] for r in session.preview_request['candidates']]

    def validate(self, artifact):
        schema = contracts.load('specs/retrieval/candidate-decision.schema.json')
        registry = contracts.Registry().with_resources(
            (s['$id'], contracts.Resource.from_contents(s))
            for s in [*contracts.SCHEMAS.values(), schema])
        contracts.Draft202012Validator(schema, registry=registry,
            format_checker=contracts.FormatChecker()).validate(artifact)

    def test_missing_host_order_is_needs_selection_and_cannot_deliver_native_pack(self):
        session=self.fresh()
        result=decision.finalize(session)
        self.assertEqual(result['status'],'needs_selection',
            'Expected behavioral RED: native preference cannot substitute for the missing host decision')
        self.assertIsNone(result['evidence_pack'])
        self.validate(result)

    def test_reversed_complete_order_preserves_exact_native_scores_and_full_ranks(self):
        session = self.fresh()
        order = self.order(session)[::-1]
        result = decision.finalize(session, order)
        receipt, pack = result['decision_receipt'], result['decision_pack']
        self.assertEqual(receipt['decision_order'], order)
        original = {r['github_repository_id']: r for r in session.native_result['candidates']}
        for record in pack['cards']:
            rid = record['card']['identity']['github_repository_id']
            self.assertEqual(record['retrieval_rank'], original[rid]['rank'])
            self.assertEqual(record['rrf_score'], original[rid]['rrf_score'])
            self.assertEqual(record['matched_fields'], original[rid]['matched_fields'])
            self.assertEqual(record['decision_rank'], order.index(rid) + 1)
            self.assertEqual(record['card'], session._data['cards'][rid])
        self.assertEqual(receipt['preview_request_sha256'], decision.digest(session.preview_request))
        self.assertEqual(pack['decision_receipt_sha256'], decision.digest(receipt))
        self.assertEqual(pack['bindings'], receipt['bindings'])
        self.assertEqual(pack['bindings'], session.preview_request['bindings'])
        self.assertNotEqual([r['decision_rank'] for r in pack['cards']],
                            [r['retrieval_rank'] for r in pack['cards']])
        for artifact in (session.preview_request, receipt, pack):
            self.validate(artifact)

    def test_real_max150_pool_keeps_all_ids_and_one_shared_ledger(self):
        session = self.fresh(broad=True)
        preview = session.preview_request
        self.assertEqual(len(preview['candidates']), 150)
        self.assertEqual(self.order(session), session.control['raw_ranked_ids'])
        self.assertEqual(preview['bindings']['native_result_sha256'], decision.digest(session.native_result))
        result = decision.finalize(session, self.order(session)[::-1])
        pack, receipt = result['decision_pack'], result['decision_receipt']
        ids = [r['card']['identity']['github_repository_id'] for r in pack['cards']] + [e['github_repository_id'] for e in pack['exclusions']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(self.order(session)))
        self.assertGreaterEqual(len(pack['cards']), 1)
        self.assertGreater(pack['cards'][0]['decision_rank'], 1,
            'Oversized earlier cards are skipped and a later real eligible record fits')
        self.assertLessEqual(len(pack['cards']), 12)
        self.assertEqual(pack['status'], 'limited')
        self.assertTrue(pack['truncated'])
        self.assertTrue(any(e['reason_codes'] == ['context_budget'] for e in pack['exclusions']))
        actual = len(decision.canonical_bytes(dict(preview_request=preview, decision_receipt=receipt, decision_pack=pack)))
        self.assertEqual(decision.ledger_bytes(session, receipt, pack), actual)
        self.assertLessEqual(actual, session.byte_accounting['evidence_cap'])
        self.assertLessEqual(actual + session.byte_accounting['input_bytes'], session.byte_accounting['input_cap'])
        self.assertLessEqual(decision.ledger_bytes(session) + sum(preview['reservation'].values()), session.byte_accounting['evidence_cap'])
        self.validate(pack)

    def test_prepare_has_one_count_one_match_finalize_and_control_have_zero_sql(self):
        statements = []
        connect = decision.native.retrieval.sqlite3.connect
        def traced(*args, **kwargs):
            connection = connect(*args, **kwargs)
            connection.set_trace_callback(statements.append)
            return connection
        with patch.object(decision.native.retrieval.sqlite3, 'connect', side_effect=traced):
            session = decision.prepare(self.b, self.i)
        matches = [s for s in statements if 'repository_fts MATCH' in s]
        self.assertEqual(len(matches), 2)
        self.assertEqual(sum('COUNT(*)' in s.upper() for s in matches), 1)
        with patch.object(decision.native.retrieval.sqlite3, 'connect', side_effect=AssertionError('finalize/control cannot query')):
            control = session.control
            result = decision.finalize(session, self.order(session))
        self.assertEqual((control['aggregate_calls'], control['retrieval_calls']), (1, 1))
        self.assertIn('decision_pack', result)
        self.assertEqual(set(session.timings), {'prepare_count_ms', 'retrieval_ms', 'local_preview_ms'})

    def test_permutation_rejects_missing_duplicate_foreign_boolean_and_card_payload(self):
        order = self.order(self.session)
        for invalid in (order[:-1], order[:-1] + [order[0]], order[:-1] + [999999999999],
                        [True] + order[1:], tuple(order), {'decision_order': order, 'cards': []}):
            with self.subTest(invalid=repr(invalid)[:70]):
                result = decision.finalize(self.fresh(), invalid)
                self.assertEqual(result['status'], 'invalid_decision')
                self.assertIsNone(result['evidence_pack'])
        session = self.fresh()
        decision.finalize(session, order)
        self.assertEqual(decision.finalize(session, order)['status'], 'invalid_decision')

    def test_accessors_are_copies_and_retained_tampering_is_stale(self):
        session = self.fresh()
        public = session.preview_request
        public['candidates'][0]['fields'][0]['text'] = 'forged'
        self.assertNotEqual(public, session.preview_request)
        self.assertIn('decision_pack', decision.finalize(session, self.order(session)))
        for member in ('brief', 'interpretation', 'observations', 'request', 'result', 'cards', 'bindings', 'preview', 'wrapper_bytes'):
            with self.subTest(member=member):
                changed = self.fresh()
                changed._data[member] = None
                result = decision.finalize(changed, self.order(self.session))
                self.assertEqual(result['status'], 'stale_binding')
                self.assertIsNone(result['evidence_pack'])
                self.assertEqual(result['bindings'], self.session.preview_request['bindings'])

    def test_caller_correction_invalidates_retained_context_and_constructor_is_not_input_api(self):
        b, i = copy.deepcopy(self.b), copy.deepcopy(self.i)
        session = decision.prepare(b, i)
        b['goal'] = 'A corrected goal'
        self.assertEqual(decision.finalize(session, self.order(session))['status'], 'stale_binding')
        with self.assertRaises(ValueError):
            decision.DecisionSession(self.session._data, {})

    def test_primary_first_reference_next_with_canonical_synthetic_eligibility(self):
        # The accepted synthetic fixture has complete advisory evidence. The
        # catalog's current unknown advisory cards cannot prove this branch.
        primary_card = copy.deepcopy(contracts.POSITIVE['catalog/repository-card.schema.json'])
        primary = decision.native.context_pack.matcher.match_candidate(primary_card, self.session.catalog_query)
        reference_id = next(r['github_repository_id'] for r in self.session.preview_request['candidates']
                            if r['guard_status'] == 'reference_only')
        reference = decision.native.context_pack.matcher.match_candidate(
            self.session._data['cards'][reference_id], self.session.catalog_query)
        self.assertEqual((primary['status'], reference['status']), ('primary_eligible', 'reference_only'))
        primary_id = primary_card['identity']['github_repository_id']
        guards = {primary_id: dict(status=primary['status']), reference_id: dict(status=reference['status']),
                  1: dict(status='blocked')}
        order = [reference_id, 1, primary_id]
        self.assertEqual(decision._ordered_selectable(order, guards), [primary_id, reference_id])
        self.assertEqual(order, [reference_id, 1, primary_id])

    def test_source_recheck_failure_cannot_fallback_or_be_semantic_exclusion(self):
        with patch.object(decision, '_bundle', side_effect=ValueError('changed physical bundle')):
            result = decision.finalize(self.fresh(), self.order(self.session))
        self.assertEqual(result['status'], 'stale_binding')
        self.assertIsNone(result['evidence_pack'])
        changed = copy.deepcopy(self.session._data['cards'])
        first = self.order(self.session)[0]
        changed[first]['descriptions']['upstream'] = 'forged source fact'
        with patch.object(decision, '_source_cards', return_value=changed):
            self.assertEqual(decision.finalize(self.fresh(), self.order(self.session))['status'], 'stale_binding')

    def test_all_blocked_is_no_eligible_but_unknown_remains_reference(self):
        b = copy.deepcopy(self.b)
        b['constraints']['allowed_licenses'] = ['LicenseRef-Impossible-Test']
        i = copy.deepcopy(self.i)
        i['brief_sha256'] = decision.digest(b)
        session = decision.prepare(b, i)
        self.assertIsInstance(session, decision.DecisionSession)
        self.assertTrue(all(r['guard_status'] == 'blocked' for r in session.preview_request['candidates']))
        pack = decision.finalize(session, self.order(session))['decision_pack']
        self.assertEqual((pack['status'], pack['cards'], pack['truncated']), ('no_eligible', [], False))
        self.assertEqual(len(pack['exclusions']), len(self.order(session)))
        self.validate(pack)
        self.assertTrue(any(r['eligibility_status'] == 'reference_only' for r in self.session.preview_request['candidates']))

    def test_explicit_product_and_documented_dependency_conflicts_are_hard_exclusions(self):
        rid = next(r for r in self.order(self.session) if r not in self.i['excluded_repository_ids'])
        i = copy.deepcopy(self.i)
        i['excluded_dependencies'] = ['forbidden-engine']
        observation = dict(github_repository_id=rid, full_name=self.session._data['cards'][rid]['identity']['full_name'],
            observed_on='2026-10-11', source_urls=['https://example.invalid/fixture'], alternatives=[['forbidden-engine']])
        session = decision.prepare(self.b, i, [observation])
        pack = decision.finalize(session, self.order(session))['decision_pack']
        excluded = {e['github_repository_id']: e['reason_codes'] for e in pack['exclusions']}
        self.assertIn('documented_dependency_conflict', excluded[rid])
        self.assertIn('explicit_product_exclusion', excluded[29207621])
        self.assertNotIn(rid, [r['card']['identity']['github_repository_id'] for r in pack['cards']])
        self.validate(pack)

    def test_nonpool_observation_keeps_native_compatibility_without_retaining_extra_cards(self):
        outside = next(rid for rid in self.broad._data['ids'] if rid not in self.session._data['cards'])
        observation = dict(github_repository_id=outside,
            full_name=self.broad._data['cards'][outside]['identity']['full_name'],
            observed_on='2026-10-11', source_urls=['https://example.invalid/fixture'], alternatives=[[]])
        session = decision.prepare(self.b, self.i, [observation])
        self.assertIsInstance(session, decision.DecisionSession)
        self.assertNotIn(outside, session._data['cards'])
        self.assertEqual(set(session._data['cards']), set(self.order(session)))
        self.assertEqual(session._data['observation_names'], {outside: observation['full_name']})
        self.assertEqual(session.control['public_observations'], [observation])
        self.assertEqual(session.preview_request['bindings']['guard_context_sha256'],
            decision.digest(dict(exclusions=session.request['exclusions'], public_observations=[observation])))
        self.assertIn('decision_pack', decision.finalize(session, self.order(session)))
        observation['full_name'] = 'forged/identity'
        self.assertEqual(decision.prepare(self.b, self.i, [observation])['status'], 'invalid_input')

    def test_native_no_match_and_preflight_failures_are_explicit(self):
        i = copy.deepcopy(self.i)
        i.update(route=None, terms=['unmatchablecp04fixtureterm'],
                 intent=dict(required_groups=[['unmatchablecp04fixtureterm']], context_terms=[]))
        no_match = decision.prepare(self.b, i)
        self.assertEqual(no_match['status'], 'no_match')
        self.assertIsNone(no_match['evidence_pack'])
        self.validate(no_match)
        for status in ('index_incompatible', 'retrieval_unavailable'):
            error = decision.native.RetrievalPreflightError(dict(status=status, match_count=None), aggregate_calls=0)
            with patch.object(decision.native, 'prepare_from_brief', side_effect=error), \
                    patch.object(decision.native.retrieval, 'retrieve', side_effect=AssertionError('failed preflight cannot retrieve')):
                failure = decision.prepare(self.b, self.i)
            self.assertEqual(failure['status'], status)
            self.assertIsNone(failure['evidence_pack'])
            self.validate(failure)

    def test_wrapper_and_input_overflow_stop_before_host_and_reserve_real_card(self):
        with patch.object(decision.native.retrieval, 'count_matches', side_effect=AssertionError('oversized input cannot count')):
            oversized = decision.prepare(self.b, self.i, targeted_context='x' * 16385)
            self.assertEqual(oversized['status'], 'budget_exceeded')
        no_room = decision.prepare(self.b, self.i, wrapper_bytes=163840)
        self.assertEqual(no_room['status'], 'budget_exceeded')
        self.assertIsNone(no_room['evidence_pack'])
        wrapped = decision.prepare(self.b, self.i, wrapper_bytes=2000)
        self.assertIsInstance(wrapped, decision.DecisionSession)
        self.assertEqual(decision.ledger_bytes(wrapped),
            len(decision.canonical_bytes(dict(preview_request=wrapped.preview_request, decision_receipt=None, decision_pack=None))) + 2000)
        self.assertGreater(wrapped.preview_request['reservation']['pack_bytes'], 2000)

    def test_waterfill_matches_literal_longest_first_unicode_ties_and_escaping(self):
        fixture = dict(candidates=[dict(fields=[dict(source_field=p, text=t, coverage='complete')
            for p, t in zip(decision.FIELD_POINTERS, ['😀\"\\', 'абв', 'abc', '', None, 'xy'])])])
        slow = copy.deepcopy(fixture)
        for removals in range(12):
            self.assertEqual(decision._trimmed(fixture, removals), slow)
            fields = [f for c in slow['candidates'] for f in c['fields']]
            longest = max(range(len(fields)), key=lambda n: len(fields[n]['text'] or ''))
            if fields[longest]['text']:
                fields[longest]['text'] = fields[longest]['text'][:-1]
                fields[longest]['coverage'] = 'truncated'
        card = dict(descriptions=dict(upstream='😀' * 1025, catalog=''), repository=dict(topics=['one', 'two']))
        self.assertEqual(decision._projection(card, '/repository/topics')['text'], 'one\ntwo')
        self.assertEqual(decision._projection(card, '/descriptions/catalog'), dict(source_field='/descriptions/catalog', text=None, coverage='unknown'))
        self.assertEqual(len(decision._projection(card, '/descriptions/upstream')['text']), 1024)

    def test_unresolved_stale_or_malformed_interpretation_does_not_query(self):
        unresolved = copy.deepcopy(self.i)
        unresolved.update(route=None, terms=None, intent=None,
            unresolved=[dict(dimension='hosting', question='Choose hosting', options=['local', 'hosted'])])
        malformed = copy.deepcopy(self.i)
        malformed['excluded_repository_ids'] = [True]
        stale = copy.deepcopy(self.i)
        stale['brief_sha256'] = '0' * 64
        with patch.object(decision.native.retrieval, 'count_matches', side_effect=AssertionError('no invalid count')):
            self.assertEqual(decision.prepare(self.b, unresolved)['status'], 'needs_clarification')
            self.assertEqual(decision.prepare(self.b, malformed)['status'], 'invalid_input')
            self.assertEqual(decision.prepare(self.b, stale)['status'], 'invalid_input')

    def test_offline_schema_rejects_full_card_preview_and_thirteenth_pack_card(self):
        preview = self.session.preview_request
        preview['candidates'][0]['card'] = self.session._data['cards'][self.order(self.session)[0]]
        with self.assertRaises(contracts.ValidationError):
            self.validate(preview)
        result = decision.finalize(self.fresh(), self.order(self.session))
        pack = result['decision_pack']
        pack['cards'] = [copy.deepcopy(pack['cards'][0]) for _ in range(13)]
        with self.assertRaises(contracts.ValidationError):
            self.validate(pack)
        self.assertEqual(hashlib.sha256((ROOT/'specs/retrieval/candidate-decision.schema.json').read_bytes()).hexdigest(), decision.CONTRACT_SCHEMA_SHA256)
        self.assertEqual(hashlib.sha256((ROOT/'specs/retrieval/candidate-decision-contract.md').read_bytes()).hexdigest(), decision.CONTRACT_DOCUMENT_SHA256)

    def test_stdio_eof_and_reply_extra_fields_are_explicit_failures(self):
        payload = decision.canonical_bytes(dict(brief=self.b, interpretation=self.i, public_observations=[])) + b'\n'
        for reply, status in ((b'', 'needs_selection'), (b'{"decision_order":[],"cards":[]}\n', 'invalid_decision'),
                              (b'{"decision_order":[],"decision_order":[]}\n', 'invalid_decision')):
            output = io.StringIO()
            code = decision.interactive_json(io.BytesIO(payload + reply), output)
            artifacts = [json.loads(line) for line in output.getvalue().splitlines()]
            self.assertEqual(len(artifacts), 2)
            self.assertEqual((code, artifacts[-1]['status']), (1, status))
            self.assertIsNone(artifacts[-1]['evidence_pack'])

    def test_actual_isolated_foreground_bridge_retains_context_for_one_reply(self):
        command = [sys.executable, '-I', '-B', str(ROOT/'plugins/myai-stackguide/scripts/recommendation_decision.py'), '--interactive-json']
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        payload = dict(brief=self.b, interpretation=self.i, public_observations=[])
        process.stdin.write(decision.canonical_bytes(payload) + b'\n')
        process.stdin.flush()
        preview = json.loads(process.stdout.readline().decode('utf-8'))
        self.assertEqual(preview['artifact_type'], 'candidate_preview_request')
        order = [p['github_repository_id'] for p in preview['candidates']][::-1]
        stdout, stderr = process.communicate(decision.canonical_bytes(dict(decision_order=order)) + b'\n', timeout=30)
        self.assertEqual(process.returncode, 0, stderr.decode('utf-8', errors='replace'))
        result = json.loads(stdout.decode('utf-8'))
        self.assertEqual(result['decision_receipt']['decision_order'], order)
        self.validate(result['decision_pack'])


if __name__=='__main__':
    unittest.main()
