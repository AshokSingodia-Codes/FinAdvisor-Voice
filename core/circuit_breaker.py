import time
import threading
from typing import Callable, Any, Optional

class CircuitBreakerOpenException(Exception):
    """Raised when the circuit breaker is OPEN and rejecting calls."""
    pass

class CircuitBreaker:
    """
    Enterprise Circuit Breaker Pattern for LLM API Gateways.
    States:
      - CLOSED: Normal operation. Requests pass through.
      - OPEN: Failures exceeded threshold. Requests immediately fail fast or route to fallback.
      - HALF-OPEN: Trial period after recovery timeout to test service recovery.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout_sec: float = 30.0, name: str = "LLM_Gateway"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.name = name
        
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_state_change = time.time()
        self._lock = threading.Lock()

    def record_success(self):
        with self._lock:
            self.failure_count = 0
            self.state = "CLOSED"

    def record_failure(self):
        with self._lock:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.last_state_change = time.time()
                print(f"[CircuitBreaker:{self.name}] State transitioned to OPEN (Failures: {self.failure_count})")

    def can_execute(self) -> bool:
        with self._lock:
            if self.state == "CLOSED":
                return True
            if self.state == "OPEN":
                # Check if recovery timeout has elapsed
                if time.time() - self.last_state_change >= self.recovery_timeout_sec:
                    self.state = "HALF-OPEN"
                    self.last_state_change = time.time()
                    print(f"[CircuitBreaker:{self.name}] State transitioned to HALF-OPEN (Testing recovery)")
                    return True
                return False
            if self.state == "HALF-OPEN":
                return True
            return False

    def execute_with_fallback(self, primary_fn: Callable[[], Any], fallback_fn: Callable[[], Any]) -> Any:
        if not self.can_execute():
            print(f"[CircuitBreaker:{self.name}] Fast-failing to fallback (Circuit is OPEN)")
            return fallback_fn()
            
        try:
            result = primary_fn()
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            print(f"[CircuitBreaker:{self.name}] Primary execution failed: {e}. Cascading to fallback.")
            return fallback_fn()

# Per-chain circuit breaker instances
fast_chain_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_sec=30.0, name="Fast_Chain_Breaker")
synthesis_chain_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_sec=45.0, name="Synthesis_Chain_Breaker")
groq_primary_breaker = synthesis_chain_breaker  # Backwards compatibility alias
