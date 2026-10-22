"""Reusable assertions for validating source and target DataFrames."""

from typing import List, Optional

import pandas as pd
from pandas.testing import assert_frame_equal


class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is intended to be used in a PyTest-based testing framework to validate
    the quality of data in DataFrames. Each method performs a specific data quality
    check and uses assertions to ensure that the data meets the expected conditions.
    """

    @staticmethod
    def check_duplicates(df: pd.DataFrame, column_names: Optional[List[str]] = None) -> None:
        """Assert there are no duplicate full rows or duplicate key values."""
        columns = column_names or list(df.columns)
        missing = [column for column in columns if column not in df.columns]
        assert not missing, "Duplicate check references missing columns: {}".format(missing)

        duplicates = df[df.duplicated(subset=columns, keep=False)]
        assert duplicates.empty, (
            "Found {} duplicate row(s) for columns {}. Sample: {}".format(
                len(duplicates), columns, duplicates.head(10).to_dict(orient="records")
            )
        )

    @staticmethod
    def check_count(df_expected: pd.DataFrame, df_actual: pd.DataFrame) -> None:
        """Assert that the expected and actual datasets have equal row counts."""
        expected_count = len(df_expected)
        actual_count = len(df_actual)
        assert expected_count == actual_count, (
            "Row count mismatch: expected {}, actual {}".format(
                expected_count, actual_count
            )
        )

    @staticmethod
    def check_data_completeness(
        df_expected: pd.DataFrame, df_actual: pd.DataFrame
    ) -> None:
        """Assert equal columns and row values, ignoring row order."""
        expected_columns = list(df_expected.columns)
        actual_columns = list(df_actual.columns)
        assert set(expected_columns) == set(actual_columns), (
            "Column mismatch: expected {}, actual {}".format(
                expected_columns, actual_columns
            )
        )

        columns = sorted(expected_columns)
        expected = df_expected.loc[:, columns].sort_values(
            by=columns, kind="mergesort", na_position="first"
        ).reset_index(drop=True)
        actual = df_actual.loc[:, columns].sort_values(
            by=columns, kind="mergesort", na_position="first"
        ).reset_index(drop=True)
        try:
            assert_frame_equal(
                expected,
                actual,
                check_dtype=False,
                check_exact=False,
                rtol=1e-6,
                atol=1e-8,
            )
        except AssertionError as exc:
            raise AssertionError(
                "Source-to-target data mismatch (row order ignored): {}".format(exc)
            ) from exc

    @staticmethod
    def check_dataset_is_not_empty(df: pd.DataFrame) -> None:
        """Assert the target dataset contains at least one row."""
        assert not df.empty, "Target dataset is empty"

    @staticmethod
    def check_not_null_values(
        df: pd.DataFrame, column_names: Optional[List[str]] = None
    ) -> None:
        """Assert that each named column exists and contains no null values."""
        columns = column_names or list(df.columns)
        missing = [column for column in columns if column not in df.columns]
        assert not missing, "Not-null check references missing columns: {}".format(missing)

        null_counts = df[columns].isna().sum()
        null_counts = null_counts[null_counts > 0].to_dict()
        assert not null_counts, "Null values found by column: {}".format(null_counts)

    @staticmethod
    def check_non_negative_values(df: pd.DataFrame, column_name: str) -> None:
        """Assert that a mapped measure contains no negative values."""
        assert column_name in df.columns, (
            "Non-negative check references missing column: {}".format(column_name)
        )
        negative_values = df.loc[df[column_name] < 0, column_name]
        assert negative_values.empty, (
            "Negative values found in {}: {}".format(
                column_name, negative_values.head(10).tolist()
            )
        )
