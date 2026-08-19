"""Specification tests for accessible shared Altair chart builders."""

import pandas as pd

from babynames.ui.charts import annual_applications_chart, comparison_chart, history_chart


def test_annual_chart_has_explicit_axes_and_tooltips() -> None:
    """The overview chart should communicate year, volume, and exact hover values."""
    chart = annual_applications_chart(pd.DataFrame({"year": [2000], "count": [100]}))
    specification = chart.to_dict()

    assert specification["title"] == "Published applications by year"
    assert specification["encoding"]["x"]["title"] == "Year"
    assert specification["encoding"]["y"]["title"] == "Published applications"
    assert len(specification["encoding"]["tooltip"]) == 2
    assert specification["description"]


def test_rank_history_reverses_axis_and_colors_categories() -> None:
    """Rank charts should place rank one at the top and distinguish source categories."""
    history = pd.DataFrame(
        {"year": [2000], "sex": ["F"], "count": [10], "rank": [1], "share": [0.5]}
    )
    specification = history_chart(history, "rank").to_dict()

    assert specification["encoding"]["y"]["scale"]["reverse"] is True
    assert specification["encoding"]["color"]["field"] == "sex"
    assert specification["encoding"]["strokeDash"]["field"] == "sex"


def test_comparison_chart_uses_name_as_series() -> None:
    """Comparison charts should encode each selected name as a separate series."""
    history = pd.DataFrame(
        {"year": [2000], "name": ["Amy"], "count": [10], "rank": [1], "share": [0.5]}
    )
    specification = comparison_chart(history, "share").to_dict()

    assert specification["encoding"]["color"]["field"] == "name"
    assert specification["encoding"]["strokeDash"]["field"] == "name"
    assert specification["encoding"]["y"]["title"] == "Share of category"
