"""Explicit, separately pinned repair of one synthetic Brief gaps fixture.

Original runner/harness/declaration/failure and actual capture bytes stay frozen.
The original harness is reused with one declared state-construction correction;
schema and relation validators, locked writer and publisher remain unchanged.
"""
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / 'evals/plugin-v1/capture_quality_join_v2.py'
spec = importlib.util.spec_from_file_location('cp04_join_repair_original', path)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def main():
    scorer = original.runner.scorer
    output = original.OUTPUT
    frozen = scorer.load_json(output / 'declaration.json')
    scorer.require(scorer.file_sha256(path) == frozen['source_hashes']['evals/plugin-v1/capture_quality_join_v2.py'],
                   'original frozen harness changed')
    original_declaration = scorer.load_json(output / 'join-declaration.json')
    for source_path, digest in original_declaration['source_hashes'].items():
        scorer.require(scorer.file_sha256(ROOT / source_path) == digest, 'original join runtime/source changed')
    amendment = {'schema_version': 'cp04_join_fixture_repair_amendment_v2',
        'original_join_declaration_sha256': scorer.file_sha256(output / 'join-declaration.json'),
        'original_join_failure_sha256': scorer.file_sha256(output / 'join-failure.json'),
        'frozen_runner_declaration_sha256': scorer.digest(frozen),
        'repair_source_sha256': scorer.file_sha256(Path(__file__)),
        'reason': 'Original synthetic Brief observations.gaps contains a string; schema requires typed objects.',
        'only_state_correction': 'observations.gaps=[]; existing synthetic/no-private-inspection assumptions retained',
        'unchanged': ['actual query/result/pack bytes', 'schemas', 'relation validators', 'runtime source',
                      'locked writer', 'publisher', 'retrieval judgments', 'thresholds'],
        'output_mapping': 'join-* -> join-repair-*; preserve original files',
        'command': '.venv/Scripts/python.exe -B evals/plugin-v1/capture_quality_join_v2_repair.py',
        'promotion_ready': False}
    write_original = original.runner.write_json
    write_original('join-repair-amendment.json', amendment)
    construct_original = original.joined_state

    def construct(case, capture, manifest):
        state = construct_original(case, capture, manifest)
        scorer.require(state['brief']['observations']['gaps'] == ['No private project inspected.'],
                       'fixture repair expected value changed')
        scorer.require('Synthetic project evaluation; no private project scan or implementation.' in
                       state['brief']['assumptions'], 'unknown synthetic context disclosure missing')
        state['brief']['observations']['gaps'] = []
        return state

    def write(name, value):
        if name == 'join-declaration.json':
            value['repair_amendment_sha256'] = scorer.digest(amendment)
            value['source_hashes']['evals/plugin-v1/capture_quality_join_v2_repair.py'] = amendment['repair_source_sha256']
        return write_original(name.replace('join-', 'join-repair-', 1), value)

    original.joined_state = construct
    original.runner.write_json = write
    return original.main()


if __name__ == '__main__':
    sys.exit(main())
