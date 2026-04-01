"""Environment detection: discovers OS, device, and available inference backends."""

import logging
import os
import platform
import shutil
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SystemInfo:
    os: str                # "darwin", "linux", "windows"
    arch: str              # "arm64", "x86_64"
    machine: str           # e.g. "Apple M3 Max", "x86_64"
    gpu: str               # "apple_silicon", "nvidia", "none"
    ram_gb: float          # total system RAM in GB
    backend: str           # resolved backend: "mlx", "vllm"
    python_version: str


def _get_ram_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().total / (1024 ** 3)
    except ImportError:
        pass
    # Fallback for Mac/Linux
    try:
        if platform.system() == "Darwin":
            import subprocess
            out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True)
            return int(out.strip()) / (1024 ** 3)
        elif platform.system() == "Linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        return int(line.split()[1]) / (1024 ** 2)
    except Exception:
        pass
    return 0.0


def _detect_gpu() -> str:
    """Detect available GPU type."""
    system = platform.system()

    # Apple Silicon
    if system == "Darwin" and platform.machine() == "arm64":
        return "apple_silicon"

    # NVIDIA
    if shutil.which("nvidia-smi"):
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return "nvidia"
        except Exception:
            pass

    # Check via torch
    try:
        import torch
        if torch.cuda.is_available():
            return "nvidia"
    except ImportError:
        pass

    return "none"


def _can_import(module: str) -> bool:
    try:
        __import__(module)
        return True
    except ImportError:
        return False


def detect_backend(override: str = "auto") -> str:
    """Determine which inference backend to use.

    Priority:
      1. Explicit override via TTS_BACKEND env var or config
      2. Mac + Apple Silicon + mlx available -> "mlx"
      3. Linux + NVIDIA GPU + vLLM reachable  -> "vllm"
      4. Mac without mlx -> error with install instructions
      5. Linux without GPU -> "vllm" (user must start vLLM server)

    Returns: "mlx" or "vllm"
    """
    # 1. Explicit override
    env_override = os.environ.get("TTS_BACKEND", override).lower()
    if env_override in ("mlx", "vllm"):
        logger.info("Backend override: %s", env_override)
        return env_override

    # 2. Auto-detect
    gpu = _detect_gpu()

    if gpu == "apple_silicon":
        if _can_import("mlx") and _can_import("mlx_audio"):
            logger.info("Detected Apple Silicon with mlx-audio -> using MLX backend")
            return "mlx"
        else:
            logger.warning(
                "Apple Silicon detected but mlx-audio not installed. "
                "Install with: pip install mlx-audio"
            )
            # Still return mlx - will fail at model load with clear error
            return "mlx"

    if gpu == "nvidia":
        logger.info("Detected NVIDIA GPU -> using vLLM-Omni backend")
        return "vllm"

    # Fallback
    logger.warning(
        "No GPU detected. Defaulting to vLLM backend (ensure vLLM-Omni server is running). "
        "On Mac, install mlx-audio: pip install mlx-audio"
    )
    return "vllm"


def get_system_info(backend: str) -> SystemInfo:
    """Gather system information for health/status reporting."""
    return SystemInfo(
        os=platform.system().lower(),
        arch=platform.machine(),
        machine=platform.processor() or platform.machine(),
        gpu=_detect_gpu(),
        ram_gb=round(_get_ram_gb(), 1),
        backend=backend,
        python_version=platform.python_version(),
    )
