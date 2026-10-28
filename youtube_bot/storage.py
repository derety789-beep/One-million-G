"""Petite base SQLite pour mémoriser ce que le bot a déjà fait."""

import sqlite3
from datetime import date

from .config import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS replied_comments (
    comment_id TEXT PRIMARY KEY,
    replied_at TEXT DEFAULT CURRENT_TIMESTAMP,
    reply TEXT
);
CREATE TABLE IF NOT EXISTS uploads (
    video_id TEXT PRIMARY KEY,
    file_name TEXT,
    title TEXT,
    uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS channel_stats (
    day TEXT PRIMARY KEY,
    subscribers INTEGER,
    views INTEGER,
    videos INTEGER
);
"""


def _connect() -> sqlite3.Connection:
    config.data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.data_dir / "bot.db")
    conn.executescript(_SCHEMA)
    return conn


def was_replied(comment_id: str) -> bool:
    with _connect() as conn:
        row = conn.execute("SELECT 1 FROM replied_comments WHERE comment_id = ?", (comment_id,)).fetchone()
    return row is not None


def mark_replied(comment_id: str, reply: str | None) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO replied_comments (comment_id, reply) VALUES (?, ?)",
            (comment_id, reply),
        )


def save_upload(video_id: str, file_name: str, title: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO uploads (video_id, file_name, title) VALUES (?, ?, ?)",
            (video_id, file_name, title),
        )


def save_stats(subscribers: int, views: int, videos: int) -> dict | None:
    """Enregistre les stats du jour et renvoie celles de la veille (ou None)."""
    today = date.today().isoformat()
    with _connect() as conn:
        previous = conn.execute(
            "SELECT subscribers, views, videos FROM channel_stats WHERE day < ? ORDER BY day DESC LIMIT 1",
            (today,),
        ).fetchone()
        conn.execute(
            "INSERT OR REPLACE INTO channel_stats (day, subscribers, views, videos) VALUES (?, ?, ?, ?)",
            (today, subscribers, views, videos),
        )
    if previous is None:
        return None
    return {"subscribers": previous[0], "views": previous[1], "videos": previous[2]}
