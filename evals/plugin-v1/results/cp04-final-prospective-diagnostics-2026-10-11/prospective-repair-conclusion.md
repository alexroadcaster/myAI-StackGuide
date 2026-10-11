# CP-04 bounded prospective diagnosis — no activation

The bounded diagnostic did not find a complete generic winner. Production, policy, assets, frozen goals, grades, literal queries, thresholds and earlier captures remain unchanged. A partial chat repair is measured; the billing floor still fails. This is exposed development evidence, not a new held-out acceptance run.

## Results

Six initial native planner profiles were executed against all45 cases. Every profile preserved the exact raw candidate order on the original30, whose macro Recall/nDCG remains 0.943710237/0.928670756. Every original literal order was independently recalculated and checked against the frozen capture. All original30 floors, hard constraints, alias identity and pack-survival checks passed.

| Prospective profile | Macro Recall | Macro nDCG | Chat Recall | Billing Recall | Remaining failing case |
| --- | ---: | ---: | ---: | ---: | --- |
| Current runtime | .847514390 | .810433088 | .25 | .50 | 07, 08 |
| Required phrase atoms, then route words | .873407248 | .825167756 | .5625 | .55 | 07, 08 |
| Atoms plus required-only equal RRF | .869835819 | .821813692 | .5625 | .50 | 07, 08 |
| Atoms plus overlapping pinned leaf vocabulary | .877871533 | .829801380 | .625 | .55 | 08 |
| Leaf vocabulary plus required-only RRF | .869835819 | .823434370 | .5625 | .50 | 07, 08 |
| Atoms-only equal RRF | .877871533 | .816653391 | .625 | .55 | 08 |

Three further context arms on the leaf-vocabulary planner all retained billing Recall .55. Their prospective macro Recall is .877871533; nDCG is .832982204 (context only), .834515074 (atoms plus context), and .835803774 (required phrases plus context). All original30 queries were exactly identical to their frozen current-runtime queries; their already frozen results were reused with explicit provenance. These arms stay within one aggregate COUNT plus two final MATCH variants, eight terms per variant and150 fetched hits. No context or original term was dropped from the full first query.

The final native SQL screen used five transparent global field-weight alternatives on the same single-variant leaf-vocabulary planner. Other fields retained their current accepted weights. The screen verified native control ranks against the full diagnostic but does not establish guard/pack acceptance for new weights.

| Upstream / catalog / topics weights | Prospective macro Recall | Prospective macro nDCG | Billing Recall |
| --- | ---: | ---: | ---: |
| Current 3 / 3 / 1 | .877871533 | .829801380 | .55 |
| 6 / 1 / .25 | .844198064 | .804788262 | .55 |
| 9 / 1 / .25 | .844198064 | .804441711 | .55 |
| 6 / 3 / .1 | .839733778 | .803919098 | .55 |
| 3 / 1 / .1 | .844198064 | .802236929 | .55 |
| 3 / 3 / 0 | .816987179 | .761015628 | .45 |

All five also lower original FINAL-HOLD-02 Recall to .578947368, versus the current passing result. No weight profile supplies a complete winner. The search stops after these declared profiles; this evidence does not prove that every possible numeric calibration is impossible.

## Cause and contract boundary

For chat, quoted multiword required terms miss useful individual lexical tokens. Original COUNT4 expands a broad container to communications/personal/ops. Required phrase atoms alone recover9/16 positives; using matching source-owned child category vocabulary recovers10/16. The leaf arm derives words only from pinned taxonomy membership whose ID words intersect required lexical atoms, without stemming, role invention or repository conditions. It changes caller query derivation and requires an accepted semantic receipt before activation.

For billing, source coverage is already present. Phrase atoms remove the metering false positive from the top12, but native BM25 still places Android Checkout at12 and leaves11/20 positives in the pack. Both Android Checkout and Powercalc have primary subscription_billing classifications, so a primary/secondary preference cannot resolve this. Source weights and equal-RRF required/context variants did not resolve the remaining ordering defect. Unknown advisory/delivery facts remain unknown; no lexical support was represented as functional fit.

The smallest demonstrated partial repair is the single full-query atom/overlapping-leaf expansion under the existing trusted underfill COUNT, preserving all originals. It is insufficient for completion and is therefore not proposed for production activation alone. The next bounded diagnostic needs an explicitly accepted additional ranking semantic, such as a source-field lexical scorer with documented length normalization, or a separately scoped already-installed local semantic reranker. Native BM25-only numeric weights cannot be declared sufficient from this screen. Any new scoring must preserve honest original C9 rank/BM25 provenance or receive a corresponding C9 policy/result semantic migration; it must not fabricate existing ranks, change fit/unknown rules, or weaken acceptance.

## Formal current calibration

