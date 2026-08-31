# Local catalog contract and taxonomy compatibility

CP-03 contract version: `1.0.0`. This is a source-owned projection of the
current catalog manifest. The 2026-08-31 owner-authorized taxonomy migration
updates the projection to taxonomy v2; it is not a GitHub metadata refresh.

## Taxonomy ownership

`data/catalog_manifest.json` remains authoritative. `taxonomy.yaml` uses the
JSON-compatible YAML 1.2 subset so a JSON parser can read it without PyYAML.
Every category preserves `key` as `id`, `title` as `label`, and `layer` exactly.
The file records the actual source-byte SHA-256 and snapshot date. Current
categories use explicit source-owned `parentId` and `kind` values: 111 thematic
leaves, 14 navigation containers and one review queue. The local projection
exposes these as `parent_id` and `kind`; aliases remain empty. Do not infer
additional hierarchy or aliases from labels or legacy generated categories.

Each card has one existing assignable primary category and zero or more distinct
secondary leaves. Navigation containers cannot be card assignments. The review
queue preserves unresolved input but does not pass classification eligibility.
Primary cannot also be secondary. Unknown keys fail validation;
they are not silently replaced with a superficially similar label. Category
changes belong in the source manifest first, followed by an explicit projection
update, reference migration and parity check. Retired IDs need a reviewed mapping;
aliases cannot collide with canonical IDs or other aliases. If hierarchy is
introduced later, all parents must exist and the parent graph must be acyclic.
Do not hand-edit generated catalog pages as part of that migration.

## v5 card mapping

| Source field | Local contract | Rule |
| --- | --- | --- |
| `id` | `repo_id` | Preserve existing v5 IDs, including `gh-pending:owner/name`. |
| `githubRepositoryId` | `github_repository_id` | Preserve a known upstream ID; otherwise `null`. Never hash a name into a supposed GitHub ID. |
| `fullName`, `url` | `full_name`, `url` | Preserve public identity; resolve redirects/aliases only with source evidence. |
| `catalogStatus` | `catalog_status` | Existing `candidate`, `accepted`, `reference` map exactly with snapshot provenance. Unknown labels require review. |
| `primaryCategory`, `secondaryCategories` | `primary_category`, `secondary_categories` | Resolve only against the current taxonomy. |
| `description`, `language` | same names | Missing or empty unknown values become `null`; do not invent summaries as upstream facts. |
| `license.spdx` | `license` | A known SPDX identifier/expression is preserved. Missing, `NOASSERTION`, or explicitly unknown becomes `null`. Legal suitability is not asserted. |
| `activity.createdAt` | `activity.createdAt` | Repository creation event, with a separate observation and evidence reference. |
| `activity.pushedAt` | `activity.pushedAt` | Repository push activity; not a verified last commit. |
| `activity.updatedAt` | no commit mapping | Metadata update is neither commit nor release evidence. |
| `activity.lastSyncedAt` | observation only when source lineage matches | Does not create any activity event. |
| verified commit/release evidence, when available | `lastCommitAt`, `lastReleaseAt` | Commit needs its SHA, branch, commit-date source field and observation. Release uses publication date, not creation or tagging date. |

No maximum age rejects a snapshot or observation. Old observations remain visible
and may motivate a targeted verification. A recent push, high star count or
unarchived status never proves operability, security, quality or project fit.

For every activity value, exactly one observation names the matching source field
and resolves to card evidence for that JSON pointer. Do not copy `pushedAt` into
`lastCommitAt`, fabricate verification times or claim a fetch from fixture data.
Distinct evidence items are needed when fields were observed at different times.

## Identity and independent statuses

The first CP-06 normalized snapshot preserves existing source IDs. Verified
aliases may join records to one canonical ID, with a deterministic migration map
and no loss of source lineage. Within a query variant, keep the best rank for a
canonical ID; count every fetched hit against the query budget before dedupe.
If two aliases cannot be resolved confidently, report the identity gap rather
than silently merging unrelated projects. Card aliases must be unique, exclude
self and not identify two different cards in one evidence pack.

The following are separate concepts:

- `catalog_status`: source catalog/curator disposition, `candidate`, `accepted`,
  or `reference`. `accepted` requires existing catalog evidence or a separate
  curator record for `/catalog_status`; a model or retrieval score cannot grant it.
- `evidence_stage`: local evidence completeness, `baseline`, `identity_validated`,
  or `advisory_evidence_complete`. This is not a recommendation or curator decision.
- eligibility: request-specific `primary_eligible`, `reference_only`, or `blocked`.
  Recompute it for every changed request or corrected Brief.
- recommendation role: `primary_candidate`, `supporting_tool`, `reference_only`,
  `compare_against`, or `avoid_for_now`. A role cannot upgrade catalog status.

Historical `normalized_candidate` may establish a baseline only when its source
fields are valid. `verified_catalog_entry` does not automatically imply either
`accepted` or complete advisory evidence. `discovered_live` and
`machine_evidence_complete` belong to the deferred CP-12 evidence workflow;
there is no automatic local promotion mapping. Preserve the source record and
review the needed fields if the meaning is ambiguous.

## Useful recommendations with incomplete data

A sparse baseline card is valid and retrievable. Unknown license, deployment,
compatibility or activity is represented explicitly. Each mandatory query field
gets one check, together with availability, archived status and advisory evidence.
The outcome is `unknown` when the value or supporting evidence is absent, `fail`
when sourced facts contradict the constraint, and `pass` when sourced facts match.
Every check reference resolves to evidence for the corresponding field. Empty or
omitted checks cannot establish primary eligibility.

For primary eligibility the card is explicitly available and unarchived, all
mandatory constraints pass, and use cases, best fit, adoption mode, project stages,
complexity, integration surface and compatibility have field-level evidence.
`compatibility` is a set of source-supported statements matched against the
request, not a semantic-version solver or proof that an integration was executed.
License/language identifiers are exact values; CP-06 owns normalization, not the
model. Deployment requirements match at least one supported deployment mode.

Any failed required check blocks adoption for that request, with a reason. Missing
mandatory facts keep a useful option as a reference with a concrete verification,
caveats and conditional integration prerequisites. Do not turn unknown facts into
an unconditional primary recommendation or refuse all useful guidance. Relevance
rank and evidence completeness do not supply a fit probability.

## Contract validation boundary

Draft 2020-12 handles shapes, enums, types, formats and field/count caps. Closed
objects exclude unrecognized raw-source/chat/private-context fields; arbitrary
strings still require minimization by the producer. A schema is not a secret
detector. `synthetic_fixture` examples are visibly labeled and cannot enter a
`catalog_snapshot` index as public evidence.

`tests/test_plugin_contracts.py` also checks source parity, references, activity
meaning, request-specific eligibility and cross-contract identity/version
invariants. These are executable contract examples for the future implementations,
not the runtime security or retrieval implementation. CP-06 must verify actual
source-to-card normalization; CP-09 must enforce the same rules on retrieved data;
CP-04/15 must evaluate real candidate relevance and integration usefulness.
