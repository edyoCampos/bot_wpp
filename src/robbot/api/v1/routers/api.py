"""API v1 router aggregating all feature controllers."""

from fastapi import APIRouter

from robbot.adapters.controllers import (
    ai_controller,
    audit_controller,
    auth_controller,
    conversation_controller,
    health_controller,
    job_controller,
    lead_controller,
    message_controller,
    notification_controller,
    playbook_controller,
    playbook_step_controller,
    queue_controller,
    tag_controller,
    topic_controller,
    user_controller,
    waha_controller,
    webhook_controller,
)

api_router = APIRouter()
api_router.include_router(auth_controller.router,
                          prefix="/auth", tags=["auth"])
api_router.include_router(health_controller.router, prefix="", tags=["health"])
api_router.include_router(user_controller.router, prefix="", tags=["users"])
api_router.include_router(message_controller.router,
                          prefix="/messages", tags=["messages"])
api_router.include_router(queue_controller.router,
                          prefix="", tags=["queue"])
api_router.include_router(waha_controller.router, prefix="")
api_router.include_router(webhook_controller.router,
                          prefix="", tags=["Webhooks"])
api_router.include_router(ai_controller.router, prefix="", tags=["AI"])
api_router.include_router(notification_controller.router, prefix="", tags=["Notifications"])
api_router.include_router(conversation_controller.router, prefix="", tags=["Conversations"])
api_router.include_router(lead_controller.router, prefix="", tags=["Leads"])
api_router.include_router(tag_controller.router, prefix="", tags=["Tags"])
api_router.include_router(job_controller.router, prefix="", tags=["Jobs"])
api_router.include_router(audit_controller.router, prefix="", tags=["Audit"])
api_router.include_router(topic_controller.router, prefix="/topics", tags=["Topics"])
api_router.include_router(playbook_controller.router, prefix="/playbooks", tags=["Playbooks"])
api_router.include_router(playbook_step_controller.router, prefix="/playbook-steps", tags=["Playbook Steps"])
