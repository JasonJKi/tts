"use client";

import { Voice, api } from "@/lib/api";
import AudioPlayer from "./AudioPlayer";

interface VoiceCardProps {
  voice: Voice;
  onDelete?: (id: string) => void;
  onSelect?: (voice: Voice) => void;
  selected?: boolean;
}

export default function VoiceCard({
  voice,
  onDelete,
  onSelect,
  selected,
}: VoiceCardProps) {
  return (
    <div
      className={`rounded-xl border p-4 transition-colors ${
        selected
          ? "border-[var(--primary)] bg-[var(--primary)]/10"
          : "border-[var(--border)] bg-[var(--card)] hover:border-[var(--muted-foreground)]"
      } ${onSelect ? "cursor-pointer" : ""}`}
      onClick={() => onSelect?.(voice)}
    >
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-semibold">{voice.name}</h3>
        <span className="rounded bg-[var(--muted)] px-2 py-0.5 text-xs text-[var(--muted-foreground)]">
          {voice.language.toUpperCase()}
        </span>
      </div>

      {voice.description && (
        <p className="mb-3 text-sm text-[var(--muted-foreground)]">
          {voice.description}
        </p>
      )}

      {voice.audio_duration_s && (
        <p className="mb-3 text-xs text-[var(--muted-foreground)]">
          Reference: {voice.audio_duration_s.toFixed(1)}s
        </p>
      )}

      <AudioPlayer src={api.getVoicePreviewUrl(voice.id)} />

      {onDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(voice.id);
          }}
          className="mt-3 text-xs text-[var(--destructive)] hover:underline"
        >
          Delete
        </button>
      )}
    </div>
  );
}
