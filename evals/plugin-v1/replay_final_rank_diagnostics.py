"""Reproduce exposed rank diagnostics without changing runtime or frozen evidence.

The active trusted bundle may have a newer policy/index receipt; immutable cards,
taxonomy, cases, judgments and literal orders are checked. SQL-only experimental
weights are declared separately and are never presented as production captures.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('rank_diagnostic_runner', ROOT/'evals/plugin-v1/run_final_quality.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runtime = runner.runtime
original_prepare = runtime.prepare_from_brief
original_execute = runtime.retrieval._execute_variant


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['planner', 'weights', 'coverage'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    profile_receipt = json.loads((ROOT/'evals/plugin-v1/results/cp04-final-rank-diagnostics-2026-10-11/rank-weight-diagnostic.json').read_bytes())
    profiles = profile_receipt['profiles']
    manifest = json.loads((runtime.ASSETS/'catalog.search-manifest.json').read_bytes())
    policy = json.loads((runtime.ASSETS/'retrieval-policy.json').read_bytes())
    cards = json.loads((runtime.ASSETS/'catalog.snapshot.json').read_bytes())['cards']
    verified = runtime.context_pack._cards_from_verified_snapshot(
        json.loads((runtime.ASSETS/'catalog.snapshot.json').read_bytes()), manifest['pins'],
        expected_count=manifest['row_count'])

    def cached_cards(value, pins, *, expected_count):
        if pins != manifest['pins'] or expected_count != manifest['row_count']:
            raise ValueError('cached verified card identity changed')
        return verified

    runtime.context_pack._cards_from_verified_snapshot = cached_cards
    connection = sqlite3.connect((runtime.ASSETS/'catalog.search.sqlite').resolve().as_uri()+'?mode=ro&immutable=1', uri=True)
    route_members = {}
    for route, member in connection.execute('SELECT route_id,match_category_id FROM taxonomy_route_registry'):
        route_members.setdefault(route, set()).add(member)
    connection.close()
    if args.mode == 'weights':
        arms = [(name, mode) for name in profiles for mode in ['current','single_full','disjoint']]
    elif args.mode == 'coverage':
        arms = [('source_text','append_route'),('source_text','second_route')]
    else:
        arms = [('active',mode) for mode in ['current','single_full','disjoint','disjoint_route']]
    output = dict(evidence_kind='exposed_development_replay_only', activation=False,
                  diagnostic_mode=args.mode, profiles=profiles, active_pins=manifest['pins'],
                  source_hashes={str(p.relative_to(ROOT)):runner.sha(p) for p in [Path(__file__),
                      ROOT/'plugins/myai-stackguide/scripts/recommendation_request.py',
                      ROOT/'plugins/myai-stackguide/scripts/retrieval.py']}, suites=[])
    count_info = {}

    def prepare(mode, brief, interpretation):
        nonlocal count_info
        request = original_prepare(brief, interpretation)
        query = request['catalog_query']
        full = copy.deepcopy(interpretation['terms'])
        required = [t for group in interpretation['intent']['required_groups'] for t in group]
        context = interpretation['intent']['context_terms']
        if mode == 'current':
            variants = [required, full] if context else [full]
        elif mode in ('disjoint','disjoint_route'):
            variants = [required]+([context] if context else [])
        else:
            variants = [full]
        count_info = dict(original_match_count=request['query_derivation']['original_match_count'])
        route_terms = list(dict.fromkeys(interpretation['route'].split('_')))
        if mode == 'disjoint_route':
            if route_terms not in variants:
                variants.append(route_terms[:policy['limits']['max_terms_per_variant']])
        elif mode in ('append_route','second_route') and count_info['original_match_count'] < query['max_cards']:
            if mode == 'second_route':
                if route_terms != full:
                    variants.append(route_terms[:policy['limits']['max_terms_per_variant']])
            else:
                keys = {runtime.retrieval._normalize(t) for t in full}
                for token in route_terms:
                    if runtime.retrieval._normalize(token) not in keys and len(full) < policy['limits']['max_terms_per_variant']:
                        full.append(token)
                        keys.add(runtime.retrieval._normalize(token))
        query['variants'] = [dict(variant_id='q'+str(n),terms=terms) for n,terms in enumerate(variants,1)]
        runtime.retrieval.validate_query(query,manifest=manifest,policy=policy)
        return request

    for label in ['repair','independent']:
        plan_path = ROOT/('evals/plugin-v1/final-quality-'+label+'-2026-10-11.json')
        capture_path = ROOT/('evals/plugin-v1/results/cp04-final-quality-'+label+'-2026-10-11/observations.json')
        plan = json.loads(plan_path.read_bytes())
        for key in ('cards_sha256','taxonomy_sha256','source_sha256'):
            if plan['pins'][key] != manifest['pins'][key]:
                raise ValueError('frozen source identity changed: '+key)
        frozen = {row['case_id']:row for row in json.loads(capture_path.read_bytes())['records']}
        rows = []
        for case in plan['cases']:
            prior = frozen[case['case_id']]
            routed = [c for c in cards if any(a['category_id'] in route_members[case['route']] for a in c['classifications'])]
            literal = runner.old.scorer.lexical_baseline(routed,case['terms'],prior['query']['max_candidates'])
            if literal != prior['baseline']['raw_ranked_ids']:
                raise ValueError('original literal order changed: '+case['case_id'])
            row = dict(case_id=case['case_id'],metric_family=case['metric_family'],tags=case['tags'],
                       container_domain_ids=case['container_domain_ids'],baseline=prior['baseline'])
            for profile, mode in arms:
                def execute(*a, **kwargs):
                    weights = runtime.retrieval.FIELD_WEIGHTS
                    try:
                        runtime.retrieval.FIELD_WEIGHTS = profiles[profile]
                        return original_execute(*a, **kwargs)
                    finally:
                        runtime.retrieval.FIELD_WEIGHTS = weights
                runtime.retrieval._execute_variant = execute
                runtime.prepare_from_brief = lambda b,i:prepare(mode,b,i)
                captured = []
                def spy(query, **kwargs):
                    result = runtime.retrieval.retrieve(query, **kwargs)
                    captured.append(result)
                    return result
                result = runtime.run(**copy.deepcopy(prior['payload']),retrieve=spy)
                observed = runner.observe(case,result,captured[0]['status'])
                observed.update(query_variants=result['request']['catalog_query']['variants'],preflight=copy.deepcopy(count_info))
                row[profile+'__'+mode] = observed
            rows.append(row)
        semantic = [row for row in rows if row['metric_family']=='semantic']
        summary = {}
        for method in ['baseline']+[p+'__'+m for p,m in arms]:
            strata = {}
            for field, values in [('tags',plan['stratification']['required_case_tags']),('container_domain_ids',plan['stratification']['container_ids'])]:
                for value in values:
                    chosen = [row for row in semantic if value in row[field]]
                    if chosen:
                        strata[value] = runner.macro(chosen,method)
            summary[method] = dict(macro=runner.macro(semantic,method),failed_strata={key:value for key,value in strata.items()
                if value['recall_at_k'] < plan['thresholds']['required_stratum_recall_at_12_min']
                or value['ndcg_at_k'] < plan['thresholds']['required_stratum_ndcg_at_12_min']})
        output['suites'].append(dict(label=label,plan_sha256=runner.sha(plan_path),capture_sha256=runner.sha(capture_path),
                                   original_literal_orders_preserved=len(rows),summary=summary,records=rows))
        print(label,json.dumps(summary),flush=True)
    runtime.prepare_from_brief = original_prepare
    runtime.retrieval._execute_variant = original_execute
    destination = args.output.resolve()
    if not destination.is_relative_to((ROOT/'work/cp04-final').resolve()):
        raise ValueError('diagnostic output must remain in assigned work directory')
    with destination.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(output,stream,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write('\n')


if __name__ == '__main__':
    main()
