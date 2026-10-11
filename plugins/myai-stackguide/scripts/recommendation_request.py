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
import re
import sys

import context
import context_pack
import request_guard
import retrieval

ASSETS = Path(__file__).resolve().parents[1]/'assets'


class RetrievalPreflightError(ValueError):
    """A typed aggregate failure must never become a widened lookup."""

    def __init__(self, result, *, aggregate_calls=1):
        self.result = result
        self.aggregate_calls = aggregate_calls
        super().__init__(result['status'])


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _required_phrase_atoms(required_terms, aliases):
    """Lexical atoms retain exact alias semantics and slash identifiers.

    Search widening supplies no new requirement, stem, translation or fit fact.
    Each atom remains bound to the original required term that supplied it.
    """
    atoms = []
    for term in required_terms:
        compiled = retrieval._compiled_terms([term], aliases)[0]
        if '/' in compiled:
            continue
        tokens = re.findall(r'[^\W_]+', compiled, flags=re.UNICODE)
        if len(tokens) > 1:
            atoms.extend((token, term) for token in tokens)
    return atoms


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
    try:
        manifest, manifest_bytes = retrieval._load_json_bytes(ASSETS/'catalog.search-manifest.json',max_bytes=65536)
        policy, policy_bytes = retrieval._load_json_bytes(ASSETS/'retrieval-policy.json',max_bytes=65536)
    except (OSError, ValueError, UnicodeDecodeError):
        raise RetrievalPreflightError(dict(status='retrieval_unavailable',match_count=None),aggregate_calls=0)
    if hashlib.sha256(manifest_bytes).hexdigest() != retrieval.TRUSTED_MANIFEST_SHA256:
        raise RetrievalPreflightError(dict(status='index_incompatible',match_count=None),aggregate_calls=0)
    try:
        retrieval._validate_manifest_policy(manifest,policy)
    except (ValueError, TypeError):
        raise RetrievalPreflightError(dict(status='index_incompatible',match_count=None),aggregate_calls=0)
    if hashlib.sha256(policy_bytes).hexdigest() != manifest['pins']['policy_sha256']:
        raise RetrievalPreflightError(dict(status='index_incompatible',match_count=None),aggregate_calls=0)
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
    if not isinstance(intent['required_groups'], list) or not intent['required_groups'] or any(not isinstance(g, list) or not g for g in intent['required_groups']):
        raise ValueError('invalid required groups')
    required_terms = [t for group in intent['required_groups'] for t in group]
    if not isinstance(intent['context_terms'], list) or any(not isinstance(t, str) for t in required_terms + intent['context_terms']):
        raise ValueError('invalid intent terms')
    if Counter(required_terms+intent['context_terms']) != Counter(interpretation['terms']):
        raise ValueError('intent must partition query terms')
    # Validate exclusions before any database operation as well as the intent.
    request = request_guard.prepare(query, intent, excluded_repository_ids=interpretation['excluded_repository_ids'],
        excluded_dependencies=interpretation['excluded_dependencies'])
    original_query_sha256 = retrieval.canonical_query_sha256(query)
    required_atoms = _required_phrase_atoms(required_terms, policy['aliases'])
    # Count only after the complete interpretation has been validated. A
    # source-backed route vocabulary can fill a sparse pool, but is not an
    # inferred capability, translation, prefix expansion or fit assertion.
    count_options = dict(include_route_leaf_ids=True) if required_atoms and interpretation['route'] is not None else {}
    preflight = retrieval.count_matches(query, index_path=ASSETS/'catalog.search.sqlite',
        manifest_path=ASSETS/'catalog.search-manifest.json', policy_path=ASSETS/'retrieval-policy.json', **count_options)
    if preflight['status'] != 'ok':
        raise RetrievalPreflightError(preflight)
    original_terms = copy.deepcopy(interpretation['terms'])
    terms = copy.deepcopy(original_terms)
    keys = {retrieval._normalize(t) for t in terms}
    added = []
    origins = []
    def append(token, source_kind, source):
        normalized = retrieval._normalize(token)
        if normalized not in keys and len(terms) < policy['limits']['max_terms_per_variant']:
            terms.append(token)
            keys.add(normalized)
            origins.append(dict(term=token, source_kind=source_kind, source=source))
            return True
        return False
    if interpretation['route'] is not None and preflight['match_count'] < query['max_cards']:
        if required_atoms:
            for token, source_term in required_atoms:
                append(token, 'required_term_atom', source_term)
            wanted = {retrieval._normalize(t) for t in required_terms}
            wanted.update(token for token, source_term in required_atoms)
            for member in preflight['route_leaf_ids']:
                tokens = member.split('_')
                if wanted.intersection(tokens):
                    for token in tokens:
                        append(token, 'pinned_taxonomy_route_member', member)
        for token in interpretation['route'].split('_'):
            if append(token, 'selected_pinned_taxonomy_route_id', interpretation['route']):
                added.append(token)
    query['variants'] = [dict(variant_id='q1', terms=terms)]
    retrieval.validate_query(query, manifest=manifest, policy=policy)
    request['aggregate_calls'] = 1
    request['query_derivation'] = dict(original_terms=original_terms,
        original_match_count=preflight['match_count'], added_route_terms=added,
        source='selected_pinned_taxonomy_route_id' if added else None,
        added_term_origins=origins,
        original_query_sha256=original_query_sha256,
        final_query_sha256=retrieval.canonical_query_sha256(query),pins=copy.deepcopy(pins))
    return request


def run(brief, interpretation, public_observations=(), *, retrieve=None):
    try:
        request = prepare_from_brief(brief, interpretation)
    except RetrievalPreflightError as error:
        return dict(status=error.result['status'], request=None, preflight=error.result,
                    aggregate_calls=error.aggregate_calls,retrieval_calls=0,evidence_pack=None)
    if request['status'] == 'needs_clarification':
        return dict(status='needs_clarification', request=request, questions=request['unresolved'],
                    aggregate_calls=0,retrieval_calls=0,evidence_pack=None)
    query = request['catalog_query']
    retrieve = retrieve or retrieval.retrieve
    result = retrieve(query, run_id=brief['run_id'], index_path=ASSETS/'catalog.search.sqlite',
                      manifest_path=ASSETS/'catalog.search-manifest.json', policy_path=ASSETS/'retrieval-policy.json')
    if result['status'] not in ('ok', 'no_match'):
        return dict(status=result['status'], request=request,aggregate_calls=1,retrieval_calls=1,evidence_pack=None)
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
    return dict(status='ready', request=request, selection=selection,aggregate_calls=1,retrieval_calls=1,evidence_pack=pack,
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
