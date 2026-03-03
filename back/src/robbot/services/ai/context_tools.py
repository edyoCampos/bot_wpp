"""
Function Calling tools for LLM to autonomously use contexts during conversations.

These tools enable the AI to:
1. Search for relevant contexts semantically (RAG)
2. Retrieve context items with full content details
3. Send content items from contexts to clients

Designed for LLM Function Calling integration.
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from robbot.services.bot.conversation_service import ConversationService
from robbot.services.content.content_service import ContentService
from robbot.services.ai.context_service import ContextService

logger = logging.getLogger(__name__)
# ============================================================================
# TOOL 1: Search Contexts (RAG Semantic Search)
# ============================================================================

SEARCH_CONTEXTS_DECLARATION = {
    "name": "search_contexts",
    "description": (
        "Busca semanticamente por contextos relevantes usando embeddings e ChromaDB. "
        "Retorna os contextos mais relevantes ordenados por score de similaridade."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Texto de busca em linguagem natural",
            },
            "top_k": {
                "type": "integer",
                "description": "Número de contextos a retornar (padrão: 3)",
                "default": 3,
            },
        },
        "required": ["query"],
    },
}


def search_contexts_tool(db: Session, query: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Execute semantic search for contexts."""
    try:
        service = ContextService(db)
        results = service.search_contexts(query, top_k=top_k, active_only=True)

        logger.info("[INFO] Context search: query='%s', results=%s", query, len(results))

        return [
            {
                "context_id": r.context_id,
                "context_name": r.name,
                "topic_name": r.topic_name,
                "description": r.description,
                "relevance_score": round(r.relevance_score, 3),
            }
            for r in results
        ]
    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("[ERROR] Error searching contexts: %s", e)
        return []


# ============================================================================
# TOOL 2: Get Context Items (with content details)
# ============================================================================

GET_CONTEXT_ITEMS_DECLARATION = {
    "name": "get_context_items",
    "description": (
        "Obtém todos os itens de um contexto com detalhes completos dos conteúdos. "
        "Use após search_contexts para ver o conteúdo detalhado de um contexto específico."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "context_id": {"type": "string", "description": "UUID do contexto (obtido de search_contexts)"}
        },
        "required": ["context_id"],
    },
}


def get_context_items_tool(db: Session, context_id: str) -> dict[str, Any]:
    """Retrieve all items for a context with full content details."""
    try:
        service = ContextService(db)
        items = service.get_context_items_with_details(context_id)

        logger.info("[INFO] Retrieved context items: context_id=%s, items=%s", context_id, len(items))

        return {"context_id": context_id, "total_items": len(items), "items": items}
    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("[ERROR] Error getting context items: %s", e)
        return {"context_id": context_id, "total_items": 0, "items": [], "error": str(e)}


# ============================================================================
# TOOL 3: Send Context Content
# ============================================================================

SEND_CONTEXT_CONTENT_DECLARATION = {
    "name": "send_context_content",
    "description": (
        "Envia um conteúdo específico de um contexto para o cliente na conversa atual. "
        "IMPORTANTE: Sempre adicione uma introdução personalizada (custom_intro) para contextualizar."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "content_id": {"type": "string", "description": "UUID do conteúdo (obtido de get_context_items)"},
            "conversation_id": {"type": "string", "description": "UUID da conversa atual"},
            "custom_intro": {
                "type": "string",
                "description": "Texto introdutório para contextualizar o envio",
            },
        },
        "required": ["content_id", "conversation_id"],
    },
}


def send_context_content_tool(
    db: Session, content_id: str, conversation_id: str, custom_intro: str = None
) -> dict[str, Any]:
    """Send content from a context to the client."""
    try:
        # Get content details
        content_service = ContentService(db)
        content = content_service.get_content(content_id)

        if not content:
            return {"success": False, "error": f"Content {content_id} not found"}

        # Get conversation
        conv_service = ConversationService(db)
        conversation = conv_service.get_by_id(conversation_id)

        if not conversation:
            return {"success": False, "error": f"Conversation {conversation_id} not found"}

        logger.info(
            f"Sending context content: content_id={content_id}, "
            f"conversation_id={conversation_id}, intro={custom_intro}"
        )

        return {
            "success": True,
            "content_id": content_id,
            "conversation_id": conversation_id,
            "content_type": content.type,
            "custom_intro": custom_intro,
            "note": "Content queued for sending",
        }

    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("[ERROR] Error sending context content: %s", e)
        return {"success": False, "error": str(e)}


# ============================================================================
# TOOL 4: Send Clinic Location
# ============================================================================

SEND_CLINIC_LOCATION_DECLARATION = {
    "name": "send_clinic_location",
    "description": (
        "Envia a localização da Go via WhatsApp para o paciente. "
        "Use quando o paciente perguntar sobre: endereço, localização, como chegar, "
        "onde fica a clínica, mapa, GPS, coordenadas, direções, rota, etc. "
        "A localização é enviada como um pin no WhatsApp com as coordenadas exatas da clínica. "
        "Endereço: Av. São Miguel, 1000 - sala 102, Dois Irmãos/RS. "
        "SEMPRE use esta tool quando houver menção a localização/endereço."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "chat_id": {"type": "string", "description": "ID do chat do WhatsApp (formato: 5551999999999@c.us)"},
            "custom_title": {
                "type": "string",
                "description": "Título customizado para o pin de localização (opcional, padrão: 'Go')",
                "default": "Go",
            },
        },
        "required": ["chat_id"],
    },
}


def send_clinic_location_tool(chat_id: str, custom_title: str = "Go") -> dict[str, Any]:
    """
    Enviar localização da Go via WhatsApp.

    Args:
        db: Database session (não usado, mas mantido por consistência)
        chat_id: ID do chat do WhatsApp
        custom_title: Título customizado para o pin

    Returns:
        Resultado do envio
    """
    try:
        from robbot.common.clinic_location import send_clinic_location_via_waha_sync

        logger.info("[INFO] Tool: send_clinic_location para %s", chat_id)

        result = send_clinic_location_via_waha_sync(chat_id=chat_id, custom_title=custom_title)

        return {
            "success": True,
            "message": "Localização da Go enviada com sucesso",
            "clinic_name": "Go",
            "address": "Av. São Miguel, 1000 - sala 102 - Centro, Dois Irmãos - RS",
            "result": result,
        }
    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("[ERROR] Failed to send location: %s", e)
        return {"success": False, "error": str(e)}


# ============================================================================
# Tool Registry
# ============================================================================

CONTEXT_TOOLS_DECLARATIONS = [
    SEARCH_CONTEXTS_DECLARATION,
    GET_CONTEXT_ITEMS_DECLARATION,
    SEND_CONTEXT_CONTENT_DECLARATION,
    SEND_CLINIC_LOCATION_DECLARATION,
]


def execute_context_tool(db: Session, tool_name: str, tool_args: dict[str, Any]) -> Any:
    """Execute a context tool by name."""
    if tool_name == "search_contexts":
        return search_contexts_tool(db, **tool_args)
    elif tool_name == "get_context_items":
        return get_context_items_tool(db, **tool_args)
    elif tool_name == "send_context_content":
        return send_context_content_tool(db, **tool_args)
    elif tool_name == "send_clinic_location":
        return send_clinic_location_tool(**tool_args)
    else:
        logger.error("[ERROR] Unknown tool: %s", tool_name)
        return {"error": f"Unknown tool: {tool_name}"}

