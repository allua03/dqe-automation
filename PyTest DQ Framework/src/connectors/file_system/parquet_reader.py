import glob
import os

import pandas as pd
from pandas import DataFrame


class ParquetReader:
    """
    Reads Parquet datasets from the local file system.

    Supports plain and Hive-partitioned datasets (directories containing
    `key=value` sub-folders), as written by the `data_dev` pipeline.
    """

    def process(self, target_path: str, include_subfolders: bool = False) -> DataFrame:
        """
        Read a Parquet dataset into a DataFrame.

        Args:
            target_path: Path to a `.parquet` file or a dataset directory.
            include_subfolders: When True, recursively read partitioned
                sub-folders and expose partition columns in the result.

        Returns:
            DataFrame with the dataset content.
        """
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Parquet target path does not exist: {target_path}")

        if os.path.isfile(target_path):
            return pd.read_parquet(target_path, engine="pyarrow")

        if include_subfolders:
            return pd.read_parquet(target_path, engine="pyarrow")

        files = glob.glob(os.path.join(target_path, "*.parquet"))
        if not files:
            raise FileNotFoundError(f"No parquet files found directly under: {target_path}")
        return pd.concat((pd.read_parquet(f, engine="pyarrow") for f in files), ignore_index=True)
