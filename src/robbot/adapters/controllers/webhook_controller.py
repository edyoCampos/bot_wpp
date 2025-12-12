"""Webhook controller for WAHA events (NO JWT auth)."""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from robbot.adapters.repositories.webhook_log_repository import WebhookLogRepository
from robbot.api.v1.dependencies import get_db
from robbot.config.settings import settings
import logging
from robbot.schemas.waha import WebhookLogOut, WebhookPayload

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)


def _get_webhook_repo(db: Session = Depends(get_db)) -> WebhookLogRepository:
    """Dependency to create WebhookLogRepository."""
    return WebhookLogRepository(db)


def _validate_webhook_secret(x_webhook_secret: str | None = Header(None)):
    """Validate webhook secret if configured.

    Args:
        x_webhook_secret: Secret from header

    Raises:
        HTTPException: If secret is invalid
    """
    if settings.WAHA_WEBHOOK_SECRET:
        if not x_webhook_secret or x_webhook_secret != settings.WAHA_WEBHOOK_SECRET:
            logger.warning("Webhook request with invalid secret")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook secret",
            )


@router.post(
    "/waha",
    response_model=WebhookLogOut,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(_validate_webhook_secret)],
)
async def receive_waha_webhook(
    payload: WebhookPayload,
    request: Request,
    repo: WebhookLogRepository = Depends(_get_webhook_repo),
):
    """Receive webhook from WAHA.

    **No JWT authentication** - Protected by optional webhook secret.

    This endpoint receives all WAHA events (messages, status, acks)
    and stores them in the database for async processing (Épico 3).

    Events:
    - `message` - Incoming message
    - `message.ack` - Message acknowledgment
    - `session.status` - Session status change
    """
    logger.info(
        f"Webhook received: {payload.event} from session {payload.session}",
        extra={"event": payload.event, "session": payload.session},
    )

    # Save webhook to database for processing
    log = repo.create(
        session_name=payload.session,
        event_type=payload.event,
        payload=payload.payload,
    )

    # TODO (Épico 3): Enqueue to Redis Queue for async processing
    # For now, just log and save to DB

    logger.debug(f"Webhook saved: id={log.id}, event={payload.event}")

    return WebhookLogOut.model_validate(log)


@router.get(
    "/waha/logs",
    response_model=list[WebhookLogOut],
    dependencies=[Depends(_validate_webhook_secret)],
)
async def get_webhook_logs(
    limit: int = 100,
    event_type: str | None = None,
    repo: WebhookLogRepository = Depends(_get_webhook_repo),
):
    """Get unprocessed webhook logs.

    **No JWT authentication** - Protected by webhook secret.

    Useful for debugging and manual reprocessing.
    """
    logs = repo.get_unprocessed(limit=limit, event_type=event_type)
    return [WebhookLogOut.model_validate(log) for log in logs]
