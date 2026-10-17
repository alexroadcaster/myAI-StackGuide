# CP-11 local lifecycle verification

**Status: `in_progress / partially_verified`.** The complete local lifecycle is implemented and verified, but CP-11 is not closed: the required final product join failed. CP-04/CP-10 owner acceptance remains closed; CP-15/16 and whole-product promotion remain separate.

Started 2026-10-17 (Europe/Moscow). [Machine-readable record](cp11-local-lifecycle-2026-10-17.json), [capacity](cp11-capacity-2026-10-17.json), [host intake](cp11-host-intake-2026-10-17.json). Runtime evidence is retained under `.codex-tmp/cp11-2026-10-17/`; those synthetic artifacts are local evidence, not a shipped package.

## Observed scenario and implementation

A synthetic Python invoice project starts through the isolated CP-07 CLI and publishes the same `docs/myai-stackguide/status.html` from revision1. One saved goal answer proceeds through an actual bounded scan/checkpoint and CP-08 Brief. A Brief-bound query executes packaged SQLite FTS5 through immutable/read-only connections, with observed `MATCH`/`bm25`, canonical numeric ID37489525 (`pytest-dev/pytest`), card2.0.0, index format3 and retrieval policy2.1.0. The source is `catalog_only`; no fallback or mock supplies the result.

New `commit-matching` and `commit-memo` commands validate existing schemas and joins under the existing CP-07 writer, commit canonical state, then publish once. The memo is authored `conditional_guidance` with `reference_only` role; current public cards do not justify primary eligibility. The proposed next step is an isolated function regression trial (100 +20 =120), pending upstream API/compatibility/license checks and a separate implementation request. No trial/install/integration was executed.

A goal correction narrows the scope to the pure invoice function and defers API/services, increments Brief1 to2 and clears selection/request/retrieval/evidence-pack/memo while preserving saved answers and scan observations. A fresh isolated process reloads and republishes the saved corrected state; this is not misuse of intake `resume`. Fresh capture/report then finalize at revision10. A successor run retains the predecessor and immutable history. Final state and immutable run have identical bytes; History is not an archive of every intermediate revision.

- Capture SHA256: `4cd6bec15746883ebddfe97dc67beffe5578e7abe7736bd5285c8e3bf751fdb9` (22 exact source bindings).
- Final run: `63f609ca-67ca-4786-9898-6272bf501602`, revision10, Brief2.
- State/History SHA256: `a76feb8dbbdda45c8546e91b6360da045363635d37377ce2888b9b4883771609`.
- HTML SHA256: `01dc83a72886cb8bdb22facd93d15514de3ad4c2ae03dc30f55cbfb31060a967`.
- Query SHA256 Brief1/2: `f05279520fcb4ff717be1a6e0acd7f4e1f7cf574a01ec6dcf8fd042ec390ce7a` / `c32738e56f88b9b51ff703a146aa9c53302348f7ba8c87ef735dea549b376062`.

The new stdlib-only validator reads a deterministic 65,949-byte closed schema projection of11 accepted sources, validates active pins/Brief/constraints/ranks/cards/eligibility/evidence/dependencies/authority/budgets and never repeats SQL or executes plans. Schema shapes and active source/index/policy pins did not change. The runtime fix adds `candidate_budget` when the existing native result reports truncation; ranking is unchanged.

`answer.next_question_id` lets the host select an unasked canonical bank question with a contiguous ledger ordinal. Two actual current-host choices route ordinal2 to `current_stack` and `license`, rather than the prior `success` default; saved/published revisions agree. The child audit hook rejects socket/subprocess/shell actions. This proves the selected CLI route and contextually different host choices, not independent semantic model evaluation or host-wide OS isolation.

## Verification and evidence ceiling

