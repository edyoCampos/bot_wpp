"""
Job para processar mensagens recebidas/enviadas via WAHA.
"""

import logging
from typing import Any, Optional

from robbot.adapters.repositories.message_repository import MessageRepository
from robbot.infra.jobs.base_job import BaseJob, JobRetryableError

logger = logging.getLogger(__name__)


class MessageProcessingJob(BaseJob):
    """
    Job para processar mensagens WhatsApp (entrada/saída).
    
    Responsabilidades:
    - Validar formato da mensagem
    - Persistir em BD (messages, message_media)
    - Aplicar anti-ban delays
    - Enfileirar para IA se necessário
    - Atualizar status de conversação
    """

    def __init__(
        self,
        message_data: dict[str, Any],
        message_direction: str = "inbound",  # "inbound" ou "outbound"
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs,
    ):
        """
        Inicializar job de mensagem.
        
        Args:
            message_data: Payload da mensagem (conteúdo, tipo, timestamp, etc)
            message_direction: "inbound" ou "outbound"
            conversation_id: ID da conversa
            user_id: ID do usuário proprietário
            **kwargs: Argumentos herdados de BaseJob
        """
        super().__init__(**kwargs)
        
        self.message_data = message_data
        self.message_direction = message_direction
        self.conversation_id = conversation_id
        self.user_id = user_id
        
        # Validação inicial
        self._validate_message_data()

    def _validate_message_data(self) -> None:
        """Validar formato básico da mensagem."""
        required_fields = ["phone", "text"]
        
        for field in required_fields:
            if field not in self.message_data or not self.message_data[field]:
                raise ValueError(f"Campo obrigatório ausente: {field}")

    def execute(self) -> dict[str, Any]:
        """
        Executar processamento da mensagem.
        
        Returns:
            Dict com ID da mensagem persistida e próximas ações
            
        Raises:
            JobRetryableError: Se BD indisponível (aguardará retry)
            ValueError: Se payload inválido (falha imediata)
        """
        logger.info(
            f"Processando mensagem {self.message_direction} para {self.message_data.get('phone')}",
            extra=self._log_context(),
        )
        
        try:
            # Persistir mensagem
            message_repo = MessageRepository()
            
            message_record = message_repo.create(
                conversation_id=self.conversation_id,
                direction=self.message_direction,
                content=self.message_data.get("text"),
                message_type=self.message_data.get("type", "text"),
                waha_message_id=self.message_data.get("id"),
                phone=self.message_data.get("phone"),
                timestamp=self.message_data.get("timestamp"),
                metadata=self.message_data,
            )
            
            logger.info(
                f"✓ Mensagem persistida: {message_record.id}",
                extra=self._log_context(),
            )
            
            # Se for mensagem recebida, enfileirar para IA processar
            if self.message_direction == "inbound":
                needs_ai_processing = True
                logger.debug(
                    f"Mensagem enfileirada para processamento de IA",
                    extra=self._log_context(),
                )
            else:
                needs_ai_processing = False
            
            return {
                "status": "success",
                "message_id": message_record.id,
                "conversation_id": self.conversation_id,
                "needs_ai_processing": needs_ai_processing,
                "phone": self.message_data.get("phone"),
            }

        except Exception as e:
            logger.error(
                f"Erro ao processar mensagem: {type(e).__name__}: {e}",
                extra=self._log_context(),
            )
            
            # Se for erro de conexão com BD, retry
            if "database" in str(e).lower() or "connection" in str(e).lower():
                raise JobRetryableError(f"Erro de BD: {e}")
            else:
                raise


class MessageBatchProcessingJob(BaseJob):
    """
    Job para processar lote de mensagens (útil para sincronização).
    
    Responsabilidades:
    - Processar múltiplas mensagens em sequência
    - Aplicar throttling para anti-ban
    - Reportar progresso
    """

    def __init__(
        self,
        messages: list[dict[str, Any]],
        conversation_id: Optional[str] = None,
        **kwargs,
    ):
        """
        Inicializar job de lote.
        
        Args:
            messages: Lista de payloads de mensagem
            conversation_id: ID da conversa
            **kwargs: Argumentos herdados
        """
        super().__init__(**kwargs)
        
        self.messages = messages
        self.conversation_id = conversation_id

    def execute(self) -> dict[str, Any]:
        """
        Executar processamento em lote.
        
        Returns:
            Dict com resultado: processadas, falhadas, total
        """
        processed = 0
        failed = 0
        
        logger.info(
            f"Iniciando processamento em lote de {len(self.messages)} mensagens",
            extra=self._log_context(),
        )
        
        for idx, msg_data in enumerate(self.messages):
            try:
                job = MessageProcessingJob(
                    message_data=msg_data,
                    conversation_id=self.conversation_id,
                    attempt=0,
                )
                job.run()
                processed += 1
                
            except Exception as e:
                logger.warning(
                    f"Falha ao processar mensagem {idx + 1}: {e}",
                    extra=self._log_context(),
                )
                failed += 1
        
        logger.info(
            f"Lote processado: {processed} OK, {failed} falhadas",
            extra=self._log_context(),
        )
        
        return {
            "status": "completed",
            "processed": processed,
            "failed": failed,
            "total": len(self.messages),
        }
