"""Brief version binding, real active retrieval, and clarification no-call proof."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest

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
        result=runtime.run(b,i,retrieve=lambda *a,**k:self.fail('unresolved retrieval'))
        self.assertEqual(result['retrieval_calls'],0)
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

    def test_bundled_guard_matches_frozen_development_implementation(self):
        self.assertEqual((ROOT/'scripts/guard_recommendation_request.py').read_bytes(),
                         (ROOT/'plugins/myai-stackguide/scripts/request_guard.py').read_bytes())


if __name__=='__main__':
    unittest.main()
