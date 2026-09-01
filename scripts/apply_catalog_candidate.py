"""Apply the frozen CAT-07/CAT-07A evidence to the canonical catalog transactionally."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_catalog_html as html_builder  # noqa: E402
import reconcile_catalog_eligibility as eligibility  # noqa: E402


MANIFEST = ROOT / "data" / "catalog_manifest.json"
HTML = ROOT / "docs" / "UNIFIED_CATALOG.html"
TEMPLATE = ROOT / "templates" / "unified_catalog.html"
GAP_RUN = ROOT / ".codex-tmp" / "catalog-refresh" / "gaps"
EXPANSION_FINAL = ROOT / ".codex-tmp" / "catalog-refresh" / "cat-07a" / "final"
DEFAULT_RUN = ROOT / ".codex-tmp" / "catalog-refresh" / "cat-08"
CANONICAL_WRITE_LOCK = html_builder.CANONICAL_WRITE_LOCK

INPUTS = {
    "manifest": (MANIFEST, "f90b6b4540ff263df7fe624b34f5f2eb4306cf5309b9e2e6e9604335614dcff1"),
    "manifestSchema": (
        ROOT / "data" / "catalog_manifest.schema.json",
        "2264afd29aa61c440fa075b430012a3aeae911425ac47ebe4b82cb13a40f0583",
    ),
    "taxonomy": (
        ROOT / "specs" / "catalog" / "taxonomy.yaml",
        "7f74561ff8206d1fb6782e7815ebb7c8080ae813f303fabfd6c9c72d8cbbaaec",
    ),
    "taxonomyRules": (
        ROOT / "specs" / "catalog" / "taxonomy-rules.md",
        "efe0ce87a3804a5fb7c6a1ff5d63224ec2656f901472b4e905dfb8dbc0fc5f0a",
    ),
    "eligibilityDecisions": (
        GAP_RUN / "eligibility-reconciliation" / "decisions.json",
        "8f0355f5d55786acbfb84cd6a1c7845f9c4310102666a1fab28086ef142ec441",
    ),
    "identityAliases": (
        GAP_RUN / "eligibility-reconciliation" / "identity-alias-map.json",
        "30803f5ad496ac8ee66d7eaaa48a5af258526ab2c5a7fa7500328d79af983574",
    ),
    "identityResolution": (
        GAP_RUN / "eligibility-reconciliation" / "identity-resolution.json",
        "820b996cafe7f022819cbdf0e85dffe07acabdae090ea0518a13f1add80736c0",
    ),
    "gapPatches": (
        GAP_RUN / "gap-reports" / "patches.json",
        "f93ac416ff9a9cf6069072390d97a8a3a79f26541bf2f151fa8c576e8a9996fc",
    ),
    "semanticDecisions": (
        GAP_RUN / "semantic-review" / "decisions" / "semantic-decisions.json",
        "cd060adba1ae9da8b25505537d30863323fc223feebf2c72a098fedc19db681c",
    ),
    "semanticDecisionSummary": (
        GAP_RUN / "semantic-review" / "decisions" / "summary.json",
        "d7497a4a89d21cc68b1af506c7a169376cb9b549707a8103b16f59f11f907ec0",
    ),
    "eligibilitySummary": (
        GAP_RUN / "eligibility-reconciliation" / "summary.json",
        "a36e94de2b4a78b619eda764001a275fe65c23554d8ab05341b88e07e7d722ee",
    ),
    "expansionCandidate": (
        EXPANSION_FINAL / "validated-expansion-candidate.json",
        "780f72833a696954bcffa8f62169686337331dd9cdfba72b9cc9dfb14b4a3422",
    ),
    "expansionCategoryCounts": (
        EXPANSION_FINAL / "category-counts.json",
        "7816fb4de5f0f790c13d46e2b4fe1e5633de5322ef9e5380772563df3832cc7b",
    ),
    "expansionSummary": (
        EXPANSION_FINAL / "summary.json",
        "c4560c0c1eb4c03a17ddae2dda5f4bc1952e236a92b7f421eebae1c010328f4e",
    ),
    "template": (TEMPLATE, "8e6e34867196a369a0c1e4d81bb871025e3c484f34cbcad51b8ee1fbb2183100"),
    "htmlBefore": (HTML, "926a902cb3557bc674d1dc41511916742d4ce5c4cc100345b41a0d57f411bda6"),
}

BASELINE_RECORD_TREE_SHA256 = "1aef6a81d66f2b5e6645b8aaa2b215198ba61abd23746668ff5b6d9fb8bb2973"
ACCEPTED_CURATION_TREE_SHA256 = "40fd450eccf8024944b7dba8478b0230d38c3cd8ff899de74e0c0b95322cded5"
TEMPLATE_BEFORE_SHA256 = "6326454467827d4c21d1effdb5c4009d018d1a22b2812d52df7d57b3d86c8136"
MANIFEST_SCHEMA_BEFORE_SHA256 = "97964dd1440d6a4604eeeb914205f18dc0b3f9b3e1809a17399048343c930303"

REVIEW_REASSIGNMENTS = {
    "gh:deepseek-ai/deepseek-harness": "agent_runtime_orchestration",
    "gh:hkuds/deeptutor": "rag_knowledge_apps",
    "gh:liyupi/yu-ai-agent": "learning_reference_resources",
}

REVIEW_SOURCE_IDS = {
    "gh-1500:corentinth/it-tools",
    "gh-1500:date-fns/date-fns",
    "gh-1500:ethereum/go-ethereum",
    "gh-1500:heyputer/puter",
    "gh-1500:lodash/lodash",
    "gh-1500:raphire/win11debloat",
    "gh-1500:zen-browser/desktop",
    "gh-1700:joooook/12306-mcp",
    "gh-pending:jacob-bd/notebooklm-mcp-cli",
    "gh:bitcoin/bitcoin",
    "gh:deepseek-ai/deepseek-harness",
    "gh:hkuds/deeptutor",
    "gh:homeassistant-ai/ha-mcp",
    "gh:liyupi/yu-ai-agent",
    "gh:torvalds/linux",
}

IDENTITY_VALUE_FIELDS = (
    "githubRepositoryId",
    "identityStatus",
    "availability",
    "watchersScope",
    "evidenceCompleteness",
    "fieldObservations",
    "eligibility",
)


class CandidateApplicationError(ValueError):
    """Raised when the frozen candidate cannot be applied safely."""


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def tree_sha(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(ROOT).as_posix()):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return html_builder.canonical_json(value).encode("utf-8")


def nested_value(item: dict[str, Any], field: str) -> Any:
    value: Any = item
    for part in field.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def set_nested_value(item: dict[str, Any], field: str, value: Any) -> None:
    parts = field.split(".")
    target = item
    for part in parts[:-1]:
        existing = target.get(part)
        if not isinstance(existing, dict):
            existing = {}
            target[part] = existing
        target = existing
    target[parts[-1]] = copy.deepcopy(value)


def apply_sparse_overlays(
    source: dict[str, Any],
    edits: list[dict[str, Any]],
    semantic_fields: dict[str, Any],
) -> dict[str, Any]:
    card = copy.deepcopy(source)
    for edit in edits:
        observed = nested_value(card, edit["field"])
        if observed != edit.get("before"):
            raise CandidateApplicationError(
                f"sparse patch before mismatch: {edit['sourceId']} {edit['field']}"
            )
        set_nested_value(card, edit["field"], edit.get("after"))
    for field, value in semantic_fields.items():
        observed = nested_value(card, field)
        if observed not in (None, value):
            raise CandidateApplicationError(
                f"semantic overlay conflicts with sparse/source value: {source['id']} {field}"
            )
        set_nested_value(card, field, value)
    return card


def record_path(source_id: str) -> Path:
    name = hashlib.sha256(source_id.encode("utf-8")).hexdigest() + ".json"
    return GAP_RUN / "records" / name


def verify_pins(*, require_pre_apply: bool = True) -> dict[str, str]:
    result = {}
    for name, (path, expected) in INPUTS.items():
        if not path.exists():
            raise CandidateApplicationError(f"missing pinned input: {path}")
        observed = sha(path)
        if observed != expected and (require_pre_apply or name not in {"manifest", "htmlBefore"}):
            raise CandidateApplicationError(f"pinned input changed: {name}")
        result[name] = observed
    return result


def _merge_unique(values: list[Any]) -> list[Any]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _merge_unique_aliases(values: Any) -> list[str]:
    result = []
    seen = set()
    for value in values:
        normalized = value.strip().casefold()
        if normalized not in seen:
            seen.add(normalized)
            result.append(value.strip())
    return result


def _apply_license(card: dict[str, Any], values: dict[str, Any]) -> None:
    license_value = copy.deepcopy(card.get("license") or {})
    for suffix in ("spdx", "name", "source", "confidence"):
        key = f"license.{suffix}"
        if key in values:
            license_value[suffix] = values[key]
    if license_value:
        card["license"] = license_value


def _apply_activity(card: dict[str, Any], values: dict[str, Any]) -> None:
    activity_value = copy.deepcopy(card.get("activity") or {})
    for key, value in values.items():
        if key.startswith("activity."):
            activity_value[key.removeprefix("activity.")] = copy.deepcopy(value)
    if activity_value:
        card["activity"] = activity_value


def normalize_baseline_card(
    source: dict[str, Any],
    values: dict[str, Any],
    alias_source_ids: list[str],
    aliases_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    card = copy.deepcopy(source)
    stable_id = source["id"]
    historical_full_name = source.get("fullName")
    for field in IDENTITY_VALUE_FIELDS:
        if field in values:
            card[field] = copy.deepcopy(values[field])
    for field in ("fullName", "url"):
        if isinstance(values.get(field), str) and values[field].strip():
            card[field] = values[field]
    observed_stars = values.get("stars")
    if (
        isinstance(observed_stars, int)
        and not isinstance(observed_stars, bool)
        and observed_stars >= 500
        and (
            not isinstance(card.get("stars"), int)
            or isinstance(card.get("stars"), bool)
            or card["stars"] < 500
        )
    ):
        card["stars"] = observed_stars
        card.setdefault("evidence", {})["cat08StarsCorrection"] = {
            "status": "observed",
            "reason": "replace_stale_or_invalid_pre_cat07_value_for_strict_membership_gate",
            "recordSha256": sha(record_path(stable_id)),
        }
    if "activity.observedAt" in values:
        card.setdefault("activity", {})["observedAt"] = values["activity.observedAt"]

    observed_aliases = card.get("aliases") if isinstance(card.get("aliases"), list) else []
    catalog_alias_names = [
        value
        for alias_id in alias_source_ids
        for value in (
            aliases_by_id.get(alias_id, {}).get("fullName"),
            alias_id.partition(":")[2],
        )
        if isinstance(value, str) and "/" in value
    ]
    stable_source_name = stable_id.partition(":")[2]
    alias_candidates = [*observed_aliases, historical_full_name, stable_source_name, *catalog_alias_names]
    canonical_name = card["fullName"].casefold()
    card["aliases"] = _merge_unique_aliases(
        value
        for value in alias_candidates
        if isinstance(value, str) and value.strip() and value.casefold() != canonical_name
    )
    existing_source_ids = card.get("sourceRecordIds") if isinstance(card.get("sourceRecordIds"), list) else []
    card["sourceRecordIds"] = _merge_unique([stable_id, *alias_source_ids, *existing_source_ids])
    canonical_assignments = [card["primaryCategory"], *card.get("secondaryCategories", [])]
    alias_assignments = [
        category
        for alias_id in alias_source_ids
        if alias_id in aliases_by_id
        for category in [
            aliases_by_id[alias_id]["primaryCategory"],
            *aliases_by_id[alias_id].get("secondaryCategories", []),
        ]
    ]
    thematic_assignments = _merge_unique(
        category
        for category in [*canonical_assignments, *alias_assignments]
        if category != "uncategorized_review"
    )
    if thematic_assignments:
        primary = card["primaryCategory"] if card["primaryCategory"] != "uncategorized_review" else thematic_assignments[0]
        card["primaryCategory"] = primary
        card["secondaryCategories"] = [category for category in thematic_assignments if category != primary]
    else:
        card["primaryCategory"] = "uncategorized_review"
        card["secondaryCategories"] = []
    old_provenance = copy.deepcopy(source.get("provenance") or {})
    old_provenance["cat07Refresh"] = copy.deepcopy(values.get("provenance") or {})
    old_provenance["identityCatalogStatuses"] = {
        stable_id: source.get("catalogStatus"),
        **{
            alias_id: aliases_by_id[alias_id].get("catalogStatus")
            for alias_id in alias_source_ids
            if alias_id in aliases_by_id
        },
    }
    card["provenance"] = old_provenance
    alias_statuses = [
        aliases_by_id[alias_id].get("catalogStatus")
        for alias_id in alias_source_ids
        if alias_id in aliases_by_id
    ]
    if card.get("catalogStatus") != "accepted" and "accepted" in alias_statuses:
        card["catalogStatus"] = "accepted"
    card["id"] = stable_id
    card["eligibility"] = copy.deepcopy(card.get("eligibility") or {})
    card["eligibility"]["globalCAT07Applied"] = True
    return card


def normalize_addition_card(source: dict[str, Any]) -> dict[str, Any]:
    card = copy.deepcopy(source)
    eligibility_value = copy.deepcopy(card.get("eligibility") or {})
    eligibility_value["globalCAT07AApplied"] = True
    card["eligibility"] = eligibility_value
    provenance = copy.deepcopy(card.get("provenance") or {})
    provenance["canonicalApplication"] = {
        "task": "CP-03.CAT-08",
        "date": "2026-09-01",
        "candidateSha256": INPUTS["expansionCandidate"][1],
    }
    card["provenance"] = provenance
    card.setdefault("form", "unknown")
    card.setdefault("deployment", ["unknown"])
    card.setdefault("hosting", "unknown")
    card.setdefault("difficulty", "unknown")
    card.setdefault("lifecycle", "unknown")
    card.setdefault("persona", "unknown")
    card.setdefault("productionEligible", None)
    card.setdefault("activity", {})
    card["activity"].setdefault("activityBand", "unknown")
    return card


def review_decisions(repositories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {item["id"]: item for item in repositories}
    if set(by_id) & REVIEW_SOURCE_IDS != REVIEW_SOURCE_IDS:
        missing = sorted(REVIEW_SOURCE_IDS - set(by_id))
        raise CandidateApplicationError(f"review identities missing from candidate: {missing}")
    result = []
    for source_id in sorted(REVIEW_SOURCE_IDS):
        repository = by_id[source_id]
        if repository.get("primaryCategory") != "uncategorized_review":
            raise CandidateApplicationError(f"unreviewed category mutation for {source_id}")
        category = REVIEW_REASSIGNMENTS.get(source_id, "uncategorized_review")
        if category != "uncategorized_review":
            repository["primaryCategory"] = category
            repository["secondaryCategories"] = []
            decision = "assigned_existing_leaf"
            reason = "Saved CAT-07 metadata and README evidence directly establish the existing functional leaf."
            evidence_refs = ["blocks.metadata", "blocks.readme", "specs/catalog/taxonomy.yaml"]
        else:
            decision = "retained_review"
            reason = "No saved CAT-07 evidence establishes one existing thematic leaf strongly enough for canonical reassignment."
            evidence_refs = ["blocks.metadata", "semantic-review/decisions/semantic-decisions.json", "specs/catalog/taxonomy.yaml"]
        decision_item = {
            "sourceId": source_id,
            "fullName": repository["fullName"],
            "decision": decision,
            "category": category,
            "evidenceRefs": evidence_refs,
            "reason": reason,
            "evidenceArtifacts": {
                "record": str(record_path(source_id).relative_to(ROOT)).replace("\\", "/"),
                "recordSha256": sha(record_path(source_id)),
                "semanticDecisions": str(INPUTS["semanticDecisions"][0].relative_to(ROOT)).replace("\\", "/"),
                "semanticDecisionsSha256": INPUTS["semanticDecisions"][1],
            },
        }
        repository.setdefault("classification", {})["cat08Review"] = copy.deepcopy(decision_item)
        result.append(decision_item)
    return result


def rebuild_taxonomy(
    categories: list[dict[str, Any]], repositories: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    result = copy.deepcopy(categories)
    by_key = {item["key"]: item for item in result}
    assignments: dict[str, list[str]] = {}
    placements = []
    for repository in repositories:
        assigned = [repository["primaryCategory"], *repository.get("secondaryCategories", [])]
        if len(assigned) != len(set(assigned)):
            raise CandidateApplicationError(f"duplicate category assignment: {repository['id']}")
        for category in assigned:
            node = by_key.get(category)
            if node is None or node.get("kind") == "container":
                raise CandidateApplicationError(f"invalid category assignment: {repository['id']} -> {category}")
        assignments[repository["id"]] = assigned
        source = "cat07a-expansion" if repository["id"].startswith("gh-expansion:") else "cat08-canonical-reconciliation"
        placements.extend(
            {"repoKey": repository["fullName"], "categoryKey": category, "source": source}
            for category in assigned
        )

    direct_members = defaultdict(list)
    for repository in repositories:
        for category in assignments[repository["id"]]:
            direct_members[category].append(repository["id"])
    for node in result:
        node["repoIds"] = sorted(direct_members[node["key"]])
        if node.get("kind") == "container":
            children = {item["key"] for item in result if item.get("parentId") == node["key"]}
            node["descendantRepoIds"] = sorted(
                repository["id"]
                for repository in repositories
                if any(category in children for category in assignments[repository["id"]])
            )
        else:
            node.pop("descendantRepoIds", None)
    return result, placements


def _recommendation_complete(repository: dict[str, Any]) -> bool:
    value = repository.get("recommendation")
    if not isinstance(value, dict):
        return False
    return all(value.get(field) for field in ("whyRecommended", "bestFor", "tradeoffs", "adoption_status"))


def recompute_summary(payload: dict[str, Any]) -> dict[str, Any]:
    repositories = payload["repositories"]
    status = Counter(item["catalogStatus"] for item in repositories)
    review_count = sum(item["primaryCategory"] == "uncategorized_review" for item in repositories)
    thematic_placements = sum(
        category != "uncategorized_review"
        for item in repositories
        for category in [item["primaryCategory"], *item.get("secondaryCategories", [])]
    )
    recommendation_complete = sum(_recommendation_complete(item) for item in repositories)
    return {
        "canonicalRepositories": len(repositories),
        "accepted": status["accepted"],
        "candidates": status["candidate"],
        "referenceOrBenchmark": status["reference"] + status["benchmark"],
        "categories": len(payload["categories"]),
        "placements": len(payload["placements"]),
        "activityEnriched": sum((item.get("activity") or {}).get("status") == "enriched" for item in repositories),
        "stackRecipes": len(payload["stackRecipes"]),
        "compatibilityEdges": len(payload["compatibility"]),
        "recommendationRationaleStored": recommendation_complete,
        "recommendationPending": len(repositories) - recommendation_complete,
        "thematicCategories": sum(item.get("kind") == "category" for item in payload["categories"]),
        "navigationContainers": sum(item.get("kind") == "container" for item in payload["categories"]),
        "reviewRepositories": review_count,
        "thematicRepositories": len(repositories) - review_count,
        "thematicPlacements": thematic_placements,
    }


def build_candidate() -> tuple[dict[str, Any], dict[str, Any]]:
    verify_pins()
    manifest = html_builder.load_manifest(MANIFEST)
    expansion = load(INPUTS["expansionCandidate"][0])
    final_counts = load(INPUTS["expansionCategoryCounts"][0])
    decisions = load(INPUTS["eligibilityDecisions"][0])["items"]
    resolutions = load(INPUTS["identityResolution"][0]).get("items", {})
    alias_items = load(INPUTS["identityAliases"][0])["aliases"]
    sparse_edits = load(INPUTS["gapPatches"][0])["edits"]
    semantic_items = load(INPUTS["semanticDecisions"][0])["items"]

    base_ids = expansion.get("baseIncludedSourceIds", [])
    additions = expansion.get("acceptedAdditions", [])
    overflow = expansion.get("qualifiedOverflow", [])
    if len(base_ids) != 1624 or len(additions) != 876 or len(overflow) != 7:
        raise CandidateApplicationError("frozen CAT-07A cardinalities changed")
    if expansion.get("finalIncluded") != 2500 or expansion.get("canonicalWritten") is not False:
        raise CandidateApplicationError("invalid frozen CAT-07A status")
    baseline_record_paths = [record_path(source_id) for source_id in base_ids]
    if any(not path.exists() for path in baseline_record_paths):
        raise CandidateApplicationError("pinned CAT-07 baseline record is missing")
    if tree_sha(baseline_record_paths) != BASELINE_RECORD_TREE_SHA256:
        raise CandidateApplicationError("pinned CAT-07 baseline record tree changed")
    curation_paths = list((GAP_RUN / "semantic-review" / "decisions" / "accepted-curation").glob("*.json"))
    if len(curation_paths) != 1599 or tree_sha(curation_paths) != ACCEPTED_CURATION_TREE_SHA256:
        raise CandidateApplicationError("pinned CAT-07 accepted-curation tree changed")

    source_by_id = {item["id"]: item for item in manifest["repositories"]}
    decision_by_id = {item["sourceId"]: item for item in decisions}
    aliases_by_root: dict[str, list[str]] = defaultdict(list)
    for item in alias_items:
        aliases_by_root[item["canonicalSourceId"]].append(item["sourceId"])
    edits_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edit in sparse_edits:
        edits_by_id[edit["sourceId"]].append(edit)
    semantic_by_id: dict[str, dict[str, Any]] = {}
    for item in semantic_items:
        fragment = item.get("acceptedFragment") or {}
        semantic_by_id[item["sourceId"]] = fragment.get("fields") or {}
    if len(set(base_ids)) != 1624 or any(source_id not in source_by_id for source_id in base_ids):
        raise CandidateApplicationError("baseline identity set is invalid")
    if any(not decision_by_id[source_id].get("eligible") for source_id in base_ids):
        raise CandidateApplicationError("baseline contains a CAT-07 ineligible identity")

    repositories = []
    observed_archived_baseline = 0
    for source_id in base_ids:
        record = load(record_path(source_id))
        values, _ = eligibility.effective_values(record, resolutions.get(source_id), source_by_id[source_id])
        observed_archived_baseline += values.get("archived") is True
        patched_source = apply_sparse_overlays(
            source_by_id[source_id],
            edits_by_id[source_id],
            semantic_by_id.get(source_id, {}),
        )
        repositories.append(
            normalize_baseline_card(patched_source, values, aliases_by_root[source_id], source_by_id)
        )
    repositories.extend(normalize_addition_card(item) for item in additions)
    review = review_decisions(repositories)

    ids = [item["id"] for item in repositories]
    numeric_ids = [item.get("githubRepositoryId") for item in repositories]
    names = [item["fullName"].casefold() for item in repositories]
    urls = [item["url"].casefold().rstrip("/") for item in repositories]
    if len(repositories) != 2500 or len(set(ids)) != 2500:
        raise CandidateApplicationError("candidate must contain exactly 2,500 unique source IDs")
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in numeric_ids):
        raise CandidateApplicationError("candidate contains unresolved numeric GitHub identity")
    if len(set(numeric_ids)) != 2500 or len(set(names)) != 2500 or len(set(urls)) != 2500:
        raise CandidateApplicationError("candidate contains duplicate GitHub identities, names or URLs")
    canonical_name_owners = {item["fullName"].casefold(): item["id"] for item in repositories}
    alias_owners: dict[str, str] = {}
    for item in repositories:
        for alias in item.get("aliases", []):
            normalized_alias = alias.casefold()
            if normalized_alias in canonical_name_owners:
                raise CandidateApplicationError("candidate alias collides with a canonical full name")
            prior_owner = alias_owners.setdefault(normalized_alias, item["id"])
            if prior_owner != item["id"]:
                raise CandidateApplicationError("candidate alias is shared by multiple identities")
    if any(
        not isinstance(item.get("stars"), int)
        or isinstance(item.get("stars"), bool)
        or item["stars"] < 500
        for item in repositories
    ):
        raise CandidateApplicationError("candidate contains a repository below 500 Stars")
    normalized_additions = repositories[1624:]
    if any(item.get("archived") is not False or item.get("visibility") != "public" for item in normalized_additions):
        raise CandidateApplicationError("CAT-07A additions contain archived or non-public repository")

    categories, placements = rebuild_taxonomy(manifest["categories"], repositories)
    payload = copy.deepcopy(manifest)
    payload["snapshot"] = "2026-09-01"
    payload["repositories"] = repositories
    payload["categories"] = categories
    payload["placements"] = placements
    included_ids = set(ids)
    payload["compatibility"] = [
        edge
        for edge in manifest["compatibility"]
        if edge["sourceRepoId"] in included_ids and edge["targetRepoId"] in included_ids
    ]
    payload["target"] = {
        "canonicalRepositories": 2500,
        "activityComplete": False,
        "note": "CAT-08 canonical reconciliation applied the frozen CAT-07 eligibility state and 876 CAT-07A additions; recommendation and deeper activity fields remain explicit downstream backlogs.",
        "requiredFields": manifest["target"].get("requiredFields", []),
        "metadataSource": "Pinned CAT-07 public GitHub observations plus the frozen CAT-07A validated expansion candidate.",
        "roadmapTarget": 2500,
    }
    payload.setdefault("enrichment", {})["canonicalReconciliation"] = {
        "date": "2026-09-01",
        "task": "CP-03.CAT-08",
        "baselineIncluded": 1624,
        "acceptedAdditions": 876,
        "qualifiedOverflowReserved": 7,
        "reviewDecisions": len(review),
        "inputHashes": {name: expected for name, (_, expected) in INPUTS.items()},
        "wholeCorpusRefreshed": False,
    }
    payload.setdefault("taxonomyMigration", {})["finalEligibilityApplied"] = True
    payload["taxonomyMigration"]["cat08ReviewDecisions"] = copy.deepcopy(review)
    payload.setdefault("catalogEligibilityPolicy", {})["fullCorpusApplied"] = True
    payload["summary"] = recompute_summary(payload)
    html_builder.validate_payload(payload)
    projected = html_builder.presentation_projection(payload)
    expected_leaf_counts = final_counts["thematicLeafCounts"]
    actual_leaf_counts = {
        item["key"]: len(item["repoIds"])
        for item in categories
        if item.get("kind") == "category"
    }
    expected_after_review = {key: row["repositoryCount"] for key, row in expected_leaf_counts.items()}
    for category in REVIEW_REASSIGNMENTS.values():
        expected_after_review[category] += 1
    if actual_leaf_counts != expected_after_review:
        raise CandidateApplicationError("thematic leaf counts drifted from frozen CAT-07A candidate")
    if payload["summary"]["reviewRepositories"] != 12 or payload["summary"]["thematicRepositories"] != 2488:
        raise CandidateApplicationError("review/thematic repository reconciliation failed")
    if payload["summary"]["thematicPlacements"] != 2618 or payload["summary"]["placements"] != 2630:
        raise CandidateApplicationError("placement reconciliation failed")
    report = {
        "task": "CP-03.CAT-08",
        "status": "candidate_verified",
        "inputHashes": {name: expected for name, (_, expected) in INPUTS.items()},
        "treeHashes": {
            "baselineRecords": BASELINE_RECORD_TREE_SHA256,
            "acceptedCuration": ACCEPTED_CURATION_TREE_SHA256,
        },
        "counts": copy.deepcopy(payload["summary"]),
        "additionCount": 876,
        "overflowReserved": 7,
        "canonicalArchivedBaselineRepositories": sum(item.get("archived") is True for item in repositories[:1624]),
        "observedArchivedBaselineRepositories": observed_archived_baseline,
        "reviewDecisions": review,
        "manifestBytes": len(canonical_bytes(payload)),
        "manifestSha256": sha_bytes(canonical_bytes(payload)),
        "presentationRepositoryFields": sorted(html_builder.PRESENTATION_REPOSITORY_FIELDS),
        "presentationTopLevelFields": sorted(html_builder.PRESENTATION_TOP_LEVEL_FIELDS),
        "presentationBytes": len(html_builder.canonical_json(projected).encode("utf-8")),
        "templateSha256": sha(TEMPLATE),
        "templateBeforeSha256": TEMPLATE_BEFORE_SHA256,
        "manifestSchemaBeforeSha256": MANIFEST_SCHEMA_BEFORE_SHA256,
        "templateBehaviorChange": "search_description_fallback_and_aliases",
        "sourceVisualCssLayoutChanged": False,
        "browserVerified": False,
    }
    return payload, report


def write_fsynced(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())


def replace_fsynced(path: Path, value: bytes, suffix: str) -> None:
    staged = path.with_name(path.name + suffix)
    write_fsynced(staged, value)
    os.replace(staged, path)


def write_transaction(payload: dict[str, Any], report: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    verify_pins()
    run_dir.mkdir(parents=True, exist_ok=True)
    lock_path = CANONICAL_WRITE_LOCK
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise CandidateApplicationError("another CAT-08 apply transaction is active") from exc
    os.write(lock_fd, str(os.getpid()).encode("ascii"))
    os.fsync(lock_fd)
    os.close(lock_fd)
    rollback = run_dir / "rollback"
    stage = run_dir / "stage"
    try:
        verify_pins()
        rollback.mkdir(parents=True, exist_ok=False)
        stage.mkdir(parents=True, exist_ok=False)
        journal_path = run_dir / "application-journal.json"
        before_manifest = MANIFEST.read_bytes()
        before_html = HTML.read_bytes()
        before_payload = json.loads(before_manifest.decode("utf-8"))
        rollback_operational_html = html_builder.page(before_payload).encode("utf-8")
        rollback_manifest = rollback / "catalog_manifest.json"
        rollback_html = rollback / "UNIFIED_CATALOG.html"
        rollback_operational = rollback / "UNIFIED_CATALOG.current-renderer.html"
        write_fsynced(rollback_manifest, before_manifest)
        write_fsynced(rollback_html, before_html)
        write_fsynced(rollback_operational, rollback_operational_html)

        manifest_bytes = canonical_bytes(payload)
        html_bytes = html_builder.page(payload).encode("utf-8")
        stage_manifest = stage / "catalog_manifest.json"
        stage_html = stage / "UNIFIED_CATALOG.html"
        write_fsynced(stage_manifest, manifest_bytes)
        write_fsynced(stage_html, html_bytes)
        if load(stage_manifest) != payload:
            raise CandidateApplicationError("staged manifest parse/parity failure")
        if stage_html.read_bytes() != html_bytes:
            raise CandidateApplicationError("staged HTML parity failure")

        final_report = copy.deepcopy(report)
        final_report.update(
            status="applied_and_verified",
            rollback={
                "manifest": str(rollback_manifest),
                "html": str(rollback_html),
                "operationalHtml": str(rollback_operational),
                "manifestSha256": sha_bytes(before_manifest),
                "htmlSha256": sha_bytes(before_html),
                "operationalHtmlSha256": sha_bytes(rollback_operational_html),
            },
            output={
                "manifest": str(MANIFEST),
                "html": str(HTML),
                "manifestSha256": sha_bytes(manifest_bytes),
                "htmlSha256": sha_bytes(html_bytes),
                "htmlBytes": len(html_bytes),
            },
        )
        report_path = run_dir / "application-report.json"
        review_path = run_dir / "review-decisions.json"
        stage_report = stage / "application-report.json"
        stage_review = stage / "review-decisions.json"
        write_fsynced(
            stage_report,
            (json.dumps(final_report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        write_fsynced(
            stage_review,
            (json.dumps({"items": final_report["reviewDecisions"]}, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        journal = {
            "task": "CP-03.CAT-08",
            "status": "prepared",
            "before": {
                "manifestSha256": sha_bytes(before_manifest),
                "htmlSha256": sha_bytes(before_html),
            },
            "after": {
                "manifestSha256": sha_bytes(manifest_bytes),
                "htmlSha256": sha_bytes(html_bytes),
            },
            "rollback": {
                "manifest": str(rollback_manifest),
                "html": str(rollback_html),
                "operationalHtml": str(rollback_operational),
            },
        }
        replace_fsynced(
            journal_path,
            (json.dumps(journal, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
            ".cat08-journal",
        )

        try:
            replace_fsynced(MANIFEST, stage_manifest.read_bytes(), ".cat08-commit")
            replace_fsynced(HTML, stage_html.read_bytes(), ".cat08-commit")
            replace_fsynced(report_path, stage_report.read_bytes(), ".cat08-commit")
            replace_fsynced(review_path, stage_review.read_bytes(), ".cat08-commit")
            if sha(TEMPLATE) != INPUTS["template"][1]:
                raise CandidateApplicationError("template changed during transaction")
            if MANIFEST.read_bytes() != manifest_bytes or HTML.read_bytes() != html_bytes:
                raise CandidateApplicationError("post-write canonical parity failed")
            if load(report_path) != final_report or load(review_path) != {"items": final_report["reviewDecisions"]}:
                raise CandidateApplicationError("post-write evidence parity failed")
            journal["status"] = "committed"
            replace_fsynced(
                journal_path,
                (json.dumps(journal, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
                ".cat08-journal",
            )
        except Exception:
            replace_fsynced(MANIFEST, before_manifest, ".cat08-restore")
            replace_fsynced(HTML, before_html, ".cat08-restore")
            for path in (report_path, review_path):
                if path.exists():
                    path.unlink()
            journal["status"] = "rolled_back"
            replace_fsynced(
                journal_path,
                (json.dumps(journal, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
                ".cat08-journal",
            )
            raise
        return final_report
    finally:
        if lock_path.exists():
            lock_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "apply", "verify", "rollback"))
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    args = parser.parse_args()

    if args.mode == "rollback":
        if CANONICAL_WRITE_LOCK.exists():
            raise CandidateApplicationError(
                "canonical writer lock exists; do not remove another transaction's lock during rollback"
            )
        report_path = args.run_dir / "application-report.json"
        journal_path = args.run_dir / "application-journal.json"
        report = load(report_path) if report_path.exists() else None
        journal = load(journal_path) if journal_path.exists() else None
        if report:
            before = report["rollback"]
            after = report["output"]
            rollback_manifest = Path(before["manifest"])
            rollback_html = Path(before.get("operationalHtml", before["html"]))
            rollback_html_sha = before.get("operationalHtmlSha256", before["htmlSha256"])
        elif journal:
            before = journal["before"]
            after = journal["after"]
            rollback_manifest = Path(journal["rollback"]["manifest"])
            rollback_html = Path(journal["rollback"].get("operationalHtml", journal["rollback"]["html"]))
            rollback_html_sha = sha(rollback_html)
        else:
            raise CandidateApplicationError("CAT-08 report/journal is missing")
        current_manifest_sha = sha(MANIFEST)
        current_html_sha = sha(HTML)
        allowed_manifest = {before["manifestSha256"], after["manifestSha256"]}
        allowed_html = {before["htmlSha256"], after["htmlSha256"], rollback_html_sha}
        if current_manifest_sha not in allowed_manifest or current_html_sha not in allowed_html:
            raise CandidateApplicationError("canonical outputs do not match either side of the transaction")
        if sha(rollback_manifest) != before["manifestSha256"] or sha(rollback_html) != rollback_html_sha:
            raise CandidateApplicationError("rollback snapshot hash mismatch")
        replace_fsynced(MANIFEST, rollback_manifest.read_bytes(), ".cat08-cli-restore")
        replace_fsynced(HTML, rollback_html.read_bytes(), ".cat08-cli-restore")
        if journal:
            journal["status"] = "rolled_back"
            replace_fsynced(
                journal_path,
                (json.dumps(journal, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
                ".cat08-journal",
            )
        print(json.dumps({"rolledBack": True, "manifestSha256": sha(MANIFEST), "htmlSha256": sha(HTML)}, ensure_ascii=False))
        return

    if args.mode == "verify" and sha(MANIFEST) != INPUTS["manifest"][1]:
        payload = html_builder.load_manifest(MANIFEST)
        report_path = args.run_dir / "application-report.json"
        if not report_path.exists():
            raise CandidateApplicationError("applied CAT-08 report is missing")
        report = load(report_path)
        if report.get("status") != "applied_and_verified" or report["output"]["manifestSha256"] != sha(MANIFEST):
            raise CandidateApplicationError("applied CAT-08 report/output mismatch")
        if html_builder.page(payload).encode("utf-8") != HTML.read_bytes():
            raise CandidateApplicationError("applied CAT-08 HTML parity mismatch")
        if sha(TEMPLATE) != INPUTS["template"][1]:
            raise CandidateApplicationError("template/design source changed")
        print(json.dumps({"verified": True, **report["output"], "counts": payload["summary"]}, ensure_ascii=False))
        return

    payload, report = build_candidate()
    if args.mode == "apply":
        report = write_transaction(payload, report, args.run_dir)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
