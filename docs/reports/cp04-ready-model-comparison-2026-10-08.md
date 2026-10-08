# CP-04 ready-model, input, fusion and capability comparison — 2026-10-08

Owner authorized the proposed improvements and comparison, without agents. Primary implemented and executed all experiments locally. Status: `partially_verified / development_no_go / promotion_ready=false`; canonical FTS5 remains the active route. Small-model resource improvement and source-coverage improvement are observed, but neither establishes complete CP-04 acceptance.

## What changed

- [Comparison runner](../../evals/plugin-v1/run_flashrank_comparison.py) reuses installed FlashRank0.2.10 and the existing scoring/pack validators, with TinyBERT and MiniLM in a separate ignored cache. No custom model, additional local LLM, paid API or credential. Model downloads reuse the reviewed GET-only wrapper and fixed public HF revision `858a1ac046a05663a35367eac852d7f76feeefdd`; archive/file hashes and model-repository `cc-by-sa-4.0` metadata are recorded separately from library licensing/adoption approval.
- Three EN inputs: original user goal/plain public fields; frozen request terms/plain fields; identical terms with labeled versions of the same nine fields. No facts, constraints or judgments are inferred from labels. Direct RU goals are a diagnostic fourth input. EN request terms are pre-existing fixture values, not observed host translation or RU lexical retrieval.
- Each input compares pure neural order and equal RRF with the unchanged FTS order, using current policy k, complete identical numeric ID sets and canonical-ID ties. Raw C9 is preserved; the fusion is experimental selection, not canonical rank replacement.
- [Capability facts](../../research/cp04-search-capability-enrichment-2026-10-08.json) add qualified Kotlin support for five backend alternatives, with source URLs, observation date, component scope and limitations. The [coverage runner](../../evals/plugin-v1/run_source_coverage_comparison.py) updates only `use_cases` in an in-memory index copy and rebuilds temporary FTS. It reuses the actual field projection, query compiler, routed variant SQL, weights and caps. Original ordered IDs must equal the frozen production capture before changes.
- The [composition diagnostic](../../evals/plugin-v1/run_source_enriched_rerank.py) compares TinyBERT on the original versus enriched Kotlin pools/cards. All are explicit temporary experiments, not compatible regenerated catalog packages. Evidence packs continue using original pinned cards; newly qualified capabilities are retained separately.

## Frozen method and development quality

The [comparison declaration](../../evals/plugin-v1/results/cp04-flashrank-comparison-v2-2026-10-08/declaration.json), SHA256 `3942ba12e46f29e6bb2524b06e4bd5433f2603bc5a850e8859ff3068f7a75b49`, froze sources/packages/model receipts/all inputs and CPU grid before captures. Every model ran the same ten exposed development cases with unchanged English lexical queries, pools and full-universe judgments. Control Recall/nDCG:0.721493/0.812905. Literal baseline:0.804899/0.874555. All known positive IDs are already present in these ten development pools; their remaining failure is selection, unlike the separate Kotlin regression.

Times below are measured inference for the complete pool, including projection/adapter validation, with batch8/threads4. RRF columns reuse the same inference and exclude its small extra selection/pack work. Model peak includes the process and all four input arms; full pipeline cold/warm capacity acceptance is not claimed.

| Model | Input / selection | Recall@12 | nDCG@12 | Median ms | p95 ms |
| --- | --- | ---: | ---: | ---: | ---: |
| TinyBERT | EN goal / pure | 0.742802 | 0.826459 | 82.12 | 263.09 |
| TinyBERT | EN goal / RRF | 0.774469 | 0.842703 | 82.12 | 263.09 |
| TinyBERT | EN terms / pure | 0.750778 | 0.871851 | 67.58 | 221.04 |
| TinyBERT | EN terms / RRF | 0.775778 | 0.846423 | 67.58 | 221.04 |
| TinyBERT | EN terms + field labels / pure | 0.759112 | 0.826892 | 90.28 | 266.42 |
| TinyBERT | EN terms + field labels / RRF | 0.787683 | 0.837659 | 90.28 | 266.42 |
| MiniLM | EN goal / pure | 0.750778 | 0.830641 | 962.75 | 3127.29 |
| MiniLM | EN goal / RRF | 0.767326 | 0.836945 | 962.75 | 3127.29 |
| MiniLM | EN terms / pure | 0.725778 | 0.858986 | 1018.07 | 4509.34 |
| MiniLM | EN terms / RRF | 0.747207 | 0.841608 | 1018.07 | 4509.34 |
| MiniLM | EN terms + field labels / pure | 0.747207 | 0.862290 | 1253.98 | 3624.35 |
| MiniLM | EN terms + field labels / RRF | 0.761493 | 0.842271 | 1253.98 | 3624.35 |

