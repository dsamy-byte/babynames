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

## Open decisions

- Select a software license before the first public release
- Confirm the detailed v1 feature and visual-design requirements

## Next task

Profile and validate the raw dataset through tested, reusable Python code, then define
the processed-data schema.
