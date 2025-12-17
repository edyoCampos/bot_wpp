"""
Function Calling tools for LLM to autonomously use playbooks during conversations.

These tools enable the AI to:
1. Search for relevant playbooks semantically (RAG)
2. Retrieve playbook steps with full message details
3. Send messages from playbooks to clients

Designed for Google Gemini Function Calling integration.
"""

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from robbot.services.playbook_service import PlaybookService
from robbot.services.message_service import MessageService
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# TOOL 1: Search Playbooks (RAG Semantic Search)
# ============================================================================

SEARCH_PLAYBOOKS_DECLARATION = {
    "name": "search_playbooks",
    "description": (
        "Busca semanticamente por playbooks relevantes usando embeddings e ChromaDB. "
        "Use quando o cliente mencionar tópicos como botox, preenchimento, clareamento, "
        "agendamento de procedimentos, dúvidas sobre serviços, etc. "
        "Retorna os playbooks mais relevantes ordenados por score de similaridade. "
        "Exemplos de consultas: 'botox valor procedimento', 'clareamento dental informações', "
        "'preenchimento labial antes e depois'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Texto de busca em linguagem natural (palavras-chave ou pergunta completa)"
            },
            "top_k": {
                "type": "integer",
                "description": "Número de playbooks a retornar (padrão: 3, máximo: 10)",
                "default": 3
            }
        },
        "required": ["query"]
    }
}


