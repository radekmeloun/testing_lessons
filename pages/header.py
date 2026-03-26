from playwright.sync_api import Page

from pages.base_page import BasePage


class HeaderComponent:
    """Reusable UI component — not a page, so it doesn't inherit BasePage.
    Uses composition: holds a BasePage instance to access shared helpers."""
    def __init__(self, page: Page) -> None:
        self.base = BasePage(page)

    def get_logo_text(self) -> str:
        return self.base.get_text(".site-title")
