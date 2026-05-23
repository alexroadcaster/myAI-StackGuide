#!/usr/bin/env python3
"""Build a standalone HTML artifact for the unified GitHub catalog."""

from __future__ import annotations

import html
import json
from pathlib import Path

import build_unified_catalog as unified


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "UNIFIED_CATALOG.html"

DECISION_LENSES = [
    {
        "title": "Agentic Systems",
        "note": "Runtime, context, tools, evaluation, execution, and interoperability.",
        "items": [
            ("Run multi-agent workflows", "agent_runtime_orchestration"),
            ("Connect tools and services", "mcp_integrations"),
            ("Add retrieval and memory", "rag_retrieval_search"),
            ("Evaluate quality and traces", "evals_observability_promptops"),
            ("Execute code safely", "sandboxed_code_execution"),
            ("Support voice or multimodal UX", "voice_realtime_agents"),
        ],
    },
    {
        "title": "Engineering Platform",
        "note": "Developer workflow, UI, data, deployment, docs, security, and research loops.",
        "items": [
            ("Build UI and browser surfaces", "frontend_ui_desktop_browser"),
            ("Improve CLI and dev workflows", "developer_tools_cli"),
            ("Deploy backend or edge systems", "cloudflare_edge_backend"),
            ("Store data and embeddings", "database_storage_sqlite"),
            ("Parse documents and OCR", "document_ocr_parsing"),
            ("Harden security and supply chain", "security_safety_supply_chain"),
        ],
    },
    {
        "title": "Business Operations",
        "note": "Marketing, sales, finance, legal, support, product, and internal operations.",
        "items": [
            ("Grow acquisition and analytics", "marketing_growth_seo"),
            ("Design and brand products", "design_brand_uiux"),
            ("Manage sales and customers", "sales_crm_lead_generation"),
            ("Run finance and accounting", "accounting_finance_erp"),
            ("Handle legal and compliance", "legal_contracts_compliance"),
            ("Automate internal operations", "automation_workflows_nocode"),
        ],
    },
]


def category_rows(categories: dict) -> list[dict]:
    rows = []
    for key, category in categories.items():
        repos = unified.category_repo_rows(category)
        rows.append(
            {
                "key": key,
                "title": category["title"],
                "description": category["description"],
                "groups": list(category["groups"].keys()),
                "repoCount": len(repos),
                "topRepos": [repo["full_name"] for repo in repos[:3]],
                "repos": [
                    {
                        "fullName": repo["full_name"],
                        "url": repo["url"],
                        "description": repo["description"],
                        "stars": repo["stars"],
                        "updated": unified.dateish(repo["updated"]),
                        "score": unified.sorted_scores(repo["scores"]),
                        "scoreValue": repo["best_score"],
                        "sources": unified.sorted_sources(repo["sources"]),
                        "sourceKeys": list(repo["sources"].keys()),
                        "language": repo["language"],
                        "license": repo["license"],
                    }
                    for repo in repos
                ],
            }
        )
    return rows


def build_payload() -> dict:
    categories = unified.load_categories()
    unified.load_repositories(categories)
    rows = category_rows(categories)
    unique_repos = {
        repo["fullName"].lower()
        for category in rows
        for repo in category["repos"]
    }
    return {
        "snapshot": unified.SNAPSHOT,
        "summary": {
            "categories": len(rows),
            "placements": sum(len(category["repos"]) for category in rows),
            "uniqueRepos": len(unique_repos),
            "sources": [
                "data/repos.csv",
                "research/github_curated_recommendations_2026-05-23.json",
                "research/github_business_curated_recommendations_2026-05-23.json",
            ],
        },
        "decisionLenses": DECISION_LENSES,
        "categories": rows,
    }


