"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [attendees, setAttendees] = useState("");
  const [transcript, setTranscript] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const create = useMutation({
    mutationFn: () => {
      const fd = new FormData();
      fd.append("title", title || "Untitled Meeting");
      fd.append("attendees", attendees);
      if (transcript) fd.append("transcript", transcript);
      if (file) fd.append("file", file);
      return api.create(fd);
    },
    onSuccess: (r) => router.push(`/meetings/${r.id}`),
  });

  const input = "w-full rounded border border-gray-300 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";

  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">New Meeting</h1>
        <p className="text-sm text-gray-500">
          Upload an audio recording or paste a transcript to extract verified action items.
        </p>
      </div>

      <div className="space-y-4 rounded-xl border bg-white p-6 shadow-sm">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">Meeting Title</label>
          <input className={input} placeholder="e.g. Q4 Strategy Sync" value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">Attendees</label>
          <input
            className={input}
            placeholder="e.g. Priya, Rahul, Alex (comma separated)"
            value={attendees}
            onChange={(e) => setAttendees(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">Audio File (MP3 / WAV / M4A)</label>
          <input
            type="file"
            accept="audio/*"
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">Transcript Text</label>
          <textarea
            className={input}
            rows={8}
            placeholder="...or paste a meeting transcript directly"
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
          />
        </div>

        <button
          className="w-full rounded-lg bg-black px-4 py-3 font-medium text-white shadow hover:bg-gray-800 disabled:opacity-50 transition-colors"
          disabled={create.isPending || (!file && !transcript)}
          onClick={() => create.mutate()}
        >
          {create.isPending ? "Processing Meeting..." : "Process Meeting"}
        </button>
        {create.error && <p className="text-sm text-red-600">{String(create.error)}</p>}
      </div>
    </main>
  );
}
