# Changelog

All notable project changes are documented here. The format follows Keep a Changelog,
and the project uses semantic versioning for release tags.

## [Unreleased]

### Added

- Reproducible validation and Parquet build commands for 146 SSA annual files spanning
  1880 through 2025
- Tested analytics for rankings, name histories, comparisons, movers, and unisex names
- A polished five-page local Streamlit application with searchable and interactive
  views
- Accessible chart descriptions, non-color series encodings, keyboard-operable native
  controls, and automated contrast checks
- Strict formatting, linting, typing, branch coverage, dependency audit, Dependabot,
  and Python 3.11/3.14 GitHub Actions checks
- Architecture, metric, data-contract, accessibility, troubleshooting, usage, and
  release-readiness documentation

### Known limitations

- The first release supports local Windows operation with national aggregate data.
- SSA suppression means absent observations cannot be treated as zero.
- Manual screen-reader and 200% zoom acceptance checks remain before `v1.0.0`.

### Fixed

- Share columns now display concise percentages instead of long fractional decimals.

[Unreleased]: https://github.com/dsamy-byte/babynames/compare/main...HEAD
