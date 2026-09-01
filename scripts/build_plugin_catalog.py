"""Build the CP-06 public RepositoryCardV2 snapshot from frozen CAT-10 data."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_catalog_html as catalog_v5  # noqa: E402


SOURCE = ROOT / "data" / "catalog_manifest.json"
SOURCE_SCHEMA = ROOT / "data" / "catalog_manifest.schema.json"
FREEZE_REPORT = ROOT / "docs" / "reports" / "catalog-final-freeze-2026-09-01.json"
TAXONOMY = ROOT / "specs" / "catalog" / "taxonomy.yaml"
FIELD_CONTRACT = ROOT / "specs" / "catalog" / "enrichment-field-contract.json"
CARD_SCHEMA = ROOT / "specs" / "catalog" / "repository-card.schema.json"
ACTIVITY_SCHEMA = ROOT / "specs" / "catalog" / "activity-evidence.schema.json"
ADVISORY_SEED = ROOT / "data" / "plugin_advisory_seed.json"
OUTPUT = ROOT / "plugins" / "myai-stackguide" / "assets" / "catalog.snapshot.json"

CARD_SCHEMA_VERSION = "2.0.0"
ACTIVITY_SCHEMA_VERSION = "2.0.0"
BUILDER_VERSION = "1.0.0"
CATALOG_RECORD_ID = re.compile(r"^gh(?:-(?:pending|expansion|[0-9]+))?:[A-Za-z0-9_.:/-]+$")
FULL_NAME = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
UNKNOWN_TOKENS = {"", "unknown", "not_known", "not_set", "n/a", "none", "null", "noassertion"}


class PluginCatalogBuildError(ValueError):
    """Raised when frozen source data cannot map safely to RepositoryCardV2."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PluginCatalogBuildError(message)


def _load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            PluginCatalogBuildError(f"non-finite JSON number in {path}: {value}")
        ),
    )


def validate_frozen_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    freeze = _load_json(FREEZE_REPORT)
    handoff = freeze["cp06Handoff"]
    required = {
        SOURCE: handoff["requiredSourceSha256"],
        SOURCE_SCHEMA: handoff["requiredSchemaSha256"],
        TAXONOMY: handoff["requiredTaxonomySha256"],
        FIELD_CONTRACT: handoff["requiredFieldContractSha256"],
    }
    for path, expected in required.items():
        actual = file_sha256(path)
        try:
            label = path.relative_to(ROOT)
        except ValueError:
            label = path
        _require(actual == expected, f"frozen pin mismatch for {label}: {actual}")

    manifest = catalog_v5.load_manifest()
    taxonomy = _load_json(TAXONOMY)
    _require(manifest["schemaVersion"] == "5.1-taxonomy-v2", "unexpected CAT-10 schema version")
    _require(manifest["snapshot"] == freeze["sourceOfTruth"]["snapshotDate"], "snapshot date mismatch")
    _require(taxonomy["source_sha256"] == required[SOURCE], "taxonomy source pin mismatch")
    _require(taxonomy["source_snapshot"] == manifest["snapshot"], "taxonomy snapshot mismatch")
    _require(_load_json(CARD_SCHEMA)["properties"]["schema_version"]["const"] == CARD_SCHEMA_VERSION,
             "RepositoryCardV2 schema version mismatch")
    _require(_load_json(ACTIVITY_SCHEMA)["properties"]["schema_version"]["const"] == ACTIVITY_SCHEMA_VERSION,
             "ActivityV2 schema version mismatch")

    seed = _load_json(ADVISORY_SEED)
    _require(seed == {
        "schema_version": "1.0.0",
        "catalog_snapshot_id": freeze["snapshotId"],
        "source_sha256": required[SOURCE],
        "entries": [],
    }, "advisory seed must remain an empty, exact-snapshot override registry")
    return manifest, taxonomy, freeze


