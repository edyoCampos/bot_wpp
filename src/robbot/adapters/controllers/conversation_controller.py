"""
Conversation Controller - REST endpoints for conversation management.
"""

import csv
import io
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from robbot.adapters.repositories.conversation_repository import ConversationRepository
from robbot.core.security import get_current_user
from robbot.domain.enums import ConversationStatus, Role
from robbot.infra.db.session import get_db
from robbot.services.conversation_service import ConversationService

router = APIRouter()


# ===== SCHEMAS =====

class ConversationOut(BaseModel):
    """Response schema for conversation."""
    id: str
    chat_id: str
    phone_number: str
    status: str
    lead_status: str
    is_urgent: bool
    lead_id: Optional[str]
    assigned_to_user_id: Optional[int]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ConversationListOut(BaseModel):
    """Response schema for conversation list."""
    conversations: List[ConversationOut]
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


# ===== ENDPOINTS =====

@router.get("/conversations", response_model=ConversationListOut, tags=["Conversations"])
def list_conversations(
    status: Optional[str] = Query(None, description="Filter by status"),
    urgent_only: bool = Query(False, description="Show only urgent conversations"),
    assigned_to_me: bool = Query(False, description="Show only assigned to current user"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List conversations with filters.
    
    Requires JWT authentication.
    
    Filters:
    - status: ACTIVE, WAITING_SECRETARY, TRANSFERRED, CLOSED
    - urgent_only: Show only is_urgent=true
    - assigned_to_me: Show only assigned to authenticated user
    """
    repo = ConversationRepository(db)
    
    # Build filters
    filters = {}
    if status:
        try:
            filters["status"] = ConversationStatus[status.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    if urgent_only:
        filters["is_urgent"] = True
    
    if assigned_to_me:
        filters["assigned_to_user_id"] = current_user.id
    
    # Get conversations
    conversations = repo.find_by_criteria(filters, limit=limit, offset=offset)
    total = len(repo.find_by_criteria(filters))
    
    # Convert to response
    conversations_out = [
        ConversationOut(
            id=c.id,
            chat_id=c.chat_id,
            phone_number=c.phone_number,
            status=c.status.value,
            lead_status=c.lead_status.value,
            is_urgent=c.is_urgent,
            lead_id=c.lead_id,
            assigned_to_user_id=c.assigned_to_user_id,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in conversations
    ]
    
    return ConversationListOut(conversations=conversations_out, total=total)


@router.get("/conversations/{conversation_id}", response_model=ConversationOut, tags=["Conversations"])
def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get conversation by ID.
    
    Requires JWT authentication.
    """
    repo = ConversationRepository(db)
    conversation = repo.get_by_id(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationOut(
        id=conversation.id,
        chat_id=conversation.chat_id,
        phone_number=conversation.phone_number,
        status=conversation.status.value,
        lead_status=conversation.lead_status.value,
        is_urgent=conversation.is_urgent,
        lead_id=conversation.lead_id,
        assigned_to_user_id=conversation.assigned_to_user_id,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
    )


@router.put("/conversations/{conversation_id}/status", tags=["Conversations"])
def update_conversation_status(
    conversation_id: str,
    request: UpdateStatusRequest,
    current_user: dict = Depends(get_current_user),
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
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {request.new_status}")
    
    try:
        conversation = service.update_status(conversation_id, new_status)
        
        return {
            "message": "Status updated successfully",
            "conversation_id": conversation.id,
            "new_status": conversation.status.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.post("/conversations/{conversation_id}/transfer", tags=["Conversations"])
def transfer_conversation(
    conversation_id: str,
    request: TransferRequest,
    current_user: dict = Depends(get_current_user),
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer: {str(e)}")


@router.post("/conversations/{conversation_id}/close", tags=["Conversations"])
def close_conversation(
    conversation_id: str,
    request: CloseRequest,
    current_user: dict = Depends(get_current_user),
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close: {str(e)}")


@router.put("/conversations/{conversation_id}/notes", tags=["Conversations"])
def update_conversation_notes(
    conversation_id: str,
    request: UpdateNotesRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update conversation notes (internal comments for secretaries).
    
    Requires JWT authentication.
    
    Notes are stored as plain text (max 5000 chars).
    """
    repo = ConversationRepository(db)
    conversation = repo.get_by_id(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        conversation = repo.update(
            conversation_id=conversation.id,
            data={"notes": request.notes}
        )
        
        return {
            "message": "Notes updated successfully",
            "conversation_id": conversation.id,
            "notes": conversation.notes,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update notes: {str(e)}")


@router.get("/conversations/export", tags=["Conversations"])
def export_conversations(
    export_format: str = Query("csv", description="Export format (csv only)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user),
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
    
    repo = ConversationRepository(db)
    
    # Build filters
    filters = {}
    if status:
        try:
            filters["status"] = ConversationStatus[status.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    # Non-admin users can only export their own conversations
    if current_user.role != Role.ADMIN:
        filters["assigned_to_user_id"] = current_user.id
    
    # Get conversations
    conversations = repo.find_by_criteria(filters)
    
    # Filter by date range
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            conversations = [c for c in conversations if c.created_at >= start_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            conversations = [c for c in conversations if c.created_at <= end_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "ID",
        "Chat ID",
        "Phone Number",
        "Status",
        "Lead Status",
        "Is Urgent",
        "Assigned To",
        "Created At",
        "Updated At",
    ])
    
    # Rows
    for conv in conversations:
        writer.writerow([
            conv.id,
            conv.chat_id,
            conv.phone_number,
            conv.status.value,
            conv.lead_status.value,
            conv.is_urgent,
            conv.assigned_to_user_id or "",
            conv.created_at.isoformat(),
            conv.updated_at.isoformat(),
        ])
    
    # Stream response
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=conversations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


@router.get("/conversations/search", response_model=ConversationListOut, tags=["Conversations"])
def search_conversations(
    q: str = Query(..., min_length=3, description="Search query (min 3 chars)"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Full-text search in conversation messages.
    
    Requires JWT authentication.
    
    Searches in message content using PostgreSQL full-text search.
    Non-admin users can only search their own assigned conversations.
    """
    from robbot.adapters.repositories.conversation_message_repository import (
        ConversationMessageRepository
    )
    
    msg_repo = ConversationMessageRepository(db)
    conv_repo = ConversationRepository(db)
    
    # Search messages with full-text query
    # Using simple LIKE for now (can be upgraded to PostgreSQL ts_vector)
    from sqlalchemy import or_
    
    result = db.execute(
        msg_repo.table.select()
        .where(msg_repo.table.c.content.ilike(f"%{q}%"))
        .limit(limit * 5)  # Get more messages to find unique conversations
    ).fetchall()
    
    # Get unique conversation IDs
    conversation_ids = list(set([row.conversation_id for row in result]))[:limit]
    
    # Get conversations
    conversations = []
    for conv_id in conversation_ids:
        conv = conv_repo.get_by_id(conv_id)
        if conv:
            # Filter by user if not admin
            if current_user.role != Role.ADMIN:
                if conv.assigned_to_user_id != current_user.id:
                    continue
            conversations.append(conv)
    
    # Convert to response
    conversations_out = [
        ConversationOut(
            id=c.id,
            chat_id=c.chat_id,
            phone_number=c.phone_number,
            status=c.status.value,
            lead_status=c.lead_status.value,
            is_urgent=c.is_urgent,
            lead_id=c.lead_id,
            assigned_to_user_id=c.assigned_to_user_id,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in conversations
    ]
    
    return ConversationListOut(conversations=conversations_out, total=len(conversations_out))
