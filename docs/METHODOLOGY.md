# Methodology

This repository uses a lightweight curation model designed for a practical engineering catalog.

## Current HTML v5 Source

`data/catalog_manifest.json` is the source-owned current catalog snapshot. `templates/unified_catalog.html` owns the standalone UI shell, and `scripts/build_catalog_html.py` validates both inputs before generating `docs/UNIFIED_CATALOG.html`.

The dated CSV and research inputs below retain the legacy 2026-05-23 boundary and generate the Markdown catalog. They must not silently overwrite newer v5 repository facts.

## Classification

Each repository receives one `primary_category` plus zero or more `secondary_tags`.

Primary categories are assigned with a curated override map first, then keyword matching over repository name, source URL, and source description. This keeps obvious projects stable while still allowing new rows to be classified automatically.

## Rating

`curation_score` is a composite score from public metadata:

| Component | Weight | Why it matters |
|---|---:|---|
| Popularity | 45% | Star count is an imperfect but useful proxy for adoption and discovery. It is log-scaled to avoid letting massive repos dominate completely. |
| Freshness | 25% | Recently updated repositories are more likely to be compatible with current agent tooling. |
| Metadata | 15% | A clear description makes the repo easier to evaluate quickly. |
| License | 10% | A visible license reduces adoption ambiguity. |
| Size practicality | 5% | Smaller repos are mildly favored because they are easier to inspect, fork, and adapt. |

The score is for catalog triage. It is not a security review, code quality audit, or production readiness certification.

## Maintenance

1. Update `data/source_repos.csv`.
2. Run `python scripts/build_catalog.py`.
3. Review diffs in `README.md`, `categories/*.md`, and `data/repos.csv`.
4. Manually adjust `PRIMARY_OVERRIDES` if a repo lands in the wrong primary category.
