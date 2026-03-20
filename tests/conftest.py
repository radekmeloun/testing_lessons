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