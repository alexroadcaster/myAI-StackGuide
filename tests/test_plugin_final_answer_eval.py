"""Distinct failures in the recorded same-canonical answer protocol."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('answer_audit',ROOT/'evals/plugin-v1/audit_final_answers.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def pair():
    result={'evidence_pack':{'cards':[{'card':{'identity':{'github_repository_id':2703394,'html_url':'https://github.com/coleifer/huey'}}}]},
            'request':{'exclusions':{'repository_ids':[2771544]}},'selection':{'excluded':[]}}
    answer={'answer_markdown':'Huey fits the task. https://github.com/coleifer/huey',
            'recommended_ids':[2703394],'cited_urls':['https://github.com/coleifer/huey'],'planning_binding':{'scenario_id':'one'}}
    return {'case_id':'unit','result':result,'answers':{lang:{'normalized':copy.deepcopy(answer),'canonical_result_sha256':audit_digest(result)} for lang in ('ru','en')}}


def audit_digest(value):
    import hashlib,json
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


class AnswerAudit(unittest.TestCase):
    def test_consistent_pair(self):
        self.assertTrue(audit.validate_pair(pair()))

    def test_recommendation_outside_pack_rejected(self):
        row=pair();row['answers']['en']['normalized']['recommended_ids']=[2771544]
        with self.assertRaisesRegex(ValueError,'pack|excluded'):
            audit.validate_pair(row)

    def test_language_projection_cannot_change_planning(self):
        row=pair();row['answers']['en']['normalized']['planning_binding']['scenario_id']='changed'
        with self.assertRaisesRegex(ValueError,'planning'):
            audit.validate_pair(row)

    def test_stale_canonical_result_rejected(self):
        row=pair();row['answers']['ru']['canonical_result_sha256']='stale'
        with self.assertRaisesRegex(ValueError,'canonical'):
            audit.validate_pair(row)

    def test_invented_citation_rejected(self):
        row=pair();row['answers']['ru']['normalized']['cited_urls']=['https://example.org/invented']
        with self.assertRaisesRegex(ValueError,'citation'):
            audit.validate_pair(row)

    def test_invented_visible_link_cannot_hide_behind_metadata(self):
        row=pair();row['answers']['ru']['normalized']['answer_markdown']='[Wrong source](https://example.org/invented)'
        with self.assertRaisesRegex(ValueError,'citation'):
            audit.validate_pair(row)

    def test_internal_identifier_in_explanation_rejected(self):
        row=pair();row['answers']['ru']['normalized']['answer_markdown']='Pick numeric repository2703394.'
        with self.assertRaisesRegex(ValueError,'metadata'):
            audit.validate_pair(row)


if __name__=='__main__':
    unittest.main()
