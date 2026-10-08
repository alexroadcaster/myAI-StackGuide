# CP-04 prospective source oracle v2

Owner: Quality Evaluator; acceptance: Product Planner. Independent source review precedes
all v2 retrieval and baseline execution. The primary records the exact final plan,
judgments and protocol file hashes in its declaration before capture. Until that
declaration is frozen, no ranking may be consumed. Historical v1 plans/results stay
untouched and do not supply relevance labels.

## Source and finite universe

`quality-plan-v2.json` is `cp04_quality_plan_v2`; its separate judgment file is
`quality-judgments-v2.json`, `cp04_source_judgments_v2`. `build_oracle_v2.py` reads
the pinned 2,500-card CP-06 snapshot, manifest, policy 2.1.0, index format 3,
taxonomy and original threshold declaration. It never imports or executes the
retrieval engine, reads historical rankings, runs baseline scoring, or uses a
model/provider. Exact input hashes are retained in `source_hashes`; the judgment
file binds the canonical plan hash and card hash.

For a leaf case, the finite universe is every distinct numeric GitHub identity
with a primary or secondary classification in that leaf. For a container case,
it is the distinct union of all descendant-leaf placements. It includes identities
that do not lexically match, archived identities and identities with sparse metadata.
There is no query/output-dependent pool selection. Every possible returned ID
must have exactly one explicit judgment with grade, source-derived constraint,
rationale, source reference, JSON pointers and exact observed values. Unjudged
results invalidate a run; they are never assigned implicit zero.

Thirty cases contain 26 functional cases (10 development, 16 held-out) and four
separate identity probes. All 14 navigation containers appear in the **functional
held-out** cases. Development intentionally covers six domains; it is a tuning
subset, not a second requirement to cover every domain. Thin and dense routes,
baseline and expansion cohorts, dual descriptions, secondary placements, RU/EN
and unknown release/commit metadata are explicit. H07 is an actual container query
over `communications_personal_ops`, including all 32 distinct identities. A leaf
case does not receive `container_union` merely because it has a parent container.
Historical alias success belongs to the identity probes and is not a semantic
quality score. Exhaustive 111-leaf/14-container structural route checks remain a
separate runner diagnostic.

The quoted-literal OR compiler preserves multiword phrases. Before any v2
execution, functional queries were prospectively normalized to ordinary goal
terms and representative synonyms/plurals (maximum eight), avoiding accidental
phrase-only brittleness. Canonical framework names such as `React Native` remain
phrases where intended. No repository names are injected into functional queries.
The RU metrics case is deliberately mixed-language task terminology, not proof
of arbitrary Russian paraphrase coverage; independent lexical RU/EN and narrative
equivalence remain distinct evidence gates.

Source review uses a compact per-case projection of goal, numeric ID, name,
aliases, both descriptions, constraint facts and activity facts. The projection
has its own exact canonical byte measurement/hash and stays below 200 KiB.
Persisted proof matrices can be larger; they are validated programmatically and
are not loaded wholesale into model context. No full 2,500-card model prompt is
allowed.

## Independent goal assessment

The fixed goals are product integration/comparison tasks: local HTTP doubles,
photo/video management, typed data validation, CLI bookkeeping, documentation,
calendar aggregation, server payment adapters, agile planning, data movement,
metrics storage, backend plumbing, own-server deployment and security checks.
Dense goals distinguish household finance from trading and data-platform metadata
from media tags. Development includes cross-browser versus mobile tests, React
components versus authoring tools, Go versus .NET frameworks, resumable transfer
versus generic uploads, and EXIF versus warehouse catalogs.

The manually authored `ASSESSMENTS` table names positive and weak alternatives
with specific source-supported reasons. Category membership only defines the
search universe. Query substrings, runtime rank, stars, freshness, and runtime
eligibility never define a topical grade.

| Grade | Meaning |
| --- | --- |
| 3 | Source explicitly states the core function and a specific requested capability. |
| 2 | Source explicitly states the core function; a requested detail remains unobserved. |
| 1 | Source explicitly states a useful adjacent/supporting function, or source is insufficient and the item is retained only as a weak verification reference. |
| 0 | Reviewed source describes a different function and gives no direct/supporting contribution to this goal. This is a source-supported relevance exclusion, not proof that upstream lacks every unstated capability. |

All remaining identities in each reviewed source projection receive explicit
grade-zero records containing their observed description and the assessed goal,
or weak verification references where descriptions are absent. The builder
materializes those recorded assessments; it does not evaluate a query-token
predicate or assign zero to unobserved IDs. Independent source review checks
plausible counterexamples before freezing. Pre-capture corrections include the
Firefly data importer as a finance support option, SQL query metadata as data
context support, and sparse design systems as UI comparison references.

