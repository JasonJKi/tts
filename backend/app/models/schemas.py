from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# --- Voice schemas ---

class VoiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    language: str = "en"


class VoiceResponse(BaseModel):
    id: str
    name: str
    description: str
    language: str
    audio_duration_s: float | None
    vllm_voice_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VoiceListResponse(BaseModel):
    voices: list[VoiceResponse]
    total: int


# --- TTS schemas ---

SUPPORTED_FORMATS = Literal["wav", "pcm", "mp3", "flac", "opus", "aac"]
SUPPORTED_LANGUAGES = Literal["en", "fr", "es", "pt", "it", "nl", "de", "hi", "ar"]

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str
    language: SUPPORTED_LANGUAGES = "en"
    output_format: SUPPORTED_FORMATS = "wav"
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


class TTSStreamRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str
    language: SUPPORTED_LANGUAGES = "en"
    output_format: Literal["pcm", "wav"] = "pcm"
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


# --- Generation history ---

class GenerationResponse(BaseModel):
    id: str
    voice_id: str
    text: str
    language: str
    output_format: str
    duration_s: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Health ---

class HealthResponse(BaseModel):
    status: str
    model_server: str
    model: str
    version: str
