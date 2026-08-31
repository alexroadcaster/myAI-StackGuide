# Catalog refresh: durable sources and disposable run state

The catalog opens and builds without a `work/` directory. That directory contains
retired one-off task packages and is ignored by Git. It is no longer a source,
test fixture, evidence target or required refresh-run location.

## Storage ownership

| Content | Location | Retention |
| --- | --- | --- |
| Current catalog and category assignments | `data/catalog_manifest.json` | Versioned source |
| Current category identity/kind projection | `specs/catalog/taxonomy.yaml` | Versioned, paired with the catalog source hash |
| Enrichment field definitions and strict Stars policy | `specs/catalog/enrichment-field-contract.json` | Versioned contract |
| Evidence for the catalog's applied replacement | `data/catalog-evidence/2026-08-31/` | Versioned public evidence; preserve observation dates |
| Legacy low-Star policy rejection fixture | `tests/fixtures/catalog_enrichment_legacy_contract.json` | Versioned test data, never an active policy |
| Collection, import and projection code | `scripts/` | Versioned reusable code |
| Current checkpoint, fetched blocks and generated review reports | `.codex-tmp/catalog-refresh/active/` | Local ignored state; retain until the run is reconciled |
| Retired work packages and pre-migration dirty files | `.codex-tmp/catalog-refresh/work-retirement-2026-08-31/retired-work-and-migration-baseline.zip` | One local archive; not a runtime dependency |

The taxonomy projection supplies the same 126 IDs/kinds as the old proposal.
Current names and assignments remain owned by the catalog. Historical scope
proposals and migration scripts are preserved in the archive, not promoted to a
second current source of truth. The applied vocabulary is documented in the
[taxonomy decision](plan/2026-08-31-catalog-taxonomy-v2.md).

## Continue the existing CAT-05 run

Run from the repository root with Python 3.11+ and the standard library:

```powershell
python -B scripts/catalog_refresh_pipeline.py batch --run-dir .codex-tmp/catalog-refresh/active
```

Each invocation processes at most 25 original/replacement records, uses the
existing GET-only public GitHub collector, saves progress and stops at a quota,
request/byte or time budget. It makes no LLM calls, uses no credentials and does
not update the canonical catalog or install a recurring task. The checkpoint's
recorded retry deadline is preserved; consult current headers when continuing.

Generate reports or verify saved records with no network:

```powershell
python -B scripts/catalog_refresh_pipeline.py report --run-dir .codex-tmp/catalog-refresh/active
python -B scripts/enrich_catalog.py verify --run-dir .codex-tmp/catalog-refresh/active
```

The storage migration retained 13 processed records: seven complete cards, four
pending review/retry and two exclusions; 1,787 originals are unstarted. The
cumulative 80 GET attempts / 1,309,367 bytes include prior pilot/manual work.
These are the migration checkpoint's counts, not a claim of fresh data today.
The exact migration is recorded locally in `active/storage-migration.json`.

The local state is intentionally not committed. Deleting `work/` does not affect
it. Deleting `.codex-tmp/catalog-refresh/active/` would lose live checkpoint state;
do not treat all `.codex-tmp/` contents as disposable while a run is unfinished.
The retained archive can recover the earlier checkpoint, but not later progress.

## Start a new refresh cycle

Choose a new, nonexistent local run directory; never overwrite an existing run:

```powershell
python -B scripts/enrich_catalog.py plan --run-dir .codex-tmp/catalog-refresh/new-run --max-requests 30
python -B scripts/catalog_refresh_pipeline.py prepare --run-dir .codex-tmp/catalog-refresh/new-run --batch-size 25
python -B scripts/catalog_refresh_pipeline.py batch --run-dir .codex-tmp/catalog-refresh/new-run
```

The example is deliberately a small bounded run. Set a deliberate request budget
when preparing a larger cycle. The wrapper does not increase collector budgets.
Successful blocks are cached; changed source/script pins require an explicit
migration or a new run, not a counter reset or integrity-check bypass.

## Eligibility, evidence and reports

Verify public identity and actual Stars first. Confirmed Stars below 500 stop
content retrieval, exclude the record from the working candidate, retain history
and trigger a search for a distinct same-category replacement. Unknown Stars or
identity conflicts remain unresolved; old zero values are never bulk-deleted.

Eligible repositories receive metadata, languages, head commit, README, up to
four root dependency manifests and latest release in one per-repository pass.
Manifest/README excerpts are bounded. Optional expensive activity totals remain
explicitly unattempted. Dependency declarations are evidence hints, not an
automatically reviewed Stack. Content/category review is queued separately and
does not require an LLM turn between fetches. Replacements need complete reviewed
cards, Stars >= 500, category fit and a unique numeric identity.

Reports under `active/reports/` include:

- `summary.json` and `repository-progress.csv`: all original dispositions and any candidates;
- `field-completeness.csv`: 71 definitions, 31 mandatory flags, absence/errors versus filled values;
- `block-freshness.csv`: evidence URLs and actual observation times;
- `review-queue.json`: compact missing-field/failed-block entries, not raw README dumps;
- `exclusion-replacements.json`: exclusions, candidate attempts and unresolved vacancies;
- `active-candidate.json`: a mixed working projection, explicitly labeling untouched snapshots.

`curation/`, `records/`, frozen inputs, plans and the checkpoint are required for
resume. `extracted/` and `reports/` are reproducible local derivatives. CAT-06/07
retain semantic/global eligibility review; CAT-08 owns canonical reconciliation
and static HTML generation. Storage cleanup does not close those tasks.

## Optional discovery sources

The default saved research pool supplies 187 names absent from the frozen input,
not 187 qualified replacements. It contains no matching candidates for the two
Adyen SDK exclusions at this checkpoint. Empty pools remain explicit.

`scripts/import_catalog_discovery.py` imports already captured public OSSInsight
or ecosyste.ms JSON with source attribution and separate retrieval/sync dates.
It makes no requests. Its default taxonomy now comes from `specs/catalog/taxonomy.yaml`.
Pass resulting pools with repeated `--pool` arguments when preparing a new wrapper.

[OSSInsight's FAQ](https://ossinsight.io/docs/faq) documents why event-derived Stars
can differ from GitHub; use it for discovery, never the final 500-Star gate.
[API documentation](https://ossinsight.io/docs/api) describes collections/trends.
The observed database collection returned only repo ID/name, not a complete card.
The importer still needs result metadata and numeric identity preservation before
automated remote integration. No remote aggregator adapter is activated here.

## History and verification

The [condensed historical record](reports/catalog-refresh-history.md) replaces
active links to retired task folders. Old paths in append-only RUNLOG entries are
historical archive member names, not current commands or runtime dependencies.
The [storage verification](reports/catalog-refresh-storage-migration.json) records
archive integrity, preserved metadata/counters and checks that deny access to
`work/`. Historical full-folder verifiers need their archived exact inputs/scripts;
they are not supported current-workspace commands.

Do not run the legacy account-catalog builder merely to refresh this standalone
catalog. Current static generation is `python -B scripts/build_catalog_html.py`;
exact byte verification is the same command with `--check`.
