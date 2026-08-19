"""Focused contract tests for the UI-independent analytics service."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import pytest

from babynames.analytics import AnalyticsError, AnalyticsInputError, BabyNameAnalytics


@pytest.fixture
def analytics() -> BabyNameAnalytics:
    """Return a small multi-year dataset containing ties and unisex observations."""
    records = pd.DataFrame(
        [
            (2000, "Amy", "F", 10),
            (2000, "Zoe", "F", 8),
            (2000, "Ada", "F", 8),
            (2000, "Sam", "F", 5),
            (2000, "Bob", "M", 12),
            (2000, "Sam", "M", 7),
            (2001, "Zoe", "F", 14),
            (2001, "Amy", "F", 9),
            (2001, "Sam", "F", 6),
            (2001, "Bob", "M", 11),
            (2001, "Sam", "M", 8),
            (2001, "Amy", "M", 5),
        ],
        columns=["year", "name", "sex", "count"],
    )
    return BabyNameAnalytics(records)


def test_rankings_use_competition_rank_and_category_share(
    analytics: BabyNameAnalytics,
) -> None:
    """Equal counts should share rank while shares use the year/category total."""
    result = analytics.rankings(2000, "f")

    assert result[["rank", "name", "count"]].values.tolist() == [
        [1, "Amy", 10],
        [2, "Ada", 8],
        [2, "Zoe", 8],
        [4, "Sam", 5],
    ]
    assert result.iloc[0]["share"] == pytest.approx(10 / 31)


def test_discovery_helpers_expose_names_categories_and_annual_totals(
    analytics: BabyNameAnalytics,
) -> None:
    """UI discovery helpers should remain canonical, filterable, and aggregated."""
    assert analytics.available_names("F") == ("Ada", "Amy", "Sam", "Zoe")
    assert analytics.name_categories("amy") == ("F", "M")
    assert analytics.annual_totals()["count"].tolist() == [50, 53]
    assert analytics.annual_totals("M")["count"].tolist() == [19, 24]


def test_history_comparison_and_summary_resolve_names_case_insensitively(
    analytics: BabyNameAnalytics,
) -> None:
    """User-entered casing should resolve without changing canonical source spelling."""
    history = analytics.name_history(" amy ", "F")
    comparison = analytics.compare_names(["amy", "ZOE"], "f")
    summary = analytics.name_summary("amy", "F")

    assert history["year"].tolist() == [2000, 2001]
    assert set(comparison["name"]) == {"Amy", "Zoe"}
    assert summary.total_applications == 19
    assert summary.peak_count_year == 2000
    assert summary.best_rank == 1


def test_trends_compare_only_names_published_at_both_endpoints(
    analytics: BabyNameAnalytics,
) -> None:
    """Endpoint rank changes should exclude suppressed or otherwise absent names."""
    rising = analytics.trend_changes(2000, 2001, "F", direction="rising")
    falling = analytics.trend_changes(2000, 2001, "F", direction="falling")

    assert rising.iloc[0]["name"] == "Zoe"
    assert rising.iloc[0]["rank_change"] == 1
    assert falling.iloc[0]["name"] == "Amy"
    assert "Ada" not in set(rising["name"])


def test_unisex_names_require_both_categories_and_include_balance(
    analytics: BabyNameAnalytics,
) -> None:
    """Unisex results should include only names published in both source categories."""
    result = analytics.unisex_names(2001)

    assert result["name"].tolist() == ["Amy", "Sam"]
    assert result.iloc[0]["total_count"] == 14
    assert result.iloc[1]["balance_score"] == pytest.approx(6 / 8)


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda service: service.rankings(1999, "F"), "Year must be between"),
        (lambda service: service.rankings(2000, "X"), "Sex must"),
        (lambda service: service.rankings(2000, "F", limit=0), "Limit must"),
        (lambda service: service.name_history("Missing"), "Name was not found"),
        (lambda service: service.compare_names(["Amy", "amy"]), "at least two"),
        (
            lambda service: service.trend_changes(2001, 2000, "F"),
            "Start year must be earlier",
        ),
    ],
)
def test_invalid_queries_have_clear_errors(
    analytics: BabyNameAnalytics,
    call: Callable[[BabyNameAnalytics], object],
    message: str,
) -> None:
    """Invalid public requests should fail early with actionable messages."""
    with pytest.raises(AnalyticsInputError, match=message):
        call(analytics)


def test_invalid_processed_contract_is_rejected() -> None:
    """Missing required columns should prevent analytics initialization."""
    with pytest.raises(AnalyticsError, match="missing required columns"):
        BabyNameAnalytics(pd.DataFrame({"name": ["Amy"]}))
