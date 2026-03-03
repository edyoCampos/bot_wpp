"""Audio transcription service using Faster-Whisper (local, zero external API cost)."""

import logging
import tempfile
from pathlib import Path

import httpx

from robbot.config.settings import get_settings
from robbot.core.custom_exceptions import LLMError

logger = logging.getLogger(__name__)
settings = get_settings()


class TranscriptionService:
    """
    Audio transcription using Faster-Whisper (local inference).

    Faster-Whisper is ~4x faster than original Whisper, runs locally.
    Supports common WhatsApp formats: ogg, mp3, mp4, m4a, wav.

    Dependency: faster-whisper (install via `uv add faster-whisper`).
    """

    def __init__(self):
        """Initialize Faster-Whisper model (lazy loading)."""
        self.model = None
        # Faster-Whisper models: tiny, base, small, medium, large, large-v2, large-v3
        # Using 'base' model (good balance between speed and accuracy)
        self.model_size = "base"
        logger.info("[SUCCESS] TranscriptionService initialized (model=%s, local inference)", self.model_size)

    def _load_model(self):
        """Load Faster-Whisper model on demand (lazy loading)."""
        if self.model is None:
            try:
                from faster_whisper import WhisperModel

                # Load model (first time downloads ~75MB for 'base', then cached)
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",  # Use "cuda" if GPU available
                    compute_type="int8",  # Optimized for CPU
                )
                logger.info("[SUCCESS] Faster-Whisper model loaded: %s", self.model_size)
            except ImportError as e:
                raise LLMError(
                    "Whisper", "faster-whisper not installed. Run: uv add faster-whisper", original_error=e
                ) from e
            except Exception as e:  # noqa: BLE001 (blind exception)
                raise LLMError("Whisper", f"Failed to load model: {e}", original_error=e) from e

    async def transcribe_audio(self, audio_url: str, language: str = "pt") -> str | None:
        """
        Transcribe audio from a URL using Faster-Whisper (local, no API cost).

        Args:
            audio_url: Audio file URL (from WAHA or storage)
            language: Language code (default: "pt" for Portuguese)

        Returns:
            Transcribed text or None if it fails

        Raises:
            LLMError: If transcription fails
        """
        self._load_model()

        try:
            logger.info("[INFO] Starting audio transcription from: %s", audio_url)

            # Download audio file
            audio_content = await self._download_audio(audio_url)
            if not audio_content:
                raise LLMError("Whisper", f"Failed to download audio from {audio_url}")

            # Choose file suffix based on URL (wav/mp3/ogg/etc.)
            from urllib.parse import urlparse

            parsed = urlparse(audio_url)
            suffix = Path(parsed.path).suffix.lower() or ".ogg"

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
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

                logger.info(
                    "[SUCCESS] Audio transcribed (length=%s chars, detected_lang=%s)", len(transcript), info.language
                )
                return transcript

            finally:
                # Clean up temp file
                temp_path.unlink(missing_ok=True)

        except LLMError:
            raise
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Transcription failed: %s", e, exc_info=True)
            raise LLMError("Whisper", f"Audio transcription failed: {e}", original_error=e) from e

    async def _download_audio(self, url: str) -> bytes | None:
        """Download audio file from URL (asynchronous)."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as e:
            logger.error("[ERROR] Failed to download audio from %s: %s", url, e)
            return None

    def _download_audio_sync(self, url: str) -> bytes | None:
        """Download audio file from URL (synchronous)."""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as e:
            logger.error("[ERROR] Failed to download audio from %s: %s", url, e)
            return None

    def transcribe_audio_sync(self, audio_url: str, language: str = "pt") -> str | None:
        """
        Transcribe audio from URL synchronously (compatible with sync services).

        Uses Faster-Whisper locally and httpx for synchronous download.
        """
        self._load_model()

        try:
            logger.info("[INFO] Starting SYNC audio transcription from: %s", audio_url)

            # Download audio file
            audio_content = self._download_audio_sync(audio_url)
            if not audio_content:
                raise LLMError("Whisper", f"Failed to download audio from {audio_url}")

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
                    vad_filter=True,
                )

                transcript = " ".join([segment.text for segment in segments]).strip()

                logger.info(
                    "[SUCCESS] SYNC audio transcribed (length=%s chars, detected_lang=%s)",
                    len(transcript),
                    info.language,
                )
                return transcript

            finally:
                temp_path.unlink(missing_ok=True)

        except LLMError:
            raise
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] SYNC transcription failed: %s", e, exc_info=True)
            return None
