from pages.base_page import BasePage


class DashboardPage(BasePage):
    URL = "https://practicetestautomation.com/logged-in-successfully/"

    def navigate(self, _url: str = "") -> None:  # overrides base, uses own URL
        super().navigate(self.URL)

    def get_page_title(self) -> str:
        return self.get_text("h1")  # overrides base, uses own URL

    def is_logged_in(self) -> bool:
        return "logged-in-successfully" in self.page.url
