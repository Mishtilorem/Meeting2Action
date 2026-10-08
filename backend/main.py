import os, uuid, shutil, tempfile
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from datetime import date
from contextlib import asynccontextmanager
from typing import Literal, Optional
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.checkpoint.postgres import PostgresSaver

import pipeline
from db import conn, audit
from mcp_client import call_tool
from trello import build_notes

@asynccontextmanager
async def lifespan(app):
    pool = ConnectionPool(
        conninfo=os.environ["DATABASE_URL"],
        min_size=1,
        max_size=5,
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
        check=ConnectionPool.check_connection,
        open=True,
    )
    saver = PostgresSaver(pool)
    saver.setup()
    pipeline.init(saver)
    yield
    pool.close()

app = FastAPI(title="Meeting-to-Action API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url or "user:password" in db_url:
        return {
            "status": "ok",
            "db": "not_configured",
            "message": "DATABASE_URL is using placeholder. Provide a valid Neon or Supabase connection string in backend/.env"
        }
    try:
        with conn() as c:
            c.execute("SELECT 1")
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": "failed", "details": str(e)}

@app.post("/meetings")
async def create_meeting(
    bg: BackgroundTasks,
    title: str = Form("Untitled"),
    attendees: str = Form(""),
    transcript: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    if not transcript and not file:
        raise HTTPException(400, "Provide a transcript or an audio file")
    mid = str(uuid.uuid4())
    names = [a.strip() for a in attendees.split(",") if a.strip()]
    path = None
    if file:
        path = os.path.join(tempfile.gettempdir(), f"{mid}_{file.filename}")
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    with conn() as c:
        row = c.execute(
            "INSERT INTO meetings (id, title, attendees, transcript) VALUES (%s,%s,%s,%s) RETURNING meeting_date",
            (mid, title, names, transcript)).fetchone()
    audit(mid, "created", {"title": title})
    bg.add_task(pipeline.run, mid, path, transcript, names, row["meeting_date"])
    return {"id": mid}

@app.get("/meetings")
def list_meetings():
    with conn() as c:
        return c.execute(
            "SELECT id, title, status, created_at FROM meetings ORDER BY created_at DESC LIMIT 50"
        ).fetchall()

@app.get("/meetings/{mid}")
def get_meeting(mid: str):
    with conn() as c:
        m = c.execute("SELECT * FROM meetings WHERE id=%s", (mid,)).fetchone()
        if not m:
            raise HTTPException(404, "Not found")
        items = c.execute("SELECT * FROM action_items WHERE meeting_id=%s ORDER BY task", (mid,)).fetchall()
    return {**m, "items": items}

class Decision(BaseModel):
    id: str
    decision: Literal["approved", "rejected"]
    task: str
    owner: Optional[str] = None
    due_date: Optional[str] = None

@app.post("/meetings/{mid}/approve")
def approve(mid: str, decisions: list[Decision], bg: BackgroundTasks):
    with conn() as c:
        m = c.execute("SELECT status FROM meetings WHERE id=%s", (mid,)).fetchone()
        if not m:
            raise HTTPException(404, "Not found")
        if m["status"] != "awaiting_approval":
            raise HTTPException(409, "Meeting is not awaiting approval")
        for d in decisions:
            c.execute(
                "UPDATE action_items SET task=%s, owner=%s, due_date=%s::date, decision=%s "
                "WHERE id=%s AND meeting_id=%s",
                (d.task, d.owner, d.due_date or None, d.decision, d.id, mid))
        c.execute("UPDATE meetings SET status='executing' WHERE id=%s", (mid,))  # blocks double-submit
    audit(mid, "approved", {"approved": sum(d.decision == "approved" for d in decisions),
                            "rejected": sum(d.decision == "rejected" for d in decisions)})
    bg.add_task(pipeline.resume, mid, [d.model_dump() for d in decisions])
    return {"ok": True}

class ItemEdit(BaseModel):
    task: str
    owner: Optional[str] = None
    due_date: Optional[date] = None

@app.patch("/meetings/{mid}/items/{item_id}")
def edit_item(mid: str, item_id: str, body: ItemEdit):
    with conn() as c:
        item = c.execute(
            "SELECT * FROM action_items WHERE id=%s AND meeting_id=%s", (item_id, mid)
        ).fetchone()
    if not item:
        raise HTTPException(404, "Item not found")
    if not item["external_id"]:
        raise HTTPException(409, "No card exists for this item yet")

    args = {
        "card_id": item["external_id"],
        "title": body.task,
        "notes": build_notes(body.owner, item["evidence_quote"]),
    }
    if body.due_date:
        args["due"] = body.due_date.isoformat()

    res = call_tool("update_task", args)          # Trello first
    if res.isError:
        raise HTTPException(502, f"Trello update failed: {res.content[0].text}")

    with conn() as c:                             # then our database
        c.execute(
            "UPDATE action_items SET task=%s, owner=%s, due_date=%s WHERE id=%s",
            (body.task, body.owner, body.due_date, item_id))
    audit(mid, "item_edited", {
        "item_id": item_id,
        "before": {"task": item["task"], "owner": item["owner"], "due": str(item["due_date"])},
        "after": {"task": body.task, "owner": body.owner, "due": str(body.due_date)},
    })
    return {"ok": True}

