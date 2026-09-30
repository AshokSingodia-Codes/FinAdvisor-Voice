import time
import threading
from typing import Callable, Any, Optional, Dict

class CircuitBreakerOpenException(Exception):
    """Raised when the circuit breaker is OPEN and rejecting calls."""
    pass

class CircuitBreaker:
    """
    Enterprise Multi-Tenant Circuit Breaker Pattern for LLM API Gateways.
    States (tracked PER USER_ID):
      - CLOSED: Normal operation. Requests pass through.
      - OPEN: Failures exceeded threshold. Requests immediately fail fast or route to fallback.
      - HALF-OPEN: Trial period after recovery timeout to test service recovery.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout_sec: float = 30.0, name: str = "LLM_Gateway"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.name = name
        
        # Isolated state per user_id: user_id -> {"state": "CLOSED", "failure_count": 0, "last_state_change": float}
        self.user_states: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def _get_user_state(self, user_id: Optional[str]) -> Dict[str, Any]:
        key = user_id if user_id else "_global"
        if key not in self.user_states:
            self.user_states[key] = {
                "state": "CLOSED",
                "failure_count": 0,
                "last_state_change": time.time()
            }
        return self.user_states[key]

    def record_success(self, user_id: Optional[str] = None):
        with self._lock:
            st = self._get_user_state(user_id)
            st["failure_count"] = 0
            st["state"] = "CLOSED"

    def record_failure(self, user_id: Optional[str] = None):
        with self._lock:
            st = self._get_user_state(user_id)
            st["failure_count"] += 1
            if st["failure_count"] >= self.failure_threshold:
                st["state"] = "OPEN"
                st["last_state_change"] = time.time()
                print(f"[CircuitBreaker:{self.name}][user:{user_id or 'global'}] State transitioned to OPEN (Failures: {st['failure_count']})")

    def can_execute(self, user_id: Optional[str] = None) -> bool:
        with self._lock:
            st = self._get_user_state(user_id)
            state = st["state"]
            if state == "CLOSED":
                return True
            if state == "OPEN":
                # Check if recovery timeout has elapsed
                if time.time() - st["last_state_change"] >= self.recovery_timeout_sec:
                    st["state"] = "HALF-OPEN"
                    st["last_state_change"] = time.time()
                    print(f"[CircuitBreaker:{self.name}][user:{user_id or 'global'}] State transitioned to HALF-OPEN (Testing recovery)")
                    return True
                return False
            if state == "HALF-OPEN":
                return True
            return False

    def execute_with_fallback(self, primary_fn: Callable[[], Any], fallback_fn: Callable[[], Any], user_id: Optional[str] = None) -> Any:
        if not self.can_execute(user_id=user_id):
            print(f"[CircuitBreaker:{self.name}][user:{user_id or 'global'}] Fast-failing to fallback (Circuit is OPEN)")
            return fallback_fn()
            
        try:
            result = primary_fn()
            self.record_success(user_id=user_id)
            return result
        except Exception as e:
            self.record_failure(user_id=user_id)
            print(f"[CircuitBreaker:{self.name}][user:{user_id or 'global'}] Primary execution failed: {e}. Cascading to fallback.")
            return fallback_fn()

    def reset_user(self, user_id: str):
        with self._lock:
            self.user_states.pop(user_id, None)

    def clear(self):
        with self._lock:
            self.user_states.clear()

# Per-chain circuit breaker instances
fast_chain_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_sec=30.0, name="Fast_Chain_Breaker")
synthesis_chain_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_sec=45.0, name="Synthesis_Chain_Breaker")
groq_primary_breaker = synthesis_chain_breaker  # Backwards compatibility alias

