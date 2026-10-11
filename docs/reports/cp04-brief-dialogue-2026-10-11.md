# CP-04 Brief-bound bilingual model dialogue

Status: `implemented_measured_local / partially_verified / no_go`. Parent CP-04 remains open; `promotion_ready=false`.

The shipped read-only entry point now binds a Codex interpretation to the exact validated ProjectContextBrief1.1 digest/version, retains canonical constraints, stops unresolved requests before retrieval, and filters explicit exclusions before building the active C9 evidence pack. The bundled guard deliberately matches the preserved development implementation byte-for-byte. Public dependency observations are transient caller inputs; unknown and conditional configurations remain unresolved rather than becoming compliance claims.

## Scope and execution

Four synthetic conversations cover Python background tasks and ambiguous product search, independently in Russian and English. The host executes the real Brief correction, active SQLite retrieval, guard and pack builder. Actual `codex exec --ephemeral --sandbox read-only --json` calls interpret and compose; recorded synthetic history connects bounded stages. Repository configuration selects `gpt-6.1-sol` / `high`, with no override. This is a CLI model/Brief boundary evaluation, not proof of a persisted desktop chat or the CP-11 writer/publication lifecycle. No subagents were used.

The initial restricted CLI execution failed before reaching the model with Windows app-server `Access is denied (os error 5)`. Its artifacts remain in the original capture's `environment-failure` folder. The permitted rerun retained the child read-only sandbox. No bypass, credential installation or project-data disclosure was introduced.

Original capture: [declaration](../../evals/plugin-v1/results/cp04-dialogue-2026-10-11/declaration.json), [observations](../../evals/plugin-v1/results/cp04-dialogue-2026-10-11/observations.json). A driver defect transmitted only six of twelve validated cards, omitting Huey. Both queue answers correctly abstained within that smaller supplied set. Search clarified corpus/capabilities first, retained the Typesense exclusion and recommended validating Meilisearch.

The [paired successor](../../evals/plugin-v1/results/cp04-dialogue-full-pack-2026-10-11/observations.json) replays the same recorded model interpretations, corrected Briefs, clarification answers and selected order, while supplying every validated pack card. Only answer generation is repeated. Model nondeterminism and prompt changes prevent treating this as a statistical quality benchmark. Frozen declarations, prompts, responses, JSONL events and execution receipts support source attribution.

## Comparison and transcripts

See [objective audit](../../evals/plugin-v1/results/cp04-dialogue-full-pack-2026-10-11/audit.json) and the appended case table/transcript links. Objective checks verify hash pins, explicit exclusions, no-call clarification, Brief correction, permitted recommendation IDs, exact paired selected order and absence of tool items. They do not score usefulness, grounding completeness or estimate accuracy.

Earlier [structured guard results](cp04-request-guard-2026-10-11.md) measured 30/30 known-conflict-free negative lists/packs, 15/15 structured clarification stops, 60 preserved orders and ten historical ranking cases (Recall@12 0.8048992673992673; nDCG@12 0.8745552065363883). Those are preserved prior observations, not newly executed or interchangeable with these four model dialogues. Canonical cards/index/policy/trust anchors remain unchanged and the active index parity check passed. The new integration adds no ranking bonus or candidate-bundle activation.

## Explicit primary self-review

The answers connect requirements to capabilities and distinguish proposed architecture, technical work, product outcomes, complexity, scoped estimates and equivalent-scope custom development. Source-backed fit remains conditional on target deployment and load. Estimates are model planning assumptions, not measured hours or savings; independent generation can produce different estimates in RU/EN. These were two independent language conversations, not a language-only display switch over one canonical recommendation.

The Russian queue full-pack output contains literal newline escapes. Its raw JSON is preserved; the readable transcript only replaces literal backslash-n sequences with newlines. Product-facing output is also too verbose and sometimes exposes catalog IDs/status vocabulary. These are presentation gaps, so this report does not award final user-experience acceptance. Unknown dependency coverage outside supplied observations remains unknown. Citation presence is not proof of every statement.

## Installed skills and verification

Installed [evaluate-rag](../../.agents/skills/evaluate-rag/SKILL.md) and [write-code-eval](../../.agents/skills/write-code-eval/SKILL.md) from [ai-evals-course/evals-skills](https://github.com/ai-evals-course/evals-skills) with the official skill installer, download method and explicit project destination. [Receipt](../../research/cp04-installed-eval-skills-2026-10-11.json) records the source, license URL and installed-byte hashes. Applied their separation of retrieval/answer evaluation and deterministic/objective checks. New discovery/activation specifications are structural evidence; fresh automatic skill routing remains untested and new-session discovery is required.

Observed checks:

- `python -B -m unittest discover -s tests -p test_plugin_brief_request.py -v`: 6/6 passed, including real active retrieval, stale Brief rejection and no-call clarification.
- Retrieval tests: 18/18 passed; matching tests: 5/5 passed.
- `python scripts/build_plugin_search_index.py --check`: passed, unchanged active bundle.
- `test_codex_contracts.py`: 11/13 passed after adding discovery cases; two existing GPT-5.6 baseline expectations conflict with current GPT-6.1 configuration. These unrelated failures were recorded without changing model policy or weakening tests.
- Product-Agent OS `validate_control_plane.py .`: passed, no errors/missing files.
- `git diff --check`: passed with existing line-ending warning.

This compatibility unit couples the bundled entry point/guard/runtime instruction with Brief tests and the bilingual eval inputs/drivers; project skill files and activation specifications are required by the explicit installation request. Changes span two existing control-document families only to record current evidence. No canonical catalog generation or Git operation occurred. Roll back only these additive files and this turn's references after checking later edits; preserve all prior dirty work and immutable captures.

Remaining gates: independent unseen/model usefulness assessment, human acceptance, source-owned dependency evidence coverage, presentation normalization and concise answers, persisted CP-11 writer/desktop lifecycle, and separate release gates. No full CP-04 closure or deployment readiness follows from four synthetic conversations.

## Captured comparison

| Case | Six-card answer | Complete-pack answer | Clarifying questions before retrieval |
| --- | --- | --- | --- |
| CP04-DIALOG-queue-ru | [] | [2703394] | 0 |
| CP04-DIALOG-search-ru | [130688011] | [130688011] | 2 |
| CP04-DIALOG-queue-en | [] | [2703394] | 0 |
| CP04-DIALOG-search-en | [130688011] | [130688011] | 1 |


[Full CP04-DIALOG-queue-ru transcript](../../evals/plugin-v1/results/cp04-dialogue-full-pack-2026-10-11/CP04-DIALOG-queue-ru/transcript.md)

[Full CP04-DIALOG-search-ru transcript](../../evals/plugin-v1/results/cp04-dialogue-full-pack-2026-10-11/CP04-DIALOG-search-ru/transcript.md)

[Full CP04-DIALOG-queue-en transcript](../../evals/plugin-v1/results/cp04-dialogue-full-pack-2026-10-11/CP04-DIALOG-queue-en/transcript.md)

[Full CP04-DIALOG-search-en transcript](../../evals/plugin-v1/results/cp04-dialogue-full-pack-2026-10-11/CP04-DIALOG-search-en/transcript.md)

Observed model calls: baseline 10; paired answer replay 4. Usage (input/cached input/output): baseline {'input_tokens': 394506, 'cached_input_tokens': 0, 'output_tokens': 11794}; replay {'input_tokens': 244359, 'cached_input_tokens': 0, 'output_tokens': 7947}. Cached input is a subset of input, not an additional token total. No dollar cost or comparative speed claim is inferred.
