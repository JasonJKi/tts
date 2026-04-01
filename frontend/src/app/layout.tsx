import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Voxtral TTS",
  description: "Self-hosted text-to-speech platform powered by Voxtral",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased">
        <nav className="border-b border-[var(--border)] px-6 py-4">
          <div className="mx-auto flex max-w-7xl items-center justify-between">
            <a href="/" className="text-xl font-bold text-[var(--accent)]">
              Voxtral TTS
            </a>
            <div className="flex gap-6 text-sm">
              <a href="/" className="text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors">
                Playground
              </a>
              <a href="/voices" className="text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors">
                Voices
              </a>
              <a href="/clone" className="text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors">
                Clone
              </a>
            </div>
          </div>
        </nav>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
