# CP-04 successor implementation and quality evidence — 2026-10-08

Task: CP-04 — define retrieval and integration-usefulness evaluation contracts.

Status: `in_progress / partially_verified`. The successor oracle, executable comparison, measurements and paired advisory packet are implemented and locally evaluated. Product quality remains `no_go`; `promotion_ready=false`, `human_calibrated=false`. Completing the experiment does not mean its measured candidate passed every gate.

## Protocol and ownership

The prior [diagnostic report](cp04-quality-closeout-2026-10-08.md), original plan, judgments, captures and failures remain historical evidence. The prospective [v2 oracle protocol](../../evals/plugin-v1/oracle-v2-protocol.md), [plan](../../evals/plugin-v1/quality-plan-v2.json), [judgments](../../evals/plugin-v1/quality-judgments-v2.json) and [runner contract](../../evals/plugin-v1/runner-v2-contract.md) were frozen before successor observations. The development review and explicit held-out gate are retained in [the result packet](../../evals/plugin-v1/results/cp04-v2-2026-10-08/pre-capture-review.md).

Product Planner authored the source-first oracle and four advisory examples; Quality Evaluator implemented and ran the comparison, measurements and join harness; Evidence Reviewer independently reviewed sources, scoped contract repairs and blinded advice. Catalog Architect clarified existing card-local evidence identity. Primary reconciles evidence and records lifecycle state. Agent reviews are not human acceptance. Applied skills were `design-recommendation-evals`, `review-advisory-evidence`, `design-catalog-contracts` and `maintain-control-plane` for their respective owned boundaries.

The compatibility unit includes the prospective oracle/runner and direct tests, the existing cross-document test helper and its owning evidence-identity clarification, plus the active lifecycle summaries. Public catalog data, policy, index, production scripts, CP-10 files and protected agent configuration are preserved. No provider, installation, Git history or external publication action was taken.

## Frozen corpus and metrics

The run uses the actual 2,500-card CAT-10/CP-06 bundle: RepositoryCardV2 / ActivityV2, retrieval policy 2.1.0 and index format 3. There are 30 cases: ten development semantic cases, sixteen held-out semantic cases, and four separate identity probes. The oracle contains 1,014 explicit routed judgments; all fourteen containers are represented in held-out semantic coverage. Every expected case has a valid observed status and complete judgment coverage.

V2 explicitly defines constrained relevance before capture: positive non-denied IDs form Recall denominators; denied raw hits retain their rank slots with zero constrained gain. Raw topical diagnostics remain separate. Exact identity and historical alias probes cannot inflate semantic macros. Numeric thresholds were not lowered, and neither labels nor candidate ranking were tuned after held-out exposure.

| Split | FTS5 Recall@12 | Literal baseline Recall@12 | FTS5 nDCG@12 | Literal baseline nDCG@12 |
| --- | ---: | ---: | ---: | ---: |
| Development | 0.721493 | 0.804899 | 0.812905 | 0.874555 |
| Held-out | 0.889931 | 0.876736 | 0.918875 | 0.894256 |

Held-out global Recall/nDCG thresholds and non-regression pass. Required `files_media_storage` stratum H03 fails: Recall@12 **0.50 < 0.60**, nDCG@12 0.905260. Both candidate and baseline miss two grade-positive oracle IDs. The candidate retrieved the directly relevant Immich and PhotoPrism entries. Jellyfin and Airsonic were graded weakly relevant by the predeclared oracle; Airsonic lacks descriptive evidence for a photo/video contribution. This is an oracle-validity limitation, not proof that the runtime missed a directly suitable photo tool. Labels remain frozen; complete enumeration does not establish human relevance validity.

Historical alias success and exact identity success are 1.0. Judged hard-constraint violations, false exclusions and duplicate canonical IDs are zero. All 126 runtime taxonomy routes pass deterministic bounds/dedupe/status checks. Route enumeration is separate from semantic usefulness. [Semantic summary](../../evals/plugin-v1/results/cp04-v2-2026-10-08/semantic-summary.json) and exact captures retain full observations.

## Capacity measurements

Actual 2,500-card retrieval: 30 cold new-process and 30 warm samples, cold p95 **88.4034 ms**, warm p95 **69.2547 ms**, maximum process-lifetime peak working set **199,589,888 bytes**, index **2,048,000 bytes**. These meet the predeclared thresholds. Hardware was Intel i7-12700H on Windows with Python 3.14 and installed SQLite. Timing surrounds `retrieve` only; startup/import and pack composition are excluded, OS cache was not flushed, and memory is not isolated SQLite allocation. Tokens and provider cost are unmeasured (`null`).

The separate 10,000-row synthetic full-card/index fixture preserves public assets. Production retrieval rejects its different trusted manifest with `index_incompatible`; full synthetic production-reader/card/pack capacity is unverified. The sentence in the frozen runner contract anticipating runtime acceptance was falsified by this observation and is not an acceptance claim.

A separately declared evaluator adapter measures existing native query compilation and bounded FTS5 SQL against that isolated fixture, with exact fixture/manifest/policy validation. It does not modify or weaken the production reader; it excludes that entrypoint and therefore cannot prove reader compatibility, full card/pack memory, or semantic quality. Initial warm p95 293.3379 ms failed. One predeclared serialized recheck with the identical method retained the failure: cold p95 **202.7226 ms** passes 500 ms; warm p95 **291.4446 ms** fails 200 ms. No further retries or threshold changes occurred. [Recheck measurements](../../evals/plugin-v1/results/cp04-v2-2026-10-08/headroom-recheck-performance.json) preserve original failures and receipts.

## Cross-document contract and actual writer join

