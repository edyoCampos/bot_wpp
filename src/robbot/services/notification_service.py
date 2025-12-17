"""
Notification Service - Sistema de notificações in-app.

Este service gerencia notificações para secretárias sobre novos leads e mensagens.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, Session, mapped_column

from robbot.core.exceptions import NotFoundException
from robbot.infra.db.base import Base

logger = logging.getLogger(__name__)


# ===== MODEL =====

class NotificationModel(Base):
    """Model para notificações in-app."""

    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Tipo: NEW_LEAD, NEW_MESSAGE, etc."
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<NotificationModel(id='{self.id}', user_id={self.user_id}, read={self.read})>"


# ===== SERVICE =====

class NotificationService:
    """
    Service para gerenciar notificações.
    
    Responsabilidades:
    - Criar notificações
    - Marcar como lida
    - Listar notificações do usuário
    """

    def __init__(self, db: Session):
        """Inicializar service com sessão do banco."""
        self.db = db

    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
    ) -> NotificationModel:
        """
        Criar nova notificação.
        
        Args:
            user_id: ID do usuário destinatário
            notification_type: Tipo da notificação (NEW_LEAD, NEW_MESSAGE, etc.)
            title: Título da notificação
            message: Mensagem detalhada
            
        Returns:
            Notificação criada
        """
        notification = NotificationModel(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            read=False,
        )
        
        self.db.add(notification)
        self.db.flush()
        
        logger.info(
            f"✓ Notificação criada (id={notification.id}, "
            f"user_id={user_id}, type={notification_type})"
        )
        
        return notification

    def mark_as_read(self, notification_id: str) -> NotificationModel:
        """
        Marcar notificação como lida.
        
        Args:
            notification_id: ID da notificação
            
        Returns:
            Notificação atualizada
            
        Raises:
            NotFoundException: Se notificação não existir
        """
        notification = (
            self.db.query(NotificationModel)
            .filter_by(id=notification_id)
            .first()
        )
        
        if not notification:
            raise NotFoundException(f"Notification {notification_id} not found")
        
        notification.read = True
        self.db.flush()
        
        logger.info(f"✓ Notificação marcada como lida (id={notification_id})")
        
        return notification

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[NotificationModel]:
        """
        Obter notificações do usuário.
        
        Args:
            user_id: ID do usuário
            unread_only: Retornar apenas não lidas
            limit: Número máximo de resultados
            
        Returns:
            Lista de notificações
        """
        query = self.db.query(NotificationModel).filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(read=False)
        
        notifications = (
            query
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
            .all()
        )
        
        logger.info(
            f"✓ Notificações obtidas (user_id={user_id}, "
            f"count={len(notifications)}, unread_only={unread_only})"
        )
        
        return notifications

    def count_unread(self, user_id: int) -> int:
        """
        Contar notificações não lidas.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Número de notificações não lidas
        """
        count = (
            self.db.query(NotificationModel)
            .filter_by(user_id=user_id, read=False)
            .count()
        )
        
        return count

    def notify_new_lead(
        self,
        user_id: int,
        lead_phone: str,
        lead_name: str,
    ) -> NotificationModel:
        """
        Notificar sobre novo lead atribuído.
        
        Args:
            user_id: ID da secretária
            lead_phone: Telefone do lead
            lead_name: Nome do lead
            
        Returns:
            Notificação criada
        """
        return self.create_notification(
            user_id=user_id,
            notification_type="NEW_LEAD",
            title="Novo Lead Atribuído",
            message=f"Novo lead: {lead_name} ({lead_phone})",
        )

    def notify_new_message(
        self,
        user_id: int,
        conversation_id: str,
        message_preview: str,
    ) -> NotificationModel:
        """
        Notificar sobre nova mensagem.
        
        Args:
            user_id: ID da secretária
            conversation_id: ID da conversa
            message_preview: Preview da mensagem
            
        Returns:
            Notificação criada
        """
        return self.create_notification(
            user_id=user_id,
            notification_type="NEW_MESSAGE",
            title="Nova Mensagem",
            message=f"Conversa {conversation_id[:8]}: {message_preview[:50]}...",
        )

    def notify_urgent_message(
        self,
        user_id: int,
        conversation_id: str,
        message_text: str,
    ) -> NotificationModel:
        """
        Notificar sobre mensagem urgente.
        
        Args:
            user_id: ID da secretária
            conversation_id: ID da conversa
            message_text: Texto da mensagem urgente
            
        Returns:
            Notificação criada
        """
        return self.create_notification(
            user_id=user_id,
            notification_type="URGENT_MESSAGE",
            title="⚠️ Mensagem Urgente",
            message=f"[URGENTE] Conversa {conversation_id[:8]}: {message_text[:100]}",
        )
