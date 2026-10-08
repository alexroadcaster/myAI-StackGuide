# CP-04 retrieval and recommendation solutions research

Observed on: 2026-10-08. Researcher: primary Codex, without subagents.
Status: source-backed research proposals; no implementation, installation, model execution, catalog promotion or new quality acceptance.

## Decision

Prefer ready-made implementations before custom retrieval work. First candidate for the existing pipeline: FlashRank's CPU pairwise reranker, evaluated separately from canonical C9 ordering. Use targeted source-backed capability enrichment to address first-stage misses. A ready full RAG application is a separate alternative, not a prerequisite for improving the current plugin. External evidence supports available functionality, not 100% correctness on this catalog.

The [current CP-04 report](../docs/reports/cp04-v3-continuation-2026-10-08.md) retains the failed frozen V3 capture. Do not rewrite that experiment after inspecting its results. A changed method needs development cases, new independent held-out evidence and appropriate contract review.

## Locally observed failure mechanism

Read-only inspection of the bundled `plugins/myai-stackguide/assets/catalog.search.sqlite` and V3 observations found:

| Kotlin backend positive | Indexed evidence | V3 control position |
| --- | --- | --- |
| `spring-projects/spring-framework` | No Kotlin term in the nine FTS columns; upstream description is only `Spring Framework.`; use cases and integration surface empty | Not retrieved |
| `spring-projects/spring-boot` | Java/Spring topics and generic descriptions; no Kotlin term; use cases and integration surface empty | Not retrieved |
| `quarkusio/quarkus` | Java/reactive topics and short Java description; no Kotlin term; use cases and integration surface empty | Not retrieved |
| `micronaut-projects/micronaut-core` | Kotlin topic present | 16 |
| `ktorio/ktor` | Kotlin, async and web-framework topics present | 1 |

The frozen query uses Kotlin, web framework, server, async and RU equivalents with OR. Three supported positives are outside the entire returned pool; another is below top 12. This establishes both searchable-information gaps and ordering failure in this case. It does not establish that all failures have the same cause.

Spring's [official release notes](https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-5.2-Release-Notes) explicitly describe Kotlin coroutines, while the FTS row lacks this information. Adding a vector engine over the same minimal descriptions cannot be assumed to recover verified capability facts. Reranking only existing candidates cannot recover missing IDs.

## Qualified methods and implementations

### 1. Enrich searchable documents, then expand queries conservatively

