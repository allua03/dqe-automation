*** Settings ***
Documentation       Verify that the Plotly report table matches its partitioned Parquet source.
Library             SeleniumLibrary
Library             ${CURDIR}${/}helper.py    WITH NAME    DataHelper
Library             OperatingSystem
Test Teardown       Close All Browsers

*** Variables ***
${REPORT_FILE}      ${CURDIR}${/}..${/}Selenium Introduction${/}report.html
${PARQUET_FOLDER}   ${CURDIR}${/}parquet_data${/}facility_type_avg_time_spent_per_visit_date
${FILTER_DATE}      ${EMPTY}

*** Test Cases ***
HTML report table matches Parquet dataset
	File Should Exist    ${REPORT_FILE}
	Directory Should Exist    ${PARQUET_FOLDER}
	${report_url}=    DataHelper.Path To File Url    ${REPORT_FILE}
	Open Browser    ${report_url}    chrome
	Wait Until Page Contains Element    css:.table .y-column    20s
	${table}=    Get WebElement    css:.table
	${report_data}=    DataHelper.Read Stable Html Table To Dataframe    ${table}

	IF    $FILTER_DATE
		${report_data}=    DataHelper.Filter Dataframe By Date    ${report_data}    ${FILTER_DATE}
		${parquet_data}=    DataHelper.Read Parquet Dataset    ${PARQUET_FOLDER}    ${FILTER_DATE}
	ELSE
		${start_date}    ${end_date}=    DataHelper.Get Dataframe Date Range    ${report_data}
		${parquet_data}=    DataHelper.Read Parquet Dataset
		...    ${PARQUET_FOLDER}
		...    ${EMPTY}
		...    ${start_date}
		...    ${end_date}
	END

	${matches}    ${differences}=    DataHelper.Compare Dataframes    ${report_data}    ${parquet_data}
	IF    not $matches
		Fail    ${differences}
	END
