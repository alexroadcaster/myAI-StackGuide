# C8/C9 Offline Retrieval Compatibility Scorer

Version: `retrieval_scenarios_v2` / `retrieval_captures_v2` plus `retrieval_quality_plan_v1`. Evidence owner: Quality Evaluator. This development tool validates the frozen CP-04 quality design and consumes captured C9 V2 objects; it does not import plugin runtime, execute SQLite retrieval, call providers, resolve network references, or write reports. The four checked-in captures are authored synthetic contract examples, not observed executions. They use the atomic card/activity/policy/index V2 tuple without a parallel shadow format; V1 captures remain historical evidence only.

## Invocation And Dependencies

Run with the ignored project-local `.venv`. Bootstrap once with `python -m venv .venv` and `.venv\Scripts\python.exe -m pip install --requirement requirements-dev.txt`. The pinned development-only `jsonschema` / `referencing` packages must never be added to the stdlib-only plugin runtime. The CP-04 quality-plan gate uses its bounded stdlib validator so it does not alter the accepted C8 schema-set pin. Missing required C8 validation is exit 2, not skip or success.

```powershell
.venv\Scripts\python.exe -B evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json
.venv\Scripts\python.exe -B evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json --results tests/fixtures/plugin_retrieval_eval.json
.venv\Scripts\python.exe -B evals/plugin-v1/evaluate_retrieval.py --quality-plan evals/plugin-v1/quality-plan.json
.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_plugin_retrieval_eval.py -v
```

C8 inputs are UTF-8 JSON objects, each limited to 2 MiB. Duplicate keys, nonfinite numbers, unexpected fields, stale schema/case pins, incomplete/duplicate case records and invalid C9 objects are rejected. CLI errors do not print payloads. All C8 schema references must resolve in the repository-only Draft 2020-12 registry; no input reference is followed. File arguments are explicit caller-selected local inputs; they are not taken from case content.

`quality-plan.json` is validated by the CP-04-only local schema and semantic checks without adding that schema to the accepted C8 contract-set hash. The plan pins and reads only the checked-in public CP-06 manifest/cards/index/policy paths. The validator hashes the SQLite bytes but never opens or queries the database. It rejects stale bundle/rubric/taxonomy pins, nonnumeric or missing public identities, incomplete/reordered judgment pools, invalid split/strata/locale/scale declarations, invalid thresholds, contradictory allowed constraints and missing alias/description/secondary/activity provenance. Its 16 MiB trusted-card read cap is separate from the 2 MiB untrusted C8 input cap.

`evals/scenario.schema.json` owns the case envelope; it references the real C9 query and index-manifest schemas. `evals/result.schema.json` owns the capture envelope; it references the real C9 retrieval-result and evidence-pack schemas. Its evidence kind intentionally permits only `synthetic_contract_capture` for this bounded release. Actual CP-11 captures need an explicit versioned extension and provenance review before a product quality run. Do not relabel synthetic captures as observations.

The `contract_set_sha256` is SHA-256 of a canonical mapping from repository-relative paths to exact-file-byte hashes for all `specs/**/*.schema.json` plus both C8 schemas. `case_set_sha256` hashes the complete canonical scenario object. Canonical serialization is sorted keys, compact separators, UTF-8, `ensure_ascii=False`, `allow_nan=False`. C9 query digests follow that serialization. C9 artifact pins remain exact-file-byte hashes; synthetic index hashes are labels, not proof of a built index. Change pins deliberately after source review; never rewrite stale pins during grading.

## Structural Versus Relational Checks

Draft 2020-12 validation uses format checks and an explicit extension for declared `x-max-utf8-bytes`, including referenced nested objects. Separate semantic checks pair run/query/Brief IDs, query digest, manifest/policy/taxonomy pins, route, executed variants, canonical IDs, contiguous ranks, RRF scores, aggregate hits, card traces and inclusion/exclusion coverage. They reject failure disguised as no-match, success with null index pins, and broken measurement units/allocations. Policy 2.1.0 bounds are a request-selected maximum of 150 fetched hits across variants, 12 detailed cards, 160 KiB evidence and 200 KiB controlled input. Capacity sizing is owner-accepted; relevance, token, latency and usefulness remain uncalibrated.

