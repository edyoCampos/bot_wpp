"""
Context Orchestrator Integration - Adds function calling support to ConversationOrchestrator.

This module extends the orchestrator to:
1. Register context tools with LLM
2. Handle function calling during conversation
3. Execute tools and return results to LLM
4. Integrate transcription for voice messages
"""

import json
import logging
from typing import Any

from robbot.core.custom_exceptions import ExternalServiceError, VectorDBError
from robbot.services.ai.context_tools import (
    CONTEXT_TOOLS_DECLARATIONS,
    execute_context_tool,
)
from robbot.services.communication.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class ContextOrchestrationMixin:
    """
    Mixin to add context capabilities to ConversationOrchestrator.

    This provides:
    - Function calling tool registration
    - Tool execution handling
    - Voice message transcription
    """

    def _get_context_tools(self) -> list[dict[str, Any]]:
        """
        Get context tool declarations for LLM Function Calling.
        """
        return CONTEXT_TOOLS_DECLARATIONS

    async def _generate_response_with_tools(
        self, session: Any, message_text: str, intent: str, context: str, conversation: Any, max_tool_calls: int = 5
    ) -> dict[str, Any]:
        """
        Generate response using Gemini with context tools enabled.

        This implements a function calling loop:
        1. Send prompt + tools to Gemini
        2. If Gemini requests tool call, execute it
        3. Return tool result to Gemini
        4. Repeat until Gemini generates final text response

        Args:
            session: Database session
            message_text: User message
            intent: Detected intent
            context: Conversation context
            conversation: ConversationModel entity
            max_tool_calls: Max iterations to prevent infinite loops

        Returns:
            Dict with response and metadata
        """
        try:
            # Build prompt with context instructions
            prompt = self._build_context_aware_prompt(message_text, intent, context, conversation)

            # Get tool declarations (currently passed to gemini_client at initialization)
            # Tools are registered in __init__ of ConversationOrchestrator
            # Future: Pass tools dynamically to generate_response()

            # Initialize conversation history for multi-turn tool calling
            messages = [{"role": "user", "content": prompt}]

            for iteration in range(max_tool_calls):
                logger.info("[INFO] Function calling iteration %s/%s", iteration + 1, max_tool_calls)

                # Generate response with tools
                # Note: This is a simplified version
                # Full implementation would use google.generativeai with tools parameter
                response = self.gemini_client.generate_response(prompt)

                # Check if response contains function call
                # In real implementation, check response.function_call
                # Note: Currently returns None (stub implementation - function calling not yet integrated)
                function_call = self._extract_function_call(response)
                assert function_call is None or isinstance(function_call, dict), "Invalid function_call type"

                if function_call is None:
                    # Final text response (no function call detected)
                    logger.info("[SUCCESS] Gemini generated final text response")
                    return response

                # Execute tool
                tool_name = function_call["name"]
                tool_args = function_call["args"]

                logger.info("[INFO] Executing tool: %s with args %s", tool_name, tool_args)

                tool_result = execute_context_tool(session, tool_name, tool_args)

                # Add tool result to conversation history
                messages.append({"role": "function", "name": tool_name, "content": json.dumps(tool_result)})

                # Continue with updated context
                prompt = self._append_tool_result_to_prompt(prompt, tool_name, tool_result)

            # Max iterations reached
            logger.warning("[WARNING] Max tool calls (%s) reached", max_tool_calls)
            return self.gemini_client.generate_response(
                "Resuma a conversa e responda ao usuário sem usar mais ferramentas."
            )

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Error in function calling loop: %s", e)
            raise VectorDBError(f"Function calling failed: {e}", original_error=e) from e

    def _build_context_aware_prompt(self, message_text: str, intent: str, context: str, conversation: Any) -> str:
        """
        Build prompt with context usage instructions.

        Teaches LLM when and how to use context tools.
        """
        base_prompt = self.prompt_templates.format_response_prompt(
            user_message=message_text,
            intent=intent,
            context=context,
            lead_name=conversation.lead.name if conversation.lead else None,
            maturity_score=conversation.lead.maturity_score if conversation.lead else 0,
            lead_status=conversation.lead.status.value if conversation.lead else "NEW",
            last_interaction="Agora",
        )

        context_instructions = """

FERRAMENTAS DE CONTEXTO DISPONÍVEIS:

Você tem acesso a 3 ferramentas para usar conteúdos prontos (contextos):

1. **search_contexts(query)**: Busca contextos relevantes semanticamente
   - Use quando cliente mencionar tópicos específicos (especialidades, tratamentos, dúvidas comuns, etc.)
   - Retorna lista de contextos com scores de relevância

2. **get_context_items(context_id)**: Obtém itens detalhados de um contexto
   - Use após search_contexts para ver conteúdo completo
   - Retorna lista ordenada de materiais (texto, imagem, vídeo, PDF, etc.)

3. **send_context_content(content_id, conversation_id, custom_intro)**: Envia conteúdo do contexto
   - Use para enviar material relevante ao cliente
   - SEMPRE adicione custom_intro para contextualizar (ex: "Aqui está o material sobre nosso método:")

QUANDO USAR CONTEXTOS:
- Cliente pergunta sobre tratamentos ou programas específicos
- Cliente pede informações detalhadas sobre a clínica ou métodos
- Cliente quer agendar consulta (enviar contexto de agendamento)
- Você identifica oportunidade de compartilhar material informativo

IMPORTANTE:
- Use contextos para complementar sua resposta, não substituir
- Sempre contextualize com custom_intro antes de enviar
- Priorize relevância sobre quantidade
"""

        return base_prompt + context_instructions

    def _extract_function_call(self, response: dict[str, Any]) -> dict[str, Any] | None:
        """
        Extract function call from Gemini response.

        Returns:
            Dict with function name and args, or None if no function call

        Note:
            IMPLEMENTATION PENDING - Gemini Function Calling integration.

            When implemented, should parse:
            - response.candidates[0].content.parts[0].function_call.name
            - response.candidates[0].content.parts[0].function_call.args

            See: https://ai.google.dev/gemini-api/docs/function-calling
        """
        # Check if response has function_call structure
        # This is compatible with google.generativeai response format
        try:
            if isinstance(response, dict) and "function_call" in response:
                return {"name": response["function_call"]["name"], "args": response["function_call"]["args"]}

            # Check for nested structure in candidates
            if "candidates" in response:
                candidates = response.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for part in parts:
                        if "function_call" in part:
                            return {"name": part["function_call"]["name"], "args": part["function_call"]["args"]}
        except (AttributeError, IndexError, KeyError, TypeError) as e:
            logger.debug("[DEBUG] No function call in response: %s", e)

        # No function call found - return None for regular text response
        return None

    def _append_tool_result_to_prompt(self, prompt: str, tool_name: str, tool_result: Any) -> str:
        """Append tool result to prompt for next iteration."""
        result_json = json.dumps(tool_result, ensure_ascii=False, indent=2)
        return f"{prompt}\n\n[RESULTADO DA FERRAMENTA {tool_name}]:\n{result_json}\n"

    async def _transcribe_voice_message(self, audio_url: str) -> str | None:
        """
        Transcribe voice message using Whisper API.

        Args:
            audio_url: URL of audio file to transcribe

        Returns:
            Transcription text or None if failed
        """
        try:
            transcription_service = TranscriptionService()
            text = await transcription_service.transcribe_audio(audio_url, language="pt")

            logger.info("[SUCCESS] Voice message transcribed: %s chars", len(text))
            return text

        except ExternalServiceError as e:
            logger.error("[ERROR] Error transcribing voice message: %s", e)
            return None
        except (OSError, ValueError, RuntimeError) as e:
            logger.error("Unexpected error transcribing voice message: %s", e, exc_info=True)
            return None

    async def _process_media_message(self, message_type: str, media_url: str | None, caption: str | None) -> str:
        """
        Process media message (image, video, audio, document).

        For voice messages, transcribe audio.
        For other media, return caption or type description.

        Args:
            message_type: Type of media (audio, image, video, document)
            media_url: URL of media file
            caption: Optional caption

        Returns:
            Text representation of media message
        """
        if message_type == "audio" and media_url:
            # Transcribe voice message
            transcription = await self._transcribe_voice_message(media_url)
            if transcription:
                return f"[Mensagem de voz transcrita]: {transcription}"
            else:
                return "[Mensagem de voz - transcrição falhou]"

        elif message_type in ("image", "video"):
            # For images/videos, use caption if available
            if caption:
                return f"[{message_type.capitalize()}]: {caption}"
            else:
                return f"[Cliente enviou {message_type}]"

        elif message_type == "document":
            # For documents, use caption as filename
            if caption:
                return f"[Documento]: {caption}"
            else:
                return "[Cliente enviou documento]"

        else:
            return f"[Mensagem de tipo {message_type}]"

