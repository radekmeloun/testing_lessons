class BasePage:
    def __init__(self, page):
        self.page = page

    def navigate(self, url):
        self.page.goto(url)

    def get_text(self, selector):
        try:
            return self.page.locator(selector).text_content(timeout=3000)
        except Exception as e:
            raise RuntimeError(
                f"Element '{selector}' not found on page: {self.page.url}"
                " or not visible within timeout."
            ) from e
