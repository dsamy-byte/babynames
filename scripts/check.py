"""Run the complete deterministic local quality gate.

The script uses the active Python interpreter so it works in PowerShell, CI, and
other shells without duplicating platform-specific command syntax. Dependency audit
is optional because it requires current package-index vulnerability information.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(command: Sequence[str]) -> None:
    """Run one quality command from the repository root and fail immediately."""
    display = " ".join(command)
    print(f"\n> {display}", flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)  # noqa: S603


def main(argv: Sequence[str] | None = None) -> int:
    """Run formatting, lint, typing, tests, coverage, and optional dependency audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Also query vulnerability data for the active environment.",
    )
    arguments = parser.parse_args(argv)
    python = sys.executable

    run([python, "-m", "ruff", "format", "--check", "."])
    run([python, "-m", "ruff", "check", "."])
    run([python, "-m", "mypy"])
    run(
        [
            python,
            "-m",
            "pytest",
            "--cov=babynames",
            "--cov-report=term-missing",
            "--cov-report=xml",
        ]
    )
    if arguments.audit:
        run([python, "-m", "pip_audit"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
