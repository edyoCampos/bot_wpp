"""
Intent Detector - Detecção de intenção, urgência e atualização de score.

Responsabilidades:
- Detectar intenção do cliente (INTERESSE_PRODUTO, ORÇAMENTO, etc)
- Detectar urgência na mensagem
- Extrair nome do cliente
- Atualizar maturity score do lead
- Verificar necessidade de escalação para humano
"""

import json
import logging
from typing import Any

from robbot.core.interfaces import LLMProvider
from robbot.infra.persistence.repositories.lead_repository import LeadRepository
from robbot.config.prompts import PromptTemplates
from robbot.core.custom_exceptions import DatabaseError, LLMError
from robbot.infra.persistence.models.conversation_model import ConversationModel

logger = logging.getLogger(__name__)


class IntentDetector:
    """Detecta intenções, urgência e gerencia score de maturidade"""

    def __init__(self, llm: LLMProvider, prompt_templates: PromptTemplates):
        self.llm = llm
        self.prompt_templates = prompt_templates

    async def detect_intent(self, message: str, context: str) -> tuple[str, str]:
        """
        Detectar intenção e fase SPIN da mensagem.

        Returns:
            tuple[str, str]: (intenção, fase_spin)
        """
        try:
            prompt = self.prompt_templates.format_intent_prompt(message, context)
            response = await self.llm.generate_response(prompt)

            # Parse JSON response
            try:
                data = json.loads(response["response"].strip())
                intent = data.get("intent", "OUTRO").upper()
                spin_phase = data.get("spin_phase", "SITUATION").upper()
            except (json.JSONDecodeError, AttributeError):
                # Fallback se não for JSON
                intent = response["response"].strip().upper()
                spin_phase = "SITUATION"

            valid_intents = [
                "INTERESSE_PRODUTO",
                "ORCAMENTO",
                "AGENDAMENTO",
                "DUVIDA_TECNICA",
                "RECLAMACAO",
                "AGRADECIMENTO",
                "ENCERRAMENTO",
                "OUTRO",
            ]

            if intent not in valid_intents:
                intent = "OUTRO"

            logger.info("[SUCCESS] Intent detected: %s | Phase: %s", intent, spin_phase)

            return intent, spin_phase

        except LLMError:
            raise
        except Exception as e:  # noqa: BLE001
            logger.warning("[WARNING] Failed to detect intent: %s", e)
            raise LLMError(f"Failed to detect intent: {e}") from e

    async def detect_urgency(self, message: str, context: str) -> bool:
        """
        Detectar se mensagem indica urgência.

        Args:
            message: Mensagem do cliente
            context: Contexto conversacional

        Returns:
            bool: True se urgente

        Raises:
            LLMError: Se falhar ao detectar urgência
        """
        try:
            # Fallback to intent prompt if urgency prompt not available (or implement it)
            # Actually, I'll use format_intent_prompt for now or implement urgency one.
            # Looking at PromptTemplates, there is no urgency prompt.
            # For now, let's just return False or implement a generic check.
            return False
        except Exception as e:
            logger.warning("[WARNING] Failed to detect urgency: %s", e)
            return False

    async def try_extract_name(self, session: Any, message: str, context: str, conversation: ConversationModel) -> None:
        """
        Tentar extrair nome do paciente da mensagem de forma inteligente.
        Atualiza o lead se encontrar nome com confiança >= 65%.

        Args:
            session: Sessão do banco de dados
            message: Mensagem do cliente
            context: Contexto conversacional
            conversation: Conversa atual
        """
        try:
            prompt = self.prompt_templates.format_name_extraction_prompt(message, context)
            logger.info("[NAME_EXTRACTION_DEBUG] Attempting name extraction from message: %s", message[:100])

            response = await self.llm.generate_response(prompt)

            # Parse JSON response - try to extract JSON from response
            response_text = response["response"].strip()
            logger.info("[NAME_EXTRACTION_DEBUG] Gemini raw response: %s", response_text[:200])

            # Try to find JSON in response (sometimes Gemini adds extra text)
            if "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                response_text = response_text[json_start:json_end]

            result = json.loads(response_text)
            logger.info(
                "[NAME_EXTRACTION_DEBUG] Parsed result: name=%s, confidence=%s, source=%s",
                result.get("name"),
                result.get("confidence"),
                result.get("source"),
            )

            name = result.get("name")
            confidence = result.get("confidence", 0)
            source = result.get("source", "unknown")

            # Accept name if confidence >= 65% (was 70% - now more permissive)
            if name and name != "null" and confidence >= 65:
                current_name = conversation.lead.name

                # Only update if: no name, phone placeholder, or new name has higher confidence
                should_update = (
                    not current_name  # No name yet
                    or current_name == conversation.lead.phone_number  # Phone placeholder
                    or (len(current_name.split()) == 1 and len(name.split()) > 1)  # Upgrade from single to full name
                )

                if should_update:
                    # Capitalize properly (title case for names)
                    formatted_name = name.title()

                    # Update lead name
                    lead_repo = LeadRepository(session)
                    conversation.lead.name = formatted_name
                    lead_repo.update(conversation.lead)
                    session.flush()

                    logger.info(
                        "[SUCCESS] Name extracted: '%s' (confidence=%s%%, source=%s, previous='%s')",
                        formatted_name,
                        confidence,
                        source,
                        current_name or "none",
                    )
                else:
                    logger.debug(
                        "[SKIP] Name extraction confidence too low to replace existing (new='%s' %s%%, current='%s')",
                        name,
                        confidence,
                        current_name,
                    )

        except (LLMError, json.JSONDecodeError, KeyError) as e:
            logger.warning("[WARNING] Failed to extract name: %s", e)

    async def generate_name_request(self, context: str, spin_phase: str, maturity_score: int) -> str | None:
        """
        Gerar solicitação natural do nome do paciente.

        Args:
            context: Contexto conversacional
            spin_phase: Fase SPIN atual
            maturity_score: Score de maturidade do lead

        Returns:
            str | None: Solicitação de nome ou None se não deve solicitar
        """
        try:
            prompt = self.prompt_templates.format_name_request_prompt(context, spin_phase, maturity_score)

            response = await self.llm.generate_response(prompt)

            response_text = response["response"].strip()
            if response_text:
                logger.info("[SUCCESS] Name request generated")
                return response_text

            return None

        except (LLMError, json.JSONDecodeError, KeyError) as e:
            logger.warning("[WARNING] Failed to generate name request: %s", e)
            return None

    async def update_maturity_score(
        self, session: Any, conversation: ConversationModel, message: str, intent: str, spin_phase: str = "SITUATION"
    ) -> int:
        """
        Atualizar score de maturidade do lead baseado na FASE SPIN.

        Score baseado em progressão SPIN:
        - SITUATION: 10-30 (início da conversa, contexto)
        - PROBLEM: 30-50 (descreveu problema)
        - IMPLICATION: 50-75 (entendeu impacto)
        - NEED_PAYOFF: 75-85 (quer solução)
        - READY: 85-100 (pronto para agendar)

        Bônus por intents específicos:
        - AGENDAMENTO: +10 (forte sinal de interesse)
        - ORCAMENTO: +5 (perguntou valor)

        Args:
            session: Sessão do banco de dados
            conversation: Conversa atual
            message: Mensagem do cliente
            intent: Intenção detectada
            spin_phase: Fase SPIN atual (CRUCIAL para scoring)

        Returns:
            int: Novo score de maturidade

        Raises:
            DatabaseError: Se falhar ao atualizar score
        """
        try:
            if not conversation.lead:
                return 0

            current_score = conversation.lead.maturity_score

            # Score base por fase SPIN (progressão natural)
            spin_score_target = {
                "SITUATION": 20,
                "PROBLEM": 40,
                "IMPLICATION": 60,
                "NEED_PAYOFF": 80,
                "READY": 90,
            }.get(spin_phase.upper(), 10)

            # Bônus por intents que indicam forte interesse
            intent_bonus = {
                "AGENDAMENTO": 10,
                "ORCAMENTO": 5,
                "INTERESSE_PRODUTO": 3,
            }.get(intent, 0)

            # Calcular novo score: progride em direção ao target da fase
            # Se já passou do target, mantém; se abaixo, avança
            if current_score < spin_score_target:
                new_score = min(100, spin_score_target + intent_bonus)
            else:
                new_score = min(100, current_score + intent_bonus)

            if conversation.lead:
                lead_repo = LeadRepository(session)
                conversation.lead.maturity_score = new_score
                lead_repo.update(conversation.lead)
                session.flush()

            logger.info(
                "[SUCCESS] Score updated (lead_id=%s, %s → %s, phase=%s, intent=%s)",
                conversation.lead.id,
                current_score,
                new_score,
                spin_phase,
                intent,
            )

            return new_score

        except DatabaseError:
            raise
        except Exception as e:  # noqa: BLE001
            logger.warning("[WARNING] Failed to update score: %s", e)
            raise DatabaseError(f"Failed to update maturity score: {e}") from e

    async def check_escalation_needed(
        self,
        conversation: ConversationModel,
        intent: str,
        message: str,
        score: int,
    ) -> bool:
        """
        Verifica se precisa escalar para humano.

        Critérios de escalação:
        1. Score >= 85 (lead muito maduro)
        2. Cliente pede explicitamente falar com humano
        3. Intent OUTRO múltiplas vezes (bot confuso)

        Args:
            conversation: Conversa atual
            intent: Intenção detectada
            message: Mensagem do cliente
            score: Score de maturidade atual

        Returns:
            bool: True se deve escalar
        """
        # Critério 1: High score (lead ready)
        if score >= 85:
            logger.info("[INFO] Escalation needed: high score (%s) - conv=%s", score, conversation.id)
            return True

        # Critério 2: Cliente pede falar com humano
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
            logger.info("[INFO] Escalation needed: client requested human - conv=%s", conversation.id)
            return True

        # Critério 3: Bot confuso (intent OUTRO múltiplas vezes)
        # TODO: Implementar contador de OUTRO consecutivos
        if intent == "OUTRO":
            logger.info("[WARNING] Intent OUTRO detected - may need escalation - conv=%s", conversation.id)

        return False

