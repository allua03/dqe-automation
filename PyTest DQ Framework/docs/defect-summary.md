# Transformation / Defect Summary

Run: `pytest tests -m "parquet_data" --db_host=postgres --db_port=5432 --db_name=mydatabase ... --html=html_report/index.html`
Result: **8 failed, 7 passed, 2 deselected** (full console log: [console.log](../console.log), report: [html_report/index.html](../html_report/index.html)).

Expected SQL in all three test modules comes only from [parquet-aggregated-data-mapping.md](../../docs/parquet-aggregated-data-mapping.md); it was not adjusted to force a green run. All failures below are judged against the mapping, not against `data_dev` ETL code.

## 1. `facility_name_min_time_spent_per_visit_date`

- `test_check_count`: expected 35,435 rows (Postgres grouped by `facility_name` + visit date), actual Parquet has 44,287 rows.
- `test_check_uniqueness`: 17,704 duplicate rows found in the Parquet dataset (full-row duplicates).
- `test_check_data_completeness`: rows present in Parquet do not match the expected grouped set.
- **Likely root cause:** the Parquet writer is not grouping at the mapping's grain (`facility_name`, `visit_date` = date part of `visit_timestamp`). Extra/duplicate rows suggest the transformation groups by a finer grain (e.g. full timestamp) or writes rows per partition sub-folder without deduplicating, producing more rows than the distinct `(facility_name, visit_date)` pairs and duplicate records within partitions.

## 2. `facility_type_avg_time_spent_per_visit_date`

- `test_check_count`: expected 35,435 rows, actual Parquet has 25,747 rows (fewer than expected).
- `test_check_data_completeness`: mismatched rows between expected and actual.
- **Likely root cause:** opposite symptom to dataset 1 — the transformation appears to be **losing** grain combinations (e.g. collapsing some `visit_date` values, or an unintended filter/join that drops rows), rather than duplicating them. Row count being lower than expected while using the same grain as dataset 1 suggests the `AVG`/rounding transformation, or the join to `facilities`, is dropping or merging some facility/date combinations.

## 3. `patient_sum_treatment_cost_per_facility_type`

- `test_check_count`: expected 120 rows (`facility_type` × distinct `full_name`), actual Parquet has 64 rows.
- `test_check_not_null_values`: 4 rows have `full_name = None` — one per `facility_type` partition, each carrying a very large positive or negative `sum_treatment_cost` (e.g. `Clinic / None / -1,748,014.95`, `Hospital / None / 26,182,934.04`).
- **Likely root cause:** a subtotal/rollup row is being written per `facility_type` partition in addition to the per-patient rows (`full_name` is null only on these extra rows), and at least one partition's subtotal has an inverted sign. This points to a `GROUP BY ROLLUP`/grouping-sets style aggregation (or a manual total-row append) in the ETL that the mapping does not call for — the mapping only defines grouping by `facility_type` + `full_name`, with no totals row.

## Conclusion

All three datasets disagree with the mapping on either grain (extra/duplicate rows), row completeness (missing rows), or structure (unexpected rollup/null rows with sign errors). These are transformation defects in the Parquet aggregation step, not test issues — the expected queries implement exactly the grouping/measures defined in the mapping and nothing more.