| Boundary | Observed result |
| --- | --- |
| First useful semantic case | Expected missing-writer-join RED after real retrieval; final lifecycle1/1 PASS. Initial fixture/setup mismatches were not counted as RED. |
| Joined lifecycle/failures/storage | 4/4 PASS: full scenario; saved memo survives failed render and one render-only retry; newer correction supersedes stale publication; checkpoint-before-state crash refuses mismatched restore and recovers; oversized writer candidate returns `storage_limit` without replacing saved files. |
| New CP-11 tests within the final join | All23 cases passed; this does not turn the full join green. |
| Validator | 13/13 PASS, including mixed pins, forged card/rank/role/evidence, ambiguity, unsupported schema constructs and UTF-8/time formats. |
| Scorer and preserved C8 regression | 28/28 PASS; original four synthetic C8 CLI captures PASS independently. |
| Actual versioned capture scorer | PASS, `local_lifecycle_compatibility_only`, `quality_observed=false`, `promotion_ready=false`. |
| Bundle/index parity | Both `--check` commands PASS; actual public package remains2500 rows/cards,2630 placements,126 routes/162 memberships; immutable write rejection preserved. |
| Browser | All16 eight-view RU/EN combinations nonempty, exactly one visible panel, no document overflow at the observed viewport;15 canonical fields, eight section IDs and two repository links unchanged across locale switch. Console error/warn list empty. Four retained artifact hashes unchanged. |
| Server-down operation | After stopping the owned one-route loopback server, loaded EN History and RU Options still operate. This is not a global network-off/request-trace proof. |
| Existing boundary regressions | Missing translation, long/hostile narrative and5MiB HTML preservation cases passed in the final join. The2MiB writer rejection intentionally tests storage before semantic admission, not a schema-valid oversized recommendation. |
| Required final product join | **FAIL**,456 tests in177.783s,5 failures +12 errors,2 optional native-backend skips. No mandatory gate waived. |

The observed C9 protocol has its own `cp11_observed_c9_capture_v1` schema; C8's synthetic envelope and schema-set hash remain unchanged. A two-line optional Python `card_validator` dispatch leaves the original C8 path intact. CP-11 checks whole-card equality to the hash-verified public snapshot and exact accepted matcher eligibility, retaining all outer C8 relational checks. This resolves actual source-field compatibility without rewriting source observations or calling an actual result synthetic.

Independent code review found two S2 issues (ownerless evidence ambiguity and missing schema-bundle binding); both were repaired and independently rechecked, including6 ownership/collision cases. Strict RFC3339 checks were repaired as well. The final additive C8 adapter received independent4/4 test review. Product Planner's source-bound verdict is `useful_conditional_local_scenario`; its normalized memo/fixture comparison transfers to the final capture. Neither review is human acceptance or a new model-quality result.

Narrative translation coverage is partial in both languages (7 of52 recorded fields). Missing translations display the original with notices. CP-10's accepted zoom/print/globally-disabled-JavaScript/clipboard/global-offline limits remain unchanged. Source-language UI wiring is not a new semantic translation-quality verdict. The live public pytest documentation was inspected transiently; no host observation was added to canonical cards/state and no catalog refresh is claimed.

## Capacity

| Retrieval metric | Actual2500 | Synthetic10000 |
| --- | ---: | ---: |
| Cold p50 / p95 | 79.459 /141.803 ms | 180.524 /202.991 ms |
| Warm p50 / p95 | 6.815 /9.274 ms | 19.140 /23.404 ms |
| Reader peak working set | 45,899,776 bytes | 47,476,736 bytes |
| Index size | 2,048,000 bytes | 8,474,624 bytes |
| Samples |30 cold +30 warm|30 cold +30 warm|

All original capacity gates pass on40 current source bindings. The actual temporary rebuild is byte-identical to the package. Alias probe323965659 matches `full_name_aliases`; CAT-07A probe206427 (`apache/tika`) matches `catalog_description`. Production rejects the synthetic package as `index_incompatible`. OS caches were not flushed; process startup/imports are excluded. Separate pack timings have no assigned whole-path SLA. Two superseded source-binding attempts are retained; no threshold/ranking retuning occurred. Synthetic duplicate text proves headroom only.

## Remaining mandatory gate and bounded next action

The full join stops on historical CP-04 fixtures opening current assets/source bytes:

- Coverage/query variants, domain review and new-domain helpers: `stale manifest pin`.
- Oracle v2: `source pin mismatch`; three negative tests stop before their intended assertions.
- Original quality runner: `incompatible query pins` or `capture-producing runtime changed`.
- Two shared-reader frozen-byte comparisons: the expected pre-extraction bytes do not match even a read-only replay of `HEAD` retrieval before CP-11. The new truncation reason is an additional deliberate delta, not the original cause. A reason-only test adjustment was tried, still failed, and was fully removed; the historical test file remains unchanged.

