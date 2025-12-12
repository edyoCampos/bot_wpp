"""WAHA controller for session and message endpoints."""

from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from robbot.adapters.external.waha_client import get_waha_client, WAHAClient
from robbot.adapters.repositories.session_repository import SessionRepository
from robbot.api.v1.dependencies import get_db, get_current_user, require_role
from robbot.core.exceptions import ExternalServiceError
from robbot.domain.enums import Role
from robbot.schemas.waha import (
    CheckNumberRequest,
    ContactAboutResponse,
    ContactBlockRequest,
    ConvertVideoRequest,
    ConvertVoiceRequest,
    EditMessageRequest,
    ForwardMessageRequest,
    GetMessagesResponse,
    GetQRCodeRequest,
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
    SendReactionRequest,
    SendStarRequest,
    SendTextRequest,
    SendVideoRequest,
    SendVoiceRequest,
    SessionCreate,
    SessionOut,
    SessionStatus,
    SetPresenceRequest,
)
from robbot.services.waha_service import WAHAService
from robbot.services.whatsapp_message_service import WhatsAppMessageService

router = APIRouter(prefix="/waha")


def _get_waha_service(db: Session = Depends(get_db)) -> WAHAService:
    """Dependency to create WAHAService."""
    return WAHAService(
        session_repo=SessionRepository(db),
        waha_client=get_waha_client(),
    )


def _get_message_service() -> WhatsAppMessageService:
    """Dependency to create WhatsAppMessageService."""
    return WhatsAppMessageService(waha_client=get_waha_client())


# ============================================================================
# SESSION MANAGEMENT (ADMIN only)
# ============================================================================


@router.post(
    "/sessions",
    response_model=SessionOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Sessions"],
    dependencies=[Depends(get_current_user),
                  Depends(require_role(Role.ADMIN))],
)
async def create_session(
    data: SessionCreate,
    service: WAHAService = Depends(_get_waha_service),
):
    """Create new WhatsApp session.

    **Admin only** - Creates session in WAHA and saves to database.
    """
    try:
        return await service.create_session(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"WAHA error: {e}",
        )


