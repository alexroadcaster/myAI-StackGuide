"""CP-11 writer-input checks against the real packaged public catalog."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'plugins/myai-stackguide/scripts'
sys.path.insert(0, str(SCRIPTS))
import context_pack
import retrieval


def inputs():
    all_fixtures = json.loads((ROOT / 'tests/fixtures/plugin_contracts.json').read_text(encoding='utf-8'))
    fixtures = all_fixtures['positive']
    brief = copy.deepcopy(all_fixtures['workspace_positive']['context/project-context-brief.schema.json'])
    query = copy.deepcopy(fixtures['retrieval/catalog-query.schema.json'])
    manifest = json.loads((SCRIPTS.parent / 'assets/catalog.search-manifest.json').read_bytes())
    query['policy_sha256'] = manifest['pins']['policy_sha256']
    query['taxonomy_route_id'] = None
    query['variants'] = [{'variant_id': 'q1', 'terms': ['sqlite']}]
    query['constraints'] = dict(languages=[], deployment=[], allowed_licenses=[], compatibility=[], require_no_server=None, mandatory_fields=[])
    brief['constraints'] = copy.deepcopy(query['constraints'])
    request = copy.deepcopy(fixtures['recommendation/recommendation-request.schema.json'])
    request.update(query=query, run_id=brief['run_id'], brief_id=brief['brief_id'], brief_version=brief['brief_version'])
    assets = SCRIPTS.parent / 'assets'
    result = retrieval.retrieve(query, run_id=brief['run_id'], index_path=assets/'catalog.search.sqlite', manifest_path=assets/'catalog.search-manifest.json', policy_path=assets/'retrieval-policy.json')
    if result['status'] != 'ok':
        raise AssertionError('real packaged retrieval setup failed: ' + result['status'])
    cards = context_pack._stream_verified_snapshot_cards(SCRIPTS.parent/'assets/catalog.snapshot.json', manifest['pins'], expected_count=manifest['row_count'], max_bytes=context_pack.MAX_SNAPSHOT_BYTES, candidate_ids=[r['github_repository_id'] for r in result['candidates']])
    pack = context_pack._build_evidence_pack_from_trusted_cards(query, result, cards, pack_id=request['pack_id'], max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
    state = dict(schema_version='1.1.0', run_id=brief['run_id'], brief=brief, index_manifest=manifest, intake={'answers': []}, scan=None)
    payload = dict(request=request, retrieval=result, evidence_pack=pack)
    state.update(copy.deepcopy(payload))
    memo = copy.deepcopy(fixtures['recommendation/recommendation-memo.schema.json'])
    eligible = pack['cards'][0]
    rid = eligible['card']['identity']['github_repository_id']
    refs = [eligible['card']['evidence'][0]['evidence_id']]
    memo.update(run_id=brief['run_id'], brief_version=brief['brief_version'], request_id=request['request_id'], pack_id=pack['pack_id'], pins=pack['pins'], category_path=[], status='conditional_guidance')
    memo['recommendations'][0].update(github_repository_id=rid, evidence_refs=refs, role='reference_only')
    # Card-local IDs repeat across this multi-card pack. Ownerless records must
    # not pretend a generic public ref identifies one repository.
    memo['reading_path'] = []
    plan = memo['integration_plan']
    plan.update(run_id=brief['run_id'], brief_version=brief['brief_version'], selected_github_repository_ids=[rid],
                evidence_refs=[brief['observations']['evidence'][0]['evidence_id']])
    return state, payload, {'memo': memo}


class SessionRecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state, cls.matching, cls.memo = inputs()

    def setUp(self):
        path = SCRIPTS/'session_recommendation.py'
        self.assertTrue(path.is_file(), 'CP-11 validated matching/memo seam is not implemented')
        spec = importlib.util.spec_from_file_location('session_recommendation', path)
        self.runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runtime)

    def test_valid_matching_and_memo_are_deep_copies_without_sql_or_retrieval(self):
        with patch.object(retrieval, 'retrieve', side_effect=AssertionError('second retrieval')), patch.object(retrieval, 'count_matches', side_effect=AssertionError('second lookup')), patch.object(retrieval.sqlite3, 'connect', side_effect=AssertionError('SQL in validator')):
            result = self.runtime.validate_matching(self.state, self.matching)
            memo = self.runtime.validate_memo(self.state, self.memo)
        self.assertEqual(result, self.matching)
        self.assertEqual(memo, self.memo)
        result['request']['query']['variants'][0]['terms'].append('changed')
        self.assertNotEqual(result, self.matching)

    def test_matching_rejects_stale_join_and_forged_native_data(self):
        mutations = [
            lambda p: p['request'].update(brief_version=2),
            lambda p: p['request']['query']['constraints']['languages'].append('forged'),
            lambda p: p['retrieval'].update(query_sha256='0'*64),
            lambda p: p['retrieval']['pins'].update(index_sha256='0'*64),
            lambda p: p['retrieval']['candidates'][0].update(github_repository_id=True),
            lambda p: p['retrieval']['candidates'][0].update(rrf_score=0.5),
            lambda p: p['retrieval']['candidates'][0]['variant_ranks'][0].update(variant_id='q3'),
            lambda p: p['evidence_pack']['cards'][0]['card']['descriptions'].update(catalog='forged'),
            lambda p: p['evidence_pack']['cards'][0]['eligibility'].update(status='blocked'),
            lambda p: p.update(public_observations=[]),
        ]
        for mutate in mutations:
            payload = copy.deepcopy(self.matching)
            mutate(payload)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                self.runtime.validate_matching(self.state, payload)

    def test_matching_rejects_state_manifest_tampering(self):
        state = copy.deepcopy(self.state)
        state['index_manifest']['built_at'] = '2099-01-01T00:00:00Z'
        with self.assertRaises(ValueError):
            self.runtime.validate_matching(state, self.matching)

    def test_actual_truncation_retains_candidate_budget_reason(self):
        matching = copy.deepcopy(self.matching)
        query = matching['request']['query']
        query.update(max_candidates=1, max_cards=1)
        assets = SCRIPTS.parent / 'assets'
        result = retrieval.retrieve(query, run_id=self.state['run_id'],
            index_path=assets/'catalog.search.sqlite',
            manifest_path=assets/'catalog.search-manifest.json', policy_path=assets/'retrieval-policy.json')
        self.assertTrue(result['truncated'])
        self.assertEqual(result['reason_codes'], ['candidate_budget'])
        cards = context_pack._stream_verified_snapshot_cards(assets/'catalog.snapshot.json',
            self.state['index_manifest']['pins'], expected_count=2500,
            max_bytes=context_pack.MAX_SNAPSHOT_BYTES,
            candidate_ids=[r['github_repository_id'] for r in result['candidates']])
        pack = context_pack._build_evidence_pack_from_trusted_cards(query, result, cards,
            pack_id=matching['request']['pack_id'], max_cards=1, max_evidence_bytes=query['max_evidence_bytes'])
        matching.update(retrieval=result, evidence_pack=pack)
        self.assertEqual(self.runtime.validate_matching(self.state, matching), matching)
        matching['retrieval']['reason_codes'] = []
        with self.assertRaises(ValueError):
            self.runtime.validate_matching(self.state, matching)

    def test_memo_rejects_unknown_refs_roles_paths_dependencies_and_execution(self):
        mutations = [
            lambda m: m.update(brief_version=2),
            lambda m: m.update(request_id='other'),
            lambda m: m['recommendations'][0].update(role='invented'),
            lambda m: m['recommendations'][0].update(github_repository_id=True),
            lambda m: m['recommendations'][0].update(evidence_refs=['ev-invented']),
            lambda m: m['integration_plan']['selected_github_repository_ids'].append(1),
            lambda m: m['integration_plan']['details']['step_dependencies'][0]['depends_on'].append('step-1'),
            lambda m: m['integration_plan']['details']['step_dependencies'][0]['safe_paths'].append('../escape'),
            lambda m: m['integration_plan']['details']['step_dependencies'][0]['safe_paths'].append('.env'),
            lambda m: m['integration_plan']['details']['step_dependencies'][0]['safe_paths'].append('invented.py'),
            lambda m: m['integration_plan'].update(execution_status='completed'),
            lambda m: m['integration_plan']['handoff'].update(permission_changes=True),
            lambda m: m.update(summary='я'*70000),
        ]
        for mutate in mutations:
            payload = copy.deepcopy(self.memo)
            mutate(payload['memo'])
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                self.runtime.validate_memo(self.state, payload)

    def test_memo_cannot_upgrade_reference_only_candidate(self):
        payload = copy.deepcopy(self.memo)
        payload['memo']['recommendations'][0]['role'] = 'primary_candidate'
        with self.assertRaises(ValueError):
            self.runtime.validate_memo(self.state, payload)

    def test_ownerless_public_refs_require_one_admissible_owner(self):
        self.runtime.validate_memo(self.state, self.memo)
        ref = self.memo['memo']['recommendations'][0]['evidence_refs'][0]
        owners = [row for row in self.state['evidence_pack']['cards']
                  if ref in {e['evidence_id'] for e in row['card']['evidence']}]
        self.assertGreater(len(owners), 1)
        for field in ('reading_path', 'integration_plan'):
            with self.subTest(field=field):
                payload = copy.deepcopy(self.memo)
                if field == 'reading_path':
                    payload['memo'][field] = [{'evidence_ref': ref, 'purpose': 'Synthetic ambiguous source'}]
                else:
                    payload['memo'][field]['evidence_refs'] = [ref]
                with self.assertRaises(ValueError):
                    self.runtime.validate_memo(self.state, payload)

    def test_schema_date_time_requires_rfc3339_syntax(self):
        for value in ('2026-10-17 01:02:03+00:00', '20261017T010203+0000'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.runtime._validate(value, {'type': 'string', 'format': 'date-time'}, {})

    def test_no_match_and_index_failure_remain_distinct(self):
        for failed in (False, True):
            state, matching, memo = copy.deepcopy((self.state, self.matching, self.memo))
            query = matching['request']['query']
            query['variants'] = [{'variant_id': 'q1', 'terms': ['zzzz-unmatched-synthetic-fixture']}]
            if failed:
                result = retrieval._failure(query, state['run_id'], 'retrieval_unavailable', 'index_corrupt', pins=state['index_manifest']['pins'])
            else:
                assets = SCRIPTS.parent / 'assets'
                result = retrieval.retrieve(query, run_id=state['run_id'], index_path=assets/'catalog.search.sqlite', manifest_path=assets/'catalog.search-manifest.json', policy_path=assets/'retrieval-policy.json')
            pack = context_pack._build_evidence_pack_from_trusted_cards(query, result, {}, pack_id=matching['request']['pack_id'], max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
            matching.update(retrieval=result, evidence_pack=pack)
            state.update(matching)
            expected = 'retrieval_unavailable' if failed else 'no_match'
            memo['memo'].update(status=expected, recommendations=[], integration_plan=None, reading_path=[])
            self.assertEqual(self.runtime.validate_matching(state, matching), matching)
            self.assertEqual(self.runtime.validate_memo(state, memo), memo)
            memo['memo']['status'] = 'no_match' if failed else 'retrieval_unavailable'
            with self.assertRaises(ValueError):
                self.runtime.validate_memo(state, memo)

    def test_plan_sourced_safe_path_is_preserved_and_unknown_source_rejected(self):
        state, payload = copy.deepcopy((self.state, self.memo))
        record = copy.deepcopy(state['brief']['observations']['evidence'][0])
        record.update(evidence_id='ev-safe-source', relative_path='src/adapter.py')
        state['brief']['observations']['evidence'].append(record)
        dependency = payload['memo']['integration_plan']['details']['step_dependencies'][0]
        dependency.update(safe_paths=['src/adapter.py'], evidence_refs=['ev-safe-source'])
        self.assertEqual(self.runtime.validate_memo(state, payload), payload)
        dependency['evidence_refs'] = []
        with self.assertRaises(ValueError):
            self.runtime.validate_memo(state, payload)

    def test_multiple_native_variants_preserve_rrf_and_deduplication(self):
        state, matching = copy.deepcopy((self.state, self.matching))
        query = matching['request']['query']
        query['variants'].append({'variant_id': 'q2', 'terms': ['search']})
        assets = SCRIPTS.parent/'assets'
        result = retrieval.retrieve(query, run_id=state['run_id'], index_path=assets/'catalog.search.sqlite', manifest_path=assets/'catalog.search-manifest.json', policy_path=assets/'retrieval-policy.json')
        cards = context_pack._stream_verified_snapshot_cards(assets/'catalog.snapshot.json', state['index_manifest']['pins'], expected_count=2500, max_bytes=context_pack.MAX_SNAPSHOT_BYTES, candidate_ids=[r['github_repository_id'] for r in result['candidates']])
        pack = context_pack._build_evidence_pack_from_trusted_cards(query, result, cards, pack_id=matching['request']['pack_id'], max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
        matching.update(retrieval=result, evidence_pack=pack)
        self.assertEqual(self.runtime.validate_matching(state, matching), matching)

    def test_schema_engine_utf8_limits_and_unknown_keywords_fail_closed(self):
        with self.assertRaises(ValueError):
            self.runtime._validate('я'*4, {'type': 'string', 'maxLength': 4, 'x-max-utf8-bytes': 4}, {})
        with self.assertRaises(ValueError):
            self.runtime._validate({}, {'anyOf': [{}, {'futureKeyword': True}]}, {})
        with self.assertRaises(ValueError):
            self.runtime._validate({}, {'$ref': 'https://untrusted.example/schema'}, {})

    def test_missing_partial_or_legacy_state_cannot_save_matching(self):
        for state in (None, {}, dict(self.state, schema_version='1.0.0'), dict(self.state, brief=None)):
            with self.subTest(state_type=type(state).__name__), self.assertRaises(ValueError):
                self.runtime.validate_matching(state, self.matching)


if __name__ == '__main__':
    unittest.main()
