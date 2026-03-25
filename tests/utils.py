
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