| Direct RU diagnostic | Recall@12 | nDCG@12 | Median ms | p95 ms |
| --- | ---: | ---: | ---: | ---: |
| TinyBERT / pure | 0.587967 | 0.542097 | 122.83 | 378.23 |
| TinyBERT / RRF | 0.688755 | 0.711128 | 122.83 | 378.23 |
| MiniLM / pure | 0.463773 | 0.437519 | 1671.60 | 6123.27 |
| MiniLM / RRF | 0.601850 | 0.684316 | 1671.60 | 6123.27 |

All EN arms improve on FTS control in both macros but fail both literal-baseline comparisons. Direct RU arms fail all four quality comparisons. Other valid status/identity/constraint/exclusion/dedupe/pack-survival/historical-equivalence gates pass. Field labels and RRF are not universal gains: TinyBERT terms/plain has the best tested neural nDCG, whereas terms/labels/RRF has higher recall. No thresholds or judgments were changed.

| Model | Startup ms | Peak process MiB | Resource interpretation |
| --- | ---: | ---: | --- |
| Previously corrected MultiBERT | 1746.81 | 423.95 | Above memory ceiling; previous capture |
| TinyBERT | 576.49 | 195.70 | Within memory ceiling in this diagnostic; latency acceptance remains open |
| MiniLM | 673.22 | 279.69 | Above memory ceiling |

For comparable original EN goal inputs, historical corrected MultiBERT median/p95 were6493.20/19716.75ms; TinyBERT82.12/263.09ms; MiniLM962.75/3127.29ms. Historical times are not newly rerun and hardware/background conditions are not controlled across turns.

## CPU and padding diagnostics

Prospectively selected TinyBERT terms/labels, separate process per configuration, all ten pools, three sequential repeats per case (30 durations/configuration). No arbitrary token truncation; actual largest encoded EN pair250, direct RU299. Reducing max_length to128 would truncate; reducing a512 ceiling without changing actual padding does not itself establish a speed gain.

| Batch | Threads | Length buckets | Median ms | p95 ms | Peak MiB | Pure Recall | Pure nDCG |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 4 | 2 | No | 119.32 | 390.34 | 195.45 | 0.784112 | 0.829916 |
| 8 | 2 | No | 128.05 | 415.56 | 195.83 | 0.759112 | 0.826892 |
| 4 | 4 | No | 150.04 | 352.77 | 195.73 | 0.784112 | 0.829916 |
| 8 | 4 | No | 84.58 | 277.98 | 195.77 | 0.759112 | 0.826892 |
| 8 | 4 | Yes | 66.53 | 240.56 | 195.78 | 0.759112 | 0.836590 |

Batch size/grouping changes scores and sometimes top12: batch4 versus8 maximum absolute score differences reached0.09221 in this packet. Thread changes retained the same final quality macros for a fixed batch size. ONNX graphs contain dynamic quantization operators (Tiny10, Mini50); quantization is a plausible explanation, not an isolated causal proof. Treat batch/grouping as part of the frozen ranking method, not a behavior-neutral tuning knob. No setting passes both quality comparisons; p95 exceeds the existing100ms warm ceiling even before full retrieval/pack costs.

Trials were sequential model processes, without controlled CPU isolation. Initial batch4/threads2 overlapped brief source-coverage setup/capture activity; numbers are noisy diagnostics, not a definitive hardware optimum. The bucketing improvement cannot be presented as final capacity acceptance. All five summaries preserve their own quality verdicts and durations.

## Source enrichment and composed Kotlin regression

[Coverage summary](../../evals/plugin-v1/results/cp04-flashrank-comparison-v2-2026-10-08/source-coverage-v2/summary.json), declaration SHA256 `1687054d814406bf5675c708bf88a43e6b9cef88ff3d64a42e6632f0a32b66e6`. The Kotlin scenario is exposed CP04-HV3-12; keep unknown judgments and original failed held-out unchanged. Report supported-positive coverage only, never replace unknowns with zeros or calculate a new accepted macro.

| Repository | Original FTS rank | Enriched FTS rank |
| --- | ---: | ---: |
| spring-projects/spring-framework | Absent | 6 |
| spring-projects/spring-boot | Absent | 19 |
| quarkusio/quarkus | Absent | 17 |
| micronaut-projects/micronaut-core | 16 | 4 |
| ktorio/ktor | 1 | 1 |

