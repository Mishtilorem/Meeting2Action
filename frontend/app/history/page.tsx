"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function History() {
  const { data, isLoading, error } = useQuery({ queryKey: ["meetings"], queryFn: api.list });

  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <h1 className="text-2xl font-bold tracking-tight">Meeting History</h1>
      {isLoading && <p className="text-sm text-gray-500">Loading history...</p>}
      {error && <p className="text-sm text-red-600">{String(error)}</p>}
      {data?.length === 0 && <p className="text-sm text-gray-500">No meetings recorded yet.</p>}
      <div className="space-y-2">
        {data?.map((m) => (
          <Link
            key={m.id}
            href={`/meetings/${m.id}`}
            className="flex items-center justify-between rounded-lg border bg-white p-4 shadow-sm hover:border-blue-500 transition-colors"
          >
            <div>
              <p className="font-semibold text-gray-900">{m.title}</p>
              <p className="text-xs text-gray-500">{new Date(m.created_at).toLocaleString()}</p>
            </div>
            <span className="rounded bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-700 capitalize">
              {m.status.replace("_", " ")}
            </span>
          </Link>
        ))}
      </div>
    </main>
  );
}
