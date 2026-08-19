"""Integration coverage for building the entire committed source snapshot."""

from pathlib import Path

import pyarrow.parquet as pq

from babynames.data_pipeline import build_dataset


def test_full_snapshot_builds_with_expected_metadata(tmp_path: Path) -> None:
    """Build all years and verify row counts, schema, metadata, and source coverage."""
    project_root = Path(__file__).resolve().parents[1]

    manifest = build_dataset(project_root / "data" / "raw" / "names", tmp_path)
    parquet_file = pq.ParquetFile(tmp_path / manifest.parquet_file)

    assert manifest.rows == 2_181_032
    assert manifest.applications == 375_362_447
    assert manifest.annual_files == 146
    assert len(manifest.sources) == 146
    assert parquet_file.metadata.num_rows == manifest.rows
    assert parquet_file.schema_arrow.names == ["year", "name", "sex", "count"]
