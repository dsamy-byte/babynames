# Project Memory

Last updated: 2026-08-18

## Purpose

Build a polished, maintainable local application for cleaning, analyzing, searching,
comparing, and visualizing U.S. baby-name data.

## Confirmed decisions

- Product name: `babynames`
- Application stack: Python and Streamlit
- Runtime: local execution only for the initial release
- Repository: public GitHub repository owned by `dsamy-byte`
- Repository URL: `https://github.com/dsamy-byte/babynames`
- Default branch: `main`
- Raw SSA source files are committed to the repository
- Work is divided into milestones; completed milestones are tested, documented,
  committed, and pushed
- This file is updated whenever a milestone or material project decision changes
- The complete execution plan and definition of done are maintained in
  `docs/ROADMAP.md`

## Data snapshot

- Location: `data/raw/names/`
- Source: Social Security Administration national baby-name data
- Coverage: 1880-2025 (146 annual text files)
- Supporting document: `NationalReadMe.pdf`
- Total data rows observed during initial profiling: 2,181,032
- Columns in annual files: `name`, `sex`, `count` (no header row)
- No malformed three-column rows were found during initial profiling

## Engineering conventions

- Use a `src` package layout and automated tests
- Keep raw data immutable; write derived files under `data/processed/`
- Never commit credentials, tokens, local secrets, or virtual environments
- Prefer repeatable scripts and commands over manual data changes
- Keep commits focused on one completed task or milestone
- Thoroughly document code with current module, class, and function docstrings;
  explain non-obvious reasoning and constraints with focused comments
- Enforce the baseline documentation standard through Ruff docstring rules
- Before each commit, update this memory when progress, decisions, risks, or the next
  task have changed
- Use `docs/ROADMAP.md` for the stable long-term plan and this file for live project
  state; keep the two consistent

## Milestone history

### Milestone 1 - Repository foundation

Status: completed

Completed:

- Installed Git for Windows and GitHub CLI
- Configured Git author `sammy <dsamyuktha@gmail.com>`
- Authenticated GitHub CLI as `dsamy-byte`
- Created the project structure
- Copied the raw dataset and source documentation
- Added repository documentation, configuration, and memory
- Created and connected the public GitHub repository

### Documentation maintenance

Status: current

Completed:

- Added `docs/ROADMAP.md` with all ten milestones, acceptance-oriented task lists,
  and the commit/push workflow
- Linked the roadmap and project memory from the README
- Made in-code documentation an enforced project standard and documented the
  convention in the roadmap

### Milestone 2 - Data profiling and validation

Status: completed

Completed:

- Added a reusable standard-library validation and profiling module
- Added the `babynames-validate` command with deterministic JSON and Markdown output
- Defined filename, year coverage, encoding, row, name, sex, count, and uniqueness rules
- Documented the raw-data contract and initial processed-data schema
- Added five focused unit tests and one full-snapshot integration test
- Added isolated development dependencies for pytest and Ruff
- Generated and committed the full-snapshot quality reports

Verification:

- Ruff: passed
- Pytest: 6 passed
- Full validation: passed with zero issues
- Validated totals: 146 files, 2,181,032 rows, 375,362,447 recorded applications,
  and 105,966 unique name spellings

### Milestone 3 - Reproducible data pipeline

Status: completed

Completed:

- Added the `babynames-build` command and documented its local workflow
- Added PyArrow as a runtime dependency
- Built a compact Parquet dataset with explicit `int16`, string, string, and `int32`
  columns and Zstandard compression
- Added a canonical sort independent of annual source row order
- Added validation-before-build and atomic replacement of generated artifacts
- Added a deterministic manifest with source and output SHA-256 checksums
- Added three focused unit tests and one full-snapshot build integration test
- Kept generated artifacts under the ignored `data/processed/` boundary

Verification:

- Ruff formatting and linting: passed
- Pytest: 10 passed
- Full build: 2,181,032 rows in a 9,932,481-byte Parquet file
- Full build SHA-256: `a195f6bcb5b02087fe43c1627fc1da62ef8047f146d00bc3a011f753734a4967`
- Repeated-build manifest hashes: identical

### Milestone 4 - Analysis domain layer

Status: completed

Completed:

- Added a UI-independent `BabyNameAnalytics` service over processed Parquet data
- Added competition rankings and within-year/category popularity shares
- Added case-insensitive name histories, lifetime summaries, and multi-name comparison
- Added rising and falling endpoint analysis without treating suppressed rows as zero
- Added annual unisex-name counts, category share, and balance score
- Added clear public input errors and processed-data contract checks
- Documented every analytical definition and source-data limitation in
  `docs/METRICS.md`
- Added eleven focused analytics cases and one full-snapshot integration test

Verification:

- Ruff formatting, linting, and docstring rules: passed
- Pytest: 22 passed across the complete project
- Full analytics integration: confirmed 1880-2025 coverage, Olivia and Liam as the
  2025 category leaders, and 5,250,638 published male applications for James

### Milestone 5 - Application foundation

Status: completed

Completed:

