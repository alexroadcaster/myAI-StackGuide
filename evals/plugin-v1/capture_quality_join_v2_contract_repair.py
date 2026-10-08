"""Separately declared exact-card evidence compatibility repair join.

Preserves original captures, sources and failures. The changed test helper uses
card-scoped public evidence, project-only evidence and source-owned activity.
The actual writer, schemas and publisher remain the original pinned versions.
"""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('cp04_join_contract_repair_original',
    ROOT / 'evals/plugin-v1/capture_quality_join_v2.py')
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def declaration():
    runner = original.runner
    scorer = runner.scorer
    old = scorer.load_json(original.OUTPUT / 'join-declaration.json')
    for source_path, digest in old['source_hashes'].items():
        if source_path != 'tests/test_plugin_contracts.py':
            scorer.require(scorer.file_sha256(ROOT / source_path) == digest, 'unchanged original join source drift')
    frozen = scorer.load_json(original.OUTPUT / 'declaration.json')
    for source_path, digest in frozen['source_hashes'].items():
        scorer.require(scorer.file_sha256(ROOT / source_path) == digest, 'frozen capture source drift')
    scorer.require(scorer.file_sha256(original.OUTPUT / 'development-observations.json') == old['observation_file_sha256'],
                   'actual development capture changed')
    paths = ('evals/plugin-v1/capture_quality_join_v2_contract_repair.py',
        'tests/test_plugin_contracts.py', 'tests/test_plugin_evidence_scope.py',
        'scripts/build_plugin_catalog.py', 'data/catalog_manifest.json')
    return {'schema_version': 'cp04_join_contract_repair_declaration_v2',
        'source_hashes': {path: scorer.file_sha256(ROOT / path) for path in paths},
        'unchanged_original_join': old,
        'previous_artifact_hashes': {name: scorer.file_sha256(original.OUTPUT / name) for name in
            ('declaration.json', 'join-declaration.json', 'join-failure.json', 'join-repair-amendment.json',
             'join-repair-declaration.json', 'join-repair-failure.json')},
        'approved_corrections': ['synthetic gaps=[]; unknown-context assumption retained',
            'public evidence resolution scoped to numeric repository identity plus local evidence ID',
            'unowned references require exactly one project/public candidate',
            'project path claims stay project-only; allowlisted presentation pointers bind explicit owner',
            'section evidence pointers cover descendants, never root or sibling prefix',
            'catalog_snapshot activity origins derived from unchanged canonical source builder/manifest'],
        'unchanged': ['actual query/result/pack', 'judgments', 'thresholds', 'runtime', 'schemas',
                      'public assets', 'writer', 'publisher'],
        'output_mapping': 'join-* -> join-contract-repair-*',
        'project_fixture': '.codex-tmp/cp04-v2-join-contract-project',
        'commands': ['.venv/Scripts/python.exe -B evals/plugin-v1/capture_quality_join_v2_contract_repair.py --predeclare',
                     '.venv/Scripts/python.exe -B evals/plugin-v1/capture_quality_join_v2_contract_repair.py --run'],
        'human_acceptance': False, 'browser_observed': False, 'cp11_complete': False, 'promotion_ready': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--predeclare', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    runner = original.runner
    try:
        declared = declaration()
        if args.predeclare:
            runner.write_json('join-contract-repair-amendment.json', declared)
            print(json.dumps({'declaration_sha256': runner.scorer.digest(declared)}))
            return 0
        runner.scorer.require(runner.scorer.load_json(original.OUTPUT / 'join-contract-repair-amendment.json') == declared,
                              'predeclared join contract repair changed')
        construct_original = original.joined_state
        write_original = runner.write_json

        def construct(case, capture, manifest):
            state = construct_original(case, capture, manifest)
            runner.scorer.require(state['brief']['observations']['gaps'] == ['No private project inspected.'],
                                  'original synthetic gaps changed')
            state['brief']['observations']['gaps'] = []
            return state

        def write(name, value):
            if name == 'join-declaration.json':
                value['contract_repair_amendment_sha256'] = runner.scorer.digest(declared)
                value['source_hashes'].update(declared['source_hashes'])
            return write_original(name.replace('join-', 'join-contract-repair-', 1), value)

        original.joined_state = construct
        original.PROJECT = ROOT / declared['project_fixture']
        runner.write_json = write
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = original.main()
        print(buffer.getvalue(), end='')
        if code != 0 and not (original.OUTPUT / 'join-contract-repair-failure.json').exists():
            write_original('join-contract-repair-failure.json', json.loads(buffer.getvalue().strip().splitlines()[-1]))
        return code
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({'verdict': 'invalid_input_or_join_failure', 'reason': str(error), 'promotion_ready': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
