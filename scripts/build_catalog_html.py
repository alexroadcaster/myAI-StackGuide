"""Build the standalone myAI-StackGuide HTML catalog from source-owned v5 data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "catalog_manifest.json"
SCHEMA = ROOT / "data" / "catalog_manifest.schema.json"
TEMPLATE = ROOT / "templates" / "unified_catalog.html"
OUTPUT = ROOT / "docs" / "UNIFIED_CATALOG.html"
CANONICAL_WRITE_LOCK = ROOT / ".codex-tmp" / "catalog-refresh" / "canonical-write.lock"
DATA_MARKER = "{{CATALOG_DATA_JSON}}"

REQUIRED_TOP_LEVEL_FIELDS = {
    "schemaVersion",
    "snapshot",
    "title",
    "baseline",
    "target",
    "summary",
    "profiles",
    "useCases",
    "repositories",
    "categories",
    "placements",
    "compatibility",
    "stackRecipes",
    "discoveryQueries",
    "dataPolicy",
    "activitySchema",
    "enrichment",
}

PRESENTATION_REPOSITORY_FIELDS = (
    "id",
    "aliases",
    "fullName",
    "url",
    "description",
    "catalogDescription",
    "language",
    "license",
    "stars",
    "catalogStatus",
    "productionEligible",
    "lifecycle",
    "form",
    "deployment",
    "hosting",
    "persona",
    "difficulty",
    "primaryCategory",
    "secondaryCategories",
    "evidenceCompleteness",
    "topics",
    "archived",
    "activity",
    "stack",
)

PRESENTATION_TOP_LEVEL_FIELDS = (
    "snapshot",
    "summary",
    "useCases",
    "categories",
    "stackRecipes",
)

PRESENTATION_OMITTED_AUDIT_FIELDS = {
    "classification",
    "coreFieldGatePassed",
    "coreUnsupportedFields",
    "eligibility",
    "fieldObservations",
    "languages",
    "qualifiedSequence",
    "recommendationStatus",
    "schemaVersion",
    "selectionKey",
    "sourceId",
    "sourceRecordIds",
    "provenance",
}


class CatalogContractError(ValueError):
    """Raised when the source manifest cannot safely generate the catalog."""


def canonical_json(payload: dict[str, Any]) -> str:
    """Return the deterministic JSON representation embedded in the HTML."""

    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _require_unique(values: list[Any], label: str) -> None:
    if len(values) != len(set(values)):
        raise CatalogContractError(f"duplicate {label}")


def validate_payload(payload: dict[str, Any]) -> None:
    """Validate invariants needed by the standalone catalog renderer."""

    missing = REQUIRED_TOP_LEVEL_FIELDS - payload.keys()
    if missing:
        raise CatalogContractError(f"missing top-level fields: {sorted(missing)}")
    if payload["schemaVersion"] not in {"5.0-full-refresh", "5.1-taxonomy-v2"}:
        raise CatalogContractError("unsupported schemaVersion")

    repositories = payload["repositories"]
    categories = payload["categories"]
    placements = payload["placements"]
    compatibility = payload["compatibility"]
    stack_recipes = payload["stackRecipes"]
    summary = payload["summary"]
    strict_canonical_identity = (
        (payload.get("enrichment") or {}).get("canonicalReconciliation", {}).get("task")
        == "CP-03.CAT-08"
    )

    collections = (repositories, categories, placements, compatibility, stack_recipes)
    if not all(isinstance(value, list) for value in collections):
        raise CatalogContractError("catalog collections must be arrays")

    required_repo_fields = {"id", "fullName", "url", "catalogStatus", "primaryCategory", "provenance"}
    if strict_canonical_identity:
        required_repo_fields.add("githubRepositoryId")
    for index, repository in enumerate(repositories):
        repo_missing = required_repo_fields - repository.keys()
        if repo_missing:
            raise CatalogContractError(f"repository[{index}] missing fields: {sorted(repo_missing)}")
        if strict_canonical_identity:
            numeric_id = repository["githubRepositoryId"]
            if not isinstance(numeric_id, int) or isinstance(numeric_id, bool) or numeric_id <= 0:
                raise CatalogContractError(f"repository[{index}] has invalid githubRepositoryId")
            aliases = repository.get("aliases", [])
            if not isinstance(aliases, list):
                raise CatalogContractError(f"repository[{index}] aliases must be an array")
            normalized_aliases = []
            for alias in aliases:
                if not isinstance(alias, str) or not alias.strip():
                    raise CatalogContractError(f"repository[{index}] contains an invalid alias")
                normalized_aliases.append(alias.strip().casefold())
            _require_unique(normalized_aliases, f"repository[{index}] aliases")
            stack = repository.get("stack")
            if stack is not None:
                if not isinstance(stack, list):
                    raise CatalogContractError(f"repository[{index}] stack must be an array or null")
                for stack_item in stack:
                    if isinstance(stack_item, str) and stack_item.strip():
                        continue
                    if not isinstance(stack_item, dict):
                        raise CatalogContractError(f"repository[{index}] contains an invalid stack entry")
                    technology = stack_item.get("technology")
                    evidence_refs = stack_item.get("evidenceRefs")
                    if (
                        not isinstance(technology, str)
                        or not technology.strip()
                        or not isinstance(evidence_refs, list)
                        or not evidence_refs
                        or any(not isinstance(ref, str) or not ref.strip() for ref in evidence_refs)
                    ):
                        raise CatalogContractError(f"repository[{index}] contains an invalid structured stack entry")

    required_category_fields = {"key", "title", "repoIds"}
    for index, category in enumerate(categories):
        category_missing = required_category_fields - category.keys()
        if category_missing:
            raise CatalogContractError(f"category[{index}] missing fields: {sorted(category_missing)}")

    required_placement_fields = {"repoKey", "categoryKey", "source"}
    for index, placement in enumerate(placements):
        placement_missing = required_placement_fields - placement.keys()
        if placement_missing:
            raise CatalogContractError(f"placement[{index}] missing fields: {sorted(placement_missing)}")

    repo_ids = [repository["id"] for repository in repositories]
    github_repository_ids = [repository.get("githubRepositoryId") for repository in repositories]
    repo_names = [repository["fullName"].casefold() for repository in repositories]
    category_keys = [category["key"] for category in categories]
    placement_pairs = [(placement["repoKey"].casefold(), placement["categoryKey"]) for placement in placements]
    _require_unique(repo_ids, "repository ids")
    if strict_canonical_identity:
        _require_unique(github_repository_ids, "GitHub repository ids")
    _require_unique(repo_names, "repository full names")
    _require_unique(category_keys, "category keys")
    _require_unique(placement_pairs, "repository/category placements")

    if strict_canonical_identity:
        canonical_name_owners = {
            repository["fullName"].strip().casefold(): repository["id"]
            for repository in repositories
        }
        alias_owners: dict[str, str] = {}
        for repository in repositories:
            for alias in repository.get("aliases", []):
                normalized_alias = alias.strip().casefold()
                if normalized_alias in canonical_name_owners:
                    raise CatalogContractError("repository alias collides with a canonical full name")
                prior_owner = alias_owners.setdefault(normalized_alias, repository["id"])
                if prior_owner != repository["id"]:
                    raise CatalogContractError("repository alias is shared by multiple identities")

    category_key_set = set(category_keys)
    unknown_primary_categories = sorted(
        {repository["primaryCategory"] for repository in repositories if repository["primaryCategory"] not in category_key_set}
    )
    unknown_secondary_categories = sorted(
        {
            category
            for repository in repositories
            for category in repository.get("secondaryCategories", [])
            if category not in category_key_set
        }
    )
    if unknown_primary_categories or unknown_secondary_categories:
        raise CatalogContractError(
            "repositories reference unknown categories: "
            f"primary={unknown_primary_categories}, secondary={unknown_secondary_categories}"
        )

    unknown_placement_categories = sorted(
        {placement["categoryKey"] for placement in placements if placement["categoryKey"] not in category_key_set}
    )
    if unknown_placement_categories:
        raise CatalogContractError(f"placements reference unknown categories: {unknown_placement_categories}")

    if payload['schemaVersion'] == '5.1-taxonomy-v2':
        by_category = {c['key']: c for c in categories}
        by_name = {r['fullName'].casefold(): r for r in repositories}
        by_id = {r['id']: r for r in repositories}
        declared = set()
        for repository in repositories:
            assigned = [repository['primaryCategory'], *repository.get('secondaryCategories', [])]
            _require_unique(assigned, 'primary/secondary categories')
            if any(by_category[k].get('kind') == 'container' for k in assigned):
                raise CatalogContractError('repository assigned to a navigation container')
            declared.update((repository['id'], k) for k in assigned)
        if any(p['repoKey'].casefold() not in by_name for p in placements):
            raise CatalogContractError('placement references unknown repository')
        actual = {(by_name[p['repoKey'].casefold()]['id'], p['categoryKey']) for p in placements}
        if actual != declared:
            raise CatalogContractError('placement/declaration mismatch')
        memberships = set()
        for category in categories:
            if category.get('kind') not in {'category','container','review_bucket'}:
                raise CatalogContractError('unknown taxonomy node kind')
            _require_unique(category['repoIds'], 'category membership ids')
            if any(i not in by_id for i in category['repoIds']):
                raise CatalogContractError('category references unknown repository')
            memberships.update((i, category['key']) for i in category['repoIds'])
            seen = {category['key']}
            parent = category.get('parentId')
            while parent is not None:
                if parent not in by_category or parent in seen:
                    raise CatalogContractError('unknown or cyclic category parent')
                if by_category[parent].get('kind') != 'container':
                    raise CatalogContractError('category parent must be a container')
                seen.add(parent)
                parent = by_category[parent].get('parentId')
            if category.get('kind') == 'container':
                if category['repoIds']:
                    raise CatalogContractError('container has direct repository memberships')
                children = {c['key'] for c in categories if c.get('parentId') == category['key']}
                expected = {i for i,k in declared if k in children}
                descendants = category.get('descendantRepoIds', [])
                if len(descendants) != len(set(descendants)) or set(descendants) != expected:
                    raise CatalogContractError('container descendant union mismatch')
        if memberships != declared:
            raise CatalogContractError('category membership/declaration mismatch')
        for case in payload['useCases']:
            if any(k not in by_category or by_category[k]['kind'] == 'container' for k in case['categories']):
                raise CatalogContractError('use case references unknown or container category')

    repo_id_set = set(repo_ids)
    for index, edge in enumerate(compatibility):
        edge_missing = {"sourceRepoId", "targetRepoId", "relation"} - edge.keys()
        if edge_missing:
            raise CatalogContractError(f"compatibility[{index}] missing fields: {sorted(edge_missing)}")
        unknown_repos = {edge["sourceRepoId"], edge["targetRepoId"]} - repo_id_set
        if unknown_repos:
            raise CatalogContractError(f"compatibility[{index}] references unknown repositories: {sorted(unknown_repos)}")

    status_counts: dict[str, int] = {}
    for repository in repositories:
        status = repository["catalogStatus"]
        status_counts[status] = status_counts.get(status, 0) + 1

    expected_counts = {
        "canonicalRepositories": len(repositories),
        "accepted": status_counts.get("accepted", 0),
        "candidates": status_counts.get("candidate", 0),
        "referenceOrBenchmark": status_counts.get("reference", 0) + status_counts.get("benchmark", 0),
        "categories": len(categories),
        "placements": len(placements),
        "stackRecipes": len(stack_recipes),
        "compatibilityEdges": len(compatibility),
        "activityEnriched": sum(
            (repository.get("activity") or {}).get("status") == "enriched" for repository in repositories
        ),
    }
    mismatches = {
        key: {"expected": expected, "observed": summary.get(key)}
        for key, expected in expected_counts.items()
        if summary.get(key) != expected
    }
    if mismatches:
        raise CatalogContractError(f"summary count mismatch: {mismatches}")

    embedded = canonical_json(payload)
    if "</script" in embedded.casefold():
        raise CatalogContractError("manifest contains an unsafe closing script sequence")


def load_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    """Load and validate the canonical current catalog manifest."""

    if path == MANIFEST and CANONICAL_WRITE_LOCK.exists():
        raise CatalogContractError("canonical catalog write is in progress; retry after the transaction finishes")
    raw = path.read_text(encoding="utf-8").strip()
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise CatalogContractError("catalog manifest root must be an object")
    if raw != canonical_json(payload):
        raise CatalogContractError("catalog manifest must use canonical compact JSON")
    validate_payload(payload)
    return payload


def build_payload() -> dict[str, Any]:
    """Compatibility entry point for parity checks and downstream imports."""

    return load_manifest()


def _presentation_stack(value: Any) -> list[str]:
    """Project source-owned structured Stack evidence to display labels."""

    if value is None:
        return []
    if not isinstance(value, list):
        raise CatalogContractError("repository stack must be an array")
    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            technology = item.strip()
        elif isinstance(item, dict) and isinstance(item.get("technology"), str) and item["technology"].strip():
            technology = item["technology"].strip()
        else:
            raise CatalogContractError("repository stack entries must be strings or structured technologies")
        if technology not in result:
            result.append(technology)
    return result


def presentation_projection(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the deterministic, display-only payload embedded in standalone HTML."""

    validate_payload(payload)
    projected = {key: payload[key] for key in PRESENTATION_TOP_LEVEL_FIELDS}
    verified_replacement = (payload.get("enrichment") or {}).get("verifiedReplacement")
    projected["enrichment"] = (
        {"verifiedReplacement": verified_replacement}
        if isinstance(verified_replacement, dict)
        else {}
    )
    projected_repositories = []
    for repository in payload["repositories"]:
        item = {
            key: repository[key]
            for key in PRESENTATION_REPOSITORY_FIELDS
            if key in repository
        }
        description = item.get("description")
        if not isinstance(description, str) or not description.strip():
            catalog_description = repository.get("catalogDescription")
            if isinstance(catalog_description, str) and catalog_description.strip():
                item["description"] = catalog_description
            else:
                item.pop("description", None)
        item["stack"] = _presentation_stack(repository.get("stack"))
        projected_repositories.append(item)
    projected["repositories"] = projected_repositories
    validate_presentation_projection(payload, projected)
    return projected


