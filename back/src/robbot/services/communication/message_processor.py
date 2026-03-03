"""
Message Processor - Processa mensagens multimídia (áudio, vídeo, texto).

Responsabilidades:
- Transcrever áudios (via faster-whisper)
- Processar vídeos (transcrever áudio + descrever visual)
- Salvar mensagens inbound/outbound no banco

REFACTORED: Dependency injection of TranscriptionService (Issue #4: Session Management)
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.conversation_message_repository import ConversationMessageRepository
from robbot.core.custom_exceptions import DatabaseError
from robbot.domain.shared.enums import MessageDirection
from robbot.infra.persistence.models.conversation_message_model import ConversationMessageModel
from robbot.services.communication.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Processa mensagens multimídia e persistência"""

    def __init__(self, db: Session, transcription_service: TranscriptionService):
        """
        Initialize MessageProcessor with DI.

        Args:
            db: SQLAlchemy session for database operations
            transcription_service: Injected TranscriptionService for audio/video processing
        """
        self.db = db
        self.transcription_service = transcription_service

    async def process_media_message(
        self,
        message_text: str,
        has_audio: bool = False,
        audio_url: str | None = None,
        has_video: bool = False,
        video_url: str | None = None,
    ) -> str:
        """
        Processar mensagem com mídia (áudio ou vídeo).

        Args:
            message_text: Texto original da mensagem
            has_audio: Se tem áudio
            audio_url: URL do áudio
            has_video: Se tem vídeo
            video_url: URL do vídeo

        Returns:
            str: Texto processado (com transcrição se houver)
        """
        # Se é vídeo: transcrever áudio + descrever visual
        if has_video and video_url:
            return await self._process_video(video_url)

        # Se é apenas áudio: transcrever
        if has_audio and audio_url:
            return await self._process_audio(audio_url)

        # Se é texto puro, retorna direto
        return message_text

    async def _process_video(self, video_url: str) -> str:
        """Processar vídeo: transcrever áudio + marcar presença de vídeo"""
        try:
            # 1. Transcrever áudio do vídeo
            transcription = await self.transcription_service.transcribe_audio(video_url, language="pt")

            if transcription:
                logger.info("[SUCCESS] Video audio transcribed: %s...", transcription[:100])

            # 2. Gerar descrição visual com Gemini Vision
            # TODO: Implementar descrição assíncrona
            # Por ora, apenas marcamos que há vídeo
            return f"[Vídeo recebido]\nÁudio: {transcription or 'não transcrito'}"

        except Exception as e:  # noqa: BLE001
            logger.error("[ERROR] Error processing video: %s", e)
            return "[Vídeo recebido - erro no processamento]"

    async def _process_audio(self, audio_url: str) -> str:
        """Processar áudio: transcrever para texto"""
        try:
            transcription = await self.transcription_service.transcribe_audio(audio_url, language="pt")

            if transcription:
                logger.info("[SUCCESS] Audio transcribed: %s...", transcription[:100])
                return f"[Áudio transcrito]: {transcription}"

            logger.warning("[WARNING] Transcription returned empty")
            return "[Áudio recebido - transcrição falhou]"

        except Exception as e:  # noqa: BLE001
            logger.error("[ERROR] Error transcribing audio: %s", e)
            return "[Áudio recebido - erro na transcrição]"

    async def save_inbound_message(
        self, session: Any, conversation_id: str, text: str, from_phone: str, to_phone: str = "BOT"
    ) -> ConversationMessageModel:
        """
        Persistir mensagem recebida do cliente no banco.

        Returns:
            ConversationMessageModel: Mensagem salva com timestamp UTC
        """
        try:
            repo = ConversationMessageRepository(session)

            message = ConversationMessageModel(
                conversation_id=conversation_id,
                direction=MessageDirection.INBOUND,
                from_phone=from_phone,
                to_phone=to_phone,
                body=text,
            )
            repo.create(message)
            session.flush()

            logger.info("[SUCCESS] Inbound message saved (id=%s)", message.id)

            return message

        except Exception as e:  # noqa: BLE001
            logger.error("[ERROR] Failed to save inbound message: %s", e)
            raise DatabaseError(f"Failed to save inbound message: {e}") from e

    async def save_outbound_message(
        self, session: Any, conversation_id: str, text: str, to_phone: str, from_phone: str = "BOT"
    ) -> ConversationMessageModel:
        """
        Persistir mensagem enviada pelo bot no banco.

        Returns:
            ConversationMessageModel: Mensagem salva com timestamp UTC
        """
        try:
            from robbot.core.text_sanitizer import enforce_whatsapp_style

            text = enforce_whatsapp_style(text)
            repo = ConversationMessageRepository(session)

            message = ConversationMessageModel(
                conversation_id=conversation_id,
                direction=MessageDirection.OUTBOUND,
                from_phone=from_phone,
                to_phone=to_phone,
                body=text,
            )
            repo.create(message)
            session.flush()

            logger.info("[SUCCESS] Outbound message saved (id=%s)", message.id)

            return message

        except Exception as e:  # noqa: BLE001
            logger.error("[ERROR] Failed to save outbound message: %s", e)
            raise DatabaseError(f"Failed to save outbound message: {e}") from e

