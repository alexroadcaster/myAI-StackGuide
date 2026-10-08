# CP-04 Independent Pre-Capture Oracle Assessment

- Assessed on: 2026-10-08.
- Reviewer: `product_planner` agent (`cp04_oracle`).
- Evidence kind: source inspection before capture; no new retrieval result or `run_quality` output was inspected for this first pass.
- Scope: frozen public catalog evaluation and recommendation acceptance protocol. No private context, network, provider call, runtime activation or human acceptance.
- Source snapshot: the exact 2,500-card tuple pinned by `quality-plan.json:8-29`. Repository freshness was not refreshed and is not a claim of this assessment.
- Original quality plan, rubric, judgments, terms, weights and thresholds are unchanged.

## Findings

### S1: Incomplete judgment coverage prevents a retrieval-quality verdict

The 24 frozen cases have 47 distinct judged identities, one or two per case. Every grade is 2 or 3; there are no independent weak or irrelevant examples. The 24 declared primary leaves contain 608 cards in total; 622 cards have any assignment to those target leaves. These counts were derived by parsing the checked-in plan and public snapshot, without executing retrieval.

`evaluate_retrieval.py:289-303` validates pool identity, category/cohort provenance and allowed constraints. Those checks do not establish goal-specific relevance or exhaustive judgment coverage. `evaluate_retrieval.py:761-768` correctly rejects unjudged ranked IDs. A plan-validation pass is therefore insufficient for scoring full routed-corpus retrieval.

Preserve that failure boundary. Do not search only the judgment pool, infer grade zero for unjudged results, or derive expected relevance from runtime labels. A diagnostic capture can report unjudged coverage, null official ranking and `no_go` without proving an implementation defect or a valid product quality score.

### S1: Category membership alone overstates goal-specific alternatives

Source comparisons below refer to `plugins/myai-stackguide/assets/catalog.snapshot.json:1` (a minified file), selecting `/cards` by numeric identity and inspecting `/descriptions`. Each card carries a canonical evidence source reference ending `/repositories/{github_repository_id}` under the frozen catalog snapshot ID.

| Frozen case and plan lines | Public-card evidence | Supported assessment |
| --- | --- | --- |
| DEV-03, `quality-plan.json:190-197` | PhotoPrism 119160553 is a photos application; Jellyfin 161012019 is a media server backend/API. | The snapshot supports PhotoPrism's photo intent. It does not establish Jellyfin as a useful self-hosted photo-library alternative merely because both share a leaf. |
| DEV-02, `quality-plan.json:177-185` | MockServer 8426406 retains the exact alias; WireMock 2544305 is another API testing identity. | Useful API testing comparison and exact historical identity lookup need distinct judgments. |
| DEV-11, `quality-plan.json:285-293` | GreptimeDB 480217156 retains the queried alias and unknown visibility/activity; MongoDB 108110 is another database identity. | Missing facts remain unknown; another database is not the exact queried identity. |
| HOLD-01, `quality-plan.json:309-317` | Dokku 10567197 is Docker-powered PaaS; PM2 10187082 is a Node.js process manager/load balancer. | Same deployment leaf does not establish equivalent PaaS fit. |
| HOLD-08, `quality-plan.json:392-400` | NLTK 299862 says `NLTK Source`; Gensim 1349775 says `Topic Modelling for Humans`. | NLP category membership alone does not establish dataset/labeling fit or justify a direct-fit grade. |
| HOLD-09, `quality-plan.json:404-412` | Formidable 655209 describes a streaming multipart parser and serverless/cloud/filesystem upload destinations. | The frozen facts do not establish a browser upload component alternative to Plupload 467461. A supporting backend role requires explicit scope. |
| HOLD-11, `quality-plan.json:428-436` | GPT Engineer 634224458 has the exact historical alias and is archived; OpenCommit 610217037 says `AI-assisted commit workflow`. | Archived identity lookup can succeed while adoption is denied. OpenCommit is not that identity; the plan must distinguish identity retrieval from a separately requested functional comparison. |

These are limitations of the frozen oracle evidence, not live upstream capability or security judgments. Do not repair catalog taxonomy or metadata to obtain an evaluation pass.

### S1: Held-out strata are incomplete

