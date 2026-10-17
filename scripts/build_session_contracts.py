"""Bundle only the offline schema-reference closure used by CP-11 inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urldefrag, urljoin

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'plugins/myai-stackguide/assets/session-contracts.json'
ROOTS = (
    'recommendation/recommendation-request.schema.json',
    'retrieval/retrieval-result.schema.json',
    'retrieval/evidence-pack.schema.json',
    'recommendation/recommendation-memo.schema.json',
)
MAP_KEYWORDS = {'properties', 'patternProperties', '$defs', 'dependentSchemas'}
SINGLE_KEYWORDS = {'items', 'additionalProperties', 'contains', 'not', 'if', 'then', 'else', 'propertyNames', 'unevaluatedProperties'}
LIST_KEYWORDS = {'allOf', 'anyOf', 'oneOf', 'prefixItems'}


def build():
    documents = {}
    sources = {}
    for path in sorted((ROOT/'specs').rglob('*.schema.json')):
        raw = path.read_bytes()
        document = json.loads(raw)
        if '$id' in document:
            documents[document['$id']] = (document, path, raw)
    schemas = {}

    def include(reference):
        if reference in schemas:
            return
        uri, fragment = urldefrag(reference)
        if uri not in documents or (fragment and not fragment.startswith('/')):
            raise ValueError('unresolved closed schema reference: ' + reference)
        document, path, raw = documents[uri]
        source = path.relative_to(ROOT).as_posix()
        sources[source] = hashlib.sha256(raw).hexdigest()
        node = document
        if fragment:
            for key in fragment[1:].split('/'):
                node = node[key.replace('~1', '/').replace('~0', '~')]
        schemas[reference] = None  # Break recursive reference expansion.
        schemas[reference] = project(node, uri)

    def project(node, base):
        if isinstance(node, bool):
            return node
        result = {}
        for key, value in node.items():
            if key == '$defs':
                continue  # Definitions are retained only when referenced.
            if key == '$ref':
                absolute = urljoin(base, value)
                include(absolute)
                result[key] = absolute
            elif key in MAP_KEYWORDS:
                result[key] = {name: project(child, base) for name, child in value.items()}
            elif key in SINGLE_KEYWORDS:
                result[key] = project(value, base)
            elif key in LIST_KEYWORDS:
                result[key] = [project(child, base) for child in value]
            else:
                result[key] = value
        return result

    roots = {}
    for relative in ROOTS:
        document = json.loads((ROOT/'specs'/relative).read_bytes())
        roots[relative] = document['$id']
        include(document['$id'])
    bundle = dict(bundle_version='1.0.0', roots=roots, sources=sources, schemas=schemas)
    return (json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    raw = build()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != raw:
            raise SystemExit('session contracts are stale')
    else:
        OUTPUT.write_bytes(raw)
    print(f'session contracts: {len(raw)} bytes sha256={hashlib.sha256(raw).hexdigest()}')


if __name__ == '__main__':
    main()
