from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, url: str) -> None:
        self.page.goto(url)

    def get_text(self, selector: str) -> str:
        try:
            text = self.page.locator(selector).text_content(timeout=3000)
            # text_content() returns str | None — assert here so callers get str
            assert text is not None, f"Element '{selector}' returned no text"
            return text
        except Exception as e:
            raise RuntimeError(
                f"Element '{selector}' not found on page: {self.page.url}"
                " or not visible within timeout."
            ) from e
