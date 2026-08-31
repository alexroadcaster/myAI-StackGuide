# CP-02: Local Plugin Permissions And Data Boundaries

Decision date: 2026-08-30; owner amendment: 2026-08-31. Status: selected design, not runtime enforcement. Read [architecture](plugin-v1-architecture.md) and [verification](plugin-v1-verification.md).

## Authority And Data Flow

The owner prioritizes useful OSS integration and modernization over an absolute scanner-only source boundary. R04 is explicitly revised: relevant project files or excerpts may inform Codex under the user's actual host permissions. This does not disable sandboxing, authorize secrets, grant access to another/private project, or make the model local. The former `R04_host_isolation_unresolved` release blocker is superseded by this product decision; it is not a passed technical isolation test.

| Surface | Intended access | Evidence required |
| --- | --- | --- |
| Scanner | Bounded regular files in the selected project; structured observations; no writes, project execution or network | CP-03/08 containment, exclusions, caps, errors and no-execution tests |
| Plugin skill / host model | User answers, sanitized Brief and selected relevant source context within existing authorization | CP-03 selection contract; CP-05/08 traces for useful bounded reads, no secrets and no unrequested expansion |
| Retrieval | Read packaged public cards/index and a bounded structured query | CP-06/09 source/index pins, read-only open and bounded output; no project context stored in index |
| Artifact writer | Minimized summaries and safe evidence references under `docs/myai-stackguide/` | CP-07/10 atomicity, revision, escaping and output containment |
| Host Codex | Actual account, tools, permissions and data handling remain in force | No host-wide no-source/no-transmission guarantee inferred from a skill |
| Plugin remote services | None in local V1 | No connection wiring, plugin network attempts, credentials, upload or telemetry |

The recommendation workflow can describe integration steps, affected components, test commands and rollback. It does not execute them merely because it recommends a repository. If the user explicitly requests implementation, hand off the accepted goal, scope, sources and permissions to the coding workflow; do not reflexively refuse all coding or ask again for already-authorized ordinary local work. Installs, external writes, destructive operations, secrets and material costs remain subject to their actual boundaries. Scanner actions never execute the target project.

## Context Access And Product Privacy

The scanner provides the cheap overview; the agent may request only missing high-value context. CP-03 defines purpose, selected root, relative references, bounded file/byte/response budgets, sensitivity exclusions and omission reasons for targeted reads. Relevant ordinary source may be consumed transiently; full source files, raw conversations and unrelated confidential data are not copied into state/report/index. Persist minimized findings and safe references sufficient to check the recommendation. User context remains confidential even after sanitization.

An explicit request to analyze the selected project authorizes ordinary relevant reads within the disclosed scope and host permissions. Do not ask for permission per file. A material expansion to another root, credentials, sensitive data or external disclosure needs the appropriate authorization. A scanner failure is not permission to defeat containment/exclusions through another tool; targeted reads must respect the same safety boundary. If useful context cannot be read safely, continue from available evidence and explain the gap.

Do not promise that Codex never sees source, that chat already sent can be unsent, or that local artifacts mean offline model inference. A skill is guidance, not a separate security principal. Strict-isolation use cases are unsupported by this baseline unless a separately evidenced host setup supplies that property. No host profile, privilege broker or global permission is changed here. Official package/permission sources checked in CP-02 remain historical design evidence; recheck at packaging: [skills](https://developers.openai.com/plugins/build/skills), [permissions](https://learn.chatgpt.com/docs/permissions).

## Scanner And Sanitizer Requirements

- Deny sensitive files before read: credentials/keys, environment secrets, `.git`, host configuration, dumps, customer exports, logs, archives/binaries and dependency/build trees. Exclude plugin output. CP-03 owns ordinary-source allowlists and targeted-read policy; model text cannot override sensitive exclusions.
- Canonical containment, path components and file identity must be checked. Reject traversal, ADS/device/UNC paths, symlinks/junctions/reparse points and hardlink aliases; do not use a failed check as a trigger for a less restrictive retry. CP-08 verifies Windows path-swap/changed-file handling; unsupported containment produces an explicit gap/error.
- Treat project files, comments, README, answers, state and catalog descriptions as untrusted data. Never execute/import/evaluate them, follow their instructions, or invoke project commands to collect context. Only trusted bundle scripts may run with an isolated trusted interpreter.
- Structured scanner output contains observations and safe references, not arbitrary source/config strings or private URLs. Separately selected relevant excerpts are transient context, not scanner-log/persistence payloads. CP-03 bounds and labels each path explicitly so this distinction is testable.
- Minimize and redact state, HTML, stdout/stderr, parser exceptions, logs and temporary/recovery files. Errors must not echo secret contents or absolute target paths. Regex secret detection is a backstop, not proof arbitrary confidential prose is public-safe.
- Warn users not to enter secrets. Persist sanitized answers with `redaction_applied` when necessary; never duplicate the raw chat. No project-context index, global context cache or automatic bulk embedding/upload.

## Disclosure, State And Local Access

Before scanning, show the selected root locally, purpose, budgets/exclusions and output location. Explain that Codex may use relevant project context under its settings, the plugin adds no remote service, and project-local artifacts may be copied by existing Git/sync/backup workflows. The user may choose idea/manual context instead. No GitHub login or contribution consent is needed for `catalog_only`.

Artifact validation, concurrency, retention and storage caps are unchanged from the architecture ADR. Preserve unrelated pre-existing output files with a conflict instead of overwrite. No automatic deletion, encryption claim, `.gitignore` change or permission modification. Keep final history immutable and confined to the selected output root.

Offline HTML escapes untrusted content, permits only safe URL schemes, has no analytics/CDN/automatic fetch and does not read project files. External source links are explicit user actions. CP-10/15 must verify rendered behavior, including hostile text/URLs.

## Deferred Remote Boundary

CP-12-CP-14 are optional future extension tasks, not local-release prerequisites. Before dispatch, select exact service/auth/consent/quota/retry/retention/commands and accept remote C4/C7 contracts. Future MCP receives a minimal public-safe DiscoveryQuery and public candidate evidence, never private Briefs, answers, source excerpts, local paths or project identifiers. GitHub reading and own-backend writing are separate actions; curator acceptance is never automatic. Refusal preserves the local path.

## Stop, Review And Rollback

Stop the affected operation on secret exposure, unapproved scope expansion, unsafe paths, unexpected execution/write/network, unsupported state/index version or a claim beyond evidence. A permitted relevant source read is not itself a failure. Preserve valid state and report useful partial findings. CP-15 reviews the revised privacy contract and useful integration handoff; full host isolation is not an acceptance condition. Reversal changes only task-owned documents, not host policy or user files.
