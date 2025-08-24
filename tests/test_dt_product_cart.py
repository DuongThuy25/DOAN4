import os
import time
import pytest
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from pages.login_page import LoginPage
from pages.add_cart_page import AddCartPage
from pages.delete_product_cart import DeleteCartPage

BASE_URL = "http://127.0.0.1:5500"
REPORT_FILE = "report/test_results_delete_product_report.xlsx"

def write_report(username, product_name, action, result, screenshot_path):
    """Ghi báo cáo Excel giống UpdateCart"""
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    df_new = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Username": username,
        "Product": product_name,
        "Action": action,
        "Result": result,
        "Screenshot": screenshot_path,

    }])
    if os.path.exists(REPORT_FILE):
        df = pd.read_excel(REPORT_FILE)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_excel(REPORT_FILE, index=False)

def accept_alert(driver, timeout=5):
    """Chờ alert và accept nếu có, không crash nếu không có alert"""
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"[ALERT] {alert.text}")
        alert.accept()
        time.sleep(0.3)  # chờ UI update
    except TimeoutException:
        print("[INFO] No alert appeared.")

def test_delete_product_bug():
    driver = webdriver.Chrome()
    username = "dương thuỳ"
    password = "123"
    product_name = "Cà phê sữa đá"
    screenshot_path = ""

    try:
        # 1) Login
        login_page = LoginPage(driver)
        login_page.open(f"{BASE_URL}/log%20in/log%20in.html")
        login_page.login(username, password)
        accept_alert(driver, timeout=5)

        # 2) Add product vào giỏ
        add_page = AddCartPage(driver, BASE_URL)
        add_page.go_to_product_page()
        add_page.go_to_product_detail(product_name)
        add_page.add_to_cart(1)
        accept_alert(driver, timeout=5)

        # 3) Vào giỏ hàng
        delete_page = DeleteCartPage(driver)
        delete_page.go_to_cart_page(BASE_URL)
        time.sleep(0.5)
        accept_alert(driver, timeout=2)  # đề phòng alert bất ngờ

        # 4) Click nút Xóa
        try:
            delete_page.delete_product(product_name)
            accept_alert(driver, timeout=2)  # đề phòng alert sau khi click Xóa
        except UnexpectedAlertPresentException:
            accept_alert(driver, timeout=2)
            delete_page.delete_product(product_name)

        time.sleep(2)
        # 5) Kiểm tra sản phẩm vẫn còn → bug
        row = delete_page.find_product_row(product_name)
        if row:
            # Chụp ảnh
            screenshot_path = f"report/screenshots/{product_name}_delete_bug.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            driver.save_screenshot(screenshot_path)
            # Ghi báo cáo
            write_report(username, product_name, "Click Xóa", "Product vẫn còn hiển thị trên UI", screenshot_path)
            pytest.fail(f"BUG: Product '{product_name}' vẫn còn trong giỏ sau khi click Xóa!")
        else:
            # Ghi báo cáo thành công
            write_report(username, product_name, "Click Xóa", "Product deleted successfully", "")

    except Exception as e:
        # Capture screenshot + ghi báo cáo khi bất kỳ lỗi nào xảy ra
        screenshot_path = f"report/screenshots/{product_name}_error.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        driver.save_screenshot(screenshot_path)
        write_report(username, product_name, "Click Xóa", f"Error: {e}", screenshot_path)
        raise

    finally:
        driver.quit()
