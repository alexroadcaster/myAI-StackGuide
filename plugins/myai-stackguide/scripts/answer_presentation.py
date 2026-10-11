"""Transient presentation checks, separate from the canonical CP-07 state contract.

No state, retrieval, model or network I/O. Numeric consistency and source binding
are objective checks; they cannot prove estimate accuracy or translation meaning.
"""
from __future__ import annotations

import copy
from decimal import Decimal, DecimalException, ROUND_CEILING, ROUND_FLOOR, localcontext
import hashlib
import json
import math
import re

_TOKEN = re.compile(r'''[^\s<>(){}\[\]"'`]+''')
_NEWLINE = re.compile(r'(?<!\\)\\(?:r\\n|n)')


def _path_or_ambiguous(token: str) -> bool:
    if '\\' not in token:
        return False
    if re.match(r'^[A-Za-z]:\\', token) or '\\\\' in token or '/' in token:
        return True
    if token.startswith('\\') or re.fullmatch(r'[\w-]+(?:\.[\w-]+)*(?:\\[\w.-]+)+[.,;]?', token):
        return True
    remainder = _NEWLINE.sub('', token)
    if '\\' in remainder:
        return True
    # Only recognizable paragraph/list boundaries are prose. A bare a\nb is
    # indistinguishable from a relative path and is deliberately preserved.
    return not ('\\n\\n' in token or re.search(r'[.!?:;\])](?:\\r)?\\n', token)
                or token.startswith(('\\n', '\\r\\n')) or token.endswith(('\\n', '\\r\\n')))


def normalize_answer_text(text: str) -> str:
    """Decode recognizable prose newline escapes without a general escape codec.

    Backtick/tilde code, quoted strings, URL/path tokens and doubled backslashes
    remain byte-for-byte intact. Ambiguous bare relative-path tokens remain as
    supplied; callers should delimit literals and format prose as paragraphs.
    Unclosed code/quoted literals conservatively protect the remaining text.
    """
    if not isinstance(text, str):
        raise ValueError('answer text must be a string')
    parts = []
    position = 0
    while position < len(text):
        character = text[position]
        if character == '`' or text.startswith('~~~', position):
            end = position + 1
            while end < len(text) and text[end] == character:
                end += 1
            delimiter = text[position:end]
            closing = text.find(delimiter, end)
            end = len(text) if closing < 0 else closing + len(delimiter)
            parts.append(text[position:end])
            position = end
            continue
        if character == '"' or (character == "'" and (position == 0 or not text[position - 1].isalnum())):
            end = position + 1
            while end < len(text):
                if text[end] == '\\':
                    end += 2
                elif text[end] == character:
                    end += 1
                    break
                else:
                    end += 1
            parts.append(text[position:end])
            position = end
            continue
        token_match = _TOKEN.match(text, position)
        if token_match:
            token = token_match.group()
            parts.append(token if _path_or_ambiguous(token) else _NEWLINE.sub('\n', token))
            position = token_match.end()
            continue
        parts.append(character)
        position += 1
    return ''.join(parts)


