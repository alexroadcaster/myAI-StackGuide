#!/usr/bin/env python3
"""Build the Agentic Engineering Catalog from data/source_repos.csv."""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
SOURCE_CSV = ROOT / "data" / "source_repos.csv"
REPOS_CSV = ROOT / "data" / "repos.csv"
REPOS_JSON = ROOT / "data" / "repos.json"
CATEGORIES_JSON = ROOT / "data" / "categories.json"
CATEGORIES_DIR = ROOT / "categories"
SNAPSHOT_DATE = datetime(2026, 5, 23, tzinfo=timezone.utc)


@dataclass(frozen=True)
class Category:
    key: str
    title: str
    description: str
    include_when: str
    patterns: tuple[str, ...]


CATEGORIES: tuple[Category, ...] = (
    Category(
        "agent_runtime_orchestration",
        "Agent Runtime & Orchestration",
        "Frameworks and systems for running agents, coordinating workflows, and composing autonomous software teams.",
        "The repo is primarily about agent execution, orchestration, multi-agent workflows, or agent operating systems.",
        ("agent", "agents", "multi-agent", "superagent", "agency", "orchestrat", "workflow", "harness", "openclaw", "safeclaw", "nanoclaw", "eliza", "autonomous"),
    ),
    Category(
        "codex_claude_workflows",
        "Codex, Claude & Skill Workflows",
        "Codex/Claude setups, skills, harnesses, prompt packs, and AI coding workflow methods.",
        "The repo is mainly about Codex, Claude Code, skills, prompt workflows, status lines, or AI coding operating practices.",
        ("codex", "claude", "skill", "skills", "prompt", "system-prompt", "statusline", "bmad", "spec-kit", "antigravity", "vibe-kanban", "gstack", "claude.md"),
    ),
    Category(
        "mcp_integrations",
        "MCP & Tool Integrations",
        "Model Context Protocol servers and connectors for external services, IDEs, knowledge systems, and productivity tools.",
        "The repo exposes an MCP server/client, connects agents to SaaS tools, or wraps external APIs for agent use.",
        ("mcp", "model context protocol", "atlassian", "jira", "notion", "notebooklm", "telegram", "beeper", "github-trending"),
    ),
    Category(
        "rag_retrieval_search",
        "RAG, Retrieval & Search",
        "Retrieval-augmented generation, semantic retrieval, vector search, sparse search, and agent search layers.",
        "The primary value is retrieval quality, search infrastructure, vector/sparse indexing, or RAG application patterns.",
        ("rag", "retrieval", "search", "sparse", "splade", "vector search", "lightrag", "ragflow", "rag-anything", "retrieve"),
    ),
    Category(
        "memory_context_systems",
        "Memory & Context Systems",
        "Long-term memory, context management, context retrieval, and reusable agent memory stores.",
        "The repo manages persistent memory, context windows, personal/team memory, or reusable agent context.",
        ("memory", "mem0", "memos", "memstate", "memobank", "mempalace", "supermemory", "context", "knowledge work"),
    ),
    Category(
        "knowledge_graphs",
        "Knowledge Graphs",
        "Graph-backed memory, knowledge graph construction, graph retrieval, and entity/relation systems for AI agents.",
        "The repo centers on graph data structures, knowledge graphs, graph construction, or graph retrieval.",
        ("knowledge graph", "graphiti", "graphify", "graph builder", "llm-graph", "graph construction"),
    ),
    Category(
        "evals_observability_promptops",
        "Evals, Observability & Prompt Ops",
        "Evaluation, tracing, prompt management, observability, metrics, and quality gates for LLM applications.",
        "The repo helps measure, trace, compare, audit, or manage LLM/application behavior.",
        ("eval", "ragas", "langfuse", "observability", "audit", "benchmark", "prompt caching", "metrics"),
    ),
    Category(
        "document_ocr_parsing",
        "Documents, OCR & Parsing",
        "PDF/OCR/document parsing, document-to-markdown conversion, and content extraction for agent workflows.",
        "The primary work is extracting structured or LLM-ready data from files, PDFs, images, archives, or documents.",
        ("document", "pdf", "ocr", "paddleocr", "mineru", "markitdown", "parse", "parsing", "archive"),
    ),
    Category(
        "cloudflare_edge_backend",
        "Cloudflare, Edge & Backend",
        "Cloudflare Workers, edge runtimes, backend platforms, serverless systems, and deployment infrastructure.",
        "The repo is backend/edge/serverless infrastructure or specifically targets Cloudflare.",
        ("cloudflare", "worker", "workers", "edge", "durable", "backend", "serverless", "deploy", "browser rendering"),
    ),
    Category(
        "database_storage_sqlite",
        "Databases, Storage & SQLite",
        "Databases, SQLite extensions, storage engines, query systems, and data persistence layers.",
        "The repo primarily implements or wraps a database, storage layer, query engine, or SQLite extension.",
        ("database", "db", "sqlite", "convex", "serenedb", "lembed", "sqlite-vec", "storage", "query engine"),
    ),
    Category(
        "frontend_ui_desktop_browser",
        "Frontend, UI, Desktop & Browser Automation",
        "Frontend frameworks, desktop apps, UI layers, design tools, browser automation, and visual agent interfaces.",
        "The repo is mainly a UI/UX surface, desktop/browser tool, frontend agent UI, or visual automation layer.",
        ("frontend", "ui", "desktop", "browser", "webui", "playwright", "screen", "expo", "gradio", "copilotkit", "vision", "open-design", "design language"),
    ),
    Category(
        "developer_tools_cli",
        "Developer Tools & CLI",
        "CLI tools, code assistants, log tools, LSP integrations, OpenAPI wrappers, and developer workflow utilities.",
        "The repo is a developer-facing command-line, IDE, code, log, LSP, terminal, or workflow utility.",
        ("cli", "developer", "tool", "tools", "code", "coding", "lsp", "openapi", "terminal", "logs", "statusline", "dashboard"),
    ),
    Category(
        "learning_references_awesome",
        "Learning, Guides & Awesome Lists",
        "Curated lists, tutorials, guides, examples, and structured learning resources.",
        "The repo is mostly educational, reference-oriented, or a curated list rather than a runtime/tool.",
        ("awesome", "guide", "beginners", "tutorial", "learn", "curated", "collection", "lessons"),
    ),
    Category(
        "research_papers_science",
        "Research, Papers & Science",
        "Research projects, paper implementations, arXiv tooling, experiments, and scientific/research workflows.",
        "The repo is primarily tied to research papers, arXiv, experiments, or academic implementations.",
        ("arxiv", "paper", "research", "emnlp", "sigir", "reasoning-bank", "karpathy", "autoresearch"),
    ),
    Category(
        "security_safety_supply_chain",
        "Security, Safety & Supply Chain",
        "Security scanners, safe execution systems, supply-chain checks, and isolation/sandboxing tools.",
        "The repo helps detect risk, isolate execution, scan packages, or make agent workflows safer.",
        ("security", "secure", "exposure", "supply-chain", "scanner", "audit", "safe", "sandbox"),
    ),
    Category(
        "communications_personal_ops",
        "Communications & Personal Ops",
        "Messaging, personal productivity, career ops, and communication automation connected to agents.",
        "The repo connects agent workflows to messaging, inboxes, career workflows, or personal operations.",
        ("telegram", "whatsapp", "slack", "discord", "gmail", "beeper", "job", "career"),
    ),
    Category(
        "uncategorized_review",
        "Uncategorized / Needs Review",
        "Useful but weakly described repositories that need manual review before public positioning.",
        "The metadata is too thin or the project does not fit the current taxonomy.",
        tuple(),
    ),
)


