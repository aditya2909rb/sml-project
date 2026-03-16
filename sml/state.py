from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat(timespec="seconds")


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    with closing(connect(db_path)) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                status TEXT NOT NULL,
                new_samples INTEGER NOT NULL DEFAULT 0,
                trained_samples INTEGER NOT NULL DEFAULT 0,
                batch_accuracy REAL,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                level TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                meta_json TEXT
            );

            CREATE TABLE IF NOT EXISTS seen_items (
                text_hash TEXT PRIMARY KEY,
                first_seen_at TEXT NOT NULL
            );
            """
        )
        conn.commit()


def log_event(db_path: str, level: str, event_type: str, message: str, meta: dict[str, Any] | None = None) -> None:
    with closing(connect(db_path)) as conn:
        conn.execute(
            "INSERT INTO events(ts, level, event_type, message, meta_json) VALUES (?, ?, ?, ?, ?)",
            (utc_now(), level, event_type, message, json.dumps(meta or {})),
        )
        conn.commit()


def start_cycle(db_path: str) -> int:
    with closing(connect(db_path)) as conn:
        cur = conn.execute(
            "INSERT INTO cycles(started_at, status) VALUES (?, ?)",
            (utc_now(), "running"),
        )
        conn.commit()
        return int(cur.lastrowid)


def end_cycle(
    db_path: str,
    cycle_id: int,
    status: str,
    new_samples: int,
    trained_samples: int,
    batch_accuracy: float | None,
    notes: str,
) -> None:
    with closing(connect(db_path)) as conn:
        conn.execute(
            """
            UPDATE cycles
            SET ended_at = ?, status = ?, new_samples = ?, trained_samples = ?, batch_accuracy = ?, notes = ?
            WHERE id = ?
            """,
            (utc_now(), status, new_samples, trained_samples, batch_accuracy, notes, cycle_id),
        )
        conn.commit()


def mark_seen_and_filter_new(db_path: str, hashes: list[str]) -> set[str]:
    new_hashes: set[str] = set()
    with closing(connect(db_path)) as conn:
        for text_hash in hashes:
            cur = conn.execute("SELECT 1 FROM seen_items WHERE text_hash = ?", (text_hash,))
            if cur.fetchone() is None:
                new_hashes.add(text_hash)
                conn.execute(
                    "INSERT INTO seen_items(text_hash, first_seen_at) VALUES (?, ?)",
                    (text_hash, utc_now()),
                )
        conn.commit()
    return new_hashes


def get_recent_batch_accuracies(db_path: str, limit: int) -> list[float]:
    if limit <= 0:
        return []
    with closing(connect(db_path)) as conn:
        rows = conn.execute(
            """
            SELECT batch_accuracy
            FROM cycles
            WHERE batch_accuracy IS NOT NULL
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [float(row[0]) for row in rows]
