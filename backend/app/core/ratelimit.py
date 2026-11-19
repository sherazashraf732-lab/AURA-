import threading
import time
from collections import defaultdict, deque

from fastapi import Request

from app.core.errors import AppError


class SlidingWindowLimiter:
    """Per-key request limiter.

    shortcut: in-process memory, so limits reset on restart and are per worker process;
    upgrade to a PostgreSQL- or Redis-backed counter before running more than one API process.
    """

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int, window_s: float) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > window_s:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = SlidingWindowLimiter()


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def enforce(
    request: Request, bucket: str, limit: int, window_s: float, key: str | None = None
) -> None:
    if not limiter.hit(f"{bucket}:{key or client_ip(request)}", limit, window_s):
        raise AppError("rate_limited", "Too many requests. Please wait and try again.", 429)
