"""Offline CP-11 observation validation; never calls retrieval or a model.

Hashes establish consistency, not trace authenticity or recommendation quality.
The observed envelope is separate from the unchanged synthetic-only C8 registry.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

import evaluate_retrieval as scoring

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "plugins/myai-stackguide/assets"
SOURCE_PATHS = tuple("plugins/myai-stackguide/scripts/" + name + ".py" for name in (
    "intake", "session_recommendation", "state_store", "scanner", "context",
    "recommendation_request", "request_guard", "retrieval", "context_pack", "matcher", "render_report")) + tuple(
    "plugins/myai-stackguide/assets/" + name for name in (
    "catalog.search-manifest.json", "catalog.search.sqlite", "catalog.snapshot.json", "retrieval-policy.json", "status-template.html", "session-contracts.json")) + (
    "scripts/build_session_contracts.py",
    "evals/plugin-v1/evaluate_retrieval.py",
    "evals/plugin-v1/evaluate_vertical_slice.py", "evals/vertical-slice-result.schema.json", "tests/test_plugin_vertical_slice.py")
require = scoring.require
_MATCHER_SPEC = importlib.util.spec_from_file_location("cp11_offline_matcher", ROOT / "plugins/myai-stackguide/scripts/matcher.py")
MATCHER = importlib.util.module_from_spec(_MATCHER_SPEC)
_MATCHER_SPEC.loader.exec_module(MATCHER)


def source_bindings():
    return {name: scoring.file_sha256(ROOT / name) for name in SOURCE_PATHS}


def check_sources(bindings):
    """Validate exact current production/assets provenance."""
    require(bindings == source_bindings(), "source bindings changed or incomplete")


def check_pins(observation, manifest):
    """Keep one canonical package tuple across request, result and pack."""
    require(all(observation[key]["pins"] == manifest["pins"]
                for key in ("retrieval", "evidence_pack")), "capture pins mismatch")


def validate_public_entry(entry, query, cards):
    """Use source-owned actual provenance; never rewrite it as synthetic C8 data."""
    card = entry["card"]
    require(card == cards.get(card["identity"]["github_repository_id"]), "public card source mismatch")
    require(MATCHER.match_candidate(card, query) == entry["eligibility"], "source card eligibility mismatch")


def check_lifecycle(events):
    """Validate saved/published revision associations."""
    expected = ["start", "answer", "commit-scan", "commit-context", "commit-matching", "commit-memo",
                "correct", "retry-publication", "commit-matching", "commit-memo", "finalize", "start"]
    require([event["command"] for event in events] == expected, "incomplete lifecycle command trace")
    previous = None
    for event in events:
        response = event["response"]
        saved = response["saved"]
        require(response["publication_status"] == "current" and response["failure_reason"] is None,
                "lifecycle publication failure")
        require(saved == response["current"] and all(response["published"][key] == value
                for key, value in saved.items()), "publication revision mismatch")
        require(response["render_attempts"] == 1 and response["retry"] == "none", "publication retry trace")
        if previous and event["command"] != "start":
            step = 0 if event["command"] == "retry-publication" else 1
            require(saved["run_id"] == previous["run_id"] and saved["revision"] == previous["revision"] + step,
                    "lifecycle revision discontinuity")
        previous = saved


def evaluate(capture_path, case_path):
    capture_path, case_path = Path(capture_path), Path(case_path)
    data, case = scoring.load_json(capture_path), scoring.load_json(case_path)
    contracts = scoring.Contracts()
    schema = scoring.load_json(ROOT / "evals/vertical-slice-result.schema.json")
    try:
        contracts.validator_type(schema, registry=contracts.registry, format_checker=contracts.checker).validate(data)
    except Exception as error:
        raise ValueError("observed capture schema rejected") from error
    require(data["case_id"] == case["case_id"] and data["case_sha256"] == scoring.file_sha256(case_path), "case source binding")
    check_sources(data["source_sha256"])
    manifest = scoring.load_json(ASSETS / "catalog.search-manifest.json")
    require(data["manifest"] == manifest, "manifest source binding")
    require(all(manifest["pins"][key] == value for key, value in case["expected"]["pins"].items()), "scenario source pins")
    for name, pin in (("catalog.snapshot.json", "cards_sha256"), ("catalog.search.sqlite", "index_sha256"), ("retrieval-policy.json", "policy_sha256")):
        require(scoring.file_sha256(ASSETS / name) == manifest["pins"][pin], "physical public source hash")
    check_lifecycle(data["lifecycle"])
    snapshot = scoring._load_json_bounded(ASSETS / "catalog.snapshot.json", 64 * 1024 * 1024)
    cards = {card["identity"]["github_repository_id"]: card for card in snapshot["cards"]}
    records = []
    for observation in data["captures"]:
        check_pins(observation, manifest)
        request, brief = observation["request"], observation["brief"]
        memo, pack = observation["memo"], observation["evidence_pack"]
        require(request["run_id"] == brief["run_id"] == memo["run_id"] and request["brief_id"] == brief["brief_id"] and request["brief_version"] == memo["brief_version"] == brief["brief_version"], "request/memo Brief join")
        require(request["pack_id"] == pack["pack_id"] == memo["pack_id"] and request["request_id"] == memo["request_id"] and memo["pins"] == manifest["pins"], "request/memo pins join")
        require(observation["brief_sha256"] == scoring.digest(brief) and observation["query_sha256"] == scoring.digest(request["query"]), "canonical source digest")
        measures = dict(brief_bytes=observation["bytes"]["brief"], targeted_context_bytes=0,
            request_bytes=observation["bytes"]["request"], evidence_pack_bytes=observation["bytes"]["pack"],
            latency_ms=None, latency_method=None, peak_memory_bytes=None, memory_method=None, input_tokens=None, tokenizer=None)
        measures["plugin_input_bytes"] = sum(measures[key] for key in ("brief_bytes", "targeted_context_bytes", "request_bytes", "evidence_pack_bytes"))
        for label, value in (("brief", brief), ("request", request), ("pack", observation["evidence_pack"]), ("memo", observation["memo"])):
            require(observation["bytes"][label] == len(scoring.canonical(value)), "capture byte binding")
        scoring.validate_capture(dict(query=request["query"], index_manifest=manifest, run_id=brief["run_id"]),
                                 dict(observation, measurements=measures), contracts,
                                 card_validator=lambda entry, query: validate_public_entry(entry, query, cards))
        require(any("repository_fts MATCH" in sql and "bm25(" in sql for sql in observation["sql_route"]), "SQL route observation missing")
        for entry in observation["evidence_pack"]["cards"]:
            require(entry["card"] == cards[entry["card"]["identity"]["github_repository_id"]], "public card source mismatch")
        records.append(dict(brief_version=brief["brief_version"], query_sha256=observation["query_sha256"],
                            ids=[row["github_repository_id"] for row in observation["retrieval"]["candidates"]]))
        require(records[-1]["ids"] == [case["expected"]["github_repository_id"]], "scenario numeric identity mismatch")
    final = scoring.load_json(capture_path.parent / "docs/myai-stackguide/state.json")
    successor = scoring.load_json(capture_path.parent / "successor-state.json")
    for state in (final, successor):
        contracts.validate("artifact/project-artifact-state.schema.json", state)
    for state, event in ((final, data["lifecycle"][-2]), (successor, data["lifecycle"][-1])):
        require(all(state[key] == value for key, value in event["response"]["saved"].items()), "state/lifecycle revision association")
    require(final["status"] == "finalized" and successor["predecessor_run_id"] == final["run_id"] and successor["history"] == final["history"], "History predecessor association")
    history_name = f"docs/myai-stackguide/runs/{final['run_id']}.json"
    expected_artifacts = {"docs/myai-stackguide/state.json", "docs/myai-stackguide/status.html", history_name, "successor-state.json"}
    require(set(data["artifact_sha256"]) == expected_artifacts, "artifact source allowlist")
    for name, expected_hash in data["artifact_sha256"].items():
        require(scoring.file_sha256(capture_path.parent / name) == expected_hash, "artifact source hash mismatch")
    require((capture_path.parent / history_name).read_bytes() == scoring.canonical(final), "immutable History bytes")
    require(data["history_sha256"] == data["artifact_sha256"][history_name] and data["html_sha256"] == data["artifact_sha256"]["docs/myai-stackguide/status.html"], "History/HTML digest binding")
    for key in ("request", "retrieval", "evidence_pack", "memo", "brief"):
        require(final[key] == data["captures"][-1][key], "final capture association")
    require([item["brief_version"] for item in records] == [1, 2], "correction Brief versions")
    return dict(schema_version="cp11_vertical_slice_verdict_v1", verdict="local_lifecycle_compatibility_only",
                passed=True, promotion_ready=False, quality_observed=False, records=records,
                case_sha256=data["case_sha256"], capture_sha256=scoring.file_sha256(capture_path),
                c8_schema_set_sha256=contracts.schema_set_sha256)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", required=True)
    parser.add_argument("--case", required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(evaluate(args.capture, args.case), ensure_ascii=False))
        return 0
    except (ValueError, RuntimeError, OSError, KeyError, TypeError):
        print(json.dumps(dict(verdict="invalid_capture", passed=False, promotion_ready=False)))
        return 2


if __name__ == "__main__":
    sys.exit(main())
