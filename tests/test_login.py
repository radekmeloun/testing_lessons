import pytest

import config
from tests.test_data import INVALID_LOGINS, VALID_LOGINS



@pytest.mark.skip(reason="not implemented yet")
def test_forgot_password():
    pass


@pytest.mark.regression
@pytest.mark.parametrize("login_data", INVALID_LOGINS)
def test_invalid_login(login_page, login_data):
    login_page.login(login_data.username, login_data.password)
    assert login_data.error in login_page.get_error_message()

@pytest.mark.regression
@pytest.mark.parametrize("login_data", VALID_LOGINS)
def test_valid_login_cases(login_page, login_data):
    # login_data is a dict (from VALID_LOGINS), not a dataclass — hence ["key"] access.
    login_page.login(login_data["username"], login_data["password"])
    assert login_page.is_logged_in()

# xfail — expected failure. pytest marks it XPASS if it starts passing, flagging a fix.
@pytest.mark.xfail
@pytest.mark.parametrize(
    # Tuple of names as first arg — parametrize unpacks each row into those parameters.
    ("empty_username", "empty_password", "expected_error"),
    [
        ("", "wrongpass", "Your username is empty!"),
        ("student", "", "Your password is empty!"),
    ],
)
def test_login_with_empty_fields(
    login_page, empty_username, empty_password, expected_error
):
    login_page.login(empty_username, empty_password)
    assert expected_error in login_page.get_error_message()


@pytest.mark.sanity
@pytest.mark.smoke
@pytest.mark.regression
def test_successful_login(login_page):
    login_page.login(config.USERNAME, config.PASSWORD)
    assert login_page.is_logged_in()
