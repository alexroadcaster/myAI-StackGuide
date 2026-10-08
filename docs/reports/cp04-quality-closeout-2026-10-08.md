# CP-04 Local Quality Evaluation Closeout — 2026-10-08

Task: CP-04 — define retrieval and integration-usefulness evaluation contracts. This report closes the current local diagnostic iteration; full CP-04 acceptance remains `partially_verified`, with `verdict=no_go` and `promotion_ready=false`. It does not accept recommendation quality, human usefulness or the CP-11 lifecycle.

## Scope and owners

The owner requested an independent CP-04 lane using agents and skills. `quality_evaluator` implemented the real offline retrieval/baseline runner and tests; `product_planner` audited the frozen relevance oracle before inspecting outputs and composed bounded paired advice; `evidence_reviewer` independently reviewed the code, provenance, measurements and advice. The primary reconciled evidence and control documents. These are agent reviews, not human calibration or acceptance.

Skills used: `design-recommendation-evals`, `review-advisory-evidence` and `maintain-control-plane`. Existing CP-10 changes and protected agent/config changes are preserved. No Git history, external write, installation, provider call or retrieval-policy tuning occurred.

## Retrieval outcome

The [frozen quality plan](../../evals/plugin-v1/quality-plan.json) contains 24 queries (12 development, 12 held-out). The [declaration](../../evals/plugin-v1/results/cp04-2026-10-08/declaration.json) registers query mapping, shared taxonomy filtering, literal-field baseline, constraints, thresholds, byte accounting and measurement methods before capture. The candidate uses the accepted runtime FTS5 route against the exact frozen 2,500-card CAT-10/CP-06 bundle. Original terms, judgments, weights, thresholds, plan, rubric and public bundle bytes are preserved.

The [observations](../../evals/plugin-v1/results/cp04-2026-10-08/observations.json) record 19 `ok` and five `no_match` results where the frozen cases expected `ok`: DEV-10, HOLD-02, HOLD-04, HOLD-08 and HOLD-09. Original observations SHA-256 is `9fa95b0c9952cf0f039d9a666857bb2fa62be7ffa3283a00bf2bff0d9e7f20a3`; measurement repair did not overwrite these captures.

The [summary](../../evals/plugin-v1/results/cp04-2026-10-08/summary.json) reports:

| Evidence | Observed result | Interpretation |
| --- | --- | --- |
| Official development/held-out Recall@12 and nDCG@12 | `null` | Judgment coverage is incomplete; no official macro or baseline superiority claim. |
| Cases with incomplete candidate judgments | 12 | Unjudged results are not assigned grade zero. |
| Cases incomplete in either method | 13 | Baseline and candidate use the same frozen oracle. |
| Known-pool Recall, development | Candidate 0.625; baseline 0.666667 | Diagnostic only; not thresholded as product recall. |
| Known-pool Recall, held-out | Candidate 0.375; baseline 0.25 | Diagnostic only; not a quality pass. |
| Alias success | 5/5 | Identity retrieval under the declared alias rule. |
| Known positive, non-denied detail-pack survival | 22/22 | Restricted to judged positives actually retrieved in raw top 12. |
| Judged-pool constraint violations, false exclusions, duplicates | 0 | Does not establish safety/fit of unjudged candidates. |
| Required held-out strata | Incomplete | Held-out covers two of 14 containers and lacks activity-unknown coverage. |

The [independent pre-capture oracle audit](../../evals/plugin-v1/cp04-oracle-audit-2026-10-08.md) found only one or two positives per case, no grade-zero/weak judgments, and category-based alternatives whose goal-specific fit is unsupported. Exact identity lookup, alternative fit and supporting roles need distinct judgments. This is an evaluation-oracle defect; it cannot be repaired by retrospectively relabeling the frozen held-out outputs.

## Capacity and performance

The [performance record](../../evals/plugin-v1/results/cp04-2026-10-08/performance.json) contains 30 cold and 30 warm samples. Cold means a fresh process and SQLite connection; timing surrounds `retrieval.retrieve`, excluding process startup. Warm uses one process with one discarded warmup and a fresh immutable connection per call. OS caches were not flushed. Nearest-rank p95 is used.

| Measure | Observed |
| --- | --- |
| Cold p50 / p95 | 112.6537 / 129.4385 ms |
| Warm p50 / p95 | 65.1889 / 85.7632 ms |
| Peak process working set | 193,851,392 bytes |
| Index size | 2,048,000 bytes |
| Maximum canonical query / pack / combined bytes | 668 / 56,046 / 56,701 |

These observed measurements pass the predeclared numeric ceilings. Windows `GetProcessMemoryInfo` reports process-lifetime peak working set, including capture preparation. CPU/machine fields are unavailable, so hardware metadata is incomplete and no portable SLA or full hardware-method gate is claimed. A subsequent read-only `Get-CimInstance Win32_Processor -ErrorAction Stop` attempt returned exit 1 (`Access to a CIM resource was not available to the client`); no retry/elevation was performed. Token counts are unmeasured. Registry counts (111 leaves, 14 containers) are structural index evidence; this run exercised 24 quality routes, not every runtime route. Separately labeled 10,000-row synthetic headroom remains CP-11 work.

