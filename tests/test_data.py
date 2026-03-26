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
    # Plain dict vs dataclass: dicts are flexible but untyped — login_data["username"]
    # vs login_data.username. No enforcement of required fields at definition time.
    {"username": "student", "password": "Password123", "description": "valid_login"}
]

# List comprehension — extracts one field from each pytest.param.
# p.values[0] unwraps the LoginCase stored inside pytest.param(...).
INVALID_USERNAMES = [p.values[0].username for p in INVALID_LOGINS]

INVALID_ERRORS = [p.values[0].error for p in INVALID_LOGINS]

# Set comprehension — same syntax as list comprehension but {} deduplicates.
UNIQUE_ERRORS = {p.values[0].error for p in INVALID_LOGINS}

# Module-level assert runs at import time (during pytest collection), not at test time.
# Acts as a structural guard: if INVALID_LOGINS grows but extraction breaks, fails fast.
assert len(INVALID_USERNAMES) == len(INVALID_LOGINS)


# Generator function — `yield` makes iteration lazy: values are produced one at a time,
# not stored in memory. parametrize consumes the generator fully at collection time.
def generate_post_ids(start: int, end: int):
    for post_id in range(start, end + 1):
        if post_id % 10 != 0:
            yield post_id
