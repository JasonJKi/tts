from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_inference_engine
from app.engine.inference import InferenceEngine
from app.models.schemas import TTSRequest, TTSStreamRequest
from app.services import tts_service
from app.services.audio_service import get_content_type

router = APIRouter()


@router.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    engine: InferenceEngine = Depends(get_inference_engine),
    session: AsyncSession = Depends(get_db),
):
    """Generate complete audio from text."""
    try:
        audio_bytes = await tts_service.synthesize(
            engine=engine,
            session=session,
            text=request.text,
            voice_id=request.voice_id,
            output_format=request.output_format,
            speed=request.speed,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS generation failed: {e}")

    return Response(
        content=audio_bytes,
        media_type=get_content_type(request.output_format),
        headers={
            "Content-Disposition": f'attachment; filename="tts_output.{request.output_format}"'
        },
    )


@router.post("/tts/stream")
async def text_to_speech_stream(
    request: TTSStreamRequest,
    engine: InferenceEngine = Depends(get_inference_engine),
    session: AsyncSession = Depends(get_db),
):
    """Stream audio chunks via Server-Sent Events (SSE) / chunked transfer."""
    try:
        # Validate voice exists before starting stream
        await tts_service.resolve_voice(session, request.voice_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    async def audio_generator():
        async for chunk in tts_service.synthesize_stream(
            engine=engine,
            session=session,
            text=request.text,
            voice_id=request.voice_id,
            output_format=request.output_format,
            speed=request.speed,
        ):
            yield chunk

    return StreamingResponse(
        audio_generator(),
        media_type=get_content_type(request.output_format),
    )
