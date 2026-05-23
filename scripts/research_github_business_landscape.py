#!/usr/bin/env python3
"""Search GitHub for business/product OSS categories adjacent to the catalog."""

from __future__ import annotations

import csv
import html as html_lib
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "research"
SNAPSHOT = datetime(2026, 5, 23, tzinfo=timezone.utc)
RAW_JSON = OUT_DIR / "github_business_search_candidates_2026-05-23.json"
CURATED_JSON = OUT_DIR / "github_business_curated_recommendations_2026-05-23.json"
CURATED_CSV = OUT_DIR / "github_business_curated_recommendations_2026-05-23.csv"
CURATED_MD = OUT_DIR / "github_business_curated_recommendations_2026-05-23.md"

UA = {
    "User-Agent": "Codex-GitHub-Business-Landscape-Research",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


CATEGORIES: OrderedDict[str, dict] = OrderedDict(
    [
        (
            "marketing_growth_seo",
            {
                "title": "Marketing, Growth & SEO",
                "description": "Marketing automation, SEO, growth analytics, attribution, campaigns, and product-led growth tooling.",
                "queries": [
                    "marketing automation open source in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                    "seo analytics growth open source in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                    "product analytics growth in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                ],
                "include": ["marketing", "seo", "growth", "analytics", "campaign", "attribution", "posthog", "plausible", "matomo", "mautic"],
                "exclude": ["awesome", "interview"],
                "anchors": [
                    "PostHog/posthog",
                    "umami-software/umami",
                    "plausible/analytics",
                    "matomo-org/matomo",
                    "mautic/mautic",
                    "growthbook/growthbook",
                    "Openpanel-dev/openpanel",
                    "Countly/countly-server",
                ],
            },
        ),
        (
            "content_social_community",
            {
                "title": "Content, Social & Community",
                "description": "CMS, publishing, newsletters, social scheduling, community platforms, and content operations.",
                "queries": [
                    "open source cms publishing newsletter in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                    "social media scheduling open source in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                    "community forum open source in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                ],
                "include": ["cms", "publishing", "newsletter", "social", "community", "forum", "blog", "content", "discourse", "ghost"],
                "exclude": ["awesome", "agency-agents", "frontend wizards"],
                "anchors": [
                    "TryGhost/Ghost",
                    "discourse/discourse",
                    "mastodon/mastodon",
                    "gitroomhq/postiz-app",
                    "inovector/mixpost",
                    "trypostit/trypost",
                    "usememos/memos",
                ],
            },
        ),
        (
            "design_brand_uiux",
            {
                "title": "Design, Brand & UI/UX",
                "description": "Design systems, prototyping, whiteboards, diagrams, UI builders, brand assets, and design workflow tools.",
                "queries": [
                    "open source design system ui components in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                    "open source design tool figma alternative in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                    "diagram whiteboard open source design in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                ],
                "include": ["design", "ui", "ux", "whiteboard", "diagram", "wireframe", "prototype", "components", "brand", "figma"],
                "exclude": ["awesome", "open-webui", "yjs/yjs"],
                "anchors": [
                    "penpot/penpot",
                    "excalidraw/excalidraw",
                    "tldraw/tldraw",
                    "storybookjs/storybook",
                    "shadcn-ui/ui",
                    "nexu-io/open-design",
                    "OpenCoworkAI/open-codesign",
                    "Vrun-design/openflowkit",
                ],
            },
        ),
        (
            "sales_crm_lead_generation",
            {
                "title": "Sales, CRM & Lead Generation",
                "description": "CRM, lead management, outbound pipelines, enrichment, sales workflows, and account management.",
                "queries": [
                    "open source crm sales in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                    "lead generation crm open source in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                    "sales pipeline open source crm in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                ],
                "include": ["crm", "sales", "lead", "pipeline", "customer relationship", "twenty", "erpnext"],
                "exclude": ["awesome"],
                "anchors": ["twentyhq/twenty", "monicahq/monica", "salesagility/SuiteCRM", "frappe/erpnext", "EspoCRM/EspoCRM"],
            },
        ),
        (
            "fundraising_investor_relations",
            {
                "title": "Fundraising, Investor Relations & Startup Ops",
                "description": "Investor CRM, fundraising pipelines, pitch/deck workflows, cap tables, donation systems, startup operating systems, and venture research.",
                "queries": [
                    "fundraising investor relations startup open source in:name,description,readme stars:>20 pushed:>2025-01-01 archived:false",
                    "cap table open source startup in:name,description,readme stars:>20 pushed:>2025-01-01 archived:false",
                    "pitch deck investor open source in:name,description,readme stars:>20 pushed:>2025-01-01 archived:false",
                ],
                "include": [
                    "fundraising",
                    "investor",
                    "cap table",
                    "capitalization",
                    "startup",
                    "venture",
                    "pitch",
                    "deck",
                    "equity",
                    "donation",
                    "donate",
                    "nonprofit",
                    "crowdfunding",
                ],
                "exclude": ["cryptocurrency", "defi", "awesome", "html-anything", "boilerplate"],
                "anchors": [
                    "Open-Cap-Table-Coalition/Open-Cap-Format-OCF",
                    "captableinc/captable",
                    "houdiniproject/houdini",
                    "impress-org/givewp",
                    "wc-donation/wc-donation-platform",
                    "OpenBB-finance/OpenBB",
                ],
            },
        ),
        (
            "accounting_finance_erp",
            {
                "title": "Accounting, Finance & ERP",
                "description": "Bookkeeping, invoicing, accounting, ERP, budgeting, expenses, and finance back-office systems.",
                "queries": [
                    "open source accounting invoicing erp in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                    "open source bookkeeping invoice finance in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                    "expense management open source accounting in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                ],
                "include": ["accounting", "invoice", "invoicing", "erp", "bookkeeping", "finance", "expense", "budget"],
                "exclude": ["awesome"],
                "anchors": [
                    "frappe/erpnext",
                    "odoo/odoo",
                    "akaunting/akaunting",
                    "invoiceplane/InvoicePlane",
                    "maybe-finance/maybe",
                    "actualbudget/actual",
                    "firefly-iii/firefly-iii",
                ],
            },
        ),
        (
            "legal_contracts_compliance",
            {
                "title": "Legal, Contracts & Compliance",
                "description": "Contracts, document automation, e-signature, privacy, governance, compliance, and policy operations.",
                "queries": [
                    "open source contract management legal in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
                    "open source e-signature document signing in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                    "open source compliance privacy governance in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                ],
                "include": [
                    "contract",
                    "legal",
                    "legaltech",
                    "signature",
                    "signing",
                    "esign",
                    "e-signature",
                    "compliance",
                    "privacy",
                    "governance",
                    "policy",
                    "docuseal",
                    "docusign",
                    "regulatory",
                ],
                "exclude": ["awesome", "system-design", "interview"],
                "anchors": [
                    "docusealco/docuseal",
                    "documenso/documenso",
                    "OpenSignLabs/OpenSign",
                    "prowler-cloud/prowler",
                    "Open-Cap-Table-Coalition/Open-Cap-Format-OCF",
                    "accordproject/template-archive",
                    "opengovsg/FormSG",
                ],
            },
        ),
        (
            "analytics_bi_reporting",
            {
                "title": "Analytics, BI & Reporting",
                "description": "Dashboards, BI, metrics stores, product analytics, reporting, and executive visibility.",
                "queries": [
                    "open source business intelligence dashboard in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                    "open source analytics dashboard reporting in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                    "metrics dashboard open source product analytics in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                ],
                "include": ["analytics", "dashboard", "bi", "business intelligence", "reporting", "metrics", "superset", "metabase"],
                "exclude": ["awesome"],
                "anchors": ["apache/superset", "metabase/metabase", "getredash/redash", "grafana/grafana", "PostHog/posthog"],
            },
        ),
        (
            "customer_support_success",
            {
                "title": "Customer Support & Success",
                "description": "Helpdesk, live chat, ticketing, customer success, knowledge support, and support automation.",
                "queries": [
                    "open source helpdesk customer support in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                    "open source live chat support ticketing in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                    "customer success open source support in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                ],
                "include": ["helpdesk", "support", "ticket", "ticketing", "live chat", "customer", "chatwoot", "zammad"],
                "exclude": ["awesome"],
                "anchors": [
                    "chatwoot/chatwoot",
                    "zammad/zammad",
                    "freescout-helpdesk/freescout",
                    "frappe/helpdesk",
                    "helpyio/helpy",
                    "uvdesk/community-skeleton",
                    "crisp-im/crisp-sdk-web",
                ],
            },
        ),
        (
            "product_management_feedback",
            {
                "title": "Product Management, Roadmaps & Feedback",
                "description": "Feature requests, roadmap planning, feedback collection, issue triage, changelogs, and product discovery.",
                "queries": [
                    "open source product roadmap feedback in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                    "feature requests open source roadmap in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                    "open source changelog feedback product management in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
                ],
                "include": ["roadmap", "feedback", "feature request", "changelog", "product", "kanban", "planning"],
                "exclude": ["awesome"],
                "anchors": [
                    "makeplane/plane",
                    "getfider/fider",
                    "QuackbackIO/quackback",
                    "logchimp/logchimp",
                    "rowyio/roadmap",
                ],
            },
        ),
        (
            "ecommerce_payments_revenue",
            {
                "title": "E-commerce, Payments & Revenue",
                "description": "Commerce platforms, checkout, payments, billing, subscriptions, pricing, and revenue operations.",
                "queries": [
                    "open source ecommerce platform payments in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                    "open source billing subscription stripe in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                    "open source payments checkout commerce in:name,description,readme stars:>100 pushed:>2025-01-01 archived:false",
                ],
                "include": ["ecommerce", "commerce", "payment", "billing", "subscription", "checkout", "stripe", "revenue"],
                "exclude": ["awesome", "starter kit", "boilerplate", "template"],
                "anchors": [
                    "medusajs/medusa",
                    "saleor/saleor",
                    "spree/spree",
                    "Sylius/Sylius",
                    "vendure-ecommerce/vendure",
                    "bagisto/bagisto",
                    "woocommerce/woocommerce",
                    "btcpayserver/btcpayserver",
                    "calcom/cal.com",
                    "KillBill/killbill",
                    "flowglad/flowglad",
                    "Subscribie/subscribie",
                    "ever-co/ever-gauzy",
                ],
            },
        ),
        (
            "hr_recruiting_people_ops",
            {
                "title": "HR, Recruiting & People Ops",
                "description": "Recruiting, applicant tracking, HRIS, payroll-adjacent workflows, employee operations, and team directories.",
                "queries": [
                    "open source applicant tracking recruiting in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
                    "open source HRIS employee management in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
                    "open source payroll HR recruiting in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
                ],
                "include": ["recruiting", "recruitment", "applicant", "ats", "hr", "hris", "employee", "payroll", "people"],
                "exclude": ["awesome", "activepieces", "n8n"],
                "anchors": [
                    "frappe/hrms",
                    "ever-co/ever-gauzy",
                    "opencats/OpenCATS",
                    "freeats/freeats",
                    "profilecity/vidur",
                    "reqcore-inc/reqcore",
                    "horilla/horilla-hr",
                ],
            },
        ),
        (
            "operations_project_management",
            {
                "title": "Operations, Project Management & Internal Tools",
                "description": "Project management, internal tools, admin panels, task systems, workflows, and operational command centers.",
                "queries": [
                    "open source project management internal tools in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                    "open source admin panel internal tool in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                    "open source kanban task management in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                ],
                "include": ["project management", "internal tool", "admin", "kanban", "tasks", "workflow", "operations"],
                "exclude": ["awesome"],
                "anchors": ["appsmithorg/appsmith", "ToolJet/ToolJet", "Budibase/budibase", "makeplane/plane", "taigaio/taiga"],
            },
        ),
        (
            "automation_workflows_nocode",
            {
                "title": "Automation, Workflows & No-code",
                "description": "Workflow builders, no-code/low-code automation, integrations, scheduling, and internal process automation.",
                "queries": [
                    "open source workflow automation no-code in:name,description,readme stars:>500 pushed:>2025-01-01 archived:false",
                    "open source zapier alternative workflow in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                    "open source low-code automation integrations in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                ],
                "include": ["workflow", "automation", "no-code", "low-code", "zapier", "integrations", "n8n", "activepieces"],
                "exclude": ["awesome"],
                "anchors": ["n8n-io/n8n", "activepieces/activepieces", "huginn/huginn", "windmill-labs/windmill", "automatisch/automatisch"],
            },
        ),
        (
            "market_research_competitive_intel",
            {
                "title": "Market Research & Competitive Intelligence",
                "description": "Research, web monitoring, trend detection, OSINT, scraping, social listening, and competitive intelligence.",
                "queries": [
                    "open source market research competitive intelligence in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
                    "open source trend monitoring social listening in:name,description,readme stars:>50 pushed:>2025-01-01 archived:false",
                    "open source osint web monitoring in:name,description,readme stars:>300 pushed:>2025-01-01 archived:false",
                ],
                "include": ["market research", "competitive", "intelligence", "trend", "monitoring", "osint", "social listening", "web monitoring"],
                "exclude": ["awesome"],
                "anchors": [
                    "mendableai/firecrawl",
                    "sansan0/TrendRadar",
                    "ArchiveBox/ArchiveBox",
                    "microsoft/markitdown",
                    "dgtlmoon/changedetection.io",
                    "lissy93/web-check",
                ],
            },
        ),
    ]
)


def api_get(url: str) -> tuple[dict, dict[str, str]]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as response:
        headers = {k.lower(): v for k, v in response.headers.items()}
        return json.loads(response.read().decode("utf-8")), headers


def wait_from_headers(headers: dict[str, str]) -> None:
    remaining = int(headers.get("x-ratelimit-remaining", "1") or 1)
    if remaining > 0:
        return
    reset = int(headers.get("x-ratelimit-reset", "0") or 0)
    delay = max(3, reset - int(time.time()) + 2)
    print(json.dumps({"event": "rate_limit_wait", "seconds": delay}, ensure_ascii=False), flush=True)
    time.sleep(delay)


def search_repositories(query: str, per_page: int = 20) -> list[dict]:
    encoded = urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": per_page})
    url = f"https://api.github.com/search/repositories?{encoded}"
    for _ in range(4):
        try:
            payload, headers = api_get(url)
            wait_from_headers(headers)
            return payload.get("items", [])
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in (403, 429):
                reset = int(exc.headers.get("x-ratelimit-reset", "0") or 0)
                delay = max(10, reset - int(time.time()) + 2)
                print(json.dumps({"event": "search_wait", "status": exc.code, "seconds": delay, "query": query, "body": body[:160]}, ensure_ascii=False), flush=True)
                time.sleep(delay)
                continue
            print(json.dumps({"event": "search_error", "status": exc.code, "query": query, "body": body[:240]}, ensure_ascii=False), flush=True)
            return []
    return []


def fetch_repo(full_name: str) -> dict | None:
    """Fetch anchor metadata from public HTML to avoid unauthenticated core API limits."""
    url = f"https://github.com/{full_name}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 Codex-GitHub-Business-Landscape-Research",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            page = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        print(json.dumps({"event": "repo_html_error", "repo": full_name, "error": str(exc)}, ensure_ascii=False), flush=True)
        return None

    def meta(name: str) -> str:
        pattern = rf'<meta\s+(?:name|property)="{re.escape(name)}"\s+content="([^"]*)"'
        match = re.search(pattern, page, re.I)
        return html_lib.unescape(match.group(1)).strip() if match else ""

    description = meta("description") or meta("og:description")
    for suffix in (f" - {full_name}", f" - GitHub - {full_name}: "):
        if suffix in description:
            description = description.split(suffix, 1)[0].strip()

    stars = 0
    match = re.search(r'<span\s+id="repo-stars-counter-star"[^>]*\btitle="([^"]*)"', page, re.S | re.I)
    if match:
        stars_text = html_lib.unescape(match.group(1)).replace(",", "").strip()
        try:
            stars = int(float(stars_text))
        except ValueError:
            stars = 0

    pushed_at = ""
    match = re.search(r'"listCacheKey"\s*:\s*"[^"]*:([0-9]{10})(?:\.[0-9]+)?', page)
    if match:
        pushed_at = datetime.fromtimestamp(int(match.group(1)), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "full_name": full_name,
        "name": full_name.split("/")[-1],
        "html_url": url,
        "description": description,
        "stargazers_count": stars,
        "forks_count": 0,
        "language": "",
        "license": None,
        "pushed_at": pushed_at,
        "updated_at": "",
        "archived": False,
        "open_issues_count": 0,
    }


def normalize(repo: dict, category: str, source: str) -> dict:
    license_payload = repo.get("license") or {}
    return {
        "category": category,
        "source": source,
        "full_name": repo.get("full_name", ""),
        "name": repo.get("name", ""),
        "url": repo.get("html_url", ""),
        "description": repo.get("description") or "",
        "stars": int(repo.get("stargazers_count") or 0),
        "forks": int(repo.get("forks_count") or 0),
        "language": repo.get("language") or "",
        "license": license_payload.get("spdx_id") or "",
        "pushed_at": repo.get("pushed_at") or "",
        "updated_at": repo.get("updated_at") or "",
        "archived": bool(repo.get("archived")),
        "open_issues": int(repo.get("open_issues_count") or 0),
    }


def text_blob(row: dict) -> str:
    return " ".join([row.get("full_name", ""), row.get("description", ""), row.get("url", "")]).lower()


def is_relevant(row: dict, spec: dict) -> bool:
    blob = text_blob(row)
    if any(term.lower() in blob for term in spec.get("exclude", [])):
        return False
    return any(term.lower() in blob for term in spec.get("include", []))


def parse_dt(value: str) -> datetime | None:
    if not value:
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
        freshness = 20
    metadata = 100 if row.get("description", "").strip() else 35
    license_score = 100 if row.get("license") and row.get("license") != "NOASSERTION" else 55
    return round(0.55 * popularity + 0.25 * freshness + 0.12 * metadata + 0.08 * license_score, 1)


def collect() -> tuple[list[dict], list[dict]]:
    raw_by_key: dict[tuple[str, str], dict] = {}
    query_log: list[dict] = []

    for category, spec in CATEGORIES.items():
        for query in spec["queries"]:
            print(json.dumps({"event": "search", "category": category, "query": query}, ensure_ascii=False), flush=True)
            items = search_repositories(query)
            query_log.append({"category": category, "query": query, "count": len(items)})
            for item in items:
                normalized = normalize(item, category, "search")
                key = (category, normalized["full_name"].lower())
                if key not in raw_by_key:
                    raw_by_key[key] = normalized

        for full_name in spec["anchors"]:
            key = (category, full_name.lower())
            if key in raw_by_key:
                raw_by_key[key]["source"] += "+anchor"
                continue
            print(json.dumps({"event": "anchor", "category": category, "repo": full_name}, ensure_ascii=False), flush=True)
            item = fetch_repo(full_name)
            if item:
                raw_by_key[key] = normalize(item, category, "anchor")

    raw = list(raw_by_key.values())
    for row in raw:
        row["relevant"] = is_relevant(row, CATEGORIES[row["category"]])
        row["triage_score"] = triage_score(row)

    return raw, query_log


def curate(raw: list[dict]) -> dict[str, list[dict]]:
    curated: dict[str, list[dict]] = {}
    for category, spec in CATEGORIES.items():
        rows = [row for row in raw if row["category"] == category and row["relevant"] and not row["archived"]]
        anchors = {name.lower() for name in spec["anchors"]}
        # Keep anchors even when metadata text is sparse.
        for row in raw:
            if row["category"] == category and row["full_name"].lower() in anchors and not row["archived"] and row not in rows:
                rows.append(row)
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

    fields = [
        "category",
        "category_title",
        "full_name",
        "url",
        "description",
        "stars",
        "forks",
        "language",
        "license",
        "pushed_at",
        "updated_at",
        "open_issues",
        "triage_score",
        "source",
    ]
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
        "Source: GitHub Search API plus direct metadata checks for known anchor repositories. Scores are triage signals based on stars, freshness, metadata, and license presence; they are not endorsements or due-diligence reviews.",
        "",
        "## Categories",
        "",
        "| Category | Repos | Scope |",
        "|---|---:|---|",
    ]
    for key, spec in CATEGORIES.items():
        lines.append(f"| [{md_escape(spec['title'])}](#{key}) | {len(curated[key])} | {md_escape(spec['description'])} |")

    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for key, spec in CATEGORIES.items():
        lines.extend(
            [
                f"### {spec['title']}",
                f"<a id=\"{key}\"></a>",
                "",
                spec["description"],
                "",
                "| Repo | Stars | Updated | Score | License | Why it matters |",
                "|---|---:|---|---:|---|---|",
            ]
        )
        for row in curated[key]:
            lines.append(
                f"| [{md_escape(row['full_name'])}]({md_escape(row['url'])}) | "
                f"{row['stars']} | {md_escape(row['pushed_at'][:10])} | {row['triage_score']} | "
                f"{md_escape(row['license'])} | {md_escape(short(row['description']))} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Query Log",
            "",
            "| Category | Results | Query |",
            "|---|---:|---|",
        ]
    )
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
