"""CP-03 contract acceptance, not a scanner, search engine or production validator.

Structural checks use Draft 2020-12 and an offline registry. The independent
semantic examples below specify cross-document invariants for CP-06--CP-11.
No repository code, proposed commands, network requests or installs are run.
"""

import copy
from datetime import date, datetime
import fnmatch
import hashlib
import json
import math
from pathlib import Path
import re
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://myai-stackguide.invalid/contracts/v1/'
COMMON = 'context/sanitized-project-summary.schema.json'

try:
    from jsonschema import Draft202012Validator, FormatChecker, ValidationError, validators
    from referencing import Registry, Resource
except ImportError:
    Draft202012Validator = None


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'),
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


FIXTURES = load('tests/fixtures/plugin_contracts.json')
POSITIVE = FIXTURES['positive']
POLICY = load('specs/retrieval/retrieval-policy.json')
SCAN_POLICY = load('specs/scanner/scan-policy.yaml')
TAXONOMY = load('specs/catalog/taxonomy.yaml')
SCHEMAS = {path: load('specs/' + path) for path in POSITIVE}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(values, label):
    require(len(values) == len(set(values)), 'duplicate ' + label)


def mutate(value, pointer, replacement):
    result = copy.deepcopy(value)
    parts = pointer.strip('/').split('/')
    target = result
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    target[int(parts[-1]) if isinstance(target, list) else parts[-1]] = replacement
    return result


def byte_violations(schema, instance, path=''):
    """Enforce our byte annotation even when a standard $ref validator ignores it."""
    if not isinstance(schema, dict):
        return
    if '$ref' in schema:
        location, _, fragment = schema['$ref'].partition('#')
        target = SCHEMAS[location.removeprefix(BASE)]
        for part in fragment.strip('/').split('/') if fragment else []:
            target = target[part]
        yield from byte_violations(target, instance, path)
    limit = schema.get('x-max-utf8-bytes')
    if limit is not None and len(canonical(instance)) > limit:
        yield path, limit
    if isinstance(instance, dict):
        for key, value in instance.items():
            if key in schema.get('properties', {}):
                yield from byte_violations(schema['properties'][key], value, path + '/' + key)
    if isinstance(instance, list) and 'items' in schema:
        for index, value in enumerate(instance):
            yield from byte_violations(schema['items'], value, path + '/' + str(index))
    def applies(branch):
        if Draft202012Validator is None:
            return True  # Conservative byte-only traversal, never standards acceptance.
        registry = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in SCHEMAS.values())
        return Draft202012Validator(branch, registry=registry).is_valid(instance)

    for keyword in ('anyOf', 'oneOf', 'allOf'):
        for branch in schema.get(keyword, []):
            if keyword == 'allOf' or applies(branch):
                yield from byte_violations(branch, instance, path)
    if 'if' in schema:
        branches = ('then', 'else') if Draft202012Validator is None else (
            'then' if applies(schema['if']) else 'else',)
        for keyword in branches:
            if keyword in schema:
                yield from byte_violations(schema[keyword], instance, path)


def lexical_path(path):
    """Policy oracle only: does not resolve files, handles, links or root races."""
    pattern = SCHEMAS[COMMON]['$defs']['relativePath']['pattern']
    if not re.fullmatch(pattern, path):
        return False, 'unsafe_path'
    parts = path.casefold().split('/')
    device = r'(?:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?'
    if any(part.endswith(('.', ' ')) or re.fullmatch(device, part) for part in parts):
        return False, 'unsafe_path'
    output = SCAN_POLICY['excluded_output_root'].casefold()
    if path.casefold() == output or path.casefold().startswith(output + '/'):
        return False, 'plugin_output'
    if set(parts) & set(SCAN_POLICY['denied_segments']):
        return False, 'excluded_segment'
    if any(fnmatch.fnmatchcase(parts[-1], glob) for glob in SCAN_POLICY['denied_filename_globs']):
        return False, 'sensitive'
    eligible = parts[-1] in {name.casefold() for name in SCAN_POLICY['allowed_filenames']}
    eligible |= Path(parts[-1]).suffix in SCAN_POLICY['allowed_extensions']
    return (True, 'eligible') if eligible else (False, 'unsupported')


def check_lines(source):
    start, end = source['line_start'], source['line_end']
    require((start is None and end is None) or
            (start is not None and end is not None and start <= end), 'line range')


def check_summary(summary):
    evidence = {item['evidence_id']: item for item in summary['evidence']}
    require(len(evidence) == len(summary['evidence']), 'duplicate project evidence')
    facts = {item['fact_id'] for item in summary['facts']}
    require(len(facts) == len(summary['facts']), 'duplicate observed fact')
    for item in summary['evidence']:
        check_lines(item)
        if item['kind'] == 'user_answer':
            require(item['answer_id'] is not None and item['relative_path'] is None
                    and item['line_start'] is None, 'answer source kind')
        else:
            require(item['answer_id'] is None and item['relative_path'] is not None,
                    'project source kind')
            require(lexical_path(item['relative_path'])[0], 'excluded project source')
    for fact in summary['facts']:
        require(set(fact['evidence_refs']) <= evidence.keys(), 'unresolved fact evidence')
    for inference in summary['inferences']:
        require(set(inference['basis_fact_ids']) <= facts, 'inference has no observed basis')
    if summary['coverage'] == 'not_scanned':
        require(all(item['kind'] == 'user_answer' for item in evidence.values()),
                'unscanned source observation')


def check_query(query):
    require(query['policy_sha256'] == file_digest('specs/retrieval/retrieval-policy.json'), 'query policy digest')
    require(query['max_cards'] <= query['max_candidates'], 'card/candidate budget')
    unique([v['variant_id'] for v in query['variants']], 'query variant')
    for variant in query['variants']:
        require(all(term.strip() for term in variant['terms']), 'empty literal term')
    fields = query['constraints']['mandatory_fields']
    for field, key in [('license', 'allowed_licenses'), ('language', 'languages'),
                       ('deployment', 'deployment'), ('compatibility', 'compatibility')]:
        require(field not in fields or bool(query['constraints'][key]), 'missing constraint target')
    require('no_server' not in fields or query['constraints']['require_no_server'] is True,
            'no-server constraint target')


ACTIVITY_FIELDS = {'createdAt': 'repository_created_at', 'pushedAt': 'repository_pushed_at',
                   'lastCommitAt': 'commit_committed_date', 'lastReleaseAt': 'release_published_at'}


def check_card(card):
    require(card['url'] == 'https://github.com/' + card['full_name'], 'repository URL identity')
    categories = {item['id'] for item in TAXONOMY['categories']}
    require(card['primary_category'] in categories and
            set(card['secondary_categories']) <= categories, 'unknown taxonomy category')
    require(card['primary_category'] not in card['secondary_categories'], 'duplicate primary category')
    require(card['repo_id'] not in card['aliases'], 'self alias')
    unique(card['aliases'], 'alias')
    require(card['license'] not in ('NOASSERTION', 'unknown', ''), 'unknown license must be null')
    evidence = {item['evidence_id']: item for item in card['evidence']}
    require(len(evidence) == len(card['evidence']), 'duplicate card evidence')
    if card['corpus_kind'] != 'synthetic_fixture':
        require(all(item['source_kind'] != 'synthetic_fixture' and
                    not item['source_ref'].startswith('fixture:') for item in evidence.values()),
                'synthetic evidence in public snapshot')
    if card['catalog_status'] == 'accepted':
        owner = 'curator_record' if card['catalog_status_source'] == 'curator_decision' else 'catalog_snapshot'
        require(any(item['source_kind'] == owner and '/catalog_status' in item['fields']
                    for item in evidence.values()), 'catalog acceptance provenance')
    activity = card['activity']
    unique([item['field'] for item in activity['observations']], 'activity observation')
    require({item['field'] for item in activity['observations']} ==
            {field for field in ACTIVITY_FIELDS if activity[field] is not None}, 'activity observation coverage')
    for observation in activity['observations']:
        field = observation['field']
        require(observation['source_field'] == ACTIVITY_FIELDS[field], 'activity source-field conflation')
        ref = observation['evidence_ref']
        require(ref in evidence and '/activity/' + field in evidence[ref]['fields'], 'activity evidence pointer')
        require(evidence[ref]['observed_at'] == observation['observedAt'], 'activity observation timestamp')


ADVISORY = ['use_cases', 'best_for', 'adoption_mode', 'project_stages', 'complexity',
            'integration_surface', 'compatibility']


