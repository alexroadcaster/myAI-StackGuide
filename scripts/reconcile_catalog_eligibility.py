"""Complete CP-03.CAT-07 identity, eligibility and category reconciliation.

The command keeps the CAT-05/06 checkpoint immutable except for cumulative GET
accounting when ``--resolve-known-ids`` is requested.  It never writes the
canonical manifest or generated HTML.  Public identity and Stars control catalog
inclusion; missing recommendation fields remain a separate downstream backlog and
never remove an otherwise eligible repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import enrich_catalog as e
from github_cli_transport import GitHubCLITransport


MINIMUM_STARS = 500
RECOMMENDATION_FIELDS = {
    "reviewStatus",
    "recommendation.whyRecommended",
    "recommendation.bestFor",
    "recommendation.tradeoffs",
    "recommendation.adoption_status",
}
TERMINAL_RESOLUTION_STATUSES = {
    "resolved_by_numeric_repository_id",
    "unavailable_by_numeric_repository_id",
    "numeric_repository_id_conflict",
}


def positive_repository_id(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.isascii() and value.isdecimal():
        parsed = int(value)
        return parsed if parsed > 0 else None
    return None


def record_file(run: Path, source_id: str) -> Path:
    return run / "records" / (hashlib.sha256(source_id.encode()).hexdigest() + ".json")


def metadata_overlay(data, observed_at, requested_id):
    observed_id = positive_repository_id(data.get("id"))
    status = "resolved_by_numeric_repository_id"
    reason = None
    if observed_id != requested_id:
        status = "numeric_repository_id_conflict"
        reason = "response_identity_does_not_match_frozen_numeric_id"
    elif data.get("private") is not False or data.get("visibility") != "public":
        status = "unavailable_by_numeric_repository_id"
        reason = "repository_is_not_confirmed_public"
    stars = data.get("stargazers_count")
    if status == "resolved_by_numeric_repository_id" and (
        not isinstance(stars, int) or isinstance(stars, bool) or stars < 0
    ):
        status = "unavailable_by_numeric_repository_id"
        reason = "repository_stars_are_not_a_valid_observation"
    result = {
        "status": status,
        "requestedRepositoryId": requested_id,
        "observedAt": observed_at,
        "reason": reason,
    }
    if status == "resolved_by_numeric_repository_id":
        result["values"] = {
            "githubRepositoryId": observed_id,
            "fullName": data.get("full_name"),
            "url": data.get("html_url"),
            "aliases": [],
            "identityStatus": "resolved",
            "availability": "available",
            "stars": stars,
            "archived": data.get("archived"),
            "visibility": data.get("visibility"),
            "defaultBranch": data.get("default_branch"),
            "language": data.get("language"),
            "description": e.clean_excerpt(data.get("description") or "") or None,
            "activity.createdAt": data.get("created_at"),
            "activity.pushedAt": data.get("pushed_at"),
        }
    return result


def resolve_known_ids(run: Path, limit: int):
    output = run / "eligibility-reconciliation"
    state_path = output / "identity-resolution.json"
    state = e.load(state_path) if state_path.exists() else {"items": {}}
    collector = e.Collector(run, GitHubCLITransport())
    source = collector.source
    pending = []
    for source_id in collector.plan["queue"]:
        record = e.load(record_file(run, source_id))
        if record.get("aliasOf") or record.get("values", {}).get("identityStatus") == "resolved":
            continue
        repository_id = positive_repository_id(source[source_id].get("githubRepositoryId"))
        if repository_id is None:
            state["items"].setdefault(source_id, {
                "status": "pending_no_frozen_numeric_repository_id",
                "requestedRepositoryId": None,
                "reason": "name_search_cannot_prove_repository_identity",
            })
            continue
        saved = state["items"].get(source_id)
        if saved and saved.get("status") in TERMINAL_RESOLUTION_STATUSES:
            continue
        pending.append((source_id, repository_id))

    before = collector.state["requests"]
    if pending:
        probe = collector.request(e.API + "/rate_limit")
        core = probe.get("data", {}).get("resources", {}).get("core", {})
        if probe.get("status") != "observed" or core.get("limit", 0) <= 60:
            raise RuntimeError("Authenticated GitHub quota was not confirmed")
        for source_id, repository_id in pending[:limit]:
            response = collector.request(e.API + "/repositories/" + str(repository_id))
            if response.get("status") == "observed":
                state["items"][source_id] = metadata_overlay(
                    response.get("data", {}), response.get("observedAt"), repository_id
                )
            else:
                state["items"][source_id] = {
                    "status": "unavailable_by_numeric_repository_id",
                    "requestedRepositoryId": repository_id,
                    "observedAt": response.get("observedAt"),
                    "reason": response.get("reason", "numeric_repository_endpoint_unavailable"),
                }
            e.atomic_json(state_path, state)
    e.atomic_json(state_path, state)
    return {
        "queuedKnownIds": len(pending),
        "attemptedKnownIds": min(len(pending), limit),
        "newTransportAttempts": collector.state["requests"] - before,
        "cumulativeTransportAttempts": collector.state["requests"],
    }


def effective_values(record, resolution, source=None):
    values = dict(record.get("values", {}))
    supplied = set()
    if resolution and resolution.get("status") == "resolved_by_numeric_repository_id":
        overlay = resolution.get("values", {})
        values.update(overlay)
        supplied.update(key for key, value in overlay.items() if value is not None)
        description = overlay.get("description")
        if isinstance(description, str) and description.strip():
            values["catalogDescription"] = description
            values["descriptionOrigin"] = "upstream"
            supplied.update({"catalogDescription", "descriptionOrigin"})
        language = overlay.get("language")
        if isinstance(language, str) and language.strip():
            values["stack"] = [{"technology": language, "evidenceRefs": ["numeric_repository_metadata"]}]
            supplied.add("stack")
    if source:
        for field in (
            "id", "fullName", "url", "catalogStatus", "primaryCategory",
            "secondaryCategories", "provenance", "language",
        ):
            if values.get(field) is None and source.get(field) is not None:
                values[field] = source[field]
                supplied.add(field)
        description = source.get("description")
        if not values.get("catalogDescription") and isinstance(description, str) and description.strip():
            values["catalogDescription"] = description
            values["descriptionOrigin"] = "upstream"
            supplied.update({"catalogDescription", "descriptionOrigin"})
    return values, supplied


def classify_root(record, resolution=None, source=None):
    values, supplied = effective_values(record, resolution, source)
    missing = sorted(set(record.get("missingMandatory", [])) - supplied)
    recommendation_gaps = sorted(field for field in missing if field in RECOMMENDATION_FIELDS)
    catalog_enrichment_gaps = sorted(field for field in missing if field not in RECOMMENDATION_FIELDS)
    stars = values.get("stars")
    result = {
        "stars": stars,
        "githubRepositoryId": positive_repository_id(values.get("githubRepositoryId")),
        "fullName": values.get("fullName"),
        "originalCatalogStatus": values.get("catalogStatus"),
        "catalogStatusChanged": False,
        "missingMandatory": missing,
        "recommendationGaps": recommendation_gaps,
        "catalogEnrichmentGaps": catalog_enrichment_gaps,
    }
    if not isinstance(stars, int) or isinstance(stars, bool):
        result.update(disposition="pending_unresolved_stars", eligible=False,
                      reasons=["stars_unknown"])
    elif stars < MINIMUM_STARS:
        result.update(disposition="excluded_below_star_threshold", eligible=False,
                      reasons=["confirmed_below_minimum_stars"])
    elif values.get("identityStatus") != "resolved" or values.get("availability") != "available":
        result.update(disposition="pending_identity_or_availability", eligible=False,
                      reasons=["identity_or_availability_unresolved"])
    elif missing:
        result.update(disposition="catalog_included_recommendation_pending", eligible=True,
                      recommendationReady=False, reasons=["recommendation_or_enrichment_backlog"])
    else:
        result.update(disposition="catalog_included_recommendation_ready", eligible=True,
                      recommendationReady=True, reasons=[])
    result.setdefault("recommendationReady", False)
    return result


def descendant_leaves(category_id, by_id, memo, visiting=None):
    if category_id in memo:
        return memo[category_id]
    visiting = set() if visiting is None else set(visiting)
    if category_id in visiting:
        raise ValueError("Taxonomy cycle detected")
    visiting.add(category_id)
    item = by_id[category_id]
    if item["kind"] == "category":
        memo[category_id] = {category_id}
        return memo[category_id]
    leaves = set()
    for child in by_id.values():
        if child.get("parent_id") == category_id:
            leaves.update(descendant_leaves(child["id"], by_id, memo, visiting))
    memo[category_id] = leaves
    return leaves


def category_counts(taxonomy, source, roots, aliases):
    by_id = {item["id"]: item for item in taxonomy["categories"]}
    leaves = {key for key, item in by_id.items() if item["kind"] == "category"}
    assignments = defaultdict(set)
    for source_id, row in source.items():
        root = aliases.get(source_id, source_id)
        if root not in roots:
            continue
        categories = [row.get("primaryCategory"), *row.get("secondaryCategories", [])]
        assignments[root].update(category for category in categories if category in leaves)
    leaf_members = {leaf: sorted(root for root in roots if leaf in assignments[root]) for leaf in sorted(leaves)}
    memo = {}
    containers = {}
    for key, item in sorted(by_id.items()):
        if item["kind"] != "container":
            continue
        descendants = descendant_leaves(key, by_id, memo)
        members = sorted({root for leaf in descendants for root in leaf_members[leaf]})
        containers[key] = {
            "label": item["label"],
            "descendantLeafIds": sorted(descendants),
            "distinctRepositoryCount": len(members),
            "repositorySourceIds": members,
        }
    leaf_rows = {
        key: {
            "label": by_id[key]["label"],
            "repositoryCount": len(members),
            "repositorySourceIds": members,
        }
        for key, members in leaf_members.items()
    }
    return {
        "thematicLeafCounts": leaf_rows,
        "containerDistinctUnions": containers,
        "emptyThematicLeaves": sorted(key for key, row in leaf_rows.items() if row["repositoryCount"] == 0),
    }


def request_log_audit(path: Path):
    phases = defaultdict(list)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            phases[item["attempt"]].append(item["phase"])
    unmatched = sorted(attempt for attempt, values in phases.items() if values != ["start", "finish"])
    return {
        "attempts": len(phases),
        "starts": sum(values.count("start") for values in phases.values()),
        "finishes": sum(values.count("finish") for values in phases.values()),
        "unmatchedAttempts": unmatched,
        "duplicatePhaseAttempts": sum(len(values) != len(set(values)) for values in phases.values()),
    }


def reconcile(run: Path):
    manifest_path = ROOT / "data" / "catalog_manifest.json"
    html_path = ROOT / "docs" / "UNIFIED_CATALOG.html"
    canonical_before = e.sha(manifest_path)
    html_before = e.sha(html_path)
    collector = e.Collector(run, lambda *_: (_ for _ in ()).throw(RuntimeError("network forbidden")))
    verification = collector.verify()
    source = collector.source
    taxonomy = e.load(run / "taxonomy.json")
    output = run / "eligibility-reconciliation"
    resolution_path = output / "identity-resolution.json"
    resolutions = e.load(resolution_path).get("items", {}) if resolution_path.exists() else {}

    records = {source_id: e.load(record_file(run, source_id)) for source_id in collector.plan["queue"]}
    aliases = {}
    for source_id, record in records.items():
        if record.get("aliasOf"):
            aliases[source_id] = record["aliasOf"]

    numeric_roots = {}
    for source_id, record in records.items():
        if source_id in aliases:
            continue
        values, _ = effective_values(record, resolutions.get(source_id), source[source_id])
        repository_id = positive_repository_id(values.get("githubRepositoryId"))
        if repository_id is None:
            continue
        previous = numeric_roots.get(repository_id)
        if previous and previous != source_id:
            previous_observed = records[previous].get("values", {}).get("identityStatus") == "resolved"
            current_observed = record.get("values", {}).get("identityStatus") == "resolved"
            if previous_observed and not current_observed:
                aliases[source_id] = previous
            elif current_observed and not previous_observed:
                aliases[previous] = source_id
                numeric_roots[repository_id] = source_id
            else:
                raise ValueError("Duplicate primary numeric identity without a unique observed root")
        else:
            numeric_roots[repository_id] = source_id

    for alias, target in list(aliases.items()):
        seen = {alias}
        while target in aliases:
            if target in seen:
                raise ValueError("Alias cycle detected")
            seen.add(target)
            target = aliases[target]
        aliases[alias] = target

    root_decisions = {}
    for source_id, record in records.items():
        if source_id not in aliases:
            root_decisions[source_id] = classify_root(record, resolutions.get(source_id), source[source_id])

    row_decisions = []
    for source_id in collector.plan["queue"]:
        if source_id in aliases:
            target = aliases[source_id]
            target_decision = root_decisions[target]
            row_decisions.append({
                "sourceId": source_id,
                "disposition": "consolidated_verified_alias",
                "eligibleAsDistinctRepository": False,
                "canonicalSourceId": target,
                "canonicalDisposition": target_decision["disposition"],
                "reason": "same_verified_numeric_github_identity",
            })
        else:
            row_decisions.append({"sourceId": source_id, "canonicalSourceId": source_id, **root_decisions[source_id]})

    excluded = sorted(key for key, row in root_decisions.items() if row["disposition"] == "excluded_below_star_threshold")
    replacement_path = run / "semantic-review" / "decisions" / "replacement-decisions.json"
    replacement_items = e.load(replacement_path)["items"]
    replacement_by_source = {item["sourceId"]: item for item in replacement_items}
    if set(excluded) != set(replacement_by_source):
        raise ValueError("Every below-threshold exclusion must have exactly one CAT-06 replacement decision")
    replacements = []
    for source_id in excluded:
        item = replacement_by_source[source_id]
        accepted = [candidate for candidate in item.get("candidates", []) if candidate.get("decision") == "accepted_qualified_replacement"]
        if accepted:
            raise ValueError("Accepted replacements require a separately collected complete card")
        replacements.append({
            "excludedSourceId": source_id,
            "decision": "unresolved_vacancy_no_qualified_replacement",
            "candidateLeadsReviewed": len(item.get("candidates", [])),
            "acceptedReplacement": None,
            "nextAction": item.get("nextAction"),
        })

    eligible_roots = {key for key, row in root_decisions.items() if row["eligible"]}
    counts = category_counts(taxonomy, source, eligible_roots, aliases)
    disposition_counts = Counter(row["disposition"] for row in root_decisions.values())
    row_disposition_counts = Counter(row["disposition"] for row in row_decisions)
    canonical_names = {}
    canonical_urls = {}
    for source_id in root_decisions:
        values, _ = effective_values(records[source_id], resolutions.get(source_id), source[source_id])
        for field, registry in (("fullName", canonical_names), ("url", canonical_urls)):
            value = values.get(field)
            if not isinstance(value, str) or not value.strip():
                continue
            normalized = value.strip().casefold().rstrip("/")
            previous = registry.get(normalized)
            if previous and previous != source_id:
                raise ValueError(f"Duplicate canonical {field}: {previous} and {source_id}")
            registry[normalized] = source_id
    if any(root_decisions[key]["stars"] < MINIMUM_STARS for key in eligible_roots):
        raise ValueError("Eligible set contains a below-threshold repository")
    recommendation_backlog = Counter(
        field for key in eligible_roots for field in root_decisions[key]["recommendationGaps"]
    )
    catalog_enrichment_backlog = Counter(
        field for key in eligible_roots for field in root_decisions[key]["catalogEnrichmentGaps"]
    )

    e.atomic_json(output / "decisions.json", {"items": row_decisions})
    e.atomic_json(output / "identity-alias-map.json", {
        "aliases": [{"sourceId": key, "canonicalSourceId": aliases[key]} for key in sorted(aliases)]
    })
    e.atomic_json(output / "replacement-reconciliation.json", {"items": replacements})
    e.atomic_json(output / "category-counts.json", counts)
    summary = {
        "scope": "cat07_identity_stars_catalog_inclusion_and_recommendation_readiness_reconciliation",
        "sourceRows": len(records),
        "distinctCanonicalIdentities": len(root_decisions),
        "verifiedAliasesConsolidated": len(aliases),
        "duplicateCanonicalIdentities": 0,
        "identityResolutionCounts": dict(sorted(Counter(
            item.get("status", "missing_resolution_status") for item in resolutions.values()
        ).items())),
        "rootDispositions": dict(sorted(disposition_counts.items())),
        "sourceRowDispositions": dict(sorted(row_disposition_counts.items())),
        "catalogIncludedRepositories": len(eligible_roots),
        "catalogIncludedSourceIds": sorted(eligible_roots),
        "recommendationReadyRepositories": sum(
            row["recommendationReady"] for row in root_decisions.values()
        ),
        "recommendationPendingRepositories": sum(
            row["disposition"] == "catalog_included_recommendation_pending"
            for row in root_decisions.values()
        ),
        "recommendationBacklogFields": dict(sorted(recommendation_backlog.items())),
        "catalogEnrichmentBacklogFields": dict(sorted(catalog_enrichment_backlog.items())),
        "minimumStars": MINIMUM_STARS,
        "belowThresholdExceptions": 0,
        "unresolvedReplacementVacancies": len(replacements),
        "replacementCandidateLeadsReviewed": sum(item["candidateLeadsReviewed"] for item in replacements),
        "replacementCandidatesAccepted": 0,
        "thematicLeaves": len(counts["thematicLeafCounts"]),
        "navigationContainers": len(counts["containerDistinctUnions"]),
        "emptyThematicLeaves": len(counts["emptyThematicLeaves"]),
        "catalogIncludedDirectPlacements": sum(
            row["repositoryCount"] for row in counts["thematicLeafCounts"].values()
        ),
        "collectorVerification": verification,
        "cumulativeTransportAttempts": collector.state["requests"],
        "requestLogAudit": request_log_audit(run / "request-log.jsonl"),
        "canonicalManifestSha256": canonical_before,
        "canonicalManifestUnchanged": canonical_before == e.sha(manifest_path),
        "canonicalHtmlSha256": html_before,
        "canonicalHtmlUnchanged": html_before == e.sha(html_path),
        "canonicalWritten": False,
        "catalogStatusChanged": False,
        "evidenceLimits": [
            "Catalog inclusion proves only public identity and the configured Stars gate.",
            "Recommendation fields are a downstream readiness backlog and never remove a repository from the catalog.",
            "Alias consolidation requires the same observed GitHub numeric repository identity.",
            "Records without a frozen numeric identity remain pending when the saved owner/name endpoint is unavailable.",
            "Recommendation-pending records are not product, security or code-quality judgments.",
            "No canonical source, generated HTML, browser or release claim is made.",
        ],
    }
    e.atomic_json(output / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--resolve-known-ids", action="store_true")
    parser.add_argument("--max-resolutions", type=int, default=20)
    args = parser.parse_args()
    if args.max_resolutions < 1 or args.max_resolutions > 20:
        parser.error("--max-resolutions must be between 1 and 20")
    run = args.run_dir.resolve()
    if args.resolve_known_ids:
        with e.single_writer(run):
            resolution = resolve_known_ids(run, args.max_resolutions)
        print(json.dumps(resolution, ensure_ascii=False))
    reconcile(run)


if __name__ == "__main__":
    main()
