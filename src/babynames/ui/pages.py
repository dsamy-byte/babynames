"""Interactive page renderers for the Streamlit application."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import streamlit as st

from babynames.analytics import BabyNameAnalytics
from babynames.ui.charts import (
    Metric,
    annual_applications_chart,
    comparison_chart,
    history_chart,
)

CATEGORY_LABELS = {"F": "Female source category", "M": "Male source category"}
METRIC_LABELS = {
    "count": "Applications",
    "rank": "Rank",
    "share": "Category share",
}


def _preferred_name(names: tuple[str, ...], preferred: str) -> int:
    """Return a stable selectbox index, falling back to the first available name."""
    try:
        return names.index(preferred)
    except ValueError:
        return 0


def _select_year(label: str, first_year: int, last_year: int, *, value: int, key: str) -> int:
    """Render a year slider, or a disabled number field for single-year datasets."""
    if first_year == last_year:
        return int(
            st.number_input(
                label,
                min_value=first_year,
                max_value=last_year,
                value=first_year,
                disabled=True,
                key=key,
            )
        )
    return st.slider(
        label,
        min_value=first_year,
        max_value=last_year,
        value=value,
        key=key,
    )


def _metric_label(metric: str) -> str:
    """Return the user-facing label for a supported analytical metric."""
    return METRIC_LABELS[metric]


def _page_header(eyebrow: str, title: str, description: str) -> None:
    """Render consistent page identity with a concise plain-language introduction."""
    st.caption(eyebrow.upper())
    st.title(title)
    st.markdown(description)


def render_overview(analytics: BabyNameAnalytics, manifest: Mapping[str, Any]) -> None:
    """Render dataset context, long-term volume, and configurable yearly rankings."""
    first_year, last_year = analytics.year_range
    _page_header(
        "National data explorer",
        "Baby Names",
        "Trace how names rise, fade, and return across generations of U.S. Social "
        "Security applications.",
    )

    coverage, records, applications = st.columns(3, gap="medium", border=True)
    coverage.metric("Coverage", f"{first_year}–{last_year}")
    records.metric("Published records", f"{int(manifest['rows']):,}")
    applications.metric("Recorded applications", f"{int(manifest['applications']):,}")
    st.altair_chart(
        annual_applications_chart(analytics.annual_totals()),
        width="stretch",
        theme="streamlit",
    )
    st.caption(
        "Totals represent published Social Security applications in this dataset, "
        "not every U.S. birth. Names with fewer than five observations are suppressed."
    )

    ranking_year = _select_year(
        "Ranking year",
        first_year,
        last_year,
        value=last_year,
        key="overview_year",
    )
    st.subheader(f"Most popular names in {ranking_year}")
    female, male = st.columns(2, gap="large", border=True)
    for column, sex in ((female, "F"), (male, "M")):
        with column:
            st.markdown(f"**{CATEGORY_LABELS[sex]}**")
            st.dataframe(
                analytics.rankings(ranking_year, sex),
                hide_index=True,
                width="stretch",
                height=390,
                column_config={"share": st.column_config.NumberColumn(format="%.2%%")},
            )


def render_explore(analytics: BabyNameAnalytics) -> None:
    """Render searchable history, summary milestones, charts, and source observations."""
    _page_header(
        "Name profile",
        "Explore a name",
        "Follow one name through its published history, peaks, rankings, and share of "
        "its source category.",
    )
    names = analytics.available_names()
    with st.container(border=True):
        selected_name = st.selectbox(
            "Name",
            names,
            index=_preferred_name(names, "Olivia"),
            key="explore_name",
            help="Type to search the complete list of published name spellings.",
        )
        categories = analytics.name_categories(selected_name)
        selected_sex = st.radio(
            "Source category",
            categories,
            format_func=CATEGORY_LABELS.get,
            horizontal=True,
            key="explore_sex",
        )
    history = analytics.name_history(selected_name, selected_sex)
    summary = analytics.name_summary(selected_name, selected_sex)

    first, total, peak, rank = st.columns(4, gap="small", border=True)
    first.metric("Published span", f"{summary.first_year}–{summary.last_year}")
    total.metric("Recorded applications", f"{summary.total_applications:,}")
    peak.metric("Peak annual count", f"{summary.peak_count:,}", f"in {summary.peak_count_year}")
    rank.metric("Best rank", f"#{summary.best_rank}", f"in {summary.best_rank_year}")

    metric_label = cast(
        Metric,
        st.segmented_control(
            "Chart metric",
            options=["count", "rank", "share"],
            default="count",
            format_func=_metric_label,
            key="explore_metric",
        )
        or "count",
    )
    st.altair_chart(
        history_chart(history, metric_label),
        width="stretch",
        theme="streamlit",
    )
    st.caption(
        "Gaps mean the name was not published for that category and year; they are not zeros."
    )
    with st.expander("View published observations"):
        st.dataframe(
            history.sort_values("year", ascending=False),
            hide_index=True,
            width="stretch",
            height=420,
            column_config={"share": st.column_config.NumberColumn(format="%.3%%")},
        )


def render_compare(analytics: BabyNameAnalytics) -> None:
    """Render a category-specific comparison for two to five names."""
    _page_header(
        "Side-by-side history",
        "Compare names",
        "Put two to five names on the same scale to compare popularity across time.",
    )
    with st.container(border=True):
        selected_sex = st.radio(
            "Source category",
            ("F", "M"),
            format_func=CATEGORY_LABELS.get,
            horizontal=True,
            key="compare_sex",
        )
        names = analytics.available_names(selected_sex)
        preferred = [name for name in ("Olivia", "Emma") if name in names]
        defaults = preferred if len(preferred) == 2 else list(names[:2])
        selected_names = st.multiselect(
            "Names",
            names,
            default=defaults,
            max_selections=5,
            key="compare_names",
            help="Choose between two and five names. Type to search the list.",
        )
    if len(selected_names) < 2:
        st.info("Choose at least two names to compare.")
        return

    metric = cast(
        Metric,
        st.segmented_control(
            "Comparison metric",
            options=["share", "count", "rank"],
            default="share",
            format_func=_metric_label,
            key="compare_metric",
        )
        or "share",
    )
    history = analytics.compare_names(selected_names, selected_sex)
    st.altair_chart(
        comparison_chart(history, metric),
        width="stretch",
        theme="streamlit",
    )
    st.caption(
        "Only published observations are connected. Missing years reflect suppression "
        "or absence from the published source."
    )
    summaries = [analytics.name_summary(name, selected_sex) for name in selected_names]
    st.dataframe(
        [
            {
                "Name": summary.name,
                "First year": summary.first_year,
                "Last year": summary.last_year,
                "Years published": summary.years_published,
                "Applications": summary.total_applications,
                "Peak count": summary.peak_count,
                "Peak year": summary.peak_count_year,
                "Best rank": summary.best_rank,
            }
            for summary in summaries
        ],
        hide_index=True,
        width="stretch",
        height=250,
    )


def render_trends(analytics: BabyNameAnalytics) -> None:
    """Render endpoint movers and annual unisex-name discovery tools."""
    _page_header(
        "Pattern finder",
        "Discover trends",
        "Find the largest rank movers between two years or names published in both "
        "source categories.",
    )
    movers_tab, unisex_tab = st.tabs(["Rising and falling", "Unisex names"])
    first_year, last_year = analytics.year_range

    with movers_tab:
        if first_year == last_year:
            st.info("Trend changes require at least two years of processed data.")
        else:
            start_default = max(first_year, last_year - 10)
            start_year, end_year = st.slider(
                "Comparison years",
                min_value=first_year,
                max_value=last_year,
                value=(start_default, last_year),
                key="trend_years",
            )
            selected_sex = st.radio(
                "Source category",
                ("F", "M"),
                format_func=CATEGORY_LABELS.get,
                horizontal=True,
                key="trend_sex",
            )
            direction = st.radio(
                "Direction",
                ("rising", "falling"),
                horizontal=True,
                key="trend_direction",
            )
            limit = st.select_slider(
                "Number of names",
                options=(10, 25, 50, 100),
                value=25,
                key="trend_limit",
            )
            changes = analytics.trend_changes(
                start_year,
                end_year,
                selected_sex,
                direction=direction,
                limit=limit,
            )
            st.dataframe(
                changes,
                hide_index=True,
                width="stretch",
                height=520,
                column_config={
                    "start_share": st.column_config.NumberColumn(format="%.3%%"),
                    "end_share": st.column_config.NumberColumn(format="%.3%%"),
                    "share_change": st.column_config.NumberColumn(format="%+.3%%"),
                },
            )
            st.caption(
                "Positive rank change means movement toward rank one. Only names "
                "published at both endpoints are eligible."
            )

    with unisex_tab:
        selected_year = _select_year(
            "Year",
            first_year,
            last_year,
            value=last_year,
            key="unisex_year",
        )
        unisex = analytics.unisex_names(selected_year, limit=100)
        st.dataframe(
            unisex,
            hide_index=True,
            width="stretch",
            height=560,
            column_config={
                "female_share": st.column_config.NumberColumn(format="%.1%%"),
                "balance_score": st.column_config.ProgressColumn(min_value=0, max_value=1),
            },
        )
        st.caption(
            "Balance approaches 1 when published counts are similar across both source categories."
        )


def render_about(manifest: Mapping[str, Any]) -> None:
    """Render source provenance, limitations, metric links, and build information."""
    _page_header(
        "Method and provenance",
        "About the data",
        "Understand what the Social Security dataset represents and how this app "
        "calculates its metrics.",
    )
    st.markdown(
        "This application uses national Social Security card application records. "
        "Names with fewer than five records in a category and year are suppressed, "
        "so a missing observation must not be interpreted as zero."
    )
    st.markdown(
        "The historical `F` and `M` values are source categories and are not a "
        "complete representation of gender identity."
    )
    st.markdown(
        "Ranks use competition ranking, shares use each year/category total, and trend "
        "movers require publication at both endpoints. See `docs/METRICS.md` for exact definitions."
    )
    st.subheader("Local artifact")
    st.code(
        f"Rows: {int(manifest['rows']):,}\n"
        f"Years: {manifest['first_year']}–{manifest['last_year']}\n"
        f"SHA-256: {manifest['parquet_sha256']}",
        language="text",
    )
