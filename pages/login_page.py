from selenium.webdriver.common.by import By

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "username")  # ô nhập username
        self.password_input = (By.ID, "password")  # ô nhập password
        self.login_button = (By.CLASS_NAME, "login-btn")
    # nút đăng nhập

    def open(self, url):
        self.driver.get(url)  # mở trang web đăng nhập

    def login(self, username, password):
        # Xoá nội dung cũ trong ô username và password
        self.driver.find_element(*self.username_input).clear()
        self.driver.find_element(*self.password_input).clear()

        # Chỉ nhập nếu có giá trị
        if username:
            self.driver.find_element(*self.username_input).send_keys(username)
        if password:
            self.driver.find_element(*self.password_input).send_keys(password)

        # Nhấn nút đăng nhập
        self.driver.find_element(*self.login_button).click()

    def get_alert_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()  # đóng alert
            return alert_text
        except:
            return ""  # Trường hợp không có alert

