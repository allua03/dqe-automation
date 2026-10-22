"""
Description: Data Quality checks for patient_sum_treatment_cost_per_facility_type.
Requirement(s): Mapping-based source-to-target validation.
Author(s): DQ Engineering Team
"""

import pytest


@pytest.fixture(scope="module")
def source_data(db_connection):
    source_query = """
    SELECT
        f.facility_type,
        CONCAT(p.first_name, ' ', p.last_name) AS full_name,
        SUM(v.treatment_cost) AS sum_treatment_cost
    FROM visits v
    JOIN facilities f ON f.id = v.facility_id
    JOIN patients p ON p.id = v.patient_id
    GROUP BY f.facility_type, p.first_name, p.last_name;
    """
    return db_connection.get_data_sql(source_query)


@pytest.fixture(scope="module")
def target_data(parquet_reader):
    target_path = "/parquet_data/patient_sum_treatment_cost_per_facility_type"
    return parquet_reader.process(target_path, include_subfolders=True)


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.dataset_patient_sum_treatment_cost_per_facility_type
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
@pytest.mark.dataset_patient_sum_treatment_cost_per_facility_type
def test_check_data_completeness(source_data, target_data, data_quality_library):
    data_quality_library.check_data_completeness(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.dataset_patient_sum_treatment_cost_per_facility_type
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.dataset_patient_sum_treatment_cost_per_facility_type
def test_check_uniqueness(target_data, data_quality_library):
    data_quality_library.check_duplicates(target_data, ["facility_type", "full_name"])


@pytest.mark.parquet_data
@pytest.mark.dataset_patient_sum_treatment_cost_per_facility_type
def test_check_not_null_values(target_data, data_quality_library):
    data_quality_library.check_not_null_values(
        target_data, ["facility_type", "full_name", "sum_treatment_cost"]
    )


@pytest.mark.parquet_data
@pytest.mark.dataset_patient_sum_treatment_cost_per_facility_type
def test_check_treatment_cost_is_non_negative(target_data, data_quality_library):
    data_quality_library.check_non_negative_values(target_data, "sum_treatment_cost")