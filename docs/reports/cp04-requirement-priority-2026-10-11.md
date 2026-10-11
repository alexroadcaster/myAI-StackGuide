# CP-04 priority of newly supported requirements — 2026-10-11

## Outcome

The isolated `new_required_first` mode places all three newly discovered Kotlin
alternatives at ranks1–3, increasing exposed Kotlin known-positive top12 coverage
from1/5 to4/5. All four top12 positives survive detailed evidence packing. It retains
the strongest original literal baseline's exact full order in all ten development
cases. Macro AND per-case non-regression gates pass. This is development selection,
not runtime activation, independent quality acceptance or parent CP-04 completion.

The alternative `all_required_first` improves macro metrics and yields5/5 Kotlin
top12 positives, but fails per-case recall/nDCG preservation. It is not selected.
No grades, intent groups, queries, thresholds or existing source facts were changed.

## Implemented behavior

[Generic ranker](../../scripts/rank_requirement_priority.py) wraps the preserved
previous separated ranker. It consumes public field projections, added capability
strings, original query terms and manually supplied intent. No case IDs, oracle
grades or expected repository IDs enter the ranking algorithm.

- `new_required_first`: a priority band for candidates where a new source-qualified
  capability fills an originally unmatched required group and every group now has
  lexical support. Other candidates retain their previous score/order.
- `all_required_first`: prioritize every candidate with lexical support for all
  required groups, regardless of whether the evidence is new.
- Both retain the previous score and numeric-ID tie-break within a band. Context
  alone or partially supported requirements cannot create the new-evidence priority.
  Unknowns remain candidates in the lower band, not hard constraint mismatches.
- Sort the complete scored routed evaluator universe before applying the cap from
  the existing frozen plan. Otherwise a new zero-baseline candidate could be removed
  before its required-feature evidence influences ranking.

The [contract](../../evals/plugin-v1/requirement-priority-contract.md) prospectively
defines both modes, unchanged gates and development selection. Select among modes
that preserve every gate and improve Kotlin top12; highest coverage wins, with a
conservative-mode tie-break. Both modes were frozen before capture.

This is a literal evaluator ordering change. Verified private fixture pack entry
retains the existing matching, provenance, candidate coverage and byte boundaries.
The original candidate package is hash-verified again, including logical SQLite
parity. Full routed literal ranking is not an activated bounded FTS shortlist.
Canonical assets, policies, trust anchors, previous code and experiment files remain.

## Fresh comparison

Five arms executed on 2026-10-11 against the same ten exposed development cases,
full routed source-based judgments, original ranks and existing intent groups.

| Method | Recall@12 | nDCG@12 | Every-case non-regression |
| --- | ---: | ---: | --- |
| Original FTS5 | 0.721493 | 0.812905 | Reference diagnostic |
| Original literal baseline | 0.804899 | 0.874555 | Reference |
| Previous separated ranking | 0.804899 | 0.874555 | Pass |
| **New missing-requirement priority** | **0.804899** | **0.874555** | **Pass** |
| All supported requirements first | 0.812042 | 0.884138 | **Fail** |

The selected mode preserves10/10 complete original literal orders. There are no
new priority qualifiers in these ten development cases; the result proves bounded
preservation, not broad improvements on arbitrary queries. Kotlin supplies the
observed novel-evidence priority path; unit tests cover its distinct failure modes.
React Native remains Recall1.0/nDCG0.810884, without the earlier enrichment regression.

The rejected broader mode changes five orders and regresses three scenarios:

| Scenario | Metric | Original | Broad priority |
| --- | --- | ---: | ---: |
| Browser uploader D08 | Recall@12 | 0.500000 | 0.428571 |
| EXIF/media tags D09 | nDCG@12 | 0.851883 | 0.824995 |
| Portfolio optimization D10 | nDCG@12 | 0.986356 | 0.984232 |

The broad mode's better mean cannot override these failed per-case gates.

## Exposed Kotlin regression

Known-positive coverage only, not newly independent held-out recall/nDCG.

| Method | Positive pool | Positive top12 | Positives packed |
| --- | ---: | ---: | ---: |
| Original literal | 2/5 | 1/5 | 1/5 |
| Previous separation | 5/5 | 1/5 | 1/5 |
| **Selected new-requirement priority** | **5/5** | **4/5** | **4/5** |
| Rejected broad priority | 5/5 | 5/5 | 5/5 |

| Repository | Previous separated rank | Selected priority rank |
| --- | ---: | ---: |
| spring-projects/spring-framework | 17 | **1** |
| spring-projects/spring-boot | 18 | **2** |
| quarkusio/quarkus | 21 | **3** |
| ktorio/ktor | 2 | 5 |
| micronaut-projects/micronaut-core | 13 | 16 |

Micronaut stays outside top12. The selected conservative rule promotes newly filled
requirements, not all older supported candidates. Source freshness/newness is not
general repository quality; this is an explicitly bounded discovery trade-off.
The three promoted repositories remain catalog candidates with their original
eligibility/metadata; ranking does not grant adoption acceptance.

## Evidence and current checks

- [Declaration](../../evals/plugin-v1/results/cp04-requirement-priority-2026-10-11/declaration.json),
  SHA256 `22463f9edfe971e1f28bff36c4ecbd0a5d902d97f92ead54c39f9f4e23000f92`.
- [Compact summary](../../evals/plugin-v1/results/cp04-requirement-priority-2026-10-11/summary.json)
  includes per-case metrics, both modes' gates, named ranks and packed positive IDs.
- [Observations](../../evals/plugin-v1/results/cp04-requirement-priority-2026-10-11/observations.json)
  preserve all five arms, explicit ranking traces and Kotlin evidence packs.
- `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_requirement_priority.py`:
  6/6 pass after observed RED for priority-before-cap and supported-requirement ordering.
  Tests also cover context-only additions, partial support, preserved old ordering,
  deterministic ID tie-break and invalid mode/limit.
- `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_capability_context.py`:
  all six previous separation checks pass unchanged.
- `.venv/Scripts/python.exe -B evals/plugin-v1/run_requirement_priority.py --predeclare`
  followed by `--run`: paired capture completes; selected mode passes all seven gates,
  while broad mode retains both per-case failures.
- `.venv/Scripts/python.exe -B scripts/build_plugin_search_index.py --check`:
  original package byte/logical parity passes, including2,500 cards/rows,
  126 routes/162 members and immutable read-only write rejection.

## Evidence limits and next work

The requested bounded top12 improvement and preservation comparison are complete.
Parent CP-04 remains `in_progress / partially_verified / no_go`,
`promotion_ready=false`. This mode is selected for further development evaluation
only. Required-group support is lexical: incidental mentions, negation, semantic
fit and project-version compatibility remain unresolved. Manually partitioned
exposed cases are not proof of automatic intent extraction or unseen quality.

Next evaluate source-verified new cases with required-feature/negative-context
distinctions and check newly promoted candidates against conflicting constraints.
Independent judgments, RU/EN/resource evidence, useful architecture/product/effort/
time/reuse explanations, human acceptance and joined CP-11/15 gates remain open.
No agent execution, model/dependency install, Git operation or external publication.
Rollback is to retain the unchanged previous ranking and canonical search package.