def check_eligibility(eligibility, card, query):
    require(eligibility['repo_id'] == card['repo_id'] and
            eligibility['query_id'] == query['query_id'], 'eligibility identity')
    checks = {item['field']: item for item in eligibility['checks']}
    required = set(query['constraints']['mandatory_fields']) | {'availability', 'archived', 'advisory_evidence'}
    require(len(checks) == len(eligibility['checks']) and set(checks) == required,
            'eligibility check coverage')
    evidence = {item['evidence_id']: item for item in card['evidence']}
    constraints = query['constraints']
    outcomes = []
    for field, check in checks.items():
        pointers = ADVISORY if field == 'advisory_evidence' else [
            {'no_server': 'requires_server'}.get(field, field)]
        refs = check['evidence_refs']
        require(set(refs) <= evidence.keys(), 'unresolved eligibility evidence')
        sourced = all(any('/' + pointer in evidence[ref]['fields'] and
                         evidence[ref]['verification'] != 'unknown' for ref in refs) for pointer in pointers)
        known = all(card[pointer] is not None and card[pointer] != [] and
                    card[pointer] != 'unknown' for pointer in pointers)
        if not known or not sourced:
            outcome = 'unknown'
        else:
            passed = {
                'license': card['license'] in constraints['allowed_licenses'],
                'language': card['language'] in constraints['languages'],
                'deployment': bool(set(card['deployment']) & set(constraints['deployment'])),
                'compatibility': set(constraints['compatibility']) <= set(card['compatibility']),
                'no_server': card['requires_server'] is False,
                'availability': card['availability'] == 'available',
                'archived': card['archived'] is False,
                'advisory_evidence': card['evidence_stage'] == 'advisory_evidence_complete',
            }[field]
            outcome = 'pass' if passed else 'fail'
        require(check['outcome'] == outcome, 'unsupported ' + field + ' outcome')
        outcomes.append(outcome)
    expected = 'blocked' if 'fail' in outcomes else 'reference_only' if 'unknown' in outcomes else 'primary_eligible'
    require(eligibility['status'] == expected, 'eligibility status contradicts checks')
    if expected == 'reference_only':
        require('mandatory_fact_unknown' in eligibility['reason_codes'] and
                eligibility['required_verifications'], 'unknown facts need concrete next checks')
    elif expected == 'blocked':
        require(bool(eligibility['reason_codes']), 'blocked candidate needs reason')


def classification(counters):
    limits = SCAN_POLICY['classification']
    if (counters['budget_reached'] or not counters['topology_complete'] or counters['workspace_declared'] or
            counters['service_roots'] >= limits['monorepo_min_service_roots']):
        return 'large_or_monorepo'
    if counters['eligible_files'] == 0:
        return 'idea_or_empty'
    if (counters['eligible_files'] <= limits['compact_max_eligible_files'] and
            counters['manifest_count'] <= limits['compact_max_manifests']):
        return 'compact'
    if (counters['eligible_files'] <= limits['standard_max_eligible_files'] and
            counters['manifest_count'] <= limits['standard_max_manifests']):
        return 'standard'
    return 'large_or_monorepo'


def check_scan(report):
    manifest, summary = report['manifest'], report['summary']
    require(report['run_id'] == manifest['run_id'] == summary['run_id'], 'scan run identity')
    require(report['mode'] == manifest['mode'], 'scan mode identity')
    counts = manifest['counters']
    limits = SCAN_POLICY['modes'][manifest['mode']]
    require(counts['file_attempts'] <= limits['max_files'] and
            counts['bytes_consumed'] <= limits['max_bytes'], 'scan mode budget')
    require(report['classification'] == classification(counts), 'scan classification')
    if not counts['topology_complete'] or counts['budget_reached']:
        require(report['status'] != 'complete' and summary['coverage'] != 'complete', 'incomplete coverage')
    if counts['elapsed_ms'] > limits['max_seconds'] * 1000:
        require(counts['budget_reached'], 'cooperative deadline overrun not reported')
    unique([item['relative_path'].casefold() for item in manifest['files']], 'scan path')
    refs = {item['evidence_id'] for item in summary['evidence']}
    for item in manifest['files']:
        require(lexical_path(item['relative_path'])[0], 'excluded scan source')
        require(item['evidence_ref'] is None or item['evidence_ref'] in refs, 'scan evidence reference')
    check_summary(summary)


FAILURES = {'no_match': {'no_hits'}, 'retrieval_unavailable': {'fts5_unavailable', 'index_missing', 'index_corrupt'},
            'index_incompatible': {'index_incompatible'}, 'invalid_query': {'invalid_query'}, 'cancelled': {'cancelled'}}


def check_retrieval(result, query, index):
    check_query(query)
    require(result['query_id'] == query['query_id'] and result['query_sha256'] == digest(query), 'query pairing')
    require(result['brief_version'] == query['brief_version'], 'stale retrieval version')
    if result['pins'] is None:
        require(index is None and result['status'] not in ('ok', 'no_match'), 'missing index pins')
    else:
        require(index is not None and result['pins'] == index['pins'], 'index pairing')
        require(result['pins']['policy_sha256'] == query['policy_sha256'], 'index policy pairing')
        require(result['pins']['taxonomy_sha256'] == file_digest('specs/catalog/taxonomy.yaml'), 'taxonomy pairing')
    require(result['retrieved_hits'] <= query['max_candidates'], 'aggregate hit budget')
    require(result['executed_variants'] <= len(query['variants']), 'executed variant count')
    candidates = result['candidates']
    unique([item['repo_id'] for item in candidates], 'canonical candidate')
    require([item['rank'] for item in candidates] == list(range(1, len(candidates) + 1)), 'contiguous ranks')
    require(candidates == sorted(candidates, key=lambda item: (-item['rrf_score'], item['repo_id'])), 'RRF sort')
    executed = {item['variant_id'] for item in query['variants'][:result['executed_variants']]}
    seen_positions = set()
    for candidate in candidates:
        ranks = candidate['variant_ranks']
        unique([item['variant_id'] for item in ranks], 'candidate variant')
        require({item['variant_id'] for item in ranks} <= executed, 'unexecuted variant rank')
        expected = sum(1 / (POLICY['rank_fusion']['k'] + item['rank']) for item in ranks)
        require(math.isclose(candidate['rrf_score'], expected, rel_tol=1e-12), 'RRF score')
        for rank in ranks:
            position = (rank['variant_id'], rank['rank'])
            require(position not in seen_positions and rank['rank'] <= result['retrieved_hits'], 'variant position')
            seen_positions.add(position)
    require(len(seen_positions) <= result['retrieved_hits'], 'dedupe hit accounting')
    if result['status'] != 'ok':
        require(not candidates and set(result['reason_codes']) <= FAILURES[result['status']]
                and result['reason_codes'], 'failure disguised as no-match')
        if result['status'] == 'no_match':
            require(result['retrieved_hits'] == 0 and result['executed_variants'] > 0, 'unexecuted no-match')
    elif result['truncated']:
        require('candidate_budget' in result['reason_codes'], 'missing candidate truncation reason')


