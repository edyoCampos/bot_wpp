"""API v1 router aggregating all feature controllers."""

from fastapi import APIRouter

from robbot.adapters.controllers import (
    auth_controller,
    health_controller,
    message_controller,
    user_controller,
)

api_router = APIRouter()
api_router.include_router(auth_controller.router,
                          prefix="/auth", tags=["auth"])
api_router.include_router(health_controller.router, prefix="", tags=["health"])
api_router.include_router(user_controller.router, prefix="", tags=["users"])
api_router.include_router(message_controller.router,
                          prefix="/messages", tags=["messages"])
