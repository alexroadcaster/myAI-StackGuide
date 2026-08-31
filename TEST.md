# TEST.md

Verification strategy for the myAI-StackGuide control plane and local SQLite FTS5/integration slice. Owner revision: 2026-08-31. Future test registries below are not execution evidence.

## Evidence Policy

- A file existing is not proof that its contract is correct.
- Current command output, reviewed source evidence, or an explicit accepted gap is required for completion claims.
- Generated catalog pages and reports are orientation or delivery artifacts; source builders and parity checks own reproducibility claims.
- Runtime/browser claims require observed behavior; private-project, provider, OAuth and MCP actions require their actual authorization. Remote CP-12-14 are not local-release prerequisites. Relevant authorized source reads are not a failure by themselves.

## CP-03 Local Contract Checks

Twenty-two local schemas now include the 1.1.0 presentation/publication addendum; the original 20 positive and 17 negative fixture records remain unchanged. Five linked current-version objects cover stored questions/scan, structured Brief, memo/plan and state; two new schema examples cover localization and publication. The [source map](specs/artifact/session-workspace-contract.md) covers 49 subsections and 164 expanded schema paths. C8 adds two schemas and an offline captured-result scorer.

Full contract acceptance passed on 2026-08-31: **46/46 CP-03 tests and 27/27 C8 tests**, without skips. Independent review repeated both full suites and found no remaining P1/P2 in the contract slice. Both scorer CLI gates passed for four synthetic captures; `promotion_ready=false`, `quality_thresholds_calibrated=false` and `verdict=synthetic_compatibility_only` remain explicit.

The owner authorized development-only wheel installation into TEMP. Python 3.14.6 uses `jsonschema==4.26.0`, `attrs==26.1.0`, `jsonschema-specifications==2025.9.1`, `referencing==0.37.0` and `rpds-py==2026.6.3` from `C:/Users/user/AppData/Local/Temp/stackguide-cp03-standards-n_tpu3_c/validator`. Default Python still has no importable jsonschema without this process-local path. No global Python, plugin dependency, profile or package configuration changed. TEMP is disposable: if absent, prepare a separately authorized development environment; never auto-install through the standard-library plugin.

Executed from the repository in child PowerShell processes with this temporary environment (do not persist PYTHONPATH):

```powershell
$env:PYTHONPATH = 'C:/Users/user/AppData/Local/Temp/stackguide-cp03-standards-n_tpu3_c/validator'
python -B -m unittest discover -s tests -p test_plugin_contracts.py -v
python -B -m unittest discover -s tests -p test_plugin_retrieval_eval.py -v
python -B evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json
python -B evals/plugin-v1/evaluate_retrieval.py --cases evals/plugin-v1/cases.json --results tests/fixtures/plugin_retrieval_eval.json
```

All commands exited 0. The full gates cover Draft 2020-12 meta-validation, offline references, formats, legacy/current version branches, positive/negative instances, nested byte budgets and complete scorer envelope/CLI checks, including CLI exits 0/1/2 on valid/pass, valid/failing and invalid inputs. The earlier missing-dependency failure remains historical evidence in RUNLOG; it is resolved by the authorized isolated environment, not converted into an expected RED or skip. No schema/test/scorer repairs were needed after installation.

