"""Post-capture integrity/lineage audit; performs no COUNT or ranked lookup."""
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('chat_audit_capture', ROOT/'evals/plugin-v1/run_final_chat_repair.py')
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)
out = owner.OUTPUT
read = lambda name: json.loads((out/name).read_bytes())
plan = read('frozen-plan.json')
cards, members, registry = owner.load(plan)
owner.verify_hashes({str((out/name).relative_to(ROOT)):digest for name,digest in read('artifact-hashes.json').items()})
policy = owner.read(plan['artifacts']['policy_path'])
observations, formal = read('observations.json')['records'], read('formal-identity-comparison.json')['records']
cases = {c['case_id']:c for c in plan['cases']}
by_id = {c['identity']['github_repository_id']:c for c in cards}
errors, details = [], []
for row in observations + formal:
    result = row.get('candidate_capture',row.get('result'))
    payload = row.get('payload')
    if payload is None:
        original = next(r for r in owner.read(owner.FORMAL_DIR+'observations.json')['records'] if r['case_id'] == row['case_id'])
        payload = dict(brief=original['brief'],interpretation=original['interpretation'],public_observations=[])
    q = result['request']['catalog_query']
    raw = row.get('candidate_raw_result',row.get('raw_result'))
    trace = row['native_trace']
    derivation = trace['query_derivation']
    intent = payload['interpretation']['intent']
    required = [t for g in intent['required_groups'] for t in g]
    atoms = owner.runtime._required_phrase_atoms(required,policy['aliases'])
    originals = payload['interpretation']['terms']
    terms = q['variants'][0]['terms']
    route = payload['interpretation']['route']
    origins = derivation['added_term_origins']
    route_members = members[route]
    original_q = copy.deepcopy(q)
    original_q['variants'] = [dict(variant_id='q1',terms=originals)]
    checks = dict(
        original_prefix=terms[:len(originals)] == originals,
        appended_origins=[x['term'] for x in origins] == terms[len(originals):],
        term_capacity=len(terms) <= policy['limits']['max_terms_per_variant'],
        one_variant=len(q['variants']) == 1 and q['variants'][0]['variant_id'] == 'q1',
        original_query_digest=derivation['original_query_sha256'] == owner.runtime.retrieval.canonical_query_sha256(original_q),
        final_query_digest=derivation['final_query_sha256'] == owner.runtime.retrieval.canonical_query_sha256(q),
        pins=derivation['pins'] == plan['pins'] == raw['pins'] == result['evidence_pack']['pins'],
        original_terms=derivation['original_terms'] == originals,
        intent=result['request']['intent'] == intent,
        aggregate_retrieval=result['aggregate_calls'] == result['retrieval_calls'] == 1,
        candidate_budget=len(raw['candidates']) <= q['max_candidates'] == policy['limits']['max_retrieved_hits'],
        hit_budget=raw['retrieved_hits'] <= policy['limits']['max_retrieved_hits'],
        pack_card_budget=len(result['evidence_pack']['cards']) <= q['max_cards'] == policy['limits']['max_detailed_cards'],
        pack_byte_budget=len(owner.runner.old.scorer.canonical(result['evidence_pack'])) <= q['max_evidence_bytes'] == policy['limits']['max_evidence_bytes'],
        original_guard_exclusions=result['request']['exclusions']['repository_ids'] == payload['interpretation']['excluded_repository_ids'] and result['request']['exclusions']['dependencies'] == payload['interpretation']['excluded_dependencies'],
        raw_digest=raw['query_sha256'] == owner.runtime.digest(q),
        selection_pack=all(c['card']['identity']['github_repository_id'] in result['selected_ids'] and raw['candidates'][c['retrieval_rank']-1]['github_repository_id'] == c['card']['identity']['github_repository_id'] for c in result['evidence_pack']['cards']),
    )
    wanted = {owner.runtime.retrieval._normalize(t) for t in required} | {token for token,source in atoms}
    for origin in origins:
        kind, source, term = origin['source_kind'], origin['source'], origin['term']
        valid = ((kind == 'required_term_atom' and (term,source) in atoms) or
                 (kind == 'selected_pinned_taxonomy_route_id' and source == route and term in route.split('_')) or
                 (kind == 'pinned_taxonomy_route_member' and source in route_members and term in source.split('_') and wanted.intersection(source.split('_'))))
        if not valid:
            errors.append(dict(case_id=row['case_id'],invalid_origin=origin))
    expected_route = [x['term'] for x in origins if x['source_kind'] == 'selected_pinned_taxonomy_route_id']
    checks['legacy_added_route_only'] = derivation['added_route_terms'] == expected_route
    metadata = [t for t in trace['sql_trace'] if t['sql'].startswith('SELECT match_category_id FROM taxonomy_route_registry')]
    counts = [t for t in trace['sql_trace'] if 'SELECT COUNT(*)' in t['sql'].upper() and ' MATCH ' in t['sql'].upper()]
    checks['metadata_same_count_connection'] = all(t['connection'] == counts[0]['connection'] and ' MATCH ' not in t['sql'].upper() for t in metadata)
    checks['conditional_metadata'] = len(metadata) == int(bool(atoms) and route is not None and derivation['original_match_count'] < q['max_cards'])
    checks['underfill_only'] = not origins or derivation['original_match_count'] < q['max_cards']
    checks.update(trace['gates'])
    for key,value in checks.items():
        if not value:
            errors.append(dict(case_id=row['case_id'],failed_check=key))
    details.append(dict(case_id=row['case_id'],checks=checks,metadata_selects=len(metadata),
        pack_cards=len(result['evidence_pack']['cards']),pack_bytes=len(owner.runner.old.scorer.canonical(result['evidence_pack'])),
        origin_count=len(origins)))
billing = next(r for r in observations if r['case_id'] == 'PROSPECTIVE-HOLD-08')
judgments = {j['github_repository_id']:j for j in cases[billing['case_id']]['judgments']}
top = [dict(rank=n,github_repository_id=rid,full_name=by_id[rid]['identity']['full_name'],grade=judgments[rid]['grade'],constraint=judgments[rid]['constraint']) for n,rid in enumerate(billing['candidate']['raw_ranked_ids'][:12],1)]
conclusion = read('conclusion.json')
value = dict(schema_version='cp04_chat_repair_post_capture_audit_v1',ranked_calls=0,errors=errors,
    source_and_artifact_hashes_valid=True,cases=details,expected_native_observations=49,
    old30_pack_exact=all(r['evidence_pack_exact'] for r in conclusion['preservation'][:30]),
    billing_top12=top,billing_positive_pool=sum(judgments[rid]['grade'] > 0 and judgments[rid]['constraint'] != 'denied' for rid in billing['candidate']['raw_ranked_ids']),
    frozen_no_go_retained=conclusion['verdict'] == 'no_go',human_acceptance=False,promotion_ready=False,
    earlier_audit_preserved='audit.json retained two invalid audit assumptions: MATCH substring matched match_category_id; pack need not be selected prefix because actual pack eligibility can exclude candidates. Corrected against context_pack.py selection and real SQL operator. No new ranking or changed captures.')
owner.runner.write('audit-corrected.json',value)
owner.runner.write('audit-corrected-hashes.json',{name:owner.runner.sha(out/name) for name in ('audit_capture.py','audit-corrected.json','audit.json','artifact-hashes.json')})
print(json.dumps(dict(errors=errors,observations=len(details),max_pack_bytes=max(x['pack_bytes'] for x in details),old30_pack_exact=value['old30_pack_exact'],billing_top12=top)))
raise SystemExit(bool(errors))
