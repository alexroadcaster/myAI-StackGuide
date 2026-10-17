"""Offline CP-11 input validation for the CP-07 writer.

These functions read trusted package assets and return detached JSON values.
They never write state, query SQLite, retrieve, compose, or execute a plan. Native
ranking consistency is checked; an execution trace remains the evidence that a
supplied result was actually produced by SQL rather than invented coherently.
"""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import uuid

SCRIPTS = Path(__file__).resolve().parent
ASSETS = SCRIPTS.parent / 'assets'


def _sibling(name):
    spec = importlib.util.spec_from_file_location('stackguide_session_' + name, SCRIPTS / (name + '.py'))
    if spec is None or spec.loader is None:
        raise ValueError('trusted validator dependency unavailable')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


reader = _sibling('retrieval')
packs = _sibling('context_pack')
context = _sibling('context')
scanner = _sibling('scanner')

_ANNOTATIONS = {'$schema', '$id', 'title', 'description', 'x-invariants'}
_KEYWORDS = _ANNOTATIONS | {
    '$ref', 'type', 'const', 'enum', 'properties', 'required', 'additionalProperties',
    'items', 'minItems', 'maxItems', 'uniqueItems', 'contains', 'minContains', 'maxContains',
    'minLength', 'maxLength', 'pattern', 'format', 'minimum', 'maximum',
    'exclusiveMinimum', 'exclusiveMaximum', 'allOf', 'anyOf', 'oneOf', 'not',
    'if', 'then', 'else', 'x-max-utf8-bytes',
}


class _Mismatch(ValueError):
    """A value mismatch, distinct from an unsupported schema instruction."""


def _bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _same(left, right):
    return _bytes(left) == _bytes(right)


def _require(condition):
    if not condition:
        raise _Mismatch('invalid session recommendation input')


def _format(value, name):
    if name == 'uuid':
        try:
            return str(uuid.UUID(value)) == value
        except (ValueError, AttributeError):
            return False
    if name == 'date-time':
        if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:[Zz]|[+-][0-9]{2}:[0-9]{2})', value) is None:
            return False
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00').replace('z', '+00:00')).tzinfo is not None
        except ValueError:
            return False
    if name == 'uri-reference':
        # RFC3986 characters and well-formed percent escapes; never dereference.
        if re.search(r"[^A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]|%(?![0-9A-Fa-f]{2})", value):
            return False
        try:
            urlsplit(value)
            return True
        except ValueError:
            return False
    raise ValueError('unsupported schema format')


