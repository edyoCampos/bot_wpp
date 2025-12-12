"""WAHA (WhatsApp HTTP API) client implementation.

Official docs: https://waha.devlike.pro/docs/overview/introduction/
Swagger: https://waha.devlike.pro/swagger/
"""

import asyncio
import logging
import random
from typing import Any

import httpx
from robbot.config.settings import settings
from robbot.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class WAHAClient:
    """Async HTTP client for WAHA API with anti-ban features."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int = 30,
    ):
        """Initialize WAHA client.

        Args:
            base_url: WAHA API base URL (default from settings)
            api_key: API key for authentication (default from settings)
            timeout: Request timeout in seconds
        """
        self.base_url = (base_url or settings.WAHA_URL).rstrip("/")
        self.api_key = api_key or settings.WAHA_API_KEY
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, *args):
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["X-Api-Key"] = self.api_key

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout,
                follow_redirects=True,
            )

    async def close(self):
        """Close HTTP client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional httpx request params

        Returns:
            Response JSON as dict

        Raises:
            ExternalServiceError: On HTTP errors or timeouts
        """
        await self._ensure_client()

        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()

            # Handle empty responses (204 No Content)
            if response.status_code == 204 or not response.content:
                return {"success": True}

            return response.json()

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(
                f"WAHA HTTP error {e.response.status_code}: {error_detail}",
                extra={"endpoint": endpoint, "method": method},
            )
            raise ExternalServiceError(
                f"WAHA API error: {e.response.status_code} - {error_detail}"
            ) from e

        except httpx.TimeoutException as e:
            logger.error(
                f"WAHA timeout on {method} {endpoint}",
                extra={"timeout": self.timeout},
            )
            raise ExternalServiceError(
                f"WAHA timeout after {self.timeout}s"
            ) from e

        except Exception as e:
            logger.error(
                f"WAHA unexpected error: {e}",
                extra={"endpoint": endpoint, "method": method},
            )
            raise ExternalServiceError(f"WAHA request failed: {e}") from e

    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================

    async def create_session(
        self,
        name: str,
        webhook_url: str | None = None,
        **config: Any,
    ) -> dict[str, Any]:
        """Create new WhatsApp session.

        Args:
            name: Session name (e.g., 'default')
            webhook_url: Webhook URL for events
            **config: Additional session config

        Returns:
            Session data dict

        Docs: POST /api/sessions
        """
        payload = {"name": name, **config}

        if webhook_url:
            payload["config"] = payload.get("config", {})
            payload["config"]["webhooks"] = [
                {"url": webhook_url, "events": ["message"]}]

        logger.info(f"Creating WAHA session: {name}")
        return await self._request("POST", "/api/sessions", json=payload)

    async def start_session(self, name: str) -> dict[str, Any]:
        """Start WhatsApp session (generates QR code).

        Args:
            name: Session name

        Returns:
            Success response

        Docs: POST /api/sessions/{name}/start
        """
        logger.info(f"Starting WAHA session: {name}")
        return await self._request("POST", f"/api/sessions/{name}/start")

    async def stop_session(self, name: str) -> dict[str, Any]:
        """Stop WhatsApp session.

        Args:
            name: Session name

        Returns:
            Success response

        Docs: POST /api/sessions/{name}/stop
        """
        logger.info(f"Stopping WAHA session: {name}")
        return await self._request("POST", f"/api/sessions/{name}/stop")

    async def restart_session(self, name: str) -> dict[str, Any]:
        """Restart WhatsApp session.

        Args:
            name: Session name

        Returns:
            Success response

        Docs: POST /api/sessions/{name}/restart
        """
        logger.info(f"Restarting WAHA session: {name}")
        return await self._request("POST", f"/api/sessions/{name}/restart")

    async def get_session_status(self, name: str) -> dict[str, Any]:
        """Get session status and details.

        Args:
            name: Session name

        Returns:
            Session status data (status, qr, etc.)

        Docs: GET /api/sessions/{name}
        """
        return await self._request("GET", f"/api/sessions/{name}")

    async def get_qr_code(self, name: str) -> dict[str, Any]:
        """Get QR code for session pairing.

        Args:
            name: Session name

        Returns:
            Session data with qr field (base64 image)

        Docs: GET /api/sessions/{session} (qr field)
        """
        return await self._request("GET", f"/api/sessions/{name}")

    async def logout_session(self, name: str) -> dict[str, Any]:
        """Logout from WhatsApp (unlink device).

        Args:
            name: Session name

        Returns:
            Success response

        Docs: POST /api/sessions/{name}/logout
        """
        logger.info(f"Logging out WAHA session: {name}")
        return await self._request("POST", f"/api/sessions/{name}/logout")

    # ========================================================================
    # ANTI-BAN HELPERS (WhatsApp Best Practices)
    # ========================================================================

    async def send_seen(self, session: str, chat_id: str, message_id: str) -> dict[str, Any]:
        """Mark message as seen (read receipt).

        Args:
            session: Session name
            chat_id: Chat ID (phone number with @c.us suffix)
            message_id: Message ID to mark as seen

        Returns:
            Success response

        Docs: POST /api/sendSeen
        """
        payload = {"session": session,
                   "chatId": chat_id, "messageId": message_id}
        return await self._request("POST", "/api/sendSeen", json=payload)

    async def start_typing(self, session: str, chat_id: str) -> dict[str, Any]:
        """Show 'typing...' indicator.

        Args:
            session: Session name
            chat_id: Chat ID

        Returns:
            Success response

        Docs: POST /api/startTyping
        """
        payload = {"session": session, "chatId": chat_id}
        return await self._request("POST", "/api/startTyping", json=payload)

    async def stop_typing(self, session: str, chat_id: str) -> dict[str, Any]:
        """Hide 'typing...' indicator.

        Args:
            session: Session name
            chat_id: Chat ID

        Returns:
            Success response

        Docs: POST /api/stopTyping
        """
        payload = {"session": session, "chatId": chat_id}
        return await self._request("POST", "/api/stopTyping", json=payload)

    # ========================================================================
    # MESSAGE SENDING (with anti-ban delays)
    # ========================================================================

    async def send_text(
        self,
        session: str,
        chat_id: str,
        text: str,
        apply_anti_ban: bool = True,
        message_id_to_reply: str | None = None,
        link_preview: bool | None = None,
        link_preview_high_quality: bool | None = None,
        mentions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Send text message with optional anti-ban delays.

        Anti-ban flow (if enabled):
        1. Send 'seen' status
        2. Start typing indicator
        3. Wait random delay (based on message length)
        4. Stop typing
        5. Send message

        Args:
            session: Session name
            chat_id: Recipient chat ID
            text: Message text
            apply_anti_ban: Apply anti-ban delays (default True)
            message_id_to_reply: Message ID to quote/reply
            link_preview: Enable/disable link preview generation
            link_preview_high_quality: Enable high-quality link preview
            mentions: List of chat IDs to mention (e.g., ['5511999999999@c.us'] or ['all'])

        Returns:
            Sent message data

        Docs: POST /api/sendText
        """
        if apply_anti_ban:
            await self._apply_anti_ban_flow(session, chat_id, text)

        payload = {"session": session, "chatId": chat_id, "text": text}
        if message_id_to_reply:
            payload["reply_to"] = message_id_to_reply
        if link_preview is not None:
            payload["linkPreview"] = link_preview
        if link_preview_high_quality is not None:
            payload["linkPreviewHighQuality"] = link_preview_high_quality
        if mentions:
            payload["mentions"] = mentions

        logger.info(f"Sending text to {chat_id}: {text[:50]}...")
        return await self._request("POST", "/api/sendText", json=payload)

    async def send_image(
        self,
        session: str,
        chat_id: str,
        file_url: str,
        filename: str | None = None,
        mimetype: str = "image/jpeg",
        caption: str | None = None,
        apply_anti_ban: bool = True,
    ) -> dict[str, Any]:
        """Send image message.

        Args:
            session: Session name
            chat_id: Recipient chat ID
            file_url: Image URL or base64
            filename: Optional filename (e.g., 'image.jpg')
            mimetype: MIME type (default image/jpeg)
            caption: Optional caption text
            apply_anti_ban: Apply anti-ban delays

        Returns:
            Sent message data

        Docs: POST /api/sendImage
        """
        if apply_anti_ban:
            await self._apply_anti_ban_flow(session, chat_id, caption or "image")

        payload = {"session": session,
                   "chatId": chat_id, "file": {"url": file_url, "mimetype": mimetype}}
        if filename:
            payload["file"]["filename"] = filename
        if caption:
            payload["caption"] = caption

        logger.info(f"Sending image to {chat_id}")
        return await self._request("POST", "/api/sendImage", json=payload)

    async def send_file(
        self,
        session: str,
        chat_id: str,
        file_url: str,
        filename: str | None = None,
        mimetype: str | None = None,
        caption: str | None = None,
    ) -> dict[str, Any]:
        """Send file/document message.

        Args:
            session: Session name
            chat_id: Recipient chat ID
            file_url: File URL
            filename: Optional filename
            mimetype: Optional MIME type (e.g., 'application/pdf')
            caption: Optional caption

        Returns:
            Sent message data

        Docs: POST /api/sendFile
        """
        payload = {"session": session,
                   "chatId": chat_id, "file": {"url": file_url}}
        if filename:
            payload["file"]["filename"] = filename
        if mimetype:
            payload["file"]["mimetype"] = mimetype
        if caption:
            payload["caption"] = caption

        logger.info(f"Sending file to {chat_id}: {filename}")
        return await self._request("POST", "/api/sendFile", json=payload)

    async def send_location(
        self,
        session: str,
        chat_id: str,
        latitude: float,
        longitude: float,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Send location message.

        Args:
            session: Session name
            chat_id: Recipient chat ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            title: Optional location title

        Returns:
            Sent message data

        Docs: POST /api/sendLocation
        """
        payload = {
            "session": session,
            "chatId": chat_id,
            "latitude": latitude,
            "longitude": longitude,
        }
        if title:
            payload["title"] = title

        logger.info(f"Sending location to {chat_id}")
        return await self._request("POST", "/api/sendLocation", json=payload)

    # ========================================================================
    # ANTI-BAN FLOW IMPLEMENTATION
    # ========================================================================

    async def _apply_anti_ban_flow(
        self,
        session: str,
        chat_id: str,
        text: str,
    ):
        """Apply WhatsApp anti-ban best practices.

        Flow:
        1. Start typing indicator
        2. Wait random delay (30-60s base + message length factor)
        3. Stop typing

        Note: sendSeen skipped here as we don't have message_id context.
        Call send_seen() explicitly when replying to a message.
        """
        try:
            # Start typing
            await self.start_typing(session, chat_id)

            # Calculate human-like delay based on message length
            # Base: 30-60s, +0.1s per character (simulate reading/typing)
            base_delay = random.uniform(30, 60)
            typing_delay = len(text) * 0.1
            total_delay = min(base_delay + typing_delay, 120)  # Max 2min

            logger.debug(
                f"Anti-ban delay: {total_delay:.1f}s for {len(text)} chars"
            )
            await asyncio.sleep(total_delay)

            # Stop typing before sending
            await self.stop_typing(session, chat_id)

        except Exception as e:
            # Don't fail message sending if anti-ban flow fails
            logger.warning(f"Anti-ban flow error (non-critical): {e}")

    # ========================================================================
    # MESSAGE MANAGEMENT
    # ========================================================================

    async def edit_message(
        self,
        session: str,
        chat_id: str,
        message_id: str,
        text: str,
    ) -> dict[str, Any]:
        """Edit text message or media caption.

        Args:
            session: Session name
            chat_id: Chat ID (must be URL encoded: 123%40c.us)
            message_id: Message ID (must be URL encoded: true_123%40c.us_AAA)
            text: New message text

        Returns:
            Success response

        Docs: PUT /api/{session}/chats/{chatId}/messages/{messageId}
        """
        endpoint = f"/api/{session}/chats/{chat_id}/messages/{message_id}"
        payload = {"text": text}

        logger.info(f"Editing message {message_id} in {chat_id}")
        return await self._request("PUT", endpoint, json=payload)

    async def delete_message(
        self,
        session: str,
        chat_id: str,
        message_id: str,
    ) -> dict[str, Any]:
        """Delete message from chat.

        Args:
            session: Session name
            chat_id: Chat ID (must be URL encoded: 123%40c.us)
            message_id: Message ID (must be URL encoded: true_123%40c.us_AAA)

        Returns:
            Success response

        Docs: DELETE /api/{session}/chats/{chatId}/messages/{messageId}
        """
        endpoint = f"/api/{session}/chats/{chat_id}/messages/{message_id}"

        logger.info(f"Deleting message {message_id} from {chat_id}")
        return await self._request("DELETE", endpoint)

    async def get_messages(
        self,
        session: str,
        chat_id: str,
        limit: int = 100,
        offset: int = 0,
        download_media: bool = False,
    ) -> dict[str, Any]:
        """Get messages from chat (chat history).

        Args:
            session: Session name
            chat_id: Chat ID (e.g., '123@c.us')
            limit: Max messages to return (default 100)
            offset: Skip messages (for pagination)
            download_media: Download media files or not

        Returns:
            List of messages

        Docs: GET /api/{session}/chats/{chatId}/messages
        """
        endpoint = f"/api/{session}/chats/{chat_id}/messages"
        params = {
            "limit": limit,
            "offset": offset,
            "downloadMedia": download_media,
        }

        logger.info(
            f"Getting messages from {chat_id} (limit={limit}, offset={offset})")
        return await self._request("GET", endpoint, params=params)

    async def send_link_custom_preview(
        self,
        session: str,
        chat_id: str,
        text: str,
        title: str,
        description: str | None = None,
        image_url: str | None = None,
    ) -> dict[str, Any]:
        """Send link with custom preview (for sites with CAPTCHA/blocks).

        Args:
            session: Session name
            chat_id: Recipient chat ID
            text: Message text containing the link
            title: Preview title
            description: Optional preview description
            image_url: Optional preview image URL or base64

        Returns:
            Sent message data

        Docs: POST /api/send/link-custom-preview
        """
        payload = {
            "session": session,
            "chatId": chat_id,
            "text": text,
            "title": title,
        }
        if description:
            payload["description"] = description
        if image_url:
            payload["image"] = {"url": image_url}

        logger.info(f"Sending link with custom preview to {chat_id}: {title}")
        return await self._request("POST", "/api/send/link-custom-preview", json=payload)

    async def send_event(
        self,
        session: str,
        chat_id: str,
        name: str,
        start_time: int,
        end_time: int | None = None,
        description: str | None = None,
        location_name: str | None = None,
        extra_guests_allowed: bool = False,
        reply_to: str | None = None,
    ) -> dict[str, Any]:
        """Send event/calendar message.

        Args:
            session: Session name
            chat_id: Recipient chat ID
            name: Event title/name
            start_time: Unix timestamp (seconds since epoch)
            end_time: Unix timestamp or None
            description: Optional event description (supports \\n for newlines, * for bold)
            location_name: Optional event location name
            extra_guests_allowed: Allow additional guests (default False)
            reply_to: Message ID to reply to (optional)

        Returns:
            Sent message data

        Docs: POST /api/{session}/events
        """
        event_obj = {
            "name": name,
            "startTime": start_time,
            "endTime": end_time,
            "extraGuestsAllowed": extra_guests_allowed,
        }

        if description:
            event_obj["description"] = description

        if location_name:
            event_obj["location"] = {"name": location_name}

        payload = {
            "chatId": chat_id,
            "event": event_obj,
        }

        if reply_to:
            payload["reply_to"] = reply_to

        logger.info(f"Sending event '{name}' to {chat_id}")
        return await self._request("POST", f"/api/{session}/events", json=payload)

    # ========================================================================
    # CONTACT & CHAT INFO
    # ========================================================================

    async def get_contacts(self, session: str) -> dict[str, Any]:
        """Get all contacts from session.

        Args:
            session: Session name

        Returns:
            List of contacts

        Docs: GET /api/{session}/contacts
        """
        return await self._request("GET", f"/api/{session}/contacts")

    async def get_chats(self, session: str) -> dict[str, Any]:
        """Get all chats from session.

        Args:
            session: Session name

        Returns:
            List of chats

        Docs: GET /api/{session}/chats
        """
        return await self._request("GET", f"/api/{session}/chats")

    # ========================================================================
    # VOICE & VIDEO MESSAGES
    # ========================================================================

    async def send_voice(
        self,
        session: str,
        chat_id: str,
        file_url: str | None = None,
        file_data: str | None = None,
        mimetype: str = "audio/ogg; codecs=opus",
        convert: bool = False,
    ) -> dict[str, Any]:
        """Send voice message (audio).

        Args:
            session: Session name
            chat_id: Recipient chat ID
            file_url: Voice file URL
            file_data: Base64 encoded voice data
            mimetype: MIME type (default audio/ogg; codecs=opus)
            convert: Auto-convert to OPUS format if needed

        Returns:
            Sent message data

        Docs: POST /api/sendVoice
        """
        payload = {"session": session, "chatId": chat_id,
                   "file": {"mimetype": mimetype}}
        if file_url:
            payload["file"]["url"] = file_url
        elif file_data:
            payload["file"]["data"] = file_data
        if convert:
            payload["convert"] = convert

        logger.info(f"Sending voice to {chat_id}")
        return await self._request("POST", "/api/sendVoice", json=payload)

    async def send_video(
        self,
        session: str,
        chat_id: str,
        file_url: str | None = None,
        file_data: str | None = None,
        filename: str | None = None,
        mimetype: str = "video/mp4",
        caption: str | None = None,
        as_note: bool = False,
        convert: bool = False,
    ) -> dict[str, Any]:
        """Send video message.

        Args:
            session: Session name
            chat_id: Recipient chat ID
            file_url: Video file URL
            file_data: Base64 encoded video data
            filename: Optional filename (e.g., 'video.mp4')
            mimetype: MIME type (default video/mp4)
            caption: Optional caption
            as_note: Send as rounded video note
            convert: Auto-convert to MP4 format if needed

        Returns:
            Sent message data

        Docs: POST /api/sendVideo
        """
        payload = {"session": session, "chatId": chat_id,
                   "file": {"mimetype": mimetype}}
        if file_url:
            payload["file"]["url"] = file_url
        elif file_data:
            payload["file"]["data"] = file_data
        if filename:
            payload["file"]["filename"] = filename
        if caption:
            payload["caption"] = caption
        if as_note:
            payload["asNote"] = as_note
        if convert:
            payload["convert"] = convert

        logger.info(f"Sending video to {chat_id}")
        return await self._request("POST", "/api/sendVideo", json=payload)

    # ========================================================================
    # INTERACTIVE MESSAGES (Buttons, Lists, Polls)
    # ========================================================================

    async def send_buttons(
        self,
        session: str,
        chat_id: str,
        body: str,
        buttons: list[dict[str, Any]],
        header: str | None = None,
        header_image: dict[str, Any] | None = None,
        footer: str | None = None,
    ) -> dict[str, Any]:
        """Send interactive buttons message (deprecated but functional).

        Args:
            session: Session name
            chat_id: Recipient chat ID
            header: Optional header title
            header_image: Optional header image dict with mimetype, filename, url
            body: Message body
            buttons: List of button objects
            footer: Optional footer text

        Returns:
            Sent message data

        Docs: POST /api/sendButtons (deprecated)
        """
        payload = {
            "session": session,
            "chatId": chat_id,
            "body": body,
            "buttons": buttons,
        }
        if header:
            payload["header"] = header
        if header_image:
            payload["headerImage"] = header_image
        if footer:
            payload["footer"] = footer

        logger.info(f"Sending buttons to {chat_id}")
        return await self._request("POST", "/api/sendButtons", json=payload)

    async def send_list(
        self,
        session: str,
        chat_id: str,
        sections: list[dict[str, Any]],
        title: str | None = None,
        description: str | None = None,
        button: str | None = None,
        footer: str | None = None,
        reply_to: str | None = None,
    ) -> dict[str, Any]:
        """Send list/menu message with sections and rows.

        Args:
            session: Session name
            chat_id: Recipient chat ID
            sections: List of section objects with rows
            title: Optional list title
            description: Optional description
            button: Button text to open list (e.g., 'Choose')
            footer: Optional footer
            reply_to: Optional message ID to reply to

        Returns:
            Sent message data

        Docs: POST /api/sendList
        """
        message_obj = {"sections": sections}
        if title:
            message_obj["title"] = title
        if description:
            message_obj["description"] = description
        if button:
            message_obj["button"] = button
        if footer:
            message_obj["footer"] = footer

        payload = {
            "session": session,
            "chatId": chat_id,
            "message": message_obj,
        }
        if reply_to:
            payload["reply_to"] = reply_to

        logger.info(f"Sending list to {chat_id}")
        return await self._request("POST", "/api/sendList", json=payload)

    async def send_poll(
        self,
        session: str,
        chat_id: str,
        name: str,
        options: list[str],
        multiple_answers: bool = False,
    ) -> dict[str, Any]:
        """Send poll/voting message.

        Args:
            session: Session name
            chat_id: Recipient chat ID
            name: Poll question/name
            options: List of option texts
            multiple_answers: Allow multiple selections

        Returns:
            Sent message data

        Docs: POST /api/sendPoll
        """
        poll_obj = {
            "name": name,
            "options": options,
            "multipleAnswers": multiple_answers,
        }

        payload = {
            "session": session,
            "chatId": chat_id,
            "poll": poll_obj,
        }

        logger.info(f"Sending poll to {chat_id}")
        return await self._request("POST", "/api/sendPoll", json=payload)

    async def send_poll_vote(
        self,
        session: str,
        chat_id: str,
        message_id: str,
        option_index: int,
    ) -> dict[str, Any]:
        """Vote on a poll message.

        Args:
            session: Session name
            chat_id: Chat ID containing the poll
            message_id: Poll message ID
            option_index: Index of selected option

        Returns:
            Success response

        Docs: POST /api/sendPollVote
        """
        payload = {
            "session": session,
            "chatId": chat_id,
            "messageId": message_id,
            "optionIndex": option_index,
        }

        logger.info(f"Voting on poll in {chat_id}")
        return await self._request("POST", "/api/sendPollVote", json=payload)

    async def send_contact_vcard(
        self,
        session: str,
        chat_id: str,
        contacts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send contact (vCard) message.

        Args:
            session: Session name
            chat_id: Recipient chat ID
            contacts: List of contact dicts with fullName, phoneNumber, organization, whatsappId

        Returns:
            Sent message data

        Docs: POST /api/sendContactVcard
        """
        payload = {
            "session": session,
            "chatId": chat_id,
            "contacts": contacts,
        }

        logger.info(f"Sending {len(contacts)} contact(s) to {chat_id}")
        return await self._request("POST", "/api/sendContactVcard", json=payload)

    async def send_buttons_reply(
        self,
        session: str,
        chat_id: str,
        reply_to: str,
        selected_display_text: str,
        selected_button_id: str,
    ) -> dict[str, Any]:
        """Reply to a button message (click a button).

        Args:
            session: Session name
            chat_id: Chat ID
            reply_to: Button message ID to reply to
            selected_display_text: Button text that was selected
            selected_button_id: Button ID that was selected

        Returns:
            Success response

        Docs: POST /api/send/buttons/reply
        """
        payload = {
            "session": session,
            "chatId": chat_id,
            "replyTo": reply_to,
            "selectedDisplayText": selected_display_text,
            "selectedButtonID": selected_button_id,
        }

        logger.info(f"Clicking button '{selected_display_text}' in {chat_id}")
        return await self._request("POST", "/api/send/buttons/reply", json=payload)

    async def forward_message(
        self,
        session: str,
        chat_id: str,
        message_id: str,
    ) -> dict[str, Any]:
        """Forward a message to another chat.

        Args:
            session: Session name
            chat_id: Destination chat ID
            message_id: Source message ID to forward

        Returns:
            Sent message data

        Docs: POST /api/forwardMessage
        """
        payload = {
            "session": session,
            "chatId": chat_id,
            "messageId": message_id,
        }

        logger.info(f"Forwarding message to {chat_id}")
        return await self._request("POST", "/api/forwardMessage", json=payload)

    # ========================================================================
    # REACTIONS & STARS
    # ========================================================================

    async def send_reaction(
        self,
        session: str,
        message_id: str,
        reaction: str,
    ) -> dict[str, Any]:
        """React to a message with an emoji.

        Args:
            session: Session name
            message_id: Message ID to react to
            reaction: Emoji character (e.g., '👍', '❤️') or empty string to remove

        Returns:
            Success response

        Docs: PUT /api/reaction
        """
        payload = {
            "session": session,
            "messageId": message_id,
            "reaction": reaction,
        }

        logger.info(f"Reacting with '{reaction}' to message")
        return await self._request("PUT", "/api/reaction", json=payload)

    async def send_star(
        self,
        session: str,
        chat_id: str,
        message_id: str,
        star: bool = True,
    ) -> dict[str, Any]:
        """Star or unstar a message.

        Args:
            session: Session name
            chat_id: Chat ID
            message_id: Message ID to star/unstar
            star: True to star, False to unstar

        Returns:
            Success response

        Docs: PUT /api/star
        """
        payload = {
            "session": session,
            "chatId": chat_id,
            "messageId": message_id,
            "star": star,
        }

        logger.info(f"Star={star} message in {chat_id}")
        return await self._request("PUT", "/api/star", json=payload)

    # ========================================================================
    # CONTACTS
    # ========================================================================

    async def check_number_exists(
        self,
        session: str,
        phone: str,
    ) -> dict[str, Any]:
        """Check if phone number is registered on WhatsApp.

        Args:
            session: Session name
            phone: Phone number (without +, e.g., '5511999999999')

        Returns:
            Number status (exists, doesNotExist, etc.)

        Docs: GET /api/contacts/check-exists
        """
        params = {"session": session, "phone": phone}
        return await self._request("GET", "/api/contacts/check-exists", params=params)

    async def get_contact_about(
        self,
        session: str,
        contact_id: str,
    ) -> dict[str, Any]:
        """Get contact's "about" status.

        Args:
            session: Session name
            contact_id: Contact ID or phone (@c.us)

        Returns:
            About text (or None if no permission)

        Docs: GET /api/contacts/about
        """
        params = {"session": session, "contactId": contact_id}
        return await self._request("GET", "/api/contacts/about", params=params)

    async def get_contact_profile_picture(
        self,
        session: str,
        contact_id: str,
    ) -> dict[str, Any]:
        """Get contact's profile picture.

        Args:
            session: Session name
            contact_id: Contact ID or phone (@c.us)

        Returns:
            Profile picture data (base64 or URL)

        Docs: GET /api/contacts/profile-picture
        """
        params = {"session": session, "contactId": contact_id}
        return await self._request("GET", "/api/contacts/profile-picture", params=params)

    async def block_contact(
        self,
        session: str,
        contact_id: str,
    ) -> dict[str, Any]:
        """Block a contact.

        Args:
            session: Session name
            contact_id: Contact ID to block

        Returns:
            Success response

        Docs: POST /api/contacts/block
        """
        payload = {
            "session": session,
            "contactId": contact_id,
        }

        logger.info(f"Blocking contact: {contact_id}")
        return await self._request("POST", "/api/contacts/block", json=payload)

    async def unblock_contact(
        self,
        session: str,
        contact_id: str,
    ) -> dict[str, Any]:
        """Unblock a contact.

        Args:
            session: Session name
            contact_id: Contact ID to unblock

        Returns:
            Success response

        Docs: POST /api/contacts/unblock
        """
        payload = {
            "session": session,
            "contactId": contact_id,
        }

        logger.info(f"Unblocking contact: {contact_id}")
        return await self._request("POST", "/api/contacts/unblock", json=payload)

    # ========================================================================
    # PRESENCE (Online/Offline Status)
    # ========================================================================

    async def set_presence(
        self,
        session: str,
        presence: str,
        chat_id: str | None = None,
    ) -> dict[str, Any]:
        """Set session presence (online, offline, typing, recording).

        Args:
            session: Session name
            presence: Presence type (available, unavailable, composing, recording)
            chat_id: Optional chat ID for specific presence

        Returns:
            Success response

        Docs: POST /api/{session}/presence
        """
        payload = {
            "session": session,
            "presence": presence,
        }
        if chat_id:
            payload["chatId"] = chat_id

        logger.info(f"Setting presence: {presence}")
        return await self._request("POST", f"/api/{session}/presence", json=payload)

    async def get_all_presence(self, session: str) -> dict[str, Any]:
        """Get all subscribed presence information.

        Args:
            session: Session name

        Returns:
            List of presence data

        Docs: GET /api/{session}/presence
        """
        return await self._request("GET", f"/api/{session}/presence")

    async def get_presence(
        self,
        session: str,
        chat_id: str,
    ) -> dict[str, Any]:
        """Get presence for a specific chat.

        Args:
            session: Session name
            chat_id: Chat ID

        Returns:
            Presence data

        Docs: GET /api/{session}/presence/{chatId}
        """
        return await self._request("GET", f"/api/{session}/presence/{chat_id}")

    async def subscribe_presence(
        self,
        session: str,
        chat_id: str,
    ) -> dict[str, Any]:
        """Subscribe to presence updates for a chat.

        Args:
            session: Session name
            chat_id: Chat ID to subscribe

        Returns:
            Success response

        Docs: POST /api/{session}/presence/{chatId}/subscribe
        """
        logger.info(f"Subscribing to presence for {chat_id}")
        return await self._request(
            "POST", f"/api/{session}/presence/{chat_id}/subscribe"
        )

    # ========================================================================
    # AUTHENTICATION (QR Code & Code-based Auth)
    # ========================================================================

    async def get_qr_code_auth(
        self,
        session: str,
        format: str = "image",
    ) -> dict[str, Any] | bytes:
        """Get QR code for authentication.

        Args:
            session: Session name
            format: 'image' for PNG or 'raw' for JSON with base64

        Returns:
            PNG image bytes or JSON with QR data

        Docs: GET /api/{session}/auth/qr
        """
        params = {"format": format}
        # For image format, might return binary
        result = await self._request("GET", f"/api/{session}/auth/qr", params=params)
        return result

    async def request_auth_code(
        self,
        session: str,
        phone_number: str,
        method: str | None = None,
    ) -> dict[str, Any]:
        """Request authentication code for phone registration.

        Args:
            session: Session name
            phone_number: Mobile phone number (e.g., '12132132130')
            method: 'sms' or 'voice' for delivery method (None for Web pairing)

        Returns:
            Code request response

        Docs: POST /api/{session}/auth/request-code
        """
        payload = {"phoneNumber": phone_number}
        if method:
            payload["method"] = method

        logger.info(f"Requesting auth code for {phone_number}")
        return await self._request("POST", f"/api/{session}/auth/request-code", json=payload)

    # ========================================================================
    # CALLS
    # ========================================================================

    async def reject_call(
        self,
        session: str,
        call_id: str,
    ) -> dict[str, Any]:
        """Reject an incoming call.

        Args:
            session: Session name
            call_id: Call ID

        Returns:
            Success response

        Docs: POST /api/{session}/calls/reject
        """
        payload = {
            "session": session,
            "callId": call_id,
        }

        logger.info(f"Rejecting call: {call_id}")
        return await self._request("POST", f"/api/{session}/calls/reject", json=payload)

    # ========================================================================
    # MEDIA CONVERSION
    # ========================================================================

    async def convert_voice_to_opus(
        self,
        session: str,
        file_url: str | None = None,
        file_data: str | None = None,
    ) -> dict[str, Any] | bytes:
        """Convert voice file to WhatsApp format (opus/ogg).

        Args:
            session: Session name
            file_url: URL of voice file (MP3, WAV, etc.)
            file_data: Base64 encoded audio data

        Returns:
            Converted audio in opus format or error

        Docs: POST /api/{session}/media/convert/voice
        """
        payload = {}
        if file_url:
            payload["url"] = file_url
        elif file_data:
            payload["data"] = file_data

        logger.info("Converting voice to opus format")
        return await self._request(
            "POST", f"/api/{session}/media/convert/voice", json=payload
        )

    async def convert_video_to_mp4(
        self,
        session: str,
        file_url: str | None = None,
        file_data: str | None = None,
    ) -> dict[str, Any] | bytes:
        """Convert video file to WhatsApp format (mp4).

        Args:
            session: Session name
            file_url: URL of video file
            file_data: Base64 encoded video data

        Returns:
            Converted video in mp4 format or error

        Docs: POST /api/{session}/media/convert/video
        """
        payload = {}
        if file_url:
            payload["url"] = file_url
        elif file_data:
            payload["data"] = file_data

        logger.info("Converting video to mp4 format")
        return await self._request(
            "POST", f"/api/{session}/media/convert/video", json=payload
        )

    # ========================================================================
    # SERVER OBSERVABILITY
    # ========================================================================

    async def ping(self) -> dict[str, Any]:
        """Ping the WAHA server.

        Returns:
            Ping response

        Docs: GET /ping
        """
        return await self._request("GET", "/ping")

    async def health_check(self) -> dict[str, Any]:
        """Check WAHA server health.

        Returns:
            Health status

        Docs: GET /health
        """
        return await self._request("GET", "/health")

    async def get_server_version(self) -> dict[str, Any]:
        """Get WAHA server version.

        Returns:
            Version information

        Docs: GET /api/server/version
        """
        return await self._request("GET", "/api/server/version")

    async def get_server_environment(self, all: bool = False) -> dict[str, Any]:
        """Get WAHA server environment info.

        Args:
            all: Include all environment variables

        Returns:
            Environment data

        Docs: GET /api/server/environment
        """
        params = {"all": all}
        return await self._request("GET", "/api/server/environment", params=params)

    async def get_server_status(self) -> dict[str, Any]:
        """Get WAHA server status.

        Returns:
            Server status data

        Docs: GET /api/server/status
        """
        return await self._request("GET", "/api/server/status")

    async def screenshot(self, session: str) -> dict[str, Any] | bytes:
        """Get screenshot of WhatsApp session.

        Args:
            session: Session name

        Returns:
            Screenshot as JPEG or base64

        Docs: GET /api/screenshot
        """
        params = {"session": session}
        logger.info(f"Taking screenshot of session: {session}")
        return await self._request("GET", "/api/screenshot", params=params)


# ============================================================================
# FACTORY FUNCTION (singleton pattern for global session)
# ============================================================================

_waha_client_instance: WAHAClient | None = None


def get_waha_client() -> WAHAClient:
    """Get or create singleton WAHA client instance.

    Returns:
        Shared WAHAClient instance
    """
    global _waha_client_instance
    if _waha_client_instance is None:
        _waha_client_instance = WAHAClient()
    return _waha_client_instance


async def close_waha_client():
    """Close global WAHA client connection."""
    global _waha_client_instance
    if _waha_client_instance:
        await _waha_client_instance.close()
        _waha_client_instance = None