def check_bundle(state):
    require(not list(byte_violations(SCHEMAS['artifact/project-artifact-state.schema.json'], state)),
            'nested serialized byte budget')
    if state['schema_version'] == '1.1.0':
        check_workspace(state)
    run = state['run_id']
    for key in ('intake', 'brief', 'selection', 'request', 'retrieval', 'evidence_pack', 'memo'):
        value = state[key]
        require(value is None or value['run_id'] == run, 'nested run identity')
    require(state['html_revision'] is None or state['html_revision'] <= state['revision'], 'future HTML revision')
    intake = state['intake']
    unique([answer['question_id'] for answer in intake['answers']], 'interview question')
    require([answer['ordinal'] for answer in intake['answers']] == list(range(1, len(intake['answers']) + 1)), 'interview ordinals')
    require(all(answer['run_id'] == run for answer in intake['answers']), 'answer run identity')
    require(intake['questions_asked'] == len(intake['answers']) + (intake['pending_question_id'] is not None), 'question count')
    if intake['questions_asked'] == 0 and intake['status'] == 'ready':
        require(state['brief'] is not None and state['brief']['context_status'] == 'reviewed', 'empty intake needs existing context')
    brief = state['brief']
    if brief is None:
        require(all(state[key] is None for key in ('selection', 'request', 'retrieval', 'evidence_pack', 'memo')), 'missing brief')
        return
    check_summary(brief['observations'])
    require(brief['observations']['run_id'] == run, 'summary run identity')
    for key in ('selection', 'request', 'retrieval', 'evidence_pack', 'memo'):
        require(state[key] is None or state[key]['brief_version'] == brief['brief_version'], 'stale brief output')
    if state['selection']:
        for item in state['selection']['requested_sources']:
            require(lexical_path(item['relative_path'])[0], 'excluded targeted source')
            check_lines(item)
    corrections = state['corrections']
    unique([item['correction_id'] for item in corrections], 'correction')
    require(brief['user_corrections'] == [item['correction_id'] for item in corrections], 'brief corrections')
    for correction in corrections:
        require(correction['run_id'] == run and correction['to_brief_version'] == correction['from_brief_version'] + 1,
                'correction version')
    request, result, pack, memo = (state[key] for key in ('request', 'retrieval', 'evidence_pack', 'memo'))
    if request is None:
        require(result is None and pack is None and memo is None, 'missing recommendation request')
        return
    query = request['query']
    require(request['brief_id'] == brief['brief_id'] and query['brief_version'] == brief['brief_version']
            and query['constraints'] == brief['constraints'], 'query/context pairing')
    check_query(query)
    if result is None:
        require(pack is None and memo is None, 'missing retrieval result')
        return
    check_retrieval(result, query, state['index_manifest'])
    if pack is None:
        require(memo is None, 'missing evidence pack')
        return
    require(pack['pins'] == result['pins'] and pack['query_id'] == query['query_id'] and
            pack['query_sha256'] == digest(query) and pack['pack_id'] == request['pack_id'], 'pack pairing')
    require(len(canonical(pack)) <= query['max_evidence_bytes'] and len(pack['cards']) <= query['max_cards'], 'evidence budget')
    candidates = {item['repo_id']: item for item in result['candidates']}
    packed = {item['card']['repo_id']: item for item in pack['cards']}
    require(len(packed) == len(pack['cards']), 'duplicate packed identity')
    excluded = {item['repo_id'] for item in pack['exclusions']}
    require(len(excluded) == len(pack['exclusions']) and not (excluded & packed.keys())
            and excluded | packed.keys() == candidates.keys(), 'candidate coverage')
    aliases = []
    for repo_id, entry in packed.items():
        card = entry['card']
        check_card(card)
        aliases.extend([repo_id, *card['aliases']])
        require(card['corpus_kind'] == pack['pins']['corpus_kind'], 'card corpus kind')
        retrieved = candidates[repo_id]
        require(entry['retrieval_rank'] == retrieved['rank'] and entry['rrf_score'] == retrieved['rrf_score']
                and entry['matched_fields'] == retrieved['matched_fields'], 'card retrieval trace')
        check_eligibility(entry['eligibility'], card, query)
    unique(aliases, 'canonical alias across pack')
    expected_status = 'ready' if result['status'] == 'ok' and packed else 'no_match' if result['status'] in ('ok', 'no_match') else 'unavailable'
    require(pack['status'] == expected_status, 'pack error status')
    if result['status'] != 'ok':
        require(pack['reason_codes'] == result['reason_codes'], 'pack failure reason')
    if memo is None:
        return
    require(memo['pins'] == pack['pins'] and memo['pack_id'] == pack['pack_id']
            and memo['request_id'] == request['request_id'], 'memo pairing')
    categories = [item['category_id'] for item in memo['category_path']]
    unique(categories, 'category path')
    require(set(categories) <= {item['id'] for item in TAXONOMY['categories']}, 'unknown category path')
    refs = {item['evidence_id'] for entry in packed.values() for item in entry['card']['evidence']}
    require(all(item['evidence_ref'] in refs for item in memo['reading_path']), 'reading-path evidence')
    unique([item['repo_id'] for item in memo['recommendations']], 'recommended repository')
    for recommendation in memo['recommendations']:
        require(recommendation['repo_id'] in packed, 'recommendation outside pack')
        entry = packed[recommendation['repo_id']]
        own_refs = {item['evidence_id'] for item in entry['card']['evidence']}
        require(set(recommendation['evidence_refs']) <= own_refs, 'recommendation evidence')
        if recommendation['role'] == 'primary_candidate':
            require(entry['eligibility']['status'] == 'primary_eligible', 'unsupported primary candidate')
        if entry['eligibility']['status'] != 'primary_eligible':
            require(recommendation['next_checks'] and recommendation['caveats'], 'conditional recommendation checks')
    plan = memo['integration_plan']
    if plan:
        require(plan['run_id'] == run and plan['brief_version'] == brief['brief_version'], 'integration context')
        require(set(plan['selected_repo_ids']) <= packed.keys() and set(plan['evidence_refs']) <= refs, 'integration evidence')
        require(all(packed[repo_id]['eligibility']['status'] != 'blocked' for repo_id in plan['selected_repo_ids']), 'blocked integration')
        if any(packed[repo_id]['eligibility']['status'] == 'reference_only' for repo_id in plan['selected_repo_ids']):
            require(plan['unresolved_questions'] and plan['prerequisites'], 'conditional integration uncertainty')
    if pack['status'] == 'unavailable':
        require(memo['status'] == 'retrieval_unavailable' and not memo['recommendations'] and plan is None, 'memo hides retrieval error')
    elif pack['status'] == 'no_match':
        require(memo['status'] == 'no_match', 'memo hides no-match')


def check_transition(before, after, expected_revision):
    """State protocol examples; no claim about atomic filesystem execution."""
    require(before['revision'] == expected_revision, 'optimistic revision conflict')
    require(before['status'] == 'active', 'immutable finalized run')
    require(before['run_id'] == after['run_id'] and after['revision'] == before['revision'] + 1, 'state transition revision')
    if before['schema_version'] == '1.1.0':
        ignored = {'revision', 'content_revision', 'presentation', 'updated_at', 'html_revision'}
        domain_before = {key: value for key, value in before.items() if key not in ignored}
        domain_after = {key: value for key, value in after.items() if key not in ignored}
        changed = domain_before != domain_after
        require(after['content_revision'] == before['content_revision'] + int(changed), 'content revision transition')
        old_p, new_p = before['presentation'], after['presentation']
        old_fields = {key: value for key, value in old_p.items() if key not in ('default_locale', 'presentation_revision')}
        new_fields = {key: value for key, value in new_p.items() if key not in ('default_locale', 'presentation_revision')}
        require(new_p['presentation_revision'] == old_p['presentation_revision'] + int(old_fields != new_fields),
                'presentation revision transition')
        if before['brief'] and after['brief']:
            semantic_before = {key: value for key, value in before['brief'].items() if key not in ('updated_at', 'brief_version')}
            semantic_after = {key: value for key, value in after['brief'].items() if key not in ('updated_at', 'brief_version')}
            if semantic_before != semantic_after:
                require(after['brief']['brief_version'] == before['brief']['brief_version'] + 1,
                        'semantic Brief correction requires version bump')
        require(before['scan'] == after['scan'] or not (before['brief'] and after['brief'] and
                before['brief']['brief_version'] != after['brief']['brief_version']), 'correction rewrites scan evidence')
    if after['brief'] and before['brief'] and after['brief']['brief_version'] != before['brief']['brief_version']:
        require(after['brief']['brief_version'] == before['brief']['brief_version'] + 1, 'brief revision jump')
        require(all(after[key] is None for key in ('selection', 'request', 'retrieval', 'evidence_pack', 'memo')),
                'correction must invalidate derived artifacts')
        require(after['brief']['observations'] == before['brief']['observations'], 'correction rewrites observed facts')
        correction = after['corrections'][-1]
        require(correction['expected_state_revision'] == expected_revision and
                correction['from_brief_version'] == before['brief']['brief_version'] and
                correction['to_brief_version'] == after['brief']['brief_version'], 'correction transition pairing')
    check_bundle(after)


def narrative_fields(state):
    pattern = SCHEMAS['artifact/localized-presentation.schema.json']['$defs']['fieldPointer']['pattern']

    def leaves(value, pointer=''):
        if isinstance(value, dict):
            for key, item in value.items():
                if key != 'presentation':
                    yield from leaves(item, pointer + '/' + key)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from leaves(item, pointer + '/' + str(index))
        elif isinstance(value, str) and re.fullmatch(pattern, pointer):
            yield pointer, value
    return dict(leaves(state))


def resolve_pointer(state, pointer):
    value = state
    for part in pointer.strip('/').split('/'):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def canonical_evidence(state):
    evidence = {}
    facts = {}
    summaries = []
    if state.get('scan'):
        summaries.append(state['scan']['summary'])
    if state['brief']:
        summaries.append(state['brief']['observations'])
    for summary in summaries:
        for fact in summary['facts']:
            require(fact['fact_id'] not in facts or facts[fact['fact_id']] == fact,
                    'contradictory duplicate observed fact')
            facts[fact['fact_id']] = fact
    groups = [summary['evidence'] for summary in summaries]
    if state['evidence_pack']:
        groups.extend(entry['card']['evidence'] for entry in state['evidence_pack']['cards'])
    for group in groups:
        for item in group:
            key = item['evidence_id']
            require(key not in evidence or evidence[key] == item, 'contradictory duplicate evidence')
            evidence[key] = item
    return evidence


def field_evidence(state, pointer):
    parts = pointer.strip('/').split('/')
    for length in range(len(parts) - 1, 0, -1):
        owner = resolve_pointer(state, '/' + '/'.join(parts[:length]))
        if isinstance(owner, dict):
            if 'evidence_refs' in owner:
                return sorted(set(owner['evidence_refs']))
            if 'evidence_ref' in owner:
                return [owner['evidence_ref']] if owner['evidence_ref'] else []
            if 'basis_fact_ids' in owner:
                summary = state['scan']['summary'] if pointer.startswith('/scan/') else state['brief']['observations']
                return sorted({ref for fact in summary['facts'] if fact['fact_id'] in owner['basis_fact_ids']
                               for ref in fact['evidence_refs']})
    return []


