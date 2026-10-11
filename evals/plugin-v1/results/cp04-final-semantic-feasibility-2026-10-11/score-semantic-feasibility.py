"""Score the frozen one-goal model proposal separately from native retrieval."""
import hashlib
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
input_path = root / 'work/cp04-final/semantic-feasibility-input.json'
output_path = root / 'work/cp04-final/semantic-feasibility-output.json'
source_path = root / 'evals/plugin-v1/final-quality-prospective-2026-10-11.json'
payload = json.loads(input_path.read_bytes())
output = json.loads(output_path.read_bytes())
assert output['input_sha256'] == hashlib.sha256(input_path.read_bytes()).hexdigest()
ids = [row['repository_id'] for row in payload['candidates']]
order = output['candidate_order']
assert len(order) == len(ids) and len(set(order)) == len(ids) and set(order) == set(ids)
spec = importlib.util.spec_from_file_location('cp04_semantic_probe_score', root / 'evals/plugin-v1/run_final_quality.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
case = next(row for row in json.loads(source_path.read_bytes())['cases'] if row['case_id'] == 'PROSPECTIVE-HOLD-08')
score = runner.rank(order, case['judgments'], case['k'])
receipt = {'evidence_kind': 'single_exposed_goal_agent_model_order_feasibility',
           'activation': False, 'promotion_ready': False, 'human_acceptance': False,
           'native_scores_or_order_modified': False,
           'source_hashes': {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in (input_path, output_path, source_path, Path(__file__))},
           'preview_bytes': len(input_path.read_bytes()), 'candidate_order': order,
           'experimental_ranking': score,
           'limits': ['One exposed goal only; no regression, fresh held-out, runtime, latency or human verdict',
                      'Model input omitted oracle judgments; root computes metrics after the proposal',
                      'Development subagent execution is not an activated shipped host selection path',
                      'New decision-order semantics require a reviewed versioned contract before production']}
target = root / 'evals/plugin-v1/results/cp04-final-semantic-feasibility-2026-10-11'
target.mkdir()
for path in (input_path, output_path, Path(__file__)):
    (target / path.name).write_bytes(path.read_bytes())
with (target / 'conclusion.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(receipt, stream, indent=2, ensure_ascii=False, allow_nan=False)
    stream.write('\n')
print(json.dumps(score))
