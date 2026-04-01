"use client";

import { useState } from "react";
import { BUILTIN_VOICES } from "@/lib/api";

interface TTSFormProps {
  onGenerate: (text: string, voiceId: string, options: { language: string; speed: number }) => void;
  onStream: (text: string, voiceId: string, options: { language: string; speed: number }) => void;
  loading?: boolean;
  streaming?: boolean;
  onStopStream?: () => void;
  customVoices?: { id: string; name: string }[];
}

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

export default function TTSForm({
  onGenerate,
  onStream,
  loading,
  streaming,
  onStopStream,
  customVoices = [],
}: TTSFormProps) {
  const [text, setText] = useState("");
  const [voiceId, setVoiceId] = useState<string>(BUILTIN_VOICES[0]);
  const [language, setLanguage] = useState("en");
  const [speed, setSpeed] = useState(1.0);

  const options = { language, speed };

  return (
    <div className="space-y-4">
      {/* Text input */}
      <div>
        <label className="mb-1 block text-sm font-medium">Text</label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to synthesize..."
          rows={4}
          maxLength={5000}
          className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3 text-sm focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)] resize-none"
        />
        <p className="mt-1 text-xs text-[var(--muted-foreground)]">
          {text.length}/5000 characters
        </p>
      </div>

      {/* Settings row */}
      <div className="grid grid-cols-3 gap-4">
        {/* Voice selector */}
        <div>
          <label className="mb-1 block text-sm font-medium">Voice</label>
          <select
            value={voiceId}
            onChange={(e) => setVoiceId(e.target.value)}
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-sm focus:border-[var(--primary)] focus:outline-none"
          >
            <optgroup label="Built-in">
              {BUILTIN_VOICES.map((v) => (
                <option key={v} value={v}>
                  {v.replace("_", " ")}
                </option>
              ))}
            </optgroup>
            {customVoices.length > 0 && (
              <optgroup label="Custom">
                {customVoices.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </optgroup>
            )}
          </select>
        </div>

        {/* Language */}
        <div>
          <label className="mb-1 block text-sm font-medium">Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-sm focus:border-[var(--primary)] focus:outline-none"
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        {/* Speed */}
        <div>
          <label className="mb-1 block text-sm font-medium">
            Speed: {speed.toFixed(1)}x
          </label>
          <input
            type="range"
            min="0.25"
            max="4.0"
            step="0.25"
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="mt-2 w-full"
          />
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => onGenerate(text, voiceId, options)}
          disabled={!text.trim() || loading || streaming}
          className="rounded-lg bg-[var(--primary)] px-6 py-2.5 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          {loading ? "Generating..." : "Generate"}
        </button>
        <button
          onClick={() =>
            streaming ? onStopStream?.() : onStream(text, voiceId, options)
          }
          disabled={!text.trim() || loading}
          className="rounded-lg border border-[var(--primary)] px-6 py-2.5 text-sm font-medium text-[var(--primary)] hover:bg-[var(--primary)]/10 disabled:opacity-50 transition-colors"
        >
          {streaming ? "Stop" : "Stream"}
        </button>
      </div>
    </div>
  );
}
