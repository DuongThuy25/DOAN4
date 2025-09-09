import time
import re
import unicodedata
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from queries.add_cart_queries import clear_cart_by_user_id
from queries.order_queries import clear_orders_by_user_id

class OrderPage:
    ADDRESS_INPUT = (By.ID, "shipping-address")
    CONFIRM_ORDER_BTN = (By.ID, "confirm-order-btn")
    CART_ROWS = (By.CSS_SELECTOR, ".cart-item-row")
    TICKALL = (By.ID, "select-all")
    BUY_BTN = (By.XPATH, "//button[contains(text(),'Mua hàng')]")
    INFO_CONTAINER = (By.CSS_SELECTOR, "div#info")
    ORDER_ITEM_ROWS = (By.CSS_SELECTOR, ".order-item-row")
    ORDERS_TABLE_ROWS = (By.CSS_SELECTOR, "#orders-table-body tr")

    def __init__(self, driver, base_url, user_id=None, wait_seconds=5):
        self.driver = driver
        self.base_url = base_url
        self.user_id = user_id
        self.wait = WebDriverWait(driver, wait_seconds)

    def clear_cart(self, user_id: int, clear_orders_too: bool = True, only_pending_orders: bool = True):
        clear_cart_by_user_id(user_id)
        if clear_orders_too:
            clear_orders_by_user_id(user_id, only_pending=only_pending_orders)

    def go_to_cart_page(self):
        self.driver.get(f"{self.base_url}/cart/cart.html")
        self.wait.until(EC.presence_of_all_elements_located(self.CART_ROWS))

    def _normalize_text(self, s: str) -> str:
        if not s:
            return ""
        s = unicodedata.normalize("NFC", s)
        return " ".join(s.split()).strip()

    def _extract_after_colon(self, text: str) -> str:
        if ":" in text:
            return text.split(":", 1)[1].strip()
        return text.strip()

    def get_customer_info(self):
        try:
            info_el = self.driver.find_element(*self.INFO_CONTAINER)
            raw = info_el.text or ""
            lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
            low_lines = [ln.lower() for ln in lines]

            name = ""
            for i, ln in enumerate(low_lines):
                if "tên khách hàng" in ln or ln.startswith("tên"):
                    name = self._extract_after_colon(lines[i])
                    break
            if not name and lines:
                name = lines[0]

            phone = ""
            for i, ln in enumerate(low_lines):
                if any(k in ln for k in ("số điện thoại", "sđt", "điện thoại", "sô")):
                    phone = self._extract_after_colon(lines[i])
                    break
            if not phone:
                m = re.search(r"((?:\+?\d[\d\s\.-]{4,}\d))", raw)
                if m:
                    phone = m.group(1).strip()

            email = ""
            for i, ln in enumerate(low_lines):
                if "email" in ln:
                    email = self._extract_after_colon(lines[i])
                    break

            return {"name": self._normalize_text(name),
                    "phone": self._normalize_text(phone),
                    "email": self._normalize_text(email)}
        except Exception:
            name = self._get_label_value("Tên khách hàng") or self._get_label_value("Tên") or ""
            phone = self._get_label_value("Số điện thoại") or self._get_label_value("SĐT") or ""
            email = self._get_label_value("Email") or ""
            return {"name": self._normalize_text(name),
                    "phone": self._normalize_text(phone),
                    "email": self._normalize_text(email)}

    def select_all_and_checkout(self):
        select_all = self.wait.until(EC.element_to_be_clickable(self.TICKALL))
        select_all.click()
        time.sleep(0.3)

        buy_btn_el = self.wait.until(EC.element_to_be_clickable(self.BUY_BTN))
        try:
            buy_btn_el.click()
        except:
            self.driver.execute_script("arguments[0].click();", buy_btn_el)
        time.sleep(0.5)

    def enter_address_and_checkout(self, address: str):
        el = self.wait.until(EC.presence_of_element_located(self.ADDRESS_INPUT))
        el.clear()
        if address:
            el.send_keys(address)
        time.sleep(0.2)

        btn = self.wait.until(EC.element_to_be_clickable(self.CONFIRM_ORDER_BTN))
        try:
            btn.click()
        except:
            self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)

    def _get_label_value(self, label):
        try:
            el = self.driver.find_element(By.XPATH, f"//*[contains(normalize-space(.),'{label}')]")
            text = el.text.strip()
            if ":" in text:
                return text.split(":", 1)[1].strip()
            parent = el.find_element(By.XPATH, "..")
            ptext = parent.text.strip()
            for line in ptext.splitlines():
                if label in line and ":" in line:
                    return line.split(":", 1)[1].strip()
            return ""
        except Exception:
            return ""

    def get_address_error_message(self, timeout=2):
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            text = alert.text.strip()
            alert.accept()
            return text
        except Exception:
            return ""

    def get_toast_message(self, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            return text.strip()
        except Exception:
            pass
        try:
            toast = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "successToast"))
            )
            body = toast.find_element(By.CSS_SELECTOR, ".toast-body")
            return body.text.strip()
        except Exception:
            pass
        try:
            body = self.driver.find_element(By.CSS_SELECTOR, ".toast-body")
            return body.text.strip()
        except Exception:
            return ""

    def get_order_info_from_ui(self):
        try:
            self.wait.until(EC.presence_of_all_elements_located(self.ORDER_ITEM_ROWS))
        except:
            pass
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".order-item-row")
        results = []
        for row in rows:
            try:
                name = self._normalize_text(row.find_element(By.CSS_SELECTOR, ".product-name").text)
                qty_text = row.find_element(By.CSS_SELECTOR, ".product-qty").text.strip()
                m_qty = re.search(r"\d+", qty_text)
                qty = int(m_qty.group()) if m_qty else int(qty_text) if qty_text.isdigit() else 0
                price_text = row.find_element(By.CSS_SELECTOR, ".product-price").text.strip()
                price_digits = "".join(ch for ch in price_text if ch.isdigit())
                price = int(price_digits) if price_digits else 0
                results.append({"name": name, "qty": qty, "price": price})
            except:
                continue
        return results

    def get_latest_order_from_ui(self):
        try:
            self.wait.until(EC.presence_of_all_elements_located(self.ORDERS_TABLE_ROWS))
            rows = self.driver.find_elements(*self.ORDERS_TABLE_ROWS)
            if not rows:
                return None
            latest_row = rows[0]
            cols = latest_row.find_elements(By.TAG_NAME, "td")
            return {
                "order_id": cols[0].text.strip(),
                "order_date": cols[1].text.strip(),
                "total_amount": cols[2].text.strip(),
                "status": cols[3].text.strip()
            }
        except:
            return None
