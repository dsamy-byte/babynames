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

## Current state

- Active milestone: Milestone 3 - Reproducible data pipeline
- Last completed milestone: Milestone 2 - Data profiling and validation
- Latest quality result: PASS with zero issues

## Open decisions

- Select a software license before the first public release
- Confirm the detailed v1 feature and visual-design requirements

## Next task

Design and implement the reproducible data pipeline that converts validated annual
files into an optimized combined dataset without modifying the raw source files.
