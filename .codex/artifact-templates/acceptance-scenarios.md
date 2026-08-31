# Acceptance Scenarios

Use this artifact before behavior changes. It links requirements to observable behavior and evidence; it does not replace requirements, tests, or evals.

## Scope

- Slice:
- Requirement IDs:
- Business rule:
- Non-goal:
- Privacy or approval boundary:
- Explicit accepted gap:

## Traceability

| Requirement | Scenario | Observable check | Evidence owner | Status |
| --- | --- | --- | --- | --- |
| Assigned requirement ID | Declarative actor/context/trigger/outcome | Deterministic, manual, contract, eval, or runtime check | Assigned role | `pending` |

## Scenario Contract

- Scenario ID:
- Actor:
- Context or Given:
- Trigger or When:
- Observable outcome or Then:
- Edge case:
- Forbidden outcome:
- Evidence command or artifact:
- Expected result:
- Evidence state: `static`, `measured_local`, `runtime`, `owner`, or `accepted_gap`
- Model and reasoning identity when AI behavior is evaluated:

## Boundaries

- Keep scenarios declarative; do not use UI selectors, database internals, function names, or test harness implementation as the business outcome.
- Stop before implementation when a behavior-changing requirement has no scenario, check, evidence owner, or explicit accepted gap.

## Optional Session Publication Scenario

When the slice changes state or HTML, name the saved revision, visible publication revision, render failure/retry/obsolete-render outcome and the canonical result expected in both languages. Use the accepted workspace contract; do not invent a second writer or require irrelevant UI checks for other tasks.
