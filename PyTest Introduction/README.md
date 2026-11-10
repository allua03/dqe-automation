# PyTest Introduction — ReportPortal

The CSV validation tests report results to the EPAM ReportPortal instance.

## Configure

1. Install this homework's dependencies: `pip install -r requirements.txt`.
2. In ReportPortal, open **Projects** and copy the exact project name into
   `tests/pytest.ini`, replacing `REPLACE_WITH_YOUR_RP_PROJECT`.
3. Generate an API key in your ReportPortal profile. Keep it out of source
   control and set it in the current PowerShell session:

   ```powershell
   $env:RP_API_KEY = "your-api-key"
   ```

## Run and verify

From this directory, run `pytest -c tests/pytest.ini`. ReportPortal is enabled
by default in the pytest configuration. The launch is named
**PyTest Introduction Homework**. The duplicate-row and invalid-email checks
are expected to fail against the supplied sample CSV; the failure messages and
logger messages are useful for reviewing defects in ReportPortal.

## Dashboard and screenshots

In ReportPortal, open **Dashboards** and create a dashboard. Add at least three
widgets, for example **Launch execution statistics**, **Test results trend**,
and **Top failed test cases**. Filter the dashboard/widgets by the launch name
above. Open a failed test item, review its logs, and choose the appropriate
**Defect Type** (for example, **Product Bug** if that matches your project's
classification policy).

Capture screenshots of: the Launches list, the dashboard with its widgets, and
the failed test details showing logs and defect type. The API key and project
name are account-specific and should not be committed to the repository.