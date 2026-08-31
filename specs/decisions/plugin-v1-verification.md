# CP-02: Local Plugin Verification And Handoff

Decision date: 2026-08-30; owner amendment: 2026-08-31. Owner: Catalog Architect; acceptance evidence owner: Quality Evaluator. Status: design registry; product commands below are future contracts unless RUNLOG explicitly records a run. Read [architecture](plugin-v1-architecture.md) and [permissions](plugin-v1-permissions.md).

## Current Documentation Acceptance

The 2026-08-31 owner revision selects SQLite FTS5, relevant context access, activity-aware guidance and an integration handoff. Accept only synchronized design/plan changes: CP-03 local contracts, CP-04 retrieval evals, CP-05 behavior alignment, CP-06 cards/index, CP-09 bounded retrieval, CP-11 local join and independent CP-15/16 acceptance. Remote CP-12-14 do not block local completion. The old CP-02 completion report remains dated evidence, not validation of newly planned behavior.

Current document checks: Product-Agent OS task/control-plane validators, focused existing control-plane tests, dependency/mapping/link/UTF-8/history audit, explicit self-review and protected-file hashes. Results belong in RUNLOG. No schema/runtime/index, new tests or model evaluation is created or executed by this revision. Unchanged source/generated surfaces do not require regeneration.

