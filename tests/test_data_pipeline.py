"""Tests for deterministic and failure-safe processed-data builds."""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from babynames.data_pipeline import DataBuildError, build_dataset


def write_year(directory: Path, year: int, rows: str) -> None:
    """Create a compact annual source fixture for pipeline tests."""
    (directory / f"yob{year}.txt").write_text(rows, encoding="utf-8")


def test_build_writes_canonical_parquet_and_manifest(tmp_path: Path) -> None:
    """A valid snapshot should produce typed, sorted, and traceable artifacts."""
    raw_dir = tmp_path / "raw"
    output_dir = tmp_path / "processed"
    raw_dir.mkdir()
    write_year(raw_dir, 2000, "Zoe,F,7\nAmy,F,10\nBob,M,8\n")
    write_year(raw_dir, 2001, "Amy,F,6\nBob,M,9\n")

    manifest = build_dataset(raw_dir, output_dir, first_year=2000, expected_last_year=2001)
    table = pq.read_table(output_dir / "baby_names.parquet")
    stored_manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))

    assert table.to_pydict() == {
        "year": [2000, 2000, 2000, 2001, 2001],
        "name": ["Amy", "Zoe", "Bob", "Amy", "Bob"],
        "sex": ["F", "F", "M", "F", "M"],
        "count": [10, 7, 8, 6, 9],
    }
    assert manifest.rows == 5
    assert manifest.applications == 40
    assert stored_manifest["parquet_sha256"] == manifest.parquet_sha256
    assert [source["file"] for source in stored_manifest["sources"]] == [
        "yob2000.txt",
        "yob2001.txt",
    ]


def test_repeated_build_is_deterministic(tmp_path: Path) -> None:
    """Unchanged inputs should yield identical Parquet content and manifest JSON."""
    raw_dir = tmp_path / "raw"
    output_dir = tmp_path / "processed"
    raw_dir.mkdir()
    write_year(raw_dir, 2000, "Amy,F,10\nBob,M,8\n")

    first = build_dataset(raw_dir, output_dir, first_year=2000, expected_last_year=2000)
    first_manifest = (output_dir / "manifest.json").read_bytes()
    second = build_dataset(raw_dir, output_dir, first_year=2000, expected_last_year=2000)

    assert second.parquet_sha256 == first.parquet_sha256
    assert (output_dir / "manifest.json").read_bytes() == first_manifest


def test_invalid_source_does_not_create_artifacts(tmp_path: Path) -> None:
    """Validation failure should stop before any processed artifact is written."""
    raw_dir = tmp_path / "raw"
    output_dir = tmp_path / "processed"
    raw_dir.mkdir()
    write_year(raw_dir, 2000, "Amy,F,not-a-number\n")

    with pytest.raises(DataBuildError, match="invalid_count"):
        build_dataset(raw_dir, output_dir, first_year=2000, expected_last_year=2000)

    assert not output_dir.exists()
