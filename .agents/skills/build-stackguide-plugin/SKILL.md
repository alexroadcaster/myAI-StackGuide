---
name: build-stackguide-plugin
description: Implement an accepted myAI-StackGuide local plugin slice for intake, scanning, sanitized state, matching, or offline reports. Use after runtime and schema gates are closed; do not use it to select missing architecture, scan private projects, or activate remote integrations.
---

# Build StackGuide Plugin

## Inputs And Gate

Require an accepted CP task, CP-02 runtime decision, CP-03 contracts, exact owned files and tests, synthetic inputs, and runnable verification commands. If any is missing, return the missing contract and owner without starting runtime implementation.

## Workflow

1. Read the active task and Implementation Loop And Handoff in [Team contracts](../../../docs/plan/plugin-v1-team-contracts.md). For intake/scanner/state work also read Intake, Context, And Local State and Permission And Tool Contract.
2. Select the smallest accepted seam and state its observable acceptance. Use deterministic scripts for bounded file processing, sanitization, state persistence, matching, and rendering; do not substitute a prompt for an enforceable boundary.
3. Follow the assigned test ownership. Cover the seam's meaningful negative case: correction invalidation, version-safe resume, partial/empty scan, path containment, unsafe output, interruption, or concurrent state.
4. Preserve snapshot/overlay pins and visible catalog-only fallback. A missing permission or failed candidate upload must not be hidden or converted into an incomplete report claimed as complete.
5. For HTML work, escape untrusted content and use offline assets. Source checks are not rendered acceptance; run authorized browser QA before claiming UI behavior.

## Output And Stops

Return exact files, input/contract versions, commands and results, evidence level, unresolved gates, rollback, and next owner. Stop before external actions, dependency installation, private-project access, schema mutation, or ownership expansion. Do not install recommended repositories. Missing CP-02 decisions are not permission to choose a runtime silently.
