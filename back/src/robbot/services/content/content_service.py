"""Content service orchestrating repository and business logic."""

from uuid import UUID

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.content_repository import ContentRepository
from robbot.core.custom_exceptions import NotFoundException
from robbot.schemas.content import (
    DeletedResponse,
    MediaFile,
    ContentCreateLocation,
    ContentCreateMedia,
    ContentCreateText,
    ContentOutLocation,
    ContentOutMedia,
    ContentOutText,
    ContentUpdateLocation,
    ContentUpdateMedia,
    ContentUpdateText,
)
from robbot.services.content.description_service import DescriptionService
from robbot.services.communication.transcription_service import TranscriptionService


class ContentService:
    """Service layer for content CRUD operations."""

    def __init__(self, db: Session):
        self.repo = ContentRepository(db)
        self.desc_service = DescriptionService(db)
        self.transcription_service = TranscriptionService()

    def create_content(
        self,
        payload: ContentCreateText | ContentCreateMedia | ContentCreateLocation,
    ) -> ContentOutText | ContentOutMedia | ContentOutLocation:
        """
        Create content based on type.
        """
        if isinstance(payload, ContentCreateText):
            msg = self.repo.create_text(text=payload.text)
            return ContentOutText.model_validate(msg)

        if isinstance(payload, ContentCreateMedia):
            if not payload.file.url:
                raise ValueError("Media file URL is required")

            transcription = None
            title = None
            description = None
            tags = None

            if payload.type == "voice":
                transcription = self._transcribe_audio(payload.file.url)
            elif payload.type == "video":
                transcription = self._transcribe_audio(payload.file.url)
                metadata = self._generate_description(
                    payload.file.url, payload.file.filename, payload.caption or "", "video"
                )
                title = metadata.get("generated_title")
                description = metadata.get("generated_description")
                tags = metadata.get("suggested_tags")
            elif payload.type == "image":
                metadata = self._generate_description(
                    payload.file.url, payload.file.filename, payload.caption or "", "image"
                )
                title = metadata.get("generated_title")
                description = metadata.get("generated_description")
                tags = metadata.get("suggested_tags")
            elif payload.type == "document":
                metadata = self._generate_file_description(payload.file.filename, payload.caption or "", "document")
                title = metadata.get("generated_title")
                description = metadata.get("generated_description")
                tags = metadata.get("suggested_tags")

            msg = self.repo.create_media(
                content_type=payload.type,
                mimetype=payload.file.mimetype,
                filename=payload.file.filename,
                url=payload.file.url,
                caption=payload.caption,
                transcription=transcription,
                title=title,
                description=description,
                tags=tags,
            )
            media_obj = msg.media[0] if msg.media else None
            if not media_obj:
                raise NotFoundException("Media object not found after creation")

            return ContentOutMedia(
                id=msg.id,
                type=msg.type,
                file=MediaFile(
                    mimetype=media_obj.mimetype,
                    filename=media_obj.filename,
                    url=media_obj.url,
                ),
                caption=msg.caption,
                title=msg.title,
                description=msg.description,
                tags=msg.tags,
                transcription=msg.transcription,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        if isinstance(payload, ContentCreateLocation):
            msg = self.repo.create_location(
                latitude=payload.latitude,
                longitude=payload.longitude,
                title=payload.title,
            )
            location_obj = msg.location
            if not location_obj:
                raise NotFoundException("Location object not found after creation")

            return ContentOutLocation(
                id=msg.id,
                type="location",
                latitude=location_obj.latitude,
                longitude=location_obj.longitude,
                title=location_obj.title,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        raise ValueError("Invalid content type")

    def get_content(self, content_id: UUID) -> ContentOutText | ContentOutMedia | ContentOutLocation:
        """Retrieve content by ID."""
        msg = self.repo.get_by_id(content_id)
        if not msg:
            raise NotFoundException(f"Content {content_id} not found")

        if msg.type == "text":
            return ContentOutText.model_validate(msg)

        if msg.type in ("image", "voice", "video", "document"):
            media_obj = msg.media[0] if msg.media else None
            if not media_obj:
                raise NotFoundException("Media metadata not found")

            return ContentOutMedia(
                id=msg.id,
                type=msg.type,
                file=MediaFile(
                    mimetype=media_obj.mimetype,
                    filename=media_obj.filename,
                    url=media_obj.url,
                ),
                caption=msg.caption,
                title=msg.title,
                description=msg.description,
                tags=msg.tags,
                transcription=msg.transcription,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        if msg.type == "location":
            location_obj = msg.location
            if not location_obj:
                raise NotFoundException("Location data not found")

            return ContentOutLocation(
                id=msg.id,
                type="location",
                latitude=location_obj.latitude,
                longitude=location_obj.longitude,
                title=location_obj.title,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        raise ValueError(f"Unknown content type: {msg.type}")

    def _transcribe_audio(self, audio_url: str) -> str | None:
        """Transcrever áudio."""
        try:
            return self.transcription_service.transcribe_audio_sync(audio_url, language="pt")
        except Exception:  # noqa: BLE001
            return None

    def _generate_description(self, media_url: str, filename: str, caption: str, media_type: str) -> dict:
        """Gerar descrição de mídia."""
        try:
            if media_type == "image" and media_url:
                return self.desc_service.analyze_image_with_blip(media_url, caption)
            return self.desc_service.generate_file_metadata(filename, caption, media_type)
        except Exception:  # noqa: BLE001
            return {}

    def _generate_file_description(self, filename: str, caption: str, file_type: str) -> dict:
        """Gerar metadata de documento."""
        try:
            return self.desc_service.generate_file_metadata(filename, caption, file_type)
        except Exception:  # noqa: BLE001
            return {}

    def list_contents(self) -> list[ContentOutText | ContentOutMedia | ContentOutLocation]:
        """Retrieve all contents."""
        messages = self.repo.list_all()
        result = []
        for msg in messages:
            if msg.type == "text":
                result.append(ContentOutText.model_validate(msg))
            elif msg.type in ("image", "voice", "video", "document"):
                media_obj = msg.media[0] if msg.media else None
                if media_obj:
                    result.append(
                        ContentOutMedia(
                            id=msg.id,
                            type=msg.type,
                            file=MediaFile(
                                mimetype=media_obj.mimetype,
                                filename=media_obj.filename,
                                url=media_obj.url,
                            ),
                            caption=msg.caption,
                            title=msg.title,
                            description=msg.description,
                            tags=msg.tags,
                            transcription=msg.transcription,
                            created_at=msg.created_at,
                            updated_at=msg.updated_at,
                        )
                    )
            elif msg.type == "location":
                location_obj = msg.location
                if location_obj:
                    result.append(
                        ContentOutLocation(
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

    def update_content(
        self,
        content_id: UUID,
        payload: ContentUpdateText | ContentUpdateMedia | ContentUpdateLocation,
    ) -> ContentOutText | ContentOutMedia | ContentOutLocation:
        """Update content fields based on type."""
        msg = self.repo.get_by_id(content_id)
        if not msg:
            raise NotFoundException(f"Content {content_id} not found")

        if isinstance(payload, ContentUpdateText) and msg.type == "text":
            if payload.text is not None:
                msg = self.repo.update_text(msg, payload.text)
            return ContentOutText.model_validate(msg)

        if isinstance(payload, ContentUpdateMedia) and msg.type in (
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
                msg = self.repo.update_media_file(msg, payload.file.mimetype, payload.file.filename, payload.file.url)

            media_obj = msg.media[0] if msg.media else None
            if not media_obj:
                raise NotFoundException("Media metadata not found")

            return ContentOutMedia(
                id=msg.id,
                type=msg.type,
                file=MediaFile(
                    mimetype=media_obj.mimetype,
                    filename=media_obj.filename,
                    url=media_obj.url,
                ),
                caption=msg.caption,
                title=msg.title,
                description=msg.description,
                tags=msg.tags,
                transcription=msg.transcription,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        if isinstance(payload, ContentUpdateLocation) and msg.type == "location":
            msg = self.repo.update_location(msg, payload.latitude, payload.longitude, payload.title)
            location_obj = msg.location
            if not location_obj:
                raise NotFoundException("Location data not found")

            return ContentOutLocation(
                id=msg.id,
                type="location",
                latitude=location_obj.latitude,
                longitude=location_obj.longitude,
                title=location_obj.title,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
            )

        raise ValueError("Payload type does not match content type")

    def delete_content(self, content_id: UUID) -> DeletedResponse:
        """Delete content."""
        msg = self.repo.get_by_id(content_id)
        if not msg:
            raise NotFoundException(f"Content {content_id} not found")

        self.repo.delete(msg)
        return DeletedResponse(deleted=True)

