"""Validation and profiling for the raw SSA national baby-name files."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

FIRST_YEAR = 1880
SNAPSHOT_LAST_YEAR = 2025
FILE_PATTERN = re.compile(r"yob(?P<year>\d{4})\.txt")
NAME_PATTERN = re.compile(r"[A-Za-z]+")
ALLOWED_SEX_VALUES = frozenset({"F", "M"})
MIN_PUBLISHED_COUNT = 5


@dataclass(frozen=True)
class ValidationIssue:
    """One violation of the raw-data contract."""

    code: str
    message: str
    file: str | None = None
    row: int | None = None


@dataclass(frozen=True)
class YearProfile:
    """Validated summary statistics for one annual file."""

    year: int
    file: str
    rows: int
    applications: int
    female_applications: int
    male_applications: int
    unique_names: int
    minimum_count: int | None
    maximum_count: int | None


@dataclass(frozen=True)
class DatasetReport:
    """Complete deterministic validation result for a dataset snapshot."""

    valid: bool
    first_year: int | None
    last_year: int | None
    annual_files: int
    rows: int
    applications: int
    unique_names: int
    sex_applications: dict[str, int]
    issues: tuple[ValidationIssue, ...]
    years: tuple[YearProfile, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


def _issue(
    issues: list[ValidationIssue],
    code: str,
    message: str,
    path: Path | None = None,
    row: int | None = None,
) -> None:
    issues.append(
        ValidationIssue(code=code, message=message, file=path.name if path else None, row=row)
    )


def _validate_file(path: Path, year: int, issues: list[ValidationIssue]) -> YearProfile:
    rows = applications = female = male = 0
    minimum: int | None = None
    maximum: int | None = None
    names: set[str] = set()
    keys: set[tuple[str, str]] = set()

    try:
        stream = path.open(encoding="utf-8-sig", newline="")
    except (OSError, UnicodeError) as error:
        _issue(issues, "unreadable_file", str(error), path)
        return YearProfile(year, path.name, 0, 0, 0, 0, 0, None, None)

    with stream:
        try:
            for row_number, values in enumerate(csv.reader(stream), start=1):
                if len(values) != 3:
                    _issue(
                        issues,
                        "invalid_column_count",
                        f"Expected 3 columns, found {len(values)}.",
                        path,
                        row_number,
                    )
                    continue

                name, sex, count_text = values
                row_is_valid = True
                if not NAME_PATTERN.fullmatch(name):
                    _issue(
                        issues,
                        "invalid_name",
                        "Name must contain ASCII letters only.",
                        path,
                        row_number,
                    )
                    row_is_valid = False
                if sex not in ALLOWED_SEX_VALUES:
                    _issue(
                        issues,
                        "invalid_sex",
                        f"Sex must be one of {sorted(ALLOWED_SEX_VALUES)}.",
                        path,
                        row_number,
                    )
                    row_is_valid = False
                try:
                    count = int(count_text)
                except ValueError:
                    _issue(
                        issues,
                        "invalid_count",
                        "Count must be an integer.",
                        path,
                        row_number,
                    )
                    row_is_valid = False
                    count = 0
                else:
                    if count < MIN_PUBLISHED_COUNT:
                        _issue(
                            issues,
                            "count_below_publication_threshold",
                            f"Count must be at least {MIN_PUBLISHED_COUNT}.",
                            path,
                            row_number,
                        )
                        row_is_valid = False

                if not row_is_valid:
                    continue

                key = (name, sex)
                if key in keys:
                    _issue(
                        issues,
                        "duplicate_name_sex",
                        f"Duplicate name/sex pair: {name}/{sex}.",
                        path,
                        row_number,
                    )
                    continue

                keys.add(key)
                names.add(name)
                rows += 1
                applications += count
                female += count if sex == "F" else 0
                male += count if sex == "M" else 0
                minimum = count if minimum is None else min(minimum, count)
                maximum = count if maximum is None else max(maximum, count)
        except UnicodeError as error:
            _issue(issues, "invalid_encoding", str(error), path)

    if rows == 0:
        _issue(issues, "empty_file", "Annual file has no valid rows.", path)

    return YearProfile(
        year=year,
        file=path.name,
        rows=rows,
        applications=applications,
        female_applications=female,
        male_applications=male,
        unique_names=len(names),
        minimum_count=minimum,
        maximum_count=maximum,
    )


def validate_dataset(
    raw_dir: Path,
    *,
    first_year: int = FIRST_YEAR,
    expected_last_year: int = SNAPSHOT_LAST_YEAR,
) -> DatasetReport:
    """Validate all annual files in *raw_dir* and return their profile."""
    issues: list[ValidationIssue] = []
    if not raw_dir.is_dir():
        _issue(issues, "missing_directory", f"Raw-data directory does not exist: {raw_dir}")
        return DatasetReport(False, None, None, 0, 0, 0, 0, {"F": 0, "M": 0}, tuple(issues), ())

    annual_paths: dict[int, Path] = {}
    for path in sorted(raw_dir.glob("yob*.txt")):
        match = FILE_PATTERN.fullmatch(path.name)
        if not match:
            _issue(issues, "invalid_filename", "Expected filename yobYYYY.txt.", path)
            continue
        year = int(match.group("year"))
        if year in annual_paths:
            _issue(issues, "duplicate_year", f"Multiple files represent {year}.", path)
            continue
        annual_paths[year] = path

    expected_years = set(range(first_year, expected_last_year + 1))
    actual_years = set(annual_paths)
    for year in sorted(expected_years - actual_years):
        _issue(issues, "missing_year", f"Missing annual file for {year}.")
    for year in sorted(actual_years - expected_years):
        _issue(issues, "unexpected_year", f"Annual file year {year} is outside the snapshot.")

    profiles = tuple(
        _validate_file(annual_paths[year], year, issues) for year in sorted(annual_paths)
    )
    all_names: set[str] = set()
    for path in annual_paths.values():
        try:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                all_names.update(row[0] for row in csv.reader(stream) if len(row) == 3)
        except (OSError, UnicodeError):
            pass

    female = sum(profile.female_applications for profile in profiles)
    male = sum(profile.male_applications for profile in profiles)
    ordered_issues = tuple(
        sorted(issues, key=lambda item: (item.file or "", item.row or 0, item.code, item.message))
    )
    return DatasetReport(
        valid=not ordered_issues,
        first_year=min(actual_years) if actual_years else None,
        last_year=max(actual_years) if actual_years else None,
        annual_files=len(profiles),
        rows=sum(profile.rows for profile in profiles),
        applications=sum(profile.applications for profile in profiles),
        unique_names=len(all_names),
        sex_applications={"F": female, "M": male},
        issues=ordered_issues,
        years=profiles,
    )


def render_markdown(report: DatasetReport) -> str:
    """Render a concise human-readable quality report."""
    status = "PASS" if report.valid else "FAIL"
    lines = [
        "# Raw Data Quality Report",
        "",
        f"- Status: **{status}**",
        f"- Coverage: {report.first_year}-{report.last_year}",
        f"- Annual files: {report.annual_files:,}",
        f"- Rows: {report.rows:,}",
        f"- Recorded applications: {report.applications:,}",
        f"- Unique name spellings: {report.unique_names:,}",
        f"- Female applications: {report.sex_applications['F']:,}",
        f"- Male applications: {report.sex_applications['M']:,}",
        f"- Validation issues: {len(report.issues):,}",
        "",
        "## Contract checks",
        "",
        "Annual filenames, year coverage, UTF-8-compatible text, three-column rows,",
        "name characters, sex codes, publication-threshold counts, and duplicate",
        "name/sex pairs were checked.",
    ]
    if report.issues:
        lines.extend(["", "## Issues", ""])
        lines.extend(
            f"- `{issue.code}` {issue.file or ''}:{issue.row or ''} {issue.message}".rstrip()
            for issue in report.issues
        )
    return "\n".join(lines) + "\n"


def write_reports(report: DatasetReport, output_dir: Path) -> None:
    """Write deterministic JSON and Markdown reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "data_quality_report.json").write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "data_quality_report.md").write_text(render_markdown(report), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """Run validation from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/names"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--expected-last-year", type=int, default=SNAPSHOT_LAST_YEAR)
    arguments = parser.parse_args(argv)

    report = validate_dataset(
        arguments.raw_dir,
        expected_last_year=arguments.expected_last_year,
    )
    write_reports(report, arguments.output_dir)
    print(render_markdown(report), end="")
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
