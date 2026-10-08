# CP-04 V3 R2 Streamed Synthetic Reader/Card/Pack Capacity

Status: implementation pending independent review and prospectively declared capture.
Owner: Quality Evaluator. This contract owns only the new isolated harness,
its named unit tests and exclusive `results/cp04-v3-2026-10-08/full-headroom-r2/`
artifacts. Shared runtime and production assets remain under their existing owners.

The original complete-JSON capture remains immutable in `full-headroom/` with
`no_go`: process peak was 523,108,352 bytes against 256 MiB. Its original harness,
contract and tests are retained as `full-headroom-initial-{source.py,contract.md,tests.py}`.
This owner-authorized R2 amendment measures the shared streamed card representation
after that failure. It does not retrospectively rewrite the original methodology,
source bindings, thresholds or verdict, and does not claim a retained whole JSON array.

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

For every measured sample the harness hashes all four complete fixture files in
bounded blocks before retrieval or parsing. Only the small manifest and policy
are read into byte buffers. The complete shared retrieval core returns candidate
IDs; `_stream_verified_snapshot_cards` then validates the entire pinned snapshot
while retaining only requested cards. The same production helper checks SHA-256
before parser construction on the open handle, seeks to its start, and checks
SHA-256 again after complete EOF. It enforces strict UTF-8, complete JSON, exact
envelope/schema/corpus pins, every card's version and corpus, all unique positive
numeric IDs, exact count and requested coverage. `_select_verified_cards` requires
canonical equality between supplied candidates and the cards selected from the
verified file. `validated_card_count=10000` is recorded separately from
`retained_card_count<=150`; the latter is never presented as the full count.
This uses a bounded test seam, not the production trust anchor. The production entrypoint must separately return
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
immutable connection and complete shared snapshot streaming per sample. OS caches are
not flushed; imports, source verification and process startup are outside timers.
The original retrieve-only thresholds remain 500 ms cold p95, 200 ms warm p95,
256 MiB process peak memory and 64 MiB index bytes. Nearest-rank p50/p95 are used.

The retrieve-only timer includes manifest/policy validation and the complete
shared reader. The v2 adapter timed manifest/policy/query validation, connection,
bundle/index validation and bounded SQL; V3 additionally measures native RRF,
highlight/result construction and connection close because they belong to the
shared core. There is no changed or fabricated end-to-end SLA. Separate timers
record bounded-block fixture hashing, small manifest/policy parsing, complete
shared card-file verification (including both hash passes), canonical candidate
card selection, real evidence-pack construction, serialization/guards and total
end-to-end time. Raw query/result/pack UTF-8 bytes, maxima, full candidate coverage
and raw-rank fidelity are recorded. Brief/context is unmeasured; exact tokens and
provider cost are null. No model or provider is invoked.

Memory is Windows process-lifetime `PeakWorkingSetSize`, including bounded
file/hash/parser buffers, all-ID validation sets, retained requested cards, actual
pack, imports, controller-retained captures and evaluator allocations; the
maximum controller/child value is retained. It is not isolated SQLite memory.
Baseline hash reconstruction reads the prior sixty captured query/result/pack
objects transiently before measurement; its allocations still count toward the
process-lifetime peak. No stage silently loads the entire 10,000-card source array.
If a gate fails, retain `no_go`; stop without raising limits or further optimizing
runtime under this packet.

The exact prior performance bytes are pinned by SHA-256
`c9de5fdc836776c5f70286575cbd9e20585c277a3aceffb5e7b8af565ccc73cf`.
Before timing, the declaration recomputes canonical query/result/pack hashes from
all sixty historical captures and requires stable hashes for each of the ten
queries. Every R2 sample recomputes those three hashes from its real output and
requires exact equality. Timing and memory are excluded from this output-fidelity
comparison. All ten cases must match across both thirty-sample schedules. This is
capacity representation parity; it does not use judgments, tune queries, grade
held-out relevance or permit oracle/ranking changes.

The declaration binds every repository execution dependency, runtime/core/cache
tests (including `test_plugin_streamed_cards.py`), versioned trust evidence,
preserved initial sources/captures, public baseline assets, fixtures, harness and
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
units. The six original protections remain. Four additional tests cover bounded
file hashing, complete validation versus retained requested-card count, malformed
unselected IDs/version/corpus/count/requested coverage, hash rejection before
parser construction, and canonical prior-capture fidelity. Acceptance remains
with Quality Evaluator; runtime core/cache/stream tests are
explicitly handed back to the primary owner for coordinated verification.

After independent review and the primary owner's explicit
`ACTUAL_MEASUREMENT_DONE`, `STREAM_RUNTIME_READY`, `ASTRA_STREAM_CLEAR` and
`HARNESS_REVIEW_CLEAR` signals, with runtime and harness sources frozen:

```powershell
.venv/Scripts/python.exe -B evals/plugin-v1/measure_full_headroom_v3.py --predeclare
.venv/Scripts/python.exe -B evals/plugin-v1/measure_full_headroom_v3.py --run
```

`full_card_pack_capacity_measured=true` is emitted only after all sixty full
samples, exact prior-capture fidelity and the production-negative check complete.
It means the complete synthetic reader/streamed-card/pack route was measured,
even if a capacity gate fails. It does not describe a whole retained JSON corpus.
Incomplete execution emits a retained failure artifact with this flag false.
Passing yields `synthetic_full_capacity_pass_only`; any threshold failure yields
`no_go`. `production_entrypoint_accepted=false`, `relevance_claim_allowed=false`,
`human_acceptance=false` and `promotion_ready=false` always remain explicit.
Scaling evidence cannot promote retrieval relevance, semantic coverage, real
catalog growth, RU/EN meaning, browser/lifecycle behavior or integration usefulness.
