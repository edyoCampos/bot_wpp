"""Webhook controller for WAHA events (NO JWT auth)."""

import logging

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.webhook_log_repository import WebhookLogRepository
from robbot.api.v1.dependencies import get_db
from robbot.config.settings import get_settings
from robbot.core.custom_exceptions import ExternalServiceError, QueueError
from robbot.schemas.waha import WebhookLogOut, WebhookPayload
from robbot.services.infrastructure.queue_service import get_queue_service
from robbot.services.communication.message_filter_service import MessageFilterService

router = APIRouter()

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_webhook_repo(db: Session = Depends(get_db)) -> WebhookLogRepository:
    """Dependency to create WebhookLogRepository."""
    return WebhookLogRepository(db)


@router.post(
    "/waha",
    response_model=WebhookLogOut,
    status_code=status.HTTP_202_ACCEPTED,
)
async def receive_waha_webhook(
    payload: WebhookPayload,
    _request: Request,
    repo: WebhookLogRepository = Depends(_get_webhook_repo),
):
    """Receive webhook from WAHA.

    **No authentication** - Webhook interno entre containers Docker.
    Para produção, configure firewall/VPN para proteger este endpoint.

    This endpoint receives all WAHA events (messages, status, acks)
    and stores them in the database for async processing (Épico 3).

    Events:
    - `message` - Incoming message
    - `message.ack` - Message acknowledgment
    - `session.status` - Session status change
    """
    logger.info(
        "Webhook received: %s from session %s",
        payload.event,
        payload.session,
        extra={"event": payload.event, "session": payload.session},
    )

    log = repo.create(
        session_name=payload.session,
        event_type=payload.event,
        payload=payload.payload,
    )

    queue_service = get_queue_service()

    try:
        if payload.event in {"message", "message.any"} and payload.payload:
            message_data = payload.payload

            if message_data.get("fromMe") is True:
                logger.debug(
                    "[WEBHOOK] Ignorando mensagem enviada pelo bot (fromMe=true)",
                    extra={"event": payload.event, "webhook_log_id": log.id},
                )
                return log

            chat_id = message_data.get("from", "")
            phone = chat_id.split("@")[0] if "@" in chat_id else chat_id

            # LID RESOLUTION: Try to resolve @lid to real phone number (non-blocking)
            if "@lid" in chat_id:
                from robbot.services.lid_resolver_service import get_lid_resolver

                lid_resolver = get_lid_resolver()
                resolved_phone = None

                try:
                    # Quick attempt with 500ms timeout (non-blocking)
                    import asyncio

                    resolved_phone = await asyncio.wait_for(
                        lid_resolver.try_resolve_lid(phone, payload.session),
                        timeout=0.5,
                    )

                    if resolved_phone:
                        phone = resolved_phone
                        logger.info(
                            "[WEBHOOK] LID resolved: %s -> %s",
                            chat_id,
                            phone,
                            extra={"lid": chat_id, "phone": phone, "webhook_log_id": log.id},
                        )
                except asyncio.TimeoutError:
                    logger.debug(
                        "[WEBHOOK] LID resolution timeout, accepting original: %s",
                        phone,
                        extra={"lid": chat_id, "webhook_log_id": log.id},
                    )
                except Exception as e:
                    logger.warning(
                        "[WEBHOOK] LID resolution error, accepting original: %s - %s",
                        phone,
                        str(e),
                        extra={"lid": chat_id, "webhook_log_id": log.id},
                    )

            # DEV MODE: Filtrar mensagens por número de telefone (exceto sessão de teste)
            # IMPORTANTE: O WAHA pode retornar LID (24988337893388@lid) ou número (555191628223@c.us)
            if settings.DEV_MODE and settings.dev_phone_list and payload.session != "test":
                # Procurar correspondência em dev_phone_list (números originais)
                phone_is_allowed = phone in settings.dev_phone_list

                # Se não encontrou direto e recebeu um LID, tenta encontrar via Redis cache
                if not phone_is_allowed and "@" in chat_id and "@lid" in chat_id:
                    from robbot.infra.redis.client import get_redis_client

                    redis_client = get_redis_client()

                    # Procurar o número original baseado no LID
                    cached_number = redis_client.get(f"waha:dev_phone:{phone}")
                    if cached_number:
                        cached_number_str = (
                            cached_number.decode() if isinstance(cached_number, bytes) else cached_number
                        )
                        if cached_number_str in settings.dev_phone_list:
                            phone_is_allowed = True
                            logger.debug(
                                "[DEV MODE] LID encontrado em cache: %s -> %s",
                                phone,
                                cached_number_str,
                            )

                if not phone_is_allowed:
                    logger.info(
                        "[DEV MODE] Mensagem ignorada - número não autorizado: %s (permitidos: %s)",
                        phone,
                        ", ".join(settings.dev_phone_list),
                        extra={
                            "dev_mode": True,
                            "phone": phone,
                            "allowed_phones": settings.dev_phone_list,
                            "webhook_log_id": log.id,
                        },
                    )
                    return log
                else:
                    logger.info(
                        "[DEV MODE] Mensagem aceita de número autorizado: %s",
                        phone,
                        extra={"dev_mode": True, "phone": phone, "webhook_log_id": log.id},
                    )

            job_id = queue_service.enqueue_message_processing_debounced(
                message_data=message_data,
                message_direction="inbound",
            )

            # De-duplication: Mark as processed immediately to prevent polling pick-up
            try:
                message_filter = MessageFilterService()
                message_filter.mark_as_processed(message_data.get("id"))
            except Exception as e:
                logger.warning("[WEBHOOK] Failed to mark message as processed: %s", e)

            logger.info(
                "[SUCCESS] Mensagem enfileirada para processamento: %s",
                job_id,
                extra={
                    "job_id": job_id,
                    "phone": phone,
                    "chat_id": chat_id,
                    "webhook_log_id": log.id,
                },
            )
        else:
            logger.debug(
                "Evento '%s' registrado mas não enfileirado",
                payload.event,
                extra={"event": payload.event, "webhook_log_id": log.id},
            )

    except (QueueError, ExternalServiceError) as e:
        logger.error(
            "Erro ao enfileirar mensagem: %s",
            e,
            extra={"webhook_log_id": log.id, "error": str(e)},
            exc_info=True,
        )

    return WebhookLogOut.model_validate(log)


@router.get(
    "/waha/logs",
    response_model=list[WebhookLogOut],
)
async def get_webhook_logs(
    limit: int = 100,
    event_type: str | None = None,
    repo: WebhookLogRepository = Depends(_get_webhook_repo),
):
    """Get unprocessed webhook logs.

    **No authentication** - Endpoint interno para debugging.
    Para produção, proteja com JWT ou remova este endpoint.

    Useful for debugging and manual reprocessing.
    """
    logs = repo.get_unprocessed(limit=limit, event_type=event_type)
    return [WebhookLogOut.model_validate(log) for log in logs]