[Document Expansion by Query Prediction](https://arxiv.org/abs/1904.08375) addresses vocabulary mismatch by adding predicted queries to documents. The authors provide [docTTTTTquery](https://github.com/castorini/docTTTTTquery), with [Apache-2.0 code license](https://raw.githubusercontent.com/castorini/docTTTTTquery/master/LICENSE), T5 inference and reproducibility material. Its MS MARCO training/domain does not establish RU/EN repository-selection quality.

**Proposal:** adopt the document-expansion principle, initially using curated, source-backed capability text in the existing owned card/search projections. Preserve upstream descriptions. Associate each added capability with an exact source, observation date, repository/addon/edition scope and uncertainty. Generate search aliases separately from factual assertions; predicted language is never evidence that a repository supports a feature. A builder must regenerate the pinned public package; runtime must not silently modify it.

[Query2doc](https://arxiv.org/abs/2303.07678) generates pseudo-documents to expand queries and reports BM25 improvements on its benchmarks. A guessed `microsoft/query2doc` repository returned 404; no author-code identity is claimed here. The method can inform bounded host query formulation, but generated pseudo-documents are not verified project facts or upstream evidence.

[When do Generative Query and Document Expansions Fail?](https://arxiv.org/abs/2309.08541) finds benefits and regressions depending on retriever/domain. Consequently, maintain an unexpanded arm and evaluate expansion separately rather than assuming universal gain. Retain literal technology identifiers and distinguish core requirements from preferences; do not turn every preference into an exclusion.

### 2. Goal-aware reranking after candidate coverage

[RankGPT](https://github.com/sunnweiwei/RankGPT) and [its paper](https://arxiv.org/abs/2304.09542) demonstrate LLM reranking. [RankLLM](https://github.com/castorini/rank_llm) provides pointwise, pairwise and listwise methods, execution analysis and reproducible evaluation. Its code is [Apache-2.0](https://raw.githubusercontent.com/castorini/rank_llm/main/LICENSE). Hosted and local inference are different optional stacks; Pyserini requires Java 21 and local model paths introduce Torch/Transformers or serving dependencies.

**Proposal:** use its ranking pattern and output validation as references for the existing user-host model, without installing the full framework. Evaluate each selected repository against the project's core function, technical constraints, architecture role, product contribution and trade-offs. Preserve raw C9 ranks/scores separately from the proposed selection order; validate exact candidate identity, dedupe and evidence budgets. Never infer supported capability or compatible license from a model's preference. Final implementation must accept a versioned selection/provenance contract before claiming canonical ranking replacement.

This addresses ordering and explanatory fit, not first-stage misses. Same-role alternatives remain choices; complementary components require explicit interfaces and separate roles. No benchmark result establishes engineering-hour savings or adoption readiness.

### 3. Multilingual neural retrieval/reranking: a second option

[Sentence Transformers](https://github.com/huggingface/sentence-transformers) provides embedding and CrossEncoder implementations under Apache-2.0; its [retrieve/rerank example](https://github.com/huggingface/sentence-transformers/blob/main/examples/sentence_transformer/applications/retrieve_rerank/README.md) separates candidate generation from pairwise query/document scoring.

[Multilingual E5](https://arxiv.org/abs/2402.05672) offers small/base/large embedding approaches; [BGE-M3](https://arxiv.org/abs/2402.03216) supports multilingual dense, sparse and multi-vector retrieval. [FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) documents the multilingual `BAAI/bge-reranker-v2-m3`; its framework [license is MIT](https://raw.githubusercontent.com/FlagOpen/FlagEmbedding/master/LICENSE). Model-weight licenses and exact revisions must be checked separately from framework licenses.

**Disposition:** suitable experimental comparators for RU/EN, not a current shipped dependency. Neither Windows/Python 3.14 compatibility nor the existing latency/memory ceiling has been tested with these models. Local model memory must be measured separately from SQLite; the passed 256-MiB reader benchmark does not cover model inference. Prefer the existing host-model path first if it supplies adequate quality within the product boundary.

[sqlite-vec](https://github.com/asg017/sqlite-vec) supplies SQLite vector storage/search and documents Windows support, but [its README](https://raw.githubusercontent.com/asg017/sqlite-vec/main/README.md) explicitly identifies pre-v1 compatibility risk. [sqlite-hybrid-search](https://github.com/liamca/sqlite-hybrid-search) demonstrates FTS/BM25 plus vector RRF. These are architectural references; the demonstration is not a verified production library for this plugin. Vector extensions, embedding generation and changed index compatibility need a separately accepted extension of the current FTS-only contract. RRF already exists in this repository and need not be reimplemented.

### 4. Independent metric checks and fresh evaluation

[BEIR](https://arxiv.org/abs/2104.08663) evaluates multiple retrieval families across domains; [the maintained framework](https://github.com/beir-cellar/beir) supports custom datasets and retrieval comparisons. It is a benchmark/method reference, not a replacement for project-specific judgments. [MTEB](https://github.com/embeddings-benchmark/mteb) is useful for choosing multilingual model comparators, without importing leaderboard scores as product acceptance.

**Choose one offline metric reference:** [ir_measures](https://github.com/terrierteam/ir_measures) (Apache-2.0) for common metric implementations; [ranx](https://github.com/AmenRa/ranx) ([MIT](https://raw.githubusercontent.com/AmenRa/ranx/master/LICENSE)) is an alternative for statistical comparison/fusion. They are development tools, not runtime dependencies.

Code inspection found a material default mismatch: [ir_measures nDCG](https://raw.githubusercontent.com/terrierteam/ir_measures/main/ir_measures/measures/ndcg.py) defaults to `dcg='log2'` and offers `exp-log2`/custom gains; [ranx](https://raw.githubusercontent.com/AmenRa/ranx/master/ranx/metrics/ndcg.py) distinguishes normal nDCG from `ndcg_burges`. Our gain is `2**grade - 1`. Select equivalent semantics explicitly and characterize denominator, ties, denied IDs, empty cases and all-rank unknowns. Neither library automatically enforces the project's unknown-invalidates-macro rule; preserve that outer validator. No scores were recalculated in this research.

### 5. Check whether sources actually support the answer

[ALCE](https://github.com/princeton-nlp/ALCE), [paper](https://arxiv.org/abs/2305.14627), evaluates correctness and citation quality, with [MIT code license](https://raw.githubusercontent.com/princeton-nlp/ALCE/main/LICENSE). [RAGChecker](https://github.com/amazon-science/RAGChecker), [paper](https://arxiv.org/abs/2408.08067), provides claim-level diagnostics for retrieval and generation under Apache-2.0. Its documented checking path needs ground-truth answers and extractor/checker models; it is not a free deterministic validation layer.

**Proposal:** adopt claim-to-evidence checks first: source URL/date, exact capability, native versus addon, OSS versus paid edition, compatibility uncertainty and conflicting observations. Evaluate citation support separately from project-fit inference and planning estimates. A citation checker cannot establish that an integration will work, that a timeline is accurate or that the end user understands the trade-off. Full framework execution would require model/runtime/cost qualification beyond this read-only research.

[Ragas](https://arxiv.org/abs/2309.15217) provides automatic RAG assessment; [ARES](https://arxiv.org/abs/2311.09476) explicitly incorporates human annotations to mitigate evaluator error. They inform evaluation design but do not replace the accepted 16/20 usefulness rubric or human acceptance.

## Remaining repository-fact gaps

Oscar's [official repository](https://github.com/django-oscar/django-oscar) identifies [django-oscar-api](https://github.com/django-oscar/django-oscar-api) as a separate extension. This supports discussing an explicit two-component proposal; it does not establish native API in the routed core repository. IDURAR inventory/edition mapping and PrestaShop decoupled shopper workflow remain unresolved by this bounded additional GitHub search. Search omission is not evidence of absent functionality. Their frozen V3 unknowns remain unchanged.

No general-purpose retrieval or evaluator package can repair absent or contradictory source facts. Source qualification and component-scoped recommendation contracts remain necessary.

## Proposed smallest implementation sequence

1. Prospectively accept capability/source enrichment at the owning source boundary. Use representative development repositories, preserve original upstream metadata and regenerate a new compatible pinned package. Do not specialize enrichment to only exposed V3 names or labels.
2. Compare unexpanded FTS, bounded source-grounded query variants, and goal-aware selection. Preserve current production route as control and raw C9 evidence. Diagnose retrieved-pool coverage separately from Recall@12/ranking.
3. Cross-check metric semantics with one offline library; characterize unknowns before computing scores. Prepare a new source-independent held-out set before running changed methods. Retain exposed V3 as regression evidence only.
4. Check source support and paired RU/EN meaning on actual generated recommendations. Include unknown/conflict/addon/paid-edition cases and the accepted stack/architecture/product/complexity/estimate explanation.
5. Present calibrated examples for actual human usefulness review. CP-10/11/15 browser/publication/lifecycle acceptance stays separate.

Superseded as the initial recommendation: the earlier 24–44 engineer-hour estimate covered a bounded custom experiment over roughly 15–30 development repositories, including enrichment/rebuild, query/selection changes and evaluation work. It was not a ready-made RAG setup estimate and should not be presented as the minimum cost of CP-04 improvement. Prefer the ready-made pilot below and estimate remaining adoption work from its measured results.

## Ready-made implementation first

Public documentation and source inspection on 2026-10-08 identified these alternatives:

| Implementation | Verified reusable capability | Fit and first check |
| --- | --- | --- |
| [FlashRank](https://github.com/PrithivirajDamodaran/FlashRank) | CPU pairwise reranking without Torch/Transformers; request/response retain passage IDs and metadata; multilingual model option | Smallest direct candidate for the existing Python retrieval pipeline. Feed retrieved public card text and repository IDs, then compare selection order. Model runtime memory, Windows/Python compatibility, RU/EN quality and latency are unmeasured. |
| [AnswerDotAI/rerankers](https://github.com/AnswerDotAI/rerankers), [author paper](https://arxiv.org/abs/2408.17344) | Unified query/documents/IDs API across FlashRank and other ranking backends; inference backends require their own dependencies | Useful if the pilot compares multiple model families. Avoid the extra wrapper if only FlashRank is needed. |
| [Haystack SentenceTransformersSimilarityRanker](https://docs.haystack.deepset.ai/docs/sentencetransformerssimilarityranker) | Existing standalone ranker or pipeline component accepting a query and documents | Viable alternative for a larger component pipeline. Its documented default model is English; qualify a multilingual model separately. |
| [LlamaIndex](https://github.com/run-llama/llama_index) | Existing fusion retriever, SentenceTransformer reranking and citation query engine | Ready framework if a broader pipeline is required. Its fusion implementation uses node hashes and its own rank convention; it cannot silently replace exact GitHub-ID deduplication and canonical C9 scores. |
| [neuml/rag](https://github.com/neuml/rag), backed by [txtai](https://github.com/neuml/txtai) | Ready Streamlit RAG application with Docker/Python setup and configurable data/model paths; txtai supports sparse/dense hybrid retrieval | Strong candidate for a standalone demonstrator. Replacing the plugin's current retrieval and presentation with it is a larger architecture decision. |

**Recommended first experiment:** directly reuse FlashRank; do not build a custom reranker or replace the whole retrieval engine first. Start with development cases for multilingual ordering and Kotlin candidate coverage. Keep exposed V3 cases as regressions, not a fresh acceptance set. A reranker cannot recover a repository absent from its input pool; source-backed searchable capability coverage remains a separate check.

Time-box the first useful prototype to 2–4 engineer-hours as a planning budget, not a measured duration or promise of CP-04 completion. Scope: one ready backend, public card inputs, preserved IDs, a baseline comparison and recorded startup/memory/latency or a concrete compatibility failure. Exclude full-catalog enrichment, final held-out evaluation and rollout from that budget. Continue only with evidence that this component improves the relevant cases; estimate remaining work after the pilot.

This is a research recommendation. No dependency was installed, no model downloaded or run, and no retrieval contract or production path changed. The rich stack/technical/architecture/product explanation, public source verification and claim support remain product responsibilities around whichever ready retrieval component is selected.

## Evidence ceiling and rejected shortcuts

Sources were inspected through public read-only web tools; local SQLite was opened read-only/immutable. No packages/models were installed, no provider calls or subagents used, no frozen judgments or runtime changed. Branch heads were inspected, not pinned/installed releases; latest activity/release freshness and end-to-end compatibility are not certified. License observations apply to inspected framework code, not automatically to every dependency/model.

No inspected project demonstrates 100% correctness for this use case. [BRIGHT](https://arxiv.org/abs/2407.12883) documents substantial remaining difficulty for reasoning-intensive retrieval. Prefer measured improvement over our baseline rather than guarantees. Do not silently convert unknowns to zero, omit failed strata, assume more candidates always improves ranking, or replace the local contract with an unmeasured vector/model stack.
