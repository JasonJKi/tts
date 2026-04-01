"use client";

import { useState, useRef, useCallback } from "react";
import { api } from "@/lib/api";

export function useStreamingTTS() {
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const nextStartTimeRef = useRef(0);

  const playChunk = useCallback((pcmData: ArrayBuffer) => {
    if (!audioCtxRef.current) return;

    const ctx = audioCtxRef.current;
    const sampleRate = 24000;
    const float32 = new Float32Array(pcmData);

    const buffer = ctx.createBuffer(1, float32.length, sampleRate);
    buffer.getChannelData(0).set(float32);

    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);

    const startTime = Math.max(ctx.currentTime, nextStartTimeRef.current);
    source.start(startTime);
    nextStartTimeRef.current = startTime + buffer.duration;
  }, []);

  const stream = useCallback(
    (
      text: string,
      voiceId: string,
      options?: { language?: string; speed?: number }
    ) => {
      setError(null);
      setStreaming(true);

      // Initialize AudioContext
      if (!audioCtxRef.current) {
        audioCtxRef.current = new AudioContext({ sampleRate: 24000 });
      }
      nextStartTimeRef.current = 0;

      const ws = new WebSocket(api.getStreamingUrl());
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(
          JSON.stringify({
            text,
            voice_id: voiceId,
            language: options?.language || "en",
            output_format: "pcm",
            speed: options?.speed || 1.0,
          })
        );
      };

      ws.onmessage = (event) => {
        if (typeof event.data === "string") {
          const msg = JSON.parse(event.data);
          if (msg.type === "done") {
            setStreaming(false);
          } else if (msg.type === "error") {
            setError(msg.detail);
            setStreaming(false);
          }
        } else if (event.data instanceof Blob) {
          event.data.arrayBuffer().then(playChunk);
        }
      };

      ws.onerror = () => {
        setError("WebSocket connection failed");
        setStreaming(false);
      };

      ws.onclose = () => {
        setStreaming(false);
      };
    },
    [playChunk]
  );

  const stop = useCallback(() => {
    wsRef.current?.close();
    setStreaming(false);
  }, []);

  return { stream, stop, streaming, error };
}
