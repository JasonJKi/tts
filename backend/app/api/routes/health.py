from fastapi import APIRouter, Request

from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    backend = request.app.state.model_backend
    system_info = request.app.state.system_info

    await backend.check_health()

    return HealthResponse(
        status="ok" if backend.is_healthy else "degraded",
        backend=backend.backend_name,
        healthy=backend.is_healthy,
        version="0.1.0",
        system=dict(
            os=system_info.os,
            arch=system_info.arch,
            gpu=system_info.gpu,
            ram_gb=system_info.ram_gb,
            python_version=system_info.python_version,
        ),
    )
