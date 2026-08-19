"""Application configuration derived from stable defaults and environment overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROCESSED_DIR_ENV = "BABYNAMES_PROCESSED_DIR"


@dataclass(frozen=True)
class ProjectSettings:
    """Hold filesystem locations needed by the local application runtime."""

    project_root: Path
    processed_dir: Path

    @classmethod
    def from_environment(cls) -> ProjectSettings:
        """Build settings with an optional processed-data directory override.

        ``BABYNAMES_PROCESSED_DIR`` supports tests and advanced local layouts. The
        default follows the documented repository structure.
        """
        project_root = Path(__file__).resolve().parents[2]
        configured_dir = os.environ.get(PROCESSED_DIR_ENV)
        processed_dir = (
            Path(configured_dir).expanduser().resolve()
            if configured_dir
            else project_root / "data" / "processed"
        )
        return cls(project_root=project_root, processed_dir=processed_dir)
