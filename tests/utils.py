
import functools
import time
from contextlib import contextmanager


@contextmanager
def timed_block(label: str):
    # @contextmanager turns a generator function into a context manager.
    # Code before yield runs on __enter__; code after (in finally) runs on __exit__.
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"{label}: {elapsed:.3f}s")

def retry(times: int = 3):
    # Decorator factory — @retry(times=3) calls retry() first, returning a decorator.
    # That extra call requires a third nesting layer. Plain @retry needs only two.
    def decorator(func):
        @functools.wraps(func)
        # functools.wraps copies __name__, __doc__, etc. so the original function's
        # identity is preserved in tracebacks and introspection.
        def wrapper(*args, **kwargs):
            # *args/**kwargs make wrapper signature-agnostic — works on any function.
            last_exception = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < times:
                        print(f"Retrying... (attempt {attempt}/{times})")
            raise last_exception  # type: ignore[misc]  # always set after loop body
        return wrapper
    return decorator
