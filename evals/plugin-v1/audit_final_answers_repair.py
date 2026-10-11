"""Audit the successor without rewriting the original audit driver or captures."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('prior_answer_audit',ROOT/'evals/plugin-v1/audit_final_answers.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
audit.OUTPUT=ROOT/'evals/plugin-v1/results/cp04-final-answers-repair-2026-10-11'
if __name__=='__main__':audit.audit()
