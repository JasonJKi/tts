"""Multi-backend model manager with auto-detection.

Provides a unified interface for TTS inference across:
  - MLXBackend:  In-process inference on Apple Silicon via mlx-audio
  - VLLMBackend: HTTP client to external vLLM-Omni server (NVIDIA GPU)
"""

import asyncio
import io
import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator

import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)


class BaseModelBackend(ABC):
    """Abstract interface for TTS inference backends."""

    @abstractmethod
    async def synthesize(
        self, text: str, voice: str, response_format: str = "wav", speed: float = 1.0
    ) -> bytes:
        """Generate complete audio. Returns audio bytes in the requested format."""

    @abstractmethod
    async def synthesize_stream(
        self, text: str, voice: str, response_format: str = "pcm", speed: float = 1.0
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks as they're generated."""

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if the backend is ready."""

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""

    @property
    @abstractmethod
    def is_healthy(self) -> bool:
        """Whether the backend is currently healthy."""

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Human-readable backend identifier."""


# ---------------------------------------------------------------------------
# MLX Backend (Apple Silicon, in-process)
# ---------------------------------------------------------------------------

class MLXBackend(BaseModelBackend):
    """In-process TTS using mlx-audio on Apple Silicon."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        self._model = None
        self._healthy = False

    async def _load_model(self) -> None:
        """Load the model (heavy, runs in thread pool)."""
        def _load():
            from mlx_audio.tts.utils import load_model
            logger.info("Loading MLX model: %s ...", self.model_id)
            model = load_model(self.model_id)
            logger.info("MLX model loaded successfully")
            return model

        self._model = await asyncio.to_thread(_load)
        self._healthy = True

    def _generate_audio_sync(
        self, text: str, voice: str, speed: float
    ) -> np.ndarray:
        """Run inference synchronously (called via to_thread)."""
        import mlx.core as mx

        audio_chunks = []
        for result in self._model.generate(text=text, voice=voice, speed=speed):
            chunk = result.audio
            if isinstance(chunk, mx.array):
                chunk = np.array(chunk)
            audio_chunks.append(chunk)

        if not audio_chunks:
            return np.array([], dtype=np.float32)

        return np.concatenate(audio_chunks)

    @staticmethod
    def _audio_to_bytes(audio: np.ndarray, fmt: str, sample_rate: int = 24000) -> bytes:
        """Convert numpy audio array to encoded bytes."""
        if fmt == "pcm":
            # 16-bit signed PCM
            pcm = (audio * 32767).astype(np.int16)
            return pcm.tobytes()

        buf = io.BytesIO()
        sf_format = {"wav": "WAV", "flac": "FLAC", "ogg": "OGG"}.get(fmt, "WAV")
        sf_subtype = {"wav": "PCM_16", "flac": "PCM_16", "ogg": "VORBIS"}.get(fmt, "PCM_16")
        sf.write(buf, audio, sample_rate, format=sf_format, subtype=sf_subtype)
        return buf.getvalue()

    async def synthesize(
        self, text: str, voice: str, response_format: str = "wav", speed: float = 1.0
    ) -> bytes:
        audio = await asyncio.to_thread(self._generate_audio_sync, text, voice, speed)
        return self._audio_to_bytes(audio, response_format)

    async def synthesize_stream(
        self, text: str, voice: str, response_format: str = "pcm", speed: float = 1.0
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks from the MLX model's generator."""
        import mlx.core as mx

        def _iter_chunks():
            """Collect chunks from the model generator (sync)."""
            chunks = []
            for result in self._model.generate(text=text, voice=voice, speed=speed):
                chunk = result.audio
                if isinstance(chunk, mx.array):
                    chunk = np.array(chunk)
                chunks.append(chunk)
            return chunks

        chunks = await asyncio.to_thread(_iter_chunks)
        for chunk in chunks:
            yield self._audio_to_bytes(chunk, response_format)

    async def check_health(self) -> bool:
        if self._model is None:
            await self._load_model()
        self._healthy = self._model is not None
        return self._healthy

    async def close(self) -> None:
        self._model = None
        self._healthy = False

    @property
    def is_healthy(self) -> bool:
        return self._healthy

    @property
    def backend_name(self) -> str:
        return f"mlx ({self.model_id})"


# ---------------------------------------------------------------------------
# vLLM-Omni Backend (NVIDIA GPU, HTTP sidecar)
# ---------------------------------------------------------------------------

class VLLMBackend(BaseModelBackend):
    """HTTP client for external vLLM-Omni model server."""

    def __init__(self, base_url: str, model: str):
        import httpx

        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(connect=5.0, read=120.0, write=10.0, pool=5.0),
        )
        self._healthy = False

    async def synthesize(
        self, text: str, voice: str, response_format: str = "wav", speed: float = 1.0
    ) -> bytes:
        payload = {
            "input": text,
            "model": self.model,
            "voice": voice,
            "response_format": response_format,
            "speed": speed,
        }
        resp = await self._client.post("/v1/audio/speech", json=payload)
        resp.raise_for_status()
        self._healthy = True
        return resp.content

    async def synthesize_stream(
        self, text: str, voice: str, response_format: str = "pcm", speed: float = 1.0
    ) -> AsyncGenerator[bytes, None]:
        payload = {
            "input": text,
            "model": self.model,
            "voice": voice,
            "response_format": response_format,
            "speed": speed,
        }
        async with self._client.stream(
            "POST", "/v1/audio/speech", json=payload
        ) as resp:
            resp.raise_for_status()
            self._healthy = True
            async for chunk in resp.aiter_bytes(chunk_size=4096):
                yield chunk

    async def check_health(self) -> bool:
        try:
            resp = await self._client.get("/health")
            self._healthy = resp.status_code == 200
            if self._healthy:
                logger.info("vLLM-Omni server healthy at %s", self.base_url)
            else:
                logger.warning("vLLM-Omni returned %d", resp.status_code)
        except Exception:
            self._healthy = False
            logger.warning("vLLM-Omni not reachable at %s", self.base_url)
        return self._healthy

    async def close(self) -> None:
        await self._client.aclose()

    @property
    def is_healthy(self) -> bool:
        return self._healthy

    @property
    def backend_name(self) -> str:
        return f"vllm-omni ({self.base_url})"


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_backend(
    backend_type: str,
    mlx_model_id: str = "mlx-community/Voxtral-4B-TTS-2603-mlx-4bit",
    vllm_base_url: str = "http://localhost:8091",
    vllm_model_id: str = "mistralai/Voxtral-4B-TTS-2603",
) -> BaseModelBackend:
    """Create the appropriate backend based on detected environment."""
    if backend_type == "mlx":
        return MLXBackend(model_id=mlx_model_id)
    elif backend_type == "vllm":
        return VLLMBackend(base_url=vllm_base_url, model=vllm_model_id)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
