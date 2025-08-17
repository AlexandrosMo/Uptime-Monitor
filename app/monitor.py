import time
import threading
import requests
from datetime import datetime, timezone
from app.db import get_conn
from prometheus_client import Counter, Histogram
import logging
import os

log = logging.getLogger("monitor")

REQUESTS_TOTAL = Counter(
    "uptime_requests_total", "Total check requests", ["target_id", "url", "result"]
)
LATENCY = Histogram(
    "uptime_latency_seconds", "Check latency in seconds", ["target_id", "url"]
)

CHECKER_INTERVAL = int(os.getenv("CHECKER_SCAN_INTERVAL", "5"))  # seconds between DB scans
TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10"))

class Checker(threading.Thread):
    daemon = True

    def run(self):
        next_run = {}
        while True:
            try:
                now = time.time()
                with get_conn() as c:
                    targets = c.execute(
                        "SELECT id, url, interval_seconds, enabled FROM targets"
                    ).fetchall()
                    for t in targets:
                        if not t[3]:
                            continue
                        tid, url, interval, _ = t
                        if now >= next_run.get(tid, 0):
                            self.check_once(tid, url)
                            next_run[tid] = now + interval
            except Exception as e:
                log.exception("checker loop error: %s", e)
            time.sleep(CHECKER_INTERVAL)

    def check_once(self, target_id: int, url: str):
        ts = datetime.now(timezone.utc).isoformat()
        status_code = None
        latency_ms = None
        ok = False
        err = None
        start = time.time()
        try:
            resp = requests.get(url, timeout=TIMEOUT)
            status_code = resp.status_code
            ok = 200 <= status_code < 400
        except Exception as e:
            err = str(e)
        finally:
            latency_ms = (time.time() - start) * 1000.0
            with get_conn() as c:
                c.execute(
                    "INSERT INTO checks (target_id, ts_utc, status_code, latency_ms, ok, error) VALUES (?, ?, ?, ?, ?, ?)",
                    (target_id, ts, status_code, latency_ms, 1 if ok else 0, err),
                )
                c.commit()
            REQUESTS_TOTAL.labels(str(target_id), url, "ok" if ok else "fail").inc()
            LATENCY.labels(str(target_id), url).observe(latency_ms / 1000.0)
            log.info(
                "check_done",
                extra={
                    "target_id": target_id,
                    "url": url,
                    "ok": ok,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "error": err,
                },
            )
