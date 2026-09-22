"""Evidence-aware candidate constraint matching for StackGuide retrieval."""

from __future__ import annotations

from typing import Any
import unicodedata


CHECK_TARGETS = {
    "license": ("/repository/license",),
    "deployment": ("/delivery/deployment",),
    "language": ("/repository/languages",),
    "compatibility": ("/advisory/compatibility",),
    "no_server": ("/delivery/requires_server",),
    "availability": ("/repository/availability",),
    "archived": ("/repository/archived",),
    "advisory_evidence": (
        "/advisory/use_cases",
        "/advisory/best_for",
        "/advisory/adoption_mode",
        "/advisory/project_stages",
        "/advisory/complexity",
        "/advisory/integration_surface",
        "/advisory/compatibility",
    ),
}
CHECK_ORDER = (
    "license", "deployment", "language", "compatibility", "no_server",
    "availability", "archived", "advisory_evidence",
)
REASON_ORDER = (
    "constraint_mismatch", "mandatory_fact_unknown", "archived", "unavailable",
    "duplicate_identity", "insufficient_evidence", "context_budget",
    "candidate_budget", "invalid_query", "fts5_unavailable", "index_missing",
    "index_corrupt", "index_incompatible", "no_hits", "cancelled",
)


def evidence_pointer_covers(source_pointer, target_pointer):
    """Return whether a non-root JSON pointer safely covers a target segment."""
    if not isinstance(source_pointer, str) or not isinstance(target_pointer, str):
        return False
    if source_pointer == "/" or target_pointer == "/":
        return False
    if not source_pointer.startswith("/") or not target_pointer.startswith("/"):
        return False
    if source_pointer.endswith("/") or "//" in source_pointer or "//" in target_pointer:
        return False
    return source_pointer == target_pointer or target_pointer.startswith(source_pointer + "/")


