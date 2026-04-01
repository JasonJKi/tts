"""Voice CRUD operations and file storage."""

import logging
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import Voice
from app.services.audio_service import validate_reference_audio

logger = logging.getLogger(__name__)


async def create_voice(
    session: AsyncSession,
    name: str,
    audio_bytes: bytes,
    filename: str,
    description: str = "",
    language: str = "en",
) -> Voice:
    """Create a new voice from reference audio."""
    # Validate audio
    audio_info = validate_reference_audio(audio_bytes, filename)

    # Store audio file
    voice_id = str(uuid.uuid4())
    ext = Path(filename).suffix.lower()
    audio_filename = f"{voice_id}{ext}"
    audio_path = settings.voices_dir / audio_filename
    audio_path.write_bytes(audio_bytes)

    voice = Voice(
        id=voice_id,
        name=name,
        description=description,
        language=language,
        reference_audio_path=str(audio_path),
        audio_duration_s=audio_info["duration_s"],
        vllm_voice_id=None,  # Will be set when custom voice support is configured
    )
    session.add(voice)
    await session.commit()
    await session.refresh(voice)

    logger.info("Created voice '%s' (id=%s, duration=%.1fs)", name, voice_id, audio_info["duration_s"])
    return voice


async def list_voices(session: AsyncSession) -> list[Voice]:
    result = await session.execute(select(Voice).order_by(Voice.created_at.desc()))
    return list(result.scalars().all())


async def get_voice(session: AsyncSession, voice_id: str) -> Voice | None:
    result = await session.execute(select(Voice).where(Voice.id == voice_id))
    return result.scalar_one_or_none()


async def delete_voice(session: AsyncSession, voice_id: str) -> bool:
    voice = await get_voice(session, voice_id)
    if not voice:
        return False

    # Delete audio file
    audio_path = Path(voice.reference_audio_path)
    if audio_path.exists():
        audio_path.unlink()

    await session.delete(voice)
    await session.commit()
    logger.info("Deleted voice id=%s", voice_id)
    return True


def get_voice_audio_path(voice: Voice) -> Path:
    return Path(voice.reference_audio_path)
