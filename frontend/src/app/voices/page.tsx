"use client";

import { useEffect, useState } from "react";
import { api, Voice } from "@/lib/api";
import VoiceCard from "@/components/VoiceCard";

export default function VoicesPage() {
  const [voices, setVoices] = useState<Voice[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchVoices = async () => {
    try {
      const res = await api.listVoices();
      setVoices(res.voices);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVoices();
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this voice?")) return;
    try {
      await api.deleteVoice(id);
      setVoices((prev) => prev.filter((v) => v.id !== id));
    } catch {
      // ignore
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Voice Library</h1>
          <p className="mt-2 text-[var(--muted-foreground)]">
            Browse and manage your cloned voices.
          </p>
        </div>
        <a
          href="/clone"
          className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:opacity-90 transition-opacity"
        >
          Clone New Voice
        </a>
      </div>

      {loading ? (
        <p className="text-[var(--muted-foreground)]">Loading voices...</p>
      ) : voices.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--border)] p-12 text-center">
          <p className="text-[var(--muted-foreground)]">
            No custom voices yet.{" "}
            <a href="/clone" className="text-[var(--primary)] hover:underline">
              Clone your first voice
            </a>
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {voices.map((voice) => (
            <VoiceCard key={voice.id} voice={voice} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
}
