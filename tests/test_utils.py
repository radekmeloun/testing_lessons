import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

import tests.utils as utils
from pages.base_page import BasePage, ElementNotFoundError, PageError


def test_flaky_function_succeeds_on_third_attempt():
    # Closure: attempts is defined in the enclosing scope so it persists across retries.
    # If it were inside flaky(), it would reset to [] on every call.
    attempts = []

    @utils.retry(times=3)
    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ValueError("Simulated failure")
        return "success"

    result = flaky()
    assert result == "success"
    assert len(attempts) == 3  # confirms it took exactly 3 calls

def test_get_text_raises_element_not_found_on_timeout(mocker):
    page = mocker.Mock()
    page.locator.return_value.text_content.side_effect = PlaywrightTimeoutError(
        "Simulated timeout")
    base = BasePage(page)
    with pytest.raises(ElementNotFoundError, match="not found"):
        base.get_text("#missing")

def test_element_not_found_error_is_subclass_of_page_error():
    assert issubclass(ElementNotFoundError, PageError)
