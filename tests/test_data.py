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

VALID_LOGINS = [
    {"username": "student", "password": "Password123", "description": "valid_login"}
    # Add more valid login cases as needed
]

INVALID_USERNAMES = [p.values[0].username for p in INVALID_LOGINS]

INVALID_ERRORS = [p.values[0].error for p in INVALID_LOGINS]

UNIQUE_ERRORS = {p.values[0].error for p in INVALID_LOGINS}

assert len(INVALID_USERNAMES) == len(INVALID_LOGINS)

def generate_post_ids(start: int, end: int):
    # yields each integer from start to end inclusive
    # skip any ID divisible by 10 (simulate "reserved" IDs)
    for post_id in range(start, end + 1):
        if post_id % 10 != 0:
            yield post_id
