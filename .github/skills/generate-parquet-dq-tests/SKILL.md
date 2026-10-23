---
name: generate-parquet-dq-tests
description: >-
  Creates parquet_files test modules from docs/parquet-aggregated-data-mapping.md
  for the PyTest DQ Framework. Invoke when asked to generate a Data Quality test
  module for a named Parquet dataset under PyTest DQ Framework/tests/dq checks/parquet_files/.
  Refuses to run without an existing framework (connectors, conftest, data_quality
  library) and refuses to embed expected SQL for a dataset anywhere in this file.
disable-model-invocation: true
---

# Generate Parquet DQ tests

Complete this skill as **Step 2** of the PyTest DQ assignment. Read first:

- `PyTest DQ Framework/docs/test-automation-strategy.md` — **§5 Skill contract**, **§6 Test design standard**
- `docs/parquet-aggregated-data-mapping.md` — dataset definitions (expected SQL comes from here)

**Do not** paste expected SQL for the three named datasets into this skill.  
**Do not** instruct the agent to copy SQL from `data_dev/`.

When finished, every `TODO` below must be replaced. Run the **Skill review** checklist before using the skill to generate tests.

## When this skill applies

Use this skill when asked to generate (or regenerate) one Parquet dataset's DQ test module for the `tafordqenetwork` pipeline. The framework must already exist: `src/connectors/postgres/postgres_connector.py`, `src/connectors/file_system/parquet_reader.py`, `src/data_quality/data_quality_validation_library.py`, `tests/conftest.py`, `tests/pytest.ini`. Allowed output path is exactly one file per invocation:
`PyTest DQ Framework/tests/dq checks/parquet_files/test_<dataset_name>.py`.
Refuse (stop and ask) if: the dataset name is not present in `docs/parquet-aggregated-data-mapping.md`; the framework files above are missing; or the request asks to embed/copy SQL from `data_dev/`.

## Inputs you must have

- **Dataset name** — must match a section heading in `docs/parquet-aggregated-data-mapping.md` and the Parquet folder name under `/parquet_data/<dataset_name>`.
- **Mapping row set** for that dataset: target columns, transformation, source table, source column, filters, partitioning — read directly from the mapping file, nothing else.
- **Author / requirement id** for the module docstring (ask the user if not given; use a placeholder like `TICKET-TBD` and the current author name only if explicitly supplied).

If the mapping section for the dataset is missing, stop and report that the mapping must be extended first — do not invent columns or joins.
**Forbidden sources:** `data_dev/queries.py`, `data_dev/src/data/parquet_loader.py`, any other ETL implementation SQL, and `tests/test_examples.py` (sample only, fixtures are swapped there).

## Hard rules

1. File path is exactly `PyTest DQ Framework/tests/dq checks/parquet_files/test_<dataset_name>.py` — one dataset per file.
2. `source_data` fixture uses `db_connection` (Postgres = source/expected). `target_data` fixture uses `parquet_reader` (Parquet = target/actual). Never swap these.
3. Expected SQL in `source_data` is derived **only** from `docs/parquet-aggregated-data-mapping.md` for this dataset — no SQL for the three named datasets may appear in this `SKILL.md` file itself.
4. Do not open, read, or reference `data_dev/` to build the expected query.
5. Do not add `UNION`, extra `WHERE`, `CASE`, or sign flips unless the mapping states them. No filters are added unless the mapping's "Filters" row is non-empty.
6. Tests call only the existing `DataQualityLibrary` methods (`check_dataset_is_not_empty`, `check_data_completeness`, `check_count`, `check_duplicates`, `check_not_null_values`). Do not reimplement comparison logic inside the test body.
7. Markers on every test: `@pytest.mark.parquet_data` and `@pytest.mark.<dataset_name>`. Add `@pytest.mark.smoke` only on `test_check_dataset_is_not_empty`.
8. `check_not_null_values` column list = every mapped target/output column for that dataset (from the mapping table's "Target column" rows).
9. `target_path` is `/parquet_data/<dataset_name>` with `include_subfolders=True`.
10. Do not modify framework library/connector/conftest code while generating a test module.

## Workflow

1. Read the dataset's section in `docs/parquet-aggregated-data-mapping.md`: target columns, transformations, source tables/columns, filters, partitioning.
2. Derive the expected SQL per "SQL derivation" below; alias every column to the mapping/Parquet name.
3. Copy the module template, substitute `<dataset_name>`, the derived `source_query`, and the not-null column list.
4. Keep test order: smoke → completeness → count → uniqueness → not-null, as in the template.
5. Save to `PyTest DQ Framework/tests/dq checks/parquet_files/test_<dataset_name>.py`. Do not touch other files.

## Template

```python
"""
Description: Data Quality checks for <dataset_name> dataset.
Requirement(s): <requirement id>
Author(s): <author>
"""

import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
    source_query = """
    -- expected query derived from mapping (grain + measures + joins)
    """
    return db_connection.get_data_sql(source_query)


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    target_path = '/parquet_data/<dataset_name>'
    return parquet_reader.process(target_path, include_subfolders=True)


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.<dataset_name>
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_data_completeness(source_data, target_data, data_quality_library):
    data_quality_library.check_data_completeness(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_uniqueness(target_data, data_quality_library):
    data_quality_library.check_duplicates(target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_not_null_values(target_data, data_quality_library):
    data_quality_library.check_not_null_values(target_data, ['<col_1>', '<col_2>', '<col_3>'])
```

## SQL derivation (generic)

1. Identify the 3NF source tables and join keys from the mapping's "Source" column (e.g. `visits` joined to `facilities` and/or `patients` on their foreign keys).
2. List the **dimensions** (grouping/grain columns) — every mapping row marked "grouping" in Comments, in the order given by the mapping.
3. List the **measures** — apply exactly the transformation stated in the mapping's "Transformation" column (e.g. `MIN(...)`, `AVG(...)` with stated rounding, `SUM(...)`, string concatenation with the stated separator). Do not add rounding, casts, or aggregation not written in the mapping.
4. Alias every selected column to the mapping's "Target column" name so the query output matches the Parquet schema.
5. Add a `WHERE` clause only if the mapping's "Filters" row for that dataset is non-empty; otherwise omit it.
6. Add `GROUP BY` over the dimension columns identified in step 2.
7. Stop once the query mirrors the mapping. Do not adjust it to match a parquet preview and do not consult ETL source code.

## After generation

- Do not run pytest automatically unless the user asks for a run.
- Never rewrite the derived expected SQL to force a passing test; if a test fails, that is a signal to report as mapping-vs-parquet, not a reason to edit the query.
- Do not add, remove, or rename test types beyond the five in the template.

---

## Skill review (self-check before Step 3)

Reject your own skill if any of these are true:

- [ ] Contains concrete expected SQL for `facility_name_min_time_spent_per_visit_date`, `facility_type_avg_time_spent_per_visit_date`, or `patient_sum_treatment_cost_per_facility_type`
- [ ] Tells the agent to use `data_dev/` or parquet loader SQL
- [ ] Omits completeness, count, uniqueness, or not-null
- [ ] Swaps Postgres vs Parquet fixtures or generates trivial always-pass checks
- [ ] Any section still says `TODO`

