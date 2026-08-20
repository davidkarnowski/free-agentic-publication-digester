"""Text-to-Speech (TTS) service layer for multi-modal digest accessibility.

Provides an abstracted factory pattern supporting OpenAI TTS REST API with extensible
adapters for additional providers (ElevenLabs, Google, local Kokoro, etc.).
"""

import abc
import json
import logging
import urllib.error
import urllib.request
from pathlib import Path

from fapd import config

logger = logging.getLogger("fapd.tts")


class BaseTTSService(abc.ABC):
    """Abstract base class for Text-to-Speech audio synthesis services."""

    @abc.abstractmethod
    def generate_audio(
        self,
        text: str,
        output_path: Path,
        voice: str | None = None,
        model: str | None = None,
        speed: float = 1.0,
    ) -> bool:
        """Synthesize prose text to audio and write binary file to output_path.
        
        Returns True if audio file was successfully written, False otherwise.
        """


class OpenAITTSService(BaseTTSService):
    """OpenAI Speech REST API adapter (tts-1 / tts-1-hd)."""

    ENDPOINT = "https://api.openai.com/v1/audio/speech"

    def __init__(self, api_key: str | None = None, default_model: str | None = None, default_voice: str | None = None):
        self.api_key = (api_key or config.OPENAI_API_KEY).strip()
        self.default_model = default_model or config.TTS_MODEL or "tts-1"
        self.default_voice = default_voice or config.TTS_VOICE or "nova"

    def generate_audio(
        self,
        text: str,
        output_path: Path,
        voice: str | None = None,
        model: str | None = None,
        speed: float = 1.0,
    ) -> bool:
        if not text or not text.strip():
            logger.warning("Empty text passed to OpenAITTSService — skipping audio generation")
            return False

        if not self.api_key:
            logger.warning("OPENAI_API_KEY is not configured — skipping TTS audio generation")
            return False

        selected_voice = voice or self.default_voice
        selected_model = model or self.default_model

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "model": selected_model,
            "input": text.strip(),
            "voice": selected_voice,
            "speed": max(0.25, min(4.0, speed)),
            "response_format": "mp3",
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.ENDPOINT,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": config.USER_AGENT,
            },
            method="POST",
        )

        try:
            logger.info(
                "OpenAI TTS synthesis request: %d chars, model=%s, voice=%s -> %s",
                len(text),
                selected_model,
                selected_voice,
                output_path.name,
            )
            with urllib.request.urlopen(req, timeout=config.REQUEST_TIMEOUT) as response:
                audio_bytes = response.read()
                output_path.write_bytes(audio_bytes)
                logger.info(
                    "OpenAI TTS synthesis completed: %d bytes written to %s",
                    len(audio_bytes),
                    output_path,
                )
                return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            logger.error("OpenAI TTS HTTP %d error: %s", e.code, err_body[:300])
            return False
        except Exception as e:  # noqa: BLE001
            logger.error("OpenAI TTS synthesis failed: %s", e)
            return False


class NullTTSService(BaseTTSService):
    """No-op TTS service used when TTS is disabled or offline."""

    def generate_audio(
        self,
        text: str,
        output_path: Path,
        voice: str | None = None,
        model: str | None = None,
        speed: float = 1.0,
    ) -> bool:
        logger.debug("NullTTSService: TTS is disabled or no provider configured")
        return False


def get_tts_service(provider: str | None = None) -> BaseTTSService:
    """Factory function returning the configured TTSService implementation."""
    selected_provider = (provider or config.TTS_PROVIDER or "none").lower()

    if selected_provider == "openai":
        if config.OPENAI_API_KEY:
            return OpenAITTSService()
        else:
            logger.warning("TTS_PROVIDER is 'openai' but OPENAI_API_KEY is unset; returning NullTTSService")
            return NullTTSService()

    elif selected_provider in ("none", "disabled", "off", ""):
        return NullTTSService()

    else:
        logger.warning("Unknown TTS_PROVIDER '%s'; falling back to NullTTSService", selected_provider)
        return NullTTSService()
