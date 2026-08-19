"""Central logging configuration for local application and command diagnostics."""

from __future__ import annotations

import logging
import os

LOG_LEVEL_ENV = "BABYNAMES_LOG_LEVEL"
DEFAULT_LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging() -> int:
    """Configure root logging from a validated environment level and return its value.

    Invalid levels fall back to ``INFO`` rather than preventing application startup.
    ``basicConfig`` respects handlers already installed by Streamlit or a test runner.
    """
    requested_level = os.environ.get(LOG_LEVEL_ENV, DEFAULT_LOG_LEVEL).upper()
    level = getattr(logging, requested_level, None)
    if not isinstance(level, int):
        level = logging.INFO
        logging.getLogger(__name__).warning(
            "Ignoring invalid %s value %r; using %s.",
            LOG_LEVEL_ENV,
            requested_level,
            DEFAULT_LOG_LEVEL,
        )
    logging.basicConfig(level=level, format=LOG_FORMAT)
    return level
