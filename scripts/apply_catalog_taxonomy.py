"""Apply explicit reviewed snapshot assignments; never fetch or infer metadata."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '5.1-taxonomy-v2'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def migrate(source, taxonomy, groups, source_hash, taxonomy_hash):
    data = copy.deepcopy(source)
    nodes = {n['id']: n for n in taxonomy['categories']}
    repos = {r['fullName'].casefold(): r for r in data['repositories']}
    original = {r['id']: r for r in source['repositories']}
    assignments = {}
    for category, names in groups.items():
        if category not in nodes or nodes[category]['kind'] != 'category':
            raise ValueError(f'Invalid target leaf: {category}')
        for name in names.split():
            key = name.casefold()
            if key not in repos or key in assignments:
                raise ValueError(f'Unknown or duplicate assignment: {name}')
            assignments[key] = category

    ledger = []
    for key, repo in repos.items():
        old = original[repo['id']]
        previous = old['primaryCategory']
        if key in assignments:
            primary = assignments[key]
            status = 'curator_snapshot_assignment_pending_upstream_refresh'
            reason = 'Explicit per-repository curator decision against accepted v2 domain scope; not current upstream verification.'
        elif previous in nodes and nodes[previous]['kind'] == 'category' and previous != 'mcp_integrations':
            primary = previous
            status = 'inherited_assignment_pending_semantic_refresh'
            reason = 'Retained valid functional category; original evidence and future CAT-06 review remain explicit.'
        else:
            primary = 'uncategorized_review'
            status = 'unresolved_category_scope_or_missing_evidence'
            reason = 'No supported exact functional placement in the accepted vocabulary from current snapshot evidence; requires review, not a guessed category.'
        secondary, removed = [], []
        for category in old.get('secondaryCategories', []):
            if category in nodes and nodes[category]['kind'] == 'category' and category not in {primary, 'mcp_integrations'}:
                if category not in secondary:
                    secondary.append(category)
            else:
                removed.append(category)
        if primary == 'uncategorized_review':
            removed.extend(secondary)
            secondary = []
        protocol_evidence = 'mcp_integrations' in [previous, *old.get('secondaryCategories', [])]
        repo['primaryCategory'] = primary
        repo['secondaryCategories'] = secondary
        repo['classification'] = dict(taxonomyVersion=taxonomy['proposal_version'], status=status,
            reviewedAt='2026-08-31', sourceSnapshotSha256=source_hash,
            evidenceKind='saved_catalog_and_curator_scope_review',
            previousPrimary=previous, previousSecondary=old.get('secondaryCategories', []),
            reason=reason, removedSecondary=removed,
            protocolFacets=[{'value':'mcp','status':'inherited_category_evidence_pending_refresh'}] if protocol_evidence else [])
        ledger.append(dict(id=repo['id'], fullName=repo['fullName'], old_primary=previous,
            new_primary=primary, old_secondary='; '.join(old.get('secondaryCategories', [])),
            new_secondary='; '.join(secondary), status=status, reason=reason,
            missing_description=not bool((repo.get('description') or '').strip())))

    categories = []
    for node in taxonomy['categories']:
        direct = [r['id'] for r in data['repositories'] if node['id'] in [r['primaryCategory'], *r['secondaryCategories']]]
        category = dict(key=node['id'], title=node['label'], description=node['scope'], layer=node['layer'],
                        source='accepted-taxonomy-v2', kind=node['kind'], parentId=node['parent_id'],
                        aliases=node['aliases'], repoIds=direct)
        if node['kind'] == 'container':
            children = {n['id'] for n in nodes.values() if n['parent_id'] == node['id']}
            category['descendantRepoIds'] = [r['id'] for r in data['repositories']
                if children.intersection([r['primaryCategory'], *r['secondaryCategories']])]
        categories.append(category)
    data['categories'] = categories
    data['placements'] = [dict(repoKey=r['fullName'], categoryKey=c, source='taxonomy-v2-snapshot-migration')
        for r in data['repositories'] for c in [r['primaryCategory'], *r['secondaryCategories']]]

    # Saved use-case/navigation queries can expand old containers; this is not a primary assignment.
    old_routes = {x['old_id']: x['target_leaf_ids'] for x in taxonomy['old_category_dispositions']}
    # The original Local AI use case referenced this absent legacy category.
    old_routes['local_llm_inference_routing'] = ['inference_model_serving', 'llm_gateways_routing_caching', 'edge_on_device_ai']
    retired = set(old_routes) - set(nodes)
    reference_changes = []

    def migrate_refs(value, path):
        if isinstance(value, list):
            out = []
            for index, item in enumerate(value):
                if isinstance(item, str) and item in old_routes:
                    if item in retired:
                        targets = [c for c in old_routes[item] if c != 'uncategorized_review']
                    elif nodes[item]['kind'] == 'container':
                        targets = [n['id'] for n in nodes.values() if n['parent_id'] == item]
                    else:
                        targets = [item]
                    if targets != [item]:
                        reference_changes.append({'path':f'{path}/{index}','before':item,'after':targets})
                    for target in targets:
                        if target not in out:
                            out.append(target)
                else:
                    out.append(migrate_refs(item, f'{path}/{index}'))
            return out
        if isinstance(value, dict):
            return {k:migrate_refs(v, f'{path}/{k}') for k,v in value.items()}
        if isinstance(value, str) and value in retired:
            raise ValueError(f'A scalar retired reference needs an explicit decision: {path}')
        return value

    for key in ['useCases','stackRecipes','discoveryQueries']:
        data[key] = migrate_refs(data[key], '/'+key)
    data['schemaVersion'] = VERSION
    data['target']['note'] = 'Intermediate taxonomy migration. Metadata remains the original snapshot; Stars/mandatory-field eligibility has not passed CAT-07.'
    data['target']['activityComplete'] = False
    data['summary']['categories'] = len(categories)
    data['summary']['placements'] = len(data['placements'])
    data['summary']['thematicCategories'] = sum(n['kind']=='category' for n in nodes.values())
    data['summary']['navigationContainers'] = sum(n['kind']=='container' for n in nodes.values())
    data['taxonomyMigration'] = dict(version=taxonomy['proposal_version'], date='2026-08-31',
        inputSha256=source_hash, taxonomySha256=taxonomy_hash, sourceSchemaVersion=source['schemaVersion'],
        status='applied_snapshot_classification_pending_metadata_refresh',
        classificationCounts=dict(Counter(x['status'] for x in ledger)),
        originalTarget=source['target'], originalSummary=source['summary'],
        referenceChanges=reference_changes, finalEligibilityApplied=False)
    counts = []
    for c in categories:
        counts.append(dict(id=c['key'],label=c['title'],kind=c['kind'],parent=c['parentId'],
            primary=sum(r['primaryCategory']==c['key'] for r in data['repositories']),
            memberships=len(c['repoIds']),descendant_unique=len(c.get('descendantRepoIds', [])),
            count_basis='intermediate_snapshot_before_Stars_and_identity_gate'))
    return data, ledger, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--taxonomy',type=Path,required=True)
    parser.add_argument('--assignments',type=Path,required=True)
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--apply',action='store_true',help='Write the canonical manifest after preparing the candidate')
    args = parser.parse_args()
    data, ledger, counts = migrate(load(args.input),load(args.taxonomy),load(args.assignments),digest(args.input),digest(args.taxonomy))
    args.run_dir.mkdir(parents=True,exist_ok=True)
    for name, rows in [('assignment-ledger.csv',ledger),('category-counts.csv',counts)]:
        with (args.run_dir/name).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    text=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    (args.run_dir/'candidate-manifest.json').write_text(text,encoding='utf-8')
    if args.apply:
        from build_catalog_html import validate_payload
        validate_payload(data)
        (ROOT/'data/catalog_manifest.json').write_text(text,encoding='utf-8')
    print(json.dumps({'records':len(ledger),'categories':len(counts),'placements':len(data['placements']),
                      'classification':data['taxonomyMigration']['classificationCounts'],'applied':args.apply}))


if __name__ == '__main__':
    main()
