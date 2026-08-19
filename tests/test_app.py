"""Streamlit smoke tests for safe application startup behavior."""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from babynames.data_pipeline import build_dataset
from babynames.settings import PROCESSED_DIR_ENV


def test_app_explains_how_to_build_missing_processed_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A clean checkout should render recovery guidance without an app exception."""
    monkeypatch.setenv(PROCESSED_DIR_ENV, str(tmp_path))
    app_path = Path(__file__).resolve().parents[1] / "src" / "babynames" / "app.py"

    app = AppTest.from_file(app_path).run(timeout=15)

    assert not app.exception
    assert app.error[0].value == "Processed data is not available."
    assert "babynames-build" in app.code[0].value


def test_app_renders_overview_with_ready_processed_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ready artifacts should load analytics and render the default overview page."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    (raw_dir / "yob2000.txt").write_text("Amy,F,10\nBob,M,12\n", encoding="utf-8")
    build_dataset(raw_dir, processed_dir, first_year=2000, expected_last_year=2000)
    monkeypatch.setenv(PROCESSED_DIR_ENV, str(processed_dir))
    app_path = Path(__file__).resolve().parents[1] / "src" / "babynames" / "app.py"

    app = AppTest.from_file(app_path).run(timeout=20)

    assert not app.exception
    assert app.title[0].value == "Baby Names"
    assert {metric.label for metric in app.metric} == {
        "Coverage",
        "Published records",
        "Recorded applications",
    }
