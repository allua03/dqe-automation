from pathlib import Path
import pytest
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "src" / "data" / "data.csv"

@pytest.fixture(scope="session")
def path_to_file():
    return DATA_FILE


# Fixture to read the CSV file

@pytest.fixture(scope="session")
def read_csv(path_to_file):
    return pd.read_csv(path_to_file)


# Fixture to validate the schema of the file

@pytest.fixture(scope="session")
def validate_schema():
    def _validate(actual_schema, expected_schema):
        assert list(actual_schema) == list(expected_schema), (
            f"Schema mismatch: expected {list(expected_schema)}, got {list(actual_schema)}"
        )
    return _validate


# Pytest hook to mark unmarked tests with a custom mark

def pytest_collection_modifyitems(items):
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unmarked)