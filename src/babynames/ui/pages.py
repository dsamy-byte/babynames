"""Documented page renderers for the Streamlit application shell."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st

from babynames.analytics import BabyNameAnalytics


def render_overview(analytics: BabyNameAnalytics, manifest: Mapping[str, Any]) -> None:
    """Render dataset context and a useful first view of the latest rankings."""
    first_year, last_year = analytics.year_range
    st.title("Baby Names")
    st.caption("Explore 146 years of U.S. Social Security baby-name records.")

    coverage, records, applications = st.columns(3)
    coverage.metric("Coverage", f"{first_year}–{last_year}")
    records.metric("Published records", f"{int(manifest['rows']):,}")
    applications.metric("Recorded applications", f"{int(manifest['applications']):,}")

    st.subheader(f"Most popular names in {last_year}")
    female, male = st.columns(2)
    with female:
        st.markdown("**Female source category**")
        st.dataframe(
            analytics.rankings(last_year, "F"),
            hide_index=True,
            width="stretch",
            column_config={"share": st.column_config.NumberColumn(format="%.2%%")},
        )
    with male:
        st.markdown("**Male source category**")
        st.dataframe(
            analytics.rankings(last_year, "M"),
            hide_index=True,
            width="stretch",
            column_config={"share": st.column_config.NumberColumn(format="%.2%%")},
        )


def render_explore() -> None:
    """Render the reserved shell for individual-name discovery."""
    st.title("Explore a name")
    st.info(
        "Name search, historical charts, rankings, and lifetime summaries arrive in Milestone 6."
    )


def render_compare() -> None:
    """Render the reserved shell for multi-name comparisons."""
    st.title("Compare names")
    st.info("Side-by-side name comparison arrives in Milestone 6.")


def render_trends() -> None:
    """Render the reserved shell for trend and unisex-name discovery."""
    st.title("Discover trends")
    st.info("Rising, falling, and unisex-name exploration arrives in Milestone 6.")


def render_about(manifest: Mapping[str, Any]) -> None:
    """Render source provenance, limitations, and local build information."""
    st.title("About the data")
    st.markdown(
        "This application uses national Social Security card application records. "
        "Names with fewer than five records in a category and year are suppressed, "
        "so a missing observation must not be interpreted as zero."
    )
    st.markdown(
        "The historical `F` and `M` values are source categories and are not a "
        "complete representation of gender identity."
    )
    st.subheader("Local artifact")
    st.code(
        f"Rows: {int(manifest['rows']):,}\n"
        f"Years: {manifest['first_year']}–{manifest['last_year']}\n"
        f"SHA-256: {manifest['parquet_sha256']}",
        language="text",
    )
