"""High-level inference interface wrapping the model backend.

Handles voice resolution and provides a clean async interface
regardless of which backend (MLX or vLLM) is active.
"""

import io
import logging
from typing import AsyncGenerator

import soundfile as sf

from app.engine.model_manager import BaseModelBackend

logger = logging.getLogger(__name__)

# Built-in voices available in Voxtral
BUILTIN_VOICES = [
    "casual_male",
    "casual_female",
    "neutral_male",
    "neutral_female",
    "cheerful_male",
    "cheerful_female",
    "expressive_male",
    "expressive_female",
]


class InferenceEngine:
    def __init__(self, backend: BaseModelBackend):
        self.backend = backend

    async def generate(
        self,
        text: str,
        voice: str = "casual_male",
        output_format: str = "wav",
        speed: float = 1.0,
    ) -> bytes:
        """Generate complete audio for the given text."""
        return await self.backend.synthesize(
            text=text,
            voice=voice,
            response_format=output_format,
            speed=speed,
        )

    async def generate_stream(
        self,
        text: str,
        voice: str = "casual_male",
        output_format: str = "pcm",
        speed: float = 1.0,
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks as they're generated."""
        async for chunk in self.backend.synthesize_stream(
            text=text,
            voice=voice,
            response_format=output_format,
            speed=speed,
        ):
            yield chunk

    @staticmethod
    def get_audio_info(audio_bytes: bytes) -> dict:
        """Extract audio metadata from WAV bytes."""
        with io.BytesIO(audio_bytes) as buf:
            info = sf.info(buf)
            return {
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "duration_s": info.duration,
                "frames": info.frames,
                "format": info.format,
            }
