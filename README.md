# Baby Names

Baby Names is a polished local Streamlit application for exploring United States
baby-name trends in Social Security Administration national data from 1880 onward.

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

Run the automated checks:

```powershell
python -m ruff check .
python -m pytest
```

The raw-data rules and processed-data schema are documented in
[`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md). The latest validation results are
available in [`reports/data_quality_report.md`](reports/data_quality_report.md).
Ranking, share, trend, comparison, summary, and unisex definitions are documented in
[`docs/METRICS.md`](docs/METRICS.md).

## License

No license has been selected yet. Until one is added, all rights are reserved.
