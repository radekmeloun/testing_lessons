import tests.utils as utils


def test_flaky_function_succeeds_on_third_attempt():
    attempts = []
    # attempts lives in the enclosing scope (this test function), NOT inside flaky().
    # Each retry call sees the same list — it persists across attempts.
    # If it were inside flaky(), it would reset to [] on every call.

    @utils.retry(times=3)
    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ValueError("Simulated failure")
        return "success"

    result = flaky()
    assert result == "success"
    assert len(attempts) == 3  # confirms it took exactly 3 calls
