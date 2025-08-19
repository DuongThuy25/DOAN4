import pytest
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pages.login_page import LoginPage
from pages.add_cart_page import AddCartPage
from utils.data_reader import read_csv_data
from utils.test_result_writer_excel import write_test_results_excel
from queries.add_cart_queries import (
    get_user_id_by_username,
    query_cart_items_by_user,
    clear_cart_by_user_id
)

raw = read_csv_data("data/Data_Add_Cart.csv")
test_data = []
for i, row in enumerate(raw):
    username, password, _, product_names, quantities, expected_total = row
    names = product_names.split("|")
    qtys = list(map(int, quantities.split("|")))
    test_data.append((i + 1, username.strip(), password.strip(), list(zip(names, qtys)), int(expected_total)))

all_results = []

@pytest.mark.parametrize("index,username,password,products,expected_total", test_data)
def test_add_cart(index, username, password, products, expected_total, driver):
    test_name = f"test_add_cart_{index}"
    status = "PASS"
    screenshot = ""
    actual_total = 0

    user_id = get_user_id_by_username(username)
    clear_cart_by_user_id(user_id)

    lp = LoginPage(driver)
    lp.open("http://127.0.0.1:5500/log%20in/log%20in.html")
    lp.login(username, password)
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present()).accept()
    except TimeoutException:
        pass

    cart_page = AddCartPage(driver, base_url="http://127.0.0.1:5500")
    cart_page.go_to_product_page()

    try:
        for name, qty in products:
            print(f"[DEBUG] Đang thêm sản phẩm {name} x{qty}")
            cart_page.go_to_product_detail(name)
            cart_page.add_to_cart(qty)
            cart_page.go_to_product_page()

        # Lấy từ UI
        cart_items = cart_page.open_cart_and_get_items()
        actual_total = sum(item["price"] for item in cart_items)
        print(f"[DEBUG] UI cart items: {cart_items}")
        print(f"[DEBUG] Actual total (UI): {actual_total}, Expected total: {expected_total}")

        if actual_total != expected_total:
            raise AssertionError(f"Tổng tiền không khớp: mong đợi {expected_total}, thực tế {actual_total}")

        # Lấy từ DB
        db_items = query_cart_items_by_user(user_id)
        print(f"[DEBUG] DB cart items: {db_items}")

        def normalize(lst):
            return sorted(f"{it['name'].strip().lower()} x{it['qty']} = {int(it['price'])}" for it in lst)

        print(f"[DEBUG] Compare DB vs UI\n DB={normalize(db_items)}\n UI={normalize(cart_items)}")

        if normalize(db_items) != normalize(cart_items):
            raise AssertionError(f"{test_name} DB & UI mismatch. DB={normalize(db_items)}, UI={normalize(cart_items)}")

    except Exception as e:
        status = "FAIL"
        screenshot = _capture(driver, test_name)
        _record(test_name, username, products, expected_total, actual_total, status, screenshot)
        pytest.fail(f"[{test_name}] Lỗi: {e}")

    _record(test_name, username, products, expected_total, actual_total, status, screenshot)

def _capture(driver, name):
    import os
    path = f"report/screenshots/{name}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)
    return path

def _record(test_name, user, products, expect, actual, status, screenshot):
    all_results.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Test Case": test_name,
        "User": user,
        "Products": ", ".join(f"{p[0]} x{p[1]}" for p in products),
        "Expected Total": expect,
        "Actual Total": actual,
        "Status": status,
        "Screenshot": screenshot if status == "FAIL" else ""
    })

def teardown_module(module):
    write_test_results_excel(all_results, filename="test_results_add_cart.xlsx", sheet_name="Add Cart Test")
