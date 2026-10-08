# CP04 Source-Pinned Successor Runner V2

`run_quality_v2.py` owns a separate, offline successor evaluation. Frozen V1 plan,
rubric, runner, captures and thresholds remain unchanged. This envelope is not C8
captured-result compatibility, human acceptance, or product promotion evidence.

## Freeze and source boundary

The prospective `quality-plan-v2.json` and `quality-judgments-v2.json` bind goals,
queries, split and exhaustive routed universes before rankings. Every routed ID,
including secondary classification membership, must have an explicit integer
grade 0/1/2/3, constraint assessment, rationale and source pointer/value/reference.
The runner validates source hashes and exact card evidence values before capture.
Unjudged returned IDs remain invalid with null official metrics. Unknown adoption
fit is separate from relevance. Source-based grade zero is not proof that upstream
lacks a capability.

The exact public tuple, artifacts, candidate caps, lexical baseline, scale protocol
and numeric thresholds must equal frozen V1. Queries use the existing `make_query`
mapping and empty optional constraints. Ranking, normalization, taxonomy filtering,
FTS5 and evidence selection reuse existing source-owned functions. Literal ranking
transport placeholders are not measured BM25/RRF.

`--predeclare` exclusively writes declaration bytes binding plan/oracle file and
canonical hashes, every query/case, split, thresholds and source/method hashes.
`--run-development` then executes development semantic cases plus separately
identified identity probes. Held-out runs require an owner-authored gate with
accepted=true, reviewer identity, exact declaration hash, development capture byte
hash and oracle review hash. This gate records a review assertion; it cannot
authenticate a human reviewer. No held-out tuning is allowed.

## Metric interpretation

Raw constrained semantic Recall@12 and nDCG@12 use the full goal-specific universe,
grade-positive non-denied IDs, and original ranks. Denied hits occupy their original
positions but have zero constrained gain; ranks are never compacted. Unknown
constraint judgments remain conditional reference candidates per the matcher.
The unconditional topical-grade metrics are retained separately as diagnostics.
This V2 applicability change is predeclared and preserves every numeric threshold
and V1 result. The same rule applies to candidate and literal baseline.
Typed retrieval failures produce null;
valid zero-hit queries with relevant judgments score zero. Official macro metrics
remain null if any case/denominator is unavailable. Complete expected case coverage
is a separate gate.

Exact identity probes are excluded from semantic macros. Historical alias success
is measured only on alias cases, so other exact identity probes cannot hide a
failing alias. Archived/denied exact identities may succeed in raw lookup while
their adoption in the detailed pack fails. Separate exact identity results and
eligible detail-pack diagnostics never replace raw semantic metrics.

Held-out semantic coverage includes all 14 containers and declared semantic tags.
Historical aliases belong to the separate identity requirement and retain their
unchanged success threshold. Development strata are reported including missing
ones; development does not silently substitute for held-out coverage. Runtime route
coverage executes every registry route separately and cannot establish relevance.
Taxonomy membership of semantic fixtures does not itself prove union-route queries.

Survival denominator is grade-positive, non-denied raw top12 IDs; numerator is the
same IDs present in the detailed pack. Hard constraint errors and false exclusions
remain independent assessments; budget truncation is separate. Both raw ranking
and detailed selection/exclusions, full actual result/pack and exact bytes are kept.

## Capacity and evidence ceiling

Actual2500 timing is 30 cold new-process samples plus30 warm samples following one
discarded warmup, cycling development cases. `perf_counter_ns` surrounds existing
`retrieval.retrieve` only; imports/process startup and pack composition are excluded.
Connections are immutable and new per call; OS cache is not flushed. Nearest-rank
p50/p95, every sample/status/count, exact Python/SQLite/OS and processor are retained.
One read-only Windows CPU registry query supplies a model string if available.
Memory is max controller/child lifetime PeakWorkingSetSize; includes validation and
fixture/capture preparation, not an isolated SQLite allocation. Query+pack byte
counts exclude host instructions/history and do not establish total model context.
Token counts and provider cost are null because no tokenizer/provider is measured.

Synthetic10000 is an isolated `.codex-tmp/cp04-v2-headroom` full card/index/manifest
fixture with four deterministic public-text replicas, distinct positive identities,
synthetic_fixture corpus markers, fixture evidence references and separate pins.
The public builder's `project_card` owns search field projection. The isolated DB
reuses production index schema and replaces only its fixed metadata CHECK values
2500/catalog_snapshot with10000/synthetic_fixture. No public index/card/manifest is
overwritten. Existing runtime accepts that separately pinned synthetic corpus.
Synthetic timing measures raw retrieval only; synthetic pack context/runtime memory
and relevance/usefulness are not inferred. Original threshold comparisons remain
unchanged and failed limits remain failures.

## Commands and outputs

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_quality_runner_v2.py -v
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v2.py --predeclare
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v2.py --run-development
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v2.py --run-held-out --gate evals/plugin-v1/results/cp04-v2-2026-10-08/heldout-gate.json
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v2.py --measure-actual
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v2.py --route-coverage
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v2.py --measure-headroom
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v2.py --summarize
```

Files are exclusively created under the successor result directory. Existing
captures cannot be replaced. Exit0 means valid declaration or measured local
evidence requiring acceptance; exit1 means retained no_go evidence; exit2 means
invalid/unavailable check. All promotion flags remain false. Saved/published joined
state, browser/no-call locale switching, paired narrative meaning, integration
usefulness and actual human calibration require separate evidence.
