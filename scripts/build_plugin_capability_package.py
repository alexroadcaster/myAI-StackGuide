"""Build a separately pinned, source-qualified CP-04 candidate bundle."""
from pathlib import Path
import argparse
import copy
from datetime import date
import hashlib
import json
import os
import tempfile
from jsonschema import Draft202012Validator, FormatChecker
import build_plugin_search_index as index
import build_plugin_catalog as catalog

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/plugin_capability_enrichment.json'
SCHEMA = ROOT / 'specs/catalog/capability-enrichment.schema.json'
OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-capability-package-2026-10-08/candidate'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_source():
    return json.loads(SOURCE.read_text(encoding='utf-8'))


def enrich(snapshot, source):
    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')),
                                     format_checker=FormatChecker())
    errors = list(validator.iter_errors(source))
    if errors:
        raise ValueError('invalid capability source: ' + errors[0].message)
    result = copy.deepcopy(snapshot)
    lookup = {card['identity']['github_repository_id']: card for card in result['cards']}
    source_digest = sha(catalog.canonical_bytes(source))
    seen = set()
    for fact in source['facts']:
        rid = fact['github_repository_id']
        if type(rid) is not int or rid not in lookup or rid in seen:
            raise ValueError('invalid or duplicate capability identity')
        seen.add(rid)
        card = lookup[rid]
        if card['identity']['full_name'] != fact['full_name']:
            raise ValueError('capability name does not match canonical identity')
        # Sources must belong to the exact joined repository, not arbitrary GitHub content.
        if fact['source_url'].split('/')[3:5] != fact['full_name'].split('/'):
            raise ValueError('upstream source repository mismatch')
        if date.fromisoformat(fact['observed_on']) > date.today():
            raise ValueError('future capability observation')
        for evidence in card['evidence']:
            if '/advisory' in evidence['fields']:
                evidence['fields'].remove('/advisory')
                for key, value in card['advisory'].items():
                    # Original parent evidence must never cover newly added facts.
                    if key in ('use_cases', 'tradeoffs', 'gaps'):
                        evidence['fields'].extend(f'/advisory/{key}/{i}' for i in range(len(value)))
                    else:
                        evidence['fields'].append('/advisory/' + key)
        observed = fact['observed_on'] + 'T00:00:00Z'
        fields = []
        for target, origin in (('use_cases', 'capability'), ('tradeoffs', 'scope'), ('gaps', 'limitations')):
            values = card['advisory'][target]
            if fact[origin] in values:
                raise ValueError('capability input duplicates existing advice')
            fields.append(f'/advisory/{target}/{len(values)}')
            values.append(fact[origin])
        for kind, suffix, ref, verification in (
            ('upstream_document', 'upstream', fact['source_url'], 'source_reported'),
            ('curator_record', 'input', f'catalog:cp04-enrichment-{source_digest}/repositories/{rid}', 'derived_reviewed'),
        ):
            card['provenance']['sources'].append(dict(source_id='src-capability-' + suffix,
                source_kind=kind, source_ref=ref, observed_at=observed, verification=verification))
            # Capability is upstream-reported; prerequisites/limitations are curated interpretation.
            card['evidence'].append(dict(evidence_id='ev-capability-' + suffix, source_kind=kind,
                source_ref=ref, observed_at=observed, verification=verification,
                fields=fields[:1] if suffix == 'upstream' else fields[1:]))
    result['catalog_snapshot_id'] = 'cp04-capability-2026-10-08-' + source_digest[:16]
    result['builder_version'] = 'cp04-capability-1.0.0'
    validate_cards(result['cards'])
    return result


def validate_cards(cards):
    schema = json.loads(catalog.CARD_SCHEMA.read_text(encoding='utf-8'))
    activity = json.loads(catalog.ACTIVITY_SCHEMA.read_text(encoding='utf-8'))
    # Resolve the single external activity contract locally; no network schema fetch.
    schema['properties']['activity'] = {'type': 'object'}
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    activity_validator = Draft202012Validator(activity, format_checker=FormatChecker())
    for card in cards:
        # Activity local references belong to its own schema, not the card root.
        activity_validator.validate(card['activity'])
        validator.validate(card)
        if len(catalog.canonical_bytes(card)) > schema['x-max-utf8-bytes']:
            raise ValueError('card byte budget exceeded')


def build(output=OUTPUT, *, built_at='2026-10-08T00:00:00Z'):
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / 'evals/plugin-v1/results') or output.exists():
        raise ValueError('a new isolated results directory is required')
    base, _ = catalog.build_snapshot()
    snapshot = enrich(base, load_source())
    encoded = catalog.canonical_bytes(snapshot)
    policy, policy_bytes = index.load_policy()
    rows = index.logical_rows(snapshot['cards'])
    routes = index.logical_routes(snapshot['taxonomy_sha256'])
    rows_sha = index.logical_rows_sha256(rows)
    routes_sha = index.logical_routes_sha256(routes)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='capability-', dir=output.parent) as temporary:
        staged = Path(temporary)
        db = staged / index.INDEX.name
        index.build_sqlite(db, snapshot['cards'], rows, snapshot, policy, sha(encoded),
                           sha(policy_bytes), rows_sha, routes, routes_sha)
        manifest = index._manifest(snapshot, policy, sha(encoded), sha(policy_bytes),
                                   sha(db.read_bytes()), rows_sha, routes_sha, built_at)
        verification = index.verify_sqlite(db, snapshot['cards'], rows, manifest)
        for name, data in ((index.CARDS.name, encoded), (index.MANIFEST.name, catalog.canonical_bytes(manifest)),
                           (index.PACKAGED_POLICY.name, policy_bytes)):
            (staged / name).write_bytes(data)
        receipt = dict(schema_version='cp04_capability_build_v1', status='candidate_not_promoted',
            source_file_sha256=sha(SOURCE.read_bytes()), source_content_sha256=sha(catalog.canonical_bytes(load_source())),
            schema_sha256=sha(SCHEMA.read_bytes()), builder_sha256=sha(Path(__file__).read_bytes()),
            base_cards_sha256=sha(catalog.canonical_bytes(base)), enriched_cards=len(load_source()['facts']),
            preserved_base_source_lineage=True, active_bundle_changed=False,
            file_sha256={p.name: sha(p.read_bytes()) for p in sorted(staged.iterdir())}, verification=verification)
        (staged / 'build-receipt.json').write_bytes(catalog.canonical_bytes(receipt))
        # Destination must be absent; no overwrite of an active or historical package.
        os.rename(staged, output)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(build(args.output), sort_keys=True))
