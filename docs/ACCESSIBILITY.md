# Accessibility and Visual Design

Baby Names uses native Streamlit controls and layout primitives so keyboard focus,
labels, zoom behavior, and responsive reflow remain available without custom HTML.
The interface is designed for local desktop use and remains usable at narrower
browser widths through Streamlit's column stacking and bounded table heights.

## Visual system

Application theme values live in `.streamlit/config.toml`; chart-specific tokens and
WCAG calculation helpers live in `src/babynames/ui/design.py`. The warm off-white
surface, dark text, purple action color, restrained borders, consistent radii, and
shared typography give every page the same hierarchy.

Automated tests verify these core WCAG contrast ratios against the 4.5:1 AA target:

- Primary purple on the surface: 6.27:1
- Main text on the surface: 16.54:1

Charts use a color-vision-deficiency-friendly palette. Source categories and name
series also receive different dash patterns, so meaning never depends on color alone.
Every chart has a programmatic description plus explicit axis, legend, and tooltip
labels. Rank charts keep rank one at the top.

## Interaction and performance

- Every input has a visible label and uses a native keyboard-operable widget.
- Page introductions explain the purpose before controls and results.
- Filter groups and result panels use bordered containers for visual structure.
- Long tables have fixed viewport heights to avoid excessive page growth.
- Frequently reused names, category mappings, and annual totals are precomputed once
  when the cached analytics service loads; callers receive immutable tuples or copies.

## Verification and limitations

Color contrast and chart encodings are checked automatically. Streamlit render tests
exercise every page. The committed overview screenshot is captured at 1440 by 1100
CSS pixels with a real local Chromium browser:

```powershell
python scripts/capture_screenshots.py
```

The screenshot is documentation, not a substitute for keyboard and screen-reader
testing. Before a public release, manually verify keyboard-only navigation, 200% zoom,
and a current screen reader on the intended operating system.