@router.post(
    "/sessions/{name}/start",
    response_model=SessionStatus,
    tags=["Sessions"],
    dependencies=[Depends(get_current_user),
                  Depends(require_role(Role.ADMIN))],
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post(
    "/sessions/{name}/stop",
    tags=["Sessions"],
    dependencies=[Depends(get_current_user),
                  Depends(require_role(Role.ADMIN))],
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post(
    "/sessions/{name}/restart",
    tags=["Sessions"],
    dependencies=[Depends(get_current_user),
                  Depends(require_role(Role.ADMIN))],
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post(
    "/sessions/{name}/logout",
    tags=["Sessions"],
    dependencies=[Depends(get_current_user),
                  Depends(require_role(Role.ADMIN))],
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
    service: WhatsAppMessageService = Depends(_get_message_service),
):
    """Send text message with anti-ban delays.

    **Authenticated users** - Rate limited per chat_id.
    """
    try:
        return await service.send_text(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post(
    "/messages/send-image",
    response_model=MessageSentResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_image_message(
    data: SendImageRequest,
    service: WhatsAppMessageService = Depends(_get_message_service),
):
    """Send image message with optional caption.

    **Authenticated users** - Rate limited per chat_id.
    """
    try:
        return await service.send_image(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post(
    "/messages/send-file",
    response_model=MessageSentResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_file_message(
    data: SendFileRequest,
    service: WhatsAppMessageService = Depends(_get_message_service),
):
    """Send file/document message.

    **Authenticated users** - Rate limited per chat_id.
    """
    try:
        return await service.send_file(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post(
    "/messages/send-location",
    response_model=MessageSentResponse,
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def send_location_message(
    data: SendLocationRequest,
    service: WhatsAppMessageService = Depends(_get_message_service),
):
    """Send location message.

    **Authenticated users** - Rate limited per chat_id.
    """
    try:
        return await service.send_location(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.send_voice(
            session=session.name,
            chat_id=request.chat_id,
            file_url=request.file_url,
            file_data=request.file_data,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.send_video(
            session=session.name,
            chat_id=request.chat_id,
            file_url=request.file_url,
            file_data=request.file_data,
            caption=request.caption,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post(
    "/messages/send-seen",
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)
async def mark_message_seen(
    chat_id: str,
    message_id: str,
    service: WhatsAppMessageService = Depends(_get_message_service),
):
    """Mark message as seen (read receipt).

    **Authenticated users** - Sends 'seen' status to WhatsApp.
    """
    try:
        return await service.send_seen(chat_id, message_id)
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.send_buttons(
            session=session.name,
            chat_id=request.chat_id,
            body=request.body,
            buttons=request.buttons,
            footer=request.footer,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.send_list(
            session=session.name,
            chat_id=request.chat_id,
            body=request.body,
            sections=request.sections,
            title=request.title,
            button_text=request.button_text,
            footer=request.footer,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.send_poll(
            session=session.name,
            chat_id=request.chat_id,
            body=request.body,
            options=request.options,
            title=request.title,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.send_poll_vote(
            session=session.name,
            chat_id=request.chat_id,
            message_id=request.message_id,
            option_index=request.option_index,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.send_contact_vcard(
            session=session.name,
            chat_id=request.chat_id,
            contact_name=request.contact_name,
            phone_number=request.phone_number,
            organization=request.organization,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.forward_message(
            session=session.name,
            chat_id=request.chat_id,
            message_id=request.message_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        # URL encode IDs (@ -> %40)
        encoded_chat_id = quote(chat_id, safe="")
        encoded_message_id = quote(message_id, safe="")

        result = await waha.edit_message(
            session=session.name,
            chat_id=encoded_chat_id,
            message_id=encoded_message_id,
            text=request.text,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        # URL encode IDs (@ -> %40)
        encoded_chat_id = quote(chat_id, safe="")
        encoded_message_id = quote(message_id, safe="")

        result = await waha.delete_message(
            session=session.name,
            chat_id=encoded_chat_id,
            message_id=encoded_message_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.send_link_custom_preview(
            session=session.name,
            chat_id=request.chat_id,
            text=request.text,
            title=request.title,
            description=request.description,
            image_url=request.image_url,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

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
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.send_event(
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
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.check_number_exists(
            session=session.name,
            phone=phone,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.get_contact_about(
            session=session.name,
            contact_id=contact_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.get_contact_profile_picture(
            session=session.name,
            contact_id=contact_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.block_contact(
            session=session.name,
            contact_id=request.contact_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.unblock_contact(
            session=session.name,
            contact_id=request.contact_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


# ============================================================================
# PRESENCE
# ============================================================================


@router.post(
    "/presence",
    status_code=status.HTTP_201_CREATED,
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.set_presence(
            session=session.name,
            presence=request.presence,
            chat_id=request.chat_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.get_all_presence(session=session.name)
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.get_presence(
            session=session.name,
            chat_id=chat_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.subscribe_presence(
            session=session.name,
            chat_id=chat_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


# ============================================================================
# AUTHENTICATION
# ============================================================================


@router.get(
    "/auth/qr",
    tags=["Authentication"],
    dependencies=[Depends(get_current_user)],
)
async def get_qr_code_auth(
    format: str = "image",
    waha: WAHAClient = Depends(get_waha_client),
    db: Session = Depends(get_db),
):
    """Get QR code for authentication."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.get_qr_code_auth(
            session=session.name,
            format=format,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.request_auth_code(
            session=session.name,
            phone_number=request.phone_number,
            method=request.method,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.reject_call(
            session=session.name,
            call_id=request.call_id,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.convert_voice_to_opus(
            session=session.name,
            file_url=request.file_url,
            file_data=request.file_data,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.convert_video_to_mp4(
            session=session.name,
            file_url=request.file_url,
            file_data=request.file_data,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
        result = await waha.health_check()
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
        result = await waha.ping()
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.get(
    "/server/version",
    tags=["Observability"],
)
async def get_version(
    waha: WAHAClient = Depends(get_waha_client),
):
    """Get WAHA server version."""
    try:
        result = await waha.get_server_version()
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.get(
    "/server/status",
    tags=["Observability"],
)
async def get_status(
    waha: WAHAClient = Depends(get_waha_client),
):
    """Get WAHA server status."""
    try:
        result = await waha.get_server_status()
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active session"
            )

        result = await waha.screenshot(session=session.name)
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
