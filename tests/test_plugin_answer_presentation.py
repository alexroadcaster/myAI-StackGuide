"""Objective text and single-scenario planning checks, not translation grading."""
from pathlib import Path
import copy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'plugins/myai-stackguide/scripts'))
import answer_presentation as presentation


def facts(scope='validation_only'):
    return dict(scenario_id='synthetic-validation-scenario', scope_status=scope,
                assumptions=dict(prerequisites=['Supported local runtime'],
                                 team_experience='One engineer familiar with the current stack',
                                 confidence='low', hours_per_engineer_day=6,
                                 allocated_engineers=0.5),
                first_validation=dict(min=4, max=8), phases=[])


class AnswerPresentation(unittest.TestCase):
    def test_prose_newlines_preserve_code_json_and_windows_paths(self):
        text = 'First paragraph.\\n\\nNext paragraph.\\n- Check `print("a\\nb")` at C:\\new\\notes.txt.\n```python\ns = "a\\nb"\n```\n{"text":"a\\nb"}'
        expected = 'First paragraph.\n\nNext paragraph.\n- Check `print("a\\nb")` at C:\\new\\notes.txt.\n```python\ns = "a\\nb"\n```\n{"text":"a\\nb"}'
        self.assertEqual(presentation.normalize_answer_text(text), expected)

    def test_ambiguous_and_doubly_escaped_tokens_remain_literal(self):
        text = r'Relative path docs\new\notes.txt and relative\new; docs\n\note, file.txt\new, \new\notes.txt; escaped \\n; URL https://example.test/\n.'
        self.assertEqual(presentation.normalize_answer_text(text), text)

    def test_crlf_prose_is_idempotent_without_general_escape_decoding(self):
        text = r'First.\r\nSecond.\n\nThird; keep \t and \u0410.'
        expected = 'First.\nSecond.\n\nThird; keep \\t and \\u0410.'
        normalized = presentation.normalize_answer_text(text)
        self.assertEqual(normalized, expected)
        self.assertEqual(presentation.normalize_answer_text(normalized), normalized)

    def test_multibacktick_tilde_and_unclosed_code_preserve_escapes(self):
        text = '`` literal ` and \\n ``\n~~~json\n{"n":"\\n"}\n~~~\n`unfinished\\n\\n'
        self.assertEqual(presentation.normalize_answer_text(text), text)

    def test_one_display_locale_from_explicit_bilingual_sections(self):
        text = '**Русский**\n\nРекомендация.\n\n---\n\n**English translation**\n\nRecommendation.'
        self.assertEqual(presentation.project_answer_locale(text, 'ru'), 'Рекомендация.')
        self.assertEqual(presentation.project_answer_locale(text, 'en'), 'Recommendation.')

    def test_language_heading_in_code_is_not_a_projection_boundary(self):
        text = 'Русский текст.\n```markdown\n**English**\nLiteral sample.\n```'
        self.assertEqual(presentation.project_answer_locale(text, 'ru'), text)
        with self.assertRaises(ValueError):
            presentation.project_answer_locale(text, 'de')

    def test_multiple_or_empty_translation_sections_are_rejected(self):
        for text in ('Русский.\n**English**\n', 'Русский.\n**English**\nOne.\n**English**\nTwo.'):
            with self.assertRaises(ValueError):
                presentation.project_answer_locale(text, 'ru')

    def test_only_validation_does_not_invent_total(self):
        original = facts()
        untouched = copy.deepcopy(original)
        result = presentation.validate_planning_facts(original)
        self.assertIsNone(result['total_engineer_hours'])
        self.assertIsNone(result['elapsed_working_days'])
        self.assertEqual(original, untouched)
        self.assertEqual(presentation.validate_planning_facts(result), result)

    def test_scoped_total_counts_validation_once_and_derives_capacity(self):
        original = facts('scoped_total')
        original['phases'] = [dict(name='integration', min=5, max=10), dict(name='rollback check', min=1, max=2)]
        result = presentation.validate_planning_facts(original)
        self.assertEqual(result['total_engineer_hours'], dict(min=10, max=20))
        self.assertEqual(result['elapsed_working_days'], dict(min=3.333333, max=6.666667))

    def test_invalid_numeric_bounds_and_capacity_are_rejected(self):
        changes = [(['first_validation', 'min'], -1),
                   (['first_validation', 'max'], 2),
                   (['first_validation', 'max'], float('nan')),
                   (['first_validation', 'max'], float('inf')),
                   (['first_validation', 'min'], True),
                   (['assumptions', 'allocated_engineers'], 0),
                   (['assumptions', 'allocated_engineers'], '1'),
                   (['assumptions', 'hours_per_engineer_day'], 25),
                   (['first_validation', 'max'], 10 ** 400)]
        for path, value in changes:
            with self.subTest(path=path, value=value):
                candidate = facts()
                candidate[path[0]][path[1]] = value
                with self.assertRaises(ValueError):
                    presentation.validate_planning_facts(candidate)

    def test_full_phases_require_scope_and_cannot_duplicate_validation(self):
        candidate = facts()
        candidate['phases'] = [dict(name='integration', min=4, max=8)]
        with self.assertRaises(ValueError):
            presentation.validate_planning_facts(candidate)
        candidate['scope_status'] = 'scoped_total'
        candidate['phases'][0]['name'] = 'first_validation'
        with self.assertRaises(ValueError):
            presentation.validate_planning_facts(candidate)
        candidate['phases'][0]['name'] = 'integration'
        candidate['phases'] += [dict(name=' INTEGRATION ', min=1, max=2)]
        with self.assertRaises(ValueError):
            presentation.validate_planning_facts(candidate)
        candidate['phases'] = []
        with self.assertRaises(ValueError):
            presentation.validate_planning_facts(candidate)

    def test_supplied_total_cannot_override_derived_or_unknown_scope(self):
        for scope in ('validation_only', 'scoped_total'):
            with self.subTest(scope=scope):
                candidate = facts(scope)
                if scope == 'scoped_total':
                    candidate['phases'] = [dict(name='integration', min=4, max=8)]
                candidate['total_engineer_hours'] = dict(min=1, max=2)
                with self.assertRaisesRegex(ValueError, 'derived'):
                    presentation.validate_planning_facts(candidate)

    def test_same_planning_binding_is_usable_for_both_locales(self):
        canonical = presentation.validate_planning_facts(facts())
        ru = presentation.planning_binding(canonical)
        en = copy.deepcopy(ru)
        presentation.validate_locale_planning_binding(canonical, ru)
        presentation.validate_locale_planning_binding(canonical, en)
        self.assertEqual(ru, en)
        self.assertEqual(len(ru['planning_sha256']), 64)
        self.assertEqual(presentation.planning_binding(facts()), ru)

    def test_stale_scope_assumptions_hash_and_locale_ranges_are_rejected(self):
        canonical = facts()
        binding = presentation.planning_binding(canonical)
        for change in ('hash', 'scenario', 'assumptions', 'range', 'total', 'extra'):
            with self.subTest(change=change):
                wrong = copy.deepcopy(binding)
                if change == 'hash':
                    wrong['planning_sha256'] = '0' * 64
                elif change == 'scenario':
                    wrong['scenario_id'] = 'another scenario'
                elif change == 'assumptions':
                    wrong['assumptions']['allocated_engineers'] = 1
                elif change == 'range':
                    wrong['first_validation']['max'] = 10
                elif change == 'total':
                    wrong['total_engineer_hours'] = dict(min=4, max=8)
                else:
                    wrong['unbound'] = 'text'
                with self.assertRaises(ValueError):
                    presentation.validate_locale_planning_binding(canonical, wrong)
        corrected = facts()
        corrected['first_validation']['max'] = 12
        with self.assertRaises(ValueError):
            presentation.validate_locale_planning_binding(corrected, binding)

    def test_unknown_fields_and_wrong_types_fail_explicitly(self):
        for candidate in (None, [], dict(facts(), unsupported=True)):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    presentation.validate_planning_facts(candidate)
        with self.assertRaises(ValueError):
            presentation.normalize_answer_text(None)

    def test_numeric_boolean_binding_and_arithmetic_overflow_are_rejected(self):
        candidate = facts()
        candidate['first_validation']['min'] = 1
        binding = presentation.planning_binding(candidate)
        binding['first_validation']['min'] = True
        with self.assertRaises(ValueError):
            presentation.validate_locale_planning_binding(candidate, binding)
        candidate = facts('scoped_total')
        candidate['first_validation'] = dict(min=1e308, max=1e308)
        candidate['phases'] = [dict(name='integration', min=1e308, max=1e308)]
        with self.assertRaisesRegex(ValueError, 'overflow'):
            presentation.validate_planning_facts(candidate)


if __name__ == '__main__':
    unittest.main()