The original pool contains2/5 supported positives; enriched pool5/5. FTS top12 increases1/5→3/5. The separate [composition capture](../../evals/plugin-v1/results/cp04-flashrank-comparison-v2-2026-10-08/enriched-kotlin-rerank/observations.json), declaration SHA256 `19633094d0905beb0251c8b11551b23589b2e1ec9be5fc66ac624c6f744a3a22`, uses TinyBERT original EN goal/plain fields:

| Selection | Original supported positives in top12 | Enriched supported positives in top12 |
| --- | ---: | ---: |
| FTS | 1/5 | 3/5 |
| TinyBERT | 2/5 | 5/5 |
| Equal FTS/TinyBERT RRF | 2/5 | 5/5 |

This shows candidate coverage and ranking working together in one diagnostic. It does not measure precision, resolve unknown returned candidates, qualify overall RU/EN quality or establish project integration readiness. Across the other ten development cases, enriched FTS Recall remains0.721493 and nDCG changes0.812905→0.812044, a small regression retained openly. Five targeted backend facts are not a full-catalog enrichment or source-independent generalization.

Primary sources: [Spring Kotlin](https://docs.spring.io/spring-framework/reference/languages/kotlin.html), [Spring coroutines](https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html), [Spring Boot Kotlin](https://github.com/spring-projects/spring-boot/blob/main/documentation/spring-boot-docs/src/docs/antora/modules/reference/pages/features/kotlin.adoc), [Quarkus Kotlin/extensions](https://quarkus.io/guides/kotlin/), [Micronaut README](https://github.com/micronaut-projects/micronaut-core), [Ktor](https://ktor.io/). Facts preserve module/dependency limits rather than claiming every capability is native in every configuration. Micronaut latest-guide retrieval returned a redirect-only page; the qualified claim uses its readable official README.

## Verification, failures and limits

- Observed TDD RED: RRF ignored the second order and accepted invalid/different pools; short query used unrelated goal text; projection lacked field labels. GREEN: new comparison4/4. Enrichment RED: capability absent and invalid provenance/identity accepted; GREEN2/2.
- Current commands: `work/cp04-flashrank-venv/Scripts/python.exe -B -m unittest discover -s tests -p 'test_plugin*flashrank*.py'` passes17/17; `-p test_plugin_source_coverage_comparison.py` passes2/2, no skips. This includes historical adapter/configured test files actually rerun now. No broad prior suite is claimed newly executed.
- Setup: `--prepare tiny`, `--prepare mini`; capture: `--predeclare`, `--run tiny`, `--run mini`, `--perf 0` through `--perf 4`, source-coverage `--predeclare/--run`, composition `--predeclare/--run`; all final captures exit0, meaning valid evidence, not accepted quality.
- Initial comparison declaration serialized tuple input names into JSON lists and failed equality before inference. Fixed in a new exclusive v2 packet; initial declaration retained. Initial coverage attempted enriched cards with original snapshot pins and failed the canonical context-pack guard. The new packet preserves that boundary, retaining facts separately and using original cards for packs. Historical outputs remain unchanged; no guard was waived.
- [Graph inspection](../../evals/plugin-v1/results/cp04-flashrank-comparison-v2-2026-10-08/model-graph-diagnostic.json) confirms both embedding vocabularies30522 match native IDs. Tiny embedding30522×128; Mini30522×384. Upstream Mini archive ships the same config/tokenizer files as Tiny, including Tiny architecture metadata. ONNX executes its actual graph; this adapter consumes only validated vocabulary/pad configuration, not those architecture fields. Artifact metadata qualification remains a release concern, not proof of a scoring failure.
- Full self-review verifies frozen source/model/package equality, complete permutations, finite scores, unchanged canonical assets/prior captures, UTF-8/local links and control-plane consistency. Exact output/source receipts accompany the results. Only primary self-review; no independent agent or human grade.

## Decision and next gate

Retain TinyBERT as the resource-feasible experimental comparator; no current neural variant replaces FTS or the literal baseline. Continue with broadly qualified searchable capabilities and compare the existing literal selection as a serious alternative. Before adopting enrichment, update its owning catalog metadata/provenance and deterministically regenerate a new compatible pinned bundle through accepted CP-03/06 contracts. Do not hand-edit generated cards or pass enriched cards under old pins.

Freeze a method that passes representative development gates before new independent held-out evaluation. Human usefulness, actual RU/EN query formulation, source-supported rich stack/technical/architectural/product explanation, conditional effort estimates and CP-11/15 joined acceptance remain open. This turn did not run host translation, a human review or a new fresh held-out capture. Model choice does not satisfy those responsibilities.

Rollback removes only new experimental scripts/tests/facts/report/links and ignored small-model cache, retaining all historical evidence and canonical runtime. No Git history, publication, provider, deployment or local LLM activation.