The initial measurement aborted on a valid `no_match` result. A [predeclared measurement amendment](../../evals/plugin-v1/results/cp04-2026-10-08/measurement-amendment.json) permits timing that status, preserves the failed expected-status gate, and binds original capture source hashes separately from amended measurement source hashes. Resumption reused original capture bytes and returned exit 1 for `no_go`. Exact original source bytes are hash-bound, not archived independently; external reconstruction needs the corresponding source revision/archive.

## Paired advice and blind agent review

The [advice packet](../../evals/plugin-v1/results/cp04-2026-10-08/recommendation-calibration.json) contains four predeclared cases and eight RU/EN projections, composed from bounded actual public evidence packs and synthetic project context. All 21 captured cards retain `reference_only`, original IDs/order, roles, source facts and evidence. GreptimeDB guidance is identity verification, not an implementation/adoption recommendation. Controlled input is 72,835 bytes; token counts and model generation latency/cost are unmeasured.

The author [self-review](../../evals/plugin-v1/results/cp04-2026-10-08/usefulness-review.json) and [independent blind review](../../evals/plugin-v1/results/cp04-2026-10-08/independent-review.json) remain separate. Blind scores were frozen before the reviewer read author scores. Observed blind RU/EN totals are DEV-08 16/16, HOLD-10 19/19, DEV-11 20/20 and HOLD-12 18/19, with no observed critical text failure. These agent scores do not calibrate the human rubric or establish runtime generation quality.

The [comparison/adjudication](../../evals/plugin-v1/results/cp04-2026-10-08/review-adjudication.json) retains all scores and explains differing judgments. No dimension differs by more than one and no critical pass/failure judgment conflicts. Total-score differences greater than one remain human calibration questions; scores are not averaged into an accepted result. Findings include premature Python focus without a confirmed language/provider, proposed experiments without verified API/data contracts and dense wording/partial RU phrasing. Evaluated advice is preserved, not edited to improve its scores. Same-result textual meaning is supported in the inspected pairs; browser locale switching and absence of calls were not observed.

## Remaining acceptance and next owners

1. Product Planner and Quality Evaluator prepare a new versioned, goal-specific judgment protocol independently of candidate ranking. Cover a declared finite evaluation universe, irrelevant/weak grades, exact-identity versus alternative/support roles and all required held-out strata. Keep this original protocol/results unchanged.
2. Re-run candidate versus literal baseline with unchanged ranking weights first. Any later tuning uses development data and a fresh untouched held-out set; it does not use these inspected held-out outputs as a new blind acceptance set.
3. CP-11 supplies actual joined lifecycle/publication/locale-switch evidence, actual capacity and separate synthetic headroom. A diagnostic protocol can support evidence collection; it does not satisfy the CP-04 quality gate or waive CP-10 browser acceptance.
4. CP-15 supplies independent human usefulness, privacy and UI acceptance. Human rubric calibration and generation latency/token/provider-cost measurements remain open.

The CP-04 → CP-11 dependency is retained. Pre-capture instrumentation readiness, CP-11 evidence collection and final CP-04/15 quality acceptance are separate gates; no task is administratively marked complete to break their evidence dependency.

Rollback restores only this lane's runner/scorer/test/document changes after checking concurrent work. Preserve frozen results as failed-run evidence, all original quality artifacts and unrelated changes.

## Verification

Exact commands, RED/GREEN observations and current source pins are retained in [runner-evidence.md](../../evals/plugin-v1/results/cp04-2026-10-08/runner-evidence.md). Current observations:

- Runner suite: `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_quality_runner.py -v` passed 13/13; independent reviewer repeated 13/13.
- Scorer suite passed 34/34 with the workspace `tempfile.tempdir` override documented in runner evidence. The initial normal-TEMP run had 33 passes and one fixture `PermissionError`; this was an environment failure, not an intended RED. No ACL or permission change was made.
- Frozen-plan validation and both C8 case/result CLI gates returned exit 0; four synthetic captures remain compatibility evidence only.
- Actual C9 schema/hash check returned exit 0 for 72 query/result/pack objects, 24 baseline transport packs and five original artifact hashes.
- Relevant RED/GREEN checks cover explicit canonical baseline candidate ceiling and measurable `no_match` status retaining `no_go`. Baseline default remains 60; explicit maximum comes from canonical policy, without policy/runtime changes.
- Focused final `git diff --check` for owned code/control files returned exit 0; only LF/CRLF notices. Independent review found no remaining blocking code P1/P2 in the assigned runner.
- Primary static reconciliation returned exit 0: all 16 recorded frozen/public/protected input hashes preserved, original capture/advice exact hashes matched, ten result JSON files parsed, all paired scores reconciled and report links resolved. Agent advice checks also verified bounded bytes, IDs/order/roles, source bindings and RU/EN encoding.

The virtualenv printed `Failed to find real location of C:\Python314\python.exe` while completing the checks; no unrelated interpreter repair was attempted. Runtime/browser, installation, full hardware metadata, tokens, live freshness and human acceptance are not implied by these checks.
