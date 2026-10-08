"""Fresh V3 source oracle validation. Source API awaits the authored packet READY."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
from urllib.parse import urlsplit
from datetime import date, datetime
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'evals/plugin-v1/quality-oracle-v3-source.json'
SNAPSHOT = 'plugins/myai-stackguide/assets/catalog.snapshot.json'
UTC_DAY_SEMANTICS = 'observed_at is the UTC retrieval date, not source update/push/commit/release date; search crawl ages are not repository activity.'
spec = importlib.util.spec_from_file_location('oracle_v3_pure_scorer', ROOT/'evals/plugin-v1/evaluate_retrieval.py')
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pointer_value(document, pointer):
    """Resolve exact JSON Pointers, rejecting malformed escapes and list indices."""
    require(isinstance(pointer, str) and pointer.startswith('/'), 'invalid source pointer')
    value = document
    for encoded in pointer[1:].split('/'):
        index = 0
        while index < len(encoded):
            if encoded[index] == '~':
                require(index + 1 < len(encoded) and encoded[index + 1] in '01', 'invalid pointer escape')
                index += 1
            index += 1
        key = encoded.replace('~1', '/').replace('~0', '~')
        if isinstance(value, list):
            require(key.isdigit() and (key == '0' or not key.startswith('0')), 'invalid pointer list index')
            require(int(key)<len(value),'source pointer unresolved')
            value = value[int(key)]
        else:
            require(isinstance(value, dict) and key in value, 'source pointer unresolved')
            value = value[key]
    return value


def validate_universe(universe, judgments, routed):
    require(isinstance(universe, list) and universe and all(type(i) is int and i > 0 for i in universe), 'invalid universe')
    require(len(universe) == len(set(universe)) and set(universe) == set(routed), 'routed universe mismatch')
    ids = [row['github_repository_id'] for row in judgments]
    require(len(ids) == len(set(ids)) and set(ids) == set(universe), 'judgment universe incomplete')


def validate_grade(row, criteria):
    grade, status = row['relevance_grade'], row['assessment_status']
    require(grade is None or type(grade) is int and 0 <= grade <= 3, 'invalid relevance grade')
    require(status == ('unknown' if grade is None else 'reviewed_unrelated' if grade == 0 else 'source_supported'), 'grade/status disagreement')
    require(row.get('adoption_fit') == 'unknown' and type(row.get('denied_by_frozen_constraints')) is bool, 'invalid adoption/constraint')
    require(isinstance(row.get('contribution_rationale'), str) and row['contribution_rationale'].strip(), 'missing contribution rationale')
    require(isinstance(row.get('unknown_reason'),str) and row['unknown_reason'].strip() if grade is None else row.get('unknown_reason') is None, 'unknown reason mismatch')
    evidence = row.get('source_evidence')
    require(isinstance(evidence, list) and evidence, 'missing source evidence')
    if grade and grade > 0:
        # This checks evidence existence/type, never substitutes a substring model for semantic source review.
        require(any(e.get('value') and (any(segment in e.get('pointer','') for segment in
                ('/descriptions/', '/repository/topics', '/repository/languages')) or
                e.get('source_kind')=='public_primary_live' and isinstance(e.get('value'),dict) and e['value'].get('disposition')=='supported')
                for e in evidence), 'positive lacks functional evidence')
    if grade == 1:
        supporting = criteria.get('explicit_supporting_function')
        require(isinstance(supporting, str) and supporting.strip() and not supporting.startswith('None'), 'grade1 lacks declared supporting function')


def public_observation_granularity(document, observed_at):
    """Validate declared public observation precision without inventing a timestamp."""
    require(document.get('schema_version')=='cp04_public_qualification_v1' and isinstance(observed_at,str),
            'invalid public observation source')
    if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',observed_at):
        date.fromisoformat(observed_at)  # Invalid calendar dates fail, including February 30.
        require(document.get('metadata_gaps',{}).get('observation_timestamp_semantics')==UTC_DAY_SEMANTICS and
                document.get('qualification_date')==observed_at,'date lacks declared UTC day granularity')
        return 'day'
    require(re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z',observed_at) is not None,
            'invalid live observation timestamp')
    # Python 3.14 accepts 24:00 as the next day; retain explicit timestamp bounds.
    require(int(observed_at[11:13])<24 and int(observed_at[14:16])<60 and int(observed_at[17:19])<60,
            'invalid live observation timestamp')
    require(datetime.fromisoformat(observed_at.replace('Z','+00:00')).tzinfo is not None,'invalid live observation timestamp')
    return 'timestamp'


def qualification_observation_report(document):
    """Derived validation facts; source date strings remain exactly unchanged."""
    return [{'case_id':record['case_id'],'github_repository_id':record['github_repository_id'],
             'check_index':index,'observed_at':check['observed_at'],
             'observation_granularity':public_observation_granularity(document,check['observed_at'])}
            for record in document['records'] for index,check in enumerate(record['requirement_checks'])]


def validate_source_reference(reference, documents, card, card_index, snapshot_date, case_id=None):
    path = reference['path']
    require(path in documents, 'unbound source artifact')
    pointer = reference['pointer']
    observed = pointer_value(documents[path], pointer)
    if path == SNAPSHOT:
        require(pointer.startswith('/cards/'+str(card_index)+'/'), 'source pointer wrong card owner')
    if 'values' in reference:
        require(isinstance(observed, dict) and all(k in observed and observed[k] == v for k,v in reference['values'].items()), 'source values mismatch')
    else:
        require('value' in reference and observed == reference['value'], 'source value mismatch')
    if path == SNAPSHOT:
        ref = reference.get('evidence_ref')
        matches = [e for e in card['evidence'] if e['source_ref'] == ref and
                   ('evidence_id' not in reference or e['evidence_id'] == reference['evidence_id'])]
        require(matches, 'source evidence reference not owned by card')
        require(reference.get('observed_at') in [e['observed_at'] for e in matches], 'source observation date mismatch')
        require(reference.get('source_snapshot_date') == snapshot_date, 'snapshot date mismatch')
        require(reference.get('observation_date_status') == ('unknown' if reference['observed_at'] is None else 'known'), 'observation status mismatch')
        for key in ('source_kind','verification'):
            if key in reference:
                require(reference[key] in [e[key] for e in matches], 'source '+key+' mismatch')
    elif reference.get('source_kind')=='public_primary_live':
        document=documents[path]
        require(document.get('schema_version')=='cp04_public_qualification_v1','unknown live source schema')
        parts=pointer.split('/')
        require(len(parts)==5 and parts[1]=='records' and parts[3]=='requirement_checks','live evidence must bind exact criterion')
        record=pointer_value(document,'/records/'+parts[2])
        require(record['case_id']==case_id and record['github_repository_id']==card['identity']['github_repository_id'] and
                record['repository']==card['identity']['full_name'] and record['adoption_fit']=='unknown','live source owner mismatch')
        require(reference.get('source_url')==observed['source_url'] and reference.get('observed_at')==observed['observed_at'],'live URL/date mismatch')
        granularity=public_observation_granularity(document,observed['observed_at'])
        require(observed['disposition'] in ('supported','unsupported','unknown') and
                observed['source_kind'] in ('upstream_readme','official_docs','upstream_license','upstream_release'),'invalid qualification type')
        url=urlsplit(observed['source_url'])
        require(url.scheme=='https' and url.netloc and not url.username and not url.password,'invalid public source URL')
        require(observed['criterion'] and observed['concise_rationale'] and isinstance(observed.get('source_excerpt'),str),'missing qualification rationale')
        require(len(observed['source_excerpt'].split())<=25,'source quote limit')
        return {'observation_granularity':granularity}
    else:
        require(path=='specs/catalog/taxonomy.yaml','unsupported noncanonical functional evidence')


def validate_document(oracle, documents):
    require(oracle.get('schema_version') == 'cp04_quality_oracle_source_v3', 'wrong source schema')
    require(oracle.get('promotion_ready') is False and oracle.get('calibrated') is False and
            oracle.get('observed_results') is False and oracle.get('threshold_change') is False, 'source cannot claim observed quality')
    snapshot = documents[SNAPSHOT]
    manifest = documents['plugins/myai-stackguide/assets/catalog.search-manifest.json']
    plan = documents['evals/plugin-v1/quality-plan-v2.json']
    require(oracle['bundle_pins'] == manifest['pins'] == plan['pins'], 'bundle pins mismatch')
    require(oracle['source_snapshot_date'] == snapshot['source_snapshot_date'], 'source snapshot mismatch')
    require(oracle['route_registry_pin'] == manifest['route_registry'], 'registry pin mismatch')
    require(set(oracle['threshold_refs']) == set(plan['thresholds']), 'threshold coverage mismatch')
    for key, reference in oracle['threshold_refs'].items():
        require(reference['path'] == 'evals/plugin-v1/quality-plan-v2.json' and reference['pointer'] == '/thresholds/'+key and
                reference['value'] == plan['thresholds'][key] and reference['sha256'] == oracle['source_hashes'][reference['path']], 'threshold binding mismatch')
    for key, reference in oracle['policy_refs'].items():
        require(reference['path'] == 'plugins/myai-stackguide/assets/retrieval-policy.json' and reference['sha256'] == oracle['source_hashes'][reference['path']] and
                pointer_value(documents[reference['path']],reference['pointer']) == reference['value'], 'policy reference mismatch')
    for document in documents.values():
        if isinstance(document,dict) and document.get('schema_version')=='cp04_public_qualification_v1':
            excerpts={}
            for record in document['records']:
                for check in record['requirement_checks']:
                    excerpts.setdefault(check['source_url'],set()).add(check['source_excerpt'])
            require(all(sum(len(text.split()) for text in texts)<=25 for texts in excerpts.values()),'aggregate source quote limit')
    cards = snapshot['cards']; by_id = {c['identity']['github_repository_id']:c for c in cards}
    require(len(cards)==plan['artifacts']['catalog_row_count'] and len(by_id)==len(cards),'canonical card corpus mismatch')
    require(scorer.file_sha256(ROOT/plan['artifacts']['index_path'])==oracle['bundle_pins']['index_sha256'],'index pin mismatch')
    indices = {c['identity']['github_repository_id']:i for i,c in enumerate(cards)}
    nodes = {n['id']:n for n in documents['specs/catalog/taxonomy.yaml']['categories']}
    cases = oracle['cases']; ids = [c['case_id'] for c in cases]
    require(len(ids) == len(set(ids)) and len(cases) == 15, 'fresh case coverage mismatch')
    semantic = [c for c in cases if c['include_in_14_domain_macro'] is True]
    require(len(semantic) == 14 and {d for c in semantic for d in c['container_domain_ids']} == set(plan['stratification']['container_ids']), 'semantic domain coverage mismatch')
    for case in cases:
        diagnostic = not case['include_in_14_domain_macro']
        require(case['split'] == ('diagnostic' if diagnostic else 'held_out') and
                case['metric_family'] == ('secondary_route_diagnostic' if diagnostic else 'functional_semantic'), 'split/family mismatch')
        require(case['k'] == plan['candidate_route']['max_cards'] and case['query_locale'] in ('ru','en'), 'query k/locale mismatch')
        criteria = case['graded_criteria']
        require(all(isinstance(criteria.get(k), str) and criteria[k].strip() for k in ('core','preferred_detail','explicit_supporting_function')) and case['user_goal'].strip(), 'missing goal criteria')
        terms = case['query_terms']; policy = documents['plugins/myai-stackguide/assets/retrieval-policy.json']
        require(isinstance(terms,list) and 1 <= len(terms) <= policy['limits']['max_terms_per_variant'] and
                all(isinstance(t,str) and 1 <= len(t) <= policy['limits']['max_term_chars'] for t in terms) and len(terms)==len(set(terms)), 'query term bounds')
        route = case['target_category_id']; require(route in nodes and case['route_kind'] == nodes[route]['kind'], 'invalid source route')
        require(pointer_value(documents[case['route_source']['path']],case['route_source']['pointer']) == nodes[route] == case['route_source']['value'], 'route source mismatch')
        categories = {n['id'] for n in nodes.values() if n.get('parent_id') == route} if nodes[route]['kind']=='container' else {route}
        routed = {i for i,c in by_id.items() if any(a['category_id'] in categories for a in c['classifications'])}
        validate_universe(case['universe_ids'],case['judgments'],routed)
        require(case['universe_ids']==sorted(routed) and case['universe_count']==len(routed), 'universe order/count mismatch')
        require(('thin_leaf' in case['tags']) == (len(routed)<=plan['stratification']['thin_leaf_max_cards']) and
                ('dense_leaf' in case['tags']) == (len(routed)>=plan['stratification']['dense_leaf_min_cards']), 'route density tag mismatch')
        require(('lexical_ru' if case['query_locale']=='ru' else 'lexical_en') in case['tags'], 'locale tag mismatch')
        for row in case['judgments']:
            validate_grade(row,criteria); i=row['github_repository_id']; card=by_id[i]
            require(row['classifications'] == card['classifications'], 'classification mismatch')
            for reference in [*row['source_evidence'],row['identity_source'],row['constraint_source'],row['membership_cohort_source']]:
                validate_source_reference(reference,documents,card,indices[i],oracle['source_snapshot_date'],case['case_id'])
            require(row['identity_source']['values']=={k:card['identity'][k] for k in ('github_repository_id','full_name','url')}, 'identity join mismatch')
            facts = {k:card['repository'][k] for k in ('archived','availability','visibility')}
            require(row['constraint_source']['values']==facts, 'constraint facts mismatch')
            require(case['hard_constraints']=={'archived':False,'availability':'available','visibility':'public','unknown_mandatory_fact':policy['unknown_mandatory_fact']}, 'hard constraint definition mismatch')
            denied = facts['archived'] is True or facts['availability']!='available' or facts['visibility']!='public'
            require(row['denied_by_frozen_constraints'] is denied, 'independent denial mismatch')
        positives = sorted(r['github_repository_id'] for r in case['judgments'] if r['relevance_grade'] is not None and r['relevance_grade']>0 and not r['denied_by_frozen_constraints'])
        unknowns = sorted(r['github_repository_id'] for r in case['judgments'] if r['relevance_grade'] is None)
        require(case['source_supported_positive_ids']==positives and case['unknown_ids']==unknowns, 'source grade summaries mismatch')
        require(case['intrinsic_recall_at_12_ceiling']==(min(case['k'],len(positives))/len(positives) if positives else None), 'recall ceiling mismatch')
        query_def={k:case[k] for k in ('case_id','user_goal','graded_criteria','query_locale','query_terms','target_category_id','hard_constraints','k')}
        require(case['query_definition_sha256']==scorer.digest(query_def),'source query definition mismatch')
        projection=[{'id':r['github_repository_id'],'evidence':r['source_evidence'],'classifications':r['classifications'],'constraint_source':r['constraint_source'],'identity_source':r['identity_source'],'membership_cohort_source':r['membership_cohort_source']} for r in case['judgments']]
        require(case['source_projection_sha256']==scorer.digest(projection) and case['source_projection_bytes']==len(scorer.canonical(projection)), 'source projection mismatch')
        require(case['unknown_coverage']['unknown_count']==len(unknowns) and case['unknown_coverage']['universe_count']==len(routed) and
                case['unknown_coverage']['unknown_share']==len(unknowns)/len(routed) and case['unknown_coverage']['threshold'] is None, 'unknown coverage mismatch')
    return oracle, plan, cards, by_id


def load_source(path=SOURCE):
    oracle = scorer._load_json_bounded(path,4*1024*1024)
    documents = {}
    for source,digest in oracle['source_hashes'].items():
        resolved=(ROOT/source).resolve()
        require(resolved.is_relative_to(ROOT) and scorer.file_sha256(resolved)==digest,'source artifact drift')
        # Snapshot cap is the unchanged production card-reader cap, not oracle input budget.
        if source not in ('data/catalog_manifest.json','evals/plugin-v1/quality-plan.json'):
            documents[source]=scorer._load_json_bounded(resolved,32*1024*1024 if source==SNAPSHOT else 4*1024*1024)
    return validate_document(oracle,documents)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true',required=True)
    parser.parse_args(argv)
    try:
        oracle,_,_,_=load_source()
        observations=[]
        for source in oracle['source_hashes']:
            if source.startswith('research/'):
                document=scorer._load_json_bounded(ROOT/source,4*1024*1024)
                if document.get('schema_version')=='cp04_public_qualification_v1':
                    observations.extend(qualification_observation_report(document))
        print(json.dumps({'status':'source_contract_valid','case_count':len(oracle['cases']),'promotion_ready':False,'frozen':False,
                          'public_observation_validation':observations}))
        return 0
    except (ValueError,KeyError,OSError,TypeError,IndexError) as error:
        print(json.dumps({'status':'invalid_source','error_type':type(error).__name__,'message':str(error)}));return 2


if __name__=='__main__':raise SystemExit(main())
