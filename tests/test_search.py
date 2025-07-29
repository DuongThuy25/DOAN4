import os
import pytest
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from pages.login_page import LoginPage
from pages.search_page import SearchPage
from queries.search_queries import query_products_by_keyword
from utils.data_reader import read_csv_data
from utils.test_result_writer_excel import write_test_results_excel

raw_data = read_csv_data("data/Data_Search.csv")
test_data = [
    (i + 1, row[0].strip())
    for i, row in enumerate(raw_data)
    if len(row) >= 1 and row[0].strip() != ""
]

all_results = []

@pytest.mark.parametrize("index,keyword", test_data)
def test_search(index, keyword, driver):
    login_page = LoginPage(driver)
    login_page.open("http://127.0.0.1:5500/log%20in/log%20in.html")
    login_page.login("dương thuỳ", "123")

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
    except TimeoutException:
        print("Không có alert hiển thị sau khi đăng nhập.")

    try:
        sanpham_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Sản phẩm"))
        )
        sanpham_link.click()
    except:
        pytest.fail("Không tìm thấy hoặc không click được liên kết 'Sản phẩm' sau khi đăng nhập")

    search_page = SearchPage(driver)
    search_page.enter_search_keyword(keyword)

    ui_product_names = []
    while True:
        ui_product_names.extend(search_page.get_all_product_names())
        if search_page.has_next_page():
            search_page.go_to_next_page()
        else:
            break

    db_product_names = query_products_by_keyword(keyword)
    test_name = f"test_search_{index}"
    screenshot_path = ""
    status = "PASS"

    if sorted(ui_product_names) != sorted(db_product_names):
        status = "FAIL"
        screenshot_dir = "report/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"{test_name}.png")
        driver.save_screenshot(screenshot_path)

    all_results.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Test Name": test_name,
        "Keyword": keyword,
        "Expected Count (DB)": len(db_product_names),
        "Actual Count (UI)": len(ui_product_names),
        "Status": status,
        "Missing In UI": ", ".join(set(db_product_names) - set(ui_product_names)),
        "Unexpected In UI": ", ".join(set(ui_product_names) - set(db_product_names)),
        "Screenshot": screenshot_path if status == "FAIL" else ""
    })

    assert status == "PASS", (
        f"[{test_name}] UI & DB mismatch.\n"
        f"Expected (DB): {db_product_names}\n"
        f"Actual (UI):   {ui_product_names}"
    )

def teardown_module(module):
    write_test_results_excel(
        all_results,
        filename="test_results_search.xlsx",
        sheet_name="Search Test Results"
    )
