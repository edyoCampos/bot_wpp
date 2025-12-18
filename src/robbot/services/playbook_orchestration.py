"""
Playbook Orchestrator Integration - Adds function calling support to ConversationOrchestrator.

This module extends the orchestrator to:
1. Register playbook tools with Gemini
2. Handle function calling during conversation
3. Execute tools and return results to LLM
4. Integrate transcription for voice messages
"""

import json
import logging
from typing import Any, Dict, List, Optional

from robbot.services.playbook_tools import (
    PLAYBOOK_TOOLS_DECLARATIONS,
    execute_playbook_tool,
)
from robbot.services.transcription_service import TranscriptionService
from robbot.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class PlaybookOrchestrationMixin:
    """
    Mixin to add playbook capabilities to ConversationOrchestrator.
    
    This provides:
    - Function calling tool registration
    - Tool execution handling
    - Voice message transcription
    """
    
    def _get_playbook_tools(self) -> List[Dict[str, Any]]:
        """
        Get playbook tool declarations for Gemini Function Calling.
        
        Returns:
            List of tool declaration dicts compatible with Gemini API
        """
        return PLAYBOOK_TOOLS_DECLARATIONS
    
    async def _generate_response_with_tools(
        self,
        session: Any,
        message_text: str,
        intent: str,
        context: str,
        conversation: Any,
        max_tool_calls: int = 5
    ) -> Dict[str, Any]:
        """
        Generate response using Gemini with playbook tools enabled.
        
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
            conversation: Conversation entity
            max_tool_calls: Max iterations to prevent infinite loops
        
        Returns:
            Dict with response and metadata
        """
        try:
            # Build prompt with playbook instructions
            prompt = self._build_playbook_aware_prompt(
                message_text, intent, context, conversation
            )
            
            # Get tool declarations (currently passed to gemini_client at initialization)
            # Tools are registered in __init__ of ConversationOrchestrator
            # Future: Pass tools dynamically to generate_response()
            
            # Initialize conversation history for multi-turn tool calling
            messages = [{"role": "user", "content": prompt}]
            
            for iteration in range(max_tool_calls):
                logger.info(f"Function calling iteration {iteration + 1}/{max_tool_calls}")
                
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
                    logger.info("✓ Gemini generated final text response")
                    return response
                
                # Execute tool
                tool_name = function_call["name"]
                tool_args = function_call["args"]
                
                logger.info(f"🔧 Executing tool: {tool_name} with args {tool_args}")
                
                tool_result = execute_playbook_tool(session, tool_name, tool_args)
                
                # Add tool result to conversation history
                messages.append({
                    "role": "function",
                    "name": tool_name,
                    "content": json.dumps(tool_result)
                })
                
                # Continue with updated context
                prompt = self._append_tool_result_to_prompt(prompt, tool_name, tool_result)
            
            # Max iterations reached
            logger.warning(f"⚠️ Max tool calls ({max_tool_calls}) reached")
            return self.gemini_client.generate_response(
                "Resuma a conversa e responda ao usuário sem usar mais ferramentas."
            )
            
        except Exception as e:
            logger.error(f"Error in function calling loop: {e}")
            raise ExternalServiceError(f"Function calling failed: {e}")
    
    def _build_playbook_aware_prompt(
        self,
        message_text: str,
        intent: str,
        context: str,
        conversation: Any
    ) -> str:
        """
        Build prompt with playbook usage instructions.
        
        Teaches LLM when and how to use playbook tools.
        """
        base_prompt = self.prompt_templates.format_response_prompt(
            user_message=message_text,
            intent=intent,
            context=context,
            maturity_score=conversation.lead.maturity_score if conversation.lead else 0,
            lead_status=conversation.lead_status.value,
            last_interaction="Agora"
        )
        
        playbook_instructions = """

FERRAMENTAS DE PLAYBOOK DISPONÍVEIS:

Você tem acesso a 3 ferramentas para usar playbooks de mensagens prontas:

1. **search_playbooks(query)**: Busca playbooks relevantes semanticamente
   - Use quando cliente mencionar tópicos específicos (emagrecimento, saúde, hormônios, metabolismo, etc.)
   - Exemplos de queries: "emagrecimento saudável médico", "tratamento hormonal perda peso"
   - Retorna lista de playbooks com scores de relevância

2. **get_playbook_steps(playbook_id)**: Obtém passos detalhados de um playbook
   - Use após search_playbooks para ver conteúdo completo
   - Retorna lista ordenada de mensagens (texto, imagem, vídeo, PDF, etc.)

3. **send_playbook_message(message_id, conversation_id, custom_intro)**: Envia mensagem do playbook
   - Use para enviar conteúdo relevante ao cliente
   - SEMPRE adicione custom_intro para contextualizar (ex: "Aqui está o material sobre emagrecimento saudável:")
   - Mantém fluxo natural da conversa

QUANDO USAR PLAYBOOKS:
- Cliente pergunta sobre tratamentos/programas de saúde específicos (emagrecimento, hormônios, metabolismo)
- Cliente pede informações detalhadas sobre abordagem médica, métodos, acompanhamento
- Cliente quer agendar consulta de avaliação (enviar playbook de agendamento)
- Você identifica oportunidade de compartilhar material educativo sobre saúde

IMPORTANTE:
- Use playbooks para complementar sua resposta, não substituir
- Sempre contextualize com custom_intro antes de enviar mensagens
- Priorize relevância sobre quantidade de mensagens
"""
        
        return base_prompt + playbook_instructions
    
    def _extract_function_call(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
                return {
                    "name": response["function_call"]["name"],
                    "args": response["function_call"]["args"]
                }
            
            # Check for nested structure in candidates
            if "candidates" in response:
                candidates = response.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for part in parts:
                        if "function_call" in part:
                            return {
                                "name": part["function_call"]["name"],
                                "args": part["function_call"]["args"]
                            }
        except (AttributeError, IndexError, KeyError, TypeError) as e:
            logger.debug(f"No function call in response: {e}")
        
        # No function call found - return None for regular text response
        return None
    
    def _append_tool_result_to_prompt(
        self,
        prompt: str,
        tool_name: str,
        tool_result: Any
    ) -> str:
        """Append tool result to prompt for next iteration."""
        result_json = json.dumps(tool_result, ensure_ascii=False, indent=2)
        return f"{prompt}\n\n[RESULTADO DA FERRAMENTA {tool_name}]:\n{result_json}\n"
    
    async def _transcribe_voice_message(
        self,
        audio_url: str
    ) -> Optional[str]:
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
            
            logger.info(f"✓ Voice message transcribed: {len(text)} chars")
            return text
            
        except ExternalServiceError as e:
            logger.error(f"Error transcribing voice message: {e}")
            return None
        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Unexpected error transcribing voice message: {e}", exc_info=True)
            return None
    
    async def _process_media_message(
        self,
        message_type: str,
        media_url: Optional[str],
        caption: Optional[str]
    ) -> str:
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

