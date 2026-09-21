# CP-08 large-project closeout observations

Date: 2026-09-21  
Status: completed_local_v13  
Evidence target: one owner-approved project with more than 100,000 filesystem files, plus focused contract and recovery checks

## Scope and safety boundary

- The target is recorded only as `mypartners-large`; its absolute root, source text, selected paths, environment values and root fingerprint are not retained in this report.
- The target is read-only. No target-project command, dependency installation, network call or persistent target write is permitted.
- Existing scanner exclusions, containment rules, mode confirmation and cumulative budgets remain active.
- Workspace changes are limited to the CP-08 runtime/contracts/tests and control-plane evidence needed to close the accepted local slice.

## Acceptance gates

1. Resolve the restart-checkpoint capacity conflict against the accepted `standard` and `deep` ceilings without weakening the 256 MiB total workspace envelope.
2. Pass focused checkpoint size, persistence, fresh-process restore, policy/version and privacy regressions.
3. Run Draft 2020-12 validation for every registered schema, or retain an explicit blocking verdict if the authorized isolated validator is unavailable.
4. Run fresh `quick`, fresh `standard` and separately confirmed cumulative `standard -> deep` observations on `mypartners-large`.
5. Persist only aggregate counters, reason codes, warnings, serialized sizes and minimized structural/usefulness observations.
6. Close CP-08 only if no P0/P1/P2 implementation finding remains and every residual item is owned by a later product/release gate rather than the scanner slice.

## Progressive observations

### 1. Preflight

- The filesystem inventory command observed 139,618 paths while reporting access-denied entries inside generated/runtime trees. This is a host inventory observation, not the scanner's eligible-file count.
- The accepted scanner profiles remain quick `2,000 / 256 MiB / 120 s`, standard `30,000 / 2 GiB / 1,200 s`, and deep `100,000 / 8 GiB / 4,000 s`.
- Existing real-project checkpoints measured 656,378-1,476,461 bytes at 2,740-5,913 attempted files. The current 2 MiB sidecar ceiling therefore has a credible scale conflict and must be resolved before the large-project run is promoted.

### 2. Contract and runtime remediation

- Scanner policy `1.3.0` keeps the accepted mode, topology, per-file and context ceilings while excluding observed generated/runtime/cache/worktree segments before allowlist evaluation.
- Checkpoint schema `1.1.0` and storage policy `1.1.0` raise only the private checkpoint slot from 2 MiB to 64 MiB. Canonical state remains 2 MiB, HTML remains 5 MiB, and the output root remains 256 MiB/128 entries. The current-plus-pending checkpoint peak is therefore bounded at 128 MiB.
- Retained schema-1.0.0 state remains read-only under storage policy 1.0.0. Current schema-1.1.0 writes require storage policy 1.1.0. Checkpoint schema 1.0.0 and earlier policy pins fail closed.
- One command selected a nonexistent test method and produced a loader error; it did not execute a product check. The corrected method passed 1/1. Four other focused checkpoint/storage/writer-policy methods passed in the same bounded remediation sequence.
- A synthetic 100,000-record checkpoint exceeded the former 2 MiB ceiling, fit the 64 MiB ceiling, was persisted to a disposable local output root and restored by a fresh Python process with all 100,000 records and attempts intact. The exact method passed 1/1 in 8.250 seconds.

### 3. Large-project mode matrix

The owner-approved root contains 139,618 filesystem paths by a host inventory command, with access-denied observations inside generated/runtime trees. After policy-v1.3 exclusions, the scanner observed 1,637-1,641 eligible files; total filesystem size is therefore intentionally not treated as relevant-source size.