Byte annotations and cross-document joins require explicit checks beyond JSON Schema. The referenced structurally legal >12 KiB card inside a <48 KiB pack is now a passing C8 byte regression. Synthetic HTML bytes validate a fixture receipt only, not rendering, atomic writes, locks or installed-plugin behavior. YAML policies use the JSON-compatible YAML 1.2 subset; no YAML parser was added. [Validator documentation](https://python-jsonschema.readthedocs.io/en/stable/validate/) and [offline referencing](https://python-jsonschema.readthedocs.io/en/stable/referencing/) distinguish standards/format/reference validation from custom checks. CP-03 is verified at contract level; full CP-04 quality calibration and all runtime/browser/usefulness gates remain open.

## Planned Session Workspace And RU-EN Checks

R15 and the [workspace design](docs/plan/plugin-v1-session-workspace-design.md) extend CP-03/07/10/11/15/16 acceptance. These are future checks, not executed results:

- CP-10 follows A-D checkpoints in the approved design: common shell/RU-EN first, views 1-4, views 5-7, then History/recovery. Use the smallest relevant fixture/browser check per checkpoint and one final complete eight-view review; no repeated concept-approval gate.
- CP-07 defines and CP-10 binds the commit/publication boundary. CP-11 verifies start -> saved answer -> scan/Brief -> actual FTS5 result -> memo -> correction/invalidation -> resume -> finalization, using one HTML path and explicit committed/published revision identity. No manual second report command is required in the normal flow.
- Inject saved-state/render failure, first-render failure and a late older render racing a newer revision. Preserve saved answers and existing valid HTML, reject obsolete publication, report typed failure to Codex and retry rendering only. No repeat scan/model/retrieval or silent state rollback; an open old file cannot detect newer state on its own.
- Validate locale/source-language, presentation revision/coverage and canonical field/evidence links; reject a translated view tied to the wrong Brief/result revision. The current contract addendum is implemented; runtime consumers and browser checks remain future work.
- Require matching complete RU/EN static UI keys, including unknown/error/status/accessibility/print text. Preserve IDs, paths, URLs, commands, technical terms, timestamps and canonical values.
- Inspect all eight views in RU/EN on desktop/laptop windows at 1280, 1440 and 1920 CSS pixels; add a narrower desktop window, long text and 200% zoom. Mobile adaptation is out of scope. Verify keyboard/focus, document/passages `lang`, direct evidence labels, print caveats and no overlap.
- Switch RU -> EN -> RU on one saved captured result: retain candidate IDs/order, evidence, selected view, comparison and disclosure; no scan/retrieval/model/network call or domain-state write.
- Verify explicit missing-dynamic-translation fallback, missing-dictionary-key build failure, invalid fragment, no JavaScript, denied storage and unavailable clipboard. Standalone-file behavior must not depend on `localStorage`.
- Exercise empty/no-match versus index-unavailable, partial scan, invalidated Brief, saved-answer/render failure, historical run and recovery states in both languages. Old HTML never claims live detection of an unseen state revision.
- Keep bilingual state <= 2 MiB, HTML <= 5 MiB, existing output-root/history caps and one canonical <= 48 KiB evidence pack. No silent budget increase or automatic pruning.

Quality Evaluator uses the existing owned test files and records exact commands when those implementations are assigned; this design task creates no runtime tests or dependencies.

## Control-Plane Checks

Run from the repository root:

```powershell
$productAgentOs = Join-Path $env:USERPROFILE '.codex\plugins\cache\personal-product-agent-plugins\product-agent-os\0.1.0\scripts'
python (Join-Path $productAgentOs 'validate_control_plane.py') .
python (Join-Path $productAgentOs 'validate_agents.py') .codex\agents
python -B -m unittest discover -s tests -p test_codex_contracts.py -v
python -B -m unittest discover -s tests -p test_agent_eval_grader.py -v
python -B scripts/grade_agent_evals.py --validate-cases evals/agents/team-behavior-cases.json
git diff --check
```

Expected results:

- Product-Agent OS reports no missing control-plane files.
- Every agent TOML parses and contains the required Codex and Product-Agent OS fields.
- Project config maps Sol/high and Terra/medium roles and caps agent concurrency at three.
- Every agent declares a nonempty relevant set of discovered skills without absolute path pinning; no fixed quota applies.
- Concrete agent source paths and local skill links resolve. Current taxonomy routes to the manifest, not legacy categories.
- Offline grader tests reject invalid, incomplete, stale, unsafe, and unreviewed packets; synthetic passes never become promotion.
- Git reports no whitespace errors.

## Skill Checks

Run `quick_validate.py` against every `.agents/skills/*` directory with a Python environment that includes PyYAML.

If PyYAML is unavailable, record the official validator as blocked and run an explicit equivalent check for frontmatter keys, skill/folder name equality, naming rules, description constraints, scaffold placeholders, and `$skill-name` metadata. The equivalent check does not convert the blocked official validator into a pass.

Expected results:

- Folder names and `name` values match.
- Frontmatter includes `name` and `description`; supported optional metadata is not rejected merely for existing. The dependency-free parser checks the project's simple metadata, not arbitrary YAML conformance.
- No scaffold placeholders remain.
- `agents/openai.yaml` contains a default prompt that names the skill.
- `.codex/skills` is absent and no agent contains a workspace-absolute skill path.
- Every skill has direct, indirect, incomplete, and non-trigger cases in `evals/skills/skill-activation-cases.json`.

Static activation-case coverage does not prove implicit selection. Fresh-context behavioral runs remain required before `promotion_ready`.

`codex doctor` is an optional environment diagnostic, not a pure offline config validator. It may run network checks and report unrelated terminal/environment failures; do not use its aggregate exit status as sole agent validation or rerun it for every edit.

## Catalog Pipeline Regression Check

The current HTML v5 catalog is generated from `data/catalog_manifest.json` and `templates/unified_catalog.html`. The Markdown artifact retains the dated legacy input boundary. Verify both without writing outputs:

```powershell
python scripts/build_catalog_html.py --check
python -c "import sys; from pathlib import Path; sys.dont_write_bytecode=True; root=Path.cwd(); sys.path.insert(0, str(root/'scripts')); import build_unified_catalog as u; c=u.load_categories(); u.load_repositories(c); assert u.build_markdown(c)==(root/'docs'/'UNIFIED_CATALOG.md').read_text(encoding='utf-8'); print('markdown parity ok')"
python -B -m unittest discover -s tests -p test_catalog_v5_pipeline.py -v
```

Expected result: exact HTML byte/hash parity, `markdown parity ok`, and nine passing v5 pipeline tests.

## Contract Test Matrix For The Next Slice

| Requirement | Positive case | Negative or edge case | Evidence owner |
| --- | --- | --- | --- |
| `V1-CAT-001` | Complete baseline and advisory cards validate. | Missing identity, source, snapshot, trust, or verification fields fail. | Quality Evaluator |
| `V1-TAX-001` | Unique category IDs and valid parents validate. | Alias collision, orphan parent, or duplicate ID fails. | Quality Evaluator |
| `V1-SCAN-001` | Allowed docs/config sources are included and reported. | Secrets, keys, dumps, logs, generated dependencies, and executable behavior are blocked. | Quality Evaluator |
| `V1-CTX-001` | Facts, inferences, confidence, evidence, corrections, and gaps are distinct. | Unsupported inference presented as fact fails. | Quality Evaluator |
| `V1-MEMO-001` | Memo contains roles, sources, caveats, integration surface/steps, first validation slice, rollback and coding-agent handoff. | Unauthorized execution/disclosure, commands falsely claimed tested, unsupported authority, or absent evidence fails; proposed integration steps are allowed. | Quality Evaluator |
| `V1-EVAL-001` | Scenario maps requirement to rubric, check, threshold, and evidence owner. | Scenario without failure criteria, privacy boundary, or human-review rule fails. | Quality Evaluator |
| `V1-GH-001` | Read-only allowlisted evidence retrieval has provenance and fallback. | Write tools, hidden scope expansion, secrets, or silent activation block the slice. | Evidence Reviewer |

## Local SQLite FTS5 And Integration Acceptance

| Tasks / requirement | Required positive evidence | Required negative / edge evidence |
| --- | --- | --- |
| CP-03 / C1-C6, C9 | Typed local query/card/pack/index/activity/context/handoff contracts; complete local acceptance without C7 | Private fields in public index, unsafe grammar, fabricated dates, unbounded pack, incompatible pins and unsupported primary-fit assertions rejected |
| CP-04 / C8 | Same frozen corpus/judgments for lexical baseline and candidate; exact runner/thresholds registered before quality runs | No FTS smoke/throughput promoted to relevance; no held-out leakage, fake token counts or synthetic inventory claims |
| CP-05 / R04, R13 | Updated loaded role/skill cases permit relevant context and actionable handoff | Still exclude secrets and unauthorized execution/install/external disclosure; old scanner-only/blanket-refusal cases explicitly superseded |
| CP-06 / R07, R11 | Source-persisted activity/provenance/coverage -> canonical cards -> logical index parity/manifest | Browser-only metadata, partial-refresh stamp-all-current, push-as-commit, duplicate aliases and user-context leakage rejected |
| CP-07/08 / R02-R05, R10 | Saved/resumed/corrected Brief, bounded scan and useful targeted ordinary source context | Secret exclusions, path escape/races, hostile instructions, cancellation/caps, stale revisions and interrupted writes; no target-project execution |
| CP-09 / R06, R07, R11 | Actual read-only FTS5, compiled/escaped queries, RU/EN/aliases, deterministic dedupe/constraints/pack | Empty/no-hit vs unavailable distinguished; missing FTS5/corrupt/mismatched index explicit; no whole-catalog fallback or index writes |
| CP-09/11 / context limits | Across all variants <=60 candidates, <=12 detailed cards, <=48 KiB serialized evidence including provenance | No counter reset across broadening, truncated data passed as complete, or Brief allocation omitted; limits encoded by CP-03 |
| CP-10/11 / R13 | Useful build/replace/upgrade report with affected components, prerequisites, first experiment and rollback | Proposed commands do not execute or claim successful integration; undefined mandatory facts remain visible |
| CP-11 / R12 | Named useful 1/1 path with actual source_mode=catalog_only and retrieval_engine=sqlite_fts5; then 2,000/10,000 synthetic scaling | No mock/alternate route masks acceptance; synthetic scaling cannot prove real repository count or search relevance |
| CP-15/16 / local release | Held-out relevance/usefulness, independent privacy/UI review, actual install/FTS5/index/version/rollback | No dependency on remote auth/ledger/scheduler; incompatible state/index cannot be silently overwritten |

CP-06 adds `tests/test_plugin_search_index.py`; CP-09 adds `tests/test_plugin_retrieval.py` alongside matching tests. Exact remaining future files/commands are registered in [CP-02 verification](specs/decisions/plugin-v1-verification.md) and the detailed CP tasks. CP-04 owns `evals/plugin-v1/evaluate_retrieval.py`, `tests/test_plugin_retrieval_eval.py` and `tests/fixtures/plugin_retrieval_eval.json`: offline metric scoring of captured C9 results, with tiny known-result positive/error fixtures. It must create the executable scorer and its exact CLI/input/output contract before quality evaluation; no product runner exists just because its name appears here. Require nonzero expected test counts; unittest discovery with zero tests is not acceptance.

Activity cases must include a mature useful repository with an old observation/snapshot, an actively committed incompatible repository, missing commit timestamp, and archived reference material. No blanket 30-day snapshot rejection. Targeted current verification may be recommended for volatile unresolved facts without making remote integration a prerequisite.

## Failure Handling

- Follow the implementation loop in `docs/plan/plugin-v1-team-contracts.md`. Predeclared expected-RED assertions permit their assigned fix; missing dependencies/import failures are not RED. Repair ordinary in-scope failures without weakening acceptance or overlapping another owner's tests.

- Record failed commands and exact observed output in `RUNLOG.md`.
- Do not repair a failing contract by weakening a required field without Product Planner and Catalog Architect review.
- Stop when verification requires private data, credentials, external writes, live provider calls, or permissions not explicitly approved.
