"""Offline C8/C9 compatibility and retrieval-metric scorer; never executes retrieval.

jsonschema/referencing are development-only dependencies, not plugin dependencies.
Schemas and their references are loaded exclusively from the local repository.
"""

import argparse
import hashlib
import json
import math
import sys
import uuid
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://myai-stackguide.invalid/contracts/v1/'
MAX_INPUT_BYTES = 2 * 1024 * 1024
FAILURES = {
    'no_match': {'no_hits'},
    'retrieval_unavailable': {'fts5_unavailable', 'index_missing', 'index_corrupt'},
    'index_incompatible': {'index_incompatible'},
    'invalid_query': {'invalid_query'},
    'cancelled': {'cancelled'},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_json(path):
    """Bounded strict JSON; reject duplicate keys and nonfinite numbers."""
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError('nonfinite JSON number')

    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    require(len(raw) <= MAX_INPUT_BYTES, 'input byte limit')
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                       parse_constant=nonfinite)
    canonical(value)  # Also rejects float overflow, for example 1e999.
    return value


class Contracts:
    """Standards validation plus declared UTF-8 byte limits; no network resolver."""

    def __init__(self):
        try:
            from jsonschema import Draft202012Validator, FormatChecker, ValidationError, validators
            from referencing import Registry, Resource
        except ImportError as exc:
            raise RuntimeError('Development-only jsonschema/referencing is required; '
                               'missing validation is not a passing gate.') from exc

        files = sorted((ROOT / 'specs').rglob('*.schema.json'))
        files += [ROOT / 'evals/scenario.schema.json', ROOT / 'evals/result.schema.json']
        self.schemas = {}
        for path in files:
            schema = load_json(path)
            Draft202012Validator.check_schema(schema)
            require(schema['$id'] not in self.schemas, 'duplicate schema identity')
            self.schemas[schema['$id']] = schema
        self.schema_set_sha256 = digest({str(path.relative_to(ROOT)).replace('\\', '/'):
                                         hashlib.sha256(path.read_bytes()).hexdigest()
                                         for path in files})
        self.registry = Registry().with_resources(
            (name, Resource.from_contents(schema)) for name, schema in self.schemas.items())

        def check_refs(value):
            if isinstance(value, dict):
                if '$ref' in value:
                    ref = value['$ref']
                    require(ref.startswith(BASE), 'unapproved schema reference')
                    try:
                        self.registry.resolver().lookup(ref)
                    except Exception as exc:
                        raise ValueError('unresolved offline schema reference') from exc
                for child in value.values():
                    check_refs(child)
            elif isinstance(value, list):
                for child in value:
                    check_refs(child)

        for schema in self.schemas.values():
            check_refs(schema)

        def byte_limit(validator, limit, instance, schema):
            if len(canonical(instance)) > limit:
                yield ValidationError('compact UTF-8 byte budget exceeded')

        validator_type = validators.extend(Draft202012Validator, {'x-max-utf8-bytes': byte_limit})
        checker = FormatChecker()

        @checker.checks('date-time', raises=ValueError)
        def utc_timestamp(value):
            return not isinstance(value, str) or (value.endswith('Z') and
                   datetime.fromisoformat(value.replace('Z', '+00:00')) is not None)

        @checker.checks('date', raises=ValueError)
        def iso_date(value):
            return not isinstance(value, str) or date.fromisoformat(value) is not None

        @checker.checks('uuid', raises=ValueError)
        def canonical_uuid(value):
            return not isinstance(value, str) or str(uuid.UUID(value)) == value

        self.validators = {name: validator_type(schema, registry=self.registry,
                                                format_checker=checker)
                           for name, schema in self.schemas.items()}
        self.validator_type = validator_type
        self.standard_validator_type = Draft202012Validator
        self.checker = checker

    def check_bytes(self, schema, value, seen=None):
        """Walk applicable branches explicitly: $schema may reset an extended validator."""
        seen = set() if seen is None else seen
        if not isinstance(schema, dict) or (id(schema), id(value)) in seen:
            return
        seen.add((id(schema), id(value)))
        if 'x-max-utf8-bytes' in schema:
            require(len(canonical(value)) <= schema['x-max-utf8-bytes'], 'nested compact UTF-8 byte budget')
        if '$ref' in schema:
            self.check_bytes(self.registry.resolver().lookup(schema['$ref']).contents, value, seen)
        if isinstance(value, dict):
            for name, child in schema.get('properties', {}).items():
                if name in value:
                    self.check_bytes(child, value[name], seen)
        if isinstance(value, list) and 'items' in schema:
            for child in value:
                self.check_bytes(schema['items'], child, seen)
        for child in schema.get('allOf', []):
            self.check_bytes(child, value, seen)
        for keyword in ('anyOf', 'oneOf'):
            for child in schema.get(keyword, []):
                validator = self.standard_validator_type(child, registry=self.registry, format_checker=self.checker)
                if validator.is_valid(value):
                    self.check_bytes(child, value, seen)
        if 'if' in schema:
            validator = self.standard_validator_type(schema['if'], registry=self.registry, format_checker=self.checker)
            keyword = 'then' if validator.is_valid(value) else 'else'
            if keyword in schema:
                self.check_bytes(schema[keyword], value, seen)

    def validate(self, relative, value):
        canonical(value)
        try:
            self.validators[BASE + relative].validate(value)
        except Exception as exc:
            # Do not echo untrusted or confidential payload values in CLI errors.
            raise ValueError('schema validation failed: ' + relative) from exc
        self.check_bytes(self.schemas[BASE + relative], value)


