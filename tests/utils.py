
import functools
import time
from contextlib import contextmanager


@contextmanager
def timed_block(label: str):
    start = time.time()   # 1. runs on enter
    try:
        yield             # 2. pauses here — test code runs now
                          #    requests.post(...) executes during this pause
    finally:
        elapsed = time.time() - start   # 3. runs on exit (always)
        print(f"{label}: {elapsed:.3f}s")

def retry(times: int = 3):
    # Three layers of nesting — this is the "decorator factory" pattern:
    #   retry(times=3)  → returns decorator
    #   decorator(func) → returns wrapper
    #   wrapper(...)    → runs the actual logic
    # Needed because @retry(times=3) calls retry() first, then applies the result.
    # A plain @retry (no parentheses) would only need two layers.

    def decorator(func):
        @functools.wraps(func)
        # functools.wraps copies __name__, __doc__, etc. from func onto wrapper.
        # Without it, all retried functions would appear as "wrapper" in tracebacks.

        def wrapper(*args, **kwargs):
            # *args and **kwargs forward whatever arguments the caller passed
            # through to the original function unchanged — makes retry generic,
            # works on any function signature without knowing it in advance.
            last_exception = None
            # Initialised to None so the variable always exists.
            # After the loop it's guaranteed to be set (loop runs at least once),
            # but the type checker can't know that — None makes the intent clear.

            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                    # Early return on success — skips remaining attempts.
                except Exception as e:
                    last_exception = e
                    if attempt < times:
                        print(f"Retrying... (attempt {attempt}/{times})")
            raise last_exception  # type: ignore[misc]  # always set after loop
            # Re-raises the last failure if every attempt failed.
        return wrapper
    return decorator
