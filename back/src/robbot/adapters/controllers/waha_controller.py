"""WAHA controller for session and message endpoints."""

from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from robbot.infra.integrations.waha.waha_client import WAHAClient, get_waha_client
from robbot.infra.persistence.repositories.session_repository import SessionRepository
from robbot.api.v1.dependencies import get_current_user, get_db, require_role
from robbot.core.custom_exceptions import ExternalServiceError
from robbot.domain.shared.enums import Role
from robbot.schemas.waha import (
    ContactBlockRequest,
    ConvertVideoRequest,
    ConvertVoiceRequest,
    EditMessageRequest,
    ForwardMessageRequest,
    GetMessagesResponse,
    HealthCheckResponse,
    LinkCustomPreviewRequest,
    MessageSentResponse,
    RejectCallRequest,
    RequestAuthCodeRequest,
    SendButtonsRequest,
    SendContactVcardRequest,
    SendEventRequest,
    SendFileRequest,
    SendImageRequest,
    SendListRequest,
    SendLocationRequest,
    SendPollRequest,
    SendPollVoteRequest,
    SendTextRequest,
    SendVideoRequest,
    SendVoiceRequest,
    SessionCreate,
    SessionOut,
    SessionStatus,
    SetPresenceRequest,
)
from robbot.services.communication.waha_service import WAHAService

router = APIRouter()


def _get_waha_service(db: Session = Depends(get_db)) -> WAHAService:
    """Dependency to create WAHAService."""
    return WAHAService(
        session_repo=SessionRepository(db),
        waha_client=get_waha_client(),
    )


def _handle_waha_error(e: ExternalServiceError) -> HTTPException:
    """Handle WAHA errors by mapping them to appropriate HTTP status codes.

    Args:
        e: The external service error from WAHA

    Returns:
        HTTPException with appropriate status code
    """
    # Map WAHA status codes to HTTP status codes
    if e.status_code:
        waha_code = e.status_code
        if waha_code == 422:  # Unprocessable Entity (session exists, validation error, etc.)
            return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        elif waha_code == 400:  # Bad Request
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        elif waha_code == 404:  # Not Found
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    # Default to 502 for other external service errors
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"WAHA error: {e}")


