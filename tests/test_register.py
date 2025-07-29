import os
import pytest
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from pages.register_page import RegisterPage
from utils.data_reader import read_csv_data
from utils.test_result_writer_excel import write_test_results_excel

test_data = read_csv_data("data/Data_Register.csv")
all_results = []

@pytest.mark.parametrize("index,username,email,password,sdt,expected_result", [(i + 1, *row) for i, row in enumerate(test_data)])
def test_register(driver, index, username, email, password, sdt, expected_result):
    register_page = RegisterPage(driver)
    register_page.open("http://127.0.0.1:5500/log%20in/register.html")

    register_page.register(username, email, password, sdt)

    test_name = f"test_register_{index}"
    screenshot_path = ""
    actual_result = ""
    status = "FAIL"

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        actual_result = alert.text
        alert.accept()

        if actual_result == expected_result:
            status = "PASS"
        else:
            raise AssertionError("Actual result doesn't match expected result.")

    except (TimeoutException, UnexpectedAlertPresentException, AssertionError) as e:
        screenshot_dir = "report/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"{test_name}.png")
        driver.save_screenshot(screenshot_path)
        if not actual_result:
            actual_result = str(e)

    all_results.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Test Name": test_name,
        "Username": username,
        "Email": email,
        "Password": password,
        "SDT": sdt,
        "Expected": expected_result,
        "Actual": actual_result,
        "Status": status,
        "Screenshot": screenshot_path if status == "FAIL" else ""
    })

    assert status == "PASS", f"[{test_name}] Expected: {expected_result}, but got: {actual_result}"

def teardown_module(module):
    write_test_results_excel(
        all_results,
        filename="test_results_register.xlsx",
        sheet_name="Test Results Register"
    )
