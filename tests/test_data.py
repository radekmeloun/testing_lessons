from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class LoginCase:
    username: str
    password: str
    error: str


INVALID_LOGINS = [
    pytest.param(
        LoginCase(
            username="student", password="wrongpass", error="Your password is invalid!"
        ),
        id="invalid_password",
    ),
    pytest.param(
        LoginCase(
            username="wronguser",
            password="Password123",
            error="Your username is invalid!",
        ),
        id="invalid_username",
    ),
]
