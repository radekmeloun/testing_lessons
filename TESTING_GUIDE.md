# Playwright + pytest Testing Guide

A complete reference for this project covering all steps of the tutorial — usable both as project documentation and a study refresh.

**Tech stack:** Python, pytest, Playwright (sync API), requests, pytest-xdist, pytest-mock, allure-pytest
**Target site:** https://practicetestautomation.com
**Fake REST API:** https://jsonplaceholder.typicode.com

---

## Table of Contents

1. [Project structure](#1-project-structure)
2. [Setup and configuration](#2-setup-and-configuration)
3. [First Playwright test](#3-first-playwright-test)
4. [Page Object Model](#4-page-object-model)
5. [Fixtures and conftest.py](#5-fixtures-and-conftestpy)
6. [pytest features — parametrize, skip, xfail](#6-pytest-features--parametrize-skip-xfail)
7. [API testing with requests](#7-api-testing-with-requests)
8. [Advanced patterns](#8-advanced-patterns)
9. [Test organization — markers and mocking](#9-test-organization--markers-and-mocking)
10. [Test reporting — HTML and Allure](#10-test-reporting--html-and-allure)
11. [CI with GitHub Actions](#11-ci-with-github-actions)

---

## 1. Project structure

```
claude_lesson/
├── conftest.py              # root fixtures: browser, page
├── pytest.ini               # pytest config
├── config.py                # env-based credentials and BASE_URL
├── pages/                   # Page Object Model classes
│   ├── base_page.py
│   ├── login_page.py
│   └── dashboard_page.py
└── tests/
    ├── conftest.py          # test-level fixtures: login_page, dashboard_page
    ├── test_login.py
    ├── test_dashboard.py
    ├── test_data.py         # shared test data / dataclasses
    ├── test_api.py          # API-only tests
    └── test_api_ui_hybrid.py  # API + UI combined tests
```

**Key rule:** `conftest.py` fixtures are automatically available to all tests in the same directory and all subdirectories. No import needed.

---

## 2. Setup and configuration

### Virtual environment and dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest playwright pytest-playwright requests pytest-html pytest-xdist
playwright install chromium
```

### pytest.ini

```ini
[pytest]
testpaths = tests
addopts = --html=report.html --self-contained-html
```

- `testpaths` — pytest only looks in the `tests/` folder
- `addopts` — flags applied automatically to every run
- `--html=report.html` — generates an HTML report after each run

### config.py — environment-based credentials

```python
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USERNAME", "student")
PASSWORD = os.getenv("PASSWORD", "Password123")
BASE_URL = "https://practicetestautomation.com"
```

`os.getenv("KEY", "default")` reads from environment variables (or a `.env` file via `dotenv`). The second argument is a fallback used in local development. In CI you set the real values as environment secrets — the code never changes.

---

## 3. First Playwright test

### How Playwright's sync API works

Playwright has two Python APIs:
- **async** — requires `asyncio`, used for concurrent browser automation
- **sync** — blocking, simpler, used in most test suites with pytest

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
```

### Locator strategies

```python
page.locator("#id")                    # CSS: by ID
page.locator(".class")                 # CSS: by class
page.locator("button[type='submit']")  # CSS: attribute
page.get_by_text("Log in")             # by visible text
page.get_by_role("button", name="Submit")  # by ARIA role
page.get_by_label("Username")          # by label text
```

Prefer `get_by_role` and `get_by_label` — they reflect how users actually interact with the page and are more resilient to HTML changes.

### Basic interaction

```python
page.fill("#username", "student")   # clear + type
page.click("#submit")               # click
page.locator(".title").wait_for()   # wait until visible
text = page.locator("h1").text_content()
assert "Logged In" in text
```

---

## 4. Page Object Model

### Why POM

Without POM, selector strings like `"#username"` are scattered across all test files. When the selector changes, you update every test. With POM, each page has one class — selectors live in one place, tests only call methods.

### BasePage

```python
# pages/base_page.py
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
            ) from e
```

`BasePage` holds the `page` object and provides shared utility methods. All page classes inherit from it.

### LoginPage

```python
# pages/login_page.py
from pages.base_page import BasePage

class LoginPage(BasePage):
    URL = "https://practicetestautomation.com/practice-test-login/"

    def navigate(self):
        super().navigate(self.URL)   # calls BasePage.navigate with own URL

    def login(self, username, password):
        self.page.fill("#username", username)
        self.page.fill("#password", password)
        self.page.click("#submit")

    def get_error_message(self):
        return self.get_text("#error")   # reuses BasePage utility

    def is_logged_in(self):
        return self.page.url != self.URL
```

### DashboardPage

```python
# pages/dashboard_page.py
from pages.base_page import BasePage

class DashboardPage(BasePage):
    URL = "https://practicetestautomation.com/logged-in-successfully/"

    def navigate(self):
        super().navigate(self.URL)

    def get_page_title(self):
        return self.get_text("h1")

    def is_logged_in(self):
        return "logged-in-successfully" in self.page.url
```

### Using POM in tests

```python
def test_successful_login(login_page):
    login_page.login(config.USERNAME, config.PASSWORD)
    assert login_page.is_logged_in()
```

The test reads like a specification — no selectors, no implementation details.

---

## 5. Fixtures and conftest.py

### What fixtures are

Fixtures are functions that provide setup (and optionally teardown) to tests. pytest injects them automatically by matching the parameter name to the fixture name.

### Root conftest.py — browser and page

```python
# conftest.py (root)
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()
```

- `scope="session"` — one browser for the entire test run (fast)
- `page` has default scope (`function`) — fresh page per test (isolated)
- `yield` separates setup (before) from teardown (after)

### tests/conftest.py — page object fixtures

```python
# tests/conftest.py
import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

@pytest.fixture
def login_page(page):
    lp = LoginPage(page)
    lp.navigate()
    return lp

@pytest.fixture
def dashboard_page(page):
    dp = DashboardPage(page)
    dp.navigate()
    return dp
```

### Fixture scope

| Scope | Created once per... | Use when... |
|-------|--------------------|-|
| `function` | each test | tests must be fully isolated (default) |
| `module` | each test file | setup is slow, tests in same file share same state |
| `session` | entire test run | very expensive setup (e.g., browser launch) |

### yield fixtures — setup and teardown

```python
@pytest.fixture(scope="function")
def new_user():
    # SETUP
    user = create_user_via_api()
    yield user          # test receives `user` here
    # TEARDOWN — runs even if the test fails
    delete_user_via_api(user["id"])
```

Using `yield` instead of `return` allows cleanup code after the test. pytest guarantees teardown runs even when a test fails.

---

## 6. pytest features — parametrize, skip, xfail

### @pytest.mark.parametrize

Run the same test with multiple inputs:

```python
@pytest.mark.parametrize("post_id", [1, 2, 3, 50, 100])
def test_valid_post_returns_200(post_id):
    response = requests.get(f"{BASE_URL}/posts/{post_id}")
    assert response.status_code == 200
```

pytest runs this as 5 separate tests: `test_valid_post_returns_200[1]`, `[2]`, etc.

**Multiple parameters:**

```python
@pytest.mark.parametrize("title,body,user_id", [
    ("First post", "Body one", 1),
    ("Second post", "Body two", 2),
    ("",           "Empty title", 1),   # edge case
])
def test_create_post(title, body, user_id):
    ...
```

**Named test cases with `pytest.param`:**

```python
@pytest.mark.parametrize("login_data", [
    pytest.param(LoginCase(username="student", password="wrongpass", ...), id="invalid_password"),
    pytest.param(LoginCase(username="wronguser", password="Password123", ...), id="invalid_username"),
])
def test_invalid_login(login_page, login_data):
    ...
```

`id=` gives a readable name in the output instead of `login_data0`, `login_data1`.

### Dataclasses for structured test data

```python
# tests/test_data.py
from dataclasses import dataclass

@dataclass(frozen=True)
class LoginCase:
    username: str
    password: str
    error: str

INVALID_LOGINS = [
    pytest.param(LoginCase("student", "wrongpass", "Your password is invalid!"), id="invalid_password"),
    pytest.param(LoginCase("wronguser", "Password123", "Your username is invalid!"), id="invalid_username"),
]
```

`frozen=True` makes instances immutable — safe to share across tests. Putting test data in a separate file keeps test files readable and the data reusable.

### @pytest.mark.skip

```python
@pytest.mark.skip(reason="not implemented yet")
def test_forgot_password():
    pass
```

Test is not run and appears as `s` in output. Always provide a `reason`.

### @pytest.mark.xfail

```python
@pytest.mark.xfail
def test_login_with_empty_fields(login_page):
    ...
```

Marks a test as **expected to fail**. Results:
- Fails as expected → `x` (xfail) — not counted as failure
- Passes unexpectedly → `X` (xpass) — shown as a warning

Use for known bugs that aren't fixed yet — keeps the suite green while tracking the issue.

### Boundary value analysis and edge cases

```python
# Boundary value analysis — test at the edges of valid range
@pytest.mark.parametrize("post_id", [0, -1, 99999])
def test_invalid_post_returns_404(post_id):
    response = requests.get(f"{BASE_URL}/posts/{post_id}")
    assert response.status_code == 404

# Edge cases — unusual inputs
@pytest.mark.parametrize("title,body,user_id", [
    ("", "Empty title post", 1),   # empty string
])
def test_create_post_edge_cases(title, body, user_id):
    ...
```

Bugs hide at boundaries — zero, negative numbers, max values, empty strings. Always test just below, at, and just above the valid range.

---

## 7. API testing with requests

### Why API tests

| | API tests | UI tests |
|---|---|---|
| Speed | Fast — no browser | Slow — browser launch, renders |
| Stability | Stable — no visual changes | Fragile — CSS changes break tests |
| Scope | Data contracts, business logic | Visual layout, user interaction |
| When to use | Verify backend returns correct data | Verify data is displayed correctly |

Use both: API tests to validate the data layer, UI tests to validate the presentation layer.

### Basic GET request

```python
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

def test_get_posts_returns_200():
    response = requests.get(f"{BASE_URL}/posts")
    assert response.status_code == 200

def test_get_posts_returns_list():
    response = requests.get(f"{BASE_URL}/posts")
    posts = response.json()
    assert isinstance(posts, list)
    assert len(posts) == 100
```

### Data contract testing

Verify both field existence and field types:

```python
def test_post_has_correct_fields(post):
    first = post[0]
    # existence
    assert "id" in first
    assert "title" in first
    assert "body" in first
    assert "userId" in first
    # types
    assert isinstance(first["id"], int)
    assert isinstance(first["title"], str)
    assert isinstance(first["body"], str)
    assert isinstance(first["userId"], int)
```

Separating existence and type checks in the same test is intentional — one request, complete contract validation.

### POST request

```python
def test_create_post():
    payload = {"title": "Test Post", "body": "Test body", "userId": 1}
    response = requests.post(f"{BASE_URL}/posts", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == payload["title"]
    assert created["body"] == payload["body"]
```

### Module-scoped fixture for shared API data

```python
@pytest.fixture(scope="module")
def post():
    response = requests.get(f"{BASE_URL}/posts")
    return response.json()

def test_get_posts_returns_list(post):
    assert isinstance(post, list)

def test_post_has_correct_fields(post):
    first = post[0]
    assert "id" in first
```

`scope="module"` means one API call for all tests in the file that use this fixture. Use when the data doesn't change between tests.

---

## 8. Advanced patterns

### API + UI hybrid

The pattern: **API fetches/creates data → Playwright verifies it is displayed correctly.**

Benefits:
- API setup is fast, reliable, and precise
- The UI test focuses only on the visual layer — not on creating test data
- When the UI changes, only the UI test breaks, not the data setup

```python
# tests/test_api_ui_hybrid.py
import requests
import pytest

API_BASE = "https://jsonplaceholder.typicode.com"
UI_BASE  = "https://practicetestautomation.com"

@pytest.fixture(scope="module")
def expected_user():
    """Source of truth — fetch from API before touching the UI."""
    response = requests.get(f"{API_BASE}/users/1")
    assert response.status_code == 200
    return response.json()

def test_api_provides_user_with_email(expected_user):
    """Validate data contract first. If this fails, skip the UI test."""
    assert "email" in expected_user
    assert "@" in expected_user["email"]

def test_login_page_loads(page):
    """Pure UI check — page renders, inputs are visible."""
    page.goto(f"{UI_BASE}/practice-test-login/")
    assert page.locator("#username").is_visible()
    assert page.locator("#password").is_visible()

@pytest.fixture(scope="function")
def new_user():
    """
    In a real project: POST to auth API → yield credentials → DELETE on teardown.
    Here: return known-good credentials for the demo site.
    """
    user = {"username": "student", "password": "Password123"}
    yield user
    # real teardown: requests.delete(f"{API_BASE}/users/{user['id']}")

def test_successful_login_leads_to_success_page(page, new_user):
    """Hybrid: credentials from API setup, verification via UI."""
    page.goto(f"{UI_BASE}/practice-test-login/")
    page.locator("#username").fill(new_user["username"])
    page.locator("#password").fill(new_user["password"])
    page.locator("#submit").click()

    success = page.locator(".post-title")
    success.wait_for()
    assert "Logged In Successfully" in success.text_content()
```

**Real-world version of `new_user`:**

```python
@pytest.fixture(scope="function")
def new_user():
    # Create a fresh user via API
    payload = {"username": "testuser", "password": "Pass123", "email": "t@test.com"}
    create_response = requests.post(f"{API_BASE}/users", json=payload)
    assert create_response.status_code == 201
    user = create_response.json()

    yield user   # test runs here

    # Clean up — guaranteed to run even if test fails
    requests.delete(f"{API_BASE}/users/{user['id']}")
```

### Fixture scope decision for test data

- `function` — maximum isolation, fresh data per test. Use by default.
- `module` — shared across the file, faster. Use when data is read-only and tests can't affect each other.
- `session` — shared for the entire run. Use only for very expensive, read-only setup.

### Parallel test runs with pytest-xdist

Install:

```bash
pip install pytest-xdist
```

Run tests in parallel:

```bash
pytest tests/ -n auto -v     # auto = number of CPU cores
pytest tests/ -n 4 -v        # fixed 4 workers
```

xdist splits tests across worker processes. Each worker is a separate Python process with its own browser instance — there is no shared browser state between workers.

**What can break in parallel:**

| Problem | Example | Fix |
|---|---|---|
| Shared external state | Two tests create a user with the same username | Use unique IDs per test (UUID, timestamp) |
| Shared database rows | Test A deletes a record Test B was reading | Use `function` scope fixtures that own their data |
| Shared files | Two tests write to the same temp file | Use `tmp_path` fixture (unique per test) |
| Order-dependent tests | Test B assumes Test A ran first | Each test must be fully independent |

**Tests that should not run in parallel:**

```python
@pytest.mark.no_parallel   # custom marker — exclude in xdist config
def test_that_modifies_global_state():
    ...
```

Or in `pytest.ini`:

```ini
[pytest]
addopts = --html=report.html
```

And run without `-n` for specific files:

```bash
pytest tests/test_sequential.py          # sequential
pytest tests/test_api.py -n auto         # parallel
```

---

## 9. Test organization — markers and mocking

### Custom markers

Register markers in `pytest.ini` to avoid warnings and document their purpose:

```ini
[pytest]
markers =
    sanity: basic happy path — successful login and core flow
    smoke: broader happy path coverage across main features
    regression: full relevant test suite excluding flaky/one-time tests
```

Apply multiple markers to one test — a test can belong to several layers:

```python
@pytest.mark.sanity
@pytest.mark.smoke
@pytest.mark.regression
def test_successful_login(login_page):
    login_page.login(config.USERNAME, config.PASSWORD)
    assert login_page.is_logged_in()

@pytest.mark.regression
def test_invalid_login(login_page, login_data):
    ...
```

Run subsets:

```bash
pytest -m sanity       # deploy confidence check (~30s)
pytest -m smoke        # pre-release check
pytest -m regression   # full nightly suite
pytest -m "smoke and not regression"
pytest -m "not flaky"
```

### CI pipeline mapping

| Pipeline stage | Marker | When to run |
|---|---|---|
| deploy | `sanity` | after every deploy — fast, basic confidence |
| pre-release | `smoke` | before releasing — broader coverage |
| nightly | `regression` | scheduled, no time pressure — full suite |

Keep separate `--alluredir` per stage so each stage has its own report:

```bash
pytest -m sanity     --alluredir=allure-results/sanity
pytest -m smoke      --alluredir=allure-results/smoke
pytest -m regression --alluredir=allure-results/regression
```

### Mocking with pytest-mock

`mocker.patch` replaces a Python object in memory for the duration of one test — no network call happens. After the test finishes, the original is restored automatically.

```text
without mock: test → requests.post() → network → real server → real response
with mock:    test → requests.post() → mock object → your fake response
```

Install:

```bash
pip install pytest-mock
```

**Basic mock:**

```python
def test_create_post_mocked(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 101, "title": "Test Post", "body": "Test body", "userId": 1
    }

    mocker.patch("requests.post", return_value=mock_response)

    response = requests.post(f"{BASE_URL}/posts", json={"title": "Test Post"})

    assert response.status_code == 201
    assert response.json()["id"] == 101
```

**Testing error paths — impossible without mocking:**

```python
def test_api_failure_handling(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 500

    mocker.patch("requests.post", return_value=mock_response)

    response = requests.post(f"{BASE_URL}/posts", json={})
    assert response.status_code == 500
```

You can't make a real server return 500 on demand — mocking is the only reliable way to test error handling.

**Verifying the mock was called with correct arguments:**

```python
def test_create_post_called_with_correct_payload(mocker):
    mock_post = mocker.patch("requests.post", return_value=mocker.Mock(status_code=201))

    payload = {"title": "Test Post", "body": "Test body", "userId": 1}
    requests.post(f"{BASE_URL}/posts", json=payload)

    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["json"]["title"] == "Test Post"
```

Use this when the function under test makes the API call internally — you want to verify it sent the right payload, not just that it returned the right thing.

### Real API tests vs mocked tests

| | Real API test | Mocked test |
|---|---|---|
| Tests | External system behaviour | Your code's logic |
| Fails when | API is down, contract changed | Your code is broken |
| Use for | Contract validation, integration | Unit logic, error paths, CI speed |

Use both. The danger of mocking everything is mock drift — mocks pass while production breaks because the real API changed and the mocks weren't updated.

---

## 10. Test reporting — HTML and Allure

### Built-in HTML report

Configured in `pytest.ini`:

```ini
addopts = --html=report.html --self-contained-html
```

Generated automatically after every run. `--self-contained-html` embeds all assets into one file — easy to share.

### Allure

Industry-standard reporting with history, screenshots, steps, and timings.

Install:

```bash
pip install allure-pytest
sudo snap install allure        # or via manual install
```

Collect results during test run:

```bash
pytest tests/ --alluredir=allure-results
```

Generate and open report:

```bash
allure serve allure-results
```

Allure opens a local web server with a full dashboard including pass/fail trends, test duration breakdown, and categorized failures.

---

## 11. CI with GitHub Actions

### Workflow structure

Workflows live in `.github/workflows/`. Each is a YAML file that defines when to run and what steps to execute.

Three workflows in this project, one per test stage:

| File | Trigger | Marker |
|---|---|---|
| `sanity.yml` | pull request to `main` | `sanity` |
| `smoke.yml` | push to `release` branch | `smoke` |
| `regression.yml` | nightly at 02:00 UTC + manual | `regression` |

### Sanity workflow (example)

```yaml
name: Sanity check

on:
  pull_request:
    branches: [main]

jobs:
  sanity:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium --with-deps

      - name: Run sanity tests
        run: pytest -m sanity --alluredir=allure-results/sanity
        env:
          USERNAME: ${{ secrets.APP_USERNAME }}
          PASSWORD: ${{ secrets.APP_PASSWORD }}

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: sanity-results
          path: allure-results/sanity/
```

### Key decisions explained

**`if: always()` on upload** — artifacts are uploaded even when tests fail. Without this, a failing run produces no report — exactly when you need it most.

**`secrets.APP_USERNAME` / `APP_PASSWORD`** — credentials never live in code. Set them in GitHub → Settings → Secrets and variables → Actions. The workflow reads them as environment variables matching what `config.py` expects via `os.getenv()`.

**`workflow_dispatch` on regression** — allows manual trigger from the GitHub UI without waiting for the nightly schedule. Useful before a big release.

**`playwright install chromium --with-deps`** — installs system-level browser dependencies on the Ubuntu runner. Required because GitHub Actions environments don't have them by default.

### Headless mode in CI

GitHub Actions has no display server (`$DISPLAY` is not set). Running Playwright with `headless=False` crashes the browser. The fix uses the `CI` environment variable that GitHub Actions sets automatically on every runner:

```python
# conftest.py
import os

HEADLESS = os.getenv("CI", "false").lower() == "true"

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        yield browser
        browser.close()
```

- **Locally:** `CI` is not set → `headless=False` → browser opens visually
- **In CI:** `CI=true` → `headless=True` → no display needed

### requirements.txt — single source of truth for dependencies

Generate from your local venv:

```bash
pip freeze | grep -E "pytest|playwright|requests|dotenv|allure|mock" > requirements.txt
```

Install locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

CI installs identically:

```yaml
pip install -r requirements.txt
playwright install chromium --with-deps
```

This guarantees local and CI environments use the same package versions — a mismatch here is a common source of "works on my machine" failures.

### Nightly schedule syntax (cron)

```yaml
on:
  schedule:
    - cron: "0 2 * * *"   # every day at 02:00 UTC
  workflow_dispatch:        # also allow manual trigger
```

Cron format: `minute hour day month weekday`

- `"0 2 * * *"` — 02:00 UTC every day
- `"0 6 * * 1"` — 06:00 UTC every Monday
- `"*/30 * * * *"` — every 30 minutes

---

## Quick reference

### Running tests

```bash
# all tests
pytest

# specific file
pytest tests/test_login.py

# specific test
pytest tests/test_login.py::test_successful_login

# by marker
pytest -m smoke

# parallel
pytest -n auto

# verbose
pytest -v

# stop on first failure
pytest -x

# show locals on failure
pytest -l
```

### Fixture scope cheatsheet

```python
@pytest.fixture                    # scope="function" (default)
@pytest.fixture(scope="module")
@pytest.fixture(scope="session")
```

### Marker cheatsheet

```python
@pytest.mark.skip(reason="...")    # never run
@pytest.mark.xfail                 # expected to fail
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.smoke                 # custom marker
```