| Run | Status / classification | Attempts | Bytes | Active time | Budget reached | Main reason classes |
| --- | --- | ---: | ---: | ---: | --- | --- |
| fresh `quick` | `partial` / `large_or_monorepo` | 1,637 | 33,672,553 | 8.114 s | no | topology, monorepo, exclusions, encoding, containment |
| fresh `standard` | `partial` / `large_or_monorepo` | 1,641 | 39,132,636 | 7.906 s | no | topology, monorepo, exclusions, encoding, containment |
| deep predecessor `standard` | `partial` / `large_or_monorepo` | 1,641 | 39,132,636 | 7.879 s | no | topology, monorepo, exclusions, encoding, containment |
| confirmed cumulative `deep` | `partial` / `large_or_monorepo` | 1,641 | 39,132,636 | 7.880 s | no | monorepo, exclusions, encoding, containment |

- No mode exhausted its aggregate file, byte or time budget. `deep` needed no additional file read after `standard` under the accepted per-file envelope.
- The private checkpoint serialized to 372,024 bytes and restored transiently with counter continuity; topology is deliberately rebuilt after restore.
- The first structural context selection was 12/12 scan-backed, read 92,876 bytes, reached the 65,536-byte model envelope with explicit truncation and produced a 5,932-byte partial Brief. The selected mix contained four ordinary source/config and eight test references; this exposed a real relevance defect rather than proving usefulness.
- The scan observed seven manifests and six service roots. Its large/monorepo classification and remaining partial reasons are non-budget gaps rather than a claim that generated dependencies should be read.
- No network, dependency installation, project execution or persistent target-project write occurred.

### 4. Draft schema and recovery gates

- The previously missing development validator was installed only into ignored `.codex-tmp/cp08-validator`; it is not a plugin/runtime dependency and does not modify global Python.
- The first Draft run exposed four synchronized fixture/conditional-version defects after the policy/storage bump. One bounded repair aligned the policy fixture, checkpoint positive, scan-commit positive and schema-version storage branch.
- The repeated `SchemaContracts` class then passed 11/11, covering all 26 registered schemas, offline references, positive/negative instances, formats and UTF-8 byte annotations.

### 5. Task-specific context remediation and closure

- Root cause: automatic selection was restricted to the small public-summary evidence sample and ranked topology-related paths before direct goal matches. A large first document could also consume the complete model-facing allowance.
- Remediation: `ScanResult` now exposes a transient read-only observed-path ledger, while CP-07 validates persisted selections against the revision/root/policy-bound private checkpoint before deleting it. The public state still stores references only; raw excerpts, the full observed-path ledger and absolute roots are not persisted.
- Direct goal matches now precede merely related paths, implementation/configuration files precede documentation and tests at equal relevance, automatic whole-file selection retains at least a 4 KiB model share per source, and transient delivery fairly allocates the model envelope across the selected set. The higher policy path ceilings remain available for callers that supply bounded line ranges.
- The repeated task-specific standard run selected 12/12 direct goal matches: configuration, README, Python/TypeScript implementation and schema migrations related to contact graph, local RAG, messaging, search and integration. It read 110,913 bytes and delivered 42,882 model-facing bytes across the selected sources with explicit truncation.
- Final bounded regression evidence passed: scanner/intake 18/18, all Draft 2020-12 plus semantic/workspace contracts 48/48, and Codex control-plane contracts 13/13. The isolated validator remains development-only under ignored `.codex-tmp`.
- A final boundary hardening makes CP-07 reconstruct and validate the persisted checkpoint against the current root/run/policy before resolving selection records; only `read` records with the deterministic path evidence ID are accepted. The three affected checkpoint/commit methods passed 3/3 after this change; the already clean broad suites were not looped.
- CP-08 is closed at `completed_local_v13`: bounded read-only scanning, cumulative modes, transient topology, goal-aware context, references-only persistence, CP-07 commit joins, corrections, checkpoint scale/restart and large-project behavior have current local evidence. Persisted crash injection, joined recommendation behavior, human product acceptance, packaging and release remain owned by CP-11/15/16 and are not CP-08 completion claims.
- `policy_limits_calibrated=false` remains intentional: the accepted ceilings are enforced and scale-tested for a 100,000-record checkpoint, but are not represented as a universal performance SLA or exhaustive calibration across arbitrary 100,000-source-file repositories.
