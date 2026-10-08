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
  const [formKey, setFormKey] = useState(0);

  const create = useMutation({
    mutationFn: () => {
      const fd = new FormData();
      fd.append("title", title || "Untitled");
      fd.append("attendees", attendees);
      if (transcript) fd.append("transcript", transcript);
      if (file) fd.append("file", file);
      return api.create(fd);
    },
    onSuccess: (r) => {
      setTitle("");
      setAttendees("");
      setTranscript("");
      setFile(null);
      setFormKey((k) => k + 1);
      router.push(`/meetings/${r.id}`);
    },
  });

  const label = "mb-1 block text-sm font-medium text-slate-700";
  const canSubmit = (!!file || !!transcript.trim()) && !create.isPending;

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-semibold text-slate-900">New meeting</h1>
      <p className="mt-1 text-sm text-slate-500">
        Upload a recording or paste a transcript. You review everything before any card is created.
      </p>

      <form
        autoComplete="off"
        onSubmit={(e) => { e.preventDefault(); create.mutate(); }}
        className="mt-6 space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div>
          <label htmlFor="title" className={label}>Title</label>
          <input id="title" name="title" autoComplete="off" className="w-full"
            placeholder="Q4 launch planning" value={title}
            onChange={(e) => setTitle(e.target.value)} />
        </div>

        <div>
          <label htmlFor="attendees" className={label}>Attendees</label>
          <input id="attendees" name="attendees" autoComplete="off" className="w-full"
            placeholder="Priya, Rahul, Ananya" value={attendees}
            onChange={(e) => setAttendees(e.target.value)} />
          <p className="mt-1 text-xs text-slate-400">Comma separated. Used to match task owners.</p>
        </div>

        <div>
          <label htmlFor="audio" className={label}>Audio file</label>
          <input key={formKey} id="audio" type="file" accept="audio/*" className="w-full text-sm"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        </div>

        <div className="flex items-center gap-3 text-xs uppercase tracking-wide text-slate-400">
          <span className="h-px flex-1 bg-slate-200" /> or <span className="h-px flex-1 bg-slate-200" />
        </div>

        <div>
          <label htmlFor="transcript" className={label}>Transcript</label>
          <textarea id="transcript" name="transcript" autoComplete="off" rows={8}
            className="w-full" placeholder="Paste the meeting transcript here"
            value={transcript} onChange={(e) => setTranscript(e.target.value)} />
        </div>

        <button type="submit" disabled={!canSubmit}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50">
          {create.isPending && (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
          )}
          {create.isPending ? "Uploading..." : "Process meeting"}
        </button>

        {create.error && (
          <p className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {String(create.error)}
          </p>
        )}
      </form>
    </main>
  );
}