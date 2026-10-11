"""Transient source-bound host preference over an unchanged native C9 pool.

No model, network, state writer or transport files. Only a complete numeric
permutation returns from the host; native facts remain in retained memory.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import time

# -I excludes the script directory. Insert only this installed sibling directory,
# never the working directory or a caller-supplied project path.
_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
import recommendation_request as native

CONTRACT_SCHEMA_SHA256 = '83373eb4ec2b0f8270d4d7e6750bc1419591151338c023f018670214ec278f92'
CONTRACT_DOCUMENT_SHA256 = '21106a3d580672f1b86caaad6edec82d9e53f0e11e6b4689439ce909961d3bc6'
METHOD = 'host_codex_full_pool_v1'
FIELD_POINTERS = (
    '/descriptions/upstream', '/descriptions/catalog', '/repository/topics',
    '/advisory/use_cases', '/advisory/integration_surface', '/advisory/best_for',
)
_FAILURES = {
    'needs_selection', 'needs_clarification', 'invalid_input', 'stale_binding',
    'index_incompatible', 'retrieval_unavailable', 'no_match', 'budget_exceeded',
    'invalid_decision',
}
_REASONS = (*native.context_pack.matcher.REASON_ORDER,
            'explicit_product_exclusion', 'documented_dependency_conflict')
_SESSION_TOKEN = object()


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _failure(status, bindings=None):
    if status not in _FAILURES:
        status = 'invalid_input'
    return dict(schema_version='1.0.0', artifact_type='candidate_decision_failure',
                status=status, bindings=copy.deepcopy(bindings), evidence_pack=None)


def _header(kind, bindings):
    return dict(schema_version='1.0.0', artifact_type=kind,
                bindings=copy.deepcopy(bindings), method=METHOD)


def _bundle(query=None):
    """Recheck physical paired files without SQL or caller-provided anchors."""
    reader = native.retrieval
    manifest, raw = reader._load_json_bytes(native.ASSETS / 'catalog.search-manifest.json', max_bytes=65536)
    if hashlib.sha256(raw).hexdigest() != reader.TRUSTED_MANIFEST_SHA256:
        raise ValueError('manifest trust anchor mismatch')
    policy, raw = reader._load_json_bytes(native.ASSETS / 'retrieval-policy.json', max_bytes=65536)
    reader._validate_manifest_policy(manifest, policy)
    if hashlib.sha256(raw).hexdigest() != manifest['pins']['policy_sha256']:
        raise ValueError('policy trust anchor mismatch')
    for filename, pin in (('catalog.search.sqlite', 'index_sha256'), ('catalog.snapshot.json', 'cards_sha256')):
        hasher = hashlib.sha256()
        with (native.ASSETS / filename).open('rb') as stream:
            while chunk := stream.read(1024 * 1024):
                hasher.update(chunk)
        if hasher.hexdigest() != manifest['pins'][pin]:
            raise ValueError('paired source bytes changed')
    if query is not None:
        reader.validate_query(query, manifest=manifest, policy=policy)
    return manifest, policy


def _source_cards(manifest, ids):
    return native.context_pack._stream_verified_snapshot_cards(
        native.ASSETS / 'catalog.snapshot.json', manifest['pins'],
        expected_count=manifest['row_count'],
        max_bytes=native.context_pack.MAX_SNAPSHOT_BYTES, candidate_ids=ids)


def _validate_result(query, result, cards):
    native.context_pack._validate_inputs(query, result, cards, 'decision-pack',
                                        query['max_cards'], query['max_evidence_bytes'])
    ids = native.context_pack._retrieval_candidate_ids(result['candidates'])
    if result['status'] != 'ok' or not ids or len(ids) != len(set(ids)) or len(ids) > min(150, query['max_candidates']):
        raise ValueError('invalid successful pool')
    for row in result['candidates']:
        if type(row['rank']) is not int:
            raise ValueError('invalid native rank')
        score = row['rrf_score']
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 < score <= 1:
            raise ValueError('invalid native score')
        fields = row['matched_fields']
        if not isinstance(fields, list) or not fields or len(fields) != len(set(fields)) or any(f not in native.retrieval.FTS_COLUMNS for f in fields):
            raise ValueError('invalid native matched fields')
    return ids


def _guarded(data):
    """Canonical eligibility then product/dependency guard, without upgrades."""
    ids, cards, query = data['ids'], data['cards'], data['request']['catalog_query']
    facts = {}
    for fact in data['observations']:
        rid = fact['github_repository_id']
        if type(rid) is not int or rid in facts or data['observation_names'].get(rid) != fact['full_name']:
            raise ValueError('observation identity mismatch')
        if not fact.get('observed_on') or not fact.get('source_urls') or any(not isinstance(s, str) or not s.startswith('https://') for s in fact['source_urls']):
            raise ValueError('observation provenance missing')
        facts[rid] = fact
    selected = native.request_guard.select(data['request'], ids, facts, limit=query['max_candidates'])
    excluded = {r['github_repository_id']: r['reason'] for r in selected['excluded']}
    unknown = set(selected['verification_required'])
    output = {}
    for rid in ids:
        eligibility = native.context_pack.matcher.match_candidate(cards[rid], query)
        status, reasons = eligibility['status'], list(eligibility['reason_codes'])
        if rid in excluded:
            status = 'blocked'
            reasons.append(excluded[rid])
        elif rid in unknown and status == 'primary_eligible':
            status = 'reference_only'
            reasons.append('insufficient_evidence')
        output[rid] = dict(eligibility=eligibility, status=status,
                          reasons=[r for r in _REASONS if r in reasons][:8])
    return output


def _projection(card, pointer):
    value = card
    for component in pointer[1:].split('/'):
        value = value[component]
    if isinstance(value, list):
        if any(not isinstance(item, str) for item in value):
            raise ValueError('unsupported projection field')
        value = '\n'.join(value)
    if value is None or value == '':
        return dict(source_field=pointer, text=None, coverage='unknown')
    if not isinstance(value, str):
        raise ValueError('unsupported projection field')
    return dict(source_field=pointer, text=value[:1024], coverage='truncated' if len(value) > 1024 else 'complete')


def _preview(data, guards):
    result = _header('candidate_preview_request', data['bindings'])
    result.update(decision_context=dict(goal=data['brief']['goal'], intent=copy.deepcopy(data['interpretation']['intent'])),
                  candidates=[], reservation=dict(receipt_bytes=1, pack_bytes=1))
    for row in data['result']['candidates']:
        rid = row['github_repository_id']
        card, guard = data['cards'][rid], guards[rid]
        result['candidates'].append(dict(
            github_repository_id=rid, full_name=card['identity']['full_name'],
            source_card_sha256=digest(card), retrieval_rank=row['rank'], rrf_score=row['rrf_score'],
            taxonomy_category_ids=list(dict.fromkeys(c['category_id'] for c in card['classifications'])),
            eligibility_status=guard['eligibility']['status'],
            eligibility_reason_codes=copy.deepcopy(guard['eligibility']['reason_codes']),
            guard_status=guard['status'], guard_reason_codes=guard['reasons'],
            fields=[_projection(card, pointer) for pointer in FIELD_POINTERS]))
    return result


def _receipt(data, preview_hash, order):
    receipt = _header('candidate_decision_receipt', data['bindings'])
    receipt.update(preview_request_sha256=preview_hash, decision_order=list(order))
    return receipt


def _pack_header(data, preview_hash, receipt_hash):
    pack = _header('candidate_decision_pack', data['bindings'])
    pack.update(pack_id='decision-pack-' + data['bindings']['interpretation_sha256'][:24],
                preview_request_sha256=preview_hash, decision_receipt_sha256=receipt_hash,
                status='no_eligible', cards=[], exclusions=[], truncated=False)
    return pack


def _record(data, rid, rank, guards):
    row = data['rows'][rid]
    return dict(card=copy.deepcopy(data['cards'][rid]), retrieval_rank=row['rank'],
                decision_rank=rank, rrf_score=row['rrf_score'],
                eligibility=copy.deepcopy(guards[rid]['eligibility']),
                matched_fields=copy.deepcopy(row['matched_fields']))


def _pack(data, preview_hash, receipt_hash, records, guards, omissions):
    pack = _pack_header(data, preview_hash, receipt_hash)
    packed = {r['card']['identity']['github_repository_id'] for r in records}
    selectable = [rid for rid in data['ids'] if guards[rid]['status'] != 'blocked']
    pack['cards'] = records
    pack['status'] = ('limited' if len(records) < len(selectable) else 'ready') if selectable else 'no_eligible'
    pack['truncated'] = pack['status'] == 'limited'
    for rid in data['ids']:
        if rid not in packed:
            default_reason = 'candidate_budget' if len(records) >= min(12, data['request']['catalog_query']['max_cards']) else 'context_budget'
            reasons = guards[rid]['reasons'] if guards[rid]['status'] == 'blocked' else [omissions.get(rid, default_reason)]
            pack['exclusions'].append(dict(github_repository_id=rid, reason_codes=reasons or ['unavailable']))
    return pack


def _ledger_size(data, preview, receipt=None, pack=None):
    return len(canonical_bytes(dict(preview_request=preview, decision_receipt=receipt,
                                    decision_pack=pack))) + data['wrapper_bytes']


def _within(data, size):
    return size <= data['evidence_cap'] and size + data['input_bytes'] <= data['input_cap']


def _ordered_selectable(order, guards):
    return [rid for status in ('primary_eligible', 'reference_only')
            for rid in order if guards[rid]['status'] == status]


def _trimmed(preview, removals):
    """Water-filling equals longest-first codepoint removal with stable ties."""
    output = copy.deepcopy(preview)
    fields = [field for candidate in output['candidates'] for field in candidate['fields']]
    lengths = [len(field['text']) if field['text'] is not None else 0 for field in fields]
    low, high = 0, max(lengths, default=0)
    while low < high:
        level = (low + high) // 2
        if sum(max(0, length - level) for length in lengths) <= removals:
            high = level
        else:
            low = level + 1
    level = low
    extra = removals - sum(max(0, length - level) for length in lengths)
    for field, length in zip(fields, lengths):
        keep = min(length, level)
        if extra and keep == level and keep > 0:
            keep -= 1
            extra -= 1
        if keep < length:
            field['text'] = field['text'][:keep]
            field['coverage'] = 'truncated'
    return output


def _reserve_and_trim(data, preview, guards):
    # Unknown final digests have fixed width; placeholders are size-only.
    placeholder = '0' * 64
    receipt = _receipt(data, placeholder, data['ids'])
    eligible = [rid for rid in data['ids'] if guards[rid]['status'] != 'blocked']
    alternatives = [_pack(data, placeholder, placeholder,
                         [_record(data, rid, len(data['ids']), guards)], guards, {}) for rid in eligible]
    minimal = min(alternatives, key=lambda pack: len(canonical_bytes(pack))) if alternatives else _pack(data, placeholder, placeholder, [], guards, {})
    preview['reservation'] = dict(receipt_bytes=len(canonical_bytes(receipt)) - 4,
                                  pack_bytes=len(canonical_bytes(minimal)) - 4)
    def fits(candidate):
        return _within(data, _ledger_size(data, candidate, receipt, minimal))
    count = sum(len(f['text']) for c in preview['candidates'] for f in c['fields'] if f['text'] is not None)
    if not fits(_trimmed(preview, count)):
        return None
    low, high = 0, count
    while low < high:
        middle = (low + high) // 2
        if fits(_trimmed(preview, middle)):
            high = middle
        else:
            low = middle + 1
    return _trimmed(preview, low)


class DecisionSession:
    """Retained trusted inputs; public properties provide readonly deep copies."""
    __slots__ = ('_data', '_seal', '_used', '_timings', '_live_inputs', '_live_seal', '_bindings')

    def __init__(self, data, timings, *, _token=None, live_inputs=None, live_seal=None):
        if _token is not _SESSION_TOKEN:
            raise ValueError('use prepare to establish a trusted session')
        self._data = copy.deepcopy(data)
        self._seal = digest(self._data)
        self._used = False
        self._timings = dict(timings)
        self._bindings = copy.deepcopy(data['bindings'])
        self._live_inputs = live_inputs
        self._live_seal = live_seal

    @property
    def preview_request(self):
        return copy.deepcopy(self._data['preview'])

    @property
    def native_result(self):
        return copy.deepcopy(self._data['result'])

    @property
    def request(self):
        return copy.deepcopy(self._data['request'])

    @property
    def catalog_query(self):
        return copy.deepcopy(self._data['request']['catalog_query'])

    @property
    def control(self):
        """Local native control, assembled from retained trusted cards, no SQL.

        This diagnostic is never a host payload or a fallback decision pack.
        Its existing native contract deliberately compacts surviving ranks.
        """
        data = self._data
        facts = {f['github_repository_id']: f for f in data['observations']}
        query = data['request']['catalog_query']
        selection = native.request_guard.select(data['request'], data['ids'], facts, limit=query['max_candidates'])
        filtered = dict(data['result'], candidates=native.request_guard.filtered_candidates(
            data['result']['candidates'], selection['selected_ids']))
        pack = native.context_pack._build_evidence_pack_from_trusted_cards(
            query, filtered, {rid: data['cards'][rid] for rid in selection['selected_ids']},
            pack_id='request-pack-' + digest(data['interpretation'])[:24],
            max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
        return copy.deepcopy(dict(status='ready', request=data['request'], selection=selection,
            aggregate_calls=1, retrieval_calls=1, evidence_pack=pack,
            public_observations=data['observations'], observations_persisted=False,
            raw_ranked_ids=data['ids'], selected_ids=selection['selected_ids']))

    @property
    def timings(self):
        return dict(self._timings)

    @property
    def byte_accounting(self):
        return dict(evidence_cap=self._data['evidence_cap'], input_cap=self._data['input_cap'],
                    input_bytes=self._data['input_bytes'], wrapper_bytes=self._data['wrapper_bytes'])


def prepare(brief, interpretation, public_observations=(), *, targeted_context=None, wrapper_bytes=0):
    """One native COUNT/MATCH; reserve full receipt and least-byte real pack.

    wrapper_bytes reserves caller-controlled prompt/tool instructions in this
    same ledger. The actual host producer must recompute their UTF-8 size.
    Context and diagnostics remain local; host receives only preview_request.
    """
    started = time.perf_counter()
    try:
        if type(wrapper_bytes) is not int or not 0 <= wrapper_bytes <= 163840:
            return _failure('invalid_input')
        if not isinstance(public_observations, (list, tuple)):
            return _failure('invalid_input')
        live_inputs = dict(brief=brief, interpretation=interpretation, public_observations=public_observations,
                           targeted_context=targeted_context, wrapper_bytes=wrapper_bytes)
        live_seal = digest(live_inputs)
        brief, interpretation, observations = copy.deepcopy(brief), copy.deepcopy(interpretation), copy.deepcopy(list(public_observations))
        limits = json.loads((native.ASSETS / 'retrieval-policy.json').read_bytes())['limits']
        payload = dict(brief=brief, interpretation=interpretation, public_observations=observations,
                       targeted_context=targeted_context, wrapper_bytes=wrapper_bytes)
        request_bytes = len(canonical_bytes(dict(interpretation=interpretation, public_observations=observations, wrapper_bytes=wrapper_bytes)))
        if len(canonical_bytes(brief)) > limits['max_brief_bytes'] or len(canonical_bytes(targeted_context)) > limits['max_targeted_context_bytes'] or request_bytes > limits['max_request_bytes'] or len(canonical_bytes(payload)) > limits['max_plugin_input_bytes']:
            return _failure('budget_exceeded')
        count_start = time.perf_counter()
        request = native.prepare_from_brief(brief, interpretation)
        count_ms = (time.perf_counter() - count_start) * 1000
        if request['status'] == 'needs_clarification':
            return _failure('needs_clarification')
        query = request['catalog_query']
        retrieval_start = time.perf_counter()
        result = native.retrieval.retrieve(query, run_id=brief['run_id'],
            index_path=native.ASSETS / 'catalog.search.sqlite',
            manifest_path=native.ASSETS / 'catalog.search-manifest.json',
            policy_path=native.ASSETS / 'retrieval-policy.json')
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000
        if result['status'] != 'ok':
            return _failure(result['status'])
        try:
            manifest, policy = _bundle(query)
        except ValueError:
            return _failure('index_incompatible')
        if manifest['pins'] != result['pins']:
            return _failure('index_incompatible')
        ids = native.context_pack._retrieval_candidate_ids(result['candidates'])
        observed_ids = []
        for fact in observations:
            rid = fact['github_repository_id']
            if type(rid) is not int or rid <= 0 or rid in observed_ids:
                return _failure('invalid_input')
            observed_ids.append(rid)
        verified = _source_cards(manifest, list(dict.fromkeys(ids + observed_ids)))
        observation_names = {rid: verified[rid]['identity']['full_name'] for rid in observed_ids}
        cards = {rid: verified[rid] for rid in ids}
        _validate_result(query, result, cards)
        bindings = dict(contract_schema_sha256=CONTRACT_SCHEMA_SHA256,
            contract_document_sha256=CONTRACT_DOCUMENT_SHA256,
            run_id=brief['run_id'], brief_id=brief['brief_id'], brief_version=brief['brief_version'],
            brief_sha256=digest(brief), interpretation_sha256=digest(interpretation),
            guard_context_sha256=digest(dict(exclusions=request['exclusions'], public_observations=observations)),
            query_id=query['query_id'], query_sha256=digest(query), native_result_sha256=digest(result),
            candidate_pool_sha256=digest(ids), pins=copy.deepcopy(result['pins']))
        data = dict(brief=brief, interpretation=interpretation, observations=observations,
                    targeted_context=copy.deepcopy(targeted_context), wrapper_bytes=wrapper_bytes,
                    input_bytes=len(canonical_bytes(payload)), input_cap=policy['limits']['max_plugin_input_bytes'],
                    evidence_cap=min(163840, query['max_evidence_bytes'], policy['limits']['max_evidence_bytes']),
                    request=request, result=result, ids=ids, cards=cards, observation_names=observation_names,
                    rows={r['github_repository_id']: r for r in result['candidates']}, bindings=bindings)
        guards = _guarded(data)
        preview = _reserve_and_trim(data, _preview(data, guards), guards)
        if preview is None:
            return _failure('budget_exceeded', bindings)
        data['preview'] = preview
        if digest(live_inputs) != live_seal:
            return _failure('stale_binding', bindings)
        session = DecisionSession(data, dict(prepare_count_ms=count_ms, retrieval_ms=retrieval_ms,
            local_preview_ms=(time.perf_counter() - started) * 1000 - count_ms - retrieval_ms),
            _token=_SESSION_TOKEN, live_inputs=live_inputs, live_seal=live_seal)
        session._timings['local_preview_ms'] = (time.perf_counter() - started) * 1000 - count_ms - retrieval_ms
        return session
    except native.RetrievalPreflightError as error:
        return _failure(error.result['status'])
    except (ValueError, KeyError, TypeError, OverflowError, native.context.ContextError):
        return _failure('invalid_input')
    except OSError:
        return _failure('retrieval_unavailable')


def ledger_bytes(session, receipt=None, pack=None):
    """Actual compact shared ledger including controlled wrapper allocation."""
    if not isinstance(session, DecisionSession):
        raise ValueError('trusted retained session required')
    return _ledger_size(session._data, session._data['preview'], receipt, pack)


def finalize(session, decision_order=None):
    """One complete permutation; revalidate source with zero COUNT/MATCH."""
    if not isinstance(session, DecisionSession):
        return _failure('invalid_input')
    data = session._data
    bindings = copy.deepcopy(session._bindings)
    if session._used:
        return _failure('invalid_decision', bindings)
    session._used = True
    try:
        if digest(data) != session._seal or digest(session._live_inputs) != session._live_seal:
            return _failure('stale_binding', bindings)
        if decision_order is None:
            return _failure('needs_selection', bindings)
        if not isinstance(decision_order, list) or any(type(rid) is not int or rid <= 0 for rid in decision_order) or len(decision_order) != len(data['ids']) or len(set(decision_order)) != len(decision_order) or set(decision_order) != set(data['ids']):
            return _failure('invalid_decision', bindings)
        manifest, _ = _bundle(data['request']['catalog_query'])
        if manifest['pins'] != bindings['pins']:
            return _failure('stale_binding', bindings)
        verified = _source_cards(manifest, list(dict.fromkeys(data['ids'] + list(data['observation_names']))))
        cards = {rid: verified[rid] for rid in data['ids']}
        if {rid: verified[rid]['identity']['full_name'] for rid in data['observation_names']} != data['observation_names']:
            return _failure('stale_binding', bindings)
        if digest(cards) != digest(data['cards']):
            return _failure('stale_binding', bindings)
        native.context.validate_project_context_brief(data['brief'])
        native.request_guard.prepare(data['request']['catalog_query'], data['interpretation']['intent'],
            excluded_repository_ids=data['interpretation']['excluded_repository_ids'],
            excluded_dependencies=data['interpretation']['excluded_dependencies'])
        _validate_result(data['request']['catalog_query'], data['result'], cards)
        guards = _guarded(data)
        expected = _reserve_and_trim(data, _preview(data, guards), guards)
        if expected != data['preview']:
            return _failure('stale_binding', bindings)
        preview_hash = digest(expected)
        receipt = _receipt(data, preview_hash, decision_order)
        receipt_hash = digest(receipt)
        eligible = _ordered_selectable(decision_order, guards)
        records, omissions = [], {}
        ranks = {rid: rank for rank, rid in enumerate(decision_order, 1)}
        for rid in eligible:
            if len(records) >= min(12, data['request']['catalog_query']['max_cards']):
                omissions[rid] = 'candidate_budget'
                continue
            tentative = records + [_record(data, rid, ranks[rid], guards)]
            pack = _pack(data, preview_hash, receipt_hash, tentative, guards, omissions)
            if _within(data, _ledger_size(data, expected, receipt, pack)):
                records = tentative
            else:
                omissions[rid] = 'context_budget'
        pack = _pack(data, preview_hash, receipt_hash, records, guards, omissions)
        if (eligible and not records) or not _within(data, _ledger_size(data, expected, receipt, pack)):
            return _failure('budget_exceeded', bindings)
        return dict(decision_receipt=receipt, decision_pack=pack)
    except (ValueError, KeyError, TypeError, OverflowError, native.context.ContextError, OSError):
        return _failure('stale_binding', bindings)


def _strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON property')
            result[key] = value
        return result
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))


def interactive_json(input_stream=None, output_stream=None):
    """Retain one foreground preparation until one reply; no files or retry."""
    input_stream = input_stream or sys.stdin.buffer
    output_stream = output_stream or sys.stdout
    session = None
    def emit(value):
        output_stream.write(canonical_bytes(value).decode('utf-8') + '\n')
        output_stream.flush()
    try:
        raw = input_stream.readline(204802)
        if not raw or len(raw) > 204800:
            emit(_failure('invalid_input' if not raw else 'budget_exceeded'))
            return 1
        payload = _strict_json(raw)
        if not isinstance(payload, dict) or not {'brief', 'interpretation', 'public_observations'}.issubset(payload) or set(payload) - {'brief', 'interpretation', 'public_observations', 'targeted_context', 'wrapper_bytes'}:
            raise ValueError('invalid initial payload')
        session = prepare(**payload)
        if not isinstance(session, DecisionSession):
            emit(session)
            return 1
        emit(session.preview_request)
        raw = input_stream.readline(8194)
        if not raw:
            result = finalize(session)
        elif len(raw) > 8192:
            result = _failure('invalid_decision', session.preview_request['bindings'])
        else:
            reply = _strict_json(raw)
            result = finalize(session, reply['decision_order']) if isinstance(reply, dict) and set(reply) == {'decision_order'} else _failure('invalid_decision', session.preview_request['bindings'])
        emit(result)
        return 0 if 'decision_pack' in result else 1
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        emit(_failure('invalid_decision' if isinstance(session, DecisionSession) else 'invalid_input',
                      session.preview_request['bindings'] if isinstance(session, DecisionSession) else None))
        return 1
    except KeyboardInterrupt:
        emit(_failure('needs_selection', session.preview_request['bindings'] if isinstance(session, DecisionSession) else None))
        return 1
    except BrokenPipeError:
        return 1


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='strict', newline='\n')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interactive-json', '--stdio', action='store_true', required=True)
    parser.parse_args()
    sys.exit(interactive_json())
