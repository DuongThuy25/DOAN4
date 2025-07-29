from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SearchPage:
    def __init__(self, driver):
        self.driver = driver

    def enter_search_keyword(self, keyword):
        search_input = self.driver.find_element(By.ID, "search-bar")
        search_input.clear()
        search_input.send_keys(keyword)


    def get_all_product_names(self):
        product_elements = self.driver.find_elements(By.CSS_SELECTOR, ".card-body .card-title")
        return [el.text.strip() for el in product_elements]

    def has_next_page(self):
        try:
            current = self.driver.find_element(By.CSS_SELECTOR, "ul.pagination li.page-item.active a")
            current_page = int(current.text.strip())
            all_links = self.driver.find_elements(By.CSS_SELECTOR, "ul.pagination li.page-item a")
            for link in all_links:
                text = link.text.strip()
                if text.isdigit() and int(text) > current_page:
                    return True
            return False
        except Exception as e:
            print("Lỗi khi kiểm tra next page:", e)
            return False

    def go_to_next_page(self):
        try:
            current = self.driver.find_element(By.CSS_SELECTOR, "ul.pagination li.page-item.active a")
            current_page = int(current.text.strip())
            all_links = self.driver.find_elements(By.CSS_SELECTOR, "ul.pagination li.page-item a")
            for link in all_links:
                text = link.text.strip()
                if text.isdigit() and int(text) == current_page + 1:
                    link.click()
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".card-body .card-title"))
                    )
                    return
            raise Exception("Không tìm thấy trang kế tiếp.")
        except Exception as e:
            raise Exception(f"Lỗi khi chuyển trang: {e}")
