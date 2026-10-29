import time
import os
import csv

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(SCRIPT_DIR, "report.html")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")


class SeleniumWebDriverContextManager:
    """Context manager that creates and tears down a Chrome WebDriver instance."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver: WebDriver | None = None

    def __enter__(self) -> WebDriver:
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver is not None:
            self.driver.quit()


def extract_table(driver: WebDriver) -> list[dict]:
    """Reads the table from the report and returns rows as a list of dicts."""
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "table")))
        # Locator #1: CLASS_NAME
        table = driver.find_element(By.CLASS_NAME, "table")
        # Locator #2: XPath scoped to the table
        columns = table.find_elements(By.XPATH, ".//*[contains(@class, 'y-column')]")

        headers = []
        column_values = []
        for column in columns:
            try:
                # Locator #3: ID scoped to column
                header_text = column.find_element(By.ID, "header").text.strip()
            except NoSuchElementException:
                header_text = ""
            headers.append(header_text)

            cells = column.find_elements(By.CLASS_NAME, "cell-text")
            values = [cell.text.strip() for cell in cells if cell.text.strip() != header_text]
            column_values.append(values)

        row_count = max((len(values) for values in column_values), default=0)
        rows = []
        for i in range(row_count):
            row = {}
            for header, values in zip(headers, column_values):
                row[header] = values[i] if i < len(values) else ""
            rows.append(row)
        return rows
    except TimeoutException:
        print("Table did not load in time.")
        return []
    except NoSuchElementException as e:
        print(f"Could not locate table element: {e}")
        return []


def save_rows_to_csv(rows: list[dict], file_path: str) -> None:
    if not rows:
        print(f"No data to write to {file_path}")
        return
    fieldnames = list(rows[0].keys())
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {file_path}")


def extract_doughnut_data(driver: WebDriver) -> list[dict]:
    """Reads category/value pairs from the doughnut chart slices."""
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "pielayer")))
        doughnut = driver.find_element(By.CLASS_NAME, "pielayer")
        labels = doughnut.find_elements(By.CSS_SELECTOR, "text.slicetext[data-notex='1']")

        data = []
        for label in labels:
            tspans = label.find_elements(By.TAG_NAME, "tspan")
            if len(tspans) >= 2:
                category = tspans[0].text.strip()
                value = tspans[1].text.strip()
                data.append({"Facility Type": category, "Min Average Time Spent": value})
        return data
    except TimeoutException:
        print("Doughnut chart did not load in time.")
        return []
    except NoSuchElementException as e:
        print(f"Could not locate doughnut chart element: {e}")
        return []


def get_legend_items(driver: WebDriver) -> list:
    try:
        legend_box = driver.find_element(By.CLASS_NAME, "scrollbox")
        return legend_box.find_elements(By.CLASS_NAME, "traces")
    except NoSuchElementException:
        return []


def run_doughnut_filters(driver: WebDriver) -> None:
    """Takes a screenshot/CSV snapshot before and after toggling each legend filter."""
    screenshot_index = 0
    csv_index = 0

    # Initial, unfiltered state
    driver.save_screenshot(os.path.join(OUTPUT_DIR, f"screenshot{screenshot_index}.png"))
    screenshot_index += 1
    initial_data = extract_doughnut_data(driver)
    save_rows_to_csv(initial_data, os.path.join(OUTPUT_DIR, f"doughnut{csv_index}.csv"))
    csv_index += 1

    legend_items = get_legend_items(driver)
    total_items = len(legend_items)

    for i in range(total_items):
        try:
            # Re-fetch legend items each iteration: DOM re-renders after each click
            legend_items = get_legend_items(driver)
            item = legend_items[i]
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "traces")))
            # JS click bypasses Plotly's transient "notifier-note" overlay intercepting the click
            driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", item)
            time.sleep(1)

            driver.save_screenshot(os.path.join(OUTPUT_DIR, f"screenshot{screenshot_index}.png"))
            screenshot_index += 1

            chart_data = extract_doughnut_data(driver)
            if not chart_data:
                print(f"Filter {i}: all slices unselected or no data visible, skipping CSV write.")
                continue

            save_rows_to_csv(chart_data, os.path.join(OUTPUT_DIR, f"doughnut{csv_index}.csv"))
            csv_index += 1
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
            print(f"Failed to apply filter {i}: {e}")
            continue


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = f"file:///{REPORT_PATH}"

    with SeleniumWebDriverContextManager() as driver:
        driver.get(file_path)

        table_rows = extract_table(driver)
        save_rows_to_csv(table_rows, os.path.join(OUTPUT_DIR, "table.csv"))

        run_doughnut_filters(driver)
