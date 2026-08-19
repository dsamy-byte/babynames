# Baby Names

[![Quality](https://github.com/dsamy-byte/babynames/actions/workflows/quality.yml/badge.svg)](https://github.com/dsamy-byte/babynames/actions/workflows/quality.yml)

Baby Names is a polished local Streamlit application for exploring United States
baby-name trends in Social Security Administration national data from 1880 onward.

The application includes yearly rankings, long-term volume, searchable name profiles,
multi-name comparisons, rising and falling names, and annual unisex-name analysis.

## Project status

The repository foundation and raw source dataset are in place. Data processing,
analysis, and application features will be implemented in subsequent milestones.

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full milestone plan and completion
criteria. See [`PROJECT_MEMORY.md`](PROJECT_MEMORY.md) for current decisions, completed
work, and the exact next task.

## Repository layout

```text
babynames/
|-- data/
|   |-- raw/names/       # Original annual SSA files and documentation
|   `-- processed/       # Reproducible generated data (not committed)
|-- docs/                # Design and project documentation
|-- scripts/             # Repeatable project commands
|-- src/babynames/       # Application package
|-- tests/               # Automated tests
|-- PROJECT_MEMORY.md    # Current decisions, progress, and next task
`-- pyproject.toml       # Python project and tool configuration
```

## Data

The raw data is the Social Security Administration's national baby-name dataset.
Each `yobYYYY.txt` file contains comma-separated `name`, `sex`, and `count` values.
The included `NationalReadMe.pdf` provides the source documentation.

The current snapshot contains 146 annual files covering 1880 through 2025.

## Development

The application targets Python 3.11 or newer. From PowerShell, create an isolated
environment and install the project with its development tools:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Validate and profile the complete raw dataset:

```powershell
babynames-validate
```

Build the validated, combined Parquet dataset and checksum manifest:

```powershell
babynames-build
```

Generated artifacts are written to `data/processed/`. They are intentionally ignored
by Git because the command reproduces them from the committed raw files.

Launch the local application:

```powershell
streamlit run src/babynames/app.py
```

Streamlit prints the local URL and opens it in your default browser. If generated
data is missing or inconsistent, the application displays the validation and build
commands needed to recover safely.

Run the automated checks:

```powershell
python scripts/check.py
```

This single gate checks formatting, lint and docstring rules, strict static types,
all tests, branch coverage, and the 80% coverage threshold. Add `--audit` to query
current dependency vulnerability information. See
[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for individual commands and
common local issues.

The raw-data rules and processed-data schema are documented in
[`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md). The latest validation results are
available in [`reports/data_quality_report.md`](reports/data_quality_report.md).
Ranking, share, trend, comparison, summary, and unisex definitions are documented in
[`docs/METRICS.md`](docs/METRICS.md).
The Streamlit startup flow, module boundaries, cache behavior, navigation, and local
configuration are documented in
[`docs/APP_ARCHITECTURE.md`](docs/APP_ARCHITECTURE.md).
Page-by-page usage and interpretation guidance are available in
[`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).

## License

No license has been selected yet. Until one is added, all rights are reserved.
