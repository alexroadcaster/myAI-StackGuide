# Release And Update Process

Short process for refreshing, verifying, and publishing a catalog snapshot.

## 1. Choose The Update Type

Pick one primary update type before editing:

- Current catalog data update: change `data/catalog_manifest.json` while preserving its schema, provenance, and snapshot boundary.
- Legacy fork-catalog update: add, remove, or correct rows in `data/source_repos.csv`.
- Current taxonomy update: change source-owned categories/aliases in `data/catalog_manifest.json` and its contract. Legacy fork taxonomy alone uses patterns/descriptions/`PRIMARY_OVERRIDES` in `scripts/build_catalog.py`.
- Research refresh: regenerate AI/engineering or business/product research snapshots.
- Artifact release: rebuild Markdown or HTML outputs from their documented source data.
- UI update: change `templates/unified_catalog.html`; keep data changes in the manifest.

Do not mix update types unless the release explicitly needs the combined change.

## 2. Refresh Inputs

For account fork catalog updates:

```powershell
python scripts/build_catalog.py
```

For AI/engineering research refreshes, use the GitHub API research script and record the snapshot date:

```powershell
python scripts/research_github_landscape.py
```

For business/product research refreshes, prefer API-backed enrichment when possible. If HTML-backed search is used, mark the source as lower-confidence in the release notes.

```powershell
python scripts/research_github_business_landscape.py
```

Use `scripts/research_github_business_landscape_html.py` only when API search is unavailable or insufficient, and record that limitation.

## 3. Rebuild Artifacts

Run from the repository root:

```powershell
python scripts/build_catalog.py
python scripts/build_unified_catalog.py
python scripts/build_catalog_html.py
```

Expected generated outputs:

- `docs/METHODOLOGY.md`
- `docs/CONTRIBUTING.md`
- `docs/LICENSE`
- `LICENSE`
- `.gitignore`
- `data/repos.csv`
- `data/repos.json`
- `data/categories.json`
- `categories/*.md`
- `docs/UNIFIED_CATALOG.md`
- `docs/UNIFIED_CATALOG.html`

`data/catalog_manifest.json` and `templates/unified_catalog.html` are the source-owned inputs for the current HTML catalog. `README.md` is a curated product-facing guide. Update it intentionally when positioning, usage guidance, stack recipes, or release instructions change.

## 4. Verify

Check repository state:

```powershell
git -c core.excludesfile= status --short
```

Run generated-output parity:

```powershell
python scripts/build_catalog_html.py --check
python -c "import sys; from pathlib import Path; sys.dont_write_bytecode=True; root=Path.cwd(); sys.path.insert(0, str(root/'scripts')); import build_unified_catalog as u; c=u.load_categories(); u.load_repositories(c); assert u.build_markdown(c)==(root/'docs'/'UNIFIED_CATALOG.md').read_text(encoding='utf-8'); print('markdown parity ok')"
python -m unittest tests.test_catalog_v5_pipeline tests.test_codex_contracts -v
```

Inspect diffs:

```powershell
git diff -- README.md docs data templates categories scripts tests
```

Manual checks:

- Confirm category counts and unique repository counts make sense.
- Confirm `README.md` still describes the product layer and does not contradict generated catalog counts.
- Confirm no secrets, private repository data, credentials, or customer data were added.
- Confirm scores are described as triage signals, not endorsements.
- Confirm lower-confidence source groups are called out when relevant.
- Open `docs/UNIFIED_CATALOG.html` locally and test search, source filters, category navigation, and responsive layout.

## 5. Record The Run

Append to `RUNLOG.md`:

- Update type and snapshot date.
- Source files changed.
- Commands run and observed result.
- Data-quality concerns.
- Any failed commands and how they were handled.
- Residual risks.

## 6. Commit Or Publish

Commit, staging, push and publication require the corresponding explicit user request; commands below are examples, not standing authorization. Before an authorized commit:

```powershell
git -c core.excludesfile= status --short
git diff --stat
```

Use a commit message that names the update type:

```powershell
git add AGENTS.md RUNLOG.md README.md docs data templates categories research scripts tests
git commit -m "docs: add catalog release process"
```

For a catalog refresh, prefer:

```powershell
git commit -m "chore(catalog): refresh catalog snapshot"
```

For an HTML experience change, prefer:

```powershell
git commit -m "feat(catalog): refine interactive catalog"
```

Do not tag or publish a release unless the snapshot date, source artifacts, and verification evidence are recorded in `RUNLOG.md`.

## Local Plugin Release Is Separate

CP-16 owns versioned local package/index/dictionaries, clean installation, fresh-session loading, upgrade and rollback after CP-15 acceptance. This catalog update guide cannot substitute for those checks. Local HTML regeneration is not external publication. Do not add MCP/backend or run every legacy generator merely to release the local plugin.
