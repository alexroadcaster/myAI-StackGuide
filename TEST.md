# TEST.md

Verification strategy for the myAI-StackGuide control plane and next contract-definition slice.

## Evidence Policy

- A file existing is not proof that its contract is correct.
- Current command output, reviewed source evidence, or an explicit accepted gap is required for completion claims.
- Generated catalog pages and reports are orientation or delivery artifacts; source builders and parity checks own reproducibility claims.
- Runtime, browser, OAuth, private-repository, and MCP activation claims require separate live evidence and approval.

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
| `V1-MEMO-001` | Memo contains roles, reasons, evidence, avoid/defer, caveats, and next decision. | Implementation commands, unsupported authority, or absent evidence fails. | Quality Evaluator |
| `V1-EVAL-001` | Scenario maps requirement to rubric, check, threshold, and evidence owner. | Scenario without failure criteria, privacy boundary, or human-review rule fails. | Quality Evaluator |
| `V1-GH-001` | Read-only allowlisted evidence retrieval has provenance and fallback. | Write tools, hidden scope expansion, secrets, or silent activation block the slice. | Evidence Reviewer |

## Failure Handling

- Follow the implementation loop in `docs/plan/plugin-v1-team-contracts.md`. Predeclared expected-RED assertions permit their assigned fix; missing dependencies/import failures are not RED. Repair ordinary in-scope failures without weakening acceptance or overlapping another owner's tests.

- Record failed commands and exact observed output in `RUNLOG.md`.
- Do not repair a failing contract by weakening a required field without Product Planner and Catalog Architect review.
- Stop when verification requires private data, credentials, external writes, live provider calls, or permissions not explicitly approved.