# ============================================================================
# SESSION MANAGEMENT (ADMIN only)
# ============================================================================
@router.get(
    "/sessions",
    tags=["Sessions"],
    dependencies=[Depends(get_current_user)],
)
async def list_sessions(service: WAHAService = Depends(_get_waha_service)):
    """List all WAHA sessions (proxy to WAHA /api/sessions)."""
    try:
        return await service.list_sessions()
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/sessions",
    response_model=SessionOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Sessions"],
    dependencies=[Depends(get_current_user), Depends(require_role(Role.ADMIN))],
)
async def create_session(
    data: SessionCreate,
    service: WAHAService = Depends(_get_waha_service),
    db: Session = Depends(get_db),
):
    """Create new WhatsApp session.

    **Admin only** - Creates session in WAHA and saves to database.

    If session already exists in WAHA (status 409), still creates the DB record
    to track it, then returns 201 (idempotent behavior).
    """
    try:
        return await service.create_session(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except ExternalServiceError as e:
        # Special handling for 409: session already exists in WAHA
        # Create DB record to track it and return success
        if e.status_code == 422:  # WAHA 422 = conflict/exists
            # Check if we need to create DB record
            session_repo = SessionRepository(db)
            existing = session_repo.get_by_name(data.name)
            if not existing:
                # Extract webhook URL
                webhook_url = data.webhook_url or None
                if not webhook_url and isinstance(data.config, dict):
                    webhooks = data.config.get("webhooks") or []
                    if isinstance(webhooks, list) and webhooks:
                        first_webhook = webhooks[0] if isinstance(webhooks[0], dict) else None
                        if first_webhook:
                            webhook_url = first_webhook.get("url")
                from robbot.config.settings import settings

                webhook_url = webhook_url or settings.WAHA_WEBHOOK_URL

                # Create DB record for existing WAHA session
                existing = session_repo.create(
                    name=data.name,
                    webhook_url=webhook_url,
                )
            # Return 201 as if created (idempotent behavior)
            return SessionOut.model_validate(existing)

        # For other WAHA errors, map status codes
        raise _handle_waha_error(e) from e


@router.post(
    "/sessions/{name}/start",
    response_model=SessionStatus,
    tags=["Sessions"],
    dependencies=[Depends(get_current_user), Depends(require_role(Role.ADMIN))],
)
async def start_session(
    name: str,
    service: WAHAService = Depends(_get_waha_service),
):
    """Start WhatsApp session (generates QR code).

    **Admin only** - Initiates session connection.
    """
    try:
        return await service.start_session(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ExternalServiceError as e:
        raise _handle_waha_error(e) from e


@router.post(
    "/sessions/{name}/stop",
    tags=["Sessions"],
    dependencies=[Depends(get_current_user), Depends(require_role(Role.ADMIN))],
)
async def stop_session(
    name: str,
    service: WAHAService = Depends(_get_waha_service),
):
    """Stop WhatsApp session.

    **Admin only** - Disconnects session.
    """
    try:
        return await service.stop_session(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ExternalServiceError as e:
        raise _handle_waha_error(e) from e


@router.post(
    "/sessions/{name}/restart",
    tags=["Sessions"],
    dependencies=[Depends(get_current_user), Depends(require_role(Role.ADMIN))],
)
async def restart_session(
    name: str,
    service: WAHAService = Depends(_get_waha_service),
):
    """Restart WhatsApp session.

    **Admin only** - Stops and starts session.
    """
    try:
        return await service.restart_session(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ExternalServiceError as e:
        raise _handle_waha_error(e) from e


@router.get(
    "/sessions/{name}/status",
    response_model=SessionStatus,
    tags=["Sessions"],
    dependencies=[Depends(get_current_user)],
)
async def get_session_status(
    name: str,
    service: WAHAService = Depends(_get_waha_service),
):
    """Get current session status.

    **Authenticated users** - Returns connection status and QR code if available.
    """
    try:
        return await service.get_session_status(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/sessions/{name}",
    response_model=SessionStatus,
    tags=["Sessions"],
    dependencies=[Depends(get_current_user)],
)
async def get_session_status_alias(
    name: str,
    service: WAHAService = Depends(_get_waha_service),
):
    """Alias for getting session status to match WAHA path semantics."""
    try:
        return await service.get_session_status(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/sessions/{name}/qr",
    tags=["Sessions"],
    dependencies=[Depends(get_current_user)],
)
async def get_qr_code(
    name: str,
    service: WAHAService = Depends(_get_waha_service),
):
    """Get QR code for session pairing.

    **Authenticated users** - Returns base64 QR code image.
    """
    try:
        return await service.get_qr_code(name)
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/sessions/{name}/logout",
    tags=["Sessions"],
    dependencies=[Depends(get_current_user), Depends(require_role(Role.ADMIN))],
)
async def logout_session(
    name: str,
    service: WAHAService = Depends(_get_waha_service),
):
    """Logout from WhatsApp (unlink device).

    **Admin only** - Removes device pairing.
    """
    try:
        return await service.logout_session(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


# ============================================================================
# MESSAGES
# ============================================================================
@router.post(
    "/messages/send-text",
    response_model=MessageSentResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_text_message(
    data: SendTextRequest,
    service: WAHAService = Depends(_get_waha_service),
):
    """Send text message with anti-ban delays.

    **Authenticated users** - Rate limited per chat_id.
    """
    try:
        return await service.send_text(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e)) from e
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-image",
    response_model=MessageSentResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_image_message(
    data: SendImageRequest,
    service: WAHAService = Depends(_get_waha_service),
):
    """Send image message with optional caption.

    **Authenticated users** - Rate limited per chat_id.
    """
    try:
        return await service.send_image(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e)) from e
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-file",
    response_model=MessageSentResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_file_message(
    data: SendFileRequest,
    service: WAHAService = Depends(_get_waha_service),
):
    """Send file/document message.

    **Authenticated users** - Rate limited per chat_id.
    """
    try:
        return await service.send_file(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e)) from e
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-location",
    response_model=MessageSentResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_location_message(
    data: SendLocationRequest,
    service: WAHAService = Depends(_get_waha_service),
):
    """Send location message.

    **Authenticated users** - Rate limited per chat_id.
    """
    try:
        return await service.send_location(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e)) from e
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-voice",
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_voice_message(
    request: SendVoiceRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Send voice message to chat."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.send_voice(
            session=session.name,
            chat_id=request.chat_id,
            file_url=request.file_url,
            file_data=request.file_data,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-video",
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_video_message(
    request: SendVideoRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Send video message to chat."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.send_video(
            session=session.name,
            chat_id=request.chat_id,
            file_url=request.file_url,
            file_data=request.file_data,
            caption=request.caption,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-seen",
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def mark_message_seen(
    chat_id: str,
    message_id: str,
    service: WAHAService = Depends(_get_waha_service),
):
    """Mark message as seen (read receipt).

    **Authenticated users** - Sends 'seen' status to WhatsApp.
    """
    try:
        return await service.send_seen(chat_id, message_id)
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-buttons",
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_buttons(
    request: SendButtonsRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Send interactive buttons message."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.send_buttons(
            session=session.name,
            chat_id=request.chat_id,
            body=request.body,
            buttons=request.buttons,
            footer=request.footer,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-list",
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_list(
    request: SendListRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Send list/menu message."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.send_list(
            session=session.name,
            chat_id=request.chat_id,
            body=request.body,
            sections=request.sections,
            title=request.title,
            button_text=request.button_text,
            footer=request.footer,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-poll",
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_poll(
    request: SendPollRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Send poll/voting message."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.send_poll(
            session=session.name,
            chat_id=request.chat_id,
            body=request.body,
            options=request.options,
            title=request.title,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-poll-vote",
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_poll_vote(
    request: SendPollVoteRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Vote on a poll."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.send_poll_vote(
            session=session.name,
            chat_id=request.chat_id,
            message_id=request.message_id,
            option_index=request.option_index,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-contact",
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_contact(
    request: SendContactVcardRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Send contact (vCard) message."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.send_contact_vcard(
            session=session.name,
            chat_id=request.chat_id,
            contact_name=request.contact_name,
            phone_number=request.phone_number,
            organization=request.organization,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/forward",
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def forward_message(
    request: ForwardMessageRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Forward message to another chat."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.forward_message(
            session=session.name,
            chat_id=request.chat_id,
            message_id=request.message_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.put(
    "/chats/{chat_id}/messages/{message_id}",
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def edit_message(
    chat_id: str,
    message_id: str,
    request: EditMessageRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Edit text message or media caption.

    **Important:** chatId and messageId must be URL encoded.
    - Example: `123@c.us` -> `123%40c.us`
    - Example: `true_123@c.us_AAA` -> `true_123%40c.us_AAA`
    """
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        # URL encode IDs (@ -> %40)
        encoded_chat_id = quote(chat_id, safe="")
        encoded_message_id = quote(message_id, safe="")

        return await waha.edit_message(
            session=session.name,
            chat_id=encoded_chat_id,
            message_id=encoded_message_id,
            text=request.text,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.delete(
    "/chats/{chat_id}/messages/{message_id}",
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def delete_message(
    chat_id: str,
    message_id: str,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Delete message from chat.

    **Important:** chatId and messageId must be URL encoded.
    - Example: `123@c.us` -> `123%40c.us`
    - Example: `true_123@c.us_AAA` -> `true_123%40c.us_AAA`
    """
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        # URL encode IDs (@ -> %40)
        encoded_chat_id = quote(chat_id, safe="")
        encoded_message_id = quote(message_id, safe="")

        return await waha.delete_message(
            session=session.name,
            chat_id=encoded_chat_id,
            message_id=encoded_message_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/messages/send-link-preview",
    response_model=MessageSentResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_link_custom_preview(
    request: LinkCustomPreviewRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Send link with custom preview (useful for CAPTCHA/blocked sites).

    **Use cases:**
    - Sites with CAPTCHA (Amazon, etc)
    - Blocked or rate-limited sites
    - Custom branding for links
    """
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.send_link_custom_preview(
            session=session.name,
            chat_id=request.chat_id,
            text=request.text,
            title=request.title,
            description=request.description,
            image_url=request.image_url,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/chats/{chat_id}/messages",
    response_model=GetMessagesResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def get_chat_messages(
    chat_id: str,
    limit: int = 100,
    offset: int = 0,
    download_media: bool = False,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Get message history from chat.

    **Parameters:**
    - `limit`: Max messages to return (default 100, max 500)
    - `offset`: Skip messages (for pagination)
    - `download_media`: Download media files or not

    **Example:** GET `/waha/chats/5511999999999@c.us/messages?limit=50&offset=0`
    """
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        # Validate limit
        if limit > 500:
            limit = 500

        result = await waha.get_messages(
            session=session.name,
            chat_id=chat_id,
            limit=limit,
            offset=offset,
            download_media=download_media,
        )

        # Return result as is or wrap if needed
        if isinstance(result, list):
            return GetMessagesResponse(messages=result)
        return result
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/events",
    response_model=MessageSentResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_event(
    request: SendEventRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Send calendar event message.

    **Parameters:**
    - `name`: Event title/name (required)
    - `start_time`: Unix timestamp in seconds (required)
    - `end_time`: Unix timestamp in seconds (optional, can be null)
    - `description`: Optional event description (supports \\n for newlines, * for bold)
    - `location`: Optional event location name
    - `extra_guests_allowed`: Allow additional guests (default false)
    - `reply_to`: Message ID to reply to (optional)

    **Example:**
    ```json
    {
      "chat_id": "5511999999999@c.us",
      "name": "Team Meeting",
      "description": "Monthly sync-up meeting",
      "location": "Conference Room A",
      "start_time": 1702627200,
      "end_time": 1702630800,
      "extra_guests_allowed": false
    }
    ```

    **To convert ISO 8601 to Unix timestamp:**
    - Python: `int(datetime.fromisoformat(iso_string.replace('Z', '+00:00')).timestamp())`
    - Node.js: `new Date(isoString).getTime() / 1000`
    """
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.send_event(
            session=session.name,
            chat_id=request.chat_id,
            name=request.name,
            start_time=request.start_time,
            end_time=request.end_time,
            description=request.description,
            location_name=request.location_name,
            extra_guests_allowed=request.extra_guests_allowed,
            reply_to=request.reply_to,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


# ============================================================================
# CONTACTS
# ============================================================================
@router.get(
    "/check-number",
    tags=["Contacts"],
    dependencies=[Depends(get_current_user)],
)
async def check_number_exists(
    phone: str,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Check if phone is registered on WhatsApp."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.check_number_exists(
            session=session.name,
            phone=phone,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/contact-about",
    tags=["Contacts"],
    dependencies=[Depends(get_current_user)],
)
async def get_contact_about(
    contact_id: str,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Get contact's about status."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.get_contact_about(
            session=session.name,
            contact_id=contact_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/contact-picture",
    tags=["Contacts"],
    dependencies=[Depends(get_current_user)],
)
async def get_contact_picture(
    contact_id: str,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Get contact's profile picture."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.get_contact_profile_picture(
            session=session.name,
            contact_id=contact_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/contact/block",
    status_code=status.HTTP_201_CREATED,
    tags=["Contacts"],
    dependencies=[Depends(get_current_user)],
)
async def block_contact(
    request: ContactBlockRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Block contact."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.block_contact(
            session=session.name,
            contact_id=request.contact_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/contact/unblock",
    status_code=status.HTTP_201_CREATED,
    tags=["Contacts"],
    dependencies=[Depends(get_current_user)],
)
async def unblock_contact(
    request: ContactBlockRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Unblock contact."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.unblock_contact(
            session=session.name,
            contact_id=request.contact_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


# ============================================================================
# PRESENCE
# ============================================================================
@router.post(
    "/presence",
    status_code=status.HTTP_200_OK,
    tags=["Presence"],
    dependencies=[Depends(get_current_user)],
)
async def set_presence(
    request: SetPresenceRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Set session presence."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.set_presence(
            session=session.name,
            presence=request.presence,
            chat_id=request.chat_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/presence/all",
    tags=["Presence"],
    dependencies=[Depends(get_current_user)],
)
async def get_all_presence(
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Get all presence information."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.get_all_presence(session=session.name)
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/presence/{chat_id}",
    tags=["Presence"],
    dependencies=[Depends(get_current_user)],
)
async def get_presence(
    chat_id: str,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Get presence for specific chat."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.get_presence(
            session=session.name,
            chat_id=chat_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/presence/{chat_id}/subscribe",
    status_code=status.HTTP_201_CREATED,
    tags=["Presence"],
    dependencies=[Depends(get_current_user)],
)
async def subscribe_presence(
    chat_id: str,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Subscribe to presence updates."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.subscribe_presence(
            session=session.name,
            chat_id=chat_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


# ============================================================================
# AUTHENTICATION
# ============================================================================
@router.get(
    "/auth/qr",
    tags=["Authentication"],
    dependencies=[Depends(get_current_user)],
)
async def get_qr_code_auth(
    fmt: str = "image",
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Get QR code for authentication."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.get_qr_code_auth(
            session=session.name,
            format=fmt,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/auth/request-code",
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    dependencies=[Depends(get_current_user)],
)
async def request_auth_code(
    request: RequestAuthCodeRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Request authentication code."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.request_auth_code(
            session=session.name,
            phone_number=request.phone_number,
            method=request.method,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


# ============================================================================
# CALLS
# ============================================================================
@router.post(
    "/call/reject",
    status_code=status.HTTP_201_CREATED,
    tags=["Calls"],
    dependencies=[Depends(get_current_user)],
)
async def reject_call(
    request: RejectCallRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Reject incoming call."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.reject_call(
            session=session.name,
            call_id=request.call_id,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


# ============================================================================
# MEDIA CONVERSION
# ============================================================================
@router.post(
    "/media/convert-voice",
    tags=["Media"],
    dependencies=[Depends(get_current_user)],
)
async def convert_voice(
    request: ConvertVoiceRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Convert voice to opus format."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.convert_voice_to_opus(
            session=session.name,
            file_url=request.file_url,
            file_data=request.file_data,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.post(
    "/media/convert-video",
    tags=["Media"],
    dependencies=[Depends(get_current_user)],
)
async def convert_video(
    request: ConvertVideoRequest,
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Convert video to mp4 format."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.convert_video_to_mp4(
            session=session.name,
            file_url=request.file_url,
            file_data=request.file_data,
        )
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


# ============================================================================
# SERVER OBSERVABILITY
# ============================================================================
@router.get(
    "/server/health",
    tags=["Observability"],
)
async def health_check(
    waha: WAHAClient = Depends(get_waha_client),
) -> HealthCheckResponse:
    """Check WAHA server health."""
    try:
        await waha.health_check()
        return HealthCheckResponse(status="ok")
    except ExternalServiceError:
        return HealthCheckResponse(status="unhealthy")


@router.get(
    "/server/ping",
    tags=["Observability"],
)
async def ping(
    waha: WAHAClient = Depends(get_waha_client),
):
    """Ping WAHA server."""
    try:
        return await waha.ping()
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/server/version",
    tags=["Observability"],
)
async def get_version(
    waha: WAHAClient = Depends(get_waha_client),
):
    """Get WAHA server version."""
    try:
        return await waha.get_server_version()
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/server/status",
    tags=["Observability"],
)
async def get_status(
    waha: WAHAClient = Depends(get_waha_client),
):
    """Get WAHA server status."""
    try:
        return await waha.get_server_status()
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e


@router.get(
    "/screenshot",
    tags=["Observability"],
    dependencies=[Depends(get_current_user)],
)
async def screenshot(
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Get screenshot of WhatsApp session."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session")

        return await waha.screenshot(session=session.name)
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e

