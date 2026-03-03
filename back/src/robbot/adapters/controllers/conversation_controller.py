"""
Conversation Controller - REST endpoints for conversation management.
"""

import csv
import hashlib
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.conversation_message_repository import ConversationMessageRepository
from robbot.infra.persistence.repositories.conversation_tag_repository import ConversationTagRepository
from robbot.infra.persistence.repositories.tag_repository import TagRepository
from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.core.custom_exceptions import NotFoundException
from robbot.domain.shared.enums import ConversationStatus, Role
from robbot.infra.persistence.models.conversation_message_model import ConversationMessageModel
from robbot.infra.persistence.models.user_model import UserModel
from robbot.services.bot.conversation_service import ConversationService

router = APIRouter()


# ===== SCHEMAS =====
class ConversationMessageOut(BaseModel):
    """Response schema for conversation message."""

    id: str
    direction: str
    from_phone: str
    to_phone: str
    body: str
    media_url: str | None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class ConversationOut(BaseModel):
    """Response schema for conversation."""

    id: str
    chat_id: str
    phone_number: str
    status: str
    lead_status: str
    is_urgent: bool
    lead_id: str | None
    assigned_to_user_id: int | None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class ConversationListOut(BaseModel):
    """Response schema for conversation list."""

    conversations: list[ConversationOut]
    total: int


class UpdateStatusRequest(BaseModel):
    """Request schema for status update."""

    new_status: str


class TransferRequest(BaseModel):
    """Request schema for transfer."""

    user_id: int


class CloseRequest(BaseModel):
    """Request schema for close."""

    reason: str


class UpdateNotesRequest(BaseModel):
    """Request schema for updating notes."""

    notes: str = Field(..., max_length=5000)


class AssignConversationRequest(BaseModel):
    """Request schema for assigning conversation to a secretary."""

    assigned_to: int
    reason: str | None = None


class ResolveConversationRequest(BaseModel):
    """Request schema for resolving a conversation."""

    outcome: str


class AddTagsByNameRequest(BaseModel):
    """Request schema for adding tags by name."""

    tags: list[str]


