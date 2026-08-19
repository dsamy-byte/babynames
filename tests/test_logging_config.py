"""Tests for predictable environment-driven logging configuration."""

import logging

import pytest

from babynames.logging_config import LOG_LEVEL_ENV, configure_logging


def test_configure_logging_accepts_standard_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """A recognized level should be returned for application diagnostics."""
    monkeypatch.setenv(LOG_LEVEL_ENV, "debug")

    assert configure_logging() == logging.DEBUG


def test_invalid_logging_level_falls_back_to_info(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An invalid environment value should warn and preserve application startup."""
    monkeypatch.setenv(LOG_LEVEL_ENV, "verbose-ish")

    with caplog.at_level(logging.WARNING):
        level = configure_logging()

    assert level == logging.INFO
    assert "Ignoring invalid" in caplog.text
