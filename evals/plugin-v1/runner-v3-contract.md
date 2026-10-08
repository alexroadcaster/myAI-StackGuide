# CP-04 fresh source-supported held-out runner V3

Quality Evaluator owns the validator, runner, named oracle/runner tests and exclusive
`results/cp04-v3-2026-10-08/held-out/` outputs. Product Planner owns prospective source
criteria/oracle; primary accepts source review, live qualification and frozen bytes.
Implementation READY is separate from ORACLE_FREEZE_READY and runtime cores READY.
Do not predeclare or capture until both execution gates are explicitly delivered.

## Inputs and source contract

`quality-oracle-v3-source.json` is `cp04_quality_oracle_source_v3`, bounded to 4 MiB.
The production snapshot uses its unchanged 32 MiB reader ceiling; hash-only large
catalog lineage is never loaded wholesale. Strict JSON rejects duplicate keys and
nonfinite values. Validate pinned snapshot/manifest/index/policy/taxonomy, source
hashes, exact pointers/values, numeric owners, dates, complete primary/secondary
routed universes, sorted IDs, grade/status/unknown parity, functional evidence,
declared supporting criteria, source projections and source-query digests. Grade
criteria remain semantic review requirements; mechanical validation cannot judge
natural-language relevance or authenticity.

Every source grade remains independent of matcher output. Grade zero is reviewed
unrelated; null is unknown, never zero/weak-positive. Adoption remains unknown.
Hard defaults are independently source-assessed; missing archived facts are unknown,
not an inferred pass. All threshold values link to exact frozen V2 file/pointers.
No historical labels/results supply new relevance labels. Old artifacts remain
unchanged; their hashes are retained only for integrity, never scored as new data.

Supplemental public qualification must be a pinned local
`cp04_public_qualification_v1` artifact. Each live evidence pointer resolves exactly
to `/records/N/requirement_checks/M`; owner case, numeric GitHub ID and canonical
repository join to the source oracle/card. Exact value, HTTPS URL and observation
date must match the local check. Only declared public-primary source kinds and
supported/unsupported/unknown dispositions are allowed. No external URL alone is
trusted evidence. Source excerpts remain bounded. Source meaning, official-source
identity and an unsupported-versus-unknown decision require independent pre-capture
review. This runner performs no public retrieval, catalog update or provider call.

For `public_primary_live` only, accept either a valid UTC timestamp ending `Z` or
an exact ISO calendar date `YYYY-MM-DD`. Date-only qualification is narrowly allowed
when schema is `cp04_public_qualification_v1`, `qualification_date` equals that
check's unchanged `observed_at`, and
`metadata_gaps.observation_timestamp_semantics` is exactly:

> observed_at is the UTC retrieval date, not source update/push/commit/release date; search crawl ages are not repository activity.

The derived validation report adds `observation_granularity=day` while preserving
the literal date, source evidence value and artifact SHA. No midnight timestamp is
synthesized. Partial dates, invalid calendar dates, trailing text, undeclared day
precision and qualification-date mismatches fail. Snapshot observation validation
retains its exact source binding; no other source-kind date rule is weakened.

## Three arms and rank fidelity

All 15 cases use the same frozen terms, query grammar, constraints, source universes,
policy/request caps and k. Fourteen functional cases cover the 14 domain leaves;
one genuine secondary-route case is a separate diagnostic, never part of semantic
macro. Domain leaves do not prove container semantic queries or a full route sweep.

1. Control: unchanged production single-OR FTS, actual C9 scores/ranks/fields plus
   canonical evidence pack.
2. Candidate: distinct literal term-field coverage over control's actual bounded
   fetched pool, numeric-ID ties, no appended IDs/full-catalog fallback. Raw C9
   result is preserved. Selection uses a transient adapter to the trusted pack
   builder, then restores every selected card's original retrieval rank/RRF/fields
   and adds `selection_rank`. The saved projection is explicitly
   `experimental_notcanonical=true`, `current_policy_fulfilled=false` and
   `executed_c9_rrf=false`; selection cannot impersonate canonical C9 policy.
3. Baseline: unchanged literal-field-or-v1 over the exact routed cards/terms, existing
   matcher/pack adapter. Placeholders are labeled experimental literal transport,
   never actual BM25/RRF or a canonical FTS pack.

Retain canonical raw result/pack and separate experimental projection. FTS category
IDs+titles versus literal titles is an unchanged declared field-content difference.
No shipping ranking or schema/policy semantics are changed by this experiment.

## Metrics, gates and frozen execution

Source-supported non-denied grades1..3 form the full denominator, including
unretrieved positives. Denied gains are zero in original rank positions. Any
unknown anywhere in a complete returned ranking, even below top12, makes official
metrics null and no_go. Unjudged/duplicate IDs and typed failures invalidate the
case. Valid no-hit with positives scores zero; no supported-positive denominator
is null. Unknown universe/raw IDs and positions remain visible; no unknown fraction
threshold is invented. A macro cannot omit a null case.

Every arm receives independent macro, domain/tag strata, numeric threshold,
baseline non-regression, raw coverage, constraint/exclusion/dedupe/survival and byte
gates. Control may pass; candidate does not become necessary merely because it was
implemented. Semantic pass is `semantic_pass_needs_owner_acceptance`, never human
calibration or product promotion. Broader alias, container query, exhaustive route,
capacity, recovery, browser/RU-EN meaning and human-usefulness gates stay explicitly
unmeasured; product quality remains no_go until those separate requirements close.

`--predeclare` binds exact source/code/runtime/test/threshold/case/query bytes before
ranking. `--capture --gate ...` requires the same declaration plus accepted review,
oracle/declaration/retrieval-runtime/pack-runtime hashes and a contained independent
review artifact/hash. Hashes bind bytes, not reviewer authenticity. Recheck sources
after capture. Outputs are exclusive; source/query/grade changes after exposure
require a new reviewed experiment and fresh held-out where semantic meaning changes.

```powershell
.venv/Scripts/python.exe -B evals/plugin-v1/validate_oracle_v3.py --check
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_quality_oracle_v3.py -v
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_quality_runner_v3.py -v
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v3.py --predeclare
.venv/Scripts/python.exe -B evals/plugin-v1/run_quality_v3.py --capture --gate <owner-heldout-freeze-gate.json>
```

Gate keys: `accepted`, `reviewer`, `independent_review_completed`, `oracle_sha256`,
`declaration_sha256`, `runtime_sha256`, `pack_runtime_sha256`,
`independent_review_path`, `independent_review_sha256`. The first four exact hashes
bind prospective inputs/current method; the review path is repository-contained.
All outputs stay in the held-out result directory. Exit0 means valid declaration
or at least one source-supported semantic arm passed; exit1 retains all-arm
semantic failure; exit2 is invalid/unavailable evidence. Every promotion flag is
false. No inference latency/cost, 10k benchmark, state/browser/runtime release or
successful integration is claimed.
