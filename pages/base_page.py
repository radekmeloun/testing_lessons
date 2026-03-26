from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


# Exception hierarchy — callers can catch PageError broadly or ElementNotFoundError
# specifically. Subclassing keeps related errors grouped under one base type.
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
        # `raise ... from e` chains exceptions — original cause is preserved.
        # text_content() returns str | None; assert narrows it for callers.
        try:
            text = self.page.locator(selector).text_content(timeout=3000)
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector) from e
        assert text is not None, f"Element '{selector}' returned no text"
        return text
