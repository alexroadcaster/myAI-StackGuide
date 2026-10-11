"""Reuse the 30 cold/30 warm local resource protocol at a fresh destination.

The source fixture and subprocess recipe are unchanged; no model is invoked.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'evals/plugin-v1/measure_final_host_decision.py'
spec = importlib.util.spec_from_file_location('allocation_resource_recipe', SOURCE)
recipe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recipe)
# The reused recipe launches cold samples via __file__ and pins that driver.
# Route both through this successor; the runtime-ready receipt also pins SOURCE.
recipe.__file__ = str(Path(__file__).resolve())
recipe.OUT = ROOT / 'evals/plugin-v1/results/cp04-final-host-allocation-resource-2026-10-11/resource-check.json'

if __name__ == '__main__':
    recipe.main()
