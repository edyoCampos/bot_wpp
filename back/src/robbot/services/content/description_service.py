"""DescriptionService for media analysis with BLIP-2 (open source, local, no cost)."""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.conversation_message_repository import ConversationMessageRepository
from robbot.core.custom_exceptions import NotFoundException
from robbot.services.content.vision_service import get_vision_service

logger = logging.getLogger(__name__)


class DescriptionService:
    """
    Generate metadata for media messages using BLIP-2.

    Local analysis with no API costs:
    - Images: BLIP-2 (Salesforce) - image captioning + VQA
    - Videos: Frame extraction + BLIP-2 analysis
    - Documents/Voice: Metadata based on filename/caption

    Model: Salesforce/blip-image-captioning-base
    - Open source (BSD-3 License)
    - ~990MB initial download
    - Runs on CPU (local inference)
    - Zero API cost

    Returns:
    - title: Short title (max 50 chars)
    - description: Detailed visual analysis description
    - tags: Relevant tags (comma-separated)
    """

    def __init__(self, db: Session):
        """Initialize description service with BLIP-2."""
        self.db = db
        self.message_repo = ConversationMessageRepository(db)
        logger.info("[SUCCESS] DescriptionService initialized (BLIP-2 local, no cost)")

    def generate_description(self, message_id: UUID, use_vision: bool = True) -> dict[str, str | None]:
        """
        Generate metadata for a message using BLIP-2 or basic metadata.

        Args:
            message_id: Message ID to analyze
            use_vision: If True, use BLIP-2 for images/videos (default)

        Returns:
            Dict with keys: generated_title, generated_description, suggested_tags

        Raises:
            NotFoundException: If message not found
        """
        # Find message
        message = self.message_repo.get_by_id(message_id)
        if not message:
            raise NotFoundException(f"Message {message_id} not found")

        try:
            # Extract data
            filename = ""
            caption = message.caption or ""
            media_url = ""

            if message.media and len(message.media) > 0:
                filename = message.media[0].filename or ""
                media_url = message.media[0].url or ""

            # If it's an image and vision is enabled, use BLIP-2
            if message.type == "image" and use_vision and media_url:
                return self.analyze_image_with_blip(media_url, caption)

            # If it's a video, analyze first frame (simplified: use metadata)
            # TODO: Implement frame extraction + BLIP-2

            # For other types or if vision is disabled, use basic metadata
            return self.generate_file_metadata(filename, caption, message.type)

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Error generating description for message %s: %s", message_id, e)
            # Fallback to basic metadata
            return self.generate_file_metadata(filename, caption, message.type)

    def analyze_image_with_blip(self, image_url: str, caption: str) -> dict[str, str | None]:
        """
        Analyze image using BLIP-2 (local, no cost).

        Public method — used by `message_service.py`.

        Args:
            image_url: Image URL
            caption: User-provided caption

        Returns:
            Dict with title, description, tags
        """
        try:
            vision = get_vision_service()

            # Analyze image with medical context
            result = vision.analyze_image_sync(image_url, context="medical")

            # Use BLIP caption as title (or user caption if provided)
            title = caption[:50] if caption else result["caption"][:50]

            # Detailed description from BLIP
            description = result["detailed_description"]
            if caption:
                description = f"{caption}. Análise visual: {description}"

            # Tags from BLIP + keywords from caption
            tags = result["tags"]

            logger.info("[SUCCESS] BLIP-2 analyzed image: %s...", title[:30])

            return {"generated_title": title, "generated_description": description, "suggested_tags": tags}

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Error using BLIP-2: %s", e)
            # Fallback to basic metadata
            logger.warning("[WARNING] Using fallback to basic metadata")
            return self.generate_file_metadata(image_url.split("/")[-1], caption, "image")

    def generate_file_metadata(self, filename: str, caption: str, file_type: str) -> dict[str, str | None]:
        """
        Generate basic metadata WITHOUT using external APIs (zero cost).

        Public method — used by `message_service.py`.

        Based on:
        - File extension
        - File name
        - User-provided caption
        - Media type

        Returns a simple structured metadata dict.
        """
        import os

        # Extract extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower().replace(".", "")

        # Map extensions to context
        extension_context = {
            # Imagens
            "jpg": "imagem",
            "jpeg": "imagem",
            "png": "imagem",
            "gif": "imagem",
            "webp": "imagem",
            # Vídeos
            "mp4": "vídeo",
            "avi": "vídeo",
            "mov": "vídeo",
            "mkv": "vídeo",
            "webm": "vídeo",
            # Áudio
            "mp3": "áudio",
            "ogg": "áudio",
            "wav": "áudio",
            "opus": "áudio",
            "oga": "áudio",
            # Documentos
            "pdf": "documento PDF",
            "doc": "documento Word",
            "docx": "documento Word",
            "xls": "planilha Excel",
            "xlsx": "planilha Excel",
            "ppt": "apresentação",
            "pptx": "apresentação",
            "txt": "arquivo de texto",
        }

        media_context = extension_context.get(ext, file_type)

        # Generate title based on caption or filename
        if caption and len(caption) > 0:
            title = caption[:50]
        else:
            # Clean filename (remove extension and underscores)
            clean_name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
            title = clean_name[:50] if clean_name else f"{file_type.capitalize()}"

        # Generate description
        description_parts = []
        if caption:
            description_parts.append(f"Descrição: {caption}")
        if filename:
            description_parts.append(f"Arquivo: {filename}")
        description_parts.append(f"Tipo: {media_context}")

        description = " | ".join(description_parts)

        # Generate tags based on medical context (weight loss focus)
        base_tags = [file_type, media_context]

        # Contextual tags based on keywords
        text_to_analyze = f"{filename} {caption}".lower()

        keyword_tags = {
            "dieta": "dieta",
            "exercicio": "exercício",
            "peso": "controle de peso",
            "alimenta": "alimentação",
            "receita": "receita",
            "consulta": "consulta",
            "exame": "exame",
            "resultado": "resultado",
            "duvida": "dúvida",
            "pergunta": "pergunta",
            "tratamento": "tratamento",
            "medicamento": "medicamento",
            "prescrição": "prescrição",
        }

        for keyword, tag in keyword_tags.items():
            if keyword in text_to_analyze:
                base_tags.append(tag)

        tags = ", ".join(base_tags[:8])  # Max 8 tags

        logger.info("[SUCCESS] Basic metadata generated: title='%s...', %s tags", title[:30], len(base_tags))

        return {"generated_title": title, "generated_description": description, "suggested_tags": tags}

