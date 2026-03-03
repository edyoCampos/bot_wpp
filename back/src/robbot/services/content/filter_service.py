"""
Filter service for applying filters to database queries.

Centralizes filter logic that was previously in controllers.
Builds SQLAlchemy filters based on FilterDTO parameters.

Resolves Issue #2: Business Logic in Controllers (SRP Violation)
"""

import logging
from typing import Any

from sqlalchemy import asc, desc
from sqlalchemy.orm import Query

from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.infra.persistence.models.lead_interaction_model import LeadInteractionModel
from robbot.infra.persistence.models.lead_model import LeadModel
from robbot.schemas.filters import (
    ConversationFilterDTO,
    InteractionFilterDTO,
    LeadFilterDTO,
    SortOrder,
)

logger = logging.getLogger("robbot.services.filter_service")


class FilterService:
    """
    Apply filters to database queries.

    Centralizes query building logic that was scattered in controllers.
    Provides reusable filters across multiple services.
    """

    @staticmethod
    def apply_lead_filters(query: Query, filters: LeadFilterDTO) -> Query:
        """
        Apply lead filters to SQLAlchemy query.

        Args:
            query: SQLAlchemy Query object
            filters: LeadFilterDTO with filter parameters

        Returns:
            Filtered query
        """
        # Status filter
        if filters.status:
            query = query.filter(LeadModel.status == filters.status)

        # Source filter
        if filters.source:
            query = query.filter(LeadModel.source == filters.source)

        # Maturity score range filter
        if filters.score_min is not None:
            query = query.filter(LeadModel.maturity_score >= filters.score_min)

        if filters.score_max is not None:
            query = query.filter(LeadModel.maturity_score <= filters.score_max)

        # Text search filters (case-insensitive)
        if filters.name:
            query = query.filter(LeadModel.name.ilike(f"%{filters.name}%"))

        if filters.phone:
            query = query.filter(LeadModel.phone_number == filters.phone)

        if filters.email:
            query = query.filter(LeadModel.email.ilike(f"%{filters.email}%"))

        # Date range filters
        if filters.created_after:
            query = query.filter(LeadModel.created_at >= filters.created_after)

        if filters.created_before:
            query = query.filter(LeadModel.created_at <= filters.created_before)

        if filters.updated_after:
            query = query.filter(LeadModel.updated_at >= filters.updated_after)

        # Sorting
        sort_column = FilterService._get_sort_column(LeadModel, filters.sort_by)
        if sort_column is not None:
            if filters.sort_order == SortOrder.DESC:
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        # Pagination
        query = query.offset(filters.skip).limit(filters.limit)

        logger.debug("Applied %s to query", filters.__class__.__name__)
        return query

    @staticmethod
    def apply_conversation_filters(
        query: Query,
        filters: ConversationFilterDTO,
    ) -> Query:
        """
        Apply conversation filters to SQLAlchemy query.

        Args:
            query: SQLAlchemy Query object
            filters: ConversationFilterDTO with filter parameters

        Returns:
            Filtered query
        """
        # Status filter
        if filters.status:
            query = query.filter(ConversationModel.status == filters.status)

        # Lead ID filter
        if filters.lead_id:
            query = query.filter(ConversationModel.lead.has(LeadModel.id == filters.lead_id))

        # Phone filter
        if filters.phone:
            query = query.filter(ConversationModel.phone_number == filters.phone)

        # Unread filter
        if filters.has_unread is not None:
            # Count unread messages per conversation
            if filters.has_unread:
                # Conversations with at least one unread message
                query = query.filter(ConversationModel.unread_count > 0)
            else:
                # Conversations with no unread messages
                query = query.filter(ConversationModel.unread_count == 0)

        # Date range filters
        if filters.started_after:
            query = query.filter(ConversationModel.created_at >= filters.started_after)

        if filters.started_before:
            query = query.filter(ConversationModel.created_at <= filters.started_before)

        if filters.updated_after:
            query = query.filter(ConversationModel.updated_at >= filters.updated_after)

        # Sorting
        sort_column = FilterService._get_sort_column(ConversationModel, filters.sort_by)
        if sort_column is not None:
            if filters.sort_order == SortOrder.DESC:
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        # Pagination
        query = query.offset(filters.skip).limit(filters.limit)

        logger.debug("Applied %s to query", filters.__class__.__name__)
        return query

    @staticmethod
    def apply_interaction_filters(
        query: Query,
        filters: InteractionFilterDTO,
    ) -> Query:
        """
        Apply interaction filters to SQLAlchemy query.

        Args:
            query: SQLAlchemy Query object
            filters: InteractionFilterDTO with filter parameters

        Returns:
            Filtered query
        """
        # Lead ID filter
        if filters.lead_id:
            query = query.filter(LeadInteractionModel.lead_id == filters.lead_id)

        # Conversation ID filter
        if filters.conversation_id:
            query = query.filter(LeadInteractionModel.conversation_id == filters.conversation_id)

        # Interaction type filter
        if filters.interaction_type:
            query = query.filter(LeadInteractionModel.interaction_type == filters.interaction_type)

        # Date range filters
        if filters.date_after:
            query = query.filter(LeadInteractionModel.created_at >= filters.date_after)

        if filters.date_before:
            query = query.filter(LeadInteractionModel.created_at <= filters.date_before)

        # Sorting
        sort_column = FilterService._get_sort_column(LeadInteractionModel, filters.sort_by)
        if sort_column is not None:
            if filters.sort_order == SortOrder.DESC:
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        # Pagination
        query = query.offset(filters.skip).limit(filters.limit)

        logger.debug("Applied %s to query", filters.__class__.__name__)
        return query

    @staticmethod
    def _get_sort_column(model: type, field_name: str) -> Any:
        """
        Get SQLAlchemy column for sorting.

        Args:
            model: SQLAlchemy model class
            field_name: Field name to sort by

        Returns:
            SQLAlchemy column or None if not found
        """
        # Map user-friendly names to model columns
        column_map = {
            "created_at": "created_at",
            "updated_at": "updated_at",
            "name": "name",
            "phone": "phone_number",
            "maturity_score": "maturity_score",
            "message_count": "message_count",
        }

        column_name = column_map.get(field_name, field_name)

        if hasattr(model, column_name):
            return getattr(model, column_name)

        logger.warning("Sort column '%s' not found on %s", column_name, model.__name__)
        return None

