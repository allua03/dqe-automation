import logging
from pathlib import Path

import pandas as pd
import pytest
from reportportal_client import RPLogger


@pytest.fixture(scope="session")
def csv_data():
	"""Load the homework CSV once for the test session."""
	data_path = Path(__file__).resolve().parents[1] / "src" / "data" / "data.csv"
	return pd.read_csv(data_path)


@pytest.fixture(scope="session")
def required_columns():
	return {"id", "name", "age", "email", "is_active"}


@pytest.fixture(scope="session")
def rp_logger():
	"""Provide a logger whose messages are attached to the ReportPortal item."""
	logging.setLoggerClass(RPLogger)
	logger = logging.getLogger("pytest-introduction")
	logger.setLevel(logging.INFO)
	return logger
