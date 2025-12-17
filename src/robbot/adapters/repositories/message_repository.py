"""Repository for message persistence and retrieval operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from robbot.infra.db.models.message_location_model import MessageLocationModel
from robbot.infra.db.models.message_media_model import MessageMediaModel
from robbot.infra.db.models.message_model import MessageModel


class MessageRepository:
    """Repository encapsulating DB access for messages."""

    def __init__(self, db: Session):
        self.db = db

    def create_text(self, text: str) -> MessageModel:
        """Create a text message."""
        msg = MessageModel(type="text", text=text)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def create_media(
        self, 
        msg_type: str, 
        mimetype: str, 
        filename: str, 
        url: str, 
        caption: Optional[str],
        transcription: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None
    ) -> MessageModel:
        """
        Criar mensagem de mídia com metadados do arquivo.
        
        Args:
            msg_type: Tipo da mensagem (image, video, voice, document)
            mimetype: MIME type do arquivo
            filename: Nome do arquivo
            url: URL do arquivo
            caption: Legenda opcional
            transcription: Transcrição de áudio (voice, video)
            title: Título gerado automaticamente
            description: Descrição gerada automaticamente
            tags: Tags sugeridas automaticamente
            
        Returns:
            MessageModel com mídia criada
        """
        msg = MessageModel(
            type=msg_type, 
            caption=caption,
            has_audio=(msg_type in ["voice", "video"]),
            audio_url=url if msg_type in ["voice", "video"] else None,
            transcription=transcription,
            title=title,
            description=description,
            tags=tags
        )
        self.db.add(msg)
        self.db.flush()  # Get msg.id before creating media

        media = MessageMediaModel(
            message_id=msg.id, mimetype=mimetype, filename=filename, url=url
        )
        self.db.add(media)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def create_location(
        self, latitude: float, longitude: float, title: Optional[str]
    ) -> MessageModel:
        """Create a location message."""
        msg = MessageModel(type="location")
        self.db.add(msg)
        self.db.flush()

        location = MessageLocationModel(
            message_id=msg.id, latitude=latitude, longitude=longitude, title=title
        )
        self.db.add(location)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_by_id(self, message_id: UUID) -> Optional[MessageModel]:
        """Retrieve message with eager-loaded relationships."""
        return (
            self.db.query(MessageModel)
            .options(joinedload(MessageModel.media), joinedload(MessageModel.location))
            .filter(MessageModel.id == message_id)
            .first()
        )

    def list_all(self) -> list[MessageModel]:
        """Retrieve all messages with relationships."""
        return (
            self.db.query(MessageModel)
            .options(joinedload(MessageModel.media), joinedload(MessageModel.location))
            .all()
        )

    def update_text(self, msg: MessageModel, text: str) -> MessageModel:
        """Update text content."""
        msg.text = text
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def update_media_caption(self, msg: MessageModel, caption: str) -> MessageModel:
        """Update media caption."""
        msg.caption = caption
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def update_media_file(
        self, msg: MessageModel, mimetype: str, filename: str, url: str
    ) -> MessageModel:
        """Replace media file metadata."""
        # Delete old media
        self.db.query(MessageMediaModel).filter(
            MessageMediaModel.message_id == msg.id
        ).delete()

        # Create new media
        media = MessageMediaModel(
            message_id=msg.id, mimetype=mimetype, filename=filename, url=url
        )
        self.db.add(media)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def update_location(
        self,
        msg: MessageModel,
        latitude: Optional[float],
        longitude: Optional[float],
        title: Optional[str],
    ) -> MessageModel:
        """Update location coordinates and title."""
        location = msg.location
        if location:
            if latitude is not None:
                location.latitude = latitude
            if longitude is not None:
                location.longitude = longitude
            if title is not None:
                location.title = title
            self.db.commit()
            self.db.refresh(msg)
        return msg

    def delete(self, msg: MessageModel) -> None:
        """Delete message (cascades to media/location)."""
        self.db.delete(msg)
        self.db.commit()
