# CP-04 ready-made FlashRank prototype — 2026-10-08

Status: implemented and measured as a development-only adapter; `development_no_go`, `promotion_ready=false`. Parent CP-04 remains `in_progress / partially_verified / no_go`. Primary executed all work without subagents, using build-stackguide-plugin and explicit self-review. Owner separately authorized local dependency installation and public model download.

## Implementation and reproducibility

- [Runner/adapter](../../evals/plugin-v1/run_flashrank_development.py) reuses FlashRank 0.2.10 rather than implementing a neural ranker. It ranks exactly the fetched public-card pool, validates a full identity permutation, finite scores and unchanged text, uses numeric-ID tie breaking and preserves raw FTS5 evidence separately. Existing pack construction enforces exclusions and budgets. No-match skips inference; errors never activate a control fallback.
- [Experiment contract](../../evals/plugin-v1/flashrank-development-contract.md) fixes ten exposed V2 development cases, English goals and manually authored Russian equivalents, model/configuration, metrics and evidence ceilings. Both use the same original English lexical FTS queries and candidate pools: Russian goal evaluation is not Russian lexical retrieval acceptance or human translation calibration.
- Isolated ignored environment: `work/cp04-flashrank-venv/`, Python 3.13.5; package versions are recorded in the declaration, installation URLs/artifact hashes in ignored `work/cp04-flashrank-install.json`. Plugin runtime remains stdlib-only.
- Public model: `ms-marco-MultiBERT-L-12`, HF revision `858a1ac046a05663a35367eac852d7f76feeefdd`, archive SHA256 `2c8ae5542f1538e355e9f295d349fc030b5cf7d398c8728c362f0e5129776971`. Six prepared file hashes and model-repository `cc-by-sa-4.0` metadata are retained in the declaration. Library Apache-2.0 and model license are separate; no adoption-license approval is claimed.
- Setup uses bounded public GET retrieval and validates archive paths; it ignores Mac metadata and extracts only expected model files. Inference verifies local hashes and disables automatic downloading. No private Brief, source text, credential, provider request, policy/bundle mutation or production-path activation.

The [first declaration](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/development/declaration.json) and [setup failure](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/development/setup-failure.json) remain preserved. Initialization failed before rankings because the installed 0.2.10 release exposes `model_dir` at the download seam, whereas inspected upstream main also exposed `model_path`. The corrected version used a separate [declaration](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/development-v2/declaration.json), SHA256 `85c7a73c49e2c2f83bd9e86ef0ad72622314a0a3318bd6add845b6cea41f233a`, before its single capture. No source/method/judgment change or rerun followed exposure of those rankings.

## Observed result

See the compact [summary](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/development-v2/summary.json) and complete [observations](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/development-v2/observations.json).

| Method on the same ten development cases | Macro Recall@12 | Macro nDCG@12 |
| --- | ---: | ---: |
| Unchanged actual FTS5 control | 0.721493 | 0.812905 |
| Unchanged literal-field baseline | 0.804899 | 0.874555 |
| FlashRank, English goal | 0.601566 | 0.556688 |
| FlashRank, Russian goal | 0.555733 | 0.450032 |

Both language arms fail all four quality non-regression comparisons against control and literal. Other declared status, duplicate, exclusion, constraint, pack-survival and historical-control/literal checks pass. Valid full judgments support development macros; this is not fresh held-out acceptance. Some individual cases improve, but they do not overturn aggregate failure.

Model startup: 2,910.56 ms. Across 20 sequential case/locale inferences, median: 7,749.19 ms, p95: 20,910.75 ms. Peak process working set including model: 2,315,374,592 bytes (about 2.16 GiB), above the existing 256-MiB ceiling. These samples diagnose cost; they are not repeated warm/cold capacity acceptance and cannot inherit SQLite-only passes. ONNX inference executed, but this configuration is unsuitable for the current product.

Post-capture [tokenizer diagnostic](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/development-v2/tokenizer-diagnostic.json): model config declares vocabulary size 105,879; the loaded JSON tokenizer has 30,522 entries. Direct encoding produced no `[UNK]` tokens for the 20 goal texts, so missing-token behavior is not established. Alignment of tokenizer IDs with model weights needs verification; this is an artifact inconsistency and hypothesis, not proven causation for the ranking failure. No model files were repaired or ranking rerun.

## Verification

- `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_flashrank_development.py -v`: 10/10 pass. Initial adapter stub produced the expected missing-behavior failure before implementation; extraction checks also cover Mac metadata and traversal rejection.
- `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_coverage_rerank_v3.py -v`: 6/6 pass.
- `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_retrieval.py -v`: 18/18 pass with TEMP/TMP set to workspace `work/cp04-temp`. First run failed on system TEMP permissions; no ACL or test/source change.
- `work/cp04-flashrank-venv/Scripts/python.exe -B -m pip check`: no broken requirements.
- Same interpreter, `evals/plugin-v1/run_flashrank_development.py --prepare-model`: setup passed after bounded archive-metadata handling repair; original rejection is retained as setup history. `--predeclare`: exit0. `--run-development`: exit1 with retained measured `development_no_go`.
- Exact 23 declaration source hashes and frozen V3 observations SHA256 were checked unchanged. Production retrieval, context pack, schemas, policy and public assets have no diff. The [execution receipt](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/development-v2/execution-evidence.json) records capture hashes and self-review findings.

## Decision and remaining work

Do not ship this model/configuration. Preserve the working control route and the measured failure. Before another neural experiment, qualify a consistent tokenizer/model artifact and a configuration capable of meeting local resources; freeze a separate development packet. Model names and repository popularity do not establish suitability.

First-stage source-supported capability coverage remains separate: a reranker cannot recover absent repositories. Follow the accepted CP-04 continuation for source-owned enrichment and fresh independent held-out judgments, followed by source-backed stack/technical/architecture/product explanations and actual human usefulness calibration. CP-11/15 joined gates remain open. Choosing another ready framework cannot substitute for these checks.

Rollback: remove only this experimental runner/tests and isolated configuration if rejected; retain canonical runtime, all frozen evidence and pre-existing dirty work. No automatic deletion or Git history operation was performed.
