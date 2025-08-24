import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from queries.add_cart_queries import get_user_id_by_username, clear_cart_by_user_id

class UpdateCartPage:
    def __init__(self, driver, base_url, username="dương thuỳ"):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)
        self.user_id = get_user_id_by_username(username)

    CART_PAGE_URL = "/cart/cart.html"
    CART_ROWS = (By.CSS_SELECTOR, ".cart-item-row")
    ITEM_TOTAL = (By.CSS_SELECTOR, ".total-price")

    def go_to_cart_page(self):
        self.driver.get(f"{self.base_url}{self.CART_PAGE_URL}")
        self.wait.until(EC.presence_of_all_elements_located(self.CART_ROWS))

    def clear_cart(self):
        clear_cart_by_user_id(self.user_id)

    def verify_cart_empty(self):
        self.go_to_cart_page()
        rows = self.driver.find_elements(*self.CART_ROWS)
        return len(rows) == 0

    def find_product_row(self, product_name):
        rows = self.driver.find_elements(*self.CART_ROWS)
        for row in rows:
            if product_name.lower() in row.text.lower():
                return row
        return None

    def get_quantity(self, row):
        qty_input = row.find_element(By.CSS_SELECTOR, "input.quantity")
        return int(qty_input.get_attribute("value"))

    def get_item_total_from_ui(self, row):
        total_elem = row.find_element(By.CSS_SELECTOR, ".total-price")
        # Lấy từ text, không lấy attribute
        total_text = total_elem.text.strip()       # ví dụ "340.000₫"
        total = int(total_text.replace(".", "").replace("₫", ""))
        return total



    def get_unit_price(self, row):
        """Tính giá 1 sản phẩm = total / quantity"""
        qty = self.get_quantity(row)
        if qty == 0:
            return 0
        total = self.get_item_total_from_ui(row)
        return total // qty

    def click_until_quantity(self, row, target_qty, max_steps=20):
        for _ in range(max_steps):
            current = self.get_quantity(row)
            if current == target_qty:
                return True
            elif current < target_qty:
                row.find_element(By.CSS_SELECTOR, ".increase").click()
            else:
                row.find_element(By.CSS_SELECTOR, ".decrease").click()
            # chờ input quantity update
            WebDriverWait(self.driver, 5).until(
                lambda d: int(row.find_element(By.CSS_SELECTOR, "input.quantity").get_attribute("value")) != current
            )
            time.sleep(0.2)
        return False

    def set_quantity_and_enter(self, row, target_qty):
        """
        Gõ số lượng trực tiếp vào ô input và nhấn Enter
        """
        qty_input = row.find_element(By.CSS_SELECTOR, "input.quantity")
        qty_input.clear()
        qty_input.send_keys(str(target_qty))
        qty_input.send_keys(Keys.ENTER)

        # Chờ UI cập nhật total
        WebDriverWait(self.driver, 3).until(
            lambda d: self.get_quantity(row) == target_qty
        )
