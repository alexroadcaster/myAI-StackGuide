# CP-04 union top-12 review and request boundary probes

The oracle assesses the 129 case/repository pairs (93 unique repositories) in the
five-arm union of the twelve frozen new-domain top-12 captures. Primary GitHub
READMEs and linked official feature documentation were read on 2026-10-11.
Judgments were authored after the prior capture, before this capture, by the same
author. They are not independent or held out and do not cover the routed universe.

Grade 3 means documented requested main capabilities; 2 means a conditionally
useful core with named unverified details; 1 means a supplementary component;
0 requires a documented role mismatch or explicit requirement conflict. Unknown
mandatory fit remains null. Grade 2 is not hard-requirement compliance. Report
counts at their actual positions; official Recall/nDCG remain unavailable.

Six prospective negative probes reuse existing positive query/intent projections:
no Redis/Valkey/RabbitMQ, no Kubernetes, no external PostgreSQL/MongoDB, no
PostgreSQL for B2B identity, explicit MinIO exclusion, and explicit Caddy exclusion.
Only documented conflicts or user product exclusions are labeled forbidden.
Uninspected dependency combinations remain unknown. Neither these labels nor
the oracle are passed to ranking or used to filter candidates.

Three prospective ambiguous requests require clarification about search corpus,
federation domain, and workflow purpose. Their routes/positive terms are evaluator
assumptions reused from prior cases; this runner observes retrieval, not model
interpretation, interview, final recommendation, or ambiguity resolution.
Do not label an unevaluated clarification path as a demonstrated model failure.

Freeze oracle, challenges, runner, tests, this contract, old captures and candidate
hashes before --run. Re-execute five arms on 21 cases and the ten original judged
regressions for literal/conservative priority. Compare exact old orders. Candidate
public retrieval must still reject the unactivated index. Compact captures retain
queries, intent, ranked/packed identities, pack hash and explicit conflicts.

Commands:

```powershell
python -m unittest discover -s tests -p test_plugin_domain_review.py
python evals/plugin-v1/run_domain_review.py --predeclare
python evals/plugin-v1/run_domain_review.py --run
```

Rollback removes only these additive eval inputs/outputs. Active retrieval,
policy, catalog, trust anchors and candidate facts remain unchanged. This evidence
does not promote either priority method or close CP-04.
