"""Expand the CAT-07 inclusion candidate without touching canonical catalog files.

CP-03.CAT-07A keeps discovery, live evidence, classification, accepted additions,
rejections and overflow in a resumable ignored checkpoint.  GitHub CLI remains the
credential owner; this script only issues bounded public GET requests through the
existing reviewed transport.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.parse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import enrich_catalog as e
import reconcile_catalog_eligibility as cat07
from github_cli_transport import GitHubCLITransport

ROOT = Path(__file__).resolve().parents[1]
MINIMUM_STARS = 500
QUERY_SCHEMA = "catalog-expansion-query-map.v1"
RUN_SCHEMA = "catalog-expansion-run.v1"
CORE_SCHEMA = "catalog-expansion-core-card.v1"
POLICY_PATH = ROOT / "specs" / "catalog" / "catalog-expansion-policy.json"
EXPANSION_POLICY = e.load(POLICY_PATH)
CORE_FACTUAL_FIELDS = tuple(EXPANSION_POLICY["core_factual_fields"])
ALLOWED_OBSERVATION_GAPS = {"source_absent", "source_unsupported"}
RECOMMENDATION_FIELDS = {
    "reviewStatus",
    "recommendation.whyRecommended",
    "recommendation.bestFor",
    "recommendation.tradeoffs",
    "recommendation.adoption_status",
}
HARD_GATE_FIELDS = {
    "githubRepositoryId", "fullName", "url", "visibility", "archived",
    "stars", "primaryCategory", "provenance",
}
GENERIC_TERMS = {
    "ai", "and", "app", "apps", "application", "applications", "code",
    "data", "developer", "development", "framework", "frameworks", "general",
    "infrastructure", "management", "open", "platform", "platforms", "service",
    "services", "software", "system", "systems", "tool", "tooling", "tools",
    "utilities", "utility", "with", "workflow", "workflows",
}
GENERIC_TOPICS = {
    "ai", "api", "app", "awesome", "awesome-list", "cli", "cloud", "database",
    "developer-tools", "docker", "framework", "github", "hacktoberfest", "javascript",
    "library", "linux", "machine-learning", "open-source", "python", "react", "self-hosted",
    "startup", "tool", "tools", "typescript", "web",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_name(value):
    return value.strip().casefold().rstrip("/") if isinstance(value, str) else None


def positive_id(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, str) and value.isascii() and value.isdecimal() and int(value) > 0:
        return int(value)
    return None


def words(value):
    return [x for x in re.findall(r"[a-z0-9]+", (value or "").casefold()) if len(x) >= 3]


def distinctive_terms(category_id, label, description):
    ordered = []
    for token in words(category_id.replace("_", " ")) + words(label) + words(description):
        if token not in GENERIC_TERMS and token not in ordered:
            ordered.append(token)
    return ordered[:12]


def query_phrases(category_id, label, description):
    segments = [part.strip() for part in re.split(r"[&/,]", label or "") if part.strip()]
    candidates = []
    for segment in segments:
        selected = [x for x in words(segment) if x not in GENERIC_TERMS]
        if selected:
            candidates.append(" ".join(selected[:3]))
    desc_first = re.split(r"[.,;]", description or "", maxsplit=1)[0]
    selected = [x for x in words(desc_first) if x not in GENERIC_TERMS]
    if selected:
        candidates.append(" ".join(selected[:3]))
    key_selected = [x for x in words(category_id.replace("_", " ")) if x not in GENERIC_TERMS]
    if key_selected:
        candidates.append(" ".join(key_selected[:3]))
    unique = []
    for value in candidates:
        if value and value not in unique:
            unique.append(value)
    if not unique:
        unique = [category_id.replace("_", " ")]
    return unique[:3]


def topic_terms_by_category(source_repositories, route_terms):
    leaf_ids = set(route_terms)
    counts = {category: Counter() for category in leaf_ids}
    topic_categories = defaultdict(set)
    for row in source_repositories or []:
        categories = [row.get("primaryCategory"), *row.get("secondaryCategories", [])]
        topics = {
            topic.casefold() for topic in row.get("topics", [])
            if isinstance(topic, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,49}", topic.casefold())
            and topic.casefold() not in GENERIC_TOPICS
        }
        for category in categories:
            if category not in counts:
                continue
            counts[category].update(topics)
            for topic in topics:
                topic_categories[topic].add(category)
    result = {}
    for category, values in counts.items():
        ranked = sorted(
            values,
            key=lambda topic: (-values[topic] / max(1, len(topic_categories[topic])), -values[topic], len(topic_categories[topic]), topic),
        )
        bound = [
            topic for topic in ranked
            if set(topic.replace("-", " ").split()) & set(route_terms[category])
        ]
        result[category] = bound[:3]
    return result


def build_query_map(
    taxonomy, manifest_categories, leaf_counts, base_included, target_included,
    source_repositories=None, zero_leaf_topic_seeds=None,
):
    leaves = {item["id"]: item for item in taxonomy["categories"] if item["kind"] == "category"}
    definitions = {item["key"]: item for item in manifest_categories if item.get("kind") == "category"}
    if set(leaves) != set(definitions):
        missing = sorted(set(leaves) - set(definitions))
        extra = sorted(set(definitions) - set(leaves))
        raise ValueError(f"Taxonomy/manifest thematic leaf mismatch: missing={missing}, extra={extra}")
    if target_included <= base_included:
        raise ValueError("Expansion target must exceed the CAT-07 included count")
    route_terms = {
        category_id: distinctive_terms(
            category_id, definitions[category_id].get("title") or node["label"],
            definitions[category_id].get("description") or "",
        )
        for category_id, node in leaves.items()
    }
    topic_map = topic_terms_by_category(source_repositories, route_terms)
    seed_policy = (
        EXPANSION_POLICY["discovery"].get("zero_leaf_name_bound_topic_seeds", {})
        if zero_leaf_topic_seeds is None else zero_leaf_topic_seeds
    )
    for category_id, seeds in seed_policy.items():
        if category_id not in leaves:
            raise ValueError(f"Unknown zero-leaf topic seed category: {category_id}")
        if int(leaf_counts.get(category_id, 0)) != 0 or topic_map[category_id]:
            continue
        validated = []
        for seed in seeds:
            normalized = seed.casefold() if isinstance(seed, str) else ""
            if (
                not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,49}", normalized)
                or normalized in GENERIC_TOPICS
                or normalized not in route_terms[category_id]
            ):
                raise ValueError(f"Unsafe zero-leaf topic seed for {category_id}: {seed!r}")
            if normalized not in validated:
                validated.append(normalized)
        topic_map[category_id] = validated[:3]
    routes = []
    for category_id, node in leaves.items():
        definition = definitions[category_id]
        count = int(leaf_counts.get(category_id, 0))
        phrases = query_phrases(category_id, definition.get("title") or node["label"], definition.get("description") or "")
        queries = []
        for index, topic in enumerate(topic_map[category_id], 1):
            seeded_zero_leaf_topic = topic in seed_policy.get(category_id, []) and count == 0
            if seeded_zero_leaf_topic:
                qualifier = (
                    f'topic:{topic} "{topic}" in:name '
                    f'is:public archived:false fork:false stars:>={MINIMUM_STARS}'
                )
            else:
                qualifier = f"topic:{topic} is:public archived:false fork:false stars:>={MINIMUM_STARS}"
            queries.append({
                "queryId": f"{category_id}:t{index}", "query": qualifier, "routeType": "category_topic",
                "topic": topic, "metadataBound": seeded_zero_leaf_topic,
                "perPage": 30, "maxPages": 3, "sort": "stars", "order": "desc",
            })
        for index, phrase in enumerate(phrases[:2], 1):
            qualifier = f'"{phrase}" in:name,description,readme is:public archived:false fork:false stars:>={MINIMUM_STARS}'
            queries.append({
                "queryId": f"{category_id}:x{index}", "query": qualifier, "routeType": "text_discovery_only",
                "perPage": 30, "maxPages": 3, "sort": "stars", "order": "desc",
            })
        routes.append({
            "categoryId": category_id,
            "label": definition.get("title") or node["label"],
            "description": definition.get("description") or "",
            "currentIncludedCount": count,
            "softFloorDeficit": max(0, 10 - count),
            "priorityTier": 0 if category_id == "embeddings_reranking" else 1 if count < 10 else 2,
            "positiveTerms": route_terms[category_id],
            "topicTerms": topic_map[category_id],
            "sourceMappings": ["github_rest_search"],
            "queries": queries,
            "stopConditions": {
                "acceptedCounter": target_included - base_included,
                "maxPagesPerQuery": 3,
                "maxItemsPerPage": 30,
                "noAggregatorAcceptance": True,
            },
        })
    routes.sort(key=lambda row: (row["priorityTier"], row["currentIncludedCount"], row["categoryId"]))
    return {
        "schemaVersion": QUERY_SCHEMA,
        "generation": "semantically_bound_topics_with_name_bound_zero_leaf_seeds_v7",
        "createdAt": utc_now(),
        "sourceAttribution": {
            "taxonomy": "frozen CAT-07 taxonomy projection",
            "categoryDefinitions": "canonical manifest category labels/descriptions",
            "acceptanceEvidence": "current GitHub REST metadata and bounded source endpoints",
        },
        "baseIncluded": base_included,
        "targetIncluded": target_included,
        "requiredAdditions": target_included - base_included,
        "leadPlanningRange": {"minimum": 1100, "maximum": 1300},
        "routes": routes,
    }


@dataclass
class IdentityRegistry:
    ids: set[int] = field(default_factory=set)
    names: set[str] = field(default_factory=set)
    aliases: set[str] = field(default_factory=set)
    urls: set[str] = field(default_factory=set)

    def add(self, repository_id=None, full_name=None, aliases=(), url=None):
        repository_id = positive_id(repository_id)
        if repository_id is not None:
            self.ids.add(repository_id)
        name = canonical_name(full_name)
        if name:
            self.names.add(name)
        for value in aliases or ():
            alias = canonical_name(value)
            if alias:
                self.aliases.add(alias)

        normalized_url = canonical_name(url)
        if normalized_url:
            self.urls.add(normalized_url)

    def duplicate_reason(self, repository_id, full_name, url=None):
        repository_id = positive_id(repository_id)
        name = canonical_name(full_name)
        if repository_id is not None and repository_id in self.ids:
            return "duplicate_numeric_id"
        if name and (name in self.names or name in self.aliases):
            return "duplicate_name_or_alias"
        normalized_url = canonical_name(url)
        if normalized_url and normalized_url in self.urls:
            return "duplicate_url"
        return None


def classify_metadata(metadata, route, registry, extra_text=""):
    reasons = []
    if metadata.get("private") is not False or metadata.get("visibility") != "public":
        reasons.append("not_public")
    if metadata.get("archived") is not False:
        reasons.append("archived")
    repository_id = positive_id(metadata.get("id"))
    if repository_id is None:
        reasons.append("invalid_numeric_id")
    full_name = metadata.get("full_name")
    if not isinstance(full_name, str) or not e.NAME.fullmatch(full_name):
        reasons.append("invalid_canonical_name")
    stars = metadata.get("stargazers_count")
    if not isinstance(stars, int) or isinstance(stars, bool):
        reasons.append("stars_unresolved")
    elif stars < MINIMUM_STARS:
        reasons.append("below_minimum_stars")
    expected_url = "https://github.com/" + full_name if isinstance(full_name, str) else None
    if not isinstance(metadata.get("html_url"), str) or canonical_name(metadata.get("html_url")) != canonical_name(expected_url):
        reasons.append("invalid_canonical_url")
    duplicate = registry.duplicate_reason(repository_id, full_name, metadata.get("html_url"))
    if duplicate:
        reasons.append(duplicate)
    if reasons:
        return {"eligible": False, "status": "rejected_hard_gate", "reasons": sorted(set(reasons)), "matchedTerms": []}
    summary = " ".join([full_name or "", metadata.get("description") or "", " ".join(metadata.get("topics") or [])]).casefold()
    list_like = (
        re.search(r"(?:^|[/_-])awesome(?:[-_/]|$)", (full_name or "").casefold()) is not None
        or bool({"awesome", "awesome-list"} & {topic.casefold() for topic in metadata.get("topics") or [] if isinstance(topic, str)})
        or re.search(r"(?:^|\b)(?:awesome(?:-| )list|list of|collection of (?:links|resources)|curated list)(?:\b|$)", summary) is not None
    )
    if list_like and route["categoryId"] != "learning_reference_resources":
        return {"eligible": False, "status": "rejected_non_product_list", "reasons": ["curated_or_resource_list"], "matchedTerms": []}
    metadata_haystack = " ".join([full_name or "", metadata.get("description") or "", " ".join(metadata.get("topics") or [])]).casefold()
    readme_haystack = (extra_text or "").casefold()
    matched = sorted(term for term in route.get("positiveTerms", []) if re.search(rf"\b{re.escape(term)}\b", metadata_haystack))
    readme_matched = sorted(term for term in route.get("positiveTerms", []) if term not in matched and re.search(rf"\b{re.escape(term)}\b", readme_haystack))
    observed_topics = {topic.casefold() for topic in metadata.get("topics") or [] if isinstance(topic, str)}
    matched_topics = sorted(observed_topics & set(route.get("topicTerms", [])))
    matched_non_topic = sorted(term for term in matched if term not in matched_topics)
    if not matched_topics and len(matched) < 2:
        return {
            "eligible": False, "status": "semantic_review_required",
            "reasons": ["insufficient_metadata_route_evidence"], "matchedTerms": matched,
            "matchedNonTopicTerms": matched_non_topic, "readmeMatchedTerms": readme_matched, "matchedTopics": matched_topics,
        }
    return {
        "eligible": True, "status": "eligible_evidence_backed_classification", "reasons": [],
        "matchedTerms": matched, "matchedNonTopicTerms": matched_non_topic,
        "readmeMatchedTerms": readme_matched, "matchedTopics": matched_topics,
        "matchStrength": 100 * len(matched_topics) + len(matched), "categoryId": route["categoryId"],
    }


def observation(status, observed_at=None, url=None, evidence_refs=None, reason=None):
    result = {"status": status}
    if observed_at:
        result["observedAt"] = observed_at
    if url:
        result["url"] = url
    if evidence_refs:
        result["evidenceRefs"] = list(evidence_refs)
    if reason:
        result["reason"] = reason
    return result


def path_value(value, dotted):
    current = value
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def build_core_card(metadata, route, observations, discovery_refs):
    meta_obs = observations.get("metadata", {})
    if meta_obs.get("status") != "observed":
        raise ValueError("Core card requires current observed metadata")
    languages_obs = observations.get("languages", {})
    head_obs = observations.get("head_commit", {})
    release_obs = observations.get("release", {})
    allowed = {"observed"} | ALLOWED_OBSERVATION_GAPS
    if languages_obs.get("status") not in allowed or head_obs.get("status") not in allowed or release_obs.get("status") not in allowed:
        raise ValueError("Core factual endpoint is unresolved or retryable")
    license_data = metadata.get("license") or {}
    language = metadata.get("language")
    languages = languages_obs.get("data") if languages_obs.get("status") == "observed" else None
    commit = head_obs.get("data") if head_obs.get("status") == "observed" else {}
    release = release_obs.get("data") if release_obs.get("status") == "observed" else {}
    description = metadata.get("description") if isinstance(metadata.get("description"), str) and metadata.get("description").strip() else None
    stack = [{"technology": language, "evidenceRefs": ["metadata", "languages"]}] if language else []
    provenance = {
        "scope": "cat07a_public_core_facts_not_canonical_catalog",
        "apiVersion": e.API_VERSION,
        "discoveryRefs": list(discovery_refs),
        "metadata": {k: meta_obs.get(k) for k in ("status", "observedAt", "url") if meta_obs.get(k) is not None},
        "languages": {k: languages_obs.get(k) for k in ("status", "observedAt", "url", "reason") if languages_obs.get(k) is not None},
        "headCommit": {k: head_obs.get(k) for k in ("status", "observedAt", "url", "reason") if head_obs.get(k) is not None},
        "release": {k: release_obs.get(k) for k in ("status", "observedAt", "url", "reason") if release_obs.get(k) is not None},
    }
    card = {
        "schemaVersion": CORE_SCHEMA,
        "sourceId": f"gh-expansion:{metadata['id']}",
        "id": f"gh-expansion:{metadata['id']}",
        "sourceRecordIds": [f"gh-expansion:{metadata['id']}"],
        "githubRepositoryId": metadata["id"],
        "fullName": metadata["full_name"],
        "url": metadata["html_url"],
        "aliases": [],
        "identityStatus": "resolved",
        "availability": "available",
        "visibility": metadata["visibility"],
        "archived": metadata["archived"],
        "disabled": metadata.get("disabled"),
        "stars": metadata["stargazers_count"],
        "forks": metadata.get("forks_count"),
        "watchers": metadata.get("subscribers_count"),
        "sizeKb": metadata.get("size"),
        "isFork": metadata.get("fork"),
        "defaultBranch": metadata.get("default_branch"),
        "language": language,
        "languages": languages,
        "topics": metadata.get("topics") or [],
        "homepage": metadata.get("homepage"),
        "license": {
            "spdx": license_data.get("spdx_id"), "name": license_data.get("name"),
            "source": license_data.get("url"), "confidence": "source_reported" if license_data.get("spdx_id") else None,
        },
        "catalogDescription": description,
        "descriptionOrigin": "upstream" if description else None,
        "stack": stack,
        "activity": {
            "createdAt": metadata.get("created_at"), "updatedAt": metadata.get("updated_at"),
            "pushedAt": metadata.get("pushed_at"), "lastCommitAt": commit.get("date"),
            "lastCommitSha": commit.get("sha"), "lastCommitBranch": commit.get("branch"),
            "lastReleaseAt": release.get("publishedAt"), "observedAt": meta_obs.get("observedAt"),
            "status": "metadata_and_bounded_sources_observed",
        },
        "catalogStatus": "candidate",
        "reviewStatus": "cat07a_evidence_backed_classification",
        "primaryCategory": route["categoryId"],
        "secondaryCategories": [],
        "provenance": provenance,
        "recommendationStatus": "downstream_backlog_not_inclusion_gate",
    }
    hard_valid = (
        positive_id(card["githubRepositoryId"]) is not None
        and e.NAME.fullmatch(card["fullName"]) is not None
        and card["url"].casefold() == ("https://github.com/" + card["fullName"]).casefold()
        and card["visibility"] == "public" and card["archived"] is False
        and isinstance(card["stars"], int) and not isinstance(card["stars"], bool) and card["stars"] >= MINIMUM_STARS
        and bool(card["primaryCategory"]) and bool(card["provenance"])
    )
    card["eligibility"] = {
        "dataGatePassed": hard_valid, "reasons": [] if hard_valid else ["hard_eligibility_gate_failed"],
        "minimumStars": MINIMUM_STARS, "catalogAcceptanceChanged": False, "globalCAT07AApplied": False,
    }
    endpoint_fields = {
        "languages": (languages_obs, ["languages"]),
        "activity.lastCommitAt": (head_obs, ["head_commit"]),
        "activity.lastCommitSha": (head_obs, ["head_commit"]),
        "activity.lastCommitBranch": (head_obs, ["head_commit"]),
        "activity.lastReleaseAt": (release_obs, ["release"]),
    }
    derived_fields = {
        "id", "sourceRecordIds", "aliases", "identityStatus", "availability", "stack",
        "catalogDescription", "descriptionOrigin", "activity.status", "catalogStatus",
        "primaryCategory", "secondaryCategories", "evidenceCompleteness", "eligibility", "provenance",
    }
    field_observations = {}
    for field_name in CORE_FACTUAL_FIELDS:
        if field_name in endpoint_fields:
            source_observation, refs = endpoint_fields[field_name]
            status = source_observation["status"]
            field_observations[field_name] = observation(
                status, source_observation.get("observedAt"), source_observation.get("url"), refs,
                source_observation.get("reason"),
            )
            continue
        value = path_value(card, field_name)
        if field_name in derived_fields:
            status = "derived_reviewed" if value not in (None, "") and not (field_name in {"stack", "catalogDescription", "descriptionOrigin"} and not value) else "source_absent"
            refs = list(discovery_refs) + ["metadata"] if field_name in {"primaryCategory", "provenance"} else ["metadata"]
        else:
            status = "observed" if value is not None else "source_absent"
            refs = ["metadata"]
        field_observations[field_name] = observation(status, meta_obs.get("observedAt"), meta_obs.get("url"), refs)
    terminal = set(EXPANSION_POLICY["terminal_observation_states"])
    unsupported = sorted(key for key, item in field_observations.items() if item["status"] in ALLOWED_OBSERVATION_GAPS)
    hard_unsupported = sorted(set(unsupported) & set(EXPANSION_POLICY["hard_fields_never_source_unsupported"]))
    card["evidenceCompleteness"] = round(100 * sum(item["status"] in terminal for item in field_observations.values()) / len(CORE_FACTUAL_FIELDS), 2)
    field_observations["evidenceCompleteness"] = observation("derived_reviewed", meta_obs.get("observedAt"), evidence_refs=["fieldObservations"])
    card["fieldObservations"] = field_observations
    card["coreFieldGatePassed"] = hard_valid and not hard_unsupported and set(field_observations) == set(CORE_FACTUAL_FIELDS) and all(
        item.get("status") in terminal for item in field_observations.values()
    )
    card["coreUnsupportedFields"] = unsupported
    return card


def freeze_exact_target(cards, base_included, target_included, base_leaf_counts=None):
    required = target_included - base_included
    if required < 1:
        raise ValueError("Exact target must exceed base included count")
    ordered = sorted(cards, key=lambda row: (row.get("selectionKey", [10**12]), row.get("qualifiedSequence", 10**12), row["fullName"].casefold()))
    ids, names = set(), set()
    for card in ordered:
        repository_id = positive_id(card.get("githubRepositoryId"))
        if repository_id in ids:
            raise ValueError("duplicate numeric candidate identity")
        name = canonical_name(card.get("fullName"))
        if name in names:
            raise ValueError("duplicate candidate name or alias")
        ids.add(repository_id)
        names.add(name)
        if not card.get("coreFieldGatePassed"):
            raise ValueError("Candidate without the CAT-07A core field gate cannot be frozen")
    if len(ordered) < required:
        raise ValueError(f"Exact target not reached: need {required}, have {len(ordered)}")
    if base_leaf_counts is None:
        accepted = ordered[:required]
    else:
        by_category = defaultdict(list)
        for card in ordered:
            by_category[card["primaryCategory"]].append(card)
        accepted = []
        selected_ids = set()
        coverage_order = sorted(
            base_leaf_counts,
            key=lambda category: (0 if category == "embeddings_reranking" else 1, base_leaf_counts[category], category),
        )
        for category in coverage_order:
            deficit = max(0, 10 - int(base_leaf_counts[category]))
            for card in by_category.get(category, [])[:deficit]:
                if len(accepted) >= required:
                    break
                accepted.append(card)
                selected_ids.add(card["githubRepositoryId"])
        remaining = {
            category: [card for card in rows if card["githubRepositoryId"] not in selected_ids]
            for category, rows in by_category.items()
        }
        categories = sorted(remaining)
        while len(accepted) < required and any(remaining.values()):
            for category in categories:
                if len(accepted) >= required:
                    break
                if remaining[category]:
                    card = remaining[category].pop(0)
                    accepted.append(card)
                    selected_ids.add(card["githubRepositoryId"])
        if len(accepted) != required:
            raise ValueError("Category-balanced selection could not reach the exact target")
    accepted_ids = {card["githubRepositoryId"] for card in accepted}
    overflow = [card for card in ordered if card["githubRepositoryId"] not in accepted_ids]
    return {
        "baseIncluded": base_included, "targetIncluded": target_included,
        "requiredAdditions": required, "acceptedAdditions": accepted,
        "qualifiedOverflow": overflow, "finalIncluded": base_included + len(accepted),
    }


def expanded_category_counts(taxonomy, base_source, base_roots, base_aliases, accepted):
    combined = dict(base_source)
    roots = set(base_roots)
    for card in accepted:
        source_id = card["sourceId"]
        if source_id in combined or source_id in roots or source_id in base_aliases:
            raise ValueError(f"Expansion source identity collides with CAT-07 membership: {source_id}")
        combined[source_id] = {
            "primaryCategory": card["primaryCategory"],
            "secondaryCategories": card["secondaryCategories"],
        }
        roots.add(source_id)
    return cat07.category_counts(taxonomy, combined, roots, dict(base_aliases))


def base_registry(base_run):
    registry = IdentityRegistry()
    source = e.load(base_run / "input.json")
    for row in source["repositories"]:
        registry.add(row.get("githubRepositoryId"), row.get("fullName"), row.get("aliases", []), row.get("url"))
    records = base_run / "records"
    if records.exists():
        for path in records.glob("*.json"):
            record = e.load(path)
            values = record.get("values", {})
            registry.add(values.get("githubRepositoryId"), values.get("fullName"), values.get("aliases", []), values.get("url"))
    resolution = base_run / "eligibility-reconciliation" / "identity-resolution.json"
    if resolution.exists():
        for item in e.load(resolution).get("items", {}).values():
            values = item.get("values", {})
            registry.add(values.get("githubRepositoryId"), values.get("fullName"), values.get("aliases", []), values.get("url"))
    return registry


def leaf_count_map(base_run):
    counts = e.load(base_run / "eligibility-reconciliation" / "category-counts.json")["thematicLeafCounts"]
    return {key: value["repositoryCount"] for key, value in counts.items()}


def eligible_topic_rows(base_run, summary):
    included = set(summary["catalogIncludedSourceIds"])
    rows = []
    for row in e.load(base_run / "input.json")["repositories"]:
        if row["id"] not in included:
            continue
        merged = dict(row)
        record_path = base_run / "records" / (hashlib.sha256(row["id"].encode()).hexdigest() + ".json")
        if record_path.exists():
            values = e.load(record_path).get("values", {})
            if isinstance(values.get("topics"), list):
                merged["topics"] = values["topics"]
        rows.append(merged)
    return rows


def prepare(run, base_run, target_included=2500):
    if run.exists():
        raise ValueError("Expansion run already exists; resume it instead of replacing state")
    summary_path = base_run / "eligibility-reconciliation" / "summary.json"
    summary = e.load(summary_path)
    policy = e.load(POLICY_PATH)
    base_included = summary.get("catalogIncludedRepositories")
    if base_included != 1624 or summary.get("duplicateCanonicalIdentities") != 0:
        raise ValueError("CAT-07 exact completed baseline is required")
    if not summary.get("canonicalManifestUnchanged") or not summary.get("canonicalHtmlUnchanged"):
        raise ValueError("CAT-07 must preserve canonical manifest and HTML")
    taxonomy = e.load(base_run / "taxonomy.json")
    manifest = e.load(ROOT / "data" / "catalog_manifest.json")
    base_rows = eligible_topic_rows(base_run, summary)
    query_map = build_query_map(
        taxonomy, manifest["categories"], leaf_count_map(base_run), base_included, target_included, base_rows,
    )
    expected = policy["baseline"]
    if (
        expected["included_distinct_identities"] != base_included
        or expected["target_included_distinct_identities"] != target_included
        or expected["required_net_additions"] != target_included - base_included
        or expected["thematic_leaves"] != len(query_map["routes"])
        or policy["selection"]["expected_soft_floor_capacity"] != sum(route["softFloorDeficit"] for route in query_map["routes"])
    ):
        raise ValueError("CAT-07A expansion policy does not match the frozen baseline/target")
    run.mkdir(parents=True, exist_ok=False)
    transport_run = run / "transport"
    transport_plan = e.create_plan(
        transport_run, base_run / "input.json", base_run / "taxonomy.json",
        base_run / "field-contract.json", max_requests=12000, max_repos=1800,
    )
    transport_plan.update({
        "maxBytes": 96_000_000,
        "maxResponseBytes": 1_000_000,
        "maxSecondsPerInvocation": 55,
        "scope": "cat07a_public_GET_search_and_core_facts_no_canonical_write",
    })
    e.atomic_json(transport_run / "plan.json", transport_plan)
    plan = {
        "schemaVersion": RUN_SCHEMA,
        "createdAt": utc_now(),
        "baseRun": str(base_run.resolve()),
        "baseSummarySha256": e.sha(summary_path),
        "baseIncluded": base_included,
        "targetIncluded": target_included,
        "requiredAdditions": target_included - base_included,
        "scriptSha256": e.sha(__file__),
        "queryMapSha256": None,
        "taxonomySha256": e.sha(base_run / "taxonomy.json"),
        "fieldContractSha256": e.sha(base_run / "field-contract.json"),
        "expansionPolicyOrigin": str(POLICY_PATH.resolve()),
        "expansionPolicySha256": e.sha(POLICY_PATH),
        "canonicalManifestSha256": e.sha(ROOT / "data" / "catalog_manifest.json"),
        "canonicalHtmlSha256": e.sha(ROOT / "docs" / "UNIFIED_CATALOG.html"),
        "leadPlanningRange": query_map["leadPlanningRange"],
        "qualifiedOverflowTarget": 25,
        "canonicalWritten": False,
    }
    e.atomic_json(run / "query-map.json", query_map)
    plan["queryMapSha256"] = e.sha(run / "query-map.json")
    e.atomic_json(run / "plan.json", plan)
    e.atomic_json(run / "state.json", {
        "queries": {}, "leads": {}, "qualifiedCards": {}, "decisions": {},
        "qualifiedSequence": 0, "createdAt": utc_now(), "updatedAt": utc_now(),
    })
    return {
        "routes": len(query_map["routes"]), "baseIncluded": base_included,
        "requiredAdditions": target_included - base_included,
        "networkPerformed": False, "canonicalWritten": False,
    }


class ExpansionPipeline:
    def __init__(self, run, transport=None):
        self.run = Path(run)
        self.plan = e.load(self.run / "plan.json")
        if self.plan["scriptSha256"] != e.sha(__file__):
            raise ValueError("CAT-07A script changed; explicit migration or a new run is required")
        if self.plan["queryMapSha256"] != e.sha(self.run / "query-map.json"):
            raise ValueError("CAT-07A query map changed")
        if e.sha(self.plan["expansionPolicyOrigin"]) != self.plan["expansionPolicySha256"]:
            raise ValueError("CAT-07A expansion policy changed; explicit migration or new run required")
        self.query_map = e.load(self.run / "query-map.json")
        self.routes = {row["categoryId"]: row for row in self.query_map["routes"]}
        self.state = e.load(self.run / "state.json")
        self.collector = e.Collector(self.run / "transport", transport or GitHubCLITransport())
        self.base_run = Path(self.plan["baseRun"])
        self.registry = base_registry(self.base_run)
        for card in self.state["qualifiedCards"].values():
            self.registry.add(card.get("githubRepositoryId"), card.get("fullName"), card.get("aliases", []), card.get("url"))

    def save(self):
        self.state["updatedAt"] = utc_now()
        e.atomic_json(self.run / "state.json", self.state)

    def assert_canonical_unchanged(self):
        if e.sha(ROOT / "data" / "catalog_manifest.json") != self.plan["canonicalManifestSha256"]:
            raise ValueError("Canonical manifest changed during CAT-07A")
        if e.sha(ROOT / "docs" / "UNIFIED_CATALOG.html") != self.plan["canonicalHtmlSha256"]:
            raise ValueError("Canonical HTML changed during CAT-07A")

    def preflight(self):
        response = self.collector.request(e.API + "/rate_limit")
        resources = response.get("data", {}).get("resources", {})
        core = resources.get("core", {})
        search = resources.get("search", {})
        if response.get("status") != "observed" or core.get("limit", 0) <= 60:
            raise RuntimeError("Authenticated GitHub quota was not confirmed")
        result = {
            "observedAt": response["observedAt"], "transport": "official_github_cli",
            "core": core, "search": search, "tokenPersisted": False,
        }
        e.atomic_json(self.run / "auth-preflight.json", result)
        return result

    def route_order(self):
        counts = Counter(card["primaryCategory"] for card in self.state["qualifiedCards"].values())
        return sorted(
            self.query_map["routes"],
            key=lambda row: (
                0 if row["categoryId"] == "embeddings_reranking" and row["currentIncludedCount"] + counts[row["categoryId"]] == 0 else
                1 if row["currentIncludedCount"] + counts[row["categoryId"]] < 10 else 2,
                row["currentIncludedCount"] + counts[row["categoryId"]], row["categoryId"],
            ),
        )

    def has_coverage_hole(self):
        counts = Counter(card["primaryCategory"] for card in self.state["qualifiedCards"].values())
        return any(
            route["currentIncludedCount"] + counts[route["categoryId"]] == 0
            for route in self.query_map["routes"]
        )

    def discover(self, max_search_requests=30):
        self.assert_canonical_unchanged()
        preflight = self.preflight()
        before = self.collector.state["requests"]
        attempted = 0
        base = base_registry(self.base_run)
        for route in self.route_order():
            if (
                len(self.state["qualifiedCards"]) >= self.plan["requiredAdditions"]
                and not self.has_coverage_hole()
            ):
                self.save()
                return self.progress({"searchRequestsThisInvocation": attempted, "preflight": preflight, "stopReason": "accepted_identity_counter_reached"})
            for query_order, query in enumerate(route["queries"], 1):
                for page in range(1, query["maxPages"] + 1):
                    if attempted >= max_search_requests or self.collector.state.get("haltReason") or time.time() < self.collector.state["retryNotBefore"]:
                        self.save()
                        return self.progress({"searchRequestsThisInvocation": attempted, "preflight": preflight})
                    progress_id = f'{query["queryId"]}:p{page}'
                    if self.state["queries"].get(progress_id, {}).get("status") == "observed":
                        continue
                    url = e.API + "/search/repositories?" + urllib.parse.urlencode({
                        "q": query["query"], "sort": query["sort"], "order": query["order"],
                        "per_page": query["perPage"], "page": page,
                    })
                    response = self.collector.request(url)
                    attempted = self.collector.state["requests"] - before
                    query_result = {
                        "queryId": query["queryId"], "categoryId": route["categoryId"], "page": page,
                        "status": response["status"], "observedAt": response.get("observedAt"), "url": url,
                        "incompleteResults": response.get("data", {}).get("incomplete_results"),
                        "resultCount": len(response.get("data", {}).get("items", [])),
                    }
                    self.state["queries"][progress_id] = query_result
                    if response["status"] != "observed":
                        self.save()
                        return self.progress({"searchRequestsThisInvocation": attempted, "preflight": preflight})
                    for rank, item in enumerate(response["data"].get("items", []), 1):
                        repository_id = positive_id(item.get("id"))
                        full_name = item.get("full_name")
                        if repository_id is None or not isinstance(full_name, str) or not e.NAME.fullmatch(full_name):
                            continue
                        key = str(repository_id)
                        lead = self.state["leads"].setdefault(key, {
                            "githubRepositoryId": repository_id, "fullName": full_name,
                            "searchStars": item.get("stargazers_count"), "searchDescription": e.clean_excerpt(item.get("description") or ""),
                            "searchLanguage": item.get("language"), "searchTopics": item.get("topics") or [],
                            "discoveryRefs": [], "discoveryOccurrences": [], "categoryHints": [], "status": "discovered_unverified",
                        })
                        if progress_id not in lead["discoveryRefs"]:
                            lead["discoveryRefs"].append(progress_id)
                            lead["discoveryOccurrences"].append({
                                "ref": progress_id, "categoryId": route["categoryId"], "queryId": query["queryId"],
                                "queryOrder": query_order, "routeType": query.get("routeType"),
                                "page": page, "rank": rank, "retrievedAt": response.get("observedAt"),
                                "source": "github_rest_search",
                            })
                        if route["categoryId"] not in lead["categoryHints"]:
                            lead["categoryHints"].append(route["categoryId"])
                        if lead.get("status") == "semantic_review_required" and query.get("routeType") == "category_topic":
                            lead["status"] = "discovered_unverified"
                            lead["reopenedReason"] = "new_category_topic_evidence"
                        duplicate = base.duplicate_reason(repository_id, full_name, item.get("html_url"))
                        if duplicate:
                            lead.update(status="rejected_existing_identity", rejectionReasons=[duplicate])
                    self.save()
        return self.progress({"searchRequestsThisInvocation": attempted, "preflight": preflight})

    def request_block(self, url, projector):
        raw = self.collector.request(url)
        result = {k: raw.get(k) for k in ("status", "observedAt", "url", "reason", "httpStatus") if raw.get(k) is not None}
        if raw.get("status") == "observed":
            try:
                result["data"] = projector(raw.get("data"))
            except (KeyError, TypeError, ValueError, AttributeError):
                result.pop("data", None)
                result.update(status="source_unsupported", reason="invalid_or_unsafe_source_shape")
        return result

    def collect_observations(self, metadata, include_readme=False):
        name = metadata["full_name"]
        base = e.API + "/repos/" + name
        languages = self.request_block(base + "/languages", lambda value: {
            key: amount for key, amount in value.items()
            if isinstance(key, str) and isinstance(amount, int) and not isinstance(amount, bool) and amount >= 0
        })
        branch = metadata.get("default_branch")
        if isinstance(branch, str) and branch:
            encoded = urllib.parse.quote(branch, safe="")
            head = self.request_block(base + "/commits/" + encoded, lambda value: {
                "sha": value["sha"], "date": value["commit"]["committer"]["date"], "branch": branch,
            })
            if head["status"] == "observed":
                sha = head["data"]["sha"]
                if include_readme:
                    query = "?ref=" + urllib.parse.quote(sha, safe="")
                    def readme_projector(value):
                        import base64
                        if value.get("type") != "file" or value.get("encoding") != "base64":
                            raise ValueError("README is not an ordinary base64 file")
                        decoded = base64.b64decode(value["content"]).decode("utf-8")
                        return {"excerpt": e.clean_excerpt(decoded), "sha": value.get("sha"), "ref": sha}
                    readme = self.request_block(base + "/readme" + query, readme_projector)
                else:
                    readme = None
            else:
                readme = None
        else:
            head = {"status": "source_absent", "observedAt": utc_now(), "reason": "default_branch_absent"}
            readme = None
        release = self.request_block(base + "/releases/latest", lambda value: {
            "publishedAt": value.get("published_at"), "tag": value.get("tag_name"),
        })
        return languages, head, release, readme

    def collect(self, max_candidates=25):
        self.assert_canonical_unchanged()
        preflight = self.preflight()
        required = self.plan["requiredAdditions"]
        desired = required + self.plan["qualifiedOverflowTarget"]
        qualified_by_category = Counter(card["primaryCategory"] for card in self.state["qualifiedCards"].values())
        leads = []
        for key, lead in self.state["leads"].items():
            if lead["status"] != "discovered_unverified":
                continue
            candidate_routes = [self.routes[category] for category in lead["categoryHints"]]
            best_route = min(
                candidate_routes,
                key=lambda route: (
                    0 if route["categoryId"] == "embeddings_reranking" and route["currentIncludedCount"] + qualified_by_category[route["categoryId"]] == 0 else
                    1 if route["currentIncludedCount"] + qualified_by_category[route["categoryId"]] < 10 else 2,
                    route["currentIncludedCount"] + qualified_by_category[route["categoryId"]], route["categoryId"],
                ),
            )
            has_topic_evidence = any(item.get("routeType") == "category_topic" for item in lead.get("discoveryOccurrences", []))
            leads.append((best_route, key, lead, has_topic_evidence))
        leads.sort(key=lambda item: (
            0 if item[3] else 1,
            0 if item[0]["categoryId"] == "embeddings_reranking" and item[0]["currentIncludedCount"] + qualified_by_category[item[0]["categoryId"]] == 0 else
            1 if item[0]["currentIncludedCount"] + qualified_by_category[item[0]["categoryId"]] < 10 else 2,
            item[0]["currentIncludedCount"] + qualified_by_category[item[0]["categoryId"]],
            -(item[2].get("searchStars") or 0), item[2]["fullName"].casefold(),
        ))
        attempted = 0
        for route, key, lead, _has_topic_evidence in leads:
            if attempted >= max_candidates or len(self.state["qualifiedCards"]) >= desired:
                break
            if self.collector.state.get("haltReason") or time.time() < self.collector.state["retryNotBefore"]:
                break
            attempted += 1
            meta_url = e.API + "/repositories/" + key
            metadata_obs = self.request_block(meta_url, lambda value: {
                target: value.get(source) for target, source in {
                    "id": "id", "full_name": "full_name", "html_url": "html_url", "private": "private",
                    "visibility": "visibility", "archived": "archived", "disabled": "disabled", "fork": "fork",
                    "stargazers_count": "stargazers_count", "forks_count": "forks_count",
                    "subscribers_count": "subscribers_count", "size": "size", "default_branch": "default_branch",
                    "language": "language", "description": "description", "topics": "topics", "homepage": "homepage",
                    "created_at": "created_at", "updated_at": "updated_at", "pushed_at": "pushed_at", "license": "license",
                }.items()
            })
            if metadata_obs["status"] != "observed":
                lead.update(status="discovered_unverified", lastAttempt={"stage": "metadata", "result": metadata_obs})
                self.save()
                break
            metadata = metadata_obs["data"]
            candidate_routes = sorted(
                (self.routes[category] for category in lead["categoryHints"]),
                key=lambda item: (item["priorityTier"], item["currentIncludedCount"] + qualified_by_category[item["categoryId"]], item["categoryId"]),
            )
            decisions = [(candidate_route, classify_metadata(metadata, candidate_route, self.registry)) for candidate_route in candidate_routes]
            eligible = next(((candidate_route, item) for candidate_route, item in decisions if item["eligible"]), None)
            terminal_rejection = next(((candidate_route, item) for candidate_route, item in decisions if item["status"] != "semantic_review_required"), None)
            if terminal_rejection and terminal_rejection[1]["status"] in {"rejected_hard_gate", "rejected_non_product_list"}:
                route, decision = terminal_rejection
                lead.update(status=decision["status"], rejectionReasons=decision["reasons"], verification=metadata_obs, classification=decision)
                self.save()
                continue
            needs_readme = eligible is None
            languages, head, release, readme = self.collect_observations(metadata, include_readme=needs_readme)
            if eligible is None and readme and readme.get("status") == "observed":
                decisions = [
                    (candidate_route, classify_metadata(metadata, candidate_route, self.registry, readme["data"]["excerpt"]))
                    for candidate_route in candidate_routes
                ]
                eligible = next(((candidate_route, item) for candidate_route, item in decisions if item["eligible"]), None)
            if eligible is None:
                lead.update(
                    status="semantic_review_required", rejectionReasons=["no_persisted_route_evidence"],
                    verification=metadata_obs, classificationAttempts=[item for _, item in decisions],
                    semanticEvidence=readme,
                )
                self.save()
                continue
            route, decision = eligible
            observations = {"metadata": metadata_obs, "languages": languages, "head_commit": head, "release": release}
            if readme is not None:
                observations["readme"] = readme
            try:
                card = build_core_card(metadata, route, observations, lead["discoveryRefs"])
            except ValueError as error:
                lead.update(
                    status="discovered_unverified", lastAttempt={"stage": "core_collection", "reason": str(error)},
                    verification=metadata_obs, coreObservations=observations,
                )
                self.save()
                break
            if not card["coreFieldGatePassed"]:
                lead.update(status="core_field_gate_failed", rejectionReasons=["core_field_gate_failed"], verification=metadata_obs, coreObservations=observations)
                self.save()
                continue
            self.state["qualifiedSequence"] += 1
            card["qualifiedSequence"] = self.state["qualifiedSequence"]
            card["classification"] = decision
            card["classification"]["evidenceRefs"] = list(lead["discoveryRefs"]) + (["readme"] if readme and readme.get("status") == "observed" else ["metadata"])
            occurrence_order = []
            route_order = {row["categoryId"]: index for index, row in enumerate(self.query_map["routes"])}
            for occurrence in lead.get("discoveryOccurrences", []):
                occurrence_order.append([
                    route_order.get(occurrence["categoryId"], 10**6),
                    occurrence.get("queryOrder", 10**6),
                    occurrence["page"], occurrence["rank"], card["githubRepositoryId"],
                ])
            card["selectionKey"] = min(occurrence_order) if occurrence_order else [10**6, 10**6, 10**6, card["githubRepositoryId"]]
            self.state["qualifiedCards"][key] = card
            self.registry.add(card["githubRepositoryId"], card["fullName"], card.get("aliases", []), card.get("url"))
            lead.update(status="qualified_core_card", verification=metadata_obs, classification=decision)
            qualified_by_category[route["categoryId"]] += 1
            self.save()
        return self.progress({"candidatesThisInvocation": attempted, "preflight": preflight})

    def progress(self, extra=None):
        statuses = Counter(item["status"] for item in self.state["leads"].values())
        query_statuses = Counter(item["status"] for item in self.state["queries"].values())
        result = {
            "routes": len(self.query_map["routes"]), "queryPages": len(self.state["queries"]),
            "queryStatuses": dict(sorted(query_statuses.items())), "leads": len(self.state["leads"]),
            "leadStatuses": dict(sorted(statuses.items())), "qualifiedCoreCards": len(self.state["qualifiedCards"]),
            "requiredAdditions": self.plan["requiredAdditions"],
            "finalizable": len(self.state["qualifiedCards"]) >= self.plan["requiredAdditions"],
            "transportAttempts": self.collector.state["requests"], "transportBytes": self.collector.state["bytes"],
            "retryNotBefore": self.collector.state["retryNotBefore"], "canonicalWritten": False,
        }
        if extra:
            result.update(extra)
        return result

    def finalize(self):
        self.assert_canonical_unchanged()
        frozen = freeze_exact_target(
            list(self.state["qualifiedCards"].values()), self.plan["baseIncluded"], self.plan["targetIncluded"],
            leaf_count_map(self.base_run),
        )
        accepted = frozen["acceptedAdditions"]
        base_summary = e.load(self.base_run / "eligibility-reconciliation" / "summary.json")
        base_source = {row["id"]: row for row in e.load(self.base_run / "input.json")["repositories"]}
        eligible = set(base_summary["catalogIncludedSourceIds"])
        alias_rows = e.load(
            self.base_run / "eligibility-reconciliation" / "identity-alias-map.json"
        )["aliases"]
        aliases = {row["sourceId"]: row["canonicalSourceId"] for row in alias_rows}
        counts = expanded_category_counts(
            e.load(self.base_run / "taxonomy.json"), base_source, eligible, aliases, accepted,
        )
        output = self.run / "final"
        output.mkdir(exist_ok=True)
        e.atomic_json(output / "validated-expansion-candidate.json", {
            "schemaVersion": "catalog-expansion-candidate.v1", "createdAt": utc_now(),
            "baseIncludedSourceIds": base_summary["catalogIncludedSourceIds"], **frozen,
            "canonicalWritten": False,
        })
        e.atomic_json(output / "decision-ledger.json", {
            "schemaVersion": "catalog-expansion-decisions.v1",
            "items": list(self.state["leads"].values()),
        })
        e.atomic_json(output / "category-counts.json", counts)
        accepted_ids = [card["githubRepositoryId"] for card in accepted]
        accepted_names = [canonical_name(card["fullName"]) for card in accepted]
        if len(accepted_ids) != len(set(accepted_ids)) or len(accepted_names) != len(set(accepted_names)):
            raise ValueError("Final accepted additions contain duplicate identity")
        summary = {
            "scope": "cat07a_exact_expansion_candidate_not_canonical_catalog",
            "baseIncludedRepositories": self.plan["baseIncluded"],
            "acceptedAdditions": len(accepted), "qualifiedOverflow": len(frozen["qualifiedOverflow"]),
            "finalIncludedRepositories": frozen["finalIncluded"],
            "distinctAcceptedNumericIds": len(set(accepted_ids)), "duplicateAcceptedNumericIds": 0,
            "duplicateAcceptedNamesOrAliases": 0,
            "acceptedBelowMinimumStars": sum(card["stars"] < MINIMUM_STARS for card in accepted),
            "acceptedArchived": sum(card["archived"] is not False for card in accepted),
            "acceptedNonPublic": sum(card["visibility"] != "public" for card in accepted),
            "acceptedCoreFieldGateFailures": sum(not card["coreFieldGatePassed"] for card in accepted),
            "thematicLeaves": len(counts["thematicLeafCounts"]),
            "navigationContainers": len(counts["containerDistinctUnions"]),
            "emptyThematicLeaves": counts["emptyThematicLeaves"],
            "leadDecisionCounts": dict(sorted(Counter(item["status"] for item in self.state["leads"].values()).items())),
            "recommendationStatus": "separate_downstream_backlog_not_inclusion_gate",
            "transportAttempts": self.collector.state["requests"],
            "requestLogAudit": cat07.request_log_audit(self.run / "transport" / "request-log.jsonl"),
            "canonicalManifestSha256": self.plan["canonicalManifestSha256"],
            "canonicalHtmlSha256": self.plan["canonicalHtmlSha256"],
            "canonicalManifestUnchanged": True, "canonicalHtmlUnchanged": True,
            "canonicalWritten": False,
            "evidenceLimits": [
                "Live GitHub evidence proves the recorded public identity, archive state, Stars and bounded core facts only at each observation time.",
                "Category assignment is evidence-backed classification under the fixed taxonomy, not recommendation quality or curator acceptance.",
                "Recommendation narrative, browser behavior, canonical reconciliation and release readiness remain downstream.",
            ],
        }
        if summary["finalIncludedRepositories"] != self.plan["targetIncluded"]:
            raise ValueError("Exact target gate failed")
        e.atomic_json(output / "summary.json", summary)
        e.atomic_json(output / "rollback-snapshot.json", {
            "scope": "delete_only_cat07a_expansion_run_to_rollback",
            "canonicalManifestSha256": self.plan["canonicalManifestSha256"],
            "canonicalHtmlSha256": self.plan["canonicalHtmlSha256"],
            "baseRun": self.plan["baseRun"], "baseSummarySha256": self.plan["baseSummarySha256"],
            "files": {path.name: e.sha(path) for path in sorted(output.glob("*.json")) if path.name != "rollback-snapshot.json"},
        })
        return summary

    def verify(self):
        self.assert_canonical_unchanged()
        if self.query_map["schemaVersion"] != QUERY_SCHEMA or len(self.query_map["routes"]) != 111:
            raise ValueError("Every one of the 111 thematic leaves needs a versioned query route")
        category_ids = [route["categoryId"] for route in self.query_map["routes"]]
        if len(category_ids) != len(set(category_ids)):
            raise ValueError("Duplicate query route category")
        result = self.progress({"networkPerformed": False})
        summary_path = self.run / "final" / "summary.json"
        if summary_path.exists():
            summary = e.load(summary_path)
            if summary["finalIncludedRepositories"] != self.plan["targetIncluded"]:
                raise ValueError("Frozen candidate no longer satisfies exact target")
            if summary.get("emptyThematicLeaves"):
                raise ValueError(
                    f"Frozen candidate has empty thematic leaves: {summary['emptyThematicLeaves']}"
                )
            if any(summary[key] for key in (
                "duplicateAcceptedNumericIds", "duplicateAcceptedNamesOrAliases",
                "acceptedBelowMinimumStars", "acceptedArchived", "acceptedNonPublic",
                "acceptedCoreFieldGateFailures",
            )):
                raise ValueError("Frozen candidate violates CAT-07A gates")
            frozen = e.load(self.run / "final" / "validated-expansion-candidate.json")
            base_summary = e.load(self.base_run / "eligibility-reconciliation" / "summary.json")
            base_source = {row["id"]: row for row in e.load(self.base_run / "input.json")["repositories"]}
            alias_rows = e.load(
                self.base_run / "eligibility-reconciliation" / "identity-alias-map.json"
            )["aliases"]
            aliases = {row["sourceId"]: row["canonicalSourceId"] for row in alias_rows}
            expected_counts = expanded_category_counts(
                e.load(self.base_run / "taxonomy.json"), base_source,
                set(base_summary["catalogIncludedSourceIds"]), aliases,
                frozen["acceptedAdditions"],
            )
            if expected_counts != e.load(self.run / "final" / "category-counts.json"):
                raise ValueError("Frozen category counts do not preserve CAT-07 alias unions")
            result["finalSummaryVerified"] = True
        else:
            result["finalSummaryVerified"] = False
        return result


def migrate_script_pin(run):
    run = Path(run)
    plan_path = run / "plan.json"
    plan = e.load(plan_path)
    before = plan["scriptSha256"]
    after = e.sha(__file__)
    policy_before = plan["expansionPolicySha256"]
    policy_after = e.sha(POLICY_PATH)
    if before == after and policy_before == policy_after:
        raise ValueError("CAT-07A script and policy pins already match; migration is not needed")
    policy = e.load(POLICY_PATH)
    if (
        policy.get("task_id") != "CP-03.CAT-07A"
        or policy.get("baseline", {}).get("included_distinct_identities") != plan["baseIncluded"]
        or policy.get("baseline", {}).get("target_included_distinct_identities") != plan["targetIncluded"]
    ):
        raise ValueError("CAT-07A policy migration does not match the pinned run baseline")
    legacy = run / "script-pin-migration.json"
    index = 2 if legacy.exists() else 1
    while (run / f"script-pin-migration-{index:02d}.json").exists():
        index += 1
    artifact = run / f"script-pin-migration-{index:02d}.json"
    state_path = run / "state.json"
    state_before = e.sha(state_path)
    transport_before = e.sha(run / "transport" / "checkpoint.json")
    state = e.load(state_path)
    query_map_path = run / "query-map.json"
    old_query_map = e.load(query_map_path)
    query_map_migrated = old_query_map.get("generation") != "semantically_bound_topics_with_name_bound_zero_leaf_seeds_v7"
    if query_map_migrated:
        base_run = Path(plan["baseRun"])
        base_summary = e.load(base_run / "eligibility-reconciliation" / "summary.json")
        base_rows = eligible_topic_rows(base_run, base_summary)
        new_query_map = build_query_map(
            e.load(base_run / "taxonomy.json"), e.load(ROOT / "data" / "catalog_manifest.json")["categories"],
            leaf_count_map(base_run), plan["baseIncluded"], plan["targetIncluded"], base_rows,
        )
        history = run / "query-map-history"
        history.mkdir(exist_ok=True)
        e.atomic_json(history / f'{plan["queryMapSha256"]}.json', old_query_map)
        e.atomic_json(query_map_path, new_query_map)
        superseded_refs = set(state.get("queries", {}))
        history_prefix = f'query-history:{plan["queryMapSha256"][:12]}:'
        for lead in state.get("leads", {}).values():
            replacements = {}
            for occurrence in lead.get("discoveryOccurrences", []):
                old_ref = occurrence.get("ref")
                if old_ref not in superseded_refs:
                    continue
                historical_ref = history_prefix + old_ref
                replacements[old_ref] = historical_ref
                occurrence["ref"] = historical_ref
                occurrence["routeType"] = "superseded_category_topic"
                occurrence["supersededReason"] = "query_contract_migrated"
            if replacements:
                lead["discoveryRefs"] = [replacements.get(ref, ref) for ref in lead.get("discoveryRefs", [])]
        state.setdefault("queryHistory", []).append({
            "queryMapSha256": plan["queryMapSha256"], "queries": state.get("queries", {}),
            "reason": "broad_text_routes_retained_as_discovery_history_not_acceptance",
        })
        state["queries"] = {}
        plan["queryMapSha256"] = e.sha(query_map_path)
    prior_cards = state.setdefault("priorQualifiedCards", {})
    active_query_map = e.load(query_map_path)
    allowed_topics = {route["categoryId"]: set(route.get("topicTerms", [])) for route in active_query_map["routes"]}
    retained_cards = {}
    for key, card in list(state.get("qualifiedCards", {}).items()):
        matched_topics = set(card.get("classification", {}).get("matchedTopics", []))
        superseded = bool(matched_topics) and not bool(matched_topics & allowed_topics.get(card["primaryCategory"], set()))
        if not superseded:
            retained_cards[key] = card
            continue
        prior_cards[f'{key}:migration:{index}'] = {
            "card": card, "supersededReason": "matched_topic_removed_by_semantic_topic_policy",
        }
        if key in state["leads"]:
            state["leads"][key].update(
                status="discovered_unverified",
                rejectionReasons=["prior_qualification_requires_current_classifier_recheck"],
            )
    state["qualifiedCards"] = retained_cards
    state["qualifiedSequence"] = max((card.get("qualifiedSequence", 0) for card in retained_cards.values()), default=0)
    e.atomic_json(state_path, state)
    plan["scriptSha256"] = after
    plan["expansionPolicySha256"] = policy_after
    plan.setdefault("migrations", []).append({
        "type": "scoped_cat07a_implementation_alignment_preserving_state_and_counters",
        "appliedAt": utc_now(), "scriptSha256Before": before, "scriptSha256After": after,
        "expansionPolicySha256Before": policy_before,
        "expansionPolicySha256After": policy_after,
        "expansionPolicySchemaVersion": policy["schema_version"],
    })
    e.atomic_json(plan_path, plan)
    state_after = e.sha(state_path)
    e.atomic_json(artifact, {
        "scope": "local_pin_migration_no_network_no_counter_reset_no_canonical_write",
        "scriptSha256Before": before, "scriptSha256After": after,
        "expansionPolicySha256Before": policy_before,
        "expansionPolicySha256After": policy_after,
        "expansionPolicySchemaVersion": policy["schema_version"],
        "stateSha256Before": state_before, "stateSha256After": state_after,
        "queryMapMigratedToCategoryTopics": query_map_migrated,
        "transportCheckpointSha256Preserved": transport_before,
        "canonicalManifestSha256": e.sha(ROOT / "data" / "catalog_manifest.json"),
        "canonicalHtmlSha256": e.sha(ROOT / "docs" / "UNIFIED_CATALOG.html"),
    })
    return e.load(artifact)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "migrate-script", "discover", "collect", "finalize", "verify", "report"])
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--base-run", type=Path, default=ROOT / ".codex-tmp" / "catalog-refresh" / "gaps")
    parser.add_argument("--target-included", type=int, default=2500)
    parser.add_argument("--max-search-requests", type=int, default=30)
    parser.add_argument("--max-candidates", type=int, default=25)
    args = parser.parse_args()
    if not 1 <= args.max_search_requests <= 30:
        parser.error("--max-search-requests must be between 1 and 30")
    if not 1 <= args.max_candidates <= 100:
        parser.error("--max-candidates must be between 1 and 100")
    if args.mode == "prepare":
        result = prepare(args.run_dir.resolve(), args.base_run.resolve(), args.target_included)
    elif args.mode == "migrate-script":
        with e.single_writer(args.run_dir.resolve()):
            result = migrate_script_pin(args.run_dir.resolve())
    else:
        with e.single_writer(args.run_dir.resolve()):
            pipeline = ExpansionPipeline(args.run_dir.resolve())
            if args.mode == "discover":
                result = pipeline.discover(args.max_search_requests)
            elif args.mode == "collect":
                result = pipeline.collect(args.max_candidates)
            elif args.mode == "finalize":
                result = pipeline.finalize()
            elif args.mode == "verify":
                result = pipeline.verify()
            else:
                result = pipeline.progress({"networkPerformed": False})
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
