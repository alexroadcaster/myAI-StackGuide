"""Frozen source-supported target coverage; not a complete relevance evaluation."""
import argparse
import importlib.util
import json
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('new_domain_priority', ROOT / 'evals/plugin-v1/run_requirement_priority.py')
priority = importlib.util.module_from_spec(spec)
spec.loader.exec_module(priority)
shared, base, builder = priority.shared, priority.base, priority.shared.builder
INPUT = ROOT / 'evals/plugin-v1/new-domain-scenarios-2026-10-11.json'
SOURCE = ROOT / 'research/cp04-new-domain-capabilities-2026-10-11.json'
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-new-domains-2026-10-11'
PACKAGE = OUTPUT / 'candidate'
ARMS = ('control', 'baseline', 'separated', *priority.ranker.MODES)


def validate_cases(cases, original, members, facts):
    """Join declared positive targets to canonical identity and upstream facts."""
    if not 10 <= len(cases) <= 15 or len({c['case_id'] for c in cases}) != len(cases):
        raise ValueError('expected 10-15 unique scenarios')
    lookup = {f['github_repository_id']: f for f in facts}
    for case in cases:
        priority.previous.ranker.validate_intent(case['query_terms'], case['intent'])
        rid = case['expected_target_id']
        card, fact = original[rid], lookup[rid]
        route = members[case['target_category_id']]
        if not any(p['category_id'] in route for p in card['classifications']):
            raise ValueError('target outside route')
        if card['identity']['full_name'] != case['expected_target_name'] or fact['full_name'] != case['expected_target_name']:
            raise ValueError('target identity mismatch')
        if fact['source_url'] != case['source_url'] or fact['observed_on'] != case['observed_on']:
            raise ValueError('target source mismatch')


def coverage(ids, pack, target):
    """Unknown candidates retain their actual ranks and never receive grade zero."""
    packed = [r['card']['identity']['github_repository_id'] for r in pack['cards']]
    return dict(target_rank=ids.index(target)+1 if target in ids else None,
                target_top12=target in ids[:12], target_packed=target in packed,
                top12_unjudged_ids=[rid for rid in ids[:12] if rid != target],
                duplicate_ids=len(ids) != len(set(ids)), ranked_ids=ids,
                relevance_metrics=None)


def verified_package(receipt_sha):
    receipt_bytes = (PACKAGE / 'build-receipt.json').read_bytes()
    if builder.sha(receipt_bytes) != receipt_sha:
        raise ValueError('candidate receipt drift')
    receipt = json.loads(receipt_bytes)
    if receipt['source_file_sha256'] != builder.sha(SOURCE.read_bytes()):
        raise ValueError('candidate source drift')
    for name, digest in receipt['file_sha256'].items():
        if Path(name).name != name or builder.sha((PACKAGE/name).read_bytes()) != digest:
            raise ValueError('candidate bytes drift')
    snapshot = json.loads((PACKAGE / builder.index.CARDS.name).read_bytes())
    manifest = json.loads((PACKAGE / builder.index.MANIFEST.name).read_bytes())
    if manifest['pins']['cards_sha256'] != receipt['file_sha256'][builder.index.CARDS.name]:
        raise ValueError('manifest card hash mismatch')
    verification = builder.index.verify_sqlite(PACKAGE/builder.index.INDEX.name, snapshot['cards'],
        builder.index.logical_rows(snapshot['cards']), manifest)
    cards = base.old.context_pack._cards_from_verified_snapshot(snapshot, manifest['pins'], expected_count=2500)
    return manifest, cards, verification


def declaration(plan, cases, original, members):
    validate_cases(cases, original, members, json.loads(SOURCE.read_bytes())['facts'])
    hashes = base.source_hashes(plan)
    for path in (INPUT, SOURCE, Path(__file__), Path(priority.__file__), Path(priority.previous.__file__),
                 Path(priority.ranker.__file__), Path(priority.previous.ranker.__file__),
                 Path(shared.__file__), Path(builder.__file__), builder.SCHEMA,
                 ROOT/'tests/test_plugin_new_domains.py', ROOT/'evals/plugin-v1/new-domain-contract.md'):
        hashes[path.relative_to(ROOT).as_posix()] = builder.sha(path.read_bytes())
    receipt_sha = builder.sha((PACKAGE/'build-receipt.json').read_bytes())
    manifest, _, _ = verified_package(receipt_sha)
    universes = {c['case_id']: sorted(rid for rid, card in original.items()
        if any(p['category_id'] in members[c['target_category_id']] for p in card['classifications'])) for c in cases}
    return dict(schema_version='cp04_new_domain_declaration_v1', source_hashes=hashes,
        receipt_sha256=receipt_sha, pins=manifest['pins'], cases=cases, routed_universes=universes,
        arms=list(ARMS), scope='Same-author prospective target coverage; all other candidates unjudged.',
        promotion_ready=False)