def unique(values, label):
    require(len(values) == len(set(values)), 'duplicate ' + label)


def validate_cases(cases, contracts):
    contracts.validate('evals/scenario.schema.json', cases)
    require(cases['contract_set_sha256'] == contracts.schema_set_sha256, 'stale contract set')
    unique([case['case_id'] for case in cases['cases']], 'case ID')
    unique([case['case_id'] for case in cases['presentation_cases']], 'presentation case ID')
    require({case['canonical_case_id'] for case in cases['presentation_cases']} <=
            {case['case_id'] for case in cases['cases']}, 'unknown canonical presentation case')
    policy_hash = hashlib.sha256((ROOT / 'specs/retrieval/retrieval-policy.json').read_bytes()).hexdigest()
    taxonomy_hash = hashlib.sha256((ROOT / 'specs/catalog/taxonomy.yaml').read_bytes()).hexdigest()
    for case in cases['cases']:
        query, manifest = case['query'], case['index_manifest']
        require(query['policy_sha256'] == policy_hash, 'query policy pin')
        require(query['max_cards'] <= query['max_candidates'], 'card/candidate budget')
        unique([variant['variant_id'] for variant in query['variants']], 'query variant')
        require(all(term.strip() for variant in query['variants'] for term in variant['terms']),
                'empty literal term')
        constraints = query['constraints']
        for field, target in [('license', 'allowed_licenses'), ('language', 'languages'),
                              ('deployment', 'deployment'), ('compatibility', 'compatibility')]:
            require(field not in constraints['mandatory_fields'] or bool(constraints[target]),
                    'missing mandatory constraint target')
        require('no_server' not in constraints['mandatory_fields'] or
                constraints['require_no_server'] is True, 'missing mandatory no-server target')
        if manifest is None:
            require(case['expected_status'] not in ('ok', 'no_match'), 'missing manifest success')
        else:
            require(manifest['pins']['policy_sha256'] == policy_hash and
                    manifest['pins']['taxonomy_sha256'] == taxonomy_hash, 'manifest policy/taxonomy pin')
        unique([item['repo_id'] for item in case['judgments']], 'judgment ID')
        require(case['judgment_provenance'] == 'independent_synthetic_known_answer',
                'unreviewed relevance provenance')
    return cases