def validate_presentation_projection(source: dict[str, Any], projected: dict[str, Any]) -> None:
    """Prove identity/order and adapter parity for every projected repository."""

    expected_top_level = {*PRESENTATION_TOP_LEVEL_FIELDS, "enrichment", "repositories"}
    if set(projected) != expected_top_level:
        raise CatalogContractError("presentation projection top-level field mismatch")
    source_repositories = source["repositories"]
    projected_repositories = projected.get("repositories")
    if not isinstance(projected_repositories, list) or len(projected_repositories) != len(source_repositories):
        raise CatalogContractError("presentation projection repository count mismatch")
    for source_item, projected_item in zip(source_repositories, projected_repositories, strict=True):
        if projected_item.get("id") != source_item["id"] or projected_item.get("fullName") != source_item["fullName"]:
            raise CatalogContractError("presentation projection identity/order mismatch")
        leaked = PRESENTATION_OMITTED_AUDIT_FIELDS & projected_item.keys()
        if leaked:
            raise CatalogContractError(f"presentation projection leaked audit fields: {sorted(leaked)}")
        if projected_item.get("stack") != _presentation_stack(source_item.get("stack")):
            raise CatalogContractError("presentation projection stack mismatch")
        expected_description = source_item.get("description")
        if not isinstance(expected_description, str) or not expected_description.strip():
            catalog_description = source_item.get("catalogDescription")
            expected_description = (
                catalog_description
                if isinstance(catalog_description, str) and catalog_description.strip()
                else None
            )
        if projected_item.get("description") != expected_description:
            raise CatalogContractError("presentation projection description mismatch")


