"""Middleware e decoradores de rate limiting para endpoints da API.

Implementa rate limiting baseado em Redis para prevenir ataques de força bruta e abuso.
Suporta múltiplas estratégias de chave (IP, user_id, email).
"""

import functools
import hashlib
from typing import Callable, Literal

from fastapi import HTTPException, Request, status
from redis import Redis

import logging
from robbot.config.settings import settings


class RateLimiter:
    """Redis-based rate limiter for API endpoints.

    Implements sliding window rate limiting using Redis.
    Supports multiple key strategies (IP, user_id, email).
    """

    def __init__(self, redis_client: Redis):
        """Initialize rate limiter with Redis client.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client

    def _get_key(
        self,
        identifier: str,
        endpoint: str,
        key_type: Literal["ip", "user", "email"],
    ) -> str:
        """Generate Redis key for rate limit counter.

        Args:
            identifier: IP address, user_id, or email
            endpoint: Endpoint path (e.g., "/auth/login")
            key_type: Type of key (ip, user, email)

        Returns:
            Redis key in format "ratelimit:{key_type}:{endpoint}:{identifier_hash}"
        """
        # Hash identifier for privacy (especially for IPs)
        identifier_hash = hashlib.sha256(identifier.encode()).hexdigest()[:16]
        return f"ratelimit:{key_type}:{endpoint}:{identifier_hash}"

    def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int,
        key_type: Literal["ip", "user", "email"] = "ip",
    ) -> tuple[bool, int, int]:
        """Check if request is within rate limit.

        Args:
            identifier: IP address, user_id, or email
            endpoint: Endpoint path
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            key_type: Type of key (ip, user, email)

        Returns:
            Tuple of (is_allowed, current_count, reset_in_seconds)
        """
        key = self._get_key(identifier, endpoint, key_type)

        try:
            # Increment counter
            current = self.redis.incr(key)

            # Set expiry on first request
            if current == 1:
                self.redis.expire(key, window_seconds)

            # Get TTL for reset time
            ttl = self.redis.ttl(key)
            if ttl == -1:  # Key exists but no TTL (shouldn't happen, but handle it)
                self.redis.expire(key, window_seconds)
                ttl = window_seconds

            # Check if limit exceeded
            is_allowed = current <= max_requests

            return is_allowed, current, ttl

        except Exception as e:
            # If Redis fails, allow request (fail open)
            logging.getLogger(__name__).exception("Rate limiter error: %s", e)
            return True, 0, 0

    def reset(self, identifier: str, endpoint: str, key_type: Literal["ip", "user", "email"] = "ip") -> None:
        """Reset rate limit for identifier (admin/testing use).

        Args:
            identifier: IP address, user_id, or email
            endpoint: Endpoint path
            key_type: Type of key (ip, user, email)
        """
        key = self._get_key(identifier, endpoint, key_type)
        self.redis.delete(key)


# Global rate limiter instance (initialized in deps.py)
_rate_limiter: RateLimiter | None = None


def init_rate_limiter(redis_client: Redis) -> None:
    """Initialize global rate limiter instance.

    Args:
        redis_client: Redis client instance
    """
    global _rate_limiter
    _rate_limiter = RateLimiter(redis_client)


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance.

    Returns:
        RateLimiter instance

    Raises:
        RuntimeError: If rate limiter not initialized
    """
    if _rate_limiter is None:
        raise RuntimeError("Rate limiter not initialized. Call init_rate_limiter() first.")
    return _rate_limiter


def rate_limit(
    max_requests: int,
    window_seconds: int,
    key_type: Literal["ip", "user", "email"] = "ip",
):
    """Decorator for rate limiting FastAPI endpoints.

    Usage:
        @router.post("/auth/login")
        @rate_limit(max_requests=5, window_seconds=900, key_type="ip")  # 5 per 15min
        async def login(request: Request, ...):
            ...

    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        key_type: Type of key to use (ip, user, email)

    Raises:
        HTTPException: 429 Too Many Requests if limit exceeded
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request: Request | None = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                # If no request found, skip rate limiting (shouldn't happen in normal usage)
                return await func(*args, **kwargs)

            # Get identifier based on key_type
            if key_type == "ip":
                identifier = request.client.host if request.client else "unknown"
            elif key_type == "user":
                # Extract user_id from request state (set by auth middleware)
                identifier = str(getattr(request.state, "user_id", "anonymous"))
            elif key_type == "email":
                # Extract email from request body (must be in JSON)
                try:
                    body = await request.json()
                    identifier = body.get("email", "unknown")
                except Exception:
                    identifier = "unknown"
            else:
                identifier = "unknown"

            # Get endpoint path
            endpoint = request.url.path

            # Check rate limit
            limiter = get_rate_limiter()
            is_allowed, current, reset_in = limiter.check_rate_limit(
                identifier=identifier,
                endpoint=endpoint,
                max_requests=max_requests,
                window_seconds=window_seconds,
                key_type=key_type,
            )

            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {reset_in} seconds.",
                    headers={
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_in),
                        "Retry-After": str(reset_in),
                    },
                )

            # Add rate limit headers to response
            response = await func(*args, **kwargs)

            # If response is a Response object, add headers
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = str(max(0, max_requests - current))
                response.headers["X-RateLimit-Reset"] = str(reset_in)

            return response

        return wrapper

    return decorator


# Predefined rate limit configurations
# Usage: @RATE_LIMIT_LOGIN
# instead of: @rate_limit(max_requests=5, window_seconds=900, key_type="ip")

RATE_LIMIT_LOGIN = rate_limit(max_requests=5, window_seconds=900, key_type="ip")  # 5 per 15min
RATE_LIMIT_REFRESH = rate_limit(max_requests=10, window_seconds=60, key_type="user")  # 10 per 1min
RATE_LIMIT_PASSWORD_RECOVERY = rate_limit(max_requests=3, window_seconds=3600, key_type="email")  # 3 per hour
RATE_LIMIT_PASSWORD_RESET = rate_limit(max_requests=5, window_seconds=900, key_type="ip")  # 5 per 15min
RATE_LIMIT_REGISTER = rate_limit(max_requests=3, window_seconds=3600, key_type="ip")  # 3 per hour
