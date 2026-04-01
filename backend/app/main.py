import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.engine.detector import detect_backend, get_system_info
from app.engine.model_manager import create_backend
from app.models.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - ensure data directories exist
    settings.voices_dir.mkdir(parents=True, exist_ok=True)
    from pathlib import Path
    db_path = settings.database_url.split("///")[-1] if "///" in settings.database_url else None
    if db_path:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    await init_db()

    # Auto-detect and create backend
    backend_type = detect_backend(override=settings.backend)
    system_info = get_system_info(backend_type)
    logger.info(
        "System: %s %s | GPU: %s | RAM: %.1f GB | Backend: %s",
        system_info.os, system_info.arch, system_info.gpu,
        system_info.ram_gb, backend_type,
    )

    backend = create_backend(
        backend_type=backend_type,
        mlx_model_id=settings.mlx_model_id,
        vllm_base_url=settings.vllm_base_url,
        vllm_model_id=settings.vllm_model_id,
    )
    await backend.check_health()

    app.state.model_backend = backend
    app.state.system_info = system_info

    yield

    # Shutdown
    await backend.close()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.routes.health import router as health_router
from app.api.routes.voices import router as voices_router
from app.api.routes.tts import router as tts_router
from app.api.websocket.streaming import router as ws_router

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(voices_router, prefix="/api/v1", tags=["voices"])
app.include_router(tts_router, prefix="/api/v1", tags=["tts"])
app.include_router(ws_router, prefix="/api/v1", tags=["websocket"])
