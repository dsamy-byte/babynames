"""Accessible Altair chart builders shared by Streamlit pages."""

from __future__ import annotations

from typing import Literal

import altair as alt
import pandas as pd

Metric = Literal["count", "rank", "share"]


def annual_applications_chart(totals: pd.DataFrame) -> alt.Chart:
    """Chart annual published application totals with explicit labels and tooltips."""
    return (
        alt.Chart(totals, title="Published applications by year")
        .mark_area(line={"color": "#6C4AB6"}, color="#C9B8EE", opacity=0.55)
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


def history_chart(history: pd.DataFrame, metric: Metric) -> alt.Chart:
    """Chart one name's published history, separating source categories by color."""
    titles = {
        "count": "Published applications",
        "rank": "Competition rank",
        "share": "Share of category",
    }
    scale = alt.Scale(reverse=True, zero=False) if metric == "rank" else alt.Scale(zero=False)
    value_format = ".2%" if metric == "share" else ","
    return (
        alt.Chart(history, title=f"{titles[metric]} over time")
        .mark_line(point=alt.OverlayMarkDef(size=35))
        .encode(
            x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
            y=alt.Y(f"{metric}:Q", title=titles[metric], scale=scale),
            color=alt.Color("sex:N", title="Source category"),
            tooltip=[
                alt.Tooltip("year:Q", title="Year", format="d"),
                alt.Tooltip("sex:N", title="Category"),
                alt.Tooltip(f"{metric}:Q", title=titles[metric], format=value_format),
            ],
        )
        .properties(height=380)
        .interactive()
    )


def comparison_chart(history: pd.DataFrame, metric: Metric) -> alt.Chart:
    """Chart several names on a common metric scale for direct comparison."""
    titles = {
        "count": "Published applications",
        "rank": "Competition rank",
        "share": "Share of category",
    }
    scale = alt.Scale(reverse=True, zero=False) if metric == "rank" else alt.Scale(zero=False)
    value_format = ".2%" if metric == "share" else ","
    return (
        alt.Chart(history, title=f"Name comparison by {titles[metric].lower()}")
        .mark_line(point=False)
        .encode(
            x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
            y=alt.Y(f"{metric}:Q", title=titles[metric], scale=scale),
            color=alt.Color("name:N", title="Name"),
            tooltip=[
                alt.Tooltip("year:Q", title="Year", format="d"),
                alt.Tooltip("name:N", title="Name"),
                alt.Tooltip(f"{metric}:Q", title=titles[metric], format=value_format),
            ],
        )
        .properties(height=420)
        .interactive()
    )
