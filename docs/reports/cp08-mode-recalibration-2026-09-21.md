# CP-08 scan-mode recalibration observations

Date: 2026-09-21  
Status: complete at bounded three-project evidence ceiling  
Evidence ceiling: policy-v1.2 three-mode observations on three roots; not universal calibration

## Scope and safety boundary

The owner accepted a new bounded Local V1 scan profile for repeat calibration:

| Mode | Files | Read bytes | Active time |
| --- | ---: | ---: | ---: |
| `quick` | 2,000 | 256 MiB | 120 s |
| `standard` | 30,000 | 2 GiB | 1,200 s |
| `deep` | 100,000 | 8 GiB | 4,000 s |

The checkpoint interval remains 2,000 file attempts or 256 MiB. Topology, per-file, targeted-context, exclusion, containment, no-network, no-install and no-project-execution rules remain unchanged unless an observed contract incompatibility requires an explicit follow-up decision.

The repeat measurement covers the current catalog, `SOL-0.6` and `codex_docs` through a fresh `quick`, a fresh `standard`, and a separate cumulative `standard -> deep` session per root. The duplicate standard pass keeps fresh-profile measurements comparable while preserving the contract that deep must continue the same run after a visible material gap and explicit confirmation. Only aliases, aggregate counters, reason codes, warnings, byte sizes and minimized structural outcomes may be recorded here. Absolute roots, selected relative paths, excerpts, source content, environment values and root fingerprints must not be retained.

## Execution log

### 1. Accepted change and preflight

- Owner supplied the exact three mode ceilings above.
- Existing worktree changes are preserved; no branch, commit, dependency installation, network call or external write is authorized.
- The previous three-project evidence showed the old 2,000-file `standard` ceiling was the binding constraint while byte and time budgets retained substantial headroom.
- Policy/schema/runtime version joins, bounded regression assertions and the calibration helper are being reviewed before the first scan.

### 2. Policy v1.2 implementation preflight

- Versioned the scanner policy as `1.2.0` / `local-scan-v1.2`; the scan-report, manifest and context-selection shapes remain schema `1.1.0` because their structure did not change. Their policy-reference fields now require `1.2.0`.
- Raised aggregate schema/checkpoint counter maxima to 100,000 file attempts and 8 GiB. The independent 2 MiB serialized-checkpoint envelope and the 2,000-file/256 MiB checkpoint cadence remain unchanged.
- Preserved topology, per-file, targeted-context, classification and exclusion values.
- The first bounded preflight ran ten checks. Nine passed. The existing 5,501-file checkpoint regression failed because it expected the old 2,000-file `standard` ceiling to produce `partial`; under v1.2, `standard` correctly completed that synthetic project.
- One narrow test repair moved that continuation setup to `quick`, whose new 2,000-file ceiling still produces the intended visible gap before `deep`. No runtime acceptance or limit was weakened. Only this affected method will be rerun before real-project reads.
- The exact affected checkpoint/Brief method then passed 1/1 in 12.522 seconds. The real-project matrix may proceed; the initial nine passing checks and this targeted rerun are retained instead of repeating the full preflight.

## Observations

- Policy v1.2 static/runtime preflight: nine initial checks passed; one stale expectation was repaired and its exact method passed 1/1.
- Focused runtime checks are sufficient to begin the bounded real-root matrix; no broad suite was repeated.
- Current catalog measurement completed; aggregate observations are recorded below.
- `SOL-0.6` measurement completed; aggregate observations are recorded below.
- `codex_docs` measurement completed; aggregate observations are recorded below.

### 3. Current catalog

| Case | Status / classification | Attempts | Read bytes | Active time | Budget reached | Main reasons |
| --- | --- | ---: | ---: | ---: | --- | --- |
| fresh `quick` | `partial` / `large_or_monorepo` | 2,000 | 13,358,945 | 12.738 s | yes | `budget_reached`, `excluded_sources` |
| fresh `standard` | `partial` / `standard` | 5,694 | 90,020,739 | 36.709 s | no | `excluded_sources` |
| deep predecessor `standard` | `partial` / `standard` | 5,694 | 90,020,739 | 27.984 s | no | `excluded_sources` |
| confirmed cumulative `deep` | `partial` / `standard` | 5,695 | 92,306,068 | 28.456 s | no | `excluded_sources` |

