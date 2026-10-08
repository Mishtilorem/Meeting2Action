"use client";

import { Suspense } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import ReviewTable from "@/components/ReviewTable";
import DoneItem from "@/components/DoneItem";
import StatusStepper from "@/components/StatusStepper";

const STEPS = ["queued", "transcribing", "extracting", "verifying", "awaiting_approval", "executing", "done"];
const STOP = ["awaiting_approval", "done", "failed"];

function MeetingContent() {
  const params = useParams<{ id: string }>();
  const id = params?.id;

  const { data, error } = useQuery({
    queryKey: ["meeting", id],
    queryFn: () => api.get(id!),
    enabled: Boolean(id),
    refetchInterval: (q) => (STOP.includes(q.state.data?.status ?? "") ? false : 2000),
  });

  if (error) return <p className="p-6 text-red-600">{String(error)}</p>;
  if (!data) return <p className="p-6">Loading meeting state...</p>;

  const current = STEPS.indexOf(data.status);

  return (
    <main className="mx-auto max-w-4xl space-y-6 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">{data.title}</h1>
        <StatusStepper status={data.status} />
      </div>

      {data.status === "failed" && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <p className="font-semibold">Pipeline Error</p>
          <p>{data.error}</p>
        </div>
      )}

      {data.status === "awaiting_approval" && <ReviewTable meetingId={id!} items={data.items} />}

      {data.status === "done" && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Final Executed Action Items</h2>
          <ul className="space-y-2">
            {data.items.map((i) => (
              <DoneItem key={i.id} meetingId={id!} item={i} />
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}

export default function MeetingPage() {
  return (
    <Suspense fallback={<p className="p-6">Loading meeting...</p>}>
      <MeetingContent />
    </Suspense>
  );
}


