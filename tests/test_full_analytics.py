"""Integration coverage for analytics over the complete processed snapshot."""

from pathlib import Path

from babynames.analytics import BabyNameAnalytics
from babynames.data_pipeline import build_dataset


def test_known_full_snapshot_analytics(tmp_path: Path) -> None:
    """Verify well-known rankings and totals through the complete production path."""
    project_root = Path(__file__).resolve().parents[1]
    manifest = build_dataset(project_root / "data" / "raw" / "names", tmp_path)
    analytics = BabyNameAnalytics.from_parquet(tmp_path / manifest.parquet_file)

    assert analytics.year_range == (1880, 2025)
    assert analytics.rankings(2025, "F").iloc[0]["name"] == "Olivia"
    assert analytics.rankings(2025, "M").iloc[0]["name"] == "Liam"
    assert analytics.name_summary("James", "M").total_applications == 5_250_638
    assert not analytics.unisex_names(2025).empty
