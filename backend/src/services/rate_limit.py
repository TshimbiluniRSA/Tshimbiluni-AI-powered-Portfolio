"""In-memory rate limiting for the public AI chat endpoint.

The backend runs as a single process behind Nginx, so process memory is
enough to bound OpenAI spend without adding Redis. Limits reset if the
container restarts, which is acceptable for cost protection.
"""

import os
import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional, Tuple

from fastapi import HTTPException, Request

MINUTE = 60
DAY = 24 * 60 * 60


def _limit(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


class SlidingWindowLimiter:
    """Counts events per key over fixed-length sliding windows."""

    def __init__(self) -> None:
        self._events: Dict[Tuple[str, int], Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int, window: int, now: float) -> Optional[int]:
        """Record an event; return seconds to wait if the limit is exceeded."""
        with self._lock:
            events = self._events[(key, window)]
            while events and events[0] <= now - window:
                events.popleft()
            if len(events) >= limit:
                return max(1, int(events[0] + window - now) + 1)
            events.append(now)
            return None

    def reset(self) -> None:
        with self._lock:
            self._events.clear()


chat_limiter = SlidingWindowLimiter()


def client_ip(request: Request) -> str:
    """Return the visitor's IP as reported by the Nginx reverse proxy.

    Nginx overwrites X-Real-IP with $remote_addr, so visitors cannot spoof
    it. Without the header (local development) the socket address is used.
    """
    forwarded = request.headers.get("x-real-ip", "").strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def enforce_chat_rate_limit(request: Request) -> None:
    """FastAPI dependency limiting chat requests per visitor and overall."""
    now = time.monotonic()
    ip = client_ip(request)
    checks = (
        (f"ip:{ip}", _limit("CHAT_RATE_LIMIT_PER_MINUTE", 6), MINUTE),
        (f"ip:{ip}", _limit("CHAT_RATE_LIMIT_PER_DAY", 60), DAY),
        # Global ceiling so spoofed or many distinct IPs still cannot run up
        # the OpenAI bill.
        ("global", _limit("CHAT_RATE_LIMIT_GLOBAL_PER_DAY", 1000), DAY),
    )
    for key, limit, window in checks:
        retry_after = chat_limiter.hit(key, limit, window, now)
        if retry_after is not None:
            raise HTTPException(
                status_code=429,
                detail="Too many messages. Please wait a moment and try again.",
                headers={"Retry-After": str(retry_after)},
            )
