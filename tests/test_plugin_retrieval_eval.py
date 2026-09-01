"""Synthetic C8 scorer tests; these are not product retrieval quality evidence."""

import copy
import importlib.util
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('retrieval_eval', ROOT / 'evals/plugin-v1/evaluate_retrieval.py')
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)


class MetricGoldenCases(unittest.TestCase):
    def test_perfect_and_reversed_graded_ranking(self):
        judgments = {'a': 3, 'b': 2, 'c': 1, 'd': 0}
        self.assertEqual(EVAL.ranking_metrics(['a', 'b', 'c'], judgments, 3),
                         {'recall_at_k': 1.0, 'ndcg_at_k': 1.0, 'relevant_count': 3})
        expected = (1 + 3 / math.log2(3) + 7 / 2) / (7 + 3 / math.log2(3) + 1 / 2)
        self.assertAlmostEqual(EVAL.ranking_metrics(['c', 'b', 'a'], judgments, 3)['ndcg_at_k'], expected)

    def test_denominator_includes_unretrieved_relevant_items(self):
        metrics = EVAL.ranking_metrics(['a', 'd'], {'a': 3, 'b': 2, 'c': 1, 'd': 0}, 2)
        self.assertEqual(metrics['recall_at_k'], 1 / 3)
        self.assertAlmostEqual(metrics['ndcg_at_k'], 7 / (7 + 3 / math.log2(3)))

    def test_empty_denominator_is_not_perfect_score(self):
        self.assertEqual(EVAL.ranking_metrics([], {}, 3),
                         {'recall_at_k': None, 'ndcg_at_k': None, 'relevant_count': 0})
        self.assertEqual(EVAL.ranking_metrics([], {'a': 1}, 3)['recall_at_k'], 0)

    def test_duplicate_unjudged_and_invalid_grade_are_rejected(self):
        for ids, grades, k in [(['a', 'a'], {'a': 3}, 2), (['b'], {'a': 3}, 2),
                               (['a'], {'a': True}, 2), (['a'], {'a': 4}, 2),
                               (['a'], {'a': 1}, True), (['a'], {'a': 1}, 0)]:
            with self.subTest(ids=ids, grades=grades, k=k), self.assertRaises(ValueError):
                EVAL.ranking_metrics(ids, grades, k)

    def test_nonfinite_duplicate_json_and_input_caps(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'
            for value in ['{"x":NaN}', '{"x":Infinity}', '{"x":1e999}', '{"x":1,"x":2}']:
                path.write_text(value, encoding='utf-8')
                with self.subTest(value=value), self.assertRaises(ValueError):
                    EVAL.load_json(path)
            path.write_bytes(b' ' * (EVAL.MAX_INPUT_BYTES + 1))
            with self.assertRaisesRegex(ValueError, 'input byte limit'):
                EVAL.load_json(path)


class CaptureSemanticCases(unittest.TestCase):
    """Explicit semantic-only checks; do not call the schema-dependent grading gate."""

    @classmethod
    def setUpClass(cls):
        cls.cases = EVAL.load_json(ROOT / 'evals/plugin-v1/cases.json')
        cls.captures = EVAL.load_json(ROOT / 'tests/fixtures/plugin_retrieval_eval.json')

    def test_four_synthetic_c9_relational_examples(self):
        captures = {item['case_id']: item for item in self.captures['records']}
        for case in self.cases['cases']:
            capture = captures[case['case_id']]
            with self.subTest(case=case['case_id']):
                EVAL.validate_capture(case, capture, None)

    def test_c9_semantic_pin_status_rank_measurement_negatives(self):
        for mutation in [lambda v: v['retrieval']['pins'].update(index_sha256='f' * 64),
                         lambda v: v['retrieval']['candidates'][0].update(rank=2),
                         lambda v: v['evidence_pack'].update(status='unavailable'),
                         lambda v: v['measurements'].update(evidence_pack_bytes=1),
                         lambda v: v['measurements'].update(latency_ms=1)]:
            capture = copy.deepcopy(self.captures['records'][0])
            mutation(capture)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                EVAL.validate_capture(self.cases['cases'][0], capture, None)

    def test_cp03_and_c8_semantic_oracles_agree_on_independent_defects(self):
        spec = importlib.util.spec_from_file_location('cp03_semantic_oracle', ROOT / 'tests/test_plugin_contracts.py')
        cp03 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cp03)
        for pointer, value in [('/evidence_pack/cards/0/card/identity/full_name_aliases',
                               [self.captures['records'][0]['evidence_pack']['cards'][0]['card']['identity']['full_name']]),
                              ('/evidence_pack/cards/0/card/repository/license', 'GPL-3.0-only'),
                              ('/evidence_pack/cards/0/eligibility/checks/0/evidence_refs', ['invented']),
                              ('/evidence_pack/cards/0/card/activity/observations/2/source_field', 'repository_pushed_at')]:
            state = cp03.mutate(cp03.baseline(), pointer, value)
            with self.subTest(cp03_pointer=pointer), self.assertRaises(ValueError):
                cp03.check_bundle(state)
            capture = copy.deepcopy(self.captures['records'][0])
            capture['evidence_pack'] = state['evidence_pack']
            with self.subTest(c8_pointer=pointer), self.assertRaises(ValueError):
                EVAL.validate_capture(self.cases['cases'][0], capture, None)


class CapturedContractCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = EVAL.Contracts()  # Missing dependency is a failed gate, never skipped.
        cls.cases = EVAL.load_json(ROOT / 'evals/plugin-v1/cases.json')
        cls.captures = EVAL.load_json(ROOT / 'tests/fixtures/plugin_retrieval_eval.json')

    def grade(self, captures=None, cases=None):
        return EVAL.evaluate(cases or self.cases, captures or self.captures, self.contracts)

    def invalid(self, mutate, message=None):
        captures = copy.deepcopy(self.captures)
        mutate(captures)
        context = self.assertRaisesRegex(ValueError, message) if message else self.assertRaises(ValueError)
        with context:
            self.grade(captures)

    def test_four_bidirectional_c9_captures(self):
        report = self.grade()
        self.assertTrue(report['passed'])
        self.assertEqual(len(report['records']), 4)
        self.assertFalse(report['promotion_ready'])
        self.assertFalse(report['quality_thresholds_calibrated'])
        self.assertIsNone(report['records'][3]['ranking'])
        self.assertIsNone(report['records'][1]['ranking']['recall_at_k'])
        positive = EVAL.load_json(ROOT / 'tests/fixtures/plugin_contracts.json')['positive']
        first = self.captures['records'][0]
        self.assertEqual(first['retrieval'], positive['retrieval/retrieval-result.schema.json'])
        self.assertEqual(first['evidence_pack'], positive['retrieval/evidence-pack.schema.json'])
        for item in self.captures['records']:
            self.contracts.validate('retrieval/retrieval-result.schema.json', item['retrieval'])
            self.contracts.validate('retrieval/evidence-pack.schema.json', item['evidence_pack'])

    def test_real_c9_ref_rejects_invalid_shape_in_c8(self):
        self.invalid(lambda value: value['records'][0]['retrieval'].update(private_context='SYNTHETIC_CANARY'),
                     'schema validation')
        self.invalid(lambda value: value['records'][0]['retrieval'].update(source_mode='live_github'),
                     'schema validation')

    def test_ids_case_digest_versions_and_index_pins(self):
        for mutate in [
            lambda v: v.update(case_set_sha256='f' * 64),
            lambda v: v['records'][0]['retrieval'].update(query_id='wrong-query'),
            lambda v: v['records'][0]['retrieval'].update(run_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'),
            lambda v: v['records'][0]['retrieval'].update(query_sha256='f' * 64),
            lambda v: v['records'][0]['retrieval'].update(brief_version=2),
            lambda v: v['records'][0]['retrieval']['pins'].update(index_sha256='f' * 64),
            lambda v: v['records'][0]['retrieval']['pins'].update(card_schema_version='1.0.0'),
            lambda v: v['records'][0]['retrieval']['pins'].update(activity_schema_version='1.0.0'),
            lambda v: v['records'][0]['retrieval']['pins'].update(index_format_version=1),
            lambda v: v['records'][0]['retrieval']['pins'].update(retrieval_policy_version='1.0.0'),
            lambda v: v['records'][0]['evidence_pack'].update(query_sha256='f' * 64),
        ]:
            with self.subTest(mutation=mutate):
                self.invalid(mutate)

    def test_c9_v2_rejects_legacy_or_generic_repository_identity(self):
        for mutate in [
            lambda v: v['records'][0]['retrieval']['candidates'][0].update(
                github_repository_id='catalog-record-id'),
            lambda v: v['records'][0]['evidence_pack']['cards'][0]['card']['identity'].update(
                github_repository_id='900000001'),
            lambda v: v['records'][0]['evidence_pack']['cards'][0]['eligibility'].update(
                github_repository_id=0),
            lambda v: v['records'][0]['retrieval']['candidates'][0].update(
                repo_id='catalog-record-id'),
        ]:
            with self.subTest(mutation=mutate):
                self.invalid(mutate)

    def test_record_cardinality_and_unknown_case(self):
        self.invalid(lambda v: v['records'].pop())
        self.invalid(lambda v: v['records'].append(copy.deepcopy(v['records'][0])))
        self.invalid(lambda v: v['records'][0].update(case_id='unknown-case'))

    def test_duplicate_ranks_variant_positions_and_hit_budget(self):
        for mutate in [
            lambda v: v['records'][0]['retrieval']['candidates'][0].update(rank=2),
            lambda v: v['records'][0]['retrieval']['candidates'].append(copy.deepcopy(v['records'][0]['retrieval']['candidates'][0])),
            lambda v: v['records'][0]['retrieval']['candidates'][0]['variant_ranks'][1].update(variant_id='q1'),
            lambda v: v['records'][0]['retrieval'].update(retrieved_hits=61),
            lambda v: v['records'][0]['retrieval'].update(executed_variants=1),
            lambda v: v['records'][0]['retrieval']['candidates'][0].update(rrf_score=0.5),
        ]:
            with self.subTest(mutation=mutate):
                self.invalid(mutate)

    def test_failure_is_not_no_match_and_null_success_is_invalid(self):
        self.invalid(lambda v: v['records'][1]['retrieval'].update(reason_codes=['fts5_unavailable']),
                     'failure disguised')
        self.invalid(lambda v: v['records'][1]['retrieval'].update(executed_variants=0), 'unexecuted no-match')
        self.invalid(lambda v: v['records'][0]['retrieval'].update(pins=None))
        self.invalid(lambda v: v['records'][3]['retrieval'].update(status='no_match'))
        self.invalid(lambda v: v['records'][0]['evidence_pack'].update(status='unavailable'))

    def test_wrong_no_match_does_not_pass(self):
        captures = copy.deepcopy(self.captures)
        first = captures['records'][0]
        first['retrieval'].update(status='no_match', candidates=[], retrieved_hits=0, reason_codes=['no_hits'])
        first['evidence_pack'].update(status='no_match', cards=[], reason_codes=['no_hits'])
        first['measurements']['evidence_pack_bytes'] = len(EVAL.canonical(first['evidence_pack']))
        report = self.grade(captures)
        self.assertFalse(report['passed'])
        self.assertFalse(report['records'][0]['status_match'])
        self.assertEqual(report['records'][0]['ranking']['recall_at_k'], 0.0)

    def test_independent_constraint_judgment_overrides_self_reported_eligibility(self):
        captures = copy.deepcopy(self.captures)
        cases = copy.deepcopy(self.cases)
        cases['cases'][0]['judgments'][0]['constraint'] = 'denied'
        cases['cases'][0]['judgments'][0]['rationale'] = 'Independent synthetic adjudication denies this identity despite its captured eligible label.'
        captures['case_set_sha256'] = EVAL.digest(cases)
        report = self.grade(captures, cases)
        self.assertEqual(report['records'][0]['hard_constraint_violations'], 1)
        self.assertFalse(report['passed'])

    def test_c9_semantic_card_alias_provenance_and_eligibility_join(self):
        for mutate in [
            lambda v: v['records'][0]['evidence_pack']['cards'][0]['card']['identity'].update(
                full_name_aliases=[v['records'][0]['evidence_pack']['cards'][0]['card']['identity']['full_name']]),
            lambda v: v['records'][0]['evidence_pack']['cards'][0]['card']['repository'].update(license='GPL-3.0-only'),
            lambda v: v['records'][0]['evidence_pack']['cards'][0]['card']['catalog'].update(status='accepted'),
            lambda v: v['records'][0]['evidence_pack']['cards'][0]['eligibility'].update(checks=[]),
            lambda v: v['records'][0]['evidence_pack']['cards'][0]['card']['activity']['observations'][2].update(
                source_field='repository_pushed_at'),
        ]:
            with self.subTest(mutation=mutate):
                self.invalid(mutate)

    def test_false_exclusion_is_independent_of_output_claim(self):
        captures = copy.deepcopy(self.captures)
        first = captures['records'][0]
        first['evidence_pack'].update(cards=[], status='no_match', reason_codes=['mandatory_fact_unknown'],
            exclusions=[{'github_repository_id':first['retrieval']['candidates'][0]['github_repository_id'],
                         'reason_codes':['mandatory_fact_unknown']}])
        first['measurements']['evidence_pack_bytes'] = len(EVAL.canonical(first['evidence_pack']))
        report = self.grade(captures)
        self.assertEqual(report['records'][0]['false_exclusions'], 1)
        self.assertFalse(report['passed'])

    def test_measurement_units_unknowns_and_nonfinite_values(self):
        for mutate in [
            lambda v: v['records'][0]['measurements'].update(evidence_pack_bytes=1),
            lambda v: v['records'][0]['measurements'].update(latency_ms=-1),
            lambda v: v['records'][0]['measurements'].update(latency_ms=1),
            lambda v: v['records'][0]['measurements'].update(input_tokens=100),
            lambda v: v['records'][0]['measurements'].update(plugin_input_bytes=0),
            lambda v: v['records'][0]['measurements'].update(evidence_pack_kib=1),
            lambda v: v['records'][0]['retrieval']['candidates'][0].update(rrf_score=float('nan')),
        ]:
            with self.subTest(mutation=mutate):
                self.invalid(mutate)

    def test_nested_utf8_budget_and_untrusted_dollar_ref_are_inert(self):
        def oversize(value):
            value['records'][0]['evidence_pack']['cards'][0]['card']['descriptions']['upstream'] = 'я' * 1801
        self.invalid(oversize)
        self.invalid(lambda v: v['records'][0].update(**{'$ref':'https://example.invalid/private'}))

    def test_nested_byte_limit_survives_dollar_schema_validator_reset(self):
        captures = copy.deepcopy(self.captures)
        card = captures['records'][0]['evidence_pack']['cards'][0]['card']
        for field in ('use_cases', 'best_for', 'tradeoffs', 'avoid_if'):
            card['advisory'][field] = ['я' * 498 + str(index) for index in range(10)]
        self.assertGreater(len(EVAL.canonical(card)), 24576)
        self.assertLess(len(EVAL.canonical(captures['records'][0]['evidence_pack'])), 49152)
        with self.assertRaisesRegex(ValueError, 'byte budget|schema validation'):
            self.grade(captures)

    def test_byte_walker_handles_allof_oneof_and_conditionals(self):
        value = {'text': 'я'}
        size = len(EVAL.canonical(value))
        schemas = [
            {'allOf': [{'x-max-utf8-bytes': size - 1}]},
            {'oneOf': [{'type': 'object', 'properties': {'text': {'x-max-utf8-bytes': 3}}}]},
            {'if': {'type': 'object'}, 'then': {'x-max-utf8-bytes': size - 1}},
        ]
        for schema in schemas:
            with self.subTest(schema=schema), self.assertRaises(ValueError):
                self.contracts.check_bytes(schema, value)

    def test_offline_registry_and_format_check(self):
        with self.assertRaises(Exception):
            self.contracts.registry.resolver().lookup('https://example.invalid/not-a-schema')
        cases = copy.deepcopy(self.cases)
        cases['cases'][0]['index_manifest']['built_at'] = '2026-99-99T00:00:00Z'
        with self.assertRaisesRegex(ValueError, 'schema validation'):
            EVAL.validate_cases(cases, self.contracts)

    def test_case_pin_corruption_and_duplicate_judgments(self):
        for mutate in [lambda c: c.update(contract_set_sha256='f' * 64),
                       lambda c: c['cases'][0]['query'].update(policy_sha256='f' * 64),
                       lambda c: c['cases'][0]['judgments'].append(copy.deepcopy(c['cases'][0]['judgments'][0]))]:
            cases = copy.deepcopy(self.cases)
            mutate(cases)
            with self.assertRaises(ValueError):
                EVAL.validate_cases(cases, self.contracts)

    def test_mandatory_constraint_cannot_have_missing_target(self):
        for key, value in [('allowed_licenses', []), ('languages', []), ('deployment', []),
                           ('compatibility', []), ('require_no_server', None)]:
            cases = copy.deepcopy(self.cases)
            cases['cases'][0]['query']['constraints'][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'mandatory'):
                EVAL.validate_cases(cases, self.contracts)

    def test_presentation_case_identity_join(self):
        cases = copy.deepcopy(self.cases)
        cases['presentation_cases'][0]['canonical_case_id'] = 'nonexistent'
        with self.assertRaisesRegex(ValueError, 'canonical presentation'):
            EVAL.validate_cases(cases, self.contracts)
        cases = copy.deepcopy(self.cases)
        cases['presentation_cases'].append(copy.deepcopy(cases['presentation_cases'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate presentation'):
            EVAL.validate_cases(cases, self.contracts)

    def test_cli_reports_success_failure_invalid_without_file_writes(self):
        with patch('builtins.print'):
            self.assertEqual(EVAL.main(['--cases', str(ROOT / 'evals/plugin-v1/cases.json')]), 0)
            self.assertEqual(EVAL.main(['--cases', str(ROOT / 'evals/plugin-v1/cases.json'),
                                       '--results', str(ROOT / 'tests/fixtures/plugin_retrieval_eval.json')]), 0)
            self.assertEqual(EVAL.main(['--cases', 'does-not-exist.json']), 2)


if __name__ == '__main__':
    unittest.main()
