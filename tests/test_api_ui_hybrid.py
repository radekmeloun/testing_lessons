"""
API + UI hybrid pattern.

Step 1: Use the API to fetch/prepare data (fast, reliable)
Step 2: Use Playwright to verify that data is correctly displayed in the browser

In a real project, both steps would hit the same backend.
Here we simulate the pattern: API gives us the expected data,
UI test verifies a page renders correctly.
"""
import requests
import pytest

API_BASE = "https://jsonplaceholder.typicode.com"
UI_BASE = "https://practicetestautomation.com"


@pytest.fixture(scope="module")
def expected_post():
    """Fetch post data via API — this is our source of truth."""
    response = requests.get(f"{API_BASE}/posts/1")
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def expected_user():
    """Fetch user data via API before any UI interaction."""
    response = requests.get(f"{API_BASE}/users/1")
    assert response.status_code == 200
    return response.json()

@pytest.fixture(scope="function")
def new_user():
    # In a real project: POST to your auth API to create a test user,
    # yield the credentials, then DELETE the user in teardown.
    # Here both API and UI point to the same backend, so we simulate
    # that by returning the hardcoded credentials this demo site accepts.
    user = {"username": "student", "password": "Password123"}
    yield user
    # teardown: in a real project — requests.delete(f"{API_BASE}/users/{user['id']}")


def test_api_provides_user_with_email(expected_user):
    """
    API-only assertion: confirm the data contract before touching the UI.
    If this fails, there's no point running the UI test.
    """
    assert "email" in expected_user
    assert "@" in expected_user["email"]
    assert "name" in expected_user


def test_login_page_loads(page):
    """
    UI test: navigate to the login page and verify it renders.
    No API involved — pure UI check.
    """
    page.goto(f"{UI_BASE}/practice-test-login/")
    assert page.title() != ""
    assert page.locator("#username").is_visible()
    assert page.locator("#password").is_visible()


def test_successful_login_leads_to_success_page(page, new_user):
    """
    Hybrid: credentials could come from an API/auth service in a real project.
    Here we use known credentials, navigate via UI, verify the result.
    """

    page.goto(f"{UI_BASE}/practice-test-login/")
    page.locator("#username").fill(new_user["username"])
    page.locator("#password").fill(new_user["password"])
    page.locator("#submit").click()

    success = page.locator(".post-title")
    success.wait_for()
    assert "Logged In Successfully" in success.text_content()
