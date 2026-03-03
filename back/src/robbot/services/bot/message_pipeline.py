"""
MessagePipeline - Handles inbound message preprocessing and validation.

Extracted from ConversationOrchestrator (Issue #7: God Object Decomposition)

Responsibilities:
- Validate incoming messages
- Extract message metadata (type, media, etc)
- Transcribe audio/video if present
- Save message to database
"""

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.conversation_message_repository import (
    ConversationMessageRepository,
)
from robbot.core.custom_exceptions import DatabaseError, ValidationError
from robbot.domain.shared.enums import MessageDirection, MessageType
from robbot.infra.persistence.models.conversation_message_model import ConversationMessageModel
from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.services.communication.message_processor import MessageProcessor

logger = logging.getLogger(__name__)


class MessagePipeline:
    """
    Process inbound WhatsApp messages through validation and storage pipeline.

    Replaces ConversationOrchestrator.process_message_pipeline().
    """

    def __init__(
        self,
        db: Session,
        message_processor: MessageProcessor,
    ):
        """
        Initialize MessagePipeline with dependencies.

        Args:
            db: SQLAlchemy session
            message_processor: Service for processing media
        """
        self.db = db
        self.message_processor = message_processor
        self.message_repo = ConversationMessageRepository(db)

    async def validate_message(self, content: str, max_length: int = 4096) -> bool:
        """
        Validate inbound message content.

        Args:
            content: Message text
            max_length: Maximum allowed length

        Returns:
            True if valid

        Raises:
            ValidationError: If message is invalid
        """
        if not content:
            raise ValidationError("Message content cannot be empty")

        if len(content) > max_length:
            raise ValidationError(f"Message exceeds maximum length ({len(content)} > {max_length})")

        # Check for injection patterns
        injection_patterns = ["<script", "javascript:", "onclick=", "onerror="]
        content_lower = content.lower()
        for pattern in injection_patterns:
            if pattern in content_lower:
                raise ValidationError(f"Message contains suspicious pattern: {pattern}")

        return True

    async def process_message(
        self,
        conversation: ConversationModel,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        has_media: bool = False,
        media_url: str | None = None,
    ) -> ConversationMessageModel:
        """
        Process inbound message through validation and storage pipeline.

        Args:
            conversation: Conversation context
            content: Message content/text
            message_type: Type of message (text, audio, video, etc)
            has_media: Whether message contains media
            media_url: URL of media if present

        Returns:
            Stored message model

        Raises:
            ValidationError: If message fails validation
            DatabaseError: If storage fails
        """
        try:
            # Step 1: Validate message
            await self.validate_message(content)

            # Step 2: Process media if present
            processed_content = content
            if has_media and media_url:
                logger.info("[INFO] Processing media for message")
                processed_content = await self.message_processor.process_media_message(
                    message_text=content,
                    has_audio=message_type == MessageType.AUDIO,
                    audio_url=media_url if message_type == MessageType.AUDIO else None,
                    has_video=message_type == MessageType.VIDEO,
                    video_url=media_url if message_type == MessageType.VIDEO else None,
                )

            # Step 3: Create message model
            message = ConversationMessageModel(
                conversation_id=conversation.id,
                direction=MessageDirection.INBOUND,
                message_type=message_type,
                content=processed_content,
                created_at=datetime.now(UTC),
            )

            # Step 4: Store in database
            stored = self.message_repo.create(message)
            self.db.flush()

            logger.info(
                "[SUCCESS] Message stored (id=%s, type=%s)",
                stored.id,
                message_type,
            )

            return stored

        except ValidationError:
            raise
        except Exception as e:
            logger.error("[ERROR] Failed to process message: %s", e)
            raise DatabaseError(f"Failed to store message: {e}") from e

    async def save_response(
        self,
        conversation: ConversationModel,
        response_text: str,
    ) -> ConversationMessageModel:
        """
        Save bot response to message history.

        Args:
            conversation: Conversation context
            response_text: Response text from bot

        Returns:
            Stored response message

        Raises:
            DatabaseError: If storage fails
        """
        try:
            # Validate response
            await self.validate_message(response_text)

            # Create response message
            message = ConversationMessageModel(
                conversation_id=conversation.id,
                direction=MessageDirection.OUTBOUND,
                message_type=MessageType.TEXT,
                content=response_text,
                created_at=datetime.now(UTC),
            )

            # Store
            stored = self.message_repo.create(message)
            self.db.flush()

            logger.info("[SUCCESS] Response stored (id=%s)", stored.id)

            return stored

        except Exception as e:
            logger.error("[ERROR] Failed to save response: %s", e)
            raise DatabaseError(f"Failed to save response: {e}") from e

