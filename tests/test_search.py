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

# Đọc dữ liệu từ CSV
raw = read_csv_data("data/Data_Search.csv")
test_data = [
    (i + 1, row[0].strip() if row and row[0] else "")
    for i, row in enumerate(raw)
]


all_results = []

def normalize(lst):
    return sorted(s.strip().casefold() for s in lst)

@pytest.mark.parametrize("index,keyword", test_data)
def test_search(index, keyword, driver):
    test_name = f"test_search_{index}"
    status = "PASS"
    screenshot = ""
    db_raw = []
    ui_raw = []

    # Đăng nhập
    lp = LoginPage(driver)
    lp.open("http://127.0.0.1:5500/log%20in/log%20in.html")
    lp.login("dương thuỳ", "123")

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present()).accept()
    except TimeoutException:
        pass

    # Chuyển sang trang Sản phẩm
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Sản phẩm"))
    ).click()

    # Truy vấn DB
    try:
        db_raw = query_products_by_keyword(keyword)
        db_clean = normalize(db_raw)
    except Exception as e:
        status = "FAIL"
        screenshot = _capture(driver, test_name)
        _record_result(test_name, keyword, db_raw, ui_raw, status, screenshot)
        pytest.fail(f"[{test_name}] Lỗi truy vấn DB: {e}")

    # Lấy kết quả từ UI
    try:
        sp = SearchPage(driver)
        sp.enter_search_keyword(keyword)
        ui_raw = sp.get_all_products_across_pages(keyword)  # ✅ truyền keyword vào đây
        ui_clean = normalize(ui_raw)
    except Exception as e:
        status = "FAIL"
        screenshot = _capture(driver, test_name)
        _record_result(test_name, keyword, db_raw, ui_raw, status, screenshot)
        pytest.fail(f"[{test_name}] Lỗi lấy dữ liệu UI: {e}")

    # So sánh kết quả
    if ui_clean != db_clean:
        status = "FAIL"
        screenshot = _capture(driver, test_name)
        _record_result(test_name, keyword, db_raw, ui_raw, status, screenshot)
        pytest.fail(
            f"[{test_name}] UI & DB mismatch.\n"
            f"DB ({len(db_clean)}): {db_clean}\n"
            f"UI ({len(ui_clean)}): {ui_clean}"
        )

    _record_result(test_name, keyword, db_raw, ui_raw, status, screenshot)

def _capture(driver, name):
    path = f"report/screenshots/{name}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)
    return path

def _record_result(test_name, keyword, db_list, ui_list, status, screenshot_path):
    all_results.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Test Case": test_name,
        "Keyword": keyword,
        "DB Count": len(db_list),
        "UI Count": len(ui_list),
        "DB Result": ", ".join(db_list),
        "UI Result": ", ".join(ui_list),
        "Status": status,
        "Screenshot": screenshot_path if status == "FAIL" else ""
    })

def teardown_module(module):
    write_test_results_excel(
        all_results,
        filename="test_results_search.xlsx",
        sheet_name="Search Test Results"
    )
