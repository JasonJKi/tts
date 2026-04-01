"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, Voice } from "@/lib/api";
import AudioPlayer from "@/components/AudioPlayer";

export default function VoiceDetailPage() {
  const params = useParams();
  const [voice, setVoice] = useState<Voice | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = params.id as string;
    api
      .getVoice(id)
      .then(setVoice)
      .catch(() => setError("Voice not found"));
  }, [params.id]);

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-[var(--destructive)]">{error}</p>
        <a href="/voices" className="mt-4 text-sm text-[var(--primary)] hover:underline">
          Back to voices
        </a>
      </div>
    );
  }

  if (!voice) {
    return <p className="text-[var(--muted-foreground)]">Loading...</p>;
  }

  return (
    <div className="max-w-2xl space-y-6">
      <a href="/voices" className="text-sm text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
        &larr; Back to voices
      </a>

      <div>
        <h1 className="text-3xl font-bold">{voice.name}</h1>
        {voice.description && (
          <p className="mt-2 text-[var(--muted-foreground)]">
            {voice.description}
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="rounded-lg bg-[var(--muted)] p-3">
          <p className="text-[var(--muted-foreground)]">Language</p>
          <p className="font-medium">{voice.language.toUpperCase()}</p>
        </div>
        <div className="rounded-lg bg-[var(--muted)] p-3">
          <p className="text-[var(--muted-foreground)]">Duration</p>
          <p className="font-medium">
            {voice.audio_duration_s ? `${voice.audio_duration_s.toFixed(1)}s` : "N/A"}
          </p>
        </div>
        <div className="rounded-lg bg-[var(--muted)] p-3">
          <p className="text-[var(--muted-foreground)]">Created</p>
          <p className="font-medium">
            {new Date(voice.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="rounded-lg bg-[var(--muted)] p-3">
          <p className="text-[var(--muted-foreground)]">ID</p>
          <p className="font-mono text-xs">{voice.id}</p>
        </div>
      </div>

      <div>
        <h2 className="mb-2 text-lg font-semibold">Reference Audio</h2>
        <AudioPlayer src={api.getVoicePreviewUrl(voice.id)} />
      </div>

      <a
        href={`/?voice=${voice.id}`}
        className="inline-block rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:opacity-90"
      >
        Use in Playground
      </a>
    </div>
  );
}
