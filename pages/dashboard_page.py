from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.header import HeaderComponent



class DashboardPage(BasePage):
    URL = "https://practicetestautomation.com/logged-in-successfully/"


    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Composition alongside inheritance — header is a separate component, not a
        # parent class. Use composition when the relationship is "has-a", not "is-a".
        self.header = HeaderComponent(page)

    def navigate(self, _url: str = "") -> None:  # overrides base navigate, uses own URL
        super().navigate(self.URL)

    def get_page_title(self) -> str:
        return self.get_text("h1")

    def is_logged_in(self) -> bool:
        return "logged-in-successfully" in self.page.url
