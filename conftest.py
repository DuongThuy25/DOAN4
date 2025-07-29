import pytest
from selenium import webdriver

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # chạy trình duyệt ở chế độ ẩn, không hiển thị UI
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)  # đợi tối đa 5 giây nếu element chưa sẵn sàng

    yield driver  # cung cấp driver cho các hàm test
    driver.quit()  # đóng trình duyệt sau khi test kết thúc
