"""
Tag Controller - REST endpoints for tag management.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from robbot.adapters.repositories.conversation_repository import ConversationRepository
from robbot.adapters.repositories.conversation_tag_repository import ConversationTagRepository
from robbot.core.security import get_current_user
from robbot.domain.enums import Role
from robbot.infra.db.session import get_db
from robbot.services.tag_service import TagService

router = APIRouter()


# ===== SCHEMAS =====

class TagOut(BaseModel):
    """Response schema for tag."""
    id: int
    name: str
    color: str
    created_at: str

    class Config:
        from_attributes = True


class CreateTagRequest(BaseModel):
    """Request schema for creating tag."""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")


class AddTagRequest(BaseModel):
    """Request schema for adding tag to conversation."""
    tag_id: int


# ===== ENDPOINTS =====

@router.post("/tags", response_model=TagOut, tags=["Tags"])
def create_tag(
    request: CreateTagRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new tag (admin only).
    
    Requires JWT authentication and admin role.
    
    Color format: #RRGGBB (hex color code)
    """
    # Check admin permission
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = TagService(db)
    
    try:
        tag = service.create_tag(name=request.name, color=request.color)
        db.commit()
        
        return TagOut(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            created_at=tag.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create tag: {str(e)}")


@router.get("/tags", response_model=List[TagOut], tags=["Tags"])
def list_tags(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all tags.
    
    Requires JWT authentication.
    """
    service = TagService(db)
    tags = service.get_all_tags()
    
    return [
        TagOut(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            created_at=tag.created_at.isoformat(),
        )
        for tag in tags
    ]


@router.delete("/tags/{tag_id}", tags=["Tags"])
def delete_tag(
    tag_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a tag (admin only).
    
    Requires JWT authentication and admin role.
    """
    # Check admin permission
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = TagService(db)
    
    try:
        deleted = service.delete_tag(tag_id)
        db.commit()
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        return {"message": "Tag deleted successfully", "tag_id": tag_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete tag: {str(e)}")


@router.post("/conversations/{conversation_id}/tags", tags=["Tags"])
def add_tag_to_conversation(
    conversation_id: str,
    request: AddTagRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a tag to a conversation.
    
    Requires JWT authentication.
    """
    # Check conversation exists
    conv_repo = ConversationRepository(db)
    conversation = conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check tag exists
    tag_service = TagService(db)
    tag = tag_service.get_tag_by_id(request.tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Add association
    try:
        conv_tag_repo = ConversationTagRepository(db)
        conv_tag_repo.add_tag_to_conversation(conversation_id, request.tag_id)
        db.commit()
        
        return {
            "message": "Tag added to conversation",
            "conversation_id": conversation_id,
            "tag_id": request.tag_id,
            "tag_name": tag.name,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add tag: {str(e)}")


@router.delete("/conversations/{conversation_id}/tags/{tag_id}", tags=["Tags"])
def remove_tag_from_conversation(
    conversation_id: str,
    tag_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove a tag from a conversation.
    
    Requires JWT authentication.
    """
    # Check conversation exists
    conv_repo = ConversationRepository(db)
    conversation = conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Remove association
    try:
        conv_tag_repo = ConversationTagRepository(db)
        deleted = conv_tag_repo.remove_tag_from_conversation(conversation_id, tag_id)
        db.commit()
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Tag not associated with this conversation")
        
        return {
            "message": "Tag removed from conversation",
            "conversation_id": conversation_id,
            "tag_id": tag_id,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove tag: {str(e)}")


@router.get("/conversations/{conversation_id}/tags", response_model=List[TagOut], tags=["Tags"])
def get_conversation_tags(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all tags for a conversation.
    
    Requires JWT authentication.
    """
    # Check conversation exists
    conv_repo = ConversationRepository(db)
    conversation = conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get tags
    conv_tag_repo = ConversationTagRepository(db)
    tags = conv_tag_repo.get_conversation_tags(conversation_id)
    
    return [
        TagOut(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            created_at=tag.created_at.isoformat(),
        )
        for tag in tags
    ]
