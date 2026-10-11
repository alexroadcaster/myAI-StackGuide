"""Isolated priority ordering over the source-qualified literal evaluator.

Support is lexical evidence, not semantic verification or hard eligibility.
The caller owns source trust and the full routed evaluation universe.
"""
from __future__ import annotations

import rank_capability_context as previous

MODES = ('new_required_first', 'all_required_first')


def rank_cards(original_fields, added_capabilities, terms, intent, *, limit, mode):
    if mode not in MODES:
        raise ValueError('unknown requirement priority mode')
    if type(limit) is not int or limit < 1:
        raise ValueError('invalid ranking limit')
    # Order the complete scored evaluation universe BEFORE applying the cap.
    rows = previous.rank_cards(original_fields, added_capabilities, terms, intent,
                               limit=max(1, len(original_fields)))
    for row in rows:
        complete = 'unknown' not in row['requirement_states']
        row['requirement_priority'] = int(complete and
            (mode == 'all_required_first' or row['requirement_bonus'] > 0))
        row['priority_reason'] = ('all_required_lexically_supported' if mode == 'all_required_first'
                                 else 'new_missing_requirement_supported') if row['requirement_priority'] else 'prior_order'
    rows.sort(key=lambda r: (-r['requirement_priority'], -r['score'], r['github_repository_id']))
    return rows[:limit]
