import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request


def client_ip(request: Request) -> str:
    # nginx sets X-Real-IP from the socket address, so it cannot be spoofed by clients.
    return request.headers.get("x-real-ip") or (
        request.client.host if request.client else "unknown"
    )


def rate_limit(name: str, max_requests: int, window_seconds: int):
    """In-memory per-IP limiter. Valid for the single API process this app runs as."""
    hits: dict[str, deque] = defaultdict(deque)
    lock = Lock()

    def dependency(request: Request):
        key = client_ip(request)
        now = time.monotonic()
        with lock:
            window = hits[key]
            while window and now - window[0] > window_seconds:
                window.popleft()
            if len(window) >= max_requests:
                retry_after = int(window_seconds - (now - window[0])) + 1
                raise HTTPException(
                    status_code=429,
                    detail="Too many attempts. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )
            window.append(now)

    return dependency


login_limit = rate_limit("login", max_requests=10, window_seconds=300)
register_limit = rate_limit("register", max_requests=5, window_seconds=3600)
password_reset_limit = rate_limit("password-reset", max_requests=5, window_seconds=900)
