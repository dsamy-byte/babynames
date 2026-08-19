"""Focused tests for raw-data validation, profiling, and report generation."""

from __future__ import annotations

import json
from pathlib import Path

from babynames.data_validation import render_markdown, validate_dataset, write_reports


def write_year(directory: Path, year: int, rows: str) -> None:
    """Create a minimal annual fixture using the production filename convention."""
    (directory / f"yob{year}.txt").write_text(rows, encoding="utf-8")


def test_valid_dataset_is_profiled(tmp_path: Path) -> None:
    """A complete valid fixture should produce accurate aggregate statistics."""
    write_year(tmp_path, 2000, "Alice,F,10\nSam,M,7\nSam,F,6\n")
    write_year(tmp_path, 2001, "Alice,F,8\nBob,M,9\n")

    report = validate_dataset(tmp_path, first_year=2000, expected_last_year=2001)

    assert report.valid
    assert report.annual_files == 2
    assert report.rows == 5
    assert report.applications == 40
    assert report.unique_names == 3
    assert report.sex_applications == {"F": 24, "M": 16}
    assert not report.issues


def test_contract_violations_are_reported(tmp_path: Path) -> None:
    """Independent row and coverage violations should all be reported in one run."""
    write_year(
        tmp_path,
        2000,
        "Alice,F,10\nAlice,F,10\nBad-Name,F,6\nChris,X,8\nDana,F,4\nEli,M,nope\n",
    )

    report = validate_dataset(tmp_path, first_year=2000, expected_last_year=2001)
    codes = {issue.code for issue in report.issues}

    assert not report.valid
    assert codes == {
        "count_below_publication_threshold",
        "duplicate_name_sex",
        "invalid_count",
        "invalid_name",
        "invalid_sex",
        "missing_year",
    }
    assert report.rows == 1


def test_invalid_filename_is_reported(tmp_path: Path) -> None:
    """A year-like file with the wrong filename shape should fail validation."""
    (tmp_path / "yob20.txt").write_text("Alice,F,10\n", encoding="utf-8")

    report = validate_dataset(tmp_path, first_year=2000, expected_last_year=2000)

    assert {issue.code for issue in report.issues} == {"invalid_filename", "missing_year"}


def test_missing_directory_is_reported(tmp_path: Path) -> None:
    """A missing source directory should return a report instead of raising an error."""
    report = validate_dataset(tmp_path / "missing", first_year=2000, expected_last_year=2000)

    assert not report.valid
    assert report.issues[0].code == "missing_directory"


def test_reports_are_deterministic_and_serializable(tmp_path: Path) -> None:
    """Repeated report writes should produce identical valid JSON and Markdown."""
    raw_dir = tmp_path / "raw"
    output_dir = tmp_path / "reports"
    raw_dir.mkdir()
    write_year(raw_dir, 2000, "Alice,F,10\n")
    report = validate_dataset(raw_dir, first_year=2000, expected_last_year=2000)

    write_reports(report, output_dir)
    first_json = (output_dir / "data_quality_report.json").read_text(encoding="utf-8")
    first_markdown = (output_dir / "data_quality_report.md").read_text(encoding="utf-8")
    write_reports(report, output_dir)

    assert json.loads(first_json)["valid"] is True
    assert first_json == (output_dir / "data_quality_report.json").read_text(encoding="utf-8")
    assert first_markdown == render_markdown(report)
