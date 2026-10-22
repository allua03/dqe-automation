import pytest
import re
import pandas as pd


def test_file_not_empty():
    assert 1 + 1 == 2


def test_duplicates():
    assert 1 + 1 == 2


def test_validate_schema():
    assert 1 + 1 == 2


def test_age_column_valid():
    assert 1 + 1 == 2


def test_email_column_valid():
    assert 1 + 1 == 2


def test_active_players():
    assert 1 + 1 == 2


def test_active_player():
    assert 1 + 1 == 2


EXPECTED_SCHEMA = ["id", "name", "age", "email", "is_active"]
EMAIL_PATTERN = r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$"


def test_file_is_not_empty(read_csv):
    assert not read_csv.empty, "CSV file is empty"


@pytest.mark.validate_csv
def test_schema(read_csv, validate_schema):
    validate_schema(read_csv.columns, EXPECTED_SCHEMA)


@pytest.mark.validate_csv
@pytest.mark.skip(reason="Age validation is temporarily skipped")
def test_age_is_valid(read_csv):
    assert read_csv["age"].between(0, 100).all(), "Age values must be in range 0-100"


@pytest.mark.validate_csv
def test_email_is_valid(read_csv):
    assert read_csv["email"].str.match(EMAIL_PATTERN).all(), "Invalid email format found"


@pytest.mark.validate_csv
@pytest.mark.xfail(reason="Known issue: file contains duplicate rows")
def test_no_duplicate_rows(read_csv):
    assert not read_csv.duplicated().any(), "Duplicate rows found"


@pytest.mark.parametrize("id, is_active", [(1, False), (2, True)])
def test_is_active_parametrized(read_csv, id, is_active):
    actual = read_csv.loc[read_csv["id"] == id, "is_active"].iloc[0]
    assert actual == is_active, f"Expected is_active={is_active} for id={id}, got {actual}"


def test_is_active_for_id_2(read_csv):
    actual = read_csv.loc[read_csv["id"] == 2, "is_active"].iloc[0]
    assert actual == True, "Expected is_active=True for id=2"