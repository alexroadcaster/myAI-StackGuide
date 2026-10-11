# CP-04 structured exclusions and clarification gate — 2026-10-11

Implemented the owner-approved continuation without agents: a development recommendation-request envelope preserves explicit product/dependency exclusions alongside unchanged C9 query/intent. Material unresolved decisions return questions before retrieval. A source-backed selector removes documented conflicts before the final pack, preserves surviving order and refills from the bounded ranked pool. Missing facts and available deployment alternatives require verification; neither implies full compliance.

This is implemented and measured in the isolated CP-04 continuation, not an installed-plugin/C9 migration. Codex/interview still supplies structured interpretation; automatic free-text interpretation, model-generated clarification and final advice are not evaluated. The active public index, policy, trust anchors, rankers and card metadata remain unchanged. Canonical cards cannot acquire a hidden shipped dependency sidecar.

## Results

| Check | Before | Guarded |
| --- | --- | --- |
| Negative top12 lists without independently known conflicts, all five methods | 1/30 | 30/30 |
| Negative final packs without independently known conflicts, all five methods | 6/30 | 30/30 |
| Three structured unresolved requests / five methods stop before retrieval | 0/15 under evaluator-preselected routes | 15/15, no route/query or pack |
| Original twelve cases / five methods retain exact full order | prior reference | 60/60 |
| Historical original/conservative full orders | prior reference | 10/10 |

The before ambiguity path was forced to a route by the evaluator; this is not a measurement of a previous model failing to clarify. After, callers mark material decisions unresolved and the boundary enforces zero calls. Negative quality is restricted to independently known conflicts, not full dependency compliance. For example, removing Caddy does not prove that HAProxy or Traefik satisfies automatic internal CA; removing Logto does not prove the unchecked providers can run without PostgreSQL. Positive-role mismatches can also remain.

Historical complete Recall@12=0.8048992673992673 and nDCG@12=0.8745552065363883 are identical to the stronger original literal baseline. New-case full-universe metrics remain unavailable. Broad priority remains rejected by its earlier per-case regressions. Parent status remains `in_progress / partially_verified / no_go`, `promotion_ready=false`.

## Negative cases: conservative mode

| Condition | Known conflicts before | Known conflicts after | First three surviving names (not full-fit assertions) |
| --- | ---: | ---: | --- |
| Python tasks with retries; no Redis, Valkey or RabbitMQ. | 1 | 0 | PrefectHQ/prefect, temporalio/sdk-python, coleifer/huey |
| Python scheduled pipelines with retries; Kubernetes is forbidden. | 1 | 0 | PrefectHQ/prefect, temporalio/sdk-python, coleifer/huey |
| Local SQLite realtime backend; no PostgreSQL or MongoDB service. | 3 | 0 | pocketbase/pocketbase, appwrite/appwrite, get-convex/convex-backend |
| B2B SaaS organizations and SSO; PostgreSQL is forbidden. | 1 | 0 | zitadel/zitadel, ory/polis, oomol-lab/open-connector |
| S3 file storage and metadata; exclude MinIO from consideration. | 1 | 0 | seaweedfs/seaweedfs, juicedata/juicefs, ceph/ceph |
| Automatic public/internal HTTPS proxy; Caddy is excluded by project policy. | 1 | 0 | haproxy/haproxy, traefik/traefik, envoyproxy/envoy |

Dependency gaps are explicitly retained in `selection.verification_required`; documented alternative configurations appear in `conditional_configuration_ids`. BullMQ is absent from the dependency fact registry because the relevant Python/PostgreSQL transport was not established. The previous retrospective source correction remains frozen.

## Artifacts and checks

- [Implementation](../../scripts/guard_recommendation_request.py), [contract](../../evals/plugin-v1/request-guard-contract.md), [structured cases](../../evals/plugin-v1/request-guard-cases-2026-10-11.json), [dependency evidence](../../research/cp04-request-dependency-evidence-2026-10-11.json). Evidence contains canonical identity, source URLs, observation dates and deployment alternatives; no oracle grades/case IDs.
- [Frozen declaration](../../evals/plugin-v1/results/cp04-request-guard-v2-2026-10-11/declaration.json), [observations](../../evals/plugin-v1/results/cp04-request-guard-v2-2026-10-11/observations.json), [summary](../../evals/plugin-v1/results/cp04-request-guard-v2-2026-10-11/summary.json). Declaration SHA256=8367201ed84f09dc52d0ee13e6d8a259520dae8d7a36c20d40f0c019dca26dae.
- `python -m unittest discover -s tests -p test_plugin_request_guard.py`: 7/7 pass. Observed RED retained forbidden products/dependencies; minimal guard fixes restore selection and clarify without retrieval. Initial placeholder also lacked conditional metadata/clarification support; these were implementation gaps, not dependency failures.
- First frozen capture failed with `ValueError: invalid retrieval candidate`: after exclusion, surviving FTS ranks were non-consecutive. [Failure record](../../evals/plugin-v1/results/cp04-request-guard-2026-10-11/failure.json) and source snapshots preserved. Transport rank repair retains original scores and source order; the added regression verifies ranks and non-mutation.
- `python evals/plugin-v1/run_request_guard.py --predeclare` then `--run`: corrected v2 declaration and capture succeeded; all stated comparisons executed.
- `python scripts/build_plugin_search_index.py --check`: passed, unchanged 2,500 cards/126 routes and active hashes. Product-Agent OS `validate_control_plane.py .`: passed, no errors or missing files.
- Explicit primary self-review plus independent arithmetic/source-hash/transport/identity/link audit; no independent agent or model judgment.

## Skills investigated via find-skills

Checked the skills.sh directory and upstream instruction files, without installing packages or executing remote scripts. Two suitable additional skills come from [ai-evals-course/evals-skills](https://github.com/ai-evals-course/evals-skills), observed approximately1.5K GitHub stars on 2026-10-11:

| Skill | Use for CP-04 | Observed skills.sh installs |
| --- | --- | ---: |
| [evaluate-rag](https://www.skills.sh/ai-evals-course/evals-skills/evaluate-rag) | Separate retrieval quality from final-answer faithfulness/relevance; avoid treating these guard counts as answer quality | 854 |
| [write-code-eval](https://www.skills.sh/ai-evals-course/evals-skills/write-code-eval) | Objective exclusion, schema, source-ID and no-call checks for observed failures | 232 |

Reviewed primary sources: [evaluate-rag instructions](https://github.com/ai-evals-course/evals-skills/blob/main/skills/evaluate-rag/SKILL.md), [write-code-eval instructions](https://github.com/ai-evals-course/evals-skills/blob/main/skills/write-code-eval/SKILL.md). Counts/popularity are discovery signals, not quality or security guarantees. Both are below the preferred1K install threshold; inspected scope and upstream instructions rather than relying on popularity alone. Their relevant principles informed separation of metrics and objective trace checks; they are not installed/automatically loaded skills. Project build-stackguide-plugin remains the implementation workflow.

Optional installation commands for a separately authorized installation:

```powershell
npx skills add https://github.com/ai-evals-course/evals-skills --skill evaluate-rag
npx skills add https://github.com/ai-evals-course/evals-skills --skill write-code-eval
```

Next integration gate: bind the structured envelope to the actual Codex/Brief/interview caller and show exclusions/verification gaps to composition; test natural-language RU/EN interpretation, source-grounded explanations and ambiguity resolution end-to-end. Canonical dependency fields need accepted public-card ownership/versioning before shipping; no automatic activation follows this development result. Rollback only this additive slice and its new control references, preserving all previous captures/dirty work.
