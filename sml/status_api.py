from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat(timespec="seconds")


def _query_one(db_path: Path, sql: str) -> dict | None:
    if not db_path.exists():
        return None
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(sql).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def _query_value(db_path: Path, sql: str) -> int:
    if not db_path.exists():
        return 0
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(sql).fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def _query_stats(db_path: Path) -> dict:
    if not db_path.exists():
        return {
            "total_new_samples": 0,
            "total_trained_samples": 0,
            "recent_avg_batch_accuracy": None,
            "last_completed_cycle_at": None,
        }
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        totals = conn.execute(
            """
            SELECT COALESCE(SUM(new_samples), 0) AS total_new_samples,
                   COALESCE(SUM(trained_samples), 0) AS total_trained_samples,
                   MAX(ended_at) AS last_completed_cycle_at
            FROM cycles
            """
        ).fetchone()
        avg_row = conn.execute(
            """
            SELECT AVG(batch_accuracy) AS recent_avg_batch_accuracy
            FROM (
                SELECT batch_accuracy
                FROM cycles
                WHERE batch_accuracy IS NOT NULL
                ORDER BY id DESC
                LIMIT 5
            )
            """
        ).fetchone()
        return {
            "total_new_samples": int(totals["total_new_samples"] or 0),
            "total_trained_samples": int(totals["total_trained_samples"] or 0),
            "recent_avg_batch_accuracy": avg_row["recent_avg_batch_accuracy"],
            "last_completed_cycle_at": totals["last_completed_cycle_at"],
        }
    finally:
        conn.close()


def build_status(db_path: Path) -> dict:
    latest = _query_one(
        db_path,
        """
        SELECT id, started_at, ended_at, status, new_samples, trained_samples, batch_accuracy
        FROM cycles
        ORDER BY id DESC
        LIMIT 1
        """,
    )
    event_count = _query_value(db_path, "SELECT COUNT(*) FROM events")
    cycle_count = _query_value(db_path, "SELECT COUNT(*) FROM cycles")
    model_progress = _query_one(
        db_path,
        """
        SELECT cycle_id, ts, n_features, estimated_params, target_params, scaled_up, scale_note
        FROM model_progress
        ORDER BY id DESC
        LIMIT 1
        """,
    )
    progress_percent = None
    stats = _query_stats(db_path)
    if model_progress is not None and int(model_progress.get("target_params", 0)) > 0:
        progress_percent = (
            float(model_progress["estimated_params"]) / float(model_progress["target_params"])
        ) * 100.0

    return {
        "now_utc": _utc_now(),
        "db_exists": db_path.exists(),
        "cycle_count": cycle_count,
        "event_count": event_count,
        "training_totals": stats,
        "latest_cycle": latest,
        "latest_model_progress": model_progress,
        "parameter_progress_percent": progress_percent,
    }


def make_handler(db_path: Path):
    class StatusHandler(BaseHTTPRequestHandler):
        def _html(self, code: int, body: str) -> None:
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _json(self, code: int, payload: dict) -> None:
            data = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._html(
                    200,
                    """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>SML Status</title>
    <style>
        :root {
            --bg: #0f172a;
            --panel: #111827;
            --ink: #e5e7eb;
            --muted: #9ca3af;
            --accent: #22c55e;
        }
        body {
            margin: 0;
            font-family: Segoe UI, Tahoma, sans-serif;
            background: radial-gradient(circle at top right, #1e293b, var(--bg));
            color: var(--ink);
            min-height: 100vh;
        }
        .wrap {
            max-width: 900px;
            margin: 32px auto;
            padding: 0 16px;
        }
        .card {
            background: color-mix(in srgb, var(--panel) 90%, black 10%);
            border: 1px solid #1f2937;
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
        }
        h1 {
            margin-top: 0;
            font-size: 1.4rem;
        }
        .muted {
            color: var(--muted);
        }
        pre {
            background: #020617;
            border: 1px solid #1f2937;
            border-radius: 10px;
            padding: 12px;
            overflow: auto;
            font-size: 12px;
            line-height: 1.45;
        }
        .ok {
            color: var(--accent);
            font-weight: 700;
        }
    </style>
</head>
<body>
    <div class="wrap">
        <div class="card">
            <h1>SML Live Status</h1>
            <p class="muted">Auto-refresh every 5 seconds from <code>/status</code>.</p>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:16px 0;">
                <div class="card" style="padding:12px;"><div class="muted">Health</div><div id="health" class="muted">loading...</div></div>
                <div class="card" style="padding:12px;"><div class="muted">Cycles</div><div id="cycleCount">-</div></div>
                <div class="card" style="padding:12px;"><div class="muted">Total Trained</div><div id="trainedTotal">-</div></div>
                <div class="card" style="padding:12px;"><div class="muted">Latest New Samples</div><div id="latestNew">-</div></div>
                <div class="card" style="padding:12px;"><div class="muted">Latest Accuracy</div><div id="latestAcc">-</div></div>
                <div class="card" style="padding:12px;"><div class="muted">Param Progress</div><div id="paramProgress">-</div></div>
            </div>
            <pre id="json">Loading status...</pre>
        </div>
    </div>

    <script>
        async function refresh() {
            try {
                const health = await fetch('/health').then(r => r.json());
                const status = await fetch('/status').then(r => r.json());
                document.getElementById('health').textContent = health.status === 'ok' ? 'ok' : 'not-ok';
                document.getElementById('health').className = health.status === 'ok' ? 'ok' : 'muted';
                document.getElementById('cycleCount').textContent = String(status.cycle_count ?? '-');
                document.getElementById('trainedTotal').textContent = String(status.training_totals?.total_trained_samples ?? '-');
                document.getElementById('latestNew').textContent = String(status.latest_cycle?.new_samples ?? '-');
                document.getElementById('latestAcc').textContent = status.latest_cycle?.batch_accuracy == null ? 'n/a' : String(status.latest_cycle.batch_accuracy);
                document.getElementById('paramProgress').textContent = status.parameter_progress_percent == null ? 'n/a' : `${status.parameter_progress_percent.toFixed(6)}%`;
                document.getElementById('json').textContent = JSON.stringify(status, null, 2);
            } catch (err) {
                document.getElementById('health').textContent = 'error';
                document.getElementById('health').className = 'muted';
                document.getElementById('json').textContent = String(err);
            }
        }

        refresh();
        setInterval(refresh, 5000);
    </script>
</body>
</html>
                    """.strip(),
                )
                return

            if parsed.path == "/health":
                self._json(200, {"status": "ok", "db_exists": db_path.exists()})
                return

            if parsed.path == "/status":
                self._json(200, build_status(db_path))
                return

            self._json(404, {"error": "not found", "available": ["/", "/health", "/status"]})

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    return StatusHandler


def run_status_server(db_path: str, host: str, port: int) -> None:
    db_file = Path(db_path)
    server = ThreadingHTTPServer((host, port), make_handler(db_file))
    server.serve_forever()
