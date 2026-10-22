import pandas as pd


class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is intended to be used in a PyTest-based testing framework to validate
    the quality of data in DataFrames. Each method performs a specific data quality
    check and uses assertions to ensure that the data meets the expected conditions.
    """

    @staticmethod
    def check_dataset_is_not_empty(df: pd.DataFrame) -> None:
        assert df is not None and not df.empty, "Dataset is empty or was not loaded."

    @staticmethod
    def check_count(df_expected: pd.DataFrame, df_actual: pd.DataFrame) -> None:
        expected_count = len(df_expected)
        actual_count = len(df_actual)
        assert expected_count == actual_count, (
            f"Row count mismatch: expected {expected_count} rows, got {actual_count} rows."
        )

    @staticmethod
    def check_data_completeness(df_expected: pd.DataFrame, df_actual: pd.DataFrame) -> None:
        common_columns = [c for c in df_expected.columns if c in df_actual.columns]
        assert common_columns, (
            f"No common columns between expected {list(df_expected.columns)} "
            f"and actual {list(df_actual.columns)}."
        )

        expected_sorted = (
            df_expected[common_columns]
            .sort_values(by=common_columns)
            .reset_index(drop=True)
        )
        actual_sorted = (
            df_actual[common_columns]
            .sort_values(by=common_columns)
            .reset_index(drop=True)
        )

        diff = pd.concat([expected_sorted, actual_sorted]).drop_duplicates(keep=False)
        preview = diff.head(20).to_string()
        more = f"\n... and {len(diff) - 20} more row(s)" if len(diff) > 20 else ""
        assert diff.empty, (
            f"Data completeness mismatch between expected and actual datasets: {len(diff)} "
            f"mismatched row(s) (from either side). First 20:\n{preview}{more}"
        )

    @staticmethod
    def check_duplicates(df: pd.DataFrame, column_names=None) -> None:
        subset = column_names if column_names else None
        duplicated_mask = df.duplicated(subset=subset, keep=False)
        duplicates = df[duplicated_mask]
        preview = duplicates.head(20).to_string()
        more = f"\n... and {len(duplicates) - 20} more row(s)" if len(duplicates) > 20 else ""
        assert duplicates.empty, (
            f"Found {len(duplicates)} duplicate row(s) "
            f"(subset={subset or 'all columns'}). First 20:\n{preview}{more}"
        )

    @staticmethod
    def check_not_null_values(df: pd.DataFrame, column_names) -> None:
        missing_columns = [c for c in column_names if c not in df.columns]
        assert not missing_columns, f"Columns not found in dataset: {missing_columns}"

        for column in column_names:
            null_rows = df[df[column].isnull()]
            assert null_rows.empty, (
                f"Column '{column}' contains {len(null_rows)} null value(s) "
                f"at index: {null_rows.index.tolist()}"
            )
