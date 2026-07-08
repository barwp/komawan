import sqlite3
from pathlib import Path


DB_PATH = Path("data") / "sentimentcloud.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                analysis_date TEXT NOT NULL,
                total_comments INTEGER NOT NULL,
                positive_count INTEGER NOT NULL,
                negative_count INTEGER NOT NULL,
                neutral_count INTEGER NOT NULL
            )
            """
        )


def save_history(
    topic: str,
    analysis_date: str,
    total_comments: int,
    positive_count: int,
    negative_count: int,
    neutral_count: int,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO analysis_history (
                topic,
                analysis_date,
                total_comments,
                positive_count,
                negative_count,
                neutral_count
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                topic,
                analysis_date,
                total_comments,
                positive_count,
                negative_count,
                neutral_count,
            ),
        )


def fetch_history():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                id,
                topic,
                analysis_date,
                total_comments,
                positive_count,
                negative_count,
                neutral_count
            FROM analysis_history
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def delete_history(history_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM analysis_history WHERE id = ?", (history_id,))
