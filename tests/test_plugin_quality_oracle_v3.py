"""Pure validation assertions; do not load the new oracle before author READY."""
import importlib.util
from pathlib import Path
import unittest
import copy

ROOT=Path(__file__).resolve().parents[1]


class QualityOracleV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('test_fresh_source_v3',ROOT/'evals/plugin-v1/validate_oracle_v3.py')
        cls.validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.validator)

    def test_pointer_escapes_and_list_indices(self):
        self.assertEqual(self.validator.pointer_value({'a/b':{'~':[3]}},'/a~1b/~0/0'),3)
        for pointer in ('/a~2b','/a~1b/~0/00'):
            with self.assertRaises(ValueError):self.validator.pointer_value({'a/b':{'~':[3]}},pointer)

    def test_routed_universe_secondary_and_judgment_completeness(self):
        rows=[{'github_repository_id':1},{'github_repository_id':2}]
        self.validator.validate_universe([1,2],rows,{1,2})
        with self.assertRaises(ValueError):self.validator.validate_universe([1,2],rows,{1,2,3})
        with self.assertRaises(ValueError):self.validator.validate_universe([1,2],rows[:1],{1,2})
        with self.assertRaises(ValueError):self.validator.validate_universe([1,2],rows+rows[:1],{1,2})

    def row(self):
        return {'relevance_grade':2,'assessment_status':'source_supported','adoption_fit':'unknown',
            'denied_by_frozen_constraints':False,'contribution_rationale':'Source states core function.',
            'unknown_reason':None,'source_evidence':[{'pointer':'/cards/0/descriptions/upstream','value':'A useful function'}]}

    def test_grade_status_positive_evidence_and_supporting_scope(self):
        criteria={'explicit_supporting_function':'None; outside supporting scope.'}
        self.validator.validate_grade(self.row(),criteria)
        for patch in ({'relevance_grade':True},{'relevance_grade':1},
            {'assessment_status':'unknown'},{'source_evidence':[{'pointer':'/cards/0/identity','value':'identity alone'}]}):
            with self.assertRaises(ValueError):self.validator.validate_grade({**self.row(),**patch},criteria)
        unknown={**self.row(),'relevance_grade':None,'assessment_status':'unknown','unknown_reason':'Missing source.'}
        self.validator.validate_grade(unknown,criteria)
        with self.assertRaises(ValueError):self.validator.validate_grade({**unknown,'unknown_reason':None},criteria)

    def test_snapshot_reference_cannot_point_to_another_card(self):
        path=self.validator.SNAPSHOT
        card={'identity':{'github_repository_id':1},'evidence':[{'source_ref':'snapshot/1','observed_at':None}]}
        docs={path:{'cards':[card,copy.deepcopy(card)]}}
        reference={'path':path,'pointer':'/cards/1/identity/github_repository_id','value':1,
            'evidence_ref':'snapshot/1','observed_at':None,'source_snapshot_date':'2026-09-01','observation_date_status':'unknown'}
        with self.assertRaisesRegex(ValueError,'wrong card owner'):self.validator.validate_source_reference(reference,docs,card,0,'2026-09-01')

    def test_public_qualification_requires_case_repo_url_and_date_binding(self):
        path='research/synthetic-safe.json';card={'identity':{'github_repository_id':1,'full_name':'owner/tool'}}
        check={'criterion':'core','disposition':'supported','source_url':'https://github.com/owner/tool','observed_at':'2026-10-08T00:00:00Z',
            'source_kind':'upstream_readme','source_excerpt':'A core function','concise_rationale':'Core is explicit.'}
        record={'case_id':'SYNTHETIC','github_repository_id':1,'repository':'owner/tool','adoption_fit':'unknown','requirement_checks':[check]}
        docs={path:{'schema_version':'cp04_public_qualification_v1','records':[record]}}
        reference={'path':path,'pointer':'/records/0/requirement_checks/0','value':check,'source_kind':'public_primary_live',
            'source_url':check['source_url'],'observed_at':check['observed_at']}
        self.validator.validate_source_reference(reference,docs,card,0,'2026-09-01','SYNTHETIC')
        for patch in ({'source_url':'https://github.com/wrong/owner'},{'observed_at':None}):
            with self.assertRaises(ValueError):self.validator.validate_source_reference({**reference,**patch},docs,card,0,'2026-09-01','SYNTHETIC')
        with self.assertRaises(ValueError):self.validator.validate_source_reference(reference,docs,card,0,'2026-09-01','WRONGCASE')

    def date_reference(self, value='2026-10-08', declared=True):
        path='research/synthetic-date.json';card={'identity':{'github_repository_id':1,'full_name':'owner/tool'}}
        check={'criterion':'core','disposition':'supported','source_url':'https://github.com/owner/tool',
            'observed_at':value,'source_kind':'upstream_readme','source_excerpt':'','concise_rationale':'Core explicit.'}
        record={'case_id':'SYNTHETIC','github_repository_id':1,'repository':'owner/tool','adoption_fit':'unknown','requirement_checks':[check]}
        document={'schema_version':'cp04_public_qualification_v1','qualification_date':'2026-10-08','records':[record]}
        if declared:document['metadata_gaps']={'observation_timestamp_semantics':'observed_at is the UTC retrieval date, not source update/push/commit/release date; search crawl ages are not repository activity.'}
        reference={'path':path,'pointer':'/records/0/requirement_checks/0','value':check,'source_kind':'public_primary_live',
            'source_url':check['source_url'],'observed_at':value}
        return reference,{path:document},card

    def test_explicit_utc_day_is_accepted_without_fabricated_timestamp(self):
        reference,documents,card=self.date_reference()
        result=self.validator.validate_source_reference(reference,documents,card,0,'2026-09-01','SYNTHETIC')
        self.assertEqual(result['observation_granularity'],'day')
        self.assertEqual(reference['observed_at'],'2026-10-08')

    def test_dates_require_exact_valid_day_and_declared_granularity(self):
        for value in ('2026-10','2026-10-08garbage','2026-02-30','2026-1-08','2026-10-07'):
            reference,documents,card=self.date_reference(value)
            with self.assertRaises(ValueError):self.validator.validate_source_reference(reference,documents,card,0,'2026-09-01','SYNTHETIC')
        reference,documents,card=self.date_reference(declared=False)
        with self.assertRaises(ValueError):self.validator.validate_source_reference(reference,documents,card,0,'2026-09-01','SYNTHETIC')
        reference,documents,card=self.date_reference('2026-10-08T12:34:56Z',declared=False)
        self.assertEqual(self.validator.validate_source_reference(reference,documents,card,0,'2026-09-01','SYNTHETIC')['observation_granularity'],'timestamp')
        for value in ('2026-10-08T24:00:00Z','2026-10-08T12:34:56Zgarbage','2026-10-08T12:34:56+00:00'):
            reference,documents,card=self.date_reference(value)
            with self.assertRaises(ValueError):self.validator.validate_source_reference(reference,documents,card,0,'2026-09-01','SYNTHETIC')

    def test_declared_real_qualification_date_preserves_pinned_artifact(self):
        import hashlib
        path=ROOT/'research/cp04-public-qualification-2026-10-08.json'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),'e4cb74f805d9d8f178cc96eb96aff6d48eea2e65543da3653eb9361fde1df239')
        document=self.validator.scorer._load_json_bounded(path,4*1024*1024)
        for record in document['records']:
            for check in record['requirement_checks']:
                self.assertEqual(self.validator.public_observation_granularity(document,check['observed_at']),'day')


if __name__=='__main__':unittest.main()