Actual cards reuse local evidence IDs across repositories. The owning [session contract](../../specs/artifact/session-workspace-contract.md) now explicitly states the existing identity `(github_repository_id, evidence_id)`. The test helper resolves explicitly owned recommendation/comparison/presentation references by that tuple; project evidence remains separately scoped; ambiguous ownerless, wrong-owner, duplicate and contradictory evidence fails. Ancestor evidence pointers use the existing component-boundary coverage rule. Catalog activity observations bind to the exact unchanged source-builder projection; `pushedAt` cannot masquerade as a last commit.

Original harness schema failure, duplicate-evidence failure, and subsequent helper compatibility failures are retained in separate immutable declarations/receipts. Repairs concern the synthetic Brief and scoped validator expectations; query/result/pack, public source and runtime bytes remain unchanged. Missing advisory facts stay `unknown/reference_only` with `mandatory_fact_unknown`; present but insufficiently sourced facts stay unknown with `insufficient_evidence`. Concrete verification requirements remain mandatory. Complete sourced values pass without substituting a catalog stage. Forged pass/primary, wrong-reason and incomplete-coverage negatives protect this parity with the unchanged matcher.

The final bounded join passed outer JSON Schema and cross-document checks, then failed at the writer filesystem entry boundary with `state_invalid`, before lock/commit. Read-only reconstruction also passes `state_store.validate_state(writable=True)`; the exact synthetic project cannot be canonically resolved in the restricted process (`PermissionError`, `WinError 5`), which the root validator reports as `invalid_root`. This is a filesystem/environment blocker, not a demonstrated semantic-state rejection. Only the empty output directories exist; no lock, state or HTML file was created. No ACL, permission or containment rule was changed. The [sanitized diagnostic](../../evals/plugin-v1/results/cp04-v2-2026-10-08/join-advisory-repair-diagnostic.json), [failure receipt](../../evals/plugin-v1/results/cp04-v2-2026-10-08/join-advisory-repair-failure.json) and [runner evidence](../../evals/plugin-v1/results/cp04-v2-2026-10-08/runner-evidence.md) retain exact declarations, commands and diagnostics. No successful saved/published/resumed state is claimed. The harness uses a synthetic minimized private Brief and actual D05 capture. It cannot substitute for automatic host validation/routing, browser interaction, full CP-11 lifecycle or recovery acceptance.

## Recommendation usefulness and language evidence

Four actual captured cases—H03 founder photo/video, D05 Go HTTP engineer, H15 incomplete personal-finance context, H11 bilingual metrics/storage—have paired RU/EN advisory text with exact capture/query/result/pack/policy/source hashes, actual selected IDs/order and `reference_only` roles. [Advice packet](../../evals/plugin-v1/results/cp04-v2-2026-10-08/recommendation-calibration.json) SHA-256 is `c71f2799c86ebd725545825715f8dc32441f33a31f03f132dc52311f59a99377`.

Independent blinded agent scores were recorded before author-score disclosure: H03 19/20 RU and 20/20 EN; D05 18/20 and 19/20; H15 18/20 and 19/20; H11 19/20 and 20/20. No critical text failure was observed. Residual findings concern RU readability, the D05 ordering of first validation, and unnecessary ordinary-pilot approval wording in H15. These scores assess this frozen packet only; they do not calibrate the rubric with humans or prove successful integration.

Controlled source projections are 4,299 / 4,712 / 6,057 / 6,171 bytes; paired outputs are 6,103 / 5,985 / 7,376 / 6,498 bytes. Authoring workflow took 963 seconds including waiting, source inspection, composition and verification. This is not model inference latency; tokens/cost remain null. Static paired canonical consistency does not establish rendered browser language switching or absence of browser calls.

The [concrete human review packet](cp04-v2-human-review-2026-10-08.md) contains the four examples, ten 0/1/2 dimensions and critical-failure checklist, without agent scores or suggested pass. EVALS.md requires human examples for calibration. A human rating request was presented; no rating is inferred from the request to finish implementation.

## Verification and remaining acceptance

Observed verification includes oracle **7/7**, runner **17/17**, separate headroom tests **3/3**, final existing cross-document contracts **48/48**, and final scoped evidence/source/eligibility tests **20/20**. The independent reviewer repeated oracle/runner and the earlier scoped **14/14** plus **48/48** at the prior helper hash; after the final eligibility repair, independent source review and the owner's new **20/20 + 48/48** results are separate evidence. Earlier GREEN counts are not carried forward to a changed helper. Commands, RED/GREEN defects, declarations and environment limits are in the runner evidence; earlier runs are not presented as newly executed.

The combined runner cannot produce a full production-headroom success receipt; its semantic summary is separately bounded and does not substitute the adapter result. A Python launcher warning remained nonfatal. No permissions or validator checks were weakened.

Remaining acceptance is explicit:

1. Human rubric calibration and relevance validity review, including H03 unknown relevance. A prospective correction requires a new version and fresh unexposed held-out cases; do not tune the existing frozen test labels.
2. Resolve the measured required-stratum failure and development regressions through a separately owned, prospectively declared search/oracle iteration.
3. Resolve synthetic warm latency and demonstrate accepted production-reader/full-card/pack headroom where required; the lower-layer adapter cannot close that gate.
4. CP-11 supplies the actual host/context/recommendation/publication/recovery lifecycle; CP-10/15 supply rendered RU/EN and human usefulness/privacy acceptance. CP-12–14 remain deferred.

CP-04 contract and evaluation implementation is complete at the measured local ceiling; the parent task remains `in_progress / partially_verified`, quality `no_go`. No remaining mandatory gate is administratively waived.
