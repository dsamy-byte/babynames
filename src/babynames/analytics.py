"""UI-independent analytical operations for the processed Baby Names dataset.

The service centralizes metric definitions so charts, tables, and future interfaces
cannot silently calculate popularity in different ways. Published SSA rows are
observations; absent rows remain unknown because counts below five are suppressed.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

REQUIRED_COLUMNS = frozenset({"year", "name", "sex", "count"})
ALLOWED_SEX_VALUES = frozenset({"F", "M"})


class AnalyticsError(RuntimeError):
    """Indicate that analytical data cannot be loaded or interpreted safely."""


class AnalyticsInputError(ValueError):
    """Indicate that a caller supplied an unsupported analytical request."""


@dataclass(frozen=True)
class NameSummary:
    """Summarize one name and source sex category across its published history."""

    name: str
    sex: str
    first_year: int
    last_year: int
    years_published: int
    total_applications: int
    peak_count: int
    peak_count_year: int
    best_rank: int
    best_rank_year: int


class BabyNameAnalytics:
    """Provide consistent query operations over normalized baby-name records.

    The constructor computes competition rank and within-category share once. Public
    methods return new DataFrames, preventing callers from mutating shared state.
    """

    def __init__(self, records: pd.DataFrame) -> None:
        """Validate records and precompute rank and share analytical columns.

        Args:
            records: Table containing at least ``year``, ``name``, ``sex``, and
                ``count`` columns.

        Raises:
            AnalyticsError: If required columns or values violate the processed
                dataset contract.

        """
        missing_columns = REQUIRED_COLUMNS - set(records.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise AnalyticsError(f"Processed data is missing required columns: {missing}")

        data = records.loc[:, ["year", "name", "sex", "count"]].copy()
        if data.empty:
            raise AnalyticsError("Processed data contains no records.")
        if data[list(REQUIRED_COLUMNS)].isnull().any().any():
            raise AnalyticsError("Processed data contains null required values.")
        if not set(data["sex"].unique()).issubset(ALLOWED_SEX_VALUES):
            raise AnalyticsError("Processed data contains an unsupported sex value.")
        if (data["count"] <= 0).any():
            raise AnalyticsError("Processed data contains a non-positive count.")
        if data.duplicated(["year", "name", "sex"]).any():
            raise AnalyticsError("Processed data contains duplicate year/name/sex keys.")

        data = data.sort_values(
            ["year", "sex", "count", "name"],
            ascending=[True, True, False, True],
            kind="stable",
            ignore_index=True,
        )
        groups = data.groupby(["year", "sex"], observed=True, sort=False)
        data["rank"] = groups["count"].rank(method="min", ascending=False).astype("int32")
        data["share"] = data["count"] / groups["count"].transform("sum")

        self._data = data
        self._first_year = int(data["year"].min())
        self._last_year = int(data["year"].max())
        self._canonical_names = {
            str(name).casefold(): str(name) for name in data["name"].drop_duplicates()
        }
        self._available_names = tuple(sorted(data["name"].unique(), key=str.casefold))
        self._available_names_by_sex = {
            sex: tuple(sorted(data.loc[data["sex"] == sex, "name"].unique(), key=str.casefold))
            for sex in sorted(ALLOWED_SEX_VALUES)
        }
        self._categories_by_name = {
            str(name): tuple(sorted(group["sex"].unique()))
            for name, group in data.groupby("name", observed=True, sort=False)
        }
        self._annual_totals = self._calculate_annual_totals(data)
        self._annual_totals_by_sex = {
            sex: self._calculate_annual_totals(data.loc[data["sex"] == sex])
            for sex in sorted(ALLOWED_SEX_VALUES)
        }

    @classmethod
    def from_parquet(cls, path: Path) -> BabyNameAnalytics:
        """Load the minimal analytical columns from a processed Parquet artifact."""
        if not path.is_file():
            raise AnalyticsError(f"Processed dataset does not exist: {path}")
        try:
            table = pq.read_table(  # type: ignore[no-untyped-call]
                path, columns=["year", "name", "sex", "count"]
            )
        except (OSError, ValueError) as error:
            raise AnalyticsError(f"Could not read processed dataset: {error}") from error
        return cls(table.to_pandas())

    @property
    def year_range(self) -> tuple[int, int]:
        """Return the inclusive minimum and maximum published years."""
        return self._first_year, self._last_year

    def _validate_year(self, year: int) -> None:
        """Require a year within the loaded dataset's inclusive coverage."""
        if not self._first_year <= year <= self._last_year:
            raise AnalyticsInputError(
                f"Year must be between {self._first_year} and {self._last_year}."
            )

    @staticmethod
    def _validate_sex(sex: str) -> str:
        """Normalize and validate an SSA source sex category."""
        normalized = sex.upper()
        if normalized not in ALLOWED_SEX_VALUES:
            raise AnalyticsInputError("Sex must be 'F' or 'M'.")
        return normalized

    @staticmethod
    def _validate_limit(limit: int) -> None:
        """Prevent empty or unbounded ranked requests."""
        if limit < 1:
            raise AnalyticsInputError("Limit must be at least 1.")

    def _resolve_name(self, name: str) -> str:
        """Resolve case-insensitive user input to the source's canonical spelling."""
        normalized = name.strip().casefold()
        if not normalized or normalized not in self._canonical_names:
            raise AnalyticsInputError(f"Name was not found: {name!r}")
        return self._canonical_names[normalized]

    @staticmethod
    def _calculate_annual_totals(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate immutable-at-boundary annual totals for constructor caches."""
        return (
            data.groupby("year", observed=True, as_index=False)
            .agg(count=("count", "sum"))
            .sort_values("year", ignore_index=True)
        )

    def available_names(self, sex: str | None = None) -> tuple[str, ...]:
        """Return canonical name spellings in case-insensitive alphabetical order."""
        if sex is None:
            return self._available_names
        return self._available_names_by_sex[self._validate_sex(sex)]

    def name_categories(self, name: str) -> tuple[str, ...]:
        """Return source sex categories with published observations for a name."""
        canonical_name = self._resolve_name(name)
        return self._categories_by_name[canonical_name]

    def annual_totals(self, sex: str | None = None) -> pd.DataFrame:
        """Return total published applications per year, optionally for one category."""
        if sex is None:
            return self._annual_totals.copy()
        return self._annual_totals_by_sex[self._validate_sex(sex)].copy()

    def rankings(self, year: int, sex: str, *, limit: int = 10) -> pd.DataFrame:
        """Return the most popular names for one year and source sex category."""
        self._validate_year(year)
        normalized_sex = self._validate_sex(sex)
        self._validate_limit(limit)
        result = self._data.loc[
            (self._data["year"] == year) & (self._data["sex"] == normalized_sex),
            ["rank", "name", "count", "share"],
        ]
        return result.head(limit).reset_index(drop=True).copy()

    def name_history(self, name: str, sex: str | None = None) -> pd.DataFrame:
        """Return every published observation for a name, optionally by sex category."""
        canonical_name = self._resolve_name(name)
        mask = self._data["name"] == canonical_name
        if sex is not None:
            mask &= self._data["sex"] == self._validate_sex(sex)
        result = self._data.loc[
            mask,
            ["year", "name", "sex", "count", "rank", "share"],
        ]
        return result.sort_values(["year", "sex"], ignore_index=True).copy()

    def compare_names(self, names: Iterable[str], sex: str | None = None) -> pd.DataFrame:
        """Return observed histories for two or more distinct names in long form."""
        canonical_names = list(dict.fromkeys(self._resolve_name(name) for name in names))
        if len(canonical_names) < 2:
            raise AnalyticsInputError("Comparison requires at least two distinct names.")
        mask = self._data["name"].isin(canonical_names)
        if sex is not None:
            mask &= self._data["sex"] == self._validate_sex(sex)
        result = self._data.loc[
            mask,
            ["year", "name", "sex", "count", "rank", "share"],
        ]
        return result.sort_values(["year", "name", "sex"], ignore_index=True).copy()

    def name_summary(self, name: str, sex: str) -> NameSummary:
        """Return lifetime totals and peak milestones for one name/category pair."""
        normalized_sex = self._validate_sex(sex)
        history = self.name_history(name, normalized_sex)
        if history.empty:
            canonical_name = self._resolve_name(name)
            raise AnalyticsInputError(
                f"No published observations for {canonical_name}/{normalized_sex}."
            )
        peak_count_row = history.sort_values(
            ["count", "year"], ascending=[False, True], kind="stable"
        ).iloc[0]
        best_rank_row = history.sort_values(
            ["rank", "year"], ascending=[True, True], kind="stable"
        ).iloc[0]
        return NameSummary(
            name=str(history.iloc[0]["name"]),
            sex=normalized_sex,
            first_year=int(history["year"].min()),
            last_year=int(history["year"].max()),
            years_published=int(history["year"].nunique()),
            total_applications=int(history["count"].sum()),
            peak_count=int(peak_count_row["count"]),
            peak_count_year=int(peak_count_row["year"]),
            best_rank=int(best_rank_row["rank"]),
            best_rank_year=int(best_rank_row["year"]),
        )

    def trend_changes(
        self,
        start_year: int,
        end_year: int,
        sex: str,
        *,
        direction: str = "rising",
        limit: int = 10,
    ) -> pd.DataFrame:
        """Rank names published at both endpoints by their change in competition rank.

        A positive ``rank_change`` means a name rose toward rank one. Names absent at
        either endpoint are excluded because suppressed values cannot be assumed zero.
        """
        self._validate_year(start_year)
        self._validate_year(end_year)
        if start_year >= end_year:
            raise AnalyticsInputError("Start year must be earlier than end year.")
        normalized_sex = self._validate_sex(sex)
        self._validate_limit(limit)
        if direction not in {"rising", "falling"}:
            raise AnalyticsInputError("Direction must be 'rising' or 'falling'.")

        columns = ["name", "rank", "count", "share"]
        start = self._data.loc[
            (self._data["year"] == start_year) & (self._data["sex"] == normalized_sex),
            columns,
        ].rename(columns={column: f"start_{column}" for column in columns if column != "name"})
        end = self._data.loc[
            (self._data["year"] == end_year) & (self._data["sex"] == normalized_sex),
            columns,
        ].rename(columns={column: f"end_{column}" for column in columns if column != "name"})
        result = start.merge(end, on="name", how="inner", validate="one_to_one")
        result["rank_change"] = result["start_rank"] - result["end_rank"]
        result["count_change"] = result["end_count"] - result["start_count"]
        result["share_change"] = result["end_share"] - result["start_share"]
        ascending = direction == "falling"
        result = result.sort_values(
            ["rank_change", "share_change", "name"],
            ascending=[ascending, ascending, True],
            kind="stable",
        )
        return result.head(limit).reset_index(drop=True).copy()

    def unisex_names(self, year: int, *, limit: int = 10) -> pd.DataFrame:
        """Return names published in both categories, ordered by combined count."""
        self._validate_year(year)
        self._validate_limit(limit)
        annual = self._data.loc[self._data["year"] == year, ["name", "sex", "count"]]
        counts = annual.pivot(index="name", columns="sex", values="count").dropna(subset=["F", "M"])
        counts = counts.rename(columns={"F": "female_count", "M": "male_count"})
        counts["total_count"] = counts["female_count"] + counts["male_count"]
        counts["female_share"] = counts["female_count"] / counts["total_count"]
        counts["balance_score"] = counts[["female_count", "male_count"]].min(axis=1) / counts[
            ["female_count", "male_count"]
        ].max(axis=1)
        return (
            counts.reset_index()
            .sort_values(["total_count", "name"], ascending=[False, True], kind="stable")
            .head(limit)
            .reset_index(drop=True)
        )
