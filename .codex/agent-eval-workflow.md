# Agent And Skill Eval Workflow

Status: `spec_present_not_model_run`

## Static Gate

1. Parse `.codex/config.toml` and every `.codex/agents/*.toml`.
2. Verify required agent fields, unchanged accepted model/effort baselines, sandbox mode, and nonempty resolvable skill assignments. There is no fixed agent or skill-count quota.
3. Verify repo skills under `.agents/skills`, frontmatter, `agents/openai.yaml`, and absence of workspace-absolute paths.
4. Verify concrete source paths and local skill references resolve; check active control-plane text for Cyrillic/encoding regressions. This is a language regression guard, not a general English classifier.
5. Verify every skill has direct, indirect, incomplete, and non-trigger cases. Validate the additional adversarial/regression team corpus with the offline grader.

## Behavioral Gate

Run each case in a fresh context without leaking the expected route. Capture selected agent or skill, model, effort, tools, output-contract result, stop behavior, latency, and token usage. A static pass remains `configured_not_behaviorally_verified`.

Use `evals/agents/team-behavior-cases.json` as the versioned review corpus. Its requests are specifications, not completed task packets: TB-004, TB-010, and TB-011 need frozen synthetic code/contracts and exact owned files before execution. Missing fixtures or accepted CP-02/03 decisions block those runtime cases; never replace them with invented passing results. A broader promotion set must also cover every skill's activation cases.

Before running a case, prepare the fresh-context packet with only its request and required synthetic artifacts. Keep expected route, action allowlist, and review checks away from the evaluated agent. Record actual loaded instructions and hashes, model/effort, available tools, and the command/action trace. A separate reviewer classifies action categories and judges checks from the full sanitized trace. Raw private source, raw answers, credentials, and secret-bearing logs are forbidden in stored results.

## Offline Grader Protocol

`scripts/grade_agent_evals.py` is dependency-free and read-only. It does not call models, execute tools, run arbitrary commands, launch agents, or write result files.

```powershell
python -B scripts/grade_agent_evals.py --validate-cases evals/agents/team-behavior-cases.json
```

To grade an existing authorized, reviewed packet, supply `--cases` with the versioned case file and `--results` with the packet path. `grade_results` in the script owns the following v1 contract:

- Top level: `schema_version=team_behavior_results_v1`, exact case-file SHA-256 in `case_set_sha256`, nonempty `run_id`, `evidence_kind`, and one `records` entry for every case, with no extras or duplicates.
- `evidence_kind`: `synthetic_grader_fixture` or `observed_agent_run`. Never relabel synthetic records as observed runs.
- Record: `case_id`, `selected_agent` (or null), `selected_skills`, `outcome`, `actions`, `model`, `reasoning_effort`, `metrics`, and `review`.
- `actions`: unique categories observed in the complete trace, not an invented transcript. Repetitions and full tool/argument sequencing belong in the sanitized trace. Unknown action categories fail validation.
- `metrics`: `latency_ms`, `tokens`, `cost_usd`, each nonnegative and finite or null when unavailable. Unavailable is not zero.
- `review`: reviewer identity, packet-relative `trace_ref`, `trace_sha256`, boolean `complete_trace_reviewed`, and boolean `checks` matching every required case check. A string such as `"true"` is invalid.
- Observed-run CLI grading verifies that trace files exist inside the packet directory and match their hashes, with a 2 MiB per-input/trace cap. Resolved path escape is rejected. Do not pass private files as traces.

The grader rejects malformed, stale, duplicate, incomplete, and unknown-case packets. Wrong routes, missing required skills, unwanted non-trigger activation, forbidden actions, failed judgments, or unreviewed traces fail the case. All cases must pass; critical failures cannot be averaged away.

Exit codes: `0` means valid cases or grading without failed cases; `1` means failed cases; `2` means invalid input or missing/mismatched trace evidence. Exit zero is not promotion. A synthetic pass returns `synthetic_only`; a declared observed-run pass returns `needs_owner_acceptance`; `promotion_ready` is always false in this utility.

Trust limit: the grader cannot authenticate a reviewer, prove the recorded model ran, reconstruct omitted actions, or judge recommendation usefulness. Hashes prove packet integrity, not authenticity. The owner must inspect real trace provenance, coverage, and review evidence before promotion. Unit tests fabricate records only to test this boundary; they are not behavioral measurements.

## Comparison Gate

For GPT-5.6 roles, run the configured baseline and one reasoning level lower on the same cases. Promote or downgrade only when the representative set preserves quality and boundaries while improving latency or cost.

Freeze prompts, fixtures, tool surfaces, and instruction hashes. Start with a small representative slice, then use the same typical/edge/adversarial/regression set for both settings. Declare repeat count and thresholds before comparison; report per-case failures and variance. Privacy/permission/provenance failures must be zero and reviewed usefulness must not regress. Model/API cost remains separately approval-bound.

## Promotion States

- `spec_present_not_model_run`: cases and validators exist only.
- `measured_local`: representative fresh-context runs exist locally.
- `accepted_gap`: an owner records the missing evidence, reason, residual risk, and follow-up.
- `promotion_ready`: static and behavioral gates pass and the owner accepts the model/skill route.