def field_literals(state, text):
    values = set(re.findall(r'`([^`]+)`', text))
    narrative = re.sub(r'`[^`]+`', '', text)
    keys = {'repo_id', 'full_name', 'url', 'relative_path', 'language', 'languages', 'compatibility',
            'command', 'proposed_commands', 'safe_paths', 'framework', 'frameworks'}

    def occurs(value):
        prefix = r'(?<!\w)' if value[0].isalnum() or value[0] == '_' else ''
        suffix = r'(?!\w)' if value[-1].isalnum() or value[-1] == '_' else ''
        return re.search(prefix + re.escape(value) + suffix, narrative) is not None

    def visit(value, key=''):
        if isinstance(value, dict):
            if value.get('kind') in ('language', 'framework', 'storage', 'dependency'):
                literal = value.get('value')
                if isinstance(literal, str) and literal and occurs(literal):
                    values.add(literal)
            for name, child in value.items():
                if name != 'presentation':
                    visit(child, name)
        elif isinstance(value, list):
            for child in value:
                visit(child, key)
        elif (key in keys or key.endswith('_id') or key.endswith('_ids')) and isinstance(value, str) and value and occurs(value):
            values.add(value)
    visit(state)
    return sorted(values)


def check_claim(claim, evidence, answers, allow_public=False):
    require(set(claim['evidence_refs']) <= evidence.keys(), 'unresolved claim evidence')
    require(set(claim['answer_ids']) <= answers, 'unresolved or skipped claim answer')
    if claim['kind'] == 'observed':
        require(any((evidence[ref].get('kind') in ('project_manifest', 'project_source', 'project_document') and
                     evidence[ref].get('relative_path') is not None) or
                    (allow_public and 'source_kind' in evidence[ref]) for ref in claim['evidence_refs']),
                'observed claim needs project/source evidence')
    if claim['kind'] == 'user_statement':
        require(bool(claim['answer_ids']), 'user statement needs saved answer')


def check_workspace(state):
    require(1 <= state['content_revision'] <= state['revision'], 'content revision range')
    require(state['html_revision'] is None or state['html_revision'] < state['revision'], 'publication cannot mutate current state')
    for key in ('intake', 'brief', 'memo'):
        require(state[key] is None or state[key]['schema_version'] == '1.1.0', 'workspace nested version')
    if state['scan']:
        require(state['scan']['run_id'] == state['run_id'], 'scan run identity')
        check_scan(state['scan'])
    intake = state['intake']
    questions = intake['questions']
    unique([item['question_id'] for item in questions], 'question ledger ID')
    require(len(questions) == intake['questions_asked'] and
            [item['ordinal'] for item in questions] == list(range(1, len(questions) + 1)), 'question ledger cardinality')
    ledger = {item['question_id']: item for item in questions}
    joined = {answer['question_id'] for answer in intake['answers']}
    if intake['pending_question_id']:
        require(intake['pending_question_id'] not in joined, 'pending question already answered')
        joined.add(intake['pending_question_id'])
    require(joined == ledger.keys(), 'question answer join')
    require(all(ledger[item['question_id']]['ordinal'] == item['ordinal'] for item in intake['answers']), 'question answer ordinal')
    require(intake['status'] != 'ready' or bool(intake['completion_reason']), 'ready completion reason')
    evidence = canonical_evidence(state)
    answers = {item['answer_id'] for item in intake['answers']
               if item['status'] == 'answered' and item['sanitized_value'] is not None}
    brief = state['brief']
    if brief:
        details = brief['details']
        claims = [details[key] for key in ('problem', 'target_user', 'workflow', 'current_behavior',
                                          'target_behavior', 'baseline', 'scope')]
        claims.extend(details['non_goals'])
        claims.extend(item['claim'] for item in details['constraint_notes'])
        for claim in claims:
            check_claim(claim, evidence, answers)
        constraints = {item['constraint_id'] for item in details['constraint_notes']}
        require(len(constraints) == len(details['constraint_notes']), 'duplicate constraint note')
        unique([item['tension_id'] for item in details['tensions']], 'tension')
        for item in details['tensions']:
            require(set(item['constraint_ids']) <= constraints, 'unresolved tension constraint')
    memo = state['memo']
    plan = memo['integration_plan'] if memo else None
    if memo and memo['comparison_details']:
        comparison = memo['comparison_details']
        cells = comparison['cells']
        unique([(item['criterion'], item['repo_id']) for item in cells], 'comparison cell')
        packed = {entry['card']['repo_id'] for entry in state['evidence_pack']['cards']}
        for cell in cells:
            require((cell['baseline'] and cell['repo_id'] is None and comparison['include_no_change']) or
                    (not cell['baseline'] and cell['repo_id'] in packed), 'comparison baseline/repository join')
            check_claim(cell['claim'], evidence, answers, allow_public=True)
    if plan:
        require(plan['schema_version'] == '1.1.0', 'integration version')
        details = plan['details']
        steps = [step['step_id'] for step in plan['steps']]
        deps = details['step_dependencies']
        unique([entry['step_id'] for entry in deps], 'step dependency')
        require({entry['step_id'] for entry in deps} == set(steps), 'step dependency coverage')
        for entry in deps:
            require(set(entry['depends_on']) <= set(steps[:steps.index(entry['step_id'])]), 'forward/cyclic dependency')
            require(set(entry['evidence_refs']) <= evidence.keys(), 'step evidence')
            for path in entry['safe_paths']:
                require(lexical_path(path)[0] and any(evidence[ref].get('relative_path') == path
                        for ref in entry['evidence_refs']), 'unsupported or unsafe step path')
        diagram = details['diagram']
        if diagram:
            nodes = {node['component_id'] for node in diagram['nodes']}
            require(len(nodes) == len(diagram['nodes']), 'duplicate diagram node')
            for node in diagram['nodes']:
                require(set(node['evidence_refs']) <= evidence.keys(), 'diagram evidence')
                if node['change'] in ('reuse', 'change'):
                    require(any(evidence[ref].get('kind') in ('project_manifest', 'project_source', 'project_document') and
                                evidence[ref].get('relative_path') is not None for ref in node['evidence_refs']),
                            'reused node lacks project evidence')
            for edge in diagram['edges']:
                require(edge['from_component_id'] in nodes and edge['to_component_id'] in nodes, 'unresolved diagram edge')
        unique([item['check_id'] for item in details['prerequisite_checks']], 'prerequisite')
        for item in details['prerequisite_checks']:
            require(set(item['evidence_refs']) <= evidence.keys() and set(item['answer_ids']) <= answers, 'prerequisite provenance')
            if item['status'] in ('unknown', 'authorization_needed'):
                require(bool(item['next_check']), 'unknown prerequisite needs next check')
            else:
                require(bool(item['evidence_refs'] or item['answer_ids']), 'known prerequisite needs provenance')
            if item['status'] == 'already_authorized':
                require(item['kind'] == 'authorization' and bool(item['answer_ids']), 'authorization needs saved scope')
    presentation = state['presentation']
    require(presentation['run_id'] == state['run_id'] and
            presentation['source_content_revision'] == state['content_revision'], 'presentation content identity')
    expected_identity = {'brief_id': brief['brief_id'] if brief else None,
                         'brief_version': brief['brief_version'] if brief else None,
                         'memo_id': memo['memo_id'] if memo else None,
                         'plan_id': plan['plan_id'] if plan else None}
    require(all(presentation[key] == value for key, value in expected_identity.items()), 'presentation result identity')
    fields = narrative_fields(state)
    unique([entry['field_pointer'] for entry in presentation['fields']], 'localized pointer')
    for entry in presentation['fields']:
        pointer = entry['field_pointer']
        require(pointer in fields, 'unresolved or forbidden narrative pointer')
        text = fields[pointer]
        require(entry['source_sha256'] == digest(text) and
                entry['source_content_revision'] == state['content_revision'], 'stale localized source')
        require(entry['evidence_refs'] == field_evidence(state, pointer) and
                set(entry['evidence_refs']) <= evidence.keys(), 'localized evidence derivation')
        literals = field_literals(state, text)
        require(entry['canonical_literals'] == literals, 'localized literal derivation')
        for locale in ('ru', 'en'):
            value = entry[locale]
            if value['status'] == 'available':
                require(all(literal in value['text'] for literal in literals), 'localized technical literal changed')
                if entry['source_locale'] == locale:
                    require(value['text'] == text, 'source-language text changed')
    for locale in ('ru', 'en'):
        available = sum(entry[locale]['status'] == 'available' for entry in presentation['fields'])
        require(presentation['coverage'][locale] == {'status': 'complete' if available == len(fields) else 'partial',
                'required_fields': len(fields), 'available_fields': available}, 'localized coverage mismatch')


