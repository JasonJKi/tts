"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AudioUploader from "@/components/AudioUploader";
import { api } from "@/lib/api";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "fr", label: "French" },
  { code: "es", label: "Spanish" },
  { code: "pt", label: "Portuguese" },
  { code: "it", label: "Italian" },
  { code: "nl", label: "Dutch" },
  { code: "de", label: "German" },
  { code: "hi", label: "Hindi" },
  { code: "ar", label: "Arabic" },
];

export default function ClonePage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [language, setLanguage] = useState("en");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!audioFile || !name.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("name", name.trim());
      formData.append("description", description.trim());
      formData.append("language", language);
      formData.append("audio", audioFile);

      await api.createVoice(formData);
      router.push("/voices");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create voice");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Clone a Voice</h1>
        <p className="mt-2 text-[var(--muted-foreground)]">
          Upload a reference audio clip (2-30 seconds) to create a new voice
          clone. The model works best with 5-25 seconds of clear speech.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Audio upload */}
        <div>
          <label className="mb-2 block text-sm font-medium">
            Reference Audio
          </label>
          <AudioUploader onUpload={setAudioFile} />
        </div>

        {/* Name */}
        <div>
          <label className="mb-1 block text-sm font-medium">Voice Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Professional Narrator"
            maxLength={100}
            required
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2.5 text-sm focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
          />
        </div>

        {/* Description */}
        <div>
          <label className="mb-1 block text-sm font-medium">
            Description (optional)
          </label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g. Warm, authoritative male voice"
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2.5 text-sm focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
          />
        </div>

        {/* Language */}
        <div>
          <label className="mb-1 block text-sm font-medium">Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2.5 text-sm focus:border-[var(--primary)] focus:outline-none"
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div className="rounded-lg border border-[var(--destructive)] bg-[var(--destructive)]/10 p-4 text-sm text-[var(--destructive)]">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={!audioFile || !name.trim() || loading}
          className="w-full rounded-lg bg-[var(--primary)] py-3 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          {loading ? "Creating Voice..." : "Create Voice"}
        </button>
      </form>
    </div>
  );
}
