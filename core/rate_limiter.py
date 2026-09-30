import time
from collections import deque
from threading import Lock
from typing import Dict, Optional
from fastapi import HTTPException

# In-memory multi-tenant sliding window rate and token usage limiter
class RateLimiter:
    def __init__(self, max_requests: int = 20, window_seconds: int = 3600, max_tokens_per_window: Optional[int] = 100000):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_tokens_per_window = max_tokens_per_window
        
        # Keyed strictly by user_id
        self.users: Dict[str, deque] = {}         # user_id -> deque of request timestamps
        self.user_tokens: Dict[str, deque] = {}   # user_id -> deque of (timestamp, token_count) tuples
        self.lock = Lock()
        
    def check_rate_limit(self, user_id: str, estimated_tokens: int = 0) -> None:
        """
        Check if the specific user_id has exceeded their rate limit or token quota limit.
        Isolates state completely per user_id.
        Raises HTTPException(429) if exceeded.
        """
        if not user_id:
            user_id = "anonymous"

        now = time.time()
        
        with self.lock:
            if user_id not in self.users:
                self.users[user_id] = deque()
            if user_id not in self.user_tokens:
                self.user_tokens[user_id] = deque()
                
            user_requests = self.users[user_id]
            user_token_history = self.user_tokens[user_id]
            
            # Remove request timestamps outside the window
            while user_requests and now - user_requests[0] > self.window_seconds:
                user_requests.popleft()

            # Remove token history tuples outside the window
            while user_token_history and now - user_token_history[0][0] > self.window_seconds:
                user_token_history.popleft()

            # 1. Request count check
            if len(user_requests) >= self.max_requests:
                earliest_request = user_requests[0]
                retry_after = int(self.window_seconds - (now - earliest_request))
                retry_after = max(1, retry_after)
                
                raise HTTPException(
                    status_code=429,
                    detail={
                        "message": "Rate limit exceeded. Please try again later.",
                        "retry_after_seconds": retry_after
                    }
                )

            # 2. Token usage quota check (if configured)
            if self.max_tokens_per_window is not None:
                current_tokens_used = sum(t_count for _, t_count in user_token_history)
                if current_tokens_used + estimated_tokens > self.max_tokens_per_window:
                    earliest_token_ts = user_token_history[0][0] if user_token_history else now
                    retry_after = int(self.window_seconds - (now - earliest_token_ts))
                    retry_after = max(1, retry_after)

                    raise HTTPException(
                        status_code=429,
                        detail={
                            "message": "Token limit exceeded. Please try again later.",
                            "retry_after_seconds": retry_after
                        }
                    )
                
            user_requests.append(now)
            if estimated_tokens > 0:
                user_token_history.append((now, estimated_tokens))

    def record_token_usage(self, user_id: str, tokens: int) -> None:
        """Record actual tokens consumed by a user after call completion."""
        if not user_id or tokens <= 0:
            return
        now = time.time()
        with self.lock:
            if user_id not in self.user_tokens:
                self.user_tokens[user_id] = deque()
            self.user_tokens[user_id].append((now, tokens))

    def reset_user(self, user_id: str) -> None:
        """Clear rate limit and token usage state for a specific user."""
        with self.lock:
            self.users.pop(user_id, None)
            self.user_tokens.pop(user_id, None)

    def clear(self) -> None:
        """Clear all rate limit state across all users (used for test setup)."""
        with self.lock:
            self.users.clear()
            self.user_tokens.clear()

# Default: 20 requests per hour (3600 seconds), 100,000 tokens per hour per user
chat_rate_limiter = RateLimiter(max_requests=20, window_seconds=3600, max_tokens_per_window=100000)

