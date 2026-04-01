"""Audio processing: validation, format conversion, duration extraction."""

import io
import logging

import soundfile as sf

from app.config import settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".aac"}


def validate_reference_audio(audio_bytes: bytes, filename: str) -> dict:
    """Validate reference audio for voice cloning.

    Returns metadata dict with duration, sample_rate, channels.
    Raises ValueError if invalid.
    """
    from pathlib import Path

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported audio format '{ext}'. Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    try:
        with io.BytesIO(audio_bytes) as buf:
            info = sf.info(buf)
    except Exception:
        raise ValueError("Could not read audio file. Ensure it is a valid audio file.")

    if info.duration < settings.min_reference_duration_s:
        raise ValueError(
            f"Reference audio too short ({info.duration:.1f}s). "
            f"Minimum is {settings.min_reference_duration_s}s."
        )

    if info.duration > settings.max_reference_duration_s:
        raise ValueError(
            f"Reference audio too long ({info.duration:.1f}s). "
            f"Maximum is {settings.max_reference_duration_s}s."
        )

    return {
        "duration_s": info.duration,
        "sample_rate": info.samplerate,
        "channels": info.channels,
    }


def get_content_type(output_format: str) -> str:
    """Return the MIME type for the given audio format."""
    return {
        "wav": "audio/wav",
        "pcm": "audio/pcm",
        "mp3": "audio/mpeg",
        "flac": "audio/flac",
        "opus": "audio/opus",
        "aac": "audio/aac",
    }.get(output_format, "application/octet-stream")
