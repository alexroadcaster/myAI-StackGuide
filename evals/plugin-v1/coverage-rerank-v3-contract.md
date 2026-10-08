# CP-04 development-only fetched-pool coverage rerank

Quality Evaluator owns `run_coverage_rerank_v3.py`, this contract,
`tests/test_plugin_coverage_rerank_v3.py` and exclusive results under
`results/cp04-v3-2026-10-08/coverage-rerank-development/`. Earlier two-variant
declaration, failed comparison, source files and all V1/V2 evidence remain immutable.

## Hypothesis and prospective method

The single-OR development captures fetched every positive ID missed from top12.
This experiment tests whether the unchanged literal baseline's distinct term-field
coverage can reorder those actual bounded FTS hits usefully. It does not append
literal-only IDs, bypass the route, search the full catalog as a candidate fallback,
or change query terms, C9 runtime, policy, weights, public cards/index or constraints.

Use exactly the exposed V2 D01-D10, unchanged labels/terms/goals/universes/pins/k
and numeric thresholds. Three arms: actual single-OR FTS control; experimental
coverage order of that control's fetched pool; unchanged literal-field-or-v1 over
the same cards and original terms. The existing source loader validates complete
routed judgments, exact source evidence, policy/index/card pairing and queries.

Candidate score counts distinct original query term/field pairs with at least one
NFKC-casefold substring match, using the existing `_baseline_fields` projection.
Repeated occurrences or topic values cannot inflate one pair. Sort descending score,
then positive numeric GitHub identity ascending. There is no BM25 tie-breaker.
Keep fetched zero-coverage IDs at the end. FTS includes category IDs and titles;
literal coverage includes titles only. This difference remains disclosed, not fixed.
Fetched caps come from the unchanged policy; missing bounded-pool IDs cannot be
recovered by this experiment even when the full literal baseline matches them.

Preserve actual C9 result/status/pins/BM25/RRF/variant ranks/matched fields. Candidate
order is a separate envelope, `transport=experimental_selection_adapter` and
`executed_c9_rrf=false`; literal-adapter placeholders permit pack selection but are
not an executed C9 ranking. The actual raw control and selection envelope are both
retained. Source/capture provenance, raw ranking and selection meaning cannot be
silently conflated.

## Freeze, checks and evidence ceiling

`--predeclare` binds the mapping, all current exact source hashes, original captures,
the failed two-variant packet, case/query hashes, numeric thresholds and pinned
public artifacts before this experiment captures any rank. `--run-development`
requires exact declaration equality and exclusive output targets. Recheck source
hashes after capture; never rewrite a declaration or old failure to obtain a pass.

Reuse unchanged V2 constrained Recall@12/nDCG arithmetic. Denied hits retain rank
positions with zero gain; unjudged results invalidate official metrics. Keep raw
unconditional diagnostics and detail-pack survival. Semantic macros contain no
identity probes, alias successes or altered labels. Report full per-case rankings,
coverage scores, actual raw scores, cards, fields, budgets and exclusions.

Worth a prospective fresh held-out review only if both macro metrics are no worse
than control AND literal using the unchanged zero-delta thresholds, historical
control/literal equivalence holds, and status/constraint/exclusion/dedupe/survival
and byte checks pass. A development pass never establishes fresh held-out quality,
human usefulness, browser meaning, runtime release or promotion. Required held-out
global/stratum thresholds stay preserved and unmeasured. No 10k benchmark,
provider/network/model, public bundle refresh or state/browser action is included.

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_coverage_rerank_v3.py -v
.venv/Scripts/python.exe -B evals/plugin-v1/run_coverage_rerank_v3.py --predeclare
.venv/Scripts/python.exe -B evals/plugin-v1/run_coverage_rerank_v3.py --run-development
```

Exit0 is a valid declaration or development-only candidate; exit1 retains measured
development failure; exit2 is invalid/unavailable evidence. All promotion flags
remain false. Results are exclusive declaration/observations/summary plus an
execution receipt. If promising, a separate owner-reviewed ranking contract must
define raw-versus-selected order and version/pin consumers before shipping; this
selection adapter does not silently change the accepted C9 RRF semantics.
