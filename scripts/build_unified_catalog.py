#!/usr/bin/env python3
"""Build one Markdown catalog from all category/repository research artifacts."""

from __future__ import annotations

import csv
import json
from collections import OrderedDict
from datetime import date
from pathlib import Path

import product_guidance


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = date(2026, 5, 23).isoformat()

DATA_REPOS = ROOT / "data" / "repos.csv"
DATA_CATEGORIES = ROOT / "data" / "categories.json"
AI_RESEARCH = ROOT / "research" / "github_curated_recommendations_2026-05-23.json"
BUSINESS_RESEARCH = ROOT / "research" / "github_business_curated_recommendations_2026-05-23.json"
OUTPUT = ROOT / "docs" / "UNIFIED_CATALOG.md"

SOURCE_ORDER = {
    "account_fork_catalog": 0,
    "github_ai_engineering_research": 1,
    "github_business_product_research": 2,
}

SOURCE_LABELS = {
    "account_fork_catalog": "Account fork catalog",
    "github_ai_engineering_research": "AI/engineering research",
    "github_business_product_research": "Business/product research",
}

FALLBACK_CATEGORY_DESCRIPTIONS = {
    "agent_protocols_interop": "Protocols and interoperability layers for agent-to-agent, app-to-agent, or UI-to-agent communication.",
    "sandboxed_code_execution": "Hosted or local sandboxes, code interpreters, notebooks, and secure execution environments for agents.",
    "voice_realtime_agents": "Realtime voice, audio, telephony, and conversational media agents.",
    "multimodal_vision_agents": "Vision-language, computer-use, screenshot, video, and multimodal agent systems.",
    "local_llm_inference_routing": "Local model serving, LLM gateways, routers, proxy layers, and inference orchestration.",
    "vector_databases_embedding_infra": "Vector databases, embedding stores, ANN indexes, and retrieval storage infrastructure beyond SQLite-only tools.",
    "agentic_code_review_swe": "SWE agents, coding benchmarks, code review automation, and repo-scale software engineering assistants.",
    "web_crawling_data_ingestion": "Crawling, scraping, browser extraction, and web-to-agent data ingestion.",
    "workflow_state_machines_durable_agents": "Durable workflows, state machines, background jobs, and long-running agent process control.",
    "benchmarks_simulation_synthetic_data": "Benchmarks, synthetic data generation, simulation environments, and scenario generation for agent testing.",
}


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def md(value: object) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def short(value: str, limit: int = 170) -> str:
    cleaned = " ".join((value or "").split())
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 3].rstrip() + "..."


def intish(value: object) -> int:
    try:
        return int(float(str(value or "0").replace(",", "")))
    except ValueError:
        return 0


def floatish(value: object) -> float:
    try:
        return float(str(value or "0"))
    except ValueError:
        return 0.0


def dateish(value: str) -> str:
    return (value or "")[:10]


def better_description(current: str, candidate: str) -> str:
    current = current or ""
    candidate = candidate or ""
    if len(candidate) > len(current):
        return candidate
    return current


def add_category(
    categories: OrderedDict[str, dict],
    key: str,
    title: str,
    description: str = "",
    group: str = "",
) -> None:
    if key not in categories:
        categories[key] = {
            "key": key,
            "title": title or key,
            "description": description or "",
            "groups": OrderedDict(),
            "repos": OrderedDict(),
        }
    category = categories[key]
    if title and not category["title"]:
        category["title"] = title
    if description and not category["description"]:
        category["description"] = description
    if group:
        category["groups"][group] = True


def add_repo(
    categories: OrderedDict[str, dict],
    category_key: str,
    row: dict,
    source_key: str,
    score_label: str,
) -> None:
    category = categories[category_key]
    full_name = row.get("full_name") or row.get("source_full_name") or row.get("name") or ""
    full_name = full_name.strip()
    if not full_name:
        return

    repo_key = full_name.lower()
    repos = category["repos"]
    if repo_key not in repos:
        repos[repo_key] = {
            "full_name": full_name,
            "url": row.get("url") or row.get("source_url") or f"https://github.com/{full_name}",
            "description": row.get("description") or row.get("source_description") or "",
            "stars": intish(row.get("stars") or row.get("source_stars")),
            "updated": row.get("updated_at") or row.get("pushed_at") or row.get("source_updated_at") or "",
            "language": row.get("language") or "",
            "license": row.get("license") or "",
            "scores": OrderedDict(),
            "sources": OrderedDict(),
            "best_score": 0.0,
        }

    repo = repos[repo_key]
    repo["url"] = repo["url"] or row.get("url") or row.get("source_url") or f"https://github.com/{full_name}"
    repo["description"] = better_description(
        repo["description"], row.get("description") or row.get("source_description") or ""
    )
    repo["stars"] = max(repo["stars"], intish(row.get("stars") or row.get("source_stars")))
    candidate_updated = row.get("updated_at") or row.get("pushed_at") or row.get("source_updated_at") or ""
    if candidate_updated > repo["updated"]:
        repo["updated"] = candidate_updated
    if row.get("language") and not repo["language"]:
        repo["language"] = row["language"]
    if row.get("license") and not repo["license"]:
        repo["license"] = row["license"]
    if score_label:
        repo["scores"][source_key] = score_label
        # Extract the first numeric token from labels like "100.0 (A)".
        repo["best_score"] = max(repo["best_score"], floatish(score_label.split()[0]))
    repo["sources"][source_key] = True


