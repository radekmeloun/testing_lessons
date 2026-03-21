import pytest

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


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
