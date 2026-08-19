"""Build the normalized Baby Names dataset from validated annual source files.

The pipeline deliberately separates immutable raw inputs from generated artifacts.
It validates the complete snapshot before reading it, applies an explicit compact
schema, writes Parquet atomically, and records checksums needed to trace every build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq

from babynames.data_validation import FIRST_YEAR, SNAPSHOT_LAST_YEAR, validate_dataset

PIPELINE_VERSION = 1
DATASET_FILENAME = "baby_names.parquet"
MANIFEST_FILENAME = "manifest.json"
PARQUET_COMPRESSION = "zstd"
PROCESSED_SCHEMA = pa.schema(
    [
        pa.field("year", pa.int16(), nullable=False),
        pa.field("name", pa.string(), nullable=False),
        pa.field("sex", pa.string(), nullable=False),
        pa.field("count", pa.int32(), nullable=False),
    ]
)


class DataBuildError(RuntimeError):
    """Indicate that source data could not safely produce a processed dataset."""


@dataclass(frozen=True)
class SourceFingerprint:
    """Identify one source file by stable content rather than modification time."""

    file: str
    sha256: str
    bytes: int


@dataclass(frozen=True)
class BuildManifest:
    """Describe the inputs, output, schema, and aggregate facts for one build."""

    pipeline_version: int
    first_year: int
    last_year: int
    annual_files: int
    rows: int
    applications: int
    unique_names: int
    schema: dict[str, str]
    sort_order: tuple[str, ...]
    parquet_compression: str
    parquet_file: str
    parquet_sha256: str
    parquet_bytes: int
    sources: tuple[SourceFingerprint, ...]

    def to_dict(self) -> dict[str, object]:
        """Return the manifest in a JSON-serializable form."""
        return asdict(self)


def sha256_file(path: Path, *, block_size: int = 1024 * 1024) -> str:
    """Return a file's SHA-256 digest without loading the entire file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(block_size):
            digest.update(block)
    return digest.hexdigest()


def _read_annual_file(path: Path, year: int) -> pa.Table:
    """Read one prevalidated annual CSV file into the processed schema."""
    source = pacsv.read_csv(
        path,
        read_options=pacsv.ReadOptions(column_names=["name", "sex", "count"]),
        parse_options=pacsv.ParseOptions(delimiter=","),
        convert_options=pacsv.ConvertOptions(
            column_types={"name": pa.string(), "sex": pa.string(), "count": pa.int32()}
        ),
    )
    year_column = pa.array([year] * source.num_rows, type=pa.int16())
    return pa.table(
        {
            "year": year_column,
            "name": source["name"],
            "sex": source["sex"],
            "count": source["count"],
        },
        schema=PROCESSED_SCHEMA,
    )


def _canonicalize(tables: list[pa.Table]) -> pa.Table:
    """Combine annual tables and impose a stable order independent of source order."""
    combined = pa.concat_tables(tables)
    order = pc.sort_indices(
        combined,
        sort_keys=[
            ("year", "ascending"),
            ("sex", "ascending"),
            ("count", "descending"),
            ("name", "ascending"),
        ],
    )
    return pc.take(combined, order)


def _write_parquet_atomically(table: pa.Table, output_path: Path) -> None:
    """Write Parquet through a sibling temporary file to avoid partial artifacts."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{output_path.stem}-",
            suffix=".tmp",
            dir=output_path.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        pq.write_table(
            table,
            temporary_path,
            compression=PARQUET_COMPRESSION,
            use_dictionary=["sex"],
            write_statistics=True,
            version="2.6",
        )
        os.replace(temporary_path, output_path)
        temporary_path = None
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _write_manifest_atomically(manifest: BuildManifest, output_path: Path) -> None:
    """Replace the build manifest only after its complete content is on disk."""
    content = json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n"
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    try:
        temporary_path.write_text(content, encoding="utf-8")
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def build_dataset(
    raw_dir: Path,
    output_dir: Path,
    *,
    first_year: int = FIRST_YEAR,
    expected_last_year: int = SNAPSHOT_LAST_YEAR,
) -> BuildManifest:
    """Validate raw inputs and atomically build Parquet plus a traceability manifest.

    Args:
        raw_dir: Directory containing immutable ``yobYYYY.txt`` source files.
        output_dir: Directory that receives generated artifacts.
        first_year: First annual file required by this snapshot.
        expected_last_year: Last annual file required by this snapshot.

    Returns:
        Metadata and fingerprints describing the completed build.

    Raises:
        DataBuildError: If validation fails or no annual tables can be built.

    """
    validation = validate_dataset(
        raw_dir,
        first_year=first_year,
        expected_last_year=expected_last_year,
    )
    if not validation.valid:
        codes = ", ".join(sorted({issue.code for issue in validation.issues}))
        raise DataBuildError(f"Raw-data validation failed: {codes}")

    annual_paths = [raw_dir / profile.file for profile in validation.years]
    tables = [
        _read_annual_file(path, profile.year)
        for path, profile in zip(annual_paths, validation.years, strict=True)
    ]
    if not tables:
        raise DataBuildError("No annual files were available to build.")

    combined = _canonicalize(tables)
    parquet_path = output_dir / DATASET_FILENAME
    _write_parquet_atomically(combined, parquet_path)

    sources = tuple(
        SourceFingerprint(file=path.name, sha256=sha256_file(path), bytes=path.stat().st_size)
        for path in annual_paths
    )
    manifest = BuildManifest(
        pipeline_version=PIPELINE_VERSION,
        first_year=validation.first_year or first_year,
        last_year=validation.last_year or expected_last_year,
        annual_files=validation.annual_files,
        rows=validation.rows,
        applications=validation.applications,
        unique_names=validation.unique_names,
        schema={field.name: str(field.type) for field in PROCESSED_SCHEMA},
        sort_order=("year ASC", "sex ASC", "count DESC", "name ASC"),
        parquet_compression=PARQUET_COMPRESSION,
        parquet_file=DATASET_FILENAME,
        parquet_sha256=sha256_file(parquet_path),
        parquet_bytes=parquet_path.stat().st_size,
        sources=sources,
    )
    _write_manifest_atomically(manifest, output_dir / MANIFEST_FILENAME)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    """Build the processed dataset from command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/names"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--expected-last-year", type=int, default=SNAPSHOT_LAST_YEAR)
    arguments = parser.parse_args(argv)

    try:
        manifest = build_dataset(
            arguments.raw_dir,
            arguments.output_dir,
            expected_last_year=arguments.expected_last_year,
        )
    except DataBuildError as error:
        parser.exit(1, f"Build failed: {error}\n")

    print(
        f"Built {manifest.parquet_file}: {manifest.rows:,} rows, "
        f"{manifest.parquet_bytes:,} bytes, SHA-256 {manifest.parquet_sha256}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
