from selenium.webdriver.common.by import By

class RegisterPage:
    def __init__(self, driver):
        self.driver = driver
        self.username = (By.ID, "username")
        self.email = (By.ID, "email")
        self.password = (By.ID, "password")
        self.sdt = (By.ID, "phone")
        self.register_button = (By.XPATH, "//button[@class='login-btn' and text()='Đăng ký']")

    def open(self, url):
        self.driver.get(url)

    def register(self, username, email, password, sdt, ):
        self.driver.find_element(*self.username).clear()
        self.driver.find_element(*self.email).clear()
        self.driver.find_element(*self.password).clear()
        self.driver.find_element(*self.sdt).clear()

        if username:
            self.driver.find_element(*self.username).send_keys(username)
        if email:
            self.driver.find_element(*self.email).send_keys(email)
        if password:
            self.driver.find_element(*self.password).send_keys(password)
        if sdt:
            self.driver.find_element(*self.sdt).send_keys(sdt)

        self.driver.find_element(*self.register_button).click()

    def get_alert_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()  # đóng alert
            return alert_text
        except:
            return ""  # Trường hợp không có alert
