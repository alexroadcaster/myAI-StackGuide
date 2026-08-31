# Catalog refresh history: 2026-08-31

This is a compact retained record, not a replacement for current-run verification.
The old dated task directories are retired. Their original bytes, including
one-off scripts, detailed ledgers, source snapshots and reports, are preserved in
one ignored local archive described in [the operating guide](../CATALOG_REFRESH.md).
No current script or test requires that archive or the original directories.

## CAT-01-02 initial audit

The selected standalone input contained 1,800 repository rows, 77 old categories
and 2,155 placements. Its original HTML SHA-256 is
`6afd4fa93502f126aa4fdf2d80f3cf10b0b93cff9c44f67a6ec1b51a41064c91`.
The audit recorded 807 stored zero-Star rows and 137 stored 1-499 rows, not current
GitHub values. It prepared 71 field definitions, 31 mandatory fields and an
initial 88-node taxonomy proposal. The 32 preparation checks were historical
local evidence only. Two missing companion files were not recreated.

Archive members: `work/catalog-refresh/2026-08-31-cat-01-02/`.
Only the legacy field contract survives as a dedicated negative-test fixture.

## CAT-02 taxonomy v2

The accepted structure replaced the initial proposal: 77 old nodes minus two
retired IDs plus 51 new IDs = 126 nodes (111 thematic categories, 14 navigation
containers and one review queue), with 76 roots and 50 children.
The [decision table](../plan/2026-08-31-catalog-taxonomy-v2.md) remains versioned;
the current machine-readable identity/kind projection is
`specs/catalog/taxonomy.yaml`, derived from the canonical catalog.

Archive members: `work/catalog-refresh/2026-08-31-cat-02-taxonomy-v2/`, including
the full scope proposal, 77 before/after dispositions, detailed registry and
pending review ledgers. Archive member paths are identifiers, not live links.

## Taxonomy application and CAT-03

Application retained 1,800 originals: 950 explicit snapshot decisions, 828
inherited assignments, 22 unresolved; 878 primary category changes and 1,945
placements. Metadata was not refreshed by this migration. Initial static HTML
and collector preparation were locally checked; the actual browser policy block
remained unverified. The initial one-repository preflight made no API requests.

Archive members: `work/catalog-refresh/2026-08-31-taxonomy-apply/` and
`work/catalog-refresh/2026-08-31-cat-03-preflight/`.

## CAT-04 pilot

The owner replaced the old low-Star exception rule with strict Stars >= 500.
Pilot evidence covered dpny518/llm-worker (one Star), 0xPlaygrounds/rig (8,464)
and Portkey-AI/gateway (12,864), using 22 GETs / 508,771 bytes. The low-Star
repository was replaced by Portkey as a candidate, not automatically accepted.
Current catalog references point to the retained public evidence in
`data/catalog-evidence/2026-08-31/`, including the exclusion and replacement decision.

At the pilot checkpoint the source SHA-256 was
`3b1d9a097133a8b578799cb7b75f5fc1aa7a93a36f15f545fa063fe5cbcd95eb`;
HTML SHA-256 was `799496ba5a7b4210338a737fc4e8f13e17fa0d586a063c79efe61cab02efe41a`.
These hashes are historical; relocating evidence references changes current bytes.

Archive members: `work/catalog-refresh/2026-08-31-cat-04/`.

## CAT-05 partial execution

After seven complete cards existed, the owner rejected per-card LLM operations.
The scripted batch processed five more originals with 17 GETs, excluded two Adyen
SDKs at 138 and 68 Stars after metadata only, and stopped at the API quota. No
matching replacement was available in the saved discovery pool.

Storage migration preserves all 13 processed records, their source blocks,
curation, status, timestamps and cumulative 80 requests / 1,309,367 bytes.
Seven complete, four pending, two excluded and 1,787 unstarted records account
for all 1,800 originals. The working candidate contains 1,798 rows; the canonical
catalog still contains 1,800 because final reconciliation remains open.
Continue through `.codex-tmp/catalog-refresh/active/`, using the operating guide.

Archive members: `work/catalog-refresh/2026-08-31-cat-05/`.

## Archive retention

The verified local ZIP contains all 196 original work files plus 14 pre-migration
owned files under `before/`, including existing dirty changes and the legacy
builder before its ignore-file preservation fix. Its manifest records every
member's SHA-256.
The original `work/` contents have not been deleted or changed by retirement.
They can be removed after the storage migration checks pass; deleting them does
not remove the archive or the relocated active run. Do not delete the active
run merely because it is Git-ignored. A new checkout does not contain local run
history and should use the documented new-run procedure.