def rebind_presentation(state):
    """Fixture builder only: does not translate; keeps unchanged fields and honest partial coverage."""
    presentation = state['presentation']
    brief, memo = state['brief'], state['memo']
    plan = memo['integration_plan'] if memo else None
    presentation.update(source_content_revision=state['content_revision'],
                        brief_id=brief['brief_id'] if brief else None,
                        brief_version=brief['brief_version'] if brief else None,
                        memo_id=memo['memo_id'] if memo else None, plan_id=plan['plan_id'] if plan else None)
    fields = narrative_fields(state)
    presentation['fields'] = [entry for entry in presentation['fields'] if entry['field_pointer'] in fields and
                              entry['source_sha256'] == digest(fields[entry['field_pointer']])]
    for entry in presentation['fields']:
        entry['source_content_revision'] = state['content_revision']
    for locale in ('ru', 'en'):
        count = sum(entry[locale]['status'] == 'available' for entry in presentation['fields'])
        presentation['coverage'][locale] = {'status': 'complete' if count == len(fields) else 'partial',
                                           'required_fields': len(fields), 'available_fields': count}


def check_publication(outcome, state, html_bytes=None):
    """Synthetic receipt oracle, not proof of lock/write/renderer execution."""
    keys = ('run_id', 'revision', 'content_revision')
    current = {key: state[key] for key in keys}
    require(outcome['current'] == current, 'publication current state mismatch')
    for stamp in (outcome['saved'], outcome['current'], outcome['published']):
        require(stamp is None or stamp['content_revision'] <= stamp['revision'], 'publication revision range')
    published = outcome['published']
    published_stamp = {key: published[key] for key in keys} if published else None
    status = outcome['publication_status']
    if status == 'current':
        require(outcome['saved'] == current == published_stamp, 'published state identity mismatch')
        require(published['presentation_revision'] == state['presentation']['presentation_revision'], 'published presentation mismatch')
        require(html_bytes is not None and hashlib.sha256(html_bytes).hexdigest() == published['html_sha256'], 'publication byte hash')
    elif status == 'superseded':
        require(outcome['saved'] != current and outcome['failure_reason'] == 'render_superseded', 'superseded target must differ')
        require(outcome['retry'] == 'stop', 'superseded retry')
    elif status == 'stale':
        require(published is not None and published_stamp != current, 'stale publication must differ')
        require(outcome['saved'] == current, 'obsolete target must be superseded')
    elif status == 'unavailable':
        require(published is None, 'first failure has no HTML')
        require(outcome['saved'] == current, 'obsolete target must be superseded')
    elif status == 'not_attempted':
        require(outcome['saved'] is None and outcome['render_attempts'] == 0 and outcome['retry'] == 'stop' and
                outcome['failure_reason'] in ('state_busy', 'state_conflict', 'state_invalid', 'state_incompatible',
                                            'state_write_failed', 'history_integrity', 'storage_limit'),
                'saved state requires publication attempt')
        require(outcome['commit_status'] == 'not_saved' or outcome['operation'] == 'render_only',
                'invalid not-attempted operation')
    if outcome['retry'] == 'render_only':
        require(outcome['saved'] == current and outcome['render_attempts'] == 1 and
                outcome['failure_reason'] in ('render_failed', 'html_write_failed'), 'retry scope')
    require(outcome['render_attempts'] <= 2, 'render retry bound')
    if outcome['commit_status'] == 'not_saved':
        require(outcome['saved'] is None and outcome['render_attempts'] == 0 and status == 'not_attempted', 'failed commit claimed saved')


class SchemaContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if Draft202012Validator is None:
            raise RuntimeError('V-CONTRACT requires the development-only jsonschema validator; '
                               'dependency missing is not a passing or skipped acceptance gate.')
        checker = FormatChecker()

        @checker.checks('date-time', raises=ValueError)
        def utc_timestamp(value):
            return not isinstance(value, str) or (value.endswith('Z') and
                   datetime.fromisoformat(value.replace('Z', '+00:00')) is not None)

        @checker.checks('date', raises=ValueError)
        def iso_date(value):
            return not isinstance(value, str) or date.fromisoformat(value) is not None

        @checker.checks('uuid', raises=ValueError)
        def uuid_value(value):
            return not isinstance(value, str) or str(uuid.UUID(value)) == value

        def byte_limit(validator, limit, instance, schema):
            if len(canonical(instance)) > limit:
                yield ValidationError('compact UTF-8 byte budget exceeded')

        cls.validator_type = validators.extend(Draft202012Validator, {'x-max-utf8-bytes': byte_limit})
        cls.checker = checker
        cls.registry = Registry().with_resources((schema['$id'], Resource.from_contents(schema))
                                                for schema in SCHEMAS.values())

    def validator(self, path):
        return self.validator_type(SCHEMAS[path], registry=self.registry, format_checker=self.checker)

    def test_all_twenty_two_schemas_preserve_legacy_and_add_workspace_examples(self):
        actual = {str(path.relative_to(ROOT / 'specs')).replace('\\', '/')
                  for path in (ROOT / 'specs').rglob('*.schema.json')}
        self.assertEqual(actual, set(POSITIVE))
        self.assertEqual(len(actual), 22)
        for path, schema in SCHEMAS.items():
            with self.subTest(schema=path):
                Draft202012Validator.check_schema(schema)
                self.validator(path).validate(POSITIVE[path])
                self.assertEqual(list(byte_violations(schema, POSITIVE[path])), [])
        for path, value in FIXTURES['workspace_positive'].items():
            with self.subTest(workspace_schema=path):
                self.validator(path).validate(value)
                self.assertEqual(list(byte_violations(SCHEMAS[path], value)), [])

    def test_legacy_and_workspace_versions_cannot_mix(self):
        path = 'artifact/project-artifact-state.schema.json'
        legacy, current = baseline(), workspace_baseline()
        for key in ('intake', 'brief', 'memo'):
            hybrid = copy.deepcopy(legacy)
            hybrid[key] = current[key]
            with self.subTest(key=key):
                self.assertTrue(list(self.validator(path).iter_errors(hybrid)))
        legacy['memo']['integration_plan'] = current['memo']['integration_plan']
        self.assertTrue(list(self.validator(path).iter_errors(legacy)))
        current['intake'] = baseline()['intake']
        self.assertTrue(list(self.validator(path).iter_errors(current)))

    def test_presentation_pointer_coverage_shape_and_publication_conditions(self):
        path = 'artifact/localized-presentation.schema.json'
        for pointer, value in [('/fields/0/field_pointer', '/memo/integration_plan/steps/0/proposed_commands/0'),
                               ('/fields/0/field_pointer', '/presentation/default_locale'),
                               ('/fields/0/ru/status', 'missing')]:
            with self.subTest(pointer=pointer):
                self.assertTrue(list(self.validator(path).iter_errors(mutate(POSITIVE[path], pointer, value))))
        path = 'artifact/publication-result.schema.json'
        for pointer, value in [('/render_attempts', 3), ('/commit_status', 'not_saved'),
                               ('/published', None), ('/operation', 'render_only')]:
            with self.subTest(pointer=pointer):
                self.assertTrue(list(self.validator(path).iter_errors(mutate(POSITIVE[path], pointer, value))))

    def test_every_reference_is_offline_and_resolvable(self):
        def visit(value):
            if isinstance(value, dict):
                if '$ref' in value:
                    reference = value['$ref']
                    self.assertTrue(reference.startswith(BASE))
                    self.registry.resolver().lookup(reference)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        for schema in SCHEMAS.values():
            visit(schema)

    def test_negative_fixtures_are_rejected(self):
        for case in FIXTURES['negative']:
            with self.subTest(case=case['name']):
                invalid = mutate(POSITIVE[case['schema']], case['pointer'], case['value'])
                self.assertTrue(list(self.validator(case['schema']).iter_errors(invalid)))

    def test_no_unrecognized_fields_on_any_top_level_contract(self):
        for path, value in POSITIVE.items():
            with self.subTest(schema=path):
                invalid = {**value, 'unrecognized_private_payload': 'SYNTHETIC_PRIVATE_CANARY'}
                self.assertTrue(list(self.validator(path).iter_errors(invalid)))

    def test_thirteen_cards_and_oversized_utf8_pack_are_rejected(self):
        path = 'retrieval/evidence-pack.schema.json'
        pack = copy.deepcopy(POSITIVE[path])
        pack['cards'] *= 13
        self.assertTrue(list(self.validator(path).iter_errors(pack)))
        pack['cards'] = copy.deepcopy(pack['cards'][:12])
        for entry in pack['cards']:
            entry['card']['description'] = 'я' * 1800
        errors = list(self.validator(path).iter_errors(pack))
        self.assertTrue(any('byte budget' in error.message for error in errors))

    def test_byte_budget_counts_utf8_and_inclusive_boundary(self):
        sample = {'value': 'я'}
        size = len(canonical(sample))
        self.assertGreater(size, len(canonical(sample).decode('utf-8')))
        self.validator_type({'x-max-utf8-bytes': size}).validate(sample)
        with self.assertRaises(ValidationError):
            self.validator_type({'x-max-utf8-bytes': size - 1}).validate(sample)

    def test_failure_without_manifest_and_early_interview_validate(self):
        state = no_result_state('retrieval_unavailable', 'index_missing')
        state['index_manifest'] = None
        for key in ('retrieval', 'evidence_pack', 'memo'):
            state[key]['pins'] = None
        self.validator('artifact/project-artifact-state.schema.json').validate(state)
        check_bundle(state)
        state = baseline()
        state['phase'] = 'intake'
        for key in ('brief', 'selection', 'request', 'index_manifest', 'retrieval', 'evidence_pack', 'memo'):
            state[key] = None
        state['intake'].update(status='asking', answers=[], questions_asked=1,
                               pending_question_id='goal', next_action='answer_question')
        self.validator('artifact/project-artifact-state.schema.json').validate(state)
        check_bundle(state)

    def test_ten_questions_then_correction_does_not_add_an_eleventh(self):
        state = baseline()
        answer = state['intake']['answers'][0]
        state['intake']['answers'] = []
        for index in range(10):
            item = copy.deepcopy(answer)
            item.update(answer_id=f'answer-{index}', question_id='question_' + chr(97 + index), ordinal=index + 1)
            state['intake']['answers'].append(item)
        state['intake']['questions_asked'] = 10
        self.validator('artifact/project-artifact-state.schema.json').validate(state)
        check_bundle(state)
        state['intake']['answers'][0]['answer_revision'] = 2
        state['intake']['answers'][0]['sanitized_value'] = 'Revised goal.'
        self.validator('artifact/project-artifact-state.schema.json').validate(state)
        check_bundle(state)

    def test_nullable_sparse_card_and_no_match_are_structurally_valid(self):
        card = sparse_card()
        self.validator('catalog/repository-card.schema.json').validate(card)
        state = no_result_state('no_match', 'no_hits')
        self.validator('artifact/project-artifact-state.schema.json').validate(state)
        check_bundle(state)


