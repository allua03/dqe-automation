"""Helpers for comparing the Plotly HTML report with its Parquet source."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
from time import monotonic, sleep
from typing import Any

import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


_REPORT_COLUMNS = ["facility_type", "visit_date", "avg_time_spent"]
_HEADER_TO_COLUMN = {
	"facility type": "facility_type",
	"visit date": "visit_date",
	"average time spent": "avg_time_spent",
}


def path_to_file_url(file_path: str) -> str:
	"""Convert a local report path into a browser-safe file URL."""
	path = Path(file_path).expanduser().resolve()
	if not path.is_file():
		raise FileNotFoundError(f"HTML report does not exist: {path}")
	return path.as_uri()


def read_html_table_to_dataframe(table: WebElement) -> pd.DataFrame:
	"""Extract the visible Plotly SVG table represented by ``table``."""
	columns = table.find_elements(By.CSS_SELECTOR, ".y-column")
	if not columns:
		raise ValueError("The located element contains no Plotly table columns.")

	headers: list[str] = []
	values_by_column: list[list[str]] = []
	for column in columns:
		try:
			header = column.find_element(By.ID, "header").text.strip()
		except NoSuchElementException:
			header = ""
		canonical_header = _HEADER_TO_COLUMN.get(header.casefold(), header.strip())
		headers.append(canonical_header)
		cell_texts = [cell.text.strip() for cell in column.find_elements(By.CSS_SELECTOR, ".cell-text")]
		values_by_column.append([value for value in cell_texts if value != header])

	if any(not header for header in headers):
		raise ValueError(f"Could not read all table headers: {headers}")
	if len(set(headers)) != len(headers):
		raise ValueError(f"Duplicate table headers found: {headers}")

	row_count = max((len(values) for values in values_by_column), default=0)
	rows = [
		{
			header: values[row_index] if row_index < len(values) else ""
			for header, values in zip(headers, values_by_column)
		}
		for row_index in range(row_count)
	]
	frame = pd.DataFrame(rows, columns=headers)
	missing_columns = set(_REPORT_COLUMNS).difference(frame.columns)
	if missing_columns:
		raise ValueError(
			"The report table is missing expected columns: "
			+ ", ".join(sorted(missing_columns))
		)
	return frame[_REPORT_COLUMNS]


def read_stable_html_table_to_dataframe(
	table: WebElement,
	timeout_seconds: float = 15,
	stable_reads: int = 4,
	poll_interval: float = 0.25,
) -> pd.DataFrame:
	"""Wait for Plotly's SVG table to stop changing, then return its data."""
	deadline = monotonic() + timeout_seconds
	previous: pd.DataFrame | None = None
	consecutive_matches = 0
	while monotonic() < deadline:
		current = read_html_table_to_dataframe(table)
		if previous is not None and current.equals(previous):
			consecutive_matches += 1
			if consecutive_matches >= stable_reads - 1:
				return current
		else:
			consecutive_matches = 0
		previous = current
		sleep(poll_interval)
	raise TimeoutError(
		f"Plotly report table did not stabilize within {timeout_seconds} seconds."
	)


def _parse_date(value: str, argument_name: str) -> pd.Timestamp:
	try:
		parsed = datetime.strptime(value, "%Y-%m-%d")
	except ValueError as exc:
		raise ValueError(f"{argument_name} must use YYYY-MM-DD format; got {value!r}.") from exc
	return pd.Timestamp(parsed.date())


def read_parquet_dataset(
	parquet_folder: str,
	filter_date: str = "",
	start_date: str = "",
	end_date: str = "",
) -> pd.DataFrame:
	"""Read a partitioned Parquet dataset and optionally filter by visit date."""
	folder = Path(parquet_folder).expanduser().resolve()
	if not folder.is_dir():
		raise FileNotFoundError(f"Parquet dataset folder does not exist: {folder}")
	if not any(folder.rglob("*.parquet")):
		raise FileNotFoundError(f"No Parquet files found under: {folder}")

	frame = pd.read_parquet(folder)
	missing_columns = set(_REPORT_COLUMNS).difference(frame.columns)
	if missing_columns:
		raise ValueError(
			"The Parquet dataset is missing expected columns: "
			+ ", ".join(sorted(missing_columns))
		)

	frame = frame[_REPORT_COLUMNS].copy()
	frame["visit_date"] = pd.to_datetime(frame["visit_date"], errors="raise").dt.normalize()
	if filter_date:
		selected_date = _parse_date(filter_date, "filter_date")
		frame = frame.loc[frame["visit_date"].eq(selected_date)]
	else:
		if bool(start_date) != bool(end_date):
			raise ValueError("start_date and end_date must either both be set or both be empty.")
		if start_date and end_date:
			first = _parse_date(start_date, "start_date")
			last = _parse_date(end_date, "end_date")
			if first > last:
				raise ValueError("start_date must be on or before end_date.")
			frame = frame.loc[frame["visit_date"].between(first, last, inclusive="both")]
	return frame.reset_index(drop=True)


