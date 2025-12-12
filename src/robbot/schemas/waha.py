"""Pydantic schemas for WAHA integration."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ============================================================================
# SESSION SCHEMAS
# ============================================================================


class SessionCreate(BaseModel):
    """Create new WAHA session."""

    name: str = Field(..., description="Session name (e.g., 'default')")
    webhook_url: str | None = Field(None, description="Webhook URL for events")


class SessionStatus(BaseModel):
    """WAHA session status response."""

    name: str
    status: str  # STOPPED, STARTING, SCAN_QR_CODE, WORKING, FAILED
    qr: str | None = None  # Base64 QR code image
    me: dict[str, Any] | None = None  # User info when connected


class SessionOut(BaseModel):
    """Session data output."""

    id: int
    name: str
    status: str
    webhook_url: str | None
    connected_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# MESSAGE SENDING SCHEMAS
# ============================================================================


class SendTextRequest(BaseModel):
    """Send text message request."""

    chat_id: str = Field(...,
                         description="Recipient chat ID (e.g., '5511999999999@c.us')")
    text: str = Field(..., min_length=1, max_length=4096)
    apply_anti_ban: bool = Field(True, description="Apply anti-ban delays")
    reply_to: str | None = Field(None, description="Message ID to reply/quote")
    link_preview: bool | None = Field(
        None, description="Enable/disable link preview generation")
    link_preview_high_quality: bool | None = Field(
        None, description="Enable high-quality link preview")
    mentions: list[str] | None = Field(
        None, description="List of chat IDs to mention (['all'] for everyone)")


class SendImageRequest(BaseModel):
    """Send image message request."""

    chat_id: str
    file_url: str = Field(..., description="Image URL or base64")
    filename: str | None = Field(
        None, description="Image filename (e.g., 'image.jpg')")
    mimetype: str = Field(
        "image/jpeg", description="MIME type (default image/jpeg)")
    caption: str | None = Field(None, max_length=1024)
    apply_anti_ban: bool = True


class SendFileRequest(BaseModel):
    """Send file/document request."""

    chat_id: str
    file_url: str
    filename: str | None = None
    mimetype: str | None = Field(
        None, description="MIME type (e.g., 'application/pdf')")
    caption: str | None = None


class SendLocationRequest(BaseModel):
    """Send location request."""

    chat_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    title: str | None = None


class MessageSentResponse(BaseModel):
    """Response after sending message."""

    message_id: str
    timestamp: int
    chat_id: str
    success: bool = True


# ============================================================================
# WEBHOOK SCHEMAS (incoming events from WAHA)
# ============================================================================


class WebhookMessage(BaseModel):
    """Incoming message from webhook."""

    id: str = Field(..., description="Message ID")
    timestamp: int
    from_: str = Field(..., alias="from", description="Sender chat ID")
    body: str | None = Field(None, description="Message text")
    hasMedia: bool = False
    type: str = Field(...,
                      description="Message type: chat, image, video, etc.")
    ack: int | None = Field(None, description="Message ACK status")


class WebhookPayload(BaseModel):
    """WAHA webhook payload wrapper."""

    event: str = Field(...,
                       description="Event type: message, message.ack, etc.")
    session: str = Field(..., description="Session name")
    payload: dict[str, Any] = Field(..., description="Event payload")


class WebhookLogOut(BaseModel):
    """Webhook log output schema."""

    id: int
    session_name: str
    event_type: str
    payload: dict[str, Any]
    processed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# VOICE & VIDEO MESSAGES
# ============================================================================


class SendVoiceRequest(BaseModel):
    """Send voice message request."""

    chat_id: str = Field(..., description="Recipient chat ID")
    file_url: str | None = Field(
        None, description="Voice file URL (MP3, WAV, etc.)")
    file_data: str | None = Field(None, description="Base64 encoded audio")
    mimetype: str = Field("audio/ogg; codecs=opus",
                          description="MIME type for WAHA")
    convert: bool = Field(False, description="Auto-convert to OPUS format")


class SendVideoRequest(BaseModel):
    """Send video message request."""

    chat_id: str = Field(..., description="Recipient chat ID")
    file_url: str | None = Field(None, description="Video file URL")
    file_data: str | None = Field(None, description="Base64 encoded video")
    filename: str | None = Field(
        None, description="Video filename (e.g., 'video.mp4')")
    mimetype: str = Field(
        "video/mp4", description="MIME type (default video/mp4)")
    caption: str | None = Field(None, max_length=1024)
    as_note: bool = Field(False, alias="asNote",
                          description="Send as rounded video note")
    convert: bool = Field(False, description="Auto-convert to MP4 format")


# ============================================================================
# INTERACTIVE MESSAGES
# ============================================================================


class ButtonOption(BaseModel):
    """Button option for interactive message."""

    type: str = Field(..., description="Button type: reply, call, copy, url")
    text: str = Field(..., min_length=1, max_length=128)
    phoneNumber: str | None = None
    copyCode: str | None = None
    url: str | None = None


class FilePreview(BaseModel):
    """File preview for buttons."""

    mimetype: str = Field(..., description="MIME type (e.g., 'image/jpeg')")
    filename: str = Field(..., description="Filename")
    url: str | None = Field(None, description="File URL")
    data: str | None = Field(None, description="Base64 encoded data")


class SendButtonsRequest(BaseModel):
    """Send buttons/interactive message request."""

    chat_id: str = Field(..., description="Recipient chat ID")
    header: str | None = Field(
        None, max_length=128, description="Button header title")
    header_image: FilePreview | None = Field(
        None, alias="headerImage", description="Header image (WAHA Plus)")
    body: str = Field(..., min_length=1, max_length=1024)
    buttons: list[ButtonOption] = Field(..., min_length=1, max_length=10)
    footer: str | None = Field(None, max_length=60)

    class Config:
        populate_by_name = True


class ListRow(BaseModel):
    """Row in list message."""

    id: str
    title: str = Field(..., max_length=128)
    description: str | None = Field(None, max_length=128)


class ListSection(BaseModel):
    """Section in list message."""

    title: str = Field(..., max_length=128)
    rows: list[ListRow] = Field(..., min_length=1, max_length=10)


class SendListRequest(BaseModel):
    """Send list/menu message request.

    Note: Structure wraps content in 'message' object with 'title', 'description', 
    'button', 'footer' and 'sections'.
    """

    chat_id: str = Field(..., description="Recipient chat ID")
    reply_to: str | None = Field(None, description="Message ID to reply to")
    message_title: str | None = Field(None, max_length=128, alias="title",
                                      description="List message title")
    message_description: str | None = Field(None, max_length=256, alias="description",
                                            description="List message description")
    button_text: str | None = Field(None, max_length=60, alias="button",
                                    description="Button label (e.g., 'Choose')")
    footer: str | None = Field(None, max_length=60, description="Footer text")
    sections: list[ListSection] = Field(...,
                                        min_length=1, description="Menu sections")

    class Config:
        populate_by_name = True


class SendPollRequest(BaseModel):
    """Send poll/voting message request."""

    chat_id: str = Field(..., description="Recipient chat ID")
    poll: dict[str, Any] = Field(
        ..., description="Poll structure with 'name', 'options', 'multipleAnswers'")


class SendPollVoteRequest(BaseModel):
    """Vote on poll message request."""

    chat_id: str = Field(..., description="Chat ID containing poll")
    message_id: str = Field(..., description="Poll message ID")
    option_index: int = Field(..., ge=0, description="Selected option index")


class SendContactVcardRequest(BaseModel):
    """Send contact (vCard) message request."""

    chat_id: str = Field(..., description="Recipient chat ID")
    contacts: list[dict[str, Any]] = Field(..., min_length=1, max_length=10,
                                           description="Contacts with fullName, phoneNumber, organization, whatsappId")


class ForwardMessageRequest(BaseModel):
    """Forward message request."""

    chat_id: str = Field(..., description="Destination chat ID")
    message_id: str = Field(..., description="Message ID to forward")


class EditMessageRequest(BaseModel):
    """Edit message request."""

    text: str = Field(..., min_length=1, max_length=4096,
                      description="New message text")


class LinkCustomPreviewRequest(BaseModel):
    """Send link with custom preview."""

    chat_id: str = Field(..., description="Recipient chat ID")
    text: str = Field(..., min_length=1, max_length=4096,
                      description="Message text with link")
    title: str = Field(..., min_length=1, max_length=256,
                       description="Preview title")
    description: str | None = Field(None, max_length=512,
                                    description="Preview description")
    image_url: str | None = Field(
        None, description="Preview image URL or base64")


# ============================================================================
# REACTIONS & STARS
# ============================================================================


class SendReactionRequest(BaseModel):
    """React to message request."""

    chat_id: str = Field(..., description="Chat ID")
    message_id: str = Field(..., description="Message ID to react to")
    reaction: str = Field(..., min_length=0, max_length=8,
                          description="Emoji char (empty string to remove)")


class SendButtonsReplyRequest(BaseModel):
    """Reply to buttons request."""

    chat_id: str = Field(..., description="Recipient chat ID")
    reply_to: str = Field(..., alias="replyTo",
                          description="Button message ID to reply to")
    selected_display_text: str = Field(..., alias="selectedDisplayText",
                                       description="Button text that was selected")
    selected_button_id: str = Field(..., alias="selectedButtonID",
                                    description="Button ID that was selected")

    class Config:
        populate_by_name = True


class SendStarRequest(BaseModel):
    """Star/unstar message request."""

    chat_id: str = Field(..., description="Chat ID")
    message_id: str = Field(..., description="Message ID to star/unstar")
    star: bool = Field(True, description="True to star, False to unstar")


# ============================================================================
# CONTACTS
# ============================================================================


class CheckNumberRequest(BaseModel):
    """Check if number exists on WhatsApp."""

    phone: str = Field(..., description="Phone without +")


class ContactBlockRequest(BaseModel):
    """Block/unblock contact request."""

    contact_id: str = Field(..., description="Contact ID or phone@c.us")


class ContactAboutResponse(BaseModel):
    """Contact about status response."""

    about: str | None = Field(None, description="About text")


# ============================================================================
# PRESENCE
# ============================================================================


class SetPresenceRequest(BaseModel):
    """Set session presence request."""

    presence: str = Field(
        ...,
        description="Presence: available, unavailable, composing, recording"
    )
    chat_id: str | None = Field(None, description="Optional specific chat")


class PresenceData(BaseModel):
    """Presence information."""

    chat_id: str
    presence: str
    last_seen: int | None = None


# ============================================================================
# AUTHENTICATION
# ============================================================================


class GetQRCodeRequest(BaseModel):
    """Get QR code request."""

    format: str = Field("image", description="Format: image or raw")


class RequestAuthCodeRequest(BaseModel):
    """Request authentication code."""

    phone_number: str = Field(..., description="Phone number")
    method: str | None = Field(None, description="sms or voice")


# ============================================================================
# CALLS
# ============================================================================


class RejectCallRequest(BaseModel):
    """Reject call request."""

    call_id: str = Field(..., description="Call ID")


class SendEventRequest(BaseModel):
    """Send event/calendar message request.

    **Note:** Times must be converted to Unix timestamp (seconds since epoch).
    Use: int(datetime.fromisoformat(iso_string.replace('Z', '+00:00')).timestamp())
    """

    chat_id: str = Field(..., description="Recipient chat ID")
    name: str = Field(..., min_length=1, max_length=256,
                      description="Event title/name")
    description: str | None = Field(None, max_length=1024,
                                    description="Event description (supports \\n for newlines, * for bold)")
    location_name: str | None = Field(None, max_length=256,
                                      alias="location",
                                      description="Event location name")
    start_time: int = Field(...,
                            description="Unix timestamp (seconds since epoch)")
    end_time: int | None = Field(None, description="Unix timestamp or null")
    extra_guests_allowed: bool = Field(False, alias="extraGuestsAllowed",
                                       description="Allow additional guests")
    reply_to: str | None = Field(
        None, description="Message ID to reply to (optional)")

    class Config:
        populate_by_name = True


# ============================================================================
# MEDIA CONVERSION
# ============================================================================


class ConvertVoiceRequest(BaseModel):
    """Convert voice to opus request."""

    file_url: str | None = Field(None, description="Voice file URL")
    file_data: str | None = Field(None, description="Base64 audio data")


class ConvertVideoRequest(BaseModel):
    """Convert video to mp4 request."""

    file_url: str | None = Field(None, description="Video file URL")
    file_data: str | None = Field(None, description="Base64 video data")


# ============================================================================
# MESSAGE RESPONSES
# ============================================================================


class MessageData(BaseModel):
    """Message data from WAHA."""

    id: str = Field(..., description="Message ID")
    timestamp: int = Field(..., description="Unix timestamp")
    from_user: str = Field(..., alias="from", description="Sender ID")
    from_me: bool = Field(..., description="Is from authenticated user")
    body: str | None = Field(None, description="Message text")
    has_media: bool = Field(False, description="Has media attachment")
    ack: int | None = Field(None, description="Acknowledgment status")
    ack_name: str | None = Field(
        None, alias="ackName", description="Ack status name")
    reply_to: str | None = Field(
        None, alias="replyTo", description="Message being replied to")

    class Config:
        populate_by_name = True


class GetMessagesResponse(BaseModel):
    """Get messages from chat response."""

    messages: list[MessageData] = Field(
        default_factory=list, description="List of messages"
    )
    total: int | None = Field(None, description="Total messages in chat")


# ============================================================================
# SERVER RESPONSES
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    timestamp: int | None = None


class ServerVersionResponse(BaseModel):
    """Server version response."""

    version: str
    engine: str | None = None


class ServerStatusResponse(BaseModel):
    """Server status response."""

    uptime: int | None = None
    sessions: int = 0
    timestamp: int | None = None


class ScreenshotResponse(BaseModel):
    """Screenshot response."""

    data: str | None = Field(None, description="Base64 image data")
    mimetype: str | None = Field(None, description="Image MIME type")