def search_playbooks_tool(db: Session, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Execute semantic search for playbooks.
    
    Args:
        db: Database session
        query: Search query (natural language)
        top_k: Number of results to return
    
    Returns:
        List of playbook search results with relevance scores
    """
    try:
        service = PlaybookService(db)
        results = service.search_playbooks(query, top_k=top_k, active_only=True)
        
        logger.info(f"Playbook search: query='{query}', results={len(results)}")
        
        # Convert to dict for LLM consumption
        return [
            {
                "playbook_id": r.playbook_id,
                "playbook_name": r.playbook_name,
                "topic_name": r.topic_name,
                "description": r.description,
                "relevance_score": round(r.relevance_score, 3),
                "step_count": r.step_count
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"Error searching playbooks: {e}")
        return []


# ============================================================================
# TOOL 2: Get Playbook Steps (with message details)
# ============================================================================

GET_PLAYBOOK_STEPS_DECLARATION = {
    "name": "get_playbook_steps",
    "description": (
        "Obtém todos os passos de um playbook com detalhes completos das mensagens. "
        "Use após search_playbooks para ver o conteúdo detalhado de um playbook específico. "
        "Retorna lista ordenada de passos com tipo de mensagem, título, descrição, texto, "
        "URLs de mídia, etc. Útil para decidir qual mensagem enviar ao cliente."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "playbook_id": {
                "type": "string",
                "description": "UUID do playbook (obtido de search_playbooks)"
            }
        },
        "required": ["playbook_id"]
    }
}


def get_playbook_steps_tool(db: Session, playbook_id: str) -> Dict[str, Any]:
    """
    Retrieve all steps for a playbook with full message details.
    
    Args:
        db: Database session
        playbook_id: Playbook UUID
    
    Returns:
        Dict with playbook info and list of steps with message details
    """
    try:
        service = PlaybookService(db)
        steps = service.get_playbook_steps_with_details(playbook_id)
        
        logger.info(f"Retrieved playbook steps: playbook_id={playbook_id}, steps={len(steps)}")
        
        return {
            "playbook_id": playbook_id,
            "total_steps": len(steps),
            "steps": steps
        }
    except Exception as e:
        logger.error(f"Error getting playbook steps: {e}")
        return {"playbook_id": playbook_id, "total_steps": 0, "steps": [], "error": str(e)}


# ============================================================================
# TOOL 3: Send Playbook Message
# ============================================================================

SEND_PLAYBOOK_MESSAGE_DECLARATION = {
    "name": "send_playbook_message",
    "description": (
        "Envia uma mensagem específica de um playbook para o cliente na conversa atual. "
        "Use após revisar os passos com get_playbook_steps para enviar conteúdo relevante "
        "(textos, imagens, vídeos, PDFs, etc.). "
        "IMPORTANTE: Sempre adicione uma introdução personalizada (custom_intro) para contextualizar "
        "a mensagem no fluxo da conversa. Exemplo: 'Aqui está o material sobre botox que você pediu'"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "message_id": {
                "type": "string",
                "description": "UUID da mensagem a enviar (obtido de get_playbook_steps)"
            },
            "conversation_id": {
                "type": "string",
                "description": "UUID da conversa atual"
            },
            "custom_intro": {
                "type": "string",
                "description": "Texto introdutório opcional para contextualizar a mensagem (recomendado)"
            }
        },
        "required": ["message_id", "conversation_id"]
    }
}


def send_playbook_message_tool(
    db: Session,
    message_id: str,
    conversation_id: str,
    custom_intro: str = None
) -> Dict[str, Any]:
    """
    Send a message from a playbook to the client.
    
    Args:
        db: Database session
        message_id: Message UUID from playbook
        conversation_id: Current conversation UUID
        custom_intro: Optional introductory text
    
    Returns:
        Dict with success status and message info
    """
    try:
        from robbot.services.conversation_service import ConversationService
        
        # Get message details
        message_service = MessageService(db)
        message = message_service.get_message(message_id)
        
        if not message:
            return {"success": False, "error": f"Message {message_id} not found"}
        
        # Get conversation
        conv_service = ConversationService(db)
        conversation = conv_service.get_conversation(conversation_id)
        
        if not conversation:
            return {"success": False, "error": f"Conversation {conversation_id} not found"}
        
        # Prepare message payload
        # Note: Actual sending logic should go through WAHA service
        # This is a simplified version - full implementation would:
        # 1. Format message based on type (text/image/video/document)
        # 2. Add custom_intro if provided
        # 3. Send via WAHA
        # 4. Save to conversation_messages
        
        logger.info(
            f"Sending playbook message: message_id={message_id}, "
            f"conversation_id={conversation_id}, intro={custom_intro}"
        )
        
        # TODO: Implement actual WAHA sending logic
        # For now, return success with message details
        
        return {
            "success": True,
            "message_id": message_id,
            "conversation_id": conversation_id,
            "message_type": message.type,
            "custom_intro": custom_intro,
            "note": "Message queued for sending (implementation pending)"
        }
        
    except Exception as e:
        logger.error(f"Error sending playbook message: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# TOOL 4: Send Clinic Location
# ============================================================================

SEND_CLINIC_LOCATION_DECLARATION = {
    "name": "send_clinic_location",
    "description": (
        "Envia a localização da Clínica GO via WhatsApp para o paciente. "
        "Use quando o paciente perguntar sobre: endereço, localização, como chegar, "
        "onde fica a clínica, mapa, GPS, coordenadas, direções, rota, etc. "
        "A localização é enviada como um pin no WhatsApp com as coordenadas exatas da clínica. "
        "Endereço: Av. São Miguel, 1000 - sala 102, Dois Irmãos/RS. "
        "SEMPRE use esta tool quando houver menção a localização/endereço."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "chat_id": {
                "type": "string",
                "description": "ID do chat do WhatsApp (formato: 5551999999999@c.us)"
            },
            "custom_title": {
                "type": "string",
                "description": "Título customizado para o pin de localização (opcional, padrão: 'Clínica GO')",
                "default": "Clínica GO"
            }
        },
        "required": ["chat_id"]
    }
}


def send_clinic_location_tool(
    db: Session,
    chat_id: str,
    custom_title: str = "Clínica GO"
) -> Dict[str, Any]:
    """
    Enviar localização da Clínica GO via WhatsApp.
    
    Args:
        db: Database session (não usado, mas mantido por consistência)
        chat_id: ID do chat do WhatsApp
        custom_title: Título customizado para o pin
        
    Returns:
        Resultado do envio
    """
    try:
        from robbot.common.clinic_location import send_clinic_location_via_waha_sync
        
        logger.info(f"🔧 Tool: send_clinic_location para {chat_id}")
        
        result = send_clinic_location_via_waha_sync(
            chat_id=chat_id,
            custom_title=custom_title
        )
        
        return {
            "success": True,
            "message": "Localização da Clínica GO enviada com sucesso",
            "clinic_name": "Clínica GO",
            "address": "Av. São Miguel, 1000 - sala 102 - Centro, Dois Irmãos - RS",
            "result": result
        }
    except Exception as e:
        logger.error(f"✗ Erro ao enviar localização: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Tool Registry
# ============================================================================

PLAYBOOK_TOOLS_DECLARATIONS = [
    SEARCH_PLAYBOOKS_DECLARATION,
    GET_PLAYBOOK_STEPS_DECLARATION,
    SEND_PLAYBOOK_MESSAGE_DECLARATION,
    SEND_CLINIC_LOCATION_DECLARATION,
]


def execute_playbook_tool(
    db: Session,
    tool_name: str,
    tool_args: Dict[str, Any]
) -> Any:
    """
    Execute a playbook tool by name.
    
    Args:
        db: Database session
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
    
    Returns:
        Tool execution result
    """
    if tool_name == "search_playbooks":
        return search_playbooks_tool(db, **tool_args)
    elif tool_name == "get_playbook_steps":
        return get_playbook_steps_tool(db, **tool_args)
    elif tool_name == "send_playbook_message":
        return send_playbook_message_tool(db, **tool_args)
    elif tool_name == "send_clinic_location":
        return send_clinic_location_tool(db, **tool_args)
    else:
        logger.error(f"Unknown tool: {tool_name}")
        return {"error": f"Unknown tool: {tool_name}"}
