# Contributing

Contributions should keep the catalog useful, auditable, and low-noise.

## Update The Current HTML Catalog

1. Update `data/catalog_manifest.json` without changing its snapshot or provenance semantics silently.
2. Update `templates/unified_catalog.html` only for standalone UI changes.
3. Run `python scripts/build_catalog_html.py`.
4. Run `python scripts/build_catalog_html.py --check` and the focused catalog pipeline tests.

Keep the manifest as canonical compact JSON. Repository facts must be source-backed; unknown values remain null or `unknown`.

## Add or Update a Repository

The following steps update the legacy account-fork catalog:

1. Edit `data/source_repos.csv`.
2. Run `python scripts/build_catalog.py`.
3. Check the generated category page.
4. Open a pull request with a short note explaining why the repository belongs in the catalog.

## Inclusion Criteria

- The repository should be directly useful for agentic software engineering, AI coding workflows, RAG, memory, MCP, evals, document processing, or supporting infrastructure.
- The project should have a public source URL.
- Metadata should be factual and based on upstream public information.

## Avoid

- Promotional descriptions that are not present upstream.
- Private or leaked data.
- Security claims without evidence.
- Star-count-only ranking arguments.
