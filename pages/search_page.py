import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SearchPage:
    def __init__(self, driver):
        self.driver = driver
        self.search_input = (By.ID, "search-bar")
        self.product_name_elems = (By.CSS_SELECTOR, ".card-body .card-title")
        self.pagination_links = (By.CSS_SELECTOR, ".pagination .page-item:not(.active) .page-link")
        self.first_page_button = (By.CSS_SELECTOR, ".pagination .page-item:first-child .page-link")

    def reset_to_first_page(self):
        try:
            btn = self.driver.find_element(*self.first_page_button)
            if btn.is_enabled():
                # Dùng JS click để tránh bị che
                self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.5)
        except Exception as e:
            print(f"[reset_to_first_page] Lỗi: {e}")

    def enter_search_keyword(self, keyword):
        self.reset_to_first_page()
        inp = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(self.search_input)
        )
        inp.clear()
        inp.send_keys(keyword)
        time.sleep(1)

    def get_all_products_across_pages(self, keyword):
        """Thu thập sản phẩm hiển thị chứa keyword qua tất cả các trang (nếu có)."""
        all_products = []
        visited_pages = set()

        while True:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(self.product_name_elems)
            )

            visibles = [
                el.text.strip()
                for el in self.driver.find_elements(*self.product_name_elems)
                if el.is_displayed()
            ]

            matched = [
                name for name in visibles
                if keyword.casefold() in name.casefold()
            ]

            if not all_products and not matched:
                return []

            for name in matched:
                if name not in all_products:
                    all_products.append(name)

            # Kiểm tra có trang kế tiếp không
            next_page = None
            for link in self.driver.find_elements(*self.pagination_links):
                page_num = link.text.strip()
                if page_num and page_num not in visited_pages:
                    visited_pages.add(page_num)
                    next_page = link
                    break

            if not next_page:
                break

            self.driver.execute_script("arguments[0].click();", next_page)
            time.sleep(1)

        return all_products