`measurements.evidence_pack_bytes` is computed from the supplied pack. Other allocations may be null when the source bytes were not captured. `plugin_input_bytes` is a sum only when every allocation is measured. Latency, memory and token counts require their method/tokenizer, otherwise both value and method are null. Bytes are not tokens. Host instructions, history and generated output remain outside controlled input. Capture assertions are not proof of provenance or runtime routing.

## Metrics And Compatibility Verdict

Report per case; no synthetic-to-product macro average or calibrated quality threshold is defined. Recall@k uses all independently judged IDs with grade greater than zero as denominator, including unretrieved IDs. nDCG@k uses `(2**grade - 1) / log2(rank + 1)` with the ideal ranking over the same complete judgments. Zero relevant/ideal denominators yield null. Typed retrieval failure yields `ranking=null`; a valid zero-hit query with relevant judgments yields zero. Unjudged returned IDs fail rather than silently receiving grade zero.

Hard-constraint violations count included cards independently judged denied. False exclusions count independently allowed candidates excluded for constraint/mandatory-fact/archived/unavailable reasons; pack-budget truncation is separate and not automatically a false constraint exclusion. Runtime eligibility labels never define expected judgments. Expected status mismatch or either constraint error fails compatibility, regardless of ranking metrics.

Output is one JSON object on stdout: `schema_version=retrieval_score_v2`, evidence kind, `verdict=synthetic_compatibility_only`, `promotion_ready=false`, `quality_thresholds_calibrated=false`, overall `passed`, and `records` with case ID, status match, ranking metrics, constraint errors, observed capture counts/bytes and compatibility. Exit 0 means valid cases or no failed compatibility cases; exit 1 means valid captures with mismatched expected status/constraint judgments; exit 2 means invalid input or unavailable validation. Exit 0 never means quality or runtime acceptance.

For `--quality-plan`, stdout is `retrieval_quality_plan_validation_v1` with the canonical plan hash, rubric hash, full source/cards/index/policy/taxonomy/version pin tuple, exact 24-query 12/12 split, 2,500 actual rows, 10,000 synthetic headroom rows, `thresholds_predeclared=true`, `quality_observed=false` and `promotion_ready=false`. Exit 0 proves only that the design still matches checked-in public assets and its own fail-closed invariants.

## Frozen Quality Design

`quality-plan.json` freezes 24 provenance-backed public-card cases: 12 development and 12 held-out. The held-out half cannot tune query terms, aliases, field weights, thresholds or acceptance logic. Cases span all 14 declared navigation containers, thin/middle/dense leaves, baseline and CAT-07A expansion cohorts, historical aliases, separate upstream/catalog descriptions, secondary-assignment dedupe, activity unknowns and EN/RU lexical intent. Judgments are attached to numeric GitHub identities and checked against the exact 2,500-card snapshot. They are pre-execution relevance judgments, not retrieval observations; every returned candidate in a future scored capture must be independently judged or the run is invalid.

The explicit `literal-field-or-v1` baseline applies NFKC + casefold, literal substring OR over the nine declared searchable card fields, one point per distinct term/field pair and numeric GitHub ID as the tie-breaker. It shares the frozen cases, judgments, constraints, `k=12`, cards and pins with the FTS5 candidate. The evaluator exposes this deterministic baseline function but the checked-in plan-validation command does not execute it against the catalog.

Predeclared held-out thresholds are macro Recall@12 >= 0.75 and nDCG@12 >= 0.65; the candidate cannot regress either metric versus the lexical baseline. Each required stratum must reach Recall@12 >= 0.60 and nDCG@12 >= 0.50. Hard-constraint violations, false exclusions and duplicate canonical IDs must be zero; alias success is 1.0 and evidence-pack survival is at least 0.90. Deterministic route coverage remains all 111 leaves and all 14 containers. These are initial acceptance thresholds, not observed scores.

