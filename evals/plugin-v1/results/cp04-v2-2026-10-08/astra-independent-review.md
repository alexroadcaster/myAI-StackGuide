# CP-04 independent GPT-6 Astra / Medium review

Requested task-level configuration: gpt-6-astra, medium. Fresh-context agent, read-only review with review-advisory-evidence skill. Tokens/cost/backend usage are not observable. Primary records reviewer-authored frozen findings; this is model evidence, not human calibration.

## Blind usefulness assessment

Prior author/reviewer scores and aggregate report were excluded until the matrix was sent and persisted in astra-independent-usefulness-review.json (SHA256142faf13f5ca26e0fc6e0b25ef653a19abf541e7884debea80e814c44b377fbf).

| Case | RU /20 | EN /20 |
| --- | ---: | ---: |
| H03 founder photo/video | 18 | 18 |
| D05 Go HTTP engineer | 18 | 19 |
| H15 low-context personal finance | 18 | 18 |
| H11 metrics/database engineer | 18 | 19 |

All critical dimensions2; no critical failure observed. No factual/negation/authority reversal between languages observed. Limitations: H15 RU grammatical errors; unexplained terms for H03/H15 audiences in both languages; all four reading paths refer generically to selected-version documentation, reducing the ability to execute the next task. Missing context is correctly disclosed; improvement should name precise documentation questions and pilot outputs after those answers, not invent live URLs or unsupported schemas.

Bindings: recommendation filec71f2799c86ebd725545825715f8dc32441f33a31f03f132dc52311f59a99377; human packetbca490fcdb933c9211dde6ff8625914241ea1d20fe4447228d25e8ec7ee2ff29. All12 observation/full-capture/pack hashes matched. All10 selected source activity subfields, description subfields and evidence arrays matched actual packs (30 subset comparisons). A first whole-object comparison differed because the projection intentionally omits fields; bounded subset comparison resolves that, not source drift. No test suites, network, captures or edits were executed by reviewer.

## Evidence and acceptance findings

1. Retain in_progress / partially_verified, no_go, promotion_ready=false. Report does not claim complete acceptance.
2. Synthetic evaluator SQL warm p95 291.4446ms exceeds200ms; production_reader_accepted=false and full_card_pack_capacity_measured=false. Human ratings cannot resolve capacity or reader compatibility.
3. H03 Recall0.50 remains valid under frozen protocol but is confounded by weak unknown function scored grade1. oracle-v2-protocol.md:75,92 explicitly permits this; H03 Airsonic descriptions are null and rationale states unknown function. This is an oracle-policy limitation, not an accidental scorer bug. A prospective policy/human relevance decision with fresh held-out cases is required; preserve current labels/failure.
4. Join diagnostic passes schema/helper/read-only state validation, but writer_called_by_diagnostic=false and invalid_root. The original state_invalid stack is unavailable; later WinError5 is separate read-only evidence. No saved/published/resumed, browser or host lifecycle proof.
5. semantic-summary retains historical not_observed/not_run fields while pointing to later separate evidence; use final report/audit and bound files, not that summary alone as consolidated lifecycle truth.

## Comparison after blind freeze

Previous independent scores H03 19/20, D05 18/19, H15 18/19, H11 19/20 were read only after freeze. Astra is stricter on integration/reading-path usefulness. H15 equal RU totals hide dimension disagreement: Astra integration1/authority2 vs prior integration2/authority1. Astra views advice-only approval wording as cumbersome but does not treat it as critical authority failure. Preserve differences; do not average them into calibration.

## Smallest human input

Start with H03 RU (EN only if the human is comfortable): what next step would you take after this advice; which phrase prevents that choice; for a personal photo/video goal should a repository with unknown descriptive function count as relevant or remain insufficient evidence? Keep actual human words and reviewer identity. Evaluator can map provisional rubric judgments and ask for confirmation/correction, retaining unanswered dimensions unrated. Continue remaining cases in small batches. EVALS requires human examples/calibration, not80 numerical scores in the first response; current full packet still requests each case, so one response is initial calibration only.

Human feedback cannot waive search/headroom failures or missing CP11/browser proof. Technical owners proceed on those independently. No request to accept known gaps merely to close CP04.
