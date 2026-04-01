from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.inference import InferenceEngine
from app.engine.model_manager import BaseModelBackend
from app.models.database import get_session


async def get_db(session: AsyncSession = Depends(get_session)):
    yield session


def get_model_backend(request: Request) -> BaseModelBackend:
    return request.app.state.model_backend


def get_inference_engine(request: Request) -> InferenceEngine:
    return InferenceEngine(request.app.state.model_backend)
