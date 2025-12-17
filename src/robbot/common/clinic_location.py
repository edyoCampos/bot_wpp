"""Constantes e funções para gerenciar localização da Clínica GO."""

import logging
from typing import Optional

from robbot.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def get_clinic_location() -> dict:
    """
    Retornar dados de localização da Clínica GO.
    
    Returns:
        Dict com:
        - name: Nome da clínica
        - address: Endereço completo
        - latitude: Coordenada de latitude
        - longitude: Coordenada de longitude
        - maps_url: Link do Google Maps
    """
    return {
        "name": settings.CLINIC_NAME,
        "address": settings.CLINIC_ADDRESS,
        "latitude": settings.CLINIC_LATITUDE,
        "longitude": settings.CLINIC_LONGITUDE,
        "maps_url": settings.CLINIC_MAPS_URL,
    }


async def send_clinic_location_via_waha(
    chat_id: str,
    session_name: str = "default",
    custom_title: Optional[str] = None
) -> dict:
    """
    Enviar localização da Clínica GO via WAHA.
    
    Args:
        chat_id: ID do chat do WhatsApp (número + @c.us)
        session_name: Nome da sessão WAHA
        custom_title: Título customizado (padrão: "Clínica GO")
        
    Returns:
        Resposta do WAHA com dados da mensagem enviada
        
    Example:
        >>> result = await send_clinic_location_via_waha("5551999999999@c.us")
        >>> print(result)  # {"id": "...", "status": "sent"}
    """
    from robbot.adapters.external.waha_client import WAHAClient
    
    location = get_clinic_location()
    title = custom_title or location["name"]
    
    logger.info(f"📍 Enviando localização da clínica para {chat_id}")
    
    async with WAHAClient() as waha:
        result = await waha.send_location(
            chat_id=chat_id,
            session=session_name,
            latitude=location["latitude"],
            longitude=location["longitude"],
            title=title
        )
    
    logger.info(f"✓ Localização da clínica enviada com sucesso")
    return result


def send_clinic_location_via_waha_sync(
    chat_id: str,
    session_name: str = "default",
    custom_title: Optional[str] = None
) -> dict:
    """
    Versão síncrona de send_clinic_location_via_waha.
    
    Útil para jobs em background (RQ).
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        send_clinic_location_via_waha(chat_id, session_name, custom_title)
    )


# Atalhos para acesso rápido
CLINIC_NAME = settings.CLINIC_NAME
CLINIC_ADDRESS = settings.CLINIC_ADDRESS
CLINIC_LATITUDE = settings.CLINIC_LATITUDE
CLINIC_LONGITUDE = settings.CLINIC_LONGITUDE
CLINIC_MAPS_URL = settings.CLINIC_MAPS_URL
