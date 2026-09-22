# GPT-5.6 Model And Reasoning Policy

Status: `configured_not_behaviorally_verified`

## Baseline

- The currently configured project baseline is `gpt-5.6-sol` with `high` reasoning. It is retained pending the same-case `high` versus `medium` comparison and is not a requirement to use high effort for every task.
- Reserve high effort for structural product, architecture, cross-boundary implementation, evidence-conflict and privacy/security work. Prefer medium for bounded implementation, focused verification and documentation when a task-level override is available and representative evidence preserves quality.
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

## Effort Selection

- Micro and contract-value changes use focused context, no subagents and the lowest evaluated effort that preserves the contract.
- Structural work may use high effort when ambiguity, blast radius or evidence conflict justifies it.
- Do not escalate reasoning because a value is repeated widely; first reduce duplicated context and derive consumers from the canonical source.
- Record the comparison before changing `.codex/config.toml` or named-agent defaults. Instruction changes alone do not justify a silent model-default change.
