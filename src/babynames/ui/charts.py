"""Accessible Altair chart builders shared by Streamlit pages."""

from __future__ import annotations

from typing import Literal, cast

import altair as alt
import pandas as pd

from babynames.ui.design import (
    CATEGORY_DASH_RANGE,
    CATEGORY_DOMAIN,
    CATEGORY_RANGE,
    COMPARISON_PALETTE,
    PRIMARY,
    polish_chart,
)

Metric = Literal["count", "rank", "share"]


def annual_applications_chart(totals: pd.DataFrame) -> alt.Chart:
    """Chart annual published application totals with explicit labels and tooltips."""
    chart = (
        alt.Chart(
            totals,
            title="Published applications by year",
            description="Area chart of total published applications for each year.",
        )
        .mark_area(line={"color": PRIMARY}, color="#C9B8EE", opacity=0.5)
        .encode(
            x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
            y=alt.Y("count:Q", title="Published applications", scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip("year:Q", title="Year", format="d"),
                alt.Tooltip("count:Q", title="Applications", format=","),
            ],
        )
        .properties(height=320)
        .interactive()
    )
    return polish_chart(cast(alt.Chart, chart))


def history_chart(history: pd.DataFrame, metric: Metric) -> alt.Chart:
    """Chart one name's published history, separating source categories by color."""
    titles = {
        "count": "Published applications",
        "rank": "Competition rank",
        "share": "Share of category",
    }
    scale = alt.Scale(reverse=True, zero=False) if metric == "rank" else alt.Scale(zero=False)
    value_format = ".2%" if metric == "share" else ","
    chart = (
        alt.Chart(
            history,
            title=f"{titles[metric]} over time",
            description=(f"Line chart of {titles[metric].lower()} by year and source category."),
        )
        .mark_line(point=alt.OverlayMarkDef(size=35))
        .encode(
            x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
            y=alt.Y(f"{metric}:Q", title=titles[metric], scale=scale),
            color=alt.Color(
                "sex:N",
                title="Source category",
                scale=alt.Scale(domain=CATEGORY_DOMAIN, range=CATEGORY_RANGE),
            ),
            strokeDash=alt.StrokeDash(
                "sex:N",
                title="Source category",
                scale=alt.Scale(domain=CATEGORY_DOMAIN, range=CATEGORY_DASH_RANGE),
            ),
            tooltip=[
                alt.Tooltip("year:Q", title="Year", format="d"),
                alt.Tooltip("sex:N", title="Category"),
                alt.Tooltip(f"{metric}:Q", title=titles[metric], format=value_format),
            ],
        )
        .properties(height=380)
        .interactive()
    )
    return polish_chart(cast(alt.Chart, chart))


def comparison_chart(history: pd.DataFrame, metric: Metric) -> alt.Chart:
    """Chart several names on a common metric scale for direct comparison."""
    titles = {
        "count": "Published applications",
        "rank": "Competition rank",
        "share": "Share of category",
    }
    scale = alt.Scale(reverse=True, zero=False) if metric == "rank" else alt.Scale(zero=False)
    value_format = ".2%" if metric == "share" else ","
    chart = (
        alt.Chart(
            history,
            title=f"Name comparison by {titles[metric].lower()}",
            description=f"Line chart comparing selected names by {titles[metric].lower()}.",
        )
        .mark_line(point=False)
        .encode(
            x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
            y=alt.Y(f"{metric}:Q", title=titles[metric], scale=scale),
            color=alt.Color("name:N", title="Name", scale=alt.Scale(range=COMPARISON_PALETTE)),
            strokeDash=alt.StrokeDash("name:N", title="Name"),
            tooltip=[
                alt.Tooltip("year:Q", title="Year", format="d"),
                alt.Tooltip("name:N", title="Name"),
                alt.Tooltip(f"{metric}:Q", title=titles[metric], format=value_format),
            ],
        )
        .properties(height=420)
        .interactive()
    )
    return polish_chart(cast(alt.Chart, chart))