def validate_card_eligibility(entry, query):
    """Verify C9 public-card provenance and constraint trace before scoring judgments."""
    card, eligibility = entry['card'], entry['eligibility']
    require(card['url'] == 'https://github.com/' + card['full_name'], 'card URL identity')
    require(card['repo_id'] not in card['aliases'], 'card self alias')
    unique(card['aliases'], 'card alias')
    taxonomy = load_json(ROOT / 'specs/catalog/taxonomy.yaml')
    categories = {item['id'] for item in taxonomy['categories']}
    require(card['primary_category'] in categories and set(card['secondary_categories']) <= categories,
            'unknown category')
    require(card['primary_category'] not in card['secondary_categories'], 'repeated primary category')
    require(card['license'] not in ('NOASSERTION', 'unknown', ''), 'unknown license must be null')
    evidence = {item['evidence_id']: item for item in card['evidence']}
    require(len(evidence) == len(card['evidence']), 'duplicate public evidence')
    if card['catalog_status'] == 'accepted':
        source = 'curator_record' if card['catalog_status_source'] == 'curator_decision' else 'catalog_snapshot'
        require(any(item['source_kind'] == source and '/catalog_status' in item['fields']
                    for item in evidence.values()), 'unsupported catalog acceptance')
    if card['corpus_kind'] != 'synthetic_fixture':
        require(all(item['source_kind'] != 'synthetic_fixture' and
                    not item['source_ref'].startswith('fixture:') for item in evidence.values()),
                'synthetic evidence mislabeled')
    activity_fields = {'createdAt': 'repository_created_at', 'pushedAt': 'repository_pushed_at',
                       'lastCommitAt': 'commit_committed_date', 'lastReleaseAt': 'release_published_at'}
    activity = card['activity']
    unique([item['field'] for item in activity['observations']], 'activity observation')
    require({item['field'] for item in activity['observations']} ==
            {field for field in activity_fields if activity[field] is not None}, 'activity observation coverage')
    for observation in activity['observations']:
        field, ref = observation['field'], observation['evidence_ref']
        require(observation['source_field'] == activity_fields[field], 'activity event conflation')
        require(ref in evidence and '/activity/' + field in evidence[ref]['fields'] and
                evidence[ref]['observed_at'] == observation['observedAt'], 'activity evidence mismatch')
    require(eligibility['repo_id'] == card['repo_id'] and eligibility['query_id'] == query['query_id'],
            'eligibility identity mismatch')
    constraints = query['constraints']
    checks = {item['field']: item for item in eligibility['checks']}
    expected_fields = set(constraints['mandatory_fields']) | {'availability', 'archived', 'advisory_evidence'}
    require(len(checks) == len(eligibility['checks']) and set(checks) == expected_fields,
            'eligibility check coverage')
    advisory = ['use_cases', 'best_for', 'adoption_mode', 'project_stages', 'complexity',
                'integration_surface', 'compatibility']
    outcomes = []
    for field, check in checks.items():
        pointers = advisory if field == 'advisory_evidence' else [{'no_server': 'requires_server'}.get(field, field)]
        refs = check['evidence_refs']
        require(set(refs) <= evidence.keys(), 'unresolved eligibility evidence')
        sourced = all(any('/' + pointer in evidence[ref]['fields'] and
                         evidence[ref]['verification'] != 'unknown' for ref in refs) for pointer in pointers)
        known = all(card[pointer] is not None and card[pointer] != [] and card[pointer] != 'unknown'
                    for pointer in pointers)
        if not sourced or not known:
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
        require(check['outcome'] == outcome, 'unsupported eligibility ' + field)
        outcomes.append(outcome)
    expected = 'blocked' if 'fail' in outcomes else 'reference_only' if 'unknown' in outcomes else 'primary_eligible'
    require(eligibility['status'] == expected, 'eligibility status contradiction')
    if expected == 'reference_only':
        require('mandatory_fact_unknown' in eligibility['reason_codes'] and eligibility['required_verifications'],
                'missing conditional verification')


