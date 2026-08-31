# TEST.md

Verification strategy for the myAI-StackGuide control plane and local SQLite FTS5/integration slice. Owner revision: 2026-08-31. Future test registries below are not execution evidence.

## Evidence Policy

- A file existing is not proof that its contract is correct.
- Current command output, reviewed source evidence, or an explicit accepted gap is required for completion claims.
- Generated catalog pages and reports are orientation or delivery artifacts; source builders and parity checks own reproducibility claims.
- Runtime/browser claims require observed behavior; private-project, provider, OAuth and MCP actions require their actual authorization. Remote CP-12-14 are not local-release prerequisites. Relevant authorized source reads are not a failure by themselves.

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
