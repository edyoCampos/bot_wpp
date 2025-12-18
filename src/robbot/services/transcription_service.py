"""Serviço de transcrição de áudio usando Faster-Whisper (local, sem custo)."""

import logging
import tempfile
from pathlib import Path
from typing import Optional

import httpx

from robbot.config.settings import get_settings
from robbot.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)
settings = get_settings()


class TranscriptionService:
    """
    Serviço de transcrição de áudio usando Faster-Whisper (inferência local).
    
    Faster-Whisper: 4x mais rápido que Whisper original, roda localmente (SEM CUSTO DE API).
    Suporta formatos comuns do WhatsApp: ogg, mp3, mp4, m4a, wav.
    
    Dependência: faster-whisper (instalado via uv add faster-whisper)
    """

    def __init__(self):
        """Inicializar modelo Faster-Whisper (lazy loading)."""
        self.model = None
        self.model_size = getattr(settings, "WHISPER_MODEL", "base")  # tiny, base, small, medium, large
        logger.info(f"✓ TranscriptionService initialized (model={self.model_size}, local inference)")

    def _load_model(self):
        """Carregar modelo Faster-Whisper sob demanda (lazy loading)."""
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                
                # Load model (first time downloads ~75MB for 'base', then cached)
                self.model = WhisperModel(
                    self.model_size, 
                    device="cpu",  # Use "cuda" if GPU available
                    compute_type="int8"  # Optimized for CPU
                )
                logger.info(f"✓ Faster-Whisper model loaded: {self.model_size}")
            except ImportError:
                raise ExternalServiceError(
                    "faster-whisper not installed. Run: uv add faster-whisper"
                )
            except Exception as e:
                raise ExternalServiceError(f"Failed to load Whisper model: {e}")
    
    async def transcribe_audio(self, audio_url: str, language: str = "pt") -> Optional[str]:
        """
        Transcrever áudio de URL usando Faster-Whisper (local, sem custo de API).
        
        Args:
            audio_url: URL do arquivo de áudio (do WAHA ou storage)
            language: Código do idioma (padrão: "pt" para Português)
            
        Returns:
            Texto transcrito ou None se falhar
            
        Raises:
            ExternalAPIError: Se transcrição falhar
        """
        self._load_model()
        
        try:
            logger.info(f"🎤 Starting audio transcription from: {audio_url}")
            
            # Download audio file
            audio_content = await self._download_audio(audio_url)
            if not audio_content:
                raise ExternalServiceError(f"Failed to download audio from {audio_url}")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
                temp_file.write(audio_content)
                temp_path = Path(temp_file.name)
            
            try:
                # Transcribe with Faster-Whisper
                segments, info = self.model.transcribe(
                    str(temp_path),
                    language=language,
                    beam_size=5,
                    vad_filter=True,  # Voice Activity Detection (remove silence)
                )
                
                # Concatenate all segments
                transcript = " ".join([segment.text for segment in segments]).strip()
                
                logger.info(f"✓ Audio transcribed (length={len(transcript)} chars, detected_lang={info.language})")
                return transcript
                
            finally:
                # Clean up temp file
                temp_path.unlink(missing_ok=True)
                
        except ExternalServiceError:
            raise
        except Exception as e:
            logger.error(f"✗ Transcription failed: {e}", exc_info=True)
            raise ExternalServiceError(f"Audio transcription failed: {e}") from e

    def _download_audio_sync(self, url: str) -> Optional[bytes]:
        """Baixar arquivo de áudio da URL (síncrono)."""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as e:
            logger.error(f"✗ Failed to download audio from {url}: {e}")
            return None