The planner diagnostics retain exact query and pack identity for payment, Greptime alias and web. The training query changes because the required phrase distributed training is underfilled and is atomized; its pack changes too. The four-case formal identity receipt records every initial planner and weight profile. Weight profiles retain query bytes but may change pack bytes. Existing model answers may only be reused where their exact grounded input remains identical; identity checks do not override failing45-case quality.

## Reproduction and handoff

Commands (all completed with exit0):

```powershell
python -B work/cp04-final/prospective-repair-diagnostic.py
python -B work/cp04-final/prospective-repair-context-diagnostic.py
python -B work/cp04-final/prospective-repair-weight-screen.py
python -B work/cp04-final/prospective-repair-formal-identities.py
```

Each creates a new exclusive results file; preserve these captures and choose a new assigned destination for any successor run. Scripts and receipts live only under the assigned prospective-repair-* work prefix. They cache the once-verified public card map while retaining runtime snapshot byte checks; no catalog content is modified. Experimental weight overrides are limited to the SQL execution seam in the diagnostic process and are explicitly distinct from the trusted production policy.

Next owner: root and catalog architect choose and scope the smallest new ranking contract/diagnostic. Runtime activation requires a complete measured generic winner, explicit file ownership, observable regression RED, minimal GREEN and independent successor evidence. Rollback is unnecessary for this read-only production diagnosis: only the assigned new diagnostic artifacts were written.

## Authorized cached TinyBERT successor

The fresh packet separately authorized the existing installed local ONNX adapter and cache. The model files were verified against the existing receipt; ONNX SHA256 is a2b09fb0de692c052a55f4165c9461377b4a31115673b7adb428503d69109196. CPU settings remain batch8, threads4, max_length512, CPUExecutionProvider, sequential ONNX execution, arena/memory_pattern false. No model download, installation, provider call or runtime activation occurred.

One immutable full Brief.goal arm was executed against all45 best atoms_leaf pools. Native C9 results, their actual BM25 floats, native variant ranks and RRF scores are retained verbatim separately from the model scores/permutation. Pure model order and equal native/model RRF use the same exact complete pool; both pass identity/permutation checks. Experimental packing reuses the existing explicitly labeled baseline adapter and does not establish compatibility of a prospective production shortlist contract. Request guard, existing hard facts and unknown handling are retained.

| Arm | Original30 Recall / nDCG | Prospective Recall / nDCG | Billing Recall |
| --- | --- | --- | ---: |
| Native phrase/leaf control | .943710237 / .928670756 | .877871533 / .829801380 | .55 |
| TinyBERT full goal, pure | .943710237 / .872861882 | .868942962 / .727256035 | .55 |
| TinyBERT full goal, equal RRF | .942886061 / .918538602 | .865371533 / .779962392 | .50 |
| Required-phrase underfill cascade, pure | .943710237 / .928670756 | .877871533 / .770393234 | .55 |
| Required-phrase underfill cascade, RRF | .943710237 / .928670756 | .874300105 / .794541812 | .50 |

The cascade uses soft model priority only when the original trusted COUNT is under max_cards and an atom from a multiword required term was actually added. It reuses the same45 inference predictions without additional45-case inference. It retains exact original30 native ordering. All arms retain hard failures0, pack survival1 and alias success. None passes the required billing/container stratum. The unrestricted pure arm additionally loses original30 nDCG nonregression against the literal baseline .914153317.

TinyBERT demotes Android Checkout but promotes Powercalc to9, so it still returns only11/20 positives in the first12. The cascade cannot repair this because the same model prediction is activated on that underfilled phrase. The four formal cascade checks leave payment, Greptime alias and web query/pack bytes unchanged and alter training input/query/pack. Only the triggered training formal case required one additional cached inference.

Observed45 inference samples: median20.455ms, nearest-rank p9549.741ms, max56.112ms. Peak process working set340140032 bytes (324.38MiB) includes the interpreter, runtime and loaded model. COUNT-plus-C9-retrieval timings are recorded separately. These single sequential samples do not claim a warmed repeated performance distribution.

Additional commands, both exit0:

```powershell
& 'work/cp04-flashrank-venv/Scripts/python.exe' -B 'work/cp04-final/prospective-repair-tiny-diagnostic.py'
& 'work/cp04-flashrank-venv/Scripts/python.exe' -B 'work/cp04-final/prospective-repair-cascade-diagnostic.py'
```

The bounded model successor also produced no complete winner. Production source hashes remain recommendation_request.py 3c3d188d51d5c6da55de2fc1655874d15f4919cecae9bea40fa71810d3084ad9 and retrieval.py 6cd0a8012ed47374afee68c957a7369020775562d21b0d8b2649ec3b850f14dd. A broader reranker or scoring-policy investigation would require an explicit successor packet; no additional model/profile arms are inferred from this failure.
