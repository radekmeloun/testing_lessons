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
    # Session 1: plain dicts alongside the dataclass — flexible, no enforced structure.
    # Call site: login_data["username"] vs login_data.username for dataclass.
    {"username": "student", "password": "Password123", "description": "valid_login"}
]

# Session 2: list comprehensions — extract a single field from each pytest.param.
# p.values[0] unwraps the LoginCase stored inside pytest.param(...).
INVALID_USERNAMES = [p.values[0].username for p in INVALID_LOGINS]

INVALID_ERRORS = [p.values[0].error for p in INVALID_LOGINS]

# Set comprehension — {expr for item in iterable} — deduplicates automatically.
# Use {} instead of [] to get a set directly, no need to wrap in set().
UNIQUE_ERRORS = {p.values[0].error for p in INVALID_LOGINS}

# Module-level assert — runs at import time (during pytest collection).
# Structural guard: if INVALID_LOGINS grows but extraction breaks, fails fast.
assert len(INVALID_USERNAMES) == len(INVALID_LOGINS)


# Session 7: generator function — `yield` makes this lazy.
# Unlike a list, no values are stored in memory upfront.
# Each value is produced only when the caller asks for the next one.
# Can only be iterated once — fine here, parametrize consumes it at collection time.
def generate_post_ids(start: int, end: int):
    for post_id in range(start, end + 1):
        if post_id % 10 != 0:
            yield post_id  # pauses here, returns post_id, resumes on next iteration
