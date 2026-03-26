from playwright.sync_api import Page

from pages.base_page import BasePage


class HeaderComponent:
    """Reusable component for the site header — not a full page."""
    def __init__(self, page: Page) -> None:
        self.base = BasePage(page)

    def get_logo_text(self) -> str:
        return self.base.get_text(".site-title")
