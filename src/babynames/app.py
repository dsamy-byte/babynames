"""Streamlit entry point for the local Baby Names application."""

from __future__ import annotations

import logging
from functools import partial

import streamlit as st

from babynames.analytics import AnalyticsError
from babynames.artifacts import inspect_processed_artifacts
from babynames.logging_config import configure_logging
from babynames.settings import ProjectSettings
from babynames.ui.data_access import load_analytics
from babynames.ui.pages import (
    render_about,
    render_compare,
    render_explore,
    render_overview,
    render_trends,
)

LOGGER = logging.getLogger(__name__)


def _render_build_guidance(message: str) -> None:
    """Show a safe recovery path when generated data is absent or inconsistent."""
    st.title("Baby Names")
    st.error("Processed data is not available.")
    st.write(message)
    st.markdown("Build or repair the local dataset from the repository root:")
    st.code("babynames-validate\nbabynames-build", language="powershell")
    st.caption("The build reads committed raw files and writes only to `data/processed/`.")


def main() -> None:
    """Configure the application, load data safely, and run page navigation."""
    configure_logging()
    st.set_page_config(
        page_title="Baby Names",
        page_icon="👶",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    settings = ProjectSettings.from_environment()
    status = inspect_processed_artifacts(settings.processed_dir)
    if not status.ready or status.manifest is None:
        _render_build_guidance(status.message)
        st.stop()

    try:
        analytics = load_analytics(status)
    except (AnalyticsError, OSError, ValueError):
        LOGGER.exception("Processed baby-name data could not be loaded.")
        _render_build_guidance("The generated dataset could not be loaded safely.")
        st.stop()

    st.sidebar.title("Baby Names")
    st.sidebar.caption(f"National data · {analytics.year_range[0]}–{analytics.year_range[1]}")
    navigation = st.navigation(
        {
            "Explore": [
                st.Page(
                    partial(render_overview, analytics, status.manifest),
                    title="Overview",
                    url_path="overview",
                    default=True,
                ),
                st.Page(
                    partial(render_explore, analytics),
                    title="Name search",
                    url_path="names",
                ),
                st.Page(
                    partial(render_compare, analytics),
                    title="Compare",
                    url_path="compare",
                ),
                st.Page(
                    partial(render_trends, analytics),
                    title="Trends",
                    url_path="trends",
                ),
            ],
            "Project": [
                st.Page(
                    partial(render_about, status.manifest),
                    title="About the data",
                    url_path="about",
                ),
            ],
        },
        expanded=True,
    )
    navigation.run()


if __name__ == "__main__":
    main()