CATEGORY_BY_KEY = {category.key: category for category in CATEGORIES}


PRIMARY_OVERRIDES: dict[str, str] = {
    "bumblebee": "security_safety_supply_chain",
    "audit-prompt-caching": "evals_observability_promptops",
    "openscreen": "frontend_ui_desktop_browser",
    "LightRAG": "rag_retrieval_search",
    "graphiti": "knowledge_graphs",
    "lazyweb-skill": "codex_claude_workflows",
    "impeccable": "frontend_ui_desktop_browser",
    "TencentDB-Agent-Memory": "memory_context_systems",
    "open-design": "frontend_ui_desktop_browser",
    "llm-worker": "cloudflare_edge_backend",
    "MemOS": "memory_context_systems",
    "sqlite-lembed": "database_storage_sqlite",
    "sqlite-vec": "database_storage_sqlite",
    "hermes-webui": "frontend_ui_desktop_browser",
    "hermes-cloudflare": "cloudflare_edge_backend",
    "documentor": "document_ocr_parsing",
    "graphify": "knowledge_graphs",
    "langfuse": "evals_observability_promptops",
    "ZetaLib": "developer_tools_cli",
    "Prompt-Engineering-Guide": "learning_references_awesome",
    "beepctl": "communications_personal_ops",
    "ccstatusline": "developer_tools_cli",
    "caveman": "codex_claude_workflows",
    "awesome-claude-skills": "learning_references_awesome",
    "lsp-mcp": "mcp_integrations",
    "notebooklm-mcp-cli": "mcp_integrations",
    "memstate-mcp": "memory_context_systems",
    "notebooklm-mcp": "mcp_integrations",
    "ragas": "evals_observability_promptops",
    "career-ops": "communications_personal_ops",
    "splade": "rag_retrieval_search",
    "reasoning-bank": "research_papers_science",
    "logzip": "developer_tools_cli",
    "Telegram-Archive": "communications_personal_ops",
    "hollow-agentOS": "agent_runtime_orchestration",
    "InsForge": "cloudflare_edge_backend",
    "snitchmd": "developer_tools_cli",
    "codbash": "developer_tools_cli",
    "playwright-cli": "developer_tools_cli",
    "RAG-Anything": "rag_retrieval_search",
    "safeclaw": "security_safety_supply_chain",
    "obsidian-skills": "codex_claude_workflows",
    "knowledge-work-plugins": "codex_claude_workflows",
    "beads": "memory_context_systems",
    "learn-claude-code": "learning_references_awesome",
    "awesome-claude-md": "learning_references_awesome",
    "mempalace": "memory_context_systems",
    "serenedb": "database_storage_sqlite",
    "agents": "cloudflare_edge_backend",
    "markitdown": "document_ocr_parsing",
    "ai-system-design-guide": "learning_references_awesome",
    "moltworker": "cloudflare_edge_backend",
    "context7": "developer_tools_cli",
    "convex-backend": "database_storage_sqlite",
    "llm-graph-builder": "knowledge_graphs",
    "supermemory": "memory_context_systems",
    "airweave": "rag_retrieval_search",
    "BMAD-METHOD": "codex_claude_workflows",
    "spec-kit": "codex_claude_workflows",
    "gsd-2": "codex_claude_workflows",
    "superpowers": "codex_claude_workflows",
    "vibe-kanban": "codex_claude_workflows",
    "gstack": "codex_claude_workflows",
    "autoresearch": "research_papers_science",
    "antigravity-awesome-skills": "learning_references_awesome",
    "mempalace": "memory_context_systems",
    "arxiv-mcp-server": "mcp_integrations",
    "idea-reality-mcp": "mcp_integrations",
    "mcp-github-trending": "mcp_integrations",
    "share": "developer_tools_cli",
    "collab-public": "agent_runtime_orchestration",
    "cloudflare-docs": "cloudflare_edge_backend",
    "mcp-server-atlassian-jira": "mcp_integrations",
    "atlassian-mcp-server": "mcp_integrations",
    "mcp-atlassian": "mcp_integrations",
    "gradio": "frontend_ui_desktop_browser",
    "PaddleOCR": "document_ocr_parsing",
    "openvino": "developer_tools_cli",
    "antigravity-kit": "codex_claude_workflows",
    "deer-flow": "agent_runtime_orchestration",
    "agency-agents": "agent_runtime_orchestration",
    "expo": "frontend_ui_desktop_browser",
    "openapi-to-cli": "developer_tools_cli",
    "MSA": "memory_context_systems",
    "UI-TARS-desktop": "frontend_ui_desktop_browser",
    "CopilotKit": "frontend_ui_desktop_browser",
    "mindsdb": "database_storage_sqlite",
    "Vision-Agents": "agent_runtime_orchestration",
    "MinerU": "document_ocr_parsing",
    "mem0": "memory_context_systems",
    "ai-agents-for-beginners": "learning_references_awesome",
    "everything-claude-code": "codex_claude_workflows",
    "browser-use": "frontend_ui_desktop_browser",
    "awesome-llm-apps": "learning_references_awesome",
    "ragflow": "rag_retrieval_search",
    "system-prompts-and-models-of-ai-tools": "learning_references_awesome",
    "nanoclaw": "security_safety_supply_chain",
    "claude-code-notion-plugin": "mcp_integrations",
    "claudeclaw": "agent_runtime_orchestration",
}


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def parse_int(value: str | None) -> int:
    if not value:
        return 0
    try:
        return int(float(str(value).replace(",", "")))
    except ValueError:
        return 0


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def age_days(value: str | None) -> int | None:
    parsed = parse_datetime(value)
    if parsed is None:
        return None
    return max(0, (SNAPSHOT_DATE - parsed).days)


