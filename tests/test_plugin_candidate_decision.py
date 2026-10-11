"""Behavioral checks for the separately versioned transient host decision boundary."""
import copy
import hashlib
import io
import itertools
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

# Exposed offline fixture: CP04-HOLD-10 order from the immutable 99-card
# cardinality capture. Replaying it is not a fresh model run. Inline IDs keep
# unit tests independent of ignored result directories in a clean checkout.
TRAINING_ORDER = [763697768,987976055,506953078,95700338,922406522,395140743,
    778281287,709422137,444377346,178626720,636372163,607845880,541386254,
    180572200,1126557956,838970603,934221781,890059746,531471133,646410686,
    797371964,725205304,627727693,616099860,693936906,670206497,650918061,
    629142696,1162516847,648788010,878416567,783744120,620843043,953478769,
    752815135,814496416,1069235905,832879402,669402660,1240872088,1222120468,
    375163159,772255271,783968898,879473096,913684633,570985989,707818217,
    977970140,1140263746,1176898834,723015178,708552127,843003613,667297720,
    646489141,644235905,1201826173,700724064,1040481901,731397562,991030974,
    1331428199,910125376,679091311,832661327,841541826,850338335,631692814,
    656385153,646537482,626790707,575628616,575997792,1003799351,603067222,
    823430322,731467355,1243340887,201314421,392708700,169991845,628028132,
    198694912,164046740,718873539,810121174,666612077,888274570,1052387869,
    658219396,715806751,800415474,789098173,594934731,569937782,973621150,
    1187805808,626773493]


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

    def test_training_comparison_preserves_first_three_complete_guarded_cards(self):
        b = brief('Compare distributed model training components and produce a bounded integration handoff.')
        b.update(brief_id='CP04-HOLD-10-current-fixed',
                 success_criterion='Explain the conditional decision and a safe first validation.')
        self.assertEqual(decision.digest(b), '05ad244fe725816b24b2c4ef2a271ad8c88da5340a4ac9328c130e0742ca5cad')
        i = interpretation(b)
        i.update(language='ru', route='training_finetuning_alignment', terms=['distributed training'],
                 intent=dict(required_groups=[['distributed training']], context_terms=[]), excluded_repository_ids=[])
        # Actual controlled wrapper allocation recorded for this exposed input.
        session = decision.prepare(b, i, [], wrapper_bytes=33737)
        self.assertIsInstance(session, decision.DecisionSession)
        self.assertEqual(set(self.order(session)), set(TRAINING_ORDER))
        guards = {r['github_repository_id']: dict(status=r['guard_status']) for r in session.preview_request['candidates']}
        expected = decision._ordered_selectable(TRAINING_ORDER, guards)[:3]
        result = decision.finalize(session, TRAINING_ORDER)
        packed = [r['card']['identity']['github_repository_id'] for r in result['decision_pack']['cards']]
        self.assertEqual(packed[:3], expected,
            'Expected RED: least-card reserve packs weak rank49 and starves the first three comparison cards')
        self.assertLessEqual(decision.ledger_bytes(session, result['decision_receipt'], result['decision_pack']), 163840)

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
        guards = {r['github_repository_id']: dict(status=r['guard_status']) for r in preview['candidates']}
        affordable_prefix = decision._ordered_selectable(self.order(session)[::-1], guards)[:session.allocation['target']]
        self.assertEqual([r['card']['identity']['github_repository_id'] for r in pack['cards']][:len(affordable_prefix)], affordable_prefix,
            'Worst-target allocation protects the first guarded candidates regardless of card size')
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

    def sizing(self, data, guards, target):
        """Private allocator arithmetic; this does not emit a trusted artifact."""
        preview = decision._preview(data, guards)
        receipt = decision._receipt(data, '0' * 64, data['ids'])
        pack = decision._worst_target_pack(data, guards, target)
        preview['reservation'] = dict(receipt_bytes=len(decision.canonical_bytes(receipt)) - 4,
                                      pack_bytes=len(decision.canonical_bytes(pack)) - 4)
        count = sum(len(f['text']) for c in preview['candidates'] for f in c['fields'] if f['text'] is not None)
        skeleton = decision._trimmed(preview, count)
        return decision._ledger_size(data, skeleton, receipt, pack), skeleton, receipt, pack

    def test_downshift_3_to_2_to_1_only_at_empty_projection_and_one_failure(self):
        data = copy.deepcopy(self.session._data)
        guards = decision._guarded(data)
        sizes = {target: self.sizing(data, guards, target)[0] for target in (1, 2, 3)}
        self.assertLess(sizes[1], sizes[2])
        self.assertLess(sizes[2], sizes[3])
        for expected, cap in ((3, sizes[3]), (2, sizes[3] - 1), (1, sizes[2] - 1)):
            with self.subTest(target=expected):
                data['evidence_cap'] = cap
                preview = decision._preview(data, guards)
                plan = decision._reservation_plan(data, preview, guards)
                self.assertEqual(plan[2], expected)
                projected = decision._reserve_and_trim(data, decision._preview(data, guards), guards)
                self.assertIsNotNone(projected)
                self.assertLessEqual(decision._ledger_size(data, projected, plan[0], plan[1]), cap)
                if expected == 3:
                    self.assertTrue(all(f['text'] in ('', None) for c in projected['candidates'] for f in c['fields']))
                    self.assertTrue(all(f['coverage'] == ('unknown' if f['text'] is None else 'truncated')
                                        for c in projected['candidates'] for f in c['fields']))
        data['evidence_cap'] = sizes[1] - 1
        self.assertIsNone(decision._reserve_and_trim(data, decision._preview(data, guards), guards))
        data['evidence_cap'] = self.session.byte_accounting['evidence_cap']
        data['input_cap'] = data['input_bytes'] + sizes[2]
        self.assertEqual(decision._reservation_plan(data, decision._preview(data, guards), guards)[2], 2)

    def test_lower_card_caps_use_exact_candidate_budget_replacements(self):
        # Lower legal caps affect only these local sizing inputs, never native
        # assets/query production or the captured control.
        for cap in (1, 2):
            data = copy.deepcopy(self.session._data)
            data['request']['catalog_query']['max_cards'] = cap
            guards = decision._guarded(data)
            receipt, pack, target = decision._reservation_plan(data, decision._preview(data, guards), guards)
            self.assertEqual(target, cap)
            self.assertEqual(len(pack['cards']), cap)
            self.assertTrue(any(e['reason_codes'] == ['candidate_budget'] for e in pack['exclusions']))
            self.assertEqual({r['decision_rank'] for r in pack['cards']}, {len(data['ids'])})
            self.assertGreater(len(decision.canonical_bytes(receipt)), 4)

    def test_increment_reservation_bounds_every_target_subset_with_real_records(self):
        data = copy.deepcopy(self.session._data)
        guards = decision._guarded(data)
        eligible = [rid for rid in data['ids'] if guards[rid]['status'] != 'blocked']
        worst = decision._worst_target_pack(data, guards, 3)
        measured = []
        for subset in itertools.combinations(eligible, 3):
            # Maximum full-pool digit width, not renumbered packed ranks.
            records = [decision._record(data, rid, len(data['ids']), guards) for rid in subset]
            pack = decision._pack(data, '0' * 64, '0' * 64, records, guards, {})
            measured.append(len(decision.canonical_bytes(pack)))
        self.assertEqual(len(decision.canonical_bytes(worst)), max(measured))
        record = worst['cards'][0]
        rid = record['card']['identity']['github_repository_id']
        exclusion = dict(github_repository_id=rid, reason_codes=['context_budget'])
        self.assertLess(len(decision.canonical_bytes(record)) - len(decision.canonical_bytes(exclusion)),
                        len(decision.canonical_bytes(record)))

    def test_largest_card_can_lead_actual_host_order_under_reduced_target(self):
        session = self.fresh(broad=True)
        largest = session.allocation['worst_candidate_ids'][0]
        order = [largest] + [rid for rid in self.order(session) if rid != largest]
        result = decision.finalize(session, order)
        packed = result['decision_pack']['cards']
        self.assertEqual(packed[0]['card']['identity']['github_repository_id'], largest)
        self.assertEqual(packed[0]['decision_rank'], 1)
        self.assertGreaterEqual(len(packed), session.allocation['target'])
        self.assertLessEqual(decision.ledger_bytes(session, result['decision_receipt'], result['decision_pack']), session.byte_accounting['evidence_cap'])

    def test_synthetic_equal_increment_ties_follow_native_rank_and_count_unicode_bytes(self):
        # Size-only synthetic records use the existing complete fixture. They
        # never enter prepare/finalize or claim a pinned production source.
        data = copy.deepcopy(self.session._data)
        data['ids'] = [900000003, 900000001, 900000002]
        data['cards'], data['rows'] = {}, {}
        for rank, rid in enumerate(data['ids'], 1):
            card = copy.deepcopy(contracts.POSITIVE['catalog/repository-card.schema.json'])
            card['identity']['github_repository_id'] = rid
            card['descriptions']['upstream'] = '😀\\"' * 3
            data['cards'][rid] = card
            data['rows'][rid] = dict(rank=rank, rrf_score=0.01, matched_fields=['upstream_description'])
        eligibility = copy.deepcopy(contracts.POSITIVE['catalog/candidate-eligibility.schema.json'])
        guards = {rid: dict(status='primary_eligible', reasons=[], eligibility=dict(eligibility, github_repository_id=rid)) for rid in data['ids']}
        pack = decision._worst_target_pack(data, guards, 2)
        self.assertEqual([r['card']['identity']['github_repository_id'] for r in pack['cards']], data['ids'][:2])
        self.assertEqual(len(decision.canonical_bytes('😀\\"')), 10)

    def test_v1_pending_bindings_cannot_be_silently_upgraded(self):
        session = self.fresh()
        old = session._data
        old['bindings']['contract_schema_sha256'] = '83373eb4ec2b0f8270d4d7e6750bc1419591151338c023f018670214ec278f92'
        old['bindings']['contract_document_sha256'] = '21106a3d580672f1b86caaad6edec82d9e53f0e11e6b4689439ce909961d3bc6'
        old['preview']['schema_version'] = '1.0.0'
        old['preview']['method'] = 'host_codex_full_pool_v1'
        session._bindings = copy.deepcopy(old['bindings'])
        session._seal = decision.digest(old)
        result = decision.finalize(session, self.order(session))
        self.assertEqual(result['status'], 'stale_binding')
        self.assertIsNone(result['evidence_pack'])

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
        self.assertEqual(session.allocation['target'], 0)
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
