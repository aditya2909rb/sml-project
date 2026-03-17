from __future__ import annotations

import json
import sqlite3
from urllib.request import Request, urlopen
from pathlib import Path

import streamlit as st

DB_PATH = Path("sml_state.sqlite3")


def fetch_github_model_budget() -> dict | None:
    url = "https://raw.githubusercontent.com/aditya2909rb/sml-project/github-model-state/model_training_report.json"
    req = Request(url, headers={"User-Agent": "OncoSML-Dashboard/1.0"})
    try:
        with urlopen(req, timeout=4) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode("utf-8"))
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def query(sql: str) -> list[dict]:
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


st.set_page_config(page_title="SML Tracker", layout="wide")
st.title("SML Learning Tracker")

cycles = query(
    """
    SELECT id, started_at, ended_at, status, new_samples, trained_samples, batch_accuracy, notes
    FROM cycles
    ORDER BY id DESC
    LIMIT 50
    """
)

events = query(
    """
    SELECT id, ts, level, event_type, message
    FROM events
    ORDER BY id DESC
    LIMIT 100
    """
)

model_progress = query(
    """
    SELECT cycle_id, ts, n_features, estimated_params, target_params, scaled_up, scale_note
    FROM model_progress
    ORDER BY id DESC
    LIMIT 50
    """
)

totals = query(
    """
    SELECT COALESCE(SUM(new_samples), 0) AS total_new_samples,
           COALESCE(SUM(trained_samples), 0) AS total_trained_samples,
           AVG(batch_accuracy) AS avg_batch_accuracy
    FROM (
        SELECT new_samples, trained_samples, batch_accuracy
        FROM cycles
        ORDER BY id DESC
        LIMIT 20
    )
    """
)

latest_cycle = cycles[0] if cycles else None
stats = totals[0] if totals else {"total_new_samples": 0, "total_trained_samples": 0, "avg_batch_accuracy": None}
github_budget = fetch_github_model_budget()

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
col1.metric("Cycles", len(cycles))
col2.metric("Events", len(events))
col3.metric("Total Trained", int(stats["total_trained_samples"] or 0))
col4.metric("Total New", int(stats["total_new_samples"] or 0))
if model_progress:
    latest = model_progress[0]
    target = max(1, int(latest["target_params"]))
    current = int(latest["estimated_params"])
    pct = (current / target) * 100.0
    col5.metric("Parameter Progress", f"{pct:.6f}%")
else:
    col5.metric("Parameter Progress", "n/a")
col6.metric("DB Exists", "Yes" if DB_PATH.exists() else "No")
col7.metric("GitHub Budget", int(github_budget.get("estimated_params", 0)) if github_budget else "n/a")

detail1, detail2, detail3 = st.columns(3)
detail1.metric("Latest Cycle New Samples", latest_cycle["new_samples"] if latest_cycle else "n/a")
detail2.metric("Latest Cycle Trained", latest_cycle["trained_samples"] if latest_cycle else "n/a")
avg_acc = stats["avg_batch_accuracy"]
detail3.metric("Recent Avg Accuracy", f"{float(avg_acc):.4f}" if avg_acc is not None else "n/a")

st.subheader("Recent Cycles")
st.dataframe(cycles, use_container_width=True)

st.subheader("Recent Events")
st.dataframe(events, use_container_width=True)

st.subheader("Model Parameter Growth")
st.dataframe(model_progress, use_container_width=True)

if github_budget:
    st.subheader("GitHub Model State")
    gh_target = max(1, int(github_budget.get("parameter_target", 1) or 1))
    gh_current = int(github_budget.get("estimated_params", 0) or 0)
    st.write(
        {
            "estimated_params": gh_current,
            "parameter_target": gh_target,
            "github_progress_percent": (gh_current / gh_target) * 100.0,
            "trained_samples": github_budget.get("trained_samples"),
            "batch_accuracy": github_budget.get("batch_accuracy"),
        }
    )

st.caption("Refresh this page to see the newest training/healing cycle.")
