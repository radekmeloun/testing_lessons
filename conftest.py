import os
import pytest
from playwright.sync_api import sync_playwright

# headless=True in CI (no display), False locally for visual debugging
HEADLESS = os.getenv("CI", "false").lower() == "true"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()
