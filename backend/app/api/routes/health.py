from fastapi import APIRouter, Depends

from app.dependencies import get_vllm_client
from app.engine.model_manager import VLLMClient
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(client: VLLMClient = Depends(get_vllm_client)):
    await client.check_health()
    return HealthResponse(
        status="ok" if client.is_healthy else "degraded",
        model_server="connected" if client.is_healthy else "unreachable",
        model=client.model,
        version="0.1.0",
    )
