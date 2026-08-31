# GPT-5.6 Model And Reasoning Policy

Status: `configured_not_behaviorally_verified`

## Baseline

- The project default is `gpt-5.6-sol` with `high` reasoning for complex product, architecture, implementation, evaluation, and evidence-review work.
- The default unnamed subagent is `gpt-5.6-terra` with `medium` reasoning for bounded everyday work.
- `github_research_curator` and `docs_maintainer` use `gpt-5.6-terra` with `medium` reasoning.
- The other named agents use `gpt-5.6-sol` with `high` reasoning.
- Do not use `xhigh`, `max`, Pro mode, persisted reasoning, Programmatic Tool Calling, or API multi-agent beta without a separate measured requirement and approval boundary.

## Promotion Rule

For every named role, compare the configured baseline with one reasoning level lower on the same representative cases before changing the durable default. Preserve task success, structured outputs, evidence, tool behavior, latency, token use, and cost. A model string, static validator, or successful spawn does not prove model suitability.

## Escalation

- Route consequential evidence conflicts, architecture ambiguity, privacy boundaries, and promotion decisions to `gpt-5.6-sol` with `high` reasoning.
- Keep bounded research, documentation maintenance, formatting, and deterministic processing on Terra/medium when quality remains acceptable.
- Never collapse all workloads onto Sol solely because it is the flagship tier.

## Evidence Required

- same task and prompt across baseline and treatment;
- model ID and reasoning effort;
- task success and output-contract validity;
- tool choice, arguments, retries, and completion;
- latency, tokens, cache behavior, and cost when available;
- edge, negative, and regression cases;
- explicit owner decision for any durable promotion.

## Instruction-Only Changes

Changed durable instructions still require representative fresh-context behavior checks. Repeating a baseline-versus-one-lower model comparison is required before changing a durable model/effort default, not after every documentation-only edit. Preserve the configured baseline during CP-05; no model suitability or promotion claim follows from static tests.
