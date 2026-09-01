# Catalog gap filling and replacement research

## Current owner-authorized mode

The owner authorizes GitHub authentication for GET-only public catalog research.
Fill missing values, preserve filled values, and verify stored Stars below 500 or
unknown. Confirmed low-Star entries receive replacement proposals, not automatic
canonical substitutions. A metadata call may return a whole field group; only
requested missing values enter the sparse patch set. Stars >= 500 are not scheduled
for wholesale refresh. An incidentally observed lower value still triggers review.

The canonical catalog remains `data/catalog_manifest.json`; the HTML builder is
`scripts/build_catalog_html.py`. This maintenance collector is not plugin runtime.
The source has gaps in all 1,800 rows, including missing Stack in 1,799. Scanning all
rows locally is cheap and is not a request to refresh every filled field. The
initial gap plan flags 943 low/unknown stored Star values. Empty/unknown/null fields
are missing; zero counts and false boolean values remain legitimate facts.

## Ready-made GitHub client

Use the installed official GitHub CLI (`gh api`, verified version 2.90.0).
`scripts/github_cli_transport.py` is a narrow adapter, not a new HTTP/OAuth client:
it fixes GET, host and allowed endpoints, bounds process output/time and suppresses
diagnostic output. Tokens are never extracted into Python, supplied as CLI arguments
or persisted. `GH_DEBUG` is disabled for child requests. No package installation,
OAuth application registration, GitHub write, private corpus access or LLM call is
part of this mode. The selected account is the one used by GitHub CLI for github.com.