def capture(plan, cases, original, by_id, members, declared, regressions):
    manifest, cards, verification = verified_package(declared['receipt_sha256'])
    run_id, records, captures = str(uuid.uuid4()), [], []
    for case in cases:
        query = base.old.make_query(plan, case)
        row = dict(case_id=case['case_id'], goal=case['user_goal'], target=case['expected_target_name'])
        packet = dict(case_id=case['case_id'], query=query)
        for arm in ARMS:
            if arm == 'control':
                result = base.old.retrieval.retrieve(query, run_id=run_id,
                    index_path=ROOT/plan['artifacts']['index_path'], manifest_path=ROOT/plan['artifacts']['manifest_path'],
                    policy_path=ROOT/plan['artifacts']['policy_path'])
                ids = [r['github_repository_id'] for r in result['candidates']]
                pack = base.old.context_pack.build_evidence_pack(query, result, {rid:by_id[rid] for rid in ids},
                    pack_id='new-domain-'+case['case_id'], max_cards=query['max_cards'], max_evidence_bytes=query['max_evidence_bytes'])
            elif arm == 'baseline':
                ids = base.old.baseline_ids(plan, case, original, members)
                pack = base.old.baseline_pack(query, ids, by_id, plan, run_id)
                result = None
            else:
                if arm == 'separated':
                    ids, trace = priority.previous.separated(case, by_id, cards, members, case['intent'], plan['lexical_baseline']['candidate_limit'])
                else:
                    ids, trace = priority.priority_ids(case, by_id, cards, members, case['intent'], plan['lexical_baseline']['candidate_limit'], arm)
                result = shared.literal_result(query, ids, cards, manifest['pins'], run_id)
                pack = shared.fixture_pack(query, result, cards, arm)
                packet[arm+'_trace'] = trace
            row[arm] = coverage(ids, pack, case['expected_target_id'])
            packet[arm] = dict(evidence_pack=pack, retrieval=result,
                transport='observed active FTS5' if arm=='control' else 'literal rank adapter; placeholder transport scores')
        records.append(row)
        captures.append(packet)
    # New source additions may affect old routes: execute the ten original judged cases again.
    intents = json.loads(priority.previous.INPUT.read_bytes())['cases']
    regression_rows=[]
    for case in regressions:
        query = base.old.make_query(plan, case)
        baseline_ids=base.old.baseline_ids(plan, case, original, members)
        baseline_pack=base.old.baseline_pack(query, baseline_ids, by_id, plan, run_id)
        ids, trace=priority.priority_ids(case, by_id, cards, members, intents[case['case_id']], plan['lexical_baseline']['candidate_limit'], 'new_required_first')
        result=shared.literal_result(query, ids, cards, manifest['pins'], run_id)
        pack=shared.fixture_pack(query,result,cards,'regression')
        regression_rows.append(dict(case_id=case['case_id'], baseline=base.observe(baseline_ids,baseline_pack,case,'ok'),
            new_required_first=base.observe(ids,pack,case,'ok'), exact_order=ids==baseline_ids))
    rejection = base.old.retrieval.retrieve(base.old.make_query(plan,cases[0]), run_id=run_id,
        index_path=PACKAGE/builder.index.INDEX.name, manifest_path=PACKAGE/builder.index.MANIFEST.name,
        policy_path=PACKAGE/builder.index.PACKAGED_POLICY.name)
    if rejection['status'] != 'index_incompatible':
        raise ValueError('public retrieval accepted unactivated candidate')
    try:
        base.old.context_pack.build_evidence_pack(query,result,cards,pack_id='negative',max_cards=query['max_cards'],max_evidence_bytes=query['max_evidence_bytes'])
    except ValueError:
        pack_rejected=True
    else:
        raise ValueError('public pack accepted unactivated candidate')
    if declaration(plan,cases,by_id,members) != declared:
        raise ValueError('declaration drift during capture')
    summary=dict(case_count=len(cases), positive_target_count=len(cases),
        arms={arm:dict(target_top12=sum(r[arm]['target_top12'] for r in records),
            target_packed=sum(r[arm]['target_packed'] for r in records),
            target_in_pool=sum(r[arm]['target_rank'] is not None for r in records)) for arm in ARMS},
        target_regressions=[r['case_id'] for r in records if r['baseline']['target_top12'] and not r['new_required_first']['target_top12']],
        historical_regressions=dict(exact_orders=sum(r['exact_order'] for r in regression_rows), cases=len(regression_rows),
            macros={arm:base.old.complete_macro(regression_rows,arm) for arm in ('baseline','new_required_first')}),
        candidate_public_rejected=rejection['status'], candidate_public_pack_rejected=pack_rejected,
        package_verification=verification, relevance_metrics=None, independent_held_out=False, promotion_ready=False)
    shared.write(OUTPUT/'observations.json',dict(declaration_sha256=base.scorer.digest(declared),records=records,captures=captures,regressions=regression_rows))
    shared.write(OUTPUT/'summary.json',summary)
    print(json.dumps(summary,sort_keys=True))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    for name in ('build','predeclare','run'):
        action.add_argument('--'+name,action='store_true')
    args=parser.parse_args()
    if args.build:
        previous_source=builder.SOURCE
        try:
            builder.SOURCE=SOURCE
            receipt=builder.build(PACKAGE,built_at='2026-10-11T00:00:00Z')
        finally:
            builder.SOURCE=previous_source
        print(json.dumps(receipt,sort_keys=True))
    else:
        plan,regressions,original,by_id,members=base.load_inputs()
        cases=json.loads(INPUT.read_bytes())['cases']
        declared=declaration(plan,cases,by_id,members)
        if args.predeclare:
            shared.write(OUTPUT/'declaration.json',declared)
            print(json.dumps(dict(predeclared=base.scorer.digest(declared))))
        else:
            saved=json.loads((OUTPUT/'declaration.json').read_bytes())
            if saved != declared or (OUTPUT/'observations.json').exists():
                raise ValueError('declaration drift or existing capture')
            capture(plan,cases,original,by_id,members,saved,regressions)
