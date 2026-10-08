# CP-04 frozen-v1 offline diagnostic evidence

Verdict: `no_go`, `promotion_ready=false`. Evidence owner: `quality_evaluator`;
product acceptance owner: `product_planner`. This is actual offline public-catalog
retrieval and literal-baseline evidence, separate from synthetic C8 compatibility,
agent routing, human quality, CP-11 state/publication and CP-15 browser acceptance.

## Identity and retained evidence

- Run: `547eabe1-59ab-453c-876e-d23805371c58`, 24 frozen cases, 12 development / 12 held-out.
- Canonical quality-plan SHA-256: `e895c54ef78505ca6bcbe12edd7385d43351b78dfd915a238cd20ea7a9bcdaa7`.
- Rubric SHA-256: `96f67da80234d4ade36c9b5e5fb50276398acce76751513e9e041926b74f3fef`.
- Original declaration canonical SHA-256: `3e7211f9d4d1dc0fdcb27a5ae4958440b4f358d589e9e5cae24291c3b673968f`.
- Original observation exact-byte SHA-256: `9fa95b0c9952cf0f039d9a666857bb2fa62be7ffa3283a00bf2bff0d9e7f20a3`.
- Capture-producing runner SHA-256: `b31a0bebaae6c0826481fafe9ebb9ef442adc66f779aff167737e9097266a98a`.
- Measurement amendment canonical SHA-256: `e606f3a43318cc55745c82e25918a189e501193644ff1e82992a3462e09794eb`.
- Measurement-only runner SHA-256: `e6ba2970a955319f5cc6d5c06b554d911263ed7f00bbe8bd17347aad8e80a321`.

The declaration and amendment preserve exact source/runtime hashes separately.
`artifact-hashes.json` verifies five machine-readable artifacts; this narrative is
an evidence interpretation, not capture truth. Independent recommendation/review
artifacts are separately owned and are not overwritten by the runner.

The public tuple remained card/activity `2.0.0`, policy `2.1.0`, index format `3`,
actual `catalog_snapshot` with 2,500 unique numeric IDs. Exact pins:

| Pin | SHA-256 |
| --- | --- |
| source | `d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e` |
| cards | `fceeaa7eaf1d83e280ed4244fed2717a820d59fcdc5b1aa849fd82f245f2ef5b` |
| index | `9678f5e265e4e3a33df3818f94c509c60728e994051ee72ec2050b0b093306c4` |
| policy | `ff6e8444c4664492bb099f0819b2d284aa5c28f0d44c7a745c63f434c3489dbf` |
| taxonomy | `09dcaac99e1e1d7110e9ab64ef33e20654be225fb6ea81dc5bfbf3483f3a721f` |
| manifest | `1d090b0e2e56f4c7cd38276d0d8b08be2436e0c75b77649cf00d32c13cb9497f` |

The snapshot identity is
`catalog-v5.1-2026-09-01-d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`.
This dated snapshot is not refreshed live GitHub evidence.

## Observed retrieval and failed requirements

- Actual FTS5: 19 `ok`, five valid `no_match` against frozen expected `ok`.
  Mismatches: DEV-10, HOLD-02, HOLD-04, HOLD-08 and HOLD-09 (all prefixed `CP04-`).
- Candidate raw rankings: 76 case-ID occurrences, including 53 unjudged occurrences.
  Literal baseline: 69, including 47 unjudged occurrences. These are per-case
  occurrences, not globally unique repository counts.
- Twelve candidate cases and thirteen candidate/baseline union cases have
  incomplete raw judgment coverage. Full ranks beyond 12 also count as incomplete.
  Official development and held-out macro Recall@12/nDCG@12 remain null for both
  methods. No unjudged result was assigned grade zero, omitted or compacted.
- Diagnostic known-positive pool Recall@12 only: development FTS5 `0.625`, baseline
  `0.6666666666666666`; held-out FTS5 `0.375`, baseline `0.25`. These values are not
  official quality metrics and were not compared with acceptance thresholds.
- Frozen-pool hard-constraint violations, false exclusions and canonical duplicates
  are zero. This does not prove all unjudged candidate decisions are correct.
- Historical aliases: five of five numeric targets found in raw top 12, including
  a denied target that correctly remains outside the detail pack. This does not
  imply an allowed alternative or useful integration exists for an alias query.
- Known grade-positive, non-denied top-12 pack survival: `22/22=1.0`, using the
  denominator declared before capture. It excludes unknown relevance, denied
  candidates and unretrieved IDs; it does not prove shortlist quality.
- Actual registry has 111 categories, 14 containers and one review bucket. These
  are structural index counts; all 126 runtime routes were not executed here.
- Held-out required-stratum gates are null. The frozen held-out cases cover only
  two of the fourteen required container domains. The independent source review
  also identifies unsupported same-leaf alternatives and incomplete pools; see
  `../../cp04-oracle-audit-2026-10-08.md`. Labels/thresholds were not repaired or
  tuned after observation.

R06/R12 retrieval-quality acceptance remains failed/incomplete. R14 activity/fit
and R15 human integration/presentation usefulness remain separate unaccepted gates.
The passing known-pool safety and performance checks cannot override these failures.

## Measured performance and bytes

Method is the predeclared mixed workload, 30 cold subprocess samples and 30 warm
samples after one discarded query. Timer surrounds `retrieval.retrieve` only;
process startup/import and pack generation are excluded. Existing runtime opens a
new immutable SQLite connection per call. Nearest-rank percentiles, OS cache not
flushed; prior asset validation/capture had warmed the cache.

