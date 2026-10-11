# CP-04 required capabilities and project context — 2026-10-11

## Outcome

Implemented an isolated generic ranking module and prospectively declared paired
comparison without agents. The separated method preserves the strongest original
literal baseline on all ten exposed development cases, including exact full result
orders. It removes the earlier React Native regression. Kotlin known-positive
candidate coverage increases from 2/5 to 5/5, but top12 coverage remains 1/5.
This is development non-regression evidence, not parent CP-04 closure or activation.

## Behavior and scope

[Ranker](../../scripts/rank_capability_context.py) consumes only original public field
projections, newly added source-qualified capability strings and an explicit intent.
It does not consume case IDs, relevance grades, expected repository IDs or a model.
[Intent input](../../evals/plugin-v1/capability-context-intents.json) partitions existing
terms exactly into required groups and context/preferred details. OR within a group,
AND across groups; no additional query terms are introduced. Explicit required
technologies remain requirements (React for the React component-library scenario).
Async is a preference in the exposed Kotlin goal, so it belongs to context there.

Ranking starts with the exact original literal field/term count and numeric-ID
tie-break. New capability evidence adds one point per previously unmatched required
group only when every group has lexical support. Synonyms cannot multiply the bonus.
Additional context matches add zero. Old context contributions remain in the baseline
score to preserve its established behavior. Unknown required groups are retained and
cannot trigger a hard exclusion. Existing pack/matcher constraints still apply.

Requirement states and bonus/context terms are captured per result. A lexical hit is
not semantic proof that a feature exists: negation, incidental words, compatibility
and version fit still require source/semantic verification. Required groups govern
enrichment scoring, not a newly proven hard eligibility contract.

The [contract](../../evals/plugin-v1/capability-context-contract.md) and
[runner](../../evals/plugin-v1/run_capability_context.py) retain original judgments,
thresholds and the previously verified candidate package. The evaluator verifies its
receipt/files/logical SQLite projection before private fixture pack entry. No change
to canonical query schemas, policies, assets, prompts or runtime trust anchors.
Full routed literal ranking is an evaluator method, not an activated bounded FTS path.

## Current observed comparison

All four arms were executed on 2026-10-11. Ten exposed development cases; constrained
full routed-universe metrics and original ranks. Higher is better.

| Method | Recall@12 | nDCG@12 |
| --- | ---: | ---: |
| Original FTS5 | 0.721493 | 0.812905 |
| Original literal baseline | 0.804899 | 0.874555 |
| Enriched literal, undifferentiated terms | 0.779899 | 0.860174 |
| Separated requirements/context | **0.804899** | **0.874555** |

The separated method recovers 0.025000 macro recall and 0.014381 macro nDCG relative
to undifferentiated enrichment. It matches the original baseline rather than proving
an improvement over it. All ten full result orders match the original baseline;
new requirement evidence does not change their ranking. Unit cases separately show
that novel required evidence can change order without granting context-only bonuses.

| React Native/mobile testing | Recall@12 | nDCG@12 |
| --- | ---: | ---: |
| Original literal baseline | 1.000000 | 0.810884 |
| Undifferentiated enrichment | 0.750000 | 0.689190 |
| Separated requirements/context | **1.000000** | **0.810884** |

| Exposed Kotlin coverage, original literal comparison | Original | Separated |
| --- | ---: | ---: |
| Supported positives in candidate pool | 2/5 | **5/5** |
| Supported positives in top12 | 1/5 | 1/5 |

Three newly discovered Kotlin candidates have baseline score0 and requirement bonus1:
Spring Framework at17, Spring Boot at18 and Quarkus at21. This increases coverage
without solving top12 precision. The prior enriched FTS experiment's top12 result
was3/5 under a different algorithm; do not conflate that result with this comparison.
No fresh Kotlin recall/nDCG or independent held-out success is asserted.

All eight declared development gates pass: macro and every-case recall/nDCG
non-regression, valid ranks/status, constraints/identity, pack survival and historical
baseline equivalence. No duplicate IDs, hard-constraint violations or false exclusions
were observed. These gates do not include semantic response or release acceptance.

## Evidence and checks

- [Current declaration](../../evals/plugin-v1/results/cp04-capability-context-v2-2026-10-11/declaration.json),
  SHA256 `49d02481a964fbaa395a911d648af4b3a40cbd3e3ba6983e57e3018609866958`.
- [Compact summary](../../evals/plugin-v1/results/cp04-capability-context-v2-2026-10-11/summary.json).
- [Observations](../../evals/plugin-v1/results/cp04-capability-context-v2-2026-10-11/observations.json),
  3,584,622 bytes including original/candidate evidence packs and ranking traces.
- The first exposed-development capture is retained in
  [its original directory](../../evals/plugin-v1/results/cp04-capability-context-2026-10-11/summary.json),
  alongside exact original runner/input bytes. Before the second declaration, the
  runner was corrected to derive its cap from the frozen plan, and React was retained
  as mandatory for React UI components. Both captures have identical measured metrics;
  the current declaration owns the final implementation. No post-capture source edits.
- `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_capability_context.py`:
  6/6 pass. Initial five checks ran after implementation. A separate observed RED
  caught synonym double-counting (bonus2 versus expected1); the correction and rerun
  pass. Tests cover context-only interference, real requirement promotion, exact
  baseline arithmetic/ties, unknown retention, term partition rejection and synonyms.
- `.venv/Scripts/python.exe -B scripts/build_plugin_search_index.py --check`:
  original package parity passes (2,500 cards/rows, 126 routes, 162 route members).
- `.venv/Scripts/python.exe -B evals/plugin-v1/run_capability_context.py --predeclare`
  followed by `--run`: final paired capture succeeds and all development gates pass.

## Remaining boundary

Parent CP-04 remains `in_progress / partially_verified / no_go` and
`promotion_ready=false`. The resolved gap is enrichment-related development
non-regression. Remaining work includes top12 placement of newly discovered useful
candidates, independently assessed new cases, semantic required-feature verification,
RU/EN and resource evidence, user-facing architecture/product/complexity/time/reuse
explanations, human usefulness and joined CP-11/15 acceptance. Inputs in this run are
manually partitioned exposed cases; no model-generated intent extraction was tested.

Rollback is to retain the original search; the new generic ranker and experiment
are isolated. No dependency install, external write, Git operation or agent execution.
