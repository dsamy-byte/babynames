# Local User Guide

## Start the application

From PowerShell in the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
babynames-validate
babynames-build
streamlit run src/babynames/app.py
```

Validation and build commands can be skipped on later runs when raw inputs and the
generated Parquet file have not changed.

## Overview

The overview shows snapshot coverage, published record and application totals, and a
long-term volume chart. Move the ranking-year control to compare the top ten names in
the two source categories for any year from 1880 through 2025.

## Name search

Select a canonical name and an available source category. Summary cards show its
published span, total recorded applications, peak annual count, and best rank. Switch
the chart between applications, competition rank, and category share. The expandable
table exposes every published observation.

## Compare names

Choose one source category and two to five names. Category share is the recommended
default because it makes years with different application totals more comparable.
Applications and rank remain available. The summary table compares lifetime spans,
totals, peaks, and best ranks.

## Trends

The rising/falling view compares two selected endpoint years. A positive rank change
means movement toward rank one. Only names published at both endpoints are eligible,
because an absent row may hide a suppressed count.

The unisex view includes names published in both source categories for the selected
year. A balance score near one indicates similar published counts; a lower score
indicates a stronger category skew.

## Interpret results carefully

- Records are Social Security card applications, not a complete birth registry.
- Counts below five are suppressed by the source.
- A missing observation is unknown and must not be interpreted as zero.
- `F` and `M` are historical source categories, not a complete representation of
  gender identity.
- Competition-ranked names with equal counts share a rank.
- Category share uses the total published count in the same year and category.

Exact formulas are maintained in `docs/METRICS.md`.

## Refresh the documentation screenshot

After materially changing the default overview, close any process using port 8511 and
run the documented capture command from the repository root:

```powershell
python scripts/capture_screenshots.py
```

The command temporarily runs Streamlit, uses an installed Chrome or Edge executable,
and replaces `docs/images/overview.png`. It does not download a browser or deploy data.
