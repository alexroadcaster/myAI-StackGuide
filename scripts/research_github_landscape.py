#!/usr/bin/env python3
"""Search GitHub for expansion candidates around the Agentic Engineering Catalog."""

from __future__ import annotations

import csv
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPOS = ROOT / "data" / "repos.csv"
OUT_DIR = ROOT / "research"
OUT_JSON = OUT_DIR / "github_search_candidates_2026-05-23.json"
OUT_CSV = OUT_DIR / "github_search_candidates_2026-05-23.csv"
OUT_MD = OUT_DIR / "github_deep_research_2026-05-23.md"
SNAPSHOT = datetime(2026, 5, 23, tzinfo=timezone.utc)
UA = {
    "User-Agent": "Codex-GitHub-Landscape-Research",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

EXISTING_QUERIES = {
    "agent_runtime_orchestration": [
        "ai agent framework in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
        "multi agent orchestration in:name,description,readme stars:>200 pushed:>2025-01-01 archived:false",
    ],
    "codex_claude_workflows": [
        "claude code skill in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
        "ai coding agent workflow in:name,description,readme stars:>200 pushed:>2025-01-01 archived:false",
    ],
    "mcp_integrations": [
        "model context protocol server in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "mcp server integration in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "rag_retrieval_search": [
        "rag framework agent in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
        "retrieval augmented generation framework in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
    ],
    "memory_context_systems": [
        "ai agent memory in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "llm memory context in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "knowledge_graphs": [
        "knowledge graph llm agent in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "graph rag llm in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "evals_observability_promptops": [
        "llm observability evals in:name,description,readme stars:>200 pushed:>2025-01-01 archived:false",
        "llm evaluation framework in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
    ],
    "document_ocr_parsing": [
        "document parsing llm ocr in:name,description,readme stars:>200 pushed:>2025-01-01 archived:false",
        "pdf to markdown llm in:name,description,readme stars:>200 pushed:>2025-01-01 archived:false",
    ],
    "cloudflare_edge_backend": [
        "cloudflare workers ai agent in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
        "edge ai agent worker in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
    ],
    "database_storage_sqlite": [
        "sqlite vector embeddings in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
        "database for ai agents in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "frontend_ui_desktop_browser": [
        "browser automation ai agent in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
        "ai agent ui framework in:name,description,readme stars:>200 pushed:>2025-01-01 archived:false",
    ],
    "developer_tools_cli": [
        "ai coding assistant cli in:name,description,readme stars:>200 pushed:>2025-01-01 archived:false",
        "developer tool llm cli in:name,description,readme stars:>200 pushed:>2025-01-01 archived:false",
    ],
    "learning_references_awesome": [
        "awesome ai agents in:name,description,readme stars:>1000 pushed:>2025-01-01 archived:false",
        "llm agents guide in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
    ],
    "research_papers_science": [
        "llm agent benchmark research in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "ai agents paper implementation in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "security_safety_supply_chain": [
        "ai agent sandbox security in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "llm security scanner prompt injection in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "communications_personal_ops": [
        "ai agent telegram slack gmail in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
        "personal assistant agent email calendar in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
}

NEW_CATEGORY_QUERIES = {
    "agent_protocols_interop": [
        "agent protocol interoperability in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
        "ag-ui agent protocol in:name,description,readme stars:>20 pushed:>2025-01-01 archived:false",
    ],
    "sandboxed_code_execution": [
        "ai code sandbox execution in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "sandbox code interpreter agent in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "voice_realtime_agents": [
        "realtime voice ai agent in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "voice assistant agent framework in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "multimodal_vision_agents": [
        "multimodal ai agent vision in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "vision language agent in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "local_llm_inference_routing": [
        "local llm serving inference in:name,description,readme stars:>1000 pushed:>2025-01-01 archived:false",
        "llm gateway router in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
    ],
    "vector_databases_embedding_infra": [
        "vector database embeddings in:name,description,readme stars:>1000 pushed:>2025-01-01 archived:false",
        "embedding search database in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
    ],
    "agentic_code_review_swe": [
        "swe agent code review in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "software engineering agent benchmark in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "web_crawling_firecrawl_data_ingestion": [
        "web crawling llm agent in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
        "web scraping for llm in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
    ],
    "workflow_state_machines_durable_agents": [
        "durable workflow ai agent in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "state machine agent workflow in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
    ],
    "synthetic_data_simulation_agents": [
        "synthetic data llm agent in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
        "agent simulation synthetic data in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
    ],
}

NEW_CATEGORY_DESCRIPTIONS = {
    "agent_protocols_interop": "Protocols and interoperability layers for agent-to-agent, app-to-agent, or UI-to-agent communication.",
    "sandboxed_code_execution": "Hosted or local sandboxes, code interpreters, notebooks, and secure execution environments for agents.",
    "voice_realtime_agents": "Realtime voice, audio, telephony, and conversational media agents.",
    "multimodal_vision_agents": "Vision-language, computer-use, screenshot, video, and multimodal agent systems.",
    "local_llm_inference_routing": "Local model serving, LLM gateways, routers, proxy layers, and inference orchestration.",
    "vector_databases_embedding_infra": "Vector databases, embedding stores, ANN indexes, and retrieval storage infrastructure beyond SQLite-only tools.",
    "agentic_code_review_swe": "SWE agents, coding benchmarks, code review automation, and repo-scale software engineering assistants.",
    "web_crawling_firecrawl_data_ingestion": "Crawling, scraping, browser extraction, and web-to-agent data ingestion.",
    "workflow_state_machines_durable_agents": "Durable workflows, state machines, background jobs, and long-running agent process control.",
    "synthetic_data_simulation_agents": "Synthetic data generation, user/task simulation, environments, and scenario generation for agent testing.",
}


def read_existing() -> set[str]:
    existing = set()
    with SOURCE_REPOS.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            url = (row.get("source_url") or "").rstrip("/")
            if url:
                existing.add(url.lower())
            full_name = row.get("source_full_name") or ""
            if full_name:
                existing.add(f"https://github.com/{full_name}".lower())
    return existing


def github_get(url: str) -> tuple[dict, dict[str, str]]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        return json.loads(response.read().decode("utf-8")), headers


def wait_if_needed(headers: dict[str, str]) -> None:
    remaining = int(headers.get("x-ratelimit-remaining", "1"))
    if remaining > 0:
        return
    reset = int(headers.get("x-ratelimit-reset", "0"))
    delay = max(3, reset - int(time.time()) + 2)
    print(json.dumps({"event": "rate_limit_wait", "seconds": delay}, ensure_ascii=False), flush=True)
    time.sleep(delay)


def search_repositories(query: str, per_page: int = 20) -> tuple[list[dict], dict[str, str]]:
    encoded = urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": per_page})
    url = f"https://api.github.com/search/repositories?{encoded}"
    for attempt in range(3):
        try:
            payload, headers = github_get(url)
            wait_if_needed(headers)
            return payload.get("items", []), headers
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in (403, 429):
                reset = int(exc.headers.get("x-ratelimit-reset", "0") or 0)
                delay = max(10, reset - int(time.time()) + 2)
                print(json.dumps({"event": "search_wait", "query": query, "status": exc.code, "seconds": delay, "body": body[:180]}, ensure_ascii=False), flush=True)
                time.sleep(delay)
                continue
            print(json.dumps({"event": "search_error", "query": query, "status": exc.code, "body": body[:300]}, ensure_ascii=False), flush=True)
            return [], {"error": str(exc.code)}
        except Exception as exc:
            if attempt == 2:
                print(json.dumps({"event": "search_exception", "query": query, "error": str(exc)}, ensure_ascii=False), flush=True)
                return [], {"error": str(exc)}
            time.sleep(2 * (attempt + 1))
    return [], {}


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def freshness_days(value: str | None) -> int | None:
    dt = parse_dt(value)
    if dt is None:
        return None
    return max(0, (SNAPSHOT - dt).days)


def score_repo(repo: dict) -> float:
    stars = int(repo.get("stargazers_count") or 0)
    days = freshness_days(repo.get("pushed_at"))
    popularity = min(100, math.log10(stars + 1) / math.log10(250_000) * 100)
    if days is None:
        freshness = 40
    elif days <= 14:
        freshness = 100
    elif days <= 60:
        freshness = 85
    elif days <= 180:
        freshness = 65
    elif days <= 365:
        freshness = 45
    else:
        freshness = 20
    metadata = 100 if (repo.get("description") or "").strip() else 35
    license_score = 100 if (repo.get("license") or {}).get("spdx_id") not in (None, "NOASSERTION") else 55
    return round(0.55 * popularity + 0.25 * freshness + 0.12 * metadata + 0.08 * license_score, 1)


def normalize_repo(repo: dict, source_category: str, query: str, group: str, existing: set[str]) -> dict:
    url = (repo.get("html_url") or "").rstrip("/")
    full_name = repo.get("full_name") or ""
    return {
        "full_name": full_name,
        "name": repo.get("name") or full_name.split("/")[-1],
        "url": url,
        "description": repo.get("description") or "",
        "stars": int(repo.get("stargazers_count") or 0),
        "forks": int(repo.get("forks_count") or 0),
        "language": repo.get("language") or "",
        "license": (repo.get("license") or {}).get("spdx_id") or "",
        "pushed_at": repo.get("pushed_at") or "",
        "updated_at": repo.get("updated_at") or "",
        "created_at": repo.get("created_at") or "",
        "open_issues": int(repo.get("open_issues_count") or 0),
        "archived": bool(repo.get("archived")),
        "source_category": source_category,
        "search_group": group,
        "query": query,
        "already_in_catalog": url.lower() in existing or f"https://github.com/{full_name}".lower() in existing,
        "interesting_score": score_repo(repo),
    }


def collect() -> list[dict]:
    existing = read_existing()
    all_queries: list[tuple[str, str, str]] = []
    for category, queries in EXISTING_QUERIES.items():
        all_queries.extend(("existing", category, query) for query in queries)
    for category, queries in NEW_CATEGORY_QUERIES.items():
        all_queries.extend(("new_category", category, query) for query in queries)

    by_url: dict[str, dict] = {}
    query_log = []
    for index, (group, category, query) in enumerate(all_queries, start=1):
        print(json.dumps({"event": "search", "index": index, "total": len(all_queries), "category": category, "query": query}, ensure_ascii=False), flush=True)
        items, headers = search_repositories(query)
        query_log.append({"group": group, "category": category, "query": query, "count": len(items)})
        for repo in items:
            item = normalize_repo(repo, category, query, group, existing)
            key = item["url"].lower()
            if not key:
                continue
            if key in by_url:
                current = by_url[key]
                current.setdefault("matched_categories", set()).add(category)
                current.setdefault("matched_queries", set()).add(query)
                if item["interesting_score"] > current["interesting_score"]:
                    current.update({k: item[k] for k in ["source_category", "search_group", "query", "interesting_score"]})
            else:
                item["matched_categories"] = {category}
                item["matched_queries"] = {query}
                by_url[key] = item
    results = []
    for item in by_url.values():
        item["matched_categories"] = sorted(item["matched_categories"])
        item["matched_queries"] = sorted(item["matched_queries"])
        results.append(item)
    results.sort(key=lambda item: (-item["interesting_score"], -item["stars"], item["full_name"].lower()))
    return results, query_log


def md_escape(value: object) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def short(value: str, limit: int = 130) -> str:
    value = " ".join((value or "").split())
    return value if len(value) <= limit else value[: limit - 3].rstrip() + "..."


def repo_table(rows: list[dict], limit: int = 7) -> str:
    lines = [
        "| Repo | Score | Stars | Updated | Why interesting |",
        "|---|---:|---:|---|---|",
    ]
    for row in rows[:limit]:
        lines.append(
            f"| [{md_escape(row['full_name'])}]({md_escape(row['url'])}) | "
            f"{row['interesting_score']} | {row['stars']} | {md_escape(row['pushed_at'][:10])} | "
            f"{md_escape(short(row['description']))} |"
        )
    return "\n".join(lines)


def write_outputs(results: list[dict], query_log: list[dict]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps({"snapshot": SNAPSHOT.date().isoformat(), "query_log": query_log, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = [
        "full_name", "url", "description", "stars", "forks", "language", "license", "pushed_at", "updated_at", "created_at", "open_issues", "archived", "source_category", "search_group", "matched_categories", "already_in_catalog", "interesting_score",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in results:
            row = dict(row)
            row["matched_categories"] = ";".join(row.get("matched_categories", []))
            writer.writerow(row)

    grouped_existing = defaultdict(list)
    grouped_new = defaultdict(list)
    for row in results:
        if row["already_in_catalog"]:
            continue
        target = grouped_new if row["search_group"] == "new_category" else grouped_existing
        target[row["source_category"]].append(row)

    lines = [
        "# GitHub Deep Research: Expansion Candidates",
        "",
        f"Snapshot date: {SNAPSHOT.date().isoformat()}",
        "",
        "Source: GitHub Search API over public repositories. Queries required `pushed:>2025-01-01` and `archived:false` where supported by GitHub repository search.",
        "",
        "The tables below exclude repositories already present in `data/repos.csv` when possible. Scores are search-triage scores, not endorsements or code reviews.",
        "",
        "## Existing Category Expansion",
        "",
    ]
    for category in EXISTING_QUERIES:
        rows = sorted(grouped_existing.get(category, []), key=lambda item: (-item["interesting_score"], -item["stars"]))
        lines.append(f"### {category}")
        lines.append("")
        if rows:
            lines.append(repo_table(rows, 7))
        else:
            lines.append("_No new candidates found in this search pass._")
        lines.append("")

    lines.extend(["## Proposed New Categories", ""])
    for category, description in NEW_CATEGORY_DESCRIPTIONS.items():
        rows = sorted(grouped_new.get(category, []), key=lambda item: (-item["interesting_score"], -item["stars"]))
        lines.append(f"### {category}")
        lines.append("")
        lines.append(description)
        lines.append("")
        if rows:
            lines.append(repo_table(rows, 8))
        else:
            lines.append("_No candidates found in this search pass._")
        lines.append("")

    lines.extend([
        "## Query Log",
        "",
        "| Group | Category | Results | Query |",
        "|---|---|---:|---|",
    ])
    for entry in query_log:
        lines.append(f"| {entry['group']} | {entry['category']} | {entry['count']} | `{md_escape(entry['query'])}` |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results, query_log = collect()
    write_outputs(results, query_log)
    print(json.dumps({
        "results": len(results),
        "new_not_in_catalog": sum(1 for item in results if not item["already_in_catalog"]),
        "output_md": str(OUT_MD),
        "output_json": str(OUT_JSON),
        "output_csv": str(OUT_CSV),
    }, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
