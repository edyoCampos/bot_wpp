"""
Tag Repository - database operations for tags.
"""

from typing import List, Optional

from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, text, MetaData
from sqlalchemy.orm import Session

from robbot.adapters.repositories.base_repository import BaseRepository
from robbot.domain.entities.tag import Tag

# Local metadata for this repository
metadata = MetaData()


# SQLAlchemy table definition
tags_table = Table(
    'tags',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(50), nullable=False, unique=True, index=True),
    Column('color', String(7), nullable=False),
    Column('created_at', DateTime(timezone=True), nullable=False, server_default=text('now()')),
)


class TagRepository(BaseRepository[Tag]):
    """Repository for Tag entity."""

    def __init__(self, session: Session):
        super().__init__(db=session, table=tags_table, entity_class=Tag)

    def get_by_name(self, name: str) -> Optional[Tag]:
        """Get tag by name."""
        result = self.session.execute(
            self.table.select().where(self.table.c.name == name)
        ).fetchone()
        
        if not result:
            return None
        
        return self._map_to_entity(result)

    def find_by_names(self, names: List[str]) -> List[Tag]:
        """Find tags by list of names."""
        result = self.session.execute(
            self.table.select().where(self.table.c.name.in_(names))
        ).fetchall()
        
        return [self._map_to_entity(row) for row in result]
