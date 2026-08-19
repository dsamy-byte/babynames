"""Cached boundary between Streamlit reruns and the analytical domain service."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from babynames.analytics import BabyNameAnalytics
from babynames.artifacts import ArtifactStatus


@st.cache_resource(show_spinner="Loading 146 years of baby-name data…")
def _load_cached(path_text: str, modified_ns: int, size: int) -> BabyNameAnalytics:
    """Load analytics once for a specific path and file signature.

    ``modified_ns`` and ``size`` deliberately participate in Streamlit's cache key;
    rebuilding the local dataset therefore invalidates stale in-memory analytics.
    """
    del modified_ns, size  # Cache-key inputs do not alter the loader operation.
    return BabyNameAnalytics.from_parquet(Path(path_text))


def load_analytics(status: ArtifactStatus) -> BabyNameAnalytics:
    """Load cached analytics for a ready artifact status.

    Raises:
        ValueError: If artifact inspection did not mark the dataset ready.

    """
    if not status.ready:
        raise ValueError("Cannot load analytics before processed artifacts are ready.")
    file_status = status.dataset_path.stat()
    return _load_cached(str(status.dataset_path), file_status.st_mtime_ns, file_status.st_size)