`adoption_fit=unknown` remains independent of topical relevance. Descriptions
cannot establish deployment compatibility, correctness, licenses beyond source
facts, production/security readiness, measured integration value, or activity
beyond their frozen observations. Missing descriptions and activity dates remain
visible. Weak unknown references count conservatively in the relevance denominator;
they are not promoted to confirmed alternatives.

Exact identity probes admit only the numeric ID reached by the requested current
name/historical alias. An alternative in the same category is grade zero for that
identity task even if useful for another functional goal. Identity probes do not
enter functional macro averages or functional stratum thresholds.

## Constraints and versioned scoring

The source oracle evaluates the frozen public/available/non-archived defaults
from `/repository/visibility`, `/repository/availability`, and
`/repository/archived`. Archived/nonpublic/unavailable is `denied`; an unresolved
mandatory constraint is `unknown`; otherwise `allowed`. These values are checked
against source evidence, never copied from runtime matcher labels. Topical grades
are preserved on denied identities so the source judgment is not rewritten to
match eligibility.

V2 explicitly uses constrained relevance for acceptance: positive grade and
`constraint != denied`. Unknown constraints follow the canonical policy's
reference-with-verification behavior. Denied items have zero constrained gain but
retain their original raw rank positions; ranks are never compacted. Recall@12
uses all independently assessed non-denied positive IDs as denominator. nDCG@12
uses `(2**grade - 1) / log2(rank + 1)` and the ideal order over that same set.
Both baseline and candidate apply exactly this rule. Original **unconditional**
topical Recall/nDCG, including denied positives, must also be reported to expose
the effect of this correction. Requiring a forbidden archived item as an
adoptable target would contradict the non-archived request defaults. This is a
versioned metric-semantic correction, not a silent claim of v1 equivalence.

All numerical thresholds are copied unchanged from `quality-plan.json`: held-out
Recall@12 >= 0.75, nDCG@12 >= 0.65, no regression against the lexical baseline;
required functional strata >= 0.60/0.50; zero hard-constraint errors, false
constraint exclusions and duplicate IDs; identity/alias success 1.0; pack survival
>= 0.90. Performance/headroom declarations and the 16/20 human rubric remain
unchanged. No threshold is lowered to match a run. Cases with more than 12 valid
alternatives report the intrinsic Recall@12 ceiling. H15/H16 deliberately retain
broad-goal realism, and their ceiling can make existing thresholds difficult or
impossible. Such a failure is reported, not repaired after observing held-out ranks.

## Freeze and human calibration

Canonical serialization is sorted keys, compact separators, UTF-8,
`ensure_ascii=False`, `allow_nan=False`. Artifact SHA-256 hashes use exact file
bytes; `plan_sha256`, source projection and query hashes use canonical JSON.
`query_sha256` binds the complete C9 query derived from the fixed terms, locale,
taxonomy route, empty explicit constraint arrays and pinned policy/card/index
versions. The effective non-archived/public/available defaults are assessed
separately above. The runner validates all pins and query/goal/source proofs before
opening the immutable index. Its declaration freezes exact source/protocol/plan/
judgment files and execution configuration before either method runs.

After the first v2 execution, held-out terms, goals, universes, grades, splits,
thresholds and scoring are immutable. Development-only tuning needs a new
declared experiment. A discovered oracle defect invalidates the affected run;
repair requires a new prospective version and a fresh unexposed held-out set.

Four narrative calibration cases were selected before capture: H03
non-technical founder/photo folders, D05 backend engineer/Go HTTP endpoint,
H15 low-context household finance/activity unknowns and H11 Russian-speaking
metrics engineer with paired RU/EN. Fixed contexts and acceptance are in the plan.
The primary composes narratives from actual bounded captures, and an independent
reviewer inspects source facts, counterarguments, unknowns, first validation,
rollback and proposed-only handoff meaning. That agent review cannot establish
human calibration. Human reviewers still supply independent rubric scores,
adjudication and usefulness acceptance; CP-11/15/browser/provider/release evidence
remains outside this oracle.

## Verification and rollback

Run `.venv/Scripts/python.exe -B evals/plugin-v1/build_oracle_v2.py --check` and
`.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_quality_oracle_v2.py -v`.
Tests reject incomplete zero-grade coverage, invented source evidence, source
constraint disagreement and identity/semantic conflation; they also verify a
photo manager versus book-reader counterexample and the actual container route.
Builder validation is integrity/configuration evidence, not semantic calibration.
Rollback consists of discarding these new v2 artifacts; no runtime, index, policy,
old plan/results, public catalog, configuration or Git history is changed.
