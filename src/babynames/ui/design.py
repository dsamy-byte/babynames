"""Visual tokens and accessibility helpers shared by presentation components."""

from __future__ import annotations

import re
from typing import cast

import altair as alt

PRIMARY = "#6C4AB6"
PRIMARY_DARK = "#4E3287"
SURFACE = "#FFFDF8"
TEXT = "#201A2E"
BORDER = "#D7CFE5"
FEMALE_CATEGORY = "#0072B2"
MALE_CATEGORY = "#D55E00"
CATEGORY_DOMAIN = ["F", "M"]
CATEGORY_RANGE = [FEMALE_CATEGORY, MALE_CATEGORY]
CATEGORY_DASH_RANGE = [[1, 0], [7, 3]]
COMPARISON_PALETTE = [
    "#0072B2",
    "#D55E00",
    "#009E73",
    "#CC79A7",
    "#E69F00",
]


def _channel_value(channel: int) -> float:
    """Convert one 8-bit sRGB channel to linear-light space."""
    normalized = channel / 255
    return normalized / 12.92 if normalized <= 0.04045 else ((normalized + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """Calculate WCAG relative luminance for a six-digit hexadecimal color."""
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_color):
        raise ValueError(f"Expected a six-digit hex color, received {hex_color!r}.")
    red, green, blue = (int(hex_color[index : index + 2], 16) for index in (1, 3, 5))
    return (
        0.2126 * _channel_value(red)
        + 0.7152 * _channel_value(green)
        + 0.0722 * _channel_value(blue)
    )


def contrast_ratio(first: str, second: str) -> float:
    """Return the WCAG contrast ratio between two hexadecimal colors."""
    lighter, darker = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def polish_chart(chart: alt.Chart) -> alt.Chart:
    """Apply consistent readable typography, grid, legend, and focus-friendly sizing."""
    styled = (
        chart.configure_axis(
            labelColor=TEXT,
            titleColor=TEXT,
            gridColor="#E8E2EF",
            domainColor=BORDER,
            tickColor=BORDER,
            labelFontSize=12,
            titleFontSize=13,
            titlePadding=12,
        )
        .configure_legend(
            labelColor=TEXT,
            titleColor=TEXT,
            labelFontSize=12,
            titleFontSize=12,
            orient="bottom",
        )
        .configure_title(color=TEXT, fontSize=17, fontWeight=600, anchor="start")
        .configure_view(stroke=None)
    )
    return cast(alt.Chart, styled)
