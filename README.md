# Voxtral TTS Platform

Self-hosted text-to-speech platform powered by [Voxtral-4B-TTS-2603](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603), Mistral's open-weight TTS model.

## Features

- **Auto-detecting backend**: Automatically selects MLX (Mac) or vLLM-Omni (Linux+NVIDIA)
- **Real-time streaming TTS** via WebSocket with sub-100ms time-to-first-audio
- **Voice cloning** from 2-30 seconds of reference audio (zero-shot)
- **9 languages**: English, French, Spanish, Portuguese, Italian, Dutch, German, Hindi, Arabic
- **REST + WebSocket API** for integration
- **Web playground** for interactive TTS generation and voice management

## Architecture

```
Frontend (Next.js :3000)
    ↕ HTTP / WebSocket
Backend (FastAPI :8000)
    ↕
┌─────────── auto-detected ───────────┐
│  Mac: MLX in-process (mlx-audio)    │
│  Linux: vLLM-Omni HTTP (:8091)     │
└─────────────────────────────────────┘
    ↕
Voxtral-4B-TTS-2603
```

## Quick Start

### Mac (Apple Silicon)

```bash
# 1. Install backend with MLX support
cd backend
pip install -e ".[mlx]"

# 2. Start the backend (auto-detects Apple Silicon + MLX)
uvicorn app.main:app --reload --port 8000

# 3. In another terminal, start the frontend
cd frontend
npm install
npm run dev

# Open http://localhost:3000
```

The backend will auto-detect Apple Silicon and use `mlx-audio` with the
`mlx-community/Voxtral-4B-TTS-2603-mlx-4bit` model (downloads on first run).

### Linux (NVIDIA GPU)

```bash
# 1. Start the model server
pip install vllm-omni
vllm serve mistralai/Voxtral-4B-TTS-2603 \
  --stage-configs-path vllm_omni/model_executor/stage_configs/voxtral_tts.yaml \
  --omni --port 8091 --trust-remote-code --enforce-eager

# 2. Start the backend (auto-detects NVIDIA GPU + vLLM)
cd backend
pip install -e .
uvicorn app.main:app --reload --port 8000

# 3. Start the frontend
cd frontend
npm install
npm run dev
```

### Docker

```bash
# Mac (no GPU passthrough needed)
docker compose up backend frontend --build

# Linux with NVIDIA GPU (includes vLLM-Omni model server)
docker compose --profile gpu up --build
```

## Environment Variables

Override auto-detection with `TTS_BACKEND`:

```bash
TTS_BACKEND=mlx   # Force MLX backend (Mac)
TTS_BACKEND=vllm  # Force vLLM backend (Linux)
TTS_BACKEND=auto  # Auto-detect (default)
```

See `.env.example` for all configuration options.

## API Reference

### HTTP Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check + system info |
| `POST` | `/api/v1/voices` | Create voice (multipart form) |
| `GET` | `/api/v1/voices` | List voices |
| `GET` | `/api/v1/voices/{id}` | Get voice |
| `DELETE` | `/api/v1/voices/{id}` | Delete voice |
| `GET` | `/api/v1/voices/{id}/preview` | Download reference audio |
| `GET` | `/api/v1/voices/builtin` | List built-in voices |
| `POST` | `/api/v1/tts` | Generate TTS (returns audio) |
| `POST` | `/api/v1/tts/stream` | Stream TTS (chunked response) |

### WebSocket

```
WS /api/v1/ws/tts

→ {"text": "Hello", "voice_id": "casual_male", "output_format": "pcm"}
← [binary audio chunks]
← {"type": "done"}
```

### Built-in Voices

`casual_male`, `casual_female`, `neutral_male`, `neutral_female`, `cheerful_male`, `cheerful_female`, `expressive_male`, `expressive_female`

## Hardware Requirements

| Platform | Minimum | Recommended |
|----------|---------|-------------|
| Mac (MLX) | M1, 8GB unified RAM | M3 Pro+, 16GB |
| Linux (vLLM) | NVIDIA GPU, 8GB VRAM | 16GB+ VRAM |

## License

Platform code: MIT. Voxtral model weights: CC BY NC 4.0.
