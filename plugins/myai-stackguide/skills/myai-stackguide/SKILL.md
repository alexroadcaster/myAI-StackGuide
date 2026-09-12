---
name: myai-stackguide
description: Build or modernize a project with bounded, evidence-grounded open-source stack guidance and a resumable local session.
---

# myAI-StackGuide

Use the trusted bundled Python entry point with an already available CPython
3.14 interpreter and isolated flags (`-I -B`). Start with `preflight`, then use
the public intake commands documented by the script. Pass free-text events as a
strict UTF-8 JSON object on stdin; never interpolate an answer into a command.

Keep all session writes under the selected project's
`docs/myai-stackguide/`. Treat `state.json` as canonical and `status.html` as a
reloadable offline projection. Report saved and published revisions separately.
Resume the active run instead of replacing it, and use the exact expected run
and revision supplied by the last validated state.

Ask no more than ten adaptive questions and stop early once one accepted answer
is enough to proceed. Explain why each question changes the decision. Preserve
sanitized answers, corrections, explicit assumptions, unknowns, sources, and
correction invalidation. Never persist raw chat or source excerpts.

Scanning is read-only, bounded, and exclusion-aware. It never executes project
code, imports project modules, installs dependencies, follows unsafe paths, or
uses network access. Relevant task-authorized project context may be read within
the accepted containment, sensitivity, and byte budgets; persist minimized
findings and safe references only.

Use only the bundled, pinned public SQLite FTS5 package for retrieval. Do not
rebuild it at runtime, load the whole catalog into model context, activate a
remote service, or silently use another engine. Recommendations and displayed
commands are proposals. Execute an integration only after a separate explicit
implementation request under its actual authorization boundary.

RU/EN presentation is one view of one canonical result. A display-language
change does not scan, retrieve, call a model, or write domain state. Missing
translation remains explicit and canonical technical literals stay unchanged.

Stop on incompatible state/package versions, unsafe or sensitive input, path
escape, busy/conflicting revisions, integrity/storage failure, or an action
outside current authorization. Preserve the last valid state and immutable
history; never delete a lock, prune runs, weaken permissions, or overwrite an
unrecognized artifact to recover.
