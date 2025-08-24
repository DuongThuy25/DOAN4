import os
import csv
import pytest
import time
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.add_cart_page import AddCartPage
from pages.update_cart_page import UpdateCartPage
from utils.test_result_writer_excel import write_test_results_excel

BASE_URL = "http://127.0.0.1:5500"
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Data_Update_Cart.csv")

all_results = []

def read_csv():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

@pytest.mark.parametrize("data", read_csv())
def test_update_cart(data):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    username       = data["username"].strip()
    password       = data["password"].strip()
    product_name   = data["product_name"].strip()
    initial_qty    = int(data["initial_quantity"])
    update_action  = data["update_action"].strip()
    expected_qty   = int(data["expected_quantity"])
    expected_total = int(data["expected_total"])

    test_name = f"test_update_cart_{username}_{product_name}_{update_action}"
    status = "PASS"
    screenshot = ""
    ui_total = None

    try:
        # 1) Login
        login_page = LoginPage(driver)
        login_page.open(f"{BASE_URL}/log%20in/log%20in.html")
        login_page.login(username, password)
        try:
            wait.until(EC.alert_is_present()).accept()
        except TimeoutException:
            pass

        # 2) Clear cart
        cart_page = UpdateCartPage(driver, BASE_URL, username=username)
        cart_page.clear_cart()

        # 3) Add product
        add_page = AddCartPage(driver, BASE_URL)
        add_page.go_to_product_page()
        add_page.go_to_product_detail(product_name)
        add_page.add_to_cart(initial_qty)

        # 4) Vào giỏ hàng
        cart_page.go_to_cart_page()
        time.sleep(0.3)
        row = cart_page.find_product_row(product_name)
        assert row is not None, f"Không tìm thấy {product_name} trong giỏ!"

        # 5) Click +/- để đạt expected_qty
        if update_action == "+" or update_action == "-":
            ok = cart_page.click_until_quantity(row, expected_qty)
            assert ok, f"Không đưa được qty tới {expected_qty}"
        elif update_action.lower() == "edit":
            cart_page.set_quantity_and_enter(row, expected_qty)
        else:
            raise ValueError(f"Unknown update_action: {update_action}")

        # 6) Kiểm tra tổng tiền
        ui_total = cart_page.get_item_total_from_ui(row)
        print(f"[DEBUG] qty={cart_page.get_quantity(row)}, UI total={ui_total}, expected_total={expected_total}")
        assert ui_total == expected_total, f"Sai tổng tiền - expected {expected_total}, got {ui_total}"

    except Exception as e:
        status = "FAIL"
        screenshot = _capture(driver, test_name)
        _record_result(test_name, data, expected_total, ui_total, status, screenshot)
        pytest.fail(f"[{test_name}] Error: {e}")

    else:
        _record_result(test_name, data, expected_total, ui_total, status, screenshot)
    finally:
        driver.quit()

# --- Helpers ---
def _capture(driver, name):
    path = f"report/screenshots/{name}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)
    return path

def _record_result(test_name, data, expected_total, actual_total, status, screenshot_path):
    all_results.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Test Case": test_name,
        "Username": data["username"],
        "Product": data["product_name"],
        "Action": data["update_action"],
        "Initial Qty": data["initial_quantity"],
        "Expected Qty": data["expected_quantity"],
        "Expected Total (CSV)": expected_total,
        "Actual Total (UI)": actual_total if actual_total is not None else "",
        "Status": status,
        "Screenshot": screenshot_path if status == "FAIL" else ""
    })

def teardown_module(module):
    write_test_results_excel(
        all_results,
        filename="test_results_update_cart.xlsx",
        sheet_name="Update Cart Results"
    )