def validate_capture(case, capture, contracts):
    """Cross-object invariants supplement, and do not replace, JSON Schema."""
    query, manifest = case['query'], case['index_manifest']
    policy = load_json(ROOT / 'specs/retrieval/retrieval-policy.json')
    result, pack = capture['retrieval'], capture['evidence_pack']
    expected_pins = manifest['pins'] if manifest is not None else None
    for item in (result, pack):
        require(item['run_id'] == case['run_id'], 'run ID mismatch')
        require(item['query_id'] == query['query_id'] and item['query_sha256'] == digest(query),
                'query identity/digest mismatch')
        require(item['brief_version'] == query['brief_version'], 'brief revision mismatch')
        require(item['pins'] == expected_pins, 'index pins mismatch')
    require(result['source_mode'] == query['source_mode'] and
            result['retrieval_engine'] == query['retrieval_engine'], 'route mismatch')
    if manifest is None:
        require(result['status'] not in ('ok', 'no_match'), 'missing index disguised as success')
    expected_pack_status = ('ready' if result['status'] == 'ok' and pack['cards'] else
                            'no_match' if result['status'] in ('ok', 'no_match') else 'unavailable')
    require(pack['status'] == expected_pack_status, 'retrieval/pack status mismatch')
    candidates = result['candidates']
    ids = [item['repo_id'] for item in candidates]
    unique(ids, 'candidate ID')
    require([item['rank'] for item in candidates] == list(range(1, len(candidates) + 1)),
            'noncontiguous candidate ranks')
    require(candidates == sorted(candidates, key=lambda item: (-item['rrf_score'], item['repo_id'])),
            'RRF ordering mismatch')
    require(result['retrieved_hits'] <= query['max_candidates'], 'aggregate hit budget')
    require(result['executed_variants'] <= len(query['variants']), 'variant cardinality')
    executed = {item['variant_id'] for item in query['variants'][:result['executed_variants']]}
    positions = set()
    for item in candidates:
        ranks = item['variant_ranks']
        unique([rank['variant_id'] for rank in ranks], 'candidate variant')
        require({rank['variant_id'] for rank in ranks} <= executed, 'unexecuted variant')
        require(math.isclose(item['rrf_score'], sum(1 / (policy['rank_fusion']['k'] + rank['rank']) for rank in ranks),
                             rel_tol=1e-12), 'RRF score mismatch')
        for rank in ranks:
            position = (rank['variant_id'], rank['rank'])
            require(position not in positions and rank['rank'] <= result['retrieved_hits'],
                    'duplicate/out-of-range variant rank')
            positions.add(position)
    require(len(positions) <= result['retrieved_hits'], 'hit accounting mismatch')
    if result['status'] != 'ok':
        require(set(result['reason_codes']) <= FAILURES[result['status']] and result['reason_codes'],
                'failure disguised as no-match')
        require(pack['reason_codes'] == result['reason_codes'], 'failure reason mismatch')
        if result['status'] == 'no_match':
            require(result['retrieved_hits'] == 0 and result['executed_variants'] > 0,
                    'unexecuted no-match')
    elif result['truncated']:
        require('candidate_budget' in result['reason_codes'], 'missing truncation reason')
    card_ids = [item['card']['repo_id'] for item in pack['cards']]
    excluded = [item['repo_id'] for item in pack['exclusions']]
    unique(card_ids, 'pack card')
    unique(excluded, 'excluded ID')
    require(not set(card_ids) & set(excluded), 'included and excluded candidate')
    require(set(card_ids) | set(excluded) == set(ids), 'candidate pack coverage mismatch')
    require(len(card_ids) <= query['max_cards'], 'pack card budget')
    require(len(canonical(pack)) <= query['max_evidence_bytes'], 'requested evidence byte budget')
    candidates_by_id = {item['repo_id']: item for item in candidates}
    aliases = []
    for item in pack['cards']:
        validate_card_eligibility(item, query)
        aliases.extend([item['card']['repo_id'], *item['card']['aliases']])
        candidate = candidates_by_id[item['card']['repo_id']]
        require(item['retrieval_rank'] == candidate['rank'] and item['rrf_score'] == candidate['rrf_score'] and
                item['matched_fields'] == candidate['matched_fields'], 'card retrieval trace mismatch')
        require(item['eligibility']['repo_id'] == item['card']['repo_id'] and
                item['eligibility']['query_id'] == query['query_id'], 'eligibility identity mismatch')
        require(item['eligibility']['status'] != 'blocked', 'blocked card in evidence pack')
        require(item['card']['corpus_kind'] == expected_pins['corpus_kind'], 'corpus kind mismatch')
    unique(aliases, 'canonical alias across pack')
    measures = capture['measurements']
    require(measures['evidence_pack_bytes'] == len(canonical(pack)), 'measured evidence bytes mismatch')
    limits = policy['limits']
    allocations = ['brief_bytes', 'targeted_context_bytes', 'evidence_pack_bytes', 'request_bytes']
    for key in allocations:
        limit = limits['max_evidence_bytes' if key == 'evidence_pack_bytes' else 'max_' + key]
        require(measures[key] is None or measures[key] <= limit, 'measured input budget')
    values = [measures[key] for key in allocations]
    if all(value is not None for value in values):
        require(measures['plugin_input_bytes'] == sum(values), 'controlled input byte sum')
        require(sum(values) <= limits['max_plugin_input_bytes'], 'controlled input budget')
    else:
        require(measures['plugin_input_bytes'] is None, 'unknown input reported as measured')
    for value_key, method_key in [('latency_ms', 'latency_method'), ('peak_memory_bytes', 'memory_method'),
                                   ('input_tokens', 'tokenizer')]:
        require((measures[value_key] is None) == (measures[method_key] is None), 'measurement method missing')


