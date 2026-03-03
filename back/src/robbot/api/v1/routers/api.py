"""API v1 router aggregating all feature controllers."""

from fastapi import APIRouter

from robbot.adapters.controllers import (
    ai_controller,
    audit_controller,
    auth_controller,
    content_controller,
    context_controller,
    context_item_controller,
    conversation_controller,
    dashboard_controller,
    handoff_controller,
    health_controller,
    job_controller,
    lead_controller,
    metrics_controller,
    notification_controller,
    queue_controller,
    queues_controller,
    tag_controller,
    topic_controller,
    user_controller,
    waha_controller,
    webhook_controller,
)
from robbot.adapters.controllers.ai_controller import get_llm_interactions
from robbot.api.v1 import worker_routes

api_router = APIRouter()

# Authentication & User Management
api_router.include_router(auth_controller.router, prefix="/auth", tags=["Auth"])
api_router.include_router(user_controller.router, prefix="/users", tags=["Users"])

# System & Infrastructure
api_router.include_router(health_controller.router, prefix="/health", tags=["Health"])
api_router.include_router(queue_controller.router, prefix="/queue", tags=["Queue"])
api_router.include_router(queues_controller.router, prefix="/queues", tags=["Queues"])
api_router.include_router(worker_routes.router, prefix="/workers", tags=["Workers"])
api_router.include_router(audit_controller.router, prefix="/audit-logs", tags=["Audit"])
api_router.include_router(job_controller.router, prefix="/jobs", tags=["Jobs"])

# Core Features
api_router.include_router(conversation_controller.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(lead_controller.router, prefix="/leads", tags=["Leads"])
api_router.include_router(notification_controller.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(tag_controller.router, prefix="/tags", tags=["Tags"])

# Contents & Contexts
api_router.include_router(content_controller.router, prefix="/contents", tags=["Contents"])
api_router.include_router(topic_controller.router, prefix="/topics", tags=["Topics"])
api_router.include_router(context_controller.router, prefix="/contexts", tags=["Contexts"])
api_router.include_router(context_item_controller.router, prefix="/context-items", tags=["Context Items"])

# AI & Automation
api_router.include_router(ai_controller.router, prefix="/ai", tags=["AI"])
# Direct endpoint for compatibility
api_router.add_api_route("/llm-interactions", get_llm_interactions, methods=["GET"], tags=["AI"])
api_router.include_router(handoff_controller.router, prefix="/handoff", tags=["Handoff"])

# Analytics & Metrics
api_router.include_router(dashboard_controller.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(metrics_controller.router, prefix="/metrics", tags=["Metrics"])

# External Integrations
api_router.include_router(waha_controller.router, prefix="/waha", tags=["WAHA"])
api_router.include_router(webhook_controller.router, prefix="/webhooks", tags=["Webhooks"])
