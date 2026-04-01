import logging

import httpx

logger = logging.getLogger(__name__)


class VLLMClient:
    """Async client for vLLM-Omni model server."""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(connect=5.0, read=120.0, write=10.0, pool=5.0),
        )
        self._healthy = False

    async def check_health(self) -> bool:
        try:
            resp = await self._client.get("/health")
            self._healthy = resp.status_code == 200
            if self._healthy:
                logger.info("vLLM-Omni server is healthy at %s", self.base_url)
            else:
                logger.warning(
                    "vLLM-Omni server returned %d at %s",
                    resp.status_code,
                    self.base_url,
                )
        except httpx.ConnectError:
            self._healthy = False
            logger.warning(
                "vLLM-Omni server not reachable at %s (will retry on requests)",
                self.base_url,
            )
        return self._healthy

    @property
    def is_healthy(self) -> bool:
        return self._healthy

    async def synthesize(
        self,
        text: str,
        voice: str = "casual_male",
        response_format: str = "wav",
        speed: float = 1.0,
    ) -> bytes:
        """Batch TTS: returns complete audio bytes."""
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
        self,
        text: str,
        voice: str = "casual_male",
        response_format: str = "pcm",
        speed: float = 1.0,
    ):
        """Streaming TTS: yields audio chunks as they arrive."""
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

    async def close(self):
        await self._client.aclose()
