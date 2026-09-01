"""Rebind a CAT-05 checkpoint after numeric-string GitHub ID normalization."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import catalog_gap_fill as gaps
import enrich_catalog as e


def migrate(run: Path):
    run = Path(run)
    plan_path = run / "plan.json"
    gap_plan_path = run / "gap-plan.json"
    evidence_path = run / "identity-type-migration.json"
    if evidence_path.exists():
        raise ValueError("Identity type migration evidence already exists")

    plan = e.load(plan_path)
    gap_plan = e.load(gap_plan_path)
    old_collector_sha = plan["collectorSha256"]
    new_collector_sha = e.sha(Path(e.__file__))
    old_plan_sha = e.sha(plan_path)
    if old_collector_sha == new_collector_sha:
        raise ValueError("Collector pin already matches; no migration required")
    if gap_plan["collectorPlanSha256"] != old_plan_sha:
        raise ValueError("Gap plan does not pin the pre-migration collector plan")

    checkpoint_before = e.load(run / "checkpoint.json")
    counters_before = {key: checkpoint_before[key] for key in ("requests", "bytes")}
    records_before = {
        path.name: e.sha(path)
        for path in sorted((run / "records").glob("*.json"))
        if not path.name.endswith(".extraction.json")
    }

    plan["collectorSha256"] = new_collector_sha
    e.atomic_json(plan_path, plan)
    gap_plan["collectorPlanSha256"] = e.sha(plan_path)
    e.atomic_json(gap_plan_path, gap_plan)

    collector = e.Collector(run)
    identities = {}
    normalized = 0
    aliases = 0
    conflicts = 0
    for record_id in collector.plan["queue"]:
        path = collector.record_path(record_id)
        if not path.exists():
            continue
        record = e.load(path)
        metadata = record.get("blocks", {}).get("metadata", {})
        identity = metadata.get("data", {}).get("githubRepositoryId")
        source = collector.source[record_id]
        if metadata.get("status") == "observed" and e.same_github_identity(
            source.get("githubRepositoryId"), identity
        ):
            previous = identities.get(str(identity))
            if previous and previous != record_id:
                record["aliasOf"] = previous
                record["status"] = "verified_identity_alias"
                aliases += 1
            else:
                record.pop("aliasOf", None)
                record = collector.normalize(record, source, record.get("curation"))
                identities[str(identity)] = record_id
                normalized += 1
        else:
            record.pop("aliasOf", None)
            record = collector.normalize(record, source, record.get("curation"))
            if record.get("values", {}).get("identityStatus") == "conflict":
                conflicts += 1
            normalized += 1
        e.atomic_json(path, record)
        collector.state["records"][record_id] = record["status"]

    collector.state["identities"] = identities
    collector.save_state()
    verification = collector.verify()
    report = gaps.GapFill(run).reports()
    checkpoint_after = e.load(run / "checkpoint.json")
    if {key: checkpoint_after[key] for key in counters_before} != counters_before:
        raise ValueError("Migration changed cumulative request or byte counters")

    result = {
        "scope": "numeric_string_repository_id_normalization_only",
        "oldCollectorSha256": old_collector_sha,
        "newCollectorSha256": new_collector_sha,
        "oldPlanSha256": old_plan_sha,
        "newPlanSha256": e.sha(plan_path),
        "requestsAndBytesPreserved": True,
        "recordsBefore": records_before,
        "recordsAfter": {
            path.name: e.sha(path)
            for path in sorted((run / "records").glob("*.json"))
            if not path.name.endswith(".extraction.json")
        },
        "normalizedRecords": normalized,
        "verifiedAliases": aliases,
        "remainingIdentityConflicts": conflicts,
        "verification": verification,
        "report": report,
    }
    e.atomic_json(evidence_path, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    with e.single_writer(args.run_dir):
        result = migrate(args.run_dir)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
