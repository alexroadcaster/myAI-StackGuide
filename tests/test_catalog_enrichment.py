"""Synthetic collector failures and state recovery; no live GitHub evidence."""
import base64
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('enrich_catalog',ROOT/'scripts/enrich_catalog.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)


class FakeAPI:
    def __init__(self,stars=777,description='Synthetic backend example.'):
        self.calls=[];self.failures={};self.stars=stars;self.description=description

    def __call__(self,url,timeout,max_bytes):
        self.calls.append(url);path=urlsplit(url).path
        for suffix,response in self.failures.items():
            if path.endswith(suffix):return response
        if path.endswith('/languages'):data={'Python':100}
        elif '/git/ref/heads/' in path:data={'object':{'sha':'a'*40}}
        elif '/git/commits/' in path:data={'sha':'a'*40,'committer':{'date':'2026-08-30T00:00:00Z','email':'do-not-persist@example.org'}}
        elif path.endswith('/readme'):data={'type':'file','encoding':'base64','content':base64.b64encode(b'Synthetic Python backend fixture.').decode(),'path':'README.md','sha':'b'*40}
        elif path.endswith('/contents'):data=[]
        elif path.endswith('/releases/latest'):return 404,{},b''
        else:data={'id':123,'full_name':'unit/repo','html_url':'https://github.com/unit/repo','private':False,'visibility':'public','archived':False,'default_branch':'main','language':'Python','description':self.description,'stargazers_count':self.stars,'forks_count':3,'subscribers_count':4,'watchers_count':777,'created_at':'2020-01-01T00:00:00Z','pushed_at':'2026-08-30T00:00:00Z','owner':{'email':'private@example.org'}}
        return 200,{},json.dumps(data).encode()


class EnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name)
        self.input=self.base/'source.json'
        e.atomic_json(self.input,{'repositories':[{'id':'gh:unit/repo','fullName':'unit/repo','catalogStatus':'candidate','githubRepositoryId':None,'stars':0,'description':'Old snapshot description'}]})
        self.run=self.base/'run'
        e.create_plan(self.run,self.input,ROOT/'specs/catalog/taxonomy.yaml',ROOT/'specs/catalog/enrichment-field-contract.json')
        self.api=FakeAPI()

    def tearDown(self):self.tmp.cleanup()

    def review(self):
        fields={'reviewStatus':'reviewed','primaryCategory':'backend_frameworks','secondaryCategories':[],
                'stack':[{'technology':'Python','evidenceRefs':['readme']}],
                'recommendation.whyRecommended':'Synthetic fixture comparison.',
                'recommendation.bestFor':'Synthetic backend checks.',
                'recommendation.tradeoffs':'Synthetic only, no product evidence.',
                'recommendation.adoption_status':'inspect'}
        return {'sourceId':'gh:unit/repo','fields':fields,'evidenceRefs':{k:['readme'] for k in fields}}

    def test_complete_card_all_groups_and_no_private_actor_fields(self):
        c=e.Collector(self.run,self.api);r=c.process('gh:unit/repo',self.review())
        self.assertEqual(r['status'],'complete_card');self.assertEqual(r['missingMandatory'],[])
        self.assertEqual(r['values']['watchers'],4);self.assertEqual(len(r['values']['fieldObservations']),71)
        text=json.dumps(r);self.assertNotIn('private@example.org',text);self.assertNotIn('do-not-persist',text)
        self.assertTrue(any('/readme?ref='+('a'*40) in x for x in self.api.calls))
        self.assertEqual(c.verify()['verifiedRecords'],1)

    def test_successful_blocks_are_not_refetched_on_resume(self):
        e.Collector(self.run,self.api).process('gh:unit/repo')
        count=len(self.api.calls)
        r=e.Collector(self.run,self.api).process('gh:unit/repo',self.review())
        self.assertEqual(len(self.api.calls),count);self.assertEqual(r['status'],'complete_card')
        self.assertEqual(e.Collector(self.run,self.api).process('gh:unit/repo')['status'],'complete_card')

    def test_failed_block_only_is_retried(self):
        self.api.failures['/languages']=(500,{},b'')
        with patch.object(e.time,'sleep'):e.Collector(self.run,self.api).process('gh:unit/repo')
        before=len(self.api.calls);self.api.failures.clear()
        e.Collector(self.run,self.api).process('gh:unit/repo')
        self.assertEqual(len(self.api.calls)-before,1);self.assertTrue(self.api.calls[-1].endswith('/languages'))

    def test_unsupported_readme_shape_is_terminal_and_not_retried(self):
        self.api.failures['/readme']=(200,{},json.dumps({'type':'symlink','target':'README.md'}).encode())
        first=e.Collector(self.run,self.api).process('gh:unit/repo')
        self.assertEqual(first['blocks']['readme']['status'],'source_unsupported')
        before=len(self.api.calls)
        second=e.Collector(self.run,self.api).process('gh:unit/repo')
        self.assertEqual(len(self.api.calls),before)
        self.assertEqual(second['blocks']['readme']['reason'],'invalid_or_unsafe_source_shape')

    def test_null_stars_never_become_zero_or_old_value(self):
        self.api.stars=None;r=e.Collector(self.run,self.api).process('gh:unit/repo')
        self.assertIsNone(r['values']['stars']);self.assertIn('stars',r['missingMandatory'])
        self.assertIn('stars_unknown',r['values']['eligibility']['reasons'])

    def test_numeric_string_repository_id_matches_github_integer(self):
        source=e.load(self.input)
        source['repositories'][0]['githubRepositoryId']='123'
        e.atomic_json(self.input,source)
        run=self.base/'numeric-string-id'
        e.create_plan(run,self.input,ROOT/'specs/catalog/taxonomy.yaml',ROOT/'specs/catalog/enrichment-field-contract.json')
        record=e.Collector(run,self.api).process('gh:unit/repo')
        self.assertEqual(record['values']['identityStatus'],'resolved')
        self.assertEqual(e.load(run/'checkpoint.json')['identities'],{'123':'gh:unit/repo'})

    def test_confirmed_zero_is_preserved_and_blocked(self):
        self.api.stars=0;r=e.Collector(self.run,self.api).process('gh:unit/repo')
        self.assertEqual(r['values']['stars'],0);self.assertIn('confirmed_zero_stars',r['values']['eligibility']['reasons'])

    def test_low_stars_are_excluded_after_metadata_without_more_requests(self):
        self.api.stars=499;r=e.Collector(self.run,self.api).process('gh:unit/repo')
        self.assertIn('confirmed_below_minimum_stars',r['values']['eligibility']['reasons'])
        self.assertEqual(r['status'],'excluded_below_star_threshold')
        self.assertTrue(r['values']['eligibility']['replacementRequired'])
        self.assertEqual(len(self.api.calls),1)
        self.assertNotIn('readme',r['blocks'])
        self.assertEqual(e.Collector(self.run,self.api).execute()['attempted'],0)
        self.assertEqual(len(self.api.calls),1)

    def test_missing_description_requires_reviewed_summary(self):
        self.api.description=None;r=e.Collector(self.run,self.api).process('gh:unit/repo',self.review())
        self.assertIn('catalogDescription',r['missingMandatory'])
        self.assertNotIn('Old snapshot description',json.dumps(r))

    def test_exactly_500_stars_can_pass_data_gate(self):
        self.api.stars=500;r=e.Collector(self.run,self.api).process('gh:unit/repo',self.review())
        self.assertEqual(r['status'],'complete_card')
        self.assertFalse(r['values']['eligibility']['replacementRequired'])

    def test_build_omits_low_stars_and_preserves_exclusion_and_replacement_queue(self):
        self.api.stars=499;c=e.Collector(self.run,self.api);c.process('gh:unit/repo')
        result=c.build();self.assertEqual(result['excludedRecords'],1)
        self.assertEqual(e.load(self.run/'candidate-cards.json')['cards'],[])
        self.assertEqual(e.load(self.run/'candidate-cards.json')['pendingCards'],[])
        self.assertEqual(e.load(self.run/'excluded-records.json')['records'][0]['values']['stars'],499)
        self.assertEqual(e.load(self.run/'replacement-queue.json')['items'][0]['status'],'replacement_search_required')
        e.atomic_json(self.run/'replacement-resolutions.json',{'gh:unit/repo':'gh:unit/not-verified'})
        with self.assertRaisesRegex(ValueError,'verified complete card'):c.build()

    def test_old_exception_contract_requires_explicit_migration(self):
        legacy=self.base/'legacy-run'
        e.create_plan(legacy,self.input,ROOT/'specs/catalog/taxonomy.yaml',ROOT/'tests/fixtures/catalog_enrichment_legacy_contract.json')
        with self.assertRaisesRegex(ValueError,'strict 500-Star minimum'):e.Collector(legacy,self.api)

    def test_rate_limit_stops_requests_and_persists_wait(self):
        self.api.failures['/repos/unit/repo']=(429,{'Retry-After':'120'},b'')
        c=e.Collector(self.run,self.api);c.process('gh:unit/repo')
        self.assertEqual(len(self.api.calls),1);self.assertGreater(c.state['retryNotBefore'],e.time.time())
        e.Collector(self.run,self.api).process('gh:unit/repo');self.assertEqual(len(self.api.calls),1)

    def test_rate_limit_evidence_is_allowlisted_without_credential_headers(self):
        def headers(url,timeout,max_bytes):
            code,_,body=self.api(url,timeout,max_bytes)
            return code,{'X-RateLimit-Limit':'60','X-RateLimit-Remaining':'29','Authorization':'secret-must-not-be-logged','Set-Cookie':'private-cookie'},body
        c=e.Collector(self.run,headers);c.process('gh:unit/repo')
        self.assertEqual(c.state['lastRateLimit']['x-ratelimit-remaining'],'29')
        trace=(self.run/'request-log.jsonl').read_text(encoding='utf-8')
        self.assertIn('x-ratelimit-limit',trace)
        self.assertNotIn('secret-must-not-be-logged',trace)
        self.assertNotIn('private-cookie',trace)

    def test_external_redirect_is_rejected(self):
        self.api.failures['/repos/unit/repo']=(301,{'Location':'https://example.com/private'},b'')
        r=e.Collector(self.run,self.api).process('gh:unit/repo')
        self.assertEqual(r['blocks']['metadata']['reason'],'unsafe_redirect');self.assertEqual(len(self.api.calls),1)

    def test_token_query_and_non_repository_paths_are_rejected(self):
        for url in ['https://api.github.com/repos/unit/repo?access_token=secret','https://api.github.com/users/unit','https://api.github.com/repos/../user']:
            with self.subTest(url=url),self.assertRaises(ValueError):e.safe_api_url(url)

    def test_changed_source_stops_resume(self):
        self.input.write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'changed'):e.Collector(self.run,self.api)

    def test_container_cannot_pass_curation(self):
        review=self.review();review['fields']['primaryCategory']='backend_baas_api'
        with self.assertRaisesRegex(ValueError,'Invalid primary category'):e.Collector(self.run,self.api).process('gh:unit/repo',review)

    def test_byte_budget_and_request_budget_are_hard_stops(self):
        plan=e.load(self.run/'plan.json');plan['maxRequests']=1;e.atomic_json(self.run/'plan.json',plan)
        c=e.Collector(self.run,self.api);r=c.process('gh:unit/repo')
        self.assertEqual(c.state['requests'],1);self.assertEqual(len(self.api.calls),1)
        self.assertEqual(r['blocks']['languages']['status'],'budget_exhausted')

    def test_oversized_response_is_not_persisted(self):
        plan=e.load(self.run/'plan.json');plan['maxResponseBytes']=2;e.atomic_json(self.run/'plan.json',plan)
        r=e.Collector(self.run,self.api).process('gh:unit/repo')
        self.assertEqual(r['blocks']['metadata']['reason'],'response_size')
        self.assertEqual(r['blocks']['metadata']['status'],'source_unsupported')
        self.assertNotIn('data',r['blocks']['metadata'])

    def test_pending_review_does_not_starve_next_record_and_alias_is_verified(self):
        source=e.load(self.input);source['repositories'].append({**source['repositories'][0],'id':'gh:unit/old-name','fullName':'unit/old-name'})
        e.atomic_json(self.input,source);run=self.base/'two-records'
        e.create_plan(run,self.input,ROOT/'specs/catalog/taxonomy.yaml',ROOT/'specs/catalog/enrichment-field-contract.json')
        e.Collector(run,self.api).execute();before=len(self.api.calls)
        c=e.Collector(run,self.api);c.execute()
        self.assertEqual(len(self.api.calls)-before,1)
        self.assertEqual(c.state['records']['gh:unit/old-name'],'verified_identity_alias')
        self.assertEqual(c.verify()['verifiedRecords'],2)

    def test_tampered_derived_values_fail_verification(self):
        c=e.Collector(self.run,self.api);c.process('gh:unit/repo',self.review())
        path=c.record_path('gh:unit/repo');r=e.load(path);r['values']['stars']=999999;e.atomic_json(path,r)
        with self.assertRaisesRegex(ValueError,'differs'):c.verify()

    def test_interrupted_temporary_file_does_not_replace_checkpoint(self):
        p=self.run/'checkpoint.json';before=e.load(p);p.with_suffix('.json.tmp').write_text('{broken',encoding='utf-8')
        self.assertEqual(e.Collector(self.run,self.api).state,before)
        e.atomic_json(p,{**before,'requests':1});self.assertEqual(e.load(p)['requests'],1)

    def test_redact_credentials_and_emails_in_public_excerpt(self):
        text=e.clean_excerpt('email@example.org ghp_abcdefghijklmnopqrstuvwxyz')
        self.assertNotIn('email@',text);self.assertNotIn('ghp_',text)

    def test_public_excerpt_redacts_personal_local_paths(self):
        text=e.clean_excerpt(r'[workflow](/Users/sample/Development/app/deploy.yml) C:\Users\sample\project\file /home/sample/config https://github.com/unit/repo')
        self.assertEqual(text.count('[LOCAL PATH REDACTED]'),3)
        self.assertNotIn('sample',text)
        self.assertIn('https://github.com/unit/repo',text)

    def test_selected_complete_repository_resume_never_advances_queue(self):
        source=e.load(self.input);source['repositories'].append({**source['repositories'][0],'id':'gh:unit/other','fullName':'unit/other'})
        e.atomic_json(self.input,source);run=self.base/'selected-record'
        e.create_plan(run,self.input,ROOT/'specs/catalog/taxonomy.yaml',ROOT/'specs/catalog/enrichment-field-contract.json')
        e.Collector(run,self.api).process('gh:unit/repo',self.review())
        before=len(self.api.calls)
        c=e.Collector(run,self.api)
        self.assertEqual(c.execute(repository='gh:unit/repo')['attempted'],0)
        self.assertEqual(len(self.api.calls),before)
        self.assertNotIn('gh:unit/other',c.state['records'])
        with self.assertRaisesRegex(ValueError,'frozen queue'):c.execute(repository='gh:unit/unknown')

    def test_missing_primary_language_cannot_pass_mandatory_gate(self):
        def no_language(url,timeout,max_bytes):
            code,headers,body=self.api(url,timeout,max_bytes)
            if urlsplit(url).path=='/repos/unit/repo':
                raw=json.loads(body);raw['language']=None;body=json.dumps(raw).encode()
            return code,headers,body
        r=e.Collector(self.run,no_language).process('gh:unit/repo',self.review())
        self.assertIn('language',r['missingMandatory'])
        self.assertIsNone(r['values']['language'])

    def test_safe_redirect_preserves_canonical_identity_and_attempt_count(self):
        def redirect(url,timeout,max_bytes):
            if urlsplit(url).path=='/repos/unit/repo':return 301,{'Location':'https://api.github.com/repositories/123'},b''
            return self.api(url,timeout,max_bytes)
        c=e.Collector(self.run,redirect);r=c.process('gh:unit/repo',self.review())
        self.assertEqual(r['status'],'complete_card')
        self.assertEqual(r['values']['githubRepositoryId'],123)
        self.assertEqual(c.state['requests'],len(self.api.calls)+1)

    def test_retired_category_is_rejected(self):
        review=self.review();review['fields']['primaryCategory']='frontend_ui_desktop_browser'
        with self.assertRaisesRegex(ValueError,'Invalid primary category'):e.Collector(self.run,self.api).process('gh:unit/repo',review)


if __name__=='__main__':unittest.main()
