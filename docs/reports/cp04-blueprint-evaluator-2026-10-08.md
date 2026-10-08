# CP-04 Accepted Blueprint Evaluator — 2026-10-08

Status: implemented and verified locally at `contract_verified_only`; independent review found no blocking issue within the declared D05/H15 profile. Parent CP-04 remains `partially_verified` with `no_go`.

## Accepted behavior

The owner accepted a recommendation format that explains the stack, technical work, architectural role, product outcome, covered and remaining problems, integration complexity, assumption-bound phased time ranges, and reuse versus equivalent-scope custom/current alternatives. The [acceptance record](../../evals/plugin-v1/results/cp04-v2-2026-10-08/owner-format-acceptance.json) binds the reviewed instruction and [two RU/EN examples](cp04-solution-blueprint-examples-2026-10-08.md).

This slice implements an offline captured-response evaluator. Its purpose is to catch broken source joins, role or authority changes, arithmetic errors and inconsistent structured locale bindings before semantic review. It does not execute a model, install a plugin or measure adoption time.

## Ownership and verification

Quality Evaluator owns the new evaluator, its targeted regression suite, evaluation contract and result receipt. The independent reviewer uses GPT-6 Astra with effort Medium, as requested by the owner. Primary owns acceptance and control-document updates. Existing retrieval judgments, thresholds, captures, public bundle, CP-10 surfaces and protected configuration remain outside this slice.

The implementation is [evaluate_solution_blueprint.py](../../evals/plugin-v1/evaluate_solution_blueprint.py), with [targeted regression tests](../../tests/test_plugin_solution_blueprint_eval.py) and the [predeclared evaluation contract](../../evals/plugin-v1/solution-blueprint-eval-contract.md). The validator reads explicitly selected bounded inputs; metadata paths and URLs are data. Candidate text and consistent conditional forecast values may vary without a whole-candidate hash gate. Trusted context/provenance, role boundaries and structured locale bindings remain fixed.

Observed commands, executed by Quality Evaluator against the frozen implementation:

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_solution_blueprint_eval.py -v
.venv/Scripts/python.exe -B evals/plugin-v1/evaluate_solution_blueprint.py --output evals/plugin-v1/results/cp04-v2-2026-10-08/solution-blueprint-eval-result.json
```

The suite passed 17/17 tests (exit 0). The accepted-capture CLI passed (exit 0), with two cases, no contract issues and `contract_verified_only`. The [receipt](../../evals/plugin-v1/results/cp04-v2-2026-10-08/solution-blueprint-eval-result.json) binds input, instruction, acceptance, evaluator, test and contract hashes. It records owner format acceptance while keeping semantic review required and promotion, human calibration, forecast calibration and installed-runtime verification false.

Observable RED cases included a duplicate pilot being accepted, bool/numeric equality bypassing locale binding, and an oversized integer escaping the typed-number guard. The final GREEN suite covers these regressions, source ownership, authority changes, stale canonical locale bindings, alternatives jointly adopted, partial-context invented totals, arithmetic/units/calendar errors and bounded sanitized CLI failures. A different valid conditional forecast also passes; tests do not merely freeze example bytes.

The [independent Astra/Medium review](../../evals/plugin-v1/results/cp04-v2-2026-10-08/solution-blueprint-evaluator-independent-review.json) confirmed all four frozen hashes and found no blocking P1/P2 issue within the declared profile. The reviewer independently ran the 15 pure in-memory unittest methods: 15/15 passed, exit 0, 0.244 seconds. Two CLI tests were excluded from that independent run to preserve read-only operation; the owner's 17/17 suite and CLI result remain separately attributed to Quality Evaluator.

Primary's bounded check confirmed all 41 protected baseline hashes unchanged, receipt source hashes/evidence flags and report links valid, and the format acceptance retained its false calibration/promotion flags. Focused `git diff --check` passed. Existing Python launcher-location warning remained nonfatal; no environment repair was attempted.

## Evidence limits

Passing structure and arithmetic cannot establish natural-language usefulness, source-claim meaning, privacy of free text, forecast accuracy or translation semantics. The existing examples provide structured locale bindings for selected fields; architecture and complexity prose still need semantic review. The maximum automated verdict is `contract_verified_only`.

The [v2 implementation report](cp04-v2-implementation-2026-10-08.md) retains the failed file/media retrieval stratum, synthetic warm-latency gate and unresolved joined-lifecycle evidence. Format acceptance does not replace human rubric calibration or CP-11/15 acceptance.

The evaluator is verified inside this repository bundle. Its provenance hashing expects the evaluator, test and contract files; missing files in a future standalone package could abort outside the typed input handler. No standalone-distribution robustness is claimed. The frozen profile covers D05/H15, and these same-role alternatives do not establish positive complementary-set quality.

## Next quality work

Retain this accepted format and executable guard while addressing the existing retrieval-stratum and capacity failures with prospectively declared experiments. Do not relabel exposed held-out cases or weaken thresholds to obtain a pass. Semantic/human calibration and actual joined lifecycle remain separate evidence requirements.