def filter_dataframe_by_date(frame: pd.DataFrame, filter_date: str) -> pd.DataFrame:
	"""Keep rows whose ``visit_date`` equals the requested ISO date."""
	if "visit_date" not in frame.columns:
		raise ValueError("The DataFrame has no 'visit_date' column.")
	selected_date = _parse_date(filter_date, "filter_date")
	dates = pd.to_datetime(frame["visit_date"], errors="raise").dt.normalize()
	return frame.loc[dates.eq(selected_date)].reset_index(drop=True)


def get_dataframe_date_range(frame: pd.DataFrame) -> tuple[str, str]:
	"""Return the minimum and maximum ISO visit dates represented in a frame."""
	if frame.empty or "visit_date" not in frame.columns:
		raise ValueError("Cannot determine a visit-date range from an empty or invalid report table.")
	dates = pd.to_datetime(frame["visit_date"], errors="raise").dt.normalize()
	return dates.min().strftime("%Y-%m-%d"), dates.max().strftime("%Y-%m-%d")


def _normalize_for_comparison(
	report_frame: pd.DataFrame, parquet_frame: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
	report = report_frame.copy()
	parquet = parquet_frame.copy()
	if set(report.columns) != set(parquet.columns):
		return report, parquet

	report = report[parquet.columns]
	for column in parquet.columns:
		if pd.api.types.is_datetime64_any_dtype(parquet[column]):
			report[column] = pd.to_datetime(report[column], errors="raise").dt.normalize()
			parquet[column] = pd.to_datetime(parquet[column], errors="raise").dt.normalize()
		elif pd.api.types.is_numeric_dtype(parquet[column]):
			cleaned = report[column].astype("string").str.replace(",", "", regex=False)
			report[column] = pd.to_numeric(cleaned, errors="raise")
		else:
			report[column] = report[column].astype("string").str.strip()
			parquet[column] = parquet[column].astype("string").str.strip()
	return report, parquet


def _row_counter(frame: pd.DataFrame) -> Counter[tuple[Any, ...]]:
	def safe_value(value: Any) -> Any:
		if pd.isna(value):
			return None
		if isinstance(value, pd.Timestamp):
			return value.strftime("%Y-%m-%d")
		if hasattr(value, "item"):
			return value.item()
		return value

	return Counter(tuple(safe_value(value) for value in row) for row in frame.itertuples(index=False, name=None))


def compare_dataframes(
	report_frame: pd.DataFrame, parquet_frame: pd.DataFrame
) -> tuple[bool, str]:
	"""Compare row content independent of ordering and return actionable differences."""
	report, parquet = _normalize_for_comparison(report_frame, parquet_frame)
	report_columns = list(report.columns)
	parquet_columns = list(parquet.columns)
	if set(report_columns) != set(parquet_columns):
		missing = sorted(set(parquet_columns) - set(report_columns))
		extra = sorted(set(report_columns) - set(parquet_columns))
		return False, f"Column mismatch. Missing from report: {missing}; extra in report: {extra}."
	if report.empty and parquet.empty:
		return False, "Both sources contain no rows to compare."

	report = report[parquet_columns]
	report_rows = _row_counter(report)
	parquet_rows = _row_counter(parquet)
	report_only = report_rows - parquet_rows
	parquet_only = parquet_rows - report_rows
	if not report_only and not parquet_only:
		return True, ""

	differences = [
		f"Row counts: report={len(report)}, Parquet={len(parquet)}; row content differs."
	]
	if report_only:
		differences.append(f"Rows only in HTML report: {list(report_only.items())}")
	if parquet_only:
		differences.append(f"Rows only in Parquet dataset: {list(parquet_only.items())}")
	return False, "\n".join(differences)
