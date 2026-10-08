# CP-04 ready-made FlashRank development prototype

Owner: primary Codex executing runtime-builder, evaluator and explicit self-review responsibilities sequentially, without subagents. Exact code/test ownership: `evals/plugin-v1/run_flashrank_development.py` and `tests/test_plugin_flashrank_development.py`; this contract and exclusive `results/cp04-flashrank-2026-10-08/development-v2/` own experiment evidence. The original `development/` declaration and model-initialization failure are preserved: upstream main used a different initialization attribute than the installed 0.2.10 release; no ranking ran in that attempt. R06/R07/R08/R12/R14/R15; no production reader/schema/policy change.

## Prospective experiment

Use FlashRank 0.2.10 with `ms-marco-MultiBERT-L-12`, CPU ONNX, pair maximum 512 tokens, identical public-card search-field text for both locales. The library truncates token pairs; this prototype does not claim full-document semantic coverage. Run the ten exposed V2 semantic development cases, English goals and the explicitly frozen Russian equivalents in the declaration. No held-out capture, private project input, provider or model training. Multilingual availability does not prove RU/EN quality; English limitations in upstream guidance are retained.

Three comparison arms per locale: unchanged actual single-OR FTS5 control; neural ordering of exactly its bounded fetched pool; unchanged literal-field baseline. Preserve raw C9 ranks/BM25/RRF/status/pins and use a separate experimental selection envelope with `executed_c9_rrf=false`. Model output must be a complete ID permutation with finite scores and unchanged public text; reject unknown/dropped/duplicate IDs and model failure rather than fallback. Sort score descending, then numeric ID ascending. Empty/no-match invokes no inference. Pack selection continues through existing constraint/byte logic; no fabricated relevance or constraint scores.

Predeclare source/test/contract hashes, all cases, both goal texts, packages, Python/platform, policy/bundle pins, thresholds and model files/revision/license metadata before capture. Setup is separately owner-authorized (2026-10-08) to install local packages and download the public model. Its GET-only wrapper retrieves revision metadata and a pinned bounded archive, validates extraction containment and records exact hashes. Runtime verifies prepared files and disables automatic model downloading. Dependency versions and artifact hashes are recorded; no claim of a security audit.

Same frozen constrained metrics and unknown-invalidates-macro semantics; denied hits retain zero-gain rank positions, constraints apply to the pack. Candidate must meet the existing development no-regression checks against both control and literal in both goal languages, with status/identity/exclusion/budget/survival and historical-control checks. A pass means worth fresh held-out review only, never CP-04 closure. Model resources are measured but cannot pass capacity from 20 non-repeated inference samples. Existing SQLite-only resource passes do not cover inference. Full human usefulness and CP-11/15 remain open.

## Commands and stops

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_flashrank_development.py -v
work/cp04-flashrank-venv/Scripts/python.exe -B evals/plugin-v1/run_flashrank_development.py --prepare-model
work/cp04-flashrank-venv/Scripts/python.exe -B evals/plugin-v1/run_flashrank_development.py --predeclare
work/cp04-flashrank-venv/Scripts/python.exe -B evals/plugin-v1/run_flashrank_development.py --run-development
```

Preparation writes ignored `work/cp04-flashrank-models/`; exclusive setup files and capture targets cannot overwrite prior receipts. Exit 0 = valid setup/declaration or promising development result, 1 = retained measured development no-go, 2 = invalid/unavailable. No post-exposure changes/rerun in the same packet. Stop and report compatibility/source/resource failures; do not widen policy caps or ship the prototype to obtain a pass. Further coverage work requires source-owned enrichment and separate evaluation; the reranker cannot recover missing candidates.

Sources: [FlashRank](https://github.com/PrithivirajDamodaran/FlashRank), [Ranker source](https://github.com/PrithivirajDamodaran/FlashRank/blob/main/flashrank/Ranker.py), [model repository](https://huggingface.co/prithivida/flashrank), [CP-04 research](../../research/cp04-retrieval-solutions-2026-10-08.md). Model-repository metadata/license is distinct from Apache-2.0 library code. No adoption license approval or quality guarantee follows.
