from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


class PageError(Exception):
    pass

class ElementNotFoundError(PageError):
    def __init__(self, selector: str) -> None:
        super().__init__(f"Element '{selector}' "
                         "not found or not visible within timeout")

class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, url: str) -> None:
        self.page.goto(url)

    def get_text(self, selector: str) -> str:
        try:
            text = self.page.locator(selector).text_content(timeout=3000)
            # text_content() returns str | None — assert here so callers get str
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector) from e
        assert text is not None, f"Element '{selector}' returned no text"
        return text
