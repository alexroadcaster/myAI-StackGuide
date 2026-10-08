"""One authorized serialized recheck of the unchanged frozen capacity method.

Original failed measurements remain immutable. This is only the SQL primitive
layer; production reader compatibility and detailed card-pack capacity are open.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('cp04_headroom_recheck_original',
    ROOT / 'evals/plugin-v1/measure_quality_headroom_v2.py')
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def declaration(plan):
    runner = original.runner
    previous = runner.scorer.load_json(runner.OUTPUT / 'headroom-adapter-declaration.json')
    runner.scorer.require(previous == original.declaration(plan), 'original adapter source/fixture changed')
    return {'schema_version': 'cp04_headroom_single_recheck_declaration_v2',
        'original_adapter_declaration_sha256': runner.scorer.digest(previous),
        'original_failed_performance_sha256': runner.scorer.file_sha256(runner.OUTPUT / 'headroom-adapter-performance.json'),
        'recheck_source_sha256': runner.scorer.file_sha256(Path(__file__)),
        'original_source_and_fixture_pins': previous,
        'reason': 'One quiet serialized recheck authorized after possible overlapping local captures.',
        'method_changes': [], 'threshold_changes': [], 'maximum_rechecks': 1,
        'quiet_condition': 'No other local eval captures or test suites run during this recheck.',
        'commands': ['.venv/Scripts/python.exe -B evals/plugin-v1/recheck_quality_headroom_v2.py --predeclare',
                     '.venv/Scripts/python.exe -B evals/plugin-v1/recheck_quality_headroom_v2.py --run']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--predeclare', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    runner = original.runner
    try:
        plan = runner.scorer.load_json(runner.HEADROOM / 'synthetic-plan.json')
        declared = declaration(plan)
        if args.predeclare:
            runner.write_json('headroom-recheck-declaration.json', declared)
            print(json.dumps({'declaration_sha256': runner.scorer.digest(declared)}))
            return 0
        runner.scorer.require(runner.scorer.load_json(runner.OUTPUT / 'headroom-recheck-declaration.json') == declared,
                              'recheck declaration changed')
        # Persist before timing so a crash cannot silently authorize a second run.
        runner.write_json('headroom-recheck-started.json', {'declaration_sha256': runner.scorer.digest(declared),
            'attempt': 1, 'maximum_attempts': 1})
        result = original.measure(plan)
        result['recheck_declaration_sha256'] = runner.scorer.digest(declared)
        result['original_failure_preserved'] = True
        result['single_serialized_recheck'] = True
        runner.write_json('headroom-recheck-performance.json', result)
        print(json.dumps({'verdict': result['verdict'], 'cold_p95_ms': result['cold_p95_ms'],
            'warm_p95_ms': result['warm_p95_ms'], **original.evidence_ceiling()}))
        return 1 if result['verdict'] == 'no_go' else 0
    except (OSError, ValueError, KeyError, original.sqlite3.DatabaseError, original.subprocess.SubprocessError) as error:
        print(json.dumps({'verdict': 'invalid_input_or_unavailable_check', 'reason': str(error)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