Official packaging/permission evidence was reviewed on 2026-08-30; it does not prove installed behavior. Recheck volatile details in CP-07/16. SQLite design uses the [official FTS5 reference](https://www.sqlite.org/fts5.html); actual runtime capability and indexed quality require separate evidence.

## Future Commands And Owners

Run repository tests from the implementation repository, not the user's analyzed project. User-project scripts/tests/builds remain forbidden as scan actions; an explicitly requested coding workflow has its own authorization. Python/runtime availability is a prerequisite; do not install tools to satisfy this registry without authorization.

The Quality Evaluator owns test files and acceptance evidence per the detailed CP tasks; builders own implementation and may run relevant checks. The gate owner labels below identify the implementation task, not permission to change another role's test files.

| Gate / owner | Command or required evidence | Availability |
| --- | --- | --- |
| V-CONTRACT / CP-03 Quality Evaluator | `python -B -m unittest discover -s tests -p test_plugin_contracts.py -v` | Future local-schema and negative-fixture suite; remote contracts separately deferred |
| V-CATALOG / CP-06 Catalog Pipeline Builder | `python -B -m unittest discover -s tests -p test_plugin_catalog.py -v`; existing `python scripts/build_catalog_html.py --check` if affected source/output warrants it | Adapter tests future; add `test_plugin_search_index.py` for source/index parity, integrity and pins; existing HTML check available |
| CP-07 Plugin Runtime Builder | `python -B -m unittest discover -s tests -p test_plugin_intake.py -v`; same command with `test_plugin_state.py` | Future |
| CP-08 Plugin Runtime Builder | `python -B -m unittest discover -s tests -p test_plugin_scanner.py -v` | Future |
| CP-09 Plugin Runtime Builder | `python -B -m unittest discover -s tests -p test_plugin_matching.py -v`; same command with `test_plugin_retrieval.py` | Future FTS5/query/cap/ranking tests |
| CP-10 Plugin Runtime Builder | `python -B -m unittest discover -s tests -p test_plugin_artifact.py -v` | Future, plus rendered offline QA |
| V-LOCAL / CP-11 Quality Evaluator | First one named semantic case/command registered by CP-11, then affected edges; final join `python -B -m unittest discover -s tests -p "test_plugin_*.py" -v` | Exact 1/1 command remains CP-11-owned, not falsely executable today |
| V-EVAL / CP-04 Quality Evaluator | Future evals/plugin-v1/evaluate_retrieval.py offline scorer for captured C9 results; test_plugin_retrieval_eval.py verifies known metric fixtures; versioned lexical baseline/RU-EN cases and human integration-usefulness calibration | Scorer/test files planned; exact CLI remains a CP-04 contract. No model/provider runs implied |
| V-MCP / future CP-12 | Backend test/migration commands only after a separately selected remote architecture | `not_applicable_for_local_slice`; remote `command_gap` retained |
| V-LIVE / future CP-14 | Authorized destination/data/cost/time scope and observed intended/fallback traces | Deferred; no external activation |
| V-RELEASE / CP-16 | Local package installation in an authorized synthetic workspace, fresh-session skill loading, cache/package/index/policy identity, actual FTS5 support, read-only query, upgrade, disable and previous-version behavior | Not run; no marketplace/global config modification now |

Proposed internal entrypoint examples, to be implemented in their owning tasks:

```powershell
# Variables refer to an already verified interpreter, trusted bundle, and synthetic project.
& $pythonExe -I -B "$pluginRoot/scripts/intake.py" start --project-root "$projectRoot"
& $pythonExe -I -B "$pluginRoot/scripts/scanner.py" scan --project-root "$projectRoot" --depth standard
& $pythonExe -I -B "$pluginRoot/scripts/matcher.py" match --project-root "$projectRoot"
& $pythonExe -I -B "$pluginRoot/scripts/render_report.py" render --project-root "$projectRoot"
```

These are design interfaces, not claims that files/commands exist. CP-03 defines input/output versions; CP-07 adds resume/answer/finalize with expected run/revision, and uses bounded JSON stdin for free-text input rather than command-line interpolation. Scanner stdout is sanitized only; the skill validates it before committing through state helpers. Match/render consume validated local state. Missing/invalid interpreter or input is a typed failure, never automatic installation, full-catalog model-context fallback or network retry.

## Smallest Meaningful Evidence Sequence

1. CP-03: accept complete local C1-C6/C9 contracts with positive, edge and adversarial fixtures. Local completion excludes remote C4/C7 by design. Reject fabricated activity, public-index private fields, unsafe query grammar, unbounded packs and unsupported primary-fit assertions. Permit appropriately bounded relevant context and a non-executed integration plan.
2. CP-04/05: define the versioned product corpus/thresholds and implement the provider-free captured-result scorer in evals/plugin-v1/evaluate_retrieval.py; align existing role, skill and team-eval contracts with the revised R04/R13 before runtime dispatch. Fresh-session behavior must be inspected; existing static tests or this document do not prove revised routing.
3. CP-07/08: one saved/resumed answer and correction invalidation; bounded scanner plus targeted relevant reads; exclusion/containment and no target-project execution. Check Windows link/ADS/races, changed files, malformed encoding, cancellation/caps, secret canaries in all output paths, prompt injection and useful partial coverage. Verify state locks, stale revisions, crash/recovery, disk/sharing failures and bounded retry debris without pruning user data.
4. CP-06/09: source-persisted field provenance/coverage, canonical aliases, source/card/index/policy hash agreement, read-only index and actual FTS5 support. Probe empty/no-hit/malformed/RU/EN/technology queries, lexical ranking, dedupe before context cap, unknown facts, archived references, mature-but-old libraries and recently-active-but-incompatible tools. Old snapshot date alone must not reject fit. Missing/corrupt/mismatched index must not masquerade as successful no-match or a full-context fallback.
5. CP-10/11: first one useful idea/modernization case through Brief -> FTS5 -> bounded evidence pack -> comparison/integration plan -> saved offline HTML. Record `source_mode=catalog_only`, `retrieval_engine=sqlite_fts5`, package/index/policy pins, result counts/bytes and revision. No mock or alternate route may mask this acceptance case. Then run edges and synthetic 2,000/10,000-row scaling fixtures; label synthetic counts separately from the real catalog and do not infer recommendation quality from timing.
6. CP-04/15: same held-out corpus against a simple frozen lexical/filter baseline, retrieval Recall@k/nDCG@k, exclusions and human usefulness. Record caps, latency/memory/context size, supported hardware, observations and failures. No embeddings or provider calls required to measure retrieval. Model/provider runs need the relevant existing authorization and must be separately labeled. Calibrate scoring before declaring improvement.
7. CP-15/16: independent local privacy/provenance review, rendered offline UI, user acceptance and authorized package/fresh-session/upgrade/rollback checks. No CP-12/13/14 prerequisite and no claim that optional remote features passed. Public release remains a separate action.

The old host-wide isolation promise is explicitly superseded by the owner, not resolved by a synthetic test. Sensitive exclusions, minimization and actual host permissions remain mandatory. Routine allowed reads and a code-oriented handoff are useful behavior, not critical failures.

## Reviewable Outcomes And Rollback

The current documentation outcome maps the owner's decisions through every CP task, requirement and active ADR. CP-03 and CP-04 may be assigned next; CP-05 aligns loaded behavior before runtime work. Runtime, retrieval quality, model usefulness and installation are still unverified. Remote CP-12-14 remain dormant until separately selected.

Stop only the failed path, preserve valid state/history and report gaps. Never hide retrieval failure by changing engine or loading the full catalog into the model. Keep the tested previous package/index for rollback; refuse incompatible state rather than overwrite it. No Git reset, automatic deletion, permission weakening or external action is authorized by this registry.
