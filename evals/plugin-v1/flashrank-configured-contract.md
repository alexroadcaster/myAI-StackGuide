# CP-04 corrected FlashRank configuration

Owner request: verify/fix the configuration, rerun and show comparative results, without subagents. Exact owned code/tests: `run_flashrank_configured.py`, `tests/test_plugin_flashrank_configured.py`. Original runner/tests/contract, source bundle/model artifacts and all earlier declarations/captures remain immutable. Reuse their public-field projection, case goals, identity validation, pack construction and metric logic. Exclusive output: `results/cp04-flashrank-2026-10-08/configured/`.

Fix the native tokenizer model through `tokenizers.models.WordPiece` using the pinned model package's `vocab.txt`; require exact contiguous vocabulary IDs and config size, preserve normalization/preprocessing/postprocessing and special IDs. Attribute assignment to `tokenizer.vocab` does not change the native tokenizer. Qualify the ONNX embedding vocabulary dimension before capture. No guessed model download or weight alteration.

Other fixed settings: maximum pair512 tokens, CPUExecutionProvider, sequential ONNX execution, intra-op4 threads, CPU memory arena and memory pattern disabled, at most8 pairs per library inference. Retain every fetched candidate and perform global score/ID ordering afterwards. These jointly changed settings test the combined correction, not isolated causal effects of tokenizer, batching or thread count.

Reuse the same ten exposed development cases, original EN lexical queries, paired EN/RU goals, control/literal arms and predeclared quality thresholds. Freeze the new runner/test/contract hashes and configuration before exactly one capture; no post-exposure tuning or rejudging. Both goal arms must be no worse than control and literal to qualify for new held-out review. No human/RU lexical/held-out/lifecycle or release acceptance follows. Measure model-inclusive resource cost, keeping the existing repeated-capacity gap visible.

```powershell
work/cp04-flashrank-venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_flashrank_configured.py -v
work/cp04-flashrank-venv/Scripts/python.exe -B evals/plugin-v1/run_flashrank_configured.py --predeclare
work/cp04-flashrank-venv/Scripts/python.exe -B evals/plugin-v1/run_flashrank_configured.py --run-development
```

Sources: [FlashRank source](https://github.com/PrithivirajDamodaran/FlashRank/blob/main/flashrank/Ranker.py), [native tokenizer source/API](https://github.com/huggingface/tokenizers/blob/main/bindings/python/py_src/tokenizers/models/__init__.pyi), [ONNX session/thread settings](https://onnxruntime.ai/docs/performance/tune-performance/threading.html). Additional ONNX inspection dependencies stay in the owner-authorized ignored local environment. Parent CP-04 stays no_go until its remaining gates pass.
