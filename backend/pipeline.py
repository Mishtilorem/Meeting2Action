import os, sys, asyncio
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from db import set_status, save_items, audit, conn
from llm import Budget
from extraction import extract
from verify import verify
from transcribe import transcribe
from trello import build_notes

GRAPH = None
SERVER = os.path.join(os.path.dirname(__file__), "mcp_server.py")

class State(TypedDict):
    meeting_id: str
    audio_path: Optional[str]
    transcript: Optional[str]
    attendees: list[str]
    meeting_date: str
    items: list[dict]
    decisions: list[dict]

def transcribe_node(s):
    set_status(s["meeting_id"], "transcribing")
    if s.get("transcript"):
        return {}
    text = transcribe(s["audio_path"])
    with conn() as c:
        c.execute("UPDATE meetings SET transcript=%s WHERE id=%s", (text, s["meeting_id"]))
    try:
        if s.get("audio_path"):
            os.remove(s["audio_path"])
    except OSError:
        pass
    return {"transcript": text}

def extract_node(s):
    set_status(s["meeting_id"], "extracting")
    budget = Budget(int(os.getenv("RUN_TOKEN_BUDGET", "60000")))
    ext = extract(s["transcript"], budget)
    return {"items": [i.model_dump() for i in ext.action_items]}

def verify_node(s):
    mid = s["meeting_id"]
    set_status(mid, "verifying")
    checked = verify(s["items"], s["transcript"], s["attendees"], s["meeting_date"])
    return {"items": save_items(mid, checked)}      # saved before the pause, so the UI can read them

def approve_node(s):
    mid = s["meeting_id"]
    if not s["items"]:
        audit(mid, "no_items")
        return {"decisions": []}
    set_status(mid, "awaiting_approval")
    decisions = interrupt({"meeting_id": mid})       # pauses here; resumes with the value passed in
    audit(mid, "reviewed", {"count": len(decisions)})
    return {"decisions": decisions}

async def _create_all(rows):
    params = StdioServerParameters(command=sys.executable, args=[SERVER], env=dict(os.environ))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for row in rows:
                args = {
                    "title": row["task"],
                    "notes": build_notes(row["owner"], row["evidence_quote"]),
                }
                if row.get("due_date"):
                    args["due"] = row["due_date"].isoformat() if hasattr(row["due_date"], "isoformat") else str(row["due_date"])
                res = await session.call_tool("create_task", args)
                with conn() as c:   # saved per card, so a retry skips cards already created
                    c.execute("UPDATE action_items SET external_id=%s WHERE id=%s",
                              (res.content[0].text, row["id"]))

def execute_node(s):
    mid = s["meeting_id"]
    set_status(mid, "executing")
    with conn() as c:
        rows = c.execute(
            "SELECT * FROM action_items WHERE meeting_id=%s AND decision='approved' AND external_id IS NULL",
            (mid,)).fetchall()
    if rows:
        asyncio.run(_create_all(rows))
    audit(mid, "executed", {"created": len(rows)})
    set_status(mid, "done")
    return {}

def build_graph(checkpointer):
    g = StateGraph(State)
    g.add_node("transcribe", transcribe_node)
    g.add_node("extract", extract_node)
    g.add_node("verify", verify_node)
    g.add_node("approve", approve_node)
    g.add_node("execute", execute_node)
    g.add_edge(START, "transcribe")
    g.add_edge("transcribe", "extract")
    g.add_edge("extract", "verify")
    g.add_edge("verify", "approve")
    g.add_edge("approve", "execute")
    g.add_edge("execute", END)
    return g.compile(checkpointer=checkpointer)

def init(saver):
    global GRAPH
    GRAPH = build_graph(saver)

def _invoke(payload, mid):
    try:
        GRAPH.invoke(payload, {"configurable": {"thread_id": mid}})
    except Exception as e:
        set_status(mid, "failed", str(e)[:500])
        audit(mid, "failed", {"error": str(e)[:500]})

def run(mid, audio_path, transcript, attendees, meeting_date):
    _invoke({"meeting_id": mid, "audio_path": audio_path, "transcript": transcript,
             "attendees": attendees, "meeting_date": str(meeting_date),
             "items": [], "decisions": []}, mid)

def resume(mid, decisions):
    _invoke(Command(resume=decisions), mid)
