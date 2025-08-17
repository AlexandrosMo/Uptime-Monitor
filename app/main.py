import os
import logging
import json
import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from threading import Thread
from contextlib import asynccontextmanager
import time
import requests
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")

DB_FILE = os.getenv("DB_PATH", "/data/uptime.db")
os.makedirs("/data", exist_ok=True)  # εξασφαλίζει ότι ο φάκελος υπάρχει

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                interval_seconds INTEGER NOT NULL,
                enabled INTEGER NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER NOT NULL,
                ts_utc TEXT NOT NULL,
                status_code INTEGER,
                latency_ms REAL,
                ok INTEGER,
                error TEXT
            )
        """)
        c.commit()


class TargetCreate(BaseModel):
    url: str
    interval_seconds: int = 60
    enabled: bool = True

class Checker(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.interval = int(os.getenv("CHECKER_SCAN_INTERVAL", 5))

    def run(self):
        while True:
            try:
                with get_conn() as c:
                    rows = c.execute("SELECT id, url, enabled FROM targets WHERE enabled=1").fetchall()
                for r in rows:
                    target_id = r["id"]
                    url = r["url"]
                    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    try:
                        start = time.time()
                        resp = requests.get(url, timeout=int(os.getenv("HTTP_TIMEOUT", 10)))
                        latency = (time.time() - start) * 1000
                        ok = 1 if resp.status_code == 200 else 0
                        error = None if ok else f"Status {resp.status_code}"
                    except Exception as e:
                        latency = None
                        ok = 0
                        error = str(e)
                        resp = type("Resp", (), {"status_code": None})()
                    with get_conn() as c:
                        c.execute("""
                            INSERT INTO checks (target_id, ts_utc, status_code, latency_ms, ok, error)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (target_id, ts, resp.status_code, latency, ok, error))
                        c.commit()
            except Exception as e:
                print("Checker error:", e)
            time.sleep(self.interval)

checker = Checker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    checker.start()
    yield

app = FastAPI(title="Uptime Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        extras = {k: v for k, v in record.__dict__.items() if k not in (
            "args","msg","levelname","levelno","pathname","filename","module",
            "exc_info","exc_text","stack_info","lineno","funcName","created",
            "msecs","relativeCreated","thread","threadName","processName","process")}
        payload.update(extras)
        return json.dumps(payload)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
for h in logging.getLogger().handlers:
    h.setFormatter(JsonFormatter())


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1>Uptime Monitor API</h1>
    <ul>
        <li><a href='/docs'>API Docs</a></li>
        <li><a href='/status'>Status Page</a></li>
    </ul>
    """
@app.get("/status", response_class=HTMLResponse)
async def status(request: Request):
    with get_conn() as c:
        rows = c.execute("""
            SELECT t.id, t.url, c.ts_utc, c.status_code, c.latency_ms, c.ok, c.error
            FROM targets t
            LEFT JOIN (
                SELECT target_id, MAX(ts_utc) as max_ts
                FROM checks
                GROUP BY target_id
            ) last ON t.id = last.target_id
            LEFT JOIN checks c ON t.id = c.target_id AND c.ts_utc = last.max_ts
        """).fetchall()
    return templates.TemplateResponse("status.html", {"request": request, "rows": rows})

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/targets")
async def create_target(t: TargetCreate):
    with get_conn() as c:
        c.execute(
            "INSERT INTO targets (url, interval_seconds, enabled) VALUES (?, ?, ?)",
            (t.url, t.interval_seconds, 1 if t.enabled else 0)
        )
        c.commit()
        tid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {"id": tid, **t.dict()}

@app.get("/targets")
async def list_targets():
    with get_conn() as c:
        rows = c.execute("SELECT id, url, interval_seconds, enabled FROM targets").fetchall()
    return [{"id": r["id"], "url": r["url"], "interval_seconds": r["interval_seconds"], "enabled": bool(r["enabled"])} for r in rows]

@app.delete("/targets/{target_id}")
async def delete_target(target_id: int):
    with get_conn() as c:
        c.execute("DELETE FROM targets WHERE id = ?", (target_id,))
        c.commit()
    return {"deleted": target_id}

