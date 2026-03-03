"""WAHA (WhatsApp HTTP API) client implementation.

Official docs: https://waha.devlike.pro/docs/overview/introduction/
Swagger: https://waha.devlike.pro/swagger/
"""

import asyncio
import logging
import random
import time
from typing import Any

import httpx

from robbot.config.settings import settings
from robbot.core.custom_exceptions import WAHAError
from robbot.core.text_sanitizer import enforce_whatsapp_style

logger = logging.getLogger(__name__)


class WAHAClient:
    """Async HTTP client for WAHA API with anti-ban features."""

    _DEFAULT_WEBHOOK_EVENTS = ["message", "message.any", "session.status"]

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
        if settings.DEV_MODE and settings.WAHA_MOCK_REQUESTS:
            return self._mock_request(method, endpoint, **kwargs)

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
                "WAHA HTTP error %s: %s",
                e.response.status_code,
                error_detail,
                extra={"endpoint": endpoint, "method": method},
            )
            raise WAHAError(
                f"WAHA API error: {e.response.status_code} - {error_detail}",
                original_error=e,
                status_code=e.response.status_code,
            ) from e

        except httpx.TimeoutException as e:
            logger.error(
                "WAHA timeout on %s %s",
                method,
                endpoint,
                extra={"timeout": self.timeout},
            )
            raise WAHAError(f"WAHA timeout after {self.timeout}s", original_error=e) from e

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(
                "WAHA unexpected error: %s",
                e,
                extra={"endpoint": endpoint, "method": method},
            )
            raise WAHAError(f"WAHA request failed: {e}", original_error=e) from e

    def _mock_request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Return mock WAHA responses for DEV_MODE."""
        payload = kwargs.get("json") or {}

        if endpoint == "/api/sessions" and method == "GET":
            return [
                {
                    "name": "default",
                    "status": "STOPPED",
                    "qr": None,
                }
            ]

        if endpoint == "/api/sessions" and method == "POST":
            name = payload.get("name", "default")
            return {
                "name": name,
                "status": "STOPPED",
                "qr": None,
            }

        if endpoint.startswith("/api/sessions/"):
            session_name = endpoint.split("/api/sessions/")[-1].split("/")[0]
            if endpoint.endswith("/start") and method == "POST":
                return {"name": session_name, "status": "STARTING"}
            if endpoint.endswith("/restart") and method == "POST":
                return {"name": session_name, "status": "STARTING"}
            if endpoint.endswith("/stop") and method == "POST":
                return {"name": session_name, "status": "STOPPED"}
            if endpoint.endswith("/logout") and method == "POST":
                return {"name": session_name, "status": "STOPPED"}
            if method == "GET":
                return {
                    "name": session_name,
                    "status": "SCAN_QR_CODE",
                    "qr": None,
                }

        if endpoint.endswith("/presence") and method == "POST":
            return {"success": True}
        if endpoint.endswith("/presence") and method == "GET":
            return []

        if endpoint == "/api/sendText" and method == "POST":
            return {
                "message_id": "mock-message-id",
                "timestamp": int(time.time()),
                "chat_id": payload.get("chatId"),
                "success": True,
            }

        if endpoint in {"/api/startTyping", "/api/stopTyping", "/api/sendSeen"} and method == "POST":
            return {"success": True}

        if endpoint == "/api/server/status" and method == "GET":
            return {"status": "ok"}

        return {"success": True}

    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================

    async def create_session(
        self,
        name: str,
        webhook_url: str | None = None,
        config: dict | None = None,
    ) -> dict[str, Any]:
        """Create new WhatsApp session.

        Args:
            name: Session name (e.g., 'default')
            webhook_url: Webhook URL for events
            config: Optional WAHA session config

        Returns:
            Session data dict

        Docs: POST /api/sessions
        """
        payload: dict[str, Any] = {"name": name}

        if config:
            payload["config"] = config

        if webhook_url:
            self._apply_webhook_config(payload, webhook_url)

        logger.info("[INFO] Creating WAHA session: %s", name)
        return await self._request("POST", "/api/sessions", json=payload)

    async def update_session(
        self,
        name: str,
        webhook_url: str | None = None,
        config: dict | None = None,
    ) -> dict[str, Any]:
        """Update an existing WhatsApp session.

        Args:
            name: Session name
            webhook_url: Webhook URL for events
            config: Optional WAHA session config

        Returns:
            Session data dict

        Docs: PUT /api/sessions/{name}
        """
        payload: dict[str, Any] = {}

        if config:
            payload["config"] = config

        if webhook_url:
            self._apply_webhook_config(payload, webhook_url)

        logger.info("[INFO] Updating WAHA session: %s", name)
        return await self._request("PUT", f"/api/sessions/{name}", json=payload)

    def _apply_webhook_config(self, payload: dict[str, Any], webhook_url: str) -> None:
        cfg = payload.setdefault("config", {})
        webhooks = cfg.setdefault("webhooks", [])
        if webhooks:
            webhooks[0]["url"] = webhook_url
            existing_events = webhooks[0].get("events") or []
            webhooks[0]["events"] = list(dict.fromkeys(existing_events + self._DEFAULT_WEBHOOK_EVENTS))
        else:
            webhooks.append({"url": webhook_url, "events": self._DEFAULT_WEBHOOK_EVENTS})

    async def start_session(self, name: str) -> dict[str, Any]:
        """Start WhatsApp session (generates QR code).

        Args:
            name: Session name

        Returns:
            Success response

        Docs: POST /api/sessions/{name}/start
        """
        logger.info("[INFO] Starting WAHA session: %s", name)
        return await self._request("POST", f"/api/sessions/{name}/start")

    async def stop_session(self, name: str) -> dict[str, Any]:
        """Stop WhatsApp session.

        Args:
            name: Session name

        Returns:
            Success response

        Docs: POST /api/sessions/{name}/stop
        """
        logger.info("[INFO] Stopping WAHA session: %s", name)
        return await self._request("POST", f"/api/sessions/{name}/stop")

    async def restart_session(self, name: str) -> dict[str, Any]:
        """Restart WhatsApp session.

        Args:
            name: Session name

        Returns:
            Success response

        Docs: POST /api/sessions/{name}/restart
        """
        logger.info("[INFO] Restarting WAHA session: %s", name)
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

    async def list_sessions(self) -> list[dict[str, Any]]:
        """List all WAHA sessions.

        Returns:
            List of session dicts

        Docs: GET /api/sessions
        """
        result = await self._request("GET", "/api/sessions")
        # WAHA returns a JSON array; ensure list type
        if isinstance(result, list):
            return result
        # Some versions may wrap; normalize to list
        return result.get("sessions", []) if isinstance(result, dict) else []

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
        logger.info("[INFO] Logging out WAHA session: %s", name)
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
        payload = {"session": session, "chatId": chat_id, "messageId": message_id}
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
        text = enforce_whatsapp_style(text)
        if apply_anti_ban:
            logger.info("[ANTI-BAN] Applying delays (chars=%s, chat_id=%s)", len(text), chat_id)
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

        logger.info("[INFO] Sending text to %s: %s...", chat_id, text[:50])
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

        payload = {"session": session, "chatId": chat_id, "file": {"url": file_url, "mimetype": mimetype}}
        if filename:
            payload["file"]["filename"] = filename
        if caption:
            payload["caption"] = caption

        logger.info("[INFO] Sending image to %s", chat_id)
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
        payload = {"session": session, "chatId": chat_id, "file": {"url": file_url}}
        if filename:
            payload["file"]["filename"] = filename
        if mimetype:
            payload["file"]["mimetype"] = mimetype
        if caption:
            payload["caption"] = caption

        logger.info("[INFO] Sending file to %s: %s", chat_id, filename)
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

        logger.info("[INFO] Sending location to %s", chat_id)
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
        """Apply WhatsApp anti-ban best practices with session heartbeat.

        Flow:
        1. Start typing indicator
        2. Wait random delay (30-60s base + message length factor)
           - Ping session status every 10 seconds to keep it alive
        3. Stop typing

        Note: sendSeen skipped here as we don't have message_id context.
        Call send_seen() explicitly when replying to a message.
        """
        try:
            # Start typing
            await self.start_typing(session, chat_id)

            # Calculate human-like delay based on message length
            # Base: from settings, +0.1s per character (simulate reading/typing)
            base_delay = random.uniform(
                settings.WAHA_MIN_DELAY_SECONDS,
                settings.WAHA_MAX_DELAY_SECONDS
            )
            typing_delay = len(text) * 0.1
            total_delay = min(base_delay + typing_delay, 120)  # Max 2min

            logger.info("Anti-ban delay: %.1fs for %s chars", total_delay, len(text))

            # Sleep in intervals with heartbeat pings to keep session alive
            # Ping every 10 seconds to prevent session timeout
            heartbeat_interval = 10
            elapsed = 0.0

            while elapsed < total_delay:
                sleep_time = min(heartbeat_interval, total_delay - elapsed)
                await asyncio.sleep(sleep_time)
                elapsed += sleep_time

                # Send heartbeat ping to keep session alive (non-critical)
                if elapsed < total_delay:
                    try:
                        await self.get_session_status(session)
                        logger.info("[HEARTBEAT] Session alive: %s (elapsed: %.1fs)", session, elapsed)
                    except Exception as e:  # noqa: BLE001
                        # Heartbeat failure is non-critical, just log and continue
                        logger.warning("[HEARTBEAT] Ping failed (non-critical): %s", e)

            # Stop typing before sending
            await self.stop_typing(session, chat_id)

        except Exception as e:  # noqa: BLE001 (blind exception)  # pylint: disable=broad-exception-caught
            # Don't fail message sending if anti-ban flow fails
            logger.warning("[WARNING] Anti-ban flow error (non-critical): %s", e)

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

        logger.info("[INFO] Editing message %s in %s", message_id, chat_id)
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

        logger.info("[INFO] Deleting message %s from %s", message_id, chat_id)
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

        logger.info("Getting messages from %s (limit=%s, offset=%s)", chat_id, limit, offset)
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

        logger.info("[INFO] Sending link with custom preview to %s: %s", chat_id, title)
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

        logger.info("[INFO] Sending event '%s' to %s", name, chat_id)
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
        payload = {"session": session, "chatId": chat_id, "file": {"mimetype": mimetype}}
        if file_url:
            payload["file"]["url"] = file_url
        elif file_data:
            payload["file"]["data"] = file_data
        if convert:
            payload["convert"] = convert

        logger.info("[INFO] Sending voice to %s", chat_id)
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
        payload = {"session": session, "chatId": chat_id, "file": {"mimetype": mimetype}}
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

        logger.info("[INFO] Sending video to %s", chat_id)
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

        logger.info("[INFO] Sending buttons to %s", chat_id)
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

        logger.info("[INFO] Sending list to %s", chat_id)
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

        logger.info("[INFO] Sending poll to %s", chat_id)
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

        logger.info("[INFO] Voting on poll in %s", chat_id)
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

        logger.info("Sending %s contact(s) to %s", len(contacts), chat_id)
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

        logger.info("Clicking button '%s' in %s", selected_display_text, chat_id)
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

        logger.info("Forwarding message to %s", chat_id)
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

        logger.info("Reacting with '%s' to message", reaction)
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

        logger.info("Star=%s message in %s", star, chat_id)
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

        logger.info("Blocking contact: %s", contact_id)
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

        logger.info("Unblocking contact: %s", contact_id)
        return await self._request("POST", "/api/contacts/unblock", json=payload)

    # ========================================================================
    # LID (Lightweight ID) RESOLUTION
    # ========================================================================

    async def get_phone_by_lid(
        self,
        session: str,
        lid: str,
    ) -> dict[str, Any] | None:
        """Resolve WhatsApp LID to real phone number.

        Args:
            session: Session name (e.g., 'default')
            lid: LID identifier (e.g., '24988337893388@lid' or '24988337893388')

        Returns:
            {"lid": "123@lid", "pn": "123456789@c.us"} or None if not found

        Note:
            - Only works if contact exists in session's contact list
            - Returns None if contact not found (404)
            - For group messages, bot must be admin to resolve participant LIDs

        Docs: GET /api/{session}/lids/{lid}
        """
        # Normalize LID format (remove @lid if present for URL)
        lid_normalized = lid.split("@")[0] if "@" in lid else lid
        lid_url_param = f"{lid_normalized}@lid"

        # URL encode @ symbol
        lid_encoded = lid_url_param.replace("@", "%40")

        try:
            response = await self._request("GET", f"/api/{session}/lids/{lid_encoded}")
            logger.debug("LID resolved: %s -> %s", lid, response.get("pn"))
            return response
        except WAHAError as e:
            if "404" in str(e):
                logger.debug("LID not found in contact list: %s", lid)
                return None
            raise

    async def get_lid_by_phone(
        self,
        session: str,
        phone: str,
    ) -> dict[str, Any] | None:
        """Resolve phone number to WhatsApp LID.

        Args:
            session: Session name
            phone: Phone number (e.g., '123456789' or '123456789@c.us')

        Returns:
            {"lid": "123@lid", "pn": "123456789@c.us"} or None if not found

        Note:
            - Only works if contact exists in session's contact list
            - Returns None if contact not found (404)

        Docs: GET /api/{session}/lids/pn/{phoneNumber}
        """
        # Normalize phone format (remove @c.us if present)
        phone_normalized = phone.split("@")[0] if "@" in phone else phone

        try:
            response = await self._request("GET", f"/api/{session}/lids/pn/{phone_normalized}")
            logger.debug("Phone resolved to LID: %s -> %s", phone, response.get("lid"))
            return response
        except WAHAError as e:
            if "404" in str(e):
                logger.debug("Phone not found in contact list: %s", phone)
                return None
            raise

    async def get_all_lids(
        self,
        session: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get all known LID mappings from contact list.

        Args:
            session: Session name
            limit: Number of records (default: 100)
            offset: Pagination offset (default: 0)

        Returns:
            List of {"lid": "123@lid", "pn": "123456789@c.us"} mappings

        Docs: GET /api/{session}/lids?limit=100&offset=0
        """
        params = {"limit": limit, "offset": offset}
        response = await self._request("GET", f"/api/{session}/lids", params=params)
        return response if isinstance(response, list) else []

    async def update_contact(
        self,
        session: str,
        chat_id: str,
        name: str,
    ) -> dict[str, Any]:
        """Create or update contact in WhatsApp contact list.

        Args:
            session: Session name
            chat_id: Contact chat ID (phone with @c.us or LID with @lid)
            name: Contact name to save

        Returns:
            Success response

        Docs: PUT /api/{session}/contacts/{chatId}
        
        Note: Adding a contact to WhatsApp's contact list is REQUIRED
        before LID resolution will work. WAHA can only resolve LIDs for
        contacts that exist in the WhatsApp contact list.
        """
        payload = {"name": name}
        logger.info(
            "[WAHA_CLIENT] Updating contact: chat_id='%s', name='%s', session='%s'",
            chat_id,
            name,
            session,
        )
        return await self._request(
            "PUT", f"/api/{session}/contacts/{chat_id}", json=payload
        )

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

        logger.info("Setting presence: %s", presence)
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
        logger.info("Subscribing to presence for %s", chat_id)
        return await self._request("POST", f"/api/{session}/presence/{chat_id}/subscribe")

    # ========================================================================
    # AUTHENTICATION (QR Code & Code-based Auth)
    # ========================================================================

    async def get_qr_code_auth(
        self,
        session: str,
        image_format: str = "image",
    ) -> dict[str, Any] | bytes:
        """Get QR code for authentication.

        Args:
            session: Session name
            image_format: 'image' for PNG or 'raw' for JSON with base64

        Returns:
            PNG image bytes or JSON with QR data

        Docs: GET /api/{session}/auth/qr
        """
        params = {"format": image_format}
        # For image format, might return binary
        return await self._request("GET", f"/api/{session}/auth/qr", params=params)

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

        logger.info("Requesting auth code for %s", phone_number)
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

        logger.info("Rejecting call: %s", call_id)
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
        return await self._request("POST", f"/api/{session}/media/convert/voice", json=payload)

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
        return await self._request("POST", f"/api/{session}/media/convert/video", json=payload)

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

    async def get_server_environment(self, include_all: bool = False) -> dict[str, Any]:
        """Get WAHA server environment info.

        Args:
            all: Include all environment variables

        Returns:
            Environment data

        Docs: GET /api/server/environment
        """
        params = {"all": include_all}
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
        logger.info("Taking screenshot of session: %s", session)
        return await self._request("GET", "/api/screenshot", params=params)


# ============================================================================
# FACTORY FUNCTION (singleton pattern for global session)
# ============================================================================

_waha_client_instance: WAHAClient | None = None


def get_waha_client() -> WAHAClient:  # pylint: disable=global-statement
    """Get or create singleton WAHA client instance.

    Returns:
        Shared WAHAClient instance
    """
    global _waha_client_instance
    if _waha_client_instance is None:
        _waha_client_instance = WAHAClient()
    return _waha_client_instance


async def close_waha_client():  # pylint: disable=global-statement
    """Close global WAHA client connection."""
    global _waha_client_instance
    if _waha_client_instance:
        await _waha_client_instance.close()
        _waha_client_instance = None

