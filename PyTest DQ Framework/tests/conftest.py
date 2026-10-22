"""Pytest options and session-scoped framework fixtures."""

import os

import pytest
from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.data_quality.data_quality_validation_library import DataQualityLibrary
from src.connectors.file_system.parquet_reader import ParquetReader

def pytest_addoption(parser):
    """Register database options; environment variables may supply defaults."""
    parser.addoption(
        "--db_host", action="store", default=os.getenv("DB_HOST", "localhost")
    )
    parser.addoption(
        "--db_port", action="store", type=int, default=int(os.getenv("DB_PORT", "5434"))
    )
    parser.addoption(
        "--db_name", action="store", default=os.getenv("DB_NAME", "mydatabase")
    )
    parser.addoption("--db_user", action="store", default=os.getenv("DB_USER"))
    parser.addoption("--db_password", action="store", default=os.getenv("DB_PASSWORD"))

@pytest.fixture(scope='session')
def db_connection(request):
    """Open one PostgreSQL connection for tests that request source data."""
    db_user = request.config.getoption("--db_user")
    db_password = request.config.getoption("--db_password")
    if not db_user or not db_password:
        pytest.fail(
            "Database credentials are required; set --db_user/--db_password "
            "or DB_USER/DB_PASSWORD.",
            pytrace=False,
        )

    connector = PostgresConnectorContextManager(
        db_host=request.config.getoption("--db_host"),
        db_port=request.config.getoption("--db_port"),
        db_name=request.config.getoption("--db_name"),
        db_user=db_user,
        db_password=db_password,
    )
    try:
        connector.__enter__()
    except Exception as exc:
        pytest.fail("Failed to connect to PostgreSQL: {}".format(exc), pytrace=False)
    try:
        yield connector
    finally:
        connector.__exit__(None, None, None)


@pytest.fixture(scope="session")
def parquet_reader():
    """Provide the Parquet dataset reader."""
    return ParquetReader()


@pytest.fixture(scope="session")
def data_quality_library():
    """Provide the reusable data quality assertions."""
    return DataQualityLibrary()


def pytest_configure(config):
    """Register project markers for pytest and IDE discovery."""
    config.addinivalue_line("markers", "parquet_data: source-to-Parquet DQ checks")
    config.addinivalue_line("markers", "smoke: fast dataset availability check")
    config.addinivalue_line("markers", "example: framework usage examples")
    config.addinivalue_line(
        "markers", "facility_name_min_time_spent_per_visit_date: dataset checks"
    )
    config.addinivalue_line(
        "markers", "facility_type_avg_time_spent_per_visit_date: dataset checks"
    )
    config.addinivalue_line(
        "markers", "dataset_patient_sum_treatment_cost_per_facility_type: dataset checks"
    )