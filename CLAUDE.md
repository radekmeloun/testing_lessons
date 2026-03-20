# CLAUDE.md — testing_lessons project context

## Who the user is

Radek is learning test automation with Python. He has solid conceptual understanding — he answers "why" questions correctly before seeing the code — but is building practical hands-on experience. He thinks in risk-based layers (sanity/smoke/regression) and reasons well about tradeoffs (e.g. fixture scope, mock vs real API). He is not a beginner but is not yet fluent in Python idioms.

**Next focus:** Python-specific programming skills using this project as the practice ground.

---

## How to guide sessions with Radek

- **Ask a conceptual question before showing code.** He consistently answers well. This confirms understanding rather than just copying patterns.
- **Keep explanations concise.** He reads code and diffs — no need to narrate every line.
- **Use the project's own code as examples.** Don't invent hypothetical snippets when the real code is available.
- **Correct wrong answers precisely.** When he swaps two concepts (e.g. smoke vs regression stage), point to his own earlier definition and correct just that part.
- **Validate good instincts explicitly.** He makes good judgment calls (e.g. `function` scope for isolation, merging two assertion groups into one test). Confirm these so he internalises them.
- **Surface tradeoffs, not just answers.** For every pattern, name what it costs (e.g. `function` scope = more API calls; mocking = mock drift risk).

---

## Project structure

```
testing_lessons/
├── CLAUDE.md                  # this file
├── TESTING_GUIDE.md           # full tutorial reference (Steps 1–11)
├── conftest.py                # root fixtures: browser (session), page (function)
├── pytest.ini                 # testpaths, addopts, markers registered here
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

### Markers (registered in pytest.ini)
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
- https://radekmeloun.github.io/testing_lessons/sanity/
- https://radekmeloun.github.io/testing_lessons/smoke/
- https://radekmeloun.github.io/testing_lessons/regression/

Run history is preserved by copying `gh-pages/<stage>/history/` into `allure-results/history/` before generation.

---

## Key design decisions made during the tutorial

| Decision | Rationale |
|---|---|
| Sync Playwright API (not async) | Simpler with pytest, no asyncio needed |
| `BasePage` with `get_text()` wrapping | Unified error messages with page URL context |
| `frozen=True` dataclass for test data | Immutable, safe to share across parametrize |
| `pytest.param(..., id=)` for named cases | Readable test names in output and reports |
| `scope="module"` for API fixture | One network call shared across the file |
| `scope="function"` for user creation fixture | Full isolation — each test owns its data |
| Separate `requirements.txt` | Single source of truth for local venv and CI |
| `if: always()` on upload/deploy steps | Reports generated even when tests fail |

---

## Target site and APIs

- **UI:** https://practicetestautomation.com/practice-test-login/
  - Valid credentials: `student` / `Password123`
  - Success page: `.post-title` contains "Logged In Successfully"
- **Fake REST API:** https://jsonplaceholder.typicode.com
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
