"""Repository for context_item persistence and retrieval operations."""

from sqlalchemy.orm import Session, joinedload

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.context_item_model import ContextItemModel


class ContextItemRepository(BaseRepository[ContextItemModel]):
    """Repository encapsulating DB access for context items."""

    def __init__(self, db: Session):
        super().__init__(db, ContextItemModel)

    def get_by_context_id(self, context_id: str, include_contents: bool = False) -> list[ContextItemModel]:
        """List items by context in order."""
        query = (
            self.db.query(ContextItemModel)
            .filter(ContextItemModel.context_id == context_id)
            .order_by(ContextItemModel.item_order)
        )

        if include_contents:
            query = query.options(joinedload(ContextItemModel.content))

        return query.all()

    def get_next_order(self, context_id: str) -> int:
        """Get next available item_order for a context."""
        max_order = (
            self.db.query(ContextItemModel.item_order)
            .filter(ContextItemModel.context_id == context_id)
            .order_by(ContextItemModel.item_order.desc())
            .first()
        )

        return (max_order[0] + 1) if max_order else 1

    def list_by_context(self, context_id: str) -> list[ContextItemModel]:
        """List all items for a given context."""
        return self.get_by_context_id(context_id, include_contents=False)

    def reorder_items(self, context_id: str, item_id_order: list[tuple[str, int]]) -> bool:
        """Reorder multiple items at once. item_id_order = [(item_id, new_order), ...]"""
        try:
            for item_id, new_order in item_id_order:
                model = (
                    self.db.query(ContextItemModel)
                    .filter(ContextItemModel.id == item_id, ContextItemModel.context_id == context_id)
                    .first()
                )
                if model:
                    model.item_order = new_order

            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

