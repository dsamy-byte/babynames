"""Integration coverage for the complete committed SSA data snapshot."""

from pathlib import Path

from babynames.data_validation import validate_dataset


def test_committed_snapshot_satisfies_contract() -> None:
    """Guard the validated snapshot contract and known aggregate totals."""
    project_root = Path(__file__).resolve().parents[1]

    report = validate_dataset(project_root / "data" / "raw" / "names")

    assert report.valid
    assert (report.first_year, report.last_year) == (1880, 2025)
    assert report.annual_files == 146
    assert report.rows == 2_181_032
    assert report.applications == 375_362_447
    assert report.unique_names == 105_966
    assert report.sex_applications == {"F": 185_559_287, "M": 189_803_160}
