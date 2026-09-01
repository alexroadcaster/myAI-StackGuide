# C8/C9 Offline Retrieval Compatibility Scorer

Version: `retrieval_scenarios_v2` / `retrieval_captures_v2`. Evidence owner: Quality Evaluator. This development tool consumes captured C9 V2 objects; it does not import plugin runtime, execute retrieval, call providers, resolve network references, or write reports. The four checked-in captures are authored synthetic contract examples, not observed executions. They use the atomic card/activity/policy/index V2 tuple without a parallel shadow format; V1 captures remain historical evidence only.

## Invocation And Dependencies

Run with Python and development-only `jsonschema` / `referencing` available. These packages must never be added to the stdlib-only plugin runtime. Missing validation is exit 2, not skip or success.

```powershell
python -B evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json
python -B evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json --results tests/fixtures/plugin_retrieval_eval.json
python -B -m unittest discover -s tests -p test_plugin_retrieval_eval.py -v
```

Inputs are UTF-8 JSON objects, each limited to 2 MiB. Duplicate keys, nonfinite numbers, unexpected fields, stale schema/case pins, incomplete/duplicate case records and invalid C9 objects are rejected. CLI errors do not print payloads. All schema references must resolve in the repository-only Draft 2020-12 registry; no input reference is followed. File arguments are explicit caller-selected local inputs; they are not taken from case content.

`evals/scenario.schema.json` owns the case envelope; it references the real C9 query and index-manifest schemas. `evals/result.schema.json` owns the capture envelope; it references the real C9 retrieval-result and evidence-pack schemas. Its evidence kind intentionally permits only `synthetic_contract_capture` for this bounded release. Actual CP-11 captures need an explicit versioned extension and provenance review before a product quality run. Do not relabel synthetic captures as observations.

The `contract_set_sha256` is SHA-256 of a canonical mapping from repository-relative paths to exact-file-byte hashes for all `specs/**/*.schema.json` plus both C8 schemas. `case_set_sha256` hashes the complete canonical scenario object. Canonical serialization is sorted keys, compact separators, UTF-8, `ensure_ascii=False`, `allow_nan=False`. C9 query digests follow that serialization. C9 artifact pins remain exact-file-byte hashes; synthetic index hashes are labels, not proof of a built index. Change pins deliberately after source review; never rewrite stale pins during grading.

## Structural Versus Relational Checks

Draft 2020-12 validation uses format checks and an explicit extension for declared `x-max-utf8-bytes`, including referenced nested objects. Separate semantic checks pair run/query/Brief IDs, query digest, manifest/policy/taxonomy pins, route, executed variants, canonical IDs, contiguous ranks, RRF scores, aggregate hits, card traces and inclusion/exclusion coverage. They reject failure disguised as no-match, success with null index pins, and broken measurement units/allocations. Bounds remain 60 fetched hits across variants, 12 detailed cards, 48 KiB evidence and 88 KiB controlled input. These ceilings remain uncalibrated.

`measurements.evidence_pack_bytes` is computed from the supplied pack. Other allocations may be null when the source bytes were not captured. `plugin_input_bytes` is a sum only when every allocation is measured. Latency, memory and token counts require their method/tokenizer, otherwise both value and method are null. Bytes are not tokens. Host instructions, history and generated output remain outside controlled input. Capture assertions are not proof of provenance or runtime routing.

## Metrics And Compatibility Verdict

Report per case; no synthetic-to-product macro average or calibrated quality threshold is defined. Recall@k uses all independently judged IDs with grade greater than zero as denominator, including unretrieved IDs. nDCG@k uses `(2**grade - 1) / log2(rank + 1)` with the ideal ranking over the same complete judgments. Zero relevant/ideal denominators yield null. Typed retrieval failure yields `ranking=null`; a valid zero-hit query with relevant judgments yields zero. Unjudged returned IDs fail rather than silently receiving grade zero.

Hard-constraint violations count included cards independently judged denied. False exclusions count independently allowed candidates excluded for constraint/mandatory-fact/archived/unavailable reasons; pack-budget truncation is separate and not automatically a false constraint exclusion. Runtime eligibility labels never define expected judgments. Expected status mismatch or either constraint error fails compatibility, regardless of ranking metrics.

Output is one JSON object on stdout: `schema_version=retrieval_score_v2`, evidence kind, `verdict=synthetic_compatibility_only`, `promotion_ready=false`, `quality_thresholds_calibrated=false`, overall `passed`, and `records` with case ID, status match, ranking metrics, constraint errors, observed capture counts/bytes and compatibility. Exit 0 means valid cases or no failed compatibility cases; exit 1 means valid captures with mismatched expected status/constraint judgments; exit 2 means invalid input or unavailable validation. Exit 0 never means quality or runtime acceptance.

## Pending Quality And Language Gates

`rubric.json` preserves the 16/20 human target, no critical dimension below 1, and zero critical failures. Human calibration examples, actual catalog judgments, development/held-out separation, lexical/filter baseline, aggregate reporting, retrieval thresholds, scale methodology and actual CP-11 provenance remain pending. Four tiny known-answer cases verify the scorer only. This does not close all CP-04 work.

The registered RU/EN presentation case is distinct from lexical RU/EN retrieval. CP-03 tests check canonical binding, partial coverage, revisions and immutability. Human review must still judge negation, uncertainty, source attribution, authority and integration usefulness. No display switch, state preservation in a browser, translation quality, latency or model execution is claimed by static cases.
