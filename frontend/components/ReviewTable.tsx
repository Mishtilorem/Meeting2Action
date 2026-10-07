"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, Item } from "@/lib/api";

type Row = Item & { choice: "approved" | "rejected" };

export default function ReviewTable({ meetingId, items }: { meetingId: string; items: Item[] }) {
  const qc = useQueryClient();
  const [rows, setRows] = useState<Row[]>(
    items.map((i) => ({ ...i, choice: i.flagged ? "rejected" : "approved" }))
  );

  const update = (idx: number, patch: Partial<Row>) =>
    setRows((rs) => rs.map((r, i) => (i === idx ? { ...r, ...patch } : r)));

  const submit = useMutation({
    mutationFn: () =>
      api.approve(
        meetingId,
        rows.map((r) => ({
          id: r.id,
          decision: r.choice,
          task: r.task,
          owner: r.owner,
          due_date: r.due_date,
        }))
      ),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["meeting", meetingId] }),
  });

  if (rows.length === 0) return <p className="text-gray-500">No action items found.</p>;
  const cell = "w-full rounded border border-gray-300 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">Proposed Action Items (Human Review)</h2>
      {rows.map((r, i) => (
        <div
          key={r.id}
          className={`space-y-3 rounded-lg border p-4 shadow-sm transition-all ${
            r.choice === "rejected" ? "bg-gray-50 opacity-60" : "bg-white"
          }`}
        >
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Task Title</label>
            <input className={cell} value={r.task} onChange={(e) => update(i, { task: e.target.value })} />
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-gray-500 mb-1">Owner</label>
              <input
                className={cell}
                placeholder="Unassigned"
                value={r.owner ?? ""}
                onChange={(e) => update(i, { owner: e.target.value || null })}
              />
            </div>
            <div className="flex-1">
              <label className="block text-xs font-semibold text-gray-500 mb-1">Due Date</label>
              <input
                className={cell}
                type="date"
                value={r.due_date ?? ""}
                onChange={(e) => update(i, { due_date: e.target.value || null })}
              />
            </div>
            <div className="w-full sm:w-36">
              <label className="block text-xs font-semibold text-gray-500 mb-1">Decision</label>
              <select
                className="w-full rounded border border-gray-300 p-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={r.choice}
                onChange={(e) => update(i, { choice: e.target.value as Row["choice"] })}
              >
                <option value="approved">Approve</option>
                <option value="rejected">Reject</option>
              </select>
            </div>
          </div>

          <div className="rounded bg-blue-50/60 p-2.5 text-xs text-gray-700">
            <span className="font-semibold text-blue-900">Verbatim Quote: </span>
            <span className="italic">"{r.evidence_quote}"</span>{" "}
            {r.flagged && (
              <span className="ml-2 inline-flex items-center rounded bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800">
                needs check
              </span>
            )}
          </div>
        </div>
      ))}

      <button
        className="rounded bg-black px-5 py-2.5 font-medium text-white shadow-sm hover:bg-gray-800 disabled:opacity-50"
        disabled={submit.isPending}
        onClick={() => submit.mutate()}
      >
        {submit.isPending ? "Submitting Review..." : "Submit Review"}
      </button>
      {submit.error && <p className="text-sm text-red-600">{String(submit.error)}</p>}
    </div>
  );
}
