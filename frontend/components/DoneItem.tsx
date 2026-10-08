"use client";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, Item } from "@/lib/api";

export default function DoneItem({ meetingId, item }: { meetingId: string; item: Item }) {
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [task, setTask] = useState(item.task);
  const [owner, setOwner] = useState(item.owner ?? "");
  const [due, setDue] = useState(item.due_date ?? "");

  const save = useMutation({
    mutationFn: () =>
      api.update(meetingId, item.id, { task, owner: owner || null, due_date: due || null }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["meeting", meetingId] });
      setEditing(false);
    },
  });

  const cancel = () => {
    setTask(item.task);
    setOwner(item.owner ?? "");
    setDue(item.due_date ?? "");
    setEditing(false);
  };

  const canEdit = item.decision === "approved" && !!item.external_id;
  const field = "w-full rounded border p-1";

  if (!editing) {
    return (
      <li className="flex items-start justify-between gap-3 rounded border p-3">
        <div>
          <span className="font-medium">{item.task}</span>
          <p className="text-sm text-gray-600">
            {item.decision}
            {item.external_id ? ", card created" : ""}
            {item.owner ? ` · ${item.owner}` : ""}
            {item.due_date ? ` · due ${item.due_date}` : ""}
          </p>
        </div>
        {canEdit && (
          <button className="text-sm underline" onClick={() => setEditing(true)}>
            Edit
          </button>
        )}
      </li>
    );
  }

  return (
    <li className="space-y-2 rounded border p-3">
      <input className={field} value={task} onChange={(e) => setTask(e.target.value)} />
      <div className="flex gap-2">
        <input
          className={field}
          placeholder="Owner"
          value={owner}
          onChange={(e) => setOwner(e.target.value)}
        />
        <input className={field} type="date" value={due} onChange={(e) => setDue(e.target.value)} />
      </div>
      <div className="flex gap-2">
        <button
          className="rounded bg-black px-3 py-1 text-white disabled:opacity-50"
          disabled={save.isPending || !task.trim()}
          onClick={() => save.mutate()}
        >
          {save.isPending ? "Saving..." : "Save"}
        </button>
        <button className="rounded border px-3 py-1" onClick={cancel}>
          Cancel
        </button>
      </div>
      {save.error && <p className="text-sm text-red-600">{String(save.error)}</p>}
    </li>
  );
}
