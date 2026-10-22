# DQ transformation / defect analysis

## Execution status

The mapping-driven Parquet DQ suite was attempted locally, but a representative end-to-end run could not complete: PostgreSQL was not listening on `localhost:5434`, the `/parquet_data/` dataset directories were not present on this Windows host, and the Docker CLI was unavailable. Therefore there are no verified mapping-vs-Parquet assertion results or database-backed HTML report from this environment. The two database-free framework examples passed, and pytest-html successfully generated `html_report/example-report.html`; that report is framework smoke evidence, not the requested DQ pipeline report.

## Transformation discrepancies to verify in Jenkins

Review of the transformation implementation indicates the following likely mapping-vs-target defects. These are code-level predictions; confirm the actual failed checks and observed rows in the archived Jenkins DQ report after the lab prerequisites are running.

| Dataset | Mapping expectation | Transformation behavior to investigate | Likely DQ evidence |
| --- | --- | --- | --- |
| `facility_name_min_time_spent_per_visit_date` | One minimum-duration aggregate per facility name and visit date; no filters. | The implementation appends a second `UNION ALL` aggregation for Clinic rows. Those groups are already included in the unfiltered aggregate. | Duplicate grain keys; excess count; completeness mismatch. |
| `facility_type_avg_time_spent_per_visit_date` | Rounded daily average for every mapped facility type/date; no filters. | The implementation filters visits after `2000-11-01` and limits facility types, excluding data the mapping includes. | Missing expected rows; count and completeness mismatches. |
| `patient_sum_treatment_cost_per_facility_type` | First and last name concatenated; treatment costs summed without a sign change; mapped sum cannot be negative. | The implementation nulls names for a patient subset and negates Clinic sums. | Not-null failures, negative-measure failure, and completeness mismatches. |

Do not alter mapping-derived expected queries to accommodate these behaviors. Capture the Jenkins console log, review the archived full DQ HTML report, and add the actual failing test names and observed discrepancy samples here after a run with generated datasets.
