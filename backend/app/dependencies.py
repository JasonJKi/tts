from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.inference import InferenceEngine
from app.engine.model_manager import VLLMClient
from app.models.database import get_session


async def get_db(session: AsyncSession = Depends(get_session)):
    yield session


def get_vllm_client(request: Request) -> VLLMClient:
    return request.app.state.vllm_client


def get_inference_engine(request: Request) -> InferenceEngine:
    return InferenceEngine(request.app.state.vllm_client)
