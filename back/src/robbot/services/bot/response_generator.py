"""
ResponseGenerator - Generates AI responses using LLM and playbook system.

Responsibilities:
- Generate contextual responses using Gemini API
- Apply SPIN selling methodology
- Select and apply playbooks
- Format responses for WhatsApp
"""

import logging
from typing import Any

from robbot.config.prompt_loader import PromptLoader
from robbot.core.custom_exceptions import LLMError
from robbot.core.interfaces import LLMProvider
from robbot.domain.shared.enums import IntentType
from robbot.services.ai.context_service import ContextService

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Generate AI responses based on conversation context and intent.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        prompt_loader: PromptLoader,
        context_service: ContextService,
    ):
        """
        Initialize response generator with dependencies.
        """
        self.llm = llm_provider
        self.prompt_loader = prompt_loader
        self.context_service = context_service

    async def generate_response(
        self,
        user_message: str,
        context: str,
        detected_intent: IntentType,
        maturity_score: int,
        clinic_info: dict[str, Any] | None = None,
    ) -> str:
        """
        Generate response for user message based on SPIN selling methodology.
        """
        try:
            # Step 1: Try to match and apply relevant context
            context_response = await self._try_context_response(
                user_message,
                detected_intent,
                clinic_info,
            )

            if context_response:
                logger.info("[INFO] Using context response for intent: %s", detected_intent)
                return context_response

            # Step 2: Generate contextual response with Gemini
            response = await self._generate_contextual_response(
                user_message=user_message,
                context=context,
                detected_intent=detected_intent,
                maturity_score=maturity_score,
                clinic_info=clinic_info,
            )

            logger.info("[SUCCESS] Response generated for intent: %s", detected_intent)

            return response

        except LLMError:
            raise
        except Exception as e:
            logger.error("[ERROR] Failed to generate response: %s", e)
            raise LLMError(f"Response generation failed: {e}") from e

    async def _try_context_response(
        self,
        user_message: str,
        detected_intent: IntentType,
        clinic_info: dict[str, Any] | None,
    ) -> str | None:
        """
        Try to retrieve context response for detected intent.
        """
        try:
            # Search for relevant contexts
            contexts = self.context_service.search_contexts(
                query=user_message,
            )

            if not contexts:
                return None

            # Get first matching context
            context_match = contexts[0]

            # Get context items
            items = self.context_service.get_context_items_with_details(
                context_id=context_match.context_id,
            )

            if not items:
                return None

            # Get first item content
            item = items[0]
            response = item.get("content_text") or item.get("content_caption") or ""

            if response and clinic_info:
                # Personalize with clinic info
                response = response.format(
                    clinic_name=clinic_info.get("name", "nossa clínica"),
                    **clinic_info,
                )

            return response

        except Exception as e:
            logger.warning("[WARNING] Failed to get context response: %s", e)
            return None

    async def _generate_contextual_response(
        self,
        user_message: str,
        context: str,
        detected_intent: IntentType,
        maturity_score: int,
        clinic_info: dict[str, Any] | None,
    ) -> str:
        """
        Generate contextual response using Gemini with SPIN methodology.

        Args:
            user_message: User input
            context: Conversation history
            detected_intent: Intent type
            maturity_score: Lead maturity (0-100)
            clinic_info: Clinic information for personalization

        Returns:
            Generated response

        Raises:
            LLMError: If Gemini call fails
        """
        try:
            # Get appropriate prompt based on maturity score and intent
            prompt = self._build_response_prompt(
                user_message=user_message,
                context=context,
                detected_intent=detected_intent,
                maturity_score=maturity_score,
            )

            # System instructions for SPIN selling methodology
            system = self._get_spin_system_prompt(maturity_score)

            # Call LLM
            response = await self.llm.generate_response(
                prompt=prompt,
                system=system,
                temperature=0.7,
                max_tokens=500,
            )

            # Extract response text
            text = response.get("text", "")

            if not text:
                raise LLMError("Empty response from LLM")

            # Personalize with clinic info
            if clinic_info:
                text = self._personalize_response(text, clinic_info)

            return text

        except Exception as e:
            logger.error("[ERROR] Failed to generate contextual response: %s", e)
            raise LLMError(f"Gemini response generation failed: {e}") from e

    @staticmethod
    def _build_response_prompt(
        user_message: str,
        context: str,
        detected_intent: IntentType,
        maturity_score: int,
    ) -> str:
        """
        Build prompt for response generation.

        Args:
            user_message: User input
            context: Conversation history
            detected_intent: Intent type
            maturity_score: Lead maturity score

        Returns:
            Formatted prompt for LLM
        """
        spin_phase = ResponseGenerator._get_spin_phase(maturity_score)

        prompt = f"""
You are a healthcare clinic assistant using SPIN selling methodology.
Current SPIN Phase: {spin_phase}
Lead Maturity Score: {maturity_score}/100
Detected Intent: {detected_intent}

Previous Context:
{context}

User Message: {user_message}

Generate a natural, empathetic response that advances the conversation
through the appropriate SPIN selling phase. Be conversational and helpful.
"""

        return prompt.strip()

    @staticmethod
    def _get_spin_phase(score: int) -> str:
        """
        Determine SPIN phase based on maturity score.

        Args:
            score: Maturity score (0-100)

        Returns:
            SPIN phase name
        """
        if score < 25:
            return "SITUATION (Gathering Information)"
        elif score < 40:
            return "PROBLEM (Identifying Pain Points)"
        elif score < 70:
            return "IMPLICATION (Exploring Consequences)"
        else:
            return "NEED-PAYOFF (Presenting Benefits & Scheduling)"

    @staticmethod
    def _get_spin_system_prompt(maturity_score: int) -> str:
        """
        Get system prompt for SPIN selling approach.

        Args:
            maturity_score: Lead maturity score

        Returns:
            System instruction prompt
        """
        if maturity_score < 25:
            return (
                "You are in SITUATION phase. Ask clarifying questions to understand "
                "the customer's background, needs, and situation without being pushy."
            )
        elif maturity_score < 40:
            return (
                "You are in PROBLEM phase. Listen to and identify the customer's problems "
                "and difficulties. Ask about their concerns and pain points."
            )
        elif maturity_score < 70:
            return (
                "You are in IMPLICATION phase. Help the customer explore the consequences "
                "and implications of their problems. Develop their sense of need."
            )
        else:
            return (
                "You are in NEED-PAYOFF phase. Help the customer identify the benefits "
                "of solving their problem. Propose scheduling an appointment."
            )

    @staticmethod
    def _personalize_response(
        response: str,
        clinic_info: dict[str, Any],
    ) -> str:
        """
        Personalize response with clinic information.

        Args:
            response: Generated response
            clinic_info: Clinic details

        Returns:
            Personalized response
        """
        replacements = {
            "{clinic_name}": clinic_info.get("name", "nossa clínica"),
            "{doctor_name}": clinic_info.get("doctor_name", "nosso médico"),
            "{phone}": clinic_info.get("phone", "nosso contato"),
            "{location}": clinic_info.get("location", "nossa clínica"),
        }

        for placeholder, value in replacements.items():
            response = response.replace(placeholder, value)

        return response