def _clean_scalar(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return None if text.casefold() in UNKNOWN_TOKENS else text


def _token(value: Any) -> str | None:
    text = _clean_scalar(value)
    if text is None:
        return None
    _require(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", text)), f"invalid token: {text!r}")
    return text


def _strings(value: Any, *, max_items: int, max_chars: int) -> list[str]:
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        text = _clean_scalar(item)
        if text is None:
            continue
        _require(len(text) <= max_chars, f"text exceeds {max_chars} characters")
        if text not in seen:
            seen.add(text)
            result.append(text)
    _require(len(result) <= max_items, f"list exceeds {max_items} items")
    return result


def _nullable_url(value: Any) -> str | None:
    text = _clean_scalar(value)
    if text is None:
        return None
    _require(not any(character.isspace() for character in text), f"invalid URL reference: {text!r}")
    return text


def _normalize_languages(repository: dict[str, Any]) -> list[dict[str, str]]:
    source = repository.get("languages")
    result: list[dict[str, str]] = []
    if isinstance(source, dict):
        ordered = sorted(source.items(), key=lambda item: (-int(item[1]), item[0].casefold()))
        primary = _clean_scalar(repository.get("language"))
        names = [str(name) for name, _ in ordered]
        if primary is not None:
            names = [primary, *[name for name in names if name.casefold() != primary.casefold()]]
        result = [{"name": name, "scope": "primary" if index == 0 else "secondary"}
                  for index, name in enumerate(names)]
    elif isinstance(source, list):
        for item in source:
            if isinstance(item, dict):
                name = _clean_scalar(item.get("name"))
                scope = item.get("scope")
                if name is not None:
                    _require(scope in {"primary", "secondary"}, f"invalid language scope for {name}")
                    result.append({"name": name, "scope": scope})
            else:
                name = _clean_scalar(item)
                if name is not None:
                    result.append({"name": name, "scope": "secondary"})
    elif source is not None:
        raise PluginCatalogBuildError("languages must be an object, array, or null")

    if not result:
        primary = _clean_scalar(repository.get("language"))
        if primary is not None:
            result = [{"name": primary, "scope": "primary"}]
    elif not any(item["scope"] == "primary" for item in result):
        result[0]["scope"] = "primary"

    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in result:
        key = item["name"].casefold()
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    _require(len(deduped) <= 80, "languages exceed RepositoryCardV2 limit")
    return deduped


def _normalize_stack(repository: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in repository.get("stack") or []:
        technology = _clean_scalar(item.get("technology") if isinstance(item, dict) else item)
        if technology is None or technology.casefold() in seen:
            continue
        _require(len(technology) <= 120, f"stack technology too long: {technology!r}")
        seen.add(technology.casefold())
        result.append({"technology": technology, "evidence_refs": ["ev-catalog-repository"]})
    _require(len(result) <= 30, "stack exceeds RepositoryCardV2 limit")
    return result


def _reviewed_scalar(value: Any) -> dict[str, str | None] | None:
    if isinstance(value, dict):
        scalar = value.get("value")
        if isinstance(scalar, list):
            scalar = ", ".join(str(item) for item in scalar)
        text = _clean_scalar(scalar)
        if text is None:
            return None
        return {"value": text, "rationale": _clean_scalar(value.get("rationale"))}
    text = _clean_scalar(value)
    return None if text is None else {"value": text, "rationale": None}


def _deployment(value: Any) -> dict[str, Any]:
    rationale = None
    raw = value
    if isinstance(value, dict):
        raw = value.get("value")
        rationale = _clean_scalar(value.get("rationale"))
    values = _strings(raw, max_items=30, max_chars=180)
    return {"values": values, "rationale": rationale}


def _activity(repository: dict[str, Any]) -> dict[str, Any]:
    source = repository.get("activity") or {}
    mapping = {
        "created_at": "createdAt",
        "repository_updated_at": "updatedAt",
        "pushed_at": "pushedAt",
        "last_commit_at": "lastCommitAt",
        "last_release_at": "lastReleaseAt",
        "last_synced_at": "lastSyncedAt",
        "observed_at": "observedAt",
    }
    result: dict[str, Any] = {"schema_version": ACTIVITY_SCHEMA_VERSION}
    for target, origin in mapping.items():
        result[target] = source.get(origin)
    result.update({
        "last_commit_sha": source.get("lastCommitSha"),
        "last_commit_branch": _clean_scalar(source.get("lastCommitBranch")),
        "status": _token(source.get("status")),
    })
    source_observations = {
        item.get("field"): item
        for item in repository.get("fieldObservations") or []
        if isinstance(item, dict) and item.get("status") != "not_attempted"
    }
    observations = []
    for target, origin in mapping.items():
        if result[target] is not None:
            source_observation = source_observations.get(f"activity.{origin}")
            observations.append({
                "field": target,
                "source_field": f"activity.{origin}",
                "observed_at": (source_observation or {}).get("observedAt") or result["observed_at"],
                "verification": (
                    "derived_reviewed"
                    if source_observation is None or source_observation.get("status") == "derived_reviewed"
                    else "source_reported"
                ),
                "evidence_refs": ["ev-catalog-repository"],
            })
    result["observations"] = observations
    return result


def _normalize_license(value: Any) -> dict[str, str | None] | None:
    if not isinstance(value, dict):
        return None
    result = {
        "spdx": _clean_scalar(value.get("spdx")),
        "name": _clean_scalar(value.get("name")),
        "source": _clean_scalar(value.get("source")),
        "confidence": _token(value.get("confidence")),
    }
    return result if any(item is not None for item in result.values()) else None


def _advisory(repository: dict[str, Any]) -> dict[str, Any]:
    source = repository.get("recommendation") or {}
    reason = _clean_scalar(source.get("whyRecommended")) or _clean_scalar(source.get("why"))
    best_for = _strings(source.get("bestFor"), max_items=12, max_chars=600)
    for item in _strings(source.get("best_for"), max_items=12, max_chars=600):
        if item not in best_for:
            best_for.append(item)
    tradeoffs = _strings(source.get("tradeoffs"), max_items=12, max_chars=600)
    eligibility = repository.get("eligibility") or {}
    status = _token(repository.get("recommendationStatus"))
    return {
        "recommendation_reason": reason,
        "best_for": best_for,
        "tradeoffs": tradeoffs,
        "use_cases": _strings(source.get("use_cases") or source.get("useCases"), max_items=12, max_chars=600),
        "avoid_if": _strings(source.get("avoid_if") or source.get("avoidIf"), max_items=12, max_chars=600),
        "adoption_status": _clean_scalar(source.get("adoption_status")),
        "adoption_mode": _token(source.get("adoption_mode")),
        "project_stages": _strings(source.get("project_stages"), max_items=30, max_chars=180),
        "complexity": _token(source.get("complexity")),
        "integration_surface": _clean_scalar(source.get("integration_surface")),
        "compatibility": _strings(source.get("compatibility"), max_items=30, max_chars=180),
        "eligibility": {
            "data_gate_passed": eligibility.get("dataGatePassed"),
            "reasons": _strings(eligibility.get("reasons"), max_items=30, max_chars=180),
            "minimum_stars": eligibility.get("minimumStars"),
            "replacement_required": eligibility.get("replacementRequired"),
            "catalog_acceptance_changed": eligibility.get("catalogAcceptanceChanged"),
            "evidence_completeness": repository.get("evidenceCompleteness"),
        },
        "recommendation_status": status,
        "gaps": [],
    }


def _classifications(
    repository: dict[str, Any],
    placements: dict[str, list[dict[str, str]]],
    categories: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    entries = placements[repository["fullName"]]
    primary = repository["primaryCategory"]
    _require(any(item["categoryKey"] == primary for item in entries),
             f"primary category missing from placements: {repository['fullName']}")
    result = []
    for item in entries:
        category = categories[item["categoryKey"]]
        _require(category["kind"] != "container", f"direct container placement: {repository['fullName']}")
        result.append({
            "category_id": category["key"],
            "title": category["title"],
            "kind": category["kind"],
            "parent_id": category.get("parentId"),
            "role": "primary" if category["key"] == primary else "secondary",
            "placement_source": item["source"],
        })
    result.sort(key=lambda item: (item["role"] != "primary", item["category_id"]))
    _require(sum(item["role"] == "primary" for item in result) == 1, "classification primary cardinality")
    return result


def build_cards(manifest: dict[str, Any], taxonomy: dict[str, Any], freeze: dict[str, Any]) -> list[dict[str, Any]]:
    taxonomy_by_id = {item["id"]: item for item in taxonomy["categories"]}
    categories = {item["key"]: item for item in manifest["categories"]}
    _require(set(categories) == set(taxonomy_by_id), "manifest/taxonomy category identity mismatch")
    for category_id, category in categories.items():
        pinned = taxonomy_by_id[category_id]
        _require((category["title"], category["kind"], category.get("parentId")) ==
                 (pinned["label"], pinned["kind"], pinned.get("parent_id")),
                 f"manifest/taxonomy category mismatch: {category_id}")

    placements: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in manifest["placements"]:
        placements[item["repoKey"]].append(item)
    frozen_pins = {
        "catalog_snapshot_id": freeze["snapshotId"],
        "source_sha256": freeze["cp06Handoff"]["requiredSourceSha256"],
        "taxonomy_sha256": freeze["cp06Handoff"]["requiredTaxonomySha256"],
        "field_contract_sha256": freeze["cp06Handoff"]["requiredFieldContractSha256"],
    }
    cards = []
    for repository in manifest["repositories"]:
        catalog_record_id = repository["id"]
        _require(CATALOG_RECORD_ID.fullmatch(catalog_record_id) is not None,
                 f"invalid catalog lineage: {catalog_record_id}")
        full_name = repository["fullName"]
        _require(FULL_NAME.fullmatch(full_name) is not None, f"invalid full name: {full_name}")
        aliases = list(repository.get("aliases") or [])
        source_ids = list(repository.get("sourceRecordIds") or [catalog_record_id])
        merged_ids = [item for item in source_ids if item != catalog_record_id]
        activity = _activity(repository)
        advisory = _advisory(repository)
        classifications = _classifications(repository, placements, categories)
        observed_at = activity["observed_at"]
        source_ref = f"catalog:{freeze['snapshotId']}/repositories/{repository['githubRepositoryId']}"
        card = {
            "schema_version": CARD_SCHEMA_VERSION,
            "identity": {
                "github_repository_id": repository["githubRepositoryId"],
                "catalog_record_id": catalog_record_id,
                "merged_catalog_record_ids": merged_ids,
                "full_name": full_name,
                "full_name_aliases": aliases,
                "url": repository["url"],
                "identity_status": _token(repository.get("identityStatus")) or "resolved",
            },
            "catalog": {
                "status": repository["catalogStatus"],
                "status_source": "catalog_snapshot",
                "membership_cohort": "cat07a_expansion" if catalog_record_id.startswith("gh-expansion:") else "baseline",
                "review_status": _token(repository.get("reviewStatus")),
                "evidence_stage": "identity_validated",
            },
            "descriptions": {
                "upstream": _clean_scalar(repository.get("description")),
                "catalog": _clean_scalar(repository.get("catalogDescription")),
                "catalog_origin": _token(repository.get("descriptionOrigin")),
            },
            "classifications": classifications,
            "repository": {
                "languages": _normalize_languages(repository),
                "license": _normalize_license(repository.get("license")),
                "topics": _strings(repository.get("topics"), max_items=30, max_chars=180),
                "stack": _normalize_stack(repository),
                "homepage": _nullable_url(repository.get("homepage")),
                "default_branch": _clean_scalar(repository.get("defaultBranch")),
                "availability": repository.get("availability") or "unknown",
                "visibility": repository.get("visibility") or "unknown",
                "archived": repository.get("archived"),
                "is_fork": repository.get("isFork"),
                "disabled": repository.get("disabled"),
                "stars": repository.get("stars"),
                "forks": repository.get("forks"),
                "watchers": repository.get("watchers"),
                "watchers_scope": _token(repository.get("watchersScope")),
                "size_kb": repository.get("sizeKb"),
            },
            "delivery": {
                "form": _reviewed_scalar(repository.get("form")),
                "deployment": _deployment(repository.get("deployment")),
                "hosting": _reviewed_scalar(repository.get("hosting")),
                "requires_server": repository.get("requiresServer"),
                "difficulty": _token(repository.get("difficulty")),
                "lifecycle": _token(repository.get("lifecycle")),
                "maturity": _token(repository.get("maturity")),
                "persona": _clean_scalar(repository.get("persona")),
            },
            "activity": activity,
            "advisory": advisory,
            "provenance": {
                "sources": [{
                    "source_id": "src-catalog-snapshot",
                    "source_kind": "catalog_snapshot",
                    "source_ref": source_ref,
                    "observed_at": observed_at,
                    "verification": "derived_reviewed",
                }],
                "frozen_pins": frozen_pins,
            },
            "evidence": [
                {
                    "evidence_id": "ev-catalog-card",
                    "source_kind": "catalog_snapshot",
                    "source_ref": source_ref,
                    "observed_at": observed_at,
                    "verification": "derived_reviewed",
                    "fields": [
                        "/identity", "/catalog", "/descriptions", "/classifications",
                        "/delivery", "/advisory", "/provenance",
                    ],
                },
                {
                    "evidence_id": "ev-catalog-repository",
                    "source_kind": "catalog_snapshot",
                    "source_ref": source_ref,
                    "observed_at": observed_at,
                    "verification": "source_reported",
                    "fields": ["/repository", "/activity"],
                },
            ],
            "corpus_kind": "catalog_snapshot",
        }
        cards.append(card)

    cards.sort(key=lambda item: item["identity"]["github_repository_id"])
    validate_cards(cards, manifest, freeze)
    return cards


def validate_cards(cards: list[dict[str, Any]], manifest: dict[str, Any], freeze: dict[str, Any]) -> dict[str, Any]:
    expected = freeze["counts"]
    _require(len(cards) == expected["repositories"] == 2500, "card count mismatch")
    ids = [card["identity"]["github_repository_id"] for card in cards]
    _require(all(isinstance(item, int) and item > 0 for item in ids), "non-positive numeric identity")
    _require(len(ids) == len(set(ids)), "duplicate numeric identity")
    names = [card["identity"]["full_name"].casefold() for card in cards]
    _require(len(names) == len(set(names)), "duplicate canonical full name")
    catalog_record_ids = [card["identity"]["catalog_record_id"] for card in cards]
    _require(len(catalog_record_ids) == len(set(catalog_record_ids)), "duplicate current catalog lineage")
    all_lineage = [
        item
        for card in cards
        for item in (card["identity"]["catalog_record_id"], *card["identity"]["merged_catalog_record_ids"])
    ]
    _require(len(all_lineage) == len(set(all_lineage)), "duplicate current or merged catalog lineage")
    aliases = [alias.casefold() for card in cards for alias in card["identity"]["full_name_aliases"]]
    _require(len(aliases) == expected["aliases"] == 55, "historical alias count mismatch")
    _require(len(aliases) == len(set(aliases)), "duplicate historical alias")
    _require(not (set(aliases) & set(names)), "historical alias collides with canonical name")
    _require(sum(len(card["classifications"]) for card in cards) == expected["directPlacements"] == 2630,
             "classification placement count mismatch")
    _require(sum(card["catalog"]["membership_cohort"] == "baseline" for card in cards) == 1624,
             "baseline cohort count mismatch")
    _require(sum(card["catalog"]["membership_cohort"] == "cat07a_expansion" for card in cards) == 876,
             "expansion cohort count mismatch")
    status_counts = Counter(card["catalog"]["status"] for card in cards)
    _require(status_counts == Counter({"candidate": 1987, "accepted": 485, "reference": 25, "benchmark": 3}),
             f"catalog status mismatch: {dict(status_counts)}")
    _require(sum(card["classifications"][0]["kind"] == "review_bucket" for card in cards) == 12,
             "review card count mismatch")
    _require(sum(bool(card["descriptions"]["catalog"]) for card in cards) == 1555,
             "catalog-description preservation mismatch")
    for card in cards:
        identity = card["identity"]
        _require(CATALOG_RECORD_ID.fullmatch(identity["catalog_record_id"]) is not None, "invalid card lineage")
        _require(all(CATALOG_RECORD_ID.fullmatch(item) is not None for item in identity["merged_catalog_record_ids"]),
                 "invalid merged lineage")
        _require(sum(item["role"] == "primary" for item in card["classifications"]) == 1,
                 "card must contain exactly one primary classification")
        _require(all(item["kind"] != "container" for item in card["classifications"]),
                 "card contains a direct container classification")
        evidence_ids = {item["evidence_id"] for item in card["evidence"]}
        _require(len(evidence_ids) == len(card["evidence"]), "duplicate evidence ID")
        _require(all(set(item["evidence_refs"]) <= evidence_ids for item in card["repository"]["stack"]),
                 "unresolved stack evidence")
        activity = card["activity"]
        non_null_activity = {key for key in (
            "created_at", "repository_updated_at", "pushed_at", "last_commit_at",
            "last_release_at", "last_synced_at", "observed_at") if activity[key] is not None}
        observed_fields = [item["field"] for item in activity["observations"]]
        _require(Counter(observed_fields) == Counter(non_null_activity), "activity observation coverage mismatch")
        _require(all(set(item["evidence_refs"]) <= evidence_ids for item in activity["observations"]),
                 "unresolved activity evidence")
        if activity["last_commit_at"] is None:
            _require(activity["last_commit_sha"] is None and activity["last_commit_branch"] is None,
                     "commit identity without verified commit time")
        else:
            _require(bool(re.fullmatch(r"[a-f0-9]{40}", activity["last_commit_sha"] or "")) and
                     activity["last_commit_branch"] is not None,
                     "verified commit time lacks SHA or branch")
        _require(len(canonical_bytes(card)) <= 24576, f"card byte limit exceeded: {identity['full_name']}")
    return {
        "cards": len(cards),
        "aliases": len(aliases),
        "placements": sum(len(card["classifications"]) for card in cards),
        "baseline": 1624,
        "cat07a_expansion": 876,
        "review_cards": 12,
        "catalog_descriptions": 1555,
        "merged_lineage_ids": len(all_lineage) - len(cards),
        "rejections": 0,
    }


def build_snapshot() -> tuple[dict[str, Any], dict[str, Any]]:
    manifest, taxonomy, freeze = validate_frozen_inputs()
    cards = build_cards(manifest, taxonomy, freeze)
    report = validate_cards(cards, manifest, freeze)
    payload = {
        "schema_version": CARD_SCHEMA_VERSION,
        "activity_schema_version": ACTIVITY_SCHEMA_VERSION,
        "catalog_snapshot_id": freeze["snapshotId"],
        "source_snapshot_date": manifest["snapshot"],
        "source_sha256": freeze["cp06Handoff"]["requiredSourceSha256"],
        "taxonomy_sha256": freeze["cp06Handoff"]["requiredTaxonomySha256"],
        "field_contract_sha256": freeze["cp06Handoff"]["requiredFieldContractSha256"],
        "builder_version": BUILDER_VERSION,
        "corpus_kind": "catalog_snapshot",
        "cards": cards,
    }
    return payload, report


def write_snapshot(payload: dict[str, Any], output: Path = OUTPUT) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_bytes(payload))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare an in-memory rebuild with the checked-in snapshot")
    args = parser.parse_args(argv)
    payload, report = build_snapshot()
    encoded = canonical_bytes(payload)
    if args.check:
        _require(OUTPUT.exists(), f"missing generated asset: {OUTPUT.relative_to(ROOT)}")
        _require(OUTPUT.read_bytes() == encoded, "catalog.snapshot.json differs from deterministic rebuild")
        mode = "checked"
    else:
        write_snapshot(payload)
        mode = "written"
    print(json.dumps({
        "status": "ok",
        "mode": mode,
        "output": str(OUTPUT.relative_to(ROOT)),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "bytes": len(encoded),
        **report,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PluginCatalogBuildError as error:
        print(f"CP-06 catalog build failed: {error}", file=sys.stderr)
        raise SystemExit(1)
