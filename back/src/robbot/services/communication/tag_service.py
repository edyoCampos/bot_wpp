"""
Tag Service - business logic for tags.
"""

import logging

from robbot.infra.persistence.repositories.tag_repository import TagRepository
from robbot.infra.persistence.models.tag_model import TagModel

logger = logging.getLogger(__name__)


class TagService:
    """
    Service for tag management.

    Business logic for:
    - Creating tags
    - Listing tags
    - Validating tag uniqueness
    """

    def __init__(self, session):
        self.session = session
        self.tag_repo = TagRepository(session)

    def create_tag(self, name: str, color: str) -> TagModel:
        """
        Create a new tag.

        Args:
            name: Tag name (max 50 chars, must be unique)
            color: Hex color code (e.g., #FF0000)

        Returns:
            Created Tag entity

        Raises:
            ValueError: If tag name already exists or invalid color format
        """
        # Validate name uniqueness
        existing = self.tag_repo.get_by_name(name)
        if existing:
            raise ValueError(f"Tag '{name}' already exists")

        # Validate color format (basic check)
        if not color.startswith("#") or len(color) != 7:
            raise ValueError(f"Invalid color format: {color}. Expected #RRGGBB")

        # Create tag
        tag = TagModel(name=name, color=color)
        self.tag_repo.create(tag)
        self.session.flush()

        logger.info("[SUCCESS] Tag created (id=%s, name=%s, color=%s)", tag.id, name, color)

        return tag

    def get_all_tags(self) -> list[TagModel]:
        """
        Get all tags.

        Returns:
            List of all tags
        """
        tags = self.tag_repo.get_all()
        logger.info("[SUCCESS] Retrieved %s tags", len(tags))
        return tags

    def get_tag_by_id(self, tag_id: int) -> TagModel | None:
        """
        Get tag by ID.

        Args:
            tag_id: Tag ID

        Returns:
            Tag entity or None
        """
        return self.tag_repo.get_by_id(tag_id)

    def get_tag_by_name(self, name: str) -> TagModel | None:
        """
        Get tag by name.

        Args:
            name: Tag name

        Returns:
            Tag entity or None
        """
        return self.tag_repo.get_by_name(name)

    def delete_tag(self, tag_id: int) -> bool:
        """
        Delete a tag.

        Args:
            tag_id: Tag ID

        Returns:
            True if deleted, False if not found
        """
        tag = self.tag_repo.get_by_id(tag_id)
        if not tag:
            return False

        self.tag_repo.delete(tag)
        self.session.flush()

        logger.info("[SUCCESS] Tag deleted (id=%s)", tag_id)

        return True

