from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.engine.inference import BUILTIN_VOICES
from app.models.schemas import VoiceCreate, VoiceListResponse, VoiceResponse
from app.services import voice_service

router = APIRouter()


@router.post("/voices", response_model=VoiceResponse, status_code=201)
async def create_voice(
    name: str = Form(...),
    description: str = Form(""),
    language: str = Form("en"),
    audio: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
):
    """Create a new voice from reference audio."""
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    try:
        voice = await voice_service.create_voice(
            session=session,
            name=name,
            audio_bytes=audio_bytes,
            filename=audio.filename or "upload.wav",
            description=description,
            language=language,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return voice


@router.get("/voices", response_model=VoiceListResponse)
async def list_voices(session: AsyncSession = Depends(get_db)):
    """List all voices (custom + builtin)."""
    custom_voices = await voice_service.list_voices(session)
    return VoiceListResponse(voices=custom_voices, total=len(custom_voices))


@router.get("/voices/builtin", response_model=list[str])
async def list_builtin_voices():
    """List built-in Voxtral voices."""
    return BUILTIN_VOICES


@router.get("/voices/{voice_id}", response_model=VoiceResponse)
async def get_voice(
    voice_id: str,
    session: AsyncSession = Depends(get_db),
):
    voice = await voice_service.get_voice(session, voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice


@router.delete("/voices/{voice_id}", status_code=204)
async def delete_voice(
    voice_id: str,
    session: AsyncSession = Depends(get_db),
):
    deleted = await voice_service.delete_voice(session, voice_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Voice not found")


@router.get("/voices/{voice_id}/preview")
async def preview_voice(
    voice_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Download the reference audio for a voice."""
    voice = await voice_service.get_voice(session, voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    audio_path = voice_service.get_voice_audio_path(voice)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Reference audio file not found")

    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav",
        filename=f"{voice.name}_reference{audio_path.suffix}",
    )
