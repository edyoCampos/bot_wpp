"""Repository for content persistence and retrieval operations."""

from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from robbot.infra.persistence.models.content_location_model import ContentLocationModel
from robbot.infra.persistence.models.content_media_model import ContentMediaModel
from robbot.infra.persistence.models.content_model import ContentModel


class ContentRepository:
    """Repository encapsulating DB access for contents."""

    def __init__(self, db: Session):
        self.db = db

    def create_text(self, text: str) -> ContentModel:
        """Create a text content entry."""
        content = ContentModel(type="text", text=text)
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    def create_media(
        self,
        content_type: str,
        mimetype: str,
        filename: str,
        url: str,
        caption: str | None,
        transcription: str | None = None,
        title: str | None = None,
        description: str | None = None,
        tags: str | None = None,
    ) -> ContentModel:
        """
        Criar conteúdo de mídia com metadados do arquivo.
        """
        content = ContentModel(
            type=content_type,
            caption=caption,
            has_audio=(content_type in ["voice", "video"]),
            audio_url=url if content_type in ["voice", "video"] else None,
            transcription=transcription,
            title=title,
            description=description,
            tags=tags,
        )
        self.db.add(content)
        self.db.flush()

        media = ContentMediaModel(content_id=content.id, mimetype=mimetype, filename=filename, url=url)
        self.db.add(media)
        self.db.commit()
        self.db.refresh(content)
        return content

    def create_location(self, latitude: float, longitude: float, title: str | None) -> ContentModel:
        """Create a location content entry."""
        content = ContentModel(type="location")
        self.db.add(content)
        self.db.flush()

        location = ContentLocationModel(content_id=content.id, latitude=latitude, longitude=longitude, title=title)
        self.db.add(location)
        self.db.commit()
        self.db.refresh(content)
        return content

    def get_by_id(self, content_id: UUID) -> ContentModel | None:
        """Retrieve content with eager-loaded relationships."""
        return (
            self.db.query(ContentModel)
            .options(joinedload(ContentModel.media), joinedload(ContentModel.location))
            .filter(ContentModel.id == content_id)
            .first()
        )

    def list_all(self, limit: int = 100, offset: int = 0) -> list[ContentModel]:
        """Retrieve all contents with relationships and pagination."""
        return (
            self.db.query(ContentModel)
            .options(joinedload(ContentModel.media), joinedload(ContentModel.location))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def update_text(self, content: ContentModel, text: str) -> ContentModel:
        """Update text content."""
        content.text = text
        self.db.commit()
        self.db.refresh(content)
        return content

    def update_media_caption(self, content: ContentModel, caption: str) -> ContentModel:
        """Update media caption."""
        content.caption = caption
        self.db.commit()
        self.db.refresh(content)
        return content

    def update_media_file(self, content: ContentModel, mimetype: str, filename: str, url: str) -> ContentModel:
        """Replace media file metadata."""
        # Delete old media
        self.db.query(ContentMediaModel).filter(ContentMediaModel.content_id == content.id).delete()

        # Create new media
        media = ContentMediaModel(content_id=content.id, mimetype=mimetype, filename=filename, url=url)
        self.db.add(media)
        self.db.commit()
        self.db.refresh(content)
        return content

    def update_location(
        self,
        content_model: ContentModel,
        latitude: float | None,
        longitude: float | None,
        title: str | None,
    ) -> ContentModel:
        """Update location coordinates and title."""
        location = content_model.location
        if location:
            if latitude is not None:
                location.latitude = latitude
            if longitude is not None:
                location.longitude = longitude
            if title is not None:
                location.title = title
            self.db.commit()
            self.db.refresh(content_model)
        return content_model

    def delete(self, content: ContentModel) -> None:
        """Delete content (cascades to media/location)."""
        self.db.delete(content)
        self.db.commit()

