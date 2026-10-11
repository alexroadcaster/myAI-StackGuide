"""Experimental literal ranking: baseline anchor plus missing requirement evidence.

Term matches are diagnostics, not semantic capability verification. An unknown
requirement is retained, never converted into a hard mismatch or excluded.
"""
from __future__ import annotations

import unicodedata


def normalized(text):
    return unicodedata.normalize('NFKC', text).casefold()


def validate_intent(terms, intent):
    if not isinstance(intent, dict) or set(intent) != {'required_groups', 'context_terms'}:
        raise ValueError('invalid separated intent')
    groups, context = intent['required_groups'], intent['context_terms']
    if not isinstance(groups, list) or not groups or any(not isinstance(g, list) or not g for g in groups) or not isinstance(context, list):
        raise ValueError('invalid requirement groups')
    flattened = [t for g in groups for t in g] + context
    if any(not isinstance(t, str) or not t.strip() for t in flattened + terms):
        raise ValueError('invalid intent term')
    if len(set(map(normalized, flattened))) != len(flattened) or set(flattened) != set(terms) or len(flattened) != len(terms):
        raise ValueError('intent must partition original terms exactly')


def rank_cards(original_fields, added_capabilities, terms, intent, *, limit):
    """No oracle, case ID, external model or context-enrichment score is consumed.

Original field/term matches use the exact prior baseline arithmetic. New evidence
    adds one point per previously unmatched requirement group, only when
ALL requirement groups have lexical support. Context can retain its prior baseline
contribution but cannot gain points through new capabilities. Equal scores use ID.
"""
    validate_intent(terms, intent)
    if type(limit) is not int or limit < 1:
        raise ValueError('invalid ranking limit')
    if any(type(rid) is not int or rid < 1 for rid in original_fields) or not set(added_capabilities) <= set(original_fields):
        raise ValueError('invalid identity join')
    groups = intent['required_groups']
    records = []
    for rid, fields in original_fields.items():
        if not isinstance(fields, dict) or any(not isinstance(values, list) or any(not isinstance(v, str) for v in values) for values in fields.values()):
            raise ValueError('invalid public field projection')
        values = [[normalized(v) for v in field] for field in fields.values()]
        base_hits = {t: sum(any(normalized(t) in v for v in field) for field in values) for t in terms}
        additions = added_capabilities.get(rid, [])
        if not isinstance(additions, list) or any(not isinstance(v, str) for v in additions):
            raise ValueError('invalid capability projection')
        extra_hits = {t: any(normalized(t) in normalized(v) for v in additions) for t in terms}
        states = []
        for group in groups:
            states.append('original_lexical_support' if any(base_hits[t] for t in group) else
                          'new_lexical_support' if any(extra_hits[t] for t in group) else 'unknown')
        bonus_terms = [next(t for t in group if extra_hits[t]) for group, state in zip(groups, states)
                       if state == 'new_lexical_support'] if 'unknown' not in states else []
        baseline_score = sum(base_hits.values())
        score = baseline_score + len(bonus_terms)
        if score:
            records.append(dict(github_repository_id=rid, baseline_score=baseline_score,
                requirement_bonus=len(bonus_terms), bonus_terms=bonus_terms, score=score,
                requirement_states=states, new_context_hits=[t for t in intent['context_terms'] if extra_hits[t]],
                new_context_bonus=0))
    records.sort(key=lambda r: (-r['score'], r['github_repository_id']))
    return records[:limit]