def _validate(value, schema, schemas, depth=0):
    _require(depth <= 100)
    if isinstance(schema, bool):
        _require(schema)
        return
    if not isinstance(schema, dict) or set(schema) - _KEYWORDS:
        raise ValueError('unsupported schema keyword')
    if '$ref' in schema:
        if schema['$ref'] not in schemas:
            raise ValueError('unresolved offline schema reference')
        _validate(value, schemas[schema['$ref']], schemas, depth + 1)
    if 'type' in schema:
        types = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        matches = dict(null=value is None, boolean=type(value) is bool, integer=type(value) is int,
                       number=type(value) in (int, float), string=isinstance(value, str),
                       array=isinstance(value, list), object=isinstance(value, dict))
        _require(any(matches.get(kind, False) for kind in types))
    if 'const' in schema:
        _require(_same(value, schema['const']))
    if 'enum' in schema:
        _require(any(_same(value, option) for option in schema['enum']))
    if 'x-max-utf8-bytes' in schema:
        _require(len(_bytes(value)) <= schema['x-max-utf8-bytes'])
    for key in ('allOf', 'anyOf', 'oneOf'):
        if key in schema:
            matches = 0
            for branch in schema[key]:
                try:
                    _validate(value, branch, schemas, depth + 1)
                    matches += 1
                except _Mismatch:
                    pass
            _require(matches == len(schema[key]) if key == 'allOf' else matches == 1 if key == 'oneOf' else matches > 0)
    if 'not' in schema:
        try:
            _validate(value, schema['not'], schemas, depth + 1)
        except _Mismatch:
            pass
        else:
            raise _Mismatch('forbidden schema branch')
    if 'if' in schema:
        try:
            _validate(value, schema['if'], schemas, depth + 1)
            branch = 'then'
        except _Mismatch:
            branch = 'else'
        if branch in schema:
            _validate(value, schema[branch], schemas, depth + 1)
    if isinstance(value, dict):
        _require(all(isinstance(key, str) for key in value))
        _require(set(schema.get('required', ())) <= set(value))
        properties = schema.get('properties', {})
        for key, child in value.items():
            if key in properties:
                _validate(child, properties[key], schemas, depth + 1)
            elif 'additionalProperties' in schema:
                _validate(child, schema['additionalProperties'], schemas, depth + 1)
    if isinstance(value, list):
        _require(schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', math.inf))
        if schema.get('uniqueItems'):
            _require(len({_bytes(item) for item in value}) == len(value))
        if 'items' in schema:
            for item in value:
                _validate(item, schema['items'], schemas, depth + 1)
        if 'contains' in schema:
            count = 0
            for item in value:
                try:
                    _validate(item, schema['contains'], schemas, depth + 1)
                    count += 1
                except _Mismatch:
                    pass
            _require(schema.get('minContains', 1) <= count <= schema.get('maxContains', math.inf))
    if isinstance(value, str):
        _require(schema.get('minLength', 0) <= len(value) <= schema.get('maxLength', math.inf))
        if 'pattern' in schema:
            _require(re.search(schema['pattern'], value) is not None)
        if 'format' in schema:
            _require(_format(value, schema['format']))
    if type(value) in (int, float):
        _require(math.isfinite(value))
        for name, compare in (('minimum', lambda a,b:a>=b), ('maximum', lambda a,b:a<=b),
                              ('exclusiveMinimum', lambda a,b:a>b), ('exclusiveMaximum', lambda a,b:a<b)):
            if name in schema:
                _require(compare(value, schema[name]))


def _contracts():
    bundle, _ = reader._load_json_bytes(ASSETS/'session-contracts.json', max_bytes=262144)
    _require(set(bundle) == {'bundle_version', 'roots', 'sources', 'schemas'} and bundle['bundle_version'] == '1.0.0')
    # Check unsupported instructions in every branch, including branches that the
    # current value would not select. No network or permissive keyword fallback.
    def inspect(schema):
        if isinstance(schema, bool):
            return
        if not isinstance(schema, dict) or set(schema) - _KEYWORDS:
            raise ValueError('unsupported schema keyword')
        if '$ref' in schema and schema['$ref'] not in bundle['schemas']:
            raise ValueError('unresolved offline schema reference')
        if 'format' in schema and schema['format'] not in {'uuid', 'date-time', 'uri-reference'}:
            raise ValueError('unsupported schema format')
        for child in schema.get('properties', {}).values():
            inspect(child)
        for key in ('items', 'additionalProperties', 'contains', 'not', 'if', 'then', 'else'):
            if key in schema:
                inspect(schema[key])
        for key in ('allOf', 'anyOf', 'oneOf'):
            for child in schema.get(key, []):
                inspect(child)
    for schema in bundle['schemas'].values():
        inspect(schema)
    return bundle


def _schema(value, name, bundle):
    reference = bundle['roots'][name]
    _validate(value, bundle['schemas'][reference], bundle['schemas'])


def _trusted(state):
    manifest, raw = reader._load_json_bytes(ASSETS/'catalog.search-manifest.json', max_bytes=65536)
    _require(hashlib.sha256(raw).hexdigest() == reader.TRUSTED_MANIFEST_SHA256)
    _require(_same(state.get('index_manifest'), manifest))
    policy, raw = reader._load_json_bytes(ASSETS/'retrieval-policy.json', max_bytes=65536)
    reader._validate_manifest_policy(manifest, policy)
    _require(hashlib.sha256(raw).hexdigest() == manifest['pins']['policy_sha256'])
    _require(reader._sha256_file(ASSETS/'catalog.search.sqlite') == manifest['pins']['index_sha256'])
    _require(state.get('schema_version') == '1.1.0')
    brief = state.get('brief')
    context.validate_project_context_brief(brief)
    _require(brief['run_id'] == state.get('run_id'))
    return manifest, policy, brief


def _native_result(query, result, manifest):
    _require(result['pins'] is None or _same(result['pins'], manifest['pins']))
    _require(result['query_id'] == query['query_id'] and result['brief_version'] == query['brief_version'])
    _require(result['query_sha256'] == reader.canonical_query_sha256(query))
    _require(result['retrieved_hits'] <= query['max_candidates'])
    _require(result['executed_variants'] <= len(query['variants']))
    if result['status'] not in ('ok', 'no_match'):
        reasons = {
            'invalid_query': {'invalid_query'},
            'index_incompatible': {'index_incompatible'},
            'retrieval_unavailable': {'fts5_unavailable', 'index_missing', 'index_corrupt'},
            'cancelled': {'cancelled'},
        }
        _require(len(result['reason_codes']) == 1 and result['reason_codes'][0] in reasons[result['status']])
        _require(result['executed_variants'] == 0 and result['retrieved_hits'] == 0 and result['truncated'] is False)
        return
    _require(_same(result['pins'], manifest['pins']))
    variants = [v['variant_id'] for v in query['variants'][:result['executed_variants']]]
    _require(bool(variants))
    ids, scores, ranks = [], [], {v: [] for v in variants}
    for expected, row in enumerate(result['candidates'], 1):
        _require(row['rank'] == expected)
        rid = row['github_repository_id']
        _require(rid not in ids)
        ids.append(rid)
        vr = row['variant_ranks']
        names = [v['variant_id'] for v in vr]
        _require(len(names) == len(set(names)) and all(name in variants for name in names))
        _require(names == [name for name in variants if name in names])
        score = sum(1.0 / (reader.RRF_K + v['rank']) for v in vr)
        _require(score == row['rrf_score'])
        _require(row['missing_facts'] == [])
        _require(row['matched_fields'] == [f for f in reader.FTS_COLUMNS if f in row['matched_fields']])
        for v in vr:
            ranks[v['variant_id']].append((v['rank'], v['bm25'], rid))
        scores.append((-score, rid))
    _require(scores == sorted(scores))
    _require(sum(len(v) for v in ranks.values()) == result['retrieved_hits'])
    remaining = query['max_candidates']
    for offset, variant in enumerate(variants):
        rows = sorted(ranks[variant])
        _require([r[0] for r in rows] == list(range(1, len(rows) + 1)))
        _require([(r[1], r[2]) for r in rows] == sorted((r[1], r[2]) for r in rows))
        allocation = math.ceil(remaining / (len(query['variants']) - offset))
        _require(len(rows) <= allocation)
        remaining -= len(rows)
    _require(result['executed_variants'] == len(query['variants']) or remaining == 0)
    _require(result['truncated'] == (result['retrieved_hits'] >= query['max_candidates']))
    expected_reasons = (['candidate_budget'] if result['truncated'] else []) if result['status'] == 'ok' else ['no_hits']
    _require(result['reason_codes'] == expected_reasons)


def _matching(state, payload, bundle):
    _require(isinstance(payload, dict) and set(payload) == {'request', 'retrieval', 'evidence_pack'})
    manifest, policy, brief = _trusted(state)
    request, result, pack = (payload[k] for k in ('request', 'retrieval', 'evidence_pack'))
    for value, name in ((request, 'recommendation/recommendation-request.schema.json'),
                        (result, 'retrieval/retrieval-result.schema.json'), (pack, 'retrieval/evidence-pack.schema.json')):
        _schema(value, name, bundle)
        _require(value['run_id'] == state['run_id'] and value['brief_version'] == brief['brief_version'])
    _require(request['brief_id'] == brief['brief_id'])
    query = request['query']
    _require(_same(query['constraints'], brief['constraints']))
    reader.validate_query(query, manifest=manifest, policy=policy)
    _native_result(query, result, manifest)
    ids = [r['github_repository_id'] for r in result['candidates']]
    cards = packs._stream_verified_snapshot_cards(ASSETS/'catalog.snapshot.json', manifest['pins'], expected_count=manifest['row_count'], max_bytes=packs.MAX_SNAPSHOT_BYTES, candidate_ids=ids)
    _require(set(cards) == set(ids))
    expected = packs._build_evidence_pack_from_trusted_cards(query, result, cards,
        pack_id=request['pack_id'], max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
    _require(_same(pack, expected))
    limits = policy['limits']
    allocation = dict(brief_bytes=limits['max_brief_bytes'], targeted_context_bytes=limits['max_targeted_context_bytes'], evidence_bytes=limits['max_evidence_bytes'], request_bytes=limits['max_request_bytes'], plugin_input_bytes=limits['max_plugin_input_bytes'])
    _require(request['input_allocation'] == allocation)
    _require(len(_bytes(brief)) + len(_bytes(request)) + len(_bytes(pack)) <= limits['max_plugin_input_bytes'])
    return payload


def _evidence(state, pack):
    project = {}
    for summary in ((state.get('scan') or {}).get('summary', {}), state['brief']['observations']):
        for record in summary.get('evidence', []):
            key = record['evidence_id']
            _require(key not in project or _same(project[key], record))
            project[key] = record
    public = {}
    for record in pack['cards']:
        rid = record['card']['identity']['github_repository_id']
        public[rid] = {e['evidence_id'] for e in record['card']['evidence']}
    answers = {a['answer_id'] for a in state.get('intake', {}).get('answers', []) if a.get('status') == 'answered' and a.get('sanitized_value') is not None}
    return project, public, answers


def _references(value, project, public, answers, owner=None):
    """Resolve card-local references through typed ownership, never prose.

    Ownerless records need one admissible identity, including project/public
    collisions. Nested comparison claims inherit their explicit repository.
    """
    def resolves(ref):
        owners = {rid for rid, refs in public.items() if ref in refs}
        if owner is not None:
            return owner in owners or (ref in project and not owners)
        return len(owners) + int(ref in project) == 1

    if isinstance(value, list):
        for item in value:
            _references(item, project, public, answers, owner)
    elif isinstance(value, dict):
        if 'github_repository_id' in value:
            owner = value['github_repository_id']
        _require(all(resolves(ref) for ref in value.get('evidence_refs', [])))
        if 'evidence_ref' in value:
            _require(resolves(value['evidence_ref']))
        _require(all(answer in answers for answer in value.get('answer_ids', [])))
        for child in value.values():
            _references(child, project, public, answers, owner)


def _plan(plan, state, memo, records, project, answers):
    _require(plan['run_id'] == state['run_id'] and plan['brief_version'] == memo['brief_version'])
    recommendations = {r['github_repository_id']: r for r in memo['recommendations']}
    for rid in plan['selected_github_repository_ids']:
        _require(rid in recommendations and recommendations[rid]['role'] not in ('avoid_for_now', 'compare_against'))
        eligibility = records[rid]['eligibility']
        if eligibility['status'] != 'primary_eligible':
            _require(memo['status'] == 'conditional_guidance' and bool(plan['unresolved_questions'] or plan['prerequisites']))
    steps = [s['step_id'] for s in plan['steps']]
    _require(len(steps) == len(set(steps)))
    details = plan['details']
    dependencies = details['step_dependencies']
    _require(len(dependencies) == len(steps) and {d['step_id'] for d in dependencies} == set(steps))
    policy = None
    for row in dependencies:
        index = steps.index(row['step_id'])
        _require(len(row['depends_on']) == len(set(row['depends_on'])) and set(row['depends_on']) <= set(steps[:index]))
        for path in row['safe_paths']:
            if policy is None:
                policy = scanner.load_policy()
            _require(scanner._path_disposition(path, policy)[0])
            _require(any(project[ref].get('relative_path') == path for ref in row['evidence_refs'] if ref in project))
    diagram = details['diagram']
    if diagram is not None:
        nodes = [n['component_id'] for n in diagram['nodes']]
        _require(len(nodes) == len(set(nodes)))
        for node in diagram['nodes']:
            if node['change'] in ('reuse', 'change'):
                _require(bool(set(node['evidence_refs']) & set(project)))
        for edge in diagram['edges']:
            _require(edge['from_component_id'] in nodes and edge['to_component_id'] in nodes)
    checks = details['prerequisite_checks']
    _require(len({r['check_id'] for r in checks}) == len(checks))
    for row in checks:
        if row['status'] in ('known', 'already_authorized'):
            _require(bool(row['evidence_refs'] or row['answer_ids']))
        else:
            _require(bool(row['next_check']))
        if row['status'] == 'already_authorized':
            _require(row['kind'] == 'authorization' and bool(set(row['answer_ids']) & answers))
        if row['kind'] != 'authorization':
            _require(row['status'] not in ('already_authorized', 'authorization_needed'))


def validate_matching(state, payload):
    """Validate exactly {request, retrieval, evidence_pack}; return a deep copy."""
    try:
        return copy.deepcopy(_matching(state, payload, _contracts()))
    except (KeyError, TypeError, AttributeError, OSError, UnicodeError, RecursionError, OverflowError) as error:
        raise ValueError('invalid matching input') from error


def validate_memo(state, payload):
    """Validate exactly {memo} against current saved matching inputs."""
    try:
        _require(isinstance(payload, dict) and set(payload) == {'memo'})
        bundle = _contracts()
        matching = {k: state.get(k) for k in ('request', 'retrieval', 'evidence_pack')}
        _matching(state, matching, bundle)
        memo = payload['memo']
        _schema(memo, 'recommendation/recommendation-memo.schema.json', bundle)
        request, result, pack = (matching[k] for k in ('request', 'retrieval', 'evidence_pack'))
        _require(memo['schema_version'] == '2.1.0')
        _require(memo['run_id'] == state['run_id'] and memo['brief_version'] == state['brief']['brief_version'])
        _require(memo['request_id'] == request['request_id'] and memo['pack_id'] == pack['pack_id'] and _same(memo['pins'], pack['pins']))
        expected_status = 'no_match' if pack['status'] == 'no_match' else 'retrieval_unavailable' if pack['status'] == 'unavailable' else None
        _require(memo['status'] == expected_status if expected_status else memo['status'] in ('recommendations', 'conditional_guidance'))
        project, public, answers = _evidence(state, pack)
        _references(memo, project, public, answers)
        records = {r['card']['identity']['github_repository_id']: r for r in pack['cards']}
        ids = []
        for row in memo['recommendations']:
            rid = row['github_repository_id']
            _require(rid in records and rid not in ids)
            ids.append(rid)
            _require(set(row['evidence_refs']) <= public[rid] and bool(row['evidence_refs']))
            eligibility = records[rid]['eligibility']['status']
            _require(eligibility != 'blocked')
            if eligibility == 'reference_only':
                _require(row['role'] in ('reference_only', 'compare_against', 'avoid_for_now'))
            if row['role'] == 'primary_candidate':
                _require(eligibility == 'primary_eligible')
        if memo['status'] == 'recommendations':
            _require(any(r['role'] == 'primary_candidate' for r in memo['recommendations']))
        categories = [r['category_id'] for r in memo['category_path']]
        # Classification keys are source-owned in these trusted public cards.
        category_ids = {a[key] for r in pack['cards'] for a in r['card']['classifications'] for key in ('category_id', 'parent_id') if a.get(key) is not None}
        _require(len(categories) == len(set(categories)) and set(categories) <= category_ids)
        comparison = memo['comparison_details']
        if comparison is not None:
            cells = set()
            for row in comparison['cells']:
                rid = row['github_repository_id']
                key = (row['criterion'], rid)
                _require(key not in cells)
                cells.add(key)
                _require((rid is None and comparison['include_no_change']) if row['baseline'] else rid in records)
        for row in memo['avoid_defer_details']:
            _require(row['github_repository_id'] in records and set(row['evidence_refs']) <= public[row['github_repository_id']])
        if memo['integration_plan'] is not None:
            _plan(memo['integration_plan'], state, memo, records, project, answers)
        return copy.deepcopy(payload)
    except (KeyError, TypeError, AttributeError, OSError, UnicodeError, RecursionError, OverflowError) as error:
        raise ValueError('invalid memo input') from error
