const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Item = {
  id: string;
  task: string;
  owner: string | null;
  due_date: string | null;
  due_text: string | null;
  evidence_quote: string;
  confidence: string;
  flagged: boolean;
  decision: string;
  external_id: string | null;
};

export type Meeting = {
  id: string;
  title: string;
  status: string;
  created_at: string;
};

export type MeetingDetail = Meeting & {
  error: string | null;
  items: Item[];
};

export type DecisionIn = {
  id: string;
  decision: "approved" | "rejected";
  task: string;
  owner: string | null;
  due_date: string | null;
};

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const api = {
  list: () => fetch(`${BASE}/meetings`).then((r) => json<Meeting[]>(r)),
  get: (id: string) => fetch(`${BASE}/meetings/${id}`).then((r) => json<MeetingDetail>(r)),
  create: (fd: FormData) =>
    fetch(`${BASE}/meetings`, { method: "POST", body: fd }).then((r) => json<{ id: string }>(r)),
  approve: (id: string, decisions: DecisionIn[]) =>
    fetch(`${BASE}/meetings/${id}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(decisions),
    }).then((r) => json<{ ok: boolean }>(r)),
};
