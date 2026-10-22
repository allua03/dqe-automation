---
name: generate-parquet-dq-tests
description: >-
  Generates one PyTest DQ module for a Parquet dataset using
  docs/parquet-aggregated-data-mapping.md as the sole expected-transformation
  source. Invoke after the framework is implemented; refuses framework, Jenkins,
  fixture, or connector changes and never derives expected SQL from ETL code.
disable-model-invocation: true
---

# Generate Parquet DQ tests

Complete this skill as **Step 2** of the PyTest DQ assignment. Read first:

- `PyTest DQ Framework/docs/test-automation-strategy.md` — **§5 Skill contract**, **§6 Test design standard**
- `docs/parquet-aggregated-data-mapping.md` — dataset definitions (expected SQL comes from here)

**Do not** paste expected SQL for the three named datasets into this skill.  
**Do not** instruct the agent to copy SQL from `data_dev/`.

Before using the skill to generate tests, replace all template placeholders and run the **Skill review** checklist.

## When this skill applies

Use this skill only when explicitly invoked to generate or update a dataset-level
Parquet DQ test. The framework connectors, fixtures, pytest configuration,
reusable validation library, and Jenkins pipeline must already exist. The only
allowed output is one module at
`PyTest DQ Framework/tests/dq checks/parquet_files/test_<dataset_name>.py`.
Do not use this skill to edit framework code, pipeline code, credentials, or
Jenkins configuration. If a required framework API is missing, stop and report
the gap instead of silently changing the framework.

## Inputs you must have

Require a dataset folder name, its complete entry in
`docs/parquet-aggregated-data-mapping.md`, and the author/requirement metadata
for the module header. Read the mapping entry for target columns, source tables
and columns, joins, grouping grain, measures, filters, and explicit constraints.
If the dataset or any required transformation detail is absent or ambiguous,
stop and ask for clarification; do not infer it from generated Parquet data.
The mapping is the only source for expected transformation logic. Do not read
`data_dev/` or inspect pipeline SQL to construct or revise expected queries.

## Hard rules

1. Create exactly one test module for the requested dataset, at the path above;
  do not combine datasets.
2. Use `db_connection` as the expected/source fixture and
  `parquet_reader` as the actual/target fixture. Never reverse these roles.
3. Derive expected SQL solely from that dataset's mapping entry. Include only
  mapped joins, dimensions, measures, aliases, rounding, and filters. Do not
  add `UNION`, extra `WHERE`, `CASE`, sign changes, or other ETL behavior not
  stated in the mapping. Keep expected aliases and output columns aligned with
  the mapping.
4. Keep this skill dataset-agnostic: do not embed concrete SQL or expected
  results for any named dataset here.
5. Load `/parquet_data/<dataset_name>` with
  `include_subfolders=True`; partition helper columns are not mapped output
  columns and must not be added to the expected result or not-null list.
6. Use the framework's `DataQualityLibrary` methods for checks; do not duplicate
  pandas comparison logic in test bodies or create checks that compare target
  data to itself.
7. Every check has `parquet_data` and a dataset-specific marker. Add `smoke`
  only to the non-empty smoke check. Because pytest marker identifiers cannot
  start with a digit, normalize the dataset name to a valid marker identifier
  by prefixing `dataset_` when needed; retain all dataset-name words and
  underscores.
8. Include smoke, completeness, count, uniqueness, and not-null checks. Pass the
  mapped grain columns to `check_duplicates`; pass every mapped output column
  to `check_not_null_values`. Add a check for any additional explicit mapping
  constraint only if the framework exposes a corresponding validation method.
9. Never change a mapping-derived expected query merely to make a test pass.

## Workflow

1. Read the requested dataset entry from the mapping and record its output
  columns, grain, measures, join keys, filters, and explicit constraints.
2. Draft a source query from the mapped 3NF tables: select each mapped output,
  express mapped measures and aliases, include mapped joins and filters only,
  then group at the mapped grain. Compare the select list with the mapped
  output schema before proceeding.
3. Create the single test module using the template below. Replace all
  placeholders with the requested dataset's mapping-derived values; include
  the complete, reviewed expected query in `source_data`.
4. Use `/parquet_data/<dataset_name>` and read all partition subfolders in
  `target_data`. Add the five required checks, using grain keys for
  uniqueness and the full mapped output-column list for not-null.
5. Add `parquet_data` and the dataset marker to each test; add `smoke` only to
  the non-empty test. Do not add `example` to production checks.
6. Review the SQL against the mapping (not pipeline code), verify no template
  placeholders remain except user metadata intentionally unavailable, and
  report any mapping ambiguity or absent framework API instead of guessing.

## Template

Use this module skeleton. Replace placeholders using only the requested mapping.
The query placeholder is deliberately generic; do not put dataset SQL into this
skill.

```python
"""
Description: Data Quality checks for <dataset_name> dataset.
Requirement(s): <requirement_id>
Author(s): <author>
"""

import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
  source_query = """
  -- Expected query derived only from this dataset's mapping.
  """
  return db_connection.get_data_sql(source_query)


@pytest.fixture(scope='module')
def target_data(parquet_reader):
  target_path = '/parquet_data/<dataset_name>'
  return parquet_reader.process(target_path, include_subfolders=True)


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.<dataset_marker>
def test_check_dataset_is_not_empty(target_data, data_quality_library):
  data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_marker>
def test_check_data_completeness(source_data, target_data, data_quality_library):
  data_quality_library.check_data_completeness(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_marker>
def test_check_count(source_data, target_data, data_quality_library):
  data_quality_library.check_count(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_marker>
def test_check_uniqueness(target_data, data_quality_library):
  data_quality_library.check_duplicates(target_data, ['<grain_col_1>', '<grain_col_2>'])


@pytest.mark.parquet_data
@pytest.mark.<dataset_marker>
def test_check_not_null_values(target_data, data_quality_library):
  data_quality_library.check_not_null_values(
    target_data, ['<mapped_output_col_1>', '<mapped_output_col_2>']
  )
```

## SQL derivation (generic)

Translate the mapping's source-to-target statements literally into a relational
query. Use the source tables and join keys named in the mapping; select mapped
dimensions and measures with the exact target aliases; express date casts,
string composition, aggregation, and rounding only as specified. Group by the
dimensions that define the mapped grain, including any source components
needed to form a mapped composite value. Include a filter only when the mapping
states it. Confirm that the resulting output columns exactly match the mapped
schema. Do not infer missing rules from samples or the ETL implementation.

## After generation

Do not run the suite unless the user requests execution or the task explicitly
requires it. Before running, verify the framework prerequisites and dataset
availability. If checks fail, preserve the mapping-derived SQL and report the
dataset, check, expected mapping behavior, observed Parquet discrepancy, and
likely transformation defect. Do not rewrite the expected SQL to force a green
run. This skill does not configure Jenkins or capture credentials/screenshots.

---

## Skill review (self-check before Step 3)

Reject your own skill if any of these are true:

- [ ] Contains concrete expected SQL for `facility_name_min_time_spent_per_visit_date`, `facility_type_avg_time_spent_per_visit_date`, or `patient_sum_treatment_cost_per_facility_type`
- [ ] Tells the agent to use `data_dev/` or parquet loader SQL
- [ ] Omits completeness, count, uniqueness, or not-null
- [ ] Swaps Postgres vs Parquet fixtures or generates trivial always-pass checks
- [ ] Any section still contains unfinished template placeholders

All boxes must be unchecked before generation. The negative statements above
are rejection conditions: reject the skill if any statement is true.
