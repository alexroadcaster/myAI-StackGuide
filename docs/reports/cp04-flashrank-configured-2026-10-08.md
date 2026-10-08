# CP-04 FlashRank tokenizer correction and configured rerun — 2026-10-08

Owner requested checking/fixing configuration and rerunning with a comparison table, without subagents. Implemented and measured locally; result remains `development_no_go`, `promotion_ready=false`. Earlier source/model artifacts, declarations and failed captures remain unchanged.

## Verified defect and correction

The installed library assigns `tokenizer.vocab` after loading the native tokenizer from JSON; direct encoding checks proved this attribute assignment did not change native IDs. JSON tokenizer vocabulary has30,522 entries while config and actual ONNX quantized word embedding both have105,879 rows (weight shape105879×768). For example, `search` has JSON ID3945 versus pinned `vocab.txt` ID17047.

[Configured adapter](../../evals/plugin-v1/run_flashrank_configured.py) installs a native `WordPiece` model using exactly the pinned vocabulary, validates size/contiguous IDs/all token mappings and special IDs, preserving the existing normalization/preprocessing/postprocessing. No weight, model-cache file, old runner, card, policy or index was modified. Existing FlashRank inference/scoring and existing bounded pack/metric code are reused.

CPU configuration: batches of8 pairs, intra-op4 threads, sequential execution, explicit CPUExecutionProvider, disabled CPU memory arena/memory pattern, maximum pair512 tokens. All fetched IDs are retained and globally ordered by score/ID after batches. These jointly changed settings measure the combined correction; separate causal gains for tokenizer, batching, threading and allocation are not claimed.

## Same-case development results

The [new declaration](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/configured/declaration.json), SHA256 `9394d17c217cb363e1c8a4e91917022f6839b089416507827caaece18f1dacc3`, froze26 source/test/contract hashes, packages, configuration, pinned model files and the same ten cases/EN/RU goal texts before a single capture. Original English lexical queries and fetched pools remain unchanged. This tests goal-language selection, not independent Russian lexical retrieval or translation acceptance. All cases are exposed development data; no fresh held-out evidence.

| Method | Recall@12 | nDCG@12 |
| --- | ---: | ---: |
| Actual unchanged FTS5 control | 0.721493 | 0.812905 |
| Unchanged literal-field baseline | 0.804899 | 0.874555 |
| Before correction, EN goal | 0.601566 | 0.556688 |
| After correction/configuration, EN goal | 0.728727 | 0.789852 |
| Before correction, RU goal | 0.555733 | 0.450032 |
| After correction/configuration, RU goal | 0.619844 | 0.591957 |

EN now passes Recall non-regression against FTS control, but fails control nDCG and both literal comparisons. RU fails all four quality comparisons. Both goal-language arms retain passing status/identity/constraint/exclusion/dedupe/pack-survival/historical-equivalence gates. The combined correction improves both metrics in both languages relative to the old model configuration, but does not meet the accepted selection gate.

| Resource diagnostic | Before | After |
| --- | ---: | ---: |
| Model startup | 2910.56 ms | 1746.81 ms |
| Inference median | 7749.19 ms | 6057.71 ms |
| Inference p95 | 20910.75 ms | 18303.38 ms |
| Peak process working set | 2315374592 B / 2208.11 MiB | 444547072 B / 423.95 MiB |

Peak memory fell80.80%, but remains above256 MiB. There are20 sequential inference timings, not repeated cold/warm capacity trials; startup includes initialization/hash validation. Same machine/process methodology is retained, but this is not an isolated, controlled performance attribution. Resource acceptance remains false.

## Verification and evidence

- Test-first RED: native `search` ID stayed1 instead of2, a19-pair request stayed one batch instead of8/8/3, and incompatible vocabularies were accepted. GREEN: all3 configured tests pass in the isolated native-backend environment. Tokenizer-dependent tests explicitly skip when optional dependencies are absent from the stdlib development environment; the acceptance run had no skips.
- Existing experimental adapter tests10/10 pass in the same isolated environment; `pip check` reports no broken requirements. Earlier6 coverage and18 retrieval checks remain unchanged historical evidence, not newly executed in this rerun.
- `onnx==1.20.1` installed only in the owner-authorized isolated environment for direct weight inspection; quantized embedding shape105879×768 observed. Installation report is ignored `work/cp04-onnx-inspection-install.json`.
- Command: `work/cp04-flashrank-venv/Scripts/python.exe -B evals/plugin-v1/run_flashrank_configured.py --predeclare` → exit0; `--run-development` → exit1 with a valid retained development no-go. No post-exposure code/configuration/judgment change or second capture.
- [Compact summary](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/configured/summary.json), [complete observations](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/configured/observations.json), [comparison/receipt](../../evals/plugin-v1/results/cp04-flashrank-2026-10-08/configured/execution-evidence.json). Exact source hashes, historical capture hashes and20 complete ID permutations/score orders are rechecked. Explicit primary self-review; no independent agent or human rating.

Keep the current production FTS5 route. This corrected model/configuration is still experimental; slower/larger inference and required RU/EN non-regression remain open. Candidate-coverage repair, fresh independent held-out and actual human/CP-11/15 acceptance remain separate CP-04 requirements. Rollback only the new adapter/configuration, retaining all prior captures and canonical state/runtime. No provider, new LLM, Git history or external publication operation.

Sources: [FlashRank implementation](https://github.com/PrithivirajDamodaran/FlashRank/blob/main/flashrank/Ranker.py), [native WordPiece API/source](https://github.com/huggingface/tokenizers/blob/main/bindings/python/py_src/tokenizers/models/__init__.pyi), [ONNX session settings](https://onnxruntime.ai/docs/performance/tune-performance/threading.html), [prospective configured contract](../../evals/plugin-v1/flashrank-configured-contract.md).
