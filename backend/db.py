import os
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg.types.json import Json

load_dotenv()

def conn():
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)

def set_status(mid, status, error=None):
    with conn() as c:
        c.execute("UPDATE meetings SET status=%s, error=%s WHERE id=%s", (status, error, mid))

def audit(mid, action, detail=None):
    with conn() as c:
        c.execute("INSERT INTO audit_log (meeting_id, action, detail) VALUES (%s,%s,%s)",
                  (mid, action, Json(detail or {})))

def save_items(mid, items):
    """Idempotent: wipes and re-inserts, returns items with their DB ids."""
    out = []
    with conn() as c:
        c.execute("DELETE FROM action_items WHERE meeting_id=%s", (mid,))
        for it in items:
            row = c.execute(
                """INSERT INTO action_items
                   (meeting_id, task, owner, due_date, due_text, evidence_quote, confidence, flagged)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (mid, it["task"], it.get("owner"), it.get("due_date"), it.get("due_text"),
                 it["evidence_quote"], it.get("confidence"), it.get("flagged", False)),
            ).fetchone()
            out.append({**it, "id": str(row["id"])})
    return out
