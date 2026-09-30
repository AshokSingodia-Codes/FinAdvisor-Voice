import pytest
from fastapi import HTTPException
from core.rate_limiter import RateLimiter

@pytest.fixture
def limiter():
    rl = RateLimiter(max_requests=3, window_seconds=3600, max_tokens_per_window=1000)
    yield rl
    rl.clear()

def test_user_a_exhaustion_does_not_block_user_b(limiter):
    user_a = 'user-a-uuid-001'
    user_b = 'user-b-uuid-002'
    for _ in range(3):
        limiter.check_rate_limit(user_a)
    with pytest.raises(HTTPException) as exc_info:
        limiter.check_rate_limit(user_a)
    assert exc_info.value.status_code == 429
    assert 'limit exceeded' in exc_info.value.detail['message'].lower()
    try:
        limiter.check_rate_limit(user_b)
    except HTTPException as e:
        pytest.fail(f'ISOLATION BUG: User B blocked by User A rate limit! HTTP {e.status_code}: {e.detail}')

def test_token_quota_isolation(limiter):
    user_a = 'user-a-token-001'
    user_b = 'user-b-token-002'
    limiter.check_rate_limit(user_a, estimated_tokens=1000)
    with pytest.raises(HTTPException) as exc_info:
        limiter.check_rate_limit(user_a, estimated_tokens=1)
    assert exc_info.value.status_code == 429
    try:
        limiter.check_rate_limit(user_b, estimated_tokens=500)
    except HTTPException as e:
        pytest.fail(f'TOKEN ISOLATION BUG: User B blocked by User A token usage! HTTP {e.status_code}: {e.detail}')

def test_three_independent_users(limiter):
    ua, ub, uc = 'user-a-001', 'user-b-002', 'user-c-003'
    for _ in range(3):
        limiter.check_rate_limit(ua)
    with pytest.raises(HTTPException):
        limiter.check_rate_limit(ua)
    limiter.check_rate_limit(ub)
    limiter.check_rate_limit(uc)

def test_reset_user_clears_only_target(limiter):
    ua, ub = 'user-a-reset', 'user-b-reset'
    limiter.check_rate_limit(ua)
    limiter.check_rate_limit(ua)
    limiter.check_rate_limit(ub)
    limiter.check_rate_limit(ub)
    limiter.reset_user(ua)
    for _ in range(3):
        limiter.check_rate_limit(ua)
    limiter.check_rate_limit(ub)
    with pytest.raises(HTTPException):
        limiter.check_rate_limit(ub)

def test_anonymous_does_not_leak_to_real_user(limiter):
    limiter.check_rate_limit('')
    limiter.check_rate_limit('')
    limiter.check_rate_limit('')
    try:
        limiter.check_rate_limit('real-user-999')
    except HTTPException as e:
        pytest.fail(f'Real user blocked by anonymous quota: {e.detail}')
