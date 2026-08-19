"""Inspect generated dataset artifacts before the application attempts to load them."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from babynames.data_pipeline import DATASET_FILENAME, MANIFEST_FILENAME


@dataclass(frozen=True)
class ArtifactStatus:
    """Describe whether generated artifacts are safe to hand to the analytics layer."""

    ready: bool
    message: str
    dataset_path: Path
    manifest_path: Path
    manifest: dict[str, Any] | None = None


def inspect_processed_artifacts(processed_dir: Path) -> ArtifactStatus:
    """Check existence and inexpensive manifest invariants for processed artifacts.

    Full checksums are created and tested by the pipeline. Application startup checks
    filenames and sizes to catch missing, partial, or mismatched local artifacts
    without hashing the Parquet file during every Streamlit rerun.
    """
    default_dataset = processed_dir / DATASET_FILENAME
    manifest_path = processed_dir / MANIFEST_FILENAME
    if not manifest_path.is_file():
        return ArtifactStatus(
            ready=False,
            message="The processed-data manifest is missing.",
            dataset_path=default_dataset,
            manifest_path=manifest_path,
        )

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return ArtifactStatus(
            ready=False,
            message=f"The processed-data manifest cannot be read: {error}",
            dataset_path=default_dataset,
            manifest_path=manifest_path,
        )
    if not isinstance(manifest, dict):
        return ArtifactStatus(
            ready=False,
            message="The processed-data manifest must contain a JSON object.",
            dataset_path=default_dataset,
            manifest_path=manifest_path,
        )

    parquet_file = manifest.get("parquet_file")
    if not isinstance(parquet_file, str) or Path(parquet_file).name != parquet_file:
        return ArtifactStatus(
            ready=False,
            message="The manifest contains an invalid Parquet filename.",
            dataset_path=default_dataset,
            manifest_path=manifest_path,
            manifest=manifest,
        )
    dataset_path = processed_dir / parquet_file
    if not dataset_path.is_file():
        return ArtifactStatus(
            ready=False,
            message="The processed Parquet dataset is missing.",
            dataset_path=dataset_path,
            manifest_path=manifest_path,
            manifest=manifest,
        )

    expected_bytes = manifest.get("parquet_bytes")
    if not isinstance(expected_bytes, int) or expected_bytes <= 0:
        return ArtifactStatus(
            ready=False,
            message="The manifest contains an invalid Parquet size.",
            dataset_path=dataset_path,
            manifest_path=manifest_path,
            manifest=manifest,
        )
    if dataset_path.stat().st_size != expected_bytes:
        return ArtifactStatus(
            ready=False,
            message="The Parquet size does not match the build manifest.",
            dataset_path=dataset_path,
            manifest_path=manifest_path,
            manifest=manifest,
        )
    return ArtifactStatus(
        ready=True,
        message="Processed data is ready.",
        dataset_path=dataset_path,
        manifest_path=manifest_path,
        manifest=manifest,
    )
