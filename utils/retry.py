import time
from typing import Callable, Any


def with_retry(fn: Callable[[], Any], max_retries: int = 3, base_delay: float = 1.0) -> Any:
    """Execute ``fn`` with exponential backoff retry.

    Retries on any exception up to ``max_retries`` times. The delay between
    attempts grows exponentially (``base_delay * 2**attempt`` seconds). If the
    final attempt still raises, the exception is propagated.
    """
    attempt = 0
    while True:
        try:
            return fn()
        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            print(f"[DEBUG] with_retry: attempt {attempt} failed ({e}), retrying in {delay}s")
            time.sleep(delay)