- Added Streamlit 1.61 as a bounded runtime dependency
- Added a documented local application entry point and themed Streamlit configuration
- Added stable navigation paths for overview, name search, comparison, trends, and
  data provenance
- Added processed-artifact startup checks for missing, malformed, unsafe, partial, or
  mismatched local files
- Added cached analytics loading keyed by Parquet path, modification time, and size
- Added user-safe build guidance and developer logging for startup failures
- Added a working overview with latest-year category rankings and dataset metrics
- Added documented shells for the Milestone 6 user workflows
- Added `BABYNAMES_PROCESSED_DIR` for tests and advanced local layouts
- Documented runtime flow and module boundaries in `docs/APP_ARCHITECTURE.md`

Verification:

- Ruff formatting, linting, and docstring rules: passed
- Pytest: 29 passed across the complete project
- Streamlit smoke tests: missing-data recovery and ready-data overview both passed

### Milestone 6 - Core user experience

Status: completed

Completed:

- Expanded the overview with a long-term published-application chart and selectable
  annual category rankings
- Added case-insensitive name discovery with category selection, summary cards,
  applications/rank/share charts, suppression guidance, and source observations
- Added comparison for two to five names with selectable metrics and lifetime summary
  tables
- Added configurable rising/falling endpoint analysis with explicit eligibility and
  rank-change definitions
- Added annual unisex-name discovery with category counts, female-category share, and
  balance score
- Added shared documented Altair chart builders with explicit axes and tooltips
- Added safe single-year controls for valid partial datasets
- Added direct analytics helpers for available names, categories, and annual totals
- Added `docs/USER_GUIDE.md` with local operation and interpretation guidance
- Added direct smoke coverage for every callable application page

Verification:

- Ruff formatting, linting, and docstring rules: passed
- Pytest: 34 passed across the complete project
- Chart contract tests: axis titles, rank direction, tooltips, and series encoding passed
- Streamlit tests: missing-data, ready overview, name search, comparison, trends, and
  about render paths passed

### Milestone 7 - Engineering automation

Status: completed

Completed:

- Added `python scripts/check.py` as the documented cross-platform local quality gate
- Added strict mypy checks for source, test, and script modules
- Resolved pandas and Streamlit type ambiguities and narrowly documented incomplete
  PyArrow stub boundaries
- Added branch-aware pytest coverage with an enforced 80% project threshold
- Added environment-driven centralized logging with safe invalid-level fallback
- Added GitHub Actions for Python 3.11 and 3.14 on pushes and pull requests
- Added an independent dependency vulnerability audit job
- Added weekly Dependabot checks for Python and GitHub Actions dependencies
- Added CI coverage artifact upload and a README status badge
- Added `docs/TROUBLESHOOTING.md` for quality commands, startup, logging, and audit
  failures

Verification:

- Unified local quality gate: passed
- Ruff formatting, linting, and docstring rules: passed
- Mypy strict mode: no issues in 23 checked source files
- Pytest: 36 passed
- Branch-aware coverage: 82.83% (80% required)
- Live pip-audit: no known vulnerabilities; local unpublished package skipped as expected
- Remote GitHub Actions executions: all Python 3.11, Python 3.14, and dependency audit
  jobs passed; Node 20 deprecation annotations on artifact-action v4 and v5 led to the
  Node 24-compatible v6 upgrade

### Milestone 8 - Visual polish and accessibility

Status: completed

Completed:

- Established shared Streamlit and Altair tokens for color, typography, borders,
  radii, axes, legends, and chart titles
- Added automated WCAG contrast helpers and tests; primary-on-surface is 6.27:1 and
  text-on-surface is 16.54:1
- Added color-vision-deficiency-friendly chart palettes, programmatic descriptions,
  and dash patterns so series do not rely on color alone
- Refined every page with clear introductions, bordered control and result groups,
  responsive native layouts, and bounded large tables
- Precomputed frequently reused name, category, and annual-total lookups in the cached
  analytics service while preserving immutable/copy-returning public boundaries
- Added a documented Playwright screenshot command that uses installed Chrome or Edge
  without downloading a browser
- Added `docs/ACCESSIBILITY.md` and refreshed the architecture, usage, roadmap, and
  README presentation documentation

Verification:

- Unified local quality gate: passed
- Ruff formatting, linting, and docstring rules: passed across 36 files
- Mypy strict mode: no issues in 26 checked source files
- Pytest: 39 passed
- Branch-aware coverage: 83.48% (80% required)
- Live pip-audit: no known vulnerabilities; local unpublished package skipped as expected
- Browser capture: fully rendered 1440 x 1100 RGB overview screenshot inspected

## Current state

- Active milestone: Milestone 9 - Release readiness
- Last completed milestone: Milestone 8 - Visual polish and accessibility
- Latest quality result: PASS with zero issues

## Open decisions

- Select a software license before the first public release
- Select the exact `v1.0.0` release notes and known-limitations wording

## Next task

Run release-readiness validation from a clean environment, verify supported setup,
resolve or document remaining limitations, select a license, prepare release notes,
and tag version `v1.0.0` only after explicit approval.