def _normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _normalized_set(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {_normalize(value) for value in values if isinstance(value, str) and _normalize(value)}


def _evidence_for(card: dict[str, Any], targets: tuple[str, ...]) -> tuple[list[str], bool]:
    usable: list[tuple[str, tuple[str, ...]]] = []
    for evidence in card.get("evidence", []):
        if not isinstance(evidence, dict) or evidence.get("verification") == "unknown":
            continue
        evidence_id = evidence.get("evidence_id")
        fields = evidence.get("fields")
        if not isinstance(evidence_id, str) or not isinstance(fields, list):
            continue
        covered = tuple(
            target for target in targets
            if any(
                isinstance(pointer, str) and evidence_pointer_covers(pointer, target)
                for pointer in fields
            )
        )
        if covered:
            usable.append((evidence_id, covered))
    refs: list[str] = []
    collectively_covered: set[str] = set()
    for evidence_id, covered in usable:
        if evidence_id not in refs:
            refs.append(evidence_id)
        collectively_covered.update(covered)
    return refs, collectively_covered.issuperset(targets)


def _value_result(card: dict[str, Any], query: dict[str, Any], field: str) -> tuple[bool | None, bool]:
    """Return (constraint result, fact_present); None means unknown."""
    constraints = query["constraints"]
    repository = card.get("repository") if isinstance(card.get("repository"), dict) else {}
    delivery = card.get("delivery") if isinstance(card.get("delivery"), dict) else {}
    advisory = card.get("advisory") if isinstance(card.get("advisory"), dict) else {}
    if field == "license":
        license_value = repository.get("license")
        if not isinstance(license_value, dict):
            return None, False
        actual = {
            _normalize(value) for value in (license_value.get("spdx"), license_value.get("name"))
            if isinstance(value, str) and _normalize(value)
        }
        if not actual:
            return None, False
        allowed = _normalized_set(constraints["allowed_licenses"])
        return (bool(actual & allowed) if allowed else True), True
    if field == "deployment":
        value = delivery.get("deployment")
        values = value.get("values") if isinstance(value, dict) else None
        actual = _normalized_set(values)
        if not actual:
            return None, False
        requested = _normalized_set(constraints["deployment"])
        return (bool(actual & requested) if requested else True), True
    if field == "language":
        languages = repository.get("languages")
        if not isinstance(languages, list):
            return None, False
        actual = {
            _normalize(item["name"])
            for item in languages
            if isinstance(item, dict) and isinstance(item.get("name"), str) and _normalize(item["name"])
        }
        if not actual:
            return None, False
        requested = _normalized_set(constraints["languages"])
        return (bool(actual & requested) if requested else True), True
    if field == "compatibility":
        actual = _normalized_set(advisory.get("compatibility"))
        if not actual:
            return None, False
        requested = _normalized_set(constraints["compatibility"])
        return (requested.issubset(actual) if requested else True), True
    if field == "no_server":
        actual = delivery.get("requires_server")
        if not isinstance(actual, bool):
            return None, False
        requested = constraints["require_no_server"]
        return (not actual if requested is True else True), True
    if field == "availability":
        actual = repository.get("availability")
        if actual == "unknown" or actual is None:
            return None, False
        return actual == "available", True
    if field == "archived":
        actual = repository.get("archived")
        if not isinstance(actual, bool):
            return None, False
        return not actual, True
    if field == "advisory_evidence":
        keys = (
            "use_cases", "best_for", "adoption_mode", "project_stages",
            "complexity", "integration_surface", "compatibility",
        )
        present = True
        for key in keys:
            value = advisory.get(key)
            if value is None or value == "" or value == []:
                present = False
                break
        return (True, True) if present else (None, False)
    raise ValueError("unknown candidate check")


def _active_constraint_checks(query: dict[str, Any]) -> set[str]:
    constraints = query["constraints"]
    active = set(constraints["mandatory_fields"])
    if constraints["allowed_licenses"]:
        active.add("license")
    if constraints["deployment"]:
        active.add("deployment")
    if constraints["languages"]:
        active.add("language")
    if constraints["compatibility"]:
        active.add("compatibility")
    if constraints["require_no_server"] is not None:
        active.add("no_server")
    return active


def _verification_message(field: str, present: bool) -> str:
    if not present:
        return {
            "license": "Verify the repository license from an authoritative upstream source.",
            "deployment": "Verify supported deployment modes from current upstream documentation.",
            "language": "Verify the supported implementation language from current repository metadata.",
            "compatibility": "Verify the requested compatibility against current upstream documentation.",
            "no_server": "Verify whether adoption requires a server from current upstream documentation.",
            "availability": "Verify that the public repository is currently available.",
            "archived": "Verify the repository archived state from the upstream repository.",
            "advisory_evidence": "Verify the advisory fit fields against source-backed public evidence.",
        }[field]
    return f"Verify source evidence covering every required {field.replace('_', ' ')} field."


def match_candidate(card, query):
    """Evaluate hard constraints without treating activity or popularity as fit."""
    if not isinstance(card, dict) or not isinstance(query, dict):
        raise ValueError("card and query must be objects")
    identity = card.get("identity")
    constraints = query.get("constraints")
    if (
        not isinstance(identity, dict)
        or not isinstance(identity.get("github_repository_id"), int)
        or isinstance(identity.get("github_repository_id"), bool)
        or identity["github_repository_id"] < 1
        or not isinstance(query.get("query_id"), str)
        or not isinstance(constraints, dict)
        or set(constraints) != {
            "languages", "deployment", "allowed_licenses", "compatibility",
            "require_no_server", "mandatory_fields",
        }
    ):
        raise ValueError("invalid candidate input")

    selected = _active_constraint_checks(query) | {"availability", "archived", "advisory_evidence"}
    checks: list[dict[str, Any]] = []
    reasons: set[str] = set()
    verifications: list[str] = []
    blocked = False
    for field in CHECK_ORDER:
        if field not in selected:
            continue
        value_result, present = _value_result(card, query, field)
        refs, fully_covered = _evidence_for(card, CHECK_TARGETS[field])
        if value_result is None or not fully_covered:
            outcome = "unknown"
            reasons.add("mandatory_fact_unknown" if not present else "insufficient_evidence")
            message = _verification_message(field, present)
            if message not in verifications:
                verifications.append(message)
        elif value_result:
            outcome = "pass"
        else:
            outcome = "fail"
            blocked = True
            if field == "availability":
                reasons.add("unavailable")
            elif field == "archived":
                reasons.add("archived")
            else:
                reasons.add("constraint_mismatch")
        checks.append({"field": field, "outcome": outcome, "evidence_refs": refs})

    unknown = any(item["outcome"] == "unknown" for item in checks)
    status = "blocked" if blocked else "reference_only" if unknown else "primary_eligible"
    if status == "primary_eligible":
        reasons.clear()
        verifications.clear()
    return {
        "schema_version": "2.1.0",
        "github_repository_id": identity["github_repository_id"],
        "query_id": query["query_id"],
        "status": status,
        "checks": checks,
        "reason_codes": [reason for reason in REASON_ORDER if reason in reasons],
        "required_verifications": verifications,
    }