def _shape(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= set(value) or set(value) - set(required) - set(optional):
        raise ValueError('invalid planning shape')


def _text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('planning text must be nonempty')


def _number(value, *, positive=False):
    try:
        valid = type(value) in (int, float) and math.isfinite(value) and value >= 0 and (not positive or value > 0)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError('invalid planning number')
    return Decimal(str(value))


def _range(value):
    _shape(value, ('min', 'max'))
    lower, upper = _number(value['min']), _number(value['max'])
    if upper < lower:
        raise ValueError('reversed planning range')
    return lower, upper


def _finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('planning arithmetic overflow')
    return result


def _elapsed_bound(hours, capacity, rounding):
    try:
        value = hours / capacity
        _finite_float(value)
        with localcontext() as arithmetic:
            arithmetic.prec = max(28, value.adjusted() + 8)
            return _finite_float(value.quantize(Decimal('0.000001'), rounding=rounding))
    except DecimalException as error:
        raise ValueError('planning arithmetic overflow') from error


def validate_planning_facts(facts: dict) -> dict:
    """Validate one hypothetical scenario and derive totals from declared scope.

    Required input: scenario_id, scope_status, assumptions, first_validation,
    phases. All ranges are engineer-hours. Scoped phases name only work *after*
    first_validation, which is counted once. validation_only requires no phases
    and yields null full-adoption total/elapsed time. No waiting-time estimate is
    invented. The returned copy additionally has total_engineer_hours and
    elapsed_working_days; supplied derived fields must agree exactly.
    """
    derived_keys = ('total_engineer_hours', 'elapsed_working_days')
    _shape(facts, ('scenario_id', 'scope_status', 'assumptions', 'first_validation', 'phases'), derived_keys)
    _text(facts['scenario_id'])
    if facts['scope_status'] not in ('validation_only', 'scoped_total'):
        raise ValueError('invalid planning scope')
    assumptions = facts['assumptions']
    _shape(assumptions, ('prerequisites', 'team_experience', 'confidence', 'hours_per_engineer_day', 'allocated_engineers'))
    if not isinstance(assumptions['prerequisites'], list):
        raise ValueError('invalid prerequisites')
    for prerequisite in assumptions['prerequisites']:
        _text(prerequisite)
    _text(assumptions['team_experience'])
    if assumptions['confidence'] not in ('low', 'medium', 'high'):
        raise ValueError('invalid planning confidence')
    hours = _number(assumptions['hours_per_engineer_day'], positive=True)
    allocation = _number(assumptions['allocated_engineers'], positive=True)
    if hours > 24:
        raise ValueError('hours per engineer-day exceeds a day')
    lower, upper = _range(facts['first_validation'])
    phases = facts['phases']
    if not isinstance(phases, list):
        raise ValueError('invalid phases')
    names = set()
    for phase in phases:
        _shape(phase, ('name', 'min', 'max'))
        _text(phase['name'])
        name = re.sub(r'[\s-]+', '_', phase['name'].strip().casefold())
        if name in names or name == 'first_validation':
            raise ValueError('duplicate planning phase or validation')
        names.add(name)
        minimum, maximum = _range({'min': phase['min'], 'max': phase['max']})
        lower += minimum
        upper += maximum
    total = elapsed = None
    if facts['scope_status'] == 'validation_only':
        if phases:
            raise ValueError('unknown adoption scope cannot include full phases')
    else:
        if not phases:
            raise ValueError('scoped total requires post-validation phases')
        total = {'min': _finite_float(lower), 'max': _finite_float(upper)}
        capacity = hours * allocation
        # Outward rounding retains the bounds instead of shortening an estimate.
        elapsed = {'min': _elapsed_bound(lower, capacity, ROUND_FLOOR),
                   'max': _elapsed_bound(upper, capacity, ROUND_CEILING)}
    result = copy.deepcopy(facts)
    for key, expected in zip(derived_keys, (total, elapsed)):
        if key in facts and facts[key] != expected:
            raise ValueError('mismatched derived planning range')
        result[key] = expected
    return result


def planning_binding(facts: dict) -> dict:
    """Return the same source-bound numerical projection for RU and EN."""
    normalized = validate_planning_facts(facts)
    canonical = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    binding = {key: copy.deepcopy(normalized[key]) for key in
               ('scenario_id', 'assumptions', 'first_validation', 'total_engineer_hours', 'elapsed_working_days')}
    binding['planning_sha256'] = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    return binding


def validate_locale_planning_binding(facts: dict, binding: dict) -> None:
    """Reject stale or altered locale bindings; prose equivalence is separate."""
    expected = planning_binding(facts)
    _shape(binding, expected)
    try:
        same = json.dumps(binding, sort_keys=True, ensure_ascii=False, allow_nan=False) == json.dumps(expected, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError('invalid locale planning binding') from error
    if not same:
        raise ValueError('stale or mismatched locale planning binding')


def project_answer_locale(text: str, locale: str) -> str:
    """Select an explicitly labelled bilingual section; never infer or translate.

    Captured composition can append an English block despite a locale request.
    Only whole-line labels outside fenced code form boundaries. Unlabelled text
    is preserved; ambiguous or empty sections fail rather than hide evidence.
    The caller retains the raw capture and binds this display-only projection.
    """
    if not isinstance(text, str) or locale not in ('ru', 'en'):
        raise ValueError('invalid answer locale')
    lines = text.splitlines(keepends=True)
    boundaries = []
    fence = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        opening = re.match(r'^(`{3,}|~{3,})', stripped)
        if opening:
            marker = opening.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None and stripped in ('**English**', '**English translation**', '**English — translation**'):
            boundaries.append(index)
    if not boundaries:
        return text
    if len(boundaries) != 1:
        raise ValueError('ambiguous translation sections')
    index = boundaries[0]
    russian = ''.join(lines[:index]).strip()
    english = ''.join(lines[index + 1:]).strip()
    if russian.startswith('**Русский**'):
        russian = russian[len('**Русский**'):].lstrip()
    if russian.endswith('---'):
        russian = russian[:-3].rstrip()
    if not russian or not english:
        raise ValueError('empty translation section')
    return russian if locale == 'ru' else english