- `quick` now performs the former standard-sized 2,000-attempt overview and emits `files_80_percent` before stopping at its file ceiling.
- Fresh `standard` reaches the full eligible set reported for its 2 MiB per-file profile with substantial headroom under 30,000 files, 2 GiB and 1,200 seconds.
- The explicit `deep` continuation adds one 2-4 MiB-eligible source: one attempt, 2,285,329 bytes and 0.472 seconds. No automatic escalation occurred.
- The minimized checkpoint is 1,476,461 bytes, restores in a fresh session with counter continuity and deliberately marks transient topology incomplete after restore.
- Context composition selects 12/12 scan-backed references, reads 108,637 bytes, reaches the unchanged 65,536-byte model-context ceiling with explicit truncation and emits a 6,183-byte partial Brief. Generic calibration terms match no retained path names; usefulness remains structural only.
- No network, install, project execution or persistent target-project write occurred.

### 4. SOL-0.6

| Case | Status / classification | Attempts | Read bytes | Active time | Budget reached | Main reasons |
| --- | --- | ---: | ---: | ---: | --- | --- |
| fresh `quick` | `partial` / `large_or_monorepo` | 2,000 | 17,928,836 | 12.318 s | yes | `budget_reached`, `monorepo_detected`, `excluded_sources` |
| fresh `standard` | `partial` / `large_or_monorepo` | 2,740 | 114,208,234 | 23.931 s | no | `monorepo_detected`, `excluded_sources` |
| deep predecessor `standard` | `partial` / `large_or_monorepo` | 2,740 | 114,208,234 | 22.172 s | no | `monorepo_detected`, `excluded_sources` |
| confirmed cumulative `deep` | `partial` / `large_or_monorepo` | 2,740 | 114,208,234 | 22.174 s | no | `monorepo_detected`, `excluded_sources` |

- `quick` stops at 2,000 attempts with `files_80_percent`; its partial result still detects 13 manifests and seven service roots within the bounded overview.
- Fresh `standard` reaches all 2,740 eligible files reported for this root and expands the observed service-root count to 13 without reaching its file, byte or time budget.
- Confirmed `deep` adds no file or byte work beyond the predecessor; only two milliseconds of cumulative call overhead are recorded. This is evidence that `standard` is already sufficient for this root under the unchanged per-file and topology rules.
- The minimized checkpoint is 656,378 bytes, restores with continuous counters and marks transient topology incomplete after restore.
- Context composition selects 14/14 scan-backed references, reads 66,194 bytes, reaches 65,535 model-facing bytes with explicit truncation and emits a 6,036-byte partial Brief. Source buckets are five documentation and nine source/config references; no generic goal term matches a retained path.
- No network, install, project execution or persistent target-project write occurred.

### 5. codex_docs

| Case | Status / classification | Attempts | Read bytes | Active time | Budget reached | Main reasons |
| --- | --- | ---: | ---: | ---: | --- | --- |
| fresh `quick` | `partial` / `large_or_monorepo` | 2,000 | 46,146,842 | 22.086 s | yes | budget, topology, monorepo, exclusions, encoding, containment |
| fresh `standard` | `partial` / `large_or_monorepo` | 5,911 | 94,320,839 | 20.092 s | no | topology, monorepo, exclusions, encoding, containment |
| deep predecessor `standard` | `partial` / `large_or_monorepo` | 5,911 | 94,320,839 | 19.438 s | no | topology, monorepo, exclusions, encoding, containment |
| confirmed cumulative `deep` | `partial` / `large_or_monorepo` | 5,913 | 101,641,668 | 20.041 s | no | monorepo, exclusions, encoding, containment |

- `quick` stops at 2,000 attempts with `files_80_percent`. It identifies 83 manifests but only three service roots before the file ceiling and does not establish the workspace declaration.
- Fresh `standard` reaches 5,911 eligible files and observes 81 service roots plus the workspace declaration without reaching file, byte or time budgets. Its partial status remains truthful because topology, encoding and containment gaps remain.
- Confirmed `deep` adds two files admitted by its larger per-file envelope: 7,320,829 bytes and 0.603 seconds. It removes the predecessor's `topology_incomplete` reason but does not erase containment or encoding gaps.
- The minimized checkpoint is 1,347,446 bytes, restores with continuous counters and marks transient topology incomplete after restore.
- Context composition selects 8/8 scan-backed source/config references, reads 700,341 bytes, reaches 65,535 model-facing bytes with explicit truncation and emits a 4,914-byte partial Brief. No generic goal term matches a retained path.
- No network, install, project execution or persistent target-project write occurred.

## Cross-root comparison

