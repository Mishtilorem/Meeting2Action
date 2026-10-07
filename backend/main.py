import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Meeting-to-Action API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Meeting-to-Action API is running."}

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
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                res = cur.fetchone()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": "connection_error", "details": str(e)}