def baseline():
    return copy.deepcopy(POSITIVE['artifact/project-artifact-state.schema.json'])


def workspace_baseline():
    return copy.deepcopy(FIXTURES['workspace_positive']['artifact/project-artifact-state.schema.json'])


def sparse_card():
    card = copy.deepcopy(POSITIVE['catalog/repository-card.schema.json'])
    for field in ('description', 'language', 'license', 'requires_server', 'archived', 'adoption_mode', 'integration_surface'):
        card[field] = None
    for field in ('deployment', 'topics', 'use_cases', 'best_for', 'avoid_if', 'project_stages', 'compatibility', 'evidence'):
        card[field] = []
    card.update(availability='unknown', complexity='unknown', evidence_stage='baseline', missing_facts=['license', 'compatibility'])
    card['activity'] = {'schema_version': '1.0.0', **dict.fromkeys(ACTIVITY_FIELDS),
                        'lastCommitSha': None, 'lastCommitBranch': None, 'observations': []}
    return card


def no_result_state(status, reason):
    state = baseline()
    state['retrieval'].update(status=status, candidates=[], retrieved_hits=0, reason_codes=[reason])
    state['evidence_pack'].update(status='no_match' if status == 'no_match' else 'unavailable', cards=[], reason_codes=[reason])
    state['memo'].update(status='no_match' if status == 'no_match' else 'retrieval_unavailable', recommendations=[], integration_plan=None, reading_path=[])
    return state


class SemanticContracts(unittest.TestCase):
    def test_one_linked_context_to_integration_example(self):
        check_bundle(baseline())
        check_scan(POSITIVE['scanner/scan-report.schema.json'])
        self.assertEqual(FIXTURES['corpus_kind'], 'synthetic_fixture')

    def test_taxonomy_exact_source_parity_and_no_invented_hierarchy(self):
        manifest = load(TAXONOMY['source_ref'])
        self.assertEqual(TAXONOMY['source_sha256'], hashlib.sha256((ROOT / TAXONOMY['source_ref']).read_bytes()).hexdigest())
        self.assertEqual(TAXONOMY['source_snapshot'], manifest['snapshot'])
        self.assertEqual(TAXONOMY['categories'], [{'id': item['key'], 'label': item['title'], 'layer': item['layer'], 'parent_id': None, 'aliases': []} for item in manifest['categories']])
        unique([item['id'] for item in TAXONOMY['categories']], 'taxonomy identifier')

    def test_scan_exclusion_examples(self):
        for case in load('specs/scanner/exclusion-cases.json')['cases']:
            with self.subTest(path=case['path']):
                self.assertEqual(lexical_path(case['path']), (case['allowed'], case['reason']))

    def test_small_monorepo_and_incomplete_topology_are_not_empty(self):
        counts = copy.deepcopy(POSITIVE['scanner/scan-manifest.schema.json']['counters'])
        counts.update(eligible_files=0, topology_complete=False)
        self.assertEqual(classification(counts), 'large_or_monorepo')
        counts.update(eligible_files=3, topology_complete=True, service_roots=2)
        self.assertEqual(classification(counts), 'large_or_monorepo')
        counts.update(eligible_files=0, service_roots=0)
        self.assertEqual(classification(counts), 'idea_or_empty')
        counts.update(eligible_files=500, manifest_count=5, service_roots=1)
        self.assertEqual(classification(counts), 'compact')
        counts['eligible_files'] = 501
        self.assertEqual(classification(counts), 'standard')

    def test_quick_scan_cannot_use_deep_budget(self):
        report = copy.deepcopy(POSITIVE['scanner/scan-report.schema.json'])
        report['manifest']['counters']['file_attempts'] = 51
        with self.assertRaisesRegex(ValueError, 'scan mode budget'):
            check_scan(report)

    def test_unknowns_are_representable_without_invented_facts(self):
        check_card(sparse_card())
        card = sparse_card()
        card['license'] = 'NOASSERTION'
        with self.assertRaisesRegex(ValueError, 'license'):
            check_card(card)

    def test_nested_brief_bytes_cannot_hide_inside_larger_state(self):
        state = baseline()
        fact = state['brief']['observations']['facts'][0]
        state['brief']['observations']['facts'] = [
            {**fact, 'fact_id': f'fact-{index}', 'value': 'я' * 240} for index in range(40)]
        errors = list(byte_violations(SCHEMAS['artifact/project-artifact-state.schema.json'], state))
        self.assertIn(('/brief/observations', 16384), errors)
        with self.assertRaisesRegex(ValueError, 'nested serialized byte budget'):
            check_bundle(state)

    def test_machine_evidence_cannot_grant_catalog_acceptance(self):
        card = copy.deepcopy(POSITIVE['catalog/repository-card.schema.json'])
        card['catalog_status'] = 'accepted'
        with self.assertRaisesRegex(ValueError, 'acceptance provenance'):
            check_card(card)
        card['evidence'][0].update(source_kind='catalog_snapshot', source_ref='catalog:fixture-existing-acceptance')
        check_card(card)

    def test_canonical_card_must_match_frozen_card_bytes(self):
        card = POSITIVE['catalog/repository-card.schema.json']
        pins = POSITIVE['retrieval/index-manifest.schema.json']['pins']
        self.assertEqual(digest([card]), pins['cards_sha256'])
        changed = copy.deepcopy(card)
        changed['license'] = 'GPL-3.0-only'
        self.assertNotEqual(digest([changed]), pins['cards_sha256'])

    def test_old_activity_is_allowed_but_push_commit_conflation_is_not(self):
        card = copy.deepcopy(POSITIVE['catalog/repository-card.schema.json'])
        check_card(card)  # observations deliberately older than thirty days
        card['activity']['observations'][2]['source_field'] = 'repository_pushed_at'
        with self.assertRaisesRegex(ValueError, 'conflation'):
            check_card(card)

    def test_unknown_license_produces_useful_conditional_guidance(self):
        state = baseline()
        entry = state['evidence_pack']['cards'][0]
        entry['card']['license'] = None
        eligibility = entry['eligibility']
        eligibility.update(status='reference_only', reason_codes=['mandatory_fact_unknown'], required_verifications=['Verify the upstream license before adoption.'])
        eligibility['checks'][0]['outcome'] = 'unknown'
        state['memo']['status'] = 'conditional_guidance'
        state['memo']['recommendations'][0]['role'] = 'reference_only'
        check_bundle(state)
        state['memo']['recommendations'][0]['role'] = 'primary_candidate'
        with self.assertRaisesRegex(ValueError, 'primary candidate'):
            check_bundle(state)

    def test_eligibility_cannot_omit_mandatory_checks_or_invent_evidence(self):
        for pointer, replacement, message in [
            ('/evidence_pack/cards/0/eligibility/checks', [], 'coverage'),
            ('/evidence_pack/cards/0/card/license', None, 'unsupported license'),
            ('/evidence_pack/cards/0/eligibility/checks/0/evidence_refs', ['ev-invented'], 'unresolved eligibility'),
            ('/evidence_pack/cards/0/card/archived', True, 'unsupported archived'),
            ('/evidence_pack/cards/0/card/availability', 'unavailable', 'unsupported availability'),
        ]:
            with self.subTest(pointer=pointer), self.assertRaisesRegex(ValueError, message):
                check_bundle(mutate(baseline(), pointer, replacement))

    def test_pairing_trace_and_budget_failures(self):
        for pointer, replacement, message in [
            ('/retrieval/pins/index_sha256', 'f' * 64, 'index pairing'),
            ('/retrieval/query_sha256', 'f' * 64, 'query pairing'),
            ('/retrieval/brief_version', 2, 'stale brief'),
            ('/retrieval/candidates/0/rrf_score', 0.5, 'RRF score'),
            ('/evidence_pack/cards/0/retrieval_rank', 2, 'retrieval trace'),
            ('/evidence_pack/cards', [], 'candidate coverage'),
            ('/html_revision', 4, 'future HTML'),
            ('/memo/recommendations/0/evidence_refs', ['ev-invented'], 'recommendation evidence'),
            ('/brief/observations/facts/0/evidence_refs', ['ev-invented'], 'unresolved fact'),
            ('/selection/requested_sources/0/relative_path', '.env', 'excluded targeted'),
        ]:
            with self.subTest(pointer=pointer), self.assertRaisesRegex(ValueError, message):
                check_bundle(mutate(baseline(), pointer, replacement))

    def test_failure_and_no_match_are_distinct(self):
        for status, reasons in FAILURES.items():
            for reason in reasons:
                with self.subTest(status=status, reason=reason):
                    check_bundle(no_result_state(status, reason))
        state = no_result_state('no_match', 'fts5_unavailable')
        with self.assertRaisesRegex(ValueError, 'failure disguised'):
            check_bundle(state)

    def test_missing_manifest_does_not_require_fabricated_hashes(self):
        state = no_result_state('retrieval_unavailable', 'index_missing')
        state['index_manifest'] = None
        for key in ('retrieval', 'evidence_pack', 'memo'):
            state[key]['pins'] = None
        check_bundle(state)
        state['retrieval']['status'] = 'no_match'
        with self.assertRaisesRegex(ValueError, 'missing index pins'):
            check_bundle(state)

    def test_sixty_hits_include_duplicate_variant_matches(self):
        state = baseline()
        query, result = state['request']['query'], state['retrieval']
        result['candidates'] = []
        result['retrieved_hits'] = 60
        for rank in range(1, 31):
            result['candidates'].append({'repo_id': f'gh-pending:fixture/r{rank:02d}', 'rank': rank,
                'rrf_score': 2 / (60 + rank), 'variant_ranks': [
                    {'variant_id': 'q1', 'rank': rank, 'bm25': -1.0},
                    {'variant_id': 'q2', 'rank': rank, 'bm25': -0.1}],
                'matched_fields': ['description'], 'missing_facts': []})
        check_retrieval(result, query, state['index_manifest'])
        result['retrieved_hits'] = 59
        with self.assertRaisesRegex(ValueError, 'hit accounting'):
            check_retrieval(result, query, state['index_manifest'])

    def test_pack_obeys_smaller_request_budget(self):
        state = baseline()
        query = state['request']['query']
        query['max_evidence_bytes'] = 1024
        for key in ('retrieval', 'evidence_pack'):
            state[key]['query_sha256'] = digest(query)
        with self.assertRaisesRegex(ValueError, 'evidence budget'):
            check_bundle(state)

    def test_correction_invalidates_outputs_without_changing_observed_facts(self):
        before, after = baseline(), baseline()
        after['revision'] = 4
        after['brief']['brief_version'] = 2
        after['brief']['goal'] = 'Compare the alternatives first.'
        after['corrections'] = [copy.deepcopy(POSITIVE['context/user-corrections.schema.json'])]
        after['brief']['user_corrections'] = ['correction-1']
        for key in ('selection', 'request', 'retrieval', 'evidence_pack', 'memo'):
            after[key] = None
        after['phase'] = 'context_review'
        check_transition(before, after, expected_revision=3)
        stale = copy.deepcopy(after)
        stale['retrieval'] = before['retrieval']
        with self.assertRaisesRegex(ValueError, 'invalidate'):
            check_transition(before, stale, expected_revision=3)
        with self.assertRaisesRegex(ValueError, 'revision conflict'):
            check_transition(before, after, expected_revision=2)
        before['status'] = 'finalized'
        with self.assertRaisesRegex(ValueError, 'immutable finalized'):
            check_transition(before, after, expected_revision=3)

    def test_storage_caps_and_input_allocation_are_explicit(self):
        storage = SCHEMAS['artifact/project-artifact-state.schema.json']['$defs']['storagePolicy']['const']
        self.assertEqual(storage['max_state_bytes'], 2 * 1024 * 1024)
        self.assertEqual(storage['max_finalized_runs'], 100)
        self.assertEqual(storage['max_total_bytes'], 256 * 1024 * 1024)
        self.assertFalse(storage['auto_delete'])
        self.assertFalse(storage['overwrite_unrecognized_files'])
        allocation = POSITIVE['recommendation/recommendation-request.schema.json']['input_allocation']
        self.assertEqual(sum(value for key, value in allocation.items() if key != 'plugin_input_bytes'), allocation['plugin_input_bytes'])
        self.assertEqual(allocation['plugin_input_bytes'], POLICY['limits']['max_plugin_input_bytes'])
        self.assertIsNone(POLICY['snapshot_max_age_days'])
        self.assertEqual(POLICY['calibration_status'], 'unmeasured_initial_policy')


