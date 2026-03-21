# CLAUDE.md — testing_lessons project context

## Who the user is

User is learning test automation with Python. They have solid conceptual understanding — they answer "why" questions correctly before seeing the code — but are building practical hands-on experience. They think in risk-based layers (sanity/smoke/regression) and reason well about tradeoffs (e.g. fixture scope, mock vs real API). Not a beginner but not yet fluent in Python idioms.

**Next focus:** Python-specific programming skills using this project as the practice ground.

---

## How to guide sessions

- **Ask a conceptual question before showing code.** User consistently answers well. This confirms understanding rather than just copying patterns.
- **Keep explanations concise.** They read code and diffs — no need to narrate every line.
- **Use the project's own code as examples.** Don't invent hypothetical snippets when the real code is available.
- **Correct wrong answers precisely.** When they swap two concepts (e.g. smoke vs regression stage), point to their own earlier definition and correct just that part.
- **Validate good instincts explicitly.** They make good judgment calls (e.g. `function` scope for isolation, merging two assertion groups into one test). Confirm these so they internalise them.
- **Surface tradeoffs, not just answers.** For every pattern, name what it costs (e.g. `function` scope = more API calls; mocking = mock drift risk).

---

## Project structure

```text
testing_lessons/
├── CLAUDE.md                  # this file
├── TESTING_GUIDE.md           # full tutorial reference (Steps 1–11)
├── conftest.py                # root fixtures: browser (session), page (function)
├── pyproject.toml             # Ruff, Pytest, Mypy config — single source of truth for tooling
├── config.py                  # credentials via os.getenv + dotenv fallback
├── requirements.txt           # pinned dependencies — source of truth for local + CI
├── pages/                     # Page Object Model
│   ├── base_page.py           # BasePage: navigate(), get_text() with error wrapping
│   ├── login_page.py          # LoginPage: login(), get_error_message(), is_logged_in()
│   └── dashboard_page.py      # DashboardPage: get_page_title(), is_logged_in()
├── tests/
│   ├── conftest.py            # login_page, dashboard_page fixtures
│   ├── test_data.py           # LoginCase dataclass + INVALID_LOGINS list
│   ├── test_login.py          # UI login tests — parametrize, skip, xfail
│   ├── test_dashboard.py      # UI dashboard test
│   ├── test_api.py            # API tests — GET/POST, data contracts, boundary values
│   ├── test_api_mocked.py     # Mocked API tests — mocker.patch, assert_called_once
│   └── test_api_ui_hybrid.py  # API setup + UI verification pattern
└── .github/workflows/
    ├── sanity.yml             # trigger: PR to main + manual
    ├── smoke.yml              # trigger: push to release + manual
    └── regression.yml         # trigger: nightly cron + manual
```

---

## Established conventions

### Markers (registered in pyproject.toml)

- `sanity` — happy path only, runs on every PR (~30s)
- `smoke` — broader happy path, runs on push to `release` branch
- `regression` — full suite, nightly at 02:00 UTC
- `flaky` — known intermittent tests, excluded from CI with `-m "not flaky"`

A test can carry multiple markers. `sanity` tests always also get `smoke` and `regression`.

### Fixture scope rules

- Default to `function` scope — full isolation per test
- Use `module` only for read-only shared data (e.g. API response reused across the file)
- Use `session` only for expensive one-time setup (browser launch)
- Always use `yield` when teardown is needed — pytest guarantees it runs even on failure

### CI headless detection

```python
HEADLESS = os.getenv("CI", "false").lower() == "true"
```

GitHub Actions sets `CI=true` automatically. No workflow change needed — local runs open the browser visually.

### Allure reports on GitHub Pages

Each workflow stage publishes to a separate subfolder:

- <https://radekmeloun.github.io/testing_lessons/sanity/>
- <https://radekmeloun.github.io/testing_lessons/smoke/>
- <https://radekmeloun.github.io/testing_lessons/regression/>

Run history is preserved by copying `gh-pages/<stage>/history/` into `allure-results/history/` before generation.

---

## Key design decisions made during the tutorial

| Decision | Rationale |
| --- | --- |
| Sync Playwright API (not async) | Simpler with pytest, no asyncio needed |
| `BasePage` with `get_text()` wrapping | Unified error messages with page URL context |
| `frozen=True` dataclass for test data | Immutable, safe to share across parametrize |
| `pytest.param(..., id=)` for named cases | Readable test names in output and reports |
| `scope="module"` for API fixture | One network call shared across the file |
| `scope="function"` for user creation fixture | Full isolation — each test owns its data |
| Separate `requirements.txt` | Dependencies for local venv and CI |
| `pyproject.toml` for tooling | Ruff + Pytest + Mypy config in one place (replaced `pytest.ini`) |
| `if: always()` on upload/deploy steps | Reports generated even when tests fail |

---

## Target site and APIs

- **UI:** <https://practicetestautomation.com/practice-test-login/>
  - Valid credentials: `student` / `Password123`
  - Success page: `.post-title` contains "Logged In Successfully"
- **Fake REST API:** <https://jsonplaceholder.typicode.com>
  - Used for API testing practice — GET /posts, POST /posts, GET /users
  - Note: POST returns 201 but doesn't persist data

---

## Running tests locally

```bash
# install
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# run
pytest                          # full suite
pytest -m sanity                # sanity only
pytest -m regression -n auto    # regression in parallel
pytest tests/test_api.py -v     # specific file
allure serve allure-results     # view report locally
```

---