Alternatives reviewed against [GitHub's client list](https://docs.github.com/en/rest/using-the-rest-api/libraries-for-the-rest-api?apiVersion=2026-03-10):

| Option | Decision |
| --- | --- |
| Official GitHub CLI | Use now: installed, existing authorization, response headers, JSON and explicit single-page requests |
| PyGithub | Viable Python SDK, not installed; would require dependency setup and deliberate retry/lazy-call budgeting |
| Official Octokit JavaScript | Viable official SDK, but adds another runtime to the existing Python pipeline |

References: [gh api](https://cli.github.com/manual/gh_api),
[PyGithub configuration](https://pygithub.readthedocs.io/en/stable/github.html).
Do not enable automatic pagination or CLI caching for fresh metadata in this
adapter. Search pages are explicit and bounded. CLI transport invocations are
counted locally; GitHub headers own real quota consumption, including client-side
redirect behavior and other consumers of the account quota.

## Storage and commands

| Content | Location |
| --- | --- |
| Current source, taxonomy projection, contract | `data/catalog_manifest.json`, `specs/catalog/taxonomy.yaml`, `specs/catalog/enrichment-field-contract.json` |
| Accepted canonical public evidence | `data/catalog-evidence/2026-08-31/` |
| Current selective successor | `.codex-tmp/catalog-refresh/gaps/` |
| Previous full-card run, retained unchanged as history | `.codex-tmp/catalog-refresh/active/` |
| Retired work archive | `.codex-tmp/catalog-refresh/work-retirement-2026-08-31/retired-work-and-migration-baseline.zip` |

`work/` is not needed. Local run folders are ignored, not backed up by Git; preserve
them while unfinished. The previous full-card run is frozen after the code change:
do not run its old commands without migration. Its 13 records, curation, request
log and counters were copied into the selective successor. The original 80 attempts
and 1,309,367 bytes remain charged; code pins changed explicitly, never bypassed.

Run from the repository root:

```powershell
python -B scripts/catalog_gap_fill.py preflight --run-dir .codex-tmp/catalog-refresh/gaps
python -B scripts/catalog_gap_fill.py run --run-dir .codex-tmp/catalog-refresh/gaps --max-requests 150 --max-records 25
python -B scripts/catalog_gap_fill.py report --run-dir .codex-tmp/catalog-refresh/gaps
python -B scripts/run_catalog_gap_fill_batches.py --run-dir .codex-tmp/catalog-refresh/gaps --max-rounds 4 --requests-per-round 1000 --records-per-round 250
python -B scripts/prepare_catalog_semantic_review.py --run-dir .codex-tmp/catalog-refresh/gaps --batch-size 10 --replacement-batch-size 20
```

One bounded invocation performs its selected records sequentially without LLM
handoffs. The run stops on its request, record, elapsed-time or provider quota
boundary. Successful blocks are reused; only failed blocks are retried. Authentication
failure halts the run; permission errors are not treated as quota exhaustion.
The auth preflight must confirm an authenticated quota; there is no silent anonymous
fallback. It records core and search buckets separately. A rate-limited response
conservatively pauses the current invocation, including search. No recurring task
is installed. The preflight adds one transport attempt outside the requested work
budget and does not consume GitHub's primary quota.

The batch driver repeats those same bounded invocations in the foreground. It does
not change the frozen collector plan or reset cumulative request/byte counters. It
stops on a quota wait, authentication/transport halt, completed queue, lack of
progress or its explicit round limit. Interrupting it leaves the per-request
checkpoint reusable; it is not a scheduler or background automation.

GitHub repository IDs are numeric identities. The collector accepts an equivalent
positive decimal string from the frozen JSON input because older catalog rows store
some verified IDs as strings while GitHub returns JSON integers. This normalization
does not accept names as identity evidence or coerce arbitrary values. A checkpoint
created with the former strict type comparison requires one explicit local migration:

```powershell
python -B scripts/migrate_catalog_numeric_ids.py --run-dir .codex-tmp/catalog-refresh/gaps
```

The migration re-normalizes saved derived records, rebuilds the numeric identity and
alias map, reruns reports and preserves source blocks plus cumulative request/byte
counters. It writes `identity-type-migration.json` with before/after record hashes
and refuses to run twice. It performs no network or canonical catalog write.

The completed CAT-05 run also required a pinned collector migration after large
single-commit responses exceeded the 1 MB safety cap. The collector now resolves
the default branch through the compact Git ref and Git commit object endpoints.
A successful GitHub response with an unsupported README representation or a body
over the configured cap is retained as terminal `source_unsupported` evidence;
repeating the same request cannot consume the queue indefinitely. Existing observed
blocks are not refetched. Apply the explicit migration only to a compatible saved
run:

```powershell
python -B scripts/migrate_catalog_compact_commit_endpoint.py --run-dir .codex-tmp/catalog-refresh/gaps
```

The migration refreshes the frozen field contract and integrity pins while
preserving all records, request logs, counters and curation. Its local migration
artifacts record both incremental applications used by the current checkpoint.

Start a new successor only in a nonexistent directory:

```powershell
python -B scripts/catalog_gap_fill.py prepare --run-dir .codex-tmp/catalog-refresh/new-gaps --reuse-run .codex-tmp/catalog-refresh/active
```

Reuse requires the same canonical input hash. Unrelated historical snapshots cannot
be merged implicitly. Without `--reuse-run`, planning starts from current sources.

## Outputs and limits

`gap-reports/patches.json` contains only missing-value edits and verified low-Star
corrections. `progress.csv` records per-repository scope; `field-completeness.csv`
reports all 71 contract fields. `review.json` identifies unsupported or semantic
gaps; `replacement-proposals.json` contains reviewed-next candidates, never accepted
swaps. Previously reviewed curation may be reused with its original evidence.
Missing Stack gets README/dependency evidence; literal dependency extraction does
not claim a finished semantic Stack. Optional exact activity totals are not silently
inferred from GitHub's combined issue/PR counts. Missing upstream facts stay explicit.

No command above writes canonical source or HTML. CAT-06 reviews unresolved Stack,
text and candidate fit; CAT-08 reconciles sparse accepted patches and rebuilds HTML.
Already-filled descriptions, taxonomy assignments and high Star values are preserved.
The scope does not include a fresh rewrite of all 1,800 full cards.

Search results require public visibility, new numeric identity and verified Stars
>= 500. Generic lists, archive projects and incompatible SDK languages must not be
presented as qualified substitutes. Keyword/language matching is only a screening
step: category fit, adoption trade-offs and the remaining candidate card need review.
A failed bounded search produces an unresolved vacancy, not a forced replacement.

## CAT-05 completed checkpoint

The 2026-09-01 checkpoint has visited all 1,800 source rows. It contains 1,641
processed rows and 159 confirmed below-threshold rows, with no `not_started`,
`retry_required` or identity-conflict status. It prepared 29,538 sparse edits,
159 replacement lists and the complete 71-field CSV without LLM calls or canonical
writes. Of those lists, 151 contain at least one bounded-search lead and eight need
expanded CAT-06 research; every lead still requires semantic fit review.

The large stored-zero count was mostly stale or placeholder metadata. Among 806
stored-zero rows, live evidence found 768 at Stars >= 500, 25 below 500 and 13 with
Stars unresolved. Among 137 stored rows from 1 to 499, 134 remain below 500 and
three are now >= 500. Nine of 857 stored rows already at 500+ also have unresolved
current Stars. CAT-07 must keep all 22 unresolved rows pending rather than treating
them as zero or eligible.

Local verification normalized all 1,800 records without network, accepted all
29,538 edits under the missing-value or verified-Star-correction guard, reconciled
12,141 request-log start/finish pairs, found no retry/identity-conflict rows and
confirmed exact 5,806,093-byte HTML parity. These checks prove collection and local
checkpoint integrity. Semantic field quality, functional replacement fit, canonical
application, browser behavior and release readiness remain downstream work.

CAT-06 starts from `semantic-review/`, generated by
`scripts/prepare_catalog_semantic_review.py`. The current output contains 165
ten-repository semantic batches, eight replacement batches and a separate factual
gap queue. Each packet includes bounded upstream/README excerpts, dependency
declarations, available source facts and observed evidence refs. It does not create
curation files, accept fields, rank functional equivalence or modify canonical data.
This packaging keeps deterministic evidence preparation out of LLM context while
leaving semantic decisions explicit and reviewable.

CAT-06 completion uses `scripts/review_catalog_semantic_queue.py`. Its dry-run writes
a complete decision ledger; `--apply` merges only exact upstream descriptions and
minimal observed-language Stack values into the ignored checkpoint with network
access disabled:

```powershell
python -B scripts/review_catalog_semantic_queue.py --run-dir .codex-tmp/catalog-refresh/gaps
python -B scripts/review_catalog_semantic_queue.py --run-dir .codex-tmp/catalog-refresh/gaps --apply
```

The completed ledger covers 1,641 records and 17,978 fields. It accepts 1,595
minimal Stack values and 676 exact upstream descriptions. It leaves 39 Stack,
18 descriptions and 15,650 other semantic decisions unresolved. All 445
metadata-only replacement leads are rejected as functionally unqualified; no
replacement is accepted. CAT-07 owns identity, Stars and replacement-vacancy
reconciliation. Recommendation fields remain downstream readiness work and do not
exclude catalog records. The durable result is
`docs/reports/catalog-semantic-review-2026-09-01.json`.

## CAT-07 completed reconciliation

`scripts/reconcile_catalog_eligibility.py` consumes the saved CAT-05/06 evidence,
consolidates aliases by observed numeric GitHub identity, applies the strict Stars
catalog-inclusion gate, tracks recommendation readiness separately, reconciles every
exclusion/replacement decision and computes all thematic-leaf and distinct
container-union counts. Its outputs remain
under the ignored checkpoint in `eligibility-reconciliation/`; it does not write
the canonical manifest or HTML.

Run the bounded numeric-ID resolver once, then rerun locally as needed:

```powershell
python -B scripts/reconcile_catalog_eligibility.py --run-dir .codex-tmp/catalog-refresh/gaps --resolve-known-ids --max-resolutions 20
python -B scripts/reconcile_catalog_eligibility.py --run-dir .codex-tmp/catalog-refresh/gaps
```

The authenticated resolver uses only `GET /rate_limit` and
`GET /repositories/{id}` for unavailable saved names that already have a frozen
numeric repository ID. It does not search by name or accept a guessed rename.
The completed run resolved five renamed repositories, retained seven no-ID rows as
pending and consolidates ten previously verified aliases. One initial restricted
local attempt received no HTTP response and remains attempt 12,142 with only a
start trace; the successful authorized run added one preflight and five repository
responses. The cumulative counter is 12,148 and rerunning the resolver makes zero
new requests.

The corrected final gate keeps 1,624 repositories in the catalog, excludes 159
confirmed low-Star identities and retains seven unresolved-Star roots as pending.
Within the included set, seven cards are recommendation-ready and 1,617 carry a
downstream recommendation backlog; they are not rejected or removed. All 159
replacement vacancies are explicit; none of the 445 metadata-only leads is a
qualified replacement. All 111 thematic leaves are reported, with only
`embeddings_reranking` empty, and all 14 container counts are distinct descendant
unions. See
`docs/reports/catalog-eligibility-reconciliation-2026-09-01.json`.

## CAT-07A completed expansion candidate

CAT-07A runs in the separate ignored successor
`.codex-tmp/catalog-refresh/cat-07a/`. Its versioned policy is
`specs/catalog/catalog-expansion-policy.json`; the single-writer CLI is
`scripts/expand_catalog_candidate.py`. It reuses the bounded GitHub CLI GET
transport, keeps cumulative counters and never writes the canonical manifest or
HTML. The five operational stages are represented by these resumable commands:

```powershell
python -B scripts/expand_catalog_candidate.py prepare --run-dir .codex-tmp/catalog-refresh/cat-07a --base-run .codex-tmp/catalog-refresh/gaps --target-included 2500
python -B scripts/expand_catalog_candidate.py discover --run-dir .codex-tmp/catalog-refresh/cat-07a --max-search-requests 30
python -B scripts/expand_catalog_candidate.py collect --run-dir .codex-tmp/catalog-refresh/cat-07a --max-candidates 100
python -B scripts/expand_catalog_candidate.py finalize --run-dir .codex-tmp/catalog-refresh/cat-07a
python -B scripts/expand_catalog_candidate.py verify --run-dir .codex-tmp/catalog-refresh/cat-07a
```

`migrate-script` is an explicit local/no-network operation for a changed script,
policy or query pin. It archives the prior query map, records before/after hashes,
preserves the transport checkpoint and never resets request/byte counters. Do not
edit the ignored state or pins manually.

The completed run contains 2,693 distinct leads and 883 core-qualified cards. The
deterministic coverage-first, category-balanced freeze selects exactly 876 additions
and retains seven qualified overflow cards, producing exactly 2,500 identities from
the 1,624-identity CAT-07 baseline. It reports 111 thematic leaves, 14 distinct
container unions and no empty leaf. The formerly empty `embeddings_reranking` leaf
is covered by `huggingface/text-embeddings-inference`; its zero-base discovery route
requires both the GitHub `embeddings` topic and the same term in the repository name.
README-only matches cannot pass classification.

The final hard-gate counters are zero for duplicate numeric IDs, duplicate
names/aliases, selected Stars below 500, archived/non-public repositories and core
field failures. One initial sandbox-restricted preflight has a request-log start but
no finish and qualified no repository; the audit preserves it as unmatched attempt
1. The remaining 4,658 attempts have matching finishes. Selected factual observation
times span `2026-09-01T07:53:11.50308Z` through
`2026-09-01T09:33:44.455075Z`; these facts may drift.

The durable minimized report is
`docs/reports/catalog-expansion-2026-09-01.json`. The large ledger, core cards,
request trace and rollback snapshot remain in the ignored run. CAT-08 owns canonical
application. This completion does not establish recommendation quality, curator
acceptance, browser behavior, retrieval relevance, release readiness or publication.

CAT-08 must treat the expansion file as an addition-bearing candidate, not as a
standalone replacement manifest: it carries 876 full addition cards and 1,624
baseline source IDs. Reconcile it with the complete CAT-07 eligibility, alias and
semantic state. The pre-migration projection contains 2,485 identities in thematic
leaves, 15 included baseline identities in `uncategorized_review`, 2,615 thematic
placements and 2,630 direct placements including review. CAT-08 performs a bounded
evidence-backed review of those 15 identities, records retained-review outcomes,
and normalizes old/addition description, structured Stack, identity, activity and
provenance shapes before generation. No new discovery, taxonomy expansion or
CAT-07A replay is part of this handoff. CAT-09 measures exact source/output/browser
behavior; CAT-10 freezes the verified CP-06 input.

## CAT-08 canonical application

CAT-08 completed the pinned source-first merge without discovery or taxonomy changes:

```powershell
python -B scripts/apply_catalog_candidate.py plan --run-dir .codex-tmp/catalog-refresh/cat-08-v4
python -B scripts/apply_catalog_candidate.py apply --run-dir .codex-tmp/catalog-refresh/cat-08-v4
python -B scripts/apply_catalog_candidate.py verify --run-dir .codex-tmp/catalog-refresh/cat-08-v4
python -B scripts/build_catalog_html.py --check
python -B -m unittest tests.test_catalog_candidate_application tests.test_catalog_v5_pipeline -v
```

The final manifest SHA-256 is `d2acb067017707bf6a01fcdfcedf1cc5324719acc7648b449980a5d4cecb371e`; the 3,932,467-byte HTML SHA-256 is `2f1d77740f0652f518fa8b155d30c1cf35112cd5067875a76cd400445aaef8b2`. Counts are 2,500 repositories, 126 nodes, 2,630 placements, 2,488 thematic repositories and 12 review records. The compact projection retains displayed/searchable descriptions, aliases and Stack labels while keeping repository audit fields and unused top-level migration/evidence data in the canonical source. The transaction journal preserves exact failure recovery plus an operational current-renderer rollback. Browser/performance evidence remains CAT-09. Durable minimized evidence is `docs/reports/catalog-canonical-application-2026-09-01.json`.

## Historical evidence

[Retained history](reports/catalog-refresh-history.md) and
[storage migration evidence](reports/catalog-refresh-storage-migration.json) describe
the earlier anonymous/full-card and work-retirement checkpoints. Their hashes and
commands are historical, not current authentication or whole-corpus freshness proof.
Old RUNLOG paths identify archive members. Current standalone parity command:

```powershell
python -B scripts/build_catalog_html.py --check
```
