"""
Notification endpoints.

Este módulo expõe endpoints REST para gerenciar notificações in-app.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_db, get_current_user
from robbot.core.exceptions import NotFoundException
from robbot.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ========== SCHEMAS ==========

class NotificationOut(BaseModel):
    """Response de notificação."""
    
    id: str
    user_id: int
    type: str
    title: str
    message: str
    read: bool
    created_at: str
    
    class Config:
        from_attributes = True


class MarkReadRequest(BaseModel):
    """Request para marcar como lida."""
    # Endpoint usa apenas o ID da URL - sem campos necessários
    model_config = {"extra": "forbid"}


# ========== ENDPOINTS ==========

@router.get(
    "",
    response_model=list[NotificationOut],
    status_code=status.HTTP_200_OK,
    summary="Listar notificações do usuário",
    description="""
    Retorna notificações do usuário autenticado.
    
    Query params:
    - unread_only: Retornar apenas não lidas (default: false)
    - limit: Número máximo de resultados (default: 50, max: 100)
    """,
)
async def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[NotificationOut]:
    """
    Listar notificações do usuário autenticado.
    
    Args:
        unread_only: Filtrar apenas não lidas
        limit: Número máximo de resultados
        db: Sessão do banco
        current_user: Usuário autenticado
        
    Returns:
        Lista de notificações
    """
    # Validar limit
    if limit > 100:
        limit = 100
    
    service = NotificationService(db)
    
    notifications = service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
    )
    
    return [
        NotificationOut(
            id=n.id,
            user_id=n.user_id,
            type=n.type,
            title=n.title,
            message=n.message,
            read=n.read,
            created_at=n.created_at.isoformat(),
        )
        for n in notifications
    ]


@router.get(
    "/unread-count",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Contar notificações não lidas",
)
async def count_unread_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Contar notificações não lidas do usuário.
    
    Args:
        db: Sessão do banco
        current_user: Usuário autenticado
        
    Returns:
        Dict com contagem: {"count": 5}
    """
    service = NotificationService(db)
    count = service.count_unread(user_id=current_user.id)
    
    return {"count": count}


@router.put(
    "/{notification_id}/read",
    response_model=NotificationOut,
    status_code=status.HTTP_200_OK,
    summary="Marcar notificação como lida",
)
async def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> NotificationOut:
    """
    Marcar notificação como lida.
    
    Args:
        notification_id: ID da notificação
        db: Sessão do banco
        current_user: Usuário autenticado
        
    Returns:
        Notificação atualizada
        
    Raises:
        HTTPException 404: Se notificação não existir
        HTTPException 403: Se notificação não pertencer ao usuário
    """
    service = NotificationService(db)
    
    try:
        # Buscar notificação
        notification = (
            db.query(service.db.query(NotificationService.NotificationModel).filter_by(
                id=notification_id
            ).first())
        )
        
        # Alternativa: usar query direta
        from robbot.services.notification_service import NotificationModel
        notification = db.query(NotificationModel).filter_by(id=notification_id).first()
        
        if not notification:
            raise NotFoundException(f"Notification {notification_id} not found")
        
        # Verificar se pertence ao usuário
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this notification",
            )
        
        # Marcar como lida
        updated = service.mark_as_read(notification_id)
        
        return NotificationOut(
            id=updated.id,
            user_id=updated.user_id,
            type=updated.type,
            title=updated.title,
            message=updated.message,
            read=updated.read,
            created_at=updated.created_at.isoformat(),
        )
        
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}",
        ) from e