The exact 2,500-card corpus is the future relevance/capacity run. A separately labeled deterministic 10,000-row synthetic corpus is headroom only. Both use 30 samples and record cold/warm p50/p95, method, hardware/runtime, peak memory, index bytes and serialized bytes. Initial ceilings are 100 ms warm p95 and 250 ms cold p95 for the actual bundle, 200/500 ms for synthetic headroom, 256 MiB peak memory and 64 MiB index bytes. OS cache state must be recorded; it is not claimed flushed. Synthetic outcomes cannot satisfy relevance or usefulness.

`rubric.json` preserves the 16/20 human target, no critical dimension below 1 and zero critical failures. It now freezes 0/1/2 anchors, paired founder/engineer/activity/dedupe cases, independent Quality Evaluator and Product Planner first passes, disagreement adjudication and required capture evidence. The anchor protocol is frozen but no recommendation has been human-scored: `calibrated=false`, `observed_results=false`.

The registered RU/EN presentation case is distinct from lexical RU/EN retrieval. Future reviewers compare RU and EN against the same canonical capture and preserve IDs/order, constraints, roles, evidence, negation, uncertainty and execution authority. The display switch must make no scan/retrieval/model/translation/network/domain-write call. CP-03 static checks do not prove browser state preservation or semantic equivalence; CP-11/15 must capture those results.

## Historical Design Evidence Ceiling And Future C8 Capture Rule

At design freeze the plan completed CP-04 design only: no actual quality route, performance, browser or human result was observed. The existing C8 schemas still admit only synthetic captures. CP-11 captures require their separately owned C8 schema/provenance extension; the diagnostic runner below does not alter or relabel that contract. CP-15 independently applies human/RU-EN/usefulness acceptance. `promotion_ready=false` remains mandatory.

## CP-04 Frozen-v1 Actual Diagnostic Runner (2026-10-08)

`run_quality.py` executes the exact public 2,500-card bundle offline through existing
`retrieval.retrieve` and `context_pack.build_evidence_pack`. It has no model,
provider, install, network, writer, renderer or index rebuild path. Its independent
envelopes are `cp04_quality_declaration_v1`, `cp04_quality_observation_v1` and
`cp04_quality_summary_v1`; none is a C8 result or product promotion evidence.

Predeclared mapping: `target_category_id` becomes `taxonomy_route_id`, exact frozen
`query_terms` form one `q1` OR variant, and `query_locale` becomes `language`.
The six optional hard constraints remain empty/null. The frozen default archived,
availability and unknown-evidence behavior is applied by the existing matcher and
pack builder; no persona or goal is converted into inferred constraints. Both
routes use the same taxonomy registry membership and numeric identity dedupe;
baseline filtering includes primary and secondary assignments. No outputs are
filtered to `judgment_pool_ids`.

The existing literal baseline retains its default limit of 60. Its explicit upper
ceiling now reads `limits.max_retrieved_hits` from the canonical retrieval policy,
so the frozen plan's explicit 150 limit is accepted without changing ranking,
normalization, fields or tie rules. Its internal packing adapter carries literal
rank and monotonically decreasing placeholder RRF values solely to reuse the
unchanged pack selector. Those values are not observed BM25/RRF scores; the
baseline is never represented as an executed FTS5 C9 capture.

Complete raw returned rankings must be independently judged, including IDs beyond
rank 12. An unjudged ID yields `ranking=null`, `incomplete_judgments` and `no_go`;
no grade zero, rank compaction or omitted-case macro average is permitted. Typed
retrieval failure likewise yields null ranking, while a valid zero-hit query with
positive judgments scores zero. Official development/held-out macro Recall@12 and
nDCG@12 are null if any case lacks complete ranking or a metric denominator.
Separate `known_pool_recall_at_12_diagnostic` values describe observed positive-ID
coverage only and never satisfy the frozen quality thresholds.

Predeclared pack survival denominator: independently grade-positive, non-denied
IDs present in the raw top 12. The numerator is those same IDs present in the final
detailed pack. Both counts are recorded; unknown relevance and unretrieved IDs do
not establish survival. Constraint errors use independent frozen allowed/denied
facts and are explicitly limited to that judgment pool; budget exclusions remain
separate. Historical alias success means its source-pinned numeric target occurs
in raw top 12 and a denied target does not occur in the pack. Alias-only recall is
separate from useful allowed recommendations and translation meaning.

