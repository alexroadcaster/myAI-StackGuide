# CP-04 source-qualified capability package — 2026-10-08

## Outcome

A reproducible candidate bundle enriches 12 of 2,500 cards with source-qualified
capabilities, prerequisites and limitations. Compatibility passes; neither tested
ranking method qualifies against both original baselines. Parent CP-04 remains
`in_progress / partially_verified / no_go`. No subagents or Git actions were used.

## Implementation

- [Public input](../../data/plugin_capability_enrichment.json) contains exact numeric
  identities, frozen names, upstream GitHub sources and observation dates. Coverage
  spans Kotlin backends, browser testing/uploading, metadata and portfolio optimization.
  These facts do not establish integration readiness or implementation time.
- [Input schema](../../specs/catalog/capability-enrichment.schema.json) and
  [builder](../../scripts/build_plugin_capability_package.py) reject malformed,
  duplicate and mismatched facts. Source URLs must belong to the joined repository.
  `tus-node-server` is absent from the frozen catalog; no new identity is introduced.
- The builder preserves status, eligibility, aliases, metadata and activity. Original
  broad advisory evidence is narrowed to its original fields; new fields receive
  precise upstream or curator evidence. Observation dates use midnight UTC as a
  date-only convention. Branch URLs are dated observations, not upstream commit pins.
- The original source SHA identifies frozen base lineage. A distinct snapshot ID,
  card SHA and build receipt bind the candidate input. RepositoryCardV2/ActivityV2
  `2.0.0`, policy `2.1.0` and index format `3` are preserved. Default assets, reserved
  advisory seed, builders and runtime trust anchors are unchanged.

## Comparison

The [contract](../../evals/plugin-v1/capability-package-contract.md) freezes ten exposed
development cases, existing source-based grades and unchanged thresholds before
capture. Metrics retain the constrained full routed-universe denominator and original
ranks. Higher is better. Input selection used exposed cases; this is not fresh evidence.

| Method | Recall@12 | nDCG@12 |
| --- | ---: | ---: |
| Original FTS5 | 0.721493 | 0.812905 |
| Original literal-field baseline | 0.804899 | 0.874555 |
| Enriched package FTS5 | 0.721493 | 0.817353 |
| Same literal algorithm on enriched cards | 0.779899 | 0.860174 |

Enriched FTS increases macro nDCG by 0.004448 without increasing recall. Its browser
uploader nDCG improves 0.520169 → 0.593777. Global BM25 statistics also change ordering
outside enriched routes: Go API nDCG decreases 0.949086 → 0.940484; resumable-upload
nDCG decreases 0.659180 → 0.638655. This is a measured cross-route regression.

The enriched literal arm loses a known relevant mobile-testing result: React Native
recall 1.0 → 0.75 and nDCG 0.810884 → 0.689190. Additional generic testing/component
words change ranking among browser/mobile alternatives. Valid capability evidence
does not automatically improve context precision. No grade or threshold was adjusted.

The exposed Kotlin regression retrieves 5/5 supported positives instead of 2/5;
top12 contains 3/5 instead of 1/5. Wider-universe unknowns are retained, so no Kotlin
recall/nDCG or fresh held-out acceptance is claimed. Prior TinyBERT composition
was not repeated in this slice.

Both candidate arms retain valid development rankings and zero observed hard
constraint violations, false exclusions or duplicate canonical IDs. Both fail
recall and nDCG non-regression against the stronger original literal baseline.

## Trust and reproducibility

Public retrieval returns `index_incompatible` for the unactivated candidate in all
ten scenarios; public packing rejects its pins after successful fixture retrieval.
The [evaluator](../../evals/plugin-v1/run_capability_package.py) verifies the predeclared
receipt and every file hash plus full logical SQLite parity before entering existing
private verified-bundle reader/pack seams. Query/bundle checks, index hashing,
immutable read-only SQL, matching, provenance and budgets still execute. No anchor
is patched or guard disabled. Literal rank adapters are not BM25/RRF observations.

The first declaration's setup failure is preserved: the harness incorrectly expected
public retrieval to accept an unactivated manifest. No observations were saved there.
The correction received a new declaration before capture.

- [Failed setup](../../evals/plugin-v1/results/cp04-capability-package-2026-10-08/comparison/setup-failure.json).
- [Successful declaration](../../evals/plugin-v1/results/cp04-capability-package-2026-10-08/comparison-v2/declaration.json):
  SHA256 `1fb8305bd24ecb071a995fb10152055f30d25bc44768a32bcde9c63775296151`.
- [Compact summary](../../evals/plugin-v1/results/cp04-capability-package-2026-10-08/comparison-v2/summary.json).
- [Observations](../../evals/plugin-v1/results/cp04-capability-package-2026-10-08/comparison-v2/observations.json):
  3,668,979 bytes including four arms' public evidence packs.
- [Candidate receipt](../../evals/plugin-v1/results/cp04-capability-package-2026-10-08/candidate/build-receipt.json)
  and [reproduction receipt](../../evals/plugin-v1/results/cp04-capability-package-2026-10-08/reproducibility/build-receipt.json).

## Current checks

- Observable RED: the stub fails added-field provenance/new snapshot identity and
  rejection of mismatched names, duplicates, invalid URLs and oversized facts.
  The initial missing-module setup failure was corrected before behavioral RED.
- `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_capability_package.py`:
  3/3 pass; all 2,500 cards/activity objects validate; preservation, deterministic
  projection and positive/negative source boundaries pass.
- `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_capability_evaluator.py`:
  2/2 pass; unpinned receipt and altered card bytes are rejected before fixture entry.
- `.venv/Scripts/python.exe -B scripts/build_plugin_capability_package.py` and a second
  build with `--output evals/plugin-v1/results/cp04-capability-package-2026-10-08/reproducibility`:
  all four assets and receipt reproduce byte-for-byte. SQLite verifies 2,500 rows,
  2,630 classifications, 126 routes/162 members, logical projections and write rejection.
- `.venv/Scripts/python.exe -B scripts/build_plugin_search_index.py --check`:
  original package retains exact default-build parity.
- Evaluator `--predeclare` then `--run`: four arms/ten cases captured; declaration
  sources remain unchanged. No candidate arm qualifies for held-out review.

## Remaining work

Preserve the stronger baseline and distinguish required product capabilities from
contextual stack words in the next ranking slice. Include the observed mobile/browser
and global BM25 regressions. Do not equate capability word frequency with feature fit.
Before activation: development non-regression, fresh independent held-out judgments,
RU/EN/resource evidence, human usefulness and joined CP-11/15 acceptance remain open.
This run does not evaluate composed user answers covering architecture, product value,
complexity, time assumptions and reuse versus developing from scratch.

Rollback means retaining the unchanged canonical bundle. The candidate builder requires
a new results directory and cannot overwrite active assets or previous outputs.
