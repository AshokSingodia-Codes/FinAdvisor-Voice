import time
from collections import deque
from threading import Lock
from typing import Dict
from fastapi import HTTPException

# In-memory sliding window rate limiter
# NOTE: This resets on process restart and won't scale across multiple workers/instances.
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.users: Dict[str, deque] = {}
        self.lock = Lock()
        
    def check_rate_limit(self, user_id: str) -> None:
        """
        Check if the user has exceeded the rate limit.
        Raises HTTPException(429) if exceeded.
        """
        now = time.time()
        
        with self.lock:
            if user_id not in self.users:
                self.users[user_id] = deque()
                
            user_requests = self.users[user_id]
            
            # Remove requests outside the window
            while user_requests and now - user_requests[0] > self.window_seconds:
                user_requests.popleft()
                
            if len(user_requests) >= self.max_requests:
                earliest_request = user_requests[0]
                retry_after = int(self.window_seconds - (now - earliest_request))
                # Ensure retry_after is at least 1 second
                retry_after = max(1, retry_after)
                
                raise HTTPException(
                    status_code=429,
                    detail={
                        "message": "Rate limit exceeded. Please try again later.",
                        "retry_after_seconds": retry_after
                    }
                )
                
            user_requests.append(now)

# Default: 20 requests per hour (3600 seconds)
chat_rate_limiter = RateLimiter(max_requests=20, window_seconds=3600)
