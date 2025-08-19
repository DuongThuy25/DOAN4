import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

class AddCartPage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def go_to_product_page(self):
        self.driver.get(f"{self.base_url}/product-list/product-list.html")
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Sản phẩm")))
        print("[DEBUG] Đã mở trang danh sách sản phẩm.")

    def go_to_product_detail(self, product_name):
        self.driver.find_element(By.LINK_TEXT, "Sản phẩm").click()
        self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card")))

        for card in self.driver.find_elements(By.CSS_SELECTOR, ".card"):
            title = card.find_element(By.CSS_SELECTOR, ".card-title").text.strip()
            if product_name.strip().lower() == title.lower():
                print(f"[DEBUG] Tìm thấy sản phẩm: {title}")
                try:
                    btn = card.find_element(By.ID, "add-to-cart")
                except Exception:
                    btn = card.find_element(By.CSS_SELECTOR, "a.btn.btn-outline-success")
                try:
                    btn.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", btn)
                self.wait.until(EC.presence_of_element_located((By.ID, "product-title")))
                return
        raise ValueError(f"Không tìm thấy sản phẩm: {product_name}")

    def add_to_cart(self, quantity: int):
        qty_input = self.wait.until(EC.presence_of_element_located((By.ID, "quantity")))
        qty_input.clear()
        qty_input.send_keys(str(quantity))
        print(f"[DEBUG] Nhập số lượng = {quantity}")

        add_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart")))
        try:
            add_btn.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", add_btn)

        try:
            self.wait.until(EC.alert_is_present()).accept()
            print("[DEBUG] Đã thêm sản phẩm vào giỏ hàng (alert).")
        except TimeoutException:
            print("[DEBUG] Đã thêm sản phẩm vào giỏ hàng (không có alert).")

    def _parse_price_to_int(self, price_text: str) -> int:
        """Chuyển giá tiền text -> int"""
        print(f"[DEBUG] Raw price text: '{price_text}'")
        cleaned = re.sub(r"\D", "", price_text)
        value = int(cleaned) if cleaned else 0
        print(f"[DEBUG] Parsed int price: {value}")
        return value

    def open_cart_and_get_items(self):
        """Mở giỏ hàng và lấy danh sách sản phẩm"""
        cart_link = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='cart']")))
        cart_link.click()

        self.wait.until(EC.url_contains("cart"))
        self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".cart-item-row")))

        items = []
        for elem in self.driver.find_elements(By.CSS_SELECTOR, ".cart-item-row"):
            name = elem.find_element(By.CSS_SELECTOR, "p.m-0").text.strip()
            qty = int(elem.find_element(By.CSS_SELECTOR, "input.quantity").get_attribute("value").strip())

            price_elem = elem.find_element(By.CSS_SELECTOR, ".total-price")
            price_text = price_elem.get_attribute("data-totalprice") or price_elem.text
            total_price = self._parse_price_to_int(price_text)
            unit_price = total_price // qty if qty > 0 else total_price

            item = {
                "name": name,
                "qty": qty,
                "unit_price": unit_price,
                "price": total_price
            }
            print(f"[DEBUG][UI] Cart item: {item}")
            items.append(item)
        return items

    def get_cart_item_by_product_name(self, product_name):
        xpath = f"//div[contains(@class, 'cart-item-row')][.//p[@class='m-0' and normalize-space(text())='{product_name}']]"
        elem = self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        print(f"[DEBUG] Found cart item element for {product_name}")
        return elem
