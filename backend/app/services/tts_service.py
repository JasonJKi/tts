"""TTS orchestration: resolves voices and delegates to inference engine."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.inference import BUILTIN_VOICES, InferenceEngine
from app.services.voice_service import get_voice

logger = logging.getLogger(__name__)


async def resolve_voice(session: AsyncSession, voice_id: str) -> str:
    """Resolve a voice_id to the identifier used by vLLM.

    For builtin voices, the voice_id is used directly.
    For custom voices, we look up the DB record and use vllm_voice_id or fall back
    to a builtin default (until custom voice registration is supported in vLLM).
    """
    if voice_id in BUILTIN_VOICES:
        return voice_id

    voice = await get_voice(session, voice_id)
    if not voice:
        raise ValueError(f"Voice '{voice_id}' not found")

    # If a custom vLLM voice ID is registered, use it
    if voice.vllm_voice_id:
        return voice.vllm_voice_id

    # Fallback: use a builtin voice (custom voice cloning via vLLM-Omni
    # requires additional configuration that depends on deployment setup)
    logger.warning(
        "Voice '%s' has no vllm_voice_id, falling back to 'casual_male'",
        voice_id,
    )
    return "casual_male"


async def synthesize(
    engine: InferenceEngine,
    session: AsyncSession,
    text: str,
    voice_id: str,
    output_format: str = "wav",
    speed: float = 1.0,
) -> bytes:
    """Generate complete audio for the given text and voice."""
    voice = await resolve_voice(session, voice_id)
    return await engine.generate(
        text=text,
        voice=voice,
        output_format=output_format,
        speed=speed,
    )


async def synthesize_stream(
    engine: InferenceEngine,
    session: AsyncSession,
    text: str,
    voice_id: str,
    output_format: str = "pcm",
    speed: float = 1.0,
) -> AsyncGenerator[bytes, None]:
    """Stream audio chunks for the given text and voice."""
    voice = await resolve_voice(session, voice_id)
    async for chunk in engine.generate_stream(
        text=text,
        voice=voice,
        output_format=output_format,
        speed=speed,
    ):
        yield chunk
