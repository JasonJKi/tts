# Voxtral TTS Platform

Self-hosted text-to-speech platform powered by [Voxtral-4B-TTS-2603](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603), Mistral's open-weight TTS model.

## Features

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
    ↕ HTTP
Model Server (vLLM-Omni :8091)
    ↕
Voxtral-4B-TTS-2603 (GPU)
```

## Quick Start

### Prerequisites

- NVIDIA GPU with 16GB+ VRAM (or Mac with 8GB+ unified memory)
- Docker + Docker Compose (with NVIDIA Container Toolkit for GPU)
- Python 3.11+ and Node.js 22+ (for local dev)

### Docker (Recommended)

```bash
# Clone and start all services
docker compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Model server: http://localhost:8091
```

### Local Development

**1. Start the model server (vLLM-Omni):**

```bash
pip install vllm-omni
vllm serve mistralai/Voxtral-4B-TTS-2603 \
  --stage-configs-path vllm_omni/model_executor/stage_configs/voxtral_tts.yaml \
  --omni --port 8091 --trust-remote-code --enforce-eager
```

**2. Start the backend:**

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload --port 8000
```

**3. Start the frontend:**

```bash
cd frontend
npm install
npm run dev
```

## API Reference

### HTTP Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check |
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

## Configuration

Environment variables (prefix `TTS_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_VLLM_BASE_URL` | `http://localhost:8091` | vLLM-Omni server URL |
| `TTS_VLLM_MODEL` | `mistralai/Voxtral-4B-TTS-2603` | Model name |
| `TTS_DATABASE_URL` | `sqlite+aiosqlite:///./data/db/voxtral.db` | Database URL |
| `TTS_VOICES_DIR` | `data/voices` | Voice audio storage |
| `TTS_CORS_ORIGINS` | `["http://localhost:3000"]` | CORS origins |

## License

Platform code: MIT. Voxtral model weights: CC BY NC 4.0.
