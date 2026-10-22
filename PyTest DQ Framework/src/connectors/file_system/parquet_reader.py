"""Read Parquet datasets, including files nested under partition directories."""

from pathlib import Path
from typing import Union

import pandas as pd
import pyarrow.dataset as ds


class ParquetReader:
	"""Load a Parquet file or dataset directory as a pandas DataFrame."""

	def process(
		self, target_path: Union[str, Path], include_subfolders: bool = False
	) -> pd.DataFrame:
		path = Path(target_path)
		if not path.exists():
			raise FileNotFoundError("Parquet path does not exist: {}".format(path))

		if path.is_file():
			parquet_source = str(path)
		elif include_subfolders:
			parquet_source = str(path)
		else:
			parquet_files = list(path.glob("*.parquet")) + list(path.glob("*.pq"))
			if not parquet_files:
				raise FileNotFoundError(
					"No top-level Parquet files found in: {}".format(path)
				)
			parquet_source = [str(file_path) for file_path in parquet_files]

		try:
			# Partition directory names are storage metadata, not mapped columns.
			dataset = ds.dataset(parquet_source, format="parquet", partitioning=None)
			return dataset.to_table().to_pandas()
		except (OSError, ValueError) as exc:
			raise ValueError(
				"Unable to read Parquet dataset at {}: {}".format(path, exc)
			) from exc
