import os
import sqlite3
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover - only happens before dependencies are installed
    psycopg2 = None
    RealDictCursor = None


DB_PATH = Path("data") / "sentimentcloud.db"


def get_database_url() -> str:
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    try:
        import streamlit as st

        return st.secrets.get("DATABASE_URL", "")
    except Exception:
        return ""


def using_postgres() -> bool:
    database_url = get_database_url()
    return database_url.startswith(("postgres://", "postgresql://"))


def get_connection():
    database_url = get_database_url()
    if database_url:
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary belum terpasang. Jalankan pip install -r requirements.txt.")
        return psycopg2.connect(database_url, sslmode="require")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        id SERIAL PRIMARY KEY,
                        topic TEXT NOT NULL,
                        analysis_date TEXT NOT NULL,
                        total_comments INTEGER NOT NULL,
                        positive_count INTEGER NOT NULL,
                        negative_count INTEGER NOT NULL,
                        neutral_count INTEGER NOT NULL
                    )
                    """
                )
        return

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
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO analysis_history (
                        topic,
                        analysis_date,
                        total_comments,
                        positive_count,
                        negative_count,
                        neutral_count
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
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
        return

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
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
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
                )
                return [dict(row) for row in cur.fetchall()]

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
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM analysis_history WHERE id = %s", (history_id,))
        return

    with get_connection() as conn:
        conn.execute("DELETE FROM analysis_history WHERE id = ?", (history_id,))
