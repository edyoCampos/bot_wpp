"""Message service orchestrating repository and business logic."""

from typing import Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from robbot.adapters.repositories.message_repository import MessageRepository
from robbot.core.exceptions import NotFoundException
from robbot.schemas.message import (
    DeletedResponse,
    MediaFile,
    MessageCreateLocation,
    MessageCreateMedia,
    MessageCreateText,
    MessageOutLocation,
    MessageOutMedia,
    MessageOutText,
    MessageUpdateLocation,
    MessageUpdateMedia,
    MessageUpdateText,
)


class MessageService:
    """Service layer for message CRUD operations."""

    def __init__(self, db: Session):
        self.repo = MessageRepository(db)

    def create_message(
        self,
        payload: Union[MessageCreateText, MessageCreateMedia, MessageCreateLocation],
    ) -> Union[MessageOutText, MessageOutMedia, MessageOutLocation]:
        """
        Create message based on type.
        For media types, file.url must be generated externally (e.g., storage upload).
        """
        if isinstance(payload, MessageCreateText):
            msg = self.repo.create_text(text=payload.text)
            return MessageOutText.model_validate(msg)

        if isinstance(payload, MessageCreateMedia):
            if not payload.file.url:
                raise ValueError("Media file URL is required")
            
            # Processar mídia automaticamente conforme tipo
            transcription = None
            title = None
            description = None
            tags = None
            
            # 1. VOICE: Transcrever áudio
            if payload.type == "voice":
                transcription = self._transcribe_audio(payload.file.url)
            
            # 2. VIDEO: Transcrever áudio + gerar metadata básico
            elif payload.type == "video":
                transcription = self._transcribe_audio(payload.file.url)
                metadata = self._generate_description(
                    payload.file.url,
                    payload.file.filename, 
                    payload.caption or "", 
                    "video"
                )
                title = metadata.get("generated_title")
                description = metadata.get("generated_description")
                tags = metadata.get("suggested_tags")
            
            # 3. IMAGE: Analisar com BLIP-2 (open source, local, sem custo)
            elif payload.type == "image":
                metadata = self._generate_description(
                    payload.file.url,
                    payload.file.filename, 
                    payload.caption or "", 
                    "image"
                )
                title = metadata.get("generated_title")
                description = metadata.get("generated_description")
                tags = metadata.get("suggested_tags")
            
            # 4. DOCUMENT: Gerar metadata baseado em filename
            elif payload.type == "document":
                metadata = self._generate_file_description(
                    payload.file.filename, 
                    payload.caption or "", 
                    "document"
                )
                title = metadata.get("generated_title")
                description = metadata.get("generated_description")
                tags = metadata.get("suggested_tags")
            
            msg = self.repo.create_media(
                msg_type=payload.type,
                mimetype=payload.file.mimetype,
                filename=payload.file.filename,
                url=payload.file.url,
                caption=payload.caption,
                transcription=transcription,
                title=title,
                description=description,
                tags=tags,
            )
            # Build response with file metadata
            media_obj = msg.media[0] if msg.media else None
            if not media_obj:
                raise NotFoundException(
                    "Media object not found after creation")

            return MessageOutMedia(
                id=msg.id,
                type=msg.type,  # type: ignore
                file=MediaFile(
                    mimetype=media_obj.mimetype,
                    filename=media_obj.filename,
                    url=media_obj.url,
                ),
                caption=msg.caption,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        if isinstance(payload, MessageCreateLocation):
            msg = self.repo.create_location(
                latitude=payload.latitude,
                longitude=payload.longitude,
                title=payload.title,
            )
            location_obj = msg.location
            if not location_obj:
                raise NotFoundException(
                    "Location object not found after creation")

            return MessageOutLocation(
                id=msg.id,
                type="location",
                latitude=location_obj.latitude,
                longitude=location_obj.longitude,
                title=location_obj.title,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        raise ValueError("Invalid message type")

    def get_message(
        self, message_id: UUID
    ) -> Union[MessageOutText, MessageOutMedia, MessageOutLocation]:
        """Retrieve message by ID."""
        msg = self.repo.get_by_id(message_id)
        if not msg:
            raise NotFoundException(f"Message {message_id} not found")

        if msg.type == "text":
            return MessageOutText.model_validate(msg)

        if msg.type in ("image", "voice", "video", "document"):
            media_obj = msg.media[0] if msg.media else None
            if not media_obj:
                raise NotFoundException("Media metadata not found")

            return MessageOutMedia(
                id=msg.id,
                type=msg.type,  # type: ignore
                file=MediaFile(
                    mimetype=media_obj.mimetype,
                    filename=media_obj.filename,
                    url=media_obj.url,
                ),
                caption=msg.caption,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        if msg.type == "location":
            location_obj = msg.location
            if not location_obj:
                raise NotFoundException("Location data not found")

            return MessageOutLocation(
                id=msg.id,
                type="location",
                latitude=location_obj.latitude,
                longitude=location_obj.longitude,
                title=location_obj.title,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        raise ValueError(f"Unknown message type: {msg.type}")

    def _transcribe_audio(self, audio_url: str) -> Optional[str]:
        """
        Transcrever áudio usando Faster-Whisper local.
        
        Args:
            audio_url: URL do arquivo de áudio
            
        Returns:
            Texto transcrito ou None se falhar
        """
        try:
            from robbot.services.transcription_service import TranscriptionService
            transcriber = TranscriptionService()
            transcription = transcriber.transcribe_audio_sync(audio_url, language="pt")
            if transcription:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"✓ Áudio transcrito: {transcription[:100]}...")
            return transcription
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"✗ Erro ao transcrever áudio: {e}")
            return None
    
    def _generate_description(self, media_url: str, filename: str, caption: str, media_type: str) -> dict:
        """
        Gerar descrição de mídia usando BLIP-2 (imagens) ou metadata básico.
        
        Args:
            media_url: URL do arquivo de mídia
            filename: Nome do arquivo
            caption: Legenda fornecida
            media_type: Tipo de mídia (image, video)
            
        Returns:
            Dict com title, description, tags ou vazio se falhar
        """
        try:
            from robbot.services.description_service import DescriptionService
            desc_service = DescriptionService(self.db)
            
            # Se é imagem, tentar usar BLIP-2 para análise visual
            if media_type == "image" and media_url:
                return desc_service._analyze_image_with_blip(media_url, caption)
            
            # Para vídeo ou se BLIP falhar, usar metadata básico
            return desc_service._generate_file_metadata(filename, caption, media_type)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"✗ Erro ao gerar descrição de {media_type}: {e}")
            return {}
    
    def _generate_file_description(self, filename: str, caption: str, file_type: str) -> dict:
        """
        Gerar metadata de documento baseado em filename e caption.
        
        Args:
            filename: Nome do arquivo
            caption: Legenda do arquivo
            file_type: Tipo do arquivo (document, voice)
            
        Returns:
            Dict com title, description, tags
        """
        try:
            from robbot.services.description_service import DescriptionService
            desc_service = DescriptionService(self.db)
            return desc_service._generate_file_metadata(filename, caption, file_type)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"✗ Erro ao gerar metadata de {file_type}: {e}")
            return {}

    def list_messages(
        self,
    ) -> list[Union[MessageOutText, MessageOutMedia, MessageOutLocation]]:
        """Retrieve all messages."""
        messages = self.repo.list_all()
        result = []
        for msg in messages:
            if msg.type == "text":
                result.append(MessageOutText.model_validate(msg))
            elif msg.type in ("image", "voice", "video", "document"):
                media_obj = msg.media[0] if msg.media else None
                if media_obj:
                    result.append(
                        MessageOutMedia(
                            id=msg.id,
                            type=msg.type,  # type: ignore
                            file=MediaFile(
                                mimetype=media_obj.mimetype,
                                filename=media_obj.filename,
                                url=media_obj.url,
                            ),
                            caption=msg.caption,
                            created_at=msg.created_at,
                            updated_at=msg.updated_at,
                        )
                    )
            elif msg.type == "location":
                location_obj = msg.location
                if location_obj:
                    result.append(
                        MessageOutLocation(
                            id=msg.id,
                            type="location",
                            latitude=location_obj.latitude,
                            longitude=location_obj.longitude,
                            title=location_obj.title,
                            created_at=msg.created_at,
                            updated_at=msg.updated_at,
                        )
                    )
        return result

    def update_message(
        self,
        message_id: UUID,
        payload: Union[MessageUpdateText, MessageUpdateMedia, MessageUpdateLocation],
    ) -> Union[MessageOutText, MessageOutMedia, MessageOutLocation]:
        """Update message fields based on type."""
        msg = self.repo.get_by_id(message_id)
        if not msg:
            raise NotFoundException(f"Message {message_id} not found")

        if isinstance(payload, MessageUpdateText) and msg.type == "text":
            if payload.text is not None:
                msg = self.repo.update_text(msg, payload.text)
            return MessageOutText.model_validate(msg)

        if isinstance(payload, MessageUpdateMedia) and msg.type in (
            "image",
            "voice",
            "video",
            "document",
        ):
            if payload.caption is not None:
                msg = self.repo.update_media_caption(msg, payload.caption)
            if payload.file is not None:
                if not payload.file.url:
                    raise ValueError("File URL is required for media update")
                msg = self.repo.update_media_file(
                    msg, payload.file.mimetype, payload.file.filename, payload.file.url
                )

            media_obj = msg.media[0] if msg.media else None
            if not media_obj:
                raise NotFoundException("Media metadata not found")

            return MessageOutMedia(
                id=msg.id,
                type=msg.type,  # type: ignore
                file=MediaFile(
                    mimetype=media_obj.mimetype,
                    filename=media_obj.filename,
                    url=media_obj.url,
                ),
                caption=msg.caption,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        if isinstance(payload, MessageUpdateLocation) and msg.type == "location":
            msg = self.repo.update_location(
                msg, payload.latitude, payload.longitude, payload.title
            )
            location_obj = msg.location
            if not location_obj:
                raise NotFoundException("Location data not found")

            return MessageOutLocation(
                id=msg.id,
                type="location",
                latitude=location_obj.latitude,
                longitude=location_obj.longitude,
                title=location_obj.title,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        raise ValueError("Payload type does not match message type")

    def delete_message(self, message_id: UUID) -> DeletedResponse:
        """Delete message and associated media/location."""
        msg = self.repo.get_by_id(message_id)
        if not msg:
            raise NotFoundException(f"Message {message_id} not found")

        self.repo.delete(msg)
        return DeletedResponse(deleted=True)