def page(payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Unified GitHub Category Catalog</title>
  <style>
    :root {{
      --bg: #060606;
      --surface: #101010;
      --surface-2: #1a1510;
      --surface-3: #0b0b0c;
      --ink: #f7ead2;
      --muted: #b7a78d;
      --line: rgba(244, 177, 65, 0.22);
      --line-strong: rgba(246, 196, 106, 0.48);
      --blue: #f0b13e;
      --green: #d08a2c;
      --amber: #f6c46a;
      --red: #e16745;
      --violet: #d9a15f;
      --shadow: 0 18px 48px rgba(0, 0, 0, 0.42);
      --radius: 8px;
      color-scheme: dark;
    }}

    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.45 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    a {{ color: inherit; text-decoration: none; }}
    a:hover {{ color: var(--blue); }}
    .shell {{
      display: grid;
      grid-template-columns: 312px minmax(0, 1fr);
      min-height: 100vh;
    }}
    .sidebar {{
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
      padding: 18px;
      border-right: 1px solid var(--line);
      background: var(--surface-3);
    }}
    .brand {{
      display: grid;
      gap: 8px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--line);
    }}
    .brand h1 {{
      margin: 0;
      font-size: 19px;
      line-height: 1.12;
      letter-spacing: 0;
    }}
    .snapshot {{ color: var(--muted); font-size: 12px; }}
    .search {{
      width: 100%;
      margin: 16px 0 10px;
      padding: 10px 11px;
      border: 1px solid var(--line-strong);
      border-radius: var(--radius);
      background: #070707;
      color: var(--ink);
      outline: none;
    }}
    .search::placeholder {{ color: #8f8069; }}
    .search:focus {{ border-color: var(--amber); box-shadow: 0 0 0 3px rgba(240,177,62,0.18); }}
    .search-help {{
      margin: -2px 0 12px;
      color: var(--muted);
      font-size: 12px;
    }}
    .filters {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }}
    .filter {{
      border: 1px solid var(--line);
      background: #0b0b0b;
      border-radius: 999px;
      padding: 6px 9px;
      font-size: 12px;
      color: var(--muted);
      cursor: pointer;
    }}
    .filter.active {{ border-color: var(--amber); color: #0b0b0b; background: var(--amber); }}
    .nav-list {{ display: grid; gap: 4px; }}
    .nav-item {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      gap: 8px;
      padding: 8px 9px;
      border-radius: var(--radius);
      color: #e1cfad;
    }}
    .nav-item:hover, .nav-item.active {{ background: var(--surface-2); color: var(--ink); }}
    .nav-title {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .count {{
      min-width: 26px;
      padding: 2px 6px;
      border-radius: 999px;
      background: #241b0f;
      color: var(--amber);
      text-align: center;
      font-size: 12px;
    }}
    main {{ min-width: 0; padding: 26px; }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;
      margin-bottom: 18px;
    }}
    .title-block h2 {{
      margin: 0 0 7px;
      font-size: clamp(28px, 4vw, 48px);
      line-height: 1.02;
      letter-spacing: 0;
      overflow-wrap: anywhere;
    }}
    .title-block p {{ margin: 0; max-width: 880px; color: var(--muted); }}
    .source-note {{
      flex: 0 0 260px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      color: var(--muted);
      font-size: 12px;
    }}
    .source-note code {{ overflow-wrap: anywhere; }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(150px, 1fr));
      gap: 10px;
      margin-bottom: 18px;
    }}
    .stat {{
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
    }}
    .stat .value {{ font-size: 27px; font-weight: 750; letter-spacing: 0; }}
    .stat .label {{ color: var(--muted); font-size: 12px; margin-top: 3px; }}
    .section-title {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      margin: 28px 0 12px;
    }}
    .section-title h3 {{ margin: 0; font-size: 20px; }}
    .section-title span {{ color: var(--muted); font-size: 12px; }}
    .decision-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .decision-card {{
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      overflow: hidden;
    }}
    .decision-head {{
      padding: 14px;
      border-bottom: 1px solid var(--line);
      background: #15110d;
    }}
    .decision-head strong {{ display: block; font-size: 15px; }}
    .decision-head p {{ margin: 5px 0 0; color: var(--muted); font-size: 12px; }}
    .decision-row {{
      display: grid;
      grid-template-columns: minmax(110px, 0.9fr) minmax(0, 1.1fr);
      gap: 10px;
      padding: 10px 14px;
      border-top: 1px solid rgba(244, 177, 65, 0.14);
    }}
    .decision-row:first-of-type {{ border-top: 0; }}
    .intent {{ color: #e0cdaa; font-size: 12px; }}
    .path a {{ color: var(--blue); font-weight: 650; }}
    .path small {{ display: block; color: var(--muted); margin-top: 3px; }}
    .visual-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.8fr);
      gap: 12px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      padding: 14px;
    }}
    .bars {{ display: grid; gap: 7px; }}
    .bar-row {{
      display: grid;
      grid-template-columns: minmax(160px, 240px) minmax(0, 1fr) 42px;
      align-items: center;
      gap: 9px;
      font-size: 12px;
    }}
    .bar-label {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .bar-track {{ height: 10px; border-radius: 999px; background: #241b0f; overflow: hidden; }}
    .bar-fill {{ height: 100%; border-radius: inherit; background: var(--blue); }}
    .source-stack {{ display: grid; gap: 10px; }}
    .stack-row {{ display: grid; gap: 5px; }}
    .stack-label {{ display: flex; justify-content: space-between; color: var(--muted); font-size: 12px; }}
    .stack-track {{ height: 16px; border-radius: 999px; background: #241b0f; overflow: hidden; }}
    .stack-fill {{ height: 100%; border-radius: inherit; }}
    .stack-fill.account {{ background: #bc7f2e; }}
    .stack-fill.ai {{ background: #f0b13e; }}
    .stack-fill.business {{ background: #f6c46a; }}
    .category {{
      margin: 14px 0;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      overflow: hidden;
    }}
    .category.hidden {{ display: none; }}
    .category-header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      padding: 16px;
      border-bottom: 1px solid var(--line);
      background: #15110d;
    }}
    .category h4 {{ margin: 0; font-size: 18px; }}
    .category p {{ margin: 6px 0 0; color: var(--muted); max-width: 920px; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 8px;
      border-radius: 999px;
      background: #241b0f;
      color: #f0d6a0;
      font-size: 12px;
    }}
    .chip.account {{ background: #1b1309; color: #d9a15f; border: 1px solid rgba(217,161,95,0.28); }}
    .chip.ai {{ background: #211804; color: var(--amber); border: 1px solid rgba(246,196,106,0.30); }}
    .chip.business {{ background: #2a1708; color: #ffb454; border: 1px solid rgba(255,180,84,0.28); }}
    .repo-total {{
      align-self: start;
      padding: 7px 10px;
      border-radius: 999px;
      background: var(--surface-2);
      color: var(--amber);
      font-weight: 650;
      white-space: nowrap;
    }}
    .repo-table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 920px; }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid rgba(244, 177, 65, 0.12);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
      background: #15110d;
    }}
    td.repo-name {{ min-width: 210px; font-weight: 650; }}
    .repo-meta {{ color: var(--muted); font-size: 12px; margin-top: 3px; }}
    .score-pill {{
      display: inline-block;
      min-width: 48px;
      padding: 4px 7px;
      border-radius: 999px;
      background: #251706;
      color: var(--amber);
      font-weight: 650;
      text-align: center;
      white-space: nowrap;
    }}
    .stars-cell {{ min-width: 110px; }}
    .stars-bar {{ margin-top: 5px; height: 5px; border-radius: 999px; background: #241b0f; overflow: hidden; }}
    .stars-bar span {{ display: block; height: 100%; background: var(--amber); }}
    mark {{
      border-radius: 3px;
      background: rgba(246, 196, 106, 0.30);
      color: #ffe2a6;
      padding: 0 2px;
    }}
    .empty {{
      padding: 22px;
      border: 1px dashed var(--line-strong);
      border-radius: var(--radius);
      background: var(--surface);
      color: var(--muted);
    }}
    .footer {{ margin: 28px 0 8px; color: var(--muted); font-size: 12px; }}

    @media (max-width: 1050px) {{
      .shell {{ grid-template-columns: 1fr; }}
      .sidebar {{
        position: relative;
        height: auto;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }}
      .nav-list {{
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding-bottom: 4px;
      }}
      .nav-item {{
        min-width: 220px;
        border: 1px solid var(--line);
        background: var(--surface);
      }}
      .topbar {{ display: grid; }}
      .source-note {{ flex: initial; }}
      .stats, .decision-grid, .visual-grid {{ grid-template-columns: 1fr; }}
      main {{ padding: 18px; }}
    }}
    @media (max-width: 640px) {{
      .title-block h2 {{ font-size: 26px; line-height: 1.08; }}
      .stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .category-header {{ grid-template-columns: 1fr; }}
      .bar-row {{ grid-template-columns: 1fr 1fr 34px; }}
      .decision-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <h1>Unified GitHub Catalog</h1>
        <div class="snapshot">Snapshot <span id="snapshot"></span></div>
      </div>
      <input id="search" class="search" type="search" placeholder="Search repos, categories, keywords">
      <div class="search-help">Search covers category names, repository names, descriptions, language, license, and source.</div>
      <div class="filters" id="filters"></div>
      <nav class="nav-list" id="nav"></nav>
    </aside>

    <main>
      <div class="topbar">
        <div class="title-block">
          <h2>Repository Decision Catalog</h2>
          <p>A navigable map of open-source repositories across agentic engineering, platform infrastructure, and business operations.</p>
        </div>
        <div class="source-note" id="sourceNote"></div>
      </div>

      <section class="stats" id="stats"></section>

      <section>
        <div class="section-title">
          <h3>Decision Matrix</h3>
          <span>Goal to category to first repository shortlist</span>
        </div>
        <div class="decision-grid" id="decisionGrid"></div>
      </section>

      <section>
        <div class="section-title">
          <h3>Category Landscape</h3>
          <span>Repository density and source coverage</span>
        </div>
        <div class="visual-grid">
          <div class="panel">
            <div class="bars" id="categoryBars"></div>
          </div>
          <div class="panel">
            <div class="source-stack" id="sourceStack"></div>
          </div>
        </div>
      </section>

      <section>
        <div class="section-title">
          <h3>Repositories By Category</h3>
          <span id="visibleCount"></span>
        </div>
        <div id="categories"></div>
        <div class="empty" id="emptyState" hidden>No categories or repositories match the current search/filter.</div>
      </section>

      <div class="footer">Generated from UNIFIED_CATALOG.md source data. Scores are triage signals, not due-diligence ratings.</div>
    </main>
  </div>

  <script id="catalog-data" type="application/json">{data}</script>
  <script>
    const DATA = JSON.parse(document.getElementById('catalog-data').textContent);
    const sourceFilters = [
      ['all', 'All'],
      ['account_fork_catalog', 'Fork catalog'],
      ['github_ai_engineering_research', 'AI/engineering'],
      ['github_business_product_research', 'Business/product']
    ];
    const sourceClass = {{
      account_fork_catalog: 'account',
      github_ai_engineering_research: 'ai',
      github_business_product_research: 'business'
    }};
    let activeSource = 'all';
    let query = '';

    const byKey = new Map(DATA.categories.map(category => [category.key, category]));
    const maxRepos = Math.max(...DATA.categories.map(category => category.repoCount));
    const maxStars = Math.max(...DATA.categories.flatMap(category => category.repos.map(repo => repo.stars)));

    function esc(value) {{
      return String(value ?? '').replace(/[&<>"']/g, ch => ({{
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      }}[ch]));
    }}

    function short(value, limit = 150) {{
      const cleaned = String(value || '').replace(/\\s+/g, ' ').trim();
      return cleaned.length <= limit ? cleaned : cleaned.slice(0, limit - 3).trimEnd() + '...';
    }}

    function formatNumber(value) {{
      return new Intl.NumberFormat('en-US').format(value || 0);
    }}

    function searchTokens() {{
      return query.trim().toLowerCase().split(/\\s+/).filter(Boolean);
    }}

    function includesTokens(text, tokens) {{
      const value = String(text || '').toLowerCase();
      return tokens.every(token => value.includes(token));
    }}

    function categorySearchText(category) {{
      return [category.title, category.description, category.groups.join(' '), category.topRepos.join(' ')].join(' ');
    }}

    function repoSearchText(repo) {{
      return [
        repo.fullName,
        repo.description,
        repo.language,
        repo.license,
        repo.sources,
        repo.updated,
        String(repo.stars)
      ].join(' ');
    }}

    function escapeRegExp(value) {{
      return String(value).replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
    }}

    function highlighted(value) {{
      let safe = esc(value);
      const tokens = searchTokens().filter(token => token.length > 1).sort((a, b) => b.length - a.length);
      for (const token of tokens) {{
        safe = safe.replace(new RegExp(escapeRegExp(esc(token)), 'ig'), match => `<mark>${{match}}</mark>`);
      }}
      return safe;
    }}

    function repoMatchesSource(repo) {{
      return activeSource === 'all' || repo.sourceKeys.includes(activeSource);
    }}

    function categoryMatches(category) {{
      const tokens = searchTokens();
      const sourceHit = activeSource === 'all' || category.repos.some(repoMatchesSource);
      if (!sourceHit) return false;
      if (!tokens.length) return true;
      if (includesTokens(categorySearchText(category), tokens)) return true;
      return category.repos.some(repo => repoMatchesSource(repo) && includesTokens(repoSearchText(repo), tokens));
    }}

    function filteredRepos(category) {{
      const tokens = searchTokens();
      const sourced = category.repos.filter(repoMatchesSource);
      if (!tokens.length) return sourced;
      const repoMatches = sourced.filter(repo => includesTokens(repoSearchText(repo), tokens));
      if (repoMatches.length) return repoMatches;
      if (includesTokens(categorySearchText(category), tokens)) return sourced;
      return [];
    }}

    function renderStats() {{
      const stats = [
        ['Categories', DATA.summary.categories],
        ['Category placements', DATA.summary.placements],
        ['Unique repositories', DATA.summary.uniqueRepos],
        ['Source files', DATA.summary.sources.length]
      ];
      document.getElementById('stats').innerHTML = stats.map(([label, value]) => `
        <div class="stat">
          <div class="value">${{formatNumber(value)}}</div>
          <div class="label">${{esc(label)}}</div>
        </div>
      `).join('');
      document.getElementById('snapshot').textContent = DATA.snapshot;
      document.getElementById('sourceNote').innerHTML = `
        <strong>Sources</strong><br>
        ${{DATA.summary.sources.map(source => `<code>${{esc(source)}}</code>`).join('<br>')}}
      `;
    }}

    function renderFilters() {{
      document.getElementById('filters').innerHTML = sourceFilters.map(([key, label]) => `
        <button class="filter ${{activeSource === key ? 'active' : ''}}" data-source="${{key}}" type="button">${{esc(label)}}</button>
      `).join('');
      document.querySelectorAll('.filter').forEach(button => {{
        button.addEventListener('click', () => {{
          activeSource = button.dataset.source;
          render();
        }});
      }});
    }}

    function renderNav(categories) {{
      document.getElementById('nav').innerHTML = categories.map(category => `
        <a class="nav-item" href="#${{esc(category.key)}}" data-nav="${{esc(category.key)}}">
          <span class="nav-title">${{esc(category.title)}}</span>
          <span class="count">${{filteredRepos(category).length}}</span>
        </a>
      `).join('');
    }}

    function decisionItem(intent, key) {{
      const category = byKey.get(key);
      if (!category) return '';
      const repos = category.repos.slice(0, 2).map(repo => repo.fullName).join(', ');
      return `
        <div class="decision-row">
          <div class="intent">${{esc(intent)}}</div>
          <div class="path">
            <a href="#${{esc(key)}}">${{esc(category.title)}}</a>
            <small>${{esc(repos)}}</small>
          </div>
        </div>
      `;
    }}

    function renderDecisionGrid() {{
      document.getElementById('decisionGrid').innerHTML = DATA.decisionLenses.map(lens => `
        <div class="decision-card">
          <div class="decision-head">
            <strong>${{esc(lens.title)}}</strong>
            <p>${{esc(lens.note)}}</p>
          </div>
          ${{lens.items.map(([intent, key]) => decisionItem(intent, key)).join('')}}
        </div>
      `).join('');
    }}

    function renderLandscape() {{
      const sorted = [...DATA.categories].sort((a, b) => b.repoCount - a.repoCount).slice(0, 18);
      document.getElementById('categoryBars').innerHTML = sorted.map(category => `
        <div class="bar-row">
          <a class="bar-label" href="#${{esc(category.key)}}">${{esc(category.title)}}</a>
          <div class="bar-track"><div class="bar-fill" style="width:${{Math.max(4, category.repoCount / maxRepos * 100)}}%"></div></div>
          <div>${{category.repoCount}}</div>
        </div>
      `).join('');

      const sourceCounts = {{
        account_fork_catalog: 0,
        github_ai_engineering_research: 0,
        github_business_product_research: 0
      }};
      DATA.categories.forEach(category => {{
        category.repos.forEach(repo => repo.sourceKeys.forEach(source => {{
          if (source in sourceCounts) sourceCounts[source] += 1;
        }}));
      }});
      const maxSource = Math.max(...Object.values(sourceCounts));
      document.getElementById('sourceStack').innerHTML = sourceFilters.slice(1).map(([key, label]) => `
        <div class="stack-row">
          <div class="stack-label"><span>${{esc(label)}}</span><span>${{formatNumber(sourceCounts[key])}}</span></div>
          <div class="stack-track"><div class="stack-fill ${{sourceClass[key]}}" style="width:${{Math.max(5, sourceCounts[key] / maxSource * 100)}}%"></div></div>
        </div>
      `).join('');
    }}

    function sourceChips(category) {{
      return category.groups.map(group => {{
        const cls = group.includes('Business') ? 'business' : group.includes('AI') ? 'ai' : 'account';
        return `<span class="chip ${{cls}}">${{esc(group)}}</span>`;
      }}).join('');
    }}

    function repoRow(repo) {{
      const starWidth = Math.max(2, Math.min(100, repo.stars / maxStars * 100));
      return `
        <tr>
          <td class="repo-name">
            <a href="${{esc(repo.url)}}" target="_blank" rel="noreferrer">${{highlighted(repo.fullName)}}</a>
            <div class="repo-meta">${{highlighted([repo.language, repo.license].filter(Boolean).join(' / '))}}</div>
          </td>
          <td class="stars-cell">
            ${{formatNumber(repo.stars)}}
            <div class="stars-bar"><span style="width:${{starWidth}}%"></span></div>
          </td>
          <td>${{esc(repo.updated)}}</td>
          <td><span class="score-pill">${{esc(repo.score || 'n/a')}}</span></td>
          <td>${{highlighted(repo.sources)}}</td>
          <td>${{highlighted(short(repo.description))}}</td>
        </tr>
      `;
    }}

    function renderCategories() {{
      const visible = DATA.categories.filter(categoryMatches);
      const repoMatchCount = visible.reduce((sum, category) => sum + filteredRepos(category).length, 0);
      document.getElementById('visibleCount').textContent = searchTokens().length
        ? `${{visible.length}} categories / ${{repoMatchCount}} matching repositories`
        : `${{visible.length}} of ${{DATA.categories.length}} categories`;
      document.getElementById('emptyState').hidden = visible.length > 0;
      document.getElementById('categories').innerHTML = visible.map(category => {{
        const repos = filteredRepos(category);
        return `
          <article class="category" id="${{esc(category.key)}}" data-category="${{esc(category.key)}}">
            <div class="category-header">
              <div>
                <h4>${{highlighted(category.title)}}</h4>
                <p>${{highlighted(category.description || 'No category description available.')}}</p>
                <div class="chips">${{sourceChips(category)}}${{category.topRepos.slice(0, 3).map(repo => `<span class="chip">${{esc(repo)}}</span>`).join('')}}</div>
              </div>
              <div class="repo-total">${{repos.length}} repos</div>
            </div>
            <div class="repo-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Repository</th>
                    <th>Stars</th>
                    <th>Updated</th>
                    <th>Score</th>
                    <th>Source</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>${{repos.map(repoRow).join('')}}</tbody>
              </table>
            </div>
          </article>
        `;
      }}).join('');
    }}

    function render() {{
      const visibleCategories = DATA.categories.filter(categoryMatches);
      renderFilters();
      renderNav(visibleCategories);
      renderCategories();
    }}

    function setupActiveNav() {{
      const observer = new IntersectionObserver(entries => {{
        entries.forEach(entry => {{
          if (!entry.isIntersecting) return;
          document.querySelectorAll('.nav-item').forEach(item => item.classList.toggle('active', item.dataset.nav === entry.target.id));
        }});
      }}, {{ rootMargin: '-20% 0px -70% 0px', threshold: 0 }});
      const watch = () => {{
        document.querySelectorAll('.category').forEach(section => observer.observe(section));
      }};
      const target = document.getElementById('categories');
      new MutationObserver(watch).observe(target, {{ childList: true }});
      watch();
    }}

    document.getElementById('search').addEventListener('input', event => {{
      query = event.target.value;
      render();
    }});

    renderStats();
    renderDecisionGrid();
    renderLandscape();
    render();
    setupActiveNav();
  </script>
</body>
</html>
"""


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(page(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "categories": payload["summary"]["categories"],
                "placements": payload["summary"]["placements"],
                "unique_repositories": payload["summary"]["uniqueRepos"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
