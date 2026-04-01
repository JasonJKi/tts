"use client";

import { useState, useRef, useCallback } from "react";

interface AudioUploaderProps {
  onUpload: (file: File) => void;
  maxDurationS?: number;
  minDurationS?: number;
}

export default function AudioUploader({
  onUpload,
  maxDurationS = 30,
  minDurationS = 2,
}: AudioUploaderProps) {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndSet = useCallback(
    (f: File) => {
      setError(null);

      if (!f.type.startsWith("audio/")) {
        setError("Please upload an audio file");
        return;
      }

      if (f.size > 50 * 1024 * 1024) {
        setError("File too large (max 50MB)");
        return;
      }

      // Check duration via Audio element
      const url = URL.createObjectURL(f);
      const audio = new Audio(url);
      audio.onloadedmetadata = () => {
        if (audio.duration < minDurationS) {
          setError(`Audio too short (min ${minDurationS}s)`);
          URL.revokeObjectURL(url);
          return;
        }
        if (audio.duration > maxDurationS) {
          setError(`Audio too long (max ${maxDurationS}s)`);
          URL.revokeObjectURL(url);
          return;
        }
        setFile(f);
        setPreviewUrl(url);
        onUpload(f);
      };
      audio.onerror = () => {
        setError("Could not read audio file");
        URL.revokeObjectURL(url);
      };
    },
    [maxDurationS, minDurationS, onUpload]
  );

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) validateAndSet(f);
  };

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition-colors ${
          dragOver
            ? "border-[var(--primary)] bg-[var(--primary)]/5"
            : "border-[var(--border)] hover:border-[var(--muted-foreground)]"
        }`}
      >
        <svg
          className="mb-3 h-10 w-10 text-[var(--muted-foreground)]"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z"
          />
        </svg>
        <p className="text-sm text-[var(--muted-foreground)]">
          {file ? file.name : "Drop audio file or click to browse"}
        </p>
        <p className="mt-1 text-xs text-[var(--muted-foreground)]">
          WAV, MP3, FLAC, OGG ({minDurationS}-{maxDurationS}s)
        </p>
        <input
          ref={inputRef}
          type="file"
          accept="audio/*"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) validateAndSet(f);
          }}
        />
      </div>

      {error && (
        <p className="mt-2 text-sm text-[var(--destructive)]">{error}</p>
      )}

      {previewUrl && (
        <div className="mt-3">
          <audio controls src={previewUrl} className="w-full" />
        </div>
      )}
    </div>
  );
}
