# CP-04 development-only query-composition ablation V3

Quality Evaluator owns the new runner, this contract, its named unit tests and
exclusive result files in `results/cp04-v3-2026-10-08/query-variants-development/`.
This is a development experiment over exposed cases, never a fresh held-out run,
human calibration, search promotion or CP-04 closure.

## Frozen inputs and prospective comparison

Use exactly V2 D01-D10 with unchanged goals, terms, judgments, taxonomy universes,
constraints, k, numeric thresholds and source/card/index/manifest/policy pins.
No old labels, captures or summaries may be replaced. Existing V2 grade-one
weak/unknown references remain positive for this comparison. A prospective source
oracle correction is another experiment, not this ablation.

The runner's explicit `PARTITIONS` registry contains two nonempty disjoint groups:
intent-specific vocabulary and context vocabulary. Their exact union equals the
original case terms; neither spelling changes, new synonyms, repository names nor
repeated terms are allowed. D01 uses named browser engines; D02 mobile platform;
D03 React; D04 isolation; D05 Go; D06 .NET; D07 recovery/protocol; D08 browser and
client technologies; D09 media/EXIF; D10 optimization/allocation. These groupings
are development-only hypotheses, never derived from held-out rankings.

Three arms share the same canonical terms, source universes, constraints and caps:

1. Control: unchanged single-OR production FTS5 query.
2. Candidate: intent then context variants, production equal-weight RRF, existing
   request-order allocation and unchanged BM25/index/policy. The partition may
   change which hits fit the shared fetched-hit cap; all variant traces are kept.
3. Literal: unchanged `literal-field-or-v1` over the original union of terms and
   existing taxonomy filter, tie-breaker, matcher and evidence pack adapter.

The existing field-content difference is retained and disclosed: FTS category
labels include category IDs plus titles; literal labels contain titles only.
Literal placeholders are never reported as observed FTS5/BM25 scores.

## Declaration, observations and scoring

`--predeclare` exclusively creates `declaration.json` before any retrieval.
It binds all current exact source bytes, old frozen input/result hashes, thresholds,
partitions and both queries per case. It does not require runtime source bytes to
equal a historical declaration: the separately assigned runtime cache change is
bound by its current hash and checked through actual control captures.

`--run-development` rejects any declaration drift or existing result target before
retrieval. Each arm retains full ranked IDs, detailed cards, exclusions, matched
fields, queries, counts, request caps, pack bytes and survival. Production FTS arms
retain observed per-variant BM25/ranks and RRF scores. Historical control comparison
checks status, complete candidates/scores/fields, executed variants, hit counts,
truncation, selected card IDs and exclusions. Historical literal comparison checks
ranked/selected IDs and exclusions. Different run/pack IDs and elapsed times are
expected and do not enter ranking equivalence.

V2 constrained Recall@12/nDCG@12 arithmetic is reused: non-denied positive IDs form
the denominator, denied hits retain their original rank with zero gain, unjudged
returned IDs invalidate official metrics. Raw unconditional diagnostics and pack
survival remain visible. Source assertions cover every routed ID independently of
the returned ranking. No unknown label receives an implicit zero.

A development candidate is worth a prospective held-out review only if both macro
metrics meet the unchanged zero-delta non-regression gates against both control
and literal, historical equivalence holds and status, privacy/constraint/exclusion,
dedupe and pack-survival checks pass. Per-case regressions remain reported. All
held-out/global-stratum quality thresholds are preserved in declaration but cannot
be evaluated by these ten exposed cases. Every promotion flag remains false.

Single sequential `retrieve` elapsed values are diagnostics, not cold/warm p95
capacity evidence. No synthetic 10k test, model/provider/network call, installation,
state write, browser check, calibration or fresh held-out capture occurs here.

## Commands and evidence handling

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_query_variants_v3.py -v
.venv/Scripts/python.exe -B evals/plugin-v1/run_query_variants_v3.py --predeclare
.venv/Scripts/python.exe -B evals/plugin-v1/run_query_variants_v3.py --run-development
```

Outputs are exclusively created as `declaration.json`,
`development-observations.json` and `development-summary.json`. A scoped execution
receipt records setup errors separately from expected RED. Exit 0 is declaration
success or a development-only candidate; exit 1 retains measured development
non-regression failure; exit 2 is invalid/unavailable evidence. Preserve failures,
do not edit partitions after capture or reuse a stale declaration. Future goals
listed in the diagnosis are unsealed proposals and cannot establish held-out
independence without prospective Product Planner review/freeze.
