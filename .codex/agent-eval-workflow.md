# Agent And Skill Eval Workflow

Status: `spec_present_not_model_run`

## Static Gate

1. Parse `.codex/config.toml` and every `.codex/agents/*.toml`.
2. Verify official required agent fields, supported GPT-5.6 model IDs, reasoning baselines, sandbox mode, and the three assigned skill names.
3. Verify repo skills under `.agents/skills`, frontmatter, `agents/openai.yaml`, and absence of workspace-absolute paths.
4. Verify every skill has direct, indirect, incomplete, and non-trigger cases.

## Behavioral Gate

Run each case in a fresh context without leaking the expected route. Capture selected agent or skill, model, effort, tools, output-contract result, stop behavior, latency, and token usage. A static pass remains `configured_not_behaviorally_verified`.

## Comparison Gate

For GPT-5.6 roles, run the configured baseline and one reasoning level lower on the same cases. Promote or downgrade only when the representative set preserves quality and boundaries while improving latency or cost.

## Promotion States

- `spec_present_not_model_run`: cases and validators exist only.
- `measured_local`: representative fresh-context runs exist locally.
- `accepted_gap`: an owner records the missing evidence, reason, residual risk, and follow-up.
- `promotion_ready`: static and behavioral gates pass and the owner accepts the model/skill route.
