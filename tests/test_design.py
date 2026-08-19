"""Accessibility contract tests for the shared visual system."""

import pytest

from babynames.ui.design import (
    PRIMARY,
    SURFACE,
    TEXT,
    contrast_ratio,
    relative_luminance,
)


def test_text_and_primary_colors_meet_wcag_contrast() -> None:
    """Core foreground colors should satisfy WCAG AA normal-text contrast."""
    assert contrast_ratio(TEXT, SURFACE) >= 4.5
    assert contrast_ratio(PRIMARY, SURFACE) >= 4.5


def test_contrast_is_order_independent() -> None:
    """Swapping foreground and background must not change the contrast ratio."""
    assert contrast_ratio(TEXT, SURFACE) == pytest.approx(contrast_ratio(SURFACE, TEXT))


def test_invalid_hex_color_has_actionable_error() -> None:
    """Malformed color tokens should fail before they reach chart configuration."""
    with pytest.raises(ValueError, match="six-digit hex"):
        relative_luminance("purple")
