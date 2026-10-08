# Captured solution blueprint evaluation contract

This evaluator implements the accepted response format as a deterministic offline
contract check. It changes no C8/C9 schema, retrieval ranking, judgment, threshold,
runtime or prior result. The normative profile, byte/node limits, required fields,
allowed states and hashes live in `evaluate_solution_blueprint.py`.

## Authority and input boundary

`evaluate(data, source, acceptedpins)` checks a candidate explanation packet against
the explicitly supplied trusted project-fit packet and owner-format declaration.
The frozen two-case profile is D05/H15. Source and acceptance canonical hashes are
pinned; CLI additionally verifies their original byte hashes. The instruction hash
comes from the accepted declaration and is compared with actual explicitly selected
instruction bytes. Candidate bytes may differ from the accepted example: alternative
conditional prose and arithmetically consistent planning ranges are permitted.
Immutable context, persona, goals, constraints, unknowns, selected identities,
captured source projection and capture bindings cannot change.

Besides its own evaluator/test/contract files for receipt hashes, the CLI reads only
its four input arguments (`--blueprints`, `--source`,
`--acceptance`, `--instruction`), whose defaults are fixed trusted repository paths.
It never follows `input_file`, `observation_path`, `source_ref`, URLs or other metadata
as a path or network instruction. Bounded JSON reads reject malformed UTF-8, duplicate
keys, nonfinite numbers, oversized input and unsupported versions. Error receipts
contain bounded categories and known JSON pointers, never source values or exception
messages. Output is stdout, or an exclusive `--output` file; no overwrite or runtime
state write occurs. No network, provider, tokenizer, browser or new capture runs.

## Deterministic checks

- Require nonempty solution, stack, technical, architecture, product, covered versus
  remaining work, complexity, assumptions, phased estimates, comparison, next question,
  rollback and paired presentation structures. Presence is not correctness of prose.
- Require each known case exactly once. Repository identity, reference-only roles,
  unknown adoption fit, evidence IDs, capability bindings and source references remain
  qualified to their explicit numeric owner and exact trusted source.
- Retained/hypothetical/proposed/alternative stack states remain conditional. The
  profile's same-role options are mutually exclusive; at most one proposed option or
  abstract option slot is allowed. No installation or execution claim is permitted.
- Phase IDs and included phase sets are unique. First validation contains the declared
  discovery and pilot once. Full scoped adoption covers each phase once and includes
  the pilot without double counting. H15 full adoption and remaining effort stay
  unknown; its discovery-only estimate covers discovery alone.
- All range bounds are finite positive numbers (bool is not a number), ordered and
  summed by phase. Engineer-days use the named eight-hour unit. The current profile
  uses one engineer, sequential full allocation, no parallelism; working-day bounds
  are the ceilings of hour bounds divided by hours per engineer-day. Remaining work
  is the sum of phases outside first validation. External waits and actual elapsed
  time remain unknown. Assumptions, team, confidence, scope and waiting caveats are
  required. Planning estimates cannot become measured results or delivery commitments.
- RU/EN stored bindings must equal canonical IDs, roles, capture, assumptions, time,
  phases and action state, not merely each other. If architecture/complexity bindings
  are supplied, both locales must equal their canonical objects. The accepted example
  has no such bindings: emit the nonblocking limitation
  `architecture_complexity_locale_semantics_unverified`, validate canonical section
  structure/status, and require semantic review. Do not invent equivalence proof.
- Structured benefit, calibration, promotion, installation and execution flags cannot
  exceed the captured authority. Arbitrary narrative privacy, source faithfulness,
  meaning, usefulness and estimate accuracy need separate review.

Typed failures: `input_limit`, `input_json`, `input_io`, `unsupported_version`,
`trusted_pin_mismatch`, `required_structure`, `case_identity`, `context_binding`,
`provenance_ownership`, `stack_state`, `alternative_joint_adoption`,
`execution_boundary`, `privacy_boundary`, `estimate_boundary`, `phase_identity`, `estimate_range`,
`estimate_arithmetic`, `presentation_binding`. The result bounds reported issues.

## Commands and verdicts (declared before accepted-capture evaluation)

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_plugin_solution_blueprint_eval.py -v
.venv/Scripts/python.exe -B evals/plugin-v1/evaluate_solution_blueprint.py --output evals/plugin-v1/results/cp04-v2-2026-10-08/solution-blueprint-eval-result.json
```

Valid contract: exit0, `contract_verified_only`; invalid candidate: exit1,
`invalid_contract`; invalid/unavailable input: exit2, `invalid_input`.
All receipts keep `semantic_review_required=true`, `promotion_ready=false`,
`human_calibrated=false`, `estimate_calibrated=false`, `installed_runtime_verified=false`.
CLI receipts bind candidate/source/instruction/acceptance bytes plus evaluator,
test and contract source hashes; they report counts and phase arithmetic observations.
No numeric quality score or previous `no_go` override is produced. Owner format
acceptance is recorded separately from runtime/installation/delivery/human rubric.

TDD uses actual versioned captured examples loaded once, with explicit missing-file
failure. Mutations test unsafe contracts rather than example byte identity. Rollback
removes only this evaluator, its test, this contract and the new receipt. Independent
Astra review follows GREEN and exact four-file handoff; all earlier evidence remains.
