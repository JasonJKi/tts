from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Voxtral TTS Platform"
    debug: bool = False

    # Backend selection: "auto", "mlx", "vllm"
    backend: str = "auto"

    # MLX backend (Apple Silicon)
    mlx_model_id: str = "mlx-community/Voxtral-4B-TTS-2603-mlx-4bit"

    # vLLM-Omni backend (NVIDIA GPU)
    vllm_base_url: str = "http://localhost:8091"
    vllm_model_id: str = "mistralai/Voxtral-4B-TTS-2603"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/db/voxtral.db"

    # Voice storage
    voices_dir: Path = Path("data/voices")

    # Audio settings
    sample_rate: int = 24000
    max_reference_duration_s: float = 30.0
    min_reference_duration_s: float = 2.0

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_prefix": "TTS_", "env_file": ".env"}


settings = Settings()
