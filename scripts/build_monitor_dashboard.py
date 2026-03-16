from __future__ import annotations

import argparse
import html
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat(timespec="seconds")


def query_rows(db_path: Path, sql: str) -> list[dict]:
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def build_payload(db_path: Path) -> dict:
    latest_cycle = query_rows(
        db_path,
        """
        SELECT id, started_at, ended_at, status, new_samples, trained_samples, batch_accuracy, notes
        FROM cycles
        ORDER BY id DESC
        LIMIT 1
        """,
    )
    latest_progress = query_rows(
        db_path,
        """
        SELECT cycle_id, ts, n_features, estimated_params, target_params, scaled_up, scale_note
        FROM model_progress
        ORDER BY id DESC
        LIMIT 1
        """,
    )
    recent_cycles = query_rows(
        db_path,
        """
        SELECT id, started_at, ended_at, status, new_samples, trained_samples, batch_accuracy
        FROM cycles
        ORDER BY id DESC
        LIMIT 30
        """,
    )
    recent_events = query_rows(
        db_path,
        """
        SELECT ts, level, event_type, message
        FROM events
        ORDER BY id DESC
        LIMIT 120
        """,
    )

    progress_pct = None
    if latest_progress:
        target = max(1, int(latest_progress[0].get("target_params", 1)))
        progress_pct = (int(latest_progress[0].get("estimated_params", 0)) / target) * 100.0

    return {
        "generated_at_utc": utc_now(),
        "db_exists": db_path.exists(),
        "latest_cycle": latest_cycle[0] if latest_cycle else None,
        "latest_model_progress": latest_progress[0] if latest_progress else None,
        "parameter_progress_percent": progress_pct,
        "recent_cycles": recent_cycles,
        "recent_events": recent_events,
    }


def render_html(payload: dict) -> str:
    data_json = json.dumps(payload, ensure_ascii=True)
    generated_at = html.escape(str(payload.get("generated_at_utc", "n/a")))
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>SML GitHub Monitor</title>
  <style>
    :root {{
      --bg: #071022;
      --panel: #0f1b33;
      --ink: #ecf2ff;
      --muted: #9ab0d9;
      --ok: #2ecc71;
      --warn: #f1c40f;
      --err: #e74c3c;
      --line: #20345c;
      --accent: #4aa3ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Segoe UI, Tahoma, sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at 85% -15%, #14386d, var(--bg));
    }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
    .head {{ display: flex; gap: 12px; align-items: center; justify-content: space-between; }}
    .badge {{
      padding: 6px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #0b162b;
      color: var(--muted);
      font-size: 12px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(140px, 1fr));
      gap: 12px;
      margin: 16px 0 22px;
    }}
    .card {{
      background: color-mix(in srgb, var(--panel) 88%, black 12%);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
    }}
    .k {{ color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .v {{ font-size: 20px; font-weight: 700; }}
    .progress {{
      height: 12px;
      background: #0a1427;
      border: 1px solid var(--line);
      border-radius: 999px;
      overflow: hidden;
      margin-top: 10px;
    }}
    .bar {{ height: 100%; background: linear-gradient(90deg, #4aa3ff, #2ecc71); width: 0%; }}
    .section {{ margin-top: 18px; }}
    h2 {{ font-size: 18px; margin: 10px 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px 6px; text-align: left; }}
    th {{ color: var(--muted); font-weight: 600; }}
    .muted {{ color: var(--muted); }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"head\">
      <h1>SML GitHub Monitor</h1>
      <div class=\"badge\">Generated: {generated_at}</div>
    </div>

    <div class=\"grid\">
      <div class=\"card\"><div class=\"k\">Latest Cycle ID</div><div class=\"v\" id=\"cycleId\">-</div></div>
      <div class=\"card\"><div class=\"k\">Cycle Status</div><div class=\"v\" id=\"cycleStatus\">-</div></div>
      <div class=\"card\"><div class=\"k\">Estimated Params</div><div class=\"v\" id=\"params\">-</div></div>
      <div class=\"card\"><div class=\"k\">Target Progress</div><div class=\"v\" id=\"progress\">-</div><div class=\"progress\"><div class=\"bar\" id=\"bar\"></div></div></div>
    </div>

    <div class=\"section\">
      <h2>Recent Cycles</h2>
      <table id=\"cycles\"></table>
    </div>

    <div class=\"section\">
      <h2>Recent Events / Logs</h2>
      <table id=\"events\"></table>
    </div>

    <p class=\"muted\">This page is rebuilt on each GitHub Actions run.</p>
  </div>

  <script>
    const data = {data_json};

    function fmt(value) {{
      if (value === null || value === undefined) return "-";
      return String(value);
    }}

    function render() {{
      const cycle = data.latest_cycle || {{}};
      const prog = data.latest_model_progress || {{}};
      const pct = data.parameter_progress_percent;

      document.getElementById("cycleId").textContent = fmt(cycle.id);
      document.getElementById("cycleStatus").textContent = fmt(cycle.status);
      document.getElementById("params").textContent = fmt(prog.estimated_params);
      document.getElementById("progress").textContent = pct == null ? "-" : pct.toFixed(8) + "%";

      const bar = document.getElementById("bar");
      const bounded = pct == null ? 0 : Math.max(0, Math.min(100, pct));
      bar.style.width = bounded + "%";

      const cycles = data.recent_cycles || [];
      const cyclesTable = document.getElementById("cycles");
      cyclesTable.innerHTML = "<tr><th>ID</th><th>Started</th><th>Ended</th><th>Status</th><th>New</th><th>Trained</th><th>Acc</th></tr>" +
        cycles.map(c => `<tr><td>${{fmt(c.id)}}</td><td>${{fmt(c.started_at)}}</td><td>${{fmt(c.ended_at)}}</td><td>${{fmt(c.status)}}</td><td>${{fmt(c.new_samples)}}</td><td>${{fmt(c.trained_samples)}}</td><td>${{fmt(c.batch_accuracy)}}</td></tr>`).join("");

      const events = data.recent_events || [];
      const eventsTable = document.getElementById("events");
      eventsTable.innerHTML = "<tr><th>Timestamp</th><th>Level</th><th>Type</th><th>Message</th></tr>" +
        events.map(e => `<tr><td>${{fmt(e.ts)}}</td><td>${{fmt(e.level)}}</td><td>${{fmt(e.event_type)}}</td><td>${{fmt(e.message)}}</td></tr>`).join("");
    }}

    render();
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static monitor dashboard from SQLite state")
    parser.add_argument("--db", default="sml_state.sqlite3", help="Path to sqlite db")
    parser.add_argument("--out-dir", default="monitor", help="Output directory")
    args = parser.parse_args()

    db_path = Path(args.db)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(db_path)
    (out_dir / "status.json").write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    (out_dir / "index.html").write_text(render_html(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