def source_full_name(source_url: str) -> str:
    match = re.search(r"github\.com/([^/]+/[^/#?]+)", source_url or "")
    return match.group(1) if match else ""


def text_blob(row: dict[str, str]) -> str:
    return " ".join(
        [
            row.get("name", ""),
            row.get("source_url", ""),
            row.get("source_description", ""),
        ]
    ).lower()


def matching_categories(row: dict[str, str]) -> list[str]:
    blob = text_blob(row)
    matches: list[str] = []
    for category in CATEGORIES:
        if category.key == "uncategorized_review":
            continue
        if any(pattern.lower() in blob for pattern in category.patterns):
            matches.append(category.key)
    return matches


def primary_category(row: dict[str, str]) -> str:
    name = row.get("name", "")
    if name in PRIMARY_OVERRIDES:
        return PRIMARY_OVERRIDES[name]
    matches = matching_categories(row)
    return matches[0] if matches else "uncategorized_review"


def freshness_score(days: int | None) -> int:
    if days is None:
        return 35
    if days <= 7:
        return 100
    if days <= 30:
        return 90
    if days <= 90:
        return 75
    if days <= 180:
        return 60
    if days <= 365:
        return 45
    if days <= 730:
        return 25
    return 10


def size_score(size_kb: int) -> int:
    if size_kb <= 50_000:
        return 100
    if size_kb <= 250_000:
        return 85
    if size_kb <= 1_000_000:
        return 65
    if size_kb <= 3_000_000:
        return 35
    return 20


