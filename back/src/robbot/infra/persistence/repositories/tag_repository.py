"""
Tag Repository - database operations for tags.
"""

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.tag_model import TagModel


class TagRepository(BaseRepository[TagModel]):
    """Repository for Tag entity."""

    def __init__(self, session: Session):
        super().__init__(session, TagModel)

    def get_by_name(self, name: str) -> TagModel | None:
        """Get tag by name."""
        return self.session.query(TagModel).filter(TagModel.name == name).first()

    def find_by_names(self, names: list[str]) -> list[TagModel]:
        """Find tags by list of names."""
        return self.session.query(TagModel).filter(TagModel.name.in_(names)).all()

