from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.engine.model_manager import VLLMClient
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings.voices_dir.mkdir(parents=True, exist_ok=True)
    await init_db()
    app.state.vllm_client = VLLMClient(
        base_url=settings.vllm_base_url,
        model=settings.vllm_model,
    )
    await app.state.vllm_client.check_health()
    yield
    # Shutdown
    await app.state.vllm_client.close()


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
