from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "https://practicetestautomation.com/practice-test-login/"

    def navigate(self, _url: str = "") -> None:  # overrides base, uses own URL
        super().navigate(self.URL)

    def login(self, username: str, password: str) -> None:
        self.page.fill("#username", username)
        self.page.fill("#password", password)
        self.page.click("#submit")

    def forgot_password(self, username: str, password: str) -> None:
        self.page.fill("#username", username)
        self.page.fill("#password", password)
        self.page.click("#forgot-password")

    def get_error_message(self) -> str:  # uses base method
        return self.get_text("#error")

    def is_logged_in(self) -> bool:
        return self.page.url != self.URL
