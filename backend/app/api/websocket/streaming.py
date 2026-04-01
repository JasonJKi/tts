import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.engine.inference import InferenceEngine
from app.models.database import async_session
from app.services import tts_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/tts")
async def websocket_tts(websocket: WebSocket):
    """WebSocket endpoint for real-time streaming TTS.

    Protocol:
      Client sends JSON: {"text": "...", "voice_id": "...", "language": "en", "output_format": "pcm", "speed": 1.0}
      Server sends binary audio chunks
      Server sends JSON: {"type": "done"} when complete
      Server sends JSON: {"type": "error", "detail": "..."} on error
    """
    await websocket.accept()
    vllm_client = websocket.app.state.vllm_client
    engine = InferenceEngine(vllm_client)

    try:
        while True:
            # Receive TTS request
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "detail": "Invalid JSON"})
                continue

            text = msg.get("text", "").strip()
            if not text:
                await websocket.send_json({"type": "error", "detail": "Empty text"})
                continue

            voice_id = msg.get("voice_id", "casual_male")
            output_format = msg.get("output_format", "pcm")
            speed = msg.get("speed", 1.0)

            try:
                async with async_session() as session:
                    async for chunk in tts_service.synthesize_stream(
                        engine=engine,
                        session=session,
                        text=text,
                        voice_id=voice_id,
                        output_format=output_format,
                        speed=speed,
                    ):
                        await websocket.send_bytes(chunk)

                await websocket.send_json({"type": "done"})

            except ValueError as e:
                await websocket.send_json({"type": "error", "detail": str(e)})
            except Exception as e:
                logger.exception("WebSocket TTS error")
                await websocket.send_json(
                    {"type": "error", "detail": f"Generation failed: {e}"}
                )

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
