# testing_lessons

A Python test automation framework built with Playwright and pytest, covering UI testing, API testing, mocking, CI/CD integration, and reporting.

## Stack

- **Python 3.12**
- **Playwright** — browser automation (sync API)
- **pytest** — test runner, fixtures, parametrize
- **requests** — API testing
- **pytest-mock** — mocking
- **pytest-xdist** — parallel test execution
- **Allure** — test reporting

## Project structure

```text
├── conftest.py              # root fixtures: browser, page
├── pytest.ini               # test config and custom markers
├── config.py                # credentials via environment variables
├── requirements.txt         # pinned dependencies
├── pages/                   # Page Object Model
│   ├── base_page.py
│   ├── login_page.py
│   └── dashboard_page.py
└── tests/
    ├── conftest.py          # page object fixtures
    ├── test_data.py         # shared test data (dataclasses)
    ├── test_login.py        # UI login tests
    ├── test_dashboard.py    # UI dashboard tests
    ├── test_api.py          # API contract tests
    ├── test_api_mocked.py   # mocked API tests
    └── test_api_ui_hybrid.py  # API setup + UI verification
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env` and set credentials (or export them directly):

```bash
export USERNAME=student
export PASSWORD=Password123
```

## Running tests

```bash
pytest                           # full suite
pytest -m sanity                 # quick confidence check (~30s)
pytest -m smoke                  # broader pre-release check
pytest -m regression             # full suite
pytest -m regression -n auto     # full suite in parallel
pytest tests/test_api.py -v      # specific file
```

## Test reports

Generate and view an Allure report locally:

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

Live reports published to GitHub Pages after each CI run:

- [Sanity](https://radekmeloun.github.io/testing_lessons/sanity/)
- [Smoke](https://radekmeloun.github.io/testing_lessons/smoke/)
- [Regression](https://radekmeloun.github.io/testing_lessons/regression/)

## CI/CD

Three GitHub Actions workflows:

| Workflow | Trigger | Marker |
| --- | --- | --- |
| Sanity check | Pull request to `main` | `sanity` |
| Smoke check | Push to `release` branch | `smoke` |
| Regression suite | Nightly 02:00 UTC + manual | `regression` |

All workflows publish Allure reports to GitHub Pages with run history.

## Contributing

Always work on a feature branch — never push directly to `main`:

```bash
git checkout -b feat/your-feature
# make changes and commit
git push -u origin feat/your-feature
# open a PR — sanity check runs automatically
```

## Reference

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for full documentation of all patterns, decisions, and concepts covered in this project.
