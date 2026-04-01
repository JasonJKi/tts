"use client";

import { useState, useCallback } from "react";
import { api } from "@/lib/api";

export function useTTS() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const generate = useCallback(
    async (
      text: string,
      voiceId: string,
      options?: { language?: string; speed?: number }
    ) => {
      setLoading(true);
      setError(null);

      // Revoke previous URL
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
        setAudioUrl(null);
      }

      try {
        const blob = await api.synthesize(text, voiceId, options);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        return url;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "TTS failed";
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [audioUrl]
  );

  const reset = useCallback(() => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setError(null);
  }, [audioUrl]);

  return { generate, loading, error, audioUrl, reset };
}
