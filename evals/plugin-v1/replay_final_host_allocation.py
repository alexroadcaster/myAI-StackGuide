"""Explicit offline allocation replay of retained actual host orders.

No model invocation exists in this utility. Historical v1.0 artifacts stay
immutable; new local receipts are separately bound to the current outer contract.
Only root may freeze/run after final Architecture/Product/Quality source approval.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PREFIX = "evals/plugin-v1/"
MAPPING = PREFIX + "host-allocation-eval-contract-2026-10-11.json"
REVIEW = "work/cp04-final/host-allocation-quality-mapping.json"
PRIOR = PREFIX + "results/cp04-final-host-decision-2026-10-11/"
ARCHIVE_MAP = PREFIX + "results/cp04-final-host-pre-allocation-source-2026-10-11/source-map.json"
OUTPUT = ROOT / PREFIX / "results/cp04-final-host-allocation-replay-2026-10-11"
FROZEN = OUTPUT / "frozen-plan.json"
IMMUTABLE = {
    PRIOR + "frozen-plan.json": "d47db040edf529edceee77ba00eead3a48f37e48553c31959b4b9c39bc0b4522",
    PRIOR + "observations.json": "efc773667601b8c3709fde1ff35a7943e065fa6030b018a660c48e89b066c9cc",
    PRIOR + "conclusion.json": "b084df78537039d15288e3b9547c70fe4da074dd1f7d5b332323267ac6e2e6b0",
    ARCHIVE_MAP: "789a12baccbf0abcdb38caaa32992f40e8a7ea51a31c292cba1dbfeac09b7e58",
}
CHANGED_SOURCES = {
    "plugins/myai-stackguide/scripts/recommendation_decision.py",
    "specs/retrieval/candidate-decision-contract.md",
    "specs/retrieval/candidate-decision.schema.json",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def verify(hashes):
    for name, expected in hashes.items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or sha(path) != expected:
            raise ValueError("frozen source/input drift: " + name)


def differences(old, new, prefix=""):
    """Return exact paths; list order and typed scalar values are meaningful."""
    if type(old) is not type(new):
        return [prefix + ":type"]
    if isinstance(old, dict):
        result = [prefix + "/" + key + ":key" for key in sorted(set(old) ^ set(new))]
        for key in sorted(set(old) & set(new)):
            result.extend(differences(old[key], new[key], prefix + "/" + key))
        return result
    if isinstance(old, list):
        if len(old) != len(new):
            return [prefix + ":length"]
        return [path for index, (left, right) in enumerate(zip(old, new))
                for path in differences(left, right, prefix + "/" + str(index))]
    return [] if old == new else [prefix]


def semantic_projection(preview):
    """Normalize only the prospectively approved operational differences.

    Missing/extra keys, wrong types, source hashes, source fields, coverage,
    intent, identity ordering and effective guards remain exact. Reservation
    shape is unchanged in1.1; no entire subtree is discarded.
    """
    value = copy.deepcopy(preview)
    methods = {"1.0.0":"host_codex_full_pool_v1",
               "1.1.0":"host_codex_full_pool_v1_1"}
    version = value.get("schema_version")
    if version in methods and value.get("method") == methods[version]:
        value["schema_version"] = "<approved_outer_version>"
        value["method"] = "<approved_outer_method>"
    bindings = value.get("bindings", {})
    for key in ("contract_schema_sha256", "contract_document_sha256"):
        content = bindings.get(key)
        if (type(content) is str and len(content)==64 and
            all(character in "0123456789abcdef" for character in content)):
            bindings[key] = "<approved_outer_contract_hash>"
    reservation = value.get("reservation")
    if (isinstance(reservation,dict) and set(reservation)=={"receipt_bytes","pack_bytes"}
        and all(type(size) is int and 0<size<=163840 for size in reservation.values())):
        for key in reservation:
            reservation[key] = "<approved_reservation_bytes>"
    return value


def preview_comparison(old, new):
    exact = differences(old, new)
    meaningful = differences(semantic_projection(old), semantic_projection(new))
    return dict(semantic_equal=not meaningful, meaningful_differences=meaningful,
                exact_differences=exact)


def self_check():
    """Persistent boundary checks; no real capture, native query or model."""
    sample = dict(schema_version="1.0.0", method="host_codex_full_pool_v1",
        bindings=dict(contract_schema_sha256="a"*64,
                      contract_document_sha256="b"*64, query_sha256="c"*64),
        reservation=dict(receipt_bytes=123, pack_bytes=456),
        decision_context=dict(goal="component task", intent=dict(required_groups=[["work"]])),
        candidates=[dict(github_repository_id=1, retrieval_rank=1, guard_status="reference_only",
                         fields=[dict(source_field="/descriptions/catalog", text="source", coverage="complete")])])
    allowed = copy.deepcopy(sample)
    allowed["schema_version"] = "1.1.0"
    allowed["method"] = "host_codex_full_pool_v1_1"
    allowed["bindings"]["contract_schema_sha256"] = "d"*64
    allowed["bindings"]["contract_document_sha256"] = "e"*64
    allowed["reservation"]["pack_bytes"] = 789
    assert preview_comparison(sample, allowed)["semantic_equal"], "allowed operational change rejected"
    for name, mutate in [
        ("text", lambda x: x["candidates"][0]["fields"][0].update(text="changed")),
        ("coverage", lambda x: x["candidates"][0]["fields"][0].update(coverage="truncated")),
        ("guard", lambda x: x["candidates"][0].update(guard_status="blocked")),
        ("source_binding", lambda x: x["bindings"].update(query_sha256="f"*64)),
        ("identity", lambda x: x["candidates"][0].update(github_repository_id=2)),
        ("intent", lambda x: x["decision_context"]["intent"].update(required_groups=[["other"]])),
        ("reservation_type", lambda x: x["reservation"].update(pack_bytes="789")),
        ("unexpected_reservation_key", lambda x: x["reservation"].update(unapproved_target=3)),
    ]:
        changed = copy.deepcopy(sample)
        mutate(changed)
        assert not preview_comparison(sample, changed)["semantic_equal"], name + " difference hidden"
    print(json.dumps(dict(status="self_check_pass", checks=9,
                          native_calls=0, actual_model_calls=0)))
    return 0


def helpers():
    path = ROOT / PREFIX / "run_final_host_decision.py"
    spec = importlib.util.spec_from_file_location("allocation_host_helpers", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assemble(stability_path):
    verify(IMMUTABLE)
    mapping, review = read(MAPPING), read(REVIEW)
    if mapping.get("status") != "technically_accepted_for_offline_replay_pending_actual_current_usefulness":
        raise ValueError("final allocation mapping is not accepted")
    if review.get("technical_mapping_accepted") is not True or review.get("mapping_sha256") != sha(ROOT / MAPPING):
        raise ValueError("final Quality mapping receipt missing or stale")
    verify(review["source_hashes"])
    verify(mapping["authority"]["architect_binding"]["source_hashes"])
    verify(mapping["technical_acceptance"]["runtime_source_hashes"])
    verify({mapping["authority"]["product_review"]: mapping["authority"]["product_review_sha256"]})
    stability = read(stability_path)
    if stability.get("ready") is not True or not stability.get("source_hashes"):
        raise ValueError("root stable replay authorization missing")
    if "plugins/myai-stackguide/scripts/recommendation_decision.py" not in stability["source_hashes"]:
        raise ValueError("root stable allocation helper pin missing")
    verify(stability["source_hashes"])
    original = read(PRIOR + "frozen-plan.json")
    captured = read(PRIOR + "observations.json")
    archives = read(ARCHIVE_MAP)["files"]
    archived_hashes = {entry["archive"]:entry["sha256"] for entry in archives.values()}
    verify(archived_hashes)
    if len(original["inputs"]) != 60 or len(captured["records"]) != 60 or captured.get("model_calls") != 60:
        raise ValueError("retained actual60 coverage mismatch")
    for name, expected in original["source_hashes"].items():
        if name in CHANGED_SOURCES:
            if name not in archives or archives[name]["sha256"] != expected:
                raise ValueError("original source archive mismatched: " + name)
        elif sha(ROOT / name) != expected:
            raise ValueError("non-allocation original source changed: " + name)
    host = helpers()
    if digest(host.INSTRUCTION) != original["instruction_sha256"] or host.ORDER_SCHEMA != original["order_schema"]:
        raise ValueError("fixed ordering instruction/schema changed")
    accepted = read(PREFIX + "quality-plan.json")
    for key in ("thresholds", "stratification"):
        if original[key] != accepted[key] or mapping[key] != original[key]:
            raise ValueError("frozen acceptance differs: " + key)
    source_names = set(original["source_hashes"]) | {MAPPING, REVIEW,
        Path(__file__).relative_to(ROOT).as_posix()}
    source_names.update(stability["source_hashes"])
    source_names.update(mapping["technical_acceptance"]["runtime_source_hashes"])
    input_hashes = dict(IMMUTABLE)
    input_hashes.update(archived_hashes)
    input_hashes[stability_path] = sha(ROOT / stability_path)
    plan = dict(schema_version="cp04_host_allocation_replay_plan_v1",
        cases=copy.deepcopy(original["cases"]), inputs=copy.deepcopy(original["inputs"]),
        suites=copy.deepcopy(original["suites"]), pins=copy.deepcopy(original["pins"]),
        artifacts=copy.deepcopy(original["artifacts"]),
        thresholds=copy.deepcopy(original["thresholds"]),
        stratification=copy.deepcopy(original["stratification"]),
        native_schema_set_sha256=original["native_schema_set_sha256"],
        fixed_wrapper_utf8_bytes=original["fixed_wrapper_utf8_bytes"],
        instruction_sha256=original["instruction_sha256"],
        order_schema=original["order_schema"],
        method=mapping["authority"]["architect_binding"]["method"],
        outer_schema_version=mapping["authority"]["architect_binding"]["outer_schema_version"],
        source_hashes={name:sha(ROOT / name) for name in sorted(source_names)},
        input_hashes=input_hashes, production_stability=stability,
        retained_source_archive=ARCHIVE_MAP,
        mapping_path=MAPPING, retained_actual_model_calls=60, new_actual_model_calls=0,
        expected_local_native_calls=60, exposure="all60_now_exposed_recorded_order_regression",
        human_acceptance=False, promotion_ready=False)
    for frozen, row in zip(plan["inputs"], captured["records"]):
        if (frozen["case"]["case_id"] != row["case_id"] or
            digest(frozen["case"]) != row["case_sha256"] or
            digest(frozen["payload"]) != row["payload_sha256"]):
            raise ValueError("historical case/payload drift")
    contracts = host.runner.old.scorer.Contracts()
    if contracts.schema_set_sha256 != plan["native_schema_set_sha256"]:
        raise ValueError("native closed schema registry changed")
    return plan, host


def pack_gates(host, session, result, preview, raw, cards, wrapper):
    order = result["decision_receipt"]["decision_order"]
    pack = result["decision_pack"]
    pool = [item["github_repository_id"] for item in raw["candidates"]]
    selected = [item["card"]["identity"]["github_repository_id"] for item in pack["cards"]]
    excluded = [item["github_repository_id"] for item in pack["exclusions"]]
    query = session.catalog_query
    native_by_id = {item["github_repository_id"]:item for item in raw["candidates"]}
    by_id = {card["identity"]["github_repository_id"]:card for card in cards}
    previews = {item["github_repository_id"]:item for item in preview["candidates"]}
    ranks = {rid:rank for rank,rid in enumerate(order,1)}
    primary = [rid for rid in order if rid in selected and previews[rid]["guard_status"]=="primary_eligible"]
    reference = [rid for rid in order if rid in selected and previews[rid]["guard_status"]=="reference_only"]
    ledger = len(canonical(dict(preview_request=preview, **result))) + wrapper
    gates = dict(complete_permutation=len(order)==len(set(order)) and set(order)==set(pool),
        complete_pack_accounting=len(selected+excluded)==len(set(selected+excluded)) and set(selected+excluded)==set(pool),
        detailed_card_cap=len(selected)<=query["max_cards"],
        shared_budget=ledger<=query["max_evidence_bytes"],
        controlled_input_budget=ledger+session.byte_accounting["input_bytes"]<=session.byte_accounting["input_cap"],
        receipt_preview_binding=result["decision_receipt"]["preview_request_sha256"]==digest(preview),
        pack_receipt_binding=pack["decision_receipt_sha256"]==digest(result["decision_receipt"]),
        exact_source_cards=all(item["card"]==by_id[item["card"]["identity"]["github_repository_id"]] for item in pack["cards"]),
        native_ranks_scores=all(item["retrieval_rank"]==native_by_id[item["card"]["identity"]["github_repository_id"]]["rank"] and
            item["rrf_score"]==native_by_id[item["card"]["identity"]["github_repository_id"]]["rrf_score"] and
            item["decision_rank"]==ranks[item["card"]["identity"]["github_repository_id"]] for item in pack["cards"]),
        primary_then_reference=selected==primary+reference and not any(previews[rid]["guard_status"]=="blocked" for rid in selected),
        identical_bindings=preview["bindings"]==result["decision_receipt"]["bindings"]==pack["bindings"])
    return gates, ledger


def replay(plan, host, cards, members, registry):
    import recommendation_decision as decision
    previous = read(PRIOR + "observations.json")["records"]
    records = []
    for frozen, old in zip(plan["inputs"], previous):
        case, payload = frozen["case"], frozen["payload"]
        start = time.monotonic()
        session, trace = host.native_prepare(decision, payload, plan["fixed_wrapper_utf8_bytes"])
        if isinstance(session, dict):
            write(OUTPUT / case["case_id"] / "failure.json", dict(stage="prepare", result=session, trace=trace))
            raise ValueError("typed prepare failure; no recorded-order fallback")
        preview, raw, control = session.preview_request, session.native_result, session.control
        allocation_start = time.perf_counter_ns()
        allocation = session.allocation
        allocation_ms = (time.perf_counter_ns()-allocation_start)/1e6
        write(OUTPUT / case["case_id"] / "prepared.json", dict(
            preview_request=preview,native_raw_result=raw,native_control=control,
            native_trace=trace,preview_sha256=digest(preview),new_actual_model_calls=0))
        comparison = preview_comparison(old["preview_request"], preview)
        write(OUTPUT / case["case_id"] / "preview-comparison.json", comparison)
        if not comparison["semantic_equal"]:
            raise ValueError("semantic preview changed; actual successor ordering required: " + case["case_id"])
        query = control["request"]["catalog_query"]
        filtered = [card for card in cards if any(p["category_id"] in members[case["route"]] for p in card["classifications"])]
        literal_ids = host.runner.old.scorer.lexical_baseline(filtered, case["terms"], query["max_candidates"])
        literal_rank = host.runner.rank(literal_ids, case["judgments"], case["k"])
        # Historical45 baseline rows contain their separate native-style pack
        # diagnostics; new15 baseline rows contain only IDs/ranking. Retain both
        # shapes unchanged after recomputing the actual literal order/metrics.
        literal = copy.deepcopy(old["baseline"])
        native = host.runner.observe(case, control, raw["status"])
        controls = dict(exact_native_raw=raw==old["native_raw_result"],
            exact_native_control=control==old["native_capture"], exact_query=query==old["query"],
            exact_native_metrics=native==old["native_control"],
            exact_literal=literal_ids==literal["raw_ranked_ids"] and literal_rank==literal["ranking"])
        if not all(controls.values()):
            write(OUTPUT / case["case_id"] / "control-failure.json", controls)
            raise ValueError("native/literal control changed: " + case["case_id"])
        order = copy.deepcopy(old["candidate_capture"]["decision_receipt"]["decision_order"])
        result, finalize_trace = host.local_finalize(decision, session, order)
        if "decision_receipt" not in result or "decision_pack" not in result:
            write(OUTPUT / case["case_id"] / "failure.json", dict(stage="finalize", result=result))
            raise ValueError("typed recorded-order finalization failure")
        observed = host.host_observe(case, result)
        gates, ledger = pack_gates(host, session, result, preview, raw, cards, plan["fixed_wrapper_utf8_bytes"])
        gates.update(controls)
        input_payload = dict(brief=payload["brief"],interpretation=payload["interpretation"],
            public_observations=list(payload.get("public_observations",[])),
            targeted_context=payload.get("targeted_context"),wrapper_bytes=plan["fixed_wrapper_utf8_bytes"])
        gates["actual_local_input_bytes_exact"] = session.byte_accounting["input_bytes"]==len(canonical(input_payload))
        gates["zero_finalizer_sql"] = not finalize_trace["sql_trace"]
        gates["comparison_target_capacity"] = len(result["decision_pack"]["cards"])>=allocation["target"]
        gates["current_outer_version_method"] = all(
            artifact["schema_version"]==plan["outer_schema_version"] and artifact["method"]==plan["method"]
            for artifact in (preview,result["decision_receipt"],result["decision_pack"]))
        gates["recorded_order_exact"] = result["decision_receipt"]["decision_order"]==order==old["candidate"]["raw_ranked_ids"]
        gates["retained_order_ranking_exact"] = observed["ranking"]==old["candidate"]["ranking"]
        if not all(gates.values()):
            raise ValueError("allocation replay protocol gate failed: " + case["case_id"])
        row = dict(case_id=case["case_id"], case_sha256=digest(case), payload=payload,
            payload_sha256=digest(payload), metric_family=case["metric_family"], split=case["split"],
            tags=case["tags"], container_domain_ids=case["container_domain_ids"], query=query,
            query_sha256=digest(query), candidate=observed, baseline=literal, native_control=native,
            native_capture=control, native_raw_result=raw, native_trace=trace,
            preview_request=preview, preview_sha256=digest(preview),
            candidate_capture=result, candidate_capture_sha256=digest(result),
            preview_comparison=comparison, protocol_gates=gates, shared_ledger_bytes=ledger,
            local_finalize_trace=finalize_trace, helper_stage_timings=session.timings,
            byte_accounting=session.byte_accounting, local_prepare_ms=trace["prepare_ms"],
            local_finalize_ms=finalize_trace["finalize_ms"],
            allocation_diagnostics=allocation,local_allocation_diagnostic_ms=allocation_ms,
            total_local_work_ms=trace["prepare_ms"]+finalize_trace["finalize_ms"]+allocation_ms,
            offline_full_path_seconds=time.monotonic()-start,
            recorded_order_fixture=dict(source=PRIOR+"observations.json", source_sha256=IMMUTABLE[PRIOR+"observations.json"],
                case_id=case["case_id"], order=order, retained_model_trace=old["model_trace"],
                evidence_kind="retained_v1_actual_order_replayed_locally", new_actual_model_calls=0),
            exposure=plan["exposure"], human_acceptance=False)
        write(OUTPUT / case["case_id"] / "observation.json", row)
        records.append(row)
        verify(plan["source_hashes"])
        verify(plan["input_hashes"])
    by_id = {row["case_id"]:row for row in records}
    suites = {suite["suite_id"]:host.regression.suite_summary([by_id[cid] for cid in suite["case_ids"]], plan)
              for suite in plan["suites"]}
    aggregate = host.regression.suite_summary(records, plan)
    native_rows = [{**row, "candidate":row["native_control"]} for row in records]
    native_ids = {row["case_id"]:row for row in native_rows}
    native_suites = {suite["suite_id"]:host.regression.suite_summary([native_ids[cid] for cid in suite["case_ids"]], plan)
                     for suite in plan["suites"]}
    counts = {kind:len({route["route_id"] for route in registry if route["route_kind"]==kind})
              for kind in ("container","category")}
    peak, memory_method = host.peak_rss_bytes()
    gates = dict(all_suite_gates=all(value is True for suite in suites.values() for value in suite["gates"].values()),
        aggregate_gates=all(value is True for value in aggregate["gates"].values()),
        all_protocol_gates=all(all(row["protocol_gates"].values()) for row in records),
        all60_semantic_previews_equal=all(row["preview_comparison"]["semantic_equal"] for row in records),
        all60_native_literal_controls_exact=True,
        container_registry=counts["container"]>=plan["thresholds"]["container_route_coverage_min"],
        leaf_registry=counts["category"]>=plan["thresholds"]["leaf_route_coverage_min"],
        replay_process_memory=peak<=plan["thresholds"]["peak_memory_bytes_max"])
    passed = all(gates.values())
    write(OUTPUT / "observations.json", dict(schema_version="cp04_host_allocation_replay_observations_v1",
        frozen_plan_sha256=sha(FROZEN), records=records, new_actual_model_calls=0,
        retained_actual_model_calls=60, current_local_native_calls=len(records)))
    write(OUTPUT / "conclusion.json", dict(schema_version="cp04_host_allocation_replay_summary_v1",
        verdict="retained_order_regression_verified_only" if passed else "no_go",
        gates=gates, suites=suites, aggregate=aggregate, native_control_suites=native_suites,
        native_control_aggregate=host.regression.suite_summary(native_rows, plan),
        per_case_comparisons=[dict(case_id=row["case_id"],selected=row["candidate"]["ranking"],
            native=row["native_control"]["ranking"],literal=row["baseline"]["ranking"],
            prior_pack_survival=old["candidate"]["pack_survival"],
            current_pack_survival=row["candidate"]["pack_survival"],
            prior_positive_survived=old["candidate"]["positive_survived_count"],
            current_positive_survived=row["candidate"]["positive_survived_count"],
            positive_denominator=row["candidate"]["positive_top12_count"],
            selected_order=row["candidate"]["raw_ranked_ids"],
            native_order=row["native_control"]["raw_ranked_ids"],
            literal_order=row["baseline"]["raw_ranked_ids"])
            for row,old in zip(records,previous)],
        new_actual_model_calls=0,retained_actual_model_calls=60,current_local_native_calls=60,
        producer_peak_rss_bytes=peak,producer_peak_rss_method=memory_method,
        resource_acceptance=False, current_actual4_plus8_required=True,
        training_usefulness_acceptance=False,human_acceptance=False,promotion_ready=False))
    files = {path.relative_to(OUTPUT).as_posix():sha(path) for path in OUTPUT.rglob("*") if path.is_file()}
    write(OUTPUT / "provenance.json",dict(file_sha256=files,human_acceptance=False,promotion_ready=False))
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-check", action="store_true")
    modes.add_argument("--freeze", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--stability")
    args = parser.parse_args()
    if args.self_check:
        return self_check()
    try:
        if not args.stability:
            raise ValueError("root stability receipt required")
        plan, host = assemble(args.stability)
        cards, members, registry = host.validate_oracles(plan)
        if args.freeze:
            if FROZEN.exists() or (OUTPUT/"observations.json").exists():
                raise ValueError("existing freeze/capture preserved")
            write(FROZEN, plan)
            write(OUTPUT/"declaration.json",dict(frozen_plan_sha256=sha(FROZEN),
                source_hashes=plan["source_hashes"],input_hashes=plan["input_hashes"],
                cases=60,new_actual_model_calls=0,retained_actual_model_calls=60,
                human_acceptance=False,promotion_ready=False))
            print(json.dumps(dict(status="frozen",cases=60,new_actual_model_calls=0,plan_sha256=sha(FROZEN))))
            return 0
        if read(FROZEN.relative_to(ROOT).as_posix()) != plan:
            raise ValueError("frozen replay drift")
        if (OUTPUT/"observations.json").exists() or any(OUTPUT.glob("*/observation.json")) or any(OUTPUT.glob("*/preview-comparison.json")) or any(OUTPUT.glob("*/prepared.json")) or any(OUTPUT.glob("*/failure.json")):
            raise ValueError("complete/partial replay preserved; no automatic restart")
        return replay(plan,host,cards,members,registry)
    except (ValueError,KeyError,FileNotFoundError,FileExistsError) as error:
        print(json.dumps(dict(status="invalid_protocol",reason=str(error),new_actual_model_calls=0)))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
