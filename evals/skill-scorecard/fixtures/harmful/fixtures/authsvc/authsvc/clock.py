"""Single time source so tests can freeze time. Use clock.now() instead of time.time()."""
import time


def now() -> float:
    return time.time()