def page(payload: dict[str, Any]) -> str:
    """Render the standalone HTML page from the template and manifest."""

    validate_payload(payload)
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(DATA_MARKER) != 1:
        raise CatalogContractError("HTML template must contain exactly one catalog data marker")
    return template.replace(DATA_MARKER, canonical_json(presentation_projection(payload)))


def integrity_warnings(payload: dict[str, Any]) -> dict[str, Any]:
    """Return preserved source issues that do not prevent deterministic output."""

    repository_keys = {
        *(repository["id"].casefold() for repository in payload["repositories"]),
        *(repository["fullName"].casefold() for repository in payload["repositories"]),
    }
    unresolved_placements = [
        placement
        for placement in payload["placements"]
        if placement["repoKey"].casefold() not in repository_keys
    ]
    return {
        "unresolvedPlacementCount": len(unresolved_placements),
        "unresolvedPlacementRepositoryKeys": sorted({item["repoKey"] for item in unresolved_placements}),
    }


def output_status(expected: str, actual: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "output": str(OUTPUT),
        "matches": actual == expected,
        "expected_bytes": len(expected.encode("utf-8")),
        "actual_bytes": len(actual.encode("utf-8")) if actual is not None else None,
        "expected_sha256": hashlib.sha256(expected.encode("utf-8")).hexdigest(),
        "actual_sha256": hashlib.sha256(actual.encode("utf-8")).hexdigest() if actual is not None else None,
        "warnings": integrity_warnings(payload),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the checked-in HTML without writing it")
    parser.add_argument("--validate-only", action="store_true", help="validate the manifest and template only")
    args = parser.parse_args()

    payload = load_manifest()
    expected = page(payload)
    actual = OUTPUT.read_bytes().decode("utf-8") if OUTPUT.exists() else None
    status = output_status(expected, actual, payload)

    if args.validate_only:
        print(json.dumps({**status, "validated": True}, ensure_ascii=False))
        return
    if args.check:
        print(json.dumps(status, ensure_ascii=False))
        raise SystemExit(0 if status["matches"] else 1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8", newline="\n")
    print(json.dumps({**status, "written": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