| Alias | Fresh quick | Fresh standard | Confirmed deep increment | Checkpoint | Context |
| --- | --- | --- | --- | ---: | --- |
| current catalog | 2,000 attempts; file cap | 5,694 attempts; no budget cap | +1 file / +2.29 MiB | 1,476,461 B | 12/12 backed; 6,183 B Brief |
| `SOL-0.6` | 2,000 attempts; file cap | 2,740 attempts; no budget cap | no additional read | 656,378 B | 14/14 backed; 6,036 B Brief |
| `codex_docs` | 2,000 attempts; file cap | 5,911 attempts; no budget cap | +2 files / +7.32 MiB | 1,347,446 B | 8/8 backed; 4,914 B Brief |

Observed interpretation:

- The new `quick` ceiling behaves like the former standard file envelope and remains a bounded overview on all three roots.
- The new `standard` ceiling completes the scanner-reported eligible set for all three roots with very large file/byte/time headroom. It does not convert explicit non-budget gaps into false completeness.
- `deep` contributes only its larger per-file eligibility on two roots and no read work on `SOL-0.6`; it is not an automatic or routinely necessary second pass for this sample.
- All measured checkpoints remain below 2 MiB, but the sample reaches only about 5.9% of the 100,000-file deep ceiling. This does not prove that a 100,000-file checkpoint can fit the unchanged storage envelope.
- All context selections are scan-backed and structurally useful under the aggregate definition. Human/task-specific semantic usefulness remains unmeasured.

## Verification observations

- The exact CP-07 scan/context commit integration method passed 1/1 in 10.216 seconds against policy v1.2, including revisioned commit, immediate replay and checkpoint cleanup behavior.
- The Draft 2020-12 `SchemaContracts` class did not run: its setup failed because the development-only `jsonschema` validator is unavailable in the current environment. This is an environment-blocked gate, not a pass or skip. No dependency was installed and no retry loop followed.
- Dependency-free policy assertions were extended to verify the 100,000-file/8 GiB manifest and checkpoint maxima, context-selection policy pin `1.2.0`, and the deliberate split between report schema `1.1.0` and policy version `1.2.0`. Their final targeted results are pending below.
- The first two-method final policy check passed the runtime/report-version method but the new semantic assertion addressed the checkpoint schema through the positive-fixture registry, where this private sidecar schema is intentionally absent. One narrow test-only repair now loads that exact schema directly; only the affected semantic method will be rerun.
- The exact affected semantic method then passed 1/1. No scanner/runtime change was required.
- Control-plane contracts passed 13/13. Seven changed JSON policy/schema/fixture documents parsed, four Python runtime/helper files compiled from source, and `git diff --check` exited zero with line-ending warnings only.
- Independent final review found one P1 checkpoint contract-parity defect before closure: runtime always exports `session.limit_overrides`, while the strict checkpoint schema did not admit that field. The schema now requires a bounded per-mode override object whose maxima match policy v1.2, and the checkpoint regression compares the runtime session keys with both the schema's required and property sets. Targeted verification and reviewer re-check are pending.
- The same review found the checkpoint and two runtime commit-request schemas absent from the mandatory Draft positive registry, plus a P2 gap for an explicit v1.1 sidecar rejection. The registry now derives three joined positives from the canonical scan/selection/Brief fixtures, raising expected schema coverage from 23 to 26 without duplicating large nested objects. The checkpoint regression now submits a representative v1.1 policy-pinned sidecar and requires fail-closed `checkpoint_invalid`. No real-root rerun is required.
- Targeted closure passed 2/2 in 6.588 seconds: runtime checkpoint/schema key parity plus explicit v1.1 rejection, and dependency-free 26-schema/policy/maxima registry parity. A separate schema-key assertion passed and `git diff --check` remained clean apart from line-ending warnings. Independent re-review is pending; Draft validation remains environment-blocked rather than claimed.
- Independent read-only re-review returned GO with no remaining P0/P1/P2. It confirmed both checkpoint P1 findings and the v1.1 fail-closed P2 are closed. This does not convert the unavailable Draft `SchemaContracts` gate into a pass or raise the evidence ceiling.

## Current claim boundary

Policy v1.2 is implemented and has bounded observations across the three approved roots. This evidence does not prove workloads near 30,000 or 100,000 files, a 100,000-file checkpoint under 2 MiB, universal-project performance, semantic relevance, human usefulness, persisted crash recovery, install, release or publication. `policy_limits_calibrated=false` remains unchanged.
