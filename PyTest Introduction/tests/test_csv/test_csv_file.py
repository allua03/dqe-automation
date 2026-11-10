import re


def test_file_not_empty(csv_data, rp_logger):
    rp_logger.info("Checking that the source CSV contains data")
    assert not csv_data.empty, "CSV file is empty"


def test_duplicates(csv_data, rp_logger):
    duplicates = csv_data[csv_data.duplicated()]
    rp_logger.warning("Duplicate CSV rows: %s", duplicates.to_dict("records"))
    assert duplicates.empty, "CSV contains duplicate rows"


def test_validate_schema(csv_data, required_columns, rp_logger):
    missing_columns = required_columns - set(csv_data.columns)
    rp_logger.info("CSV columns: %s", list(csv_data.columns))
    assert not missing_columns, f"Missing required columns: {sorted(missing_columns)}"


def test_age_column_valid(csv_data):
    ages = csv_data["age"]
    assert ages.notna().all(), "Age column contains empty values"
    assert (ages >= 0).all(), "Age column contains negative values"


def test_email_column_valid(csv_data, rp_logger):
    email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    invalid_emails = csv_data.loc[
        ~csv_data["email"].astype(str).str.match(email_pattern), "email"
    ].tolist()
    rp_logger.warning("Invalid email values: %s", invalid_emails)
    assert not invalid_emails, f"Invalid email values: {invalid_emails}"


def test_active_players(csv_data):
    assert csv_data["is_active"].sum() > 0, "No active players found"


def test_active_player(csv_data):
    active_players = csv_data.loc[csv_data["is_active"]]
    assert not active_players.empty, "No active player records found"
    assert (active_players["age"] > 0).all(), "An active player has an invalid age"