The task requires held-out stratification across the 14 containers (`docs/plan/2026-08-30-codex-plugin-v1-implementation-plan.md:353`). The plan declares all 14 at `quality-plan.json:91-105`, but development cases cover 12 containers and held-out cases cover only `deployment_containers_paas` and `supply_chain_devsecops`. Development has no dense-leaf/expansion cases; held-out has no `activity_unknown` case. Each split has one Russian lexical case. Judged identities do not overlap between splits, which supports identity separation but does not repair missing strata.

`evaluate_retrieval.py:274-331` unions container/tag/locale coverage across both splits. Consequently, its pass cannot establish complete held-out coverage. Every missing held-out stratum must remain unavailable/unsupported in reporting. Deterministic navigation coverage of 14 containers/111 leaves and semantic held-out quality are separate gates.

### S2: Frozen anchors are not human calibration

`rubric.json:55-88` declares four paired calibration cases and independent reviewer/adjudication evidence. `rubric.json:104-105` correctly retains `calibrated=false` and `observed_results=false`. Named AI roles are agents, not human reviewers. `EVALS.md:99` requires human examples before a product quality verdict. An observed agent-authored advisory assessment can support `agent_assessed_not_human_accepted`; it cannot set actual human acceptance or close CP-15.

## Minimum Independent Protocol Corrections Before a Quality Rerun

1. Retain the original frozen artifacts and diagnostic run. Register a separate versioned adjudication/protocol revision rather than rewriting prior judgments to fit output.
2. Give each goal an explicit relevance interpretation before inspecting ranking: exact identity, functional alternative, or supporting integration component. Separate relevance from adoption constraints. An archived exact match may be a successful identity lookup and a denied adoption candidate at once.
3. Independently judge the complete finite routed universe, including secondary assignments, from source facts and synthetic goal/constraints. Record evidence pointers and grade rationale, including grades 0/1 where justified. If a bounded reviewed pool is used instead, predeclare its coverage method and limit the verdict to that pool; do not present it as full-corpus recall. Preserve `unjudged_candidate=invalid_input_not_implicitly_zero`.
4. Add missing held-out strata through a separately frozen revision, or record an explicit owner-accepted coverage gap. A combined corpus union cannot silently waive the held-out requirement. Do not adjust terms, aliases, weights or thresholds on held-out results.
5. Predeclare whether ranking measures raw identity retrieval or policy-eligible recommendations. The current all-grade-positive denominator includes denied archived identities; it must not silently become an eligible-only denominator during scoring.
6. Keep protocol readiness, observed retrieval, agent advisory review, joined runtime/browser evidence and human acceptance as distinct status fields.

## Smallest Meaningful Advisory And RU/EN Assessment

Use exactly the four rubric calibration cases: DEV-08 (founder), HOLD-10 (engineer), DEV-11 (activity unknown) and HOLD-12 (secondary dedupe). Produce eight language projections. Use each actual bounded public evidence pack and frozen synthetic case context only.

Before semantic composition, freeze canonical capture hash, source/card/index/policy pins, candidate IDs/order and evidence references. Compose one canonical advisory decision with RU and EN projections. Preserve facts, roles, constraints, negation, uncertainty, missing translation disclosure and proposed-versus-executed authority. Unknown mandatory adoption facts require conditional or reference roles and an explicit verification prerequisite; catalog eligibility is not curator acceptance.

Each language is scored independently on the existing ten 0/1/2 dimensions. Retain the 16/20 target, critical dimensions at least 1 and zero critical failures. Record original scores, evidence references, reviewer identities and adjudication; differences greater than one or critical disagreements require resolution, not averaging. Both languages must meet the declared conditions; bilingual averaging cannot conceal a failure.

The founder case must allow an explanation of the decision and strongest counterargument, and a copyable first task with prerequisites, acceptance and rollback. The engineer case must identify the component boundary and first validation. The unknown case must preserve missing-fact verification; the dedupe case must preserve one numeric identity and distinguish primary/supporting roles. A proposed first step does not execute installation, integration, provider or external actions; execution belongs to a separate scoped implementation request.

Agent assessment is distinct from human scoring. Human acceptance remains false until the actual owner/human review occurs. Paired text alone cannot prove browser switching, absence of calls, model quality, runtime activation, actual implementation outcomes or time saved.