def sorted_sources(sources: OrderedDict[str, bool]) -> str:
    keys = sorted(sources, key=lambda key: SOURCE_ORDER.get(key, 99))
    return ", ".join(SOURCE_LABELS.get(key, key) for key in keys)


def sorted_scores(scores: OrderedDict[str, str]) -> str:
    keys = sorted(scores, key=lambda key: SOURCE_ORDER.get(key, 99))
    return ", ".join(scores[key] for key in keys if scores[key])


def load_categories() -> OrderedDict[str, dict]:
    categories: OrderedDict[str, dict] = OrderedDict()

    for item in read_json(DATA_CATEGORIES):
        add_category(
            categories,
            item["key"],
            item["title"],
            item.get("description", ""),
            "Account fork catalog",
        )

    ai = read_json(AI_RESEARCH)
    for key, section in ai["sections"].items():
        add_category(
            categories,
            key,
            section.get("title") or key,
            section.get("description") or FALLBACK_CATEGORY_DESCRIPTIONS.get(key, ""),
            "AI/engineering research",
        )

    business = read_json(BUSINESS_RESEARCH)
    for key, section in business["categories"].items():
        add_category(
            categories,
            key,
            section.get("title") or key,
            section.get("description") or "",
            "Business/product research",
        )

    return categories


def load_repositories(categories: OrderedDict[str, dict]) -> None:
    for row in read_csv(DATA_REPOS):
        key = row.get("primary_category", "")
        if key not in categories:
            add_category(categories, key, row.get("primary_category_title") or key, "", "Account fork catalog")
        score = row.get("curation_score", "")
        rating = row.get("rating", "")
        score_label = f"{score} ({rating})" if score and rating else score
        add_repo(categories, key, row, "account_fork_catalog", score_label)

    ai = read_json(AI_RESEARCH)
    for key, section in ai["sections"].items():
        for row in section.get("repos", []):
            add_repo(categories, key, row, "github_ai_engineering_research", str(row.get("triage_score", "")))

    business = read_json(BUSINESS_RESEARCH)
    for key, section in business["categories"].items():
        for row in section.get("repos", []):
            add_repo(categories, key, row, "github_business_product_research", str(row.get("triage_score", "")))


def category_repo_rows(category: dict) -> list[dict]:
    return sorted(
        category["repos"].values(),
        key=lambda repo: (-floatish(repo["best_score"]), -intish(repo["stars"]), repo["full_name"].lower()),
    )


def build_markdown(categories: OrderedDict[str, dict]) -> str:
    total_placements = sum(len(category["repos"]) for category in categories.values())
    unique_repos = {
        repo["full_name"].lower()
        for category in categories.values()
        for repo in category["repos"].values()
    }

    lines = [
        "# myAI-StackGuide Catalog",
        "",
        f"Snapshot: {SNAPSHOT}",
        "",
        "This file combines all repository categories collected so far: the account fork catalog, the AI/engineering GitHub landscape research, and the business/product GitHub landscape research.",
        "",
        "Scores are triage signals from their source artifacts. They are useful for sorting within a source, but they are not due-diligence ratings and are not strictly comparable across every source.",
        "",
        "The same repository can appear in more than one category when it is genuinely useful in multiple workflows.",
        "",
        "## Summary",
        "",
        f"- Categories: {len(categories)}",
        f"- Category placements: {total_placements}",
        f"- Unique repositories: {len(unique_repos)}",
        "- Sources: `data/repos.csv`, `research/github_curated_recommendations_2026-05-23.json`, `research/github_business_curated_recommendations_2026-05-23.json`",
        "",
        product_guidance.markdown_section(level=2).rstrip(),
        "",
        "## Category Index",
        "",
        "| Category | Repos | Source groups | Scope |",
        "|---|---:|---|---|",
    ]

    for key, category in categories.items():
        groups = ", ".join(category["groups"].keys())
        lines.append(
            f"| [{md(category['title'])}](#{md(key)}) | {len(category['repos'])} | {md(groups)} | {md(category['description'])} |"
        )

    lines.extend(["", "## Categories", ""])

    for key, category in categories.items():
        rows = category_repo_rows(category)
        groups = ", ".join(category["groups"].keys())
        lines.extend(
            [
                f"### {category['title']}",
                f"<a id=\"{key}\"></a>",
                "",
                category["description"] or "No category description available yet.",
                "",
                f"Source groups: {groups}",
                "",
                "| Repository | Stars | Updated | Score | Source | Description |",
                "|---|---:|---|---:|---|---|",
            ]
        )
        for repo in rows:
            lines.append(
                f"| [{md(repo['full_name'])}]({md(repo['url'])}) | "
                f"{repo['stars']} | {md(dateish(repo['updated']))} | {md(sorted_scores(repo['scores']))} | "
                f"{md(sorted_sources(repo['sources']))} | {md(short(repo['description']))} |"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    categories = load_categories()
    load_repositories(categories)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_markdown(categories), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "categories": len(categories),
                "category_placements": sum(len(category["repos"]) for category in categories.values()),
                "unique_repositories": len(
                    {
                        repo["full_name"].lower()
                        for category in categories.values()
                        for repo in category["repos"].values()
                    }
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
