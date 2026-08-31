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

## Historical evidence

[Retained history](reports/catalog-refresh-history.md) and
[storage migration evidence](reports/catalog-refresh-storage-migration.json) describe
the earlier anonymous/full-card and work-retirement checkpoints. Their hashes and
commands are historical, not current authentication or whole-corpus freshness proof.
Old RUNLOG paths identify archive members. Current standalone parity command:

```powershell
python -B scripts/build_catalog_html.py --check
```
