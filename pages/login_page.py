from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "https://practicetestautomation.com/practice-test-login/"

    def navigate(self):  # overrides base, uses own URL
        super().navigate(self.URL)

    def login(self, username, password):
        self.page.fill("#username", username)
        self.page.fill("#password", password)
        self.page.click("#submit")

    def forgot_password(self, username, password):
        self.page.fill("#username", username)
        self.page.fill("#password", password)
        self.page.click("#forgot-password")

    def get_error_message(self):  # uses base method
        return self.get_text("#error")

    def is_logged_in(self):
        return self.page.url != self.URL
