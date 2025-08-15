import os
import logging
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.db import get_conn, init_db
from app.models import TargetCreate
from app.monitor import Checker

PORT = int(os.getenv("PORT", "8000"))

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k
            not in (
                "args", "msg", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process"
            )
        }
        payload.update(extras)
        return json.dumps(payload)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
for h in logging.getLogger().handlers:
    h.setFormatter(JsonFormatter())

app = FastAPI(title="Uptime Monitor")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()
    Checker().start()

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
            (str(t.url), t.interval_seconds, 1 if t.enabled else 0),
        )
        c.commit()
        tid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {"id": tid, **t.model_dump()}

@app.get("/targets")
async def list_targets():
    with get_conn() as c:
        rows = c.execute("SELECT id, url, interval_seconds, enabled FROM targets").fetchall()
    return [
        {
            "id": r[0],
            "url": r[1],
            "interval_seconds": r[2],
            "enabled": bool(r[3]),
        }
        for r in rows
    ]

@app.delete("/targets/{target_id}")
async def delete_target(target_id: int):
    with get_conn() as c:
        c.execute("DELETE FROM targets WHERE id = ?", (target_id,))
        c.commit()
    return {"deleted": target_id}

@app.get("/")
async def status_page():
    html_template = """
    <html>
    <head><title>Uptime Status</title></head>
    <body>
    <h1>Uptime Monitor</h1>
    <table border="1">
    <tr><th>ID</th><th>URL</th><th>Last Check</th><th>Status Code</th><th>Latency (ms)</th><th>OK</th><th>Error</th></tr>
    {rows}
    </table>
    </body>
    </html>
    """
    with get_conn() as c:
        rows = c.execute("""
            SELECT t.id, t.url, c.ts_utc, c.status_code, c.latency_ms, c.ok, c.error
            FROM targets t
            LEFT JOIN checks c ON t.id = c.target_id
            WHERE c.id = (SELECT MAX(id) FROM checks WHERE target_id = t.id)
        """).fetchall()
    rows_html = "\n".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[6]}</td></tr>"
        for r in rows
    )
    return HTMLResponse(html_template.replace("{rows}", rows_html))
