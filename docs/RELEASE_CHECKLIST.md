# Release Checklist

This checklist records reproducible evidence for the first local release. A release
is not complete until every required item is checked, the version is committed, and
the signed-off commit is tagged.

## Verified on 2026-08-18

- [x] Fresh local clone created from commit `e0d6bd1`
- [x] Fresh Python 3.14.6 virtual environment created
- [x] Documented `pip install -e ".[dev]"` setup completed successfully
- [x] All 146 raw files validated with zero issues
- [x] Processed data rebuilt with 2,181,032 rows
- [x] Rebuilt Parquet SHA-256 matched
  `a195f6bcb5b02087fe43c1627fc1da62ef8047f146d00bc3a011f753734a4967`
- [x] Formatting, linting, strict typing, tests, and coverage gate passed
- [x] 39 tests passed with 83.48% branch coverage
- [x] Dependency audit reported no known vulnerabilities
- [x] GitHub Actions passed on supported Python 3.11 and Python 3.14
- [x] Repository tracking audit found no generated data or obvious secret files

## Required before `v1.0.0`

- [x] Select and add the MIT License
- [ ] Update package version from `0.1.0` to `1.0.0`
- [ ] Finalize the release notes and known-limitations wording
- [ ] Run the complete quality gate after release metadata changes
- [ ] Confirm GitHub Actions passes on the release commit
- [ ] Obtain explicit approval to create and push the `v1.0.0` tag

## Known limitations

- The application runs locally; hosting, authentication, and multi-user operation are
  outside the first-release scope.
- The included snapshot ends in 2025 and must be rebuilt when SSA publishes another
  annual file.
- Source counts below five are suppressed. Missing rows therefore represent unknown
  values rather than zero.
- Source categories `F` and `M` reflect the historical SSA data contract and are not a
  complete model of gender identity.
- The application presents national aggregates and does not include state-level data.
- Automated accessibility checks supplement, but do not replace, manual keyboard,
  200% zoom, and screen-reader verification on a release workstation.
- Windows is the verified local workstation environment. CI exercises Python 3.11
  and 3.14 on Windows; other operating systems are not yet part of the support claim.