def has_clear_license(value: str | None) -> bool:
    value = (value or "").strip().upper()
    return bool(value and value != "NOASSERTION")


def rating_tier(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "E"


def score_row(row: dict[str, str], max_stars: int) -> dict[str, str | int | float]:
    stars = parse_int(row.get("source_stars"))
    size_kb = parse_int(row.get("size_kb"))
    days = age_days(row.get("source_updated_at"))
    popularity = 0 if max_stars <= 0 else math.log10(stars + 1) / math.log10(max_stars + 1) * 100
    freshness = freshness_score(days)
    metadata = 100 if row.get("source_description", "").strip() else 40
    license_score = 100 if has_clear_license(row.get("license")) else 50
    practicality = size_score(size_kb)
    score = (
        0.45 * popularity
        + 0.25 * freshness
        + 0.15 * metadata
        + 0.10 * license_score
        + 0.05 * practicality
    )
    score = round(score, 1)
    return {
        "curation_score": score,
        "rating": rating_tier(score),
        "rating_5": round(score / 20, 1),
        "freshness_days": "" if days is None else days,
        "popularity_score": round(popularity, 1),
        "freshness_score": freshness,
        "metadata_score": metadata,
        "license_score": license_score,
        "size_practicality_score": practicality,
    }


def read_rows() -> list[dict[str, str]]:
    with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def enrich_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    rows = [dict(row) for row in rows]
    max_stars = max((parse_int(row.get("source_stars")) for row in rows), default=0)
    enriched: list[dict[str, str]] = []
    for row in rows:
        primary = primary_category(row)
        secondary = [key for key in matching_categories(row) if key != primary]
        scored = score_row(row, max_stars)
        enriched_row = {
            "name": row.get("name", ""),
            "source_full_name": source_full_name(row.get("source_url", "")),
            "source_url": row.get("source_url", ""),
            "source_description": row.get("source_description", ""),
            "primary_category": primary,
            "primary_category_title": CATEGORY_BY_KEY[primary].title,
            "secondary_tags": ";".join(secondary[:5]),
            "source_stars": parse_int(row.get("source_stars")),
            "source_updated_at": row.get("source_updated_at", ""),
            "freshness_days": scored["freshness_days"],
            "license": row.get("license", ""),
            "size_kb": parse_int(row.get("size_kb")),
            "curation_score": scored["curation_score"],
            "rating": scored["rating"],
            "rating_5": scored["rating_5"],
            "popularity_score": scored["popularity_score"],
            "freshness_score": scored["freshness_score"],
            "metadata_score": scored["metadata_score"],
            "license_score": scored["license_score"],
            "size_practicality_score": scored["size_practicality_score"],
        }
        enriched.append(enriched_row)
    return sorted(enriched, key=lambda item: (-float(item["curation_score"]), item["name"].lower()))


def md_escape(value: object) -> str:
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\n", " ").strip()


def short_description(value: str, limit: int = 150) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def repo_table(rows: list[dict[str, str | int | float]], limit: int | None = None) -> str:
    selected = rows[:limit] if limit else rows
    lines = [
        "| Repository | Score | Stars | Updated | License | Description |",
        "|---|---:|---:|---|---|---|",
    ]
    for row in selected:
        name = md_escape(row["name"])
        url = md_escape(row["source_url"])
        updated = md_escape(str(row["source_updated_at"])[:10])
        lines.append(
            "| "
            f"[{name}]({url}) | "
            f"{row['curation_score']} ({row['rating']}) | "
            f"{row['source_stars']} | "
            f"{updated} | "
            f"{md_escape(row['license'])} | "
            f"{md_escape(short_description(str(row['source_description'])))} |"
        )
    return "\n".join(lines)


def write_csv(rows: list[dict[str, str | int | float]]) -> None:
    fieldnames = [
        "name",
        "source_full_name",
        "source_url",
        "source_description",
        "primary_category",
        "primary_category_title",
        "secondary_tags",
        "source_stars",
        "source_updated_at",
        "freshness_days",
        "license",
        "size_kb",
        "curation_score",
        "rating",
        "rating_5",
        "popularity_score",
        "freshness_score",
        "metadata_score",
        "license_score",
        "size_practicality_score",
    ]
    with REPOS_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(rows: list[dict[str, str | int | float]]) -> None:
    REPOS_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    payload = []
    grouped = defaultdict(list)
    for row in rows:
        grouped[str(row["primary_category"])].append(row)
    for category in CATEGORIES:
        category_rows = grouped.get(category.key, [])
        payload.append(
            {
                "key": category.key,
                "title": category.title,
                "description": category.description,
                "include_when": category.include_when,
                "count": len(category_rows),
                "average_score": round(sum(float(row["curation_score"]) for row in category_rows) / len(category_rows), 1) if category_rows else 0,
            }
        )
    CATEGORIES_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_category_pages(rows: list[dict[str, str | int | float]]) -> None:
    CATEGORIES_DIR.mkdir(exist_ok=True)
    for existing in CATEGORIES_DIR.glob("*.md"):
        existing.unlink()
    grouped = defaultdict(list)
    for row in rows:
        grouped[str(row["primary_category"])].append(row)
    for category in CATEGORIES:
        category_rows = grouped.get(category.key, [])
        lines = [
            f"# {category.title}",
            "",
            category.description,
            "",
            f"Include when: {category.include_when}",
            "",
            f"Repositories: {len(category_rows)}",
            "",
        ]
        if category_rows:
            lines.append(repo_table(category_rows))
        else:
            lines.append("_No repositories currently assigned._")
        lines.append("")
        (CATEGORIES_DIR / f"{category.key}.md").write_text("\n".join(lines), encoding="utf-8")


def write_readme(rows: list[dict[str, str | int | float]]) -> None:
    grouped = defaultdict(list)
    for row in rows:
        grouped[str(row["primary_category"])].append(row)
    category_lines = [
        "| Category | Repos | Avg score | Scope |",
        "|---|---:|---:|---|",
    ]
    for category in CATEGORIES:
        category_rows = grouped.get(category.key, [])
        avg = round(sum(float(row["curation_score"]) for row in category_rows) / len(category_rows), 1) if category_rows else 0
        category_lines.append(
            f"| [{category.title}](categories/{category.key}.md) | {len(category_rows)} | {avg} | {md_escape(category.description)} |"
        )

    top_rows = rows[:20]
    lines = [
        "# Agentic Engineering Catalog",
        "",
        "A curated, categorized catalog of open-source repositories for agentic software engineering, AI coding workflows, RAG, memory, MCP integrations, evals, and supporting infrastructure.",
        "",
        "This catalog is generated from public GitHub repository metadata and a manually curated category map. It is intended as a practical working map, not a benchmark or endorsement.",
        "",
        "## Snapshot",
        "",
        f"- Repositories: {len(rows)}",
        f"- Categories: {len(CATEGORIES)}",
        f"- Snapshot date: {SNAPSHOT_DATE.date().isoformat()}",
        "- Source fields: repository URL, stars, update timestamp, license, size, and description.",
        "",
        "## Categories",
        "",
        "\n".join(category_lines),
        "",
        "## Top Rated Repositories",
        "",
        repo_table(top_rows),
        "",
        "## Data Files",
        "",
        "- `data/source_repos.csv` - input file, edited manually before generation.",
        "- `data/repos.csv` - generated catalog with categories and rating fields.",
        "- `data/repos.json` - JSON version of the generated catalog.",
        "- `data/categories.json` - category definitions and counts.",
        "",
        "## Rating Method",
        "",
        "The `curation_score` is a transparent 0-100 utility score, not an objective quality score:",
        "",
        "- 45% popularity: log-scaled GitHub stars.",
        "- 25% freshness: recency of `source_updated_at`.",
        "- 15% metadata completeness: repository description present or missing.",
        "- 10% license completeness: license field present or missing.",
        "- 5% practical footprint: smaller repositories receive a mild advantage for easier inspection and adoption.",
        "",
        "Ratings are assigned from the score: A >= 85, B >= 70, C >= 55, D >= 40, E < 40.",
        "",
        "## Regenerate",
        "",
        "```bash",
        "python scripts/build_catalog.py",
        "```",
        "",
        "## Caveats",
        "",
        "- Stars and update timestamps are a snapshot and may drift over time.",
        "- Some repositories solve multiple problems; the catalog uses one `primary_category` and optional `secondary_tags`.",
        "- Descriptions are inherited from upstream public metadata and may be incomplete.",
        "- Inclusion does not imply affiliation with, or endorsement by, the upstream maintainers.",
        "",
    ]
    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_methodology() -> None:
    lines = [
        "# Methodology",
        "",
        "This repository uses a lightweight curation model designed for a practical engineering catalog.",
        "",
        "## Current HTML v5 Source",
        "",
        "`data/catalog_manifest.json` is the source-owned current catalog snapshot. `templates/unified_catalog.html` owns the standalone UI shell, and `scripts/build_catalog_html.py` validates both inputs before generating `docs/UNIFIED_CATALOG.html`.",
        "",
        "The dated CSV and research inputs below retain the legacy 2026-05-23 boundary and generate the Markdown catalog. They must not silently overwrite newer v5 repository facts.",
        "",
        "## Classification",
        "",
        "Each repository receives one `primary_category` plus zero or more `secondary_tags`.",
        "",
        "Primary categories are assigned with a curated override map first, then keyword matching over repository name, source URL, and source description. This keeps obvious projects stable while still allowing new rows to be classified automatically.",
        "",
        "## Rating",
        "",
        "`curation_score` is a composite score from public metadata:",
        "",
        "| Component | Weight | Why it matters |",
        "|---|---:|---|",
        "| Popularity | 45% | Star count is an imperfect but useful proxy for adoption and discovery. It is log-scaled to avoid letting massive repos dominate completely. |",
        "| Freshness | 25% | Recently updated repositories are more likely to be compatible with current agent tooling. |",
        "| Metadata | 15% | A clear description makes the repo easier to evaluate quickly. |",
        "| License | 10% | A visible license reduces adoption ambiguity. |",
        "| Size practicality | 5% | Smaller repos are mildly favored because they are easier to inspect, fork, and adapt. |",
        "",
        "The score is for catalog triage. It is not a security review, code quality audit, or production readiness certification.",
        "",
        "## Maintenance",
        "",
        "1. Update `data/source_repos.csv`.",
        "2. Run `python scripts/build_catalog.py`.",
        "3. Review diffs in `README.md`, `categories/*.md`, and `data/repos.csv`.",
        "4. Manually adjust `PRIMARY_OVERRIDES` if a repo lands in the wrong primary category.",
        "",
    ]
    (DOCS_DIR / "METHODOLOGY.md").write_text("\n".join(lines), encoding="utf-8")


def write_contributing() -> None:
    lines = [
        "# Contributing",
        "",
        "Contributions should keep the catalog useful, auditable, and low-noise.",
        "",
        "## Update The Current HTML Catalog",
        "",
        "1. Update `data/catalog_manifest.json` without changing its snapshot or provenance semantics silently.",
        "2. Update `templates/unified_catalog.html` only for standalone UI changes.",
        "3. Run `python scripts/build_catalog_html.py`.",
        "4. Run `python scripts/build_catalog_html.py --check` and the focused catalog pipeline tests.",
        "",
        "Keep the manifest as canonical compact JSON. Repository facts must be source-backed; unknown values remain null or `unknown`.",
        "",
        "## Add or Update a Repository",
        "",
        "The following steps update the legacy account-fork catalog:",
        "",
        "1. Edit `data/source_repos.csv`.",
        "2. Run `python scripts/build_catalog.py`.",
        "3. Check the generated category page.",
        "4. Open a pull request with a short note explaining why the repository belongs in the catalog.",
        "",
        "## Inclusion Criteria",
        "",
        "- The repository should be directly useful for agentic software engineering, AI coding workflows, RAG, memory, MCP, evals, document processing, or supporting infrastructure.",
        "- The project should have a public source URL.",
        "- Metadata should be factual and based on upstream public information.",
        "",
        "## Avoid",
        "",
        "- Promotional descriptions that are not present upstream.",
        "- Private or leaked data.",
        "- Security claims without evidence.",
        "- Star-count-only ranking arguments.",
        "",
    ]
    (DOCS_DIR / "CONTRIBUTING.md").write_text("\n".join(lines), encoding="utf-8")


def write_license() -> None:
    lines = [
        "MIT License",
        "",
        "Copyright (c) 2026",
        "",
        "Permission is hereby granted, free of charge, to any person obtaining a copy",
        "of this software and associated documentation files (the \"Software\"), to deal",
        "in the Software without restriction, including without limitation the rights",
        "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell",
        "copies of the Software, and to permit persons to whom the Software is",
        "furnished to do so, subject to the following conditions:",
        "",
        "The above copyright notice and this permission notice shall be included in all",
        "copies or substantial portions of the Software.",
        "",
        "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR",
        "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,",
        "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE",
        "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER",
        "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,",
        "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE",
        "SOFTWARE.",
        "",
    ]
    license_text = "\n".join(lines)
    (ROOT / "LICENSE").write_text(license_text, encoding="utf-8")
    (DOCS_DIR / "LICENSE").write_text(license_text, encoding="utf-8")


def write_gitignore() -> None:
    # Existing ignore rules are user-owned, including resumable local run state.
    # Only bootstrap a missing file; regeneration must not erase those rules.
    if (ROOT / ".gitignore").exists():
        return
    (ROOT / ".gitignore").write_text(
        "\n".join(
            [
                "__pycache__/",
                "*.pyc",
                ".DS_Store",
                "Thumbs.db",
                ".codex-tmp/",
                "/work/",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    rows = enrich_rows(read_rows())
    write_csv(rows)
    write_json(rows)
    write_category_pages(rows)
    # README.md is a curated product-facing guide. Do not overwrite it from the
    # base fork-catalog generator; update it intentionally when the product
    # narrative changes.
    write_methodology()
    write_contributing()
    write_license()
    write_gitignore()

    counts = Counter(str(row["primary_category"]) for row in rows)
    print(
        json.dumps(
            {
                "repos": len(rows),
                "categories": len(CATEGORIES),
                "category_counts": counts.most_common(),
                "top_score": rows[0] if rows else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
