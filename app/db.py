import sqlite3
from contextlib import contextmanager
import os

DB_PATH = os.getenv("DB_PATH", "/data/uptime.db")

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                interval_seconds INTEGER NOT NULL DEFAULT 60,
                enabled INTEGER NOT NULL DEFAULT 1
            );
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER NOT NULL,
                ts_utc TEXT NOT NULL,
                status_code INTEGER,
                latency_ms REAL,
                ok INTEGER NOT NULL,
                error TEXT,
                FOREIGN KEY(target_id) REFERENCES targets(id)
            );
            """
        )
        c.commit()