class WorkspaceSemanticContracts(unittest.TestCase):
    def test_technology_literals_are_bounded_and_include_typed_facts(self):
        state = {'brief': {'constraints': {'languages': ['Go', 'C']},
                           'observations': {'facts': [{'kind': 'framework', 'value': 'FastAPI'}]}}}
        self.assertEqual(field_literals(state, 'Goal: Compare alternatives.'), [])
        self.assertEqual(field_literals(state, 'Use Go with a C library and FastAPI.'), ['C', 'FastAPI', 'Go'])
        self.assertEqual(field_literals(state, 'Keep `C++` exactly.'), ['C++'])

    def test_user_answer_is_not_observed_project_evidence(self):
        evidence = {'ev-answer': {'kind': 'user_answer', 'relative_path': None, 'answer_id': 'answer-goal-1'}}
        claim = dict(text='Synthetic observation claim.',kind='observed',evidence_refs=['ev-answer'],
                     answer_ids=[],limitation=None)
        with self.assertRaisesRegex(ValueError, 'project/source evidence'):
            check_claim(claim, evidence, {'answer-goal-1'})
        state = workspace_baseline()
        summary = state['brief']['observations']
        entry = dict(evidence_id='ev-answer',kind='user_answer',relative_path=None,line_start=None,line_end=None,
                     answer_id='answer-goal-1',content_persisted=False)
        summary['evidence'].append(entry)
        state['memo']['integration_plan']['details']['diagram'] = {
            'status':'proposed','nodes':[dict(component_id='existing',label='Existing component',change='reuse',
                                            evidence_refs=['ev-answer'])],'edges':[]}
        with self.assertRaisesRegex(ValueError, 'reused node'):
            check_bundle(state)

    def test_linked_workspace_keeps_canonical_retrieval_and_partial_translation(self):
        state = workspace_baseline()
        check_bundle(state)
        self.assertEqual(state['retrieval'], baseline()['retrieval'])
        self.assertEqual(state['evidence_pack'], baseline()['evidence_pack'])
        self.assertEqual(state['presentation']['coverage']['ru']['required_fields'], 45)
        self.assertEqual(state['presentation']['coverage']['ru']['available_fields'], 2)
        self.assertEqual(state['presentation']['coverage']['en']['status'], 'partial')

    def test_zero_question_no_brief_no_memo_and_scan_before_brief(self):
        state = workspace_baseline()
        for key in ('brief', 'selection', 'request', 'index_manifest', 'retrieval', 'evidence_pack', 'memo', 'scan'):
            state[key] = None
        state.update(phase='intake', revision=1, content_revision=1, html_revision=None)
        state['intake'].update(status='asking', questions_asked=0, answers=[], questions=[],
                                pending_question_id=None, completion_reason=None, next_action='answer_question')
        rebind_presentation(state)
        check_bundle(state)
        self.assertEqual(state['presentation']['coverage']['ru'],
                         {'status':'complete', 'required_fields':0, 'available_fields':0})
        state['scan'] = copy.deepcopy(POSITIVE['scanner/scan-report.schema.json'])
        rebind_presentation(state)
        check_bundle(state)
        self.assertGreater(state['presentation']['coverage']['ru']['required_fields'], 0)

    def test_question_ledger_missing_duplicate_and_wrong_ordinal(self):
        for pointer, value in [('/intake/questions', []), ('/intake/questions/0/ordinal', 2),
                               ('/intake/questions/0/question_id', 'different'), ('/intake/completion_reason', None)]:
            with self.subTest(pointer=pointer), self.assertRaises(ValueError):
                check_bundle(mutate(workspace_baseline(), pointer, value))

    def test_claim_saved_answer_and_scan_provenance(self):
        for pointer, value in [('/brief/details/problem/answer_ids', ['invented']),
                               ('/intake/answers/0/status', 'skipped'),
                               ('/brief/details/problem/kind', 'observed'),
                               ('/scan/summary/evidence/0/relative_path', 'README.md'),
                               ('/brief/observations/facts/0/value', 'Contradictory observed fact.')]:
            with self.subTest(pointer=pointer), self.assertRaises(ValueError):
                check_bundle(mutate(workspace_baseline(), pointer, value))

    def test_stale_revision_hash_id_unresolved_pointer_and_forged_coverage(self):
        for pointer, value in [('/presentation/source_content_revision', 2),
                               ('/presentation/brief_version', 2), ('/presentation/memo_id', 'memo-other'),
                               ('/presentation/fields/0/source_sha256', 'f' * 64),
                               ('/presentation/fields/0/source_content_revision', 2),
                               ('/presentation/fields/0/field_pointer', '/memo/recommendations/99/fit_rationale'),
                               ('/presentation/coverage/ru/status', 'complete'),
                               ('/presentation/coverage/en/required_fields', 2),
                               ('/presentation/fields/1/evidence_refs', []),
                               ('/presentation/fields/1/canonical_literals', []),
                               ('/presentation/fields/1/ru/text', 'Локальная интеграция без названия технологии.'),
                               ('/presentation/fields/1/en/text', 'Different original statement.')]:
            with self.subTest(pointer=pointer), self.assertRaises(ValueError):
                check_bundle(mutate(workspace_baseline(), pointer, value))
        state = workspace_baseline()
        state['brief']['goal'] = 'A different goal with the same Brief identity.'
        with self.assertRaisesRegex(ValueError, 'stale localized source'):
            check_bundle(state)

    def test_locale_only_and_translation_only_saves_do_not_invalidate_result(self):
        before = workspace_baseline()
        after = copy.deepcopy(before)
        after['revision'] += 1
        after['presentation']['default_locale'] = 'en'
        check_transition(before, after, before['revision'])
        self.assertEqual(after['content_revision'], before['content_revision'])
        self.assertEqual(after['retrieval'], before['retrieval'])
        self.assertEqual(after['presentation']['presentation_revision'], before['presentation']['presentation_revision'])
        after = copy.deepcopy(before)
        after['revision'] += 1
        after['presentation']['presentation_revision'] += 1
        after['presentation']['fields'][0]['ru'] = {'status':'missing', 'text':None}
        rebind_presentation(after)
        check_transition(before, after, before['revision'])
        self.assertEqual(after['presentation']['coverage']['ru']['available_fields'], 1)
        self.assertEqual(after['memo'], before['memo'])

    def test_semantic_correction_invalidates_and_cannot_be_locale_change(self):
        before, after = workspace_baseline(), workspace_baseline()
        after['revision'] += 1
        after['content_revision'] += 1
        after['brief']['brief_version'] += 1
        after['brief']['goal'] = 'Compare local alternatives before implementation.'
        after['corrections'] = [copy.deepcopy(POSITIVE['context/user-corrections.schema.json'])]
        after['brief']['user_corrections'] = ['correction-1']
        for key in ('selection', 'request', 'retrieval', 'evidence_pack', 'memo'):
            after[key] = None
        after['phase'] = 'context_review'
        after['presentation']['presentation_revision'] += 1
        rebind_presentation(after)
        check_transition(before, after, before['revision'])
        self.assertEqual(after['scan'], before['scan'])
        bad = copy.deepcopy(after)
        bad['retrieval'] = before['retrieval']
        with self.assertRaisesRegex(ValueError, 'invalidate'):
            check_transition(before, bad, before['revision'])
        bad = copy.deepcopy(before)
        bad['revision'] += 1
        bad['brief']['details']['target_user']['limitation'] = 'Changed audience interpretation.'
        with self.assertRaisesRegex(ValueError, 'content revision'):
            check_transition(before, bad, before['revision'])

    def test_finalized_runs_reject_locale_translation_and_html_revision_writes(self):
        before = workspace_baseline()
        before['status'] = 'finalized'
        for mutation in ('locale', 'translation', 'html_revision'):
            after = copy.deepcopy(before)
            after['revision'] += 1
            if mutation == 'locale':
                after['presentation']['default_locale'] = 'en'
            elif mutation == 'translation':
                after['presentation']['fields'][0]['ru']['text'] = 'Изменённый перевод.'
            else:
                after['html_revision'] = after['revision']
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'immutable finalized'):
                check_transition(before, after, before['revision'])

    def test_nested_workspace_brief_byte_limit_not_hidden_by_state(self):
        state = workspace_baseline()
        details = state['brief']['details']
        details['non_goals'] = [dict(text='я' * 700, kind='user_statement', evidence_refs=[],
                                   answer_ids=['answer-goal-1'], limitation='Synthetic byte-boundary example.')
                                for _ in range(12)]
        self.assertLess(len(canonical(state)), 2 * 1024 * 1024)
        self.assertGreater(len(canonical(state['brief'])), 16384)
        self.assertIn(('/brief', 16384), list(byte_violations(SCHEMAS['artifact/project-artifact-state.schema.json'], state)))
        with self.assertRaisesRegex(ValueError, 'nested serialized byte budget'):
            check_bundle(state)

    def test_integration_dependency_and_known_authorization_require_sources(self):
        state = workspace_baseline()
        deps = state['memo']['integration_plan']['details']['step_dependencies'][0]
        deps['depends_on'] = [deps['step_id']]
        with self.assertRaisesRegex(ValueError, 'cyclic'):
            check_bundle(state)
        state = workspace_baseline()
        state['memo']['integration_plan']['details']['step_dependencies'][0]['safe_paths'] = ['src/app.py']
        with self.assertRaisesRegex(ValueError, 'step path'):
            check_bundle(state)
        state = workspace_baseline()
        state['memo']['integration_plan']['details']['prerequisite_checks'] = [
            dict(check_id='auth-1',kind='authorization',detail='Synthetic asserted permission',
                 status='already_authorized',evidence_refs=[],answer_ids=[],next_check=None)]
        with self.assertRaisesRegex(ValueError, 'provenance'):
            check_bundle(state)

    def test_publication_current_requires_state_and_exact_fixture_bytes(self):
        state = workspace_baseline()
        receipt = copy.deepcopy(POSITIVE['artifact/publication-result.schema.json'])
        html = FIXTURES['publication_html_fixture'].encode('utf-8')
        check_publication(receipt, state, html)
        for pointer, value in [('/published/revision', state['revision']-1),
                               ('/published/run_id','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'),
                               ('/published/presentation_revision',2), ('/published/html_sha256','f'*64),
                               ('/saved/content_revision',2)]:
            with self.subTest(pointer=pointer), self.assertRaises(ValueError):
                check_publication(mutate(receipt,pointer,value), state, html)
        with self.assertRaisesRegex(ValueError, 'byte hash'):
            check_publication(receipt, state, html+b'changed')

    def test_first_render_failure_stale_prior_run_and_bounded_retry(self):
        state = workspace_baseline()
        receipt = copy.deepcopy(POSITIVE['artifact/publication-result.schema.json'])
        receipt.update(publication_status='unavailable',published=None,failure_reason='render_failed',retry='render_only')
        check_publication(receipt,state)
        receipt.update(publication_status='stale',published=copy.deepcopy(POSITIVE['artifact/publication-result.schema.json']['published']))
        receipt['published']['run_id'] = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
        check_publication(receipt,state)
        receipt['render_attempts']=2
        with self.assertRaisesRegex(ValueError,'retry scope'):
            check_publication(receipt,state)
        receipt['retry']='stop'
        check_publication(receipt,state)

    def test_late_render_and_commit_failure_preserve_saved_target(self):
        state = workspace_baseline()
        receipt = copy.deepcopy(POSITIVE['artifact/publication-result.schema.json'])
        receipt['saved']['revision'] -= 1
        receipt.update(publication_status='superseded',failure_reason='render_superseded',retry='stop')
        check_publication(receipt,state)
        receipt['saved'] = copy.deepcopy(receipt['current'])
        with self.assertRaisesRegex(ValueError,'superseded target'):
            check_publication(receipt,state)
        receipt.update(commit_status='not_saved',saved=None,publication_status='not_attempted',
                       failure_reason='state_write_failed',render_attempts=0,retry='stop')
        check_publication(receipt,state)
        receipt['saved'] = copy.deepcopy(receipt['current'])
        with self.assertRaisesRegex(ValueError,'saved state requires|failed commit'):
            check_publication(receipt,state)

    def test_saved_cannot_skip_publication_or_hide_supersession(self):
        state = workspace_baseline()
        receipt = copy.deepcopy(POSITIVE['artifact/publication-result.schema.json'])
        receipt.update(publication_status='not_attempted',published=None,render_attempts=0)
        with self.assertRaisesRegex(ValueError, 'requires publication'):
            check_publication(receipt,state)
        receipt.update(publication_status='unavailable',render_attempts=1,failure_reason='render_failed',retry='stop')
        receipt['saved']['revision'] -= 1
        with self.assertRaisesRegex(ValueError, 'superseded'):
            check_publication(receipt,state)


if __name__ == '__main__':
    unittest.main()
