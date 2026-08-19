# Baby Names

Baby Names is a polished local Streamlit application for exploring United States
baby-name trends in Social Security Administration national data from 1880 onward.

## Project status

The repository foundation and raw source dataset are in place. Data processing,
analysis, and application features will be implemented in subsequent milestones.

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

The application targets Python 3.11 or newer. Setup and run commands will be added
when the first executable application milestone is implemented.

## License

No license has been selected yet. Until one is added, all rights are reserved.
