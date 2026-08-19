# Raw Data Contract

## Source boundary

The application treats `data/raw/names/` as immutable source material. Generated or
cleaned data must never overwrite these files.

The current national snapshot contains one annual file for every year from 1880
through 2025 and the source document `NationalReadMe.pdf`.

## Annual files

- Filename: `yobYYYY.txt`, where `YYYY` is the four-digit record year.
- Encoding: UTF-8-compatible text (the current files contain ASCII data).
- Format: comma-separated rows without a header.
- Columns, in order: `name`, `sex`, `count`.
- `name`: non-empty ASCII letters using the spelling supplied by SSA.
- `sex`: `F` or `M`, reflecting the categories published in the source files.
- `count`: an integer of at least five. SSA suppresses name/sex/year combinations
  with fewer than five occurrences for privacy.
- Key: a `name` and `sex` pair occurs at most once within an annual file.

The sex field is a characteristic of this historical aggregate dataset and should
not be presented as a complete representation of gender identity.

## Validated snapshot profile

The committed quality reports under `reports/` record the exact totals for the
current snapshot. They are regenerated with:

```powershell
babynames-validate
```

A nonzero exit code means the raw data violates the contract. JSON is provided for
automation and Markdown for review.

## Processed-data schema

Milestone 3 will produce a normalized table with these initial fields:

| Field | Type | Meaning |
|---|---|---|
| `year` | integer | Year derived from the source filename |
| `name` | string | SSA-provided name spelling |
| `sex` | categorical string | Source category, `F` or `M` |
| `count` | positive integer | Published number of applications |

The unique key is `(year, name, sex)`. Derived rankings and analytical measures will
be calculated in the domain layer rather than silently added to the raw facts.
