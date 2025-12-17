"""
Re-engagement Job - Reactivate inactive conversations.

Job automático que:
1. Detecta conversas inativas (sem mensagem há > 48h)
2. Envia mensagem automática via WAHA
3. Atualiza status para AWAITING_RESPONSE
"""

import logging
from datetime import datetime, timedelta, UTC

from robbot.adapters.external.waha_client import WAHAClient
from robbot.adapters.repositories.conversation_message_repository import (
    ConversationMessageRepository
)
from robbot.adapters.repositories.conversation_repository import ConversationRepository
from robbot.core.custom_exceptions import WAHAError, DatabaseError, JobError
from robbot.domain.enums import ConversationStatus, MessageDirection
from robbot.domain.entities.conversation_message import ConversationMessage
from robbot.infra.db.session import SessionLocal

logger = logging.getLogger(__name__)


class ReEngagementJob:
    """
    Job para reativar conversas inativas.
    
    Detecta conversas:
    - Status: ACTIVE
    - Última mensagem: > 48h
    - Não tem urgência (is_urgent=False)
    
    Ação:
    - Envia mensagem automática
    - Atualiza status para AWAITING_RESPONSE
    """
    
    # Template de mensagem de re-engagement
    REENGAGEMENT_TEMPLATES = [
        "Olá! Notamos que você estava interessado em nossos serviços. Podemos ajudar em algo?",
        "Oi! Está tudo bem? Ainda tem interesse em conversar conosco?",
        "Olá! Vimos que você nos procurou recentemente. Gostaria de retomar nossa conversa?",
    ]
    
    INACTIVE_THRESHOLD_HOURS = 48
    
    def __init__(self):
        self.waha_client = WAHAClient()
    
    def execute(self) -> dict:
        """
        Executar job de re-engagement.
        
        Returns:
            Dict com estatísticas:
            {
                "status": "success",
                "conversations_found": int,
                "messages_sent": int,
                "errors": int
            }
        """
        logger.info("🔄 Iniciando job de re-engagement")
        
        stats = {
            "status": "success",
            "conversations_found": 0,
            "messages_sent": 0,
            "errors": 0,
        }
        
        try:
            with SessionLocal() as session:
                # Buscar conversas inativas
                inactive_conversations = self._find_inactive_conversations(session)
                stats["conversations_found"] = len(inactive_conversations)
                
                logger.info(
                    f"✓ Encontradas {len(inactive_conversations)} conversas inativas"
                )
                
                # Processar cada conversa
                for conversation in inactive_conversations:
                    try:
                        self._reengage_conversation(session, conversation)
                        stats["messages_sent"] += 1
                    except (WAHAError, DatabaseError) as e:
                        logger.error(
                            f"✗ Erro ao reengajar conversa {conversation.id}: {e}"
                        )
                        stats["errors"] += 1
                
                session.commit()
                
                logger.info(
                    f"✓ Re-engagement concluído: {stats['messages_sent']} enviadas, "
                    f"{stats['errors']} erros"
                )
        
        except JobError:
            raise
        except Exception as e:
            logger.error(f"✗ Erro fatal no job de re-engagement: {e}")
            stats["status"] = "error"
            stats["error_message"] = str(e)
            raise JobError(job_name="reengagement", message=f"Fatal error: {e}", original_error=e)
        
        return stats
    
    def _find_inactive_conversations(self, session) -> list:
        """
        Buscar conversas inativas (> 48h sem mensagem).
        
        Critérios:
        - Status: ACTIVE
        - is_urgent: False
        - Última mensagem: > 48h
        """
        conv_repo = ConversationRepository(session)
        msg_repo = ConversationMessageRepository(session)
        
        # Data limite (48h atrás)
        cutoff_time = datetime.now(UTC) - timedelta(hours=self.INACTIVE_THRESHOLD_HOURS)
        
        # Buscar conversas ACTIVE e não urgentes
        active_conversations = conv_repo.find_by_criteria({
            "status": ConversationStatus.ACTIVE,
            "is_urgent": False,
        })
        
        # Filtrar por última mensagem
        inactive_conversations = []
        
        for conv in active_conversations:
            # Buscar última mensagem da conversa
            messages = msg_repo.get_by_conversation_id(conv.id, limit=1)
            
            if not messages:
                # Sem mensagens, pular
                continue
            
            last_message = messages[0]
            
            # Verificar se última mensagem é > 48h
            if last_message.timestamp < cutoff_time:
                inactive_conversations.append(conv)
        
        return inactive_conversations
    
    def _reengage_conversation(self, session, conversation) -> None:
        """
        Reengajar uma conversa inativa.
        
        1. Envia mensagem via WAHA
        2. Salva mensagem outbound
        3. Atualiza status para AWAITING_RESPONSE
        """
        # Escolher template (round-robin baseado em ID)
        template_index = hash(conversation.id) % len(self.REENGAGEMENT_TEMPLATES)
        message_text = self.REENGAGEMENT_TEMPLATES[template_index]
        
        # Enviar via WAHA
        try:
            self.waha_client.send_text_message(
                session="default",
                chat_id=conversation.chat_id,
                text=message_text
            )
            logger.info(
                f"✓ Mensagem de re-engagement enviada (conv_id={conversation.id})"
            )
        except Exception as e:
            logger.error(f"✗ Falha ao enviar via WAHA: {e}")
            raise
        
        # Salvar mensagem outbound
        msg_repo = ConversationMessageRepository(session)
        message = ConversationMessage(
            conversation_id=conversation.id,
            direction=MessageDirection.OUTBOUND,
            content=message_text,
            timestamp=datetime.now(UTC),
        )
        msg_repo.create(message)
        session.flush()
        
        # Atualizar status da conversa
        conv_repo = ConversationRepository(session)
        conv_repo.update(
            conversation_id=conversation.id,
            data={"status": ConversationStatus.WAITING_SECRETARY}
        )
        session.flush()
        
        logger.info(
            f"✓ Conversa reengajada (id={conversation.id}, "
            f"status={conversation.status.value})"
        )


def run_reengagement_job():
    """
    Entry point para executar o job.
    
    Pode ser chamado por:
    - RQ scheduler (diário)
    - Cron job
    - Manualmente via API
    """
    job = ReEngagementJob()
    return job.execute()
