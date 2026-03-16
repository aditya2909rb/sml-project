from __future__ import annotations

import sqlite3
from pathlib import Path

import streamlit as st

DB_PATH = Path("sml_state.sqlite3")


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

col1, col2, col3 = st.columns(3)
col1.metric("Cycles", len(cycles))
col2.metric("Events", len(events))
col3.metric("DB Exists", "Yes" if DB_PATH.exists() else "No")

st.subheader("Recent Cycles")
st.dataframe(cycles, use_container_width=True)

st.subheader("Recent Events")
st.dataframe(events, use_container_width=True)

st.caption("Refresh this page to see the newest training/healing cycle.")
