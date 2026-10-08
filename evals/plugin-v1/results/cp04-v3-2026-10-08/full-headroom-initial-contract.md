# CP-04 V3 Full Synthetic Reader/Card/Pack Capacity

Status: implementation pending independent review and prospectively declared capture.
Owner: Quality Evaluator. This contract owns only the new isolated harness,
its named unit tests and exclusive `results/cp04-v3-2026-10-08/full-headroom/`
artifacts. Shared runtime and production assets remain under their existing owners.

## Trust And Execution

The evidence label is `shared_full_reader_engine_under_exact_fixture_trust`.
The harness accepts only `.codex-tmp/cp04-v2-headroom/` and the four exact fixture
files named by the versioned v2 `headroom-adapter-declaration.json`. It verifies
that declaration and `headroom-fixture.json` against fixed SHA-256 anchors before
using their hashes, expected count, expected file sizes and pins. The snapshot is
exactly 54,378,585 bytes; the index is 8,474,624 bytes; the frozen snapshot contains
10,000 distinct positive numeric IDs. The exact synthetic plan hash binds the ten
original development cases and the original query schedule. No supplied manifest,
supplied trust hash, arbitrary fixture path or runtime monkeypatch is accepted.

For every measured sample the harness reads and hashes the entire snapshot, parses
the entire JSON corpus, and calls `_cards_from_verified_snapshot` for the exact
count, identity and envelope pins. All cards must also preserve card schema and
corpus kind. `_select_verified_cards` requires canonical equality between supplied
candidate cards and the verified corpus. This uses a bounded test seam, not the
production trust anchor. The production entrypoint must separately return
`index_incompatible` for this synthetic manifest. The production fixed public
manifest, 2,500-card count, 32 MiB snapshot limit and one-card synthetic trust remain
unchanged. No production fixture acceptance is claimed.

The shared `_retrieve_verified_bundle` performs complete native C9 retrieval:
query validation, immutable read-only SQLite, exact index hash, full/cached bundle
validation, bounded variants, weighted FTS5 ranking, RRF, identity dedupe, matched
fields and the real result envelope. `_build_evidence_pack_from_trusted_cards`
performs real eligibility, selection, exclusions, byte budgets and pack bindings.
The harness preserves all result and pack fields and records full synthetic
captures. It rejects missing candidate coverage, overlapping packed/excluded IDs,
fake pack scores, changed raw ranks/matched fields, incomplete variants or budgets.
Denied candidates remain represented by exclusions and retain their native ranks
in the captured retrieval result.

## Prospective Measurement

Predeclare 30 cold samples and 30 warm samples with one discarded warmup, cycling
the same ten frozen v2 synthetic development queries three times. Cold samples
use separate child processes; warm samples use one controller process, a fresh
immutable connection and full snapshot reading/parsing per sample. OS caches are
not flushed; imports, source verification and process startup are outside timers.
The original retrieve-only thresholds remain 500 ms cold p95, 200 ms warm p95,
256 MiB process peak memory and 64 MiB index bytes. Nearest-rank p50/p95 are used.

The retrieve-only timer includes manifest/policy validation and the complete
shared reader. The v2 adapter timed manifest/policy/query validation, connection,
bundle/index validation and bounded SQL; V3 additionally measures native RRF,
highlight/result construction and connection close because they belong to the
shared core. There is no changed or fabricated end-to-end SLA. Separate timers
record fixture hashing, full JSON parsing, card normalization, canonical candidate
card selection, real evidence-pack construction, serialization/guards and total
end-to-end time. Raw query/result/pack UTF-8 bytes, maxima, full candidate coverage
and raw-rank fidelity are recorded. Brief/context is unmeasured; exact tokens and
provider cost are null. No model or provider is invoked.

Memory is Windows process-lifetime `PeakWorkingSetSize`, including whole parsed
corpus, raw byte buffers, actual pack, imports and evaluator allocations; the
maximum controller/child value is retained. It is not isolated SQLite memory.
Full JSON parsing is the accepted initial approach. If the memory gate fails,
retain `no_go`; stop without streaming, raising limits or optimizing runtime.

The declaration binds every repository execution dependency, runtime/core/cache
tests, versioned trust evidence, public baseline assets, fixtures, harness and
contract. It records CPU, OS, Python executable/version, SQLite and architecture.
Current source/fixture/environment equality is checked before each child capture,
after each child, and before and after parent measurement. Loaded runtime bytes
must match the declaration. Outputs and failure artifacts use exclusive writes.
No earlier failure or capture is overwritten.

## Commands And Gates

Run the primary named unit tests without requiring the ignored scale fixture:

```powershell
.venv/Scripts/python.exe -B -m unittest tests.test_plugin_full_headroom_v3 -v
```

They use versioned C8 and contract fixtures for exact-byte trust negatives,
duplicate IDs, card schema/corpus mismatch, tampered card equality, denial and
complete coverage, fake scores, request byte/hit limits and nanosecond/percentile
units. Acceptance remains with Quality Evaluator; runtime core/cache tests are
explicitly handed back to the primary owner for coordinated verification.

After independent review and `ACTUAL_MEASUREMENT_DONE` from the primary owner:

```powershell
.venv/Scripts/python.exe -B evals/plugin-v1/measure_full_headroom_v3.py --predeclare
.venv/Scripts/python.exe -B evals/plugin-v1/measure_full_headroom_v3.py --run
```

`full_card_pack_capacity_measured=true` is emitted only after all sixty full
samples and the production-negative check complete. It means the complete
synthetic reader/card/pack route was measured, even if a capacity gate fails.
Incomplete execution emits a retained failure artifact with this flag false.
Passing yields `synthetic_full_capacity_pass_only`; any threshold failure yields
`no_go`. `production_entrypoint_accepted=false`, `relevance_claim_allowed=false`,
`human_acceptance=false` and `promotion_ready=false` always remain explicit.
Scaling evidence cannot promote retrieval relevance, semantic coverage, real
catalog growth, RU/EN meaning, browser/lifecycle behavior or integration usefulness.
