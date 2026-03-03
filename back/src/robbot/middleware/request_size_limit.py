"""
Request size limit middleware for protecting against resource exhaustion.

Limits maximum request body size to prevent DoS attacks.

Resolves Issue #8: Missing Input Validation at API Layer
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("robbot.middleware.request_size_limit")

# Maximum request body size: 1MB
MAX_REQUEST_SIZE = 1024 * 1024


async def size_limit_middleware(request: Request, call_next):
    """
    Middleware to limit request body size.

    Args:
        request: HTTP request
        call_next: Next middleware/handler

    Returns:
        Response or 413 Payload Too Large if exceeds limit
    """
    # Get Content-Length header
    content_length = request.headers.get("content-length")

    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        logger.warning(
            "Request body too large: %d bytes (limit: %d)",
            content_length,
            MAX_REQUEST_SIZE,
        )
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": f"Request body too large (max {MAX_REQUEST_SIZE} bytes)"},
        )

    return await call_next(request)


def add_request_size_limit(app: FastAPI) -> None:
    """
    Add request size limit middleware to FastAPI app.

    Call during app initialization:

    Example:
        add_request_size_limit(app)

    Args:
        app: FastAPI application
    """
    app.middleware("http")(size_limit_middleware)
    logger.info(f"Request size limit middleware added (max: {MAX_REQUEST_SIZE} bytes)")