| Measure | Observed |
| --- | ---: |
| Cold p50 / p95 | 112.6537 / 129.4385 ms |
| Warm p50 / p95 | 65.1889 / 85.7632 ms |
| Process-lifetime peak working set | 193,851,392 bytes |
| Actual SQLite index | 2,048,000 bytes |
| Maximum compact UTF-8 query | 668 bytes |
| Maximum candidate evidence pack | 56,046 bytes |
| Maximum query + candidate pack | 56,701 bytes |

The measured bounds pass the frozen actual-bundle latency/memory/index ceilings.
They are not a universal SLA or product-quality verdict. Memory is Windows
`GetProcessMemoryInfo PeakWorkingSetSize` and includes capture preparation, not an
isolated SQLite memory peak. Hardware metadata is incomplete: `platform.machine()`
and `platform.processor()` returned empty strings. Available environment:
Windows 11 build 26200, Python 3.14.6 / MSC v.1944 64 bit AMD64, SQLite 3.50.4.
No additional host probes were authorized for this lane.

Brief/context allocations are absent from this route; controlled bytes are query
plus pack only. Tokens and provider cost are null, not inferred from bytes.
The 10,000-row synthetic headroom lane was not run or rebuilt.

## Commands, TDD and verification

Commands run from the repository root with `.venv/Scripts/python.exe -B`:

| Command suffix | Result |
| --- | --- |
| `evals/plugin-v1/evaluate_retrieval.py --quality-plan evals/plugin-v1/quality-plan.json` | exit 0; 24 frozen cases/pins valid; design only |
| `-m unittest discover -s tests -p test_plugin_retrieval_eval.py -k frozen_policy_candidate_ceiling -v` | expected RED exit 1: explicit policy cap rejected; minimal helper change then GREEN exit 0 |
| `-m unittest discover -s tests -p test_plugin_quality_runner.py -v` before implementation | expected RED exit 1: runner file absent |
| `-m unittest discover -s tests -p test_plugin_retrieval_eval.py -v` | initial exit 1: one sandbox TEMP fixture `PermissionError`, 33 other cases pass |
| workspace-temporary override command below | exit 0; 34/34 scorer tests |
| `-m unittest discover -s tests -p test_plugin_quality_runner.py -k valid_no_match_sample -v` | expected RED exit 1 for timing controller's valid-no-match rejection; measurement repair GREEN |
| `-m unittest discover -s tests -p test_plugin_quality_runner.py -v` final | exit 0; 13/13, including full-rank unknowns, typed failures, macro nulls, route/secondary baseline, constraint/budget distinction, no-match mismatch and amendment provenance |
| `evals/plugin-v1/run_quality.py --predeclare --plan-sha256 e895c54ef78505ca6bcbe12edd7385d43351b78dfd915a238cd20ea7a9bcdaa7` | exit 0; source/measurement frozen before capture |
| same runner `--run` and hash | exit 1 observed; all 24 captures retained, timing aborted at valid no-match sample |
| same runner `--predeclare-measurement-amendment` and hash | exit 0; separately bound original observations and measurement repair |
| same runner `--resume-measurement` and hash | exit 1; retained `no_go`, 30/30 cold and 30/30 warm samples complete |
| `evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json` | exit 0; four C8 cases valid |
| same scorer with `--results tests/fixtures/plugin_retrieval_eval.json` | exit 0; four synthetic captures compatible, `synthetic_compatibility_only` |
| actual C9 schema + artifact integrity check | exit 0; 72 actual query/result/pack objects, 24 baseline transport pack objects, five exact artifact hashes valid; original observation bytes unchanged |

Comparable temporary-fixture retry (no ACL or permission change):

```powershell
New-Item -ItemType Directory -Force .codex-tmp/cp04-tests | Out-Null
.venv/Scripts/python.exe -B -c "import tempfile,unittest; from pathlib import Path; tempfile.tempdir=str(Path('.codex-tmp/cp04-tests').resolve()); suite=unittest.TestLoader().discover('tests',pattern='test_plugin_retrieval_eval.py'); result=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(not result.wasSuccessful())"
```

The virtualenv emits `Failed to find real location of C:\Python314\python.exe`
while completing the passing checks. It was recorded once as a launcher diagnostic;
no installation or unrelated environment repair was attempted.

## Ownership, limits and handoff

Owned executable changes: new `run_quality.py`, baseline ceiling compatibility in
`evaluate_retrieval.py`, new `tests/test_plugin_quality_runner.py`, one named cap
test in `tests/test_plugin_retrieval_eval.py`, appended `runner-contract.md`, and
this lane's declaration/observation/amendment/performance/summary/hash/evidence files.
Quality Evaluator retains acceptance-test ownership; builders may run these named
tests but must not weaken them. Runtime, source/catalog assets, policy, frozen
quality plan/rubric, writer/renderer, protected configuration and unrelated dirty
files were preserved. No Git operations or external activation occurred.

The parent accepted the narrow measurement-controller repair and separate
provenance amendment. CPU description/architecture completeness remains an explicit
metadata gap. Human relevance adjudication, actual paired RU/EN meaning,
browser/no-call switching, saved/published recovery, fresh agent routing, synthetic
headroom, installation/release and live freshness are open; this lane does not
claim those accepted.

Next owners: Product Planner and Catalog Architect should decide a prospective,
versioned oracle/case correction and new pre-run split/stratum contract; preserve
this frozen-v1 failure evidence. Quality Evaluator executes a later independently
frozen complete-pool run. CP-11 owns runtime/state/publication/headroom evidence;
CP-15 owns human usefulness and actual browser/localization acceptance. Agent-only
calibration/review artifacts are supporting evidence, not human acceptance.