Every required tag and container is reported separately for all/development/
held-out, with missing cases null. Actual route-registry counts cover the 111
categories and 14 containers structurally; this does not claim that all those
runtime routes were queried. Actual quality queries are listed separately.

Measurement: 30 cold samples use separate local Python processes and immutable
SQLite connections, with `perf_counter_ns` around `retrieval.retrieve` only.
Process startup/import time is outside that timer. Thirty warm samples use one
process after one discarded query; the existing runtime opens a new immutable
connection per call. Cases cycle in frozen order, so these percentiles describe a
mixed workload, not a per-query SLA. Percentiles use nearest rank `ceil(p*n)`.
OS cache is not flushed and prior validation/capture has warmed it. Runtime/
OS/architecture/processor, index size, process-lifetime Windows
`GetProcessMemoryInfo PeakWorkingSetSize`, raw samples and exact canonical UTF-8
query/pack bytes are retained. Process peak includes capture preparation and is
not an isolated SQLite allocation measure. Brief/context allocations are absent;
the measured controlled input is query plus pack. Token counts and provider cost
are null. The 10,000-row synthetic headroom corpus belongs to the separate CP-11
lane and is not rebuilt here.

Commands are declared before the first capture; the plan hash is canonical JSON:

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_quality_runner.py -v
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality.py --predeclare --plan-sha256 e895c54ef78505ca6bcbe12edd7385d43351b78dfd915a238cd20ea7a9bcdaa7
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality.py --run --plan-sha256 e895c54ef78505ca6bcbe12edd7385d43351b78dfd915a238cd20ea7a9bcdaa7
```

`--predeclare` validates the plan and pins, then exclusively creates
`results/cp04-2026-10-08/declaration.json` with commands, measurement, thresholds,
source hashes and pins. `--run` requires exact equality with that declaration and
exclusively creates observations/performance/summary/artifact-hash files, preserving
earlier captures and independently owned recommendation/review files. Observation
records retain case/query hashes, raw numeric ranks, full actual C9 result and pack,
literal baseline IDs/pack, exclusions, coverage and bytes. Output directory is
fixed inside the assigned repository result lane. Exit 0 means valid declaration
or a complete local diagnostic requiring owner acceptance; exit 1 means retained
`no_go` observations; exit 2 means invalid input/protocol or unavailable check.

Human oracle calibration, same-canonical RU/EN meaning, browser/no-call switching,
saved/published recovery, synthetic headroom and broad CP-11 integration remain
separate gates. Agent self-review and agent-only independent review must retain
their identities and cannot be labeled human acceptance.

### Measurement-only repair declared before resume

The first capture retained all 24 cases, including valid `no_match` results that
fail the frozen expected `ok` status. The timing controller incorrectly aborted
when encountering such a zero-hit result. The bounded repair accepts `ok` and
`no_match` as measurable samples while leaving the quality mismatch gate intact.
It does not change terms, labels, ranks, pins, thresholds or pack selection.

`--predeclare-measurement-amendment` exclusively creates
`measurement-amendment.json`, binding exact original observation bytes and original
declaration/capture-producing source hashes separately from current measurement
source hashes. Only the runner and this contract may differ from the original
source tuple. `--resume-measurement` requires exact amendment equality and original
observation hash; it reuses those saved records to produce performance and summary,
without recapturing or overwriting queries/rankings/packs. Valid zero-hit timing
samples retain their status; expected-status mismatch remains a failed gate.

```powershell
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality.py --predeclare-measurement-amendment --plan-sha256 e895c54ef78505ca6bcbe12edd7385d43351b78dfd915a238cd20ea7a9bcdaa7
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality.py --resume-measurement --plan-sha256 e895c54ef78505ca6bcbe12edd7385d43351b78dfd915a238cd20ea7a9bcdaa7
```
