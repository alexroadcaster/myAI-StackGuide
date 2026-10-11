"""Brief version binding, real active retrieval, and clarification no-call proof."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'plugins/myai-stackguide/scripts'))
import recommendation_request as runtime


def brief(goal='Public and internal HTTPS proxy, exclude Caddy.'):
    unknown = dict(text=None, kind='unknown', evidence_refs=[], answer_ids=[], limitation='Synthetic fixture; not established.')
    details = {name: copy.deepcopy(unknown) for name in runtime.context._DETAIL_FIELDS}
    details.update(non_goals=[], constraint_notes=[], tensions=[])
    return dict(schema_version='1.1.0', run_id='11111111-1111-4111-8111-111111111111',
        brief_id='synthetic-dialogue', brief_version=1, goal=goal, decision='evaluate', project_stage='prototype',
        success_criterion='Explain the fit and a first validation step.', constraints=dict(languages=[], deployment=[],
        allowed_licenses=[], compatibility=[], require_no_server=None, mandatory_fields=[]), observations=dict(run_id='11111111-1111-4111-8111-111111111111'),
        assumptions=[], user_corrections=[], context_status='preliminary', updated_at='2026-10-11T00:00:00Z', details=details)


def interpretation(b):
    return dict(brief_sha256=runtime.digest(b), brief_version=b['brief_version'], language='en',
        route='network_proxies_gateways', terms=['HTTPS', 'certificates', 'internal', 'proxy'],
        intent=dict(required_groups=[['HTTPS'], ['certificates']], context_terms=['internal', 'proxy']),
        excluded_repository_ids=[29207621], excluded_dependencies=[], unresolved=[])


class BriefRequest(unittest.TestCase):
    def test_sparse_required_chat_phrase_uses_pinned_leaf_words_and_honest_origins(self):
        b=brief('Evaluate team chat for asynchronous messages.');i=interpretation(b)
        i.update(route='communications_personal_ops',terms=['team chat','asynchronous','messages'],
            intent=dict(required_groups=[['team chat'],['messages']],context_terms=['asynchronous']),
            excluded_repository_ids=[])
        counted=[];statements=[];connect=runtime.retrieval.sqlite3.connect
        count_matches=runtime.retrieval.count_matches
        def count(query,**kwargs):
            counted.append(copy.deepcopy(query));return count_matches(query,**kwargs)
        def traced_connect(*args,**kwargs):
            connection=connect(*args,**kwargs);connection.set_trace_callback(statements.append);return connection
        with patch.object(runtime.retrieval,'count_matches',side_effect=count),patch.object(runtime.retrieval.sqlite3,'connect',side_effect=traced_connect):
            result=runtime.run(b,i)
        self.assertEqual(result['status'],'ready')
        request=result['request'];query=request['catalog_query']
        # Expected RED: current container-only widening omits these source-backed atoms/member words.
        self.assertEqual(query['variants'],[dict(variant_id='q1',terms=i['terms']+
            ['team','chat','messaging','communications','personal'])])
        self.assertEqual(request['intent'],i['intent'])
        origins=request['query_derivation']['added_term_origins']
        self.assertIn(dict(term='team',source_kind='required_term_atom',source='team chat'),origins)
        self.assertIn(dict(term='messaging',source_kind='pinned_taxonomy_route_member',source='messaging_chat'),origins)
        self.assertIn(dict(term='communications',source_kind='selected_pinned_taxonomy_route_id',source=i['route']),origins)
        self.assertEqual([o['term'] for o in origins],query['variants'][0]['terms'][len(i['terms']):])
        self.assertEqual(request['query_derivation']['original_query_sha256'],runtime.digest(counted[0]))
        self.assertEqual(request['query_derivation']['final_query_sha256'],runtime.digest(query))
        self.assertEqual((result['aggregate_calls'],result['retrieval_calls']),(1,1))
        self.assertEqual(len([s for s in statements if 'repository_fts MATCH' in s]),2)
        snapshot=json.loads((runtime.ASSETS/'catalog.snapshot.json').read_bytes())['cards']
        rocket=next(c['identity']['github_repository_id'] for c in snapshot if c['identity']['full_name']=='RocketChat/Rocket.Chat')
        self.assertIn(rocket,[c['card']['identity']['github_repository_id'] for c in result['evidence_pack']['cards']])

    def test_underfilled_query_adds_only_selected_route_vocabulary(self):
        b=brief('Customer invoicing.'); i=interpretation(b)
        i.update(route='accounting_invoicing', terms=['invoice','invoices','payments'],
                 intent=dict(required_groups=[['invoice'],['invoices']],context_terms=['payments']),
                 excluded_repository_ids=[])
        counted=[]
        def count_result(query,**kwargs):
            counted.append(copy.deepcopy(query))
            return dict(status='ok',match_count=7)
        with patch.object(runtime.retrieval, 'count_matches', side_effect=count_result) as count:
            request=runtime.prepare_from_brief(b,i)
        self.assertEqual(count.call_count,1)
        self.assertEqual(counted[0]['variants'],[dict(variant_id='q1',terms=i['terms'])])
        self.assertEqual(request['catalog_query']['variants'],[
            dict(variant_id='q1',terms=i['terms']+['accounting','invoicing'])])
        self.assertEqual(request['intent'],i['intent'])
        self.assertEqual(request['query_derivation']['original_match_count'],7)
        self.assertEqual(request['query_derivation']['original_query_sha256'],runtime.digest(counted[0]))
        self.assertEqual(request['query_derivation']['final_query_sha256'],runtime.digest(request['catalog_query']))

    def test_failed_count_is_typed_and_never_executes_retrieval(self):
        b=brief(); i=interpretation(b)
        with patch.object(runtime.retrieval,'count_matches',create=True,
                          return_value=dict(status='index_incompatible',match_count=None)):
            result=runtime.run(b,i,retrieve=lambda *a,**k:self.fail('failed preflight retrieved'))
        self.assertEqual(result['status'],'index_incompatible')
        self.assertEqual(result['retrieval_calls'],0)
        self.assertEqual(result['aggregate_calls'],1)
        self.assertIsNone(result['evidence_pack'])

    def test_invalid_exclusions_never_count_or_retrieve(self):
        b=brief()
        for field,value in [('excluded_repository_ids',[-1]),('excluded_dependencies',['Unnormalized'])]:
            i=interpretation(b);i[field]=value
            with self.subTest(field=field),patch.object(runtime.retrieval,'count_matches',side_effect=AssertionError('invalid exclusion COUNT')):
                with self.assertRaises(ValueError):
                    runtime.run(b,i,retrieve=lambda *a,**k:self.fail('invalid exclusion retrieved'))

    def test_expansion_keeps_original_terms_and_respects_scope_capacity_and_case(self):
        b=brief();base=interpretation(b)
        for route,terms,expected_count in [('api_graphql_rpc',['API','graphql'],3),
            (None,['invoice'],1),('network_proxies_gateways',['one','two','three','four','five','six','seven','eight'],8)]:
            with self.subTest(route=route):
                i=copy.deepcopy(base);i.update(route=route,terms=terms,
                    intent=dict(required_groups=[terms],context_terms=[]),excluded_repository_ids=[])
                with patch.object(runtime.retrieval,'count_matches',return_value=dict(status='ok',match_count=0)):
                    request=runtime.prepare_from_brief(b,i)
                derived=request['catalog_query']['variants'][0]['terms']
                self.assertEqual(derived[:len(terms)],terms)
                self.assertEqual(len(derived),expected_count)
                self.assertEqual(len({runtime.retrieval._normalize(t) for t in derived}),len(derived))

    def test_sparse_accounting_sources_and_security_order_use_actual_reader(self):
        # These exposed regressions test implementation, not unseen relevance.
        b=brief('Create customer invoices.');i=interpretation(b)
        i.update(route='accounting_invoicing',terms=['invoice','invoices','payments'],
            intent=dict(required_groups=[['invoice'],['invoices']],context_terms=['payments']),excluded_repository_ids=[])
        result=runtime.run(b,i)
        self.assertEqual(result['status'],'ready')
        self.assertIn('accounting',result['request']['query_derivation']['added_route_terms'])
        snapshot=json.loads((runtime.ASSETS/'catalog.snapshot.json').read_bytes())['cards']
        identity={c['identity']['full_name']:c['identity']['github_repository_id'] for c in snapshot}
        self.assertIn(identity['Gnucash/gnucash'],result['raw_ranked_ids'])
        self.assertIn(identity['kittendevv/Invio'],result['raw_ranked_ids'])
        b=brief('Scan configuration and IaC security.');i=interpretation(b)
        i.update(route='infrastructure_security',terms=['configuration','IaC','security','scanning'],
            intent=dict(required_groups=[['configuration'],['IaC']],context_terms=['security','scanning']),excluded_repository_ids=[])
        result=runtime.run(b,i)
        self.assertEqual(result['status'],'ready')
        self.assertLess(result['raw_ranked_ids'].index(identity['kubescape/kubescape']),
                        result['raw_ranked_ids'].index(identity['wazuh/wazuh']))

    def test_correction_cannot_reuse_stale_interpretation(self):
        b=brief(); i=interpretation(b); b['goal']='Caddy now allowed'; b['brief_version']+=1
        with self.assertRaisesRegex(ValueError, 'stale Brief'):
            runtime.run(b, i, retrieve=lambda **kw: self.fail('stale query executed'))

    def test_same_version_changed_brief_is_also_rejected(self):
        b=brief(); i=interpretation(b); b['goal']='Different scope'
        with self.assertRaisesRegex(ValueError, 'stale Brief'):
            runtime.prepare_from_brief(b,i)

    def test_unresolved_brief_never_selects_route_or_calls_retrieval(self):
        b=brief('Need search'); i=interpretation(b)
        i.update(route=None, terms=None, intent=None, unresolved=[dict(dimension='corpus',question='Own data or external web?',options=['own','web'])])
        with patch.object(runtime.retrieval,'count_matches',side_effect=AssertionError('unresolved COUNT')):
            result=runtime.run(b,i,retrieve=lambda *a,**k:self.fail('unresolved retrieval'))
        self.assertEqual(result['retrieval_calls'],0)
        self.assertEqual(result['aggregate_calls'],0)
        self.assertEqual(result['status'],'needs_clarification')

    def test_active_retrieval_pack_excludes_product_and_keeps_prior_raw_order(self):
        b=brief(); i=interpretation(b); result=runtime.run(b,i)
        self.assertEqual(result['status'],'ready')
        self.assertIn(29207621,result['raw_ranked_ids'])
        self.assertNotIn(29207621,result['selected_ids'])
        packed=[r['card']['identity']['github_repository_id'] for r in result['evidence_pack']['cards']]
        self.assertNotIn(29207621,packed)
        self.assertEqual(result['selected_ids'],[r for r in result['raw_ranked_ids'] if r!=29207621])

    def test_canonical_brief_constraints_are_not_reset(self):
        b=brief();b['constraints']['languages']=['Go']; i=interpretation(b)
        self.assertEqual(runtime.prepare_from_brief(b,i)['catalog_query']['constraints'],b['constraints'])

    def test_full_capabilities_and_context_share_one_variant(self):
        b=brief('Browser automation for web UI testing.'); i=interpretation(b)
        i.update(route='browser_mobile_testing', terms=['browser','automation','testing'],
                 intent=dict(required_groups=[['browser']],context_terms=['automation','testing']),
                 excluded_repository_ids=[])
        request=runtime.prepare_from_brief(b,i)
        self.assertEqual(request['catalog_query']['variants'],[
            dict(variant_id='q1',terms=['browser','automation','testing'])])

    def test_without_context_keeps_one_original_variant(self):
        b=brief(); i=interpretation(b)
        i['intent']=dict(required_groups=[['certificates'],['HTTPS','internal','proxy']],context_terms=[])
        with patch.object(runtime.retrieval,'count_matches',return_value=dict(status='ok',match_count=12)):
            request=runtime.prepare_from_brief(b,i)
        self.assertEqual(request['catalog_query']['variants'],[dict(variant_id='q1',terms=i['terms'])])
        self.assertEqual(request['query_derivation']['original_query_sha256'],request['query_derivation']['final_query_sha256'])
        self.assertEqual(request['query_derivation']['final_query_sha256'],runtime.digest(request['catalog_query']))
        self.assertEqual(request['query_derivation']['pins'],json.loads((runtime.ASSETS/'catalog.search-manifest.json').read_bytes())['pins'])

    def test_ready_request_executes_one_count_and_one_candidate_match(self):
        statements=[];connect=runtime.retrieval.sqlite3.connect
        def traced_connect(*args,**kwargs):
            connection=connect(*args,**kwargs)
            connection.set_trace_callback(statements.append)
            return connection
        b=brief();i=interpretation(b)
        with patch.object(runtime.retrieval.sqlite3,'connect',side_effect=traced_connect):
            result=runtime.run(b,i)
        matches=[s for s in statements if 'repository_fts MATCH' in s]
        self.assertEqual(result['status'],'ready')
        self.assertEqual((result['aggregate_calls'],result['retrieval_calls']),(1,1))
        self.assertEqual(len(matches),2)
        self.assertEqual(sum(s.startswith('SELECT count(*)') for s in matches),1)

    def test_invalid_partition_and_literal_syntax_cannot_retrieve(self):
        b=brief()
        for change in ('missing_required','duplicated_term','wrong_context_type','unsafe_literal'):
            with self.subTest(change=change):
                i=interpretation(b)
                if change=='missing_required':
                    i['intent']['required_groups']=[]
                elif change=='duplicated_term':
                    i['intent']['context_terms'].append('HTTPS')
                elif change=='wrong_context_type':
                    i['intent']['context_terms']='internal proxy'
                else:
                    i['terms'][0]='HTTPS*'
                    i['intent']['required_groups'][0]=['HTTPS*']
                with patch.object(runtime.retrieval,'count_matches',side_effect=AssertionError('invalid COUNT')):
                    with self.assertRaises(ValueError):
                        runtime.run(b,i,retrieve=lambda *args,**kwargs:self.fail('invalid request retrieved'))

    def test_browser_pack_uses_real_equal_weight_rrf_and_deprioritizes_mobile_only(self):
        # Exposed development regression, not a prospective quality judgment.
        b=brief('Browser automation for web UI testing.'); i=interpretation(b)
        i.update(route='browser_mobile_testing',terms=['browser','automation','testing'],
                 intent=dict(required_groups=[['browser']],context_terms=['automation','testing']),
                 excluded_repository_ids=[])
        captured=[]
        def retrieve(query,**kwargs):
            result=runtime.retrieval.retrieve(query,**kwargs)
            captured.append(result)
            return result
        result=runtime.run(b,i,retrieve=retrieve)
        self.assertEqual(result['status'],'ready')
        self.assertEqual(result['retrieval_calls'],1)
        raw=captured[0]
        self.assertEqual(raw['executed_variants'],len(result['request']['catalog_query']['variants']))
        policy=json.loads((runtime.ASSETS/'retrieval-policy.json').read_bytes())
        for row in raw['candidates']:
            self.assertAlmostEqual(row['rrf_score'],sum(1/(policy['rank_fusion']['k']+r['rank']) for r in row['variant_ranks']))
        # cavy is the measured mobile-only result in the browser-intent case.
        cavy=80435465
        self.assertIn(cavy,result['raw_ranked_ids'])
        packed=[row['card']['identity']['github_repository_id'] for row in result['evidence_pack']['cards']]
        self.assertNotIn(cavy,packed)
        self.assertEqual(result['raw_ranked_ids'],[row['github_repository_id'] for row in raw['candidates']])
        self.assertEqual(result['selected_ids'],result['raw_ranked_ids'])

    def test_derived_variant_retains_canonical_limits_and_original_terms(self):
        b=brief(); i=interpretation(b)
        request=runtime.prepare_from_brief(b,i)
        query=request['catalog_query']
        self.assertEqual(len(query['variants']),1)
        self.assertEqual(query['variants'][0]['terms'][:len(i['terms'])],i['terms'])
        policy=json.loads((runtime.ASSETS/'retrieval-policy.json').read_bytes())
        self.assertLessEqual(len(query['variants']),policy['limits']['max_query_variants'])
        self.assertEqual(query['max_candidates'],policy['limits']['max_retrieved_hits'])
        self.assertEqual(query['max_cards'],policy['limits']['max_detailed_cards'])
        self.assertEqual(query['max_evidence_bytes'],policy['limits']['max_evidence_bytes'])

    def test_bundled_guard_matches_frozen_development_implementation(self):
        self.assertEqual((ROOT/'scripts/guard_recommendation_request.py').read_bytes(),
                         (ROOT/'plugins/myai-stackguide/scripts/request_guard.py').read_bytes())


if __name__=='__main__':
    unittest.main()
