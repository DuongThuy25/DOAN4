import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class DeleteCartPage:
    CART_ROWS = (By.CSS_SELECTOR, ".cart-item-row")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def go_to_cart_page(self, base_url):
        self.driver.get(f"{base_url}/cart/cart.html")
        self.wait.until(EC.presence_of_all_elements_located(self.CART_ROWS))

    def find_product_row(self, product_name):
        rows = self.driver.find_elements(*self.CART_ROWS)
        for row in rows:
            if product_name.lower() in row.text.lower():
                return row
        return None

    def click_delete_button(self, row):
        delete_btn = row.find_element(By.CSS_SELECTOR, "button.delete-btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", delete_btn)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.delete-btn")))
        try:
            ActionChains(self.driver).move_to_element(delete_btn).click().perform()
        except:
            self.driver.execute_script("arguments[0].click();", delete_btn)
        time.sleep(0.3)  # chờ UI update

    def delete_product(self, product_name):
        row = self.find_product_row(product_name)
        if row:
            self.click_delete_button(row)
        else:
            print(f"[INFO] Product '{product_name}' not found in cart")