Read-only `HEAD` replay reproduces the old quality-plan guard failure. Current manifest/index/policy bytes equal `HEAD`, while frozen plans pin older bytes. Exact old assets exist under `evals/plugin-v1/results/cp04-final-source-archive-2026-10-11/baseline/assets/`; source-map pins were verified. Some earliest measurement producer versions are absent from the four checked source maps. Do not repin old captures, rewrite judgments, disable guards or reopen CP-04 acceptance to make these checks green.

Proposed next bounded assignment: tests-only historical fixture migration, with an exact-hash archive resolver and explicit context for the seven affected test families (`coverage_rerank_v3`, `domain_review`, `new_domains`, `quality_oracle_v2`, `quality_runner`, `query_variants_v3`, `shared_reader_core`); two measurement unit cases require an explicitly synthetic/in-memory declaration rather than pretending to replay unavailable producer bytes. This crosses CP-11's currently assigned new test files and needs a separate exact file/fixture handoff. Only after that gate passes can CP-11 close and unblock CP-15. Wider product acceptance and CP-16 install/upgrade/rollback remain separate.

## Changes, preservation and rollback

Owned changes are the intake/retrieval join, new validator/schema bundle/builder, new adaptive/vertical/scorer tests and fixture, explicit observed scorer/schema, capacity runner/reports and current CP-11 evidence/status documentation. Original cards/index/policy, CP-04 captures/judgments, CP-10 owner receipt and unrelated pre-existing dirty work are preserved. No branch/stage/commit/push, installation, external write, deployment, permission/model change or integration execution occurred.

Rollback is limited to these owned code/adapters/tests/docs changes; preserve immutable finalized runs and prior valid state/HTML. Do not use broad reset/deletion or rewrite frozen historical evidence. The current scoped scenario remains useful and reviewable while the mandatory gate is open.

## Registered final checks

Run from the repository with `TEMP` and `TMP` under `.codex-tmp/cp11-2026-10-17/test-temp`; for development schema validation, `PYTHONPATH` points to `.venv/Lib/site-packages`. The installed CPython 3.14.6 satisfies the existing runtime preflight; no dependency installation or permission change is included.

- First semantic command: `C:\Python314\python.exe -B -m unittest tests.test_plugin_vertical_slice.VerticalSliceTests.test_useful_lifecycle -v`.
- Lifecycle/fault/storage cases: `C:\Python314\python.exe -B -m unittest tests.test_plugin_vertical_slice -v`.
- Actual capture scorer: `.venv/Scripts/python.exe -B evals/plugin-v1/evaluate_vertical_slice.py --capture .codex-tmp/cp11-2026-10-17/session/lifecycle-evidence.json --case tests/fixtures/plugin_vertical_slice.json`.
- Capacity declaration and execution: `C:\Python314\python.exe -B evals/plugin-v1/run_vertical_capacity.py --predeclare`, then the same entry point with `--run`; exact source-bound declaration and observations are retained in its own task lane.
- Final product join: `C:\Python314\python.exe -B -m unittest discover -s tests -p "test_plugin_*.py" -v`.
- Existing C8 synthetic compatibility: `C:\Python314\python.exe -B evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json --results tests/fixtures/plugin_retrieval_eval.json --policy-source tests/fixtures/plugin_retrieval_policy.json`.
- Bundled validation schema parity: `C:\Python314\python.exe -B scripts/build_session_contracts.py --check`.
- Public packaged index parity: `C:\Python314\python.exe -B scripts/build_plugin_search_index.py --check`.
- Final focused diff/UTF-8/link/source-binding review after documentation updates.

Browser acceptance will inspect the retained actual joined HTML at the already permitted `http://127.0.0.1:8765/` origin through a loopback-only one-route harness. It serves only synthetic session HTML; state, run JSON, project files and directory listings are unavailable.

## Evidence ceiling

The named case uses a synthetic Python project, actual packaged SQLite FTS5 and an authored conditional memo. The new explicit `cp11_observed_c9_capture_v1` envelope reuses C8 schema/relational validation without relabeling real retrieval as a synthetic C8 capture. It proves local lifecycle compatibility, not a new model-quality or human-acceptance result. The public snapshot remains frozen; host source checks do not refresh it. Partial narrative translations and prior CP-10 accepted browser limits remain explicit.
