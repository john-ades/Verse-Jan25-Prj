import time
import threading


class RateLimiter:
    """
    A token bucket rate limiter.
    Allows `max_calls` in a rolling window of `period` seconds.
    If you run out of tokens, it will block until a token is available.
    """

    def __init__(self, max_calls: int, period: float):
        """
        :param max_calls: max number of calls in the given period
        :param period: rolling window in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self._available_tokens = max_calls
        self._last_refill_time = time.time()
        self._lock = threading.Lock()

    def _refill_tokens(self):
        now = time.time()
        elapsed = now - self._last_refill_time

        # How many tokens to add based on elapsed time
        tokens_to_add = (elapsed / self.period) * self.max_calls
        if tokens_to_add >= 1:
            self._available_tokens = min(float(self.max_calls), self._available_tokens + tokens_to_add)
            self._last_refill_time = now

    def acquire(self):
        """
        Block until a token is available.
        """
        with self._lock:
            # Refill tokens if possible
            self._refill_tokens()

            # If no tokens available, wait
            while self._available_tokens < 1:
                # Estimate how long until next token
                now = time.time()
                self._refill_tokens()
                if self._available_tokens < 1:
                    # Sleep a small fraction to let tokens accumulate
                    time.sleep(0.05)

            # Consume one token
            self._available_tokens -= 1