# C8/C9 Offline Retrieval Compatibility Scorer

Version: `retrieval_scenarios_v2` / `retrieval_captures_v2` plus `retrieval_quality_plan_v1`. Evidence owner: Quality Evaluator. This development tool validates the frozen CP-04 quality design and consumes captured C9 V2 objects; it does not import plugin runtime, execute SQLite retrieval, call providers, resolve network references, or write reports. The four checked-in captures are authored synthetic contract examples, not observed executions. They use the atomic card/activity/policy/index V2 tuple without a parallel shadow format; V1 captures remain historical evidence only.

## Invocation And Dependencies

Run with Python. The two C8 commands and full C8 test class also require development-only `jsonschema` / `referencing`; these packages must never be added to the stdlib-only plugin runtime. The CP-04 quality-plan gate uses its bounded stdlib validator so it does not alter the accepted C8 schema-set pin. Missing required C8 validation is exit 2, not skip or success.

```powershell
python -B evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json
python -B evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json --results tests/fixtures/plugin_retrieval_eval.json
python -B evals/plugin-v1/evaluate_retrieval.py --quality-plan evals/plugin-v1/quality-plan.json
python -B -m unittest discover -s tests -p test_plugin_retrieval_eval.py -v
```

C8 inputs are UTF-8 JSON objects, each limited to 2 MiB. Duplicate keys, nonfinite numbers, unexpected fields, stale schema/case pins, incomplete/duplicate case records and invalid C9 objects are rejected. CLI errors do not print payloads. All C8 schema references must resolve in the repository-only Draft 2020-12 registry; no input reference is followed. File arguments are explicit caller-selected local inputs; they are not taken from case content.

`quality-plan.json` is validated by the CP-04-only local schema and semantic checks without adding that schema to the accepted C8 contract-set hash. The plan pins and reads only the checked-in public CP-06 manifest/cards/index/policy paths. The validator hashes the SQLite bytes but never opens or queries the database. It rejects stale bundle/rubric/taxonomy pins, nonnumeric or missing public identities, incomplete/reordered judgment pools, invalid split/strata/locale/scale declarations, invalid thresholds, contradictory allowed constraints and missing alias/description/secondary/activity provenance. Its 16 MiB trusted-card read cap is separate from the 2 MiB untrusted C8 input cap.

`evals/scenario.schema.json` owns the case envelope; it references the real C9 query and index-manifest schemas. `evals/result.schema.json` owns the capture envelope; it references the real C9 retrieval-result and evidence-pack schemas. Its evidence kind intentionally permits only `synthetic_contract_capture` for this bounded release. Actual CP-11 captures need an explicit versioned extension and provenance review before a product quality run. Do not relabel synthetic captures as observations.

The `contract_set_sha256` is SHA-256 of a canonical mapping from repository-relative paths to exact-file-byte hashes for all `specs/**/*.schema.json` plus both C8 schemas. `case_set_sha256` hashes the complete canonical scenario object. Canonical serialization is sorted keys, compact separators, UTF-8, `ensure_ascii=False`, `allow_nan=False`. C9 query digests follow that serialization. C9 artifact pins remain exact-file-byte hashes; synthetic index hashes are labels, not proof of a built index. Change pins deliberately after source review; never rewrite stale pins during grading.

## Structural Versus Relational Checks

Draft 2020-12 validation uses format checks and an explicit extension for declared `x-max-utf8-bytes`, including referenced nested objects. Separate semantic checks pair run/query/Brief IDs, query digest, manifest/policy/taxonomy pins, route, executed variants, canonical IDs, contiguous ranks, RRF scores, aggregate hits, card traces and inclusion/exclusion coverage. They reject failure disguised as no-match, success with null index pins, and broken measurement units/allocations. Bounds remain 60 fetched hits across variants, 12 detailed cards, 48 KiB evidence and 88 KiB controlled input. These ceilings remain uncalibrated.

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

## Evidence Ceiling And Future Capture Rule

The frozen plan completes CP-04 design only. No actual CP-09 route or CP-11 capture exists, no model/provider was called, no 2,500/10,000 performance run was executed, and no browser or human result was observed. Therefore `promotion_ready=false` is mandatory. CP-11 must produce the actual pinned C9 captures and baseline records without altering held-out judgments; CP-15 independently applies the human/RU-EN/usefulness rubric. Any capture-schema extension needs its separately owned contract and provenance review before scoring.
