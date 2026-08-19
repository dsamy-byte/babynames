"""Tests for processed-artifact startup health checks."""

from __future__ import annotations

import json
from pathlib import Path

from babynames.artifacts import inspect_processed_artifacts


def write_manifest(directory: Path, **overrides: object) -> None:
    """Write the smallest valid manifest, optionally replacing selected fields."""
    manifest: dict[str, object] = {
        "parquet_file": "baby_names.parquet",
        "parquet_bytes": 4,
    }
    manifest.update(overrides)
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_missing_manifest_has_actionable_status(tmp_path: Path) -> None:
    """A fresh checkout should report the missing generated manifest cleanly."""
    status = inspect_processed_artifacts(tmp_path)

    assert not status.ready
    assert "manifest is missing" in status.message


def test_invalid_manifest_is_rejected(tmp_path: Path) -> None:
    """Malformed JSON must not reach the analytics loader."""
    (tmp_path / "manifest.json").write_text("not-json", encoding="utf-8")

    status = inspect_processed_artifacts(tmp_path)

    assert not status.ready
    assert "cannot be read" in status.message


def test_missing_or_wrong_size_parquet_is_rejected(tmp_path: Path) -> None:
    """Manifest and Parquet presence and size must agree before loading."""
    write_manifest(tmp_path)
    missing = inspect_processed_artifacts(tmp_path)
    (tmp_path / "baby_names.parquet").write_bytes(b"wrong")
    wrong_size = inspect_processed_artifacts(tmp_path)

    assert "dataset is missing" in missing.message
    assert "size does not match" in wrong_size.message


def test_matching_artifacts_are_ready(tmp_path: Path) -> None:
    """A matching filename and byte size should pass the inexpensive startup check."""
    (tmp_path / "baby_names.parquet").write_bytes(b"data")
    write_manifest(tmp_path)

    status = inspect_processed_artifacts(tmp_path)

    assert status.ready
    assert status.manifest is not None
    assert status.dataset_path.name == "baby_names.parquet"


def test_manifest_filename_cannot_escape_processed_directory(tmp_path: Path) -> None:
    """Reject absolute and nested filenames supplied by a damaged manifest."""
    write_manifest(tmp_path, parquet_file="../outside.parquet")

    status = inspect_processed_artifacts(tmp_path)

    assert not status.ready
    assert "invalid Parquet filename" in status.message