# ===== ENDPOINTS =====
@router.get("", response_model=ConversationListOut | list[ConversationOut], tags=["Conversations"])
def list_conversations(
    phone_number: str | None = Query(None, description="Filter by phone number"),
    status: str | None = Query(None, description="Filter by status"),
    urgent_only: bool = Query(False, description="Show only urgent conversations"),
    assigned_to_me: bool = Query(False, description="Show only assigned to current user"),
    tags: str | None = Query(None, description="Filter by tag names (comma-separated)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List conversations with filters.

    Requires JWT authentication.

    Filters:
    - phone_number: Filter by phone number
    - status: ACTIVE, WAITING_SECRETARY, TRANSFERRED, CLOSED
    - urgent_only: Show only is_urgent=true
    - assigned_to_me: Show only assigned to current user
    """
    service = ConversationService(db)

    # Parse status filter
    status_enum = None
    if status:
        try:
            status_enum = ConversationStatus[status.upper()]
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}") from exc

    conversation_ids: list[str] | None = None
    if tags:
        tag_names = [name.strip() for name in tags.split(",") if name.strip()]
        if tag_names:
            tag_repo = TagRepository(db)
            tag_models = tag_repo.find_by_names(tag_names)
            if not tag_models:
                conversation_ids = []
            else:
                conv_tag_repo = ConversationTagRepository(db)
                ids: set[str] = set()
                for tag in tag_models:
                    ids.update(conv_tag_repo.get_conversations_by_tag(tag.id))
                conversation_ids = list(ids)
        else:
            conversation_ids = []

    # Get conversations using service
    conversations, total = service.list_conversations(
        phone_number=phone_number,
        status=status_enum,
        is_urgent=True if urgent_only else None,
        assigned_to_user_id=current_user.id if assigned_to_me else None,
        conversation_ids=conversation_ids,
        limit=limit,
        offset=offset,
    )

    # Convert to response
    conversations_out = [
        ConversationOut(
            id=c.id,
            chat_id=c.chat_id,
            phone_number=c.phone_number,
            status=(
                "active"
                if c.status
                in (ConversationStatus.ACTIVE, ConversationStatus.ACTIVE_BOT, ConversationStatus.PENDING_HANDOFF)
                else c.status.value
            ),
            lead_status=c.lead.status.value if c.lead and c.lead.status else "NEW",
            is_urgent=getattr(c, "is_urgent", False),
            lead_id=c.lead.id if c.lead else None,
            assigned_to_user_id=getattr(c.lead, "assigned_to_user_id", None) if c.lead else None,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in conversations
    ]

    if phone_number is None:
        return conversations_out

    return ConversationListOut(conversations=conversations_out, total=total)


@router.post("/{conversation_id}/tags", tags=["Conversations"])
def add_tags_to_conversation(
    conversation_id: str,
    request: AddTagsByNameRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add tags to a conversation by name (test compatibility)."""
    from robbot.infra.persistence.repositories.conversation_repository import ConversationRepository
    from robbot.services.communication.tag_service import TagService

    conv_repo = ConversationRepository(db)
    conversation = conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    tag_service = TagService(db)
    tag_repo = TagRepository(db)
    conv_tag_repo = ConversationTagRepository(db)

    tags_added: list[str] = []
    for raw_name in request.tags:
        name = raw_name.strip()
        if not name:
            continue
        tag = tag_repo.get_by_name(name)
        if not tag:
            color = f"#{hashlib.md5(name.encode()).hexdigest()[:6]}"
            tag = tag_service.create_tag(name=name, color=color)
        conv_tag_repo.add_tag_to_conversation(conversation_id, tag.id)
        tags_added.append(tag.name)

    db.commit()

    return {
        "conversation_id": conversation_id,
        "tags": tags_added,
    }


@router.get("/export", tags=["Conversations"])
def export_conversations(
    export_format: str = Query("csv", description="Export format (csv only)"),
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    status: str | None = Query(None, description="Filter by status"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export conversations to CSV.

    Requires JWT authentication.

    Filters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - status: Conversation status

    Non-admin users can only export their own assigned conversations.
    """
    if export_format != "csv":
        raise HTTPException(status_code=400, detail="Only CSV format is supported")

    service = ConversationService(db)

    # Build filters
    filters = {}
    if status:
        try:
            filters["status"] = ConversationStatus[status.upper()]
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}") from exc

    # Non-admin users can only export their own conversations
    if current_user.role != Role.ADMIN:
        filters["assigned_to_user_id"] = current_user.id

    # Get conversations
    conversations = service.find_by_criteria(filters)

    # Filter by date range
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            conversations = [c for c in conversations if c.created_at >= start_dt]
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid start_date format") from exc

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            conversations = [c for c in conversations if c.created_at <= end_dt]
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid end_date format") from exc

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "ID",
            "Chat ID",
            "Phone Number",
            "Status",
            "Lead Status",
            "Is Urgent",
            "Assigned To",
            "Created At",
            "Updated At",
        ]
    )

    # Rows
    for conv in conversations:
        writer.writerow(
            [
                conv.id,
                conv.chat_id,
                conv.phone_number,
                conv.status.value,
                conv.lead.status.value if conv.lead else "NEW",
                getattr(conv, "is_urgent", False),
                getattr(conv.lead, "assigned_to_user_id", None) if conv.lead else "",
                conv.created_at.isoformat(),
                conv.updated_at.isoformat(),
            ]
        )

    # Stream response
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=conversations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


@router.get("/search", response_model=ConversationListOut, tags=["Conversations"])
def search_conversations(
    q: str = Query(..., min_length=3, description="Search query (min 3 chars)"),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Full-text search in conversation messages.

    Requires JWT authentication.

    Searches in message content using PostgreSQL full-text search.
    Non-admin users can only search their own assigned conversations.
    """
    ConversationMessageRepository(db)
    service = ConversationService(db)

    # Search messages with full-text query using the model directly

    result = (
        db.query(ConversationMessageModel).filter(ConversationMessageModel.body.ilike(f"%{q}%")).limit(limit * 5).all()
    )  # Get more messages to find unique conversations

    # Get unique conversation IDs
    conversation_ids = list({msg.conversation_id for msg in result})[:limit]

    # Get conversations
    conversations = []
    for conv_id in conversation_ids:
        conv = service.get_by_id(conv_id)
        if conv:
            # Filter by user if not admin
            assigned_user_id = getattr(conv.lead, "assigned_to_user_id", None) if conv.lead else None
            if current_user.role != Role.ADMIN and assigned_user_id != current_user.id:
                continue
            conversations.append(conv)

    # Convert to response
    conversations_out = [
        ConversationOut(
            id=c.id,
            chat_id=c.chat_id,
            phone_number=c.phone_number,
            status=c.status.value,
            lead_status=c.lead.status.value if c.lead else "NEW",
            is_urgent=getattr(c, "is_urgent", False),
            lead_id=c.lead.id if c.lead else None,
            assigned_to_user_id=getattr(c.lead, "assigned_to_user_id", None) if c.lead else None,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in conversations
    ]

    return ConversationListOut(conversations=conversations_out, total=len(conversations_out))


@router.get(
    "/{conversation_id}",
    response_model=ConversationOut,
    tags=["Conversations"],
)
def get_conversation(
    conversation_id: str,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get conversation by ID.

    Requires JWT authentication.
    """
    service = ConversationService(db)
    conversation = service.get_by_id(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationOut(
        id=conversation.id,
        chat_id=conversation.chat_id,
        phone_number=conversation.phone_number,
        status=conversation.status.value,
        lead_status=conversation.lead.status.value if conversation.lead and conversation.lead.status else "NEW",
        is_urgent=getattr(conversation, "is_urgent", False),
        lead_id=conversation.lead.id if conversation.lead else None,
        assigned_to_user_id=getattr(conversation.lead, "assigned_to_user_id", None) if conversation.lead else None,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=list[ConversationMessageOut],
    tags=["Conversations"],
)
def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get messages for a specific conversation.

    Requires JWT authentication.
    """
    repo = ConversationMessageRepository(db)
    messages = repo.get_by_conversation(conversation_id, limit=limit)

    return [
        ConversationMessageOut(
            id=m.id,
            direction=m.direction.value,
            from_phone=m.from_phone,
            to_phone=m.to_phone,
            body=m.body,
            media_url=m.media_url,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]


@router.put("/{conversation_id}/status", tags=["Conversations"])
def update_conversation_status(
    conversation_id: str,
    request: UpdateStatusRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update conversation status.

    Requires JWT authentication.

    Valid transitions:
    - ACTIVE → WAITING_SECRETARY, TRANSFERRED, CLOSED
    - WAITING_SECRETARY → TRANSFERRED, CLOSED
    - TRANSFERRED → CLOSED
    """
    service = ConversationService(db)

    try:
        new_status = ConversationStatus[request.new_status.upper()]
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid status: {request.new_status}") from exc

    try:
        conversation = service.update_status(conversation_id, new_status)

        return {
            "message": "Status updated successfully",
            "conversation_id": conversation.id,
            "new_status": conversation.status.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to update status: {e!s}") from e


@router.post("/{conversation_id}/transfer", tags=["Conversations"])
def transfer_conversation(
    conversation_id: str,
    request: TransferRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Transfer conversation to user (secretary).

    Requires JWT authentication.
    """
    service = ConversationService(db)

    try:
        conversation = service.transfer_to_secretary(conversation_id, request.user_id)

        return {
            "message": "Conversation transferred successfully",
            "conversation_id": conversation.id,
            "assigned_to": request.user_id,
            "status": conversation.status.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to transfer: {e!s}") from e


@router.patch("/{conversation_id}/assign", tags=["Conversations"])
def assign_conversation(
    conversation_id: str,
    request: AssignConversationRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Assign conversation to secretary (compatibility endpoint)."""
    service = ConversationService(db)

    try:
        conversation = service.transfer_to_secretary(conversation_id, request.assigned_to)

        return {
            "message": "Conversation assigned successfully",
            "conversation_id": conversation.id,
            "assigned_to": request.assigned_to,
            "status": conversation.status.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to assign: {e!s}") from e


@router.post("/{conversation_id}/resolve", tags=["Conversations"])
def resolve_conversation(
    conversation_id: str,
    request: ResolveConversationRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resolve a conversation with outcome (test compatibility)."""
    service = ConversationService(db)

    try:
        conversation = service.close(conversation_id, reason=request.outcome)

        return {
            "message": "Conversation resolved successfully",
            "conversation_id": conversation.id,
            "status": "COMPLETED" if conversation.status == ConversationStatus.CLOSED else conversation.status.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to resolve: {e!s}") from e


@router.post("/{conversation_id}/close", tags=["Conversations"])
def close_conversation(
    conversation_id: str,
    request: CloseRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Close conversation with reason.

    Requires JWT authentication.
    """
    service = ConversationService(db)

    try:
        conversation = service.close(conversation_id, request.reason)

        return {
            "message": "Conversation closed successfully",
            "conversation_id": conversation.id,
            "status": conversation.status.value,
            "reason": request.reason,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to close: {e!s}") from e


@router.put("/{conversation_id}/notes", tags=["Conversations"])
def update_conversation_notes(
    conversation_id: str,
    request: UpdateNotesRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update conversation notes (internal comments for secretaries).

    Requires JWT authentication.

    Notes are stored as plain text (max 5000 chars).
    """
    service = ConversationService(db)

    try:
        conversation = service.update_notes(conversation_id, request.notes)

        return {
            "message": "Notes updated successfully",
            "conversation_id": conversation.id,
            "notes": conversation.notes,
        }
    except NotFoundException as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to update notes: {e!s}") from e

