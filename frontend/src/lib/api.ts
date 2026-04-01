const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export interface Voice {
  id: string;
  name: string;
  description: string;
  language: string;
  audio_duration_s: number | null;
  vllm_voice_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface VoiceListResponse {
  voices: Voice[];
  total: number;
}

export interface HealthResponse {
  status: string;
  model_server: string;
  model: string;
  version: string;
}

// Built-in voices
export const BUILTIN_VOICES = [
  "casual_male",
  "casual_female",
  "neutral_male",
  "neutral_female",
  "cheerful_male",
  "cheerful_female",
  "expressive_male",
  "expressive_female",
] as const;

export const api = {
  // Health
  async health(): Promise<HealthResponse> {
    const res = await fetch(`${API_URL}/api/v1/health`);
    return res.json();
  },

  // Voices
  async listVoices(): Promise<VoiceListResponse> {
    const res = await fetch(`${API_URL}/api/v1/voices`);
    return res.json();
  },

  async getVoice(id: string): Promise<Voice> {
    const res = await fetch(`${API_URL}/api/v1/voices/${id}`);
    if (!res.ok) throw new Error("Voice not found");
    return res.json();
  },

  async createVoice(data: FormData): Promise<Voice> {
    const res = await fetch(`${API_URL}/api/v1/voices`, {
      method: "POST",
      body: data,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to create voice");
    }
    return res.json();
  },

  async deleteVoice(id: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/v1/voices/${id}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete voice");
  },

  getVoicePreviewUrl(id: string): string {
    return `${API_URL}/api/v1/voices/${id}/preview`;
  },

  // TTS
  async synthesize(
    text: string,
    voiceId: string,
    options?: { language?: string; output_format?: string; speed?: number }
  ): Promise<Blob> {
    const res = await fetch(`${API_URL}/api/v1/tts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        voice_id: voiceId,
        language: options?.language || "en",
        output_format: options?.output_format || "wav",
        speed: options?.speed || 1.0,
      }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "TTS failed");
    }
    return res.blob();
  },

  // WebSocket URL for streaming TTS
  getStreamingUrl(): string {
    return `${WS_URL}/api/v1/ws/tts`;
  },
};
