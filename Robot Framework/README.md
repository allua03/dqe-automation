# HTML report vs. Parquet Robot test

This test opens the Plotly report in Chrome, extracts the displayed table, reads the partitioned `facility_type_avg_time_spent_per_visit_date` dataset, and compares rows without relying on row order.

## Setup

Install dependencies from this directory with `pip install -r requirements.txt`. Chrome must be installed; Selenium Manager resolves the matching ChromeDriver.

By default, the test uses `../Selenium Introduction/report.html` and `parquet_data/facility_type_avg_time_spent_per_visit_date` in this folder. Copy the matching dataset from the container into that location, or override paths on the Robot command line.

## Run

From this directory, run `robot --outputdir ./results test.robot`.

To supply other paths or compare one date (inclusive exact date in both sources), run for example:

`robot --outputdir ./results --variable REPORT_FILE:C:/data/report.html --variable PARQUET_FOLDER:C:/data/facility_type_avg_time_spent_per_visit_date --variable FILTER_DATE:2026-10-31 test.robot`

Leave `FILTER_DATE` empty to compare the report's displayed date range against the corresponding Parquet date range. The browser is closed in test teardown, including on failure. Robot creates `results/output.xml`, `results/log.html`, and `results/report.html`.