## Git workflow

Always work on a feature branch — never commit directly to `main`.

```bash
git checkout -b <branch-name>   # create and switch to branch
# ... make changes, commit ...
git push -u origin <branch-name>
# then open a PR on GitHub — sanity workflow will run automatically
```

Branch naming convention used in this project: `type/short-description`

- `feat/add-payment-tests`
- `fix/login-timeout`
- `ci/update-workflows`

**Never** use `git push` to `main` directly. The sanity check runs on PRs — pushing directly to main bypasses it.

---

## What to focus on next (Python skills practice)

Using this project as the base, areas to develop:

1. **Python data structures** — refactor test data using dicts, lists, generators
2. **Comprehensions and functional tools** — `map`, `filter`, `zip` applied to test datasets
3. **Context managers** — write custom ones (e.g. timed test blocks, temp file cleanup)
4. **Decorators** — build custom pytest markers or retry decorators from scratch
5. **Type hints** — add annotations to page objects and fixtures
6. **Exception handling** — improve `BasePage.get_text()` with custom exception hierarchy
7. **Generators** — use `yield`-based data generators for parametrize inputs
8. **OOP patterns** — extend POM with more page classes, explore composition vs inheritance

---

## Coding style

All rules are enforced via Ruff — see `pyproject.toml` for the active rule-sets. This section explains *intent*.

- **PEP 8** enforced automatically (E, W, N rule-sets).
- **Type hints** on all function signatures. Use `X | None` instead of `Optional[X]`.
  - Playwright types: `page: Page`, `browser: Browser`, `context: BrowserContext`.
- **No bare `try/except`** — always catch a specific exception.
- **No `type: ignore`** without an inline comment explaining *why*.
- **Constants** in `UPPER_SNAKE_CASE` at module level.
- **f-strings** over `format()` or `%` — Ruff's `UP` rules enforce this.

```python
# ✅ Good — specific exception, clear intent
try:
    response = client.get(url, timeout=10)
    response.raise_for_status()
except requests.HTTPError as exc:
    logger.error("Request failed: %s", exc)
    raise

# ❌ Bad — swallows everything, hides bugs
try:
    response = client.get(url)
except Exception:
    pass
```

### Imports

Ruff `I` (isort) handles ordering automatically:

1. Standard library
2. Third-party (`playwright`, `pytest`, `requests`, …)
3. Local (`pages/` Page Objects, helpers)

Never use wildcard imports (`from module import *`).

---

## Playwright-specific rules

### Locators — always prefer semantic selectors

```python
# ✅ Good — resilient, readable
page.get_by_role("button", name="Submit")
page.get_by_label("Email address")
page.get_by_text("Welcome back")

# ❌ Bad — brittle, tied to DOM structure
page.locator("#btn-submit")
page.locator("div.form > button:nth-child(2)")
```

Priority: `get_by_role` > `get_by_label` > `get_by_text` > `get_by_test_id` > CSS/XPath.

### Assertions — always use `expect()`

```python
from playwright.sync_api import expect

# ✅ Good — auto-retrying, clear error messages
expect(page.get_by_text("Dashboard")).to_be_visible()
expect(page.get_by_role("alert")).to_have_text("Saved")
expect(page).to_have_url("/dashboard")

# ❌ Bad — no retry, race conditions
assert page.is_visible("text=Dashboard")
assert "dashboard" in page.url
```

### Waits — never use arbitrary timeouts

```python
# ✅ Good — event-based, deterministic
page.wait_for_url("**/dashboard")
expect(page.get_by_text("Loaded")).to_be_visible(timeout=10_000)

# ❌ Bad — arbitrary sleep, flaky
page.wait_for_timeout(3000)
import time; time.sleep(2)
```

---

## Testing rules (Pytest)

- **Fixtures over setup/teardown** — Ruff `PT` enforces this.
- **`pytest.raises`** for expected exceptions — never wrap assertions in `try/except`.
- **Descriptive test names**: `test_<what>_<condition>_<expected>`.
- **Factory fixtures** for reusable test data — return a callable, not a static value.
- **Teardown via `yield`** — clean up resources after the yield in fixtures.
- **No `try/except` in tests** — let exceptions propagate; pytest reports them clearly.

```python
# ✅ Good — clear, uses fixtures, descriptive name
def test_login_with_invalid_password_shows_error(login_page):
    login_page.login("student", "wrong")
    assert "Your password is invalid!" in login_page.get_error_message()

# ❌ Bad — try/except in test, vague name
def test_login(login_page):
    try:
        login_page.login("student", "wrong")
        assert login_page.get_error_message()
    except Exception:
        pytest.fail("Login failed")
```

---

## Workflow — quality checks

Before committing code, run all three steps in order:

```bash
# 1. Auto-format
ruff format .

# 2. Lint + auto-fix
ruff check --fix .

# 3. Run tests
pytest
```

Quick check during development: `ruff check . && pytest -m sanity`

---

## What NOT to do

- Do not add `setup.cfg`, `.flake8`, `.isort.cfg`, or `black.toml` — Ruff replaces all of them.
- Do not use `unittest.TestCase` — use plain pytest functions and fixtures.
- Do not use `page.wait_for_timeout()` or `time.sleep()` — use `expect()` or event-based waits.
- Do not use CSS/XPath selectors when a semantic locator exists.
- Do not put locator strings directly in tests — use Page Objects.
- Do not silence linter warnings without a comment explaining the reason.
- Do not commit code that fails `ruff check` or `pytest`.