### Predeclared Negative Outcomes And Review Method

The second-stage author reads only the four named actual candidate evidence packs, their frozen synthetic goals and contexts, and source identity/pin bindings. Freeze the exact observations-file byte SHA-256 and canonical per-case query/result/pack SHA-256 before composing any advice. Bind each advisory record to those hashes and preserve pack candidate IDs/order; there is no extra retrieval, private source inspection or imported live metadata.

Parse the observations file locally without exposing its full contents to the model. Extract exactly the four selected packs, then minimize to the identity, description, classification, relevant repository/activity/delivery facts, gaps, roles/constraints and provenance needed for composition. Measure compact sorted-key JSON with UTF-8, `ensure_ascii=False` and `allow_nan=False`. Each original source pack must stay within its 160 KiB envelope; the combined selected controlled composition input must stay within 200 KiB. If necessary, minimize further or handle bounded cases separately. Report bytes and method; token count remains null without a tokenizer measurement. This input measurement does not include host instructions/history/output and does not claim their total context size.

Treat source-supported fit as a prerequisite, not a desired score. If no captured card supports the requested role, return no adoption recommendation and a specific conditional verification/next check. Do not invent an alternative, fill missing facts, imply curator acceptance, or force a 16/20 pass. Sparse or irrelevant evidence may yield a safe advisory outcome and a failing usefulness score simultaneously. Preserve any negative reviewer verdict.

Record author identity, language-specific original dimension scores and concrete text/source references. Self-review is explicitly an agent author assessment and is not the independent first pass required by the rubric. The separate Evidence Reviewer receives the advisory packet without author scores, records an independent first pass, and compares only after that review is frozen. An AI review cannot authenticate a human reviewer or establish human acceptance. Keep actual human acceptance false.

For each language, inspect all ten dimensions and the full critical-failure list. Mark unavailable runtime/browser facts as gaps rather than automatic pass. Check literal identity/source/evidence and semantic parity explicitly: negation, uncertainty, proposed authority, roles, constraints, prerequisites, validation and rollback. Any critical disagreement or score difference greater than one remains an adjudication gate. Honest failures are reportable evidence, not a reason to change the frozen rubric, labels or thresholds.

## Noncircular Gate Sequence

The detailed task graph has a practical cycle if whole CP-04 completion is required before CP-11: CP-04 blocks CP-11 (`task:345`), CP-11 depends on CP-04 (`task:717`), while CP-04's quality verdict requires actual CP-11 captures (`task:355`, `quality-plan.json:128`).

The smallest coherent sequence is:

1. CP-04 accepts pre-capture protocol/judgment readiness, with explicit unresolved gaps.
2. CP-11 captures the actual joined lifecycle and retrieval route using that protocol; its V-LOCAL/V-RETRIEVAL gates remain distinct from V-EVAL (`task:728`).
3. CP-04 reviews observed retrieval and paired advisory evidence without tuning held-out labels.
4. CP-15 independently accepts human usefulness/privacy/UI; CP-16 owns package/install/release evidence.

An accepted diagnostic capture protocol can unblock CP-11 evidence collection without declaring CP-04 product quality complete. CP-12-14 remain deferred and are not local prerequisites.

## Sources And Verification

Read: `AGENTS.md`, `.codex/TEAM.md`, task packet template, `.codex/agents/product-planner.toml`, `design-recommendation-evals/SKILL.md`, CP-04/CP-11 detailed tasks, team contracts, `EVALS.md`, agent eval workflow, runner contract, frozen plan/schema/rubric/cases/scorer, public snapshot, targeted R06/R12/R14/R15 PRD/roadmap/REQUIREMENTS/PLAN and CP-04 RUNLOG references.

Checks: bounded local JSON parsing for card/judgment counts, split strata, identity overlap and selected frozen descriptions; exit 0. A base Python executable-location warning appeared, but the parsing commands completed and returned their expected source-derived output. No test, new result, fresh retrieval, browser, provider or human run is claimed. No expected RED applies to this read-only assessment.

Next owners: Quality Evaluator records diagnostic captures and fail-closed coverage; primary updates task gate boundaries; Product Planner and independent Evidence Reviewer assess paired advisory evidence; human owner supplies acceptance.
