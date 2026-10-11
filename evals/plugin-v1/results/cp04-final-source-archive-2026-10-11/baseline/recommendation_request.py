"""Read-only Codex interpretation -> validated Brief -> active C9 pack boundary.

Host public observations are transient inputs, never catalog metadata or saved
state. This entry point performs no scan, state write, model or network call.
"""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys

import context
import context_pack
import request_guard
import retrieval

ASSETS = Path(__file__).resolve().parents[1]/'assets'


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def prepare_from_brief(brief, interpretation):
    context.validate_project_context_brief(brief)
    expected = {'brief_sha256', 'brief_version', 'language', 'route', 'terms', 'intent', 'excluded_repository_ids', 'excluded_dependencies', 'unresolved'}
    if not isinstance(interpretation, dict) or set(interpretation) != expected:
        raise ValueError('invalid interpretation shape')
    if interpretation['brief_sha256'] != digest(brief) or interpretation['brief_version'] != brief['brief_version']:
        raise ValueError('stale Brief interpretation')
    if interpretation['language'] not in ('ru', 'en'):
        raise ValueError('invalid language')
    unresolved = interpretation['unresolved']
    if unresolved:
        if interpretation['route'] is not None or interpretation['terms'] is not None or interpretation['intent'] is not None:
            raise ValueError('unresolved goal must not preselect retrieval')
        return request_guard.prepare(None, None, excluded_repository_ids=interpretation['excluded_repository_ids'],
            excluded_dependencies=interpretation['excluded_dependencies'], unresolved=unresolved)
    manifest = json.loads((ASSETS/'catalog.search-manifest.json').read_bytes())
    policy = json.loads((ASSETS/'retrieval-policy.json').read_bytes())
    pins = manifest['pins']
    query = dict(schema_version=manifest['schema_version'], query_id='request-'+digest(interpretation)[:24], brief_version=brief['brief_version'],
        source_mode=policy['source_mode'], retrieval_engine=policy['retrieval_engine'],
        policy_version=pins['retrieval_policy_version'], policy_sha256=pins['policy_sha256'],
        card_schema_version=pins['card_schema_version'], activity_schema_version=pins['activity_schema_version'],
        index_format_version=pins['index_format_version'], taxonomy_route_id=interpretation['route'],
        language=interpretation['language'], variants=[dict(variant_id='q1', terms=interpretation['terms'])],
        constraints=copy.deepcopy(brief['constraints']), max_candidates=policy['limits']['max_retrieved_hits'],
        max_cards=policy['limits']['max_detailed_cards'], max_evidence_bytes=policy['limits']['max_evidence_bytes'])
    # Reuse the actual C9 version/validation instead of accepting a model-built query.
    retrieval.validate_query(query, manifest=manifest, policy=policy)
    intent = interpretation['intent']
    if not isinstance(intent, dict) or set(intent) != {'required_groups', 'context_terms'}:
        raise ValueError('invalid intent')
    if not intent['required_groups'] or any(not isinstance(g, list) or not g for g in intent['required_groups']):
        raise ValueError('invalid required groups')
    if Counter([t for g in intent['required_groups'] for t in g]+intent['context_terms']) != Counter(interpretation['terms']):
        raise ValueError('intent must partition query terms')
    return request_guard.prepare(query, intent, excluded_repository_ids=interpretation['excluded_repository_ids'],
        excluded_dependencies=interpretation['excluded_dependencies'])


def run(brief, interpretation, public_observations=(), *, retrieve=None):
    request = prepare_from_brief(brief, interpretation)
    if request['status'] == 'needs_clarification':
        return dict(status='needs_clarification', request=request, questions=request['unresolved'],
                    retrieval_calls=0, evidence_pack=None)
    query = request['catalog_query']
    retrieve = retrieve or retrieval.retrieve
    result = retrieve(query, run_id=brief['run_id'], index_path=ASSETS/'catalog.search.sqlite',
                      manifest_path=ASSETS/'catalog.search-manifest.json', policy_path=ASSETS/'retrieval-policy.json')
    if result['status'] not in ('ok', 'no_match'):
        return dict(status=result['status'], request=request, retrieval_calls=1, evidence_pack=None)
    manifest = json.loads((ASSETS/'catalog.search-manifest.json').read_bytes())
    raw = (ASSETS/'catalog.snapshot.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != result['pins']['cards_sha256']:
        raise ValueError('snapshot integrity failure')
    cards = context_pack._cards_from_verified_snapshot(json.loads(raw), result['pins'], expected_count=manifest['row_count'])
    facts = {}
    for fact in public_observations:
        rid = fact['github_repository_id']
        if rid in facts or rid not in cards or cards[rid]['identity']['full_name'] != fact['full_name']:
            raise ValueError('observation identity mismatch')
        if not fact.get('observed_on') or not fact.get('source_urls') or any(not s.startswith('https://') for s in fact['source_urls']):
            raise ValueError('observation provenance missing')
        facts[rid] = fact
    ids = [r['github_repository_id'] for r in result['candidates']]
    selection = request_guard.select(request, ids, facts, limit=query['max_candidates'])
    filtered = dict(result, candidates=request_guard.filtered_candidates(result['candidates'], selection['selected_ids']))
    pack = context_pack.build_evidence_pack(query, filtered, {r: cards[r] for r in selection['selected_ids']},
        pack_id='request-pack-'+digest(interpretation)[:24], max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
    return dict(status='ready', request=request, selection=selection, retrieval_calls=1, evidence_pack=pack,
        public_observations=list(public_observations), observations_persisted=False,
        raw_ranked_ids=ids, selected_ids=selection['selected_ids'])


if __name__ == '__main__':
    try:
        raw = sys.stdin.buffer.read(204801)
        if len(raw) > 204800:
            raise ValueError('input budget exceeded')
        payload = json.loads(raw.decode('utf-8'))
        if set(payload) != {'brief', 'interpretation', 'public_observations'}:
            raise ValueError('invalid input shape')
        print(json.dumps(run(**payload), ensure_ascii=False, allow_nan=False))
    except (ValueError, KeyError, TypeError, context.ContextError):
        print(json.dumps(dict(status='invalid_input', evidence_pack=None)))
        sys.exit(1)
