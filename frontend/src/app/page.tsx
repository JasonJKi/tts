"use client";

import { useEffect, useState } from "react";
import TTSForm from "@/components/TTSForm";
import AudioPlayer from "@/components/AudioPlayer";
import { useTTS } from "@/hooks/useTTS";
import { useStreamingTTS } from "@/hooks/useStreamingTTS";
import { api, Voice } from "@/lib/api";

export default function PlaygroundPage() {
  const { generate, loading, error: ttsError, audioUrl } = useTTS();
  const {
    stream,
    stop,
    streaming,
    error: streamError,
  } = useStreamingTTS();
  const [customVoices, setCustomVoices] = useState<Voice[]>([]);

  useEffect(() => {
    api.listVoices().then((res) => setCustomVoices(res.voices)).catch(() => {});
  }, []);

  const handleGenerate = (
    text: string,
    voiceId: string,
    options: { language: string; speed: number }
  ) => {
    generate(text, voiceId, options);
  };

  const handleStream = (
    text: string,
    voiceId: string,
    options: { language: string; speed: number }
  ) => {
    stream(text, voiceId, options);
  };

  const error = ttsError || streamError;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">TTS Playground</h1>
        <p className="mt-2 text-[var(--muted-foreground)]">
          Generate speech from text using Voxtral. Choose a voice, type your
          text, and hit generate or stream for real-time playback.
        </p>
      </div>

      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
        <TTSForm
          onGenerate={handleGenerate}
          onStream={handleStream}
          loading={loading}
          streaming={streaming}
          onStopStream={stop}
          customVoices={customVoices.map((v) => ({ id: v.id, name: v.name }))}
        />
      </div>

      {error && (
        <div className="rounded-lg border border-[var(--destructive)] bg-[var(--destructive)]/10 p-4 text-sm text-[var(--destructive)]">
          {error}
        </div>
      )}

      {audioUrl && (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Generated Audio</h2>
          <AudioPlayer src={audioUrl} />
        </div>
      )}

      {streaming && (
        <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
          <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-[var(--primary)]" />
          Streaming audio...
        </div>
      )}
    </div>
  );
}
