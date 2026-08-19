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

## Current state

- Active milestone: Milestone 4 - Analysis domain layer
- Last completed milestone: Milestone 3 - Reproducible data pipeline
- Latest quality result: PASS with zero issues

## Open decisions

- Select a software license before the first public release
- Confirm the detailed v1 feature and visual-design requirements

## Next task

Define the analytical metric contracts, then implement and test popularity rankings,
name histories, comparisons, trends, and unisex-name analysis independently of the
Streamlit interface.
