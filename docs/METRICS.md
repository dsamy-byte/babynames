# Analytical Metric Contract

This document defines the calculations exposed by the domain layer. Interfaces must
use these definitions rather than reimplementing metrics in page code.

## Source categories and suppressed observations

SSA publishes `F` and `M` categories in this historical aggregate dataset. The
application describes them as source sex categories and does not interpret them as a
complete representation of gender identity.

SSA omits a name/category/year combination when its count is below five. An absent
row therefore means **not published**, not zero. Histories and comparisons preserve
these gaps. Trend calculations never replace them with zero.

## Rank

Rank is calculated independently inside each `(year, sex)` group using count in
descending order. Competition ranking is used: equal counts share the best applicable
rank and the next rank includes the size of the tie. For example, counts producing
positions `1, 2, 2, 4` receive ranks `1, 2, 2, 4`.

Name spelling in ascending order provides deterministic display order within a tie;
it does not break the statistical tie.

## Share

Share is a name's published count divided by the sum of all published counts in the
same year and source sex category:

```text
share = count / sum(count for the same year and sex)
```

This is a share of published SSA applications represented in the files, not a share
of every U.S. birth.

## Name history and summary

A history contains only published observations. A summary reports:

- first and last published years;
- number of years published;
- sum of published applications;
- peak annual count and its earliest year if tied; and
- best competition rank and its earliest year if tied.

Name lookup is case-insensitive, while results preserve SSA's canonical spelling.

## Name comparison

Comparisons return long-form published histories for at least two distinct names.
They do not manufacture rows for missing years. The interface may visually show a
gap but must not label the missing value as zero.

## Rising and falling names

Trend change compares two endpoint years for names published at both endpoints:

```text
rank_change = start_rank - end_rank
count_change = end_count - start_count
share_change = end_share - start_share
```

A positive rank change means the name moved toward rank one; a negative change means
it fell. Names absent at either endpoint are excluded because their suppressed counts
and ranks are unknown.

## Unisex analysis

For a selected year, a name is included only if SSA published it in both `F` and `M`
categories. Results include combined count, female-category share, and balance:

```text
balance_score = min(female_count, male_count) / max(female_count, male_count)
```

The score ranges above zero through one. A value of one means equal published counts;
lower values indicate a stronger skew toward one source category.
