"""Prospective allocation successor: unchanged formal inputs and 4+8 capture.

Reuse the frozen cardinality recipe; preserve its original producer and outputs.
Only source authority and the destination change. No retries or score transfer.
"""
import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'evals/plugin-v1/run_final_host_calibration_cardinality.py'
spec = importlib.util.spec_from_file_location('allocation_formal_recipe', SOURCE)
recipe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recipe)
recipe.OUTPUT = ROOT / 'evals/plugin-v1/results/cp04-final-host-calibration-allocation-2026-10-11'
recipe.shared.OUTPUT = recipe.OUTPUT
original_declaration = recipe.declaration


def declaration():
    value = original_declaration()
    value['schema_version'] = 'cp04_host_calibration_allocation_declaration_v1'
    value['outer_contract_method'] = recipe.decision.METHOD
    value['scope'] = ('Four unchanged formal inputs; new allocation contract; '
                      'four actual full-pool orders and eight actual RU/EN compositions.')
    value['predecessor'] = 'cp04-final-host-calibration-cardinality-2026-10-11'
    authorities = [Path(__file__), SOURCE,
                   ROOT / 'evals/plugin-v1/host-allocation-eval-contract-2026-10-11.json',
                   ROOT / 'work/cp04-final/allocation-product-review.json',
                   ROOT / 'work/cp04-final/host-allocation-runtime-ready.json']
    for path in authorities:
        value['source_hashes'][path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return value


recipe.declaration = declaration

if __name__ == '__main__':
    recipe.main()
