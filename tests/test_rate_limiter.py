import time
from verse_jan25_prj.rate_limiter import RateLimiter

def test_rate_limiter_allows_within_limit():
    rate_limiter = RateLimiter(max_calls=5, period=1.0)  # 5 calls per second
    start_time = time.time()
    for _ in range(5):
        rate_limiter.acquire()
    end_time = time.time()
    assert end_time - start_time < 1.0  # All calls should be allowed within 1 second

def test_rate_limiter_blocks_when_limit_exceeded():
    rate_limiter = RateLimiter(max_calls=2, period=1.0)  # 2 calls per second
    start_time = time.time()
    for _ in range(2):
        rate_limiter.acquire()
    # Next acquire should block until a token is refilled
    rate_limiter.acquire()
    end_time = time.time()
    assert end_time - start_time >= 0.5  # At least half a second should have passed