def ranking_metrics(ranked_ids, judgments, k):
    """Recall uses all grade>0 judgments; nDCG uses gain=2**grade-1/log2(rank+1)."""
    unique(ranked_ids, 'metric candidate')
    require(type(k) is int and 1 <= k <= 60, 'invalid metric k')
    require(all(type(grade) is int and 0 <= grade <= 3 for grade in judgments.values()),
            'invalid relevance grade')
    require(set(ranked_ids) <= judgments.keys(), 'unjudged candidate; do not assume irrelevant')
    relevant = {repo_id for repo_id, grade in judgments.items() if grade > 0}
    selected = ranked_ids[:k]
    dcg = sum((2 ** judgments[repo_id] - 1) / math.log2(rank + 2)
              for rank, repo_id in enumerate(selected))
    ideal = sum((2 ** grade - 1) / math.log2(rank + 2)
                for rank, grade in enumerate(sorted(judgments.values(), reverse=True)[:k]))
    return {'recall_at_k': len(set(selected) & relevant) / len(relevant) if relevant else None,
            'ndcg_at_k': dcg / ideal if ideal else None,
            'relevant_count': len(relevant)}


def evaluate(cases, captures, contracts=None):
    contracts = contracts or Contracts()
    validate_cases(cases, contracts)
    contracts.validate('evals/result.schema.json', captures)
    require(captures['case_set_sha256'] == digest(cases), 'case-set digest mismatch')
    ids = [item['case_id'] for item in captures['records']]
    unique(ids, 'capture case ID')
    require(set(ids) == {case['case_id'] for case in cases['cases']}, 'capture case cardinality')
    captured = {item['case_id']: item for item in captures['records']}
    records = []
    for case in cases['cases']:
        capture = captured[case['case_id']]
        validate_capture(case, capture, contracts)
        result, pack = capture['retrieval'], capture['evidence_pack']
        expected = {item['repo_id']: item for item in case['judgments']}
        ranked_ids = [item['repo_id'] for item in result['candidates']]
        require(set(ranked_ids) <= expected.keys(), 'unjudged candidate')
        status_ok = result['status'] == case['expected_status']
        eligible = {repo_id for repo_id, item in expected.items() if item['constraint'] == 'allowed'}
        denied = {repo_id for repo_id, item in expected.items() if item['constraint'] == 'denied'}
        selected = {item['card']['repo_id'] for item in pack['cards']}
        excluded = {item['repo_id'] for item in pack['exclusions']
                    if set(item['reason_codes']) & {'constraint_mismatch', 'mandatory_fact_unknown', 'archived', 'unavailable'}}
        violations = len(selected & denied)
        false_exclusions = len(excluded & eligible)
        metrics = ranking_metrics(ranked_ids, {key: item['grade'] for key, item in expected.items()}, case['k']) \
            if result['status'] in ('ok', 'no_match') else None
        records.append({'case_id': case['case_id'], 'status_match': status_ok, 'ranking': metrics,
                        'hard_constraint_violations': violations, 'false_exclusions': false_exclusions,
                        'candidate_count': len(ranked_ids), 'pack_card_count': len(selected),
                        'evidence_pack_bytes': len(canonical(pack)),
                        'compatible': status_ok and violations == 0 and false_exclusions == 0})
    return {'schema_version': 'retrieval_score_v1', 'evidence_kind': captures['evidence_kind'],
            'verdict': 'synthetic_compatibility_only', 'promotion_ready': False,
            'quality_thresholds_calibrated': False, 'records': records,
            'passed': all(item['compatible'] for item in records)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', required=True)
    parser.add_argument('--results')
    args = parser.parse_args(argv)
    try:
        contracts = Contracts()
        cases = load_json(args.cases)
        if args.results is None:
            validate_cases(cases, contracts)
            report = {'valid': True, 'promotion_ready': False, 'case_count': len(cases['cases'])}
        else:
            report = evaluate(cases, load_json(args.results), contracts)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False))
        return 0 if report.get('passed', True) else 1
    except (ValueError, RuntimeError, OSError, RecursionError) as exc:
        print(json.dumps({'error': type(exc).__name__, 'detail': 'Invalid input or unavailable local validator; '
                          'no retrieval or provider was executed.'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
