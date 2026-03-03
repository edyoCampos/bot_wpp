"""Job de Polling do WAHA Refatorado (Clean Architecture)."""

import logging
from rq import get_current_job

from robbot.config.settings import get_settings
from robbot.services.infrastructure.queue_service import get_queue_service
from robbot.services.communication.polling_strategies import get_polling_strategy
from robbot.services.communication.waha_metadata_service import WahaMetadataService
from robbot.services.communication.message_filter_service import MessageFilterService

logger = logging.getLogger(__name__)
settings = get_settings()

def poll_waha_messages(**_kwargs):
    """
    Job otimizado para buscar mensagens do WAHA.
    
    Arquitetura:
    - Strategy Pattern: Define alvos (DEV=Lista Fixa + Cache, PROD=Todos os Chats)
    - Metadata Service: Resolve LIDs com Cache Redis (Zero HTTP redundante)
    - Message Filter: Centraliza validação de regras de negócio e deduplicação
    """
    job = get_current_job()
    job_id = job.id if job else "no-job"

    # Logger com contexto reduzido para evitar spam, foca no ciclo macro
    # logger.debug("[POLLING] Iniciando ciclo...") 

    try:
        # 1. Obter serviços e estratégias
        metadata_service = WahaMetadataService()
        strategy = get_polling_strategy()
        message_filter = MessageFilterService()
        queue_service = get_queue_service()

        # 2. Definir alvos (Chats/LIDs)
        target_chats = strategy.get_target_chats()
        
        if not target_chats:
            if settings.DEV_MODE:
                logger.warning("[POLLING] Sem alvos configurados ou resolvidos em DEV_MODE")
            return

        messages_processed = 0
        messages_skipped = 0

        # 3. Iterar Chats
        for chat_id in target_chats:
            # Busca mensagens (Já trata erros 404/422 internamente no service)
            # Aumentado limit de 10 -> 50 para evitar perder mensagens se houver muito tráfego
            messages = metadata_service.get_messages_from_chat(chat_id, limit=50)
            
            # Conjunto para evitar logs repetidos de validação por remetente neste ciclo específico
            cycle_senders_checked = set()

            # 4. Iterate messages
            # REMOVED reversed() and early break optimization to ensure reliability.
            # We process all messages in the batch (limit=10) to guarantee no new message is skipped
            # regardless of the API sort order (New->Old or Old->New).
            # Performance impact is minimal for small limits.
            for message in messages:
                # 4a. Filtragem e Validação (Regras de Negócio)
                
                # Otimização de Log: Só logar verificação uma vez por remetente por ciclo
                sender = message.get("from")
                if settings.DEV_MODE and sender and sender not in cycle_senders_checked:
                    cycle_senders_checked.add(sender)
                    # O filter service fará a validação real abaixo silenciosamente
                
                # DEV Mode logic...
                allowed_senders = None
                
                if not message_filter.should_process(message, allowed_senders=allowed_senders):
                    messages_skipped += 1
                    # Removed early break to strictly process all messages
                    continue

                # 5. Processamento (Enfileiramento)
                try:
                    message_data = {
                        "id": message.get("id"),
                        "from": message.get("from"),
                        "to": message.get("to"),
                        "body": message.get("body", ""),
                        "timestamp": message.get("timestamp", 0),
                        "hasMedia": message.get("hasMedia", False),
                        "ack": message.get("ack", 0),
                        "_data": message.get("_data", {}),
                    }

                    # Enfileirar
                    # Nota: Debounce poderia ser aplicado aqui ou no worker. 
                    # Mantendo lógica original de debounce da fila.
                    queue_id = queue_service.enqueue_message_processing_debounced(
                        message_data=message_data,
                        message_direction="inbound",
                    )
                    
                    # Marcar como processado no Redis para evitar reprocessamento (Deduplicação)
                    message_filter.mark_as_processed(message_data["id"])
                    
                    messages_processed += 1
                    logger.info(
                        "[POLLING] Msg processada: %s | Chat: %s | QID: %s", 
                        message_data["id"], 
                        message_data['from'], 
                        queue_id
                    )

                except Exception as e:
                    logger.error("[POLLING] Falha ao enfileirar mensagem %s: %s", message.get("id"), e)

        # Log Final do Ciclo (Sempre para diagnóstico)
        if messages_processed > 0:
            logger.info(
                "[POLLING] Ciclo concluído. Processadas: %d | Ignoradas: %d",
                messages_processed,
                messages_skipped
            )
        elif messages_skipped > 0:
            logger.debug(
                "[POLLING] Ciclo sem novas mensagens. Ignoradas: %d (dedup/filtro)",
                messages_skipped
            )
        # Se ambos são 0, nenhuma mensagem foi retornada pela API
            
        return {
            "status": "success",
            "processed": messages_processed,
            "skipped": messages_skipped
        }

    except Exception as e:
        logger.error("[POLLING] Erro crítico no job: %s", e, exc_info=True)
        return {"status": "error", "message": str(e)}
