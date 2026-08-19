# Project Roadmap

This roadmap is the durable execution plan for Baby Names. Work proceeds one task at
a time. Scope changes and completed work must also be recorded in
`PROJECT_MEMORY.md`.

## Delivery workflow

For every task:

1. Confirm its goal and acceptance criteria.
2. Implement the smallest coherent change.
3. Run checks appropriate to the change.
4. Update documentation and `PROJECT_MEMORY.md`.
5. Review the Git diff for accidental changes or secrets.
6. Create a focused commit with a descriptive message.
7. Push the commit to `main` and confirm the working tree is clean.

All code must include useful in-code documentation. Modules, classes, and functions
receive docstrings that explain purpose and contracts; comments capture non-obvious
reasoning and constraints. Documentation must stay current when behavior changes.
Automated linting enforces the baseline docstring standard.

A milestone is complete only when its acceptance criteria pass, its documentation is
current, and its commits have been pushed.

## Milestone 1 - Repository foundation

Status: complete

- Create a dedicated project directory and Git repository.
- Configure the public `dsamy-byte/babynames` GitHub repository.
- Establish the `src`, `tests`, `scripts`, `docs`, and `data` layout.
- Copy and preserve the original SSA national-name files.
- Add README, project configuration, ignore rules, and project memory.

## Milestone 2 - Data profiling and validation

Status: complete

- Convert exploratory profiling into reusable Python modules and commands.
- Define the raw-file contract: filename, year, encoding, columns, and value rules.
- Validate file coverage, row shape, names, sex values, and positive integer counts.
- Detect duplicate name/sex pairs within each year.
- Produce a deterministic machine-readable and human-readable quality report.
- Add unit tests using small fixtures plus an integration check against the full data.
- Document the validated source limitations and processed-data schema.

## Milestone 3 - Reproducible data pipeline

Status: complete

- Load all valid annual files and derive the year from each filename.
- Normalize column names and data types without modifying raw files.
- Generate an optimized combined dataset under `data/processed/`.
- Add metadata so generated data can be traced to its raw inputs.
- Make builds deterministic and provide a single documented build command.
- Test error handling, idempotency, and important transformations.

## Milestone 4 - Analysis domain layer

Status: next

- Implement popularity and rank by year and sex.
- Implement individual-name history and multi-name comparison.
- Calculate rank changes, peaks, long-term trends, and rising or declining names.
- Define and implement unisex-name analysis.
- Keep analytical logic independent from Streamlit and cover it with unit tests.
- Document definitions so displayed metrics cannot be misinterpreted.

## Milestone 5 - Application foundation

Status: planned

- Add pinned runtime and development dependencies.
- Establish Streamlit entry points, page structure, navigation, configuration, and theme.
- Add a shared data-access layer with caching.
- Provide helpful startup, empty-state, and error behavior.
- Document local installation and run commands.

## Milestone 6 - Core user experience

Status: planned

- Build an overview dashboard with key dataset facts and trends.
- Build name search with suggestions and a complete historical profile.
- Build side-by-side name comparison.
- Build trend discovery with filters, rankings, and tables.
- Add clear chart titles, definitions, sources, and accessible interactions.
- Test critical application flows.

## Milestone 7 - Engineering automation

Status: planned

- Configure formatting, linting, type checking, and test coverage.
- Add GitHub Actions checks for every push and pull request.
- Add dependency and basic security checks.
- Standardize logging and user-safe error reporting.
- Document developer commands and troubleshooting.

## Milestone 8 - Visual polish and accessibility

Status: planned

- Establish a coherent visual system for color, type, spacing, and charts.
- Improve responsive behavior for common desktop and mobile widths.
- Verify keyboard usability, contrast, labels, and non-color indicators.
- Optimize loading, caching, rendering, and large-table behavior.
- Add screenshots and a concise usage guide.

## Milestone 9 - Release readiness

Status: planned

- Run the full test and data-validation suites from a clean environment.
- Verify documented setup on the supported Python version.
- Resolve or explicitly document remaining limitations and technical debt.
- Select and add a software license.
- Prepare release notes and tag version `v1.0.0`.

## Milestone 10 - Maintenance

Status: planned

- Document how to import a new annual SSA data file.
- Rebuild and validate processed data when the source changes.
- Track enhancements and defects without silently changing metric definitions.
- Keep dependencies, tests, roadmap, README, and project memory current.
