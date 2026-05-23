#!/usr/bin/env python3
"""HTML-backed GitHub search for business/product OSS categories.

This fallback avoids the unauthenticated GitHub REST core limit by reading public
repository search pages and repository pages.
"""

from __future__ import annotations

import csv
import html as html_lib
import json
import math
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from research_github_business_landscape import CATEGORIES, OUT_DIR, SNAPSHOT


RAW_JSON = OUT_DIR / "github_business_search_candidates_html_2026-05-23.json"
CURATED_JSON = OUT_DIR / "github_business_curated_recommendations_2026-05-23.json"
CURATED_CSV = OUT_DIR / "github_business_curated_recommendations_2026-05-23.csv"
CURATED_MD = OUT_DIR / "github_business_curated_recommendations_2026-05-23.md"

HTML_UA = {
    "User-Agent": "Mozilla/5.0 Codex-GitHub-Business-Landscape-Research",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_html(url: str) -> str:
    request = urllib.request.Request(url, headers=HTML_UA)
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read().decode("utf-8", errors="replace")


def decode_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html_lib.unescape(value)
    return " ".join(value.split()).strip()


def parse_stars(value: str) -> int:
    value = html_lib.unescape(value).strip().lower().replace(",", "")
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([km]?)", value)
    if not match:
        return 0
    number = float(match.group(1))
    suffix = match.group(2)
    if suffix == "k":
        number *= 1_000
    elif suffix == "m":
        number *= 1_000_000
    return int(number)


def normalize_updated(value: str) -> str:
    value = html_lib.unescape(value).strip()
    for fmt in ("%b %d, %Y, %I:%M %p UTC", "%B %d, %Y, %I:%M %p UTC"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            pass
    return value


def parse_search_results(page: str, category: str, source: str) -> list[dict]:
    rows: list[dict] = []
    chunks = page.split('Result-module__Result')
    for chunk in chunks[1:]:
        name_match = re.search(r'href="/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"[^>]*>\s*<span[^>]*>(.*?)</span>', chunk, re.S)
        if not name_match:
            continue
        full_name = html_lib.unescape(name_match.group(1)).strip()
        if full_name.startswith(("search/", "topics/")):
            continue
        desc_match = re.search(r'Content-module__Content[^>]*>\s*<span[^>]*>(.*?)</span>', chunk, re.S)
        lang_match = re.search(r'aria-label="([^"]+) language"', chunk)
        stars_match = re.search(r'aria-label="([^"]+) stars"', chunk)
        updated_match = re.search(r'title="([^"]+ UTC)"', chunk)
        rows.append(
            {
                "category": category,
                "source": source,
                "full_name": full_name,
                "name": full_name.split("/")[-1],
                "url": f"https://github.com/{full_name}",
                "description": decode_text(desc_match.group(1)) if desc_match else "",
                "stars": parse_stars(stars_match.group(1)) if stars_match else 0,
                "forks": 0,
                "language": html_lib.unescape(lang_match.group(1)).strip() if lang_match else "",
                "license": "",
                "pushed_at": normalize_updated(updated_match.group(1)) if updated_match else "",
                "updated_at": normalize_updated(updated_match.group(1)) if updated_match else "",
                "archived": False,
                "open_issues": 0,
            }
        )
    return rows


def search_html(query: str, category: str) -> list[dict]:
    url = "https://github.com/search?" + urllib.parse.urlencode(
        {"q": query, "type": "repositories", "s": "stars", "o": "desc"}
    )
    page = fetch_html(url)
    return parse_search_results(page, category, "search_html")


def repo_html(full_name: str, category: str) -> dict | None:
    url = f"https://github.com/{full_name}"
    try:
        page = fetch_html(url)
    except Exception as exc:
        print(json.dumps({"event": "repo_html_error", "repo": full_name, "error": str(exc)}, ensure_ascii=False), flush=True)
        return None

    def meta(name: str) -> str:
        match = re.search(rf'<meta\s+(?:name|property)="{re.escape(name)}"\s+content="([^"]*)"', page, re.I)
        return html_lib.unescape(match.group(1)).strip() if match else ""

    description = meta("description") or meta("og:description")
    for marker in (f" - GitHub - {full_name}: ", f" - {full_name}"):
        if marker in description:
            description = description.split(marker, 1)[0].strip()

    stars = 0
    match = re.search(r'<span\s+id="repo-stars-counter-star"[^>]*\btitle="([^"]*)"', page, re.S | re.I)
    if match:
        stars = parse_stars(match.group(1))

    pushed_at = ""
    match = re.search(r'"listCacheKey"\s*:\s*"[^"]*:([0-9]{10})(?:\.[0-9]+)?', page)
    if match:
        pushed_at = datetime.fromtimestamp(int(match.group(1)), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "category": category,
        "source": "anchor_html",
        "full_name": full_name,
        "name": full_name.split("/")[-1],
        "url": url,
        "description": description,
        "stars": stars,
        "forks": 0,
        "language": "",
        "license": "",
        "pushed_at": pushed_at,
        "updated_at": pushed_at,
        "archived": False,
        "open_issues": 0,
    }


def text_blob(row: dict) -> str:
    return " ".join([row.get("full_name", ""), row.get("description", ""), row.get("url", "")]).lower()


def is_relevant(row: dict, spec: dict) -> bool:
    blob = text_blob(row)
    if any(term.lower() in blob for term in spec.get("exclude", [])):
        return False
    return any(term.lower() in blob for term in spec.get("include", []))


def parse_dt(value: str) -> datetime | None:
    if not value or not re.match(r"\d{4}-\d{2}-\d{2}T", value):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def age_days(value: str) -> int:
    parsed = parse_dt(value)
    if parsed is None:
        return 9999
    return max(0, (SNAPSHOT - parsed).days)


def triage_score(row: dict) -> float:
    stars = int(row.get("stars") or 0)
    popularity = min(100, math.log10(stars + 1) / math.log10(250_000) * 100) if stars else 0
    days = age_days(row.get("pushed_at", ""))
    if days <= 14:
        freshness = 100
    elif days <= 60:
        freshness = 85
    elif days <= 180:
        freshness = 65
    elif days <= 365:
        freshness = 45
    else:
        freshness = 25
    metadata = 100 if row.get("description", "").strip() else 35
    return round(0.62 * popularity + 0.25 * freshness + 0.13 * metadata, 1)


def collect() -> tuple[list[dict], list[dict]]:
    raw: dict[tuple[str, str], dict] = {}
    query_log: list[dict] = []
    for category, spec in CATEGORIES.items():
        for query in spec["queries"]:
            print(json.dumps({"event": "html_search", "category": category, "query": query}, ensure_ascii=False), flush=True)
            try:
                rows = search_html(query, category)
            except Exception as exc:
                print(json.dumps({"event": "html_search_error", "category": category, "query": query, "error": str(exc)}, ensure_ascii=False), flush=True)
                rows = []
            query_log.append({"category": category, "query": query, "count": len(rows)})
            for row in rows:
                raw.setdefault((category, row["full_name"].lower()), row)
            time.sleep(0.7)

        for full_name in spec["anchors"]:
            key = (category, full_name.lower())
            if key in raw:
                raw[key]["source"] += "+anchor"
                continue
            print(json.dumps({"event": "html_anchor", "category": category, "repo": full_name}, ensure_ascii=False), flush=True)
            row = repo_html(full_name, category)
            if row:
                raw[key] = row
            time.sleep(0.4)

    rows = list(raw.values())
    for row in rows:
        row["relevant"] = is_relevant(row, CATEGORIES[row["category"]])
        row["triage_score"] = triage_score(row)
    return rows, query_log


def curate(raw: list[dict]) -> dict[str, list[dict]]:
    curated: dict[str, list[dict]] = {}
    for category, spec in CATEGORIES.items():
        anchors = {name.lower() for name in spec["anchors"]}
        rows = [
            row
            for row in raw
            if row["category"] == category
            and not row["archived"]
            and (row["relevant"] or row["full_name"].lower() in anchors)
        ]
        rows.sort(key=lambda row: (-float(row["triage_score"]), -int(row["stars"]), row["full_name"].lower()))
        seen = set()
        unique = []
        for row in rows:
            if row["full_name"].lower() in seen:
                continue
            seen.add(row["full_name"].lower())
            unique.append(row)
        curated[category] = unique[:10]
    return curated


def md_escape(value: object) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def short(value: str, limit: int = 145) -> str:
    value = " ".join((value or "").split())
    return value if len(value) <= limit else value[: limit - 3].rstrip() + "..."


def write_outputs(raw: list[dict], query_log: list[dict], curated: dict[str, list[dict]]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    RAW_JSON.write_text(json.dumps({"snapshot": SNAPSHOT.date().isoformat(), "query_log": query_log, "results": raw}, ensure_ascii=False, indent=2), encoding="utf-8")
    CURATED_JSON.write_text(
        json.dumps(
            {
                "snapshot": SNAPSHOT.date().isoformat(),
                "source": "GitHub public HTML search + repository pages",
                "categories": {
                    key: {
                        "title": spec["title"],
                        "description": spec["description"],
                        "repos": curated[key],
                    }
                    for key, spec in CATEGORIES.items()
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    fields = ["category", "category_title", "full_name", "url", "description", "stars", "language", "license", "pushed_at", "triage_score", "source"]
    with CURATED_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for key, rows in curated.items():
            for row in rows:
                writer.writerow({"category": key, "category_title": CATEGORIES[key]["title"], **{field: row.get(field, "") for field in fields if field not in {"category", "category_title"}}})

    lines = [
        "# GitHub Business/Product Landscape Research",
        "",
        f"Snapshot: {SNAPSHOT.date().isoformat()}",
        "",
        "Research scope: open-source repositories for marketing, design, fundraising, finance, legal, support, product, operations, and adjacent startup/business workflows.",
        "",
        "Source: GitHub public repository search pages plus direct public repository pages for known anchors. Scores are triage signals based on stars, freshness, and metadata; they are not endorsements or due-diligence reviews.",
        "",
        "## Categories",
        "",
        "| Category | Repos | Scope |",
        "|---|---:|---|",
    ]
    for key, spec in CATEGORIES.items():
        lines.append(f"| [{md_escape(spec['title'])}](#{key}) | {len(curated[key])} | {md_escape(spec['description'])} |")

    lines.extend(["", "## Recommendations", ""])
    for key, spec in CATEGORIES.items():
        lines.extend(
            [
                f"### {spec['title']}",
                f"<a id=\"{key}\"></a>",
                "",
                spec["description"],
                "",
                "| Repo | Stars | Updated | Score | Why it matters |",
                "|---|---:|---|---:|---|",
            ]
        )
        for row in curated[key]:
            lines.append(
                f"| [{md_escape(row['full_name'])}]({md_escape(row['url'])}) | "
                f"{row['stars']} | {md_escape(row['pushed_at'][:10])} | {row['triage_score']} | "
                f"{md_escape(short(row['description']))} |"
            )
        lines.append("")

    lines.extend(["## Query Log", "", "| Category | Results | Query |", "|---|---:|---|"])
    for entry in query_log:
        lines.append(f"| {entry['category']} | {entry['count']} | `{md_escape(entry['query'])}` |")
    lines.append("")
    CURATED_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    raw, query_log = collect()
    curated = curate(raw)
    write_outputs(raw, query_log, curated)
    print(
        json.dumps(
            {
                "raw_candidates": len(raw),
                "curated_recommendations": sum(len(rows) for rows in curated.values()),
                "categories": len(CATEGORIES),
                "empty_categories": [key for key, rows in curated.items() if not rows],
                "outputs": {
                    "markdown": str(CURATED_MD),
                    "csv": str(CURATED_CSV),
                    "json": str(CURATED_JSON),
                    "raw": str(RAW_JSON),
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
