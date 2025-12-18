"""
Conversation Orchestrator - orquestra fluxo completo de conversação.

Este módulo é o componente central que coordena:
1. Recebimento de mensagens
2. Busca de contexto (ChromaDB)
3. Geração de respostas (Gemini + LangChain)
4. Detecção de intenção
5. Atualização de score de maturidade
6. Envio de respostas (WAHA)
7. Persistência de dados
"""

import json
import logging
from datetime import datetime, UTC
from typing import Any, Optional

from robbot.adapters.external.gemini_client import get_gemini_client
from robbot.adapters.external.waha_client import WAHAClient
from robbot.core.custom_exceptions import (
    DatabaseError,
    LLMError,
    WAHAError,
    QueueError,
    JobError,
    VectorDBError,
)
from robbot.services.playbook_tools import PLAYBOOK_TOOLS_DECLARATIONS
from robbot.adapters.repositories.conversation_message_repository import (
    ConversationMessageRepository
)
from robbot.adapters.repositories.conversation_repository import ConversationRepository
from robbot.adapters.repositories.lead_interaction_repository import (
    LeadInteractionRepository
)
from robbot.adapters.repositories.lead_repository import LeadRepository
from robbot.adapters.repositories.llm_interaction_repository import (
    LLMInteractionRepository
)
from robbot.config.prompts import get_prompt_templates
from robbot.core.exceptions import BusinessRuleError, ExternalServiceError
from robbot.domain.entities.conversation import Conversation
from robbot.domain.entities.conversation_message import ConversationMessage
from robbot.domain.entities.lead import Lead
from robbot.domain.entities.lead_interaction import LeadInteraction
from robbot.domain.entities.llm_interaction import LLMInteraction
from robbot.domain.enums import (
    ConversationStatus,
    InteractionType,
    LeadStatus,
    MessageDirection,
)
from robbot.infra.db.session import get_sync_session
from robbot.infra.vectordb.chroma_client import get_chroma_client

logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """
    Orquestrador central do fluxo de conversação.
    
    Responsabilidades:
    - Coordenar todos os componentes (Gemini, ChromaDB, WAHA, Repositórios)
    - Implementar lógica de negócio do fluxo de conversação
    - Gerenciar estado da conversa
    - Detectar intenções
    - Atualizar score de maturidade
    """

    def __init__(self):
        self.gemini_client = get_gemini_client(tools=PLAYBOOK_TOOLS_DECLARATIONS)
        self.chroma_client = get_chroma_client()
        self.prompt_templates = get_prompt_templates()
        self.waha_client = WAHAClient()
        
        logger.info("✓ ConversationOrchestrator inicializado com playbook tools")

    async def process_inbound_message(
        self,
        chat_id: str,
        phone_number: str,
        message_text: str,
        session_name: str = "default",
        has_audio: bool = False,
        audio_url: Optional[str] = None,
        has_video: bool = False,
        video_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Processar mensagem inbound e gerar resposta.
        
        FLUXO COMPLETO:
        1. Buscar ou criar conversa
        2. Transcrever áudio/vídeo e gerar descrição visual (se houver)
        3. Salvar mensagem inbound
        4. Buscar contexto do ChromaDB
        5. Detectar intenção
        6. Gerar resposta com Gemini
        7. Atualizar score de maturidade
        8. Salvar contexto no ChromaDB
        9. Enviar resposta via WAHA
        10. Salvar mensagem outbound
        11. Registrar interação
        
        Args:
            chat_id: ID do chat
            phone_number: Número do telefone
            message_text: Texto da mensagem
            session_name: Nome da sessão WAHA
            has_audio: Se mensagem tem áudio (voice)
            audio_url: URL do arquivo de áudio
            has_video: Se mensagem tem vídeo
            video_url: URL do arquivo de vídeo
            
        Returns:
            Dict com resultado:
            {
                "conversation_id": str,
                "response_sent": bool,
                "response_text": str,
                "intent": str,
                "maturity_score": int
            }
            
        Raises:
            BusinessRuleError: Se falhar na lógica de negócio
            ExternalServiceError: Se falhar em serviço externo
        """
        try:
            logger.info(
                f"🔄 Processando mensagem inbound (chat_id={chat_id}, "
                f"phone={phone_number}, length={len(message_text)}, "
                f"has_audio={has_audio}, has_video={has_video})"
            )
            
            with get_sync_session() as session:
                conversation = await self._get_or_create_conversation(
                    session, chat_id, phone_number
                )
                
                # BOT SILENCIA se humano está conversando
                if conversation.status in [
                    ConversationStatus.ACTIVE_HUMAN,
                    ConversationStatus.PENDING_HANDOFF,
                    ConversationStatus.COMPLETED,
                    ConversationStatus.CLOSED,
                ]:
                    # Apenas salva mensagem, não gera resposta automática
                    await self._save_inbound_message(
                        session, conversation.id, message_text
                    )
                    logger.info(
                        f"🤐 Bot silenciado: conversa em status {conversation.status} "
                        f"(conv_id={conversation.id})"
                    )
                    
                    # TODO: Notificar atendente via WebSocket
                    # await self.notification_service.notify_user(
                    #     conversation.assigned_to, 
                    #     f"Nova mensagem de {conversation.phone_number}"
                    # )
                    
                    session.commit()
                    return {
                        "conversation_id": conversation.id,
                        "response_sent": False,
                        "bot_silenced": True,
                        "status": conversation.status.value,
                    }
                
                # Processar mídia conforme tipo
                transcription = None
                
                # Se é vídeo: transcrever áudio + descrever visual
                if has_video and video_url:
                    try:
                        # 1. Transcrever áudio do vídeo
                        from robbot.services.transcription_service import TranscriptionService
                        transcriber = TranscriptionService()
                        transcription = await transcriber.transcribe_audio(video_url, language="pt")
                        
                        if transcription:
                            logger.info(f"✓ Áudio do vídeo transcrito: {transcription[:100]}...")
                        
                        # 2. Gerar descrição visual com Gemini Vision
                        # TODO: Implementar descrição assíncrona
                        # Por ora, apenas marcamos que há vídeo
                        message_text = f"[Vídeo recebido]\nÁudio: {transcription or 'não transcrito'}"
                        
                    except Exception as e:
                        logger.error(f"✗ Erro ao processar vídeo: {e}")
                        message_text = "[Vídeo recebido - erro no processamento]"
                
                # Se é apenas áudio, transcrever
                elif has_audio and audio_url:
                    try:
                        from robbot.services.transcription_service import TranscriptionService
                        transcriber = TranscriptionService()
                        transcription = await transcriber.transcribe_audio(audio_url, language="pt")
                        
                        if transcription:
                            logger.info(f"✓ Áudio transcrito: {transcription[:100]}...")
                            message_text = f"[Áudio transcrito]: {transcription}"
                        else:
                            logger.warning("⚠️ Transcrição retornou vazio")
                            message_text = "[Áudio recebido - transcrição falhou]"
                    except Exception as e:
                        logger.error(f"✗ Erro ao transcrever áudio: {e}")
                        message_text = "[Áudio recebido - erro na transcrição]"
                
                await self._save_inbound_message(
                    session, conversation.id, message_text
                )
                
                context_text = await self._get_conversation_context(conversation.id)
                intent = await self._detect_intent(message_text, context_text)
                
                is_urgent = await self._detect_urgency(message_text, context_text)
                if is_urgent and not conversation.is_urgent:
                    conversation.is_urgent = True
                    conv_repo = ConversationRepository(session)
                    conv_repo.update(conversation.id, {"is_urgent": True})
                    session.flush()
                    logger.info(f"🚨 Urgência detectada (conv_id={conversation.id})")
                
                # Extrair nome do paciente se ainda não temos
                if conversation.lead and conversation.lead.name == conversation.lead.phone_number:
                    await self._try_extract_name(session, message_text, context_text, conversation)
                
                response_data = await self._generate_response(
                    message_text=message_text,
                    intent=intent,
                    context=context_text,
                    conversation=conversation,
                )
                
                response_text = response_data["response"]
                
                # Se ainda não temos nome E score >= 20, solicitar de forma natural
                should_ask_name = (
                    conversation.lead 
                    and conversation.lead.name == conversation.lead.phone_number
                    and conversation.lead.maturity_score >= 20
                    and conversation.lead.maturity_score < 50
                )
                
                if should_ask_name:
                    name_request = await self._generate_name_request(
                        context_text, 
                        conversation.lead.maturity_score
                    )
                    if name_request:
                        response_text = f"{response_text}\n\n{name_request}"
                
                new_score = await self._update_maturity_score(
                    session, conversation, message_text, intent
                )
                
                # Verificar se precisa escalar para humano
                should_escalate = await self._check_escalation_needed(
                    conversation, intent, message_text, new_score
                )
                
                if should_escalate:
                    # Trigger handoff antes de responder
                    from robbot.services.handoff_service import HandoffService
                    handoff_service = HandoffService(
                        ConversationRepository(session),
                        LeadRepository(session)
                    )
                    
                    escalation_reason = "score_high" if new_score >= 85 else "bot_confused"
                    handoff_result = await handoff_service.trigger_handoff(
                        session=session,
                        conversation_id=conversation.id,
                        reason=escalation_reason,
                        score=new_score,
                    )
                    
                    # Sobrescrever resposta com mensagem de transição
                    response_text = handoff_result["message"]
                    
                    logger.info(
                        f"🚀 Handoff automático triggered: conv={conversation.id}, "
                        f"reason={escalation_reason}, score={new_score}"
                    )
                
                await self._save_to_chroma(
                    conversation.id,
                    f"User: {message_text}\nBot: {response_text}",
                    {"intent": intent, "score": new_score}
                )
                
                sent = await self._send_response_via_waha(
                    chat_id, response_text, session_name
                )
                
                await self._save_outbound_message(
                    session, conversation.id, response_text
                )
                
                await self._register_interaction(
                    session,
                    conversation.lead_id,
                    intent,
                    f"Inbound: {message_text[:50]}... | Outbound: {response_text[:50]}..."
                )
                
                await self._log_llm_interaction(
                    session,
                    conversation.id,
                    f"Intent: {intent} | {message_text[:100]}",
                    response_text[:200],
                    response_data.get("tokens_used", 0),
                    response_data.get("latency_ms", 0)
                )
                
                session.commit()
                
                logger.info(
                    f"✓ Mensagem processada com sucesso (conv_id={conversation.id}, "
                    f"intent={intent}, score={new_score}, sent={sent})"
                )
                
                return {
                    "conversation_id": conversation.id,
                    "response_sent": sent,
                    "response_text": response_text,
                    "intent": intent,
                    "maturity_score": new_score,
                }
                
        except Exception as e:
            logger.error(
                f"✗ Falha ao processar mensagem: {e}",
                exc_info=True,
                extra={"chat_id": chat_id, "phone": phone_number}
            )
            
            try:
                fallback_response = await self._generate_fallback_response(str(e))
                await self._send_response_via_waha(chat_id, fallback_response, session_name)
            except (LLMError, WAHAError) as fallback_error:
                logger.error(f"✗ Falha no fallback: {fallback_error}")
            
            raise BusinessRuleError(f"Failed to process message: {e}") from e

    async def _get_or_create_conversation(
        self,
        session: Any,
        chat_id: str,
        phone_number: str
    ) -> Conversation:
        """
        Buscar conversa existente por chat_id ou criar nova com lead associado.
        
        Returns:
            Conversation: Conversa existente ou recém-criada
            
        Raises:
            DatabaseError: Se falhar ao criar conversa ou lead
        """
        repo = ConversationRepository(session)
        
        conversation = repo.get_by_chat_id(chat_id)
        
        if conversation:
            logger.info(f"✓ Conversa encontrada (id={conversation.id})")
            return conversation
        
        lead_repo = LeadRepository(session)
        
        lead = Lead(
            phone_number=phone_number,
            name=phone_number,
            maturity_score=0,
        )
        lead_repo.create(lead)
        session.flush()
        
        conversation = repo.create(
            chat_id=chat_id,
            phone_number=phone_number,
            status=ConversationStatus.ACTIVE,
        )
        conversation.lead_status = LeadStatus.NEW
        conversation.lead_id = lead.id
        session.flush()
        
        logger.info(
            f"✓ Nova conversa criada (id={conversation.id}, lead_id={lead.id})"
        )
        
        return conversation

    async def _save_inbound_message(
        self,
        session: Any,
        conversation_id: str,
        text: str
    ) -> ConversationMessage:
        """
        Persistir mensagem recebida do lead no banco.
        
        Returns:
            ConversationMessage: Mensagem salva com timestamp UTC
            
        Raises:
            DatabaseError: Se falhar ao salvar mensagem
        """
        repo = ConversationMessageRepository(session)
        
        message = ConversationMessage(
            conversation_id=conversation_id,
            direction=MessageDirection.INBOUND,
            content=text,
            timestamp=datetime.now(UTC),
        )
        repo.create(message)
        session.flush()
        
        logger.info(f"✓ Mensagem inbound salva (id={message.id})")
        
        return message

    async def _save_outbound_message(
        self,
        session: Any,
        conversation_id: str,
        text: str
    ) -> ConversationMessage:
        """
        Persistir mensagem enviada pelo bot no banco.
        
        Returns:
            ConversationMessage: Mensagem salva com timestamp UTC
            
        Raises:
            DatabaseError: Se falhar ao salvar mensagem
        """
        repo = ConversationMessageRepository(session)
        
        message = ConversationMessage(
            conversation_id=conversation_id,
            direction=MessageDirection.OUTBOUND,
            content=text,
            timestamp=datetime.now(UTC),
        )
        repo.create(message)
        session.flush()
        
        logger.info(f"✓ Mensagem outbound salva (id={message.id})")
        
        return message

    async def _get_conversation_context(self, conversation_id: str) -> str:
        """
        Recuperar contexto conversacional do ChromaDB (últimas 5 interações).
        
        Returns:
            str: Contexto formatado (vazio se sem histórico)
            
        Raises:
            VectorDBError: Se falhar ao acessar ChromaDB
        """
        try:
            results = self.chroma_client.get_context(conversation_id, limit=5)
            
            if not results:
                return ""
            
            context_parts = [r["text"] for r in results]
            context_text = "\n---\n".join(context_parts)
            
            logger.info(f"✓ Contexto obtido ({len(results)} documentos)")
            
            return context_text
            
        except VectorDBError:
            raise
        except Exception as e:
            logger.warning(f"⚠️ Falha ao buscar contexto: {e}")
            raise VectorDBError(f"Failed to get context: {e}")

    async def _try_extract_name(
        self, 
        session: Any,
        message: str, 
        context: str, 
        conversation: Conversation
    ) -> None:
        """
        Tentar extrair nome do paciente da mensagem de forma inteligente.
        Atualiza o lead se encontrar nome com confiança >= 70%.
        """
        try:
            prompt = self.prompt_templates.format_name_extraction_prompt(message, context)
            response = self.gemini_client.generate_response(prompt)
            
            # Parse JSON response
            import json
            result = json.loads(response["response"].strip())
            
            name = result.get("name")
            confidence = result.get("confidence", 0)
            
            if name and name != "null" and confidence >= 70:
                # Atualizar nome do lead
                lead_repo = LeadRepository(session)
                conversation.lead.name = name
                lead_repo.update(conversation.lead)
                session.flush()
                
                logger.info(
                    f"✓ Nome extraído: '{name}' (confiança={confidence}%, "
                    f"fonte={result.get('source')})"
                )
        
        except (json.JSONDecodeError, LLMError) as e:
            logger.debug(f"Não foi possível extrair nome: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao tentar extrair nome: {e}")

    async def _generate_name_request(
        self, 
        context: str, 
        score: int
    ) -> str | None:
        """
        Gerar pergunta natural para descobrir o nome do paciente.
        Integra a pergunta de forma fluida no fluxo SPIN.
        
        Returns:
            str com a pergunta ou None se não for apropriado perguntar
        """
        try:
            # Determinar fase SPIN baseada no score
            if score < 30:
                spin_phase = "SITUATION"
            elif score < 50:
                spin_phase = "PROBLEM"  
            elif score < 75:
                spin_phase = "IMPLICATION"
            elif score < 85:
                spin_phase = "NEED_PAYOFF"
            else:
                spin_phase = "READY"
            
            prompt = self.prompt_templates.format_name_request_prompt(
                context, spin_phase, score
            )
            
            response = self.gemini_client.generate_response(prompt)
            name_request = response["response"].strip()
            
            logger.info(f"✓ Solicitação de nome gerada (fase={spin_phase}, score={score})")
            
            return name_request
            
        except LLMError as e:
            logger.warning(f"⚠️ Falha ao gerar solicitação de nome: {e}")
            return None

    async def _detect_urgency(self, message: str, context: str) -> bool:
        """
        Detectar se a mensagem é urgente usando LLM.
        
        Palavras-chave de urgência:
        - emergência, urgente, URGENTE, EMERGÊNCIA
        - dor, problema sério, imediato
        - não funciona, quebrado, parado
        - preciso agora, hoje mesmo
        """
        try:
            urgent_keywords = [
                "urgente", "emergência", "emergencia", "imediato", "agora",
                "hoje", "dor", "problema sério", "não funciona", "quebrado",
                "parado", "crítico", "critico", "grave", "help", "socorro"
            ]
            
            message_lower = message.lower()
            has_keyword = any(keyword in message_lower for keyword in urgent_keywords)
            
            if not has_keyword:
                return False
            
            prompt = f"""Analise se esta mensagem indica uma situação URGENTE que requer atenção imediata:

Mensagem: "{message}"
Contexto: {context[:200]}

Uma mensagem é URGENTE se:
- Usa palavras como "urgente", "emergência", "imediato", "agora"
- Relata problemas sérios/críticos que impedem trabalho
- Expressa dor ou situação grave
- Requer ação imediata

Responda apenas: SIM ou NÃO"""

            response = self.gemini_client.generate_response(prompt)
            result = response["response"].strip().upper()
            
            is_urgent = "SIM" in result
            
            if is_urgent:
                logger.warning(f"🚨 URGÊNCIA detectada: {message[:50]}...")
            
            return is_urgent
            
        except LLMError:
            raise
        except Exception as e:
            logger.warning(f"⚠️ Erro ao detectar urgência: {e}")
            return has_keyword if 'has_keyword' in locals() else False

    async def _detect_intent(self, message: str, context: str) -> str:
        """
        Classificar intenção da mensagem usando Gemini (10 categorias).
        
        Returns:
            str: Intent classificado (INTERESSE_PRODUTO, AGENDAMENTO, etc.) ou 'OUTRO'
            
        Raises:
            LLMError: Se Gemini falhar após retries
        """
        try:
            prompt = self.prompt_templates.format_intent_prompt(message, context)
            
            response = self.gemini_client.generate_response(prompt)
            intent = response["response"].strip().upper()
            
            valid_intents = [
                "INTERESSE_PRODUTO", "DUVIDA_TECNICA", "ORCAMENTO",
                "AGENDAMENTO", "RECLAMACAO", "INFORMACAO",
                "SAUDACAO", "DESPEDIDA", "CONFIRMACAO", "OUTRO"
            ]
            
            if intent not in valid_intents:
                intent = "OUTRO"
            
            logger.info(f"✓ Intenção detectada: {intent}")
            
            return intent
            
        except LLMError:
            raise
        except Exception as e:
            logger.warning(f"⚠️ Falha ao detectar intenção: {e}")
            return "OUTRO"

    async def _generate_response(
        self,
        message_text: str,
        intent: str,
        context: str,
        conversation: Conversation
    ) -> dict[str, Any]:
        """
        Gerar resposta contextualizada usando Gemini com template específico por intenção.
        
        Returns:
            dict: {"response": str, "tokens_used": int, "latency_ms": int}
            
        Raises:
            LLMError: Se Gemini falhar após retries
        """
        prompt = self.prompt_templates.format_response_prompt(
            user_message=message_text,
            intent=intent,
            context=context,
            maturity_score=conversation.lead.maturity_score if conversation.lead else 0,
            lead_status=conversation.lead_status.value,
            last_interaction="Agora"
        )
        
        response_data = self.gemini_client.generate_response(prompt)
        
        logger.info(f"✓ Resposta gerada ({response_data['tokens_used']} tokens)")
        
        return response_data

    async def _update_maturity_score(
        self,
        session: Any,
        conversation: Conversation,
        message: str,
        intent: str
    ) -> int:
        """
        Atualizar score de maturidade do lead baseado em engajamento e intenção.
        
        Scoring inteligente implementado (Card 085):
        - Considera engajamento do lead
        - Pondera dados fornecidos
        - Analisa intenção detectada
        
        Returns:
            int: Novo score de maturidade (0-100)
        """
        try:
            current_score = conversation.lead.maturity_score if conversation.lead else 0
            
            score_delta = {
                "INTERESSE_PRODUTO": 10,
                "ORCAMENTO": 15,
                "AGENDAMENTO": 20,
                "CONFIRMACAO": 25,
                "DUVIDA_TECNICA": 5,
                "INFORMACAO": 3,
                "SAUDACAO": 1,
                "OUTRO": 0,
            }.get(intent, 0)
            
            new_score = min(100, current_score + score_delta)
            
            if conversation.lead:
                lead_repo = LeadRepository(session)
                conversation.lead.maturity_score = new_score
                lead_repo.update(conversation.lead)
                session.flush()
            
            logger.info(
                f"✓ Score atualizado (lead_id={conversation.lead_id}, "
                f"{current_score} → {new_score}, delta={score_delta})"
            )
            
            return new_score
            
        except DatabaseError:
            raise
        except Exception as e:
            logger.warning(f"⚠️ Falha ao atualizar score: {e}")
            raise DatabaseError(f"Failed to update maturity score: {e}")

    async def _save_to_chroma(
        self,
        conversation_id: str,
        text: str,
        metadata: dict[str, Any]
    ) -> None:
        """
        Persistir par de mensagens (User/Bot) no ChromaDB para contexto futuro.
        """
        try:
            self.chroma_client.add_conversation(
                conversation_id=conversation_id,
                text=text,
                metadata=metadata
            )
            logger.info(f"✓ Contexto salvo no ChromaDB (conv_id={conversation_id})")
        except VectorDBError:
            raise
        except Exception as e:
            logger.warning(f"⚠️ Falha ao salvar no ChromaDB: {e}")
            raise VectorDBError(f"Failed to save to ChromaDB: {e}")

    async def _send_response_via_waha(
        self,
        chat_id: str,
        text: str,
        session: str
    ) -> bool:
        """
        Enviar mensagem de texto via WAHA WhatsApp API.
        
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            self.waha_client.send_text_message(
                session=session,
                chat_id=chat_id,
                text=text
            )
            logger.info(f"✓ Resposta enviada via WAHA (chat_id={chat_id})")
            return True
        except WAHAError:
            raise
        except Exception as e:
            logger.error(f"✗ Falha ao enviar via WAHA: {e}")
            raise WAHAError(f"Failed to send message: {e}", original_error=e)

    async def _register_interaction(
        self,
        session: Any,
        lead_id: Optional[str],
        interaction_type: str,
        notes: str
    ) -> None:
        """
        Registrar interação no histórico do lead para análise de engajamento.
        """
        if not lead_id:
            return
        
        try:
            repo = LeadInteractionRepository(session)
            
            type_map = {
                "INTERESSE_PRODUTO": InteractionType.MESSAGE,
                "ORCAMENTO": InteractionType.MEETING,
                "AGENDAMENTO": InteractionType.MEETING,
                "RECLAMACAO": InteractionType.CALL,
            }
            
            interaction = LeadInteraction(
                lead_id=lead_id,
                interaction_type=type_map.get(interaction_type, InteractionType.MESSAGE),
                notes=notes,
                timestamp=datetime.now(UTC),
            )
            repo.create(interaction)
            session.flush()
            
            logger.info(f"✓ Interação registrada (lead_id={lead_id})")
            
        except DatabaseError:
            raise
        except Exception as e:
            logger.warning(f"⚠️ Falha ao registrar interação: {e}")
            raise DatabaseError(f"Failed to register interaction: {e}")

    async def _check_escalation_needed(
        self,
        conversation: Conversation,
        intent: str,
        message: str,
        score: int,
    ) -> bool:
        """
        Verifica se precisa escalar para humano.
        
        Critérios de escalação:
        1. Score >= 85 (lead muito maduro)
        2. 3 ou mais intents OUTRO consecutivos (bot confuso)
        3. Cliente pede explicitamente falar com humano
        4. Múltiplas detecções de baixa confiança
        
        Args:
            conversation: Conversa atual
            intent: Intenção detectada
            message: Mensagem do cliente
            score: Score de maturidade atual
            
        Returns:
            bool: True se deve escalar
        """
        # Critério 1: Score alto (lead pronto)
        if score >= 85:
            logger.info(
                f"✓ Escalação necessária: score alto ({score}) - conv={conversation.id}"
            )
            return True
        
        # Critério 2: Cliente pede explicitamente humano
        human_keywords = [
            "falar com alguém",
            "atendente",
            "pessoa de verdade",
            "humano",
            "gerente",
            "supervisor",
        ]
        
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in human_keywords):
            logger.info(
                f"✓ Escalação necessária: cliente pediu humano - conv={conversation.id}"
            )
            return True
        
        # Critério 3: Bot confuso (intent OUTRO múltiplas vezes)
        # TODO: Implementar contador de OUTRO consecutivos
        # Por ora, apenas detectamos se intent é OUTRO com frequência
        if intent == "OUTRO":
            # Na produção, verificaríamos histórico no ChromaDB
            # Para v1, apenas logamos
            logger.info(
                f"⚠️ Intent OUTRO detectado - pode precisar escalação - conv={conversation.id}"
            )
        
        return False

    async def _log_llm_interaction(
        self,
        session: Any,
        conversation_id: str,
        prompt: str,
        response: str,
        tokens: int,
        latency_ms: int
    ) -> None:
        """
        Registrar interação com LLM para auditoria e análise de custos.
        """
        try:
            repo = LLMInteractionRepository(session)
            
            interaction = LLMInteraction(
                conversation_id=conversation_id,
                prompt_text=prompt,
                response_text=response,
                tokens_used=tokens,
                latency_ms=latency_ms,
                timestamp=datetime.now(UTC),
            )
            repo.create(interaction)
            session.flush()
            
            logger.info(f"✓ LLM interaction logged (conv_id={conversation_id})")
            
        except DatabaseError:
            raise
        except Exception as e:
            logger.warning(f"⚠️ Falha ao logar LLM interaction: {e}")
            raise DatabaseError(f"Failed to log LLM interaction: {e}")

    async def _generate_fallback_response(self, error: str) -> str:
        """
        Gerar resposta de fallback amigável quando ocorre erro no processamento.
        
        Returns:
            str: Mensagem de fallback (template ou do Gemini)
        """
        try:
            prompt = self.prompt_templates.format_fallback_prompt(
                situation="Erro ao processar mensagem",
                error=error
            )
            
            response = self.gemini_client.generate_response(prompt, max_retries=1)
            return response["response"]
            
        except LLMError:
            return (
                "Desculpe, estou com dificuldades técnicas no momento. "
                "Um atendente humano entrará em contato em breve."
            )


# Singleton global
_orchestrator: Optional[ConversationOrchestrator] = None


def get_conversation_orchestrator() -> ConversationOrchestrator:
    """
    Obter instância singleton do orchestrador.
    
    Returns:
        ConversationOrchestrator singleton
    """
    global _orchestrator
    
    if _orchestrator is None:
        _orchestrator = ConversationOrchestrator()
        logger.info("🎯 ConversationOrchestrator inicializado como singleton")
    
    return _orchestrator
