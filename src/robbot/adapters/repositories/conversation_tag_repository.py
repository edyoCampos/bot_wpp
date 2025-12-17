"""
Conversation Tag Repository - manage conversation-tag associations.
"""

from typing import List

from sqlalchemy import Table, Column, String, Integer, DateTime, ForeignKey, text, MetaData
from sqlalchemy.orm import Session

from robbot.adapters.repositories.tag_repository import TagRepository
from robbot.domain.entities.tag import Tag

# Local metadata for this repository
metadata = MetaData()


# SQLAlchemy association table
conversation_tags_table = Table(
    'conversation_tags',
    metadata,
    Column('conversation_id', String(36), ForeignKey('conversations.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), nullable=False, server_default=text('now()')),
)


class ConversationTagRepository:
    """Repository for conversation-tag associations."""

    def __init__(self, session: Session):
        self.session = session
        self.table = conversation_tags_table
        self.tag_repo = TagRepository(session)

    def add_tag_to_conversation(self, conversation_id: str, tag_id: int) -> None:
        """Add a tag to a conversation."""
        # Check if already exists
        existing = self.session.execute(
            self.table.select().where(
                (self.table.c.conversation_id == conversation_id) &
                (self.table.c.tag_id == tag_id)
            )
        ).fetchone()
        
        if existing:
            return  # Already associated
        
        # Insert
        self.session.execute(
            self.table.insert().values(
                conversation_id=conversation_id,
                tag_id=tag_id
            )
        )
        self.session.flush()

    def remove_tag_from_conversation(self, conversation_id: str, tag_id: int) -> bool:
        """Remove a tag from a conversation. Returns True if deleted, False if not found."""
        result = self.session.execute(
            self.table.delete().where(
                (self.table.c.conversation_id == conversation_id) &
                (self.table.c.tag_id == tag_id)
            )
        )
        self.session.flush()
        return result.rowcount > 0

    def get_conversation_tags(self, conversation_id: str) -> List[Tag]:
        """Get all tags for a conversation."""
        # Join with tags table
        result = self.session.execute(
            self.table.select().where(
                self.table.c.conversation_id == conversation_id
            )
        ).fetchall()
        
        if not result:
            return []
        
        # Get tag IDs
        tag_ids = [row.tag_id for row in result]
        
        # Fetch tags
        tags = []
        for tag_id in tag_ids:
            tag = self.tag_repo.get_by_id(tag_id)
            if tag:
                tags.append(tag)
        
        return tags

    def get_conversations_by_tag(self, tag_id: int) -> List[str]:
        """Get all conversation IDs that have this tag."""
        result = self.session.execute(
            self.table.select().where(self.table.c.tag_id == tag_id)
        ).fetchall()
        
        return [row.conversation_id for row in result]
